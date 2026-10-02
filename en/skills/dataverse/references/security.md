# Security in Dataverse: who reads which rows

Security role, business unit, owner team, row scope and column security, with the risk of
Organization scope. Authorization *inside the flow* belongs to `power-automate`; the rule that scope
on the screen is UX and not a control is `default-decisions.md` A3 -- here is what to do in Dataverse
so that the barrier really exists.

## Contents

1. [The model in one table](#1-the-model-in-one-table)
2. [Security role and access level](#2-security-role-and-access-level)
3. [The risk of Organization scope](#3-the-risk-of-organization-scope)
4. [Row isolation: owner team + business unit](#4-row-isolation-owner-team--business-unit)
5. [Column security](#5-column-security)
6. [Application profile × security role](#6-application-profile--security-role)
7. [How to test outside the app](#7-how-to-test-outside-the-app)
8. [Decision and risk record](#8-decision-and-risk-record)

---

## 1. The model in one table

| Piece | What it controls | Granularity |
|---|---|---|
| **Security role** | Privileges (create, read, write, delete, append, append to, assign, share) per table | Table × access level |
| **Access level** | Which rows the privilege applies to: User, Business unit, Parent: child, Organization | Row, by **owner** and by **BU** |
| **Business unit (BU)** | Isolation hierarchy: the row's owner belongs to a BU | Tree of units |
| **Owner team / access team** | A group that can **own** rows (owner team) or receive access to specific rows (access team) | Set of users |
| **Column security** | Who reads/writes a specific column (column security profile) | Column |
| **Gallery filter** | Nothing security-related: only what the screen shows | — |

General source:
[Security roles and privileges](https://learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges)
and [Security concepts in Dataverse](https://learn.microsoft.com/en-us/power-platform/admin/wp-security-cds).
The detail of behavior per access level and BU inheritance was not reconfirmed here
`[unverified]`; the practice of the reference projects is recorded in the Script of §4.

## 2. Security role and access level

- The role says **which tables** and **which verb**; the **access level** says **which rows**. A role
  with Read at *Organization* reads all rows of the table, from all BUs.
- Whoever uses the app needs a role with the privileges of the tables the app touches, **including
  Append/Append to** on the tables related by Lookup (to write a Lookup).
- Least-privilege principle: domain tables (catalogs, profiles) on Read; transactional ones with
  Create/Read/Write; **Delete off** when the business does not delete (it uses `ativo` or the "closed" state).
  A second role (administration) with Create/Write on the user and link tables, assigned only to
  whoever has the matching application permission.
- The role is assigned to the **user or to a team**; the Entra group that provisions access is the same
  one the provisioning flow manipulates: agree on the group name before creating the role.
- A flow's service **connector** runs as the connection's account, not as the app user: that
  account's role decides what the flow can read (`power-automate`).

## 3. The risk of Organization scope

A security role at **Organization** scope on the app's tables limits **which tables** the user accesses,
**not which rows**. Effect: any user with access to the environment and the role can read the whole
table -- all units -- through **Excel, Power BI, the Web API (OData)** or any other
Dataverse client, **regardless of what the app's gallery shows**.
`[verified: reference project]` -- risk formally accepted for time and cost reasons.

Points the team tends to underestimate:

- The unit filter in the gallery **helps navigation**; the server is what blocks. The screen can be bypassed.
- "Only whoever has the app" is not a barrier: the role gives access to the table, not to the app.
- This is a **reduction** in security compared with an architecture where only the application talks to the
  database (SQL Server with a service account and procedures).
- Power BI and Excel over Dataverse read with the identity of whoever queries and inherit the same problem.

If the operation does **not** need real isolation (the units already see each other; the filter is a convenience),
Organization scope is a legitimate choice -- **as long as it is recorded as an accepted risk** (§8). If it
does, go to §4.

## 4. Row isolation: owner team + business unit

Recommendation for real isolation per unit: **Owner Teams + Business Unit**. Script
(`[verified: reference project]` as a plan and estimated cost; **not executed**, by decision):

1. **Define the granularity.** One BU/owner team per **region** (few) is viable. One BU per
   **unit** (dozens) costs a lot of administration and was discarded in the reference project; isolating
   unit from unit within the same region requires one BU per unit.
2. **Create the Owner Teams** (one per isolation unit) and link each to its BU.
3. **Change the role's access level** from Organization to **Business unit** (or Parent: child,
   if the region sees its units).
4. **Assign each row's `ownerid`** to its unit's team, **at write time** -- through the
   registration flow, which knows the row's unit. Tables that will undergo this isolation must be
   born **UserOwned** (see `references/modeling.md`): a table's ownership type
   cannot be changed after it is created `[unverified: a claim from a creation script; check Learn
   before relying on it]`.
5. **Keep the screen filter**, now as a convenience, not as a control.
6. **Test outside the app** (§7).

Costs and risks:

- A row without the right owner is invisible (or too visible): the flow that assigns `ownerid` becomes the
  critical point. Imported legacy rows must receive the right owner on load (`references/data-import.md`).
- A user who serves more than one unit needs more than one team.
- Shared domain tables (unit catalog, profiles) stay **OrganizationOwned** with
  Read at Organization -- they are not isolated.

## 5. Column security

To hide **one column** (sensitive data inside a table everyone reads), use
[column-level security](https://learn.microsoft.com/en-us/power-platform/admin/field-level-security):
mark the column as protected and grant a **column security profile** to whoever reads/creates/updates.

- It protects against direct reading through the API, unlike hiding the field on the screen.
- It does not isolate **rows**; combine with owner team/BU when the requirement is per unit.
- A protected column appears as empty/blocked to whoever does not have the profile: a formula that depends on it
  must handle `Blank()`.
- `[unverified]`: exact behavior of a protected column in a Canvas formula and in Power BI.

## 6. Application profile × security role

They are different layers and do not replace each other:

| | Application profile | Security role |
|---|---|---|
| Where it lives | App table (`perfis` + `pode_x` flags) | Dataverse |
| Who enforces it | The app and the **flow** | The server |
| Bypassed from the client? | Yes, if only the app enforces it | No |
| Used for | Showing/hiding a button; per-action flag in the flow | Blocking access to the data |

Permission by **profile flag** (`pode_x`), never by profile name (T8); no resolved profile = no
access (fail-closed). The flag decides what the app offers and what the flow accepts; the role decides what
the data hands to whoever queries it by another path. If only the flag exists, the control belongs to the app.

## 7. How to test outside the app

The test that isolation exists **cannot be done through the screen**. With a test account that has
**only** the app's role and belongs to **another** unit:

```
GET https://<org>.crm.dynamics.com/api/data/v9.2/<EntitySet>?$select=<coluna>&$top=50
```

(through the browser authenticated as that account, or through Excel/Power BI connected to Dataverse with it).
Expected result: **only** rows of that account's unit. Returning rows from other units =
effective Organization scope. Record the command, the account used (no personal data) and the date.

Do the same for **writing** (try to update a row from another unit) and for the **protected column**.

## 8. Decision and risk record

Choose and write it in the project's ADR (`default-decisions.md` A3/A4):

| Situation | Decision | Record |
|---|---|---|
| Units already see each other; the filter is a convenience | Organization scope | Formal **accepted risk**: "any user with the role reads all units through Excel/Power BI/Web API", with owner and date |
| Isolation per region required | Owner Teams + BU | Plan for assigning `ownerid` in the registration flow and on load |
| Isolation per unit required | Reassess the track (SQL + procedures with authorization in the flow) or a BU per unit | ADR with the administration cost |
| Sensitive column | Column security | Profile and the list of who receives it |

Never: a gallery filter as the only control with no recorded risk; Power BI over Dataverse with
Organization scope without addressing the risk.

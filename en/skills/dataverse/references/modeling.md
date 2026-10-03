# Dataverse modeling for Power Apps apps

Tables, ownership, relationships, column types, alternate keys, calculated columns and
auditing — what to decide **before** creating, because a lot of it cannot be undone. Solution, environment and
environment variables are ALM: `skills/power-platform/references/alm-environments.md`.

## Contents

1. [Who creates the schema](#1-who-creates-the-schema)
2. [Names and convention](#2-names-and-convention)
3. [Table: ownership and primary name](#3-table-ownership-and-primary-name)
4. [Column types: what to choose](#4-column-types-what-to-choose)
5. [Relationship: Lookup, Choice or text](#5-relationship-lookup-choice-or-text)
6. [Denormalized columns](#6-denormalized-columns)
7. [Alternate keys](#7-alternate-keys)
8. [Calculated and rollup columns](#8-calculated-and-rollup-columns)
9. [Requirement level](#9-requirement-level)
10. [Auditing and trail](#10-auditing-and-trail)
11. [Checklist before creating](#11-checklist-before-creating)

---

## 1. Who creates the schema

Choose **one** owner per environment and declare it:

| Owner | Advantage | Risk |
|---|---|---|
| **Maker by hand / Excel** | Fast, no prerequisite | The as-built diverges from any plan; default publisher; wrong types |
| **Script (Web API)** | Reproducible, idempotent, versionable | Needs a credential and maintenance; the environment can be changed from outside and diverge from the script |
| **Imported solution** | Reproducible across environments (ALM) | The schema is born in the source environment |

Whichever it is, **after creating**, extract the as-built (`references/as-built-names.md`) and start
writing against it. In a reference project, a complete script was written (publisher, choices,
tables, columns, Lookups, alternate keys, idempotent) and **never used**: the environment was built
by hand beforehand. `[verified: reference project]` The script did not become the authority just by existing.

If it is a script: it should read the dictionary (not embed the schema), be idempotent (skip what
exists), check the result (integer values of the Choices, `EntityKeyIndexStatus`) and **not** run against an
environment that already has hand-made tables without first extracting the as-built.

## 2. Names and convention

- **The prefix belongs to the publisher**, not to you. Create your own publisher (and the solution) **before** the tables;
  a table created outside a solution lands in the default publisher and does not export cleanly to other environments.
- An assumption of a reference project that **did not hold**: "without a prefix on the names we generate, Dataverse applies the
  publisher's". Through the maker it is true; through the Web API the prefix **must** come in the `SchemaName`; and the
  publisher of the real environment was not the planned one. Plan with an explicit `<prefixo>_`.
- **Display name = the name Power Fx will read.** If formulas will be written with
  `status_cadastro`, the column must have **that** display name; the human label goes in the `Description`
  and in the screen tokens. Mixing a human label with a formula name is a source of errors.
  `[verified: reference project]` (decision of the creation script).
- The logical name cannot be derived from the display name (`references/names-and-types.md` §2): do not write a
  document that assumes it can.
- **No environment name in the table name** (`dev…`): each environment would have a different table and
  ALM breaks (`default-decisions.md` F5). `[verified: reference project]` — in one project
  the DEV tables had `dev` in the logical name and the production ones did not.
- One convention per project: `snake_case` everywhere helps port to SQL without translation.

## 3. Table: ownership and primary name

- **Ownership** (`OwnershipType`): *UserOwned* (the row has a user/team owner — required for
  isolation by owner team/BU) or *OrganizationOwned* (no owner; catalogs and domain tables).
  **Decide at creation:** the type does not change afterwards `[unverified: claim from a reference project; check
  on Learn]`. A transactional table that may need isolation by unit is born UserOwned.
- **Primary name** (`PrimaryNameAttribute`): required on every table, it is the label in grids and
  Lookups. Choose a short, readable column; do **not** use the long narrative or a field that repeats.
  A "short label" column and a separate "description/note" column avoid a
  `Coalesce(note, summary)` hack on the screen. `[verified: reference project]`
- The **primary key** is a generated GUID; the business uses its own key (§7).
- A table no screen uses (a "dead table") costs maintenance; if a modeling decision left it
  without a function, record it (the case of a roles table when `perfil` became a Choice).

## 4. Column types: what to choose

| Need | Type | Note |
|---|---|---|
| **Closed** domain (small, stable list) | **Choice** (local or global) | Validates on the server; `Choices()` feeds the ComboBox; a new option is a schema change, not a screen change |
| Closed domain shared across tables | **Global choice** | Integer values prefixed by the publisher: do not assume `1,2,3` |
| Domain that changes without a schema change (a user-maintained list) | **Table + Lookup** | Keeps integrity; cost: a join |
| Short code the business already uses as a key (an abbreviation) | **Single line of text** + alternate key on the source table | Loses referential integrity |
| Yes/No | **Yes/No** | `col = true` |
| Date only (deadline, birth date) | **Date only** | Removes time zones and the class of bug of comparing dates as text |
| Instant (event, audit) | **Date and time**, explicit time zone behavior | `UserLocal` for what the user sees; `TimeZoneIndependent` for what cannot change |
| Numeric identifier of a legacy system | **Whole number** | Candidate for an alternate key to import |
| Short text | **Single line of text** with a length | Limit the length; long text does not filter well |

Rules:

- **Text does not become Choice or Lookup later.** Dataverse does not convert. Changing the type means recreating the
  column and migrating. Decide before importing (`references/data-import.md`).
- **Unused Choice**: a global Choice created and not tied to any column is not seen by
  `Choices()`; the ComboBox for that option needs a literal table. `[verified: reference project]`
- The source for types and their mapping to Power Apps is
  [Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service).

## 5. Relationship: Lookup, Choice or text

| Option | Integrity | Delegation | Import | When |
|---|---|---|---|---|
| **Lookup** | Yes (Dataverse guarantees it) | Filtering by the Lookup compares with a record; by a column of the related table: a join, avoid | Resolves by the primary name column or by the alternate key | A real 1:N relationship the business requires to be intact |
| **Choice** | Closed domain | `=` delegates | Resolves by label | Small, stable list with no attributes of its own |
| **Text with a code** | **None** | `=` and `StartsWith` delegate | Trivial | Short deadline; the risk is accepted (see below) |

What is lost when swapping a Lookup for text `[verified: reference project]`:

- **Referential integrity**: an invalid value gets in (a unit that does not exist); this was one of the goals of the migration.
- **A homonym collides** when the text is a person's name; the real link becomes another field (e.g. the UPN).
- **Manual join** (`LookUp`/`AddColumns`) instead of `col.field`.
- **The closed domain** disappears when a Choice becomes text: changing an option means editing the screen, and nothing
  stops the flow from writing outside the domain.

If the as-built already has text in place of the Lookup, **record the divergence** as a decision (keep or
realign, `references/as-built-names.md` §6) and compensate: validate the domain **in the flow** before writing,
and check the text against the source table on the registration screen.

## 6. Denormalized columns

A hot filter on a column of a related table forces a join and puts delegation at risk
(`references/dataverse-delegation.md`). The way out is to **copy** the column to the child table as text:

| Distance to the data | Solution |
|---|---|
| 0 levels (column of the table itself) | filter directly |
| 1 level (Lookup column) | compare the Lookup with the record |
| 2 levels (Lookup of the Lookup) | **denormalized column** on the child table |

`[unverified: the premise that filtering by a Lookup column "gives up delegation" came from the plan of a reference project; Learn
talks about a limit on lookup levels. Test with limit 1 before calling denormalization mandatory.]`

Rules for denormalization: document **who writes** the copy (the flow, in the same action that creates the row) and
**when diverging is correct** (the trail keeps the value in force at the event, not the current one).

## 7. Alternate keys

An alternate key = one or more columns that identify a row **without the GUID**. It is what enables
**upsert** and import that resolves a Lookup by a business key.
([Define alternate keys](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/define-alternate-keys-portal),
[for developers](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/define-alternate-keys-entity)).

Facts:

- The key is **not available right away**: on save, a system job creates the index. Status:
  `Pending` → `In Progress` → `Active` (or `Failed`). Through the Web API:
  `GET <org>/api/data/v9.2/EntityDefinitions(LogicalName='<tabela>')/Keys?$select=SchemaName,EntityKeyIndexStatus`.
  A key in `Pending` **does not resolve a Lookup on import and the error is silent**. `[verified: reference project]`
- If the key column data contains `/ # < > * % & : \ ? +`, `GET` and `PATCH` by key **do not
  work** (Learn, page above). Uniqueness alone is fine; for integration, choose columns without those
  characters.
- A key can be **composite** (several columns). Limits from Learn: up to 10 keys per table, 16 columns and
  900 bytes per key; only single line of text, whole number or decimal, date and time,
  Lookup and Choice columns; a column with column security cannot be in a key; keys do not exist on virtual tables
  ([Work with alternate keys](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/define-alternate-keys-entity)).
- Example: the order's business identifier (`id_pedido`) is **not unique** under the business rule, so the
  import wizard would not resolve the Lookup by the primary name; a numeric `id_legado` was
  marked as an alternate key and the load used it as the matching column.
- Example: the `$batch` upsert depends on a **composite key** (several columns: unit, type,
  date); the flow builds a `{key → GUID}` index to separate Update from Create.
  With an active composite alternate key, the lookup by GUID can be replaced by addressing the row by the
  key (upsert), `[unverified: not tested]`; the `$batch` format belongs to `power-automate`.

Define the alternate key **when modeling**, activate it and **wait for `Active`** before importing or bringing up the flow.

## 8. Calculated and rollup columns

- **Calculated**: a formula evaluated on read, on the row itself
  ([Learn](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/define-calculated-fields)).
  Useful for display and to derive a value the screen should not assemble.
- **Rollup**: an aggregation over related rows, recalculated by an asynchronous job
  ([Learn](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/define-rollup-fields)):
  the value is **not real time**.
- Do not assume that filtering by a calculated column delegates: `[unverified]` — confirm in Monitor.
  When you need to filter by a derived value (e.g. "overdue" calculated from a date), **filter by the source
  column** (the date) and use the calculated one only to display. `[verified: reference project]` (the
  deadline status column is display only; the filter uses the date).
- **Creation**: a calculated column with a complex formula is usually made in the maker; do not assume a
  Web API script creates it (in a reference project it was one of the two items that stayed manual).
- For SQL, the persisted computed column belongs to `sql-procedures` (B2); do not confuse it with this one.

## 9. Requirement level

Requirement levels in Dataverse: optional, **business recommended** and **business required**.
Required breaks the load of legacy data that lacks the field.

| Situation | Decision |
|---|---|
| New rule, no legacy | Required |
| The business rule demands it, but the legacy is empty (e.g. the vast majority has no date) | **Recommended** in Dataverse + requirement **in the flow** for registration/editing |

That way the legacy comes in as it is (empty is information) and the rule holds for 100% of new records.
Before deciding, **measure** the legacy: `[verified: reference project]` — nearly
all rows came without the date the rule requires; if it were required in the schema, the whole historical load would fail.
Confirm with the operation first: if the rule was never practiced, making it required in the flow blocks
registration on day one.

## 10. Auditing and trail

Two different things:

- **Dataverse auditing**: automatic record of who changed what, per table/column, enabled
  on the environment and on the table
  ([Manage Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing)).
  Good for compliance; consumes capacity; it is **not** the business trail shown to the user.
  `[unverified]` whether any reference project turned it on.
- **App trail table** (a business event with type, old and new value, user): written
  by the flow in the same action as the change. It is what the history screen reads. Denormalize the unit and the
  business identifier into it (§6) and keep the **value in force at the moment** of the event.
- **Flow run log tables** (run and parent flow) in Dataverse itself: the log design belongs to
  `power-automate`, but the tables belong to this skill. Define which columns **every** flow fills
  (a new version of the flow that leaves null columns the previous one filled breaks the report).

## 11. Checklist before creating

- [ ] Own publisher and solution created; prefix noted.
- [ ] Owner of schema creation defined (script **or** maker).
- [ ] Each relationship with a decision: Lookup, Choice or text, with the cost recorded.
- [ ] Each table with ownership (UserOwned/OrganizationOwned) decided, considering §3 and `references/security.md`.
- [ ] Alternate keys defined for everything imported or receiving upsert; plan to wait for `Active`.
- [ ] Choices created **before** the tables that use them; integer values noted.
- [ ] Requirement level checked against the legacy data.
- [ ] A closed domain left as text has validation in the flow.
- [ ] After creating: as-built extracted (`references/as-built-names.md`).

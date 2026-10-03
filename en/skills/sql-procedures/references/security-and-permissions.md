# Security and permissions

What the database actually guarantees when the app and the flow talk to it through a **shared service
account**, what the procedure authorizes (and what it does not), and when to disagree with the
"the procedure does not authorize" standard (A2). Authorization **inside the flow** (per-action gate,
scope) belongs to the `power-automate` skill.

## Contents

1. [Threat model](#1-threat-model)
2. [The service account: GRANT EXECUTE and nothing else](#2-the-service-account-grant-execute-and-nothing-else)
3. [What the procedure authorizes](#3-what-the-procedure-authorizes)
4. [When to disagree with "the procedure does not authorize"](#4-when-to-disagree-with-the-procedure-does-not-authorize)
5. [A limit no code closes: the caller as a parameter](#5-a-limit-no-code-closes-the-caller-as-a-parameter)
6. [Injection and leaks through errors](#6-injection-and-leaks-through-errors)
7. [Verification queries](#7-verification-queries)

---

## 1. Threat model

The SQL connector connects as **one** account, not as the end user. To the database, every caller is
the same person. Who can make the account run a procedure with parameters of their choice?

- anyone who edits the **app** or the **flow** that uses the connection reference, or creates another
  one with it;
- any other consumer of the same account (ETL, another app, a support script).

Consequences: the rule "scope on the screen is UX, not access control" (A3) applies to the flow
**too**: it is the barrier **against the end user**, not against whoever edits the flow or uses the
account. The database can only enforce what is **structurally** in the account and the objects.

## 2. The service account: GRANT EXECUTE and nothing else

What closes the direct-`Patch`-on-the-table path by construction:

```sql
-- Connector service account. Replace with the real name, read from the environment.
GRANT EXECUTE ON SCHEMA::dbo TO [<conta_do_conector>];
GO

-- And NO DML on the tables. If there is already a grant, revoke it.
REVOKE INSERT, UPDATE, DELETE ON dbo.APP_Pedido        FROM [<conta_do_conector>];
REVOKE INSERT, UPDATE, DELETE ON dbo.APP_PedidoTrilha  FROM [<conta_do_conector>];
GO

-- SELECT is still needed where the app reads the table directly (gallery, filters).
GRANT SELECT ON dbo.APP_Pedido TO [<conta_do_conector>];
GO
```

- **Without DML on the account, `Patch` does not come back**, neither by oversight nor through a new
  app on the same connection. The path is closed by construction, not by discipline.
- `GRANT EXECUTE ON SCHEMA::dbo` covers every **present and future** object in the schema. Convenient,
  but every helper procedure created there is immediately callable. For a new project, prefer **a
  schema just for the exposed procedures** (`CREATE SCHEMA app` and `GRANT EXECUTE ON SCHEMA::app`),
  or `GRANT EXECUTE` per procedure. The lint requires a qualified schema, not `dbo` in particular.
- **One account per app and per environment.** An account shared between apps is the worst case for
  tracing and for revoking.
- A table in **another database** (e.g. the corporate registry): *ownership chaining* does not cross
  databases by default; the procedure needs explicit permission, and a different collation breaks
  the `JOIN` (error 468). Confirm where the table lives before writing the procedure that reads it.
  `[unverified: confirm in your environment]`
- What this `GRANT` does **not** close: the **content** of the write. With validation and
  authorization in the flow, whoever calls the procedure writes whatever they want. State this in the
  contract; it is the biggest loss of the declarative variant and is what §4 addresses.

## 3. What the procedure authorizes

| Posture | Where the rule lives | What the database blocks |
|---|---|---|
| **A. The flow authorizes** (kit default, A2) | flow | only direct writes to the table. Anyone with the account calls the procedure |
| **B. The flow authorizes + defensive block in the procedure** | flow **and** procedure | unknown/inactive caller or one without the action's flag, **as long as** the id provided is real |
| **C. The procedure authorizes** (classic) | procedure (and the flow repeats it to give the sentence) | same as B, with business refusals in the database too |

A, B and C do **not** stop whoever lies about `@Id_UsuarioChamador` (§5). B and C reduce errors,
flow regressions and misuse by people who do not know the rule. Code for posture B/C:
`procedure-standard.md` §7.

## 4. When to disagree with "the procedure does not authorize"

The kit default is posture A because it keeps the rule in one place that is editable without a DBA,
and the database tends to freeze. **Disagree** (and record it in the project ADR) when **any** of
these is true:

| Signal | Why |
|---|---|
| The connection/account is used by **more than one app or flow**, or by people outside the flow team | the rule in the flow protects only one of the paths |
| The operation is **irreversible or financial** (closing, refund, payment) | a late refusal in the database is worth more than the nice message |
| Audit requires **trustworthy authorship** | the trail by parameter does not prove who; only resolving the caller in the procedure (still with the limit of §5) improves it |
| The DBA owns the logic and refuses a "dumb" procedure | freezing has a cost: changing a rule becomes a DBA request |
| The rule has to hold even if the flow is **replaced** or regenerated | the flow is replaceable; the database is usually what lasts |

What does **not** count as an argument: "it is safer" without saying against whom. Name the actor
(end user, flow editor, another consumer of the account) and what the block prevents.

Costs of posture B/C, to decide with open eyes: the rule now exists in **two copies** (database and
flow) that can diverge; the procedure reads the role table (a new dependency between objects); a rule
change becomes a procedure change (a DBA request if the database is frozen); more codes in the
vocabulary (`SEM_PERMISSAO`) and one more refusal for the flow to translate.

A low-cost combination: **posture A** + minimal `GRANT EXECUTE` + a **defensive block only on
irreversible operations** (the action's flag, read from the role, and the caller's status). The rest
stays declarative.

## 5. A limit no code closes: the caller as a parameter

`@Id_UsuarioChamador` arrives **as a parameter**. A rule such as "the administrator does not
deactivate themselves", written as `Id_Usuario <> @Id_UsuarioChamador`, compares the real PK against a
value **the caller chooses**: passing another id disarms the rule. It cannot be closed in SQL without
moving identity resolution back into the procedure, which goes against the design.
`[verified: reference project]`

Consequences for the contract:

- The **trail proves what and when; it does not prove who.** Write this in the contract and in the
  audit documentation.
- A domain rule in the database is a **net** (it stops the honest mistake); the source of the message
  and the control against the end user remain in the flow.
- Mitigations that reduce the risk without changing the design: one account per app; `GRANT` per
  procedure; restrict who edits the flow (ALM, managed solution); flow run log with caller and
  parameters (F4); periodic review of who has access to the connection reference.
- A signed token between flow and procedure or per-user `EXECUTE AS` are **not** ready-made solutions
  with a shared account; treat them as a project of their own `[unverified]`.

**One identity column, normalized.** The column the app uses in `LookUp(... = Lower(User().Email))`,
the one the resolution procedure uses and the one the flow sends must be the **same**, normalized
(`LOWER(LTRIM(RTRIM()))`) at load. Divergence: the app finds the user, the flow does not, and every
write comes back "no permission". A one-minute test with two real users before the first deploy
(`deploy-and-dba.md`).

## 6. Injection and leaks through errors

- **Dynamic SQL by concatenation** is potential injection: `lint-procedure.py` reports `P009`
  (`EXEC (@sql)` and `sp_executesql` with `+`). Use `sp_executesql` with parameters and `QUOTENAME`
  for object names. Controlled internal metadata (load script) can be waived with `-- lint-ok P009`
  **and one sentence saying why**.
- A procedure parameter never becomes a column or table name without an allow list.
- `ERROR_MESSAGE()` in the return leaks the schema to the user: let the error bubble up (`THROW`) and
  let the flow build the generic sentence. The flow's `Catch` is mandatory.
- Connection string, password and user do **not** go in the repository or in the flow's literal
  `CONFIG` (environment variable + connection reference, F5).
- Migration artifacts contain real data (names, e-mails): they stay out of the repository, with
  `.gitignore`, and are deleted after the load (`data-migration.md`).
- Minimum scope for a load operation: **temporary**, dedicated `db_owner` on the database, never for
  the connector account.

## 7. Verification queries

Queries (a), (a2), (b) and (c) **come back empty** when all is right; (d) is a read-through check.
Run them after each deploy wave and keep the output.

```sql
-- (a) the connector account has no DML
SELECT p.permission_name, p.class_desc, p.major_id,
       CASE WHEN p.class_desc = 'OBJECT_OR_COLUMN' THEN OBJECT_NAME(p.major_id) END AS Objeto
  FROM sys.database_permissions AS p
  JOIN sys.database_principals  AS d ON d.principal_id = p.grantee_principal_id
 WHERE d.name = '<conta_do_conector>'
   AND p.permission_name IN ('INSERT', 'UPDATE', 'DELETE');

-- (a2) the connector account is not in a role with DML (query (a) only reads direct permission)
SELECT r.name AS Papel, m.name AS Membro
  FROM sys.database_role_members AS rm
  JOIN sys.database_principals   AS r ON r.principal_id = rm.role_principal_id
  JOIN sys.database_principals   AS m ON m.principal_id = rm.member_principal_id
 WHERE m.name = '<conta_do_conector>'
   AND r.name IN ('db_datawriter', 'db_owner', 'db_ddladmin');

-- (b) SET NOCOUNT ON in every procedure and every trigger of the project
SELECT o.name AS Objeto_Sem_NoCount, o.type_desc
  FROM sys.sql_modules AS m
  JOIN sys.objects     AS o ON o.object_id = m.object_id
 WHERE o.type IN ('P', 'TR')
   AND o.name LIKE '%APP[_]%'
   AND m.definition NOT LIKE '%SET NOCOUNT ON%';

-- (c) write procedures with dynamic SQL (review one by one)
SELECT o.name AS Procedure_Com_Sql_Dinamico
  FROM sys.sql_modules AS m
  JOIN sys.objects     AS o ON o.object_id = m.object_id
 WHERE o.type = 'P'
   AND o.name LIKE '%APP[_]%'
   AND (m.definition LIKE '%sp[_]executesql%' OR m.definition LIKE '%EXEC (@%' OR m.definition LIKE '%EXEC(@%');

-- (d) who has EXECUTE on the schema (confirm only the app account is in the list)
SELECT d.name AS Principal, p.permission_name, p.state_desc
  FROM sys.database_permissions AS p
  JOIN sys.database_principals  AS d ON d.principal_id = p.grantee_principal_id
 WHERE p.class_desc = 'SCHEMA'
   AND p.permission_name = 'EXECUTE';
```

What `lint-procedure.py` covers **in the repository** (before deploy) and what only these queries
cover **in the database** (after): the lint cannot see what the DBA changed by hand in production;
query (b) can. Use both.

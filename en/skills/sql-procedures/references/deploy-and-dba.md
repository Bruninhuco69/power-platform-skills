# Deploy and handoff to the DBA

How to assemble the package the DBA (whoever has permission on the database) runs, in what order, with
what environment proofs, and what to expect once the database is frozen in production. Request DDL
with `assets/dba-ddl-request-template.md`.

## Contents

1. [Package principles](#1-package-principles)
2. [Execution order](#2-execution-order)
3. [Environment proofs](#3-environment-proofs)
4. [Before replacing what already exists](#4-before-replacing-what-already-exists)
5. [Validate without executing](#5-validate-without-executing)
6. [After the freeze](#6-after-the-freeze)
7. [As-built names and what not to regenerate](#7-as-built-names-and-what-not-to-regenerate)
8. [Final check](#8-final-check)

---

## 1. Package principles

- **Numbered, idempotent scripts** (`CREATE OR ALTER`, `IF NOT EXISTS`); the DBA can rerun them
  without fear.
- **DDL is not extracted automatically.** A DDL document has *probes*, mutually exclusive
  alternatives, a deliberately commented-out `DROP COLUMN` and unanswered questions: extracting it
  would produce a script that runs and destroys something that was right. Assemble the DDL **by
  hand**, section by section, and deliver the procedures (which are `CREATE OR ALTER`, safe)
  separately.
- **A `.sql` generated from the source** (the contract in `.md`) carries "generated, do not edit" and
  the origin in its header. Fixes go to the source (P3).
- **One letter to the DBA** (`_READ-ME-FIRST`): what is not in the folder and why, the order, the proofs
  that stop the plan, what is on *hold*, the questions only they can answer.
- **Nothing was compiled** is a statement the package has to make when it is true: with no SQL Server
  instance at hand, all that is left is to ask the DBA for `PARSEONLY`. Have a DEV instance (or a
  container) to compile **before** sending.
- Each procedure states the minimum SQL Server version it requires (`OPENJSON`: 2016,
  `COMPATIBILITY_LEVEL >= 130`; `STRING_AGG`: 2017, `ProductMajorVersion >= 14`;
  `CREATE OR ALTER`: 2016 SP1).

## 2. Execution order

| # | Item | Note |
|--:|---|---|
| 1 | Prerequisite DDL: PKs, `Flg_*` as `BIT NOT NULL DEFAULT 0`, computed columns, unique indexes, FKs, `Dt_Alteracao` triggers | by hand; each block with the query that proves the effect |
| 2 | **Environment proofs** (§3) | run **before** the procedures; the ones that fail **stop the plan** |
| 3 | Read function and supporting indexes | the function **before** the procedures that call it |
| 4 | Caller resolution procedure | unblocks the trunk of every flow |
| 5 | Write procedures, **per wave** (user → main entity → dependent records → report) | the count one **before** the export one |
| 6 | Load normalization (`LOWER`/`TRIM` of identity, codes without padding, vocabulary) | only this script cleans what is already in the table |
| 7 | `GRANT EXECUTE` and `REVOKE` of DML (`security-and-permissions.md` §2) | **last** |
| 8 | Final check (§8) | paste the output into `AS-BUILT-NAMES` |

Mark in the package what is on **HOLD**: the object that depends on an unanswered business question
(e.g. "can a user without an e-mail exist?"). The rest goes up without it.

## 3. Environment proofs

Four proofs. Bring the answer from the **real** environment, not from what is assumed about it.

**3.1 Version and compatibility level** (for `OPENJSON` and `STRING_AGG`):

```sql
SELECT SERVERPROPERTY('ProductMajorVersion') AS Versao_Major,   -- >= 13 (OPENJSON), >= 14 (STRING_AGG)
       compatibility_level                   AS Nivel,          -- >= 130
       DB_NAME()                             AS Banco
  FROM sys.databases
 WHERE name = DB_NAME();
```

If the level is below 130 **and** the DBA refuses to raise it, JSON parameters die and the way out is
a signature with dozens of scalar parameters: it changes the signature **and** the flow. Stop and
report. (`OPENJSON` only exists at level 130+:
https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql.)

**3.2 `OUTPUT ... INTO` on a table with an active trigger** (stop condition: without this, the
procedures that chain writes have no valid body). The documentation already answers (the `INTO` form
is the supported one), but **prove it in your database** with the real trigger active, in DEV:

```sql
DECLARE @tv TABLE (Id_Pedido INT NOT NULL);

UPDATE dbo.APP_Pedido
   SET Nom_Abvd_Unidade = Nom_Abvd_Unidade      -- deliberate no-op
OUTPUT INSERTED.Id_Pedido INTO @tv (Id_Pedido)
 WHERE Id_Pedido = <id existente>;

SELECT Id_Pedido FROM @tv;
```

Gate: 1 row in `@tv`, no error and **a single** result set. Any "target table of the OUTPUT INTO
clause cannot have any enabled triggers" error or two result sets: stop.

**3.3 Does the app's identity match the database column?** If not, the resolution procedure returns
zero rows and the flow denies every write in the system. In the app, `User().Email` of two real
users; in the database:

```sql
SELECT TOP (5) Id_Usuario, Email_Usuario, Upn_Entra, Flg_Situacao
  FROM dbo.APP_Usuario
 ORDER BY Id_Usuario;

-- a LEFT space is not protected by any collation; it must come back empty
SELECT Id_Usuario, '[' + Email_Usuario + ']' AS Email_Com_Delimitador
  FROM dbo.APP_Usuario
 WHERE Email_Usuario <> LTRIM(RTRIM(Email_Usuario));
```

`User().Email` is usually equal to the UPN, **but not in every tenant**: compare the two values.

**3.4 Collation, isolation and recursive triggers:**

```sql
SELECT DATABASEPROPERTYEX(DB_NAME(), 'Collation') AS Collation_Banco,
       is_read_committed_snapshot_on              AS Rcsi,
       is_recursive_triggers_on                   AS Triggers_Recursivos   -- must be 0
  FROM sys.databases
 WHERE name = DB_NAME();
```

- A `_CS_AS` collation breaks re-entry gates (`<> N'encerrado'` does not block `'Encerrado'`) and
  identity guards: record what the database has.
- `RCSI` on: a `SELECT` without a hint does **not** protect a decision; `UPDATE`-as-predicate is still
  correct (`procedure-standard.md` §8).
- `Triggers_Recursivos` at `1`: the `Dt_Alteracao` trigger fires itself inside the transaction.

## 4. Before replacing what already exists

`CREATE OR ALTER` **replaces** a procedure in use, it does not create one alongside. If a previous
version exists, the signatures may have changed. Before running anything, **save what is there**:

```sql
-- 1) what already exists
SELECT o.name, o.type_desc, o.create_date, o.modify_date
  FROM sys.objects AS o
 WHERE o.name LIKE 'usp[_]APP[_]%' OR o.name LIKE 'tvf[_]APP[_]%';

-- 2) the way back: keep the output BEFORE the first CREATE OR ALTER
SELECT OBJECT_NAME(m.object_id) AS objeto, m.definition
  FROM sys.sql_modules AS m
 WHERE OBJECT_NAME(m.object_id) LIKE 'usp[_]APP[_]%'
    OR OBJECT_NAME(m.object_id) LIKE 'tvf[_]APP[_]%';
```

Swap the pattern for the real names. A **new** object (a function that does not exist) is a different
conversation from **altering** an existing one; the request says which is which.

## 5. Validate without executing

Syntax, without creating anything:

```sql
SET PARSEONLY ON;
GO
-- paste the content of each .sql here, one at a time
GO
SET PARSEONLY OFF;
GO
```

`PARSEONLY` validates **syntax** and does not resolve names. To validate the columns too, use
`SET NOEXEC ON` after the step 1 DDL is applied. Neither replaces compiling on a DEV instance.

In the repository, before sending: `python <skill-folder>/scripts/lint-procedure.py <folder>` (zero
errors) and the divergence check in `proc-flow-contract.md` §4.

## 6. After the freeze

In production, the DBA usually freezes the database after Go Live: "every fix has to fit in a screen
or flow". Learn the right question **before** proposing any DDL:

| Object | Usually accepted? | Criterion |
|---|---|---|
| **Computed** column (`Ref_*`, counter, derived status) | **yes** | stores no data of its own |
| New table | no | stores data of its own |
| New column that **stores** data | no | stores data of its own |
| New view | no | new object |
| Signature change on an existing procedure | no | breaks the flow already pasted |
| Supporting index | depends; ask with the plan proof | write-side maintenance cost |
| New procedure replacing via `CREATE OR ALTER` | conversation with the DBA | new object × alteration |

`[verified: reference project]` for the first row (the computed column was accepted after the freeze).
**The test is "does the object store its own data?", not "is it DDL?".**

Strategy: plan the schema **before** the first deploy; ask in one go for everything that may be
needed (`Ref_*` columns, indexes, FKs); and, for each post-freeze fix, first ask whether it fits in a
screen or flow. When you need a new object, open a request with the measurable justification and the
outcome the screen/flow would have without it (the DBA refuses more easily what shows no avoided
cost).

## 7. As-built names and what not to regenerate

- Before assembling any flow call, **read the real name** from the environment:

  ```sql
  SELECT s.name AS Schema_, p.name AS Procedure_, p.create_date, p.modify_date
    FROM sys.procedures AS p
    JOIN sys.schemas    AS s ON s.schema_id = p.schema_id
   ORDER BY p.name;
  ```

  The documented pattern (`usp_<SIGLA>_<Entidade>_<Acao>`) diverged from the real name
  (`SP_<SIGLA>_<VERBO>_<OBJETO>`) in the reference project, and the real name is **not deducible by
  rule**. Record the mapping in a data block with the verification date; mark as a hypothesis
  whatever was not confirmed.
- If the toolchain **generates** flows or `.sql` from the source, the baseline already pasted and
  hand-fixed is the only environment evidence there is: the generator writes only to `dist/`, never
  over it (F6, P3). Running the generator "because the gate says so" erased real fixes in the
  reference project.
- Account permission: `GRANT EXECUTE` last, `REVOKE` of DML; recheck after each wave.

## 8. Final check

| # | Check | Expected result |
|--:|---|---|
| 1 | PKs exist on every table | query from `data-model.md` §10 empty |
| 2 | No nullable `Flg_*` | query from `data-model.md` §4 empty |
| 3 | No identity duplicates | `GROUP BY ... HAVING COUNT(*) > 1` empty |
| 4 | `RECURSIVE_TRIGGERS` | `0` |
| 5 | `SET NOCOUNT ON` in every procedure and trigger | query (b) from `security-and-permissions.md` §7 empty |
| 6 | The connector account with no DML | query (a) empty |
| 7 | `UPDATE ... OUTPUT ... INTO` with an active trigger | 1 row, one result set |
| 8 | `COMPATIBILITY_LEVEL >= 130` | number on screen |
| 9 | **Return test** of each write procedure | **1** result set · **1** row · **4** columns, **including** the zero-rows-written outcomes |

Item 9 is the one that fails silently: no functional test catches it, because the procedure *works*;
only the return goes missing. Execute each write procedure and check what the connector receives. A
data read procedure does not return the four columns: what is checked there is the column list.

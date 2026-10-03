# DDL request to the DBA · <project> · <YYYY-MM-DD>

> Template. One request per set of related changes. Fill it in with what the **real environment**
> showed (pasted query), not with what the plan assumes. Database frozen in production? Read section 2
> before asking for anything.
>
> How to deliver the package: `sql-procedures/references/deploy-and-dba.md`.

| | |
|---|---|
| Requester | `<team name, not the person>` |
| Database / instance | `<database>` on `<server>\<instance>` (in the real request; **not** in this repository) |
| Environment | DEV / HML / PRD |
| Database frozen? | yes, since `<date>` / no |
| Deadline and impact of not having it | `<when it is needed and what breaks without it>` |

## 1. Summary in one table

| # | Object | Type | New or alters? | Stores its own data? | Why the app needs it | Alternative without the DBA |
|--:|---|---|---|---|---|---|
| 1 | `dbo.<SIGLA>_<Entidade>.Ref_<Dt>` | `PERSISTED` computed column | alters table | **no** | date filter does not delegate behind a gateway | filter on the client: wrong answer above the cap |
| 2 | `dbo.<SIGLA>_<Entidade>.Ref_Contador` | computed column | alters table | **no** | `Sum` delegates, `CountRows` does not | `2,000+` cap on screen |
| 3 | `IX_<...>` | index | new | no (structure) | backs the `HOLDLOCK` and the scope | table lock / scan |
| 4 | `FK_<...>` | FK | alters table | no | prevents an orphan record | phantom child record saved successfully |

## 2. Criterion

On a frozen database, what is usually accepted is what **does not store its own data** (computed
column); supporting indexes and FKs depend on the DBA (justify with the plan proof or the measured
orphan); what is usually refused is a new table, a column that stores data, a new view and a
signature change on an existing procedure. For each item, the "Stores its own data?" column in
section 1 answers the DBA's question before they ask it.

## 3. Current state of the environment

Result of the queries **run by the requester** (or by the DBA, if the requester has no access):

```sql
SELECT SERVERPROPERTY('ProductMajorVersion') AS Versao_Major,
       compatibility_level                   AS Nivel,
       DATABASEPROPERTYEX(DB_NAME(), 'Collation') AS Collation_Banco,
       is_read_committed_snapshot_on         AS Rcsi,
       is_recursive_triggers_on              AS Triggers_Recursivos
  FROM sys.databases
 WHERE name = DB_NAME();
```

| Item | Value found | Required |
|---|---|---|
| Major version | `<n>` | `>= 13` if using `OPENJSON` |
| `COMPATIBILITY_LEVEL` | `<n>` | `>= 130` if using `OPENJSON` |
| Collation | `<name>` | `_CI_AI` assumed in several gates: **confirm** |
| `RCSI` | `<0/1>` | informational |
| `RECURSIVE_TRIGGERS` | `<0/1>` | `0` |

## 3.1 What already exists

```sql
SELECT o.name, o.type_desc, o.create_date, o.modify_date
  FROM sys.objects AS o
 WHERE o.name LIKE '<prefixo>%';
```

Paste the output. For each procedure that will be **replaced** by `CREATE OR ALTER`, save the current
definition first (`sys.sql_modules`) and say whether the signature changes.

## 4. DDL requested

One block per item, idempotent, with the query that proves the effect right below it.

```sql
-- Item 1: day number for date filter (derived; stores no data)
ALTER TABLE dbo.<SIGLA>_<Entidade>
    ADD Ref_<Dt> AS (DATEDIFF(day, 0, <Dt>)) PERSISTED;
GO

-- proof: must return 0 rows (the computed column matches the manual derivation)
SELECT COUNT_BIG(*) AS Divergentes
  FROM dbo.<SIGLA>_<Entidade>
 WHERE Ref_<Dt> <> DATEDIFF(day, 0, <Dt>);
GO
```

Replace `<...>` with the real names **before** sending. A request with placeholders is not a request.

## 5. Risk and window

| Item | Risk | Suggested window | Rollback |
|--:|---|---|---|
| 1 | `ALTER TABLE ... ADD ... PERSISTED` writes the column on every row; locks the table during the operation (cost proportional to volume: `<n rows>`) | `<outside business hours>` | `ALTER TABLE ... DROP COLUMN Ref_<Dt>` (and the index first) |
| 3 | index maintenance cost on write | same | `DROP INDEX` |

## 6. What this request does **not** ask for

List what was considered and left out (new table, view, signature change) and the screen or flow
alternative the project adopted instead. This saves the DBA from having to guess what you accepted
losing.

## 7. Questions only the DBA can answer

| # | Question | Blocks |
|--:|---|---|
| 1 | Is raising `COMPATIBILITY_LEVEL` to `>= 130` accepted? | JSON parameters, read functions |
| 2 | Collation of the database and of the project's tables? | re-entry gates and identity guards |
| 3 | `<business or environment question>` | `<object on hold>` |

## 8. Check after applying

Run and paste the output into `AS-BUILT-NAMES` (`deploy-and-dba.md` §8): PKs exist; no nullable `Flg_*`;
no identity duplicates; `RECURSIVE_TRIGGERS = 0`; `SET NOCOUNT ON` in every procedure and trigger;
connector account without DML; return of each write procedure with 1 result set, 1 row, 4 columns.

# Data migration to SQL Server

Playbook for a **one-time initial load** from a legacy source (spreadsheet, local database, another
database) into the SQL Server behind a Power Apps app. The method is target-agnostic: extract → staging →
validate → map → load → reconcile, with the name and vocabulary mapping kept isolated. The code comes
from a reference project; **compile every script on a DEV instance before delivering it**:
the snippets below follow the project's pattern, but this skill did not run them
`[unverified: run on an instance]`.

## Contents

1. [Scope and design](#1-scope-and-design)
2. [The steps](#2-the-steps)
3. [Staging, all NVARCHAR](#3-staging-all-nvarchar)
4. [Metadata-driven validation](#4-metadata-driven-validation)
5. [Guard and action in the same batch](#5-guard-and-action-in-the-same-batch)
6. [The load: trigger, IDENTITY and transaction](#6-the-load-trigger-identity-and-transaction)
7. [Reseed and reconciliation](#7-reseed-and-reconciliation)
8. [Rollback](#8-rollback)
9. [Generated files and encoding](#9-generated-files-and-encoding)
10. [Normalizing what already exists](#10-normalizing-what-already-exists)
11. [Load security](#11-load-security)
12. [Lessons](#12-lessons)

---

## 1. Scope and design

- A **one-time** load, not an incremental sync. The typical volume of a departmental app (thousands of
  rows) runs in seconds; do not optimize.
- **Staging before the target.** Moving the data (`stg`, all text) is separate from converting and
  validating it (typed target). If it fails, you know which of the two halves.
- **Validate everything at once**: the validation phase writes the **complete list** of problems to a
  table and only then aborts, instead of stopping at the first violated `CHECK`.
- **All-or-nothing generation**: if a generator fails midway, delete what it already wrote. An
  incomplete package on disk looks exactly like a finished one.
- The source is opened **read-only**; secrets (password hashes) stay out of the artifacts by
  default.
- **Map against the real environment**, not the plan. The reference project's package was
  written for a proposed schema; the DBA built another (`dbo`, corporate prefixes), and the bridge
  between the two was not documented. The logic is 100% reusable; what changes is the naming layer
  (`AS-BUILT-NAMES`, N1).

## 2. The steps

Numbering from the reference package; each script checks the prerequisite and aborts with a specific
message if something is out of order.

| Step | File | Function | Safeguard |
|---|---|---|---|
| 01 | `01_staging_ddl.sql` | `stg` schema, everything `NVARCHAR` | `DENY` read/write to `db_datareader`/`db_datawriter`; step 30 rechecks |
| 02 | `02_staging_dados.sql` (generated) | `INSERT` of the source data, in pure ASCII | immune to a wrong codepage; `03_bulk_insert_alternativo.sql` as plan B |
| 04 | `04_metadados_validacao.sql` (generated) | metadata tables: type, vocabulary, length, FK, format, required | same Python definition as the pre-load validation; no SQL stored as data |
| 10 | `10_pre_carga_ajustes.sql` | removes seed rows that collide with the source IDs; collation round-trip | refuses if any record already references the seed |
| 20 | `20_carga.sql` | full validation → disables trigger → load in a transaction → re-enables | guard and action in the same batch |
| 21 | `21_reseed_identity.sql` (generated) | repositions `IDENTITY` | from the source counter, not `MAX(id)` |
| 30 | `30_validacao_pos_carga.sql` | trusted constraints, trigger back on, `DENY` in place | every row `OK` |
| 31 | `31_reconciliacao.sql` (generated) | count per table, `MIN/MAX` of dates, accent canaries, manifest | everything must be `OK` |
| 90 | `90_rollback.sql` | returns the target to the post-DDL state; staging stays | can reload from step 10 |

`MANIFESTO.json` and `RELATORIO_PRE_CARGA.md` carry counts, `SHA-256` per table, findings and the
`LIBERADO`/`BLOQUEADO` verdict. The generator returns exit `0` (no blockers), `1` (there are blockers,
do not load), `2` (execution error).

**Business decisions** that change the result (the region of a unit that differs between source and
seed, dropping a classification the code does not read, local login × Entra) are raised
**before** running, with a marked default and the decision owner. None belongs to the DBA.

## 3. Staging, all NVARCHAR

Columns identical to the source's, **all** text, **zero** constraints: any restriction would abort the
transport before the validation could report the problem. Also keep what the target does not carry
(dropping it is a business decision; the data stays available).

```sql
IF SCHEMA_ID('stg') IS NULL
    EXEC (N'CREATE SCHEMA stg');
GO

DROP TABLE IF EXISTS stg.itens;
DROP TABLE IF EXISTS stg.erros_validacao;
DROP TABLE IF EXISTS stg.regra_coluna;
GO

CREATE TABLE stg.itens (
    id           NVARCHAR(400) NULL,
    protocolo    NVARCHAR(400) NULL,
    status_item  NVARCHAR(400) NULL,
    unidade      NVARCHAR(400) NULL,
    criado_em    NVARCHAR(400) NULL
);

CREATE TABLE stg.erros_validacao (
    tabela   NVARCHAR(128)  NOT NULL,
    regra    NVARCHAR(200)  NOT NULL,
    chave    NVARCHAR(400)  NULL,
    detalhe  NVARCHAR(1000) NULL
);

-- validation metadata: one row per typed column
CREATE TABLE stg.regra_coluna (
    tabela  NVARCHAR(128) NOT NULL,
    coluna  NVARCHAR(128) NOT NULL,
    tipo    NVARCHAR(30)  NOT NULL,     -- texto | int | date | datetime2 | bit
    limite  INT           NULL
);
GO
```

## 4. Metadata-driven validation

The validation phases (type, vocabulary, length, FK, format, required) come from the metadata tables
that step 04 populates, **generated from the same definition** the pre-load validation uses. There is
no hand-kept copy of the vocabulary to drift out of sync. The required check covers every `NOT NULL`
column of the target, instead of a hand-written list.

Details that bite:

- `TRY_CONVERT` returning `NULL` for a **non-null** value means the real conversion would fail.
- **Length in UTF-16 units**, the way `NVARCHAR(n)` counts: use `DATALENGTH(col) / 2`, not `LEN()`,
  which drops trailing spaces (51 characters ending in a space would pass as 50 and the `INSERT`
  would truncate).
- Every check filters `IS NOT NULL` before comparing (`NULL NOT LIKE pattern` is `NULL`); the
  required check is a **phase of its own**, otherwise a null column passes the whole validation and
  blows up at the `INSERT` with a raw error.
- Vocabulary is compared **with accents** (accent-sensitive collation): a value that arrived with a
  wrong codepage does not match and shows up as an error.
- `ANSI_WARNINGS ON` **explicit** in the load scripts: with `OFF` SQL Server silently truncates a
  string that is too long, instead of failing.

A generated phase (type conversion validation). The dynamic SQL uses only **column names coming from
internal metadata, passed through `QUOTENAME`**, never a source value; that is why `lint-procedure.py`
(P009) is waived with a justification:

```sql
SET ANSI_WARNINGS ON;
GO

DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql = @sql
    + N'INSERT INTO stg.erros_validacao (tabela, regra, chave, detalhe) '
    + N'SELECT ' + QUOTENAME(r.tabela, '''') + N', '
    + N'N''tipo/' + REPLACE(r.coluna, '''', '''''') + N' -> ' + r.tipo + N''', t.id, '
    + N'CONCAT(N''unconvertible value: ['', t.' + QUOTENAME(r.coluna) + N', N'']'') '
    + N'FROM stg.' + QUOTENAME(r.tabela) + N' AS t '
    + N'WHERE t.' + QUOTENAME(r.coluna) + N' IS NOT NULL AND TRY_CONVERT('
    + CASE r.tipo
          WHEN 'date'      THEN N'date, t.'         + QUOTENAME(r.coluna) + N', 23'
          WHEN 'datetime2' THEN N'datetime2(0), t.' + QUOTENAME(r.coluna) + N', 120'
          WHEN 'int'       THEN N'int, t.'          + QUOTENAME(r.coluna)
          ELSE N'bit, t.' + QUOTENAME(r.coluna)
      END
    + N') IS NULL;' + CHAR(10)
  FROM stg.regra_coluna AS r
 WHERE r.tipo <> 'texto';

EXEC sp_executesql @sql;   -- lint-ok P009: internal metadata names via QUOTENAME, no external value
GO
```

## 5. Guard and action in the same batch

**An error in one batch does not stop the following batches**, neither in SSMS nor in `sqlcmd` without
`-b`. If the validation exit gate is in one batch and the load in another, a `THROW` there aborts that
batch and the load runs **anyway**, with rejected data. Rule:

- The validation exit gate, the `DISABLE TRIGGER` and all the `INSERT`s go in **a single batch**,
  with the guards **repeated** (if someone ignored the previous batch's error, this one aborts before
  touching the target).
- Run from the command line with `sqlcmd -b -f 65001`: `-b` aborts on the first error; `-f 65001` rules
  out any codepage doubt.

## 6. The load: trigger, IDENTITY and transaction

The `Dt_Alteracao` trigger (or any update-date trigger) **overwrites the real date** of each loaded
row with the migration date, **with no error, no warning, nothing in the log**. It is the only step
whose omission causes silent data loss. Disable it for the load and re-enable it **outside** the
transaction:

```sql
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

IF EXISTS (SELECT 1 FROM stg.erros_validacao)
    THROW 50023, 'Validation failed. Nothing was loaded. See stg.erros_validacao.', 1;

IF EXISTS (SELECT 1 FROM dbo.APP_Pedido)
    THROW 50025, 'Target already has data: initial load. Run the rollback before repeating.', 1;

ALTER TABLE dbo.APP_Pedido DISABLE TRIGGER TR_APP_Pedido_Dt_Alteracao;

BEGIN TRANSACTION;

SET IDENTITY_INSERT dbo.APP_Pedido ON;

INSERT INTO dbo.APP_Pedido
      (Id_Pedido, Nr_Protocolo, Des_Status, Nom_Abvd_Unidade, Flg_Situacao, Dt_Inclusao)
SELECT CAST(i.id AS INT), i.protocolo, i.status_item, i.unidade, 1,
       CONVERT(datetime2(3), i.criado_em, 120)
  FROM stg.itens AS i
 ORDER BY CAST(i.id AS INT);

SET IDENTITY_INSERT dbo.APP_Pedido OFF;

COMMIT TRANSACTION;
GO

-- own batch and WITHOUT an error guard, on purpose: if the load aborted midway, the trigger stayed
-- disabled, and leaving it that way would silence the rule in production. Idempotent.
IF EXISTS (SELECT 1 FROM sys.triggers
            WHERE name = N'TR_APP_Pedido_Dt_Alteracao' AND is_disabled = 1)
    ALTER TABLE dbo.APP_Pedido ENABLE TRIGGER TR_APP_Pedido_Dt_Alteracao;
GO
```

- `IDENTITY_INSERT` when other tables reference the id (audit trail, child records): losing the id
  breaks the audit trail. Only one per session, and **always turned off** at the end.
- **Explicit** conversions (`CONVERT(..., 120)` for datetime, `23` for date, `CAST` for
  uniqueidentifier, `CASE` for bit): no implicit text-to-date conversion.
- Are the source dates already in UTC? Confirm and document; no time zone conversion in the load.
- Target seed rows that **collide with the source IDs** (e.g. a domain table seeded with a few rows,
  the source with more, in a different order) would silently reassign the data. Remove the seed with a
  guard, load with `IDENTITY_INSERT`.
- **Collation and accents:** a `VARCHAR` column with accented vocabulary, in a collation with an
  incompatible codepage, stores `?` and the `CHECK` accepts it. Step 10 does the
  `NVARCHAR → VARCHAR → NVARCHAR` round-trip of each vocabulary value with the **real** collation and
  aborts if any value does not come back identical.

## 7. Reseed and reconciliation

**Reseed from the source counter, not from `MAX(id)`.** If the source deletes ids (a sync that
removes rows), the counter is ahead of the `MAX`; recycling the ids would make history rows point to
another record:

```sql
DBCC CHECKIDENT ('dbo.APP_Pedido', RESEED, 1305) WITH NO_INFOMSGS;
```

(`1305` is the counter value of **your** source; the generator writes it in step 21.)

**Reconciliation** (step 31): everything must be `OK`.

```sql
SELECT 'APP_Pedido'                             AS Tabela,
       (SELECT COUNT_BIG(*) FROM dbo.APP_Pedido) AS No_Destino,
       1200                                           AS Na_Origem,   -- number from the MANIFESTO
       CASE WHEN (SELECT COUNT_BIG(*) FROM dbo.APP_Pedido) = 1200 THEN 'OK' ELSE 'FALHA' END AS Situacao;

-- real dates preserved: MIN/MAX against the source values
SELECT MIN(Dt_Inclusao) AS Menor, MAX(Dt_Inclusao) AS Maior FROM dbo.APP_Pedido;

-- accent canary: one per accented value actually present
SELECT COUNT_BIG(*) AS Canario_Acento
  FROM dbo.APP_Pedido
 WHERE Des_Status = N'Em An' + NCHAR(0x00E1) + N'lise';
```

Step 31 carries, commented out, the manifest's `SHA-256` values: reproduce them at any time with the
generator's checksum command; if they match, the source has not changed since generation.

Step 30, before it: **trusted** constraints (`is_not_trusted = 0`; a load with `NOCHECK` leaves them
untrusted), the trigger back on (`is_disabled = 0`) and the `DENY` on the `stg` schema in place.

## 8. Rollback

`90_rollback.sql` returns the target to the state right after the DDL: it deletes in **reverse FK
order**, in a transaction, does a `RESEED` to zero and confirms the trigger is enabled. It does **not**
drop the `stg` schema: it is the documentary proof of what came from the source and lets you reload
without repeating step 02 (there is a final, commented-out section to drop it at cutover).

Caution: if the system is already in use, the rollback deletes data created in the target, not only
the migrated data. The script shows the current volume before deleting and tells you to **stop** if
any date later than the migration's exists.

## 9. Generated files and encoding

- **Pure ASCII.** Accented vocabulary (`Em Análise`) compared by a `CHECK` against an exact literal
  breaks if the `.sql` is read with the wrong codepage (`sqlcmd` without `-f 65001`, a legacy editor,
  a file that went through e-mail): `Em Análise` becomes `Em AnÃ¡lise`. The generator emits every
  non-ASCII character as `NCHAR(0xXXXX)` (as in the canary above), and the files are identical in any
  tool.
- The generated `INSERT` is the main path; `BULK INSERT` stays as the alternative: it requires a path
  reachable by the SQL Server **service**, the `ADMINISTER BULK OPERATIONS` permission and the right
  codepage.
- A text literal escapes the apostrophe (`'` → `''`): without that the literal closes too early and
  the rest of the value becomes SQL. Cover this literal generator with tests out of proportion to its
  size: it is where an error does not show up as an error.
- Validate at the source: line break, TAB, quotes, NUL byte and empty string (indistinguishable from
  `NULL` in the CSV). `NCHAR(0)` nulls the whole field.

## 10. Normalizing what already exists

The procedure **does not clean existing data**: it only writes what it receives. A dirty load (mixed-case
e-mail, padded abbreviation, vocabulary with a different accent, swapped fields) is cleaned by a
**normalization script of its own**, before creating the unique index and before opening the app.
Normalizing in the procedure hides the problem: the screen reads the table directly and stays broken.
Typical list: `LOWER(LTRIM(RTRIM()))` of identity; `LTRIM(RTRIM())` of abbreviations; vocabularies;
check for swapped fields.
See `data-model.md` §8.

Do not infer type or domain from test rows in the load (`Teste1`), and do not promote them to
production.

## 11. Load security

- The scripts use `CREATE SCHEMA`, `IDENTITY_INSERT`, `DISABLE TRIGGER`, `DBCC CHECKIDENT` and
  `ALTER TABLE`: in practice, `db_owner` **of the database**. Treat it as a session: a dedicated,
  temporary DBA login; **never** for the app's service account (it needs `EXECUTE`, `SELECT`, and
  nothing else). After step 31 closes `OK`, disable the login.
- The artifacts **contain real data**. `saida/` goes in `.gitignore` and is **deleted** after the load;
  regenerating is one command. Hand them to the DBA through an internal channel, not by e-mail.
- Password hashes and other sensitive data stay out by default and only come out with an explicit
  flag.

## 12. Lessons

1. Load and DDL for the **real target** first; a script written against the plan becomes rework.
2. Validate **vocabulary and accents** against the real target, not against the plan.
3. Mark in the package which steps the DBA runs and which the team runs (and with what permission).
4. What the target does not carry stays in `stg` and in the CSVs: "we decided not to load it" is not
   "we lost it".
5. Reconciliation without the manifest number reconciles nothing: the document that states a count
   carries the command that measures it (P5).

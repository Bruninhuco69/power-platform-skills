# Data model

Table and column conventions for a SQL Server backend consumed by Power Apps and procedures.
The **real name** of everything comes from the environment (N1: `AS-BUILT-NAMES`); what is here is the
standard to ask the DBA for and what to check in what already exists. Dataverse tables belong to the
`dataverse` skill.

## Contents

1. [Column prefixes](#1-column-prefixes)
2. [Keys and what the connector requires](#2-keys-and-what-the-connector-requires)
3. [Audit: Dt_Inclusao and Dt_Alteracao](#3-audit-dt_inclusao-and-dt_alteracao)
4. [Flags: BIT NOT NULL DEFAULT 0](#4-flags-bit-not-null-default-0)
5. [Text: type, collation and padding](#5-text-type-collation-and-padding)
6. [Role and user: permission flags](#6-role-and-user-permission-flags)
7. [Filtered unique indexes and FKs](#7-filtered-unique-indexes-and-fks)
8. [Vocabularies](#8-vocabularies)
9. [Spelling is not fixed](#9-spelling-is-not-fixed)
10. [What to check in what already exists](#10-what-to-check-in-what-already-exists)

---

## 1. Column prefixes

Corporate standard observed in the reference project. Adopt your DBA's; the important thing is **one**,
documented in `AS-BUILT-NAMES`.

| Prefix | Use | Example |
|---|---|---|
| `Id_` | integer PK or FK. `Id_Legado*` holds the source id in the migration | `Id_Pedido` |
| `Nr_` | business number (fixed-format text when it is a code) | `Nr_Protocolo` |
| `Nom_` | name. `Nom_Abvd_` = abbreviation (unit) | `Nom_Abvd_Unidade` |
| `Des_` | description, status, vocabulary item | `Des_Status` |
| `Tp_` | type | `Tp_Evento` |
| `Flg_` | yes/no indicator, `BIT NOT NULL DEFAULT 0` | `Flg_Situacao` |
| `Dt_` | date/time, in UTC | `Dt_Inclusao` |
| `Nv_` | level | `Nv_Perfil` |
| `Cod_` | corporate table code | `Cod_Grupo` |
| `Ref_` | **computed column** that supports a filter (holds no data of its own) | `Ref_DtInclusao` |
| `Upn_`, `Email_`, `Objectid_` | identity | `Email_Usuario` |

Tables: `<SIGLA>_<Entidade>` in the singular. Inline functions: `tvf_<SIGLA>_<Entidade>_<Name>`. If the
database already has another convention, the database's wins.

## 2. Keys and what the connector requires

- **A declared PK on every table.** Without a PK, the SQL connector opens the table read-only and
  `Patch`/`Defaults` disappear `[verified: reference project]`.
- `tinyint` and `smallint` are not supported as a PK; types such as `binary`, `varbinary`, `image`,
  `rowversion`, `hierarchyid`, `sql_variant`, `xml` and spatial types are not supported.
  Source: https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview
- Type mapping for the app: numeric → Number, `char`/`varchar`/`nvarchar` → Text, `bit` →
  Boolean, dates → DateTime, `uniqueidentifier` → Guid (same source).
- The business key of a unit is the **abbreviation** when it is unique and stable; numeric codes from
  a corporate table are often **not** unique on their own (the identity is a pair). Confirm with
  `SELECT sigla, COUNT(*) ... HAVING COUNT(*) > 1` before using one as a key.
- A **real** FK in the database whenever the relationship exists. A missing FK lets you save an orphan
  record and return success; the reference project only found out in review.

## 3. Audit: Dt_Inclusao and Dt_Alteracao

| Column | Who writes it | Value |
|---|---|---|
| `Dt_Inclusao` | the procedure, on creation | the **database's** `SYSUTCDATETIME()` |
| `Dt_Alteracao` | `AFTER UPDATE` **trigger**, never a procedure | `SYSUTCDATETIME()` |
| who did it | the procedure, from `@Id_UsuarioChamador` | the caller's declaration (`security-and-permissions.md`) |

No procedure accepts an audit date **as a parameter**: the client's date is the local clock,
and one row is born hours ahead of the others. Everything in UTC; time zone conversion belongs to the
display layer. Consequence for a per-day filter: `Ref_<col>`
is the UTC day, and the `DatePicker` returns a local date (see `computed-columns-delegation.md` §2).

The table has more than one writer (procedure, load, manual fix); the column cannot depend on
everyone remembering, hence a trigger:

```sql
CREATE OR ALTER TRIGGER dbo.TR_APP_Pedido_Dt_Alteracao
ON dbo.APP_Pedido AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;   -- required: the trigger runs INSIDE the procedure's transaction
    IF NOT EXISTS (SELECT 1 FROM inserted) RETURN;

    UPDATE s
       SET Dt_Alteracao = SYSUTCDATETIME()
      FROM dbo.APP_Pedido AS s
      JOIN inserted AS i ON i.Id_Pedido = s.Id_Pedido;
END
GO
```

Cautions:

- **`SET NOCOUNT ON` in the trigger too.** Without it the inner `UPDATE`'s rowcount is added to the
  procedure's result. A silent failure, the likeliest one in the delivery.
- `RECURSIVE_TRIGGERS` must be `OFF` (the product default; a backup restore and creation scripts
  sometimes bring another value), otherwise the trigger fires itself inside the transaction.
  Proof in `deploy-and-dba.md`.
- A table with a trigger **requires `OUTPUT ... INTO`** in the procedures; `OUTPUT` without `INTO` fails.
  `INSERTED.Dt_Alteracao` in the `OUTPUT` comes out with the value **from before** the trigger: do not
  read it that way.
  Source: https://learn.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql
- A bulk load of historical data with the trigger active **overwrites** the real date: disable it
  during the load (`data-migration.md`).
- The trigger and `Dt_Alteracao` exist only where the table has `Dt_Alteracao`; do not invent one for a
  log table.

## 4. Flags: BIT NOT NULL DEFAULT 0

Every `Flg_*` column is `BIT NOT NULL` with a `DEFAULT`. Two families, with opposite defaults: the
role's **permission flag** is born `DEFAULT 0` (nobody gains permission by omission); the **security
switch in the flow's `CONFIG`** is born **on** (see `authorization-in-flow.md` §4 in `power-automate`).
Why the `NOT NULL`, in order of damage:

1. **Permission:** the flow reads the action's flag in a condition. `NULL` becomes a null value
   traveling down to the `Switch`; with authorization in the flow there is no second line of defense in
   the database.
2. **Caller resolution:** `p.Flg_Situacao = 1` with `NULL` is `UNKNOWN`: the row disappears and
   **every write of that role is denied**, silently.
3. **Typing:** with a typed parameter, an `INT` column the app treats as a boolean becomes a silent
   implicit conversion (the `Patch` that did not compile starts writing).

Migrating an existing column (order matters: `UPDATE`, `ALTER COLUMN`, `DEFAULT`):

```sql
UPDATE dbo.APP_Perfil SET Flg_Encerrar = 0 WHERE Flg_Encerrar IS NULL;
GO
ALTER TABLE dbo.APP_Perfil ALTER COLUMN Flg_Encerrar BIT NOT NULL;
GO
ALTER TABLE dbo.APP_Perfil ADD CONSTRAINT DF_APP_Perfil_Flg_Encerrar DEFAULT 0 FOR Flg_Encerrar;
GO
```

Watch for the **default that is not 0**: "active" is usually born `1` (a new record has to show up).
Confirm the column's semantics before running and note the exception in `AS-BUILT-NAMES`.

Check query (it must come back **empty**):

```sql
SELECT OBJECT_NAME(c.object_id) AS Tabela, c.name AS Coluna
  FROM sys.columns AS c
 WHERE c.name LIKE 'Flg[_]%'
   AND c.is_nullable = 1;
```

## 5. Text: type, collation and padding

- **`NVARCHAR` for text with accents.** `VARCHAR` with an incompatible codepage stores `?` in place of
  the character, with no error, and a `CHECK` may accept it because it compares after the conversion.
  The `NVARCHAR → VARCHAR → NVARCHAR` round-trip of each vocabulary value, with the database's real
  collation, proves it (`data-migration.md`).
- **Collation.** The reference project assumed `_CI_AI` in several premises and **never checked**:
  with `_CS_AS`, a `<> N'encerrado'` gate does not block `'Encerrado'` coming from the load, and the
  guard and the identity index stop matching. Ask the DBA for the collation of the database **and** of
  the tables; see `deploy-and-dba.md`. A different collation between databases breaks a `JOIN` across
  them (error 468).
- **Power Fx is case-insensitive and accent-sensitive**, and most comparisons run on the client: no
  collation fixes that. Accented vocabulary has to be **normalized at load time**.
- **`CHAR(n)` carries padding.** `CHAR(7)` with `'AAA'` stores `'AAA    '`. In SQL Server `=` ignores
  trailing blanks `[unverified: confirm with SELECT 1 WHERE 'a' = 'a ']`; in Power Fx text
  comparison is literal and does **not** match. Two ways out: `VARCHAR(n)` on the tables you
  control, and `Trim()` when loading any collection read from a `CHAR` column of a corporate table
  (never afterwards, never on the screen).
  The connector documentation recommends `varchar`/`nvarchar` over `char`/`nchar`, because `Len`
  delegates but counts SQL's padding, not Power Apps'. Source: sql-connection-overview, note 5.
- **Leading** space is not protected by any collation: normalize with `LTRIM(RTRIM())` in the
  load and in the procedure, on **both** sides of the comparison.
- An identity comparison (e-mail) is always `LOWER(LTRIM(RTRIM()))` of the parameter **and** a column
  normalized at load time, so the index is used.

## 6. Role and user: permission flags

Permission is a **flag per action** in the role table, not a role name (T8). Minimal example, used by
the code in `procedure-standard.md`:

```sql
IF OBJECT_ID(N'dbo.APP_Perfil', N'U') IS NULL
    CREATE TABLE dbo.APP_Perfil (
        Id_Perfil           INT IDENTITY(1, 1) NOT NULL CONSTRAINT PK_APP_Perfil PRIMARY KEY,
        Des_Perfil          NVARCHAR(50) NOT NULL,
        Nv_Perfil           INT          NOT NULL CONSTRAINT DF_APP_Perfil_Nv DEFAULT 0,
        Flg_Consultar       BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Consultar DEFAULT 0,
        Flg_Encerrar        BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Encerrar DEFAULT 0,
        Flg_Cancelar        BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Cancelar DEFAULT 0,
        Flg_TodasUnidades   BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Todas DEFAULT 0,
        Flg_Adm             BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Adm DEFAULT 0,
        Flg_Situacao        BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Situacao DEFAULT 0
    );
GO

IF OBJECT_ID(N'dbo.APP_Usuario', N'U') IS NULL
    CREATE TABLE dbo.APP_Usuario (
        Id_Usuario          INT IDENTITY(1, 1) NOT NULL CONSTRAINT PK_APP_Usuario PRIMARY KEY,
        Nom_Usuario         NVARCHAR(100) NOT NULL,
        Email_Usuario       NVARCHAR(100) NULL,
        Upn_Entra           NVARCHAR(100) NULL,
        Id_Perfil           INT           NOT NULL
                            CONSTRAINT FK_APP_Usuario_Perfil
                            FOREIGN KEY REFERENCES dbo.APP_Perfil (Id_Perfil),
        Nom_Abvd_Unidade    VARCHAR(3)    NULL,
        Flg_Situacao        BIT           NOT NULL CONSTRAINT DF_APP_Usuario_Situacao DEFAULT 0,
        Dt_Inclusao         DATETIME2(3)  NOT NULL,
        Dt_Alteracao        DATETIME2(3)  NULL
    );
GO
```

- **One identity column** for "who are you": the one the app uses in `LookUp(... = Lower(User().Email))`,
  the one the resolution procedure uses and the one the flow sends **must be the same**. A mismatch
  (e-mail in the app, UPN in the procedure) makes the app find the user and the flow not: every write
  comes back "no permission". `User().Email` is not always equal to the UPN; test with two real users
  before the first deploy (proof in `deploy-and-dba.md`).
- **Unit scope** as a role attribute (`Flg_TodasUnidades`) only expresses "all or one". A user
  with 3 of the dozens of units **cannot be represented**: record it as a limit or model a link table
  (see `unit-scope.md`).
- An inactive role or inactive user **authorizes nothing**, itself included; both conditions go in the
  resolution's `WHERE`.

## 7. Filtered unique indexes and FKs

```sql
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = N'UX_APP_Usuario_Email'
                 AND object_id = OBJECT_ID(N'dbo.APP_Usuario'))
    CREATE UNIQUE NONCLUSTERED INDEX UX_APP_Usuario_Email
        ON dbo.APP_Usuario (Email_Usuario)
        WHERE Email_Usuario IS NOT NULL AND Email_Usuario <> '';
GO
```

- The filter excludes `NULL` and empty **on purpose** (a user not yet provisioned), which also
  means `NULL` and `''` are **not protected**: the procedure's registration guard has to handle
  both explicitly (product decision: can a user without an e-mail exist?).
- **Normalize before creating the index** (`LOWER(LTRIM(RTRIM()))`), otherwise it fails; check for
  duplicates first (`GROUP BY ... HAVING COUNT(*) > 1`).
- The unique index backs the `UPDLOCK, HOLDLOCK` of the guards (`procedure-standard.md` §8).
- Without the index, a `LookUp` by e-mail returns "whichever row SQL hands back", with no `ORDER BY`:
  role and unit become a per-session lottery.

## 8. Vocabularies

A closed text domain (`Des_Status`, `Tp_Evento`) is a `CHECK` **or** a domain table, the DBA's choice;
what it cannot be is a vocabulary that lives only in the app. Record the canonical values in the
contract and check the load: divergent accent, case and spacing (`ANDAMENTO` × `Em Andamento`) make a
screen filter not match and a counter count zero. Normalize in the **load script**, not in the
procedure: normalizing in the procedure hides the problem and the screen, which reads the table
directly, stays broken.

A value written outside the vocabulary (e.g. an "archived" state that does not exist in the filters'
domain) is a product decision: either it enters the vocabulary and the filter, or the operation writes
another value.

## 9. Spelling is not fixed

The SQL connector is **case-sensitive** on column and table names. If the environment has
`Nom_Abvd_UNidade` in one table and `Nom_Abvd_UnidadeOrig` in another, **do not make them uniform**:
screens and flows are already written against those names, and getting it wrong is not flagged while
editing, it fails at runtime, silently. Record the real spelling per table in `AS-BUILT-NAMES` and let
the project's name lint check it.
`[verified: reference project]`

## 10. What to check in what already exists

Before writing the first procedure, run this and paste the result into `AS-BUILT-NAMES` (N1, N3):

```sql
-- columns, type, length, nullability and collation of each project table
SELECT t.name AS Tabela, c.name AS Coluna, ty.name AS Tipo, c.max_length, c.is_nullable,
       c.is_computed, c.collation_name
  FROM sys.tables AS t
  JOIN sys.columns AS c  ON c.object_id = t.object_id
  JOIN sys.types   AS ty ON ty.user_type_id = c.user_type_id
 WHERE t.name LIKE 'APP[_]%'
 ORDER BY t.name, c.column_id;

-- tables without a PK (they open read-only in the connector)
SELECT t.name AS Tabela_Sem_PK
  FROM sys.tables AS t
 WHERE NOT EXISTS (SELECT 1 FROM sys.key_constraints AS k
                    WHERE k.parent_object_id = t.object_id AND k.type = 'PK')
   AND t.name LIKE 'APP[_]%';
```

Before stating that a column **does not exist**, open the table's full schema; never a filtered
extract (N3).

# Procedure ↔ flow contract

What the procedure returns, what the flow has to do with it, and how both sides avoid drifting apart.
The **flow side** (expressions, `Switch`, `Catch`, `Response`, authorization) belongs to the
`power-automate` skill; here is what the **database** promises. Decided defaults:
`power-platform/references/default-decisions.md` (A2, C1, C2, C4).

## Contents

1. [What the procedure promises](#1-what-the-procedure-promises)
2. [How the flow reads the return](#2-how-the-flow-reads-the-return)
3. [Flow obligations](#3-flow-obligations)
4. [Divergence checklist before deploy](#4-divergence-checklist-before-deploy)
5. [JSON parameter](#5-json-parameter)
6. [A return that is not the four-column contract](#6-a-return-that-is-not-the-four-column-contract)
7. [Keeping the contract from going stale](#7-keeping-the-contract-from-going-stale)

---

## 1. What the procedure promises

| Type | Return | Who consumes it |
|---|---|---|
| Write | 1 result set, 1 row, `status`/`description`/`id`/`url`, in every outcome | the flow's `Response`, after translating the code |
| Data read | the result set **is** the data (fixed column list) | flow, which turns it into a body/file |
| Count | 4-column contract; `id` = total, text, no thousands separator | flow decision before listing/exporting |
| Caller resolution | 1 row with identity + flags, or **zero rows** | flow gate |

An infrastructure failure (deadlock, timeout, constraint violation, `THROW`) does **not** come back
as a code: the connector action fails and the flow handles it in the `Catch`. That is why the `Catch`
is mandatory.

Gateway connector limits that affect the contract
(https://learn.microsoft.com/en-us/connectors/sql/): `OUTPUT` parameters and the return value do not
come back; only the **first** result set; `ResultSets` is untyped; request up to 2 MB and response up
to 8 MB; the action times out at 110 s.

## 2. How the flow reads the return

Result set name and read path: `[verified: reference project]`

```
body('<action name>')?['ResultSets']?['Table1']?[0]?['status']
body('<action name>')?['ResultSets']?['Table1']?[0]?['description']
```

- **Zero rows** is a first-class case: `empty(body(...)?['ResultSets']?['Table1'])` is the test for
  "unknown caller".
- A `BIT` column reaches the flow as a boolean (`true`/`false`), not `1`/`0`; a condition and a
  `$filter` have to handle both `[verified: reference project]`. The exact expression belongs to the
  `power-automate` skill.
- `id` arrives as **text**, which is the type in the C1 contract.
- Unknown code → `error` naming the code (do not pass it through raw).

A computed column returned by the final `SELECT` must have a unique, non-empty name, or the connector
rejects the result set schema.

## 3. Flow obligations

The declarative procedure **checks nothing beyond what the `WHERE` requires**: it writes what it
receives. These obligations are the contract on the other side; each one has a **silent** failure mode.
Copy the list into each procedure's contract and mark the ones that apply.

| # | Obligation | If not met |
|--:|---|---|
| 1 | Resolve the caller **once**, on the trunk, and use the returned `Id_Usuario` as `@Id_UsuarioChamador`; never a value from the trigger | the caller says who they are; trail with false authorship |
| 2 | Authorize **per action**: each branch reads the flag for **that** action | a "create" flag starts granting the right to edit and close |
| 3 | Normalize, validate and derive everything before calling: zero-fill, `UPPER`/`LOWER`, trim, domain, FK, minimum lengths, scope | the procedure writes garbage without complaint |
| 4 | Send the unit **of the record**, never the one the screen is viewing | trail and child records log the wrong unit |
| 5 | Cut text at the column limit (and the JSON limit) before calling | silent truncation or an overflow error |
| 6 | Build **all** trail text and titles | migrated and new rows stop reading the same in the same column |
| 7 | Do not call when there is nothing to write (empty diff) | a useless `UPDATE` stamps `Dt_Alteracao` on every Save |
| 8 | Resolve the scope (`NULL` = all; `''` matches nothing) and **refuse** when the role does not see everything and the unit is empty | `NULL` becomes "all units", silently |
| 9 | Do not pass a semantic `NULL` through `coalesce`/generic truncation | the `NULL` becomes `''` and the report comes back empty, with no error |
| 10 | Call the **count before** listing/exporting, with the same `@Filtros` and the same scope | there is nowhere to get the total from |
| 11 | Translate the code in a `Switch` with a `default` that answers `error` naming the code | raw code in the toast |
| 12 | `Catch` listening for `Failed`, `TimedOut` and `Skipped` | the user gets a generic Power Automate error, or no response |
| 13 | Treat deadlock (1205) as transient, with a retry limit | intermittent failure under a real race |
| 14 | Bind the caller's e-mail **only** at the output of the role step, never at the trigger | the only identity invariant disappears |

## 4. Divergence checklist before deploy

Run it before handing off to the DBA and before regenerating any flow. Any difference is a bug, in the
flow or in the procedure; decide which side is right and fix **the other one**, not both "to make
them match".

| # | Check | Where it breaks if they diverge |
|--:|---|---|
| 1 | Number and **order** of the parameters: flow × `CREATE PROCEDURE` | at runtime, silently: the wrong position writes to the wrong column |
| 2 | Type of each parameter (text × integer × bit) | the connector conversion fails, or hits the wrong target |
| 3 | Which procedures receive `@Id_UsuarioChamador` and which do not | a missing parameter breaks the call; an extra one is an ignored parameter |
| 4 | Real procedure name in the environment (`sys.procedures`) × the name in the flow | the action fails on execution |
| 5 | Code vocabulary: procedure × flow `Switch` × contract | raw code or an unwarranted `error` |
| 6 | Exact spelling of table/column (case-sensitive in the connector) | the column "does not exist", at runtime |
| 7 | Parameter count in the contract × in the flow, per procedure | any different number is a divergence |
| 8 | Size of text parameters × column | silent truncation on assignment |

Automate item 1/4 whenever possible: the signature read from the `.sql` (or from `sys.sql_modules`) is
the source; the flow is what gets compared. A hand-written contract doc goes stale the day it is
written; generate what you can.

## 5. JSON parameter

`Execute stored procedure (V2)` only binds **scalar** parameters: a table-valued parameter (TVP) does
not cross the connector. For N rows (for example the trail rows of an edit), send **a JSON array in
`NVARCHAR(MAX)`** and open it with `OPENJSON ... WITH`. Requires `COMPATIBILITY_LEVEL >= 130`
(https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql).

JSON schema (keys in `snake_case`, one entry per trail row):

| Key | Type in `WITH` | Target column | Required |
|---|---|---|---|
| `ordem` | `INT` | only the `ORDER BY` | yes |
| `tp_evento` | `NVARCHAR(30)` | `Tp_Evento` | yes |
| `resumo` | `NVARCHAR(400)` | `Des_Resumo` | yes |
| `valor_anterior` | `NVARCHAR(200)` | `Des_ValorAnterior` | yes (can be `null`) |
| `valor_novo` | `NVARCHAR(200)` | `Des_ValorNovo` | yes (can be `null`) |

```sql
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Editar
    @Id_Pedido           INT,
    @Nr_Protocolo        VARCHAR(12),
    @Trilha_Json         NVARCHAR(MAX),
    @Id_UsuarioChamador  INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @Alterado TABLE (
        Id_Pedido  INT          NOT NULL,
        Dt_Evento  DATETIME2(3) NOT NULL
    );

    BEGIN TRANSACTION;

    -- Nr_Protocolo <> @Nr_Protocolo: no change, zero rows (no useless Dt_Alteracao stamp)
    UPDATE s
       SET s.Nr_Protocolo = @Nr_Protocolo
    OUTPUT INSERTED.Id_Pedido, SYSUTCDATETIME()
      INTO @Alterado (Id_Pedido, Dt_Evento)
      FROM dbo.APP_Pedido AS s
     WHERE s.Id_Pedido    = @Id_Pedido
       AND s.Flg_Situacao = 1
       AND s.Nr_Protocolo <> @Nr_Protocolo;

    -- N trail rows in a single INSERT; an empty array ('[]') writes the UPDATE and zero trail
    INSERT dbo.APP_PedidoTrilha
          (Id_Pedido, Tp_Evento, Des_Resumo, Des_ValorAnterior, Des_ValorNovo,
           Id_UsuarioChamador, Dt_Inclusao)
    SELECT a.Id_Pedido, j.tp_evento, j.resumo, j.valor_anterior, j.valor_novo,
           @Id_UsuarioChamador, a.Dt_Evento
      FROM @Alterado AS a
     CROSS JOIN OPENJSON(@Trilha_Json)
           WITH (ordem          INT           '$.ordem',
                 tp_evento      NVARCHAR(30)  '$.tp_evento',
                 resumo         NVARCHAR(400) '$.resumo',
                 valor_anterior NVARCHAR(200) '$.valor_anterior',
                 valor_novo     NVARCHAR(200) '$.valor_novo') AS j
     ORDER BY j.ordem;

    COMMIT TRANSACTION;

    SELECT TOP (1)
           v.status AS status, v.description AS description, v.id AS id, N'' AS url
      FROM (VALUES (1, 'success', N'EDITADA',      CONVERT(NVARCHAR(20), @Id_Pedido)),
                   (0, 'warning', N'NAO_APLICADO', N'')
           ) AS v (Gravou, status, description, id)
     WHERE v.Gravou = (SELECT COUNT(*) FROM @Alterado);
END
GO
```

JSON rules:

1. **Malformed JSON makes the connector action fail** and nothing is written: validating the JSON is
   the flow's job.
2. **`OPENJSON ... WITH` can silently truncate** a value larger than the declared type (the coercion
   is `CAST`-style): the overflow that a direct parameter would report does not exist on this path.
   The flow validates length (400/200/50) **before** building the JSON. `[unverified in an
   environment; flagged in a review of the reference project]`
3. `ORDER BY` on `INSERT ... SELECT` is best effort for the `IDENTITY` order: do not rely on it for
   anything beyond chronological reading; the real order comes from an explicit column.
4. A key that is only known **inside** the transaction (e.g. "did this edit create a duplicate?")
   becomes a pair of flags in the JSON itself (`so_com_duplicidade`, `so_sem_duplicidade`), and the
   `INSERT`'s `WHERE` picks the variant that survives; that way the procedure never learns the rule.
5. A retry reapplies the precomputed trail (the `UPDATE` matches again): see idempotency in
   `procedure-standard.md` §12.

## 6. A return that is not the four-column contract

A data read returns the data. Document in the contract: the **column list** and the **order** (the
flow maps by name, but the CSV/file generated from it depends on the order), the row limit
(`@Limite`) and the count procedure the flow calls first. Count and listing **share the same filter
function**: two copies of the `WHERE` diverge. Acceptance test: the count's `id` == the number of
rows in the listing, with the same `@Filtros` and the same scope.

## 7. Keeping the contract from going stale

- Each procedure has a contract in the `assets/procedure-contract-template.md` template, **generated
  or checked** against the `.sql`.
- The `.sql` the DBA runs is generated from the source and marked "generated, do not edit"; fixes go
  to the source.
- Changed a signature? A new parameter goes **at the end** (the app's `.Run()` is positional; see C4)
  and the contract and the flow change in the same commit.
- Found a defect in a body already handed off? Do not "fix it silently": record the deviation (what
  changed and why), or the next person fixes it back.

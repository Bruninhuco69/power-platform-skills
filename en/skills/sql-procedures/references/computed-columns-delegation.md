# Computed columns for delegation

When the Power Apps app filters, sorts or counts a SQL source, whatever **does not delegate** runs on
the client, over the first N rows (the app's data row limit), and gives a wrong answer with no error.
Computed columns in the database solve three cases without creating new data. The app side (the
`Filter` formula, the limits, the variables) belongs to the `powerapps-canvas` skill; here is the column.

## Contents

1. [Why this exists](#1-why-this-exists)
2. [Date Ref_ column](#2-date-ref_-column)
3. [Why never CAST AS INT](#3-why-never-cast-as-int)
4. [Counting](#4-counting)
5. [Derived status](#5-derived-status)
6. [Index and requirements](#6-index-and-requirements)
7. [Handing off to the DBA](#7-handing-off-to-the-dba)

---

## 1. Why this exists

The table of functions that delegate to SQL Server (source:
https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview)
says, among other things:

- `CountRows` and `CountIf` are **not** in the delegable list; `Sum`, `Min`, `Max`, `Average`,
  `Filter`, `LookUp`, `Sort`, `SortByColumns`, `StartsWith`, `EndsWith` are.
- **Direct date filters do not work with SQL Server behind an on-premises gateway.** The
  documentation's own note suggests a numeric "computed column" and filtering by it.
- `IsBlank(column)` does not delegate; `column <> Blank()` delegates (and does not treat `""` as empty).

The connector also charges for the format: `bit` becomes Boolean, dates become DateTime, and types
such as `rowversion`/`xml`/spatial are not supported. Details in `data-model.md` §2.

| Problem in the app | Way out in the database |
|---|---|
| Date range filter behind a gateway | integer `Ref_<col>` column (§2) |
| `CountRows(Filter(...))` showing a wrong number above the limit | count on the server (§4) or `Sum` of a constant column |
| Compound predicate repeated in 20 formulas (e.g. "overdue", "due soon") | derived status column (§5) |

## 2. Date Ref_ column

```sql
ALTER TABLE dbo.APP_Pedido
    ADD Ref_DtInclusao AS (DATEDIFF(day, 0, Dt_Inclusao)) PERSISTED;
GO
```

`DATEDIFF(day, 0, x)`: the `0` converted to `datetime` is `1900-01-01`; the result is the **day
number** since that date, an integer, deterministic, `PERSISTED` and indexable.
`[verified: reference project]`

In the app, the date picker converts to the **same number** (the difference in days to `1900-01-01`)
and the variable stores an integer, not a date. The formula and the `Reset()` trap of `DatePicker` are
in `powerapps-canvas`. Two points that depend on the database:

- **`Ref_` is a day number: `<=` already includes the whole day.** Do not add `+1` to the upper bound
  (the old pattern, with `DateAdd(+1)` and a date, also included midnight of the next day: one extra
  day in the window, silently).
- The screen and the **filters JSON sent to the flow** are different things: the JSON carries the date
  as text (`"yyyy-mm-dd"`) because what filters there is T-SQL (the read function), not the connector.

**Time zone.** `Ref_<col>` is the day **in the time zone the column was written in** (normally UTC,
`SYSUTCDATETIME()`). The app's `DatePicker` returns a local date: with UTC-3, records from 9pm to
11:59pm fall on the next day and the filter is wrong, silently. Decide and record in
`AS-BUILT-NAMES` whether `Ref_` is a UTC or a local day. For a local day with UTC writes, use a fixed
offset, which is deterministic and persistable:

```sql
ALTER TABLE dbo.APP_Pedido
    ADD Ref_DtInclusaoLocal AS (DATEDIFF(day, 0, DATEADD(hour, -3, Dt_Inclusao))) PERSISTED;
```

`[unverified: a fixed offset only holds without daylight saving time]`. `AT TIME ZONE` is **not**
suitable here: Microsoft classifies it as non-deterministic, because the time zone rules live outside
SQL Server (https://learn.microsoft.com/en-us/sql/t-sql/queries/at-time-zone-transact-sql), and an
indexable or `PERSISTED` computed column requires a deterministic expression
(https://learn.microsoft.com/en-us/sql/relational-databases/indexes/indexes-on-computed-columns).

Alternative documented by Microsoft (same source): `YEAR(c)*10000 + MONTH(c)*100 + DAY(c)`, a number
in `yyyymmdd` format. It works the same; pick **one** per project and record it in `AS-BUILT-NAMES`
(the app's conversion has to match the database's).

Apply the column to **each** table whose date filter the app uses, and expose it in the views the app
reads (the view has to list the new column).

## 3. Why never CAST AS INT

`CAST(<datetime> AS INT)` **rounds**: a record at 1:00pm becomes the next day and drops out of the
window when the filter is `<=` the limit day, wrong for about one record in two, and silent.
`DATEDIFF` **truncates**. `[verified: reference project]`

Prove it in your database (the two columns differ by 1 for any time from noon on):

```sql
SELECT CAST(CAST('2026-03-10T13:00:00' AS datetime) AS int)              AS Cast_Int,
       DATEDIFF(day, 0, CAST('2026-03-10T13:00:00' AS datetime))         AS Datediff_Dia,
       CAST(CAST('2026-03-10T09:00:00' AS datetime) AS int)              AS Cast_Int_Manha;
```

`lint-procedure.py` flags `CAST(<date column or function> AS INT)` and `CONVERT(INT, <date>)` with
`P006`.

## 4. Counting

`CountRows(Filter(source, ...))` runs the `Filter` on the server, but **counts on the client**, over
what came down (up to the limit). The number is exact below the limit and **silently wrong** above it.

Three ways out, from the simplest to the most expensive:

1. **Limit declared on the screen.** The label shows `2,000+` when the count reaches the limit, and
   never pretends the limit is the total. What closes the defect is not the number always being exact;
   it is never being silently wrong. (Formula in `powerapps-canvas`.)
2. **`Sum` of a constant column** (the column is a count disguised as a sum, and `Sum` delegates):
   `[verified: reference project]`

   ```sql
   ALTER TABLE dbo.APP_Pedido ADD Ref_Contador AS (CAST(1 AS INT));
   GO
   ```

   In the app, `Sum(Filter(source, ...), Ref_Contador)` delivers the exact total. The column is
   computed, stores no data and does not need `PERSISTED`.
3. **Count on the server**, through a count procedure called by the flow
   (`assets/read-function-template.sql`, `usp_APP_Pedido_Contar`). It is the only path when the
   filter uses the read function with JSON, and the one the export button should use.

Do not create an **aggregate view** for a counter: a new view is a new object, and the view and the
gallery have to agree all the time. A counter and a gallery over the same table and the same
predicate agree by construction.

## 5. Derived status

A predicate that shows up in many formulas becomes a computed column:

```sql
ALTER TABLE dbo.APP_Pedido ADD Des_StatusPrazo AS (
    CASE
        WHEN Dt_Inclusao IS NULL THEN NULL
        WHEN Dt_Inclusao < DATEADD(day, -30, CAST(GETUTCDATE() AS DATE)) THEN 'Atrasado'
        WHEN Dt_Inclusao < DATEADD(day, -20, CAST(GETUTCDATE() AS DATE)) THEN 'A vencer'
        ELSE 'No prazo'
    END
);
GO
```

- It depends on `GETUTCDATE()`, which is **not deterministic**: the column **cannot** be `PERSISTED`
  or indexed; filtering by it does a scan. Acceptable at the current volume; record the limit.
- **The boundary (30, 20 days) is a business rule**, and it is rarely written in a document. Confirm
  it with the business before creating the column; it is the number that separates the bands across
  the whole screen.
- To the connector it is an ordinary text column: `=` and `<>` delegate.
- If the rule changes, it changes in the DDL (a request to the DBA). That is why a rule that changes
  every week lives in the flow and not in a column.

## 6. Index and requirements

An index on a computed column requires (source:
https://learn.microsoft.com/en-us/sql/relational-databases/indexes/indexes-on-computed-columns):

- a **deterministic** and **precise** expression (no `float`/`real`); functions owned by the same
  owner as the table; `PERSISTED` allows indexing a deterministic but imprecise expression;
- at creation and on **every connection that writes**, `ANSI_NULLS`, `ANSI_PADDING`, `ANSI_WARNINGS`,
  `ARITHABORT`, `CONCAT_NULL_YIELDS_NULL`, `QUOTED_IDENTIFIER` set `ON` and `NUMERIC_ROUNDABORT` set
  `OFF`; the optimizer ignores the index for the `SELECT` of a connection without these options;
- `QUOTED_IDENTIFIER ON` when creating or altering the index (tool-generated scripts sometimes
  carry `OFF`);
- there is no **filtered** index on a computed column.

```sql
CREATE NONCLUSTERED INDEX IX_APP_Pedido_Ref_DtInclusao
    ON dbo.APP_Pedido (Ref_DtInclusao)
    INCLUDE (Nom_Abvd_Unidade, Des_Status);
GO
```

Confirm the index is used in the plan of a real query (`Index Seek`), without trusting intuition. On a
large table, `ALTER TABLE ... ADD ... PERSISTED` writes the column on every row: ask the DBA for a
window `[unverified: cost at your volume]`.

## 7. Handing off to the DBA

A database frozen in production tends to refuse a new table, a column that stores data, a new view and
a signature change, and to **accept a computed column**. The real criterion is not "is it DDL?", it is
**"does the object store its own data?"**: a computed column derives from another and carries no new
information. `[verified: reference project]`

Ask for all the project's computed columns (`Ref_*`, counter, status) together, in the same request,
with the delegation justification and the query that proves the effect. Template:
`assets/dba-ddl-request-template.md`. The DBA decides what goes into the database; the screen and the
flow can always absorb what they refuse, with the cost in performance or accuracy stated.

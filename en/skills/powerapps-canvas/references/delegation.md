# Delegation: SQL Server and Dataverse on the app side

The topic that produces the most silent bugs in Canvas: the app does not fail, does not warn, it
just returns an incomplete result. Here is what delegates, what does not, the caps, the tricks and
how to prove it. The database side (computed column, procedure, collation) belongs to the
`sql-procedures` skill; the Dataverse schema, to the `dataverse` skill.

## Contents

1. [The golden rule and the cap](#1-the-golden-rule-and-the-cap)
2. [SQL Server connector](#2-sql-server-connector)
3. [Counting](#3-counting)
4. [Dates](#4-dates)
5. [Dataverse](#5-dataverse)
6. [Search, `in` and `LookUp`](#6-search-in-and-lookup)
7. [A wrong column fails silently](#7-a-wrong-column-fails-silently)
8. [What breaks delegation without a warning](#8-what-breaks-delegation-without-a-warning)
9. [When it does not delegate: alternatives](#9-when-it-does-not-delegate-alternatives)
10. [How to prove it](#10-how-to-prove-it)
11. [Declare it in writing (T7)](#11-declare-it-in-writing-t7)
12. [Sources](#12-sources)

---

## 1. The golden rule and the cap

> "If any part of a query expression is nondelegable, Power Apps doesn't delegate any part of
> the query." ([Understand delegation](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview))

There is no partial delegation. One nondelegable function in the middle brings everything down, and
the app starts downloading the first **500** rows (adjustable up to **2,000** in *Settings > General >
Data row limit*) and filters on the client. Row 501 is not found and nothing warns you.

- The delegation warning (triangle) only appears on formulas over a **delegable source**.
  **No warning does not prove delegation.**
- `With`, `UpdateContext` and `Set` create collections internally; a collection does not take part
  in delegation **and raises no warning** (see §8).
- What is not in the table for **your** connector does not delegate, even if it delegates in another.

## 2. SQL Server connector

Official table, by data type
([SQL Server connector](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview),
page updated 2025-03, read 2026-10). Expressions joined by `And`, `Or` and `Not` delegate.

| Operation or function | Number | Text | Boolean | Date and time | Guid |
|---|---|---|---|---|---|
| `*`, `+`, `-`, `/` | yes | - | - | no | - |
| `<`, `<=`, `>`, `>=` | yes | **no** | **no** | yes | - |
| `=`, `<>` | yes | yes | yes | yes | yes |
| `Filter` | yes | yes | yes | yes [2] | yes |
| `LookUp` | yes | yes | yes | yes | yes |
| `Sort`, `SortByColumns` | yes | yes | yes | yes | - |
| `Sum`, `Average` | yes | - | - | - | - |
| `Min`, `Max` | yes | - | - | no | - |
| `StartsWith` | - | yes [6] | - | - | - |
| `EndsWith` | - | yes [1] | - | - | - |
| `Search` | no | yes | no | no | - |
| `in` (substring) | - | yes [3] | - | - | - |
| `Len` | - | yes [5] | - | - | - |
| `IsBlank` | **no** [4] | no | no | no | no |

Official notes, summarized:

1. `EndsWith(column, "x")` delegates; `EndsWith("x", column)` does not. In `CHAR(10)`, `"hello"` has
   10 characters: `EndsWith(column, "llo")` returns false, by design.
2. **A direct date filter does not work with SQL Server behind an on-premises gateway.** The
   documented way out is a numeric computed column and filtering on it (§4).
3. `"text" in column` delegates; `column in "text"` does not. A literal list
   (`column in ["a", "b"]`) is **not listed** in the SQL table: treat it as nondelegable.
4. `!IsBlank(column)` does not delegate; `column <> Blank()` delegates and is semantically close
   (it does not treat `""` as empty). Does not work for Guid.
5. `Len` delegates, but Power Apps treats `CHAR(10)` with `"hello"` as length 5 and SQL as 10.
   Use `VARCHAR`/`NVARCHAR`, not `CHAR`/`NCHAR`.
6. `StartsWith(column, "x")` delegates; `StartsWith("x", column)` does not.

More rules on the app side: comparing a column with a variable that is `Blank()` is not resolved on
the server; use the idiom `IsBlank(variable) || column = variable` (the left side is a client
constant and is folded before the query, so it delegates)
`[verified: reference project]` (verified on the SQL connector; for Dataverse see
`dataverse-delegation.md`).

Destination: YAML pasted into Studio.

```yaml
# xx-gal-pedidos
Items: |-
  =Sort(
    Filter(
      Pedido,
      StartsWith(Unidade, varUnidadeFiltro),
      IsBlank(varStatusFiltro) || Status = varStatusFiltro
    ),
    Dt_Inclusao,
    SortOrder.Descending
  )
```

(Property illustration; the full screen is in [screen-template.md](../assets/screen-template.md).)

## 3. Counting

**`CountRows` and `CountIf` do not delegate on the SQL connector**: the table in §2 does not list
them. The inner `Filter` delegates and becomes a `WHERE`; only the count runs on the client, over
the up to 2,000 rows that came down. The classic defect is the card showing `2,000` as if it were
the total. `[verified: reference project]`

Ways out, from cheapest to most exact:

| Way out | When | Cost |
|---|---|---|
| **Cap in the UI**: if `n >= fxLimiteLinhas`, show `fxTxtTeto` (`2,000+`) | card and informational label | zero; the number is exact or declared incomplete, it never lies |
| **`Sum` of a column that is 1** (computed column `1`, or numeric `Flg_*`) | exact count without a procedure | `Sum` delegates on SQL (Number) |
| **Count on the server**: procedure with `COUNT_BIG` returned by the flow | exact number above the cap (report, export) | one flow per count |

Destination: YAML pasted into Studio.

```yaml
# xx-lbl-total
Text: |-
  =If(
    varPedidoTotal >= fxLimiteLinhas,
    fxTxtTeto,
    Text(varPedidoTotal)
  )
```

When the card and the gallery read the **same source with the same predicate**, they agree by
construction: that is what closed the "the card number does not match the list" defect. Keep the
predicate (including the scope one) in a single place. `[verified: reference project]`

A counter must be **recalculated** in `OnVisible` and after each flow that writes. A counter
calculated only in `OnStart` freezes and diverges from the gallery.

## 4. Dates

A direct date filter does not delegate behind an on-premises gateway. Note [2] of the table itself
gives the way out: a numeric computed column in the database and a filter on it.

**In the database** (a request to the `sql-procedures` skill): an integer column `Ref_<column>`
equal to the number of days since 1900-01-01, persisted:
`Ref_DtInclusao AS DATEDIFF(day, 0, Dt_Inclusao) PERSISTED`. **Never `CAST(... AS INT)`**: the
`CAST` rounds, it does not truncate; an event at 1:00 PM on the cutoff day becomes the next day and
drops out of the window, wrong on every other record, silently.

**In Power Fx**: the `DatePicker` converts in `OnChange` and the variable holds an **integer**, not
a date. `36524` is the distance from 1900-01-01 to 2000-01-01 (Power Fx has no 1900 literal).

Destination: YAML pasted into Studio.

```yaml
# xx-dtp-filtro-de
OnChange: |-
  =Set(
    varPedidoDe,
    If(
      IsBlank(Self.SelectedDate),
      Blank(),
      36524 + DateDiff(Date(2000, 1, 1), Self.SelectedDate, TimeUnit.Days)
    )
  )
```

The `If` exists because an empty `DatePicker` delivers a blank `SelectedDate`: without it the
variable becomes a number, the `Filter`'s `IsBlank` stops recognizing "no filter" and the gallery
opens empty.

Destination: YAML pasted into Studio.

```yaml
# xx-gal-pedidos-janela
Items: |-
  =Filter(
    Pedido,
    IsBlank(varPedidoDe) || Ref_DtInclusao >= varPedidoDe,
    IsBlank(varPedidoAte) || Ref_DtInclusao <= varPedidoAte
  )
```

- **No `DateAdd(+1)` on the upper bound.** `Ref_*` is a day number: `<=` already includes the whole
  day. The old pattern added 1 day to a date and used `<=`, which also included midnight of the
  next day (one extra day, silent).
- **`Reset()` on a `DatePicker` does not fire `OnChange`.** The Clear button rewrites the variable
  with the **same** value as `OnVisible`; otherwise the control shows one window and the `Filter`
  uses another.
- Window variables are born in the screen's `OnVisible`, not in `OnStart`.

**Time zone.** `Ref_<col>` is the day **in the time zone the column was written in** (normally
UTC). The `DatePicker` returns a local date: with UTC-3, records from 9 PM to 11:59 PM fall on the
next day and the day filter is silently wrong. Record in `AS-BUILT-NAMES` whether `Ref_` is a UTC
day or a local day and use the same rule on both sides; a local-day column is DDL (see
`sql-procedures/references/computed-columns-delegation.md`).
- Does not apply to what travels to the flow: date as **text** `yyyy-mm-dd`; whoever filters there
  is the procedure, in T-SQL, not the connector.

## 5. Dataverse

This skill owns **SQL** delegation; **Dataverse** delegation belongs to the `dataverse` skill. The
difference in one sentence: in Dataverse the connector accepts more functions and aggregations,
with its own cap of 50,000, and `Filter` with a variable, `Today()` and `CountRows(Filter(...))`
have rules different from SQL. Matrix, caps and caveats: see
`dataverse/references/dataverse-delegation.md`.

## 6. Search, `in` and `LookUp`

- **`StartsWith` first** (uses an index, becomes `LIKE 'x%'`). `Search` and `"x" in column` become
  `LIKE '%x%'`: no index, slow on a large table. Microsoft recommends `StartsWith` or `Filter`
  instead of `in`
  ([Optimized query data patterns](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/optimized-query-data-patterns)).
- **`column in [list]` over a SQL source does not delegate**: the app downloads up to the cap and
  filters on the client, with no error. Alternatives: equalities joined by `Or` (few values), a
  computed group column, or a procedure via flow. The validator flags `Search(`/`in` inside
  `Filter(` over a source that is not `col*` (T011); on SQL, `Search` on a text column delegates
  (table in §2), so the warning asks for **a check**, it is not a verdict.
- **Never `LookUp(<source>, ...)` inside a gallery**: one query per rendered row (N+1; 50 rows = 51
  requests). Resolve the label from a **collection** loaded in `OnStart`
  (`LookUp(colCategorias, ...)` is free). The same goes for `AddColumns` with `LookUp` inside.
- **3-stage funnel** when you need to join domains: reduce on the server (delegable `Filter`),
  join with `in` over a small collection, look up by name already in memory.
  `Distinct` and `With` in stage 1 truncate: see §8.

## 7. A wrong column fails silently

`SearchFields`, `DisplayFields` and `SortByColumns` take **column names in quotes**. A nonexistent
name **raises no error**: `DisplayFields` returns an empty field in the `ComboBox`, `SearchFields`
finds nothing and `SortByColumns` simply does not sort. This happens because `AddColumns` keeps
the source columns, so the wrong name keeps "resolving". `[verified: reference project]`

- The logical name (Dataverse) / column name in the source (SQL) comes from the environment
  (`AS-BUILT-NAMES`, `dataverse` skill), not from the display name or the dictionary. On the SQL
  connector the name is **case-sensitive**; a wrong spelling is not flagged while editing and
  fails at runtime, silently.
- **A filtered extract does not prove the schema.** Before stating that a column does not exist (or
  that it does), open the table schema, not a sample (decision N3).
- `DisplayFields` needs the column name in the source: SQL has no *primary name column*; `[""]` does
  not work.
- Test by typing in the control and looking at the result. The validator only flags what can be
  seen without the environment: T014 (prefix, on the Dataverse track).

## 8. What breaks delegation without a warning

| Pattern | Effect | Way out |
|---|---|---|
| `With({x: ...}, Filter(source, ...))` | the source becomes a collection; no warning | `With` only for scalars, outside the `Filter` |
| `Distinct(Filter(source, ...), col)` | `Distinct` does not delegate: truncates at 500/2,000 | grouping column or a join table in the database |
| `AddColumns`/`ShowColumns` on a large query | the argument delegates, the **output** truncates | use over an already reduced set |
| `FirstN(Sort(Filter(...)), 50)` | `FirstN` does not delegate; if the `Filter` does not either, it becomes "top 50 of the first 500 arbitrary rows" | pagination or "load more" over a delegable `Items` |
| `Gallery.AllItems` as a source | only what is already loaded | `AllItemsCount` or a delegable predicate |
| `UpdateIf`/`RemoveIf` over a large source | simulates delegation up to 500/2,000 | operation on the server |
| `If(...)` inside `Filter` | does not delegate | resolve the `If` into the variable, beforehand |
| 50 scalar variables + `Or` to simulate `in` | delegates, but costs 150 `Set` | grouping column |

## 9. When it does not delegate: alternatives

In order of preference:

1. **View or computed column on the server** (Microsoft's strongest recommendation; a view turns off
   aggregation in Dataverse).
2. **Denormalized column** + `=` or `StartsWith` (uses an index), filled by a flow or procedure.
3. **Flow/procedure** that returns the already resolved set (costs ~0.6 s to instantiate the flow).
4. **`Or` of equalities**: delegates, but approaches the condition cap and hurts readability.
5. **Local filter with a high *Data row limit***: **incorrect** result above 2,000 rows.
   Last resort, and only with the cap declared in the UI.

Small, stable domains (a few thousand rows, used by 4 screens or more) go into a **collection or
named formula**, loaded once. Transactional data that another user changes in parallel does not:
the cache becomes a decision about stale data.

## 10. How to prove it

1. **Data row limit = 1** on a clone of the app (*Settings > General*): every nondelegable query
   returns one row, and the list that "disappears" shows up in seconds. It is the technique
   Microsoft recommends. Do it before delivering a new screen.
2. **App checker**: count the delegation warnings and note the control of each one.
3. **Live monitor**: open the screen and read the query sent (`WHERE`/`$filter`). One request per
   gallery page is good; one per row is N+1.
4. Test with **volume above the cap** (synthetic load): the `2,000+` and the delegation behavior
   can only be proven this way.
5. `[unverified]` `in [list]` over a SQL source: confirm in the Monitor whether your app sends the
   `WHERE` or downloads and filters.

## 11. Declare it in writing (T7)

At the top of each screen file, in a `#` comment (the file is pure YAML; `//` breaks the parse
outside a formula): for each table function, whether it delegates and what the cap is.

Destination: comment at the top of the `.pa.yaml` file (not a formula).

```text
# DELEGATION of this screen (SQL source, cap fxLimiteLinhas = 2000)
#   Filter + StartsWith + Sort ............ delegates (WHERE / ORDER BY)
#   CountRows(Filter(...)) ................ does NOT delegate; label shows fxTxtTeto
#   Date filter ........................... by Ref_DtInclusao (integer), delegates
#   column in [list] ...................... not used
```

A YAML comment (`#`) outside a formula is allowed in the source file, but **is not preserved** by
Studio on re-export: the declaration lives in the repository, not in the app.

## 12. Sources

- [Understand delegation in a canvas app](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview)
- [Connect to SQL Server from Power Apps overview](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview)
- [Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service)
- [Count, CountA, CountIf, CountRows](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-table-counts)
- [AddColumns, DropColumns, RenameColumns, ShowColumns](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-table-shaping)
- [Optimized query data patterns](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/optimized-query-data-patterns)
- [Top performance issues (N+1)](https://learn.microsoft.com/en-us/power-platform/architecture/key-concepts/performance/top-issues)

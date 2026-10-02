# Delegation in the Dataverse connector

What Dataverse delegates, what it does not, the limits and how to test. The app side (how to write the
gallery, `OnStart`, counters) belongs to `powerapps-canvas`; this reference covers what is **specific
to the Dataverse connector** and how it differs from the SQL Server connector.

## Contents

1. [The rule and the cap](#1-the-rule-and-the-cap)
2. [Dataverse connector matrix](#2-dataverse-connector-matrix)
3. [Counting and aggregation](#3-counting-and-aggregation)
4. [In, StartsWith, Search](#4-in-startswith-search)
5. [Dates](#5-dates)
6. [Silent pitfalls](#6-silent-pitfalls)
7. [Dataverse vs SQL Server](#7-dataverse-vs-sql-server)
8. [When it does not delegate: alternatives](#8-when-it-does-not-delegate-alternatives)
9. [How to test](#9-how-to-test)

---

## 1. The rule and the cap

- If **any part** of the expression does not delegate, **no part** delegates: the app downloads the first
  **500** rows (adjustable up to **2,000**, in *Settings > General > Data row limit*)
  and filters on the client, **with no error**.
  Source: [Understand delegation](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview).
- The warning (yellow triangle) only appears on formulas over a delegable source and does not cover everything. **No
  warning does not prove delegation.** Test with a limit of 1 (§9).
- The wrong result "looks right": it is silent truncation (the most expensive class of defect in a Canvas app). Every query
  declares in writing what delegates (`default-decisions.md` T7).

## 2. Dataverse connector matrix

Transcribed from the connector table
([Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service),
read 2026-10). The connector table is the authority: what is **not** in it does not delegate.

| Operation | Number | Text | Choice | DateTime | GUID |
|---|---|---|---|---|---|
| `<` `<=` `>` `>=` | yes | yes | **no** | yes | - |
| `=` `<>` | yes | yes | yes | yes | yes |
| `And` / `Or` / `Not` | yes | yes | yes | yes | yes |
| `Filter`, `LookUp`, `Sort`, `SortByColumns` | yes | yes | yes | yes | `Filter`/`LookUp`: yes |
| `First` | yes | yes | yes | yes | yes |
| `In` (belongs to a list) | yes | yes | yes | yes | yes |
| `In` (substring) | - | yes | - | - | - |
| `IsBlank` | yes | yes | **no** | yes | yes |
| `Search` | no | **yes** | no | no | - |
| `StartsWith` | - | yes | - | - | - |
| `CountRows`, `CountIf` | yes | yes | yes | yes | yes |
| `Sum`, `Min`, `Max`, `Avg` | yes | - | - | **no** | - |

Notes from the official table that change formulas:

1. **Number**: an arithmetic expression on the column (`Filter(t, col + 10 > 100)`) does not delegate; a cast to
   number does not either; a column the app sees as a number but the backend does not store as a plain number (currency) does not delegate.
2. **Text**: `Trim`, `Trim[Ends]` and `Len` are not supported; `Left`, `Mid`, `Right`, `Upper`,
   `Lower`, `Replace` and `Substitute` are listed as supported in the official note; `Text(col)` is not.
   A reference project recorded `Upper`/`Lower`/`Left`/`Mid` over a column as **not** delegable in
   practice `[verified: reference project, differs from the official note]` — **test before using**.
3. **DateTime** delegates, **except** the `Now()` and `Today()` functions (see §5).
4. `CountRows` uses a **cached value** (see §3).
5. For `CountRows`, the user needs permission to get table totals.
6. Every aggregation is capped at **50,000** rows and **does not work on views**.
7. **`FirstN` is not supported.**
8. `In` is subject to the limit of **15 tables** per Dataverse query (connector note). Another
   source in a reference project cites 20 entities per query on another page; the documentation is
   inconsistent `[unverified which one holds]`.
9. `IsBlank` accepts comparisons (`col = Blank()`), but **not** on Choice.
10. `UpdateIf`/`RemoveIf` only simulate delegation up to 500/2,000 records.

Outside the table and therefore **not delegable**: `EndsWith`, `Distinct`, `GroupBy`/`Ungroup`, `ForAll`,
`Concat`, `Collect`/`ClearCollect`, `Choices`, `With`, `If` inside the predicate, `Left`/`Mid`/`Right`
over a column (according to a reference project), `exactin`, `StdevP`/`VarP`, local collections as a source.
`EndsWith` appears in the general delegation list but not in the Dataverse connector table: treat it as not
delegable and validate it in Monitor `[verified: reference project]`.

Structural query limits (cited by a reference project from Learn, **not reconfirmed**):
conditions per OData query ≈ 500 (`TooManyConditionsInQuery`), lookup/expand levels = 2,
`$expand` clauses = 10, strings in an `In` ≈ 850 characters in total
([Filter rows using OData](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query/filter-rows))
`[unverified]`. To reduce conditions, use `In`/`NotIn` instead of a chain of `Or`.

## 3. Counting and aggregation

Unlike SQL Server, **Dataverse delegates counting**, with three caveats:

| Use | Delegates | Cap | Accuracy |
|---|---|---|---|
| `CountRows(Table)` with no filter | yes | no hard cap | **approximate** (cached value) |
| `CountRows(Filter(Table, …))` | yes | 50,000 | exact up to the cap `[unverified: a reference project says it requires the "Enhanced delegation for Microsoft Dataverse" option; the connector page does not mention it]` |
| `CountIf(Table, cond)` | yes | 50,000 | exact up to the cap |
| `CountIf(Table, true)` | yes | 50,000 | exact — bypasses the `CountRows` cache |

Source: connector note 4 and [Count, CountA, CountIf, CountRows](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-table-counts).

Consequences:

- `CountRows` with no filter serves "roughly how many"; to check a load use
  `CountIf(Table, true)` (`references/data-import.md`).
- **A counter that shows `50000` may be the broken query, not the volume.** `IfError(..., 50000)`
  masks a failure with the exact number of the cap. Show the error, or `—`, never a plausible number.
  `[verified: reference project]`
- Aggregation on a **view** does not work; a view resolves the filter on the server, but turns off `Sum`/`CountIf`.
- Above 50,000, aggregate on the server (flow, materialized view, summary/rollup column).

## 4. In, StartsWith, Search

- `col in [list]` and `col in collection` (column of the **base table**) delegate; the docs only exemplify
  `in` with a literal array, and delegation against a **variable collection** is shown by a third-party blog
  (not by documentation). **Validate with limit 1** `[unverified]`.
- `col in [list]` over a column of **another table** (through a relationship) does not delegate.
- `"text" in col` (substring) delegates on Text, but is equivalent to `LIKE '%x%'` and **does not use an index**:
  Microsoft prefers `StartsWith`
  ([Optimized query data patterns](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/optimized-query-data-patterns)).
  Do not confuse the two `in`.
- `StartsWith(column, text)` delegates and uses an index; the **column goes on the left**. So does equality:
  `column = variable`, not `variable = column`, or the expression does not delegate `[verified: reference project]`.
- `Search` delegates only on text columns; `SearchFields` with a wrong name **fails silently**
  (`references/names-and-types.md` §3).

```
// formula bar (en-US: , and ;)
// Delegates: column on the left, text, StartsWith
Filter(
  Pedidos,
  StartsWith(unidade, varUnidadeFiltro),
  situacao = 'situacao (Pedidos)'.Aberto
)
```

Beware of the scope filter `""` = "all": `StartsWith(unidade, "")` is true for every
row with a value, and **leaves out a row with an empty `unidade`**. If empty must mean "all",
handle the case (`IsBlank(varUnidadeFiltro) || …` breaks delegation — prefer two `If` branches
*outside* the `Filter`, or make the column required). `[unverified in Dataverse; in SQL the idiom delegates — verified]`

## 5. Dates

DateTime delegates in Dataverse. The exception is the `Now()`/`Today()` function (connector note 3), which **conflicts**
with the general delegation page (which says `Today()` "folds to a constant" and does not block).
**Treat it as a risk** and remove the doubt:

```
// formula bar (en-US: , and ;)
// OnStart or OnVisible: compute the date once
Set(varLimite, DateAdd(Today(), -30, TimeUnit.Days));

// Filter: the variable is a constant, the column stands alone on the left
Filter(Pedidos, data_pedido >= varLimite)
```

Careful not to swing to the other extreme: **`With(…)` around the source breaks delegation without a warning**
(§6). The variable must be a **scalar** (`Set`), not a `With` that wraps the table.

## 6. Silent pitfalls

| Pitfall | Effect | Way out |
|---|---|---|
| `With`, `Set` or `UpdateContext` over a **source** | They create an in-memory collection: no delegation, **no warning** | Use `With` only for scalars and constants; keep the table out of it |
| `AddColumns`/`ShowColumns` | The arguments delegate, the **output truncates** at 500/2,000 | Project only the needed columns; do not use it as a join of a large table |
| `AddColumns` with `LookUp` inside | One network call **per row** (N+1) | Denormalize the column or load the small master into a collection |
| `Distinct(Filter(…))` | Does not delegate; the filter list truncates | Domain table, or a flow that returns the values |
| Constant inside the `Filter` (`!varFlag && col = x`) | The constant clause does not delegate in Dataverse | `If(varFlag, Blank(), Filter(…))` outside the `Filter` |
| `Choices()` as a gallery source | Does not delegate | Only for a ComboBox with few options |
| `IfError(…, 50000)` | A failure becomes a plausible number | Show the error |
| Dataverse query inside `Visible` or `Timer.Start` | Network on every evaluation | Variable updated on an event |

Source for the first item: [Delegation overview](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview).

## 7. Dataverse vs SQL Server

The same formula delegates one way on one connector and another way on the other. Changing the data track invalidates the
delegation audit.

| Aspect | Dataverse | SQL Server |
|---|---|---|
| `CountRows`/`CountIf` | delegates (≤ 50,000; without a filter it is approximate) | **does not delegate**: show a cap (`2,000+`) or count on the server (B3) |
| Direct date filter | delegates | **does not delegate** behind a gateway: integer computed column `Ref_<col>` (B2) |
| `Sum`/`Min`/`Max`/`Avg` | delegates on Number (≤ 50,000) | delegates on Number |
| `EndsWith`, `Len` | no | yes (text) |
| `In` (belongs to) | yes | no (substring only) |
| `Search` | text only | text only |
| `*` `/` over a column | no | yes (number) |
| View as output | resolves the filter on the server; **no aggregation** | same (view) |
| Types | native Choice/Lookup/Yes/No | `bit`, text, number |

Origin: matrix of `default-decisions.md` B2/B3 and the connector table of a reference project
(`[verified: reference project]` for the SQL column; the Dataverse column follows the Learn page above).

## 8. When it does not delegate: alternatives

In order of preference for Dataverse:

1. **View** pre-filtered on the server (the one Microsoft recommends most): filter and join run on the
   server and the payload shrinks. Price: no aggregation.
2. **`Filter(table, col in colValues)`**, respecting ≈ 850 characters of strings per query.
3. **Denormalized column** + `=` or `StartsWith` (uses an index), filled by a flow, plugin or
   app write (`references/modeling.md`).
4. **Flow** that returns the result already aggregated/filtered (volume above 50,000; export).
5. **Accept the cap** and show it (`2,000+`), if the business rule allows.

Never: export from a gallery or collection (loses data without an error); use the gallery filter as the
only access control (`references/security.md`).

## 9. How to test

1. *Settings > General > Data row limit* = **1**. Every nondelegable query now
   returns one row, which is easy to see. This is the documentation's own recommendation.
2. Walk through the screen: gallery, counters, filter combos, identity `LookUp`. A single row where
   there should be a list = does not delegate.
3. Open **Monitor** (*Advanced > Open Monitor*) and check the query sent to the server: the
   `$filter` must contain the predicate. A missing predicate = client-side filter.
4. Put the limit back to 500 (or 2,000) and note in the screen header what delegates, what does not and the cap.

The audit does not end in Studio: production data has more rows than test data. Test with
a data set larger than the limit.

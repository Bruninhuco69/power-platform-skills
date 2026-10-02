# Performance and loading

Each pattern comes as **problem, symptom, solution, when not to use it**. Delegation (what gets
downloaded and what runs on the server) is in [delegation.md](delegation.md); timers and
auto-refresh, in [timers-async.md](timers-async.md). Diagnostic findings from real apps are in
[field-lessons.md](field-lessons.md).

## Contents

1. [Minimal `OnStart` and named formulas](#1-minimal-onstart-and-named-formulas)
2. [`Concurrent`](#2-concurrent)
3. [Deferred screen loading](#3-deferred-screen-loading)
4. [Deferred data loading](#4-deferred-data-loading)
5. [Pagination](#5-pagination)
6. [Domain cache](#6-domain-cache)
7. [Controls per screen](#7-controls-per-screen)
8. [`With` and recomputation](#8-with-and-recomputation)
9. [Images and media](#9-images-and-media)
10. [Query in a UI property](#10-query-in-a-ui-property)
11. [Global `Set` fanout](#11-global-set-fanout)
12. [Connector limit](#12-connector-limit)
13. [Loading coverage](#13-loading-coverage)
14. [How to measure](#14-how-to-measure)
15. [Sources](#15-sources)

Anti-patterns named by Microsoft: "loading too much data, turning everything into
collections, and overloading OnStart"
([Create performant apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-performant-apps-overview)).

---

## 1. Minimal `OnStart` and named formulas

**Problem.** `OnStart` runs in sequence before the app becomes usable, even if 90% of what it
loads is only used on the fifth screen. **Symptom.** Long opening spinner, slow Studio start, an
"Inefficient Delay Loading" warning in the App checker.

**Solution.** Move everything constant or derived to `App.Formulas`. Microsoft reports Studio load
time dropping by up to 80% from this change alone
([Working with large apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/working-with-large-apps)).
A named formula has four properties that `OnStart` does not: always available, always up to date,
immutable definition and deferrable calculation. And *"There's no penalty for including a formula
definition that isn't used"*: a heavy named formula that no screen reads costs zero; the same
calculation in an `OnStart` `Set` costs a query on every boot
([App object](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)).

| The value... | Goes to |
|---|---|
| never changes once calculated (theme, `User()`, derived values, reference lists) | `App.Formulas` |
| changes by user action | `OnStart` (initialization only) or `OnVisible` |
| only exists on one screen | `UpdateContext` in `OnVisible` |
| depends on an action (`Patch`, `.Run()`) | never in `Formulas` |

**When not to use it.** Anything with `Set`, `Collect`, `Patch`, `Notify`, `Navigate`,
`Reset`; a value the user edits; circular reference. `StartScreen` does not see globals or
collections, only named formulas. Template: [app-onstart-template.md](../assets/app-onstart-template.md).

## 2. `Concurrent`

**Problem.** A chain of sequential `ClearCollect` calls pays network latency n times.
**Solution.** `Concurrent(a, b, c)` for **independent** calls.

Documented contracts: the start and end order is unpredictable; on some devices only part of the
formulas actually run in parallel; if one fails, the others continue
([Concurrent](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-concurrent)).

**When not to use it.** There is a dependency between branches (use separate, sequential
`Concurrent` calls); trivial `Set` calls (pure CPU, no I/O, only adds overhead); more than ~10
simultaneous calls (throttling risk, [Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)).

## 3. Deferred screen loading

1. Keep **Delayed load** on (the default in a new app).
2. **Never reference a control on another screen**: a cross reference cancels the deferred load of
   the referenced screen (shows up as "Inefficient Delay Loading").
3. **The first screen must be light**: it is packaged together with the initialization logic
   ([Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)).
   A start menu that renders three aggregations on the very first paint pays three queries before
   any click; move the KPIs to on-demand loading (button, or `Visible` tied to a flag) or use
   `StartScreen` for a light screen.
4. A control that is **initially invisible is not rendered** (new apps since Dec/2022). It only
   applies to the initial state: once the user switches tabs, everything has been instantiated and
   stays. A heavy tab must be hidden in the initial state.

**When not to use it.** Only turn Delayed load off if `ConfirmExit` needs to reference a control
outside the first screen (otherwise the published app does not open).

## 4. Deferred data loading

Cost hierarchy, cheapest first:

| Technique | When | Cost |
|---|---|---|
| direct query in `Gallery.Items` | a list the user only reads and scrolls | zero until the gallery renders |
| named formula | derived value read on 1 or more screens | zero until someone reads it |
| `ClearCollect` in `Screen.OnVisible` | data filtered or sorted locally on the screen | 1 trip to the server on entry |
| on-demand `ClearCollect` (open a tab or modal) | details, dependent lists | 1 trip on click |
| `ClearCollect` in `App.OnStart` | almost never | penalizes every boot |

"Load when the tab opens" pattern, with the collection as a session cache:

Destination: YAML pasted into Studio.

```yaml
# xx-btn-tab-referencias.OnSelect
OnSelect: |-
  =Set(varXXTab, 2);
  If(
    IsEmpty(colReferencias),
    Set(varShowLoading, true);
    Set(varLoadingMessage, fxMsgLoadingDefault);
    ClearCollect(colReferencias, ShowColumns(Referencia, "Id_Referencia", "Descricao"));
    Set(varShowLoading, false)
  )
```

`ShowColumns` is not optional: with *Explicit column selection* on, only the declared columns
survive into the collection ([Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)).
Well-behaved screens have an `OnVisible` with state only (`Set`/`Clear`), no I/O; the data comes
from `Items`.

**When not to use it.** A **small, stable** reference list used by 4 screens or more: load it once
(or use a named formula). Data required by `StartScreen`.

## 5. Pagination

**Problem.** A gallery whose `Items` returns thousands of rows, or one that compensates with a
fixed `FirstN` that **hides** records from the user. **Symptom.** Stuck scrolling; "the record
exists but does not show up".

The gallery paginates in increments of ~100 rows; aim for 100 to 200 in the default query
([Small data payloads](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/small-data-payloads)).
`FirstN` does not delegate: over a nondelegable filter it becomes "top N of the first 500 arbitrary rows".

**Solution A: "load more"** (over a delegable `Items`):

Destination: YAML pasted into Studio.

```yaml
# button xx-btn-carregar-mais
Visible: ='xx-gal-pedidos'.AllItemsCount >= varLinhasVisiveis
OnSelect: =Set(varLinhasVisiveis, varLinhasVisiveis + fxPageSize)
Text: ="Load more (" & 'xx-gal-pedidos'.AllItemsCount & " loaded)"
```

**Solution B: fixed page over a collection**: `LastN(FirstN(colDados, varPagina * fxPageSize), fxPageSize)`;
next page is just `If(varPagina * fxPageSize < CountRows(colDados), Set(varPagina, varPagina + 1))`.

**`TemplateSize` never 0**: use `Max(20, ...)`. A `MaxTemplateSize` that is too high (50,000) allows
a 50,000 px row and removes the predictability of virtualization; use the largest real value expected.

**When not to use it.** `Items` already delegated and under 200 rows. If the user needs an
**aggregate of the whole set**, paginate the display and calculate the aggregate separately
(see [delegation.md](delegation.md) §3); never with `CountRows(gal.AllItems)`.

## 6. Domain cache

**Problem.** A domain table (units, types) queried dozens of times per session.
**Solution A, named formula** (for what does not change during the session): one query per session,
evaluated when the first control reads it, shared across screens.

Destination: App object formula bar, `Formulas` property (en-US: `,` and `;`).

```powerfx
frmUnidades = SortByColumns(ShowColumns(Unidade, "Cod_Unidade", "Nom_Unidade"), "Nom_Unidade", SortOrder.Ascending);
```

**Solution B, collection with explicit invalidation** (when the app itself edits the domain):

Destination: YAML pasted into Studio.

```yaml
# Screen.OnVisible
OnVisible: |-
  =If(
    IsEmpty(colUnidades) || varUnidadesVelhas,
    ClearCollect(colUnidades, ShowColumns(Unidade, "Cod_Unidade", "Nom_Unidade"));
    Set(varUnidadesVelhas, false)
  )
```

After any `Patch` on the domain: `Set(varUnidadesVelhas, true)`.

**When not to cache.** Transactional data that another user changes in parallel; a table above
2,000 rows (the collection truncates). If it is already a named formula, it **already is** the
cache: do not copy it into a collection.

## 7. Controls per screen

**Problem.** Each control is a node in the dependency engine; each property is a formula
re-evaluated. **Symptom.** The screen is slow to paint; interaction lag with no network.

- There is no official limit of controls per screen; the guideline is qualitative. The common
  review metric (Power CAT Code Review Tool) flags more than ~300 controls per screen
  ([CODE_REVIEW.md](https://github.com/microsoft/Power-CAT-Tools/blob/main/CODE_REVIEW.md)).
  The numbers "500 per app / 300 per screen" are a community recommendation.
- Inside the **gallery template**, more than ~10 controls calls for review: with 30 visible rows,
  40 controls per row are ~1,200 instances.
- **Collapse label and value into a single control**; one aggregated `HtmlViewer` per block instead
  of several pairs. `HtmlViewer` does **not** replace `Label` for performance (it is more
  expensive): for a simple pair use `Label` with `FontWeight`.
- **One container per visual block, with `Visible` on the container**, not on each child: hundreds
  of individual `Visible` properties are hundreds of formulas re-evaluated on every tab switch.
- A screen with 300+ controls is usually three screens; but do not split if that creates a
  reference between screens (the cure kills deferred loading).
- Nested containers: at most 3 to 4 levels; gallery, at most 2 levels of nesting
  ([Gallery](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-gallery)).

## 8. `With` and recomputation

`With` avoids evaluating the same subexpression five times (and a repeated `LookUp`, a disguised
N+1). Use it for **scalars and constants**, never to wrap a data source expecting delegation (see
[delegation.md](delegation.md) §8). A value read by several controls: named formula, not `With`.

Destination: YAML pasted into Studio.

```yaml
# Gallery.Items over an already loaded collection
Items: |-
  =With(
    {
      fTipo: Coalesce('xx-cbo-filtro-tipo'.Selected.Value, "All"),
      fCodigo: varCodigoSelecionado
    },
    Filter(
      colDados,
      (fTipo = "All" || Tipo = fTipo) && (IsBlank(fCodigo) || Codigo = fCodigo)
    )
  )
```

## 9. Images and media

Prefer `.svg` over `.png` for icons and logos. Use the Dataverse thumbnail (~1 KB, comes in the
response); the full image requires a separate call and **never goes in a gallery**
([Efficient calculations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/efficient-calculations)).
`User().Image` repeated in the header of every screen is one Graph call per screen: a value that is
immutable during the session is a named formula (`frmUsuarioFoto = User().Image`).

## 10. Query in a UI property

**Problem.** `Visible`, `Text`, `Fill`, `DisplayMode` and `Start` are re-evaluated on every
dependency change: a query in them is network per render (invisible N+1; 429 throttling).
**Solution.** Calculate once as a named formula and read from it.

Destination: App object formula bar, `Formulas` property (en-US).

```powerfx
frmTemHistorico = !IsEmpty(Historico);
```

`CountIf(t, cond) > 0` is cheaper than `CountRows(Filter(t, cond)) > 0` where `CountIf`
delegates (Dataverse): the first aggregates on the server, the second materializes. Acceptable only
in the property of **one** control (outside a gallery) read once per session, and even then the
named formula is better.

## 11. Global `Set` fanout

Each global `Set` invalidates every control that references it: 150 `Set` calls in one transaction
are 150 waves of invalidation (a 1 to 3 s freeze with no network in the Monitor). **A list of values
is a collection, not N numbered variables.** A global `Set` is right for shared UI state, of low
cardinality and few readers (`varShowLoading`, `varShowToast`).

## 12. Connector limit

Keep **at most 10 connectors and 20 connection references** per app; above that, loading gets
slower and saving may fail
([Connections list](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections-list)).
The "30" figure that circulates in the community comes from old documentation.
Consolidating flows with a similar contract into one, with an `acao` parameter, reduces connectors;
do not consolidate flows with very different security or SLA. Instantiating a flow costs ~0.6 s
([Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)).
Two tables with nearly identical names (singular and plural) may be the same table added
twice: each one counts as a connection.

## 13. Loading coverage

**Problem.** A long operation with no feedback: the user clicks again and fires it twice.
**Solution.** Every button that calls a flow, or runs a heavy chain, turns on `varShowLoading`
beforehand and turns it off **on every exit path**, and disables itself meanwhile:
`DisplayMode: =If(varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)`. Full flow in
[flow-call.md](flow-call.md); overlay block in [ux-feedback.md](ux-feedback.md).

**When not to use a blocking overlay.** An operation under ~300 ms (the flicker bothers more than
the wait) and an operation during which the user can keep working: use a local indicator on the
button.

## 14. How to measure

- **Live monitor** (*Advanced tools > Open live monitor*; in the published app, app menu >
  Live monitor > Play published app): every call, rows, duration. Requires Environment Admin or
  Maker. It is the only reliable way to prove a data bottleneck
  ([Monitor](https://learn.microsoft.com/en-us/power-apps/maker/monitor-overview)).
- `Settings > Debug published app` shows the formulas in the published app's Monitor, but
  *"has a detrimental impact on the performance of your app for all your users"*: turn it on,
  measure, turn it off.
- Tenant metrics (Managed Environments): open rate, time to interactive (TTI), time to full load
  (TTFL), data latency; 75th percentile, recalculated every 24 h
  ([Monitor app performance](https://learn.microsoft.com/en-us/power-apps/maker/common/monitor-app-performance)).
- Stopwatch inside the app: `Set(varT0, Now())` before and
  `DateDiff(varT0, Now(), TimeUnit.Milliseconds)` after.

Diagnostic checklist (each item is binary):

1. **Data row limit = 1** on a clone: a list that disappears has a nondelegable query.
2. App checker: is there an "Inefficient Delay Loading"? Is there a delegation warning? Note the control and formula.
3. Live monitor at boot: requests **before** the first paint (goal: 0 to 2).
4. Live monitor with 60 s idle on the screen: is there a recurring request (timer or UI query)?
5. Live monitor while scrolling the gallery: one per page (good) or one per row (N+1)?
6. Controls per screen (above ~300) and per gallery template (above ~10).
7. Does `OnStart` have a `ClearCollect`? Migrate it.
8. Does any formula exceed 256,000 characters? Almost every slow-loading app has one
   ([Working with large apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/working-with-large-apps)).
9. Connectors at most 10; connection references at most 20.
10. Does each `IfError` have a fallback that cannot be mistaken for valid data?

## 15. Sources

- [How to create performant Power Apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-performant-apps-overview)
- [Small data payloads](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/small-data-payloads)
- [Efficient calculations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/efficient-calculations)
- [Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)
- [Working with large apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/working-with-large-apps)
- [Top performance issues](https://learn.microsoft.com/en-us/power-platform/architecture/key-concepts/performance/top-issues)
- [Monitor canvas apps](https://learn.microsoft.com/en-us/power-apps/maker/monitor-canvasapps)

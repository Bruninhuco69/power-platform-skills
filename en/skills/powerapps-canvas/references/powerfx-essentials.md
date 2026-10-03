# Power Fx essentials

Actionable reference for writing Power Fx in a Canvas app. Delegation: [delegation.md](delegation.md).
Flow call: [flow-call.md](flow-call.md). Performance: [performance.md](performance.md).

Every block states its **destination**. `yaml` blocks use the dialect of pasted YAML (`,` argument,
`;` chain, `.` decimal) and are validated by `scripts/validar-telas.py`. `powerfx` blocks use the
dialect of the en-US formula bar (`,` argument, `;` chain, `.` decimal), the same as pasted YAML.

## Contents

1. [Separators by destination](#1-separators-by-destination)
2. [Variables and scope](#2-variables-and-scope)
3. [Collections](#3-collections)
4. [Error](#4-error)
5. [Dates and time zones](#5-dates-and-time-zones)
6. [Text, number and mask](#6-text-number-and-mask)
7. [Navigation](#7-navigation)
8. [Writing: flow, Patch and form](#8-writing-flow-patch-and-form)
9. [Quick reference](#9-quick-reference)
10. [Sources](#10-sources)

---

## 1. Separators by destination

Power Fx adapts the syntax to the language of whoever edits; the saved file is invariant.

| Destination | Argument | Chain | Decimal |
|---|---|---|---|
| **Pasted YAML** (`.pa.yaml`, Code view) | `,` | `;` | `.` |
| **Formula bar** in en-US (includes `App.OnStart`, `App.Formulas`) | `,` | `;` | `.` |
| Formula bar in a pt-BR locale (only if your Studio runs in pt-BR) | `;` | `;;` | `,` |

Function names (`If`, `Filter`), properties (`Screen.Fill`), enums (`FontWeight.Bold`) and the
`.` selection operator are always in English, in any language
([Global support in Power Fx](https://learn.microsoft.com/en-us/power-platform/power-fx/global)).
Mixing the dialects in one block does not compile in either. The kit rule is in
[default-decisions.md](../../power-platform/references/default-decisions.md) §3.

In `Text()` with a format, the locale prefix is explicit and does not depend on who edits:

Destination: pasted YAML.

```yaml
# Formats
Data: =Text(Now(), "[$-en-US]mm/dd/yyyy hh:mm")
IdParaFlow: =Text(varPedido.Id_Pedido, "[$-en-US]0")
```

Without the prefix, the format is interpreted in the language of whoever edited the formula.
**`Text(<integer>)` in a pt-BR locale generates `"1.234"`** (and `"1,234"` in en-US): an id sent to
a flow or JSON always uses `[$-en-US]0` `[verified: reference project]`.
A thousands separator inside the format is ambiguous between locales; to display a count with a
thousands separator use `Text(n, "[$-en-US]#,##0")` and test it in your Studio `[unverified]`.

## 2. Variables and scope

| | Global `Set()` | Screen `UpdateContext()` | Named formula (`App.Formulas`) |
|---|---|---|---|
| Reach | app | one screen | app |
| Who writes | any formula | only the owning screen | nobody (immutable) |
| When it calculates | at the `Set` | at the `UpdateContext` | **when someone reads it** |
| Updates by itself | no | no | yes, reactive to its dependencies |
| Side effect | allowed | allowed | **forbidden** |
| Exists before `OnStart` | no | no | yes |

Prefixes: `var*` global, `ctx*` context, `col*` collection, `fx*` token/named formula. A global and
a context variable with the same name are **two variables**: on the screen, the context one shadows
the global and the `Set` writes where nobody reads. The `ctx*` prefix prevents the collision.

### 2.1 Named formula

Documented advantages: the value is always available and up to date, the definition is the single
source and the calculation can be deferred until someone reads it. Limits: no behavior function
(`Set`, `Collect`, `Patch`, `Notify`, `Navigate`), no circular reference
([App object](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)).

**Kit rule (T6): a named formula never reads a global variable.** It only recalculates when one of
its inputs changes; `Refresh()` does not re-run it and the number goes stale (this caused KPIs that
did not match in the reference projects). `[verified: reference project]`

Destination: formula bar of the App object, `Formulas` property (en-US: `,` and `;`).

```powerfx
fxColorPrimary = RGBA(15, 108, 189, 1);
fxIsCompact = App.Width < 1600;
fxRowHeight = If(fxIsCompact, 40, 50);
frmUsuarioFoto = User().Image;
```

### 2.2 Migrating from `OnStart` to `Formulas`

Microsoft's recommendation: `OnStart` can cause load problems; to cache data or create a global
variable, use a named formula; for the first screen, `StartScreen` instead of `Navigate`; for
screen logic, `OnVisible`
([App object](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)).
With `OnStart` **non-blocking** (the current default), a variable initialized in it may not be
ready when another rule reads it, and a screen may render before it finishes.
`StartScreen` does not see globals or collections; only named formulas.

| The value... | Goes to |
|---|---|
| never changes after being calculated (theme, `User()`, derived values) | `App.Formulas` |
| changes by user action | `App.OnStart` (initialization) or `OnVisible` |
| only exists on one screen | `UpdateContext` in `OnVisible` |
| depends on an action (`Patch`, `.Run()`) | never in `Formulas` |

Template: [app-onstart-template.md](../assets/app-onstart-template.md).

### 2.3 User-defined function

`App.Formulas` accepts a typed function, useful for the scope predicate or the color by status.

Destination: formula bar of the App object, `Formulas` property (en-US: `,` and `;`).

```powerfx
CorDoStatus(status: Text): Color =
    Switch(
        status,
        "open", fxBadgeInfoText,
        "completed", fxBadgeSuccessText,
        fxBadgeNeutralText
    );
```

`[unverified: availability of user-defined functions in your tenant]`

## 3. Collections

Destination: pasted YAML.

```yaml
# Collections
Carregar: =ClearCollect(colUnidades, ShowColumns(Unidade, "Cod_Unidade", "Nom_Unidade"))
Acrescentar: =Collect(colSelecionados, ThisItem)
Remover: =RemoveIf(colSelecionados, Id_Pedido = ThisItem.Id_Pedido)
```

- `ClearCollect` always downloads into memory: it **never delegates** (cap 500/2,000 rows).
- **A collection of records has no `.Value`.** `Self.Selected.Value` returns blank; use the column
  name (`Self.Selected.Sigla`). The gallery that filters by it opens empty with no error.
- **Invert `ForAll` + `Collect`**: `Collect(target, ForAll(source, {...}))` notifies the
  dependents once; `ForAll(source, Collect(target, {...}))` notifies on every iteration
  ([Efficient calculations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/efficient-calculations)).
- `ThisRecord` disambiguates scope inside `ForAll`, `Filter`, `With`; qualify it when the column
  name may collide with a variable.
- `Concurrent(...)` only for **independent** calls; the start and finish order is
  unpredictable and, with a dependency between branches, the result is indeterminate
  ([Concurrent](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-concurrent)).
  It is not for trivial `Set` calls (pure CPU, no I/O).
- **`Gallery.AllItems` is expensive**: it generates a new table on every read. To count, use
  `Gallery.AllItemsCount`. `AllItems` only sees what has already loaded (gallery paging is
  ~100 rows): "select all" on a gallery that was not scrolled gets only the first page.

## 4. Error

### 4.1 `IfError`

Destination: pasted YAML.

```yaml
# Error
Fluxo: |-
  =IfError(
    Set(varRet, 'app-flow-pedido-acao'.Run("encerrar", "1")),
    Trace("Failure: " & FirstError.Message);
    Set(varRet, Blank())
  )
```

`FirstError` and `AllErrors` carry `Kind`, `Message`, `Source`, `Observed` and
`Details.HttpStatusCode`. `IfError` requires the **Formula-level error management** feature
(*Settings > Updates > Retired*): if it is off, `IfError` does not work properly
([IfError](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-iferror)).
Check it before relying on `IfError` in a legacy app.

### 4.2 Why a magic value is wrong

- The fallback value is **coerced to the type of the first argument**; `IfError(1/x, "#DIV/0!")`
  becomes another error.
- `IsError` and `IsBlankOrError` consume the error: nothing reaches `App.OnError`, the log or the Monitor.
- `Blank()` reintroduces the ambiguity that error handling solved (database null vs. error).
- `OnError` only controls the **reporting**; it does not replace the value.

Rule: a fallback is only acceptable if it is impossible to confuse with a real result **and** the UI
flags the degraded state. `IfError(count, 50000)` fails both (50,000 is the Dataverse aggregation
cap). `Blank()` + `If(IsBlank(x), "-", x)` + an error color passes.

### 4.3 Pass on the unexpected error

Destination: pasted YAML.

```yaml
# Error2
Dividir: =IfError(a / b, If(FirstError.Kind <> ErrorKind.Div0, Error(FirstError), -1))
```

### 4.4 `App.OnError`

Destination: formula bar of the App object, `OnError` property (en-US: `,` and `;`).

```powerfx
Trace($"Error {FirstError.Message} in {FirstError.Source}");
Error(FirstError)
```

`OnError` is evaluated concurrently; use `With` for local values.

## 5. Dates and time zones

- Construction: `Today()`, `Now()`, `Date(2026, 7, 29)`, `DateValue("07/29/2026", "en-US")`.
- Arithmetic: `DateAdd(x, n, TimeUnit.Days)`, `DateDiff(a, b, TimeUnit.Days)`.
- **Date arithmetic always on the constant side, never on the column side**: `DateAdd(column, ...)`
  does not delegate. A date filter behind a gateway has its own rule (integer column `Ref_*`):
  [delegation.md](delegation.md) §Dates.
- Time zone: a *User local* column is converted on display; *Date only* and *Time-zone independent*
  are not. `TimeZoneOffset()` does not delegate; convert the **variable** before filtering.
- UTC data and a local `DatePicker` shift the day cutoff by up to a few hours: decide on **one**
  rule (UTC in the database, conversion in a single place) `[verified: reference project]`.
- For a flow, send **text with an explicit format** (`yyyy-mm-dd` or ISO 8601), never a raw date.

Destination: pasted YAML.

```yaml
# Dates
ParaFlow: =Text('xx-dtp-filtro'.SelectedDate, "yyyy-mm-dd")
ParaTela: =Text(ThisItem.Dt_Inclusao, "[$-en-US]mm/dd/yyyy")
HaTrintaDias: =DateAdd(Today(), -30, TimeUnit.Days)
```

## 6. Text, number and mask

- Text in Power Fx is **case-insensitive and accent-sensitive**; no database collation
  resolves the client side. Normalize the domain (accent, case) **at load**, not on the screen.
- `TextInput.Text` returns `""`, not `Blank()`: an optional filter tests both
  (`IsBlank(x) || x = ""`) or uses `StartsWith(col, "")`.
- `Trim()` at load on any `CHAR(n)`: SQL ignores trailing space in `=`, Power Fx
  compares literally.
- A SQL boolean (`BIT`) is a boolean in Power Fx: `Flg_Encerrar` is `true`/`false`, never `= 1`.
  Inside a delegated `Filter`, `= true` and `<> true` exclude a `NULL` row; that is why the `BIT` must
  be `NOT NULL DEFAULT 0` (a request to the database owner, `sql-procedures` skill).
- Never `Choices()` on a SQL source: there is no option set. A literal list for a fixed domain
  (`["A", "B"]`) or a collection for a table domain.

**A mask never goes into the filter**: normalize the **variable**, compare the raw column.

Destination: pasted YAML.

```yaml
# Mask
Limpar: =Substitute(Substitute(Substitute(varBusca, ".", ""), "/", ""), "-", "")
Validar: =IsMatch(varCNPJ, "^\d{14}$")
FiltroDelegavel: =Filter(Cliente, Cod_Documento = varDocumentoLimpo)
```

Applying a CNPJ mask (display only):

Destination: pasted YAML.

```yaml
# Mask2
Exibir: |-
  =With(
    { d: Substitute(Substitute(Substitute(varDocumento, ".", ""), "/", ""), "-", "") },
    If(
      Len(d) <> 14,
      varDocumento,
      Mid(d, 1, 2) & "." & Mid(d, 3, 3) & "." & Mid(d, 6, 3) & "/" & Mid(d, 9, 4) & "-" & Mid(d, 13, 2)
    )
  )
```

Text search: prefer `StartsWith(column, term)` (uses an index) over `Search` or `term in column`
(`LIKE '%x%'`, no index) and turn on `DelayOutput: =true` on the field so it does not query on every keystroke
([Optimized query data patterns](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/optimized-query-data-patterns)).

## 7. Navigation

Destination: pasted YAML.

```yaml
# Navigate
Simples: =Navigate(Pedidos, ScreenTransition.Fade)
ComContexto: '=Navigate(Detalhe, ScreenTransition.CoverRight, { ctxPedido: ThisItem, ctxModo: "edit" })'
```

- `Navigate` in `App.OnStart` is retired: it forces `OnStart` to finish before the first
  screen. Use `App.StartScreen` (named formula only).
- `Reset(control)` returns the control to its `Default`; it **does not fire `OnChange`** of the `DatePicker`
  (every Clear button rewrites the variable together with the `Reset`).

## 8. Writing: flow, Patch and form

Decision A1 ([default-decisions.md](../../power-platform/references/default-decisions.md)): **the screen
does not write directly to the source when there is a business rule.** A write with a rule goes through a flow
(which calls the procedure or writes to Dataverse); the flow decides, validates and authorizes. A rule
on the client can be bypassed and gets duplicated on every screen. App-side call:
[flow-call.md](flow-call.md).

| Situation | Path |
|---|---|
| operation with a rule, more than one effect, or that needs authorization | flow |
| a record **without** a business rule and without authorization (the user's own preference, a draft) | `Patch` with `IfError` |
| standard form | `SubmitForm`; `OnSuccess` receives `Self.LastSubmit`, `OnFailure` shows `Self.Error` |

If you use `Patch`: `Defaults(source)` creates, `LookUp(source, key)` updates, the return is the
written record (capture it with `Set`). `Patch` on a record read earlier overwrites the supplied fields
without checking for someone else's change; for a sensitive operation, re-read and compare the state first.
`ForAll(col, Patch(...))` makes one call per row; prefer `Patch` with a table of records.
On a SQL source, leave the connector account without `INSERT/UPDATE/DELETE` (only `EXECUTE`) so the
rule is structural, not just convention (`sql-procedures` skill).

After writing: `Refresh(source)` and **recount** the screen's counters (decision C5).

## 9. Quick reference

| I need... | Use |
|---|---|
| state that crosses screens | `Set(varX, ...)` |
| state for this screen only | `UpdateContext({ ctxX: ... })` |
| a constant or derived value | named formula in `App.Formulas` |
| a value before `OnStart` finishes | named formula (mandatory) |
| count over SQL | `CountRows(Filter())` + cap `fxTxtTeto`, or count on the server |
| count over Dataverse with a filter | `CountIf` (cap 50,000; see `dataverse/references/dataverse-delegation.md`) |
| text search | `StartsWith(column, term)` + `DelayOutput` |
| detect truncation | *Data row limit* = 1 on a clone |
| flow failure vs. business error | `IfError` + return `status` |
| error fallback | `Blank()` + `If(IsBlank(x), "-", x)`; never a magic number |
| send a date to a flow | `Text(d, "yyyy-mm-dd")` |
| send an id to a flow | `Text(id, "[$-en-US]0")` |
| count gallery rows | `Gallery.AllItemsCount` |
| parallelize independent loads | `Concurrent(...)` |

## 10. Sources

- [Understand delegation in a canvas app](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview)
- [App object (OnStart, Formulas, StartScreen, OnError)](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)
- [Error, IfError, IsError](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-iferror)
- [Concurrent](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-concurrent)
- [Global support in Power Fx](https://learn.microsoft.com/en-us/power-platform/power-fx/global)
- [Efficient calculations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/efficient-calculations)
- [Operators and identifiers](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/operators)
- [Create performant apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-performant-apps-overview)

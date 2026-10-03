# Anti-patterns: the most expensive

Each with the **silent symptom**, the **why** and the **fix**. Ordered by cost. Most
items are **silent** failures: the app raises no error, it just does the wrong thing. Code `T0xx` =
what the validator reports (`python <skill-folder>/scripts/validar-telas.py --codigos`).

## Contents

1. [Data and delegation](#1-data-and-delegation)
2. [Power Fx](#2-power-fx)
3. [Scope and permission](#3-scope-and-permission)
4. [Interface](#4-interface)
5. [YAML and Studio](#5-yaml-and-studio)
6. [Process](#6-process)
7. [Validator codes](#7-validator-codes)

---

## 1. Data and delegation

**D1. `CountRows`/`CountIf` over SQL without declaring the cap.** The card shows `2,000` as if it were
the total. *Why:* they do not delegate on the SQL connector; the `Filter` delegates, the count runs on the client
over what came down. *Fix:* `If(n >= fxLimiteLinhas, fxTxtTeto, Text(n))`, or a `Sum` of a column
that is 1, or count on the server. [delegation.md](delegation.md) §3. **T013** (sql-server track).

**D2. A date filter directly behind a gateway.** The gallery downloads up to the cap and filters on the client.
*Why:* a documented limitation of the SQL connector. *Fix:* an integer column `Ref_*` in the database;
an integer variable `36524 + DateDiff(Date(2000, 1, 1), x, TimeUnit.Days)`; upper bound `<=`
without `DateAdd(+1)`; Clear rewrites the variable. Never `CAST(... AS INT)` (it rounds).
[delegation.md](delegation.md) §4.

**D3. `in`/`Search` in a `Filter` over a source, and `LookUp(source)` in a gallery.** Prefer `StartsWith`. `Search` and
`"x" in column` delegate only on text (they become `LIKE '%x%'`, no index); `column in [list]`/collection
does not delegate on SQL; never `LookUp(source)` inside a gallery (a query per row, N+1).
*Fix:* `StartsWith`, equalities, a group column; the label from an `OnStart` **collection**. **T011**.

**D4. `SearchFields`/`DisplayFields`/`SortByColumns` with a column that does not exist.** Empty combo,
a search with no results, an unsorted list, no error. *Why:* `AddColumns` preserves the source
columns. *Fix:* logical name (Dataverse) / column name in the source (SQL), taken from the environment; test by typing; a filtered extract does **not** prove the
schema. **T014** (Dataverse with prefix).

**D5. `With`, `Distinct`, `FirstN` between the source and the `Filter`.** Truncates at 500/2,000, with no warning.
*Fix:* [delegation.md](delegation.md) §8.

**D6. `IfError(count, 50000)`.** The error value is the aggregation cap: indistinguishable from a
real result. *Fix:* `Blank()` and a degraded-state label.

**D7. Dirty domain data (accent, case, `CHAR` with a space).** Power Fx is accent-sensitive and
no collation resolves the client. *Fix:* normalize at load; `Trim` once in `OnStart`.

## 2. Power Fx

**F1. `.Run()` without `IfError`.** A timeout, 401 or a flow turned off leaves the result undefined; a blank
`status` passes `<> "error"` as success. *Fix:* the skeleton in
[flow-call.md](flow-call.md) §2 (loading, `IfError`, `Coalesce`, toast). **T018**.

**F2. Stuck loading overlay.** The `Set(varShowLoading, false)` was only in the success branch.
*Fix:* outside the `If`, after the `IfError`; a watchdog for the worst case
([timers-async.md](timers-async.md) §5).

**F3. `Text(<id>)` in a flow parameter.** `"1.234"` in a pt-BR locale; the flow does not find the record (closing
was irreversible). *Fix:* `Text(id, "[$-en-US]0")`.

**F4. A global used and never declared in `OnStart`.** `Blank() = 0` is false: a filter compared to 0
opens the gallery empty with no error. *Fix:* every global is born in `OnStart`
([app-onstart-template.md](../assets/app-onstart-template.md)).

**F5. A named formula that reads a global variable.** It does not recalculate on `Refresh()`; the KPI does not match.
*Fix:* a named formula only of constants and data sources.

**F6. A global and a context variable with the same name.** The context shadows; the `Set` writes where nobody reads.
*Fix:* `ctx*` for context, `var*` for global.

**F7. Dozens of numbered variables to simulate a list.** Hundreds of `Set` and of `CountRows` per filter.
*Fix:* a collection (and a grouping column in the database when `in` does not delegate).

**F8. `Set`/`Collect` inside a named formula, `Navigate` in `OnStart`.** Forbidden / retired.
*Fix:* `StartScreen`, `OnVisible`.

**F9. `Gallery.AllItems` to count or select.** A new table on every read; it only sees what is
loaded. *Fix:* `AllItemsCount`; `colSelecionados` by checkbox.

**F10. `Reset()` of a `DatePicker` thinking it clears the filter.** It does not fire `OnChange`: the control
shows one window and the `Filter` uses another. *Fix:* Clear rewrites the variable.

**F11. `.Value` on a collection of records.** Returns blank; the gallery opens empty when the
unit changes. *Fix:* the column name (`.Sigla`).

## 3. Scope and permission

**E1. A `Filter` with organizational scope without the predicate.** It delegates perfectly, never warns and
**leaks** the whole network. *Fix:* the same token (`StartsWith(col, varUnidadeFiltro)`) in every
gallery and every counter. [scope-and-permission.md](scope-and-permission.md) §5.

**E2. `""` = "all" without a fail-closed guard.** A record with no unit reads the whole network; an emptied
combo falls into "all". *Fix:* `varSemAcesso` with `(!varTodasUnidades && IsBlank(home unit))`
and an `OnChange` that returns to the home unit.

**E3. Authorization only on the screen.** The menu and the filter are UX; the client can be manipulated and the connector
account is shared. *Fix:* the flow revalidates per action; the flow reads the caller from the context (the screen does not send identity).

**E4. Permission by role name.** Breaks on rename. *Fix:* the role flag (`Flg_*`).

**E5. Write unit = "the unit I am looking at".** Writes to the wrong unit with a global
role. *Fix:* the unit is a field of the record.

**E6. `Patch` for an operation with a business rule.** The rule lives on the client, bypassable and duplicated.
*Fix:* flow (decision A1); connector account with `EXECUTE` only.

## 4. Interface

**U1. A literal `RGBA(`.** Color debt that only grows. *Fix:* an `fx*` token. **T009**.

**U2. Green on a destructive action; an emoji as a label.** Confusing and does not scale to a screen reader.
*Fix:* `fxColorError` and an explicit verb; no emoji.

**U3. `Notify()` for a flow return.** Truncates and disappears. *Fix:* a 3-type toast; `Notify`
only for form validation.

**U4. A button that calls a flow with no loading state.** A double click writes twice. *Fix:*
`DisplayMode` and `Text` bound to `varShowLoading`.

**U5. A modal above the toast or the loading.** *Fix:* order `content, modals, loading, toast`.
**T016**.

**U6. A timer with `Repeat` and no stop.** Refresh on every cycle until the user closes the app.
*Fix:* a stop rule, `Reset: =!flag`, `Start` tied to the real state and to the screen
([timers-async.md](timers-async.md) §7). A toast without `Reset`: the second inherits the first one's time.

**U7. `PressedFill` and `PressedColor` swapped.** Invisible text when pressed. *Fix:*
`ColorFade(Self.Fill, -30%)`.

**U8. Failed contrast** (light gray placeholder, white on amber, a pastel badge with mid-tone
text). *Fix:* the pairs in [design-tokens.md](design-tokens.md) §3 and §4.

**U9. A truncated list with no warning, a gallery `TemplateSize` disconnected from the content, 300+ controls
per screen, 18 `HtmlViewer` per row.** *Fix:* [performance.md](performance.md) §5 and §7.

**U10. Different margins and gutters per screen; two type families.** *Fix:* single
layout and font tokens.

## 5. YAML and Studio

**Y1. An unattested property.** PA2108 takes down the whole block. *Fix:*
[nonexistent-properties.md](nonexistent-properties.md). **T008**.

**Y2. `;;` inside `.pa.yaml`.** The formula-bar dialect of a pt-BR locale pasted into YAML does not parse.
*Fix:* `,` and `;` in the YAML; `;;` only in a pt-BR formula bar. **T007**.

**Y3. A property without `=`, `Control` without `@version`, `Control` with a formula, a repeated key, a duplicate
name.** Studio refuses. **T002, T004, T005, T012, T006**.

**Y4. A one-line formula with `: ` or ` #`, or a record literal `{a: 1}` without quotes.** Breaks the
parse or **truncates the formula silently**. *Fix:* YAML single quotes around the whole
formula, or `|-`. **T001, T015**.

**Y5. `#` as a comment inside `|-`.** It becomes text and Power Fx rejects it. *Fix:* `//`.

**Y6. Pasting a block without renaming the prefix.** Studio renames to `_1`, `_2`.

**Y7. Validating only with the script.** The validator is not a sufficient gate: script **and** paste into
Studio **and** *Data row limit* = 1.

## 6. Process

**P1. Writing against the dictionary instead of the real environment.** Column name, type and prefix
diverge from what exists. *Fix:* `AS-BUILT-NAMES` first (`dataverse` skill).

**P2. "DONE" without evidence.** Marking a task done with no command and output: the regression comes back
(a scope fix was erased by a generator that rewrote the file). *Fix:* an Evidence column
(`power-platform` skill).

**P3. Blocks replicated by hand that diverge** (identical counters, menu and loading and
toast repeated across several screens). *Fix:* a single place when possible (user-defined function, component
library) and, while replicated, mark `BLOCK n of N`.

**P4. Outdated documentation living alongside the current one.** *Fix:* a "what is current" index per
folder and a review date.

**P5. Two live data tracks** (SQL and Dataverse) with docs pointing to the wrong one. *Fix:*
one active track per layer, declared in `trilha_dados` (decision A4).

## 7. Validator codes

| Code | Level | What it reports |
|---|---|---|
| T001 | ERROR | YAML does not parse (line of the error) |
| T002 | ERROR | property without `=` |
| T003 | ERROR | control without `Control:` |
| T004 | ERROR | `Control:` without `@version` |
| T005 | ERROR | `Control`/`Variant` with a formula |
| T006 | ERROR | duplicate control name in the set |
| T007 | ERROR | `;;` in the YAML |
| T008 | ERROR or WARNING | property rejected (PA2108); WARNING on another control version |
| T009 | WARNING | literal `RGBA(` |
| T010 | WARNING | name not in kebab-case |
| T011 | WARNING | `Search(`/`in` in `Filter(` over a source that is not `col*` |
| T012 | ERROR | duplicate key |
| T013 | WARNING | `CountRows`/`CountIf` over a SQL source (`sql-server` track) |
| T014 | WARNING | column without a prefix in `DisplayFields`/`SearchFields`/`SortByColumns` (`dataverse` track) |
| T015 | WARNING | ` #` after a one-line formula |
| T016 | WARNING | z-order of the screen's `Children` |
| T017 | ERROR | invalid structure (`Properties`/`Children`) |
| T018 | WARNING | `.Run(` without `IfError(` |
| T020 | WARNING | not a YAML screen, ignored |
| T022 | ERROR | top-level key outside the schema |

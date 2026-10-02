---
name: powerapps-canvas
description: "Use when the work is Power Apps Canvas: creating or changing a screen, gallery, modal, toast, loading, filter, tab or form; writing or fixing Power Fx formulas; generating or reviewing .pa.yaml YAML to paste into Studio (\"won't paste\", PA2108, `;` or `;;`); a combo box/ComboBox that can't find the value (SearchFields, DisplayFields); delegation on the SQL connector (\"the gallery comes back empty\", \"the counter shows 2,000\", CountRows, date filter); timers, auto-refresh and debounce; the app side of a flow's .Run() call (loading, IfError, toast); fx* tokens, naming, accessibility and role and unit scope on the screen. Do not use for a KPI vs gallery mismatch with no obvious cause (use `power-platform`), flow definition, Try/Catch and HTTP (use `power-automate`), procedures, DDL and computed columns (use `sql-procedures`), tables, Choice, Security Role and Dataverse delegation (use `dataverse`), ALM, Power BI, model-driven apps or Power Pages."
argument-hint: "[screen|component|formula|audit|refactor|performance] [target]"
user-invocable: true
---

# Power Apps Canvas

Produces and reviews Canvas screens as **`.pa.yaml` YAML you can paste into Studio** and Power Fx
in the right dialect for the destination. Default: ManualLayout + Classic controls, 1920x1080
canvas, `fx*` tokens, writes always through a flow. The kit's decided defaults (app and flow
contract, separators, screens, names) are in
[default-decisions.md](../power-platform/references/default-decisions.md); this skill applies them.

## Non-negotiable rules

1. **Separator by destination.** Pasted YAML: `,` between arguments, `;` chains, `.` decimal.
   Studio formula bar in en-US (`App.OnStart`, `App.Formulas`): `,`, `;`, `.`. Never `;;` in YAML
   (it is the pt-BR formula-bar chain). Every code block states its destination. Why: mixing them
   parses in neither.
2. **YAML valid by the schema.** Every property starts with `=`; 2-space indentation;
   `Control: Type@version` with the app's version; multi-line formula in `|-`; `Control` and
   `Variant` without a formula; the order of `Children` is the z-index. Why: Studio validates
   before pasting and rejects the whole block.
3. **Only properties attested on that control type.** Before emitting a new property, look for it
   on the same type already used in the app; known rejections in
   [nonexistent-properties.md](references/nonexistent-properties.md). Why: one nonexistent
   property (PA2108) brings down the whole block.
4. **Color, font, size and text by `fx*` token.** No `RGBA(` literal on a screen. Why: one
   value, one place; migrating literals later is manual and expensive.
5. **Delegation declared in writing.** Every `Filter`, `LookUp`, `CountRows` and date filter has
   its delegation checked and declared in the screen header, and the cap shows in the UI
   (`2,000+`). Prefer `StartsWith`. `Search` and `"x" in column` delegate only on text (they become `LIKE '%x%'`, no index); `column in [list]`/collection does not delegate on SQL; never `LookUp(source)` inside a gallery.
   Why: silent failure, no error and no warning. [delegation.md](references/delegation.md)
6. **Every `.Run()` call inside `IfError`**; success is `status <> "error"` (a blank response is an
   error); ids with `Text(id, "[$-en-US]0")` (YAML); after writing, `Refresh` and recount.
   Why: a timeout or a disabled flow leaves the overlay stuck or closes the modal as a success.
   [flow-call.md](references/flow-call.md)
7. **The screen does not write directly with business rules and does not authorize.** Writes go
   through a flow; permission on the screen is a role flag (UX); no resolved role, no access
   (fail-closed). Why: the client can be tampered with and the connector account is shared.
   [scope-and-permission.md](references/scope-and-permission.md)
8. **Every global is born in `OnStart`; a named formula does not read a global.** Why: `Blank() = 0`
   is false (empty gallery, no error) and a named formula does not recalculate with `Refresh()`.
9. **The name comes from the real environment**, not the dictionary: column, table and prefix from
   `AS-BUILT-NAMES` (skill `dataverse`); a filtered extract does not prove the schema. Why: a wrong
   column in `SearchFields`/`SortByColumns` gives no error.
10. **The validator is not a sufficient gate: the gate is the script plus pasting into Studio**
    (and *Data row limit* = 1 on a clone). Why: the script only sees what is in the file; PA2108
    and delegation are confirmed only by Studio.
11. **End of the screen's `Children`: content, modals, loading, toast. Every timer has a stop
    rule.** Why: a modal above the toast and a `Repeat` with no stop were real defects.

## Workflow

### 1. Load only what the task requires

| Task | Load |
|---|---|
| new screen or component | **catalog first**: [assets/components/INDEX.md](assets/components/INDEX.md) (25 pasteable components); then `assets/screen-template.md`, [ux-components.md](references/ux-components.md), [pa-yaml-format.md](references/pa-yaml-format.md), [naming.md](references/naming.md) |
| modal, toast, loading | [ux-feedback.md](references/ux-feedback.md), [flow-call.md](references/flow-call.md) |
| Power Fx formula | [powerfx-essentials.md](references/powerfx-essentials.md) |
| data, filter, counter, date, "comes back empty" | [delegation.md](references/delegation.md) |
| slow app, laggy gallery | [performance.md](references/performance.md), [delegation.md](references/delegation.md) |
| auto-refresh, debounce, polling, toast that won't go away | [timers-async.md](references/timers-async.md) |
| button that writes (calls a flow) | [flow-call.md](references/flow-call.md) |
| role, unit, "sees another unit's data" | [scope-and-permission.md](references/scope-and-permission.md) |
| color, font, size, messages | [design-tokens.md](references/design-tokens.md), `assets/app-formulas-tokens.md` |
| `OnStart` and globals | `assets/app-onstart-template.md` |
| contrast, focus, screen reader | [accessibility.md](references/accessibility.md) |
| "PA2108", "won't paste" | [nonexistent-properties.md](references/nonexistent-properties.md), [pa-yaml-format.md](references/pa-yaml-format.md) |
| auditing a screen | [anti-patterns.md](references/anti-patterns.md), [style.md](references/style.md) and whatever the finding points to |

Large screen file: never read it whole; `Grep` to locate and `Read` in windows of 200 to 400
lines.

### 2. Before generating, answer for yourself

- Which screen and which prefix? What is the data track (`trilha_dados` in
  `power-platform.config.json`)?
- Which sources and **real columns**? Are they delegable for the requested filter? What is the cap?
- Does the data go in `OnStart`, `OnVisible`, a named formula or on demand?
- Is there already an equivalent block in [ux-components.md](references/ux-components.md)? Reuse it.
- Does this action need a flow (business rule, more than one effect, authorization)? If so, the
  flow belongs to the `power-automate` skill; here, only the screen side.

### 3. Deliver, in this order

1. **The finished YAML or Power Fx**, with no placeholder the user has to guess.
2. **How to apply it**, in **one** of the three ways (detail in
   [pa-yaml-format.md](references/pa-yaml-format.md) §7): *Code view* (control block, name the
   parent control); *formula bar* (single property: control and property); *App object*
   (`OnStart` and `Formulas`: type it in; there is no Code view for App). State the **dialect**.
3. **Warnings**: delegation and cap, dependency on an uninitialized variable, performance impact,
   what was not verified in Studio.

### 4. Validate

Run the script **and** paste into Studio (rule 10). Fix before answering: do not deliver YAML
that Studio will reject.

### 5. Sub-commands

`/powerapps-canvas <sub> <target>`; with no sub-command, infer it from the question.

| Sub | Does |
|---|---|
| `screen <name>` | full screen from `assets/screen-template.md` |
| `component <type>` | block from [ux-components.md](references/ux-components.md): `header`, `kpi`, `tabs`, `filters`, `gallery`, `badge`, `modal`, `loading`, `toast`, `selection`, `empty` |
| `formula <description>` | Power Fx with verified delegation and error handling; states the property and the dialect |
| `audit <file\|screen>` | findings with severity, `file` and validator code, on 5 axes: data and delegation, performance, UX, accessibility, conventions |
| `refactor <snippet>` | before and after, with the expected gain, keeping the behavior |
| `performance` | what loads when, what becomes a named formula, what is deferred, what runs in parallel, which timers run |

## References

| File | When to read |
|---|---|
| [pa-yaml-format.md](references/pa-yaml-format.md) | grammar, escaping, indentation, control versions, pasting into Studio |
| [powerfx-essentials.md](references/powerfx-essentials.md) | variables, collections, errors, dates, text, navigation, Patch vs flow |
| [delegation.md](references/delegation.md) | what delegates (SQL and Dataverse), cap, counting, `Ref_*` date, search |
| [performance.md](references/performance.md) | `OnStart`, `Concurrent`, deferred load, paging, measuring |
| [timers-async.md](references/timers-async.md) | Timer: auto-refresh, debounce, toast, timeout, polling |
| [flow-call.md](references/flow-call.md) | button that writes: loading, `IfError(.Run)`, toast, refresh |
| [scope-and-permission.md](references/scope-and-permission.md) | flags by role, fail-closed, `""` = all, write unit |
| [ux-components.md](references/ux-components.md) | corrected block catalog (header, filters, gallery, buttons) |
| [ux-feedback.md](references/ux-feedback.md) | modal, loading, toast |
| [design-tokens.md](references/design-tokens.md) | `fx*` families, contrast, typography, grid, messages |
| [accessibility.md](references/accessibility.md) | WCAG AA checklist and platform limits |
| [naming.md](references/naming.md) | control, variable, collection, token, flow |
| [nonexistent-properties.md](references/nonexistent-properties.md) | PA2108 table and how to verify in Studio |
| [style.md](references/style.md) | file anatomy, golden files, gate, Classic decision |
| [anti-patterns.md](references/anti-patterns.md) | the costliest ones, with why, fix and validator code |
| [field-lessons.md](references/field-lessons.md) | what already went wrong in real apps and which rule prevents it |
| [assets/components/INDEX.md](assets/components/INDEX.md) | catalog of pasteable components (header, side menu, top menu, home with cards, filters, table gallery, modals, toast, loading…): one `.md` per component, validated |
| [assets/screen-template.md](assets/screen-template.md) | complete, pasteable YAML screen |
| [assets/app-formulas-tokens.md](assets/app-formulas-tokens.md) | `App.Formulas` block with the tokens |
| [assets/app-onstart-template.md](assets/app-onstart-template.md) | `App.OnStart` in dependency order |

## Scripts

Reads fenced blocks and plain YAML (no false green). Read-only; reads `power-platform.config.json` (`pastas.telas`,
`telas_formato`, `ignorar`, `trilha_dados`, `prefixo_publisher`) walking up the directories or via
`--config`. Run **from the project root** (the script looks for `power-platform.config.json` from the
current directory upward) or pass `--config`; the skill folder appears as *Base directory*
when the skill is loaded.

| Command | What it checks | Exit |
|---|---|---|
| `python <skill-folder>/scripts/validar-telas.py <file-or-folder>` | parse with line (T001), `=` (T002), `Control@version` (T003 to T005), duplicate name (T006), `;;` (T007), PA2108 (T008), `RGBA(` (T009), kebab-case (T010), `in`/`Search` (T011), repeated key (T012), `.Run(` without `IfError` (T018), z-order (T016) | 0 no errors, 1 with errors, 2 wrong usage |
| `python <skill-folder>/scripts/validar-telas.py --trilha sql-server <folder>` | adds `CountRows`/`CountIf` without delegation (T013) | same |
| `python <skill-folder>/scripts/validar-telas.py --codigos` | lists the codes | 0 |

`auto` format: a `.md` with ```` ```yaml ```` blocks validates each block; a `.md` without fences is plain YAML,
read whole; a file that is not a screen (documentation, formula-bar block) produces **one** T020 warning. A block with
`# validador: ignorar` is skipped. Full table of codes in
[anti-patterns.md](references/anti-patterns.md) §7.

## Definition of done

- [ ] `python <skill-folder>/scripts/validar-telas.py <screen>` returns `0 error(s)` (warnings justified in writing).
- [ ] The block was **pasted into Studio** with no `PA2108` (evidence: the control shows in the tree).
- [ ] *Data row limit* = 1 on a clone: the gallery still lists (evidence: non-empty list).
- [ ] Delegation header written; counters with the `fxTxtTeto` cap (grep for `CountRows`).
- [ ] `grep -c "RGBA(" <screen>` = 0 outside the multi-line status formula.
- [ ] Every button that calls a flow: `IfError`, `varShowLoading` turned off on every path,
      tested with the flow disabled (evidence: red toast, overlay closed).
- [ ] Every scoped source `Filter` has the predicate (grep the `Filter(` calls).
- [ ] Contrast >= 4.5:1 and Accessibility checker with no new error (evidence: checker report).
- [ ] Timers with a stop (`Reset: =!flag`, `Start` tied to the screen); `.Run()` outside `Items`.
- [ ] Destination dialect declared in every delivered block.

## Pitfalls

The ten costliest (detail and fix in [anti-patterns.md](references/anti-patterns.md)):

1. `CountRows` over SQL showing the cap as the total: [delegation.md](references/delegation.md) §3.
2. `.Run()` without `IfError`; stuck overlay: [flow-call.md](references/flow-call.md).
3. Direct date filter behind a gateway: `Ref_*` column: [delegation.md](references/delegation.md) §4.
4. Scoped `Filter` without the unit predicate (silent leak): [scope-and-permission.md](references/scope-and-permission.md) §5.
5. `;;` in YAML or `;` as argument separator in the en-US formula bar: [pa-yaml-format.md](references/pa-yaml-format.md) §2.
6. Unattested property bringing down the block (PA2108): [nonexistent-properties.md](references/nonexistent-properties.md).
7. `SearchFields`/`SortByColumns` with the wrong column (silent failure): [delegation.md](references/delegation.md) §7.
8. Timer with `Repeat` and no stop, and a toast without `Reset`: [timers-async.md](references/timers-async.md) §7.
9. Single-line formula with `: ` or ` #` (breaks or truncates): [pa-yaml-format.md](references/pa-yaml-format.md) §4.
10. Global not declared in `OnStart` (`Blank() = 0`): [app-onstart-template.md](assets/app-onstart-template.md).

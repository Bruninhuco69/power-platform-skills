# Canvas screen style

Style rules extracted from a reference app with several screens and over a thousand controls (full
YAML parse), generalized. The goal: a new screen **looks written by the same hand**. Complements
[naming.md](naming.md), [design-tokens.md](design-tokens.md) and
[ux-components.md](ux-components.md).

## Contents

1. [Golden files](#1-golden-files)
2. [Anatomy of the screen file](#2-anatomy-of-the-screen-file)
3. [Layout](#3-layout)
4. [Controls](#4-controls)
5. [Colors and text](#5-colors-and-text)
6. [Operation feedback](#6-operation-feedback)
7. [What not to do](#7-what-not-to-do)
8. [Verification gate](#8-verification-gate)
9. [Recorded decision: Classic + ManualLayout](#9-recorded-decision-classic--manuallayout)

---

## 1. Golden files

Every project picks a few exemplar files and **starts a new screen by copying one of them**, never
from a blank sheet:

| Exemplar | What it demonstrates |
|---|---|
| the leanest, most complete screen in the project | the whole anatomy (new screen template) |
| the navigation shell | menu and "no access", reusable almost entirely |
| the App object's `Formulas` block | token and message catalog |

The kit's template is [screen-template.md](../assets/screen-template.md). Record the project's golden files
in `00-READ-ME-FIRST.md`.

## 2. Anatomy of the screen file

Order of `Children`, which **is** the z-order:

```text
1. header (title, user, divider)
2. tabs (if any)
3. filters
4. KPIs
5. column headers + gallery + empty state + truncated
6. no-access panel
7. modals
8. loading
9. toast  (always last)
```

Screen properties: `Fill`, `Height`, `Width`, `LoadingSpinnerColor`, `OnVisible`. `OnVisible`
**clears what the previous screen left behind** (modal, selection, loading, toast) and recomputes counters,
with no heavy I/O. The file's header comment declares the delegation
([delegation.md](delegation.md) §11).

Source file conventions (`.pa.yaml` in `.md`):

- Comment at the top with `#` (the file is pure YAML; `//` outside a formula breaks the parse);
  inside a formula `//` and `/* */` work.
- Standardized comment markers help review: `[FIX]` (pre-existing defect fixed)
  and `DECIDE:`. **Never delete a `NOTE:` without replacing it**: it documents
  a trap; if the trap is gone, it becomes `resolved: <what>`.
- Properties in alphabetical order and without repeating the control's default (Studio reorders and deletes
  them on the first paste).
- Every property value starts with `=`; a multiline formula uses `|-`.

## 3. Layout

- **ManualLayout with absolute `X`/`Y`, 1920 by 1080 canvas.** It is not a preference: it is what the
  canonical blocks assume (`X: =Parent.Width - Self.Width - 20`).
- Responsiveness by a **conditional token** (`fxIsCompact`), not by AutoLayout.
- Centering by formula: `X: =(Parent.Width - Self.Width) / 2`.
- A modal's button pair sizes itself: `Width: =(Parent.Width - fxModalPadding * 3) / 2`.
  Never a magic width.
- `Wrap: =false` on every single-line `Label` (navigation, tab, column header, badge, KPI) and
  explicit padding (the default 5 misaligns); see [pa-yaml-format.md](pa-yaml-format.md) §9 for what
  is attested.

## 4. Controls

Use what the app **already uses**, **always with `@version`** (T2):

| Function | Control |
|---|---|
| text | `Label@2.5.1` |
| button, tab, rounded shape | `Classic/Button@2.2.0` |
| container, modal, veil | `GroupContainer@1.5.0` |
| text input | `Classic/TextInput@2.3.2` |
| selection | `Classic/ComboBox@2.4.0` |
| list | `Gallery@2.15.0` |
| date | `Classic/DatePicker@2.6.0` |
| loading | `Spinner@1.4.6` |

Mixing modern and Classic controls without a plan creates islands (modern buttons in the menu coexisting
with hundreds of classic ones in the body) and formulas that change property (`FontSize` to `Size`).

## 5. Colors and text

- **Zero `RGBA()` literals in a new screen.** Migrating literals to tokens is expensive and
  partly manual work: do not recreate the debt.
- Primary action `fxColorPrimary`; destructive `fxColorError`; **never green to confirm a
  cancellation** (a real defect already seen in several modals).
- Modal button pair: left `fxTxtVoltar` gray, right = **the action's verb**. Radius 8,
  height 45.
- Every visible string comes from the `fxMsg*` and `fxTxt*` catalog.

## 6. Operation feedback

| Situation | Mechanism |
|---|---|
| flow or procedure return | **toast** (`varShowToast`, `varToastType`, `varToastMessage`) |
| form validation | `Notify()` |
| operation in progress | `varShowLoading` + `varLoadingMessage` + overlay |
| button during processing | `DisplayMode` and `Text` tied to `varShowLoading` |

`varToastType` is `"success"`, `"warning"` (partial batch) or `"error"`; duration by token
(6,000, 12,000 and 15,000 ms), never on the control.

## 7. What not to do

Summary; each item with the why and the fix in [anti-patterns.md](anti-patterns.md).

1. Literal `RGBA()` in a screen.
2. Emoji as semantics (`✅ Yes, Cancel`).
3. Green on a destructive action.
4. `Notify()` for a flow return.
5. Automatic name (`Button1_38`).
6. Unattested property (PA2108 takes down the block).
7. `Timer` with `Repeat` and no stop rule.
8. Gallery filter as access control.
9. Direct `Patch` for an operation with a business rule.
10. `in` and `Search()` in `Filter` over a large table.

## 8. Verification gate

Before calling the screen done (no item is a declarative "✅": each one has a command):

1. `python <skill-folder>/scripts/validar-telas.py <screen>`: parse of the **whole** file (broken indentation
   dies here), `;;`, PA2108, `Control` without a version, literal `RGBA(`, z-order.
2. Grep for `RGBA(` outside formulas: zero in a new screen.
3. Grep for the refused properties ([nonexistent-properties.md](nonexistent-properties.md)):
   zero.
4. `Wrap: =false` on single-line labels; explicit padding.
5. Final order of `Children`: content, modals, loading, toast (T016).
6. **Paste into Studio** and check that `PA2108` did not come back.
7. *Data row limit* = 1 on a clone: the list still lists.
8. Flow with the flow turned off: error toast and overlay closed.

The MCP `compile_canvas` does not catch what breaks at runtime, and the validator does not replace Studio:
the gate is **script plus paste into Studio**.

## 9. Recorded decision: Classic + ManualLayout

The platform's generic guides (DesignGuide and TechnicalGuide of the `canvas-apps` plugin) recommend
modern controls and responsive AutoLayout. The real code of the reference projects does the opposite, by
a wide margin (Classic far ahead of modern; ManualLayout on every screen). **Decided: follow the real
code**, because the canonical blocks, the tokens and the PA2108 gate were built on Classic
and ManualLayout; adopting the generic guide would reopen a class of error already closed and would cost rewriting
the catalog. Reverting is an ADR decision (T1), not a matter of preference. The generic guide's "bold
aesthetics" advice also does **not** apply as a rule in a corporate design system.

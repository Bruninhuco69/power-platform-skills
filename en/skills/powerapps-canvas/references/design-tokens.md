# `fx*` design tokens

Color, typography, layout, component and text as **named formulas** of the App object. The values
are in [app-formulas-tokens.md](../assets/app-formulas-tokens.md) (single source); here are the
families, the usage rules and the reasoning. Decision T3 of
[default-decisions.md](../../power-platform/references/default-decisions.md): color, font and size
only by token; no `RGBA(` literal in a screen (validator: T009).

## Contents

1. [Rules](#1-rules)
2. [Token families](#2-token-families)
3. [Color and contrast](#3-color-and-contrast)
4. [Badge with contrast](#4-badge-with-contrast)
5. [Typography](#5-typography)
6. [Layout and grid](#6-layout-and-grid)
7. [`fxMsg*` message catalog](#7-fxmsg-message-catalog)
8. [How to evolve the tokens](#8-how-to-evolve-the-tokens)

---

## 1. Rules

1. **A token is a named formula in `App.Formulas`**, never `Set()` in `OnStart`. A theme as a global
   only exists after `OnStart` finishes, slows the load and cannot be used in another named
   formula. `[verified: reference project]`
2. **A token does not read a global variable** (T6). `fxIsCompact = App.Width < 1600` is fine;
   `fxCor = varTema` is not.
3. **One name, one role.** A token defined and never used is debt; a token used for two roles
   (the same border for a decorative card and for an interactive input) is a contrast error waiting
   to happen: split it (`fxColorBorder` and `fxColorBorderInteractive`).
4. **Zero `RGBA(` literals in a new screen.** Transparent is a token too
   (`fxColorTransparent`). What is left inside a multiline formula (status `Switch`) migrates
   to `fxBadge*`.
5. **No alpha out of range**: `RGBA(255, 255, 255, 100)` is invalid (alpha goes from 0 to 1).
6. **Visible text comes from the catalog** (`fxTxt*`, `fxMsg*`), not a literal in the screen: placeholder,
   modal title and button label included. A screen title and a column label specific to the
   domain may be literals.
7. A value changes in one place only: if someone needs to edit the same color in two screens, a token is missing.

## 2. Token families

| Prefix | Content | Examples |
|---|---|---|
| `fxColor*` | brand palette, surface, text, border, state, button, tab, table, toast | `fxColorPrimary`, `fxColorTextOnPrimary`, `fxColorBorderInteractive` |
| `fxBadge*` | text/background pair by semantics | `fxBadgeSuccessText`, `fxBadgeSuccessBg` |
| `fxIsCompact` | the only breakpoint | `App.Width < 1600` |
| `fxLayout*`, `fxRowHeight`, `fxFilterHeight`, `fxKPI*`, `fxTableHeaderHeight` | measures that depend on `fxIsCompact` | `fxRowHeight = If(fxIsCompact, 40, 50)` |
| `fxFont` | the single typeface (`Font.'Segoe UI'`); every control uses `Font: =fxFont` | `fxFont` |
| `fxFontSize*` | type scale | `fxFontSizeTitle`, `fxFontSizeTable`, `fxFontSizeToast` |
| `fxBtn*`, `fxModal*`, `fxLoading*`, `fxToast*` | component geometry and timing | `fxBtnHeight`, `fxToastDurationError` |
| `fxLimiteLinhas`, `fxTxtTeto`, `fxPageSize` | connector and pagination limits | `fxLimiteLinhas = 2000` |
| `fxTxt*` | reusable labels | `fxTxtVoltar`, `fxTxtProcessando` |
| `fxMsg*` | messages, in `...Error` and `...Hint` pairs | `fxMsgFalhaFlow`, `fxMsgFalhaFlowHint` |
| `frm*` | named formula of **data** (KPI, list) | `frmKPIAbertos` |

`fx*` is theme and text; `frm*` is derived data. Do not mix them.

## 3. Color and contrast

WCAG 2.x goal: normal text >= 4.5:1, large text >= 3:1, border and icon of an interactive
component >= 3:1 against the outer color. Values of the template's neutral palette (Fluent 2 blue ramp), measured by the
relative luminance formula `[verified: own calculation]`:

| Pair | Ratio | Use |
|---|---:|---|
| white on `fxColorPrimary` (15, 108, 189) | 5.38 | primary button |
| white on `fxColorPrimaryDark` (12, 59, 94) | 11.65 | header, menu |
| `fxColorTableHeaderText` (17, 94, 163) on `fxColorTableHeaderBg` (235, 243, 252) | 5.95 | table header |
| white on `fxColorSuccess` (21, 128, 61) | 5.02 | **state** confirmation |
| white on `fxColorError` (200, 35, 51) | 5.61 | destructive action |
| white on `fxColorButtonCancel` (108, 117, 125) | 4.69 | secondary |
| `fxColorTextOnWarning` on `fxColorWarning` (255, 193, 7) | 10.88 | text on amber |
| `fxColorTextSecondary` on white | 8.45 | label, inactive tab |
| `fxColorToastText` on `fxColorToastBg` | 7.43 | toast message |
| `fxColorBorderInteractive` (117, 117, 117) on white | 4.61 | input border |

Common failures to avoid: **white on amber** (1.63; hence `fxColorTextOnWarning`),
white on the green `(40, 167, 69)` (3.13), input border `(209, 213, 219)` (1.47) and
placeholder `(156, 163, 175)` (2.54). `fxColorBorder` (166, 166, 166) is decorative only (card):
3:1 only applies to an interactive control.

Review: open the Studio Accessibility checker after changing the palette
([accessibility.md](accessibility.md)).

## 4. Badge with contrast

Pattern: **dark text on a pastel of the same hue**, with text or an underline alongside (never color
alone). Pairs from the template, all above 4.5:1:

| Semantics | Text | Background | Ratio |
|---|---|---|---:|
| success | (22, 101, 52) | (220, 252, 231) | 6.49 |
| information | (15, 84, 140) | (207, 228, 250) | 6.05 |
| warning | (146, 64, 14) | (255, 218, 185) | 5.40 |
| danger | (139, 0, 0) | (255, 182, 193) | 6.06 |
| in progress | (133, 77, 14) | (255, 230, 100) | 5.47 |
| neutral | (52, 58, 64) | (206, 212, 218) | 7.70 |

Common pairs that **fail** (already fixed in the template): activate `(8, 145, 158)` on `(175, 236, 239)`
(2.89, becomes `(6, 95, 103)`, 5.66); review `(180, 83, 9)` on `(255, 218, 185)` (3.82, becomes
`(146, 64, 14)`); link `(25, 115, 42)` on `(163, 228, 179)` (4.06) and process
`(0, 85, 187)` on `(162, 210, 255)` (4.37).

## 5. Typography

One typeface: **`Font.'Segoe UI'`**, declared once as the `fxFont` token and used as `Font: =fxFont` (native to Fluent 2, on every client). Two typefaces
without a rule (header in one, form in another) is a defect. Hierarchy by **weight and size**:
using only `Semibold` and `Bold` flattens the hierarchy.

| Role | Size | Weight | Token |
|---|---|---|---|
| screen title | 35 (compact 28) | Semibold | `fxFontSizeTitle` |
| KPI value | 25 (compact 20) | Bold | `fxFontSizeKPI` |
| section or modal title | 16 to 18 | Bold | `fxModalTitleSize` (16) |
| body, input, message | 14 | Normal | `fxFontSizeBody` |
| table row | 13 (compact 11) | Normal | `fxFontSizeTable` |
| column header | 13 (compact 11) | Bold | `fxFontSizeHeader` |
| caption, badge | 12 (compact 11) | Normal or Semibold | `fxFontSizeTableSmall` |
| KPI label | 11 | Semibold | `fxFontSizeKPITitle` |
| toast: icon, title, message | 18, 15, 12 | Bold, Bold, Normal | `fxFontSizeToastIcon`, `fxFontSizeToastTitle`, `fxFontSizeToast` |
| access denied notice | 20 | Bold | `fxFontSizeSemAcesso` |

Floor for a form label: 12. A label smaller than the field value inverts the hierarchy.

## 6. Layout and grid

Fixed **1920 by 1080** canvas, ManualLayout (decision T1). Typical vertical bands:

| Band | Y | Height |
|---|---:|---:|
| header | 0 | 100 |
| KPIs | 110 | 85 (65) |
| filters | 120 to 220 | 100 |
| tabs | 250 | 46 plus a 3 stroke |
| table header | 196 | 50 (35) |
| gallery | ~246 | `fxRowHeight * 12` |
| footer | 1040 | 40 |

- **A single side margin** (`fxLayoutMargin`): it is common for screens to have different margins
  from each other and for the token to be used by none of them. Define the token **equal to what
  the screens use** (here 100 in normal mode) and use it.
- **Gutter** between cards: `fxLayoutGutter`, the same in every KPI row.
- `X` of repeated elements by **formula** (`base + (width + gutter) * n`), never typed in.
- `fxIsCompact = App.Width < 1600` is the only breakpoint; responsiveness is a conditional token, not
  AutoLayout. If the project is truly responsive, the official recommendation is to turn off *Scale
  to fit*, use `Parent.*` and containers, and that is a **different decision** (T1 changes; it needs an ADR).
  Dragging or resizing a control in Studio **overwrites** the `X`, `Y`, `Width`
  and `Height` formulas with constants
  ([Create responsive layout](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-responsive-layout)).

## 7. `fxMsg*` message catalog

- Messages in **pairs**: `fxMsgXError` (what happened) and `fxMsgXHint` (what to do). It is the pattern
  the official error guidance recommends.
- **Complete, polished text.** A catalog of clipped or placeholder strings (`"Err: no perm"`)
  reads as unfinished across a whole app.
- A **domain** message (from a business rule) lives in the project's catalog, not in the generic
  template. A **rule** message that comes from the flow arrives ready in `description`.
- Every visible string by token, placeholder and modal title too; automatic checking of
  literals is an open item of the validator.

## 8. How to evolve the tokens

1. Edit **only** [app-formulas-tokens.md](../assets/app-formulas-tokens.md) (or the project's
   equivalent) and paste it again into the `Formulas` property.
2. Single source across projects: keep one token file and inject it into each project's `Formulas` block
   by script, instead of copying by hand; a manual copy diverges.
3. A modern theme (`App.Theme`, 16-shade palette generated from `BasePaletteColor`, preview) is
   an alternative for an app with modern controls; applying a modern theme to a Classic control does not
   line up visually with Fluent v9 and **turning on "Lock primary color" can break contrast**
   ([Modern theming](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/modern-controls/modern-theming)).
   Outside the v1 standard.
4. When changing the brand, recompute the contrast of every pair in §3 and §4 before pasting.

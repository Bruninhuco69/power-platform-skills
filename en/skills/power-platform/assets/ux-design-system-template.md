# Design system and UX — <PROJECT>

> Stage 3 (`/pp-en:design`, Designer Branding Agent). References: `powerapps-canvas/references/design-tokens.md`, `ux-components.md`,
> `ux-feedback.md`, `accessibility.md`; values in `powerapps-canvas/assets/app-formulas-tokens.md`.
> No color, font or size value outside an `fx*` token (T3).

## 1. Principles (3 to 5)
<e.g. the main cycle in at most 3 taps; every number on screen says whether it is partial>

## 2. Canvas and grid
Fixed resolution: <width×height> · manual layout with Classic controls (T1) · margins <n> ·
base spacing <n> · columns <n>.

## 2.1 Navigation
Chosen by the user in `/pp-en:design`, with a preview (`power-platform/references/navigation.md`).

| Item | Decision |
|---|---|
| Pattern | <`lateral-fixo` · `lateral-recolhivel` · `gaveta` · `topo` · `inicio-cartoes`> |
| Why | <device, frequency of use, number of areas> |
| Catalog component | <`side-menu` (variation) · `top-menu` · `home-cards`> |
| Planned first-level areas | <from the PRD; the screen inventory confirms in stage 4> |
| Initial state | <collapsible: closed or open; drawer: closed> |
| User's sentence | <"…", date> |

## 3. Tokens
| Family | Token | Value | Use |
|---|---|---|---|
| brand color | `fxColorPrimary`, `fxColorPrimaryDark`, `fxColorPrimaryLight` | <hex> | main actions, menu, table header |
| semantic color | `fxColorSuccess`, `fxColorWarning`, `fxColorError` | <hex> | states |
| neutral color | `fxColorBackground`, `fxColorSurface`, `fxColorTextPrimary`, `fxColorTextSecondary`, `fxColorBorder` | <hex> | base |
| typography | `fxFont`, `fxFontSize*` | <font>, scale <n> | text |
| layout | `fxLayoutMargin`, `fxLayoutGutter` | <n> | spacing |

Names and base values in `powerapps-canvas/assets/app-formulas-tokens.md`; here goes the **hex**
decided for the project. This is the column `pp-en:mockups-agent` copies the palette from for the
mockups (stage 4).

Theme: single or light/dark. Contrast (text × effective background, minimum 4.5:1):

| Pair | Contrast | Passes AA? |
|---|---|---|

## 4. Chosen components (catalog `powerapps-canvas/assets/components/`)
| Interface pattern | Catalog component | Allowed variations | Gap? |
|---|---|---|---|
| navigation (section 2.1) | | | |
| gallery with filters | | | |
| form | | | |
| confirmation modal | | | |
| toast | | | |
| empty state | | | |
| loading | | | |
| counter (KPI) | | | |

## 5. States
For each interactive component: normal, focus, disabled, loading, empty, error, success. The
state never depends on color alone (text or icon alongside).

## 6. Feedback
Success, warning and error toast (`status` of contract C1), confirmation for an irreversible action,
loading indicator during `.Run()`.

## 7. Accessibility
Accessible label on every control, tab order, visible focus, minimum touch target, reading order,
contrast, state not by color alone.

## 8. Main flows
For each P0 flow: steps, screens, error states, what the user sees without permission.

## 9. Inputs for the mockups (stage 4)
- Palettes and visual references brought in the brainstorm (block 3.3): where each color in section 3 came from.
- Style in one sentence (e.g. "Fluent 2, corporate, high information density, line icons").
- Interface language and what must never appear in an image (third-party logo, real data).

## Exit gate
- [ ] No "to be defined" item; contrast calculated.
- [ ] Components chosen from the catalog; gaps listed.
- [ ] Template screen (if any) and canonical blocks indicated.

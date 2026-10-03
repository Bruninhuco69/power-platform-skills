# Design system and screen inventory

Stage between the PRD and the architecture. Three artifacts:

| Artifact | Template | Phase | Led by |
|---|---|---|---|
| project design system | `assets/ux-design-system-template.md` | 3 | UX role (`prompts/ux.md`) |
| screen inventory, with the app frame | `assets/screen-inventory-template.md` | 4 | `pp-en:mockups-agent` (`/pp-en:mockups`) |
| mockups | `assets/mockups-template.json` | 4 | `pp-en:mockups-agent` + `scripts/desenhar-mockups.py` |
| clickable prototype | `assets/prototype-template.html` | 5 | `pp-en:prototype-agent` (`/pp-en:prototype`) |

The design system is decided in conversation by the Branding Designer Agent (`/pp-en:design`, stage 3);
inventory, mockups and prototype come from the plugin's agents (`pipeline.md`).

## Contents

1. [Inputs](#1-inputs)
2. [Design system](#2-design-system)
3. [Catalog components](#3-catalog-components)
4. [Screen inventory](#4-screen-inventory)
5. [Mockups](#5-mockups)
6. [Exit gate](#6-exit-gate)

---

## 1. Inputs

- PRD (vision, roles, scope per unit, rules, volumes, MVP).
- Answers to block 3 of `brainstorm.md` (resolution, brand, template screen, accessibility).
- If a sibling app exists: its `app-formulas-tokens.md` is the starting point; start from it, not
  from a new palette.

## 2. Design system

No screen is drawn without this. Decide and record it in the template:

| Item | What to decide | Where the standard is |
|---|---|---|
| Tokens | `fx*` family for color, typography, layout, component and text, as App named formulas | `powerapps-canvas/references/design-tokens.md`; values in `powerapps-canvas/assets/app-formulas-tokens.md` |
| Color | brand, neutrals, semantic (success, warning, error, info), single theme or light/dark | same; minimum WCAG AA contrast 4.5:1 for normal text |
| Typography | font, size scale, weights; nothing outside the scale | same |
| Grid and layout | canvas resolution (T1: manual layout, fixed canvas), margins, columns, spacing | `powerapps-canvas/references/ux-components.md` |
| States | normal, focus, disabled, loading, empty, error, success; a state is never conveyed by color alone | `ux-components.md`, `ux-feedback.md`, `accessibility.md` |
| Feedback | toast, loading, confirmation of an irreversible action | `ux-feedback.md`; `.Run()` contract in `flow-call.md` |
| Accessibility | accessible label, tab order, visible focus, touch target, reading order | `accessibility.md` |

Rule T3: color, font and size only through an `fx*` token. A new value is a new token, decided here,
never a loose `RGBA(` in a screen. The `validar-telas.py` validator flags a literal.

## 3. Catalog components

For each interface pattern in the project, pick the component from the `powerapps-canvas` skill
catalog (`assets/components/`) instead of drawing from scratch: menu, header, gallery with
filters, form, confirmation modal, toast, empty state, loading indicator, counter
(KPI). List in the design system the ones chosen and the allowed variations.

- A component the catalog does not have: record it as a gap; it becomes its own story (a new
  template also feeds the catalog later).
- A property only if the app already uses it on that control type (T4); exact control version (T2).
- Control names: T5 (`<screen-prefix>-<type>-<module>-<element>`).

## 4. Screen inventory

`pp-en:mockups-agent` lists the pages. It starts from the PRD's FR items
and adds the cross-cutting screens (home, no access, detail, access management, export).
Before the screens, it settles the **app frame**, the same on all of them:

- header;
- navigation, in the pattern the user chose in `/pp-en:design` (`ux-design-system.md`
  §2.1, `references/navigation.md`);
- unit selector;
- notifications (toast);
- pop-ups (confirmation, form, destructive, informational);
- loading;
- empty and no-access states;
- footer.

A master table, the frame, the navigation map and, for each screen, a short sheet (template in
`assets/`). Sheet fields:

| Field | Content |
|---|---|
| Screen | name and control prefix |
| Goal | the decision or action it allows, in one sentence |
| Roles | who sees, who acts (by flag, T8) |
| Components | from the catalog; canonical blocks used |
| Data sources | tables and columns read; expected volume per filter |
| Flows called | write actions and their parameters (contract C1–C6) |
| Expected delegation | what delegates, what does not, and the cap (T7); counters with "2,000+"? |
| States | empty, loading, error, no access |
| Pop-ups and notifications | modals the screen opens; toast for each action (every write: loading + toast) |
| Mockup | `docs/planning/mockups/<id>.png` and the owner's acceptance |
| Priority/cut | P0 main cycle, P1, P2; position on the cut ladder |

Rules:
- Every screen in the PRD appears; every screen in the inventory traces to a requirement (FR-xx).
- The inventory **names the columns it needs**. It is the architecture's input (data model) and
  waits for `AS-BUILT-ENVIRONMENT` to become real names.
- A screen that writes without going through a flow violates A1: fix it in the inventory.
- The inventory's cut ladder becomes the `GOAL.md` ladder.

## 5. Mockups

One image per screen and per relevant state, generated by the OpenAI image API from the spec
`docs/planning/mockups/mockups.json`. The palette comes from the design system. It requires `OPENAI_API_KEY`, and the
model is a variable (`OPENAI_IMAGE_MODEL`, default `gpt-image-2`).

- Step by step, key, model and errors: `references/mockups.md`.
- Validate at no cost: `scripts/desenhar-mockups.py <spec> --simular`.
- Generate only after the user's acceptance: it costs per image, and the spec text goes to an external service.
- The mockup is a reference to approve structure and flow. It is not a source of color or measurement.

**Clickable prototype** (`/pp-en:prototype`, stage 5): `pp-en:prototype-agent` reproduces each mockup
in an `index.html` that opens offline, with the catalog components, the tokens and a role
selector. This is what the user approves; an adjustment goes back to `/pp-en:design`. File contract: top comment
of `assets/prototype-template.html`; checker: `scripts/verificar-prototipo.py`.

## 6. Exit gate

- Design system complete: no "to be defined" item; contrast of the text/background pairs calculated.
- Inventory closed: each screen with roles, sources, flows, delegation and priority.
- The process owner saw the inventory (one acceptance sentence recorded). Screens cut later
  without agreeing with the people who use them become a scope dispute.
- Catalog gaps listed.
- Mockups generated, or the waiver recorded with who decided and the date (no key or no security
  approval).
- Prototype approved by the user, with who approved and the date recorded in the inventory.

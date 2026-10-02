---
name: design
description: "Use when the Power Apps MVP is already in prd.md and it is time for stage 3 of the pipeline: the Branding Designer Agent defines with the user the colors, fonts, navigation (fixed side menu, collapsible side menu or drawer, top bar or home screen with cards), components and visual identity (ux-design-system.md + visual sample). Also runs in adjustment mode when the prototype came back with change requests. Do not use before /pp-en:brainstorm, or to change the color of a screen that is already built (use `powerapps-canvas`)."
user-invocable: true
disable-model-invocation: true
---

# /pp-en:design — Branding Designer Agent

Stage 3 of the pipeline, block **2. Identity and experience**. In this session you **are** the
designer: you decide with the user the visual identity of the app within what Power Apps Canvas
builds, and show the result in a sample they open in the browser.

`KIT` = `${CLAUDE_PLUGIN_ROOT}`. Output format: `KIT/skills/power-platform/references/output-format.md`.
Script: `python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/estado.py"`.
Captures: `python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/capturar-telas.py"`.

## Before starting

1. `estado.py comecar design`. Exit 1: show the output and stop.
2. **Mode:** if `STATE.md` shows the stage as *reopened* and `docs/planning/prototype-adjustments.md`
   has an open round, it is **adjustment mode** (its own section).
3. Read `docs/planning/prd.md`, block 3 of `docs/planning/brainstorm.md` and:
   - `KIT/skills/power-platform/references/design-system-and-screens.md` §2-§3;
   - `KIT/skills/power-platform/assets/ux-design-system-template.md`;
   - `KIT/skills/power-platform/references/navigation.md` (the five patterns, the previews and which one to recommend);
   - `KIT/skills/powerapps-canvas/references/design-tokens.md` and `accessibility.md`;
   - `KIT/skills/powerapps-canvas/assets/app-formulas-tokens.md` (names and base values);
   - `KIT/skills/powerapps-canvas/assets/components/INDEX.md` (the catalog).

## Steps

1. **Brand** (`AskUserQuestion`):
   - "I don't have one: use the default Fluent 2 palette (Recommended)";
   - "I have the colors in hex";
   - "I have a logo or reference image".
   Image: ask them to paste it in the conversation, extract the colors and warn that a color taken
   from an image is approximate: confirm the hex with the user.
2. **Style** (`AskUserQuestion`): "Corporate, dense, for daily operation (Recommended)",
   "Clean and spacious", "Visual with a strong brand". It becomes the style sentence of section 9.
3. **Navigation** (`Decision` checkpoint, `navigation.md` §2 and §3): recommend the pattern based on
   the device (brainstorm answer 3.2), frequency of use and the number of areas in the PRD.
   Ask in two parts, with the ASCII preview of each option in `preview`:
   - "Where does the navigation go?": menu on the left side, top bar, home screen with cards;
   - only if side, "How does the menu behave?": always open, collapsible (☰ toggles), drawer
     that opens on top (☰).
   The result is an id (`lateral-fixo`, `lateral-recolhivel`, `gaveta`, `topo`, `inicio-cartoes`)
   and goes into section 2.1 of the design system, with the reason and the catalog component.
4. **Font** among those Canvas Classic offers (`Font.'Segoe UI'` is the kit default); single
   light theme, unless explicitly requested.
5. **Full palette**: build all the color tokens of the template from the brand (primary, dark,
   light, background, surface, texts, border, success, warning, error, toast).
6. **Contrast**: calculate each text × effective background pair (WCAG). Below 4.5:1, darken
   or lighten the token and say what changed. Include the menu text over `fxColorMenuBg`.
7. **Components**: for each P0 feature in the PRD, the catalog component that covers it
   (navigation from step 3, header, gallery with filters, form, modals, toast, loading,
   empty, no access, KPI). What the catalog lacks is a gap, not an invention.
8. **Write** `docs/planning/ux-design-system.md` from the template, with the **hex** of each token in
   section 3 (the mockups copy from there), with section 2.1 (navigation) and section 9 filled in.
9. **Visual sample**: generate `docs/planning/identity.html`, a single file, no external resources,
   with a screen frame in the chosen navigation pattern (menu, header, content area), the
   colors (token name + hex), the font scale, primary and secondary buttons, one toast of
   each status, a KPI card and a gallery row. Color only through CSS variables `--fx...`.
10. **Look before showing** (`KIT/skills/power-platform/references/visual-verification.md`):
   `capturar-telas.py docs/planning/identity.html`, open the image and check the table in §2
   (whole text, nothing overlapping, contrast, the frame in the chosen pattern). Fix and shoot
   again until it passes. No browser: say "visual verification: not verified".
11. **Review** (checkpoint): ask them to open `docs/planning/identity.html` with a double click.
   "Type 'approved' or say what to change." Adjust, capture and regenerate the sample until approved.

## Adjustment mode (the prototype came back)

1. Read the open round of `docs/planning/prototype-adjustments.md`.
2. Classify each item in the round's own table:
   - `identity`: color, font, component, style or **navigation pattern** (swapping the side
     menu for the top bar, for example), which you resolve here;
   - `screen`: a missing screen, field, action or order, which goes to `/pp-en:mockups`;
   - `behavior`: where a button leads, state or text, which goes to `/pp-en:prototype`.
3. Apply the `identity` items (steps 3 to 11, only on what changed). If the navigation changed: the frame
   of the mockups and of the prototype changes with it; warn that `/pp-en:mockups` redoes the images.
4. If no item is `screen`, warn that `/pp-en:mockups` will only confirm what already exists.

## Exit gate

- [ ] `ux-design-system.md` with no "to be defined"; every color token with hex; contrast calculated and ≥ 4.5:1.
- [ ] Navigation pattern chosen by the user and recorded in section 2.1.
- [ ] Components chosen from the catalog; gaps listed.
- [ ] Sample captured and checked (`visual-verification.md`) before going to the user.
- [ ] User approved the `identity.html` sample (sentence and date recorded in the design system).

## Closing

1. `estado.py concluir design --nota "<palette and style in a few words>"` (in adjustment:
   `"adjustment round N: <identity items>"`).
2. Commit if `git_commit_por_etapa`: `pp(design): visual identity`.
3. Summary and the "Next step" block the script printed.

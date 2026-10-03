# Navigation patterns

How the app takes the user from one area to another. The user decides, in `/pp-en:design`
(stage 3), with a preview of each option. The decision goes to `ux-design-system.md` §2.1 and the
following stages only apply it: the mockups draw it, the prototype shows it and the build pastes the
matching catalog component.

## Contents

1. [The five patterns](#1-the-five-patterns)
2. [Which to recommend](#2-which-to-recommend)
3. [How to ask](#3-how-to-ask)
4. [Previews](#4-previews)
5. [What each stage does with the decision](#5-what-each-stage-does-with-the-decision)

---

## 1. The five patterns

| Id | Pattern | Canvas catalog component | Good for | Watch out |
|---|---|---|---|---|
| `lateral-fixo` | side menu always open | `side-menu` | daily desktop use, 3 or more areas | takes 220–260 px of width |
| `lateral-recolhivel` | side menu that ☰ toggles between just the initial of each item and the full label | `side-menu`, collapsible variation | screens with a wide table | collapsed, it shows only the initial: labels must start with different letters |
| `gaveta` | hidden menu; ☰ in the header opens it over the content (hamburger) | `side-menu`, drawer variation | tablet, narrow screen, occasional use | one extra tap to switch areas; the current area is not visible |
| `topo` | horizontal bar at the top, items side by side | `top-menu` | 2 to 6 areas with short names; full width for the content | does not fit more than 6 items or a long label |
| `inicio-cartoes` | home screen with one card per area; "‹ Home" on the other screens | `home-cards` | occasional use, one task per visit, people not used to menus | back and forth through home on every area switch |

In all of them: each item's visibility comes from the role **flag** (never from the name), the active
item has a background **and** bold, and with no role the navigation disappears ("no access" panel).
Hiding an item is not security: the flow is what blocks.

## 2. Which to recommend

Read answer 3.2 of `brainstorm.md` (devices and resolution), the number of first-level areas the PRD
suggests (P0 features grouped) and the frequency of use.

| Situation | Recommend |
|---|---|
| tablet, phone or narrow window | `gaveta` |
| occasional use, each person comes in for one task | `inicio-cartoes` |
| 2 to 6 areas with short names, screens with a wide table | `topo` |
| daily use, screens with a wide table, 4 or more areas | `lateral-recolhivel` |
| daily desktop use, 3 or more areas (the common case) | `lateral-fixo` |
| only one or two screens | no menu: a back button (record `nenhum` and the reason) |

When torn between two, recommend the one that keeps the current area visible (`lateral-fixo` or `topo`).

## 3. How to ask

`AskUserQuestion` accepts up to 4 options, so it takes two questions, each option with the preview from
§4 in the `preview` field and the recommended one first, with "(Recommended)":

1. **Where does the navigation go?** (header `Navigation`): "Menu on the left side", "Bar at the top",
   "Home screen with cards".
2. **Only if they chose the side: how does the menu behave?** (header `Side menu`): "Always open",
   "Collapsible (☰ toggles)", "Drawer that opens over the content (☰)".

Then, if it is `lateral-recolhivel`, ask whether it starts open or closed (default: closed,
to give the table width). Record the user's own phrase in `ux-design-system.md` §2.1.

## 4. Previews

Use these drawings in each option's `preview` (monospaced, up to 40 columns).

**Menu on the left side**

```text
┌────────┬─────────────────────────┐
│ ▣ App  │ Orders                  │
│        ├─────────────────────────┤
│ Home   │                         │
│▌Orders │   screen content        │
│ Reports│                         │
│        │                         │
│ Ana    │                         │
└────────┴─────────────────────────┘
```

**Bar at the top**

```text
┌──────────────────────────────────┐
│ App  Home ▌Orders  Reports   Ana │
├──────────────────────────────────┤
│ Orders                           │
├──────────────────────────────────┤
│                                  │
│   content at full width          │
│                                  │
└──────────────────────────────────┘
```

**Home screen with cards**

```text
┌──────────────────────────────────┐
│ Home                             │
├──────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌──────┐ │
│ │ Orders  │ │ Reports │ │ Users│ │
│ │ Register│ │ See the │ │ Give │ │
│ │ [Open]  │ │ [Open]  │ │[Open]│ │
│ └─────────┘ └─────────┘ └──────┘ │
└──────────────────────────────────┘
 on the other screens: [‹ Home] Orders
```

**Always open**

```text
┌────────┬─────────────────────────┐
│ ▣ App  │ Orders                  │
│ Home   ├─────────────────────────┤
│▌Orders │                         │
│ Reports│   content               │
└────────┴─────────────────────────┘
 the menu takes 260 px all the time
```

**Collapsible (☰ toggles)**

```text
 closed               open
┌──┬─────────────┐   ┌────────┬──────┐
│☰ │ Orders      │   │‹  Menu │Order.│
│ H├─────────────┤   │ Home   ├──────┤
│▌O│ content     │   │▌Orders │ cont.│
│ R│ wider       │   │ Reports│      │
└──┴─────────────┘   └────────┴──────┘
```

**Drawer that opens over the content (☰)**

```text
 closed               open
┌────────────────┐   ┌────────┬░░░░░░┐
│☰ Orders        │   │App   ✕ │░░░░░░│
├────────────────┤   │ Home   │░ veil│
│ content at     │   │▌Orders │░░░░░░│
│ full width     │   │ Reports│░░░░░░│
└────────────────┘   └────────┴░░░░░░┘
```

## 5. What each stage does with the decision

| Stage | What it does |
|---|---|
| `/pp-en:design` | asks, records in `ux-design-system.md` §2.1 (pattern, reason, component) and shows the navigation in the `identity.html` sample |
| `/pp-en:mockups` | `pp-en:mockups-agent` copies the pattern into the inventory frame and into the spec's `moldura.navegacao`; the navigation map follows the pattern (with cards, every screen goes back to home) |
| `/pp-en:prototype` | `pp-en:prototype-agent` puts the id in `NAVEGACAO`; the "Navigation" selector in the prototype bar lets the user compare the five patterns live. Switching patterns is an `identity` item of the adjustment and goes back to `/pp-en:design` |
| `/pp-en:build app` | `pp-en:canvas-agent` pastes the component from the §1 table, in the right variation, on every screen (with `inicio-cartoes`, the "‹ Home" button on every screen that is not the home) |
| `/pp-en:test` | the script checks the navigation with each role: item hidden by flag, active item, back to home, drawer closing when the screen changes |

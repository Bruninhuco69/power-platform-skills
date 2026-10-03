# Visual verification: look before showing

A file validator proves structure (tokens, screens, catalog components), not appearance. Cut-off text,
a button on top of a button, poor contrast and a blank screen all pass at `0 error(s)`. So whoever
hands a page to the user **takes a screenshot and looks** first: the agent that wrote it (self-check) and
the session that judges.

## 1. Take the screenshots

```bash
# prototype: one image per screen, in the design's navigation pattern
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/capturar-telas.py" docs/planning/prototype/index.html
# the first screen in all five navigation patterns
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/capturar-telas.py" docs/planning/prototype/index.html --navegacoes
# another role (PERFIS key of the prototype)
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/capturar-telas.py" docs/planning/prototype/index.html --perfil operador
# the design sample
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/capturar-telas.py" docs/planning/identity.html
```

The images go to `capturas/` next to the HTML (outside Git: the project's `.gitignore`). The script
uses Chrome or Edge without a window, with a temporary profile (it does not touch the open browser).
With no browser (exit 2): the visual verification is **not verified** in the summary, never "ok".

## 2. Look

Open each image with the read tool and check, in this order:

| # | What | Typical failure |
|---|---|---|
| 1 | The screen rendered | blank image or only the prototype bar: script error on the page |
| 2 | Whole text | cut-off label, "..." where it should not be, text spilling out of the button or card |
| 3 | Nothing overlapping | menu over the content, modal behind the overlay, two controls in the same place |
| 4 | Alignment and breathing room | misaligned columns, different margins between screens, a large empty area on one side only |
| 5 | Hierarchy | the title is the largest text; one primary action per area; destructive in red |
| 6 | Color and contrast | color outside the design system palette, light text on a light background |
| 7 | Navigation | the pattern from section 2.1 of the design system; correct active item; "‹ Home" with cards |
| 8 | Fidelity to Canvas | nothing Canvas cannot do (thin shadow, gradient, outside font, reflowing layout) |

Each failure becomes an item with the image, the region and what is wrong (e.g., `tela-pedidos.png`,
Actions column: "Cancel" button cut off at 1920 px).

## 3. Who does what

| Who | When | On failure |
|---|---|---|
| `prototype-agent` | after a clean `verificar-prototipo.py` | fixes and takes screenshots again; what it did not resolve goes to the alerts |
| `/pp-en:prototype` session | when judging the delivery | revision back to the agent, with the image and the region |
| `/pp-en:design` session | before showing `identity.html` | fixes the sample (it is the session's own file) and takes screenshots again |

The user sees the page after this. Visual verification does not replace their review; it keeps
them from spending their review on a defect the machine could already have seen.

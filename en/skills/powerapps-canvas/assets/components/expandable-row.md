# Expandable row

Maturity: **unique** · Frequency: **occasional**.

## Purpose

Clicking the gallery row expands a detail panel right below it, without a modal. The state is a variable with the id of the expanded row (one at a time).

## When to use / when not to use

**Use when**

- the detail is short (2 to 4 fields) and the user compares several rows;
- a modal per row is not worth it.

**Do not use when**

- the detail is long or has an action (use a modal or a screen);
- the list is large and the row height needs to be stable.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-btn-gal-fundo-linha  (Button)
xx-lbl-gal-chevron  (Label)
xx-rec-gal-detalhe-fundo  (Rectangle)
xx-lbl-gal-detalhe-observacoes  (Label)
xx-lbl-gal-detalhe-responsavel  (Label)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorDivider`, `fxColorTransparent`, `fxColorPrimaryLight`, `fxColorSurface`, `fxFont`, `fxRowHeight`, `fxColorPrimary`, `fxFontSizeBody`, `fxColorBackground`, `fxColorTextBody`, `fxFontSizeTableSmall`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varLinhaExpandida`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (en-US: `,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

These controls go **inside the gallery template** (`Children` of `xx-gal-pedidos`).

```yaml
- xx-btn-gal-fundo-linha:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorDivider
      Color: =fxColorTransparent
      Fill: =If(varLinhaExpandida = ThisItem.<col-id>, fxColorPrimaryLight, fxColorSurface)
      Font: =fxFont
      Height: =fxRowHeight
      HoverFill: =fxColorPrimaryLight
      OnSelect: |-
        =Set(
          varLinhaExpandida,
          If(varLinhaExpandida = ThisItem.<col-id>, Blank(), ThisItem.<col-id>)
        )
      PressedFill: =fxColorPrimaryLight
      TabIndex: =0
      Text: =""
      Tooltip: =If(varLinhaExpandida = ThisItem.<col-id>, "Collapse details", "Expand details")
      Width: =Parent.TemplateWidth
      X: =0
      Y: =0
- xx-lbl-gal-chevron:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxRowHeight
      Size: =fxFontSizeBody
      Text: =If(varLinhaExpandida = ThisItem.<col-id>, "▴", "▾")
      VerticalAlign: =VerticalAlign.Middle
      Width: =30
      X: =Parent.TemplateWidth - 44
      Y: =0
- xx-rec-gal-detalhe-fundo:
    Control: Rectangle@2.3.0
    Properties:
      BorderStyle: =BorderStyle.None
      Fill: =fxColorBackground
      Height: =fxRowHeight * 3
      Visible: =varLinhaExpandida = ThisItem.<col-id>
      Width: =Parent.TemplateWidth
      X: =0
      Y: =fxRowHeight
- xx-lbl-gal-detalhe-observacoes:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorTextBody
      Font: =fxFont
      Height: =28
      Size: =fxFontSizeTableSmall
      Text: |-
        ="Notes: " & Coalesce(ThisItem.<col-observacoes>, "no notes")
      Visible: =varLinhaExpandida = ThisItem.<col-id>
      Width: =Parent.TemplateWidth - 32
      X: =16
      Y: =fxRowHeight + 8
- xx-lbl-gal-detalhe-responsavel:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorTextBody
      Font: =fxFont
      Height: =28
      Size: =fxFontSizeTableSmall
      Text: |-
        ="Owner: " & ThisItem.<col-responsavel>
      Visible: =varLinhaExpandida = ThisItem.<col-id>
      Width: =Parent.TemplateWidth - 32
      X: =16
      Y: =fxRowHeight + 44
```

## Parameters to change

| In the block | Change to | Note |
|---|---|---|
| `varLinhaExpandida` | screen variable | starts as `Blank()` in `OnStart`; reset it when a filter changes |
| `<col-id>`, `<col-observacoes>`, `<col-responsavel>` | real columns |  |
| `TemplateSize` of the gallery | `If(IsBlank(varLinhaExpandida), fxRowHeight, fxRowHeight * 4)` | see Pitfalls: **all** rows grow |

## Behavior

Destination of the formulas below: the same as the YAML (en-US: `,` and `;`).

**`xx-btn-gal-fundo-linha`.OnSelect**: toggles the expanded row: the same row collapses, another one replaces it

```powerfx
Set(
  varLinhaExpandida,
  If(varLinhaExpandida = ThisItem.<col-id>, Blank(), ThisItem.<col-id>)
)
```

## Accessibility

- The row background is a button: focus and Enter work; the `Tooltip` says the current action.
- The state (expanded or collapsed) shows in a symbol and in the background, not only in color.

## Pitfalls

- `TemplateSize` cannot read `ThisItem`: it belongs to the gallery itself, so when one row expands, all of them grow (the non-expanded ones are left with empty space). That is why the pattern is limited to a short detail.
- Variable height per row only with a flexible vertical gallery (`BrowseLayout_Flexible_*` with `AutoHeight`) `[unverified]`.
- Two clicks in a row open and close: keep `OnSelect` idempotent (the formula above is).
- An action inside the detail (cancel, edit) becomes a modal: the panel is read-only.

## Variations

- Side detail (a fixed panel on the right reads `varPedidoSel`): without the height problem.
- Chevron as an image: use `Image@2.2.3` with a media resource in place of the `Label`.

# KPI card (counter with a ceiling)

Maturity: **stable** · Frequency: **common** (a row of 3 to 5 cards right below the header).

## Purpose

Counter for a summary row (total, open, completed): title with an `fxBadge*` color pair, large value and an honest ceiling when the count does not delegate.

## When to use / when not to use

**Use when**

- summarize the list right below in up to 5 or 6 numbers;
- the counter must match the gallery by construction (same scope filter).

**Do not use when**

- the metric requires a server-side calculation (use a flow or a view and show the result);
- more than 6 cards: it becomes a BI dashboard, use Power BI.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-con-kpis  (GroupContainer)
  xx-con-kpi-total  (GroupContainer)
    xx-lbl-kpi-total-titulo  (Label)
    xx-lbl-kpi-total-valor  (Label)
  xx-con-kpi-abertos  (GroupContainer)
    xx-lbl-kpi-abertos-titulo  (Label)
    xx-lbl-kpi-abertos-valor  (Label)
  xx-con-kpi-andamento  (GroupContainer)
    xx-lbl-kpi-andamento-titulo  (Label)
    xx-lbl-kpi-andamento-valor  (Label)
  xx-con-kpi-encerrados  (GroupContainer)
    xx-lbl-kpi-encerrados-titulo  (Label)
    xx-lbl-kpi-encerrados-valor  (Label)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxLayoutMargin`, `fxLayoutGutter`, `fxKPIWidth`, `fxKPIHeight`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxBadgeNeutralText`, `fxFont`, `fxFontSizeKPITitle`, `fxBadgeNeutralBg`, `fxKPITitleHeight`, `fxColorTextPrimary`, `fxFontSizeKPI`, `fxLimiteLinhas`, `fxTxtTeto`, `fxKPIValueHeight`, `fxBadgeInfoText`, `fxBadgeInfoBg`, `fxBadgeProgressText`, `fxBadgeProgressBg`, `fxBadgeSuccessText`, `fxBadgeSuccessBg`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxHeaderHeight`.
- **Global variables** (born in `OnStart`, `assets/app-onstart-template.md`): `varPedidoTotal`, `varPedidoAbertos`, `varPedidoAndamento`, `varPedidoEncerrados`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as the parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-con-kpis:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorTransparent
      Height: =fxKPIHeight
      Width: =(fxKPIWidth + fxLayoutGutter) * 4
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + fxLayoutGutter
    Children:
      - xx-con-kpi-total:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Regular
            Fill: =fxColorSurface
            Height: =fxKPIHeight
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxKPIWidth
            X: =(fxKPIWidth + fxLayoutGutter) * 0
            Y: =0
          Children:
            - xx-lbl-kpi-total-titulo:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxBadgeNeutralText
                  Fill: =fxBadgeNeutralBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxKPITitleHeight
                  Size: =fxFontSizeKPITitle
                  Text: ="Total"
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =0
            - xx-lbl-kpi-total-valor:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxKPIValueHeight
                  Size: =fxFontSizeKPI
                  Text: =If(varPedidoTotal >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoTotal, "[$-en-US]#,##0"))
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =fxKPITitleHeight
      - xx-con-kpi-abertos:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Regular
            Fill: =fxColorSurface
            Height: =fxKPIHeight
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxKPIWidth
            X: =(fxKPIWidth + fxLayoutGutter) * 1
            Y: =0
          Children:
            - xx-lbl-kpi-abertos-titulo:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxBadgeInfoText
                  Fill: =fxBadgeInfoBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxKPITitleHeight
                  Size: =fxFontSizeKPITitle
                  Text: ="Open"
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =0
            - xx-lbl-kpi-abertos-valor:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxKPIValueHeight
                  Size: =fxFontSizeKPI
                  Text: =If(varPedidoAbertos >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoAbertos, "[$-en-US]#,##0"))
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =fxKPITitleHeight
      - xx-con-kpi-andamento:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Regular
            Fill: =fxColorSurface
            Height: =fxKPIHeight
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxKPIWidth
            X: =(fxKPIWidth + fxLayoutGutter) * 2
            Y: =0
          Children:
            - xx-lbl-kpi-andamento-titulo:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxBadgeProgressText
                  Fill: =fxBadgeProgressBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxKPITitleHeight
                  Size: =fxFontSizeKPITitle
                  Text: ="In progress"
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =0
            - xx-lbl-kpi-andamento-valor:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxKPIValueHeight
                  Size: =fxFontSizeKPI
                  Text: =If(varPedidoAndamento >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoAndamento, "[$-en-US]#,##0"))
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =fxKPITitleHeight
      - xx-con-kpi-encerrados:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Regular
            Fill: =fxColorSurface
            Height: =fxKPIHeight
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxKPIWidth
            X: =(fxKPIWidth + fxLayoutGutter) * 3
            Y: =0
          Children:
            - xx-lbl-kpi-encerrados-titulo:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxBadgeSuccessText
                  Fill: =fxBadgeSuccessBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxKPITitleHeight
                  Size: =fxFontSizeKPITitle
                  Text: ="Completed"
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =0
            - xx-lbl-kpi-encerrados-valor:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxKPIValueHeight
                  Size: =fxFontSizeKPI
                  Text: =If(varPedidoEncerrados >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoEncerrados, "[$-en-US]#,##0"))
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =fxKPITitleHeight
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `slug` (`total`, `abertos`, ...) | metric name | in the names of the card's 3 controls |
| `varPedidoTotal` ... `varPedidoEncerrados` | counter variable | born as 0 in `OnStart` |
| `"Total"`, `"Open"` | card title | short, one or two words |
| `Neutral`, `Info`, `Progress`, `Success` | `fxBadge*` pair of the same hue | dark text on pastel, contrast checked |
| `* 0`, `* 1` ... | card position in the row | `X` by formula, never typed |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-lbl-kpi-total-valor`.Text**: shows the ceiling when the count hits the connector limit

```powerfx
If(varPedidoTotal >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoTotal, "[$-en-US]#,##0"))
```

## Accessibility

- Title and value are separate labels, read in sequence ("Total", "1,234").
- The `fxBadge*Text` on `fxBadge*Bg` pair has a contrast of at least 4.5:1.

## Pitfalls

- A counter calculated only in `OnStart` freezes and spends the day diverging from the gallery.
- Showing the raw value (`2000`) when the connector limit was reached is a lie: always `fxTxtTeto`.
- `CountRows(Filter(...))` inside the card `Text` recalculates on every screen change.
- A named formula **cannot** read the scope variable (`varUnidadeFiltro`); that is why the counter is a variable.

## Variations

- Clickable card that applies a filter: replace the `GroupContainer` with a background `Classic/Button` and put the `OnSelect` on it (`GroupContainer` has no `OnSelect`).
- Compact (`fxIsCompact`): the `fxKPI*` tokens already shrink.

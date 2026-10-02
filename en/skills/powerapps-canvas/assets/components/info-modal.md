# Info modal (details and history)

Maturity: **stable** · Frequency: **occasional**.

## Purpose

Read-only modal: title, a mini-table (history, trail, batch result) and the `Close` button. No write action, so no loading and no flow.

## When to use / when not to use

**Use when**

- show the detail or history of a record without leaving the screen;
- show the result of a batch operation.

**Do not use when**

- the content is large (many columns or rows): use a dedicated screen;
- the user needs to act on the content (use a form).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-mod-detalhes  (GroupContainer)
  xx-mod-detalhes-bloqueio  (Button)
  xx-mod-detalhes-card  (GroupContainer)
    xx-mod-detalhes-titulo  (Label)
    xx-hdr-gal-mod-data  (Button)
    xx-hdr-gal-mod-evento  (Button)
    xx-hdr-gal-mod-usuario  (Button)
    xx-hdr-gal-mod-descricao  (Button)
    xx-gal-mod-historico  (Gallery)
      xx-lbl-mod-historico-data  (Label)
      xx-lbl-mod-historico-evento  (Label)
      xx-lbl-mod-historico-usuario  (Label)
      xx-lbl-mod-historico-descricao  (Label)
    xx-mod-detalhes-vazio  (Label)
    xx-mod-detalhes-btn-fechar  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorOverlayDark`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxColorPrimaryDark`, `fxFont`, `fxModalTitleSize`, `fxModalPadding`, `fxColorTableHeaderText`, `fxColorTableHeaderBg`, `fxFontSizeHeader`, `fxTableHeaderHeight`, `fxRowHeight`, `fxColorTextSecondary`, `fxFontSizeTableSmall`, `fxColorTextPrimary`, `fxFontSizeTable`, `fxFontSizeBody`, `fxMsgNoResultsError`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxBtnRadius`, `fxTxtFechar`, `fxBtnFontSize`, `fxBtnWidth`, `fxBtnHeight`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxModalWidthL`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varMostrarDetalhes`, `varPedidoSel`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-mod-detalhes:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlayDark
      Height: =Parent.Height
      Visible: =varMostrarDetalhes
      Width: =Parent.Width
    Children:
      - xx-mod-detalhes-bloqueio:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            Color: =fxColorTransparent
            Fill: =fxColorTransparent
            Height: =Parent.Height
            HoverFill: =fxColorTransparent
            OnSelect: =false
            PressedFill: =fxColorTransparent
            TabIndex: =-1
            Text: =""
            Width: =Parent.Width
            X: =0
            Y: =0
      - xx-mod-detalhes-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =560
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxModalWidthL + 260
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-mod-detalhes-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorPrimaryDark
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =32
                  Size: =fxModalTitleSize
                  Text: ="Order history " & varPedidoSel.<col-codigo>
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =fxModalPadding
            - xx-hdr-gal-mod-data:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Date"
                  Width: =140
                  X: =fxModalPadding
                  Y: =70
            - xx-hdr-gal-mod-evento:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Event"
                  Width: =200
                  X: =fxModalPadding + 140
                  Y: =70
            - xx-hdr-gal-mod-usuario:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="User"
                  Width: =200
                  X: =fxModalPadding + 340
                  Y: =70
            - xx-hdr-gal-mod-descricao:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Description"
                  Width: =300
                  X: =fxModalPadding + 540
                  Y: =70
            - xx-gal-mod-historico:
                Control: Gallery@2.15.0
                Variant: BrowseLayout_Flexible_SocialFeed_ver5.0
                Properties:
                  BorderColor: =fxColorBorder
                  BorderThickness: =1
                  Height: =fxRowHeight * 5
                  Items: |-
                    =Sort(
                      Filter('<fonte-historico>', <col-pedido> = varPedidoSel.<col-id>),
                      <col-data>,
                      SortOrder.Descending
                    )
                  TemplatePadding: =0
                  TemplateSize: =Max(20, fxRowHeight)
                  Width: =840
                  X: =fxModalPadding
                  Y: =70 + fxTableHeaderHeight
                Children:
                  - xx-lbl-mod-historico-data:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorTextSecondary
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTableSmall
                        Text: =Text(ThisItem.<col-data>, "[$-en-US]mm/dd/yyyy hh:mm")
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =130
                        X: =8
                        Y: =0
                  - xx-lbl-mod-historico-evento:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorTextPrimary
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTable
                        Text: =ThisItem.<col-evento>
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =190
                        X: =140
                        Y: =0
                  - xx-lbl-mod-historico-usuario:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorTextSecondary
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTableSmall
                        Text: =ThisItem.<col-usuario>
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =190
                        X: =340
                        Y: =0
                  - xx-lbl-mod-historico-descricao:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorTextPrimary
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTableSmall
                        Text: =ThisItem.<col-descricao>
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =290
                        X: =540
                        Y: =0
            - xx-mod-detalhes-vazio:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  Height: =40
                  Size: =fxFontSizeBody
                  Text: =fxMsgNoResultsError
                  Visible: ='xx-gal-mod-historico'.AllItemsCount = 0
                  Width: =840
                  X: =fxModalPadding
                  Y: =70 + fxTableHeaderHeight + 40
            - xx-mod-detalhes-btn-fechar:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =fxColorButtonCancel
                  BorderThickness: =1
                  Color: =fxColorTextOnPrimary
                  Fill: =fxColorButtonCancel
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxBtnHeight
                  HoverBorderColor: =fxColorButtonCancelHover
                  HoverColor: =fxColorTextOnPrimary
                  HoverFill: =fxColorButtonCancelHover
                  OnSelect: |-
                    =Set(varMostrarDetalhes, false);
                    Set(varPedidoSel, Blank())
                  PressedBorderColor: =fxColorButtonCancelHover
                  PressedColor: =fxColorTextOnPrimary
                  PressedFill: =fxColorButtonCancelHover
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxBtnFontSize
                  TabIndex: =0
                  Text: =fxTxtFechar
                  Width: =fxBtnWidth
                  X: =Parent.Width - Self.Width - fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
```

## Parameters to change

| In the block | Change to | Note |
|---|---|---|
| `xx-mod-detalhes`, `varMostrarDetalhes` | `xx-mod-<subject>`, `varMostrar<Subject>` | the gallery button opens it |
| `'<fonte-historico>'`, `<col-pedido>`, `<col-data>` | real history table and columns | filter by the key of the selected record |
| widths 140, 200, 200 and 300 | real columns | the sum must fit in the gallery `Width` (840) |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-mod-detalhes-btn-fechar`.OnSelect**: closes and clears the selection

```powerfx
Set(varMostrarDetalhes, false);
Set(varPedidoSel, Blank())
```

**`xx-gal-mod-historico`.Items**: history of the selected record, most recent first

```powerfx
Sort(
  Filter('<fonte-historico>', <col-pedido> = varPedidoSel.<col-id>),
  <col-data>,
  SortOrder.Descending
)
```

## Accessibility

- There is only one button and it is `Close`: keep it in the tab order and with text.
- No `Escape` and no clicking the veil to close (a Canvas limitation): the button is the only way.

## Pitfalls

- Clicking the veil does not close it (the blocker has `OnSelect: =false`): if you want that, change it to `Set(varMostrarDetalhes, false)`, but accept accidental closing.
- `Filter(<fonte>, <col-pedido> = varPedidoSel.<col-id>)` delegates on equality; `LookUp` per row does not.
- Card width derived from a token (`fxModalWidthL + 260`): adjust it to the content, but keep the centering by formula.

## Variations

- Batch result: change the gallery source to `colResultadoLote`.
- Without a table: two or three `Label`s with `fxColorTextBody`.

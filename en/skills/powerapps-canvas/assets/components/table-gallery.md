# Table-style gallery

Maturity: **stable** · Frequency: **very common** (the basis of every listing; only the columns change).

## Purpose

Tabular list in three layers: a fixed column header (outside the gallery), a gallery with a clickable row and columns aligned by `X` and `Width`, and the delegable `Items` that reads the filters from the bar above.

## When to use / when not to use

**Use when**

- list of records with 4 to 10 columns and one action per row;
- `Items` can be expressed with delegable predicates only.

**Do not use when**

- a 2D table that must be accessible to a screen reader (use the classic Data Table);
- rows whose height varies with long content (use a conditional `TemplateSize` and review the alignment).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-hdr-gal-codigo  (Button)
xx-hdr-gal-descricao  (Button)
xx-hdr-gal-status  (Button)
xx-hdr-gal-data  (Button)
xx-hdr-gal-acoes  (Button)
xx-gal-pedidos  (Gallery)
  xx-btn-gal-fundo-linha  (Button)
  xx-lbl-gal-codigo  (Label)
  xx-lbl-gal-descricao  (Label)
  xx-lbl-gal-status  (Label)
  xx-lbl-gal-data  (Label)
  xx-btn-gal-detalhes  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTableHeaderText`, `fxColorTableHeaderBg`, `fxFont`, `fxFontSizeHeader`, `fxLayoutMargin`, `fxTableHeaderHeight`, `fxColorBorder`, `fxRowHeight`, `fxColorDivider`, `fxColorTransparent`, `fxColorPrimaryLight`, `fxColorSurface`, `fxColorPrimary`, `fxFontSizeTable`, `fxColorTextBody`, `fxBadgeInfoText`, `fxBadgeProgressText`, `fxBadgeSuccessText`, `fxBadgeNeutralText`, `fxFontSizeTableSmall`, `fxBadgeInfoBg`, `fxBadgeProgressBg`, `fxBadgeSuccessBg`, `fxBadgeNeutralBg`, `fxColorTextPrimary`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxBtnRadius`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varUnidadeFiltro`, `varPedidoDe`, `varPedidoAte`, `varPedidoSel`, `varMostrarDetalhes`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (en-US: `,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-hdr-gal-codigo:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      DisplayMode: =DisplayMode.View
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      Size: =fxFontSizeHeader
      Text: ="Code"
      Width: =160
      X: =fxLayoutMargin
      Y: =300
- xx-hdr-gal-descricao:
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
      Width: =560
      X: =fxLayoutMargin + 160
      Y: =300
- xx-hdr-gal-status:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      DisplayMode: =DisplayMode.View
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      Size: =fxFontSizeHeader
      Text: ="Status"
      Width: =160
      X: =fxLayoutMargin + 720
      Y: =300
- xx-hdr-gal-data:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      DisplayMode: =DisplayMode.View
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      Size: =fxFontSizeHeader
      Text: ="Added"
      Width: =160
      X: =fxLayoutMargin + 880
      Y: =300
- xx-hdr-gal-acoes:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      DisplayMode: =DisplayMode.View
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      Size: =fxFontSizeHeader
      Text: ="Actions"
      Width: =140
      X: =fxLayoutMargin + 1040
      Y: =300
- xx-gal-pedidos:
    Control: Gallery@2.15.0
    Variant: BrowseLayout_Flexible_SocialFeed_ver5.0
    Properties:
      BorderColor: =fxColorBorder
      BorderThickness: =1
      Height: =fxRowHeight * 12
      Items: |-
        =Sort(
          Filter(
            '<fonte>',
            StartsWith(<col-unidade>, varUnidadeFiltro),
            IsBlank('xx-cbo-filtro-status'.Selected)
              || <col-status> = 'xx-cbo-filtro-status'.Selected.Value,
            StartsWith(<col-codigo>, Trim('xx-txt-filtro-busca'.Text)),
            IsBlank(varPedidoDe) || Ref_<col-data> >= varPedidoDe,
            IsBlank(varPedidoAte) || Ref_<col-data> <= varPedidoAte
          ),
          <col-data>,
          SortOrder.Descending
        )
      TemplatePadding: =0
      TemplateSize: =Max(20, fxRowHeight)
      Width: =1180
      X: =fxLayoutMargin
      Y: =300 + fxTableHeaderHeight
    Children:
      - xx-btn-gal-fundo-linha:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorDivider
            Color: =fxColorTransparent
            Fill: =If(varPedidoSel.<col-id> = ThisItem.<col-id>, fxColorPrimaryLight, fxColorSurface)
            Font: =fxFont
            Height: =Parent.TemplateHeight
            HoverFill: =fxColorPrimaryLight
            OnSelect: =Set(varPedidoSel, ThisItem)
            PressedFill: =fxColorPrimaryLight
            TabIndex: =0
            Text: =""
            Width: =Parent.TemplateWidth
            X: =0
            Y: =0
      - xx-lbl-gal-codigo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =Parent.TemplateHeight
            Size: =fxFontSizeTable
            Text: =ThisItem.<col-codigo>
            VerticalAlign: =VerticalAlign.Middle
            Width: =140
            X: =16
            Y: =0
      - xx-lbl-gal-descricao:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextBody
            Font: =fxFont
            Height: =Parent.TemplateHeight
            Size: =fxFontSizeTable
            Text: =ThisItem.<col-descricao>
            VerticalAlign: =VerticalAlign.Middle
            Width: =550
            X: =164
            Y: =0
      - xx-lbl-gal-status:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: |-
              =Switch(
                ThisItem.<col-status>,
                "open", fxBadgeInfoText,
                "in progress", fxBadgeProgressText,
                "completed", fxBadgeSuccessText,
                fxBadgeNeutralText
              )
            Fill: |-
              =Switch(
                ThisItem.<col-status>,
                "open", fxBadgeInfoBg,
                "in progress", fxBadgeProgressBg,
                "completed", fxBadgeSuccessBg,
                fxBadgeNeutralBg
              )
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =24
            Size: =fxFontSizeTableSmall
            Text: =ThisItem.<col-status>
            VerticalAlign: =VerticalAlign.Middle
            Width: =140
            X: =730
            Y: =(Parent.TemplateHeight - Self.Height) / 2
      - xx-lbl-gal-data:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorTextPrimary
            Font: =fxFont
            Height: =Parent.TemplateHeight
            Size: =fxFontSizeTableSmall
            Text: =Text(ThisItem.<col-data>, "[$-en-US]mm/dd/yyyy")
            VerticalAlign: =VerticalAlign.Middle
            Width: =150
            X: =880
            Y: =0
      - xx-btn-gal-detalhes:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorButtonCancel
            BorderThickness: =1
            Color: =fxColorTextOnPrimary
            Fill: =fxColorButtonCancel
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =34
            HoverBorderColor: =fxColorButtonCancelHover
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorButtonCancelHover
            OnSelect: |-
              =Set(varPedidoSel, ThisItem);
              Set(varMostrarDetalhes, true)
            PressedBorderColor: =fxColorButtonCancelHover
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorButtonCancelHover
            RadiusBottomLeft: =fxBtnRadius
            RadiusBottomRight: =fxBtnRadius
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxFontSizeTableSmall
            TabIndex: =0
            Text: ="Details"
            Width: =120
            X: =1050
            Y: =(Parent.TemplateHeight - Self.Height) / 2
```

## Parameters to change

| In the block | Change to | Note |
|---|---|---|
| `'xx-gal-pedidos'` | gallery name | referenced by the empty state and by the footer |
| `'<fonte>'`, `<col-...>` | real table and columns | the name comes from the environment (`AS-BUILT-NAMES`), never from the dictionary |
| widths 160, 560, 160, 160 and 140 | real columns and widths | the `X` of each column is the sum of the previous widths; header and cell use the same `X` |
| `varPedidoSel`, `varMostrarDetalhes` | selection and modal variables | created in `OnStart` |
| `Ref_<col-data>` | calculated integer date column | a direct date filter on the SQL connector does not delegate |

## Behavior

Destination of the formulas below: the same as the YAML (en-US: `,` and `;`).

**`xx-gal-pedidos`.Items**: filter by unit, status, code and date window, sorted by date descending

```powerfx
Sort(
  Filter(
    '<fonte>',
    StartsWith(<col-unidade>, varUnidadeFiltro),
    IsBlank('xx-cbo-filtro-status'.Selected)
      || <col-status> = 'xx-cbo-filtro-status'.Selected.Value,
    StartsWith(<col-codigo>, Trim('xx-txt-filtro-busca'.Text)),
    IsBlank(varPedidoDe) || Ref_<col-data> >= varPedidoDe,
    IsBlank(varPedidoAte) || Ref_<col-data> <= varPedidoAte
  ),
  <col-data>,
  SortOrder.Descending
)
```

**`xx-btn-gal-fundo-linha`.OnSelect**: selects the row (GroupContainer has no `OnSelect`; that is why the background is a button)

```powerfx
Set(varPedidoSel, ThisItem)
```

## Accessibility

- The header is a `DisplayMode.View` button: it is not in the tab order and does not click.
- Status by color **and** text (never color alone); the `fxBadge*` pair has a 4.5:1 contrast.
- A clickable row without its own label: the text of the cells is read; a screen reader does not build a semantic table (limitation recorded in `accessibility.md`).

## Pitfalls

- `TemplateSize: =Max(20, fxRowHeight)`: never 0 and never fixed and disconnected from the content.
- Inside the gallery use `Parent.TemplateWidth` and `Parent.TemplateHeight`, not `Parent.Width`.
- `LookUp(source)` inside the gallery fires one query per row: load the domain into a collection.
- `Patch` on the same source as the gallery inside `OnChange` creates a reload loop.
- `Sort` + `Filter` delegate; `Search` and `in` only on a text column.

## Variations

- Sort by clicking the header: `column-sort.md`.
- Row that expands into detail: `expandable-row.md`.
- Bulk selection: `bulk-selection.md`.
- Empty state and footer: `empty-state.md`, `count-footer.md`.

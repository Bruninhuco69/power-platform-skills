# Bulk selection

Maturity: **unique** · Frequency: **occasional**.

## Purpose

A checkbox per row and "select all", a counter with singular and plural, and a bulk action button, all backed by a `colSelecionados` collection (not by `Filter(gal.AllItems, ...)`).

## When to use / when not to use

**Use when**

- the same action applies to several records;
- the flow accepts a list of ids.

**Do not use when**

- the action is always on one record (use the row button);
- the list exceeds the connector limit and "all" is not all.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-chk-selecionar-todos  (CheckBox)
xx-lbl-selecao-contador  (Label)
xx-btn-lote-encerrar  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorBorderInteractive`, `fxColorPrimary`, `fxFont`, `fxLayoutMargin`, `fxFontSizeFilter`, `fxColorTextOnPrimary`, `fxBtnRadius`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtEncerrar`, `fxBtnFontSize`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varMostrarConfirmarLote`, `varShowLoading`, `varPerfil`.
- **Collections**: `colSelecionados`.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste it in Code view > Paste code, with the screen (or a container) as the parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-chk-selecionar-todos:
    Control: Classic/CheckBox@2.1.0
    Properties:
      CheckboxBorderColor: =fxColorBorderInteractive
      CheckmarkFill: =fxColorPrimary
      Default: =false
      Font: =fxFont
      Height: =40
      OnCheck: =ClearCollect(colSelecionados, 'xx-gal-pedidos'.AllItems)
      OnUncheck: =Clear(colSelecionados)
      TabIndex: =0
      Text: ="Select all"
      Width: =200
      X: =fxLayoutMargin
      Y: =270
- xx-lbl-selecao-contador:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =28
      Size: =fxFontSizeFilter
      Text: |-
        =With(
          { n: CountRows(colSelecionados) },
          n & If(n = 1, " order selected", " orders selected")
        )
      VerticalAlign: =VerticalAlign.Middle
      Visible: =CountRows(colSelecionados) > 0
      Width: =280
      X: =fxLayoutMargin + 220
      Y: =272
- xx-btn-lote-encerrar:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =Self.Fill
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      DisabledBorderColor: =fxColorDisabled
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      DisplayMode: |-
        =If(
          varShowLoading || CountRows(colSelecionados) = 0,
          DisplayMode.Disabled,
          DisplayMode.Edit
        )
      Fill: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =40
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: =Set(varMostrarConfirmarLote, true)
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtEncerrar
      Visible: =varPerfil.Flg_Encerrar
      Width: =180
      X: =fxLayoutMargin + 520
      Y: =266
```

### Row checkbox

It goes **inside the gallery template** (`Children` of `xx-gal-pedidos`), before the labels, and shifts the columns by 44 px.

```yaml
- xx-chk-gal-selecionar:
    Control: Classic/CheckBox@2.1.0
    Properties:
      CheckboxBorderColor: =fxColorBorderInteractive
      CheckmarkFill: =fxColorPrimary
      Default: =!IsBlank(LookUp(colSelecionados, <col-id> = ThisItem.<col-id>))
      Font: =fxFont
      Height: =40
      OnCheck: =Collect(colSelecionados, ThisItem)
      OnUncheck: =RemoveIf(colSelecionados, <col-id> = ThisItem.<col-id>)
      TabIndex: =0
      Text: =""
      Width: =40
      X: =4
      Y: =(Parent.TemplateHeight - Self.Height) / 2
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `colSelecionados` | the screen's collection | starts empty; `Clear` when the filter, tab or page changes |
| `<col-id>` | real key |  |
| `fxTxtEncerrar`, `varPerfil.Flg_Encerrar` | real verb and flag | the button only exists for users who have the flag |
| `varMostrarConfirmarLote` | bulk confirmation modal | see `confirm-modal.md` (text with `CountRows(colSelecionados)`) |

## Behavior

Destination of the formulas below: the same as the YAML (`,` between arguments, `;` chains).

**`xx-chk-selecionar-todos`.OnCheck**: copies the loaded items into the collection (only the ones already loaded)

```powerfx
ClearCollect(colSelecionados, 'xx-gal-pedidos'.AllItems)
```

**`xx-lbl-selecao-contador`.Text**: singular and plural in a single formula

```powerfx
With(
  { n: CountRows(colSelecionados) },
  n & If(n = 1, " order selected", " orders selected")
)
```

## Accessibility

- Empty `Text` on the row checkbox leaves it without a name for a screen reader: a limitation to record in `accessibility.md`.
- The text counter announces the current selection.

## Pitfalls

- Do not use `Filter(gal.AllItems, ...)` to find out what is selected: it only sees what is loaded and `AllItems` is expensive.
- "Select all" selects only what the gallery has loaded: if the list is truncated, the button lies; show the truncation warning.
- `Default` referencing the collection keeps the check when the gallery scrolls; without it the check disappears.
- Clear the collection when the filter changes: a selection of items that left the list is the most common cause of a wrong bulk action.

## Variations

- Bulk with a result per item: the flow returns `colResultadoLote` and `info-modal.md` shows the list.
- Single selection (radio): replace the collection with `varPedidoSel`.

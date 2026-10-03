# Cursor pagination

Maturity: **unique** · Frequency: **rare**.

## Purpose

Previous, next and "Page N of M" for a list larger than the connector limit. The cursor is the sort-key value of the last item on the page; a local stack stores the cursors of the pages already visited.

## When to use / when not to use

**Use when**

- the list exceeds `fxLimiteLinhas` and the user needs to go through all of it;
- there is a unique, stable sort key.

**Do not use when**

- the list fits within the connector limit (use search and filter);
- the sort changes on click (the cursor depends on a fixed key).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-btn-pagina-anterior  (Button)
xx-lbl-pagina-atual  (Label)
xx-btn-pagina-proxima  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTableHeaderText`, `fxColorBorder`, `fxColorDisabledText`, `fxColorDisabled`, `fxColorPrimaryLight`, `fxFont`, `fxBtnFontSize`, `fxBtnRadius`, `fxLayoutMargin`, `fxColorTextPrimary`, `fxFontSizeBody`, `fxPageSize`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxTxtAnterior`, `fxTxtProxima`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varPagina`, `varShowLoading`, `varCursorAtual`, `varPedidoTotal`.
- **Collections**: `colCursores`.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-btn-pagina-anterior:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =ColorFade(Self.Fill, -15%)
      Color: =fxColorTableHeaderText
      DisabledBorderColor: =fxColorBorder
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      DisplayMode: =If(varPagina <= 1 || varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: =fxColorPrimaryLight
      Font: =fxFont
      Height: =34
      HoverBorderColor: =ColorFade(Self.BorderColor, 20%)
      HoverColor: =fxColorTableHeaderText
      HoverFill: =ColorFade(Self.Fill, -10%)
      OnSelect: |-
        =Set(varCursorAtual, LookUp(colCursores, pag = varPagina - 1).cursor);
        RemoveIf(colCursores, pag = varPagina - 1);
        Set(varPagina, Max(1, varPagina - 1));
        Reset('xx-gal-pedidos')
      PressedColor: =fxColorTableHeaderText
      PressedFill: =ColorFade(Self.Fill, -20%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtAnterior
      Width: =150
      X: =fxLayoutMargin + 420
      Y: ='xx-gal-pedidos'.Y + 'xx-gal-pedidos'.Height + 8
- xx-lbl-pagina-atual:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: =fxColorTextPrimary
      Font: =fxFont
      Height: =34
      Size: =fxFontSizeBody
      Text: ="Page " & varPagina & " of " & Max(1, RoundUp(varPedidoTotal / fxPageSize, 0))
      VerticalAlign: =VerticalAlign.Middle
      Width: =160
      X: =fxLayoutMargin + 580
      Y: ='xx-gal-pedidos'.Y + 'xx-gal-pedidos'.Height + 8
- xx-btn-pagina-proxima:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =ColorFade(Self.Fill, -15%)
      Color: =fxColorTableHeaderText
      DisabledBorderColor: =fxColorBorder
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      DisplayMode: =If(varPagina >= Max(1, RoundUp(varPedidoTotal / fxPageSize, 0)) || varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: =fxColorPrimaryLight
      Font: =fxFont
      Height: =34
      HoverBorderColor: =ColorFade(Self.BorderColor, 20%)
      HoverColor: =fxColorTableHeaderText
      HoverFill: =ColorFade(Self.Fill, -10%)
      OnSelect: |-
        =Collect(colCursores, { pag: varPagina, cursor: varCursorAtual });
        Set(varCursorAtual, Last('xx-gal-pedidos'.AllItems).<col-chave>);
        Set(varPagina, varPagina + 1);
        Reset('xx-gal-pedidos')
      PressedColor: =fxColorTableHeaderText
      PressedFill: =ColorFade(Self.Fill, -20%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtProxima
      Width: =150
      X: =fxLayoutMargin + 750
      Y: ='xx-gal-pedidos'.Y + 'xx-gal-pedidos'.Height + 8
```

## Parameters to change

| In the block | Change to | Note |
|---|---|---|
| `<col-chave>` | unique, stable sort column | with ties the cursor skips rows |
| `varPagina`, `varCursorAtual`, `colCursores` | pagination state | created in `OnStart`; reset when the filter changes |
| `fxPageSize` | page size | existing token (100) |
| `varPedidoTotal` | scope total | the same counter as the footer |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-btn-pagina-proxima`.OnSelect**: pushes the current cursor, advances the cursor to the key of the last item and the page

```powerfx
Collect(colCursores, { pag: varPagina, cursor: varCursorAtual });
Set(varCursorAtual, Last('xx-gal-pedidos'.AllItems).<col-chave>);
Set(varPagina, varPagina + 1);
Reset('xx-gal-pedidos')
```

**`xx-btn-pagina-anterior`.OnSelect**: pops the cursor of the previous page

```powerfx
Set(varCursorAtual, LookUp(colCursores, pag = varPagina - 1).cursor);
RemoveIf(colCursores, pag = varPagina - 1);
Set(varPagina, Max(1, varPagina - 1));
Reset('xx-gal-pedidos')
```

## Accessibility

- Buttons with text ("‹ Previous", "Next ›") and a `DisplayMode` consistent with the page.
- "Page N of M" as text, read in tab order.

## Pitfalls

- Jumping to page N is not possible: the cursor only advances in sequence.
- Changing the filter without resetting the cursor shows an empty page.
- Total pages over SQL uses `CountRows`, which stops at the cap: show `fxTxtTeto` when the total hits the limit.
- The cursor `Collect` without a `Clear` when the filter changes leaks old pages.

## Variations

- Without a total: only previous and next (next is disabled when the page returns fewer than `fxPageSize` items).
- Infinite scroll: the gallery already paginates natively within the connector limit; use it only if the list fits.

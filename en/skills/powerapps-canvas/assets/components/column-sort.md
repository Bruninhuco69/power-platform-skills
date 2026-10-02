# Sortable header

Maturity: **unique** · Frequency: **rare**.

## Purpose

Clickable column header that sorts the gallery: the first click sorts ascending, the second reverses, and the active column shows the arrow in its own text.

## When to use / when not to use

**Use when**

- the user needs to reorder the same list by more than one column;
- the sort is delegable to the source.

**Do not use when**

- the order is a fixed business rule (descending date is enough in the `Items` `Sort`);
- the source does not delegate `SortByColumns` and the list exceeds the connector limit.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-hdr-gal-codigo  (Button)
xx-hdr-gal-data  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTableHeaderText`, `fxColorTableHeaderBg`, `fxFont`, `fxFontSizeHeader`, `fxLayoutMargin`, `fxTableHeaderHeight`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxTxtOrdemAsc`, `fxTxtOrdemDesc`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varPedidoSortColuna`, `varPedidoSortAsc`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-hdr-gal-codigo:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      HoverColor: =fxColorTableHeaderText
      HoverFill: =ColorFade(Self.Fill, -10%)
      OnSelect: |-
        =If(
          varPedidoSortColuna = "<col-codigo>",
          Set(varPedidoSortAsc, !varPedidoSortAsc),
          Set(varPedidoSortColuna, "<col-codigo>");
          Set(varPedidoSortAsc, true)
        )
      PressedColor: =fxColorTableHeaderText
      PressedFill: =ColorFade(Self.Fill, -20%)
      Size: =fxFontSizeHeader
      TabIndex: =0
      Text: ="Code" & If(varPedidoSortColuna = "<col-codigo>", If(varPedidoSortAsc, fxTxtOrdemAsc, fxTxtOrdemDesc), "")
      Width: =160
      X: =fxLayoutMargin
      Y: =300
- xx-hdr-gal-data:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      HoverColor: =fxColorTableHeaderText
      HoverFill: =ColorFade(Self.Fill, -10%)
      OnSelect: |-
        =If(
          varPedidoSortColuna = "<col-data>",
          Set(varPedidoSortAsc, !varPedidoSortAsc),
          Set(varPedidoSortColuna, "<col-data>");
          Set(varPedidoSortAsc, true)
        )
      PressedColor: =fxColorTableHeaderText
      PressedFill: =ColorFade(Self.Fill, -20%)
      Size: =fxFontSizeHeader
      TabIndex: =0
      Text: ="Created" & If(varPedidoSortColuna = "<col-data>", If(varPedidoSortAsc, fxTxtOrdemAsc, fxTxtOrdemDesc), "")
      Width: =160
      X: =fxLayoutMargin + 160
      Y: =300
```

## Parameters to change

| In the block | Change to | Note |
|---|---|---|
| `<col-codigo>`, `<col-data>` | real column names | the string is the **physical** name; a mistake raises no error, it just sorts nothing |
| `varPedidoSortColuna`, `varPedidoSortAsc` | the screen's sort variables | created in `OnVisible` with the default order |
| `fxTxtOrdemAsc`, `fxTxtOrdemDesc` | arrows | new tokens |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-hdr-gal-codigo`.OnSelect**: same column reverses the direction; a new column starts ascending

```powerfx
If(
  varPedidoSortColuna = "<col-codigo>",
  Set(varPedidoSortAsc, !varPedidoSortAsc),
  Set(varPedidoSortColuna, "<col-codigo>");
  Set(varPedidoSortAsc, true)
)
```

**`xx-hdr-gal-codigo`.Text**: the arrow appears only on the active column

```powerfx
"Code" & If(varPedidoSortColuna = "<col-codigo>", If(varPedidoSortAsc, fxTxtOrdemAsc, fxTxtOrdemDesc), "")
```

## Accessibility

- The header text changes ("Code ▲"): the screen reader reads the current order.
- Unlike the passive header, this one is focusable: keep it in the tab order, before the gallery.
- `HoverColor` and `PressedColor` equal to `fxColorTableHeaderText` (they never invert with the background).

## Pitfalls

- A wrong column name in the string gives no error or warning: the list does not reorder. `[unverified: SortByColumns delegation with a column name in a variable on the SQL connector]`.
- Changing the sort without returning to the first row leaves the user in the middle of the list: `Reset('xx-gal-pedidos')` in `OnSelect` if the list is long.
- The arrow is text: do not use a colored emoji instead.

## Variations

- Sorting by two columns: chain `SortByColumns(fonte, "colA", ..., "colB", ...)`.
- Sorting only a local collection: change to `Sort(colX, ...)`, which has no delegation restriction.

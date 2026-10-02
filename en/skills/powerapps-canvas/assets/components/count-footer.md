# "Showing N of M" footer

Maturity: **unique** · Frequency: **occasional**.

## Purpose

Line under the gallery that says how many records appear and out of how many in the current scope, with an honest cap (`2,000+`) and the conditional scope suffix.

## When to use / when not to use

**Use when**

- the list has no pagination and the real total matters;
- the scope (unit) changes the universe and the user needs to know.

**Do not use when**

- the list is paginated (use `cursor-pagination.md`);
- the total is irrelevant (short, fixed list).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-lbl-tabela-total  (Label)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTextSecondary`, `fxFont`, `fxFontSizeTableSmall`, `fxLimiteLinhas`, `fxTxtTeto`, `fxLayoutMargin`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxTxtExibindo`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varPedidoTotal`, `varUnidadeFiltro`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-lbl-tabela-total:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Right
      Color: =fxColorTextSecondary
      Font: =fxFont
      Height: =32
      Size: =fxFontSizeTableSmall
      Text: |-
        =fxTxtExibindo & " " & 'xx-gal-pedidos'.AllItemsCount & " of "
          & If(varPedidoTotal >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoTotal, "[$-en-US]#,##0"))
          & " orders "
          & If(IsBlank(varUnidadeFiltro), "from all units", "from unit " & varUnidadeFiltro)
      VerticalAlign: =VerticalAlign.Middle
      Width: ='xx-gal-pedidos'.Width
      X: =fxLayoutMargin
      Y: ='xx-gal-pedidos'.Y + 'xx-gal-pedidos'.Height + 40
```

## Parameters to change

| In the block | Change to | Note |
|---|---|---|
| `'xx-gal-pedidos'` | the screen's gallery |  |
| `varPedidoTotal` | scope counter | recounted as in the cards |
| `orders` | plural noun |  |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-lbl-tabela-total`.Text**: N local (loaded items), M from the counter with a cap, and the scope suffix

```powerfx
fxTxtExibindo & " " & 'xx-gal-pedidos'.AllItemsCount & " of "
  & If(varPedidoTotal >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoTotal, "[$-en-US]#,##0"))
  & " orders "
  & If(IsBlank(varUnidadeFiltro), "from all units", "from unit " & varUnidadeFiltro)
```

## Accessibility

- Static informational text: no focus; the screen reader reads it after the list.
- `fxColorTextSecondary` keeps a 4.5:1 contrast.

## Pitfalls

- A fixed scope suffix (`"from unit " & varUnidadeFiltro`) prints "from unit " and stops when the filter is empty (total scope): use the `If(IsBlank(...))`.
- `IsBlank` and not `= ""`: empty and `Blank()` get mixed up in Power Fx and empty **means** total scope.
- A raw M at the cap (`2000`) looks like a total: always `fxTxtTeto`.

## Variations

- Without scope: remove the last `& If(...)`.
- With pagination: replace with `varPagina` and total pages.

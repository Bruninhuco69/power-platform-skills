# Empty state and truncated-list notice

Maturity: **stable** · Frequency: **very common** (the truncated-list notice is less common).

## Purpose

The gallery has no native empty state: a `Label` bound to the gallery itself warns when there is no result (what happened and what to do), and an amber notice warns when the counter hit the connector ceiling.

## When to use / when not to use

**Use when**

- every filterable gallery;
- the list may be truncated by the connector limit (count over SQL).

**Do not use when**

- the absence of data is a load error (show an error message with the try-again action);
- the list is a small local collection that is always populated.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-lbl-gal-vazio  (Label)
xx-lbl-gal-truncado  (Label)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTextSecondary`, `fxFont`, `fxFontSizeBody`, `fxMsgNoResultsError`, `fxMsgNoResultsHint`, `fxBadgeWarningText`, `fxFontSizeFilter`, `fxMsgListaTruncada`, `fxBadgeWarningBg`, `fxLimiteLinhas`.
- **Global variables** (born in `OnStart`, `assets/app-onstart-template.md`): `varPedidoTotal`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as the parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-lbl-gal-vazio:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: =fxColorTextSecondary
      Font: =fxFont
      Height: =120
      Size: =fxFontSizeBody
      Text: =fxMsgNoResultsError & Char(10) & fxMsgNoResultsHint
      VerticalAlign: =VerticalAlign.Middle
      Visible: ='xx-gal-pedidos'.Visible && 'xx-gal-pedidos'.AllItemsCount = 0
      Width: ='xx-gal-pedidos'.Width
      X: ='xx-gal-pedidos'.X
      Y: ='xx-gal-pedidos'.Y + 80
- xx-lbl-gal-truncado:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: =fxBadgeWarningText
      Fill: =fxBadgeWarningBg
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =28
      Size: =fxFontSizeFilter
      Text: =fxMsgListaTruncada
      VerticalAlign: =VerticalAlign.Middle
      Visible: =varPedidoTotal >= fxLimiteLinhas
      Width: ='xx-gal-pedidos'.Width
      X: ='xx-gal-pedidos'.X
      Y: ='xx-gal-pedidos'.Y + 'xx-gal-pedidos'.Height + 8
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `'xx-gal-pedidos'` | gallery name | the empty and truncated notices depend on it |
| `varPedidoTotal` | screen counter | the same as the KPI card and the footer |
| `fxMsgNoResultsError`, `fxMsgNoResultsHint`, `fxMsgListaTruncada` | project texts | pair "what happened" + "what to do" |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-lbl-gal-vazio`.Visible**: only when the gallery is visible **and** has no items

```powerfx
'xx-gal-pedidos'.Visible && 'xx-gal-pedidos'.AllItemsCount = 0
```

**`xx-lbl-gal-truncado`.Visible**: only when the counter hit the limit

```powerfx
varPedidoTotal >= fxLimiteLinhas
```

## Accessibility

- Text color with a 4.5:1 contrast (`fxColorTextSecondary`); the light gray of a placeholder fails.
- Message in two short sentences: what happened and what to do.

## Pitfalls

- A truncated list with no notice is a UX error, not just a data one: the user believes they saw everything.
- `AllItemsCount` is local and cheap; `CountRows(AllItems)` also works, but do not swap it for `CountRows(source)`.
- The empty notice shows while the query is still loading if `Visible` does not depend on loading: combine it with `varShowLoading` if the list is slow.

## Variations

- Empty with no active filter ("No orders registered") vs. with a filter ("No results"): `If(<active filter>, fxMsgNoResultsError, "No orders registered")`.
- Load error: a third label with `fxMsgFalhaFlow` and a "Try again" button.

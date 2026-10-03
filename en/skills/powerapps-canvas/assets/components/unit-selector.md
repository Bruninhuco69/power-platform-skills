# Unit selector

Maturity: **stable** · Frequency: **common** (in the header or as a filter).

## Purpose

A combo box that changes the screen's **read scope** (`varUnidadeFiltro`). It only appears for users who can choose: a global role or more than one unit. Empty goes back to the user's home scope, never to the whole database.

## When to use / when not to use

**Use when**

- the user can see more than one unit;
- counters and gallery must obey the same scope.

**Do not use when**

- the user has only one unit (the combo box is hidden through `Visible`, not removed);
- scope as an access rule: the barrier belongs to the flow, the combo box is only a navigation convenience.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-lbl-unidade-escopo  (Label)
xx-cbo-unidade  (ComboBox)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTextSecondary`, `fxFont`, `fxFontSizeFilter`, `fxLayoutMargin`, `fxFilterHeight`, `fxColorBorderInteractive`, `fxColorTextPrimary`, `fxColorPrimary`.
- **Tokens of the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxHeaderHeight`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varUnidadeFiltro`, `varTodasUnidades`, `varUnidadeLotacao`, `varPedidoTotal`.
- **Collections**: `colUnidadesEscopo`.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste it in Code view > Paste code, with the screen (or a container) as the parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-lbl-unidade-escopo:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Right
      Color: =fxColorTextSecondary
      Font: =fxFont
      Height: =fxFilterHeight
      Size: =fxFontSizeFilter
      Text: |-
        ="Scope: " & If(IsBlank(varUnidadeFiltro), "all units", varUnidadeFiltro)
      VerticalAlign: =VerticalAlign.Middle
      Width: =260
      X: =Parent.Width - fxLayoutMargin - 180 - 8 - 260
      Y: =(fxHeaderHeight - fxFilterHeight) / 2
- xx-cbo-unidade:
    Control: Classic/ComboBox@2.4.0
    Properties:
      BorderColor: =fxColorBorderInteractive
      Color: =fxColorTextPrimary
      DisplayFields: =["Sigla"]
      FocusedBorderColor: =fxColorPrimary
      Height: =fxFilterHeight
      InputTextPlaceholder: =If(varTodasUnidades, "(All units)", "Find unit")
      Items: =colUnidadesEscopo
      OnChange: |-
        =Set(
          varUnidadeFiltro,
          If(
            IsBlank(Self.Selected),
            If(varTodasUnidades, "", varUnidadeLotacao),
            Self.Selected.Sigla
          )
        );
        Set(
          varPedidoTotal,
          CountRows(Filter('<fonte>', StartsWith(<col-unidade>, varUnidadeFiltro)))
        )
      SearchFields: =["Sigla"]
      SelectMultiple: =false
      Visible: =varTodasUnidades || CountRows(colUnidadesEscopo) > 1
      Width: =180
      X: =Parent.Width - fxLayoutMargin - Self.Width
      Y: =(fxHeaderHeight - fxFilterHeight) / 2
```

### Variation: cascading region and unit

The second combo box lists only the units of the chosen region; `Reset()` in the first one's `OnChange` clears the second one's selection.

```yaml
- xx-cbo-regiao:
    Control: Classic/ComboBox@2.4.0
    Properties:
      BorderColor: =fxColorBorderInteractive
      Color: =fxColorTextPrimary
      DisplayFields: =["Result"]
      FocusedBorderColor: =fxColorPrimary
      Height: =fxFilterHeight
      InputTextPlaceholder: ="Region"
      IsSearchable: =false
      Items: =Distinct(colUnidadesEscopo, Regiao)
      OnChange: =Reset('xx-cbo-unidade-filtrada')
      SearchFields: =["Result"]
      SelectMultiple: =false
      Width: =160
      X: =20
      Y: =44
- xx-cbo-unidade-filtrada:
    Control: Classic/ComboBox@2.4.0
    Properties:
      BorderColor: =fxColorBorderInteractive
      Color: =fxColorTextPrimary
      DisplayFields: =["Sigla"]
      FocusedBorderColor: =fxColorPrimary
      Height: =fxFilterHeight
      InputTextPlaceholder: ="Unit"
      Items: =Filter(colUnidadesEscopo, IsBlank('xx-cbo-regiao'.Selected) || Regiao = 'xx-cbo-regiao'.Selected.Result)
      OnChange: =Set(varUnidadeFiltro, Coalesce(Self.Selected.Sigla, If(varTodasUnidades, "", varUnidadeLotacao)))
      SearchFields: =["Sigla"]
      SelectMultiple: =false
      Width: =160
      X: =196
      Y: =44
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `'<fonte>'`, `<col-unidade>` | real table and column | `StartsWith` delegates and covers both modes (equality and empty = all) |
| `colUnidadesEscopo` | collection loaded in `OnStart` | what the user **can** choose (keyed by the home unit, not by the filter) |
| `Sigla`, `Regiao` | real columns of the collection | `Trim()` on load, once |
| `varPedidoTotal` | the screen's counter(s) | recount in the same `OnChange` |

## Behavior

Destination of the formulas below: the same as the YAML (`,` between arguments, `;` chains).

**`xx-cbo-unidade`.OnChange**: empty goes back to the home unit (or to all, for a global role); then the counters are recounted

```powerfx
Set(
  varUnidadeFiltro,
  If(
    IsBlank(Self.Selected),
    If(varTodasUnidades, "", varUnidadeLotacao),
    Self.Selected.Sigla
  )
);
Set(
  varPedidoTotal,
  CountRows(Filter('<fonte>', StartsWith(<col-unidade>, varUnidadeFiltro)))
)
```

**`xx-cbo-unidade`.Visible**: only users who can choose see the selector

```powerfx
varTodasUnidades || CountRows(colUnidadesEscopo) > 1
```

## Accessibility

- The "Scope: ..." label shows in text what the combo box applies, useful for anyone who reads only through a screen reader.
- The classic combo box is keyboard navigable; keep `TabIndex` consistent with the header.

## Pitfalls

- `Visible` with only `CountRows(...) > 1` hides the combo box from a user with a global role and a one-row collection: the first branch (`varTodasUnidades`) solves it.
- Writing the read scope into `varUnidadeLotacao` erases the user's home unit: they are separate variables.
- Sending `varUnidadeFiltro` as the write unit saves to the wrong place: the flow derives the unit from the record.
- `SearchFields: =[""]` inherits the Dataverse primary name concept and yields a blank row; use the real column.

## Variations

- Fixed scope chip (no combo box) for a single-unit user: just the `xx-lbl-unidade-escopo` label.
- Cascade (above).

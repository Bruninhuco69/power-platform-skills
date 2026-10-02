# Filter bar (combo, text, dates and clear)

Maturity: **stable** · Frequency: **common** (the combination varies: combo, search, dates; the Clear button is in all of them).

## Purpose

Filter strip above a gallery: status combo, search by start of the code, date range and a Clear button. The filters feed the gallery `Items` directly, with no Filter button.

## When to use / when not to use

**Use when**

- gallery with more than about 50 records;
- the filters are delegable on the connector (`StartsWith`, equality, whole-date range).

**Do not use when**

- the query is expensive and must run only on demand (use the variation with a Filter button);
- the filter needs `Search` or `in` on a non-text column (it does not delegate).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-con-filtros  (GroupContainer)
  xx-lbl-filtro-status  (Label)
  xx-cbo-filtro-status  (ComboBox)
  xx-lbl-filtro-busca  (Label)
  xx-txt-filtro-busca  (TextInput)
  xx-lbl-filtro-de  (Label)
  xx-dtp-filtro-de  (DatePicker)
  xx-lbl-filtro-ate  (Label)
  xx-dtp-filtro-ate  (DatePicker)
  xx-btn-filtro-limpar  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxLayoutMargin`, `fxLayoutGutter`, `fxColorTextSecondary`, `fxFont`, `fxFontSizeHeader`, `fxColorBorderInteractive`, `fxColorTextPrimary`, `fxColorPrimary`, `fxFilterHeight`, `fxFontSizeFilter`, `fxBtnRadius`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxTxtLimpar`, `fxBtnWidthFilter`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtFiltrar`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxHeaderHeight`.
- **Global variables** (born with a neutral value in `OnStart`, `assets/app-onstart-template.md`; the date-window ones are reset again in the screen `OnVisible`): `varPedidoDe`, `varPedidoAte`, `varPedidoFiltroAplicado`, `varPedidoStatusAplicado`, `varPedidoBuscaAplicada`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as the parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-con-filtros:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorBorder
      BorderThickness: =1
      Fill: =fxColorSurface
      Height: =104
      RadiusBottomLeft: =fxModalRadius
      RadiusBottomRight: =fxModalRadius
      RadiusTopLeft: =fxModalRadius
      RadiusTopRight: =fxModalRadius
      Width: =1180
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + fxLayoutGutter
    Children:
      - xx-lbl-filtro-status:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextSecondary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =20
            Size: =fxFontSizeHeader
            Text: ="Status"
            Width: =180
            X: =20
            Y: =16
      - xx-cbo-filtro-status:
          Control: Classic/ComboBox@2.4.0
          Properties:
            BorderColor: =fxColorBorderInteractive
            Color: =fxColorTextPrimary
            DisplayFields: =["Value"]
            FocusedBorderColor: =fxColorPrimary
            Height: =fxFilterHeight
            InputTextPlaceholder: ="All"
            IsSearchable: =false
            Items: =["open", "in progress", "completed"]
            SearchFields: =["Value"]
            SelectMultiple: =false
            Width: =180
            X: =20
            Y: =44
      - xx-lbl-filtro-busca:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextSecondary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =20
            Size: =fxFontSizeHeader
            Text: ="Code"
            Width: =180
            X: =216
            Y: =16
      - xx-txt-filtro-busca:
          Control: Classic/TextInput@2.3.2
          Properties:
            BorderColor: =If(IsBlank(Self.Text), fxColorBorderInteractive, fxColorPrimary)
            Color: =fxColorTextPrimary
            Default: =""
            DelayOutput: =true
            FocusedBorderColor: =fxColorPrimary
            Font: =fxFont
            Height: =fxFilterHeight
            HintText: ="Search by start of code"
            RadiusBottomLeft: =fxBtnRadius
            RadiusBottomRight: =fxBtnRadius
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxFontSizeFilter
            TabIndex: =0
            Width: =240
            X: =216
            Y: =44
      - xx-lbl-filtro-de:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextSecondary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =20
            Size: =fxFontSizeHeader
            Text: ="From"
            Width: =180
            X: =472
            Y: =16
      - xx-dtp-filtro-de:
          Control: Classic/DatePicker@2.6.0
          Properties:
            BorderColor: =fxColorBorderInteractive
            DefaultDate: =Blank()
            FocusedBorderColor: =fxColorPrimary
            Font: =fxFont
            Format: ="mm/dd/yyyy"
            Height: =fxFilterHeight
            IconBackground: =fxColorPrimary
            IconFill: =fxColorSurface
            OnChange: |-
              =Set(
                varPedidoDe,
                If(
                  IsBlank(Self.SelectedDate),
                  Blank(),
                  36524 + DateDiff(Date(2000, 1, 1), Self.SelectedDate, TimeUnit.Days)
                )
              )
            TabIndex: =0
            Width: =180
            X: =472
            Y: =44
      - xx-lbl-filtro-ate:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextSecondary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =20
            Size: =fxFontSizeHeader
            Text: ="To"
            Width: =180
            X: =668
            Y: =16
      - xx-dtp-filtro-ate:
          Control: Classic/DatePicker@2.6.0
          Properties:
            BorderColor: =fxColorBorderInteractive
            DefaultDate: =Blank()
            FocusedBorderColor: =fxColorPrimary
            Font: =fxFont
            Format: ="mm/dd/yyyy"
            Height: =fxFilterHeight
            IconBackground: =fxColorPrimary
            IconFill: =fxColorSurface
            OnChange: |-
              =Set(
                varPedidoAte,
                If(
                  IsBlank(Self.SelectedDate),
                  Blank(),
                  36524 + DateDiff(Date(2000, 1, 1), Self.SelectedDate, TimeUnit.Days)
                )
              )
            TabIndex: =0
            Width: =180
            X: =668
            Y: =44
      - xx-btn-filtro-limpar:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorButtonCancel
            BorderThickness: =1
            Color: =fxColorTextOnPrimary
            Fill: =fxColorButtonCancel
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =fxFilterHeight
            HoverBorderColor: =fxColorButtonCancelHover
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorButtonCancelHover
            OnSelect: |-
              =Reset('xx-cbo-filtro-status');
              Reset('xx-txt-filtro-busca');
              Reset('xx-dtp-filtro-de');
              Reset('xx-dtp-filtro-ate');
              // DatePicker Reset does not fire OnChange: rewrite the variable
              Set(varPedidoDe, Blank());
              Set(varPedidoAte, Blank())
            PressedBorderColor: =fxColorButtonCancelHover
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorButtonCancelHover
            RadiusBottomLeft: =fxBtnRadius
            RadiusBottomRight: =fxBtnRadius
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxFontSizeFilter
            TabIndex: =0
            Text: =fxTxtLimpar
            Width: =fxBtnWidthFilter
            X: =864
            Y: =44
```

### Variation: with a Filter button

The gallery lists only after the click: the controls do not filter, the button copies the value to "applied" variables and the gallery reads those variables. Replace the `xx-btn-filtro-limpar` button with this pair.

```yaml
- xx-btn-filtro-aplicar:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =Self.Fill
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      DisabledBorderColor: =fxColorDisabled
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      Fill: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxFilterHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: |-
        =Set(varPedidoFiltroAplicado, true);
        Set(varPedidoStatusAplicado, Coalesce('xx-cbo-filtro-status'.Selected.Value, ""));
        Set(varPedidoBuscaAplicada, Trim('xx-txt-filtro-busca'.Text))
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxFontSizeFilter
      TabIndex: =0
      Text: =fxTxtFiltrar
      Width: =fxBtnWidthFilter
      X: =864
      Y: =44
- xx-btn-filtro-limpar-aplicado:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorButtonCancel
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      Fill: =fxColorButtonCancel
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxFilterHeight
      HoverBorderColor: =fxColorButtonCancelHover
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =fxColorButtonCancelHover
      OnSelect: |-
        =Reset('xx-cbo-filtro-status');
        Reset('xx-txt-filtro-busca');
        Set(varPedidoFiltroAplicado, false);
        Set(varPedidoStatusAplicado, "");
        Set(varPedidoBuscaAplicada, "")
      PressedBorderColor: =fxColorButtonCancelHover
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =fxColorButtonCancelHover
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxFontSizeFilter
      TabIndex: =0
      Text: =fxTxtLimpar
      Width: =fxBtnWidthFilter
      X: =1004
      Y: =44
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `xx-` | screen prefix |  |
| `'xx-cbo-filtro-status'` and `["Open", ...]` | control and domain of real values | small fixed list; a large domain comes from a `col*` collection |
| `varPedidoDe`, `varPedidoAte` | the screen's date-window variables | integers; `Blank()` in `OnStart` and again in `OnVisible` |
| `36524` | days between 1900-01-01 and 2000-01-01 | only if the database column `Ref_<col>` is `DATEDIFF(day, 0, <col>)` |
| `fxTxtLimpar`, `fxTxtFiltrar` | text tokens |  |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-dtp-filtro-de`.OnChange**: converts the chosen date into an integer (number of days since 1900-01-01), which is what the database computed column compares and delegates

```powerfx
Set(
  varPedidoDe,
  If(
    IsBlank(Self.SelectedDate),
    Blank(),
    36524 + DateDiff(Date(2000, 1, 1), Self.SelectedDate, TimeUnit.Days)
  )
)
```

**`xx-btn-filtro-limpar`.OnSelect**: clears the controls and **rewrites** the date variables

```powerfx
Reset('xx-cbo-filtro-status');
Reset('xx-txt-filtro-busca');
Reset('xx-dtp-filtro-de');
Reset('xx-dtp-filtro-ate');
// DatePicker Reset does not fire OnChange: rewrite the variable
Set(varPedidoDe, Blank());
Set(varPedidoAte, Blank())
```

## Accessibility

- Each filter has a visible label above it (a placeholder disappears when typing and is not a label).
- The text field border changes from gray to blue when there is a value, and `fxColorBorderInteractive` keeps a control-border contrast of at least 3:1.
- Combo, text and dates are focusable in left-to-right order (`TabIndex: =0`).

## Pitfalls

- `Reset()` on a `DatePicker` does not fire `OnChange`: without rewriting the variables, the gallery stays filtered by a date the control no longer shows.
- `Size`, `Radius*` and `FocusedBorderThickness` do not exist on `ComboBox` and `DatePicker` (PA2108).
- `DefaultDate: =Blank()` keeps the period filter empty at the start; a date default hides old records.
- `IsSearchable` is true by default: when removing search from a combo, **delete** the property or use `false`; never set the value to `true`.

## Variations

- Reactive (main) or with a Filter button (above).
- Unit selector: `unit-selector.md`.
- Combo with many items: `IsSearchable: =true` e `Items: =colUnidades`.

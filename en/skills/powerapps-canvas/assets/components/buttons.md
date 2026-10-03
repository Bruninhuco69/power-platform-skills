# Buttons: primary, secondary, destructive and neutral

Maturity: **stable** · Frequency: **very common**.

## Purpose

The four button roles with the same geometry (`fxBtnHeight`, `fxBtnRadius`), a hover that darkens and a pressed state that never swaps `Fill` and `Color`.

## When to use / when not to use

**Use when**

- any action button: choose the role by the nature of the action, never by the text;
- a new button in the app: start from here.

**Do not use when**

- a button inside a gallery with a row height (use height 30 to 34 and `fxFontSizeTableSmall`);
- menu navigation (use `side-menu.md`).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-btn-primario  (Button)
xx-btn-secundario  (Button)
xx-btn-destrutivo  (Button)
xx-btn-neutro  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTextOnPrimary`, `fxColorPrimary`, `fxFont`, `fxBtnRadius`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtConfirmar`, `fxBtnFontSize`, `fxBtnWidth`, `fxBtnHeight`, `fxColorButtonCancel`, `fxColorButtonCancelHover`, `fxTxtCancelar`, `fxColorError`, `fxColorTableHeaderText`, `fxColorPrimaryLight`.
- **Global variables** (born in `OnStart`, `assets/app-onstart-template.md`): `varShowLoading`, `varMostrarConfirmar`, `varMostrarCancelar`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-btn-primario:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =Self.Fill
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      DisabledBorderColor: =fxColorDisabled
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      DisplayMode: =If(varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: |-
        =Set(varShowLoading, true);
        Set(varShowLoading, false)
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtConfirmar
      Width: =fxBtnWidth
      X: =20
      Y: =20
- xx-btn-secundario:
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
      OnSelect: =Set(varMostrarConfirmar, false)
      PressedBorderColor: =fxColorButtonCancelHover
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =fxColorButtonCancelHover
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtCancelar
      Width: =fxBtnWidth
      X: =20
      Y: =20
- xx-btn-destrutivo:
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
          Len(Trim('xx-txt-motivo'.Text)) < 5,
          DisplayMode.Disabled,
          DisplayMode.Edit
        )
      Fill: =fxColorError
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: =Set(varMostrarCancelar, false)
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="Confirm cancellation"
      Width: =230
      X: =20
      Y: =20
- xx-btn-neutro:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =ColorFade(Self.Fill, -15%)
      Color: =fxColorTableHeaderText
      Fill: =fxColorPrimaryLight
      Font: =fxFont
      Height: =fxBtnHeight
      HoverFill: =ColorFade(Self.Fill, -10%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="Short label"
      Width: =140
      X: =20
      Y: =20
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `fxTxtConfirmar`, `fxTxtCancelar` | the action's verb | in the modal, the right one is the verb (`Save`, `Complete`), the left one `Back` |
| `'xx-txt-motivo'` | reason field | destructive rule; change the minimum of 5 |
| `X`, `Y`, `Width` | real position | the primary takes the **same position** on every screen |

## Behavior

Destination of the formulas below: the same as the YAML (`,` between arguments, `;` chains).

**`xx-btn-primario`.DisplayMode**: disables during processing

```powerfx
If(varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
```

**`xx-btn-destrutivo`.DisplayMode**: enables only with a reason

```powerfx
If(
  Len(Trim('xx-txt-motivo'.Text)) < 5,
  DisplayMode.Disabled,
  DisplayMode.Edit
)
```

## Accessibility

- Icon button: no `AccessibleLabel` (PA2108 on `Classic/Button@2.2.0`); use `Tooltip` and descriptive text.
- `Disabled*` always defined: disabled text must be distinguishable from enabled.
- `TabIndex: =0` on all: natural screen order.

## Pitfalls

- **Pressed** never swaps `Fill` and `Color` (a white button on white disappears when pressed): use `ColorFade(Self.Fill, -30%)`.
- **Hover** darkens on all buttons: never lightens on one and darkens on another.
- Green is state, never action; a destructive action is always `fxColorError`.
- No emoji as semantics (`✅ Yes`, `❌ Cancel`).
- `Radius*` on `Classic/Button@2.2.0` is accepted; on `Rectangle`, `ComboBox` and `DatePicker` it is not.

## Variations

- Filter button: height `fxFilterHeight` and width `fxBtnWidthFilter` (see `filter-bar.md`).
- Button with a loading state: `Text: =If(varShowLoading, fxTxtProcessando, <verb>)`.

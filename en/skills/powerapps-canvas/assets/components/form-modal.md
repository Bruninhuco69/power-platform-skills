# Form modal

Maturity: **stable** · Frequency: **common**.

## Purpose

Scrim and larger card with fields (combo, search and long text), a validation message in a single place and the `Cancel`/verb pair. The confirm button only enables when the validation is empty.

## When to use / when not to use

**Use when**

- creating or editing a record with few fields (up to about 8);
- the validation is local and simple.

**Do not use when**

- the form has many fields or steps (use a dedicated screen: this is also the accessibility recommendation);
- the flow needs its own URL.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-mod-form  (GroupContainer)
  xx-mod-form-bloqueio  (Button)
  xx-mod-form-card  (GroupContainer)
    xx-mod-form-titulo  (Label)
    xx-mod-form-lbl-tipo  (Label)
    xx-cbo-form-tipo  (ComboBox)
    xx-mod-form-lbl-item  (Label)
    xx-cbo-form-item  (ComboBox)
    xx-mod-form-lbl-descricao  (Label)
    xx-txt-form-descricao  (TextInput)
    xx-mod-form-lbl-validacao  (Label)
    xx-mod-form-btn-voltar  (Button)
    xx-mod-form-btn-confirmar  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorOverlayDark`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxColorPrimaryDark`, `fxFont`, `fxModalTitleSize`, `fxModalPadding`, `fxColorTextSecondary`, `fxFontSizeHeader`, `fxColorBorderInteractive`, `fxColorTextPrimary`, `fxColorPrimary`, `fxFilterHeight`, `fxFontSizeFilter`, `fxBtnRadius`, `fxColorError`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxTxtCancelar`, `fxBtnFontSize`, `fxBtnHeight`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtProcessando`, `fxTxtSalvar`, `fxMsgFalhaFlow`, `fxLayoutMargin`, `fxLayoutGutter`, `fxBtnWidth`.
- **Tokens of the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxModalWidthL`, `fxHeaderHeight`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varMostrarForm`, `varUnidadeFiltro`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType`, `varToastMessage`, `varShowToast`, `varPedidoTotal`, `varPerfil`.
- **Collections**: none.
- **Flows**: `app-flow-pedido-acao`.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-mod-form:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlayDark
      Height: =Parent.Height
      Visible: =varMostrarForm
      Width: =Parent.Width
    Children:
      - xx-mod-form-bloqueio:
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
      - xx-mod-form-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =470
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxModalWidthL
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-mod-form-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorPrimaryDark
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =32
                  Size: =fxModalTitleSize
                  Text: ="New order"
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =fxModalPadding
            - xx-mod-form-lbl-tipo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =20
                  Size: =fxFontSizeHeader
                  Text: ="Type"
                  Width: =270
                  X: =fxModalPadding
                  Y: =70
            - xx-cbo-form-tipo:
                Control: Classic/ComboBox@2.4.0
                Properties:
                  BorderColor: =fxColorBorderInteractive
                  Color: =fxColorTextPrimary
                  DisplayFields: =["Value"]
                  FocusedBorderColor: =fxColorPrimary
                  Height: =fxFilterHeight
                  InputTextPlaceholder: ="Select the type"
                  IsSearchable: =false
                  Items: =["Standard", "Urgent", "Other"]
                  SearchFields: =["Value"]
                  SelectMultiple: =false
                  Width: =270
                  X: =fxModalPadding
                  Y: =94
            - xx-mod-form-lbl-item:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =20
                  Size: =fxFontSizeHeader
                  Text: ="Item"
                  Width: =280
                  X: =320
                  Y: =70
            - xx-cbo-form-item:
                Control: Classic/ComboBox@2.4.0
                Properties:
                  BorderColor: =fxColorBorderInteractive
                  Color: =fxColorTextPrimary
                  DisplayFields: =["<col-codigo>"]
                  FocusedBorderColor: =fxColorPrimary
                  Height: =fxFilterHeight
                  InputTextPlaceholder: ="Search by code"
                  Items: |-
                    =Sort(
                      Filter('<fonte-item>', StartsWith(<col-unidade>, varUnidadeFiltro)),
                      <col-codigo>
                    )
                  SearchFields: =["<col-codigo>"]
                  SelectMultiple: =false
                  Width: =280
                  X: =320
                  Y: =94
            - xx-mod-form-lbl-descricao:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =20
                  Size: =fxFontSizeHeader
                  Text: ="Description"
                  Width: =580
                  X: =fxModalPadding
                  Y: =166
            - xx-txt-form-descricao:
                Control: Classic/TextInput@2.3.2
                Properties:
                  BorderColor: =fxColorBorderInteractive
                  Color: =fxColorTextPrimary
                  Default: =""
                  FocusedBorderColor: =fxColorPrimary
                  Font: =fxFont
                  Height: =140
                  HintText: ="Minimum 10 characters"
                  MaxLength: =1000
                  Mode: =TextMode.MultiLine
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxFontSizeFilter
                  TabIndex: =0
                  Width: =580
                  X: =fxModalPadding
                  Y: =190
            - xx-mod-form-lbl-validacao:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorError
                  Font: =fxFont
                  Height: =24
                  Size: =fxFontSizeFilter
                  Text: |-
                    =If(
                      IsBlank('xx-cbo-form-tipo'.Selected),
                      "Select the type.",
                      IsBlank('xx-cbo-form-item'.Selected),
                      "Select the item.",
                      Len(Trim('xx-txt-form-descricao'.Text)) < 10,
                      "Describe it with at least 10 characters.",
                      ""
                    )
                  Width: =580
                  X: =fxModalPadding
                  Y: =338
            - xx-mod-form-btn-voltar:
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
                  OnSelect: =Set(varMostrarForm, false)
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
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
            - xx-mod-form-btn-confirmar:
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
                      varShowLoading || !IsBlank('xx-mod-form-lbl-validacao'.Text),
                      DisplayMode.Disabled,
                      DisplayMode.Edit
                    )
                  Fill: =fxColorPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxBtnHeight
                  HoverBorderColor: =ColorFade(Self.Fill, -20%)
                  HoverColor: =fxColorTextOnPrimary
                  HoverFill: =ColorFade(Self.Fill, -20%)
                  OnSelect: |-
                    =Set(varShowLoading, true);
                    Set(varLoadingMessage, "Creating order...");
                    IfError(
                      Set(
                        varRet,
                        'app-flow-pedido-acao'.Run(
                          "criar",
                          "",
                          Text('xx-cbo-form-item'.Selected.<col-id>, "[$-en-US]0"),
                          'xx-cbo-form-tipo'.Selected.Value,
                          Trim('xx-txt-form-descricao'.Text),
                          Lower(User().Email)
                        )
                      ),
                      Trace("Flow transport failure: " & FirstError.Message);
                      Set(varRet, Blank())
                    );
                    Set(varShowLoading, false);
                    Set(varToastType, Coalesce(varRet.status, "error"));
                    Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
                    Set(varShowToast, true);
                    If(
                      varToastType <> "error",
                      Set(varMostrarForm, false);
                      Refresh('<fonte>');
                      Set(
                        varPedidoTotal,
                        CountRows(Filter('<fonte>', StartsWith(<col-unidade>, varUnidadeFiltro)))
                      )
                    )
                  PressedBorderColor: =ColorFade(Self.Fill, -30%)
                  PressedColor: =fxColorTextOnPrimary
                  PressedFill: =ColorFade(Self.Fill, -30%)
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxBtnFontSize
                  TabIndex: =0
                  Text: =If(varShowLoading, fxTxtProcessando, fxTxtSalvar)
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =Parent.Width - Self.Width - fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
```

### Button that opens the modal

`Reset()` of each control **before** opening, so it does not inherit the previous value.

```yaml
- xx-btn-novo:
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
      Height: =fxBtnHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: |-
        =Reset('xx-cbo-form-tipo');
        Reset('xx-cbo-form-item');
        Reset('xx-txt-form-descricao');
        Set(varMostrarForm, true)
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="New order"
      Visible: =varPerfil.Flg_Cria
      Width: =fxBtnWidth
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + fxLayoutGutter
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `xx-mod-form`, `varMostrarForm` | `xx-mod-<action>` and `varMostrar<Action>` |  |
| `'<fonte-item>'`, `<col-codigo>`, `<col-unidade>` | the real table and columns | delegable combo Items (`Filter` with `StartsWith`) |
| `["Standard", "Urgent", "Other"]` | the real type domain |  |
| `Trim(...)`, `Lower(User().Email)` | the flow's real parameters | the flow validates again: the screen only helps |
| `'app-flow-pedido-acao'` | the flow's name in the app | positional parameters, all text; a new parameter always goes at the end |
| `"encerrar"`, `<col-id>` | the real action and id | a numeric id goes as `Text(id, "[$-en-US]0")` |
| `'<fonte>'`, `<col-unidade>` | the real table and column | the `Refresh` and the recount close the write cycle |

## Behavior

Destination of the formulas below: the same as the YAML (`,` between arguments, `;` chains).

**`xx-mod-form-lbl-validacao`.Text**: returns the **first** pending item; empty when the form is ready

```powerfx
If(
  IsBlank('xx-cbo-form-tipo'.Selected),
  "Select the type.",
  IsBlank('xx-cbo-form-item'.Selected),
  "Select the item.",
  Len(Trim('xx-txt-form-descricao'.Text)) < 10,
  "Describe it with at least 10 characters.",
  ""
)
```

**`xx-mod-form-btn-confirmar`.DisplayMode**: disabled while there is a pending item or processing

```powerfx
If(
  varShowLoading || !IsBlank('xx-mod-form-lbl-validacao'.Text),
  DisplayMode.Disabled,
  DisplayMode.Edit
)
```

**`xx-mod-form-btn-confirmar`.OnSelect**: calls the flow; closes only if there was no error

```powerfx
Set(varShowLoading, true);
Set(varLoadingMessage, "Creating order...");
IfError(
  Set(
    varRet,
    'app-flow-pedido-acao'.Run(
      "criar",
      "",
      Text('xx-cbo-form-item'.Selected.<col-id>, "[$-en-US]0"),
      'xx-cbo-form-tipo'.Selected.Value,
      Trim('xx-txt-form-descricao'.Text),
      Lower(User().Email)
    )
  ),
  Trace("Flow transport failure: " & FirstError.Message);
  Set(varRet, Blank())
);
Set(varShowLoading, false);
Set(varToastType, Coalesce(varRet.status, "error"));
Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
Set(varShowToast, true);
If(
  varToastType <> "error",
  Set(varMostrarForm, false);
  Refresh('<fonte>');
  Set(
    varPedidoTotal,
    CountRows(Filter('<fonte>', StartsWith(<col-unidade>, varUnidadeFiltro)))
  )
)
```

## Accessibility

- Official limitation: dialog and overlay are not supported by the screen reader (Microsoft recommends a separate screen or `Notify()`). The pattern's mitigation is the `Back` button, always present and in the tab order.
- The confirm button changes its text and is disabled during processing (`varShowLoading`).
- Visible label above each field; required is stated in the text ("Type" in the validation), not only by `*`.
- The pending item appears as text, in `fxColorError`, next to the disabled button.

## Pitfalls

- Validation duplicated in the client and in the flow diverges over time: the client only avoids the round trip, the flow decides.
- `Mode: =TextMode.MultiLine` is a documented property of `Classic/TextInput`; do not invent `Mode` on other types.
- Without `Reset` on open, the form reopens with what the user typed before and gave up on.
- A combo with `Items` over a large source needs `IsSearchable: =true` and a delegable predicate.

## Variations

- Edit form: fill it from the record's `Default`/`DefaultSelectedItems` in `varPedidoSel`.
- Per-field error (under the field, after the first attempt): pattern in `ux-components.md` §14.

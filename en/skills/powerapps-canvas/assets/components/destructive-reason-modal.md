# Destructive modal with required reason

Maturity: **stable** · Frequency: **occasional**.

## Purpose

Modal for an irreversible action: title and button in `fxColorError`, a required reason field and a button disabled until the reason reaches the minimum length. The reason goes to the flow for auditing.

## When to use / when not to use

**Use when**

- canceling, deleting or reversing something that does not come back;
- the rule requires a recorded justification.

**Do not use when**

- the action is reversible (use `confirm-modal.md`);
- no rule requires a justification.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-mod-cancelar  (GroupContainer)
  xx-mod-cancelar-bloqueio  (Button)
  xx-mod-cancelar-card  (GroupContainer)
    xx-mod-cancelar-titulo  (Label)
    xx-mod-cancelar-mensagem  (Label)
    xx-mod-cancelar-lbl-motivo  (Label)
    xx-txt-cancelar-motivo  (TextInput)
    xx-mod-cancelar-btn-voltar  (Button)
    xx-mod-cancelar-btn-confirmar  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorOverlayDark`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxColorError`, `fxFont`, `fxModalTitleSize`, `fxModalPadding`, `fxColorTextBody`, `fxFontSizeBody`, `fxColorTextSecondary`, `fxFontSizeHeader`, `fxColorBorderInteractive`, `fxColorPrimary`, `fxColorTextPrimary`, `fxFontSizeFilter`, `fxBtnRadius`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxTxtVoltar`, `fxBtnFontSize`, `fxBtnHeight`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtProcessando`, `fxMsgFalhaFlow`.
- **Tokens of the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxModalWidthM`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varMostrarCancelar`, `varPedidoSel`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType`, `varToastMessage`, `varShowToast`, `varPedidoTotal`, `varUnidadeFiltro`.
- **Collections**: none.
- **Flows**: `app-flow-pedido-acao`.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-mod-cancelar:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlayDark
      Height: =Parent.Height
      Visible: =varMostrarCancelar
      Width: =Parent.Width
    Children:
      - xx-mod-cancelar-bloqueio:
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
      - xx-mod-cancelar-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =340
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxModalWidthM
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-mod-cancelar-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorError
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =32
                  Size: =fxModalTitleSize
                  Text: ="Cancel the order"
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =fxModalPadding
            - xx-mod-cancelar-mensagem:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextBody
                  Font: =fxFont
                  Height: =48
                  Size: =fxFontSizeBody
                  Text: ="Order " & varPedidoSel.<col-codigo> & " will be canceled and cannot be reopened."
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =56
            - xx-mod-cancelar-lbl-motivo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =20
                  Size: =fxFontSizeHeader
                  Text: ="Reason (required)"
                  Width: =300
                  X: =fxModalPadding
                  Y: =110
            - xx-txt-cancelar-motivo:
                Control: Classic/TextInput@2.3.2
                Properties:
                  BorderColor: =If(IsBlank(Self.Text), fxColorBorderInteractive, fxColorPrimary)
                  Color: =fxColorTextPrimary
                  Default: =""
                  FocusedBorderColor: =fxColorPrimary
                  Font: =fxFont
                  Height: =80
                  HintText: ="Describe the reason (minimum 5 characters)"
                  MaxLength: =500
                  Mode: =TextMode.MultiLine
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxFontSizeFilter
                  TabIndex: =0
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =134
            - xx-mod-cancelar-btn-voltar:
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
                  OnSelect: |-
                    =Set(varMostrarCancelar, false);
                    Set(varPedidoSel, Blank())
                  PressedBorderColor: =fxColorButtonCancelHover
                  PressedColor: =fxColorTextOnPrimary
                  PressedFill: =fxColorButtonCancelHover
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxBtnFontSize
                  TabIndex: =0
                  Text: =fxTxtVoltar
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
            - xx-mod-cancelar-btn-confirmar:
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
                      varShowLoading || Len(Trim('xx-txt-cancelar-motivo'.Text)) < 5,
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
                  OnSelect: |-
                    =Set(varShowLoading, true);
                    Set(varLoadingMessage, "Canceling order...");
                    IfError(
                      Set(
                        varRet,
                        'app-flow-pedido-acao'.Run(
                          "cancelar",
                          Text(varPedidoSel.<col-id>, "[$-en-US]0"),
                          Trim('xx-txt-cancelar-motivo'.Text)
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
                      Set(varMostrarCancelar, false);
                      Set(varPedidoSel, Blank());
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
                  Text: =If(varShowLoading, fxTxtProcessando, "Confirm cancellation")
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =Parent.Width - Self.Width - fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `xx-mod-cancelar`, `varMostrarCancelar` | `xx-mod-<action>` and `varMostrar<Action>` |  |
| `5` | the minimum reason length | the same value in the flow |
| `"Confirm cancellation"` | the explicit verb of the destructive action | never `Yes` or `Cancel` to execute ("Cancel" means leaving) |
| `'app-flow-pedido-acao'` | the flow's name in the app | positional parameters, all text; a new parameter always goes at the end |
| `"encerrar"`, `<col-id>` | the real action and id | a numeric id goes as `Text(id, "[$-en-US]0")` |
| `'<fonte>'`, `<col-unidade>` | the real table and column | the `Refresh` and the recount close the write cycle |

## Behavior

Destination of the formulas below: the same as the YAML (`,` between arguments, `;` chains).

**`xx-mod-cancelar-btn-confirmar`.DisplayMode**: enabled only with a reason of 5 or more characters and no processing in progress

```powerfx
If(
  varShowLoading || Len(Trim('xx-txt-cancelar-motivo'.Text)) < 5,
  DisplayMode.Disabled,
  DisplayMode.Edit
)
```

**`xx-mod-cancelar-btn-confirmar`.OnSelect**: sends the id and the reason to the flow; closes only on success

```powerfx
Set(varShowLoading, true);
Set(varLoadingMessage, "Canceling order...");
IfError(
  Set(
    varRet,
    'app-flow-pedido-acao'.Run(
      "cancelar",
      Text(varPedidoSel.<col-id>, "[$-en-US]0"),
      Trim('xx-txt-cancelar-motivo'.Text)
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
  Set(varMostrarCancelar, false);
  Set(varPedidoSel, Blank());
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
- The left button is `Back` (give up) and the right one is the action verb: "Cancel" never means both.

## Pitfalls

- Green confirming a destructive action was a real defect: destructive is always `fxColorError`.
- The reason is validated again in the flow; the client only avoids the round trip.
- Clear the reason on open: the button that opens the modal does `Reset('xx-txt-cancelar-motivo')`.
- No automatic focus on the field: there is no `SetFocus` in Classic; leave the field first in the tab order.

## Variations

- Bulk cancellation: the message text uses `CountRows(colSelecionados)` (see `bulk-selection.md`).
- No reason: use `confirm-modal.md` with `fxColorError` on the button.

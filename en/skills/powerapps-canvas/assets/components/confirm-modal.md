# Confirmation modal

Maturity: **stable** · Frequency: **occasional**.

## Purpose

Centered scrim and card that ask for confirmation of an action before calling the flow. `Back` on the left, the action verb on the right; success closes the modal, error keeps it open.

## When to use / when not to use

**Use when**

- an action with a server-side effect that the user may want to undo right away;
- an accidental click would have a cost.

**Do not use when**

- a destructive action with a required reason (use `destructive-reason-modal.md`);
- the action is trivial and reversible (use a toast with undo).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-mod-confirmar  (GroupContainer)
  xx-mod-confirmar-bloqueio  (Button)
  xx-mod-confirmar-card  (GroupContainer)
    xx-mod-confirmar-titulo  (Label)
    xx-mod-confirmar-mensagem  (Label)
    xx-mod-confirmar-btn-voltar  (Button)
    xx-mod-confirmar-btn-confirmar  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorOverlayDark`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxColorPrimaryDark`, `fxFont`, `fxModalTitleSize`, `fxModalPadding`, `fxColorTextBody`, `fxFontSizeBody`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxBtnRadius`, `fxTxtVoltar`, `fxBtnFontSize`, `fxBtnHeight`, `fxColorPrimary`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtProcessando`, `fxTxtEncerrar`, `fxMsgFalhaFlow`.
- **Tokens of the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxModalWidthS`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varMostrarConfirmar`, `varPedidoSel`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType`, `varToastMessage`, `varShowToast`, `varPedidoTotal`, `varUnidadeFiltro`.
- **Collections**: none.
- **Flows**: `app-flow-pedido-acao`.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-mod-confirmar:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlayDark
      Height: =Parent.Height
      Visible: =varMostrarConfirmar
      Width: =Parent.Width
    Children:
      - xx-mod-confirmar-bloqueio:
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
      - xx-mod-confirmar-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =240
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxModalWidthS
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-mod-confirmar-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorPrimaryDark
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =32
                  Size: =fxModalTitleSize
                  Text: ="Complete the order"
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =fxModalPadding
            - xx-mod-confirmar-mensagem:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextBody
                  Font: =fxFont
                  Height: =80
                  Size: =fxFontSizeBody
                  Text: ="Confirm completing order " & varPedidoSel.<col-codigo> & "?"
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =70
            - xx-mod-confirmar-btn-voltar:
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
                    =Set(varMostrarConfirmar, false);
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
            - xx-mod-confirmar-btn-confirmar:
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
                    Set(varLoadingMessage, "Completing...");
                    IfError(
                      Set(
                        varRet,
                        'app-flow-pedido-acao'.Run(
                          "encerrar",
                          Text(varPedidoSel.<col-id>, "[$-en-US]0")
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
                      Set(varMostrarConfirmar, false);
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
                  Text: =If(varShowLoading, fxTxtProcessando, fxTxtEncerrar)
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =Parent.Width - Self.Width - fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `xx-mod-confirmar` | `xx-mod-<action>` | one modal per action |
| `varMostrarConfirmar` | `varMostrar<Action>` | **one** variable per modal; `Visible` from a single variable |
| `"Complete the order"`, `fxTxtEncerrar` | title and verb | the action's verb; never a generic `Yes`/`Confirm` on an irreversible action |
| `'app-flow-pedido-acao'` | the flow's name in the app | positional parameters, all text; a new parameter always goes at the end |
| `"encerrar"`, `<col-id>` | the real action and id | a numeric id goes as `Text(id, "[$-en-US]0")` |
| `'<fonte>'`, `<col-unidade>` | the real table and column | the `Refresh` and the recount close the write cycle |

## Behavior

Destination of the formulas below: the same as the YAML (`,` between arguments, `;` chains).

**`xx-mod-confirmar-btn-confirmar`.OnSelect**: loading, call protected by `IfError`, toast; closes only if `status <> "error"`; then `Refresh` and recount

```powerfx
Set(varShowLoading, true);
Set(varLoadingMessage, "Completing...");
IfError(
  Set(
    varRet,
    'app-flow-pedido-acao'.Run(
      "encerrar",
      Text(varPedidoSel.<col-id>, "[$-en-US]0")
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
  Set(varMostrarConfirmar, false);
  Set(varPedidoSel, Blank());
  Refresh('<fonte>');
  Set(
    varPedidoTotal,
    CountRows(Filter('<fonte>', StartsWith(<col-unidade>, varUnidadeFiltro)))
  )
)
```

**`xx-mod-confirmar-btn-voltar`.OnSelect**: closes and **clears the state** (the next opening does not show stale data)

```powerfx
Set(varMostrarConfirmar, false);
Set(varPedidoSel, Blank())
```

## Accessibility

- Official limitation: dialog and overlay are not supported by the screen reader (Microsoft recommends a separate screen or `Notify()`). The pattern's mitigation is the `Back` button, always present and in the tab order.
- The confirm button changes its text and is disabled during processing (`varShowLoading`).

## Pitfalls

- `GroupContainer` is not clickable: the scrim does not block clicks on its own. The first child (`xx-mod-confirmar-bloqueio`) is a transparent full-screen button with `OnSelect: =false`.
- `Visible` with an `And` of several flags makes it impossible to find out why it does not open.
- Success is `status <> "error"` (`warning` also closes); a blank response is an error.
- Z-order: the modal goes before the loading and the toast in the screen's `Children`.
- No emoji on the buttons; no green on a destructive action.

## Variations

- Destructive with a reason: `destructive-reason-modal.md`.
- Form: `form-modal.md`.
- Information only: `info-modal.md`.

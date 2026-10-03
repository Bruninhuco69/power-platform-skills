# Operation feedback: modal, loading and toast

Continuation of [ux-components.md](ux-components.md). Same common rules (pasted-YAML dialect,
no PA2108, `fx*` tokens). State contract: `varMostrar<Acao>`, `varShowLoading`,
`varLoadingMessage`, `varShowToast`, `varToastType`, `varToastMessage`.

## Contents

1. [Modal](#9-modal)
2. [Loading](#10-loading)
3. [Toast](#11-toast)

## 9. Modal

Veil + card, centered by formula, button pair sized by formula. The full modal with a flow call
is in [screen-template.md](../assets/screen-template.md). Decisions:

- **Veil** `fxColorOverlayDark`; card with `fxModalRadius`, `fxModalPadding` and a bold title at
  `fxModalTitleSize` (`fxColorPrimaryDark`, or `fxColorError` if destructive).
- **Button pair**: left `fxTxtVoltar` gray; right = **the action's verb** (`Confirm closing`,
  `Save changes`), never a generic `Confirm`/`Yes` on a destructive action. No emoji.
- The modal **clears state** on close (message variable, selection): without that, the next
  open shows stale data. `Visible` from **one** variable (`varMostrar<Acao>`); an `And` of
  several flags makes it impossible to find out why it does not open.
- `GroupContainer` is not clickable: the veil **does not block clicks** on the controls below. To
  really block, a transparent 1920 by 1080 `Classic/Button` as the **first** child of the
  veil, with `OnSelect: =false`.
- **Official accessibility limitation**: dialog and overlay are not supported; Microsoft
  recommends a separate screen or `Notify()`. The kit's standard is the modal; the mitigation is an
  always-present `Back` button and focus in the tab order ([accessibility.md](accessibility.md)).
- Card size by token (`fxModalWidthS`, `fxModalWidthM`, `fxModalWidthL`; see the catalog in
  [INDEX.md](../assets/components/INDEX.md)); radius, colors, centering and the button pair are
  standardized too. In ManualLayout the content is positioned at absolute `X`/`Y`.

**Destructive** variation (cancellation with a required reason, `fxColorError` on the title and the button):

```yaml
- xx-mod-cancelar:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlayDark
      Height: =1080
      Visible: =varMostrarCancelar
      Width: =1920
    Children:
      - xx-mod-cancelar-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =300
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =520
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
            - xx-mod-cancelar-aviso:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorError
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =24
                  Size: =fxFontSizeFilter
                  Text: ="This action cannot be undone."
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =62
            - xx-txt-motivo:
                Control: Classic/TextInput@2.3.2
                Properties:
                  BorderColor: =fxColorBorderInteractive
                  Color: =fxColorTextPrimary
                  Default: =""
                  FocusedBorderColor: =fxColorPrimary
                  Font: =fxFont
                  Height: =100
                  HintText: ="Reason (minimum 5 characters)"
                  Mode: =TextMode.MultiLine
                  Size: =fxFontSizeFilter
                  TabIndex: =0
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =100
            - xx-mod-cancelar-btn-voltar:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =Self.Fill
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
                    =Set(varMostrarCancelar, false)
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
                      varShowLoading || Len(Trim('xx-txt-motivo'.Text)) < 5,
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
                    =Set(varMostrarCancelar, false)
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

Informational variation (single centered button):

```yaml
- xx-mod-info-btn-fechar:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =Self.Fill
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
        =Set(varMostrarInfo, false)
      PressedBorderColor: =fxColorButtonCancelHover
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =fxColorButtonCancelHover
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtFechar
      Width: =fxBtnWidth
      X: =(Parent.Width - Self.Width) / 2
      Y: =Parent.Height - Self.Height - fxModalPadding
```

## 10. Loading

Overlay with card and spinner; contract `varShowLoading` and `varLoadingMessage` (falls back to
`fxMsgLoadingDefault` when empty). Second to last in `Children`, before the toast. Native
gallery extras: `LoadingSpinnerColor` on the **screen** and, on the gallery, the loading ones (`[not
verified]`: `DelayItemLoading` and `LoadingSpinner` on `Gallery@2.15.0`; test in a small block).

```yaml
- xx-cmp-loading:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlay
      Height: =1080
      Visible: =varShowLoading
      Width: =1920
    Children:
      - xx-con-loading-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =fxLoadingCardHeight
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxLoadingCardWidth
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-spn-loading:
                Control: Spinner@1.4.6
                Properties:
                  Height: =fxLoadingSpinnerSize
                  Width: =fxLoadingSpinnerSize
                  X: =(Parent.Width - Self.Width) / 2
                  Y: =20
            - xx-lbl-loading-texto:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Size: =fxFontSizeBody
                  Text: =Coalesce(varLoadingMessage, fxMsgLoadingDefault)
                  Width: =Parent.Width - 20
                  X: =10
                  Y: =90
```

## 11. Toast

Flow return, the same for a single action and a batch. Three types (`success` green, `warning` amber,
`error` red), duration by severity (6, 12 and 15 s), progress bar and `✕` with a
`Tooltip`. The timer needs `Reset: =!varShowToast` (see [timers-async.md](timers-async.md) §4).
Last child of the screen. The progress bar depends on `Timer.Value` `[unverified]`.

Filling it in (single action and batch use the same contract):

- single: `Set(varToastType, Coalesce(varRet.status, "error"))` and the flow's description;
- batch: the **flow** aggregates and returns `warning` with the count; the screen only displays it.

```yaml
- xx-cmp-toast:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      DropShadow: =DropShadow.Bold
      Fill: =fxColorToastBg
      Height: =Max(80, 'xx-lbl-toast-mensagem'.Height + 50)
      RadiusBottomLeft: =fxModalRadius
      RadiusBottomRight: =fxModalRadius
      RadiusTopLeft: =fxModalRadius
      RadiusTopRight: =fxModalRadius
      Visible: =varShowToast
      Width: =fxToastWidth
      X: =Parent.Width - Self.Width - 20
      Y: =20
    Children:
      - xx-shp-toast-acento:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            DisabledBorderColor: =fxColorTransparent
            DisabledFill: |-
              =Switch(
                varToastType,
                "success", fxColorSuccess,
                "warning", fxColorWarning,
                fxColorError
              )
            DisplayMode: =DisplayMode.Disabled
            Fill: |-
              =Switch(
                varToastType,
                "success", fxColorSuccess,
                "warning", fxColorWarning,
                fxColorError
              )
            Height: =Parent.Height
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =0
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =0
            Text: =""
            Width: =5
            X: =0
            Y: =0
      - xx-shp-toast-icone-fundo:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            DisabledBorderColor: =fxColorTransparent
            DisabledFill: |-
              =Switch(
                varToastType,
                "success", ColorFade(fxColorSuccess, 80%),
                "warning", ColorFade(fxColorWarning, 80%),
                ColorFade(fxColorError, 80%)
              )
            DisplayMode: =DisplayMode.Disabled
            Fill: |-
              =Switch(
                varToastType,
                "success", ColorFade(fxColorSuccess, 80%),
                "warning", ColorFade(fxColorWarning, 80%),
                ColorFade(fxColorError, 80%)
              )
            Height: =40
            RadiusBottomLeft: =20
            RadiusBottomRight: =20
            RadiusTopLeft: =20
            RadiusTopRight: =20
            Text: =""
            Width: =40
            X: =18
            Y: =20
      - xx-lbl-toast-icone:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorTextOnPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =40
            Size: =18
            Text: =Switch(varToastType, "success", "✓", "warning", "!", "✕")
            VerticalAlign: =VerticalAlign.Middle
            Width: =40
            X: =18
            Y: =20
      - xx-lbl-toast-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextOnPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =28
            Size: =15
            Text: |-
              =Switch(
                varToastType,
                "success", fxTxtToastSuccess,
                "warning", fxTxtToastWarning,
                fxTxtToastError
              )
            VerticalAlign: =VerticalAlign.Bottom
            Width: =290
            X: =70
            Y: =10
      - xx-lbl-toast-mensagem:
          Control: Label@2.5.1
          Properties:
            AutoHeight: =true
            Color: =fxColorToastText
            Font: =fxFont
            Height: =28
            Size: =12
            Text: =varToastMessage
            VerticalAlign: =VerticalAlign.Top
            Width: =290
            X: =70
            Y: =38
      - xx-btn-toast-fechar:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            BorderThickness: =1
            Color: =fxColorToastText
            Fill: =fxColorTransparent
            Font: =fxFont
            FontWeight: =FontWeight.Normal
            Height: =30
            HoverBorderColor: =fxColorToastBg
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorToastBg
            OnSelect: |-
              =Set(varShowToast, false)
            PressedBorderColor: =fxColorToastBg
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorToastBg
            RadiusBottomLeft: =15
            RadiusBottomRight: =15
            RadiusTopLeft: =15
            RadiusTopRight: =15
            Size: =14
            TabIndex: =0
            Text: ="✕"
            Tooltip: ="Close notification"
            Width: =30
            X: =Parent.Width - Self.Width - 10
            Y: =8
      - xx-shp-toast-progresso-barra:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            DisabledBorderColor: =fxColorTransparent
            DisabledFill: |-
              =Switch(
                varToastType,
                "success", fxColorSuccess,
                "warning", fxColorWarning,
                fxColorError
              )
            DisplayMode: =DisplayMode.Disabled
            Fill: |-
              =Switch(
                varToastType,
                "success", fxColorSuccess,
                "warning", fxColorWarning,
                fxColorError
              )
            Height: =3
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =0
            RadiusTopLeft: =0
            RadiusTopRight: =0
            Text: =""
            Width: =Parent.Width * (1 - 'xx-tim-toast'.Value / Max('xx-tim-toast'.Duration, 1))
            X: =0
            Y: =Parent.Height - 3
      - xx-tim-toast:
          Control: Timer@2.1.0
          Properties:
            Duration: |-
              =If(
                varToastType = "error", fxToastDurationError,
                varToastType = "warning", fxToastDurationLong,
                Len(varToastMessage) > 100, fxToastDurationLong,
                fxToastDurationShort
              )
            OnTimerEnd: =Set(varShowToast, false)
            Repeat: =false
            Reset: =!varShowToast
            Start: =varShowToast
            Visible: =false
```


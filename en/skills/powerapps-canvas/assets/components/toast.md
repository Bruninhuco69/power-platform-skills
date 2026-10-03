# Flow return toast

Maturity: **stable** · Frequency: **very common**.

## Purpose

A non-blocking notification in the top right corner: type (`success`, `warning`, `error`) shown by accent color, icon and title, a ready-made message coming from the flow, manual close and a progress bar. It disappears on its own; the duration grows with severity.

## When to use / when not to use

**Use when**

- returning from any flow call (the message comes ready in `description`);
- confirming an action without interrupting the flow of work.

**Do not use when**

- field validation (show it on the field);
- an error that requires a decision from the user (use a modal).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-cmp-toast  (GroupContainer)
  xx-shp-toast-acento  (Button)
  xx-shp-toast-icone-fundo  (Button)
  xx-lbl-toast-icone  (Label)
  xx-lbl-toast-titulo  (Label)
  xx-lbl-toast-mensagem  (Label)
  xx-btn-toast-fechar  (Button)
  xx-shp-toast-progresso-fundo  (Button)
  xx-shp-toast-progresso-barra  (Button)
  xx-tim-toast  (Timer)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorToastBg`, `fxModalRadius`, `fxToastWidth`, `fxColorSuccess`, `fxColorWarning`, `fxColorError`, `fxColorTextOnPrimary`, `fxColorTextOnWarning`, `fxFont`, `fxFontSizeToastIcon`, `fxFontSizeToastTitle`, `fxTxtToastSuccess`, `fxTxtToastWarning`, `fxTxtToastError`, `fxColorToastText`, `fxFontSizeToast`, `fxFontSizeBody`, `fxToastDurationError`, `fxToastDurationLong`, `fxToastDurationShort`.
- **Tokens of the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxColorToastTrack`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varShowToast`, `varToastType`, `varToastMessage`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste it in Code view > Paste code, with the screen (or a container) as the parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

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
            Color: =If(varToastType = "warning", fxColorTextOnWarning, fxColorTextOnPrimary)
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =40
            Size: =fxFontSizeToastIcon
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
            Size: =fxFontSizeToastTitle
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
            Size: =fxFontSizeToast
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
            OnSelect: =Set(varShowToast, false)
            PressedBorderColor: =fxColorToastBg
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorToastBg
            RadiusBottomLeft: =15
            RadiusBottomRight: =15
            RadiusTopLeft: =15
            RadiusTopRight: =15
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="✕"
            Tooltip: ="Close notification"
            Width: =30
            X: =Parent.Width - Self.Width - 10
            Y: =8
      - xx-shp-toast-progresso-fundo:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            DisabledBorderColor: =fxColorTransparent
            DisabledFill: =fxColorToastTrack
            DisplayMode: =DisplayMode.Disabled
            Fill: =fxColorToastTrack
            Height: =3
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =0
            RadiusTopRight: =0
            Text: =""
            Width: =Parent.Width
            X: =0
            Y: =Parent.Height - 3
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

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `xx-cmp-toast` | `xx-cmp-toast` with the screen's prefix | it ships **already prefixed** |
| `varToastType` | `success`, `warning` or `error` | the `status` of the flow contract; any other value falls back to error |
| `fxTxtToast*`, `fxToastDuration*` | the project's texts and times | error lasts longer than success |

## Behavior

Destination of the formulas below: the same as the YAML (`,` between arguments, `;` chains).

**`xx-cmp-toast`.Visible**: a single global variable

```powerfx
varShowToast
```

**`xx-tim-toast`.Duration**: 6 s for a short success, 12 s for a warning or a long message, 15 s for an error

```powerfx
If(
  varToastType = "error", fxToastDurationError,
  varToastType = "warning", fxToastDurationLong,
  Len(varToastMessage) > 100, fxToastDurationLong,
  fxToastDurationShort
)
```

**`xx-tim-toast`.Start**: the timer starts and restarts on the `varShowToast` transition

```powerfx
varShowToast
```

## Accessibility

- No attested `Live` region (`Label@2.5.1` rejects `Live`, PA2108): a critical error must also go to a modal or to a message on the field.
- Close button with `Tooltip`; an error lasts 15 s to leave time to read it (WCAG: time limit).
- Light text `fxColorToastText` on `fxColorToastBg` with a 4.5:1 contrast.
- Icon: white glyph on the type's solid color; on the warning, a dark glyph (`fxColorTextOnWarning`), because white on yellow does not reach 4.5:1. Do not lighten the icon background with `ColorFade`: close to white, the white glyph vanishes.

## Pitfalls

- The toast is the **last** of the screen's `Children`, above the modal and the loading overlay.
- Every rounded shape is a disabled `Classic/Button`: `Rectangle` has no `Radius*`.
- `Reset: =!varShowToast` re-arms the timer on every display; without it the second toast does not count again.
- The flow's message is the ready-made sentence (`description`); the screen does not build business error text.

## Variations

- Text-only toast: remove the `*-icone-*` controls and the bar.
- Native `Notify()` is better for accessibility, but loses the look: reserve it for unhandled technical errors.

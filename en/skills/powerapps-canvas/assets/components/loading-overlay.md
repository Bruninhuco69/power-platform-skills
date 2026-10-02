# Loading overlay

Maturity: **stable** · Frequency: **very common**.

## Purpose

Translucent full-screen veil with a central card (spinner and message) while a flow call runs. It blocks clicks and disappears when `varShowLoading` goes back to `false`.

## When to use / when not to use

**Use when**

- every flow `.Run()` call;
- heavy screen-opening load that takes more than 1 second.

**Do not use when**

- the wait is milliseconds (the spinner flickers);
- the loading belongs to a single control (use the button state).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-cmp-loading  (GroupContainer)
  xx-cmp-loading-bloqueio  (Button)
  xx-con-loading-card  (GroupContainer)
    xx-spn-loading  (Spinner)
    xx-lbl-loading-texto  (Label)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorOverlay`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxLoadingCardWidth`, `fxLoadingCardHeight`, `fxLoadingSpinnerSize`, `fxColorPrimary`, `fxFont`, `fxFontSizeBody`, `fxMsgLoadingDefault`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varShowLoading`, `varLoadingMessage`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-cmp-loading:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlay
      Height: =Parent.Height
      Visible: =varShowLoading
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-cmp-loading-bloqueio:
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
                  Height: =30
                  Size: =fxFontSizeBody
                  Text: =Coalesce(varLoadingMessage, fxMsgLoadingDefault)
                  Width: =Parent.Width - 20
                  X: =10
                  Y: =90
```

## Parameters to change

| In the block | Change to | Note |
|---|---|---|
| `xx-cmp-loading` | `xx-cmp-loading` with the screen prefix | shared block comes out **already prefixed**; without a prefix Studio renames it to `_1` |
| `varLoadingMessage` | the operation message | falls back to `fxMsgLoadingDefault` when empty |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-cmp-loading`.Visible**: a single global variable

```powerfx
varShowLoading
```

**`xx-lbl-loading-texto`.Text**: operation message, with a default

```powerfx
Coalesce(varLoadingMessage, fxMsgLoadingDefault)
```

## Accessibility

- The veil blocks the click (first transparent child with `OnSelect: =false`), preventing double submit.
- Message as text: "Processing, please wait..." is what a screen reader finds when navigating; there is no attested `Live` on the `Label` (PA2108).

## Pitfalls

- Second to last in the screen `Children`, right before the toast; modal below it.
- A `varShowLoading` not reset by an error in the middle of the chain leaves the overlay stuck: every `.Run()` is inside `IfError` and `Set(varShowLoading, false)` comes **after** it.
- Initial state: `varShowLoading` is created `false` in `OnStart`.
- The action button also binds to `varShowLoading` (text and `DisplayMode`).

## Variations

- Lighter veil for short operations: replace `fxColorOverlay` with a white veil token.
- Message per step: `Set(varLoadingMessage, ...)` between the calls.

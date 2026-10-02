# Screen header

Maturity: **stable** · Frequency: **very common** (every content screen; a screen with only shortcuts can do without it).

## Purpose

Fixed strip at the top of every screen: title, signed-in user and divider. It gives the user the "where am I" and anchors the vertical grid: everything else starts at `fxHeaderHeight`.

## When to use / when not to use

**Use when**

- every content screen, without exception;
- the app has more than one screen and the user needs to know which one they are on.

**Do not use when**

- the screen is an overlay or modal (use the modal card);
- the title already appears in the side menu and the screen is just an embedded panel.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-con-header  (GroupContainer)
  xx-lbl-header-titulo  (Label)
  xx-lbl-header-usuario  (Label)
  xx-rec-header-divisor  (Rectangle)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorSurface`, `fxColorPrimary`, `fxFont`, `fxFontSizeTitle`, `fxLayoutMargin`, `fxColorTextSecondary`, `fxFontSizeBody`, `fxColorDivider`, `fxFontSizeTableSmall`, `fxLayoutGutter`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxHeaderHeight`.
- **Global variables** (born in `OnStart`, `assets/app-onstart-template.md`): `varAgora`, `varTelaAtiva`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as the parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-con-header:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorSurface
      Height: =fxHeaderHeight
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-lbl-header-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =60
            Size: =fxFontSizeTitle
            Text: ="Screen title"
            VerticalAlign: =VerticalAlign.Middle
            Width: =700
            X: =fxLayoutMargin
            Y: =20
      - xx-lbl-header-usuario:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Right
            Color: =fxColorTextSecondary
            Font: =fxFont
            Height: =24
            Size: =fxFontSizeBody
            Text: =User().FullName
            Width: =320
            X: =Parent.Width - fxLayoutMargin - Self.Width
            Y: =30
      - xx-rec-header-divisor:
          Control: Rectangle@2.3.0
          Properties:
            BorderStyle: =BorderStyle.None
            Fill: =fxColorDivider
            Height: =1
            Width: =Parent.Width
            X: =0
            Y: =fxHeaderHeight - 1
```

### Variation: clock (date and time)

`Now()` directly in the `Text` property is volatile and re-evaluates on every recalculation; the clock reads `varAgora`, updated by a timer every 30 s (minute precision is enough in the `hh:mm` format).

```yaml
- xx-lbl-header-datahora:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Right
      Color: =fxColorTextSecondary
      Font: =fxFont
      Height: =20
      Size: =fxFontSizeTableSmall
      Text: =Text(varAgora, "[$-en-US]mm/dd/yyyy hh:mm")
      Width: =220
      X: =Parent.Width - fxLayoutMargin - Self.Width
      Y: =56
- xx-tim-header-relogio:
    Control: Timer@2.1.0
    Properties:
      Duration: =30000
      OnTimerEnd: =Set(varAgora, Now())
      Repeat: =true
      Start: =varTelaAtiva = "pedidos"
      Visible: =false
```

### Variation: with logo

Replace `xx-lbl-header-titulo` with this pair. The image comes from the app media resource (Media > Add); the alternative text is the title next to it.

```yaml
- xx-img-header-logo:
    Control: Image@2.2.3
    Properties:
      DisplayMode: =DisplayMode.View
      Height: =60
      Image: ='<imagem-logo>'
      Width: =160
      X: =fxLayoutMargin
      Y: =20
- xx-lbl-header-titulo-logo:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =60
      Size: =fxFontSizeTitle
      Text: ="Screen title"
      VerticalAlign: =VerticalAlign.Middle
      Width: =700
      X: =fxLayoutMargin + 160 + fxLayoutGutter
      Y: =20
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `xx-` | the screen's 2-letter prefix | a control name is unique across the whole app |
| `"Screen title"` | screen name | the same text as `varTelaAtiva`/menu, so they do not diverge |
| `User().FullName` | profile field if there is a display name of its own | e.g. `varUsuario.Nom_Usuario` |
| `varTelaAtiva = "pedidos"` (clock) | the screen identifier | the timer runs only while the screen is active |
| `'<imagem-logo>'` | media resource name | logo variation |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-lbl-header-titulo`.Text**: fixed title, no formula

```powerfx
"Screen title"
```

**`xx-lbl-header-usuario`.Text**: Entra user name

```powerfx
User().FullName
```

## Accessibility

- The title is the first text read by the screen reader in tab order: keep the title as the first child.
- Title color (`fxColorPrimary` on `fxColorSurface`) and user color (`fxColorTextSecondary`) exceed 4.5:1; if you change the brand, recheck.
- Decorative logo image: with no alternative text of its own, the title next to it does the job.

## Pitfalls

- Title position (left or centered): choose **one** per app.
- `Now()` directly in the clock `Text`: keeps the property volatile and weighs on the screen recalculation.
- The clock only runs in Preview (`F5`): in the editing canvas the timer does not run.
- With a side menu, use `X: =fxContentX` and `Width: =fxContentWidth` on the container instead of `0` and `Parent.Width`.

## Variations

- With a subtitle: a `Label` of `fxFontSizeBody` below the title, `Y: =68`.
- With a unit selector in the strip: see `unit-selector.md`.
- Without a user (public screen): remove `xx-lbl-header-usuario`.

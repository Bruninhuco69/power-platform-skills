# Tabs (button and stroke)

Maturity: **stable** · Frequency: **common**.

## Purpose

Switches between data sets on the same screen (for example open, completed, all) through a numeric variable; the active tab has a fill, bold text and a 3 px stroke.

## When to use / when not to use

**Use when**

- up to 4 sets of the same entity on the same screen;
- the counter of each set helps the choice.

**Do not use when**

- the sets are different screens (use the menu);
- the app must meet strict tab accessibility: the accessible pattern is the modern Tab list control, and a button-and-rectangle tab is not one.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-con-abas  (GroupContainer)
  xx-btn-tab-abertos  (Button)
  xx-shp-tab-abertos-traco  (Rectangle)
  xx-btn-tab-encerrados  (Button)
  xx-shp-tab-encerrados-traco  (Rectangle)
  xx-btn-tab-todos  (Button)
  xx-shp-tab-todos-traco  (Rectangle)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxLayoutMargin`, `fxLayoutGutter`, `fxColorPrimary`, `fxColorTextSecondary`, `fxColorSurface`, `fxColorTabInactive`, `fxFont`, `fxFontSizeFilter`, `fxBtnRadius`, `fxColorTextPrimary`, `fxFontSizeBody`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxHeaderHeight`.
- **Global variables** (born in `OnStart`, `assets/app-onstart-template.md`): `varXXTab`, `varPedidoAbertos`, `varPedidoEncerrados`, `varPedidoTotal`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-con-abas:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorTransparent
      Height: =49
      Width: =760
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + fxLayoutGutter
    Children:
      - xx-btn-tab-abertos:
          Control: Classic/Button@2.2.0
          Properties:
            AutoDisableOnSelect: =false
            BorderThickness: =0
            Color: =If(varXXTab = 1, fxColorPrimary, fxColorTextSecondary)
            Fill: =If(varXXTab = 1, fxColorSurface, fxColorTabInactive)
            Font: =fxFont
            FontWeight: =If(varXXTab = 1, FontWeight.Bold, FontWeight.Semibold)
            Height: =46
            HoverColor: =fxColorPrimary
            HoverFill: =fxColorSurface
            OnSelect: =Set(varXXTab, 1)
            PressedColor: =fxColorPrimary
            PressedFill: =fxColorSurface
            RadiusBottomLeft: =0
            RadiusBottomRight: =0
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxFontSizeFilter
            TabIndex: =0
            Text: ="Open (" & varPedidoAbertos & ")"
            Width: =240
            X: =0
            Y: =0
      - xx-shp-tab-abertos-traco:
          Control: Rectangle@2.3.0
          Properties:
            BorderStyle: =BorderStyle.None
            Fill: =If(varXXTab = 1, fxColorPrimary, fxColorTransparent)
            Height: =3
            Width: =240
            X: =0
            Y: =46
      - xx-btn-tab-encerrados:
          Control: Classic/Button@2.2.0
          Properties:
            AutoDisableOnSelect: =false
            BorderThickness: =0
            Color: =If(varXXTab = 2, fxColorPrimary, fxColorTextSecondary)
            Fill: =If(varXXTab = 2, fxColorSurface, fxColorTabInactive)
            Font: =fxFont
            FontWeight: =If(varXXTab = 2, FontWeight.Bold, FontWeight.Semibold)
            Height: =46
            HoverColor: =fxColorPrimary
            HoverFill: =fxColorSurface
            OnSelect: =Set(varXXTab, 2)
            PressedColor: =fxColorPrimary
            PressedFill: =fxColorSurface
            RadiusBottomLeft: =0
            RadiusBottomRight: =0
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxFontSizeFilter
            TabIndex: =0
            Text: ="Completed (" & varPedidoEncerrados & ")"
            Width: =240
            X: =248
            Y: =0
      - xx-shp-tab-encerrados-traco:
          Control: Rectangle@2.3.0
          Properties:
            BorderStyle: =BorderStyle.None
            Fill: =If(varXXTab = 2, fxColorPrimary, fxColorTransparent)
            Height: =3
            Width: =240
            X: =248
            Y: =46
      - xx-btn-tab-todos:
          Control: Classic/Button@2.2.0
          Properties:
            AutoDisableOnSelect: =false
            BorderThickness: =0
            Color: =If(varXXTab = 3, fxColorPrimary, fxColorTextSecondary)
            Fill: =If(varXXTab = 3, fxColorSurface, fxColorTabInactive)
            Font: =fxFont
            FontWeight: =If(varXXTab = 3, FontWeight.Bold, FontWeight.Semibold)
            Height: =46
            HoverColor: =fxColorPrimary
            HoverFill: =fxColorSurface
            OnSelect: =Set(varXXTab, 3)
            PressedColor: =fxColorPrimary
            PressedFill: =fxColorSurface
            RadiusBottomLeft: =0
            RadiusBottomRight: =0
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxFontSizeFilter
            TabIndex: =0
            Text: ="All (" & varPedidoTotal & ")"
            Width: =240
            X: =496
            Y: =0
      - xx-shp-tab-todos-traco:
          Control: Rectangle@2.3.0
          Properties:
            BorderStyle: =BorderStyle.None
            Fill: =If(varXXTab = 3, fxColorPrimary, fxColorTransparent)
            Height: =3
            Width: =240
            X: =496
            Y: =46
```

### Conditional content

Each tab has its own container whose `Visible` compares the variable; only one is visible at a time.

```yaml
- xx-con-aba-abertos:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorTransparent
      Height: =600
      Visible: =varXXTab = 1
      Width: =Parent.Width - fxLayoutMargin * 2
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + fxLayoutGutter + 49 + fxLayoutGutter
    Children:
      - xx-lbl-aba-abertos-conteudo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextPrimary
            Font: =fxFont
            Height: =28
            Size: =fxFontSizeBody
            Text: ="Content of the Open tab"
            Width: =400
            X: =0
            Y: =0
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `varXXTab` | the screen's `var<Prefix>Tab` | born as 1 in `OnStart` and rewritten in `OnVisible` |
| `Open`, `Completed`, `All` | name of the sets | the text includes the count in parentheses |
| `varPedido*` | count variables | same as the KPI card |
| `240` and `X` 0, 248, 496 | width and step | step = width + 8 |

## Behavior

Destination of the formulas below: the same as the YAML (`,` between arguments, `;` chains).

**`xx-btn-tab-abertos`.OnSelect**: switches the active tab

```powerfx
Set(varXXTab, 1)
```

**`xx-btn-tab-abertos`.Fill**: active = surface; inactive = `fxColorTabInactive` (they must be different)

```powerfx
If(varXXTab = 1, fxColorSurface, fxColorTabInactive)
```

## Accessibility

- Official limitation: a button tab does not announce "selected"; the stroke and bold text give the visual cue, but the screen reader only reads the text. Record the limitation (see `accessibility.md`).
- Active and inactive never with the same `Fill`.

## Pitfalls

- `AutoDisableOnSelect: =false` prevents the button from disabling on click; keep it.
- Forgetting to reset the gallery selection when switching tabs leaves the selected row from another tab.
- A tab count over SQL does not delegate: show the ceiling as in the KPI card.

## Variations

- Variable-width tabs: `Width: =Len(Self.Text) * 9 + 40`.
- Tab with an icon: do not use an emoji as semantics; the icon is a separate control.

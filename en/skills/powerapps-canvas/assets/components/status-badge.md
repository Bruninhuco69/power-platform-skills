# Status badge (pill)

Maturity: **stable** · Frequency: **common** (status pill in a gallery row; also as an action badge-button).

## Purpose

Visual mark of a row's state: a rounded pill in a pastel color with dark text of the same hue, always accompanied by the state text (never color alone).

## When to use / when not to use

**Use when**

- status column of a gallery or detail;
- the state has a closed, short vocabulary.

**Do not use when**

- the state is long or open-ended (a sentence): use plain text;
- the label is a user action: use the badge-button (variation).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-shp-gal-status-pill  (Button)
xx-lbl-gal-status  (Label)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxBadgeInfoBg`, `fxBadgeProgressBg`, `fxBadgeSuccessBg`, `fxBadgeNeutralBg`, `fxModalPadding`, `fxBadgeInfoText`, `fxBadgeProgressText`, `fxBadgeSuccessText`, `fxBadgeNeutralText`, `fxFont`, `fxFontSizeTableSmall`, `fxBadgeWarningText`, `fxBadgeDangerText`, `fxColorBorder`, `fxBadgeWarningBg`, `fxBadgeDangerBg`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxPillHeight`.
- **Global variables** (born in `OnStart`, `assets/app-onstart-template.md`): none.
- **Collections**: none.
- **Flows**: none.
- Both blocks go in a gallery's template (they use `ThisItem`).

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

These two controls go **inside the gallery template** (`Children` of `xx-gal-pedidos`).

```yaml
- xx-shp-gal-status-pill:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorTransparent
      DisabledBorderColor: =fxColorTransparent
      DisabledFill: |-
        =Switch(
          ThisItem.<col-status>,
          "Open", fxBadgeInfoBg,
          "In progress", fxBadgeProgressBg,
          "Completed", fxBadgeSuccessBg,
          fxBadgeNeutralBg
        )
      DisplayMode: =DisplayMode.Disabled
      Fill: |-
        =Switch(
          ThisItem.<col-status>,
          "Open", fxBadgeInfoBg,
          "In progress", fxBadgeProgressBg,
          "Completed", fxBadgeSuccessBg,
          fxBadgeNeutralBg
        )
      Height: =fxPillHeight
      RadiusBottomLeft: =Self.Height / 2
      RadiusBottomRight: =Self.Height / 2
      RadiusTopLeft: =Self.Height / 2
      RadiusTopRight: =Self.Height / 2
      Text: =""
      Width: =134
      X: =Parent.TemplateWidth - fxModalPadding - 134
      Y: =(Parent.TemplateHeight - Self.Height) / 2
- xx-lbl-gal-status:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: |-
        =Switch(
          ThisItem.<col-status>,
          "Open", fxBadgeInfoText,
          "In progress", fxBadgeProgressText,
          "Completed", fxBadgeSuccessText,
          fxBadgeNeutralText
        )
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxPillHeight
      Size: =fxFontSizeTableSmall
      Text: =ThisItem.<col-status>
      VerticalAlign: =VerticalAlign.Middle
      Width: =134
      X: ='xx-shp-gal-status-pill'.X
      Y: ='xx-shp-gal-status-pill'.Y
```

### Variation: action badge (button)

An in-row action button with a color derived from its own label (`Self.Text`); hover darkens on all of them.

```yaml
- xx-btn-gal-acao:
    Control: Classic/Button@2.2.0
    Properties:
      BorderStyle: =BorderStyle.None
      Color: |-
        =Switch(
          Self.Text,
          "Approve", fxBadgeSuccessText,
          "Review", fxBadgeWarningText,
          "Cancel", fxBadgeDangerText,
          fxBadgeNeutralText
        )
      DisabledBorderColor: =fxColorBorder
      DisplayMode: =If(ThisItem.Bloqueado, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: |-
        =Switch(
          Self.Text,
          "Approve", fxBadgeSuccessBg,
          "Review", fxBadgeWarningBg,
          "Cancel", fxBadgeDangerBg,
          fxBadgeNeutralBg
        )
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =35
      HoverFill: =ColorFade(Self.Fill, -12%)
      PressedFill: =ColorFade(Self.Fill, -24%)
      Size: =fxFontSizeTableSmall
      TabIndex: =0
      Text: ="Approve"
      Underline: =true
      Width: =88
      X: =1000
      Y: =8
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `<col-status>` | the real state column |  |
| `"Open"`, `"In progress"`, `"Completed"` | the real vocabulary | one `fxBadge*` pair per state; the last branch is the neutral one |
| `Parent.TemplateWidth - fxModalPadding - 134` | column position | align with the header |
| `Approve`, `Review`, `Cancel` | real actions | button variation |

## Behavior

Destination of the formulas below: the same as the YAML (`,` between arguments, `;` chains).

**`xx-shp-gal-status-pill`.DisabledFill**: pill background color by state (the shape is a disabled button)

```powerfx
Switch(
  ThisItem.<col-status>,
  "Open", fxBadgeInfoBg,
  "In progress", fxBadgeProgressBg,
  "Completed", fxBadgeSuccessBg,
  fxBadgeNeutralBg
)
```

**`xx-lbl-gal-status`.Color**: text color by state

```powerfx
Switch(
  ThisItem.<col-status>,
  "Open", fxBadgeInfoText,
  "In progress", fxBadgeProgressText,
  "Completed", fxBadgeSuccessText,
  fxBadgeNeutralText
)
```

## Accessibility

- Each `fxBadge*Text` over `fxBadge*Bg` pair has a 4.5:1 contrast.
- The state text is always present: color is reinforcement.
- The disabled shape is not in the tab order.

## Pitfalls

- `Rectangle` has no `Radius*`: the pill is a disabled `Classic/Button` with `DisabledFill`.
- `Self.Height / 2` in the radius keeps the pill round if the height changes.
- A new vocabulary value from the database falls into the neutral branch: if everything shows up as "Completed", the final branch is swapped.
- Hover must **darken** on all buttons; lightening on one and darkening on another is inconsistent.

## Variations

- Text-only badge (a `Label` with `Fill` and `Color` per `Switch`): as in `table-gallery.md`.
- Count badge in the menu: `Label` with a radius via a disabled button.

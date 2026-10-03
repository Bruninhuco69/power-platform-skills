# Top menu

Maturity: **new** · Frequency: **to be measured**.

## Purpose

Main navigation in a horizontal bar at the top of the screen: system name on the left, one button per first-level screen in the middle (visibility by profile flag) and the user with profile on the right. The active item is highlighted by background and bold. The screen keeps its full width for content. This pattern is chosen in `/pp-en:design` (`ux-design-system.md` §2.1).

## When to use / when not to use

**Use when**

- the app has 2 to 6 first-level screens, with short labels;
- the screens have a wide table and every pixel of width counts;
- the navigation must respect the profile's permission.

**Do not use when**

- there are more than 6 first-level screens or long labels (use `side-menu.md`);
- the app is used on a narrow screen (tablet in portrait): the bar does not fit; use the drawer from `side-menu.md`;
- the permission is a business rule: button visibility is only UX, the flow is what blocks.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-cmp-topo-con  (GroupContainer)
  xx-cmp-topo-lbl-titulo  (Label)
  xx-cmp-topo-btn-pedidos  (Button)
  xx-cmp-topo-btn-relatorios  (Button)
  xx-cmp-topo-btn-usuarios  (Button)
  xx-cmp-topo-lbl-usuario  (Label)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorTextOnPrimary`, `fxColorPrimaryLight`, `fxFont`, `fxFontSizeBody`, `fxFontSizeFilter`.
- **Tokens of the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxColorMenuBg`, `fxColorMenuItemActive`, `fxTopNavHeight`, `fxTopNavItemWidth`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varSemAcesso`, `varTelaAtiva`, `varPerfil`, `varUsuario`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen as parent, **before** the screen header; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-cmp-topo-con:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorMenuBg
      Height: =fxTopNavHeight
      Visible: =!varSemAcesso
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-cmp-topo-lbl-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextOnPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =fxTopNavHeight
            Size: =fxFontSizeBody
            Text: ="System name"
            VerticalAlign: =VerticalAlign.Middle
            Width: =220
            Wrap: =false
            X: =24
            Y: =0
      - xx-cmp-topo-btn-pedidos:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "pedidos", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "pedidos", FontWeight.Bold, FontWeight.Normal)
            Height: =fxTopNavHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varTelaAtiva, "pedidos");
              Navigate(Pedidos, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            RadiusBottomLeft: =0
            RadiusBottomRight: =0
            RadiusTopLeft: =0
            RadiusTopRight: =0
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="Orders"
            Width: =fxTopNavItemWidth
            X: =260
            Y: =0
      - xx-cmp-topo-btn-relatorios:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "relatorios", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "relatorios", FontWeight.Bold, FontWeight.Normal)
            Height: =fxTopNavHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varTelaAtiva, "relatorios");
              Navigate(Relatorios, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            RadiusBottomLeft: =0
            RadiusBottomRight: =0
            RadiusTopLeft: =0
            RadiusTopRight: =0
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="Reports"
            Visible: =varPerfil.Flg_Relatorio
            Width: =fxTopNavItemWidth
            X: =260 + fxTopNavItemWidth
            Y: =0
      - xx-cmp-topo-btn-usuarios:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "usuarios", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "usuarios", FontWeight.Bold, FontWeight.Normal)
            Height: =fxTopNavHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varTelaAtiva, "usuarios");
              Navigate(Usuarios, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            RadiusBottomLeft: =0
            RadiusBottomRight: =0
            RadiusTopLeft: =0
            RadiusTopRight: =0
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="Users"
            Visible: =varPerfil.Flg_Adm
            Width: =fxTopNavItemWidth
            X: =260 + fxTopNavItemWidth * (1 + If(varPerfil.Flg_Relatorio, 1, 0))
            Y: =0
      - xx-cmp-topo-lbl-usuario:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Right
            Color: =fxColorPrimaryLight
            Font: =fxFont
            Height: =fxTopNavHeight
            Size: =fxFontSizeFilter
            Text: =varUsuario.Nom_Usuario & " · " & varPerfil.Des_Perfil
            VerticalAlign: =VerticalAlign.Middle
            Width: =360
            Wrap: =false
            X: =Parent.Width - 384
            Y: =0
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `xx-cmp-topo-` | the screen's prefix | the bar is replicated on every screen, with its own prefix (a legitimate exception to the naming) |
| `Orders`, `Reports`, `Users` | the button texts | short label (one word fits in `fxTopNavItemWidth`); the screen name in `Navigate(...)` must exist in the app |
| `"pedidos"` | the `varTelaAtiva` identifier | one per screen, same as the `Set` in its `OnVisible` |
| `varPerfil.Flg_Relatorio`, `varPerfil.Flg_Adm` | the profile's real flags | never compare the profile name |
| `X` of the buttons | `260 + fxTopNavItemWidth * <visible items before>` | count only the items the profile sees, so the bar has no gap |
| `Y` of the header and of the content | `fxTopNavHeight` more | with the bar, the `screen-header` container goes to `Y: =fxTopNavHeight` and the content moves down with it |

## Behavior

Destination of the formulas below: the same as the YAML (`,` between arguments, `;` chains).

**`xx-cmp-topo-btn-usuarios`.X**: position that counts only the items visible before it

```powerfx
260 + fxTopNavItemWidth * (1 + If(varPerfil.Flg_Relatorio, 1, 0))
```

**`xx-cmp-topo-btn-relatorios`.OnSelect**: saves the active screen and navigates without transition

```powerfx
Set(varTelaAtiva, "relatorios");
Navigate(Relatorios, ScreenTransition.None)
```

**`xx-cmp-topo-btn-relatorios`.Fill**: active item with its own background

```powerfx
If(varTelaAtiva = "relatorios", fxColorMenuItemActive, fxColorTransparent)
```

## Accessibility

- Every item is a focusable button and has a text label.
- The active item is told apart by background **and** bold, never by color alone.
- The bar comes before the content in the tab order; check it in the Accessibility checker.
- Light text on `fxColorMenuBg`: check the contrast of the user's `fxColorPrimaryLight` (minimum 4.5:1).

## Pitfalls

- A button hidden by flag with a fixed `X` leaves a gap in the bar: the `X` of each item counts only the items visible before it.
- More than 6 items or a long label does not fit in 1366 px of width: switch to `side-menu.md`.
- Forgetting to move the header and the content down by `fxTopNavHeight`: the bar covers the screen title.
- `varTelaAtiva` must be set by the `OnVisible` of every screen, as in the side menu.
- A button hidden by flag is not security: the screen validates the profile again.

## Variations

- Light bar: `Fill: =fxColorSurface`, text `fxColorTextPrimary` and active item with `fxColorPrimaryLight`; check the contrast.
- No submenu: Canvas has no reliable navigation dropdown; more than 6 screens calls for `side-menu.md`.

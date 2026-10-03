# Side menu

Maturity: **stable** · Frequency: **very common**.

## Purpose

Main navigation on the left, in three forms: **fixed** (an always-open column with the system name, one button per screen, the logged-in user and the current scope), **collapsible** (☰ toggles between icons only and icon + label) and **drawer** (hidden; ☰ in the header opens it over the content). The visibility of each button comes from the role's flag; the active item is highlighted by background and bold. The form is decided in `/pp-en:design` (`ux-design-system.md` §2.1).

## When to use / when not to use

**Use when**

- the app has 3 or more first-level screens;
- the navigation must respect the role's permission;
- fixed: daily use on desktop; collapsible: screens with a wide table; drawer: narrow screen (tablet) or an app for occasional use.

**Do not use when**

- the app has one or two screens (a back button is enough);
- the design chose a top bar (`top-menu.md`) or a home screen with cards (`home-cards.md`);
- permission is a business rule: button visibility is UX only, the flow is what blocks.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-cmp-menu-con  (GroupContainer)
  xx-cmp-menu-img-logo  (Image)
  xx-cmp-menu-lbl-titulo  (Label)
  xx-cmp-menu-lbl-subtitulo  (Label)
  xx-cmp-menu-btn-pedidos  (Button)
  xx-cmp-menu-btn-relatorios  (Button)
  xx-cmp-menu-btn-usuarios  (Button)
  xx-cmp-menu-lbl-usuario  (Label)
  xx-cmp-menu-lbl-perfil  (Label)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorTextOnPrimary`, `fxFont`, `fxFontSizeBody`, `fxColorPrimaryLight`, `fxFontSizeTableSmall`, `fxFontSizeFilter`, `fxColorToastText`, `fxColorButtonCancelHover`, `fxBtnRadius`, `fxBtnFontSize`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxColorMenuBg`, `fxMenuWidth`, `fxColorMenuItemActive`, `fxMenuItemHeight`, `fxNavWidthExpandida`, `fxNavWidthRecolhida`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varSemAcesso`, `varTelaAtiva`, `varPerfil`, `varUsuario`, `varUnidadeFiltro`, `varNavExpandida`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (en-US: `,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-cmp-menu-con:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorMenuBg
      Height: =Parent.Height
      Visible: =!varSemAcesso
      Width: =fxMenuWidth
      X: =0
      Y: =0
    Children:
      - xx-cmp-menu-img-logo:
          Control: Image@2.2.3
          Properties:
            DisplayMode: =DisplayMode.View
            Height: =40
            Image: ='<imagem-logo>'
            Width: =160
            X: =20
            Y: =24
      - xx-cmp-menu-lbl-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextOnPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =28
            Size: =fxFontSizeBody
            Text: ="System name"
            Width: =Parent.Width - 40
            X: =20
            Y: =76
      - xx-cmp-menu-lbl-subtitulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorPrimaryLight
            Font: =fxFont
            Height: =20
            Size: =fxFontSizeTableSmall
            Text: ="Module"
            Width: =Parent.Width - 40
            X: =20
            Y: =104
      - xx-cmp-menu-btn-pedidos:
          Control: Classic/Button@2.2.0
          Properties:
            Align: =Align.Left
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "pedidos", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "pedidos", FontWeight.Bold, FontWeight.Normal)
            Height: =fxMenuItemHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varTelaAtiva, "pedidos");
              Navigate(Pedidos, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="   Orders"
            Width: =fxMenuWidth
            X: =0
            Y: =160
      - xx-cmp-menu-btn-relatorios:
          Control: Classic/Button@2.2.0
          Properties:
            Align: =Align.Left
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "relatorios", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "relatorios", FontWeight.Bold, FontWeight.Normal)
            Height: =fxMenuItemHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varTelaAtiva, "relatorios");
              Navigate(Relatorios, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="   Reports"
            Visible: =varPerfil.Flg_Relatorio
            Width: =fxMenuWidth
            X: =0
            Y: =160 + fxMenuItemHeight
      - xx-cmp-menu-btn-usuarios:
          Control: Classic/Button@2.2.0
          Properties:
            Align: =Align.Left
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "usuarios", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "usuarios", FontWeight.Bold, FontWeight.Normal)
            Height: =fxMenuItemHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varTelaAtiva, "usuarios");
              Navigate(Usuarios, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="   Users"
            Visible: =varPerfil.Flg_Adm
            Width: =fxMenuWidth
            X: =0
            Y: =160 + fxMenuItemHeight * 2
      - xx-cmp-menu-lbl-usuario:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextOnPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =20
            Size: =fxFontSizeFilter
            Text: =varUsuario.Nom_Usuario
            Width: =Parent.Width - 40
            X: =20
            Y: =Parent.Height - 80
      - xx-cmp-menu-lbl-perfil:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorToastText
            Font: =fxFont
            Height: =36
            Size: =fxFontSizeTableSmall
            Text: =varPerfil.Des_Perfil & " · " & If(IsBlank(varUnidadeFiltro), "All units", varUnidadeFiltro)
            Width: =Parent.Width
            X: =0
            Y: =Parent.Height - 56
```

### Variation: collapsible

The container width comes from `varNavExpandida`. A named formula cannot read a variable, so the content area uses `'xx-cmp-menu-con'.Width` in place of `fxContentX`.

```yaml
- xx-cmp-menu-con:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorMenuBg
      Height: =Parent.Height
      Visible: =!varSemAcesso
      Width: =If(varNavExpandida, fxNavWidthExpandida, fxNavWidthRecolhida)
      X: =0
      Y: =0
    Children:
      - xx-cmp-menu-btn-alternar:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorMenuItemActive
            BorderThickness: =1
            Color: =fxColorTextOnPrimary
            Fill: =fxColorMenuItemActive
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =40
            HoverBorderColor: =fxColorButtonCancelHover
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorButtonCancelHover
            OnSelect: =Set(varNavExpandida, !varNavExpandida)
            PressedBorderColor: =fxColorButtonCancelHover
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorButtonCancelHover
            RadiusBottomLeft: =fxBtnRadius
            RadiusBottomRight: =fxBtnRadius
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxBtnFontSize
            TabIndex: =0
            Text: =If(varNavExpandida, "‹", "☰")
            Tooltip: =If(varNavExpandida, "Collapse menu", "Expand menu")
            Width: =54
            X: =8
            Y: =20
      - xx-cmp-menu-lbl-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextOnPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =28
            Size: =fxFontSizeBody
            Text: ="Menu"
            Visible: =varNavExpandida
            Width: =Parent.Width - 80
            X: =70
            Y: =28
      - xx-cmp-menu-btn-pedidos:
          Control: Classic/Button@2.2.0
          Properties:
            Align: =Align.Left
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "pedidos", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "pedidos", FontWeight.Bold, FontWeight.Normal)
            Height: =fxMenuItemHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varTelaAtiva, "pedidos");
              Navigate(Pedidos, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: =If(varNavExpandida, "   Orders", Left("Orders", 1))
            Tooltip: ="Orders"
            Width: =Parent.Width
            X: =0
            Y: =100
```

### Variation: drawer (hamburger)

**New** variation, not yet seen in production: confirm it when pasting. The menu stays hidden and the screen uses the full width (content with `X: =0`). The ☰ button sits in the corner of the header and opens the menu over the content, with a scrim that closes on tap. It reuses `varNavExpandida` as "drawer open". Paste the block **after** the content and **before** the modals (order of `T016`): the drawer covers the screen, the modals cover the drawer.

```yaml
- xx-cmp-menu-btn-abrir:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorTransparent
      BorderThickness: =0
      Color: =fxColorPrimary
      Fill: =fxColorTransparent
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =48
      HoverBorderColor: =fxColorTransparent
      HoverColor: =fxColorPrimaryDark
      HoverFill: =fxColorPrimaryLight
      OnSelect: =Set(varNavExpandida, true)
      PressedBorderColor: =fxColorTransparent
      PressedColor: =fxColorPrimaryDark
      PressedFill: =fxColorPrimaryLight
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="☰"
      Tooltip: ="Open menu"
      Visible: =!varSemAcesso
      Width: =48
      X: =16
      Y: =(fxHeaderHeight - 48) / 2
- xx-cmp-menu-veu:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorTransparent
      BorderThickness: =0
      Color: =fxColorTransparent
      Fill: =fxColorOverlay
      Height: =Parent.Height
      HoverBorderColor: =fxColorTransparent
      HoverFill: =fxColorOverlay
      OnSelect: =Set(varNavExpandida, false)
      PressedBorderColor: =fxColorTransparent
      PressedFill: =fxColorOverlay
      TabIndex: =-1
      Text: =""
      Visible: =varNavExpandida
      Width: =Parent.Width
      X: =0
      Y: =0
- xx-cmp-menu-con:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      DropShadow: =DropShadow.Bold
      Fill: =fxColorMenuBg
      Height: =Parent.Height
      Visible: =varNavExpandida && !varSemAcesso
      Width: =fxNavWidthExpandida
      X: =0
      Y: =0
    Children:
      - xx-cmp-menu-btn-fechar:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorMenuItemActive
            BorderThickness: =1
            Color: =fxColorTextOnPrimary
            Fill: =fxColorMenuItemActive
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =40
            HoverBorderColor: =fxColorButtonCancelHover
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorButtonCancelHover
            OnSelect: =Set(varNavExpandida, false)
            PressedBorderColor: =fxColorButtonCancelHover
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorButtonCancelHover
            RadiusBottomLeft: =fxBtnRadius
            RadiusBottomRight: =fxBtnRadius
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxBtnFontSize
            TabIndex: =0
            Text: ="✕"
            Tooltip: ="Close menu"
            Width: =40
            X: =Parent.Width - 56
            Y: =20
      - xx-cmp-menu-lbl-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextOnPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =28
            Size: =fxFontSizeBody
            Text: ="System name"
            Width: =Parent.Width - 88
            X: =20
            Y: =26
      - xx-cmp-menu-btn-pedidos:
          Control: Classic/Button@2.2.0
          Properties:
            Align: =Align.Left
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "pedidos", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "pedidos", FontWeight.Bold, FontWeight.Normal)
            Height: =fxMenuItemHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varNavExpandida, false);
              Set(varTelaAtiva, "pedidos");
              Navigate(Pedidos, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="   Orders"
            Width: =Parent.Width
            X: =0
            Y: =80
```

## Parameters to change

| In the block | Change to | Note |
|---|---|---|
| `xx-cmp-menu-` | prefix of the screen | the menu is replicated on every screen, with its own prefix (a legitimate exception to the name rule) |
| `Orders`, `Reports`, `Users` | button texts | the screen name in `Navigate(Pedidos, ...)` (no accents, capitalized) must exist in the app |
| `"pedidos"` | identifier of `varTelaAtiva` | one per screen, equal to the `Set` in its `OnVisible` |
| `varPerfil.Flg_Relatorio`, `varPerfil.Flg_Adm` | real role flags | never compare the role name |
| `'<imagem-logo>'` | media resource | or remove the image |

## Behavior

Destination of the formulas below: the same as the YAML (en-US: `,` and `;`).

**`xx-cmp-menu-btn-relatorios`.Visible**: the button exists only for those who have the flag

```powerfx
varPerfil.Flg_Relatorio
```

**`xx-cmp-menu-btn-relatorios`.OnSelect**: stores the active screen and navigates without a transition

```powerfx
Set(varTelaAtiva, "relatorios");
Navigate(Relatorios, ScreenTransition.None)
```

**`xx-cmp-menu-btn-relatorios`.Fill**: active item with its own background

```powerfx
If(varTelaAtiva = "relatorios", fxColorMenuItemActive, fxColorTransparent)
```

## Accessibility

- Every item is a focusable button and has a text label.
- The active item is told apart by background **and** bold, never by color alone.
- The menu comes before the content in the tab order: focus goes through it first; check the shortcut to skip straight to the content in the Accessibility checker.

## Pitfalls

- `varTelaAtiva` must be set by the `OnVisible` of each screen; only the button's `Set` leaves the highlight wrong when navigation comes from elsewhere.
- A button hidden by a flag is not security: the user can still open the screen by another path; the screen validates the role again.
- Long role text cut off: the `Label` has no `AutoHeight`; reserve enough `Width` (`Parent.Width`) and `Align.Center`.
- `Navigate()` with a nonexistent screen name shows up as a formula error only after pasting.
- Drawer: the item must close the drawer (`Set(varNavExpandida, false)`) before navigating; otherwise it shows open on the next screen. The scrim is a button without text and with `TabIndex: =-1`: keyboard users close it with the ✕.

## Variations

- Collapsible (above), with `varNavExpandida` starting as `false` in `OnStart`.
- Drawer (above), with `varNavExpandida` starting as `false` (drawer closed).
- Horizontal bar at the top: its own component, `top-menu.md`.
- Home screen with cards, no fixed menu: `home-cards.md`.

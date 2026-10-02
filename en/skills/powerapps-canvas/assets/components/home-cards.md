# Home screen with cards

Maturity: **new** · Frequency: **to be measured**.

## Purpose

Navigation through a home screen: one card per area of the app (title, one sentence about what you do there, and the "Open" button), with visibility by the role's flag. There is no fixed menu; the other screens use the full width and have a "‹ Home" button in the header to go back. This pattern is chosen in `/pp-en:design` (`ux-design-system.md` §2.1).

## When to use / when not to use

**Use when**

- the app is for occasional use and each person comes in for a single task;
- there are 2 to 8 first-level areas, and a sentence helps to choose;
- the app runs on a narrow screen (tablet) or is used by people not used to menus.

**Do not use when**

- use is daily and the person switches screens all the time: the way back to the home costs one extra tap (use `side-menu.md` or `top-menu.md`);
- permission is a business rule: card visibility is UX only, the flow is what blocks.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-cmp-inicio-con  (GroupContainer)
  xx-cmp-inicio-card-pedidos  (GroupContainer)
    xx-cmp-inicio-lbl-pedidos-titulo  (Label)
    xx-cmp-inicio-lbl-pedidos-desc  (Label)
    xx-cmp-inicio-btn-pedidos  (Button)
  xx-cmp-inicio-card-relatorios  (GroupContainer)
    xx-cmp-inicio-lbl-relatorios-titulo  (Label)
    xx-cmp-inicio-lbl-relatorios-desc  (Label)
    xx-cmp-inicio-btn-relatorios  (Button)
```

The second block (`xx-cmp-inicio-btn-voltar`) goes in the header of each of the other screens.

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorBorder`, `fxColorSurface`, `fxColorPrimary`, `fxColorPrimaryDark`, `fxColorPrimaryLight`, `fxColorTextOnPrimary`, `fxColorTextSecondary`, `fxFont`, `fxFontSizeBody`, `fxBtnRadius`, `fxBtnFontSize`, `fxModalRadius`, `fxLayoutMargin`, `fxLayoutGutter`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxHeaderHeight`, `fxHubCardWidth`, `fxHubCardHeight`, `fxFontSizeCardTitle`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varSemAcesso`, `varTelaAtiva`, `varPerfil`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (en-US: `,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the home screen as parent, after its header; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-cmp-inicio-con:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorTransparent
      Height: =fxHubCardHeight + 24
      Visible: =!varSemAcesso
      Width: =Parent.Width - fxLayoutMargin * 2
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + 40
    Children:
      - xx-cmp-inicio-card-pedidos:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            BorderThickness: =1
            DropShadow: =DropShadow.Light
            Fill: =fxColorSurface
            Height: =fxHubCardHeight
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxHubCardWidth
            X: =0
            Y: =0
          Children:
            - xx-cmp-inicio-lbl-pedidos-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =32
                  Size: =fxFontSizeCardTitle
                  Text: ="Orders"
                  Width: =Parent.Width - 40
                  Wrap: =false
                  X: =20
                  Y: =18
            - xx-cmp-inicio-lbl-pedidos-desc:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  Height: =48
                  Size: =fxFontSizeBody
                  Text: ="Create and track the orders of your unit."
                  VerticalAlign: =VerticalAlign.Top
                  Width: =Parent.Width - 40
                  X: =20
                  Y: =54
            - xx-cmp-inicio-btn-pedidos:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =fxColorPrimary
                  BorderThickness: =1
                  Color: =fxColorTextOnPrimary
                  Fill: =fxColorPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =40
                  HoverBorderColor: =fxColorPrimaryDark
                  HoverColor: =fxColorTextOnPrimary
                  HoverFill: =fxColorPrimaryDark
                  OnSelect: |-
                    =Set(varTelaAtiva, "pedidos");
                    Navigate(Pedidos, ScreenTransition.None)
                  PressedBorderColor: =fxColorPrimaryDark
                  PressedColor: =fxColorTextOnPrimary
                  PressedFill: =fxColorPrimaryDark
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxBtnFontSize
                  TabIndex: =0
                  Text: ="Open Orders"
                  Width: =160
                  X: =20
                  Y: =Parent.Height - 58
      - xx-cmp-inicio-card-relatorios:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            BorderThickness: =1
            DropShadow: =DropShadow.Light
            Fill: =fxColorSurface
            Height: =fxHubCardHeight
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Visible: =varPerfil.Flg_Relatorio
            Width: =fxHubCardWidth
            X: =fxHubCardWidth + fxLayoutGutter * 2
            Y: =0
          Children:
            - xx-cmp-inicio-lbl-relatorios-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =32
                  Size: =fxFontSizeCardTitle
                  Text: ="Reports"
                  Width: =Parent.Width - 40
                  Wrap: =false
                  X: =20
                  Y: =18
            - xx-cmp-inicio-lbl-relatorios-desc:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  Height: =48
                  Size: =fxFontSizeBody
                  Text: ="See the numbers for the period and export them."
                  VerticalAlign: =VerticalAlign.Top
                  Width: =Parent.Width - 40
                  X: =20
                  Y: =54
            - xx-cmp-inicio-btn-relatorios:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =fxColorPrimary
                  BorderThickness: =1
                  Color: =fxColorTextOnPrimary
                  Fill: =fxColorPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =40
                  HoverBorderColor: =fxColorPrimaryDark
                  HoverColor: =fxColorTextOnPrimary
                  HoverFill: =fxColorPrimaryDark
                  OnSelect: |-
                    =Set(varTelaAtiva, "relatorios");
                    Navigate(Relatorios, ScreenTransition.None)
                  PressedBorderColor: =fxColorPrimaryDark
                  PressedColor: =fxColorTextOnPrimary
                  PressedFill: =fxColorPrimaryDark
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxBtnFontSize
                  TabIndex: =0
                  Text: ="Open Reports"
                  Width: =160
                  X: =20
                  Y: =Parent.Height - 58
```

### "‹ Home" button on the other screens

Paste it inside the `screen-header` container of every screen that is not the home screen and move the title to the right of the button (`X: =fxLayoutMargin + 120`).

```yaml
- xx-cmp-inicio-btn-voltar:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorPrimary
      BorderThickness: =1
      Color: =fxColorPrimary
      Fill: =fxColorTransparent
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =40
      HoverBorderColor: =fxColorPrimaryDark
      HoverColor: =fxColorPrimaryDark
      HoverFill: =fxColorPrimaryLight
      OnSelect: |-
        =Set(varTelaAtiva, "inicio");
        Navigate(Inicio, ScreenTransition.None)
      PressedBorderColor: =fxColorPrimaryDark
      PressedColor: =fxColorPrimaryDark
      PressedFill: =fxColorPrimaryLight
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="‹ Home"
      Tooltip: ="Back to the home screen"
      Width: =104
      X: =fxLayoutMargin
      Y: =(fxHeaderHeight - 40) / 2
```

## Parameters to change

| In the block | Change to | Note |
|---|---|---|
| `xx-cmp-inicio-` | prefix of the home screen | the cards exist only on the home screen; the "‹ Home" button carries the prefix of each screen |
| `Orders`, `Reports` | title of each area | the screen name in `Navigate(...)` (no accents, capitalized) must exist in the app |
| the sentence on each card | what the person does there, in one line | verb first ("Create", "See", "Approve") |
| `varPerfil.Flg_Relatorio` | real role flags | never compare the role name |
| `X` of the cards | `(fxHubCardWidth + fxLayoutGutter * 2) * <visible cards before>` | count only the cards the role sees; with more than 4 per row, start another row with `Y` plus `fxHubCardHeight + 24` |
| `Inicio`, `"inicio"` | name of the home screen and its identifier | the same `Set` as in its `OnVisible` |

## Behavior

Destination of the formulas below: the same as the YAML (en-US: `,` and `;`).

**`xx-cmp-inicio-card-relatorios`.Visible**: the card exists only for those who have the flag

```powerfx
varPerfil.Flg_Relatorio
```

**X of the third card**: counts only the cards visible before it

```powerfx
(fxHubCardWidth + fxLayoutGutter * 2) * (1 + If(varPerfil.Flg_Relatorio, 1, 0))
```

**`xx-cmp-inicio-btn-voltar`.OnSelect**: goes back to the home screen

```powerfx
Set(varTelaAtiva, "inicio");
Navigate(Inicio, ScreenTransition.None)
```

## Accessibility

- The action of each card is a real button, with a label that says the destination ("Open Orders"), not a whole clickable card without text.
- Title and sentence are text, read in the card's order; the button comes last.
- The "‹ Home" is the first focusable item of the header on the other screens.

## Pitfalls

- A card hidden by a flag with a fixed `X` leaves a gap: `X` counts only the cards visible before it.
- Without the "‹ Home" on every screen, the user gets stuck: check every screen in the test script.
- A long sentence overflows the two lines of the 48 px `Label`: cut the sentence, do not enlarge the card.
- A card hidden by a flag is not security: the destination screen validates the role again.

## Variations

- With a counter: a `Label` to the right of the title with the number of pending items in the area (e.g., orders awaiting approval), read from a variable loaded in `OnVisible`, never from `CountRows` over a SQL source.
- With a menu too: combine it with the collapsible `side-menu.md` when daily use calls for quick screen switching; the cards become the home screen.

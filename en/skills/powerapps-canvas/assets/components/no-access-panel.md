# "No access" panel

Maturity: **unique** · Frequency: **common**.

## Purpose

Full-screen panel shown when the user has no profile or unit registered. It is the visible end of fail-closed: `varSemAcesso` starts `true` and only becomes `false` after access is proven.

## When to use / when not to use

**Use when**

- every screen of an app with profile control;
- the content and the menu have `Visible: =!varSemAcesso`.

**Do not use when**

- the app is open to any user in the tenant;
- the restriction is on an **action** (hide the button and let the flow block it).

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-cmp-sem-acesso  (GroupContainer)
  xx-lbl-sem-acesso-titulo  (Label)
  xx-lbl-sem-acesso-hint  (Label)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorBackground`, `fxColorPrimary`, `fxFont`, `fxFontSizeSemAcesso`, `fxMsgSemAcessoTitulo`, `fxColorTextBody`, `fxFontSizeBody`, `fxMsgSemAcessoHint`, `fxColorTextPrimary`, `fxMsgSemPermissao`.
- **Global variables** (created in `OnStart`, `assets/app-onstart-template.md`): `varSemAcesso`, `varPerfil`.
- **Collections**: none.
- **Flows**: none.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-cmp-sem-acesso:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorBackground
      Height: =Parent.Height
      Visible: =varSemAcesso
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-lbl-sem-acesso-titulo:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =40
            Size: =fxFontSizeSemAcesso
            Text: =fxMsgSemAcessoTitulo
            Width: =700
            X: =(Parent.Width - Self.Width) / 2
            Y: =400
      - xx-lbl-sem-acesso-hint:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorTextBody
            Font: =fxFont
            Height: =60
            Size: =fxFontSizeBody
            Text: =fxMsgSemAcessoHint
            Width: =700
            X: =(Parent.Width - Self.Width) / 2
            Y: =450
```

### Variation: no permission for this screen

The user has access to the app but not to this screen: the panel covers it based only on the screen flag.

```yaml
- xx-cmp-sem-permissao:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorBackground
      Height: =Parent.Height
      Visible: =!varSemAcesso && !varPerfil.Flg_Relatorio
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-lbl-sem-permissao:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorTextPrimary
            Font: =fxFont
            Height: =40
            Size: =fxFontSizeBody
            Text: =fxMsgSemPermissao
            Width: =700
            X: =(Parent.Width - Self.Width) / 2
            Y: =470
```

## Parameters to change

| In the block | Change to | Note |
|---|---|---|
| `fxMsgSemAcessoTitulo`, `fxMsgSemAcessoHint` | the project texts | say what happened and who to contact |
| `varPerfil.Flg_Relatorio` | the screen's real flag | variation; never compare the profile name |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-cmp-sem-acesso`.Visible**: `varSemAcesso`, computed in `OnStart` after identity, profile and scope

```powerfx
varSemAcesso
```

## Accessibility

- The title is in `fxColorPrimary` and the text in `fxColorTextBody` over `fxColorBackground`, with a 4.5:1 contrast.
- The panel replaces the content: the screen reader finds the title and instruction first.

## Pitfalls

- Place it right before the modals in `Children`: the content and the menu already disappear through `Visible`, the panel covers the rest.
- `varSemAcesso` initialized `false` lets everyone in during `OnStart` (`OnStart` does not block the first render).
- Hiding the panel is not authorization: the flow validates the profile again.

## Variations

- No permission (above).
- Panel with a "Contact the administrator" button (`Launch("mailto:...")`).

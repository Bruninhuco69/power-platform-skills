# Menu lateral

Maturidade: **estável** · Frequência: **muito comum**.

## Propósito

Navegação principal à esquerda, em três formas: **fixa** (coluna sempre aberta com o nome do sistema, um botão por tela, usuário logado e escopo atual), **recolhível** (☰ alterna entre só ícones e ícone + rótulo) e **gaveta** (escondida; ☰ no cabeçalho abre por cima do conteúdo). A visibilidade de cada botão vem da flag do perfil; o item ativo é destacado por fundo e negrito. A forma é decidida no `/pp:design` (`ux-design-system.md` §2.1).

## Quando usar / quando não usar

**Use quando**

- o app tem 3 ou mais telas de primeiro nível;
- a navegação precisa respeitar permissão do perfil;
- fixa: uso diário no desktop; recolhível: telas com tabela larga; gaveta: tela estreita (tablet) ou app de uso eventual.

**Não use quando**

- o app tem uma ou duas telas (botão de voltar basta);
- o design escolheu barra no topo (`menu-topo.md`) ou tela inicial com cartões (`inicio-cartoes.md`);
- a permissão é regra de negócio: a visibilidade do botão é só UX, quem barra é o flow.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

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

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorTextOnPrimary`, `fxFont`, `fxFontSizeBody`, `fxColorPrimaryLight`, `fxFontSizeTableSmall`, `fxFontSizeFilter`, `fxColorToastText`, `fxColorButtonCancelHover`, `fxBtnRadius`, `fxBtnFontSize`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxColorMenuBg`, `fxMenuWidth`, `fxColorMenuItemActive`, `fxMenuItemHeight`, `fxNavWidthExpandida`, `fxNavWidthRecolhida`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varSemAcesso`, `varTelaAtiva`, `varPerfil`, `varUsuario`, `varUnidadeFiltro`, `varNavExpandida`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

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
            Text: ="Nome do sistema"
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
            Text: ="Módulo"
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
            Text: ="   Pedidos"
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
            Text: ="   Relatórios"
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
            Text: ="   Usuários"
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
            Text: =varPerfil.Des_Perfil & " · " & If(IsBlank(varUnidadeFiltro), "Todas as unidades", varUnidadeFiltro)
            Width: =Parent.Width
            X: =0
            Y: =Parent.Height - 56
```

### Variação: recolhível

A largura do contêiner vem de `varNavExpandida`. Um named formula não pode ler variável, então a área de conteúdo usa `'xx-cmp-menu-con'.Width` no lugar de `fxContentX`.

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
            Tooltip: =If(varNavExpandida, "Recolher menu", "Expandir menu")
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
            Text: =If(varNavExpandida, "   Pedidos", Left("Pedidos", 1))
            Tooltip: ="Pedidos"
            Width: =Parent.Width
            X: =0
            Y: =100
```

### Variação: gaveta (hambúrguer)

Variação **nova**, ainda não vista em produção: confirme na colagem. O menu fica escondido e a tela usa a largura toda (conteúdo com `X: =0`). O botão ☰ fica no canto do cabeçalho e abre o menu por cima do conteúdo, com um véu que fecha ao toque. Reaproveita `varNavExpandida` como "gaveta aberta". Cole o bloco **depois** do conteúdo e **antes** dos modais (ordem do `T016`): a gaveta cobre a tela, os modais cobrem a gaveta.

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
      Tooltip: ="Abrir menu"
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
            Tooltip: ="Fechar menu"
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
            Text: ="Nome do sistema"
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
            Text: ="   Pedidos"
            Width: =Parent.Width
            X: =0
            Y: =80
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-cmp-menu-` | prefixo da tela | o menu é replicado em cada tela, com prefixo próprio (exceção legítima do nome) |
| `Pedidos`, `Relatórios`, `Usuários` | textos dos botões | o nome da tela em `Navigate(Pedidos, ...)` (sem acento, capitalizado) precisa existir no app |
| `"pedidos"` | identificador de `varTelaAtiva` | um por tela, igual ao `Set` do `OnVisible` dela |
| `varPerfil.Flg_Relatorio`, `varPerfil.Flg_Adm` | flags reais do perfil | nunca comparar nome do perfil |
| `'<imagem-logo>'` | recurso de mídia | ou remova a imagem |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-cmp-menu-btn-relatorios`.Visible**: o botão só existe para quem tem a flag

```powerfx
varPerfil.Flg_Relatorio
```

**`xx-cmp-menu-btn-relatorios`.OnSelect**: grava a tela ativa e navega sem transição

```powerfx
Set(varTelaAtiva, "relatorios");
Navigate(Relatorios, ScreenTransition.None)
```

**`xx-cmp-menu-btn-relatorios`.Fill**: item ativo com fundo próprio

```powerfx
If(varTelaAtiva = "relatorios", fxColorMenuItemActive, fxColorTransparent)
```

## Acessibilidade

- Todo item é botão focável e tem rótulo de texto.
- O item ativo se distingue por fundo **e** negrito, nunca só por cor.
- O menu fica antes do conteúdo na ordem de tabulação: foco passa por ele primeiro; confira o atalho para pular direto ao conteúdo no Accessibility checker.

## Armadilhas

- `varTelaAtiva` precisa ser gravada pelo `OnVisible` de cada tela; só o `Set` do botão deixa o destaque errado quando a navegação vem de outro ponto.
- Botão oculto por flag não é segurança: o usuário ainda consegue abrir a tela por outro caminho; a tela valida o perfil de novo.
- Texto do perfil longo cortado: o `Label` não tem `AutoHeight`; reserve `Width` suficiente (`Parent.Width`) e `Align.Center`.
- `Navigate()` com nome de tela inexistente aparece como erro de fórmula só depois da colagem.
- Gaveta: o item precisa fechar a gaveta (`Set(varNavExpandida, false)`) antes de navegar; senão ela aparece aberta na próxima tela. O véu é botão sem texto e com `TabIndex: =-1`: quem usa teclado fecha pelo ✕.

## Variações

- Recolhível (acima), com `varNavExpandida` nascida `false` no `OnStart`.
- Gaveta (acima), com `varNavExpandida` nascida `false` (gaveta fechada).
- Barra horizontal no topo: componente próprio, `menu-topo.md`.
- Tela inicial com cartões, sem menu fixo: `inicio-cartoes.md`.

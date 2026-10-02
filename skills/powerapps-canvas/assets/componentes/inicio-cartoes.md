# Tela inicial com cartões

Maturidade: **novo** · Frequência: **a medir**.

## Propósito

Navegação por uma tela inicial: um cartão por área do app (título, uma frase do que se faz ali e o botão "Abrir"), com visibilidade por flag do perfil. Não há menu fixo; as demais telas usam a largura toda e têm o botão "‹ Início" no cabeçalho para voltar. A escolha deste padrão é feita no `/pp:design` (`ux-design-system.md` §2.1).

## Quando usar / quando não usar

**Use quando**

- o app é de uso eventual e cada pessoa entra para uma tarefa só;
- há de 2 a 8 áreas de primeiro nível, e uma frase ajuda a escolher;
- o app roda em tela estreita (tablet) ou por gente pouco acostumada a menus.

**Não use quando**

- o uso é diário e a pessoa troca de tela o tempo todo: o caminho de volta ao início custa um toque a mais (use `menu-lateral.md` ou `menu-topo.md`);
- a permissão é regra de negócio: a visibilidade do cartão é só UX, quem barra é o flow.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

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

O segundo bloco (`xx-cmp-inicio-btn-voltar`) vai no cabeçalho de cada uma das outras telas.

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorBorder`, `fxColorSurface`, `fxColorPrimary`, `fxColorPrimaryDark`, `fxColorPrimaryLight`, `fxColorTextOnPrimary`, `fxColorTextSecondary`, `fxFont`, `fxFontSizeBody`, `fxBtnRadius`, `fxBtnFontSize`, `fxModalRadius`, `fxLayoutMargin`, `fxLayoutGutter`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxHeaderHeight`, `fxHubCardWidth`, `fxHubCardHeight`, `fxFontSizeCardTitle`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varSemAcesso`, `varTelaAtiva`, `varPerfil`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela inicial como pai, depois do cabeçalho dela; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

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
                  Text: ="Pedidos"
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
                  Text: ="Cadastre e acompanhe os pedidos da sua unidade."
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
                  Text: ="Abrir Pedidos"
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
                  Text: ="Relatórios"
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
                  Text: ="Veja os números do período e exporte."
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
                  Text: ="Abrir Relatórios"
                  Width: =160
                  X: =20
                  Y: =Parent.Height - 58
```

### Botão "‹ Início" nas demais telas

Cole dentro do contêiner do `cabecalho-tela` de cada tela que não é a inicial e desloque o título para a direita do botão (`X: =fxLayoutMargin + 120`).

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
      Text: ="‹ Início"
      Tooltip: ="Voltar para a tela inicial"
      Width: =104
      X: =fxLayoutMargin
      Y: =(fxHeaderHeight - 40) / 2
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-cmp-inicio-` | prefixo da tela inicial | os cartões só existem na tela inicial; o botão "‹ Início" leva o prefixo de cada tela |
| `Pedidos`, `Relatórios` | título de cada área | o nome da tela em `Navigate(...)` (sem acento, capitalizado) precisa existir no app |
| a frase de cada cartão | o que a pessoa faz ali, em uma linha | verbo no começo ("Cadastre", "Veja", "Aprove") |
| `varPerfil.Flg_Relatorio` | flags reais do perfil | nunca comparar nome do perfil |
| `X` dos cartões | `(fxHubCardWidth + fxLayoutGutter * 2) * <cartões visíveis antes>` | conte só os cartões que o perfil vê; mais de 4 por linha, comece outra linha com `Y` somado de `fxHubCardHeight + 24` |
| `Inicio`, `"inicio"` | nome da tela inicial e seu identificador | o mesmo `Set` do `OnVisible` dela |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-cmp-inicio-card-relatorios`.Visible**: o cartão só existe para quem tem a flag

```powerfx
varPerfil.Flg_Relatorio
```

**X do terceiro cartão**: conta só os cartões visíveis antes dele

```powerfx
(fxHubCardWidth + fxLayoutGutter * 2) * (1 + If(varPerfil.Flg_Relatorio, 1, 0))
```

**`xx-cmp-inicio-btn-voltar`.OnSelect**: volta para a tela inicial

```powerfx
Set(varTelaAtiva, "inicio");
Navigate(Inicio, ScreenTransition.None)
```

## Acessibilidade

- A ação de cada cartão é um botão de verdade, com rótulo que diz o destino ("Abrir Pedidos"), não um cartão inteiro clicável sem texto.
- Título e frase são texto, lidos na ordem do cartão; o botão vem por último.
- O "‹ Início" é o primeiro item focável do cabeçalho nas demais telas.

## Armadilhas

- Cartão oculto por flag com `X` fixo deixa um buraco: o `X` conta só os cartões visíveis antes dele.
- Sem o "‹ Início" em toda tela, o usuário fica preso: confira cada tela no roteiro de teste.
- Frase longa estoura as duas linhas do `Label` de 48 px: corte a frase, não aumente o cartão.
- Cartão oculto por flag não é segurança: a tela de destino valida o perfil de novo.

## Variações

- Com contador: um `Label` à direita do título com o número de pendências da área (ex.: pedidos aguardando aprovação), lido de variável carregada no `OnVisible`, nunca de `CountRows` sobre fonte SQL.
- Com menu também: combine com o `menu-lateral.md` recolhível quando o uso diário pedir troca rápida de tela; os cartões viram a tela inicial.

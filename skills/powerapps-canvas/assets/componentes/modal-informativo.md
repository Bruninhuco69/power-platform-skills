# Modal informativo (detalhes e histórico)

Maturidade: **estável** · Frequência: **ocasional**.

## Propósito

Modal só de leitura: título, uma mini-tabela (histórico, trilha, resultado de lote) e o botão `Fechar`. Sem ação de gravação, portanto sem loading nem flow.

## Quando usar / quando não usar

**Use quando**

- mostrar detalhe ou histórico de um registro sem sair da tela;
- mostrar o resultado de uma operação em lote.

**Não use quando**

- o conteúdo é grande (muitas colunas ou linhas): use tela dedicada;
- o usuário precisa agir sobre o conteúdo (use formulário).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-mod-detalhes  (GroupContainer)
  xx-mod-detalhes-bloqueio  (Button)
  xx-mod-detalhes-card  (GroupContainer)
    xx-mod-detalhes-titulo  (Label)
    xx-hdr-gal-mod-data  (Button)
    xx-hdr-gal-mod-evento  (Button)
    xx-hdr-gal-mod-usuario  (Button)
    xx-hdr-gal-mod-descricao  (Button)
    xx-gal-mod-historico  (Gallery)
      xx-lbl-mod-historico-data  (Label)
      xx-lbl-mod-historico-evento  (Label)
      xx-lbl-mod-historico-usuario  (Label)
      xx-lbl-mod-historico-descricao  (Label)
    xx-mod-detalhes-vazio  (Label)
    xx-mod-detalhes-btn-fechar  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorOverlayDark`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxColorPrimaryDark`, `fxFont`, `fxModalTitleSize`, `fxModalPadding`, `fxColorTableHeaderText`, `fxColorTableHeaderBg`, `fxFontSizeHeader`, `fxTableHeaderHeight`, `fxRowHeight`, `fxColorTextSecondary`, `fxFontSizeTableSmall`, `fxColorTextPrimary`, `fxFontSizeTable`, `fxFontSizeBody`, `fxMsgNoResultsError`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxBtnRadius`, `fxTxtFechar`, `fxBtnFontSize`, `fxBtnWidth`, `fxBtnHeight`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxModalWidthL`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varMostrarDetalhes`, `varPedidoSel`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-mod-detalhes:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlayDark
      Height: =Parent.Height
      Visible: =varMostrarDetalhes
      Width: =Parent.Width
    Children:
      - xx-mod-detalhes-bloqueio:
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
      - xx-mod-detalhes-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =560
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxModalWidthL + 260
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-mod-detalhes-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorPrimaryDark
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =32
                  Size: =fxModalTitleSize
                  Text: ="Histórico do pedido " & varPedidoSel.<col-codigo>
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =fxModalPadding
            - xx-hdr-gal-mod-data:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Data"
                  Width: =140
                  X: =fxModalPadding
                  Y: =70
            - xx-hdr-gal-mod-evento:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Evento"
                  Width: =200
                  X: =fxModalPadding + 140
                  Y: =70
            - xx-hdr-gal-mod-usuario:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Usuário"
                  Width: =200
                  X: =fxModalPadding + 340
                  Y: =70
            - xx-hdr-gal-mod-descricao:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Descrição"
                  Width: =300
                  X: =fxModalPadding + 540
                  Y: =70
            - xx-gal-mod-historico:
                Control: Gallery@2.15.0
                Variant: BrowseLayout_Flexible_SocialFeed_ver5.0
                Properties:
                  BorderColor: =fxColorBorder
                  BorderThickness: =1
                  Height: =fxRowHeight * 5
                  Items: |-
                    =Sort(
                      Filter('<fonte-historico>', <col-pedido> = varPedidoSel.<col-id>),
                      <col-data>,
                      SortOrder.Descending
                    )
                  TemplatePadding: =0
                  TemplateSize: =Max(20, fxRowHeight)
                  Width: =840
                  X: =fxModalPadding
                  Y: =70 + fxTableHeaderHeight
                Children:
                  - xx-lbl-mod-historico-data:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorTextSecondary
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTableSmall
                        Text: =Text(ThisItem.<col-data>, "[$-pt-BR]dd/mm/yyyy hh:mm")
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =130
                        X: =8
                        Y: =0
                  - xx-lbl-mod-historico-evento:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorTextPrimary
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTable
                        Text: =ThisItem.<col-evento>
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =190
                        X: =140
                        Y: =0
                  - xx-lbl-mod-historico-usuario:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorTextSecondary
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTableSmall
                        Text: =ThisItem.<col-usuario>
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =190
                        X: =340
                        Y: =0
                  - xx-lbl-mod-historico-descricao:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorTextPrimary
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTableSmall
                        Text: =ThisItem.<col-descricao>
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =290
                        X: =540
                        Y: =0
            - xx-mod-detalhes-vazio:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  Height: =40
                  Size: =fxFontSizeBody
                  Text: =fxMsgNoResultsError
                  Visible: ='xx-gal-mod-historico'.AllItemsCount = 0
                  Width: =840
                  X: =fxModalPadding
                  Y: =70 + fxTableHeaderHeight + 40
            - xx-mod-detalhes-btn-fechar:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =fxColorButtonCancel
                  BorderThickness: =1
                  Color: =fxColorTextOnPrimary
                  Fill: =fxColorButtonCancel
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxBtnHeight
                  HoverBorderColor: =fxColorButtonCancelHover
                  HoverColor: =fxColorTextOnPrimary
                  HoverFill: =fxColorButtonCancelHover
                  OnSelect: |-
                    =Set(varMostrarDetalhes, false);
                    Set(varPedidoSel, Blank())
                  PressedBorderColor: =fxColorButtonCancelHover
                  PressedColor: =fxColorTextOnPrimary
                  PressedFill: =fxColorButtonCancelHover
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxBtnFontSize
                  TabIndex: =0
                  Text: =fxTxtFechar
                  Width: =fxBtnWidth
                  X: =Parent.Width - Self.Width - fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-mod-detalhes`, `varMostrarDetalhes` | `xx-mod-<assunto>`, `varMostrar<Assunto>` | o botão da galeria o abre |
| `'<fonte-historico>'`, `<col-pedido>`, `<col-data>` | tabela e colunas reais do histórico | filtro pela chave do registro selecionado |
| larguras 140, 200, 200 e 300 | colunas reais | a soma deve caber em `Width` da galeria (840) |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-mod-detalhes-btn-fechar`.OnSelect**: fecha e limpa a seleção

```powerfx
Set(varMostrarDetalhes, false);
Set(varPedidoSel, Blank())
```

**`xx-gal-mod-historico`.Items**: histórico do registro selecionado, mais recente primeiro

```powerfx
Sort(
  Filter('<fonte-historico>', <col-pedido> = varPedidoSel.<col-id>),
  <col-data>,
  SortOrder.Descending
)
```

## Acessibilidade

- Só existe um botão e ele é `Fechar`: mantenha-o na ordem de tabulação e com texto.
- Sem `Escape` e sem clicar no véu para fechar (limitação do Canvas): o botão é o único caminho.

## Armadilhas

- Clicar no véu não fecha (o bloqueio tem `OnSelect: =false`): se quiser, troque por `Set(varMostrarDetalhes, false)`, mas aceite o fechamento acidental.
- `Filter(<fonte>, <col-pedido> = varPedidoSel.<col-id>)` delega em igualdade; `LookUp` por linha, não.
- Largura do card derivada de token (`fxModalWidthL + 260`): ajuste ao conteúdo, mas mantenha a centralização por fórmula.

## Variações

- Resultado de lote: troque a fonte da galeria por `colResultadoLote`.
- Sem tabela: dois ou três `Label`s com `fxColorTextBody`.

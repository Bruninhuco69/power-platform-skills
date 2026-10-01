# Molde: tela YAML completa e colável

Uma tela de listagem com ação de gravação, na ordem certa: cabeçalho, filtro, cabeçalho de
coluna, galeria com estado vazio e aviso de teto, painel de "sem acesso", modal de confirmação,
overlay de loading e toast. Todo valor visual vem de token `fx*`
([app-formulas-tokens.md](app-formulas-tokens.md)); todo estado, de variável nascida no
`OnStart` ([app-onstart-molde.md](app-onstart-molde.md)).

Origem: blocos canônicos de UX de apps de referência, reescritos para o
dialeto do YAML e sem as propriedades que o Studio recusa (PA2108).
Detalhe de cada bloco em [ux-componentes.md](../references/ux-componentes.md).

## Sumário

1. [Antes de colar](#antes-de-colar)
2. [Como colar](#como-colar)
3. [O que trocar](#o-que-trocar)
4. [Cabeçalho de delegação](#cabeçalho-de-delegação)
5. [A tela](#a-tela)
6. [Depois de colar](#depois-de-colar)

## Antes de colar

1. Os tokens do bloco `Formulas` já estão no objeto App.
2. As variáveis globais abaixo já nascem no `OnStart` (valor inicial neutro):
   `varTelaAtiva`, `varUnidadeFiltro`, `varSemAcesso`, `varPerfil`, `varPedidoTotal`,
   `varPedidoSel`, `varMostrarConfirmar`, `varShowLoading`, `varLoadingMessage`,
   `varShowToast`, `varToastType`, `varToastMessage`, `varRet`.
3. A fonte de dados `Pedido` (tabela de exemplo) e o flow `app-flow-pedido-acao` estão
   adicionados ao app. Colunas usadas: `Id_Pedido`, `Codigo`, `Descricao`, `Status`, `Unidade`,
   `Dt_Inclusao`. **Nome de coluna vem do ambiente real** (`NOMES-AS-BUILT`, skill `dataverse`),
   nunca do dicionário de dados.

## Como colar

Destino: **YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal)**. Duas vias,
ambas sem `;;`:

- **Arquivo `.pa.yaml`** (Git Integration ou `pac canvas`): o bloco inteiro, com `Screens:`.
- **Code view**: botão direito na tela > **Paste code**, com o conteúdo de `Children:`
  (a partir de `- xx-con-conteudo:`). Colar **cria** controles novos; não substitui.

Antes de colar, troque o prefixo `xx` pelo prefixo da tela: nomes de controle são únicos no app
inteiro, e o Studio renomeia duplicado para `_1`, que quebra a convenção.

## O que trocar

| No molde | Troque por |
|---|---|
| `xx-` | prefixo de 2 letras da tela (`pd-`) |
| `Pedidos` (nome da tela) e `"Pedidos"` (título) | nome da tela |
| `Pedido`, `Id_Pedido`, `Codigo`, `Descricao`, `Status`, `Unidade`, `Dt_Inclusao` | fonte e colunas reais |
| `'app-flow-pedido-acao'` | nome do flow no app; parâmetros posicionais, todos texto |
| `varPerfil.Flg_Encerrar` | flag do perfil que autoriza a ação (nunca nome de perfil) |
| `"aberto"`, `"encerrado"` e as cores do `Switch` | vocabulário do domínio e token `fxBadge*` |
| `fxTxtEncerrar`, título e mensagem do modal | verbo e texto da ação (crie `fxTxt<Acao>`) |

## Cabeçalho de delegação

Cada tela declara por escrito, em comentário no topo do arquivo `.pa.yaml`, o que delega, o que
não delega e o teto (decisão T7 em
[decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md)). Para este molde,
com fonte SQL:

- `Filter` com `StartsWith` em duas colunas de texto e `Sort` por data: **delega**.
- `CountRows(Filter(...))` no `OnVisible` e no modal: **não delega**; o contador mostra
  `fxTxtTeto` ao bater em `fxLimiteLinhas`. O validador acusa T013 nesses dois pontos de
  propósito, e só com `trilha_dados: sql-server`.
- `AllItemsCount` no estado vazio: local, sem custo de rede.

## A tela

Destino: YAML colado no Studio (`,` e `;`).

```yaml
Screens:
  Pedidos:
    Properties:
      Fill: =fxColorBackground
      Height: =1080
      LoadingSpinnerColor: =fxColorPrimary
      OnVisible: |-
        =Set(varTelaAtiva, "pedidos");
        Set(varMostrarConfirmar, false);
        Set(varPedidoSel, Blank());
        Set(varShowLoading, false);
        Set(varLoadingMessage, "");
        Set(varShowToast, false);
        Set(
          varPedidoTotal,
          CountRows(Filter(Pedido, StartsWith(Unidade, varUnidadeFiltro)))
        )
      Width: =1920
    Children:
      - xx-con-conteudo:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorTransparent
            Fill: =fxColorTransparent
            Height: =Parent.Height
            Visible: =!varSemAcesso
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
                  Text: ="Pedidos"
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =600
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
                  X: =Parent.Width - 420
                  Y: =30
            - xx-rec-header-divisor:
                Control: Rectangle@2.3.0
                Properties:
                  BorderStyle: =BorderStyle.None
                  Fill: =fxColorDivider
                  Height: =1
                  Width: =Parent.Width - fxLayoutMargin * 2
                  X: =fxLayoutMargin
                  Y: =84
            - xx-txt-filtro-busca:
                Control: Classic/TextInput@2.3.2
                Properties:
                  BorderColor: =fxColorBorderInteractive
                  Color: =fxColorTextPrimary
                  Default: =""
                  DelayOutput: =true
                  FocusedBorderColor: =fxColorPrimary
                  Font: =fxFont
                  Height: =fxFilterHeight
                  HintText: ="Buscar por código"
                  Size: =fxFontSizeFilter
                  TabIndex: =0
                  Width: =280
                  X: =fxLayoutMargin
                  Y: =110
            - xx-btn-filtro-limpar:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =Self.Fill
                  BorderThickness: =1
                  Color: =fxColorTextOnPrimary
                  Fill: =fxColorButtonCancel
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxFilterHeight
                  HoverBorderColor: =fxColorButtonCancelHover
                  HoverColor: =fxColorTextOnPrimary
                  HoverFill: =fxColorButtonCancelHover
                  OnSelect: |-
                    =Reset('xx-txt-filtro-busca')
                  PressedBorderColor: =fxColorButtonCancelHover
                  PressedColor: =fxColorTextOnPrimary
                  PressedFill: =fxColorButtonCancelHover
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxFontSizeFilter
                  TabIndex: =0
                  Text: =fxTxtLimpar
                  Width: =fxBtnWidthFilter
                  X: =fxLayoutMargin + 280 + fxLayoutGutter
                  Y: =110
            - xx-lbl-total:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Right
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =28
                  Size: =fxFontSizeFilter
                  Text: |-
                    =If(
                      varPedidoTotal >= fxLimiteLinhas,
                      "Total: " & fxTxtTeto,
                      "Total: " & Text(varPedidoTotal)
                    )
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =280
                  X: =Parent.Width - fxLayoutMargin - 280
                  Y: =120
            - xx-hdr-gal-codigo:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Código"
                  Width: =160
                  X: =fxLayoutMargin
                  Y: =196
            - xx-hdr-gal-descricao:
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
                  Width: =640
                  X: =fxLayoutMargin + 160
                  Y: =196
            - xx-hdr-gal-status:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Status"
                  Width: =160
                  X: =fxLayoutMargin + 800
                  Y: =196
            - xx-hdr-gal-data:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Inclusão"
                  Width: =160
                  X: =fxLayoutMargin + 960
                  Y: =196
            - xx-hdr-gal-acoes:
                Control: Classic/Button@2.2.0
                Properties:
                  Color: =fxColorTableHeaderText
                  DisplayMode: =DisplayMode.View
                  Fill: =fxColorTableHeaderBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxTableHeaderHeight
                  Size: =fxFontSizeHeader
                  Text: ="Ações"
                  Width: =160
                  X: =fxLayoutMargin + 1120
                  Y: =196
            - xx-gal-pedidos:
                Control: Gallery@2.15.0
                Variant: BrowseLayout_Flexible_SocialFeed_ver5.0
                Properties:
                  BorderColor: =fxColorBorder
                  BorderThickness: =1
                  Height: =fxRowHeight * 12
                  Items: |-
                    =Sort(
                      Filter(
                        Pedido,
                        StartsWith(Unidade, varUnidadeFiltro),
                        StartsWith(Codigo, 'xx-txt-filtro-busca'.Text)
                      ),
                      Dt_Inclusao,
                      SortOrder.Descending
                    )
                  TemplatePadding: =0
                  TemplateSize: =Max(20, fxRowHeight)
                  Width: =1280
                  X: =fxLayoutMargin
                  Y: =196 + fxTableHeaderHeight
                Children:
                  - xx-btn-gal-fundo-linha:
                      Control: Classic/Button@2.2.0
                      Properties:
                        BorderColor: =fxColorDivider
                        Color: =fxColorTransparent
                        Fill: =If(varPedidoSel.Id_Pedido = ThisItem.Id_Pedido, fxColorPrimaryLight, fxColorSurface)
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        HoverFill: =fxColorPrimaryLight
                        OnSelect: =Set(varPedidoSel, ThisItem)
                        PressedFill: =fxColorPrimaryLight
                        TabIndex: =0
                        Text: =""
                        Width: =Parent.TemplateWidth
                        X: =0
                        Y: =0
                  - xx-lbl-gal-codigo:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorPrimary
                        Font: =fxFont
                        FontWeight: =FontWeight.Semibold
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTable
                        Text: =ThisItem.Codigo
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =140
                        X: =16
                        Y: =0
                  - xx-lbl-gal-descricao:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorTextBody
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTable
                        Text: =ThisItem.Descricao
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =630
                        X: =160
                        Y: =0
                  - xx-lbl-gal-status:
                      Control: Label@2.5.1
                      Properties:
                        Align: =Align.Center
                        Color: |-
                          =Switch(
                            ThisItem.Status,
                            "aberto", fxBadgeInfoText,
                            "encerrado", fxBadgeSuccessText,
                            fxBadgeNeutralText
                          )
                        Fill: |-
                          =Switch(
                            ThisItem.Status,
                            "aberto", fxBadgeInfoBg,
                            "encerrado", fxBadgeSuccessBg,
                            fxBadgeNeutralBg
                          )
                        Font: =fxFont
                        FontWeight: =FontWeight.Semibold
                        Height: =24
                        Size: =fxFontSizeTableSmall
                        Text: =ThisItem.Status
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =140
                        X: =800
                        Y: =(Parent.TemplateHeight - Self.Height) / 2
                  - xx-lbl-gal-data:
                      Control: Label@2.5.1
                      Properties:
                        Align: =Align.Center
                        Color: =fxColorTextPrimary
                        Font: =fxFont
                        Height: =Parent.TemplateHeight
                        Size: =fxFontSizeTableSmall
                        Text: =Text(ThisItem.Dt_Inclusao, "[$-pt-BR]dd/mm/yyyy")
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =150
                        X: =960
                        Y: =0
                  - xx-btn-gal-encerrar:
                      Control: Classic/Button@2.2.0
                      Properties:
                        BorderColor: =Self.Fill
                        BorderThickness: =1
                        Color: =fxColorTextOnPrimary
                        DisabledBorderColor: =fxColorDisabled
                        DisabledColor: =fxColorDisabledText
                        DisabledFill: =fxColorDisabled
                        DisplayMode: =If(varShowLoading || ThisItem.Status = "encerrado", DisplayMode.Disabled, DisplayMode.Edit)
                        Fill: =fxColorPrimary
                        Font: =fxFont
                        FontWeight: =FontWeight.Semibold
                        Height: =34
                        HoverBorderColor: =ColorFade(Self.Fill, -20%)
                        HoverColor: =fxColorTextOnPrimary
                        HoverFill: =ColorFade(Self.Fill, -20%)
                        OnSelect: |-
                          =Set(varPedidoSel, ThisItem);
                          Set(varMostrarConfirmar, true)
                        PressedBorderColor: =ColorFade(Self.Fill, -30%)
                        PressedColor: =fxColorTextOnPrimary
                        PressedFill: =ColorFade(Self.Fill, -30%)
                        RadiusBottomLeft: =fxBtnRadius
                        RadiusBottomRight: =fxBtnRadius
                        RadiusTopLeft: =fxBtnRadius
                        RadiusTopRight: =fxBtnRadius
                        Size: =fxFontSizeTableSmall
                        TabIndex: =0
                        Text: =fxTxtEncerrar
                        Visible: =varPerfil.Flg_Encerrar
                        Width: =120
                        X: =1120
                        Y: =(Parent.TemplateHeight - Self.Height) / 2
            - xx-lbl-gal-vazio:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  Height: =120
                  Size: =fxFontSizeBody
                  Text: =fxMsgNoResultsError & Char(10) & fxMsgNoResultsHint
                  VerticalAlign: =VerticalAlign.Middle
                  Visible: ='xx-gal-pedidos'.Visible && 'xx-gal-pedidos'.AllItemsCount = 0
                  Width: ='xx-gal-pedidos'.Width
                  X: ='xx-gal-pedidos'.X
                  Y: ='xx-gal-pedidos'.Y + 80
            - xx-lbl-gal-truncado:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxBadgeWarningText
                  Fill: =fxBadgeWarningBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =28
                  Size: =fxFontSizeFilter
                  Text: =fxMsgListaTruncada
                  VerticalAlign: =VerticalAlign.Middle
                  Visible: =varPedidoTotal >= fxLimiteLinhas
                  Width: ='xx-gal-pedidos'.Width
                  X: ='xx-gal-pedidos'.X
                  Y: ='xx-gal-pedidos'.Y + 'xx-gal-pedidos'.Height + 8
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
      - xx-mod-confirmar:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorTransparent
            Fill: =fxColorOverlayDark
            Height: =1080
            Visible: =varMostrarConfirmar
            Width: =1920
          Children:
            - xx-mod-confirmar-card:
                Control: GroupContainer@1.5.0
                Variant: ManualLayout
                Properties:
                  BorderColor: =fxColorBorder
                  DropShadow: =DropShadow.Bold
                  Fill: =fxColorSurface
                  Height: =240
                  RadiusBottomLeft: =fxModalRadius
                  RadiusBottomRight: =fxModalRadius
                  RadiusTopLeft: =fxModalRadius
                  RadiusTopRight: =fxModalRadius
                  Width: =520
                  X: =(Parent.Width - Self.Width) / 2
                  Y: =(Parent.Height - Self.Height) / 2
                Children:
                  - xx-mod-confirmar-titulo:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorPrimaryDark
                        Font: =fxFont
                        FontWeight: =FontWeight.Bold
                        Height: =32
                        Size: =fxModalTitleSize
                        Text: ="Encerrar o pedido"
                        Width: =Parent.Width - fxModalPadding * 2
                        X: =fxModalPadding
                        Y: =fxModalPadding
                  - xx-mod-confirmar-mensagem:
                      Control: Label@2.5.1
                      Properties:
                        Color: =fxColorTextBody
                        Font: =fxFont
                        Height: =80
                        Size: =fxFontSizeBody
                        Text: ="Confirma o encerramento do pedido " & varPedidoSel.Codigo & "?"
                        Width: =Parent.Width - fxModalPadding * 2
                        X: =fxModalPadding
                        Y: =70
                  - xx-mod-confirmar-btn-voltar:
                      Control: Classic/Button@2.2.0
                      Properties:
                        BorderColor: =Self.Fill
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
                          =Set(varMostrarConfirmar, false)
                        PressedBorderColor: =fxColorButtonCancelHover
                        PressedColor: =fxColorTextOnPrimary
                        PressedFill: =fxColorButtonCancelHover
                        RadiusBottomLeft: =fxBtnRadius
                        RadiusBottomRight: =fxBtnRadius
                        RadiusTopLeft: =fxBtnRadius
                        RadiusTopRight: =fxBtnRadius
                        Size: =fxBtnFontSize
                        TabIndex: =0
                        Text: =fxTxtVoltar
                        Width: =(Parent.Width - fxModalPadding * 3) / 2
                        X: =fxModalPadding
                        Y: =Parent.Height - Self.Height - fxModalPadding
                  - xx-mod-confirmar-btn-confirmar:
                      Control: Classic/Button@2.2.0
                      Properties:
                        BorderColor: =Self.Fill
                        BorderThickness: =1
                        Color: =fxColorTextOnPrimary
                        DisabledBorderColor: =fxColorDisabled
                        DisabledColor: =fxColorDisabledText
                        DisabledFill: =fxColorDisabled
                        DisplayMode: =If(varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
                        Fill: =fxColorPrimary
                        Font: =fxFont
                        FontWeight: =FontWeight.Semibold
                        Height: =fxBtnHeight
                        HoverBorderColor: =ColorFade(Self.Fill, -20%)
                        HoverColor: =fxColorTextOnPrimary
                        HoverFill: =ColorFade(Self.Fill, -20%)
                        OnSelect: |-
                          =Set(varShowLoading, true);
                          Set(varLoadingMessage, "Encerrando...");
                          IfError(
                            Set(
                              varRet,
                              'app-flow-pedido-acao'.Run(
                                "encerrar",
                                Text(varPedidoSel.Id_Pedido, "[$-en-US]0")
                              )
                            ),
                            Trace("Falha de transporte no flow: " & FirstError.Message);
                            Set(varRet, Blank())
                          );
                          Set(varShowLoading, false);
                          Set(varToastType, Coalesce(varRet.status, "error"));
                          Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
                          Set(varShowToast, true);
                          If(
                            varToastType <> "error",
                            Set(varMostrarConfirmar, false);
                            Set(varPedidoSel, Blank());
                            Refresh(Pedido);
                            Set(
                              varPedidoTotal,
                              CountRows(Filter(Pedido, StartsWith(Unidade, varUnidadeFiltro)))
                            )
                          )
                        PressedBorderColor: =ColorFade(Self.Fill, -30%)
                        PressedColor: =fxColorTextOnPrimary
                        PressedFill: =ColorFade(Self.Fill, -30%)
                        RadiusBottomLeft: =fxBtnRadius
                        RadiusBottomRight: =fxBtnRadius
                        RadiusTopLeft: =fxBtnRadius
                        RadiusTopRight: =fxBtnRadius
                        Size: =fxBtnFontSize
                        TabIndex: =0
                        Text: =If(varShowLoading, fxTxtProcessando, fxTxtEncerrar)
                        Width: =(Parent.Width - fxModalPadding * 3) / 2
                        X: =Parent.Width - Self.Width - fxModalPadding
                        Y: =Parent.Height - Self.Height - fxModalPadding
      - xx-cmp-loading:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorTransparent
            Fill: =fxColorOverlay
            Height: =1080
            Visible: =varShowLoading
            Width: =1920
          Children:
            - xx-con-loading-card:
                Control: GroupContainer@1.5.0
                Variant: ManualLayout
                Properties:
                  BorderColor: =fxColorBorder
                  DropShadow: =DropShadow.Bold
                  Fill: =fxColorSurface
                  Height: =fxLoadingCardHeight
                  RadiusBottomLeft: =fxModalRadius
                  RadiusBottomRight: =fxModalRadius
                  RadiusTopLeft: =fxModalRadius
                  RadiusTopRight: =fxModalRadius
                  Width: =fxLoadingCardWidth
                  X: =(Parent.Width - Self.Width) / 2
                  Y: =(Parent.Height - Self.Height) / 2
                Children:
                  - xx-spn-loading:
                      Control: Spinner@1.4.6
                      Properties:
                        Height: =fxLoadingSpinnerSize
                        Width: =fxLoadingSpinnerSize
                        X: =(Parent.Width - Self.Width) / 2
                        Y: =20
                  - xx-lbl-loading-texto:
                      Control: Label@2.5.1
                      Properties:
                        Align: =Align.Center
                        Color: =fxColorPrimary
                        Font: =fxFont
                        FontWeight: =FontWeight.Semibold
                        Size: =fxFontSizeBody
                        Text: =Coalesce(varLoadingMessage, fxMsgLoadingDefault)
                        Width: =Parent.Width - 20
                        X: =10
                        Y: =90
      - xx-cmp-toast:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorTransparent
            DropShadow: =DropShadow.Bold
            Fill: =fxColorToastBg
            Height: =Max(80, 'xx-lbl-toast-mensagem'.Height + 50)
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Visible: =varShowToast
            Width: =fxToastWidth
            X: =Parent.Width - Self.Width - 20
            Y: =20
          Children:
            - xx-shp-toast-acento:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =fxColorTransparent
                  DisabledBorderColor: =fxColorTransparent
                  DisabledFill: |-
                    =Switch(
                      varToastType,
                      "success", fxColorSuccess,
                      "warning", fxColorWarning,
                      fxColorError
                    )
                  DisplayMode: =DisplayMode.Disabled
                  Fill: |-
                    =Switch(
                      varToastType,
                      "success", fxColorSuccess,
                      "warning", fxColorWarning,
                      fxColorError
                    )
                  Height: =Parent.Height
                  RadiusBottomLeft: =fxModalRadius
                  RadiusBottomRight: =0
                  RadiusTopLeft: =fxModalRadius
                  RadiusTopRight: =0
                  Text: =""
                  Width: =5
                  X: =0
                  Y: =0
            - xx-shp-toast-icone-fundo:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =fxColorTransparent
                  DisabledBorderColor: =fxColorTransparent
                  DisabledFill: |-
                    =Switch(
                      varToastType,
                      "success", ColorFade(fxColorSuccess, 80%),
                      "warning", ColorFade(fxColorWarning, 80%),
                      ColorFade(fxColorError, 80%)
                    )
                  DisplayMode: =DisplayMode.Disabled
                  Fill: |-
                    =Switch(
                      varToastType,
                      "success", ColorFade(fxColorSuccess, 80%),
                      "warning", ColorFade(fxColorWarning, 80%),
                      ColorFade(fxColorError, 80%)
                    )
                  Height: =40
                  RadiusBottomLeft: =20
                  RadiusBottomRight: =20
                  RadiusTopLeft: =20
                  RadiusTopRight: =20
                  Text: =""
                  Width: =40
                  X: =18
                  Y: =20
            - xx-lbl-toast-icone:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextOnPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =40
                  Size: =fxFontSizeToastIcon
                  Text: =Switch(varToastType, "success", "✓", "warning", "!", "✕")
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =40
                  X: =18
                  Y: =20
            - xx-lbl-toast-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextOnPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =28
                  Size: =fxFontSizeToastTitle
                  Text: |-
                    =Switch(
                      varToastType,
                      "success", fxTxtToastSuccess,
                      "warning", fxTxtToastWarning,
                      fxTxtToastError
                    )
                  VerticalAlign: =VerticalAlign.Bottom
                  Width: =290
                  X: =70
                  Y: =10
            - xx-lbl-toast-mensagem:
                Control: Label@2.5.1
                Properties:
                  AutoHeight: =true
                  Color: =fxColorToastText
                  Font: =fxFont
                  Height: =28
                  Size: =fxFontSizeToast
                  Text: =varToastMessage
                  VerticalAlign: =VerticalAlign.Top
                  Width: =290
                  X: =70
                  Y: =38
            - xx-btn-toast-fechar:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =fxColorTransparent
                  BorderThickness: =1
                  Color: =fxColorToastText
                  Fill: =fxColorTransparent
                  Font: =fxFont
                  FontWeight: =FontWeight.Normal
                  Height: =30
                  HoverBorderColor: =fxColorToastBg
                  HoverColor: =fxColorTextOnPrimary
                  HoverFill: =fxColorToastBg
                  OnSelect: |-
                    =Set(varShowToast, false)
                  PressedBorderColor: =fxColorToastBg
                  PressedColor: =fxColorTextOnPrimary
                  PressedFill: =fxColorToastBg
                  RadiusBottomLeft: =15
                  RadiusBottomRight: =15
                  RadiusTopLeft: =15
                  RadiusTopRight: =15
                  Size: =fxFontSizeBody
                  TabIndex: =0
                  Text: ="✕"
                  Tooltip: ="Fechar notificação"
                  Width: =30
                  X: =Parent.Width - Self.Width - 10
                  Y: =8
            - xx-shp-toast-progresso-barra:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =fxColorTransparent
                  DisabledBorderColor: =fxColorTransparent
                  DisabledFill: |-
                    =Switch(
                      varToastType,
                      "success", fxColorSuccess,
                      "warning", fxColorWarning,
                      fxColorError
                    )
                  DisplayMode: =DisplayMode.Disabled
                  Fill: |-
                    =Switch(
                      varToastType,
                      "success", fxColorSuccess,
                      "warning", fxColorWarning,
                      fxColorError
                    )
                  Height: =3
                  RadiusBottomLeft: =fxModalRadius
                  RadiusBottomRight: =0
                  RadiusTopLeft: =0
                  RadiusTopRight: =0
                  Text: =""
                  Width: =Parent.Width * (1 - 'xx-tim-toast'.Value / Max('xx-tim-toast'.Duration, 1))
                  X: =0
                  Y: =Parent.Height - 3
            - xx-tim-toast:
                Control: Timer@2.1.0
                Properties:
                  Duration: |-
                    =If(
                      varToastType = "error", fxToastDurationError,
                      varToastType = "warning", fxToastDurationLong,
                      Len(varToastMessage) > 100, fxToastDurationLong,
                      fxToastDurationShort
                    )
                  OnTimerEnd: =Set(varShowToast, false)
                  Repeat: =false
                  Reset: =!varShowToast
                  Start: =varShowToast
                  Visible: =false
```

## Depois de colar

1. Rode `python <pasta-da-skill>/scripts/validar-telas.py <arquivo>` (esperado: 0 erros) **e cole no Studio**:
   o validador não é o portão, o Studio é. `PA2108` no Studio = propriedade recusada; anote em
   [propriedades-inexistentes.md](../references/propriedades-inexistentes.md).
2. **Settings > General > Data row limit = 1** num clone: a galeria precisa continuar listando
   (se esvaziar, algum predicado não delegou). Volte ao valor normal depois.
3. Abra o Monitor: uma consulta por abertura de tela, nenhuma por linha da galeria.
4. Dispare a ação com o flow desligado: toast vermelho com `fxMsgFalhaFlow` e overlay fechado.
   Teste também sucesso e aviso (`warning`) do flow.
5. Abra com um usuário sem perfil: só o painel de "sem acesso" aparece (fail-closed).
6. Timers só rodam em Preview (`F5`) `[verificado: Learn, control-timer]`. A barra de progresso
   do toast depende de `Timer.Value` recalcular com o timer invisível `[não verificado]`; se não
   animar, troque a `Width` da barra por `=Parent.Width`.

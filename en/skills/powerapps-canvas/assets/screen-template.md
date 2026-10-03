# Template: complete, pasteable YAML screen

A list screen with a write action, in the right order: header, filter, column header, gallery
with empty state and cap warning, "no access" panel, confirmation modal, loading overlay and
toast. Every visual value comes from an `fx*` token
([app-formulas-tokens.md](app-formulas-tokens.md)); every state comes from a variable created in
`OnStart` ([app-onstart-template.md](app-onstart-template.md)).

Origin: canonical UX blocks from reference apps, rewritten for the YAML dialect and without the
properties Studio rejects (PA2108).
Details of each block in [ux-components.md](../references/ux-components.md).

## Contents

1. [Before pasting](#before-pasting)
2. [How to paste](#how-to-paste)
3. [What to change](#what-to-change)
4. [Delegation header](#delegation-header)
5. [The screen](#the-screen)
6. [After pasting](#after-pasting)

## Before pasting

1. The tokens of the `Formulas` block are already in the App object.
2. The global variables below are already created in `OnStart` (neutral initial value):
   `varTelaAtiva`, `varUnidadeFiltro`, `varSemAcesso`, `varPerfil`, `varPedidoTotal`,
   `varPedidoSel`, `varMostrarConfirmar`, `varShowLoading`, `varLoadingMessage`,
   `varShowToast`, `varToastType`, `varToastMessage`, `varRet`.
3. The `Pedido` data source (sample table, the Order) and the `app-flow-pedido-acao` flow are
   added to the app. Columns used: `Id_Pedido`, `Codigo`, `Descricao`, `Status`, `Unidade`,
   `Dt_Inclusao`. **Column names come from the real environment** (`AS-BUILT-NAMES`, skill
   `dataverse`), never from the data dictionary.

## How to paste

Destination: **YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal)**. Two
ways, both without `;;`:

- **`.pa.yaml` file** (Git Integration or `pac canvas`): the whole block, with `Screens:`.
- **Code view**: right-click the screen > **Paste code**, with the content of `Children:`
  (starting at `- xx-con-conteudo:`). Pasting **creates** new controls; it does not replace.

Before pasting, replace the `xx` prefix with the screen's prefix: control names are unique across
the whole app, and Studio renames a duplicate to `_1`, which breaks the convention.

## What to change

| In the template | Replace with |
|---|---|
| `xx-` | the screen's 2-letter prefix (`pd-`) |
| `Pedidos` (screen name) and `"Orders"` (title) | the screen name |
| `Pedido`, `Id_Pedido`, `Codigo`, `Descricao`, `Status`, `Unidade`, `Dt_Inclusao` | the real source and columns |
| `'app-flow-pedido-acao'` | the flow name in the app; positional parameters, all text |
| `varPerfil.Flg_Encerrar` | the role flag that authorizes the action (never a role name) |
| `"Open"`, `"Completed"` and the colors of the `Switch` | the domain vocabulary and the `fxBadge*` token |
| `fxTxtEncerrar`, modal title and message | the action's verb and text (create `fxTxt<Action>`) |

## Delegation header

Each screen declares in writing, in a comment at the top of the `.pa.yaml` file, what it
delegates, what it does not and the cap (decision T7 in
[default-decisions.md](../../power-platform/references/default-decisions.md)). For this template,
with a SQL source:

- `Filter` with `StartsWith` on two text columns and `Sort` by date: **delegates**.
- `CountRows(Filter(...))` in `OnVisible` and in the modal: **does not delegate**; the counter
  shows `fxTxtTeto` when it reaches `fxLimiteLinhas`. The validator reports T013 at those two
  points on purpose, and only with `trilha_dados: sql-server`.
- `AllItemsCount` in the empty state: local, no network cost.

## The screen

Destination: YAML pasted into Studio (`,` and `;`).

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
                  Text: ="Orders"
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
                  HintText: ="Search by code"
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
                  Text: ="Code"
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
                  Text: ="Description"
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
                  Text: ="Created"
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
                  Text: ="Actions"
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
                            "Open", fxBadgeInfoText,
                            "Completed", fxBadgeSuccessText,
                            fxBadgeNeutralText
                          )
                        Fill: |-
                          =Switch(
                            ThisItem.Status,
                            "Open", fxBadgeInfoBg,
                            "Completed", fxBadgeSuccessBg,
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
                        Text: =Text(ThisItem.Dt_Inclusao, "[$-en-US]mm/dd/yyyy")
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
                        DisplayMode: =If(varShowLoading || ThisItem.Status = "Completed", DisplayMode.Disabled, DisplayMode.Edit)
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
                        Text: ="Complete the order"
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
                        Text: ="Confirm completing order " & varPedidoSel.Codigo & "?"
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
                          Set(varLoadingMessage, "Completing...");
                          IfError(
                            Set(
                              varRet,
                              'app-flow-pedido-acao'.Run(
                                "encerrar",
                                Text(varPedidoSel.Id_Pedido, "[$-en-US]0")
                              )
                            ),
                            Trace("Flow transport failure: " & FirstError.Message);
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
                  Tooltip: ="Close notification"
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

## After pasting

1. Run `python <skill-folder>/scripts/validar-telas.py <file>` (expected: 0 errors) **and paste into
   Studio**: the validator is not the gate, Studio is. `PA2108` in Studio = rejected property; note
   it in [nonexistent-properties.md](../references/nonexistent-properties.md).
2. **Settings > General > Data row limit = 1** on a clone: the gallery must keep listing
   (if it goes empty, some predicate did not delegate). Restore the normal value afterwards.
3. Open the Monitor: one query per screen open, none per gallery row.
4. Trigger the action with the flow turned off: red toast with `fxMsgFalhaFlow` and overlay
   closed. Also test success and warning (`warning`) from the flow.
5. Open with a user without a role: only the "no access" panel shows (fail-closed).
6. Timers only run in Preview (`F5`) `[verified: Learn, control-timer]`. The toast progress bar
   depends on `Timer.Value` recalculating with the invisible timer `[unverified]`; if it does
   not animate, replace the bar's `Width` with `=Parent.Width`.

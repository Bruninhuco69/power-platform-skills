# Feedback de operação: modal, loading e toast

Continuação de [ux-componentes.md](ux-componentes.md). Mesmas regras comuns (dialeto do YAML
colado, sem PA2108, tokens `fx*`). Contrato de estado: `varMostrar<Acao>`, `varShowLoading`,
`varLoadingMessage`, `varShowToast`, `varToastType`, `varToastMessage`.

## Sumário

1. [Modal](#9-modal)
2. [Loading](#10-loading)
3. [Toast](#11-toast)

## 9. Modal

Véu + card, centralizados por fórmula, par de botões dimensionado por fórmula. O modal completo
com chamada de flow está em [tela-molde.md](../assets/tela-molde.md). Decisões:

- **Véu** `fxColorOverlayDark`; card com `fxModalRadius`, `fxModalPadding` e título
  `fxModalTitleSize` em negrito (`fxColorPrimaryDark`, ou `fxColorError` se destrutivo).
- **Par de botões**: esquerdo `fxTxtVoltar` cinza; direito = **verbo da ação** (`Confirmar encerramento`,
  `Salvar alterações`), nunca `Confirmar`/`Sim` genérico em ação destrutiva. Sem emoji.
- O modal **limpa o estado** ao fechar (variável da mensagem, seleção): sem isso a próxima
  abertura mostra dado velho. `Visible` de **uma só** variável (`varMostrar<Acao>`); `And` de
  várias flags torna impossível descobrir por que não abre.
- `GroupContainer` não é clicável: o véu **não bloqueia clique** nos controles de baixo. Para
  bloquear de fato, um `Classic/Button` transparente de 1920 por 1080 como **primeiro** filho do
  véu, com `OnSelect: =false`.
- **Limitação oficial de acessibilidade**: diálogo e overlay não são suportados; a Microsoft
  recomenda tela separada ou `Notify()`. O padrão do kit é o modal; a mitigação é botão
  `Voltar` sempre presente e foco na ordem de tabulação ([acessibilidade.md](acessibilidade.md)).
- Tamanho do card por token (`fxModalWidthS`, `fxModalWidthM`, `fxModalWidthL`; ver o catálogo em
  [INDICE.md](../assets/componentes/INDICE.md)); padronizam-se também raio, cores, centralização e o
  par de botões. Em ManualLayout o conteúdo é posicionado em `X`/`Y` absoluto.

Variação **destrutiva** (cancelamento com motivo obrigatório, `fxColorError` no título e no botão):

```yaml
- xx-mod-cancelar:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlayDark
      Height: =1080
      Visible: =varMostrarCancelar
      Width: =1920
    Children:
      - xx-mod-cancelar-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =300
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =520
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-mod-cancelar-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorError
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =32
                  Size: =fxModalTitleSize
                  Text: ="Cancelar o pedido"
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =fxModalPadding
            - xx-mod-cancelar-aviso:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorError
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =24
                  Size: =fxFontSizeFilter
                  Text: ="Esta ação não pode ser desfeita."
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =62
            - xx-txt-motivo:
                Control: Classic/TextInput@2.3.2
                Properties:
                  BorderColor: =fxColorBorderInteractive
                  Color: =fxColorTextPrimary
                  Default: =""
                  FocusedBorderColor: =fxColorPrimary
                  Font: =fxFont
                  Height: =100
                  HintText: ="Motivo (mínimo 5 caracteres)"
                  Mode: =TextMode.MultiLine
                  Size: =fxFontSizeFilter
                  TabIndex: =0
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =100
            - xx-mod-cancelar-btn-voltar:
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
                    =Set(varMostrarCancelar, false)
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
            - xx-mod-cancelar-btn-confirmar:
                Control: Classic/Button@2.2.0
                Properties:
                  BorderColor: =Self.Fill
                  BorderThickness: =1
                  Color: =fxColorTextOnPrimary
                  DisabledBorderColor: =fxColorDisabled
                  DisabledColor: =fxColorDisabledText
                  DisabledFill: =fxColorDisabled
                  DisplayMode: |-
                    =If(
                      varShowLoading || Len(Trim('xx-txt-motivo'.Text)) < 5,
                      DisplayMode.Disabled,
                      DisplayMode.Edit
                    )
                  Fill: =fxColorError
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxBtnHeight
                  HoverBorderColor: =ColorFade(Self.Fill, -20%)
                  HoverColor: =fxColorTextOnPrimary
                  HoverFill: =ColorFade(Self.Fill, -20%)
                  OnSelect: |-
                    =Set(varMostrarCancelar, false)
                  PressedBorderColor: =ColorFade(Self.Fill, -30%)
                  PressedColor: =fxColorTextOnPrimary
                  PressedFill: =ColorFade(Self.Fill, -30%)
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxBtnFontSize
                  TabIndex: =0
                  Text: =If(varShowLoading, fxTxtProcessando, "Confirmar cancelamento")
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =Parent.Width - Self.Width - fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
```

Variação informativa (botão único centralizado):

```yaml
- xx-mod-info-btn-fechar:
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
        =Set(varMostrarInfo, false)
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
      X: =(Parent.Width - Self.Width) / 2
      Y: =Parent.Height - Self.Height - fxModalPadding
```

## 10. Loading

Overlay com card e spinner; contrato `varShowLoading` e `varLoadingMessage` (cai em
`fxMsgLoadingDefault` quando vazio). Penúltimo em `Children`, antes do toast. Complementos
nativos na galeria: `LoadingSpinnerColor` na **tela** e, na galeria, os de carga (`[não
verificado]`: `DelayItemLoading` e `LoadingSpinner` na `Gallery@2.15.0`; teste num bloco pequeno).

```yaml
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
```

## 11. Toast

Retorno de flow, igual em ação singular e em lote. Três tipos (`success` verde, `warning` âmbar,
`error` vermelho), duração por severidade (6, 12 e 15 s), barra de progresso e `✕` com
`Tooltip`. O timer precisa de `Reset: =!varShowToast` (ver [timers-async.md](timers-async.md) §4).
Último filho da tela. A barra de progresso depende de `Timer.Value` `[não verificado]`.

Preenchimento (ação singular e lote usam o mesmo contrato):

- singular: `Set(varToastType, Coalesce(varRet.status, "error"))` e a descrição do flow;
- lote: o **flow** agrega e devolve `warning` com a contagem; a tela só exibe.

```yaml
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
            Size: =18
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
            Size: =15
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
            Size: =12
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
            Size: =14
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


# Toast de retorno de flow

Maturidade: **estável** · Frequência: **muito comum**.

## Propósito

Notificação não bloqueante no canto superior direito: tipo (`success`, `warning`, `error`) por cor de acento, ícone e título, mensagem pronta vinda do flow, fechar manual e barra de progresso. Some sozinho; a duração cresce com a gravidade.

## Quando usar / quando não usar

**Use quando**

- retorno de qualquer chamada de flow (a mensagem vem pronta em `description`);
- confirmação de ação sem interromper o fluxo.

**Não use quando**

- validação de campo (mostre no campo);
- erro que exige decisão do usuário (use modal).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-cmp-toast  (GroupContainer)
  xx-shp-toast-acento  (Button)
  xx-shp-toast-icone-fundo  (Button)
  xx-lbl-toast-icone  (Label)
  xx-lbl-toast-titulo  (Label)
  xx-lbl-toast-mensagem  (Label)
  xx-btn-toast-fechar  (Button)
  xx-shp-toast-progresso-fundo  (Button)
  xx-shp-toast-progresso-barra  (Button)
  xx-tim-toast  (Timer)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorToastBg`, `fxModalRadius`, `fxToastWidth`, `fxColorSuccess`, `fxColorWarning`, `fxColorError`, `fxColorTextOnPrimary`, `fxColorTextOnWarning`, `fxFont`, `fxFontSizeToastIcon`, `fxFontSizeToastTitle`, `fxTxtToastSuccess`, `fxTxtToastWarning`, `fxTxtToastError`, `fxColorToastText`, `fxFontSizeToast`, `fxFontSizeBody`, `fxToastDurationError`, `fxToastDurationLong`, `fxToastDurationShort`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxColorToastTrack`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varShowToast`, `varToastType`, `varToastMessage`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

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
            Color: =If(varToastType = "warning", fxColorTextOnWarning, fxColorTextOnPrimary)
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
            OnSelect: =Set(varShowToast, false)
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
      - xx-shp-toast-progresso-fundo:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            DisabledBorderColor: =fxColorTransparent
            DisabledFill: =fxColorToastTrack
            DisplayMode: =DisplayMode.Disabled
            Fill: =fxColorToastTrack
            Height: =3
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =0
            RadiusTopRight: =0
            Text: =""
            Width: =Parent.Width
            X: =0
            Y: =Parent.Height - 3
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

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-cmp-toast` | `xx-cmp-toast` com o prefixo da tela | sai **já prefixado** |
| `varToastType` | `success`, `warning` ou `error` | o `status` do contrato do flow; qualquer outro valor cai em erro |
| `fxTxtToast*`, `fxToastDuration*` | textos e tempos do projeto | erro dura mais que sucesso |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-cmp-toast`.Visible**: uma só variável global

```powerfx
varShowToast
```

**`xx-tim-toast`.Duration**: 6 s para sucesso curto, 12 s para aviso ou mensagem longa, 15 s para erro

```powerfx
If(
  varToastType = "error", fxToastDurationError,
  varToastType = "warning", fxToastDurationLong,
  Len(varToastMessage) > 100, fxToastDurationLong,
  fxToastDurationShort
)
```

**`xx-tim-toast`.Start**: o timer liga e reinicia pela transição de `varShowToast`

```powerfx
varShowToast
```

## Acessibilidade

- Sem `Live` região atestada (`Label@2.5.1` recusa `Live`, PA2108): erro crítico deve ir também a um modal ou à mensagem no campo.
- Botão de fechar com `Tooltip`; erro dura 15 s para dar tempo de ler (WCAG: limite de tempo).
- Texto claro `fxColorToastText` sobre `fxColorToastBg` com contraste de 4,5:1.
- Ícone: glifo branco sobre a cor cheia do tipo; no aviso, glifo escuro (`fxColorTextOnWarning`), porque branco sobre o amarelo não passa de 4,5:1. Não clareie o fundo do ícone com `ColorFade`: perto do branco, o glifo branco some.

## Armadilhas

- O toast é o **último** de `Children` da tela, acima de modal e loading.
- Toda forma arredondada é `Classic/Button` desabilitado: `Rectangle` não tem `Radius*`.
- `Reset: =!varShowToast` re-arma o timer a cada exibição; sem ele o segundo toast não conta de novo.
- Mensagem do flow é a frase pronta (`description`); a tela não monta texto de erro de negócio.

## Variações

- Toast só de texto: remova os controles `*-icone-*` e a barra.
- `Notify()` nativo é melhor para acessibilidade, mas perde o visual: reserve-o a erro técnico não tratado.

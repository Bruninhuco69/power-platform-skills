# Catálogo de componentes de UX

Blocos canônicos de ManualLayout + controles Classic, prontos para colar, com o prefixo `xx` a
trocar pelo da tela. Corrigidos contra os dois erros mais comuns: **dialeto** (todo
YAML aqui usa `,` e `;`, nunca `;;`) e **PA2108** (nenhuma propriedade que o Studio recusa:
ver [propriedades-inexistentes.md](propriedades-inexistentes.md)). Cor, fonte e medida vêm de
token ([design-tokens.md](design-tokens.md), valores em
[app-formulas-tokens.md](../assets/app-formulas-tokens.md)); a tela inteira montada está em
[tela-molde.md](../assets/tela-molde.md).

Cada bloco tem a versão canônica, completa e validada, em [INDICE.md](../assets/componentes/INDICE.md): comece por lá
e use esta referência para a regra e o porquê ([licoes-de-campo.md](licoes-de-campo.md)).

## Sumário

1. [Regras comuns](#1-regras-comuns)
2. [Cabeçalho de tela](#2-cabeçalho-de-tela)
3. [Card de KPI](#3-card-de-kpi)
4. [Abas](#4-abas)
5. [Filtros](#5-filtros)
6. [Galeria com cabeçalho de coluna](#6-galeria-com-cabeçalho-de-coluna)
7. [Badge de ação](#7-badge-de-ação)
8. [Botões](#8-botões)
9. [Modal, loading e toast](ux-feedback.md)
12. [Seleção em lote](#12-seleção-em-lote)
13. [Estados: vazio, truncado, erro, desabilitado](#13-estados-vazio-truncado-erro-desabilitado)
14. [Formulário: obrigatório e erro por campo](#14-formulário-obrigatório-e-erro-por-campo)
15. [Z-order](#15-z-order)

---

## 1. Regras comuns

- **Destino de todo bloco**: YAML colado (Code view > Paste code), `,` entre argumentos, `;`
  encadeia. Renomeie `xx` antes de colar: nome de controle é único no app inteiro.
- **Contrato de estado compartilhado**: `varShowLoading` e `varLoadingMessage` (loading);
  `varShowToast`, `varToastType` (`success`, `warning`, `error`) e `varToastMessage` (toast);
  `varMostrar<Acao>` (um modal). Todas nascem no `OnStart`.
- **Uma única família tipográfica** (`fxFont`), uma paleta, uma geometria de modal:
  mudar o token muda todas as telas.
- **Retângulo com canto arredondado**: `Rectangle` e vários inputs **não têm** `Radius*`. O
  padrão para forma decorativa arredondada é `Classic/Button@2.2.0` com
  `DisplayMode: =DisplayMode.Disabled` e `DisabledFill` (botão desabilitado também não entra na
  ordem de tabulação).
- **Sem emoji como semântica** (`✅ Sim`, `❌ Cancelar`): não escala para leitor de tela e trava
  tradução. Ícone é um controle separado; rótulo é texto. (O `✓`, `!` e `✕` do toast são glifos
  decorativos ao lado do texto, nunca o texto.)
- **Verde é estado, nunca ação**; ação destrutiva é sempre `fxColorError`.
- Antes de usar propriedade nova num tipo de controle, procure-a em controle do **mesmo tipo**
  já usado no app.

## 2. Cabeçalho de tela

Em toda tela, sem exceção; título, usuário e divisor. Variação sem logo ou com logo: troque o
`X` do título por `fxLayoutMargin + <largura do logo>`.

```yaml
- xx-con-header:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorSurface
      Height: =100
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
            Text: ="Título da tela"
            VerticalAlign: =VerticalAlign.Middle
            Width: =700
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
            Width: =Parent.Width
            X: =0
            Y: =99
```

Relógio no cabeçalho: use variável atualizada por timer; **nunca `Now()` direto** (volátil,
reavalia a cada recálculo). Posição do cabeçalho: escolha **uma** (esquerda ou centralizada) por
app; é uma divergência que custa mover a faixa inteira para fechar depois.

## 3. Card de KPI

Régua de contadores logo abaixo do cabeçalho; no máximo 5 ou 6 cards. `X` sempre por fórmula
(`base + (fxKPIWidth + fxLayoutGutter) * n`), nunca digitado. O valor vem de **variável de contador**
(`varPedidoAbertos`, recalculada no `OnVisible` e depois de cada gravação: named formula não lê
`varUnidadeFiltro`), nunca de consulta em propriedade de UI
([performance.md](performance.md) §10). Contagem sobre SQL mostra o teto
([delegacao.md](delegacao.md) §3). Cores do título: par `fxBadge*` da mesma matiz (texto escuro
sobre pastel, contraste conferido).

```yaml
- xx-con-kpi-abertos:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorBorder
      DropShadow: =DropShadow.Regular
      Fill: =fxColorSurface
      Height: =fxKPIHeight
      RadiusBottomLeft: =fxModalRadius
      RadiusBottomRight: =fxModalRadius
      RadiusTopLeft: =fxModalRadius
      RadiusTopRight: =fxModalRadius
      Width: =fxKPIWidth
      X: =fxLayoutMargin + (fxKPIWidth + fxLayoutGutter) * 0
      Y: =110
    Children:
      - xx-lbl-kpi-abertos-titulo:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxBadgeInfoText
            Fill: =fxBadgeInfoBg
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =fxKPITitleHeight
            Size: =fxFontSizeKPITitle
            Text: ="Abertos"
            VerticalAlign: =VerticalAlign.Middle
            Width: =Parent.Width
            X: =0
            Y: =0
      - xx-lbl-kpi-abertos-valor:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorTextPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =fxKPIValueHeight
            Size: =fxFontSizeKPI
            Text: =If(varPedidoAbertos >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoAbertos, "[$-en-US]#,##0"))
            VerticalAlign: =VerticalAlign.Middle
            Width: =Parent.Width
            X: =0
            Y: =fxKPITitleHeight
```

## 4. Abas

Botão + retângulo de traço; aba ativa com fundo `fxColorSurface`, negrito e traço de 3 px. Até
4 conjuntos de dados na mesma tela. **Limitação oficial**: aba feita de botão e retângulo não é
acessível; o único padrão acessível é o controle moderno Tab list
([Accessibility limitations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessible-apps-limitations)).
A decisão do kit (T1) é manter Classic; a migração é item de [acessibilidade.md](acessibilidade.md).
Aba ativa e inativa **não** podem ter o mesmo `Fill`: a diferença só por cor de texto e traço de
3 px é fraca.

```yaml
- xx-btn-tab-abertos:
    Control: Classic/Button@2.2.0
    Properties:
      AutoDisableOnSelect: =false
      BorderThickness: =0
      Color: =If(varXXTab = 1, fxColorPrimary, fxColorTextSecondary)
      Fill: =If(varXXTab = 1, fxColorSurface, fxColorTabInactive)
      Font: =fxFont
      FontWeight: =If(varXXTab = 1, FontWeight.Bold, FontWeight.Semibold)
      Height: =46
      HoverColor: =fxColorPrimary
      HoverFill: =fxColorSurface
      OnSelect: =Set(varXXTab, 1)
      PressedColor: =fxColorPrimary
      PressedFill: =fxColorSurface
      RadiusBottomLeft: =0
      RadiusBottomRight: =0
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxFontSizeFilter
      TabIndex: =0
      Text: ="Abertos (" & varPedidoAbertos & ")"
      Width: =350
      X: =fxLayoutMargin
      Y: =252
- xx-shp-tab-abertos-traco:
    Control: Rectangle@2.3.0
    Properties:
      BorderStyle: =BorderStyle.None
      Fill: =If(varXXTab = 1, fxColorPrimary, fxColorTransparent)
      Height: =3
      Width: =350
      X: =fxLayoutMargin
      Y: =294
- xx-btn-tab-encerrados:
    Control: Classic/Button@2.2.0
    Properties:
      AutoDisableOnSelect: =false
      BorderThickness: =0
      Color: =If(varXXTab = 2, fxColorPrimary, fxColorTextSecondary)
      Fill: =If(varXXTab = 2, fxColorSurface, fxColorTabInactive)
      Font: =fxFont
      FontWeight: =If(varXXTab = 2, FontWeight.Bold, FontWeight.Semibold)
      Height: =46
      HoverColor: =fxColorPrimary
      HoverFill: =fxColorSurface
      OnSelect: =Set(varXXTab, 2)
      PressedColor: =fxColorPrimary
      PressedFill: =fxColorSurface
      RadiusBottomLeft: =0
      RadiusBottomRight: =0
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxFontSizeFilter
      TabIndex: =0
      Text: ="Encerrados (" & varPedidoEncerrados & ")"
      Width: =350
      X: =fxLayoutMargin + 358
      Y: =252
- xx-shp-tab-encerrados-traco:
    Control: Rectangle@2.3.0
    Properties:
      BorderStyle: =BorderStyle.None
      Fill: =If(varXXTab = 2, fxColorPrimary, fxColorTransparent)
      Height: =3
      Width: =350
      X: =fxLayoutMargin + 358
      Y: =294
```

## 5. Filtros

Acima de qualquer galeria com mais de ~50 registros. Quatro regras:

1. **`Filtrar` azul e `Limpar` cinza**, 128 por `fxFilterHeight`; nunca laranja.
2. Borda do input muda de cinza para azul quando há valor (feedback de "filtro ativo" sem ocupar
   espaço).
3. **`Limpar` reescreve a variável de cada filtro**, não só faz `Reset`: `Reset` de
   `DatePicker` não dispara `OnChange`.
4. `DelayOutput: =true` no campo de texto; combo com muitos itens com `IsSearchable`.

A data guarda **inteiro** (`Ref_*`, ver [delegacao.md](delegacao.md) §4), não data.
`FocusedBorderColor` é a única propriedade de foco atestada nos inputs; `Size`, `Radius*` e
`FocusedBorderThickness` **não existem** em `ComboBox` e `DatePicker`.

```yaml
- xx-con-filtros:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorBorder
      BorderThickness: =1
      Fill: =fxColorSurface
      Height: =100
      RadiusBottomLeft: =fxModalRadius
      RadiusBottomRight: =fxModalRadius
      RadiusTopLeft: =fxModalRadius
      RadiusTopRight: =fxModalRadius
      Width: =1280
      X: =fxLayoutMargin
      Y: =120
    Children:
      - xx-cbo-filtro-unidade:
          Control: Classic/ComboBox@2.4.0
          Properties:
            BorderColor: =fxColorBorderInteractive
            ChevronBackground: =fxColorSurface
            ChevronFill: =fxColorTextSecondary
            Color: =fxColorTextPrimary
            DisplayFields: =["Sigla"]
            Fill: =fxColorSurface
            FocusedBorderColor: =fxColorPrimary
            Font: =fxFont
            Height: =fxFilterHeight
            InputTextPlaceholder: ="Unidade"
            IsSearchable: =true
            Items: =colUnidadesEscopo
            OnChange: |-
              =Set(
                varUnidadeFiltro,
                If(
                  IsBlank(Self.Selected),
                  If(varTodasUnidades, "", varUnidadeLotacao),
                  Self.Selected.Sigla
                )
              )
            SearchFields: =["Sigla"]
            SelectMultiple: =false
            SelectionColor: =fxColorPrimary
            SelectionFill: =fxColorPrimaryLight
            TabIndex: =0
            Width: =200
            X: =16
            Y: =25
      - xx-dtp-filtro-de:
          Control: Classic/DatePicker@2.6.0
          Properties:
            BorderColor: =fxColorBorderInteractive
            FocusedBorderColor: =fxColorPrimary
            Font: =fxFont
            Format: =DateTimeFormat.ShortDate
            Height: =fxFilterHeight
            IconBackground: =fxColorSurface
            IconFill: =fxColorPrimary
            InputTextPlaceholder: ="De"
            OnChange: |-
              =Set(
                varPedidoDe,
                If(
                  IsBlank(Self.SelectedDate),
                  Blank(),
                  36524 + DateDiff(Date(2000, 1, 1), Self.SelectedDate, TimeUnit.Days)
                )
              )
            TabIndex: =0
            Width: =180
            X: =232
            Y: =25
      - xx-txt-filtro-busca:
          Control: Classic/TextInput@2.3.2
          Properties:
            BorderColor: =If(IsBlank(Self.Text), fxColorBorderInteractive, fxColorPrimary)
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
            X: =428
            Y: =25
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
              =Reset('xx-cbo-filtro-unidade');
              Reset('xx-dtp-filtro-de');
              Reset('xx-txt-filtro-busca');
              Set(varUnidadeFiltro, If(varTodasUnidades, "", varUnidadeLotacao));
              // Reset de DatePicker nao dispara OnChange: reescreve a variavel igual ao OnVisible
              Set(varPedidoDe, Blank())
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
            X: =724
            Y: =25
```

## 6. Galeria com cabeçalho de coluna

Três camadas: filtros, cabeçalho de colunas (controles fixos **fora** da galeria, alinhados por
`X` e `Width` ao template) e galeria. Cabeçalho é `Classic/Button` com `DisplayMode.View` (não
focável, não clicável), numa paleta só.

- **`TemplateSize: =Max(20, fxRowHeight)`**, nunca 0 e nunca um valor fixo desconectado do
  conteúdo (uma linha de 658 px com conteúdo de 75 px é desperdício de rolagem).
- **Primeiro filho = fundo clicável da linha** (`GroupContainer` não tem `OnSelect`).
- Dentro da galeria use `Parent.TemplateWidth` e `Parent.TemplateHeight`, não `Parent.Width`.
- No máximo 2 níveis de aninhamento; nunca `Patch` na mesma fonte da galeria dentro de `OnChange`
  (loop de patch e recarga).
- `Items` delegável ([delegacao.md](delegacao.md)); empty state por `AllItemsCount`.
- Altura de linha que expande para detalhe inline: `TemplateSize` condicional, não um número
  fixo que quebra o painel.
- Tabela 2D acessível só com o Data Table clássico; galeria com labels não constrói tabela
  semântica para leitor de tela.

```yaml
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
- xx-gal-registros:
    Control: Gallery@2.15.0
    Variant: BrowseLayout_Flexible_SocialFeed_ver5.0
    Properties:
      BorderColor: =fxColorBorder
      Height: =fxRowHeight * 12
      Items: |-
        =Filter(colRegistros, StartsWith(Codigo, 'xx-txt-filtro-busca'.Text))
      TemplatePadding: =0
      TemplateSize: =Max(20, fxRowHeight)
      Width: =800
      X: =fxLayoutMargin
      Y: =196 + fxTableHeaderHeight
    Children:
      - xx-btn-gal-fundo-linha:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorDivider
            Color: =fxColorTransparent
            Fill: =If(varRegistroSel.Id = ThisItem.Id, fxColorPrimaryLight, fxColorSurface)
            Font: =fxFont
            Height: =Parent.TemplateHeight
            HoverFill: =fxColorPrimaryLight
            OnSelect: =Set(varRegistroSel, ThisItem)
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
```

## 7. Badge de ação

Botão de ação dentro da linha, com cor derivada do próprio rótulo (`Self.Text`) via tokens
`fxBadge*` (todos com contraste de texto de pelo menos 4,5:1). `Underline: =true` mantém a ação
legível sem depender só de cor. Hover **escurece** em todos os botões (`ColorFade(Self.Fill, -12%)`),
nunca clareia num e escurece noutro.

```yaml
- xx-btn-gal-acao:
    Control: Classic/Button@2.2.0
    Properties:
      BorderStyle: =BorderStyle.None
      Color: |-
        =Switch(
          Self.Text,
          "Aprovar", fxBadgeSuccessText,
          "Revisar", fxBadgeWarningText,
          "Cancelar", fxBadgeDangerText,
          fxBadgeNeutralText
        )
      DisabledBorderColor: =fxColorBorder
      DisplayMode: =If(ThisItem.Bloqueado, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: |-
        =Switch(
          Self.Text,
          "Aprovar", fxBadgeSuccessBg,
          "Revisar", fxBadgeWarningBg,
          "Cancelar", fxBadgeDangerBg,
          fxBadgeNeutralBg
        )
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =35
      HoverFill: =ColorFade(Self.Fill, -12%)
      PressedFill: =ColorFade(Self.Fill, -24%)
      Size: =fxFontSizeTableSmall
      TabIndex: =0
      Text: ="Aprovar"
      Underline: =true
      Width: =88
      X: =1100
      Y: =8
```

## 8. Botões

Quatro papéis, mesma geometria (`fxBtnHeight`, `fxBtnRadius`):

| Papel | Fill | Texto | Uso |
|---|---|---|---|
| primário | `fxColorPrimary` | verbo da ação | ação principal da tela ou do modal |
| secundário | `fxColorButtonCancel` | `Voltar`, `Cancelar`, `Fechar` | sair sem agir |
| destrutivo | `fxColorError` | verbo explícito (`Confirmar cancelamento`) | irreversível; habilita só com motivo |
| neutro | `fxColorPrimaryLight` | rótulo curto | filtro rápido, chip |

Regras: o primário ocupa a **mesma posição** em todas as telas; no modal, secundário à esquerda e
primário à direita, ambos com largura `(Parent.Width - fxModalPadding * 3) / 2`. **Pressed nunca
inverte `Fill` e `Color`** (botão branco sobre branco fica com texto invisível ao pressionar);
use `ColorFade(Self.Fill, -30%)`. Defina sempre as cores de `Disabled*`. Todo botão que chama
flow liga `DisplayMode` e `Text` a `varShowLoading` ([chamada-flow.md](chamada-flow.md)).

```yaml
- xx-btn-primario:
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
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtConfirmar
      Width: =fxBtnWidth
      X: =20
      Y: =20
- xx-btn-secundario:
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
      PressedBorderColor: =fxColorButtonCancelHover
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =fxColorButtonCancelHover
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtCancelar
      Width: =fxBtnWidth
      X: =20
      Y: =20
- xx-btn-destrutivo:
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
          Len(Trim('xx-txt-motivo'.Text)) < 5,
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
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="Confirmar cancelamento"
      Width: =230
      X: =20
      Y: =20
- xx-btn-neutro:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =ColorFade(Self.Fill, -15%)
      Color: =fxColorTableHeaderText
      Fill: =fxColorPrimaryLight
      Font: =fxFont
      Height: =fxBtnHeight
      HoverFill: =ColorFade(Self.Fill, -10%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="Sistema"
      Width: =90
      X: =20
      Y: =20
```

## 9. Modal, loading e toast

Movidos para [ux-feedback.md](ux-feedback.md), para manter este arquivo abaixo de 1.000 linhas.

## 12. Seleção em lote

Contador com singular e plural numa fórmula só. `colSelecionados` recebe o item no `OnCheck` e o
perde no `OnUncheck`: **não** use `Filter(gal.AllItems, ...)` (só enxerga o já carregado e
`AllItems` é caro). `Text` vazio no checkbox deixa o controle sem nome para leitor de tela:
limitação a registrar em [acessibilidade.md](acessibilidade.md).

```yaml
- xx-chk-gal-selecionar:
    Control: Classic/CheckBox@2.1.0
    Properties:
      CheckboxBorderColor: =fxColorBorderInteractive
      CheckmarkFill: =fxColorPrimary
      Default: =false
      Font: =fxFont
      Height: =40
      OnCheck: =Collect(colSelecionados, ThisItem)
      OnUncheck: =RemoveIf(colSelecionados, Id = ThisItem.Id)
      TabIndex: =0
      Text: =""
      Width: =40
      X: =4
      Y: =5
- xx-lbl-selecao-contador:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =28
      Size: =fxFontSizeFilter
      Text: |-
        =With(
          { n: CountRows(colSelecionados) },
          n & If(n = 1, " registro selecionado", " registros selecionados")
        )
      VerticalAlign: =VerticalAlign.Middle
      Visible: =CountRows(colSelecionados) > 0
      Width: =280
      X: =1000
      Y: =120
```

## 13. Estados: vazio, truncado, erro, desabilitado

- **Vazio**: não existe empty state nativo na galeria. Um `Label` por galeria, ligado à própria
  galeria (`'gal'.X`, `.Width`, `.AllItemsCount = 0`) e usando `fxMsgNoResultsError` +
  `fxMsgNoResultsHint` (o que houve e o que fazer). Cor de texto com contraste >= 4,5:1: o cinza
  claro de placeholder reprova (2,54:1).
- **Truncado**: quando o contador bate no teto (`varPedidoTotal >= fxLimiteLinhas`), um
  rótulo âmbar avisa. Lista truncada sem aviso é problema de **UX**, não só de dados.
- **Erro**: par `Error` + `Hint` por mensagem do catálogo; erro de campo aparece **no campo** (§14),
  não só no toast global.
- **Desabilitado**: `DisplayMode` derivado de precondição (seleção feita, motivo com 5+
  caracteres, campo anterior escolhido, `varShowLoading`); defina `DisabledFill`, `DisabledColor`
  e `DisabledBorderColor`. Texto desabilitado não tem requisito de contraste, mas precisa ser
  distinguível do habilitado.
- **Hover, pressed, foco**: `HoverFill: =ColorFade(Self.Fill, -20%)`, `PressedFill: =ColorFade(Self.Fill, -30%)`;
  foco só por `FocusedBorderColor` nos inputs atestados.
- **Seleção em galeria**: fundo da linha por dado ou por seleção **mais** um badge textual
  (nunca só cor).

```yaml
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
      Visible: ='xx-gal-registros'.Visible && 'xx-gal-registros'.AllItemsCount = 0
      Width: ='xx-gal-registros'.Width
      X: ='xx-gal-registros'.X
      Y: ='xx-gal-registros'.Y + 80
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
      Width: ='xx-gal-registros'.Width
      X: ='xx-gal-registros'.X
      Y: ='xx-gal-registros'.Y + 'xx-gal-registros'.Height + 8
```

## 14. Formulário: obrigatório e erro por campo

Obrigatório sinalizado de forma não ambígua (rótulo com `*` **e** texto de ajuda; `*` sozinho
não basta), rótulo com pelo menos `fxFontSizeFilter` (rótulo menor que o valor inverte a
hierarquia) e erro por campo, visível depois da primeira tentativa de salvar
(`varTentouSalvar`). Validação de formulário usa `Notify()`; retorno de flow, toast.

```yaml
- xx-lbl-form-email-rotulo:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorTextPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =20
      Size: =fxFontSizeFilter
      Text: ="E-mail *"
      Width: =300
      X: =fxModalPadding
      Y: =20
- xx-txt-form-email:
    Control: Classic/TextInput@2.3.2
    Properties:
      BorderColor: =If(varTentouSalvar && !IsMatch(Self.Text, Match.Email), fxColorError, fxColorBorderInteractive)
      Color: =fxColorTextPrimary
      Default: =""
      FocusedBorderColor: =fxColorPrimary
      Font: =fxFont
      Height: =fxFilterHeight
      HintText: ="usuario@contoso.com"
      Size: =fxFontSizeFilter
      TabIndex: =0
      Width: =300
      X: =fxModalPadding
      Y: =44
- xx-lbl-form-email-erro:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorError
      Font: =fxFont
      Height: =20
      Size: =fxFontSizeFilter
      Text: ="Informe um e-mail válido."
      Visible: =varTentouSalvar && !IsMatch('xx-txt-form-email'.Text, Match.Email)
      Width: =300
      X: =fxModalPadding
      Y: =44 + fxFilterHeight + 4
```

## 15. Z-order

A ordem em `Children` é o z-index. O fim de toda tela é:

```text
conteúdo -> painel de sem acesso -> modais -> loading -> toast
```

O toast fica acima de modal e de véu de carregamento. Inverter põe modal acima do toast (defeito
comum, já visto em mais de uma tela). Validador: T016.

# Barra de filtros (combo, texto, datas e limpar)

Maturidade: **estável** · Frequência: **comum** (a combinação varia: combo, busca, datas; o botão Limpar está em todas).

## Propósito

Faixa de filtros acima de uma galeria: combo de status, busca por início do código, intervalo de datas e botão Limpar. Os filtros alimentam o `Items` da galeria direto, sem botão Filtrar.

## Quando usar / quando não usar

**Use quando**

- galeria com mais de uns 50 registros;
- os filtros são delegáveis no conector (`StartsWith`, igualdade, intervalo de data inteira).

**Não use quando**

- a consulta é cara e deve rodar só sob demanda (use a variação com botão Filtrar);
- o filtro precisa de `Search` ou `in` em coluna não textual (não delega).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-con-filtros  (GroupContainer)
  xx-lbl-filtro-status  (Label)
  xx-cbo-filtro-status  (ComboBox)
  xx-lbl-filtro-busca  (Label)
  xx-txt-filtro-busca  (TextInput)
  xx-lbl-filtro-de  (Label)
  xx-dtp-filtro-de  (DatePicker)
  xx-lbl-filtro-ate  (Label)
  xx-dtp-filtro-ate  (DatePicker)
  xx-btn-filtro-limpar  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxLayoutMargin`, `fxLayoutGutter`, `fxColorTextSecondary`, `fxFont`, `fxFontSizeHeader`, `fxColorBorderInteractive`, `fxColorTextPrimary`, `fxColorPrimary`, `fxFilterHeight`, `fxFontSizeFilter`, `fxBtnRadius`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxTxtLimpar`, `fxBtnWidthFilter`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtFiltrar`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxHeaderHeight`.
- **Variáveis globais** (nascem com valor neutro no `OnStart`, `assets/app-onstart-molde.md`; as de janela de data são zeradas de novo no `OnVisible` da tela): `varPedidoDe`, `varPedidoAte`, `varPedidoFiltroAplicado`, `varPedidoStatusAplicado`, `varPedidoBuscaAplicada`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-con-filtros:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorBorder
      BorderThickness: =1
      Fill: =fxColorSurface
      Height: =104
      RadiusBottomLeft: =fxModalRadius
      RadiusBottomRight: =fxModalRadius
      RadiusTopLeft: =fxModalRadius
      RadiusTopRight: =fxModalRadius
      Width: =1180
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + fxLayoutGutter
    Children:
      - xx-lbl-filtro-status:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextSecondary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =20
            Size: =fxFontSizeHeader
            Text: ="Status"
            Width: =180
            X: =20
            Y: =16
      - xx-cbo-filtro-status:
          Control: Classic/ComboBox@2.4.0
          Properties:
            BorderColor: =fxColorBorderInteractive
            Color: =fxColorTextPrimary
            DisplayFields: =["Value"]
            FocusedBorderColor: =fxColorPrimary
            Height: =fxFilterHeight
            InputTextPlaceholder: ="Todos"
            IsSearchable: =false
            Items: =["aberto", "em andamento", "encerrado"]
            SearchFields: =["Value"]
            SelectMultiple: =false
            Width: =180
            X: =20
            Y: =44
      - xx-lbl-filtro-busca:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextSecondary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =20
            Size: =fxFontSizeHeader
            Text: ="Código"
            Width: =180
            X: =216
            Y: =16
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
            HintText: ="Buscar pelo início do código"
            RadiusBottomLeft: =fxBtnRadius
            RadiusBottomRight: =fxBtnRadius
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxFontSizeFilter
            TabIndex: =0
            Width: =240
            X: =216
            Y: =44
      - xx-lbl-filtro-de:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextSecondary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =20
            Size: =fxFontSizeHeader
            Text: ="De"
            Width: =180
            X: =472
            Y: =16
      - xx-dtp-filtro-de:
          Control: Classic/DatePicker@2.6.0
          Properties:
            BorderColor: =fxColorBorderInteractive
            DefaultDate: =Blank()
            FocusedBorderColor: =fxColorPrimary
            Font: =fxFont
            Format: ="dd/mm/yyyy"
            Height: =fxFilterHeight
            IconBackground: =fxColorPrimary
            IconFill: =fxColorSurface
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
            X: =472
            Y: =44
      - xx-lbl-filtro-ate:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextSecondary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =20
            Size: =fxFontSizeHeader
            Text: ="Até"
            Width: =180
            X: =668
            Y: =16
      - xx-dtp-filtro-ate:
          Control: Classic/DatePicker@2.6.0
          Properties:
            BorderColor: =fxColorBorderInteractive
            DefaultDate: =Blank()
            FocusedBorderColor: =fxColorPrimary
            Font: =fxFont
            Format: ="dd/mm/yyyy"
            Height: =fxFilterHeight
            IconBackground: =fxColorPrimary
            IconFill: =fxColorSurface
            OnChange: |-
              =Set(
                varPedidoAte,
                If(
                  IsBlank(Self.SelectedDate),
                  Blank(),
                  36524 + DateDiff(Date(2000, 1, 1), Self.SelectedDate, TimeUnit.Days)
                )
              )
            TabIndex: =0
            Width: =180
            X: =668
            Y: =44
      - xx-btn-filtro-limpar:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorButtonCancel
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
              =Reset('xx-cbo-filtro-status');
              Reset('xx-txt-filtro-busca');
              Reset('xx-dtp-filtro-de');
              Reset('xx-dtp-filtro-ate');
              // Reset de DatePicker não dispara OnChange: reescreve a variável
              Set(varPedidoDe, Blank());
              Set(varPedidoAte, Blank())
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
            X: =864
            Y: =44
```

### Variação: com botão Filtrar

A galeria só lista depois do clique: os controles não filtram, o botão copia o valor para variáveis "aplicadas" e a galeria lê essas variáveis. Troque o par de botões `xx-btn-filtro-limpar` por este.

```yaml
- xx-btn-filtro-aplicar:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =Self.Fill
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      DisabledBorderColor: =fxColorDisabled
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      Fill: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxFilterHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: |-
        =Set(varPedidoFiltroAplicado, true);
        Set(varPedidoStatusAplicado, Coalesce('xx-cbo-filtro-status'.Selected.Value, ""));
        Set(varPedidoBuscaAplicada, Trim('xx-txt-filtro-busca'.Text))
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxFontSizeFilter
      TabIndex: =0
      Text: =fxTxtFiltrar
      Width: =fxBtnWidthFilter
      X: =864
      Y: =44
- xx-btn-filtro-limpar-aplicado:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorButtonCancel
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
        =Reset('xx-cbo-filtro-status');
        Reset('xx-txt-filtro-busca');
        Set(varPedidoFiltroAplicado, false);
        Set(varPedidoStatusAplicado, "");
        Set(varPedidoBuscaAplicada, "")
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
      X: =1004
      Y: =44
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-` | prefixo da tela |  |
| `'xx-cbo-filtro-status'` e `["Aberto", ...]` | controle e domínio de valores reais | lista fixa pequena; domínio grande vem de coleção `col*` |
| `varPedidoDe`, `varPedidoAte` | variáveis de janela de data da tela | inteiros; `Blank()` no `OnStart` e de novo no `OnVisible` |
| `36524` | dias entre 1900-01-01 e 2000-01-01 | só se a coluna `Ref_<col>` do banco for `DATEDIFF(day, 0, <col>)` |
| `fxTxtLimpar`, `fxTxtFiltrar` | tokens de texto |  |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-dtp-filtro-de`.OnChange**: converte a data escolhida em inteiro (número de dias desde 1900-01-01), que é o que a coluna calculada do banco compara e delega

```powerfx
Set(
  varPedidoDe,
  If(
    IsBlank(Self.SelectedDate),
    Blank(),
    36524 + DateDiff(Date(2000, 1, 1), Self.SelectedDate, TimeUnit.Days)
  )
)
```

**`xx-btn-filtro-limpar`.OnSelect**: limpa os controles e **reescreve** as variáveis de data

```powerfx
Reset('xx-cbo-filtro-status');
Reset('xx-txt-filtro-busca');
Reset('xx-dtp-filtro-de');
Reset('xx-dtp-filtro-ate');
// Reset de DatePicker não dispara OnChange: reescreve a variável
Set(varPedidoDe, Blank());
Set(varPedidoAte, Blank())
```

## Acessibilidade

- Cada filtro tem rótulo visível acima (placeholder some ao digitar e não é rótulo).
- A borda do campo de texto muda de cinza para azul quando há valor, e `fxColorBorderInteractive` mantém contraste de borda de controle de pelo menos 3:1.
- Combo, texto e datas são focáveis na ordem esquerda para direita (`TabIndex: =0`).

## Armadilhas

- `Reset()` de `DatePicker` não dispara `OnChange`: sem reescrever as variáveis, a galeria continua filtrada por uma data que o controle já não mostra.
- `Size`, `Radius*` e `FocusedBorderThickness` não existem em `ComboBox` e `DatePicker` (PA2108).
- `DefaultDate: =Blank()` mantém o filtro de período vazio no início; um default de data some com registros antigos.
- `IsSearchable` é verdadeiro por padrão: ao remover a busca de um combo, **apague** a propriedade ou use `false`; nunca troque o valor por `true`.

## Variações

- Reativa (principal) ou com botão Filtrar (acima).
- Seletor de unidade: `seletor-unidade.md`.
- Combo com muitos itens: `IsSearchable: =true` e `Items: =colUnidades`.

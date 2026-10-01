# Abas (botão e traço)

Maturidade: **estável** · Frequência: **comum**.

## Propósito

Alterna entre conjuntos de dados na mesma tela (por exemplo abertos, concluídos, todos) por uma variável numérica; a aba ativa tem fundo, negrito e traço de 3 px.

## Quando usar / quando não usar

**Use quando**

- até 4 conjuntos da mesma entidade na mesma tela;
- o contador de cada conjunto ajuda a escolher.

**Não use quando**

- os conjuntos são telas diferentes (use o menu);
- o app precisa cumprir acessibilidade estrita de abas: o padrão acessível é o controle moderno Tab list, e aba de botão e retângulo não o é.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-con-abas  (GroupContainer)
  xx-btn-tab-abertos  (Button)
  xx-shp-tab-abertos-traco  (Rectangle)
  xx-btn-tab-encerrados  (Button)
  xx-shp-tab-encerrados-traco  (Rectangle)
  xx-btn-tab-todos  (Button)
  xx-shp-tab-todos-traco  (Rectangle)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxLayoutMargin`, `fxLayoutGutter`, `fxColorPrimary`, `fxColorTextSecondary`, `fxColorSurface`, `fxColorTabInactive`, `fxFont`, `fxFontSizeFilter`, `fxBtnRadius`, `fxColorTextPrimary`, `fxFontSizeBody`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxHeaderHeight`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varXXTab`, `varPedidoAbertos`, `varPedidoEncerrados`, `varPedidoTotal`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-con-abas:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorTransparent
      Height: =49
      Width: =760
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + fxLayoutGutter
    Children:
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
            Width: =240
            X: =0
            Y: =0
      - xx-shp-tab-abertos-traco:
          Control: Rectangle@2.3.0
          Properties:
            BorderStyle: =BorderStyle.None
            Fill: =If(varXXTab = 1, fxColorPrimary, fxColorTransparent)
            Height: =3
            Width: =240
            X: =0
            Y: =46
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
            Width: =240
            X: =248
            Y: =0
      - xx-shp-tab-encerrados-traco:
          Control: Rectangle@2.3.0
          Properties:
            BorderStyle: =BorderStyle.None
            Fill: =If(varXXTab = 2, fxColorPrimary, fxColorTransparent)
            Height: =3
            Width: =240
            X: =248
            Y: =46
      - xx-btn-tab-todos:
          Control: Classic/Button@2.2.0
          Properties:
            AutoDisableOnSelect: =false
            BorderThickness: =0
            Color: =If(varXXTab = 3, fxColorPrimary, fxColorTextSecondary)
            Fill: =If(varXXTab = 3, fxColorSurface, fxColorTabInactive)
            Font: =fxFont
            FontWeight: =If(varXXTab = 3, FontWeight.Bold, FontWeight.Semibold)
            Height: =46
            HoverColor: =fxColorPrimary
            HoverFill: =fxColorSurface
            OnSelect: =Set(varXXTab, 3)
            PressedColor: =fxColorPrimary
            PressedFill: =fxColorSurface
            RadiusBottomLeft: =0
            RadiusBottomRight: =0
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxFontSizeFilter
            TabIndex: =0
            Text: ="Todos (" & varPedidoTotal & ")"
            Width: =240
            X: =496
            Y: =0
      - xx-shp-tab-todos-traco:
          Control: Rectangle@2.3.0
          Properties:
            BorderStyle: =BorderStyle.None
            Fill: =If(varXXTab = 3, fxColorPrimary, fxColorTransparent)
            Height: =3
            Width: =240
            X: =496
            Y: =46
```

### Conteúdo condicional

Cada aba tem um contêiner próprio cujo `Visible` compara a variável; só um fica visível por vez.

```yaml
- xx-con-aba-abertos:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorTransparent
      Height: =600
      Visible: =varXXTab = 1
      Width: =Parent.Width - fxLayoutMargin * 2
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + fxLayoutGutter + 49 + fxLayoutGutter
    Children:
      - xx-lbl-aba-abertos-conteudo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextPrimary
            Font: =fxFont
            Height: =28
            Size: =fxFontSizeBody
            Text: ="Conteúdo da aba Abertos"
            Width: =400
            X: =0
            Y: =0
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `varXXTab` | `var<Prefixo>Tab` da tela | nasce em 1 no `OnStart` e é regravada no `OnVisible` |
| `Abertos`, `Encerrados`, `Todos` | nome dos conjuntos | o texto inclui a contagem entre parênteses |
| `varPedido*` | variáveis de contagem | mesmas do card de KPI |
| `240` e `X` 0, 248, 496 | largura e passo | passo = largura + 8 |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-btn-tab-abertos`.OnSelect**: troca a aba ativa

```powerfx
Set(varXXTab, 1)
```

**`xx-btn-tab-abertos`.Fill**: ativa = superfície; inativa = `fxColorTabInactive` (precisam ser diferentes)

```powerfx
If(varXXTab = 1, fxColorSurface, fxColorTabInactive)
```

## Acessibilidade

- Limitação oficial: aba de botão não anuncia "selecionada"; o traço e o negrito dão a pista visual, mas o leitor de tela só lê o texto. Registre a limitação (ver `acessibilidade.md`).
- Ativa e inativa nunca com o mesmo `Fill`.

## Armadilhas

- `AutoDisableOnSelect: =false` evita que o botão desabilite ao clicar; mantenha.
- Esquecer de zerar a seleção da galeria ao trocar de aba deixa a linha selecionada de outra aba.
- Contagem de aba sobre SQL não delega: mostre o teto como no card de KPI.

## Variações

- Abas de largura variável: `Width: =Len(Self.Text) * 9 + 40`.
- Aba com ícone: não use emoji como semântica; ícone é controle separado.

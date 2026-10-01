# Card de KPI (contador com teto)

Maturidade: **estável** · Frequência: **comum** (régua de 3 a 5 cards logo abaixo do cabeçalho).

## Propósito

Contador de uma linha de resumo (total, abertos, concluídos): título com par de cor `fxBadge*`, valor grande e teto honesto quando a contagem não delega.

## Quando usar / quando não usar

**Use quando**

- resumir a lista que está logo abaixo em até 5 ou 6 números;
- o contador precisa bater com a galeria por construção (mesmo filtro de escopo).

**Não use quando**

- a métrica exige cálculo no servidor (use um flow ou uma view e mostre o resultado);
- mais de 6 cards: vira painel de BI, use Power BI.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-con-kpis  (GroupContainer)
  xx-con-kpi-total  (GroupContainer)
    xx-lbl-kpi-total-titulo  (Label)
    xx-lbl-kpi-total-valor  (Label)
  xx-con-kpi-abertos  (GroupContainer)
    xx-lbl-kpi-abertos-titulo  (Label)
    xx-lbl-kpi-abertos-valor  (Label)
  xx-con-kpi-andamento  (GroupContainer)
    xx-lbl-kpi-andamento-titulo  (Label)
    xx-lbl-kpi-andamento-valor  (Label)
  xx-con-kpi-encerrados  (GroupContainer)
    xx-lbl-kpi-encerrados-titulo  (Label)
    xx-lbl-kpi-encerrados-valor  (Label)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxLayoutMargin`, `fxLayoutGutter`, `fxKPIWidth`, `fxKPIHeight`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxBadgeNeutralText`, `fxFont`, `fxFontSizeKPITitle`, `fxBadgeNeutralBg`, `fxKPITitleHeight`, `fxColorTextPrimary`, `fxFontSizeKPI`, `fxLimiteLinhas`, `fxTxtTeto`, `fxKPIValueHeight`, `fxBadgeInfoText`, `fxBadgeInfoBg`, `fxBadgeProgressText`, `fxBadgeProgressBg`, `fxBadgeSuccessText`, `fxBadgeSuccessBg`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxHeaderHeight`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varPedidoTotal`, `varPedidoAbertos`, `varPedidoAndamento`, `varPedidoEncerrados`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-con-kpis:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorTransparent
      Height: =fxKPIHeight
      Width: =(fxKPIWidth + fxLayoutGutter) * 4
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + fxLayoutGutter
    Children:
      - xx-con-kpi-total:
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
            X: =(fxKPIWidth + fxLayoutGutter) * 0
            Y: =0
          Children:
            - xx-lbl-kpi-total-titulo:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxBadgeNeutralText
                  Fill: =fxBadgeNeutralBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxKPITitleHeight
                  Size: =fxFontSizeKPITitle
                  Text: ="Total"
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =0
            - xx-lbl-kpi-total-valor:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxKPIValueHeight
                  Size: =fxFontSizeKPI
                  Text: =If(varPedidoTotal >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoTotal, "[$-en-US]#,##0"))
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =fxKPITitleHeight
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
            X: =(fxKPIWidth + fxLayoutGutter) * 1
            Y: =0
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
      - xx-con-kpi-andamento:
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
            X: =(fxKPIWidth + fxLayoutGutter) * 2
            Y: =0
          Children:
            - xx-lbl-kpi-andamento-titulo:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxBadgeProgressText
                  Fill: =fxBadgeProgressBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxKPITitleHeight
                  Size: =fxFontSizeKPITitle
                  Text: ="Em andamento"
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =0
            - xx-lbl-kpi-andamento-valor:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxKPIValueHeight
                  Size: =fxFontSizeKPI
                  Text: =If(varPedidoAndamento >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoAndamento, "[$-en-US]#,##0"))
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =fxKPITitleHeight
      - xx-con-kpi-encerrados:
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
            X: =(fxKPIWidth + fxLayoutGutter) * 3
            Y: =0
          Children:
            - xx-lbl-kpi-encerrados-titulo:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxBadgeSuccessText
                  Fill: =fxBadgeSuccessBg
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =fxKPITitleHeight
                  Size: =fxFontSizeKPITitle
                  Text: ="Encerrados"
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =0
            - xx-lbl-kpi-encerrados-valor:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorTextPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =fxKPIValueHeight
                  Size: =fxFontSizeKPI
                  Text: =If(varPedidoEncerrados >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoEncerrados, "[$-en-US]#,##0"))
                  VerticalAlign: =VerticalAlign.Middle
                  Width: =Parent.Width
                  X: =0
                  Y: =fxKPITitleHeight
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `slug` (`total`, `abertos`, ...) | nome da métrica | nos nomes dos 3 controles do card |
| `varPedidoTotal` ... `varPedidoEncerrados` | variável do contador | nasce em 0 no `OnStart` |
| `"Total"`, `"Abertos"` | título do card | curto, uma ou duas palavras |
| `Neutral`, `Info`, `Progress`, `Success` | par `fxBadge*` da mesma matiz | texto escuro sobre pastel, contraste conferido |
| `* 0`, `* 1` ... | posição do card na régua | `X` por fórmula, nunca digitado |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-lbl-kpi-total-valor`.Text**: mostra o teto quando a contagem bate no limite do conector

```powerfx
If(varPedidoTotal >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoTotal, "[$-en-US]#,##0"))
```

## Acessibilidade

- Título e valor são rótulos separados, lidos em sequência ("Total", "1.234").
- O par `fxBadge*Text` sobre `fxBadge*Bg` tem contraste de pelo menos 4,5:1.

## Armadilhas

- Contador calculado só no `OnStart` congela e passa o dia divergindo da galeria.
- Valor exibido cru (`2000`) quando o limite do conector foi atingido é mentira: sempre `fxTxtTeto`.
- `CountRows(Filter(...))` dentro do `Text` do card recalcula a cada mudança da tela.
- Named formula **não** pode ler a variável de escopo (`varUnidadeFiltro`); por isso o contador é variável.

## Variações

- Card clicável que aplica filtro: troque o `GroupContainer` por um `Classic/Button` de fundo e ponha o `OnSelect` nele (`GroupContainer` não tem `OnSelect`).
- Compacto (`fxIsCompact`): os tokens `fxKPI*` já encolhem.

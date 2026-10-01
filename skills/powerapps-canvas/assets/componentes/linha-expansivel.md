# Linha expansível

Maturidade: **único** · Frequência: **ocasional**.

## Propósito

Clique na linha da galeria expande um painel de detalhe logo abaixo dela, sem modal. O estado é uma variável com o id da linha expandida (uma por vez).

## Quando usar / quando não usar

**Use quando**

- o detalhe é curto (2 a 4 campos) e o usuário compara várias linhas;
- não vale um modal por linha.

**Não use quando**

- o detalhe é longo ou tem ação (use modal ou tela);
- a lista é grande e a altura da linha precisa ser estável.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-btn-gal-fundo-linha  (Button)
xx-lbl-gal-chevron  (Label)
xx-rec-gal-detalhe-fundo  (Rectangle)
xx-lbl-gal-detalhe-observacoes  (Label)
xx-lbl-gal-detalhe-responsavel  (Label)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorDivider`, `fxColorTransparent`, `fxColorPrimaryLight`, `fxColorSurface`, `fxFont`, `fxRowHeight`, `fxColorPrimary`, `fxFontSizeBody`, `fxColorBackground`, `fxColorTextBody`, `fxFontSizeTableSmall`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varLinhaExpandida`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

Estes controles ficam **dentro do template da galeria** (`Children` de `xx-gal-pedidos`).

```yaml
- xx-btn-gal-fundo-linha:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorDivider
      Color: =fxColorTransparent
      Fill: =If(varLinhaExpandida = ThisItem.<col-id>, fxColorPrimaryLight, fxColorSurface)
      Font: =fxFont
      Height: =fxRowHeight
      HoverFill: =fxColorPrimaryLight
      OnSelect: |-
        =Set(
          varLinhaExpandida,
          If(varLinhaExpandida = ThisItem.<col-id>, Blank(), ThisItem.<col-id>)
        )
      PressedFill: =fxColorPrimaryLight
      TabIndex: =0
      Text: =""
      Tooltip: =If(varLinhaExpandida = ThisItem.<col-id>, "Recolher detalhes", "Expandir detalhes")
      Width: =Parent.TemplateWidth
      X: =0
      Y: =0
- xx-lbl-gal-chevron:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxRowHeight
      Size: =fxFontSizeBody
      Text: =If(varLinhaExpandida = ThisItem.<col-id>, "▴", "▾")
      VerticalAlign: =VerticalAlign.Middle
      Width: =30
      X: =Parent.TemplateWidth - 44
      Y: =0
- xx-rec-gal-detalhe-fundo:
    Control: Rectangle@2.3.0
    Properties:
      BorderStyle: =BorderStyle.None
      Fill: =fxColorBackground
      Height: =fxRowHeight * 3
      Visible: =varLinhaExpandida = ThisItem.<col-id>
      Width: =Parent.TemplateWidth
      X: =0
      Y: =fxRowHeight
- xx-lbl-gal-detalhe-observacoes:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorTextBody
      Font: =fxFont
      Height: =28
      Size: =fxFontSizeTableSmall
      Text: |-
        ="Observações: " & Coalesce(ThisItem.<col-observacoes>, "sem observações")
      Visible: =varLinhaExpandida = ThisItem.<col-id>
      Width: =Parent.TemplateWidth - 32
      X: =16
      Y: =fxRowHeight + 8
- xx-lbl-gal-detalhe-responsavel:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorTextBody
      Font: =fxFont
      Height: =28
      Size: =fxFontSizeTableSmall
      Text: |-
        ="Responsável: " & ThisItem.<col-responsavel>
      Visible: =varLinhaExpandida = ThisItem.<col-id>
      Width: =Parent.TemplateWidth - 32
      X: =16
      Y: =fxRowHeight + 44
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `varLinhaExpandida` | variável da tela | nasce `Blank()` no `OnStart`; zere ao mudar filtro |
| `<col-id>`, `<col-observacoes>`, `<col-responsavel>` | colunas reais |  |
| `TemplateSize` da galeria | `If(IsBlank(varLinhaExpandida), fxRowHeight, fxRowHeight * 4)` | ver Armadilhas: **todas** as linhas crescem |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-btn-gal-fundo-linha`.OnSelect**: alterna a linha expandida: a mesma linha recolhe, outra substitui

```powerfx
Set(
  varLinhaExpandida,
  If(varLinhaExpandida = ThisItem.<col-id>, Blank(), ThisItem.<col-id>)
)
```

## Acessibilidade

- O fundo da linha é botão: foco e Enter funcionam; o `Tooltip` diz a ação atual.
- O estado (expandido ou recolhido) aparece em símbolo e em fundo, não só em cor.

## Armadilhas

- `TemplateSize` não pode ler `ThisItem`: ele é da própria galeria, então ao expandir uma linha, todas crescem (as não expandidas ficam com espaço vazio). Por isso o padrão é limitar a um detalhe curto.
- Altura variável por linha só com galeria vertical flexível (`BrowseLayout_Flexible_*` com `AutoHeight`) `[não verificado]`.
- Dois cliques seguidos abrem e fecham: mantenha `OnSelect` idempotente (a fórmula acima é).
- Ação dentro do detalhe (cancelar, editar) vira modal: o painel é só leitura.

## Variações

- Detalhe lateral (painel fixo à direita lê `varPedidoSel`): sem o problema de altura.
- Chevron em imagem: use `Image@2.2.3` com recurso de mídia no lugar do `Label`.

# Cabeçalho ordenável

Maturidade: **único** · Frequência: **rara**.

## Propósito

Cabeçalho de coluna clicável que ordena a galeria: primeiro clique ordena de forma crescente, o segundo inverte, e a coluna ativa mostra a seta no próprio texto.

## Quando usar / quando não usar

**Use quando**

- o usuário precisa reordenar a mesma lista por mais de uma coluna;
- a ordenação é delegável na fonte.

**Não use quando**

- a ordem é regra de negócio fixa (data decrescente basta no `Sort` do `Items`);
- a fonte não delega `SortByColumns` e a lista passa do limite do conector.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-hdr-gal-codigo  (Button)
xx-hdr-gal-data  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTableHeaderText`, `fxColorTableHeaderBg`, `fxFont`, `fxFontSizeHeader`, `fxLayoutMargin`, `fxTableHeaderHeight`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxTxtOrdemAsc`, `fxTxtOrdemDesc`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varPedidoSortColuna`, `varPedidoSortAsc`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-hdr-gal-codigo:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      HoverColor: =fxColorTableHeaderText
      HoverFill: =ColorFade(Self.Fill, -10%)
      OnSelect: |-
        =If(
          varPedidoSortColuna = "<col-codigo>",
          Set(varPedidoSortAsc, !varPedidoSortAsc),
          Set(varPedidoSortColuna, "<col-codigo>");
          Set(varPedidoSortAsc, true)
        )
      PressedColor: =fxColorTableHeaderText
      PressedFill: =ColorFade(Self.Fill, -20%)
      Size: =fxFontSizeHeader
      TabIndex: =0
      Text: ="Código" & If(varPedidoSortColuna = "<col-codigo>", If(varPedidoSortAsc, fxTxtOrdemAsc, fxTxtOrdemDesc), "")
      Width: =160
      X: =fxLayoutMargin
      Y: =300
- xx-hdr-gal-data:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      HoverColor: =fxColorTableHeaderText
      HoverFill: =ColorFade(Self.Fill, -10%)
      OnSelect: |-
        =If(
          varPedidoSortColuna = "<col-data>",
          Set(varPedidoSortAsc, !varPedidoSortAsc),
          Set(varPedidoSortColuna, "<col-data>");
          Set(varPedidoSortAsc, true)
        )
      PressedColor: =fxColorTableHeaderText
      PressedFill: =ColorFade(Self.Fill, -20%)
      Size: =fxFontSizeHeader
      TabIndex: =0
      Text: ="Inclusão" & If(varPedidoSortColuna = "<col-data>", If(varPedidoSortAsc, fxTxtOrdemAsc, fxTxtOrdemDesc), "")
      Width: =160
      X: =fxLayoutMargin + 160
      Y: =300
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `<col-codigo>`, `<col-data>` | nomes reais das colunas | a string é o nome **físico**; erro não acusa, só ordena nada |
| `varPedidoSortColuna`, `varPedidoSortAsc` | variáveis de ordenação da tela | nascem no `OnVisible` com a ordem padrão |
| `fxTxtOrdemAsc`, `fxTxtOrdemDesc` | setas | tokens novos |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-hdr-gal-codigo`.OnSelect**: mesma coluna inverte a direção; coluna nova começa crescente

```powerfx
If(
  varPedidoSortColuna = "<col-codigo>",
  Set(varPedidoSortAsc, !varPedidoSortAsc),
  Set(varPedidoSortColuna, "<col-codigo>");
  Set(varPedidoSortAsc, true)
)
```

**`xx-hdr-gal-codigo`.Text**: a seta aparece só na coluna ativa

```powerfx
"Código" & If(varPedidoSortColuna = "<col-codigo>", If(varPedidoSortAsc, fxTxtOrdemAsc, fxTxtOrdemDesc), "")
```

## Acessibilidade

- O texto do cabeçalho muda ("Código ▲"): o leitor de tela lê a ordem atual.
- Diferente do cabeçalho passivo, este é focável: mantenha na ordem de tabulação, antes da galeria.
- `HoverColor` e `PressedColor` iguais a `fxColorTableHeaderText` (nunca invertem com o fundo).

## Armadilhas

- Nome de coluna errado na string não dá erro nem aviso: a lista não reordena. `[não verificado: delegação de SortByColumns com nome de coluna em variável no conector SQL]`.
- Mudar a ordenação sem voltar à primeira linha deixa o usuário no meio da lista: `Reset('xx-gal-pedidos')` no `OnSelect` se a lista for longa.
- A seta é texto: não use emoji colorido no lugar.

## Variações

- Ordenação em duas colunas: encadeie `SortByColumns(fonte, "colA", ..., "colB", ...)`.
- Só ordenar por coleção local: troque por `Sort(colX, ...)`, que não tem restrição de delegação.

# Rodapé "Exibindo N de M"

Maturidade: **único** · Frequência: **ocasional**.

## Propósito

Linha sob a galeria que diz quantos registros aparecem e de quantos no escopo atual, com o teto honesto (`2.000+`) e o sufixo de escopo condicional.

## Quando usar / quando não usar

**Use quando**

- a lista não tem paginação e o total real importa;
- o escopo (unidade) muda o universo e o usuário precisa saber.

**Não use quando**

- a lista é paginada (use `paginacao-cursor.md`);
- o total é irrelevante (lista curta e fixa).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-lbl-tabela-total  (Label)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTextSecondary`, `fxFont`, `fxFontSizeTableSmall`, `fxLimiteLinhas`, `fxTxtTeto`, `fxLayoutMargin`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxTxtExibindo`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varPedidoTotal`, `varUnidadeFiltro`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-lbl-tabela-total:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Right
      Color: =fxColorTextSecondary
      Font: =fxFont
      Height: =32
      Size: =fxFontSizeTableSmall
      Text: |-
        =fxTxtExibindo & " " & 'xx-gal-pedidos'.AllItemsCount & " de "
          & If(varPedidoTotal >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoTotal, "[$-en-US]#,##0"))
          & " pedidos "
          & If(IsBlank(varUnidadeFiltro), "de todas as unidades", "da unidade " & varUnidadeFiltro)
      VerticalAlign: =VerticalAlign.Middle
      Width: ='xx-gal-pedidos'.Width
      X: =fxLayoutMargin
      Y: ='xx-gal-pedidos'.Y + 'xx-gal-pedidos'.Height + 40
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `'xx-gal-pedidos'` | galeria da tela |  |
| `varPedidoTotal` | contador do escopo | recontado como nos cards |
| `pedidos` | substantivo no plural |  |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-lbl-tabela-total`.Text**: N local (itens carregados), M do contador com teto, e sufixo de escopo

```powerfx
fxTxtExibindo & " " & 'xx-gal-pedidos'.AllItemsCount & " de "
  & If(varPedidoTotal >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoTotal, "[$-en-US]#,##0"))
  & " pedidos "
  & If(IsBlank(varUnidadeFiltro), "de todas as unidades", "da unidade " & varUnidadeFiltro)
```

## Acessibilidade

- Texto informativo estático: sem foco; o leitor de tela o lê depois da lista.
- `fxColorTextSecondary` mantém contraste de 4,5:1.

## Armadilhas

- Sufixo de escopo fixo (`"da unidade " & varUnidadeFiltro`) imprime "da unidade " e para quando o filtro é vazio (escopo total): use o `If(IsBlank(...))`.
- `IsBlank` e não `= ""`: vazio e `Blank()` se confundem em Power Fx e o vazio **significa** escopo total.
- M cru no teto (`2000`) parece total: sempre `fxTxtTeto`.

## Variações

- Sem escopo: remova o último `& If(...)`.
- Com paginação: troque por `varPagina` e total de páginas.

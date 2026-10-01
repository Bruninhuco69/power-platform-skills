# Estado vazio e aviso de lista truncada

Maturidade: **estável** · Frequência: **muito comum** (o aviso de lista truncada é menos comum).

## Propósito

A galeria não tem estado vazio nativo: um `Label` ligado à própria galeria avisa quando não há resultado (o que houve e o que fazer), e um aviso âmbar avisa quando o contador bateu no teto do conector.

## Quando usar / quando não usar

**Use quando**

- toda galeria filtrável;
- a lista pode estar truncada pelo limite do conector (contagem sobre SQL).

**Não use quando**

- a ausência de dados é erro de carga (mostre mensagem de erro com a ação de tentar de novo);
- a lista é uma coleção local pequena e sempre populada.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-lbl-gal-vazio  (Label)
xx-lbl-gal-truncado  (Label)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTextSecondary`, `fxFont`, `fxFontSizeBody`, `fxMsgNoResultsError`, `fxMsgNoResultsHint`, `fxBadgeWarningText`, `fxFontSizeFilter`, `fxMsgListaTruncada`, `fxBadgeWarningBg`, `fxLimiteLinhas`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varPedidoTotal`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

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
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `'xx-gal-pedidos'` | nome da galeria | o vazio e o truncado dependem dele |
| `varPedidoTotal` | contador da tela | o mesmo do card de KPI e do rodapé |
| `fxMsgNoResultsError`, `fxMsgNoResultsHint`, `fxMsgListaTruncada` | textos do projeto | par "o que houve" + "o que fazer" |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-lbl-gal-vazio`.Visible**: só quando a galeria está visível **e** sem itens

```powerfx
'xx-gal-pedidos'.Visible && 'xx-gal-pedidos'.AllItemsCount = 0
```

**`xx-lbl-gal-truncado`.Visible**: só quando o contador bateu no limite

```powerfx
varPedidoTotal >= fxLimiteLinhas
```

## Acessibilidade

- Cor do texto com contraste de 4,5:1 (`fxColorTextSecondary`); o cinza claro de placeholder reprova.
- Mensagem em duas frases curtas: o que houve e o que fazer.

## Armadilhas

- Lista truncada sem aviso é erro de UX, não só de dados: o usuário acredita que viu tudo.
- `AllItemsCount` é local e barato; `CountRows(AllItems)` também funciona, mas não troque por `CountRows(fonte)`.
- O vazio aparece enquanto a consulta ainda carrega se o `Visible` não depender de loading: combine com `varShowLoading` se a lista for lenta.

## Variações

- Vazio sem filtro ativo ("Nenhum pedido cadastrado") vs. com filtro ("Nenhum resultado"): `If(<filtro ativo>, fxMsgNoResultsError, "Nenhum pedido cadastrado")`.
- Erro de carga: um terceiro rótulo com `fxMsgFalhaFlow` e botão "Tentar novamente".

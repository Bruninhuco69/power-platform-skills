# Paginação por cursor

Maturidade: **único** · Frequência: **rara**.

## Propósito

Anterior, próxima e "Página N de M" para lista maior que o limite do conector. O cursor é o valor da chave de ordenação do último item da página; uma pilha local guarda os cursores das páginas já visitadas.

## Quando usar / quando não usar

**Use quando**

- a lista passa de `fxLimiteLinhas` e o usuário precisa percorrer tudo;
- existe uma chave de ordenação única e estável.

**Não use quando**

- a lista cabe no limite do conector (use busca e filtro);
- a ordenação muda por clique (o cursor depende de uma chave fixa).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-btn-pagina-anterior  (Button)
xx-lbl-pagina-atual  (Label)
xx-btn-pagina-proxima  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTableHeaderText`, `fxColorBorder`, `fxColorDisabledText`, `fxColorDisabled`, `fxColorPrimaryLight`, `fxFont`, `fxBtnFontSize`, `fxBtnRadius`, `fxLayoutMargin`, `fxColorTextPrimary`, `fxFontSizeBody`, `fxPageSize`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxTxtAnterior`, `fxTxtProxima`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varPagina`, `varShowLoading`, `varCursorAtual`, `varPedidoTotal`.
- **Coleções**: `colCursores`.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-btn-pagina-anterior:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =ColorFade(Self.Fill, -15%)
      Color: =fxColorTableHeaderText
      DisabledBorderColor: =fxColorBorder
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      DisplayMode: =If(varPagina <= 1 || varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: =fxColorPrimaryLight
      Font: =fxFont
      Height: =34
      HoverBorderColor: =ColorFade(Self.BorderColor, 20%)
      HoverColor: =fxColorTableHeaderText
      HoverFill: =ColorFade(Self.Fill, -10%)
      OnSelect: |-
        =Set(varCursorAtual, LookUp(colCursores, pag = varPagina - 1).cursor);
        RemoveIf(colCursores, pag = varPagina - 1);
        Set(varPagina, Max(1, varPagina - 1));
        Reset('xx-gal-pedidos')
      PressedColor: =fxColorTableHeaderText
      PressedFill: =ColorFade(Self.Fill, -20%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtAnterior
      Width: =150
      X: =fxLayoutMargin + 420
      Y: ='xx-gal-pedidos'.Y + 'xx-gal-pedidos'.Height + 8
- xx-lbl-pagina-atual:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: =fxColorTextPrimary
      Font: =fxFont
      Height: =34
      Size: =fxFontSizeBody
      Text: ="Página " & varPagina & " de " & Max(1, RoundUp(varPedidoTotal / fxPageSize, 0))
      VerticalAlign: =VerticalAlign.Middle
      Width: =160
      X: =fxLayoutMargin + 580
      Y: ='xx-gal-pedidos'.Y + 'xx-gal-pedidos'.Height + 8
- xx-btn-pagina-proxima:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =ColorFade(Self.Fill, -15%)
      Color: =fxColorTableHeaderText
      DisabledBorderColor: =fxColorBorder
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      DisplayMode: =If(varPagina >= Max(1, RoundUp(varPedidoTotal / fxPageSize, 0)) || varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: =fxColorPrimaryLight
      Font: =fxFont
      Height: =34
      HoverBorderColor: =ColorFade(Self.BorderColor, 20%)
      HoverColor: =fxColorTableHeaderText
      HoverFill: =ColorFade(Self.Fill, -10%)
      OnSelect: |-
        =Collect(colCursores, { pag: varPagina, cursor: varCursorAtual });
        Set(varCursorAtual, Last('xx-gal-pedidos'.AllItems).<col-chave>);
        Set(varPagina, varPagina + 1);
        Reset('xx-gal-pedidos')
      PressedColor: =fxColorTableHeaderText
      PressedFill: =ColorFade(Self.Fill, -20%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtProxima
      Width: =150
      X: =fxLayoutMargin + 750
      Y: ='xx-gal-pedidos'.Y + 'xx-gal-pedidos'.Height + 8
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `<col-chave>` | coluna de ordenação única e estável | com empate o cursor pula linhas |
| `varPagina`, `varCursorAtual`, `colCursores` | estado da paginação | nascem no `OnStart`; zere ao mudar o filtro |
| `fxPageSize` | tamanho da página | token existente (100) |
| `varPedidoTotal` | total do escopo | o mesmo contador do rodapé |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-btn-pagina-proxima`.OnSelect**: empilha o cursor atual, avança o cursor para a chave do último item e a página

```powerfx
Collect(colCursores, { pag: varPagina, cursor: varCursorAtual });
Set(varCursorAtual, Last('xx-gal-pedidos'.AllItems).<col-chave>);
Set(varPagina, varPagina + 1);
Reset('xx-gal-pedidos')
```

**`xx-btn-pagina-anterior`.OnSelect**: desempilha o cursor da página anterior

```powerfx
Set(varCursorAtual, LookUp(colCursores, pag = varPagina - 1).cursor);
RemoveIf(colCursores, pag = varPagina - 1);
Set(varPagina, Max(1, varPagina - 1));
Reset('xx-gal-pedidos')
```

## Acessibilidade

- Botões com texto ("‹ Anterior", "Próxima ›") e `DisplayMode` coerente com a página.
- "Página N de M" em texto, lido na ordem de tabulação.

## Armadilhas

- Pular para a página N não é possível: o cursor só avança em sequência.
- Mudar filtro sem zerar o cursor mostra uma página vazia.
- Total de páginas sobre SQL usa `CountRows`, que para no teto: mostre `fxTxtTeto` quando o total bater no limite.
- O `Collect` de cursor sem `Clear` ao trocar de filtro vaza páginas antigas.

## Variações

- Sem total: só anterior e próxima (próxima desabilita quando a página volta menos que `fxPageSize` itens).
- Rolagem infinita: a galeria já faz paginação nativa dentro do limite do conector; use só se a lista couber.

# Seleção em lote

Maturidade: **único** · Frequência: **ocasional**.

## Propósito

Checkbox por linha e "selecionar todos", contador com singular e plural e botão de ação em lote, tudo apoiado em uma coleção `colSelecionados` (não em `Filter(gal.AllItems, ...)`).

## Quando usar / quando não usar

**Use quando**

- a mesma ação se aplica a vários registros;
- o flow aceita uma lista de ids.

**Não use quando**

- a ação é sempre de um registro (use o botão da linha);
- a lista passa do limite do conector e "todos" não é todos.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-chk-selecionar-todos  (CheckBox)
xx-lbl-selecao-contador  (Label)
xx-btn-lote-encerrar  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorBorderInteractive`, `fxColorPrimary`, `fxFont`, `fxLayoutMargin`, `fxFontSizeFilter`, `fxColorTextOnPrimary`, `fxBtnRadius`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtEncerrar`, `fxBtnFontSize`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varMostrarConfirmarLote`, `varShowLoading`, `varPerfil`.
- **Coleções**: `colSelecionados`.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-chk-selecionar-todos:
    Control: Classic/CheckBox@2.1.0
    Properties:
      CheckboxBorderColor: =fxColorBorderInteractive
      CheckmarkFill: =fxColorPrimary
      Default: =false
      Font: =fxFont
      Height: =40
      OnCheck: =ClearCollect(colSelecionados, 'xx-gal-pedidos'.AllItems)
      OnUncheck: =Clear(colSelecionados)
      TabIndex: =0
      Text: ="Selecionar todos"
      Width: =200
      X: =fxLayoutMargin
      Y: =270
- xx-lbl-selecao-contador:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =28
      Size: =fxFontSizeFilter
      Text: |-
        =With(
          { n: CountRows(colSelecionados) },
          n & If(n = 1, " pedido selecionado", " pedidos selecionados")
        )
      VerticalAlign: =VerticalAlign.Middle
      Visible: =CountRows(colSelecionados) > 0
      Width: =280
      X: =fxLayoutMargin + 220
      Y: =272
- xx-btn-lote-encerrar:
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
          varShowLoading || CountRows(colSelecionados) = 0,
          DisplayMode.Disabled,
          DisplayMode.Edit
        )
      Fill: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =40
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: =Set(varMostrarConfirmarLote, true)
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtEncerrar
      Visible: =varPerfil.Flg_Encerrar
      Width: =180
      X: =fxLayoutMargin + 520
      Y: =266
```

### Checkbox da linha

Vai **dentro do template da galeria** (`Children` de `xx-gal-pedidos`), antes dos rótulos, e desloque as colunas em 44 px.

```yaml
- xx-chk-gal-selecionar:
    Control: Classic/CheckBox@2.1.0
    Properties:
      CheckboxBorderColor: =fxColorBorderInteractive
      CheckmarkFill: =fxColorPrimary
      Default: =!IsBlank(LookUp(colSelecionados, <col-id> = ThisItem.<col-id>))
      Font: =fxFont
      Height: =40
      OnCheck: =Collect(colSelecionados, ThisItem)
      OnUncheck: =RemoveIf(colSelecionados, <col-id> = ThisItem.<col-id>)
      TabIndex: =0
      Text: =""
      Width: =40
      X: =4
      Y: =(Parent.TemplateHeight - Self.Height) / 2
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `colSelecionados` | coleção da tela | nasce vazia; `Clear` ao mudar filtro, aba ou página |
| `<col-id>` | chave real |  |
| `fxTxtEncerrar`, `varPerfil.Flg_Encerrar` | verbo e flag reais | o botão só existe para quem tem a flag |
| `varMostrarConfirmarLote` | modal de confirmação em lote | ver `modal-confirmacao.md` (texto com `CountRows(colSelecionados)`) |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-chk-selecionar-todos`.OnCheck**: copia os itens carregados para a coleção (só os já carregados)

```powerfx
ClearCollect(colSelecionados, 'xx-gal-pedidos'.AllItems)
```

**`xx-lbl-selecao-contador`.Text**: singular e plural numa fórmula só

```powerfx
With(
  { n: CountRows(colSelecionados) },
  n & If(n = 1, " pedido selecionado", " pedidos selecionados")
)
```

## Acessibilidade

- `Text` vazio no checkbox da linha o deixa sem nome para leitor de tela: limitação a registrar em `acessibilidade.md`.
- O contador em texto informa a seleção atual.

## Armadilhas

- Não use `Filter(gal.AllItems, ...)` para saber o que está selecionado: só enxerga o carregado e `AllItems` é caro.
- "Selecionar todos" seleciona só o que a galeria carregou: se a lista está truncada, o botão mente; mostre o aviso de truncado.
- `Default` referenciando a coleção mantém o visto ao rolar a galeria; sem ele o visto some.
- Limpe a coleção ao mudar de filtro: seleção de itens que saíram da lista é a causa mais comum de ação em lote errada.

## Variações

- Lote com resultado por item: o flow devolve `colResultadoLote` e o `modal-informativo.md` mostra a lista.
- Seleção única (radio): troque a coleção por `varPedidoSel`.

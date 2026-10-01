# Galeria em formato de tabela

Maturidade: **estável** · Frequência: **muito comum** (a base de toda listagem; só variam as colunas).

## Propósito

Lista tabular em três camadas: cabeçalho de colunas fixo (fora da galeria), galeria com linha clicável e colunas alinhadas por `X` e `Width`, e o `Items` delegável que lê os filtros da barra acima.

## Quando usar / quando não usar

**Use quando**

- lista de registros com 4 a 10 colunas e uma ação por linha;
- o `Items` pode ser expresso só com predicados delegáveis.

**Não use quando**

- tabela 2D acessível a leitor de tela (use o Data Table clássico);
- linhas com altura variável por conteúdo longo (use `TemplateSize` condicional e revise o alinhamento).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-hdr-gal-codigo  (Button)
xx-hdr-gal-descricao  (Button)
xx-hdr-gal-status  (Button)
xx-hdr-gal-data  (Button)
xx-hdr-gal-acoes  (Button)
xx-gal-pedidos  (Gallery)
  xx-btn-gal-fundo-linha  (Button)
  xx-lbl-gal-codigo  (Label)
  xx-lbl-gal-descricao  (Label)
  xx-lbl-gal-status  (Label)
  xx-lbl-gal-data  (Label)
  xx-btn-gal-detalhes  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTableHeaderText`, `fxColorTableHeaderBg`, `fxFont`, `fxFontSizeHeader`, `fxLayoutMargin`, `fxTableHeaderHeight`, `fxColorBorder`, `fxRowHeight`, `fxColorDivider`, `fxColorTransparent`, `fxColorPrimaryLight`, `fxColorSurface`, `fxColorPrimary`, `fxFontSizeTable`, `fxColorTextBody`, `fxBadgeInfoText`, `fxBadgeProgressText`, `fxBadgeSuccessText`, `fxBadgeNeutralText`, `fxFontSizeTableSmall`, `fxBadgeInfoBg`, `fxBadgeProgressBg`, `fxBadgeSuccessBg`, `fxBadgeNeutralBg`, `fxColorTextPrimary`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxBtnRadius`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varUnidadeFiltro`, `varPedidoDe`, `varPedidoAte`, `varPedidoSel`, `varMostrarDetalhes`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

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
      Y: =300
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
      Width: =560
      X: =fxLayoutMargin + 160
      Y: =300
- xx-hdr-gal-status:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      DisplayMode: =DisplayMode.View
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      Size: =fxFontSizeHeader
      Text: ="Status"
      Width: =160
      X: =fxLayoutMargin + 720
      Y: =300
- xx-hdr-gal-data:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      DisplayMode: =DisplayMode.View
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      Size: =fxFontSizeHeader
      Text: ="Inclusão"
      Width: =160
      X: =fxLayoutMargin + 880
      Y: =300
- xx-hdr-gal-acoes:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      DisplayMode: =DisplayMode.View
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      Size: =fxFontSizeHeader
      Text: ="Ações"
      Width: =140
      X: =fxLayoutMargin + 1040
      Y: =300
- xx-gal-pedidos:
    Control: Gallery@2.15.0
    Variant: BrowseLayout_Flexible_SocialFeed_ver5.0
    Properties:
      BorderColor: =fxColorBorder
      BorderThickness: =1
      Height: =fxRowHeight * 12
      Items: |-
        =Sort(
          Filter(
            '<fonte>',
            StartsWith(<col-unidade>, varUnidadeFiltro),
            IsBlank('xx-cbo-filtro-status'.Selected)
              || <col-status> = 'xx-cbo-filtro-status'.Selected.Value,
            StartsWith(<col-codigo>, Trim('xx-txt-filtro-busca'.Text)),
            IsBlank(varPedidoDe) || Ref_<col-data> >= varPedidoDe,
            IsBlank(varPedidoAte) || Ref_<col-data> <= varPedidoAte
          ),
          <col-data>,
          SortOrder.Descending
        )
      TemplatePadding: =0
      TemplateSize: =Max(20, fxRowHeight)
      Width: =1180
      X: =fxLayoutMargin
      Y: =300 + fxTableHeaderHeight
    Children:
      - xx-btn-gal-fundo-linha:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorDivider
            Color: =fxColorTransparent
            Fill: =If(varPedidoSel.<col-id> = ThisItem.<col-id>, fxColorPrimaryLight, fxColorSurface)
            Font: =fxFont
            Height: =Parent.TemplateHeight
            HoverFill: =fxColorPrimaryLight
            OnSelect: =Set(varPedidoSel, ThisItem)
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
            Text: =ThisItem.<col-codigo>
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
            Text: =ThisItem.<col-descricao>
            VerticalAlign: =VerticalAlign.Middle
            Width: =550
            X: =164
            Y: =0
      - xx-lbl-gal-status:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: |-
              =Switch(
                ThisItem.<col-status>,
                "aberto", fxBadgeInfoText,
                "em andamento", fxBadgeProgressText,
                "encerrado", fxBadgeSuccessText,
                fxBadgeNeutralText
              )
            Fill: |-
              =Switch(
                ThisItem.<col-status>,
                "aberto", fxBadgeInfoBg,
                "em andamento", fxBadgeProgressBg,
                "encerrado", fxBadgeSuccessBg,
                fxBadgeNeutralBg
              )
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =24
            Size: =fxFontSizeTableSmall
            Text: =ThisItem.<col-status>
            VerticalAlign: =VerticalAlign.Middle
            Width: =140
            X: =730
            Y: =(Parent.TemplateHeight - Self.Height) / 2
      - xx-lbl-gal-data:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorTextPrimary
            Font: =fxFont
            Height: =Parent.TemplateHeight
            Size: =fxFontSizeTableSmall
            Text: =Text(ThisItem.<col-data>, "[$-pt-BR]dd/mm/yyyy")
            VerticalAlign: =VerticalAlign.Middle
            Width: =150
            X: =880
            Y: =0
      - xx-btn-gal-detalhes:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorButtonCancel
            BorderThickness: =1
            Color: =fxColorTextOnPrimary
            Fill: =fxColorButtonCancel
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =34
            HoverBorderColor: =fxColorButtonCancelHover
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorButtonCancelHover
            OnSelect: |-
              =Set(varPedidoSel, ThisItem);
              Set(varMostrarDetalhes, true)
            PressedBorderColor: =fxColorButtonCancelHover
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorButtonCancelHover
            RadiusBottomLeft: =fxBtnRadius
            RadiusBottomRight: =fxBtnRadius
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxFontSizeTableSmall
            TabIndex: =0
            Text: ="Detalhes"
            Width: =120
            X: =1050
            Y: =(Parent.TemplateHeight - Self.Height) / 2
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `'xx-gal-pedidos'` | nome da galeria | referenciado pelo estado vazio e pelo rodapé |
| `'<fonte>'`, `<col-...>` | tabela e colunas reais | nome vem do ambiente (`NOMES-AS-BUILT`), nunca do dicionário |
| larguras 160, 560, 160, 160 e 140 | colunas e larguras reais | o `X` de cada coluna é a soma das larguras anteriores; cabeçalho e célula usam o mesmo `X` |
| `varPedidoSel`, `varMostrarDetalhes` | variáveis de seleção e de modal | nascem no `OnStart` |
| `Ref_<col-data>` | coluna calculada inteira de data | filtro de data direto no conector SQL não delega |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-gal-pedidos`.Items**: filtro de unidade, status, código e janela de data, ordenado por data decrescente

```powerfx
Sort(
  Filter(
    '<fonte>',
    StartsWith(<col-unidade>, varUnidadeFiltro),
    IsBlank('xx-cbo-filtro-status'.Selected)
      || <col-status> = 'xx-cbo-filtro-status'.Selected.Value,
    StartsWith(<col-codigo>, Trim('xx-txt-filtro-busca'.Text)),
    IsBlank(varPedidoDe) || Ref_<col-data> >= varPedidoDe,
    IsBlank(varPedidoAte) || Ref_<col-data> <= varPedidoAte
  ),
  <col-data>,
  SortOrder.Descending
)
```

**`xx-btn-gal-fundo-linha`.OnSelect**: seleciona a linha (GroupContainer não tem `OnSelect`; por isso o fundo é um botão)

```powerfx
Set(varPedidoSel, ThisItem)
```

## Acessibilidade

- Cabeçalho é botão `DisplayMode.View`: não entra na ordem de tabulação nem clica.
- Status por cor **e** texto (nunca só cor); contraste do par `fxBadge*` de 4,5:1.
- Linha clicável sem rótulo próprio: o texto das células é lido; um leitor de tela não monta tabela semântica (limitação registrada em `acessibilidade.md`).

## Armadilhas

- `TemplateSize: =Max(20, fxRowHeight)`: nunca 0 nem fixo desconectado do conteúdo.
- Dentro da galeria use `Parent.TemplateWidth` e `Parent.TemplateHeight`, não `Parent.Width`.
- `LookUp(fonte)` dentro da galeria dispara uma consulta por linha: carregue o domínio em coleção.
- `Patch` na mesma fonte da galeria dentro de `OnChange` cria laço de recarga.
- `Sort` + `Filter` delegam; `Search` e `in` só em coluna de texto.

## Variações

- Ordenação por clique no cabeçalho: `ordenacao-coluna.md`.
- Linha que expande para detalhe: `linha-expansivel.md`.
- Seleção em lote: `selecao-em-lote.md`.
- Estado vazio e rodapé: `estado-vazio.md`, `rodape-contagem.md`.

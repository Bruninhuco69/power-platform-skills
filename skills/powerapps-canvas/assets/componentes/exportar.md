# Botão de exportar

Maturidade: **estável** · Frequência: **ocasional** (entrega por download ou por e-mail).

## Propósito

Botão que pede ao flow um arquivo com **todos** os registros do filtro atual (o flow lê no servidor, não a galeria truncada) e entrega por `Download(varRet.url)` ou por e-mail.

## Quando usar / quando não usar

**Use quando**

- o usuário precisa do conjunto completo do filtro, não do que cabe na tela;
- o arquivo é gerado no servidor.

**Não use quando**

- exportar só o que está na galeria (a galeria está truncada pelo limite do conector);
- gerar arquivo no cliente com `Concat` e `JSON`: não escala e perde acento.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-btn-exportar  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTextOnPrimary`, `fxColorPrimary`, `fxFont`, `fxBtnRadius`, `fxColorDisabled`, `fxColorDisabledText`, `fxBtnFontSize`, `fxMsgFalhaFlow`, `fxLayoutMargin`, `fxBtnWidth`, `fxBtnHeight`, `fxColorButtonCancel`, `fxColorButtonCancelHover`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxTxtExportar`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varShowLoading`, `varLoadingMessage`, `varRet`, `varUnidadeFiltro`, `varPedidoDe`, `varPedidoAte`, `varToastType`, `varToastMessage`, `varShowToast`.
- **Coleções**: nenhuma.
- **Flows**: `app-flow-pedido-exportar`.
- O flow lê no servidor com os filtros recebidos e devolve `{ status, description, id, url }`.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-btn-exportar:
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
          varShowLoading || 'xx-gal-pedidos'.AllItemsCount = 0,
          DisplayMode.Disabled,
          DisplayMode.Edit
        )
      Fill: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: |-
        =Set(varShowLoading, true);
        Set(varLoadingMessage, "Gerando arquivo...");
        IfError(
          Set(
            varRet,
            'app-flow-pedido-exportar'.Run(
              "csv",
              JSON(
                {
                  unidade: varUnidadeFiltro,
                  de: If(IsBlank(varPedidoDe), "", Text(DateAdd(Date(2000, 1, 1), varPedidoDe - 36524, TimeUnit.Days), "yyyy-mm-dd")),
                  ate: If(IsBlank(varPedidoAte), "", Text(DateAdd(Date(2000, 1, 1), varPedidoAte - 36524, TimeUnit.Days), "yyyy-mm-dd")),
                  status: Coalesce('xx-cbo-filtro-status'.Selected.Value, "")
                },
                JSONFormat.IgnoreUnsupportedTypes
              )
            )
          ),
          Trace("Falha de transporte no flow: " & FirstError.Message);
          Set(varRet, Blank())
        );
        Set(varShowLoading, false);
        Set(varToastType, Coalesce(varRet.status, "error"));
        Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
        Set(varShowToast, true);
        If(
          varToastType = "success" && !IsBlank(varRet.url),
          Download(varRet.url)
        )
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtExportar
      Tooltip: ="Gera o arquivo com todos os registros do filtro atual, lidos no servidor."
      Width: =fxBtnWidth
      X: =fxLayoutMargin + 1180 - 210
      Y: =16
```

### Variação: entrega por e-mail

O flow gera o arquivo e envia ao usuário logado; o toast confirma. Útil quando o arquivo é grande ou o navegador bloqueia o download.

```yaml
- xx-btn-exportar-email:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorButtonCancel
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      DisplayMode: =If(varShowLoading || 'xx-gal-pedidos'.AllItemsCount = 0, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: =fxColorButtonCancel
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =fxColorButtonCancelHover
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =fxColorButtonCancelHover
      OnSelect: |-
        =Set(varShowLoading, true);
        Set(varLoadingMessage, "Gerando arquivo e enviando...");
        IfError(
          Set(
            varRet,
            'app-flow-pedido-exportar'.Run("email", JSON(
              {
                unidade: varUnidadeFiltro,
                de: If(IsBlank(varPedidoDe), "", Text(DateAdd(Date(2000, 1, 1), varPedidoDe - 36524, TimeUnit.Days), "yyyy-mm-dd")),
                ate: If(IsBlank(varPedidoAte), "", Text(DateAdd(Date(2000, 1, 1), varPedidoAte - 36524, TimeUnit.Days), "yyyy-mm-dd")),
                status: Coalesce('xx-cbo-filtro-status'.Selected.Value, "")
              },
              JSONFormat.IgnoreUnsupportedTypes
            ))
          ),
          Trace("Falha de transporte no flow: " & FirstError.Message);
          Set(varRet, Blank())
        );
        Set(varShowLoading, false);
        Set(varToastType, Coalesce(varRet.status, "error"));
        Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
        Set(varShowToast, true)
      PressedBorderColor: =fxColorButtonCancelHover
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =fxColorButtonCancelHover
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="Enviar por e-mail"
      Width: =fxBtnWidth
      X: =fxLayoutMargin + 1180 - 210 - 220
      Y: =16
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `'app-flow-pedido-exportar'` | nome do flow no app | contrato de retorno `{ status, description, id, url }`, todos texto |
| `"csv"` | formato | vocabulário fechado do flow (`csv`, `xlsx`, `pdf`, `email`) |
| `unidade`, `de`, `ate`, `status` | filtros reais da tela | o flow **revalida** o escopo: a tela só manda o que o usuário vê; `de` e `ate` vão como texto `yyyy-mm-dd` (a variável da tela é o inteiro `Ref_*`, que o flow não entende) |
| `fxTxtExportar` | rótulo | token novo |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-btn-exportar`.DisplayMode**: desabilita sem registros ou com processamento em curso

```powerfx
If(
  varShowLoading || 'xx-gal-pedidos'.AllItemsCount = 0,
  DisplayMode.Disabled,
  DisplayMode.Edit
)
```

**`xx-btn-exportar`.OnSelect**: monta os filtros, chama o flow dentro de `IfError`, mostra o toast e baixa o arquivo só em sucesso

```powerfx
Set(varShowLoading, true);
Set(varLoadingMessage, "Gerando arquivo...");
IfError(
  Set(
    varRet,
    'app-flow-pedido-exportar'.Run(
      "csv",
      JSON(
        {
          unidade: varUnidadeFiltro,
          de: If(IsBlank(varPedidoDe), "", Text(DateAdd(Date(2000, 1, 1), varPedidoDe - 36524, TimeUnit.Days), "yyyy-mm-dd")),
          ate: If(IsBlank(varPedidoAte), "", Text(DateAdd(Date(2000, 1, 1), varPedidoAte - 36524, TimeUnit.Days), "yyyy-mm-dd")),
          status: Coalesce('xx-cbo-filtro-status'.Selected.Value, "")
        },
        JSONFormat.IgnoreUnsupportedTypes
      )
    )
  ),
  Trace("Falha de transporte no flow: " & FirstError.Message);
  Set(varRet, Blank())
);
Set(varShowLoading, false);
Set(varToastType, Coalesce(varRet.status, "error"));
Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
Set(varShowToast, true);
If(
  varToastType = "success" && !IsBlank(varRet.url),
  Download(varRet.url)
)
```

## Acessibilidade

- Rótulo de texto claro (`Exportar`); `Tooltip` explica o que sai.
- O resultado é anunciado pelo toast: considere reforçar o aviso de erro.

## Armadilhas

- `Download()` só abre no navegador; no aplicativo móvel o comportamento é outro: teste em cada cliente.
- Sem `IfError`, falha de transporte deixa o overlay preso.
- A URL de retorno vence: use link de curta duração e valide que `status = "success"` antes de baixar.
- Mandar o escopo da tela como autorização não adianta: o flow deriva o que o usuário pode exportar.

## Variações

- Formatos múltiplos: um botão por formato (`csv`, `pdf`), mesma função.
- Exportação em lote de uma seleção: mande os ids de `colSelecionados`.

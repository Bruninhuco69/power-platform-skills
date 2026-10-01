# Overlay de loading

Maturidade: **estável** · Frequência: **muito comum**.

## Propósito

Véu translúcido de tela cheia com um card central (spinner e mensagem) enquanto uma chamada de flow roda. Bloqueia cliques e some quando `varShowLoading` volta a `false`.

## Quando usar / quando não usar

**Use quando**

- toda chamada `.Run()` de flow;
- carga pesada de abertura de tela com mais de 1 segundo.

**Não use quando**

- a espera é de milissegundos (o spinner pisca);
- o loading é de um controle só (use o estado do botão).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-cmp-loading  (GroupContainer)
  xx-cmp-loading-bloqueio  (Button)
  xx-con-loading-card  (GroupContainer)
    xx-spn-loading  (Spinner)
    xx-lbl-loading-texto  (Label)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorOverlay`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxLoadingCardWidth`, `fxLoadingCardHeight`, `fxLoadingSpinnerSize`, `fxColorPrimary`, `fxFont`, `fxFontSizeBody`, `fxMsgLoadingDefault`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varShowLoading`, `varLoadingMessage`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-cmp-loading:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlay
      Height: =Parent.Height
      Visible: =varShowLoading
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-cmp-loading-bloqueio:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            Color: =fxColorTransparent
            Fill: =fxColorTransparent
            Height: =Parent.Height
            HoverFill: =fxColorTransparent
            OnSelect: =false
            PressedFill: =fxColorTransparent
            TabIndex: =-1
            Text: =""
            Width: =Parent.Width
            X: =0
            Y: =0
      - xx-con-loading-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =fxLoadingCardHeight
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxLoadingCardWidth
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-spn-loading:
                Control: Spinner@1.4.6
                Properties:
                  Height: =fxLoadingSpinnerSize
                  Width: =fxLoadingSpinnerSize
                  X: =(Parent.Width - Self.Width) / 2
                  Y: =20
            - xx-lbl-loading-texto:
                Control: Label@2.5.1
                Properties:
                  Align: =Align.Center
                  Color: =fxColorPrimary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =30
                  Size: =fxFontSizeBody
                  Text: =Coalesce(varLoadingMessage, fxMsgLoadingDefault)
                  Width: =Parent.Width - 20
                  X: =10
                  Y: =90
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-cmp-loading` | `xx-cmp-loading` com o prefixo da tela | bloco compartilhado sai **já prefixado**; sem prefixo o Studio renomeia para `_1` |
| `varLoadingMessage` | mensagem da operação | cai em `fxMsgLoadingDefault` quando vazia |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-cmp-loading`.Visible**: uma só variável global

```powerfx
varShowLoading
```

**`xx-lbl-loading-texto`.Text**: mensagem da operação, com padrão

```powerfx
Coalesce(varLoadingMessage, fxMsgLoadingDefault)
```

## Acessibilidade

- O véu bloqueia o clique (primeiro filho transparente com `OnSelect: =false`), evitando duplo envio.
- Mensagem em texto: "Processando, aguarde..." é o que um leitor de tela encontra ao navegar; não há `Live` atestado no `Label` (PA2108).

## Armadilhas

- Penúltimo em `Children` da tela, logo antes do toast; modal abaixo dele.
- `varShowLoading` não zerado por um erro no meio da cadeia deixa o overlay preso: toda `.Run()` está dentro de `IfError` e o `Set(varShowLoading, false)` vem **depois** dele.
- Estado inicial: `varShowLoading` nasce `false` no `OnStart`.
- O botão de ação também liga a `varShowLoading` (texto e `DisplayMode`).

## Variações

- Véu mais claro para operações curtas: troque `fxColorOverlay` por um token de véu branco.
- Mensagem por etapa: `Set(varLoadingMessage, ...)` entre as chamadas.

# Badge de status (pílula)

Maturidade: **estável** · Frequência: **comum** (pílula de status em linha de galeria; também como badge-botão de ação).

## Propósito

Marca visual do estado de uma linha: pílula arredondada de cor pastel com texto escuro da mesma matiz, sempre acompanhada do texto do estado (nunca só cor).

## Quando usar / quando não usar

**Use quando**

- coluna de status de galeria ou detalhe;
- o estado tem vocabulário fechado e curto.

**Não use quando**

- o estado é longo ou aberto (frase): use texto simples;
- o rótulo é ação do usuário: use o botão-badge (variação).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-shp-gal-status-pill  (Button)
xx-lbl-gal-status  (Label)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxBadgeInfoBg`, `fxBadgeProgressBg`, `fxBadgeSuccessBg`, `fxBadgeNeutralBg`, `fxModalPadding`, `fxBadgeInfoText`, `fxBadgeProgressText`, `fxBadgeSuccessText`, `fxBadgeNeutralText`, `fxFont`, `fxFontSizeTableSmall`, `fxBadgeWarningText`, `fxBadgeDangerText`, `fxColorBorder`, `fxBadgeWarningBg`, `fxBadgeDangerBg`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxPillHeight`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): nenhuma.
- **Coleções**: nenhuma.
- **Flows**: nenhum.
- Ambos os blocos vão no template de uma galeria (usam `ThisItem`).

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

Estes dois controles ficam **dentro do template da galeria** (`Children` de `xx-gal-pedidos`).

```yaml
- xx-shp-gal-status-pill:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorTransparent
      DisabledBorderColor: =fxColorTransparent
      DisabledFill: |-
        =Switch(
          ThisItem.<col-status>,
          "aberto", fxBadgeInfoBg,
          "em andamento", fxBadgeProgressBg,
          "encerrado", fxBadgeSuccessBg,
          fxBadgeNeutralBg
        )
      DisplayMode: =DisplayMode.Disabled
      Fill: |-
        =Switch(
          ThisItem.<col-status>,
          "aberto", fxBadgeInfoBg,
          "em andamento", fxBadgeProgressBg,
          "encerrado", fxBadgeSuccessBg,
          fxBadgeNeutralBg
        )
      Height: =fxPillHeight
      RadiusBottomLeft: =Self.Height / 2
      RadiusBottomRight: =Self.Height / 2
      RadiusTopLeft: =Self.Height / 2
      RadiusTopRight: =Self.Height / 2
      Text: =""
      Width: =134
      X: =Parent.TemplateWidth - fxModalPadding - 134
      Y: =(Parent.TemplateHeight - Self.Height) / 2
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
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxPillHeight
      Size: =fxFontSizeTableSmall
      Text: =ThisItem.<col-status>
      VerticalAlign: =VerticalAlign.Middle
      Width: =134
      X: ='xx-shp-gal-status-pill'.X
      Y: ='xx-shp-gal-status-pill'.Y
```

### Variação: badge de ação (botão)

Botão de ação em linha com cor derivada do próprio rótulo (`Self.Text`); hover escurece em todos.

```yaml
- xx-btn-gal-acao:
    Control: Classic/Button@2.2.0
    Properties:
      BorderStyle: =BorderStyle.None
      Color: |-
        =Switch(
          Self.Text,
          "Aprovar", fxBadgeSuccessText,
          "Revisar", fxBadgeWarningText,
          "Cancelar", fxBadgeDangerText,
          fxBadgeNeutralText
        )
      DisabledBorderColor: =fxColorBorder
      DisplayMode: =If(ThisItem.Bloqueado, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: |-
        =Switch(
          Self.Text,
          "Aprovar", fxBadgeSuccessBg,
          "Revisar", fxBadgeWarningBg,
          "Cancelar", fxBadgeDangerBg,
          fxBadgeNeutralBg
        )
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =35
      HoverFill: =ColorFade(Self.Fill, -12%)
      PressedFill: =ColorFade(Self.Fill, -24%)
      Size: =fxFontSizeTableSmall
      TabIndex: =0
      Text: ="Aprovar"
      Underline: =true
      Width: =88
      X: =1000
      Y: =8
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `<col-status>` | coluna real do estado |  |
| `"aberto"`, `"em andamento"`, `"encerrado"` | vocabulário real | um par `fxBadge*` por estado; o ramo final é o neutro |
| `Parent.TemplateWidth - fxModalPadding - 134` | posição da coluna | alinhe com o cabeçalho |
| `Aprovar`, `Revisar`, `Cancelar` | ações reais | variação botão |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-shp-gal-status-pill`.DisabledFill**: cor de fundo da pílula por estado (a forma é botão desabilitado)

```powerfx
Switch(
  ThisItem.<col-status>,
  "aberto", fxBadgeInfoBg,
  "em andamento", fxBadgeProgressBg,
  "encerrado", fxBadgeSuccessBg,
  fxBadgeNeutralBg
)
```

**`xx-lbl-gal-status`.Color**: cor do texto por estado

```powerfx
Switch(
  ThisItem.<col-status>,
  "aberto", fxBadgeInfoText,
  "em andamento", fxBadgeProgressText,
  "encerrado", fxBadgeSuccessText,
  fxBadgeNeutralText
)
```

## Acessibilidade

- Cada par `fxBadge*Text` sobre `fxBadge*Bg` tem contraste de 4,5:1.
- O texto do estado está sempre presente: a cor é reforço.
- A forma desabilitada não entra na ordem de tabulação.

## Armadilhas

- `Rectangle` não tem `Radius*`: a pílula é `Classic/Button` desabilitado com `DisabledFill`.
- `Self.Height / 2` no raio mantém a pílula redonda se a altura mudar.
- Vocabulário novo do banco cai no ramo neutro: se todos aparecerem como "encerrado", o ramo final está trocado.
- Hover precisa **escurecer** em todos os botões; clarear num e escurecer noutro é inconsistência.

## Variações

- Badge só de texto (um `Label` com `Fill` e `Color` por `Switch`): como em `galeria-tabela.md`.
- Badge de contagem no menu: `Label` com raio via botão desabilitado.

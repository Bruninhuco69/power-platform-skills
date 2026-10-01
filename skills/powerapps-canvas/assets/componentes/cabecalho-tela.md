# Cabeçalho de tela

Maturidade: **estável** · Frequência: **muito comum** (toda tela de conteúdo; uma tela só de atalhos pode dispensá-lo).

## Propósito

Faixa fixa no topo de toda tela: título, usuário logado e divisor. Dá ao usuário o "onde estou" e ancora o grid vertical: tudo o mais começa em `fxHeaderHeight`.

## Quando usar / quando não usar

**Use quando**

- toda tela de conteúdo, sem exceção;
- o app tem mais de uma tela e o usuário precisa saber em qual está.

**Não use quando**

- a tela é um overlay ou modal (use o card do modal);
- o título já aparece no menu lateral e a tela é só um painel embutido.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-con-header  (GroupContainer)
  xx-lbl-header-titulo  (Label)
  xx-lbl-header-usuario  (Label)
  xx-rec-header-divisor  (Rectangle)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorSurface`, `fxColorPrimary`, `fxFont`, `fxFontSizeTitle`, `fxLayoutMargin`, `fxColorTextSecondary`, `fxFontSizeBody`, `fxColorDivider`, `fxFontSizeTableSmall`, `fxLayoutGutter`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxHeaderHeight`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varAgora`, `varTelaAtiva`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-con-header:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorSurface
      Height: =fxHeaderHeight
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-lbl-header-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =60
            Size: =fxFontSizeTitle
            Text: ="Título da tela"
            VerticalAlign: =VerticalAlign.Middle
            Width: =700
            X: =fxLayoutMargin
            Y: =20
      - xx-lbl-header-usuario:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Right
            Color: =fxColorTextSecondary
            Font: =fxFont
            Height: =24
            Size: =fxFontSizeBody
            Text: =User().FullName
            Width: =320
            X: =Parent.Width - fxLayoutMargin - Self.Width
            Y: =30
      - xx-rec-header-divisor:
          Control: Rectangle@2.3.0
          Properties:
            BorderStyle: =BorderStyle.None
            Fill: =fxColorDivider
            Height: =1
            Width: =Parent.Width
            X: =0
            Y: =fxHeaderHeight - 1
```

### Variação: relógio (data e hora)

`Now()` direto na propriedade `Text` é volátil e reavalia a cada recálculo; o relógio lê `varAgora`, atualizada por timer a cada 30 s (precisão de minuto basta no formato `hh:mm`).

```yaml
- xx-lbl-header-datahora:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Right
      Color: =fxColorTextSecondary
      Font: =fxFont
      Height: =20
      Size: =fxFontSizeTableSmall
      Text: =Text(varAgora, "[$-pt-BR]dd/mm/yyyy hh:mm")
      Width: =220
      X: =Parent.Width - fxLayoutMargin - Self.Width
      Y: =56
- xx-tim-header-relogio:
    Control: Timer@2.1.0
    Properties:
      Duration: =30000
      OnTimerEnd: =Set(varAgora, Now())
      Repeat: =true
      Start: =varTelaAtiva = "pedidos"
      Visible: =false
```

### Variação: com logo

Troque `xx-lbl-header-titulo` por este par. A imagem vem do recurso de mídia do app (Mídia > Adicionar); o texto alternativo é o título ao lado.

```yaml
- xx-img-header-logo:
    Control: Image@2.2.3
    Properties:
      DisplayMode: =DisplayMode.View
      Height: =60
      Image: ='<imagem-logo>'
      Width: =160
      X: =fxLayoutMargin
      Y: =20
- xx-lbl-header-titulo-logo:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =60
      Size: =fxFontSizeTitle
      Text: ="Título da tela"
      VerticalAlign: =VerticalAlign.Middle
      Width: =700
      X: =fxLayoutMargin + 160 + fxLayoutGutter
      Y: =20
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-` | prefixo de 2 letras da tela | nome de controle é único no app inteiro |
| `"Título da tela"` | nome da tela | o mesmo texto de `varTelaAtiva`/menu, para não divergir |
| `User().FullName` | campo do perfil se existir um nome de exibição próprio | ex.: `varUsuario.Nom_Usuario` |
| `varTelaAtiva = "pedidos"` (relógio) | o identificador da tela | o timer só roda com a tela ativa |
| `'<imagem-logo>'` | nome do recurso de mídia | variação com logo |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-lbl-header-titulo`.Text**: título fixo, sem fórmula

```powerfx
"Título da tela"
```

**`xx-lbl-header-usuario`.Text**: nome do usuário do Entra

```powerfx
User().FullName
```

## Acessibilidade

- Título é o primeiro texto lido pelo leitor de tela na ordem de tabulação: mantenha o título como primeiro filho.
- Cor do título (`fxColorPrimary` sobre `fxColorSurface`) e do usuário (`fxColorTextSecondary`) passam de 4,5:1; se trocar a marca, reconfira.
- Imagem de logo decorativa: sem texto alternativo próprio, o título ao lado cumpre o papel.

## Armadilhas

- Posição do título (esquerda ou centralizada): escolha **uma** por app.
- `Now()` direto no `Text` do relógio: mantém a propriedade volátil e pesa o recálculo da tela.
- O relógio só anda em Preview (`F5`): no canvas de edição o timer não corre.
- Com menu lateral, use `X: =fxContentX` e `Width: =fxContentWidth` no contêiner em vez de `0` e `Parent.Width`.

## Variações

- Com subtítulo: um `Label` de `fxFontSizeBody` abaixo do título, `Y: =68`.
- Com seletor de unidade na faixa: ver `seletor-unidade.md`.
- Sem usuário (tela pública): remova `xx-lbl-header-usuario`.

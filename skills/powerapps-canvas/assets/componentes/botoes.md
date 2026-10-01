# Botões: primário, secundário, destrutivo e neutro

Maturidade: **estável** · Frequência: **muito comum**.

## Propósito

Os quatro papéis de botão com a mesma geometria (`fxBtnHeight`, `fxBtnRadius`), hover que escurece e pressed que nunca inverte `Fill` e `Color`.

## Quando usar / quando não usar

**Use quando**

- qualquer botão de ação: escolha o papel pela natureza da ação, nunca pelo texto;
- um novo botão do app: parta daqui.

**Não use quando**

- botão dentro de galeria com altura de linha (use altura 30 a 34 e `fxFontSizeTableSmall`);
- navegação do menu (use `menu-lateral.md`).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-btn-primario  (Button)
xx-btn-secundario  (Button)
xx-btn-destrutivo  (Button)
xx-btn-neutro  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTextOnPrimary`, `fxColorPrimary`, `fxFont`, `fxBtnRadius`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtConfirmar`, `fxBtnFontSize`, `fxBtnWidth`, `fxBtnHeight`, `fxColorButtonCancel`, `fxColorButtonCancelHover`, `fxTxtCancelar`, `fxColorError`, `fxColorTableHeaderText`, `fxColorPrimaryLight`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varShowLoading`, `varMostrarConfirmar`, `varMostrarCancelar`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-btn-primario:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =Self.Fill
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      DisabledBorderColor: =fxColorDisabled
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      DisplayMode: =If(varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: |-
        =Set(varShowLoading, true);
        Set(varShowLoading, false)
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtConfirmar
      Width: =fxBtnWidth
      X: =20
      Y: =20
- xx-btn-secundario:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorButtonCancel
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      Fill: =fxColorButtonCancel
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =fxColorButtonCancelHover
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =fxColorButtonCancelHover
      OnSelect: =Set(varMostrarConfirmar, false)
      PressedBorderColor: =fxColorButtonCancelHover
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =fxColorButtonCancelHover
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtCancelar
      Width: =fxBtnWidth
      X: =20
      Y: =20
- xx-btn-destrutivo:
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
          Len(Trim('xx-txt-motivo'.Text)) < 5,
          DisplayMode.Disabled,
          DisplayMode.Edit
        )
      Fill: =fxColorError
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: =Set(varMostrarCancelar, false)
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="Confirmar cancelamento"
      Width: =230
      X: =20
      Y: =20
- xx-btn-neutro:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =ColorFade(Self.Fill, -15%)
      Color: =fxColorTableHeaderText
      Fill: =fxColorPrimaryLight
      Font: =fxFont
      Height: =fxBtnHeight
      HoverFill: =ColorFade(Self.Fill, -10%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="Rótulo curto"
      Width: =140
      X: =20
      Y: =20
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `fxTxtConfirmar`, `fxTxtCancelar` | verbo da ação | no modal, o direito é o verbo (`Salvar`, `Encerrar`), o esquerdo `Voltar` |
| `'xx-txt-motivo'` | campo de motivo | regra do destrutivo; troque o mínimo de 5 |
| `X`, `Y`, `Width` | posição real | o primário ocupa a **mesma posição** em todas as telas |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-btn-primario`.DisplayMode**: desabilita durante o processamento

```powerfx
If(varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
```

**`xx-btn-destrutivo`.DisplayMode**: habilita só com motivo

```powerfx
If(
  Len(Trim('xx-txt-motivo'.Text)) < 5,
  DisplayMode.Disabled,
  DisplayMode.Edit
)
```

## Acessibilidade

- Botão de ícone: sem `AccessibleLabel` (PA2108 em `Classic/Button@2.2.0`); use `Tooltip` e texto descritivo.
- `Disabled*` sempre definidos: texto desabilitado precisa ser distinguível do habilitado.
- `TabIndex: =0` em todos: ordem natural da tela.

## Armadilhas

- **Pressed** nunca inverte `Fill` e `Color` (botão branco sobre branco some ao pressionar): use `ColorFade(Self.Fill, -30%)`.
- **Hover** escurece em todos os botões: nunca clareia num e escurece noutro.
- Verde é estado, nunca ação; ação destrutiva é sempre `fxColorError`.
- Sem emoji como semântica (`✅ Sim`, `❌ Cancelar`).
- `Radius*` em `Classic/Button@2.2.0` é aceito; em `Rectangle`, `ComboBox` e `DatePicker` não.

## Variações

- Botão de filtro: altura `fxFilterHeight` e largura `fxBtnWidthFilter` (ver `barra-filtros.md`).
- Botão com estado de carregamento: `Text: =If(varShowLoading, fxTxtProcessando, <verbo>)`.

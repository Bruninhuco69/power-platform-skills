# Modal de formulário

Maturidade: **estável** · Frequência: **comum**.

## Propósito

Véu e card maior com campos (combo, busca e texto longo), mensagem de validação em um só ponto e o par `Cancelar`/verbo. O botão de confirmar só habilita quando a validação fica vazia.

## Quando usar / quando não usar

**Use quando**

- criar ou editar um registro com poucos campos (até uns 8);
- a validação é local e simples.

**Não use quando**

- o formulário tem muitos campos ou passos (use uma tela dedicada: é também a recomendação de acessibilidade);
- o fluxo precisa de URL própria.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-mod-form  (GroupContainer)
  xx-mod-form-bloqueio  (Button)
  xx-mod-form-card  (GroupContainer)
    xx-mod-form-titulo  (Label)
    xx-mod-form-lbl-tipo  (Label)
    xx-cbo-form-tipo  (ComboBox)
    xx-mod-form-lbl-item  (Label)
    xx-cbo-form-item  (ComboBox)
    xx-mod-form-lbl-descricao  (Label)
    xx-txt-form-descricao  (TextInput)
    xx-mod-form-lbl-validacao  (Label)
    xx-mod-form-btn-voltar  (Button)
    xx-mod-form-btn-confirmar  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorOverlayDark`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxColorPrimaryDark`, `fxFont`, `fxModalTitleSize`, `fxModalPadding`, `fxColorTextSecondary`, `fxFontSizeHeader`, `fxColorBorderInteractive`, `fxColorTextPrimary`, `fxColorPrimary`, `fxFilterHeight`, `fxFontSizeFilter`, `fxBtnRadius`, `fxColorError`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxTxtCancelar`, `fxBtnFontSize`, `fxBtnHeight`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtProcessando`, `fxTxtSalvar`, `fxMsgFalhaFlow`, `fxLayoutMargin`, `fxLayoutGutter`, `fxBtnWidth`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxModalWidthL`, `fxHeaderHeight`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varMostrarForm`, `varUnidadeFiltro`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType`, `varToastMessage`, `varShowToast`, `varPedidoTotal`, `varPerfil`.
- **Coleções**: nenhuma.
- **Flows**: `app-flow-pedido-acao`.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-mod-form:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlayDark
      Height: =Parent.Height
      Visible: =varMostrarForm
      Width: =Parent.Width
    Children:
      - xx-mod-form-bloqueio:
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
      - xx-mod-form-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =470
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxModalWidthL
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-mod-form-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorPrimaryDark
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =32
                  Size: =fxModalTitleSize
                  Text: ="Novo pedido"
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =fxModalPadding
            - xx-mod-form-lbl-tipo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =20
                  Size: =fxFontSizeHeader
                  Text: ="Tipo"
                  Width: =270
                  X: =fxModalPadding
                  Y: =70
            - xx-cbo-form-tipo:
                Control: Classic/ComboBox@2.4.0
                Properties:
                  BorderColor: =fxColorBorderInteractive
                  Color: =fxColorTextPrimary
                  DisplayFields: =["Value"]
                  FocusedBorderColor: =fxColorPrimary
                  Height: =fxFilterHeight
                  InputTextPlaceholder: ="Selecione o tipo"
                  IsSearchable: =false
                  Items: =["Padrão", "Urgente", "Outros"]
                  SearchFields: =["Value"]
                  SelectMultiple: =false
                  Width: =270
                  X: =fxModalPadding
                  Y: =94
            - xx-mod-form-lbl-item:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =20
                  Size: =fxFontSizeHeader
                  Text: ="Item"
                  Width: =280
                  X: =320
                  Y: =70
            - xx-cbo-form-item:
                Control: Classic/ComboBox@2.4.0
                Properties:
                  BorderColor: =fxColorBorderInteractive
                  Color: =fxColorTextPrimary
                  DisplayFields: =["<col-codigo>"]
                  FocusedBorderColor: =fxColorPrimary
                  Height: =fxFilterHeight
                  InputTextPlaceholder: ="Busque pelo código"
                  Items: |-
                    =Sort(
                      Filter('<fonte-item>', StartsWith(<col-unidade>, varUnidadeFiltro)),
                      <col-codigo>
                    )
                  SearchFields: =["<col-codigo>"]
                  SelectMultiple: =false
                  Width: =280
                  X: =320
                  Y: =94
            - xx-mod-form-lbl-descricao:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =20
                  Size: =fxFontSizeHeader
                  Text: ="Descrição"
                  Width: =580
                  X: =fxModalPadding
                  Y: =166
            - xx-txt-form-descricao:
                Control: Classic/TextInput@2.3.2
                Properties:
                  BorderColor: =fxColorBorderInteractive
                  Color: =fxColorTextPrimary
                  Default: =""
                  FocusedBorderColor: =fxColorPrimary
                  Font: =fxFont
                  Height: =140
                  HintText: ="Mínimo de 10 caracteres"
                  MaxLength: =1000
                  Mode: =TextMode.MultiLine
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxFontSizeFilter
                  TabIndex: =0
                  Width: =580
                  X: =fxModalPadding
                  Y: =190
            - xx-mod-form-lbl-validacao:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorError
                  Font: =fxFont
                  Height: =24
                  Size: =fxFontSizeFilter
                  Text: |-
                    =If(
                      IsBlank('xx-cbo-form-tipo'.Selected),
                      "Selecione o tipo.",
                      IsBlank('xx-cbo-form-item'.Selected),
                      "Selecione o item.",
                      Len(Trim('xx-txt-form-descricao'.Text)) < 10,
                      "Descreva com pelo menos 10 caracteres.",
                      ""
                    )
                  Width: =580
                  X: =fxModalPadding
                  Y: =338
            - xx-mod-form-btn-voltar:
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
                  OnSelect: =Set(varMostrarForm, false)
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
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
            - xx-mod-form-btn-confirmar:
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
                      varShowLoading || !IsBlank('xx-mod-form-lbl-validacao'.Text),
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
                    Set(varLoadingMessage, "Criando pedido...");
                    IfError(
                      Set(
                        varRet,
                        'app-flow-pedido-acao'.Run(
                          "criar",
                          "",
                          Text('xx-cbo-form-item'.Selected.<col-id>, "[$-en-US]0"),
                          'xx-cbo-form-tipo'.Selected.Value,
                          Trim('xx-txt-form-descricao'.Text),
                          Lower(User().Email)
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
                      varToastType <> "error",
                      Set(varMostrarForm, false);
                      Refresh('<fonte>');
                      Set(
                        varPedidoTotal,
                        CountRows(Filter('<fonte>', StartsWith(<col-unidade>, varUnidadeFiltro)))
                      )
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
                  Text: =If(varShowLoading, fxTxtProcessando, fxTxtSalvar)
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =Parent.Width - Self.Width - fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
```

### Botão que abre o modal

`Reset()` de cada controle **antes** de abrir, para não herdar o valor da vez anterior.

```yaml
- xx-btn-novo:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =Self.Fill
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      DisabledBorderColor: =fxColorDisabled
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      Fill: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: |-
        =Reset('xx-cbo-form-tipo');
        Reset('xx-cbo-form-item');
        Reset('xx-txt-form-descricao');
        Set(varMostrarForm, true)
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="Novo pedido"
      Visible: =varPerfil.Flg_Cria
      Width: =fxBtnWidth
      X: =fxLayoutMargin
      Y: =fxHeaderHeight + fxLayoutGutter
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-mod-form`, `varMostrarForm` | `xx-mod-<acao>` e `varMostrar<Acao>` |  |
| `'<fonte-item>'`, `<col-codigo>`, `<col-unidade>` | tabela e colunas reais | Items do combo delegável (`Filter` com `StartsWith`) |
| `["Padrão", "Urgente", "Outros"]` | domínio real do tipo |  |
| `Trim(...)`, `Lower(User().Email)` | parâmetros reais do flow | o flow valida de novo: a tela só facilita |
| `'app-flow-pedido-acao'` | nome do flow no app | parâmetros posicionais, todos texto; parâmetro novo entra sempre no fim |
| `"encerrar"`, `<col-id>` | ação e id reais | id numérico vai como `Text(id, "[$-en-US]0")` |
| `'<fonte>'`, `<col-unidade>` | tabela e coluna reais | o `Refresh` e a recontagem fecham o ciclo de gravação |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-mod-form-lbl-validacao`.Text**: devolve a **primeira** pendência; vazio quando o formulário está pronto

```powerfx
If(
  IsBlank('xx-cbo-form-tipo'.Selected),
  "Selecione o tipo.",
  IsBlank('xx-cbo-form-item'.Selected),
  "Selecione o item.",
  Len(Trim('xx-txt-form-descricao'.Text)) < 10,
  "Descreva com pelo menos 10 caracteres.",
  ""
)
```

**`xx-mod-form-btn-confirmar`.DisplayMode**: desabilitado enquanto há pendência ou processamento

```powerfx
If(
  varShowLoading || !IsBlank('xx-mod-form-lbl-validacao'.Text),
  DisplayMode.Disabled,
  DisplayMode.Edit
)
```

**`xx-mod-form-btn-confirmar`.OnSelect**: chama o flow; fecha só se não houve erro

```powerfx
Set(varShowLoading, true);
Set(varLoadingMessage, "Criando pedido...");
IfError(
  Set(
    varRet,
    'app-flow-pedido-acao'.Run(
      "criar",
      "",
      Text('xx-cbo-form-item'.Selected.<col-id>, "[$-en-US]0"),
      'xx-cbo-form-tipo'.Selected.Value,
      Trim('xx-txt-form-descricao'.Text),
      Lower(User().Email)
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
  varToastType <> "error",
  Set(varMostrarForm, false);
  Refresh('<fonte>');
  Set(
    varPedidoTotal,
    CountRows(Filter('<fonte>', StartsWith(<col-unidade>, varUnidadeFiltro)))
  )
)
```

## Acessibilidade

- Limitação oficial: diálogo e overlay não são suportados pelo leitor de tela (a Microsoft recomenda tela separada ou `Notify()`). A mitigação do padrão é o botão `Voltar` sempre presente e na ordem de tabulação.
- O botão de confirmar muda de texto e fica desabilitado durante o processamento (`varShowLoading`).
- Rótulo visível acima de cada campo; obrigatório declarado no texto ("Tipo" na validação), não só por `*`.
- A pendência aparece em texto, em `fxColorError`, ao lado do botão desabilitado.

## Armadilhas

- Validação duplicada no cliente e no flow diverge com o tempo: o cliente só evita a ida e volta, o flow decide.
- `Mode: =TextMode.MultiLine` é propriedade atestada de `Classic/TextInput`; não invente `Mode` em outros tipos.
- Sem `Reset` ao abrir, o formulário reabre com o que o usuário digitou antes e desistiu.
- Combo com `Items` sobre fonte grande precisa de `IsSearchable: =true` e predicado delegável.

## Variações

- Formulário de edição: preencha por `Default`/`DefaultSelectedItems` do registro em `varPedidoSel`.
- Erro por campo (sob o campo, depois da primeira tentativa): padrão de `ux-componentes.md` §14.

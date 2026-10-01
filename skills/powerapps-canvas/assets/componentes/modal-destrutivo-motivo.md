# Modal destrutivo com motivo obrigatório

Maturidade: **estável** · Frequência: **ocasional**.

## Propósito

Modal para ação irreversível: título e botão em `fxColorError`, campo de motivo obrigatório e botão desabilitado até o motivo ter o tamanho mínimo. O motivo vai ao flow para auditoria.

## Quando usar / quando não usar

**Use quando**

- cancelar, excluir ou estornar algo que não volta;
- a regra pede justificativa registrada.

**Não use quando**

- ação reversível (use `modal-confirmacao.md`);
- a justificativa não é exigida por regra.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-mod-cancelar  (GroupContainer)
  xx-mod-cancelar-bloqueio  (Button)
  xx-mod-cancelar-card  (GroupContainer)
    xx-mod-cancelar-titulo  (Label)
    xx-mod-cancelar-mensagem  (Label)
    xx-mod-cancelar-lbl-motivo  (Label)
    xx-txt-cancelar-motivo  (TextInput)
    xx-mod-cancelar-btn-voltar  (Button)
    xx-mod-cancelar-btn-confirmar  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorOverlayDark`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxColorError`, `fxFont`, `fxModalTitleSize`, `fxModalPadding`, `fxColorTextBody`, `fxFontSizeBody`, `fxColorTextSecondary`, `fxFontSizeHeader`, `fxColorBorderInteractive`, `fxColorPrimary`, `fxColorTextPrimary`, `fxFontSizeFilter`, `fxBtnRadius`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxTxtVoltar`, `fxBtnFontSize`, `fxBtnHeight`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtProcessando`, `fxMsgFalhaFlow`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxModalWidthM`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varMostrarCancelar`, `varPedidoSel`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType`, `varToastMessage`, `varShowToast`, `varPedidoTotal`, `varUnidadeFiltro`.
- **Coleções**: nenhuma.
- **Flows**: `app-flow-pedido-acao`.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-mod-cancelar:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlayDark
      Height: =Parent.Height
      Visible: =varMostrarCancelar
      Width: =Parent.Width
    Children:
      - xx-mod-cancelar-bloqueio:
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
      - xx-mod-cancelar-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =340
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxModalWidthM
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-mod-cancelar-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorError
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =32
                  Size: =fxModalTitleSize
                  Text: ="Cancelar o pedido"
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =fxModalPadding
            - xx-mod-cancelar-mensagem:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextBody
                  Font: =fxFont
                  Height: =48
                  Size: =fxFontSizeBody
                  Text: ="O pedido " & varPedidoSel.<col-codigo> & " será cancelado e não poderá ser reaberto."
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =56
            - xx-mod-cancelar-lbl-motivo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextSecondary
                  Font: =fxFont
                  FontWeight: =FontWeight.Semibold
                  Height: =20
                  Size: =fxFontSizeHeader
                  Text: ="Motivo (obrigatório)"
                  Width: =300
                  X: =fxModalPadding
                  Y: =110
            - xx-txt-cancelar-motivo:
                Control: Classic/TextInput@2.3.2
                Properties:
                  BorderColor: =If(IsBlank(Self.Text), fxColorBorderInteractive, fxColorPrimary)
                  Color: =fxColorTextPrimary
                  Default: =""
                  FocusedBorderColor: =fxColorPrimary
                  Font: =fxFont
                  Height: =80
                  HintText: ="Descreva o motivo (mínimo de 5 caracteres)"
                  MaxLength: =500
                  Mode: =TextMode.MultiLine
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxFontSizeFilter
                  TabIndex: =0
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =134
            - xx-mod-cancelar-btn-voltar:
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
                  OnSelect: |-
                    =Set(varMostrarCancelar, false);
                    Set(varPedidoSel, Blank())
                  PressedBorderColor: =fxColorButtonCancelHover
                  PressedColor: =fxColorTextOnPrimary
                  PressedFill: =fxColorButtonCancelHover
                  RadiusBottomLeft: =fxBtnRadius
                  RadiusBottomRight: =fxBtnRadius
                  RadiusTopLeft: =fxBtnRadius
                  RadiusTopRight: =fxBtnRadius
                  Size: =fxBtnFontSize
                  TabIndex: =0
                  Text: =fxTxtVoltar
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
            - xx-mod-cancelar-btn-confirmar:
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
                      varShowLoading || Len(Trim('xx-txt-cancelar-motivo'.Text)) < 5,
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
                  OnSelect: |-
                    =Set(varShowLoading, true);
                    Set(varLoadingMessage, "Cancelando pedido...");
                    IfError(
                      Set(
                        varRet,
                        'app-flow-pedido-acao'.Run(
                          "cancelar",
                          Text(varPedidoSel.<col-id>, "[$-en-US]0"),
                          Trim('xx-txt-cancelar-motivo'.Text)
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
                      Set(varMostrarCancelar, false);
                      Set(varPedidoSel, Blank());
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
                  Text: =If(varShowLoading, fxTxtProcessando, "Confirmar cancelamento")
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =Parent.Width - Self.Width - fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-mod-cancelar`, `varMostrarCancelar` | `xx-mod-<acao>` e `varMostrar<Acao>` |  |
| `5` | tamanho mínimo do motivo | o mesmo valor no flow |
| `"Confirmar cancelamento"` | verbo explícito da ação destrutiva | nunca `Sim` nem `Cancelar` para executar ("Cancelar" é sair) |
| `'app-flow-pedido-acao'` | nome do flow no app | parâmetros posicionais, todos texto; parâmetro novo entra sempre no fim |
| `"encerrar"`, `<col-id>` | ação e id reais | id numérico vai como `Text(id, "[$-en-US]0")` |
| `'<fonte>'`, `<col-unidade>` | tabela e coluna reais | o `Refresh` e a recontagem fecham o ciclo de gravação |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-mod-cancelar-btn-confirmar`.DisplayMode**: habilita só com motivo de 5 ou mais caracteres e sem processamento em curso

```powerfx
If(
  varShowLoading || Len(Trim('xx-txt-cancelar-motivo'.Text)) < 5,
  DisplayMode.Disabled,
  DisplayMode.Edit
)
```

**`xx-mod-cancelar-btn-confirmar`.OnSelect**: envia o id e o motivo ao flow; fecha só em sucesso

```powerfx
Set(varShowLoading, true);
Set(varLoadingMessage, "Cancelando pedido...");
IfError(
  Set(
    varRet,
    'app-flow-pedido-acao'.Run(
      "cancelar",
      Text(varPedidoSel.<col-id>, "[$-en-US]0"),
      Trim('xx-txt-cancelar-motivo'.Text)
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
  Set(varMostrarCancelar, false);
  Set(varPedidoSel, Blank());
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
- O botão esquerdo é `Voltar` (desistir) e o direito é o verbo da ação: "Cancelar" nunca significa as duas coisas.

## Armadilhas

- Verde confirmando ação destrutiva foi defeito real: destrutivo é sempre `fxColorError`.
- O motivo é validado de novo no flow; o cliente só evita a ida e volta.
- Limpar o motivo ao abrir: o botão que abre o modal faz `Reset('xx-txt-cancelar-motivo')`.
- Sem foco automático no campo: não há `SetFocus` em Classic; deixe o campo primeiro na ordem de tabulação.

## Variações

- Cancelamento em lote: o texto da mensagem usa `CountRows(colSelecionados)` (ver `selecao-em-lote.md`).
- Sem motivo: use `modal-confirmacao.md` com `fxColorError` no botão.

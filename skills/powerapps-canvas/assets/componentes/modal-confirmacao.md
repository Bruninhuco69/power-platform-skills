# Modal de confirmação

Maturidade: **estável** · Frequência: **ocasional**.

## Propósito

Véu e card centralizados que pedem confirmação de uma ação antes de chamar o flow. Esquerda `Voltar`, direita o verbo da ação; sucesso fecha o modal, erro o mantém aberto.

## Quando usar / quando não usar

**Use quando**

- ação com efeito no servidor que o usuário pode querer desfazer na hora;
- um clique acidental teria custo.

**Não use quando**

- ação destrutiva com motivo obrigatório (use `modal-destrutivo-motivo.md`);
- a ação é trivial e reversível (use toast com desfazer).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-mod-confirmar  (GroupContainer)
  xx-mod-confirmar-bloqueio  (Button)
  xx-mod-confirmar-card  (GroupContainer)
    xx-mod-confirmar-titulo  (Label)
    xx-mod-confirmar-mensagem  (Label)
    xx-mod-confirmar-btn-voltar  (Button)
    xx-mod-confirmar-btn-confirmar  (Button)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorOverlayDark`, `fxColorBorder`, `fxColorSurface`, `fxModalRadius`, `fxColorPrimaryDark`, `fxFont`, `fxModalTitleSize`, `fxModalPadding`, `fxColorTextBody`, `fxFontSizeBody`, `fxColorButtonCancel`, `fxColorTextOnPrimary`, `fxColorButtonCancelHover`, `fxBtnRadius`, `fxTxtVoltar`, `fxBtnFontSize`, `fxBtnHeight`, `fxColorPrimary`, `fxColorDisabled`, `fxColorDisabledText`, `fxTxtProcessando`, `fxTxtEncerrar`, `fxMsgFalhaFlow`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxModalWidthS`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varMostrarConfirmar`, `varPedidoSel`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType`, `varToastMessage`, `varShowToast`, `varPedidoTotal`, `varUnidadeFiltro`.
- **Coleções**: nenhuma.
- **Flows**: `app-flow-pedido-acao`.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-mod-confirmar:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorOverlayDark
      Height: =Parent.Height
      Visible: =varMostrarConfirmar
      Width: =Parent.Width
    Children:
      - xx-mod-confirmar-bloqueio:
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
      - xx-mod-confirmar-card:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            BorderColor: =fxColorBorder
            DropShadow: =DropShadow.Bold
            Fill: =fxColorSurface
            Height: =240
            RadiusBottomLeft: =fxModalRadius
            RadiusBottomRight: =fxModalRadius
            RadiusTopLeft: =fxModalRadius
            RadiusTopRight: =fxModalRadius
            Width: =fxModalWidthS
            X: =(Parent.Width - Self.Width) / 2
            Y: =(Parent.Height - Self.Height) / 2
          Children:
            - xx-mod-confirmar-titulo:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorPrimaryDark
                  Font: =fxFont
                  FontWeight: =FontWeight.Bold
                  Height: =32
                  Size: =fxModalTitleSize
                  Text: ="Encerrar o pedido"
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =fxModalPadding
            - xx-mod-confirmar-mensagem:
                Control: Label@2.5.1
                Properties:
                  Color: =fxColorTextBody
                  Font: =fxFont
                  Height: =80
                  Size: =fxFontSizeBody
                  Text: ="Confirma o encerramento do pedido " & varPedidoSel.<col-codigo> & "?"
                  Width: =Parent.Width - fxModalPadding * 2
                  X: =fxModalPadding
                  Y: =70
            - xx-mod-confirmar-btn-voltar:
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
                    =Set(varMostrarConfirmar, false);
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
            - xx-mod-confirmar-btn-confirmar:
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
                    Set(varLoadingMessage, "Encerrando...");
                    IfError(
                      Set(
                        varRet,
                        'app-flow-pedido-acao'.Run(
                          "encerrar",
                          Text(varPedidoSel.<col-id>, "[$-en-US]0")
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
                      Set(varMostrarConfirmar, false);
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
                  Text: =If(varShowLoading, fxTxtProcessando, fxTxtEncerrar)
                  Width: =(Parent.Width - fxModalPadding * 3) / 2
                  X: =Parent.Width - Self.Width - fxModalPadding
                  Y: =Parent.Height - Self.Height - fxModalPadding
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-mod-confirmar` | `xx-mod-<acao>` | um modal por ação |
| `varMostrarConfirmar` | `varMostrar<Acao>` | **uma** variável por modal; `Visible` de uma só variável |
| `"Encerrar o pedido"`, `fxTxtEncerrar` | título e verbo | verbo da ação; nunca `Sim`/`Confirmar` genérico em ação irreversível |
| `'app-flow-pedido-acao'` | nome do flow no app | parâmetros posicionais, todos texto; parâmetro novo entra sempre no fim |
| `"encerrar"`, `<col-id>` | ação e id reais | id numérico vai como `Text(id, "[$-en-US]0")` |
| `'<fonte>'`, `<col-unidade>` | tabela e coluna reais | o `Refresh` e a recontagem fecham o ciclo de gravação |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-mod-confirmar-btn-confirmar`.OnSelect**: loading, chamada protegida por `IfError`, toast; só fecha se `status <> "error"`; depois `Refresh` e recontagem

```powerfx
Set(varShowLoading, true);
Set(varLoadingMessage, "Encerrando...");
IfError(
  Set(
    varRet,
    'app-flow-pedido-acao'.Run(
      "encerrar",
      Text(varPedidoSel.<col-id>, "[$-en-US]0")
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
  Set(varMostrarConfirmar, false);
  Set(varPedidoSel, Blank());
  Refresh('<fonte>');
  Set(
    varPedidoTotal,
    CountRows(Filter('<fonte>', StartsWith(<col-unidade>, varUnidadeFiltro)))
  )
)
```

**`xx-mod-confirmar-btn-voltar`.OnSelect**: fecha e **limpa o estado** (a próxima abertura não mostra dado velho)

```powerfx
Set(varMostrarConfirmar, false);
Set(varPedidoSel, Blank())
```

## Acessibilidade

- Limitação oficial: diálogo e overlay não são suportados pelo leitor de tela (a Microsoft recomenda tela separada ou `Notify()`). A mitigação do padrão é o botão `Voltar` sempre presente e na ordem de tabulação.
- O botão de confirmar muda de texto e fica desabilitado durante o processamento (`varShowLoading`).

## Armadilhas

- `GroupContainer` não é clicável: o véu não bloqueia clique sozinho. O primeiro filho (`xx-mod-confirmar-bloqueio`) é um botão transparente de tela cheia com `OnSelect: =false`.
- `Visible` com `And` de várias flags torna impossível descobrir por que não abre.
- Sucesso é `status <> "error"` (`warning` também fecha); resposta em branco é erro.
- Z-order: o modal vai antes do loading e do toast em `Children` da tela.
- Sem emoji nos botões; sem verde em ação destrutiva.

## Variações

- Destrutivo com motivo: `modal-destrutivo-motivo.md`.
- Formulário: `modal-formulario.md`.
- Só informação: `modal-informativo.md`.

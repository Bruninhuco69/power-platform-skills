# Painel "sem acesso"

Maturidade: **único** · Frequência: **comum**.

## Propósito

Painel de tela cheia exibido quando o usuário não tem perfil ou unidade cadastrados. É a ponta visível do fail-closed: `varSemAcesso` nasce `true` e só vira `false` depois de provar acesso.

## Quando usar / quando não usar

**Use quando**

- toda tela de um app com controle de perfil;
- o conteúdo e o menu têm `Visible: =!varSemAcesso`.

**Não use quando**

- o app é aberto a qualquer usuário do tenant;
- a restrição é de uma **ação** (esconda o botão e deixe o flow barrar).

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-cmp-sem-acesso  (GroupContainer)
  xx-lbl-sem-acesso-titulo  (Label)
  xx-lbl-sem-acesso-hint  (Label)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorBackground`, `fxColorPrimary`, `fxFont`, `fxFontSizeSemAcesso`, `fxMsgSemAcessoTitulo`, `fxColorTextBody`, `fxFontSizeBody`, `fxMsgSemAcessoHint`, `fxColorTextPrimary`, `fxMsgSemPermissao`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varSemAcesso`, `varPerfil`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-cmp-sem-acesso:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorBackground
      Height: =Parent.Height
      Visible: =varSemAcesso
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-lbl-sem-acesso-titulo:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =40
            Size: =fxFontSizeSemAcesso
            Text: =fxMsgSemAcessoTitulo
            Width: =700
            X: =(Parent.Width - Self.Width) / 2
            Y: =400
      - xx-lbl-sem-acesso-hint:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorTextBody
            Font: =fxFont
            Height: =60
            Size: =fxFontSizeBody
            Text: =fxMsgSemAcessoHint
            Width: =700
            X: =(Parent.Width - Self.Width) / 2
            Y: =450
```

### Variação: sem permissão para esta tela

O usuário tem acesso ao app, mas não a esta tela: o painel cobre só pela flag da tela.

```yaml
- xx-cmp-sem-permissao:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorBackground
      Height: =Parent.Height
      Visible: =!varSemAcesso && !varPerfil.Flg_Relatorio
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-lbl-sem-permissao:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorTextPrimary
            Font: =fxFont
            Height: =40
            Size: =fxFontSizeBody
            Text: =fxMsgSemPermissao
            Width: =700
            X: =(Parent.Width - Self.Width) / 2
            Y: =470
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `fxMsgSemAcessoTitulo`, `fxMsgSemAcessoHint` | textos do projeto | diga o que houve e a quem recorrer |
| `varPerfil.Flg_Relatorio` | flag real da tela | variação; nunca comparar nome do perfil |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-cmp-sem-acesso`.Visible**: `varSemAcesso`, calculada no `OnStart` depois de identidade, perfil e escopo

```powerfx
varSemAcesso
```

## Acessibilidade

- O título está em `fxColorPrimary` e o texto em `fxColorTextBody` sobre `fxColorBackground`, com contraste de 4,5:1.
- O painel substitui o conteúdo: o leitor de tela encontra título e instrução primeiro.

## Armadilhas

- Estar logo antes dos modais no `Children`: o conteúdo e o menu já somem por `Visible`, o painel cobre o resto.
- `varSemAcesso` inicializada `false` libera todos durante o `OnStart` (o `OnStart` não bloqueia o primeiro render).
- Esconder o painel não é autorização: o flow valida o perfil de novo.

## Variações

- Sem permissão (acima).
- Painel com botão "Falar com o administrador" (`Launch("mailto:...")`).

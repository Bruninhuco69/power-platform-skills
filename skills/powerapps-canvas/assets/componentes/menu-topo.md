# Menu no topo

Maturidade: **novo** · Frequência: **a medir**.

## Propósito

Navegação principal numa barra horizontal no alto da tela: nome do sistema à esquerda, um botão por tela de primeiro nível no meio (visibilidade por flag do perfil) e usuário com perfil à direita. O item ativo é destacado por fundo e negrito. A tela fica com a largura toda para o conteúdo. A escolha deste padrão é feita no `/pp:design` (`ux-design-system.md` §2.1).

## Quando usar / quando não usar

**Use quando**

- o app tem de 2 a 6 telas de primeiro nível, com rótulos curtos;
- as telas têm tabela larga e cada pixel de largura conta;
- a navegação precisa respeitar permissão do perfil.

**Não use quando**

- há mais de 6 telas de primeiro nível ou rótulos longos (use `menu-lateral.md`);
- o app é usado em tela estreita (tablet em pé): a barra não cabe; use a gaveta do `menu-lateral.md`;
- a permissão é regra de negócio: a visibilidade do botão é só UX, quem barra é o flow.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-cmp-topo-con  (GroupContainer)
  xx-cmp-topo-lbl-titulo  (Label)
  xx-cmp-topo-btn-pedidos  (Button)
  xx-cmp-topo-btn-relatorios  (Button)
  xx-cmp-topo-btn-usuarios  (Button)
  xx-cmp-topo-lbl-usuario  (Label)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTransparent`, `fxColorTextOnPrimary`, `fxColorPrimaryLight`, `fxFont`, `fxFontSizeBody`, `fxFontSizeFilter`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxColorMenuBg`, `fxColorMenuItemActive`, `fxTopNavHeight`, `fxTopNavItemWidth`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varSemAcesso`, `varTelaAtiva`, `varPerfil`, `varUsuario`.
- **Coleções**: nenhuma.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela como pai, **antes** do cabeçalho da tela; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-cmp-topo-con:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorMenuBg
      Height: =fxTopNavHeight
      Visible: =!varSemAcesso
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-cmp-topo-lbl-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextOnPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =fxTopNavHeight
            Size: =fxFontSizeBody
            Text: ="Nome do sistema"
            VerticalAlign: =VerticalAlign.Middle
            Width: =220
            Wrap: =false
            X: =24
            Y: =0
      - xx-cmp-topo-btn-pedidos:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "pedidos", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "pedidos", FontWeight.Bold, FontWeight.Normal)
            Height: =fxTopNavHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varTelaAtiva, "pedidos");
              Navigate(Pedidos, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            RadiusBottomLeft: =0
            RadiusBottomRight: =0
            RadiusTopLeft: =0
            RadiusTopRight: =0
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="Pedidos"
            Width: =fxTopNavItemWidth
            X: =260
            Y: =0
      - xx-cmp-topo-btn-relatorios:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "relatorios", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "relatorios", FontWeight.Bold, FontWeight.Normal)
            Height: =fxTopNavHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varTelaAtiva, "relatorios");
              Navigate(Relatorios, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            RadiusBottomLeft: =0
            RadiusBottomRight: =0
            RadiusTopLeft: =0
            RadiusTopRight: =0
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="Relatórios"
            Visible: =varPerfil.Flg_Relatorio
            Width: =fxTopNavItemWidth
            X: =260 + fxTopNavItemWidth
            Y: =0
      - xx-cmp-topo-btn-usuarios:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorTransparent
            BorderThickness: =0
            Color: =fxColorTextOnPrimary
            Fill: =If(varTelaAtiva = "usuarios", fxColorMenuItemActive, fxColorTransparent)
            Font: =fxFont
            FontWeight: =If(varTelaAtiva = "usuarios", FontWeight.Bold, FontWeight.Normal)
            Height: =fxTopNavHeight
            HoverBorderColor: =fxColorTransparent
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorMenuItemActive
            OnSelect: |-
              =Set(varTelaAtiva, "usuarios");
              Navigate(Usuarios, ScreenTransition.None)
            PressedBorderColor: =fxColorTransparent
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorMenuItemActive
            RadiusBottomLeft: =0
            RadiusBottomRight: =0
            RadiusTopLeft: =0
            RadiusTopRight: =0
            Size: =fxFontSizeBody
            TabIndex: =0
            Text: ="Usuários"
            Visible: =varPerfil.Flg_Adm
            Width: =fxTopNavItemWidth
            X: =260 + fxTopNavItemWidth * (1 + If(varPerfil.Flg_Relatorio, 1, 0))
            Y: =0
      - xx-cmp-topo-lbl-usuario:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Right
            Color: =fxColorPrimaryLight
            Font: =fxFont
            Height: =fxTopNavHeight
            Size: =fxFontSizeFilter
            Text: =varUsuario.Nom_Usuario & " · " & varPerfil.Des_Perfil
            VerticalAlign: =VerticalAlign.Middle
            Width: =360
            Wrap: =false
            X: =Parent.Width - 384
            Y: =0
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `xx-cmp-topo-` | prefixo da tela | a barra é replicada em cada tela, com prefixo próprio (exceção legítima do nome) |
| `Pedidos`, `Relatórios`, `Usuários` | textos dos botões | rótulo curto (uma palavra cabe em `fxTopNavItemWidth`); o nome da tela em `Navigate(...)` precisa existir no app |
| `"pedidos"` | identificador de `varTelaAtiva` | um por tela, igual ao `Set` do `OnVisible` dela |
| `varPerfil.Flg_Relatorio`, `varPerfil.Flg_Adm` | flags reais do perfil | nunca comparar nome do perfil |
| `X` dos botões | `260 + fxTopNavItemWidth * <itens visíveis antes>` | conte só os itens que o perfil vê, para não abrir buraco na barra |
| `Y` do cabeçalho e do conteúdo | `fxTopNavHeight` a mais | com a barra, o contêiner do `cabecalho-tela` vai para `Y: =fxTopNavHeight` e o conteúdo desce junto |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-cmp-topo-btn-usuarios`.X**: posição que conta só os itens visíveis antes dele

```powerfx
260 + fxTopNavItemWidth * (1 + If(varPerfil.Flg_Relatorio, 1, 0))
```

**`xx-cmp-topo-btn-relatorios`.OnSelect**: grava a tela ativa e navega sem transição

```powerfx
Set(varTelaAtiva, "relatorios");
Navigate(Relatorios, ScreenTransition.None)
```

**`xx-cmp-topo-btn-relatorios`.Fill**: item ativo com fundo próprio

```powerfx
If(varTelaAtiva = "relatorios", fxColorMenuItemActive, fxColorTransparent)
```

## Acessibilidade

- Todo item é botão focável e tem rótulo de texto.
- O item ativo se distingue por fundo **e** negrito, nunca só por cor.
- A barra vem antes do conteúdo na ordem de tabulação; confira no Accessibility checker.
- Texto claro sobre `fxColorMenuBg`: confira o contraste do `fxColorPrimaryLight` do usuário (mínimo 4,5:1).

## Armadilhas

- Botão oculto por flag com `X` fixo deixa um buraco na barra: o `X` de cada item conta só os visíveis antes dele.
- Mais de 6 itens ou rótulo longo não cabe em 1366 px de largura: troque para `menu-lateral.md`.
- Esquecer de descer o cabeçalho e o conteúdo em `fxTopNavHeight`: a barra cobre o título da tela.
- `varTelaAtiva` precisa ser gravada pelo `OnVisible` de cada tela, como no menu lateral.
- Botão oculto por flag não é segurança: a tela valida o perfil de novo.

## Variações

- Barra clara: `Fill: =fxColorSurface`, texto `fxColorTextPrimary` e item ativo com `fxColorPrimaryLight`; confira o contraste.
- Sem submenu: o Canvas não tem menu suspenso de navegação confiável; mais de 6 telas pede o `menu-lateral.md`.

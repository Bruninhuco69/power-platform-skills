# Catálogo de componentes reutilizáveis

Um arquivo por componente de UX de Power Apps Canvas, em ManualLayout com controles Classic, no dialeto do YAML colado, com tokens `fx*`, nomes `xx-<tipo>-<módulo>-<elemento>` e só propriedades atestadas por tipo (PA2108). Fonte de dados e colunas aparecem como placeholders (`'<fonte>'`, `<col-...>`); o domínio de exemplo é `Pedido` e `Unidade`. Cada arquivo traz o bloco YAML **completo e colável**, é a versão canônica do componente e foi validado por `scripts/validar-telas.py`.

## Sumário

1. [Como colar e como é validado](#como-colar-e-como-é-validado)
2. [Componentes](#componentes)
3. [Tokens a acrescentar](#tokens-a-acrescentar)
4. [Variáveis e coleções a acrescentar ao OnStart](#variáveis-e-coleções-a-acrescentar-ao-onstart)
5. [Relação com as referências](#relação-com-as-referências)
6. [O que ficou de fora](#o-que-ficou-de-fora)

## Como colar e como é validado

Cada bloco é um **fragmento**: uma lista de controles (`- nome:`), o mesmo formato de `Children:` de uma tela. É o que o Code view do Studio aceita em **Paste code** com a tela (ou um contêiner) selecionada; colar **cria** controles novos e não substitui os existentes. Renomeie o prefixo `xx` antes: nome de controle é único no app inteiro e o Studio renomeia duplicado para `_1`.

O validador classifica o bloco como fragmento e checa cada controle (`T001` a `T022`), sem o aviso `T020` ("não é tela YAML"), que só aparece em arquivo sem nenhum bloco `yaml`. A forma mínima que ele valida:

```yaml
- xx-con-exemplo:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorTransparent
      Height: =80
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-lbl-exemplo-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextPrimary
            Font: =fxFont
            Size: =fxFontSizeBody
            Text: ="Exemplo"
            Width: =300
            X: =fxLayoutMargin
            Y: =20
```

Para uma tela completa, ponha o fragmento sob `Children:` de uma tela em `Screens:` (ver `assets/tela-molde.md`). Comandos:

```bash
python skills/powerapps-canvas/scripts/validar-telas.py skills/powerapps-canvas/assets/componentes
python -m pytest tests/powerapps-canvas -q -p no:cacheprovider
```

Destino de todo bloco YAML: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Os tokens da seção abaixo vão para a barra de fórmulas do objeto App (pt-BR: `;` e `;;`), nunca para o YAML. O validador não substitui o Studio: cole num app de teste e confira `PA2108` (propriedade recusada). Três propriedades usadas aqui não constam da tabela de atestadas de `references/yaml-pa-formato.md` §8.3 (existem no Learn; confirme na colagem): `Align` e `BorderStyle` em `Classic/Button@2.2.0` e `MaxLength` em `Classic/TextInput@2.3.2`.

**Maturidade.** `estável` = visto em produção em mais de um projeto real; `único` = visto em um só. **Frequência**: quanto o componente se repetiu nas telas de referência: `muito comum` (quase toda tela), `comum`, `ocasional` (poucas telas) ou `rara` (uma tela).

## Componentes

| Componente | Arquivo | Quando usar | Dependências | Frequência | Maturidade |
|---|---|---|---|---|---|
| [Cabeçalho de tela](cabecalho-tela.md) | `cabecalho-tela.md` | toda tela de conteúdo, sem exceção. | tokens do bloco `COMPONENTES`: `fxHeaderHeight`; variáveis: `varAgora`, `varTelaAtiva`; tokens `fx*` existentes: 11 | muito comum | estável |
| [Menu lateral](menu-lateral.md) | `menu-lateral.md` | o app tem 3 ou mais telas de primeiro nível. | tokens do bloco `COMPONENTES`: `fxColorMenuBg`, `fxMenuWidth`, `fxColorMenuItemActive`, `fxMenuItemHeight`, `fxNavWidthExpandida`, `fxNavWidthRecolhida`; variáveis: `varSemAcesso`, `varTelaAtiva`, `varPerfil`, `varUsuario`, `varUnidadeFiltro`, `varNavExpandida`; tokens `fx*` existentes: 11 | muito comum | estável |
| [Card de KPI (contador com teto)](card-kpi.md) | `card-kpi.md` | resumir a lista que está logo abaixo em até 5 ou 6 números. | tokens do bloco `COMPONENTES`: `fxHeaderHeight`; variáveis: `varPedidoTotal`, `varPedidoAbertos`, `varPedidoAndamento`, `varPedidoEncerrados`; tokens `fx*` existentes: 24 | comum | estável |
| [Abas (botão e traço)](abas.md) | `abas.md` | até 4 conjuntos da mesma entidade na mesma tela. | tokens do bloco `COMPONENTES`: `fxHeaderHeight`; variáveis: `varXXTab`, `varPedidoAbertos`, `varPedidoEncerrados`, `varPedidoTotal`; tokens `fx*` existentes: 12 | comum | estável |
| [Barra de filtros (combo, texto, datas e limpar)](barra-filtros.md) | `barra-filtros.md` | galeria com mais de uns 50 registros. | tokens do bloco `COMPONENTES`: `fxHeaderHeight`; variáveis: `varPedidoDe`, `varPedidoAte`, `varPedidoFiltroAplicado`, `varPedidoStatusAplicado`, `varPedidoBuscaAplicada`; tokens `fx*` existentes: 22 | comum | estável |
| [Seletor de unidade](seletor-unidade.md) | `seletor-unidade.md` | o usuário pode ver mais de uma unidade. | tokens do bloco `COMPONENTES`: `fxHeaderHeight`; variáveis: `varUnidadeFiltro`, `varTodasUnidades`, `varUnidadeLotacao`, `varPedidoTotal`; coleções: `colUnidadesEscopo`; tokens `fx*` existentes: 8 | comum | estável |
| [Galeria em formato de tabela](galeria-tabela.md) | `galeria-tabela.md` | lista de registros com 4 a 10 colunas e uma ação por linha. | variáveis: `varUnidadeFiltro`, `varPedidoDe`, `varPedidoAte`, `varPedidoSel`, `varMostrarDetalhes`; tokens `fx*` existentes: 29 | muito comum | estável |
| [Cabeçalho ordenável](ordenacao-coluna.md) | `ordenacao-coluna.md` | o usuário precisa reordenar a mesma lista por mais de uma coluna. | tokens do bloco `COMPONENTES`: `fxTxtOrdemAsc`, `fxTxtOrdemDesc`; variáveis: `varPedidoSortColuna`, `varPedidoSortAsc`; tokens `fx*` existentes: 6 | rara | único |
| [Estado vazio e aviso de lista truncada](estado-vazio.md) | `estado-vazio.md` | toda galeria filtrável. | variáveis: `varPedidoTotal`; tokens `fx*` existentes: 10 | muito comum | estável |
| [Rodapé "Exibindo N de M"](rodape-contagem.md) | `rodape-contagem.md` | a lista não tem paginação e o total real importa. | tokens do bloco `COMPONENTES`: `fxTxtExibindo`; variáveis: `varPedidoTotal`, `varUnidadeFiltro`; tokens `fx*` existentes: 6 | ocasional | único |
| [Badge de status (pílula)](badge-status.md) | `badge-status.md` | coluna de status de galeria ou detalhe. | tokens do bloco `COMPONENTES`: `fxPillHeight`; tokens `fx*` existentes: 17 | comum | estável |
| [Botões: primário, secundário, destrutivo e neutro](botoes.md) | `botoes.md` | qualquer botão de ação: escolha o papel pela natureza da ação, nunca pelo texto. | variáveis: `varShowLoading`, `varMostrarConfirmar`, `varMostrarCancelar`; tokens `fx*` existentes: 16 | muito comum | estável |
| [Modal de confirmação](modal-confirmacao.md) | `modal-confirmacao.md` | ação com efeito no servidor que o usuário pode querer desfazer na hora. | tokens do bloco `COMPONENTES`: `fxModalWidthS`; variáveis: `varMostrarConfirmar`, `varPedidoSel`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType` ...; tokens `fx*` existentes: 24 | ocasional | estável |
| [Modal de formulário](modal-formulario.md) | `modal-formulario.md` | criar ou editar um registro com poucos campos (até uns 8). | tokens do bloco `COMPONENTES`: `fxModalWidthL`, `fxHeaderHeight`; variáveis: `varMostrarForm`, `varUnidadeFiltro`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType` ...; tokens `fx*` existentes: 32 | comum | estável |
| [Modal destrutivo com motivo obrigatório](modal-destrutivo-motivo.md) | `modal-destrutivo-motivo.md` | cancelar, excluir ou estornar algo que não volta. | tokens do bloco `COMPONENTES`: `fxModalWidthM`; variáveis: `varMostrarCancelar`, `varPedidoSel`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType` ...; tokens `fx*` existentes: 28 | ocasional | estável |
| [Modal informativo (detalhes e histórico)](modal-informativo.md) | `modal-informativo.md` | mostrar detalhe ou histórico de um registro sem sair da tela. | tokens do bloco `COMPONENTES`: `fxModalWidthL`; variáveis: `varMostrarDetalhes`, `varPedidoSel`; tokens `fx*` existentes: 28 | ocasional | estável |
| [Overlay de loading](overlay-loading.md) | `overlay-loading.md` | toda chamada `.Run()` de flow. | variáveis: `varShowLoading`, `varLoadingMessage`; tokens `fx*` existentes: 12 | muito comum | estável |
| [Toast de retorno de flow](toast.md) | `toast.md` | retorno de qualquer chamada de flow (a mensagem vem pronta em `description`). | tokens do bloco `COMPONENTES`: `fxColorToastTrack`; variáveis: `varShowToast`, `varToastType`, `varToastMessage`; tokens `fx*` existentes: 20 | muito comum | estável |
| [Painel "sem acesso"](painel-sem-acesso.md) | `painel-sem-acesso.md` | toda tela de um app com controle de perfil. | variáveis: `varSemAcesso`, `varPerfil`; tokens `fx*` existentes: 11 | comum | único |
| [Botão de exportar](exportar.md) | `exportar.md` | o usuário precisa do conjunto completo do filtro, não do que cabe na tela. | tokens do bloco `COMPONENTES`: `fxTxtExportar`; variáveis: `varShowLoading`, `varLoadingMessage`, `varRet`, `varUnidadeFiltro`, `varPedidoDe`, `varPedidoAte` ...; tokens `fx*` existentes: 13 | ocasional | estável |
| [Paginação por cursor](paginacao-cursor.md) | `paginacao-cursor.md` | a lista passa de `fxLimiteLinhas` e o usuário precisa percorrer tudo. | tokens do bloco `COMPONENTES`: `fxTxtAnterior`, `fxTxtProxima`; variáveis: `varPagina`, `varShowLoading`, `varCursorAtual`, `varPedidoTotal`; coleções: `colCursores`; tokens `fx*` existentes: 12 | rara | único |
| [Seleção em lote](selecao-em-lote.md) | `selecao-em-lote.md` | a mesma ação se aplica a vários registros. | variáveis: `varMostrarConfirmarLote`, `varShowLoading`, `varPerfil`; coleções: `colSelecionados`; tokens `fx*` existentes: 11 | ocasional | único |
| [Linha expansível](linha-expansivel.md) | `linha-expansivel.md` | o detalhe é curto (2 a 4 campos) e o usuário compara várias linhas. | variáveis: `varLinhaExpandida`; tokens `fx*` existentes: 11 | ocasional | único |

## Tokens a acrescentar

Nenhum no momento: os tokens que os componentes usam estão em [`../app-formulas-tokens.md`](../app-formulas-tokens.md), bloco `COMPONENTES`. Ao criar um componente novo, liste aqui (bloco `powerfx`, destino barra de fórmulas pt-BR) os tokens que faltarem e depois mova-os para o molde.

## Variáveis e coleções a acrescentar ao OnStart

Toda global nasce no `OnStart` com valor neutro (`assets/app-onstart-molde.md`). Estas são usadas pelos componentes e ainda não constam do molde:

| Variável | Componentes que a leem | Valor inicial |
|---|---|---|
| `varAgora` | cabecalho-tela | `Now()` |
| `varCursorAtual` | paginacao-cursor | `Blank()` |
| `varLinhaExpandida` | linha-expansivel | `Blank()` |
| `varMostrarCancelar` | botoes, modal-destrutivo-motivo | `false` |
| `varMostrarConfirmarLote` | selecao-em-lote | `false` |
| `varMostrarDetalhes` | galeria-tabela, modal-informativo | `false` |
| `varMostrarForm` | modal-formulario | `false` |
| `varNavExpandida` | menu-lateral | `false` |
| `varPagina` | paginacao-cursor | `1` |
| `varPedidoAbertos` | card-kpi, abas | `0` |
| `varPedidoAndamento` | card-kpi | `0` |
| `varPedidoAte` | barra-filtros, galeria-tabela, exportar | `Blank()` (zerada no `OnVisible`) |
| `varPedidoBuscaAplicada` | barra-filtros | `""` |
| `varPedidoDe` | barra-filtros, galeria-tabela, exportar | `Blank()` (zerada no `OnVisible`) |
| `varPedidoEncerrados` | card-kpi, abas | `0` |
| `varPedidoFiltroAplicado` | barra-filtros | `false` |
| `varPedidoSortAsc` | ordenacao-coluna | `false` |
| `varPedidoSortColuna` | ordenacao-coluna | `"<col-data>"` |
| `varPedidoStatusAplicado` | barra-filtros | `""` |
| `varXXTab` | abas | `1` |

Coleções ainda não declaradas no molde: `colCursores`, `colSelecionados` (todas nascem vazias com `Clear`/`ClearCollect`).

## Relação com as referências

Estes arquivos repetem, em forma canônica e normalizada, blocos que já existem em `references/ux-componentes.md`, `references/ux-feedback.md` e `assets/tela-molde.md`. A referência explica a regra; o componente é a versão colável. A correspondência por seção:

| Referência | Seção | Componente |
|---|---|---|
| `ux-componentes.md` | 2. Cabeçalho de tela | `cabecalho-tela.md` |
| `ux-componentes.md` | 3. Card de KPI | `card-kpi.md` |
| `ux-componentes.md` | 4. Abas | `abas.md` |
| `ux-componentes.md` | 5. Filtros | `barra-filtros.md`, `seletor-unidade.md` |
| `ux-componentes.md` | 6. Galeria com cabeçalho de coluna | `galeria-tabela.md`, `ordenacao-coluna.md` |
| `ux-componentes.md` | 7. Badge de ação | `badge-status.md` |
| `ux-componentes.md` | 8. Botões | `botoes.md` |
| `ux-componentes.md` | 12. Seleção em lote | `selecao-em-lote.md` |
| `ux-componentes.md` | 13. Estados | `estado-vazio.md`, `rodape-contagem.md` |
| `ux-feedback.md` | 9. Modal | `modal-confirmacao.md`, `modal-destrutivo-motivo.md`, `modal-formulario.md`, `modal-informativo.md` |
| `ux-feedback.md` | 10. Loading | `overlay-loading.md` |
| `ux-feedback.md` | 11. Toast | `toast.md` |
| `tela-molde.md` | A tela (sem acesso, modal, loading, toast) | `painel-sem-acesso.md`, `modal-confirmacao.md`, `overlay-loading.md`, `toast.md` |

Diferenças em relação às referências: todo `Font` é `fxFont`, como nas referências; as cores `RGBA(...)` residuais do toast viraram token (`fxColorToastTrack`); o véu de modal e de loading ganhou um botão transparente de bloqueio como primeiro filho.

## O que ficou de fora

- **Auto-refresh, debounce de busca e polling**: já completos em `references/timers-async.md`.
- **Rodapé de versão e direitos da tela**: rótulo estático sem lógica, não vale arquivo.
- **Card de atalho da tela inicial** (raro): é composição de cards com `Navigate`, coberto por `card-kpi.md` mais `botoes.md`.
- **Toggle de "todas"** (raro): uma linha de `Classic/Toggle@2.1.0` com `OnChange`; sem padrão a extrair.
- **Relógio do cabeçalho**: virou variação de `cabecalho-tela.md`.
- **Campo de busca**: virou parte de `barra-filtros.md` (`DelayOutput`).
- **Formulário de duas colunas e editor em tela dedicada**: variam demais entre telas; só o modal de formulário se repete.

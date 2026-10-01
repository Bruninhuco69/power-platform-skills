# Chamada de flow do lado do app

O botão que grava: loading, `IfError(.Run(...))`, toast, `If(status <> "error", fecha o modal,
Refresh, recontagem)` (YAML). O **lado do flow** (esqueleto, autorização por ação, `Try/Catch`, `Response`,
log) é da skill `power-automate`; a procedure, da `sql-procedures`. Aqui está só o que a tela faz.

## Sumário

1. [O contrato](#1-o-contrato)
2. [O esqueleto do botão](#2-o-esqueleto-do-botão)
3. [Por que cada passo](#3-por-que-cada-passo)
4. [Parâmetros](#4-parâmetros)
5. [Lote e operação longa](#5-lote-e-operação-longa)
6. [O que nunca fazer](#6-o-que-nunca-fazer)
7. [Checklist de revisão do botão](#7-checklist-de-revisão-do-botão)
8. [Fontes](#8-fontes)

---

## 1. O contrato

Decisões C1 a C5 de [decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md):

- Resposta do flow: **`{ status, description, id, url }`**, todos texto. `status` é `success`,
  `warning` ou `error`. `description` é a frase pronta para o usuário (montada no flow, a
  procedure devolve só um código). O `Response` do flow precisa de **schema JSON**; sem ele o app
  não conhece os campos e `varRet.status` não compila.
- Sucesso é **`status <> "error"`**: `warning` (sucesso parcial) também fecha o modal.
- Toda chamada `.Run()` fica dentro de `IfError`. Chamada sem `IfError` é a lacuna mais
  comum em app real: se o transporte falha (timeout, 401, flow desligado), o
  resultado é indefinido e, sem tratamento, um `status` em branco passaria no teste `<> "error"`
  como sucesso. `[não verificado: comportamento exato de .Run() em timeout ou erro HTTP; confirme
  no Monitor]`
- Parâmetros do gatilho Power Apps (V2) são **posicionais e texto**; parâmetro novo entra
  **sempre no fim**.
- Depois de gravar: `Refresh(fonte)` e recontagem dos contadores da tela.
- A tela **não autoriza**: o flow revalida a permissão e o escopo do chamador. O que a tela faz
  com a flag do perfil (`Visible`, `DisplayMode`) é UX
  ([escopo-e-permissao.md](escopo-e-permissao.md)).

## 2. O esqueleto do botão

Botão de confirmação de um modal. O `OnSelect` está no dialeto do YAML colado (`,` e `;`). O
bloco completo, com o modal ao redor, está em [tela-molde.md](../assets/tela-molde.md).

Destino: YAML colado (`,` e `;`).

```yaml
# xx-mod-confirmar-btn-confirmar
DisplayMode: =If(varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
Text: =If(varShowLoading, fxTxtProcessando, fxTxtEncerrar)
OnSelect: |-
  =Set(varShowLoading, true);
  Set(varLoadingMessage, "Encerrando...");
  IfError(
    Set(
      varRet,
      'app-flow-pedido-acao'.Run(
        "encerrar",
        Text(varPedidoSel.Id_Pedido, "[$-en-US]0")
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
    Refresh(Pedido);
    Set(
      varPedidoTotal,
      CountRows(Filter(Pedido, StartsWith(Unidade, varUnidadeFiltro)))
    )
  )
```

A mesma sequência em quatro tempos:

1. **Prepara**: liga o loading (`varShowLoading`, `varLoadingMessage`).
2. **Chama dentro de `IfError`**: falha de transporte zera `varRet`.
3. **Fecha o loading em qualquer caminho** e **traduz** o resultado em `varToastType` e
   `varToastMessage`. `Coalesce(varRet.status, "error")` trata resposta em branco como erro;
   `Coalesce(varRet.description, fxMsgFalhaFlow)` dá mensagem mesmo sem resposta.
4. **Se não for erro**: fecha o modal, limpa a seleção, `Refresh` e recontagem.

## 3. Por que cada passo

| Passo | Motivo |
|---|---|
| `Set(varShowLoading, true)` antes de tudo | `.Run()` é síncrono e bloqueante; sem overlay o usuário clica de novo e grava duas vezes |
| `DisplayMode` e `Text` do botão ligados a `varShowLoading` | impede duplo clique e dá feedback no próprio botão; vale para **todo** botão que chama flow |
| `IfError(Set(varRet, ...Run(...)), ...)` | separa **falha de transporte** de **falha de negócio**; a segunda chega pelo `status` |
| `Set(varRet, Blank())` no ramo de erro | evita reaproveitar o retorno **velho** da chamada anterior |
| `Set(varShowLoading, false)` fora do `If` | o overlay fecha em qualquer caminho; overlay preso é o chamado de suporte mais comum |
| `Coalesce(varRet.status, "error")` | `Blank() <> "error"` é verdadeiro e fecharia o modal como sucesso |
| toast para retorno de flow | `Notify()` fica para validação de formulário; retorno de flow é toast |
| `Refresh(fonte)` depois de gravar | o app cacheia a consulta; sem `Refresh` a galeria mostra o estado antigo |
| recontagem dos contadores | contador só no `OnStart` congela e passa o dia divergindo da galeria |
| `Trace(...)` | a falha de transporte aparece no Monitor com o texto do erro |

O desfecho tem **três** estados no toast (`success`, `warning`, `error`), em tokens de cor e de
título (`fxTxtToast*`). `warning` é o lote com sucesso parcial e **fecha** o modal: nada de
pintar sucesso parcial de vermelho. Bloco do toast em [ux-feedback.md](ux-feedback.md).

## 4. Parâmetros

- **Todos texto, na ordem do gatilho.** O primeiro parâmetro é a ação; os de negócio seguem a ordem do gatilho;
  parâmetro novo entra no fim (C4). Identidade nunca viaja por parâmetro — o flow a lê do contexto.
  Parâmetro que não se aplica vai como `""`.
- **Id numérico: `Text(id, "[$-en-US]0")`.** `Text(1234)` em pt-BR é `"1.234"` e o flow não acha a
  linha: editar e encerrar falhavam para todo id a partir de 1.000, e o encerramento era irreversível.
  `[verificado: projeto de referência]`
- **Data**: texto `yyyy-mm-dd` (ou ISO 8601), nunca data crua.
- **Chave estrangeira** vai como o id (`Text(Selected.Id_Categoria, "[$-en-US]0")`), não o nome de
  exibição; trocar o significado de um parâmetro **sem mudar a posição** exige atualizar o
  contrato (`CONTRATOS`, skill `power-automate`) no mesmo commit.
- **A unidade de gravação é campo do registro**, não estado global: no cadastro vem do
  controle do formulário; na edição e no encerramento, do próprio registro (`varPedidoSel.Unidade`). Ver
  [escopo-e-permissao.md](escopo-e-permissao.md).
- **Identidade**: o app **não** envia e-mail nem identidade; o flow obtém o chamador do contexto
  (`Office 365 Users — MyProfile_V2`) e revalida a permissão por ação.
- **Constante com nome** (`fxCodigo...`) no lugar de número mágico (`12`, `-300`) no `.Run(...)`.
- **Nome do flow** `<app>-flow-<entidade>-<verbo>` e **uma** variável de retorno por app
  (`varRet`), declarada no `OnStart`. Duas variáveis (`varRet`, `varRetg`) para a mesma coisa só
  geram dúvida.

## 5. Lote e operação longa

**Lote.** Mande a coleção inteira como JSON numa **única** chamada, não `.Run()` dentro de
`ForAll` (N chamadas, N × ~0,6 s só de instanciação):

Destino: YAML colado (`,` e `;`).

```yaml
# xx-mod-lote-btn-confirmar
OnSelect: |-
  =Set(varShowLoading, true);
  IfError(
    Set(
      varRet,
      'app-flow-pedido-lote'.Run(
        "encerrar",
        JSON(
          ForAll(colSelecionados, { id: Text(ThisRecord.Id_Pedido, "[$-en-US]0") }),
          JSONFormat.Compact
        )
      )
    ),
    Set(varRet, Blank())
  );
  Set(varShowLoading, false);
  Set(varToastType, Coalesce(varRet.status, "error"));
  Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
  Set(varShowToast, true)
```

O flow devolve `status: "warning"` com `description` agregada ("12 encerrados, 3 com erro") e o app
mostra **um** toast. `colSelecionados` vem de `Collect` por linha (checkbox), não de
`Filter(gal.AllItems, ...)`: `AllItems` só enxerga o que já foi carregado.

**Operação longa** (acima do timeout do conector, que costuma ser de ~120 s
`[não verificado: confirme o limite do seu ambiente]`): o flow responde "aceito" e grava
progresso numa tabela; o app faz polling com backoff e teto
([timers-async.md](timers-async.md) §6). Declare no contrato se a resposta é **síncrona**
(processou) ou **aceite** (processando); em aceite, a tela precisa de consulta de status.

## 6. O que nunca fazer

- `.Run()` em `Items` de galeria, em `Visible` ou em qualquer propriedade de UI.
- `.Run()` sem `IfError` (validador: T018).
- `Text(<id>)` sem `[$-en-US]0` em parâmetro ou JSON.
- `If(status = "200", ...)`: o contrato é `success`, `warning`, `error`; `"200"` como texto é
  dependência frágil.
- Retry automático de operação que grava, sem chave de idempotência.
- `Notify()` para retorno de flow.
- Fechar o loading só no ramo de sucesso.
- Confiar no `DisplayMode` ou na tela para impedir duplicidade ou auto-ação: guarda de duplicata
  vai **dentro da transação**, no servidor (ler e depois gravar na tela perde corrida).
- Validar permissão só na tela. A tela esconde; o flow nega.

## 7. Checklist de revisão do botão

- [ ] `varShowLoading` liga antes e desliga em todos os caminhos; botão desabilitado e com
      "Processando...".
- [ ] `.Run()` dentro de `IfError`; `varRet` zerado no ramo de falha.
- [ ] `status` em branco tratado como erro; sucesso por `<> "error"`.
- [ ] Toast com os 3 tipos; sem `Notify()` para retorno de flow.
- [ ] Ids com `[$-en-US]0`; datas em texto; parâmetro novo só no fim.
- [ ] `Refresh(fonte)` e recontagem no sucesso; modal fecha só se não for erro.
- [ ] Nenhuma permissão decidida só na tela; unidade de gravação vem do registro.
- [ ] Testado com o flow **desligado** (toast vermelho, overlay fecha) e com sucesso parcial.

## 8. Fontes

- [Run a flow from Power Apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/using-logic-flows)
- [Error, IfError](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-iferror)
- [Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)

# Anatomia de um flow chamado pelo app

Esqueleto que decide o desenho de qualquer flow de escrita chamado por tela (decisões F1–F3
em [decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md)). O molde colável
que implementa tudo isto está em `assets/flow-gravar-molde.json` e passa no
`scripts/verificar-fluxo.py`.

## Sumário

1. [A árvore](#1-a-árvore)
2. [Por que cada bloco existe](#2-por-que-cada-bloco-existe)
3. [Nega e Terminate](#3-nega-e-terminate)
4. [Catch escuta Failed, TimedOut e Skipped](#4-catch-escuta-failed-timedout-e-skipped)
5. [Switch por ação](#5-switch-por-ação)
6. [Regras de nome](#6-regras-de-nome)
7. [O que fica fora do escopo colável](#7-o-que-fica-fora-do-escopo-colável)

---

## 1. A árvore

```
Trigger Power Apps (V2)                    digitado à mão, não é colável
Escopo_<flow>                              1 Scope raiz = 1 colagem
  CONFIG                 Compose           flags e textos do ambiente (flags de segurança nascem LIGADAS)
  Perfil_do_chamador     Office 365 Users  MyProfile_V2: identidade vem do contexto, nunca de parâmetro
  Chamador               Compose           e-mail/UPN normalizado em minúsculas
  Try_<flow>             Scope
    Ler_chamador         procedure/consulta devolve perfil e flags; ZERO linha = negar
    Se_chamador_desconhecido   If -> Nega_chamador + Terminate
    Switch_acao          Switch sobre toLower(trim(triggerBody()['text']))
      Caso_<acao>
        Autorizar_<acao>   If not(flag DA ação) -> Nega_perm_x + Terminate
        Normalizar_x       Compose  (trim, take, toUpper, número em texto)
        [Estado_antes_x]   leitura do registro real, quando o escopo depende dele
        Validar_x          Compose  cadeia if() devolve a 1a mensagem ou ''
        Se_invalido_x      If -> Nega_x + Terminate
        Gravar_x           procedure (ver sql-no-flow.md) ou Dataverse
        Codigo_x           Compose  código devolvido pela escrita
        Responder_x        Response traduz código -> {status, description, id, url}
      default              Nega_acao + Terminate   (nomeia o valor recebido)
  Catch_<flow>           Scope  runAfter Try [Failed, TimedOut, Skipped] -> Nega_conector + Terminate
```

A ordem dentro do `Try` é a ordem do risco: **autorizar -> normalizar -> validar -> gravar ->
responder**. Nada que escreve vem antes de qualquer `Nega_*`. [verificado: projeto de
referência]

## 2. Por que cada bloco existe

| Bloco | Função | Por quê |
|---|---|---|
| `CONFIG` | Único lugar de texto e flag do ambiente | Literal espalhado leva e-mail/servidor de DEV para produção. O verificador acusa literal fora dele (F014) |
| `Perfil_do_chamador` + `Chamador` | Quem está chamando | O parâmetro do trigger é falsificável; o contexto de execução não. Detalhe em [autorizacao-no-flow.md](autorizacao-no-flow.md) |
| `Try` / `Catch` | Isolar falha de conector | Sem `Catch` o app recebe timeout em vez de mensagem |
| `Switch_acao` | Uma ação de negócio por caso | Cada caso autoriza e valida a própria ação; um portão único antes do `Switch` não sabe qual ramo vai rodar |
| `Validar_x` como cadeia de `if()` | Primeira mensagem de erro ou `''` | Uma expressão, uma mensagem, testável sem executar a escrita |
| `Codigo_x` | Guardar o código uma vez | Evita repetir a expressão longa de leitura em `status` e `description` (limite de 8.192 caracteres) |

## 3. Nega e Terminate

`Response` só existe em flow com gatilho HTTP (Request) ou Power Apps, e **não encerra** o flow: a ação seguinte roda com a resposta já enviada. Por isso todo
`Nega_*` é um par `Response` + `Terminate` (`runStatus: Succeeded`), e o verificador acusa
`Response` sem `Terminate` quando o flow continua depois dela (F015). A regra vale também para
`Response` dentro de `If`: o `If` termina e o flow segue para a ação seguinte do bloco pai.
[verificado: projeto de referência]

```json
{
  "Nega_perm_grv": {
    "type": "Response",
    "kind": "PowerApp",
    "inputs": {
      "schema": {
        "type": "object",
        "properties": {
          "status": { "title": "status", "x-ms-dynamically-added": true, "type": "string" },
          "description": { "title": "description", "x-ms-dynamically-added": true, "type": "string" },
          "id": { "title": "id", "x-ms-dynamically-added": true, "type": "string" },
          "url": { "title": "url", "x-ms-dynamically-added": true, "type": "string" }
        },
        "additionalProperties": {}
      },
      "statusCode": 200,
      "body": { "status": "error", "description": "Seu perfil não permite esta ação.", "id": "", "url": "" }
    },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000001" }
  },
  "Nega_perm_grv_fim": {
    "type": "Terminate",
    "inputs": { "runStatus": "Succeeded" },
    "runAfter": { "Nega_perm_grv": ["Succeeded"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000002" }
  }
}
```

Destino: dentro de `actions` de um `If` (colado como parte de um escopo, ver
[formato-clipboard.md](formato-clipboard.md)). `statusCode` fica `200` mesmo no erro de negócio:
o app lê `status`, não o código HTTP (ver [contrato-app-flow.md](contrato-app-flow.md)).

## 4. Catch escuta Failed, TimedOut e Skipped

Quando uma ação falha, as seguintes ficam `Skipped`
([Learn: run after](https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling)).
`CONFIG`, `Perfil_do_chamador` e `Chamador` são **irmãos** do `Try`: se o conector de perfil
cair, o `Try` fica `Skipped`, e um `Catch` que só escuta `Failed` também fica `Skipped` -- a
execução termina **sem `Response`** e o app espera até o timeout. Por isso o `runAfter` do
`Catch` leva os três estados. O verificador acusa a falta (F009).

```json
{
  "Catch_gravar": {
    "type": "Scope",
    "runAfter": { "Try_gravar": ["Failed", "TimedOut", "Skipped"] },
    "actions": {},
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000003" }
  }
}
```

Para obter o texto do erro do conector (log, suporte) use
`result('Try_gravar')` filtrado por `status = 'Failed'`; `result()` devolve só as ações de
**primeiro nível** do escopo, não as aninhadas em `If`/`Switch`
([Learn](https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling)). Ver
[log-execucao.md](log-execucao.md).

Exceção legítima: uma ação de **absorção** (ex.: gravar cache que não pode derrubar o fluxo)
pode omitir `Skipped` de propósito, para não mascarar a falha de outra ação -- documente isso na
descrição da ação.

## 5. Switch por ação

- Valor do `Switch`: `@toLower(trim(triggerBody()['text']))` (a ação é o 1º parâmetro).
- Casos se chamam `Caso_<acao>`. O designer coloca **casos e ações no mesmo espaço de nomes**:
  caso com o mesmo nome de uma ação sobrescreve o outro e a colagem morre com `Required property
  'case' not found`, apontando para um caso que **tem** `case`. O verificador acusa (F008).
  [verificado: projeto de referência]
- `default` responde `error` **nomeando o valor** recebido; nunca cai calado num valor padrão
  (o `CASE ... ELSE` silencioso do SQL era a mesma armadilha).
- Derivação com `Switch` aninhado: cada caso é um `Compose` com nome próprio (`Local_x_base`),
  nunca igual ao nome do caso.

## 6. Regras de nome

| Elemento | Regra |
|---|---|
| Ação | Único no flow inteiro (em qualquer nível); sem espaço no `nodeId`. Duplicado vira `_1` em silêncio (F004) |
| Caso de Switch | `Caso_*`; não pode repetir nome de ação |
| Response de negação | `Nega_<motivo>`; seguido de `Nega_<motivo>_fim` (`Terminate`) |
| Escopos | `Try_<flow>`, `Catch_<flow>`, `Escopo_<flow>` |
| Referência a ação | Pelo nome exato. Renomear sem reescrever os tokens quebra tudo abaixo, sem aviso do designer (F006) |

## 7. O que fica fora do escopo colável

- **O trigger.** `Power Apps (V2)` e seus parâmetros são digitados à mão, na ordem do
  [contrato](contrato-app-flow.md). É o passo de maior risco da entrega.
- **A conexão.** A colagem precisa da connection reference criada antes; `allConnectionData`
  a religa (R1 em [gabarito-designer.md](gabarito-designer.md)). Criar a referência por
  ambiente é assunto da skill `power-platform` (ALM).
- **O log.** O molde não traz o escopo `Log`; ver [log-execucao.md](log-execucao.md) para o
  desenho e a tensão com `Terminate`.
- **`Initialize variable`.** Só vale no nível raiz do flow; dentro de escopo use `Compose` com
  `coalesce`. [verificado: projeto de referência]

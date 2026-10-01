# Log de execução

Decisão F4 de [decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md): todo flow
tem um escopo `Log`. O `Catch` devolve só "o sistema não respondeu"; sem log, ninguém sabe qual
ação quebrou, para quem, nem quanto durou. Padrão herdado de um flow de recebimento de referência
([licoes-de-campo.md](licoes-de-campo.md)).

## Sumário

1. [Modelo pai/filho](#1-modelo-paifilho)
2. [O escopo Log](#2-o-escopo-log)
3. [Falhar a execução depois de logar](#3-falhar-a-execução-depois-de-logar)
4. [Tensão com Response + Terminate](#4-tensão-com-response--terminate)
5. [Onde gravar quando os dados estão em SQL](#5-onde-gravar-quando-os-dados-estão-em-sql)
6. [Correlação com o suporte](#6-correlação-com-o-suporte)

---

## 1. Modelo pai/filho

| Tabela | Uma linha por | Colunas |
|---|---|---|
| **Flow monitorado** (pai) | flow | `flowid` (`workflow()['name']`), `flowdisplayname`, `lastrunstatus`, `lastruntime`, `totalruns`, `totalfailedruns`, `consecutivefailures`, `isactive` |
| **Execução** (filho) | execução | `runidentifier` (`workflow()['run']['name']`), `flowidentifier`, `starttime`, `endtime`, `durationseconds`, `runstatus`, `triggername`, `rowsreceived`, `rowsprocessed`, `rowsfailed`, `inputpayloadsize`, `errorcode` (**nome da ação** que falhou), `errormessage` |

- `errorcode` guarda o nome da ação, não um código: quem consome (relatório, Power BI) trata como
  "ação com erro".
- **Nunca** grave token, senha ou o corpo bruto no log. `inputpayloadsize` sim, JSON enviado só
  sem credencial.
- Padronize quais colunas **todo** flow preenche; flows antigos preenchendo colunas diferentes
  deixam o relatório de erro HTTP nulo para os novos.
- As tabelas são da skill `dataverse`; nomes `<prefixo>_...` do ambiente.

## 2. O escopo Log

Escopo **irmão** do principal (fora dele), `runAfter` em `Succeeded`, `Failed` e `TimedOut`:

```json
{
  "nodeId": "Log",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Filter_FailedActions": {
        "type": "Query",
        "description": "Ações de primeiro nível do Escopo_Principal com status Failed. result() só aceita Scope/Foreach/Until, não If.",
        "inputs": {
          "from": "@result('Escopo_Principal')",
          "where": "@equals(item()?['status'], 'Failed')"
        },
        "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000011" }
      },
      "Compose_Log": {
        "type": "Compose",
        "description": "Um Compose no lugar de uma variável por campo. Expressões seguras com lista vazia e nulo (if() avalia os dois ramos).",
        "inputs": {
          "RunId": "@workflow()?['run']?['name']",
          "StartTime": "@trigger()?['startTime']",
          "EndTime": "@utcNow()",
          "DurationSeconds": "@div(sub(ticks(utcNow()), ticks(trigger()?['startTime'])), 10000000)",
          "Status": "@if(empty(body('Filter_FailedActions')), 0, 1)",
          "FailedAction": "@if(empty(body('Filter_FailedActions')), null, last(body('Filter_FailedActions'))?['name'])",
          "ErrorMessage": "@if(empty(body('Filter_FailedActions')), null, take(string(last(body('Filter_FailedActions'))?['error']?['message']), 4000))",
          "PayloadSize": "@length(string(triggerBody()))",
          "TriggerName": "@trigger()?['name']",
          "FlowId": "@workflow()?['name']"
        },
        "runAfter": { "Filter_FailedActions": ["Succeeded"] },
        "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000012" }
      },
      "Add_FlowRun": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_flowruns",
            "item/<prefixo>_runidentifier": "@outputs('Compose_Log')?['RunId']",
            "item/<prefixo>_flowidentifier": "@outputs('Compose_Log')?['FlowId']",
            "item/<prefixo>_starttime": "@outputs('Compose_Log')?['StartTime']",
            "item/<prefixo>_endtime": "@outputs('Compose_Log')?['EndTime']",
            "item/<prefixo>_durationseconds": "@outputs('Compose_Log')?['DurationSeconds']",
            "item/<prefixo>_runstatus": "@outputs('Compose_Log')?['Status']",
            "item/<prefixo>_triggername": "@outputs('Compose_Log')?['TriggerName']",
            "item/<prefixo>_inputpayloadsize": "@outputs('Compose_Log')?['PayloadSize']",
            "item/<prefixo>_errorcode": "@outputs('Compose_Log')?['FailedAction']",
            "item/<prefixo>_errormessage": "@outputs('Compose_Log')?['ErrorMessage']"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "CreateRecord"
          }
        },
        "runAfter": { "Compose_Log": ["Succeeded"] },
        "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000013" }
      }
    },
    "runAfter": { "Escopo_Principal": ["Succeeded", "Failed", "TimedOut"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000014" }
  },
  "allConnectionData": {
    "Add_FlowRun": {
      "connectionReference": {
        "api": { "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps" },
        "connection": { "id": "<prefixo>_shared_commondataserviceforapps" },
        "connectionName": "<prefixo>_shared_commondataserviceforapps"
      },
      "referenceKey": "shared_commondataserviceforapps"
    }
  },
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

Destino: `Ctrl+V` **depois** de um escopo chamado `Escopo_Principal` (o `runAfter` da raiz aponta
para ele; ajuste ao nome do seu escopo raiz); versão reduzida (só o filho). A parte do pai (upsert dos contadores de execuções e de
falhas consecutivas) segue o mesmo desenho com `List`, `If` e `Update`/`Add`. Para flow de
recebimento de lote acrescente `RowsReceived/Processed/Failed`; para flow SQL, as linhas afetadas
pela procedure.

Pontos de atenção:

- `Escopo_Principal` é a raiz da lógica; o `Log` precisa **enxergar a falha lá** (por isso a
  validação de credencial fica dentro do principal: [http-entrada-externa.md](http-entrada-externa.md)).
- `result()` devolve só o **primeiro nível**: falha dentro de `If`/`Switch` aparece como falha da
  ação de primeiro nível que a contém.
- O verificador dá aviso F009 neste escopo (sem `Skipped`) e F006 (`Escopo_Principal` está fora do
  trecho): esperado. `Skipped` fica de fora de propósito -- com o principal `Skipped` não há
  falha a registrar, e o filtro devolveria status 0.
- O log em si pode falhar: ele não pode derrubar a resposta ao chamador.

## 3. Falhar a execução depois de logar

Fluxo que trata o erro e responde "normalmente" fica como `Succeeded` no histórico do Power
Automate, o que esconde a falha de quem monitora pelo histórico. Marque como falha **depois** de
gravar o log:

```json
{
  "Falhar_execucao": {
    "type": "If",
    "expression": { "and": [{ "equals": ["@outputs('Compose_Log')?['Status']", 1] }] },
    "actions": {
      "Terminate": {
        "type": "Terminate",
        "inputs": {
          "runStatus": "Failed",
          "runError": { "code": "FluxoFalhou", "message": "@coalesce(outputs('Compose_Log')?['ErrorMessage'], 'Falha sem mensagem')" }
        },
        "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000015" }
      }
    },
    "else": { "actions": {} },
    "runAfter": { "Add_FlowRun": ["Succeeded"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000016" }
  }
}
```

Destino: ação dentro do escopo `Log`, depois de `Add_FlowRun`. [verificado: projeto de
referência]

## 4. Tensão com Response + Terminate

O padrão de [anatomia-flow.md](anatomia-flow.md) responde e **termina** em cada `Nega_*`. Um
`Terminate` encerra a execução imediatamente, então um escopo `Log` **depois** do principal não
roda nesses ramos `[não verificado: confirme no seu ambiente que a execução encerra sem rodar o
Log]`. No flow de recebimento HTTP (que não termina nos ramos) o `Log` irmão funciona como
descrito. Para flow chamado pelo app há três saídas, nenhuma testada nos projetos de referência:

1. **Resposta única**: cada ramo só `Compose`a o resultado e há um `Response` no fim, depois do
   `Log` (perde o `Terminate`; reescreve a anatomia).
2. **Log por ramo**: o escopo `Log` (ou um flow filho de log) dentro dos ramos que importam
   (`Catch`, falha de gravação), antes do `Response`; negações de autorização/validação não logam.
3. **Só o `Catch` loga**: negações são resposta normal, falha de conector é o que o suporte quer.
   É o mínimo viável e a recomendação inicial.

Registre a escolha em ADR do projeto.

## 5. Onde gravar quando os dados estão em SQL

**Em aberto** (F4): Dataverse (recomendado: já alimenta o Power BI) mesmo com dados em SQL, ou
tabela de log no próprio SQL via procedure (autônomo, mas exige DDL novo e o banco tende a
congelar). Decida no ADR do projeto antes de escrever o primeiro flow.

## 6. Correlação com o suporte

Inclua `workflow()['run']['name']` no `description` das respostas de **erro de infraestrutura**
(`Nega_conector`), por exemplo `concat('... Código: ', workflow()?['run']?['name'])`: o usuário
cola o código no chamado e o suporte acha a execução. Não coloque o código em negações de negócio
(ruído).

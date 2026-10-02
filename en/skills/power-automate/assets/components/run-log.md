# Execution log parent/child + failing the run history

> **File**: `run-log.json` · **Frequency**: rare · **Maturity**: unique
> **Depends on**: `token-cache-and-http-response` (`Escopo_Principal`); `batch-upsert-changeset` (variables); monitoring and execution tables

## Purpose

A scope sibling of the main one, with `runAfter` on `Succeeded`, `Failed` and `TimedOut`: it filters the first-level actions with `Failed`, builds the record in a `Compose`, updates or creates the monitored flow (parent), creates the execution (child) and, if there was a failure, ends the run as `Failed` **after** writing.

## When to use / when not to use

**Use**

- HTTP inbound flow; flow called by the app, with the `Terminate` caveat (below).

**Do not use**

- To store a token, password or raw body: never.

## Where to paste

Flow root, after `Escopo_Principal`.

## Inputs and outputs

**Reads**

- `result('Escopo_Principal')`, `triggerBody()`, `variables('Erros_lote')`, `variables('Linhas_com_erro')`.

**Exposes**

- Row in `<prefixo>_execucoes`, updated row in `<prefixo>_monitoramentos`; run marked `Failed` when there is an error.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Log`; the same content is in `run-log.json`). Fictitious GUIDs; connections: `<prefixo>_sharedcommondataserviceforapps`.


```json
{
  "nodeId": "Log",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Filtrar_acoes_falhas": {
        "type": "Query",
        "description": "First-level actions of Escopo_Principal with status Failed. result() only accepts Scope, Foreach and Until, not If.",
        "inputs": {
          "from": "@result('Escopo_Principal')",
          "where": "@equals(item()?['status'],'Failed')"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000194"
        }
      },
      "Compor_log": {
        "type": "Compose",
        "description": "One Compose instead of one variable per field. Safe with an empty list and null: if() evaluates both branches.",
        "inputs": {
          "RunId": "@workflow()?['run']?['name']",
          "StartTime": "@trigger()?['startTime']",
          "EndTime": "@utcNow()",
          "DurationSeconds": "@div(sub(ticks(utcNow()),ticks(trigger()?['startTime'])),10000000)",
          "RowsReceived": "@length(coalesce(triggerBody()?['dados'],json('[]')))",
          "RowsFailed": "@if(not(empty(body('Filtrar_acoes_falhas'))),length(coalesce(triggerBody()?['dados'],json('[]'))),variables('Linhas_com_erro'))",
          "Status": "@if(or(not(empty(body('Filtrar_acoes_falhas'))),greater(length(variables('Erros_lote')),0)),1,0)",
          "FailedAction": "@if(not(empty(body('Filtrar_acoes_falhas'))),last(body('Filtrar_acoes_falhas'))?['name'],if(greater(length(variables('Erros_lote')),0),'Enviar_lote',null))",
          "ErrorMessage": "@if(not(empty(body('Filtrar_acoes_falhas'))),take(string(last(body('Filtrar_acoes_falhas'))?['error']?['message']),4000),if(greater(length(variables('Erros_lote')),0),take(variables('Erros_lote'),4000),null))",
          "PayloadSize": "@length(string(triggerBody()))",
          "TriggerName": "@trigger()?['name']",
          "FlowId": "@workflow()?['name']",
          "FlowDisplayName": "@workflow()?['tags']?['flowDisplayName']"
        },
        "runAfter": {
          "Filtrar_acoes_falhas": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000195"
        }
      },
      "Listar_monitorado": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_monitoramentos",
            "$select": "<prefixo>_monitoramentoid,<prefixo>_totalexecucoes,<prefixo>_totalfalhas,<prefixo>_falhasseguidas",
            "$filter": "@concat('<prefixo>_flowid eq ''',workflow()?['name'],'''')",
            "$top": 1
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000196"
        }
      },
      "Se_monitorado_existe": {
        "type": "If",
        "expression": {
          "and": [
            {
              "greater": [
                "@length(outputs('Listar_monitorado')?['body/value'])",
                0
              ]
            }
          ]
        },
        "actions": {
          "Atualizar_monitorado": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "entityName": "<prefixo>_monitoramentos",
                "recordId": "@first(outputs('Listar_monitorado')?['body/value'])?['<prefixo>_monitoramentoid']",
                "item/<prefixo>_ultimostatus": "@outputs('Compor_log')?['Status']",
                "item/<prefixo>_ultimaexecucao": "@outputs('Compor_log')?['EndTime']",
                "item/<prefixo>_falhasseguidas": "@if(equals(outputs('Compor_log')?['Status'],1),add(coalesce(first(outputs('Listar_monitorado')?['body/value'])?['<prefixo>_falhasseguidas'],0),1),0)",
                "item/<prefixo>_totalfalhas": "@add(coalesce(first(outputs('Listar_monitorado')?['body/value'])?['<prefixo>_totalfalhas'],0),if(equals(outputs('Compor_log')?['Status'],1),1,0))",
                "item/<prefixo>_totalexecucoes": "@add(coalesce(first(outputs('Listar_monitorado')?['body/value'])?['<prefixo>_totalexecucoes'],0),1)"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                "connection": "shared_commondataserviceforapps",
                "operationId": "UpdateRecord"
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000197"
            }
          }
        },
        "else": {
          "actions": {
            "Criar_monitorado": {
              "type": "OpenApiConnection",
              "inputs": {
                "parameters": {
                  "entityName": "<prefixo>_monitoramentos",
                  "item/<prefixo>_flowid": "@outputs('Compor_log')?['FlowId']",
                  "item/<prefixo>_nome": "@outputs('Compor_log')?['FlowDisplayName']",
                  "item/<prefixo>_ultimostatus": "@outputs('Compor_log')?['Status']",
                  "item/<prefixo>_ultimaexecucao": "@outputs('Compor_log')?['EndTime']",
                  "item/<prefixo>_falhasseguidas": "@if(equals(outputs('Compor_log')?['Status'],1),1,0)",
                  "item/<prefixo>_totalfalhas": "@if(equals(outputs('Compor_log')?['Status'],1),1,0)",
                  "item/<prefixo>_totalexecucoes": 1
                },
                "host": {
                  "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                  "connection": "shared_commondataserviceforapps",
                  "operationId": "CreateRecord"
                }
              },
              "metadata": {
                "operationMetadataId": "00000000-0000-0000-0000-000000000198"
              }
            }
          }
        },
        "runAfter": {
          "Compor_log": [
            "Succeeded"
          ],
          "Listar_monitorado": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000199"
        }
      },
      "Registrar_execucao": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_execucoes",
            "item/<prefixo>_runidentifier": "@outputs('Compor_log')?['RunId']",
            "item/<prefixo>_flowidentifier": "@outputs('Compor_log')?['FlowId']",
            "item/<prefixo>_starttime": "@outputs('Compor_log')?['StartTime']",
            "item/<prefixo>_endtime": "@outputs('Compor_log')?['EndTime']",
            "item/<prefixo>_durationseconds": "@outputs('Compor_log')?['DurationSeconds']",
            "item/<prefixo>_runstatus": "@outputs('Compor_log')?['Status']",
            "item/<prefixo>_triggername": "@outputs('Compor_log')?['TriggerName']",
            "item/<prefixo>_rowsreceived": "@outputs('Compor_log')?['RowsReceived']",
            "item/<prefixo>_rowsfailed": "@outputs('Compor_log')?['RowsFailed']",
            "item/<prefixo>_inputpayloadsize": "@outputs('Compor_log')?['PayloadSize']",
            "item/<prefixo>_errorcode": "@outputs('Compor_log')?['FailedAction']",
            "item/<prefixo>_errormessage": "@outputs('Compor_log')?['ErrorMessage']"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "CreateRecord"
          }
        },
        "runAfter": {
          "Compor_log": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000200"
        }
      },
      "Falhar_execucao": {
        "type": "If",
        "description": "Only after the log is written: the handled failure stops showing as Succeeded in the run history.",
        "expression": {
          "and": [
            {
              "equals": [
                "@outputs('Compor_log')?['Status']",
                1
              ]
            }
          ]
        },
        "actions": {
          "Terminar_com_falha": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Failed",
              "runError": {
                "code": "FluxoFalhou",
                "message": "@coalesce(outputs('Compor_log')?['ErrorMessage'],'Failure without a message')"
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000201"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Se_monitorado_existe": [
            "Succeeded"
          ],
          "Registrar_execucao": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000202"
        }
      }
    },
    "runAfter": {
      "Escopo_Principal": [
        "Succeeded",
        "Failed",
        "TimedOut"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000203"
    }
  },
  "allConnectionData": {
    "Listar_monitorado": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
        },
        "connection": {
          "id": "<prefixo>_sharedcommondataserviceforapps"
        },
        "connectionName": "<prefixo>_sharedcommondataserviceforapps",
        "impersonation": {}
      },
      "referenceKey": "shared_commondataserviceforapps"
    },
    "Atualizar_monitorado": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
        },
        "connection": {
          "id": "<prefixo>_sharedcommondataserviceforapps"
        },
        "connectionName": "<prefixo>_sharedcommondataserviceforapps",
        "impersonation": {}
      },
      "referenceKey": "shared_commondataserviceforapps"
    },
    "Criar_monitorado": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
        },
        "connection": {
          "id": "<prefixo>_sharedcommondataserviceforapps"
        },
        "connectionName": "<prefixo>_sharedcommondataserviceforapps",
        "impersonation": {}
      },
      "referenceKey": "shared_commondataserviceforapps"
    },
    "Registrar_execucao": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
        },
        "connection": {
          "id": "<prefixo>_sharedcommondataserviceforapps"
        },
        "connectionName": "<prefixo>_sharedcommondataserviceforapps",
        "impersonation": {}
      },
      "referenceKey": "shared_commondataserviceforapps"
    }
  },
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

## Parameters to change

| Item | Value in the JSON | Change to |
|---|---|---|
| `Escopo_Principal` | name of the root scope | the name of your scope |
| `<prefixo>_monitoramentos`, `<prefixo>_execucoes` | parent and child tables | AS-BUILT tables (`dataverse` skill) |
| `FluxoFalhou` | `Terminate` code | the project's code |
| `take(..., 4000)` | message size | the column size |

## runAfter

The root depends on `Escopo_Principal` with `Succeeded`, `Failed`, `TimedOut`; `Falhar_execucao` depends on the parent and the child.

## Pitfalls

- `Skipped` is left out on purpose: with the main scope `Skipped` there is no failure to record and the filter would return status 0. The verifier warns (F009): expected.
- `errorcode` holds the **name of the action** that failed, not a code; whoever consumes it treats it as 'action with error'.
- `result()` only accepts `Scope`, `Foreach` and `Until` (not `If`) and returns the first level: a failure inside an `If` shows up as a failure of the first-level action that contains it.
- `Terminate` after `Response + Terminate` in the deny branches ends the run before the `Log`: in the flow called by the app the `Log` only runs where execution reaches it. Minimum viable: only the `Catch` logs; a business denial does not log.
- The log itself can fail and must not take down the response to the caller; it already runs after the `Response` in the HTTP inbound flow.
- Standardize the columns every flow fills; old flows with different columns leave the error report null for the new ones.
- `if()` evaluates both branches: the `Compose` expressions are safe with an empty list and null.

## Variations

- Child only: delete `Listar_monitorado` and `Se_monitorado_existe` and make `Falhar_execucao` depend on `Registrar_execucao`.
- SQL target: replace the `ListRecords/CreateRecord` with a procedure; open decision in the project ADR.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/run-log.json
```

Expected result: `0 error(s), 2 warning(s)`.

Intrinsic warnings of the isolated component:

- `F006` (reference to an action outside the pasted snippet): `Escopo_Principal`. These are the block's **inputs**: they exist in the target flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.
- `F009` on `Log`: expected, see *Pitfalls*.

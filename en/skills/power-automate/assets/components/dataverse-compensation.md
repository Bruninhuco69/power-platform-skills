# Compensate in Dataverse (delete what was left orphaned)

> **File**: `dataverse-compensation.json` · **Frequency**: rare · **Maturity**: designed [unverified]: basis of a generated flow, never returned by the designer
> **Depends on**: `normalize-input`; Dataverse connector; `deny-response-terminate`

## Purpose

`Try_criar` creates the order and the item. If something fails, `Compensar_criar` uses `result('Try_criar')` to find out whether the order was actually created and, only then, deletes it; it responds `error` and ends. On success, `Responder_criar` responds.

## When to use / when not to use

**Use**

- Each Dataverse `Add a new row` is a commit; without a changeset, compensating in reverse order is the undo.

**Do not use**

- Independent rows in a batch: use `$batch` (`batch-upsert-changeset`).
- Writing to SQL: the procedure opens the transaction.

## Where to paste

Inside `Caso_<acao>` (or `Try_pedido`), in place of `write-via-procedure`.

## Inputs and outputs

**Reads**

- `outputs('Normalizar_gravar')`.

**Exposes**

- Success response with the order GUID; or `Nega_criacao` and end.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_criar_com_compensacao`; the same content is in `dataverse-compensation.json`). Fictitious GUIDs; connections: `<prefixo>_sharedcommondataserviceforapps`.

```json
{
  "nodeId": "Bloco_criar_com_compensacao",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Try_criar": {
        "type": "Scope",
        "actions": {
          "Criar_pedido": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "entityName": "<prefixo>_pedidos",
                "item/<prefixo>_descricao": "@outputs('Normalizar_gravar')?['descricao']",
                "item/<prefixo>_unidade": "@outputs('Normalizar_gravar')?['unidade']"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                "connection": "shared_commondataserviceforapps",
                "operationId": "CreateRecord"
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000087"
            }
          },
          "Criar_item": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "entityName": "<prefixo>_itenspedido",
                "item/<prefixo>_Pedido@odata.bind": "@concat('/<prefixo>_pedidos(',body('Criar_pedido')?['<prefixo>_pedidoid'],')')",
                "item/<prefixo>_quantidade": "@outputs('Normalizar_gravar')?['quantidade']"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                "connection": "shared_commondataserviceforapps",
                "operationId": "CreateRecord"
              }
            },
            "runAfter": {
              "Criar_pedido": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000088"
            }
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000089"
        }
      },
      "Compensar_criar": {
        "type": "Scope",
        "actions": {
          "Filtrar_pedido_criado": {
            "type": "Query",
            "inputs": {
              "from": "@result('Try_criar')",
              "where": "@and(equals(item()?['name'],'Criar_pedido'),equals(item()?['status'],'Succeeded'))"
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000090"
            }
          },
          "Se_pedido_criado": {
            "type": "If",
            "expression": {
              "and": [
                {
                  "greater": [
                    "@length(body('Filtrar_pedido_criado'))",
                    0
                  ]
                }
              ]
            },
            "actions": {
              "Apagar_pedido_orfao": {
                "type": "OpenApiConnection",
                "inputs": {
                  "parameters": {
                    "entityName": "<prefixo>_pedidos",
                    "recordId": "@body('Criar_pedido')?['<prefixo>_pedidoid']"
                  },
                  "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                    "connection": "shared_commondataserviceforapps",
                    "operationId": "DeleteRecord"
                  }
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000091"
                }
              }
            },
            "else": {
              "actions": {}
            },
            "runAfter": {
              "Filtrar_pedido_criado": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000092"
            }
          },
          "Nega_criacao": {
            "type": "Response",
            "kind": "PowerApp",
            "inputs": {
              "schema": {
                "type": "object",
                "properties": {
                  "status": {
                    "title": "status",
                    "x-ms-dynamically-added": true,
                    "type": "string"
                  },
                  "description": {
                    "title": "description",
                    "x-ms-dynamically-added": true,
                    "type": "string"
                  },
                  "id": {
                    "title": "id",
                    "x-ms-dynamically-added": true,
                    "type": "string"
                  },
                  "url": {
                    "title": "url",
                    "x-ms-dynamically-added": true,
                    "type": "string"
                  }
                },
                "additionalProperties": {}
              },
              "statusCode": 200,
              "body": {
                "status": "error",
                "description": "Could not register the order. Try again; if it persists, tell support.",
                "id": "",
                "url": ""
              }
            },
            "runAfter": {
              "Se_pedido_criado": [
                "Succeeded",
                "Failed",
                "Skipped",
                "TimedOut"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000093"
            }
          },
          "Nega_criacao_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_criacao": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000094"
            }
          }
        },
        "runAfter": {
          "Try_criar": [
            "Failed",
            "TimedOut"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000095"
        }
      },
      "Responder_criar": {
        "type": "Response",
        "kind": "PowerApp",
        "inputs": {
          "schema": {
            "type": "object",
            "properties": {
              "status": {
                "title": "status",
                "x-ms-dynamically-added": true,
                "type": "string"
              },
              "description": {
                "title": "description",
                "x-ms-dynamically-added": true,
                "type": "string"
              },
              "id": {
                "title": "id",
                "x-ms-dynamically-added": true,
                "type": "string"
              },
              "url": {
                "title": "url",
                "x-ms-dynamically-added": true,
                "type": "string"
              }
            },
            "additionalProperties": {}
          },
          "statusCode": 200,
          "body": {
            "status": "success",
            "description": "Order registered.",
            "id": "@{body('Criar_pedido')?['<prefixo>_pedidoid']}",
            "url": ""
          }
        },
        "runAfter": {
          "Try_criar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000096"
        }
      }
    },
    "runAfter": {
      "Bloco_normalizar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000097"
    }
  },
  "allConnectionData": {
    "Criar_pedido": {
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
    "Criar_item": {
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
    "Apagar_pedido_orfao": {
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

| Item | Value in the JSON | Replace with |
|---|---|---|
| `<prefixo>_pedidos`, `<prefixo>_itenspedido` | entity sets | AS-BUILT names |
| `item/<prefixo>_Pedido` + `@odata.bind` suffix | lookup from the item to the order | name of the lookup's navigation property (case-sensitive) |
| `<prefixo>_pedidoid` | primary key | AS-BUILT key column |

## runAfter

`Compensar_criar` depends on `Try_criar` with `Failed` and `TimedOut`; `Responder_criar` with `Succeeded`.

## Pitfalls

- `Compensar_criar` deliberately does **not** include `Skipped`: with `Skipped` it would delete when nothing was created. This is the inverse of the `Catch` rule and the verifier warns (F009); the warning is expected.
- Delete the orphan only if `Criar_pedido` ended `Succeeded` (filter over `result()`): without the filter, `DeleteRecord` runs with an empty `recordId` and fails.
- The compensation can fail too: `Nega_criacao` runs in any state of the delete, and the message tells the user to notify support if it persists. Record it in `run-log`.
- `result()` returns only first-level actions of the scope: `Criar_pedido` and `Criar_item` must be direct children of `Try_criar`.
- If creating the item is repeatable, prefer an alternate key and upsert over compensating.

## Variations

- More than two steps: compensate in reverse order, one filter and one `If` per step created.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/dataverse-compensation.json
```

Expected result: `0 error(s), 4 warning(s)`.

Warnings intrinsic to the component on its own:

- `F006` (reference to an action outside the pasted snippet): `Normalizar_gravar`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.
- `F009` in `Compensar_criar`: expected, see *Pitfalls*.

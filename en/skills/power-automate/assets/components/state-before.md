# Read the record's actual state before writing

> **File**: `state-before.json` · **Frequency**: common · **Maturity**: stable
> **Depends on**: `normalize-input`; SQL connector; `<tabela_pedido>`

## Purpose

Reads the record (`GetItems_V2`, `$top 1`) by the normalized id and denies with `Nega_inexistente` when no row comes back. It is the source of truth for unit scope and for 'nothing changed'.

## When to use / when not to use

**Use**

- Edit, close, resolve: any action on a record that already exists.

**Do not use**

- Create (the record does not exist yet): compare the parameter that will be written.

## Where to paste

Inside `Caso_<acao>`, after `Bloco_normalizar`.

## Inputs and outputs

**Reads**

- `outputs('Normalizar_gravar')?['idNumero']`.

**Exposes**

- `body('Estado_antes_gravar')?['value']`: list of 0 or 1 rows; `first(...)` reads the record.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_estado_antes`; the same content is in `state-before.json`). Fictitious GUIDs; connections: `<prefixo>_sharedsql`.


```json
{
  "nodeId": "Bloco_estado_antes",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Estado_antes_gravar": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "server": "default",
            "database": "default",
            "table": "[dbo].[<tabela_pedido>]",
            "$filter": "@concat('Id_Pedido eq ',string(outputs('Normalizar_gravar')?['idNumero']))",
            "$top": 1
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sql",
            "connection": "shared_sql",
            "operationId": "GetItems_V2"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000036"
        }
      },
      "Se_pedido_inexistente_gravar": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(coalesce(body('Estado_antes_gravar')?['value'],json('[]')))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Nega_inexistente_gravar": {
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
                "description": "Order not found.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000037"
            }
          },
          "Nega_inexistente_gravar_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_inexistente_gravar": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000038"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Estado_antes_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000039"
        }
      }
    },
    "runAfter": {
      "Bloco_normalizar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000040"
    }
  },
  "allConnectionData": {
    "Estado_antes_gravar": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_sql"
        },
        "connection": {
          "id": "<prefixo>_sharedsql"
        },
        "connectionName": "<prefixo>_sharedsql"
      },
      "referenceKey": "shared_sql"
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
| `<tabela_pedido>` | table in brackets | AS-BUILT table name |
| `Id_Pedido` | id column | AS-BUILT column |
| `$top` | `1` | keep |
| `*_gravar` names | action suffix | replace with the suffix of your case |

## runAfter

The root depends on `Bloco_normalizar`; `Se_pedido_inexistente_gravar` depends on `Estado_antes_gravar`.

## Pitfalls

- Compare the unit of the **actual record**, not the parameter's: the parameter is ignored outside create, and checking it would let the caller choose their own authorization.
- An action that writes to two records reads and checks both.
- `$filter` on a `bit` uses `true`/`false`, not `1`/`0`.
- A wrong column name in `$filter` returns an empty list, which looks like 'not found'.

## Variations

- Dataverse: `GetItem` by `recordId` (when the app has the GUID) or `ListRecords` with `$top 1`; reading with `first(body(...)?['value'])` is the same.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/state-before.json
```

Expected result: `0 error(s), 1 warning(s)`.

Warnings intrinsic to the component on its own:

- `F006` (reference to an action outside the pasted snippet): `Normalizar_gravar`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

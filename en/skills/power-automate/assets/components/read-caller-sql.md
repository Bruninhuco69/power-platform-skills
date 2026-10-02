# Read the caller through a procedure and deny unknown users

> **File**: `read-caller-sql.json` · **Frequency**: common · **Maturity**: stable
> **Depends on**: `identify-caller`; SQL connector; `<procedure_obter_chamador>`

## Purpose

Creates the `Try_pedido` scope (root of the flow's work), calls the procedure that returns the user's row already joined to the profile and flags, and denies with `Response` + `Terminate` when no row comes back (unknown or inactive user).

## When to use / when not to use

**Use**

- Flow whose profile lives in SQL.

**Do not use**

- Profile in Dataverse: use `read-caller-dataverse`.
- When the caller needs no profile (open flow): it does not exist.

## Where to paste

Root of the flow's scope, after `Bloco_chamador`. All the following components (switch, authorize...) are pasted **inside** `Try_pedido`.

## Inputs and outputs

**Reads**

- `outputs('Chamador')`.

**Exposes**

- `body('Ler_chamador')?['ResultSets']?['Table1']?[0]`: caller row (`Flg_*` flags, `Id_Usuario`, unit). Zero rows denies and terminates.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Try_pedido`; the same content is in `read-caller-sql.json`). Fictitious GUIDs; connections: `<prefixo>_sharedsql`.

```json
{
  "nodeId": "Try_pedido",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Ler_chamador": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "server": "default",
            "database": "default",
            "procedure": "[dbo].[<procedure_obter_chamador>]",
            "parameters/Email_Chamador": "@outputs('Chamador')"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sql",
            "connection": "shared_sql",
            "operationId": "ExecuteProcedure_V2"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000008"
        }
      },
      "Se_chamador_desconhecido": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(coalesce(body('Ler_chamador')?['ResultSets']?['Table1'],json('[]')))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Nega_chamador": {
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
                "description": "Your profile does not allow this action.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000009"
            }
          },
          "Nega_chamador_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_chamador": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000010"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Ler_chamador": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000011"
        }
      }
    },
    "runAfter": {
      "Bloco_chamador": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000012"
    }
  },
  "allConnectionData": {
    "Ler_chamador": {
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
| `<procedure_obter_chamador>` | name in brackets, `[dbo].[...]` | the procedure's AS-BUILT name in the environment (`sql-procedures` skill); never the one in the document |
| `parameters/Email_Chamador` | `@outputs('Chamador')` | the procedure's real parameter name |
| `server` and `database` | `default` | keep: the real server comes from the connection reference (R4) |
| `Try_pedido` | scope name | `Try_<flow>`; the `Catch` points to it |
| `Nega_chamador` message | generic profile sentence | the same sentence as every profile denial |

## runAfter

The root depends on `Bloco_chamador`. `Se_chamador_desconhecido` depends on `Ler_chamador`. The `Catch` (`connector-catch`) depends on `Try_pedido` with `Failed`, `TimedOut`, `Skipped`.

## Pitfalls

- The denial message is the same for an unknown user and for a user without permission: do not reveal which of the two it is.
- SQL `bit` arrives as `true`/`false`, not `1`: the flags are read by comparing the lowercase text with `'1'` and `'true'` (see `authorize-by-flag`).
- Zero rows = deny. Never treat a missing profile as a default profile.
- This action is the most expensive in the flow in time: one single read per run, all flags at once.

## Variations

- Read straight from the table (`GetItems_V2`) when there is no procedure: loses the profile join; get the unit and the flags in a view.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/read-caller-sql.json
```

Expected result: `0 error(s), 1 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted snippet): `Chamador`. These are the block's **inputs**: they exist in the target flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

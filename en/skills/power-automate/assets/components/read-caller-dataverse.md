# Read the caller and the profile in Dataverse

> **File**: `read-caller-dataverse.json` · **Frequency**: common · **Maturity**: designed [unverified]: generated, never returned by the designer
> **Depends on**: `identify-caller`; Dataverse connector; tables `<prefixo>_usuarios` and `<prefixo>_perfis`

## Purpose

Creates `Try_pedido`, looks up the active user by UPN, denies when none exists and reads the profile row (permission flags) through the user's lookup.

## When to use / when not to use

**Use**

- Project on the Dataverse track; profile as a table with Boolean permission columns.

**Do not use**

- Profile in SQL: use `read-caller-sql`.

## Where to paste

Root of the flow's scope, after `Bloco_chamador`. The other components go inside `Try_pedido`.

## Inputs and outputs

**Reads**

- `outputs('Chamador')`.

**Exposes**

- `body('Ler_chamador')?['value']` (user) and `body('Ler_perfil')?['value']` (profile and flags).

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Try_pedido`; the same content is in `read-caller-dataverse.json`). Fictitious GUIDs; connections: `<prefixo>_sharedcommondataserviceforapps`.

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
            "entityName": "<prefixo>_usuarios",
            "$filter": "@concat('<prefixo>_upn eq ''',replace(outputs('Chamador'),'''',''''''),''' and <prefixo>_ativo eq true')",
            "$top": 1
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000013"
        }
      },
      "Se_chamador_desconhecido": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(coalesce(body('Ler_chamador')?['value'],json('[]')))",
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
              "operationMetadataId": "00000000-0000-0000-0000-000000000014"
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
              "operationMetadataId": "00000000-0000-0000-0000-000000000015"
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
          "operationMetadataId": "00000000-0000-0000-0000-000000000016"
        }
      },
      "Ler_perfil": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_perfis",
            "$filter": "@concat('<prefixo>_perfilid eq ',coalesce(first(body('Ler_chamador')?['value'])?['_<prefixo>_perfil_value'],'null'))",
            "$top": 1
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "runAfter": {
          "Se_chamador_desconhecido": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000017"
        }
      }
    },
    "runAfter": {
      "Bloco_chamador": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000018"
    }
  },
  "allConnectionData": {
    "Ler_chamador": {
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
    "Ler_perfil": {
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
| `<prefixo>_usuarios`, `<prefixo>_perfis` | entity sets | AS-BUILT names read from the environment (AS-BUILT-NAMES) |
| `<prefixo>_upn`, `<prefixo>_ativo` | logical columns | real logical names (in flows and OData the logical name applies, not the display name) |
| `_<prefixo>_perfil_value` | the user's lookup to the profile | the lookup name; if the profile is a Choice, filter by the formatted value |

## runAfter

The root depends on `Bloco_chamador`; `Ler_perfil` depends on `Se_chamador_desconhecido`.

## Pitfalls

- A filter with a wrong column name raises no error: it returns an empty list, indistinguishable from 'no record'. Check the table schema, never a filtered extract.
- The UPN goes into `$filter` with the apostrophe doubled (`replace(x,'''','''''')`): without it a name with an apostrophe breaks the query.
- Without a resolved profile, `$filter` becomes `eq null` and returns empty: authorization denies (fail-closed). Keep it that way.
- A profile stored as a Choice arrives as a number; the text is in `<column>@OData.Community.Display.V1.FormattedValue`.

## Variations

- Permission flag for `authorize-by-flag` in this design:

```text
@not(equals(first(body('Ler_perfil')?['value'])?['<prefixo>_podegravar'],true))
```

Destination: `expression` of an `If` (`equals` with `@true`). A Dataverse Boolean column arrives as `true`/`false`; missing denies.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/read-caller-dataverse.json
```

Expected result: `0 error(s), 1 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted snippet): `Chamador`. These are the block's **inputs**: they exist in the target flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

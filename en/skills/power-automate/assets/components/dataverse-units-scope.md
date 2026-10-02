# Scope across several units (Dataverse track)

> **File**: `dataverse-units-scope.json` · **Frequency**: occasional · **Maturity**: designed [unverified]: generated, never returned by the designer
> **Depends on**: `read-caller-dataverse`; user-unit link table

## Purpose

Builds the list of allowed units (links plus the primary unit), computes `Pode_todas_unidades` from the profile flag, and denies a user with no unit or with a unit that does not match the record.

## When to use / when not to use

**Use**

- Profile with several units, on Dataverse.

**Do not use**

- One unit only and data in SQL: `unit-scope`.

## Where to paste

Inside `Try_pedido` (single-action flow) or the `Caso`, after `Ler_perfil`.

## Inputs and outputs

**Reads**

- `outputs('Chamador')`, `body('Ler_chamador')`, `body('Ler_perfil')`, the trigger unit parameter.

**Exposes**

- `outputs('Unidades_permitidas')`, `outputs('Pode_todas_unidades')`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_escopo_unidades`; the same content is in `dataverse-units-scope.json`). Fictitious GUIDs; connections: `<prefixo>_sharedcommondataserviceforapps`.


```json
{
  "nodeId": "Bloco_escopo_unidades",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Minhas_unidades": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_usuariounidades",
            "$filter": "@concat('<prefixo>_upn eq ''',replace(outputs('Chamador'),'''',''''''),'''')"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000046"
        }
      },
      "Lista_minhas_unidades": {
        "type": "Select",
        "inputs": {
          "from": "@coalesce(body('Minhas_unidades')?['value'],json('[]'))",
          "select": "@trim(string(item()?['<prefixo>_unidade']))"
        },
        "runAfter": {
          "Minhas_unidades": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000047"
        }
      },
      "Unidades_permitidas": {
        "type": "Compose",
        "inputs": "@union(body('Lista_minhas_unidades'),if(empty(trim(string(first(body('Ler_chamador')?['value'])?['<prefixo>_unidade']))),json('[]'),createArray(trim(string(first(body('Ler_chamador')?['value'])?['<prefixo>_unidade'])))))",
        "runAfter": {
          "Lista_minhas_unidades": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000048"
        }
      },
      "Pode_todas_unidades": {
        "type": "Compose",
        "inputs": "@equals(first(body('Ler_perfil')?['value'])?['<prefixo>_todasunidades'],true)",
        "runAfter": {
          "Unidades_permitidas": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000049"
        }
      },
      "Se_sem_unidade": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@outputs('Pode_todas_unidades')",
                false
              ]
            },
            {
              "equals": [
                "@empty(trim(join(outputs('Unidades_permitidas'),'')))",
                true
              ]
            }
          ]
        },
        "actions": {
          "Nega_sem_unidade": {
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
                "description": "Your user is not linked to any unit. Contact support.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000050"
            }
          },
          "Nega_sem_unidade_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_sem_unidade": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000051"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Pode_todas_unidades": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000052"
        }
      },
      "Se_unidade_alheia": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@outputs('Pode_todas_unidades')",
                false
              ]
            },
            {
              "or": [
                {
                  "equals": [
                    "@empty(trim(coalesce(triggerBody()['text_3'],'')))",
                    true
                  ]
                },
                {
                  "equals": [
                    "@contains(outputs('Unidades_permitidas'),toUpper(trim(coalesce(triggerBody()['text_3'],''))))",
                    false
                  ]
                }
              ]
            }
          ]
        },
        "actions": {
          "Nega_unidade_alheia": {
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
                "description": "You do not have access to this record's unit.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000053"
            }
          },
          "Nega_unidade_alheia_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_unidade_alheia": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000054"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Se_sem_unidade": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000055"
        }
      }
    },
    "runAfter": {
      "Ler_perfil": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000056"
    }
  },
  "allConnectionData": {
    "Minhas_unidades": {
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
| `<prefixo>_usuariounidades` | link table | AS-BUILT name |
| `<prefixo>_unidade`, `<prefixo>_todasunidades` | columns | AS-BUILT logical names |
| `param(3)` (`text_3`) | trigger unit | position of the unit parameter |

## runAfter

The root depends on `Ler_perfil`; the `If` actions chain from `Pode_todas_unidades`.

## Pitfalls

- With no assignment the list arrives as `['']`, a one-item array that `empty()` treats as non-empty: test `empty(trim(join(list,'')))`.
- Optional filter where 'all' = `null`: wire the raw `null`, without `coalesce` (`''` matches nothing and the report comes out empty for someone who sees everything).
- In an action on an existing record, compare against the unit of the record you read, not the parameter.
- A user value that goes into `$filter` gets a doubled apostrophe.

## Variations

- List of requested units (report): `intersection(requested, allowed)` and deny if the result is smaller than the request.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/dataverse-units-scope.json
```

Expected result: `0 error(s), 3 warning(s)`.

Warnings intrinsic to the component on its own:

- `F006` (reference to an action outside the pasted snippet): `Chamador`, `Ler_chamador`, `Ler_perfil`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

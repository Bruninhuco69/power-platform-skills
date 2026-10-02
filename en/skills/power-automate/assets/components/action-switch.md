# Switch by action, with authorization per case

> **File**: `action-switch.json` · **Frequency**: common · **Maturity**: stable
> **Depends on**: `read-caller-sql`; `authorize-by-flag`; `deny-response-terminate`

## Purpose

`Switch` on `toLower(trim(triggerBody()['text']))`, one `Caso_<acao>` per action (each starts with its own authorization) and a `default` that responds `error` **naming** the value received.

## When to use / when not to use

**Use**

- Flow with 2 or more actions (create, edit, close...).

**Do not use**

- Single-action flow: use `authorize-by-flag` directly.
- To derive a value: use `derive-value-switch`.

## Where to paste

Inside `Try_pedido`, after `Se_chamador_desconhecido`.

## Inputs and outputs

**Reads**

- `triggerBody()['text']`: the action name (1st trigger parameter).

**Exposes**

- The chosen branch runs the blocks pasted into each `Caso_`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Switch_acao`; the same content is in `action-switch.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Switch_acao",
  "serializedValue": {
    "type": "Switch",
    "expression": "@toLower(trim(coalesce(triggerBody()['text'],'')))",
    "cases": {
      "Caso_gravar": {
        "case": "gravar",
        "actions": {
          "Autorizar_gravar": {
            "type": "If",
            "expression": {
              "and": [
                {
                  "equals": [
                    "@not(or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'true')))",
                    "@true"
                  ]
                }
              ]
            },
            "actions": {
              "Nega_perm_gravar": {
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
                    "description": "Your role does not allow this action.",
                    "id": "",
                    "url": ""
                  }
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000025"
                }
              },
              "Nega_perm_gravar_fim": {
                "type": "Terminate",
                "inputs": {
                  "runStatus": "Succeeded"
                },
                "runAfter": {
                  "Nega_perm_gravar": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000026"
                }
              }
            },
            "else": {
              "actions": {}
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000027"
            }
          }
        }
      },
      "Caso_excluir": {
        "case": "excluir",
        "actions": {
          "Autorizar_excluir": {
            "type": "If",
            "expression": {
              "and": [
                {
                  "equals": [
                    "@not(or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Excluir'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Excluir'],'0'))),'true')))",
                    "@true"
                  ]
                }
              ]
            },
            "actions": {
              "Nega_perm_excluir": {
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
                    "description": "Your role does not allow this action.",
                    "id": "",
                    "url": ""
                  }
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000028"
                }
              },
              "Nega_perm_excluir_fim": {
                "type": "Terminate",
                "inputs": {
                  "runStatus": "Succeeded"
                },
                "runAfter": {
                  "Nega_perm_excluir": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000029"
                }
              }
            },
            "else": {
              "actions": {}
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000030"
            }
          }
        }
      }
    },
    "default": {
      "actions": {
        "Nega_acao": {
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
              "description": "@{concat('Unknown action: ',toLower(trim(coalesce(triggerBody()['text'],''))),'.')}",
              "id": "",
              "url": ""
            }
          },
          "metadata": {
            "operationMetadataId": "00000000-0000-0000-0000-000000000031"
          }
        },
        "Nega_acao_fim": {
          "type": "Terminate",
          "inputs": {
            "runStatus": "Succeeded"
          },
          "runAfter": {
            "Nega_acao": [
              "Succeeded"
            ]
          },
          "metadata": {
            "operationMetadataId": "00000000-0000-0000-0000-000000000032"
          }
        }
      }
    },
    "runAfter": {
      "Se_chamador_desconhecido": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000033"
    }
  },
  "allConnectionData": {},
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

## Parameters to change

| Item | Value in the JSON | Change to |
|---|---|---|
| `Caso_gravar`, `Caso_excluir` | case names | `Caso_<acao>`: **never** equal to an action name |
| `case` | `gravar`, `excluir` | the action value in lowercase, equal to what the app sends |
| `Autorizar_*`, `Nega_perm_*` | names | one pair per case; change the flag |
| `default` | message with the value | keep: never fall silently into a default value |

## runAfter

The root depends on `Se_chamador_desconhecido`. Inside each case the first node has no `runAfter`.

## Pitfalls

- The designer puts cases and actions in the same namespace: a case with the same name as an action breaks the paste with `Required property 'case' not found` pointing to a case that **has** `case` (F008 flags it).
- A duplicated action name in different cases silently becomes `_1` and the tokens keep pointing to the original: suffix by action (`_gravar`, `_excluir`).
- The action comes from the app: normalize with `toLower(trim())` and treat the `default` as a contract error, not as a default action.
- Each case authorizes its **own** flag; copying the `Autorizar` from another case without changing the column reopens the single-gate defect.

## Variations

- More cases: duplicate the `Caso_*` pair and change names, `case` and flag.
- Value derivation by type: nest with `derive-value-switch`, each case with a `Compose` of its own name.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/action-switch.json
```

Expected result: `0 error(s), 2 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted fragment): `Ler_chamador`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow the same fragment passes without this warning.

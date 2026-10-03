# Derive a value with a nested Switch

> **File**: `derive-value-switch.json` · **Frequency**: rare · **Maturity**: unique: baseline from one flow; `coalesce` read of cases that did not run [unverified]
> **Depends on**: `normalize-input`

## Purpose

A `Switch` where each case is a `Compose` with its **own** name (`Destino_<value>`). Consumers read the result with `coalesce(outputs('Destino_aberto'), outputs('Destino_fechado'))`.

## When to use / when not to use

**Use**

- Derivation from a table of combinations, instead of an 8-level nested `if()`.

**Do not use**

- Only two states: a plain `if()` is enough.

## Where to paste

Inside `Caso_<acao>`, after `Bloco_normalizar`.

## Inputs and outputs

**Reads**

- Normalized decision value (here, `situacao`, the 7th parameter).

**Exposes**

- One of the `Destino_*` actions runs; `default` denies with `Nega_situacao`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_derivar_destino`; the same content is in `derive-value-switch.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Bloco_derivar_destino",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Derivar_destino_gravar": {
        "type": "Switch",
        "expression": "@toLower(trim(coalesce(trim(coalesce(triggerBody()['text_6'],'')),'')))",
        "cases": {
          "Caso_destino_aberto": {
            "case": "aberto",
            "actions": {
              "Destino_aberto": {
                "type": "Compose",
                "inputs": "In progress",
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000072"
                }
              }
            }
          },
          "Caso_destino_fechado": {
            "case": "fechado",
            "actions": {
              "Destino_fechado": {
                "type": "Compose",
                "inputs": "Archived",
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000073"
                }
              }
            }
          }
        },
        "default": {
          "actions": {
            "Nega_situacao": {
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
                  "description": "Unknown status.",
                  "id": "",
                  "url": ""
                }
              },
              "metadata": {
                "operationMetadataId": "00000000-0000-0000-0000-000000000074"
              }
            },
            "Nega_situacao_fim": {
              "type": "Terminate",
              "inputs": {
                "runStatus": "Succeeded"
              },
              "runAfter": {
                "Nega_situacao": [
                  "Succeeded"
                ]
              },
              "metadata": {
                "operationMetadataId": "00000000-0000-0000-0000-000000000075"
              }
            }
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000076"
        }
      }
    },
    "runAfter": {
      "Bloco_normalizar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000077"
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
| `aberto`, `fechado` | decision values | the ones from your domain |
| `In progress`, `Archived` | derived values | the text/code to be saved |
| `Destino_*` | the `Compose` of each case | own name per case |

## runAfter

The root depends on `Bloco_normalizar`.

## Pitfalls

- Case and action share the designer's namespace: `Caso_destino_aberto` ≠ `Destino_aberto` (F008).
- Reading `outputs()` of a `Compose` that did not run: the reference project uses `coalesce` over all cases and the designer accepted it; the runtime behavior with cases that did not run was not recorded `[unverified]`. Test with each value.
- `default` is required: an unknown value denies, it never falls into a default destination.

## Variations

- Combination of two states: outer `Switch` on one and inner `Switch` on the other, each leaf with a `Compose` of its own name.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/derive-value-switch.json
```

Expected result: `0 error(s), 0 warning(s)`.

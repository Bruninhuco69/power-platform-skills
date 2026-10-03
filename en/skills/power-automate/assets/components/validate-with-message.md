# Validate with the first error message

> **File**: `validate-with-message.json` · **Frequency**: common · **Maturity**: stable
> **Depends on**: `normalize-input`; `deny-response-terminate`

## Purpose

`Validar_gravar` is a `Compose` with a chain of `if()` that returns the first applicable message or `''`; `Se_invalido_gravar` denies with that message. One expression, one message, testable without running the write.

## When to use / when not to use

**Use**

- Before every write or export.

**Do not use**

- To check permission or scope (they deny with their own message, earlier).

## Where to paste

Inside `Caso_<acao>`, after the scope.

## Inputs and outputs

**Reads**

- `outputs('Normalizar_gravar')`, records read earlier.

**Exposes**

- `outputs('Validar_gravar')`: text, empty when valid.

## JSON

Destination: `Ctrl+V` at the designer's insertion point (clipboard scope envelope, `nodeId` `Bloco_validar`; the same content is in `validate-with-message.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Bloco_validar",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Validar_gravar": {
        "type": "Compose",
        "inputs": "@if(empty(outputs('Normalizar_gravar')?['descricao']),'Enter a description.',if(less(outputs('Normalizar_gravar')?['quantidade'],1),'Enter a quantity greater than zero.',''))",
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000057"
        }
      },
      "Se_invalido_gravar": {
        "type": "If",
        "expression": {
          "and": [
            {
              "greater": [
                "@length(outputs('Validar_gravar'))",
                0
              ]
            }
          ]
        },
        "actions": {
          "Nega_gravar": {
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
                "description": "@{outputs('Validar_gravar')}",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000058"
            }
          },
          "Nega_gravar_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_gravar": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000059"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Validar_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000060"
        }
      }
    },
    "runAfter": {
      "Bloco_escopo_unidade": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000061"
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
| messages | `Enter a description.` and `Enter a quantity greater than zero.` | the rules and sentences of your domain |
| `Validar_gravar`, `Se_invalido_gravar` | names | the action suffix |

## runAfter

The root depends on `Bloco_escopo_unidade`; `Se_invalido_gravar` depends on `Validar_gravar`.

## Pitfalls

- A message **without quotes** inside `if()` made none of the flows save (`InvalidTemplate`): fixed text goes between single quotes; a literal apostrophe is doubled.
- A value inside the message uses `concat('text ', value, '.')`, never `@{}` inside an `if()` literal.
- The chain **grows** with every rule: the limit is 8,192 characters per expression and the designer rejects it with 'invalid expressions', without mentioning size. The verifier warns above 80% (F013).
- Every branch of the `if()` is evaluated: the next rule cannot depend on the previous one having passed.

## Variations

- Chain too long: split it into two `Compose` actions (`Validar_a`, `Validar_b`) and join them with `coalesce` over the non-empty messages.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/validate-with-message.json
```

Expected result: `0 error(s), 1 warning(s)`.

Intrinsic warnings of the component on its own:

- `F006` (reference to an action outside the pasted snippet): `Normalizar_gravar`. These are the block's **inputs**: they exist in the target flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

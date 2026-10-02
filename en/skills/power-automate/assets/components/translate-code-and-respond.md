# Translate a code into a message and respond (4 fields)

> **File**: `translate-code-and-respond.json` · **Frequency**: very common · **Maturity**: stable in form; map per object [unverified]
> **Depends on**: `write-via-procedure`; `deny-response-terminate` (same contract)

## Purpose

A `Compose` with the map `code -> {status, description}` and a 4-field `Response` that looks up the map by the code and falls back to `error` with 'Unexpected system response: <code>.' when the code does not exist.

## When to use / when not to use

**Use**

- Success/warning/error response of a write.

**Do not use**

- Denials before the write: `deny-response-terminate`.

## Where to paste

Inside `Caso_<acao>`, after `Bloco_gravar`. Last node of the case (no `Terminate` needed).

## Inputs and outputs

**Reads**

- `outputs('Codigo_gravar')`, `body('Gravar_pedido')`.

**Exposes**

- Response `{status, description, id, url}`.

## JSON

Destination: `Ctrl+V` at the designer's insertion point (scope clipboard envelope, `nodeId` `Bloco_responder`; the same content is in `translate-code-and-respond.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Bloco_responder",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Mensagens_gravar": {
        "type": "Compose",
        "inputs": {
          "GRAVADO": {
            "status": "success",
            "description": "Order saved."
          },
          "NAO_APLICADO": {
            "status": "warning",
            "description": "Nothing was changed."
          },
          "DUPLICADO": {
            "status": "warning",
            "description": "An order with this number already exists."
          },
          "NAO_ENCONTRADO": {
            "status": "error",
            "description": "Order not found."
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000081"
        }
      },
      "Responder_gravar": {
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
            "status": "@{coalesce(outputs('Mensagens_gravar')?[outputs('Codigo_gravar')]?['status'],'error')}",
            "description": "@{coalesce(outputs('Mensagens_gravar')?[outputs('Codigo_gravar')]?['description'],concat('Unexpected system response: ',outputs('Codigo_gravar'),'.'))}",
            "id": "@{coalesce(body('Gravar_pedido')?['ResultSets']?['Table1']?[0]?['id'],'')}",
            "url": ""
          }
        },
        "runAfter": {
          "Mensagens_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000082"
        }
      }
    },
    "runAfter": {
      "Bloco_gravar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000083"
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
| `GRAVADO`, `NAO_APLICADO`, `DUPLICADO`, `NAO_ENCONTRADO` | code vocabulary | the procedure's **closed** vocabulary; a new code needs a new row |
| sentences | English text | sentences ready for the user |
| `id` | `...?['id']` | the `id` the procedure returns (text) |

## runAfter

The root depends on `Bloco_gravar`; the `Response` depends on `Mensagens_gravar`.

## Pitfalls

- In the reference project the translation was a chain of `if(equals(...))` with 16 codes repeated in `status` and in `description`: close to the 8,192-character limit. The object map reads the code **once** (`Codigo_*`) and each code is one row. Access by dynamic key `outputs('Map')?[key]` was used in the inbound flow; in this use the format is `[unverified]`.
- The same code may need a different `status` per action; keep one map per flow, not a global one.
- A `description` with no map entry (`''`) falls back to 'Unexpected system response': better to see the code in the app than an empty message.
- Never return the connector's exception text to the user.

## Variations

- A code that changes the text with a number (changed fields): `concat(string(length(body('Trilha_gravar'))), ' field(s) changed.')` in the `description`; remember `body()` and not `outputs()`.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/translate-code-and-respond.json
```

Expected result: `0 error(s), 3 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted snippet): `Codigo_gravar`, `Gravar_pedido`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

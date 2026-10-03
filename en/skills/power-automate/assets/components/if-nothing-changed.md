# Idempotency: nothing changed, warn and finish

> **File**: `if-nothing-changed.json` · **Frequency**: common · **Maturity**: stable
> **Depends on**: `state-before`; `normalize-input`; `deny-response-terminate`

## Purpose

Compares the actual record with the normalized one and responds `warning` 'No changes to record.' with `Terminate`.

## When to use / when not to use

**Use**

- Repeatable edits and status changes.

**Do not use**

- When the history must log the attempt even without a change.

## Where to paste

Inside `Caso_<acao>`, after `Bloco_validar` (or the audit trail).

## Inputs and outputs

**Reads**

- `body('Estado_antes_gravar')`, `outputs('Normalizar_gravar')`.

**Exposes**

- A `warning` response and the end of the run, or it continues to the write.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Se_nada_mudou_gravar`; the same content is in `if-nothing-changed.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Se_nada_mudou_gravar",
  "serializedValue": {
    "type": "If",
    "expression": {
      "and": [
        {
          "equals": [
            "@and(equals(trim(string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido'])),outputs('Normalizar_gravar')?['descricao']),equals(string(coalesce(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido'],0)),string(outputs('Normalizar_gravar')?['quantidade'])))",
            "@true"
          ]
        }
      ]
    },
    "actions": {
      "Avisa_nada_mudou": {
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
            "status": "warning",
            "description": "No changes to record.",
            "id": "@{outputs('Normalizar_gravar')?['id']}",
            "url": ""
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000069"
        }
      },
      "Avisa_nada_mudou_fim": {
        "type": "Terminate",
        "inputs": {
          "runStatus": "Succeeded"
        },
        "runAfter": {
          "Avisa_nada_mudou": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000070"
        }
      }
    },
    "else": {
      "actions": {}
    },
    "runAfter": {
      "Bloco_validar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000071"
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
| `Des_Pedido`, `Qtd_Pedido` | compared columns | the editable columns of your record |
| message | `No changes to record.` | the project's wording |

## runAfter

The root depends on `Bloco_validar`. With `audit-trail`, point it to `Bloco_trilha`.

## Pitfalls

- `warning` closes the modal in the app (success is `status <> 'error'`); use `warning`, not `success`, so the user sees that nothing was saved.
- Idempotency is decided **in the flow**: the procedure may return `warning` for another reason (e.g. a newly created user is born active). Stop only on `error` after the write.
- Compare normalized text with normalized text (`trim`, case) so it does not report a change the user did not make.
- `string(coalesce(x,0))` (coalesce inside `string`) to compare a number that may come back null.

## Variations

- With the audit trail: `equals(outputs('Trilha_gravar_campos'), 0)` plus the comparison of the field the trail does not audit (e.g. note).
- Status change (grant/revoke): compare the desired state with the current one; see `support-email-with-partial`.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/if-nothing-changed.json
```

Expected result: `0 error(s), 3 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted fragment): `Estado_antes_gravar`, `Normalizar_gravar`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow the same fragment passes without this warning.

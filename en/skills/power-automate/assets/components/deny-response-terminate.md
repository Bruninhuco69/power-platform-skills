# Deny: 4-field Response + Terminate

> **File**: `deny-response-terminate.json` · **Frequency**: very common (several pairs per flow) · **Maturity**: stable
> **Depends on**: none

## Purpose

The pair `Nega_<motivo>` (`Response` to Power Apps with `status`, `description`, `id`, `url`) and `Nega_<motivo>_fim` (`Terminate` with `Succeeded`). `Response` does not end the flow: without the `Terminate` the next node runs with the response already sent.

## When to use / when not to use

**Use**

- Inside the `Yes` branch of any `If` that denies (role, validation, scope, idempotency).

**Do not use**

- The final success response of the flow: the last `Response` does not need a `Terminate` (nothing comes after it).
- HTTP inbound flow: the contract is different (`kind: Http`, real HTTP code).

## Where to paste

Inside `actions` of an `If` or a `Caso`. This envelope is only the pair; paste it into the branch and rename `motivo`.

## Inputs and outputs

**Reads**

- Message text (`description`) and, when present, `id` and `url`.

**Exposes**

- Response `{status, description, id, url}` (text) and end of the run with `Succeeded`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_nega`; the same content is in `deny-response-terminate.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Bloco_nega",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Nega_motivo": {
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
          "operationMetadataId": "00000000-0000-0000-0000-000000000019"
        }
      },
      "Nega_motivo_fim": {
        "type": "Terminate",
        "inputs": {
          "runStatus": "Succeeded"
        },
        "runAfter": {
          "Nega_motivo": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000020"
        }
      }
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000021"
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
| `Nega_motivo`, `Nega_motivo_fim` | names of the two actions | `Nega_<motivo>`: unique in the whole flow (F004) |
| `status` | `error` | `success`, `warning` or `error` |
| `description` | role sentence | a sentence ready for the user, built in the flow |
| `statusCode` | `200` | keep 200: the app reads `status`, not the HTTP code |

## runAfter

First action of the branch has no `runAfter`; the `Terminate` depends on the `Response` with `Succeeded`.

## Pitfalls

- `Response` without `Terminate` responds twice and keeps writing (F015 flags it).
- The 4 fields are always sent, even when empty; if one is missing, the screen reads `ret.url` in a flow that does not export it (F010 flags it).
- `Terminate` with `Succeeded`: the denial is a normal response. For the history to show a failure, use the `Falhar_execucao` of `run-log`.
- The denial message does not say the unit or the name of someone else's record: it would answer whoever is probing.

## Variations

- Infrastructure error: add the run id to the sentence, `concat('... Code: ', workflow()?['run']?['name'])`, so support can find the run (see `connector-catch`).

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/deny-response-terminate.json
```

Expected result: `0 error(s), 0 warning(s)`.

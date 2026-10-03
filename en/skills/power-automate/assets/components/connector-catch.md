# Catch: connector failure becomes a message

> **File**: `connector-catch.json` · **Frequency**: common · **Maturity**: stable
> **Depends on**: `read-caller-sql` (creates `Try_pedido`); `deny-response-terminate`

## Purpose

`Catch_pedido` listens for `Failed`, `TimedOut` **and** `Skipped` from `Try_pedido` and responds with an infrastructure message plus the run code, then ends.

## When to use / when not to use

**Use**

- Every flow called by the app.

**Do not use**

- Inside the `Try`: the `Catch` is its sibling.

## Where to paste

Root of the flow scope, after `Try_pedido`.

## Inputs and outputs

**Reads**

- Status of `Try_pedido`; `workflow()?['run']?['name']`.

**Exposes**

- `error` response with the run code; end.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Catch_pedido`; the same content is in `connector-catch.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Catch_pedido",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Nega_conector": {
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
            "description": "@{concat('The system did not respond. Try again in a moment. Code: ',workflow()?['run']?['name'])}",
            "id": "",
            "url": ""
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000084"
        }
      },
      "Nega_conector_fim": {
        "type": "Terminate",
        "inputs": {
          "runStatus": "Succeeded"
        },
        "runAfter": {
          "Nega_conector": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000085"
        }
      }
    },
    "runAfter": {
      "Try_pedido": [
        "Failed",
        "TimedOut",
        "Skipped"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000086"
    }
  },
  "allConnectionData": {},
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

## Parameters to change

| Item | Value in the JSON | Replace with |
|---|---|---|
| `Try_pedido` | name of the Try | `Try_<flow>` |
| message | the system did not respond | the project's message; the run code stays at the end |

## runAfter

Root depends on `Try_pedido` with `Failed`, `TimedOut`, `Skipped`.

## Pitfalls

- `CONFIG`, `Perfil_do_chamador` and `Chamador` are siblings of the `Try`: if the role connector goes down, the `Try` is `Skipped`, and a `Catch` with only `Failed` is also `Skipped`: the run ends with no `Response` and the app waits for the timeout (F009 flags it).
- The message does not promise 'nothing was changed': a failure after the write would make that promise false. Use neutral text and the run code.
- The code comes from `workflow()['run']['name']`: the user pastes it in the ticket and support finds the run. Only for infrastructure errors, not for business denials.
- `result('Try_pedido')` only returns first-level actions; for the error text use a filter on `status = 'Failed'` (see `run-log`).
- A legitimate exception to `Skipped`: an absorbing action (writing a cache that must not bring the flow down) — document it in the description.

## Variations

- Flow with a possible partial write: use `support-email-with-partial` or `dataverse-compensation` instead of promising 'nothing was done'.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/connector-catch.json
```

Expected result: `0 error(s), 0 warning(s)`.

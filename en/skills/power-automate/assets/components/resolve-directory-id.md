# Resolve the directory id when the app did not send it

> **File**: `resolve-directory-id.json` · **Frequency**: occasional · **Maturity**: designed [unverified]: generated, never returned by the designer
> **Depends on**: `validate-with-message`; Office 365 Users connector

## Purpose

If the id parameter came in empty, queries `UserProfile_V2` by e-mail; `Id_diretorio_final` holds the returned id or `(unresolved)`. A failed lookup does not break the flow: the request goes out anyway.

## When to use / when not to use

**Use**

- Access request by e-mail to support, before `support-email-with-partial`.

**Do not use**

- When the id is required: validate and deny.

## Where to paste

Inside `Try_pedido`, after `Bloco_validar`.

## Inputs and outputs

**Reads**

- `text_1` (target e-mail) and `text_2` (optional id).

**Exposes**

- `outputs('Id_diretorio_final')`: the id or `(unresolved)`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_resolver_id`; the same content is in `resolve-directory-id.json`). Fictitious GUIDs; connections: `<prefixo>_sharedoffice365users`.


```json
{
  "nodeId": "Bloco_resolver_id",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Se_id_diretorio_vazio": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(trim(coalesce(triggerBody()['text_2'],'')))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Obter_perfil_do_alvo": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "userId": "@toLower(trim(coalesce(triggerBody()['text_1'],'')))"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365users",
                "connection": "shared_office365users",
                "operationId": "UserProfile_V2"
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000098"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000099"
        }
      },
      "Id_diretorio_final": {
        "type": "Compose",
        "inputs": "@if(empty(trim(coalesce(triggerBody()['text_2'],''))),coalesce(body('Obter_perfil_do_alvo')?['id'],'(unresolved)'),trim(coalesce(triggerBody()['text_2'],'')))",
        "runAfter": {
          "Se_id_diretorio_vazio": [
            "Succeeded",
            "Failed",
            "Skipped",
            "TimedOut"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000100"
        }
      }
    },
    "runAfter": {
      "Bloco_validar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000101"
    }
  },
  "allConnectionData": {
    "Obter_perfil_do_alvo": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_office365users"
        },
        "connection": {
          "id": "<prefixo>_sharedoffice365users"
        },
        "connectionName": "<prefixo>_sharedoffice365users"
      },
      "referenceKey": "shared_office365users"
    }
  },
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

## Parameters to change

| Item | Value in the JSON | Change to |
|---|---|---|
| `text_1`, `text_2` | target e-mail and id | positions in the trigger contract |
| `(unresolved)` | marker | the text support recognizes; becomes `''` when saved |

## runAfter

The root depends on `Bloco_validar`; `Id_diretorio_final` depends on `Se_id_diretorio_vazio` in every state.

## Pitfalls

- `Id_diretorio_final` runs on `Succeeded, Failed, Skipped, TimedOut`: this is deliberate absorption. If the lookup fails, the `Try` ends `Failed` anyway; use `Terminate` before the `Catch` or accept the `Catch`.
- Reading `body('Obter_perfil_do_alvo')` when the action did not run depends on the designer returning null `[unverified]`.
- The `(unresolved)` marker must not reach the database: convert it to `''`.

## Variations

- Required id: replace the absorption with `Nega_` and `Terminate` when the lookup fails.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/resolve-directory-id.json
```

Expected result: `0 error(s), 0 warning(s)`.

# Single-row upsert (N = 1)

> **File**: `single-upsert.json` · **Frequency**: rare · **Maturity**: unique
> **Depends on**: `map-batch`; `inbound-config`; HTTP connector with Entra ID (`InvokeHttp`) and Dataverse

## Purpose

`Condicao_unitario` tests `length(body('Mapear_lote')) = 1`. In the `Yes` branch: an exact query by the key (`$top 1`, GUID only), `PATCH` by id with `If-Match: *` when it exists, `POST` when it does not. The `No` branch is left for the batch (index + `$batch`).

## When to use / when not to use

**Use**

- Inbound where many submissions carry one record.

**Do not use**

- Large batch: that is the `No` branch.

## Where to paste

Inside `Escopo_Principal`, hanging from `Resposta_sucesso`.

## Inputs and outputs

**Reads**

- `body('Mapear_lote')`, `CONFIG`.

**Exposes**

- Row created or updated; no response (the 200 was already sent).

## JSON

Destination: `Ctrl+V` at the designer's insertion point (clipboard scope envelope, `nodeId` `Condicao_unitario`; the same content is in `single-upsert.json`). Fictitious GUIDs; connections: `<prefixo>_sharedcommondataserviceforapps`, `<prefixo>_sharedwebcontents`.


```json
{
  "nodeId": "Condicao_unitario",
  "serializedValue": {
    "type": "If",
    "expression": {
      "and": [
        {
          "equals": [
            "@length(body('Mapear_lote'))",
            1
          ]
        }
      ]
    },
    "actions": {
      "Buscar_existente": {
        "type": "OpenApiConnection",
        "description": "N=1: one exact query by the business key, GUID only.",
        "inputs": {
          "parameters": {
            "entityName": "@outputs('CONFIG')?['EntitySetName']",
            "$select": "@outputs('CONFIG')?['ColunaGuid']",
            "$filter": "@concat(outputs('CONFIG')?['ColunaChave1'],' eq ',string(first(body('Mapear_lote'))?[outputs('CONFIG')?['ColunaChave1']]),' and ',outputs('CONFIG')?['ColunaChave2'],' eq ''',replace(string(first(body('Mapear_lote'))?[outputs('CONFIG')?['ColunaChave2']]),'''',''''''),'''')",
            "$top": 1
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000155"
        }
      },
      "Se_existe": {
        "type": "If",
        "expression": {
          "and": [
            {
              "greater": [
                "@length(body('Buscar_existente')?['value'])",
                0
              ]
            }
          ]
        },
        "actions": {
          "Atualizar_unitario": {
            "type": "OpenApiConnection",
            "description": "PATCH by GUID; If-Match * = update only, never creates.",
            "inputs": {
              "parameters": {
                "request/method": "PATCH",
                "request/url": "/api/data/v9.2/@{outputs('CONFIG')?['EntitySetName']}(@{first(body('Buscar_existente')?['value'])?[outputs('CONFIG')?['ColunaGuid']]})",
                "request/headers": {
                  "OData-MaxVersion": "4.0",
                  "OData-Version": "4.0",
                  "Accept": "application/json",
                  "Content-Type": "application/json",
                  "If-Match": "*"
                },
                "request/body": "@string(first(body('Mapear_lote')))"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_webcontents",
                "connection": "shared_webcontents",
                "operationId": "InvokeHttp"
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000156"
            }
          }
        },
        "else": {
          "actions": {
            "Criar_unitario": {
              "type": "OpenApiConnection",
              "inputs": {
                "parameters": {
                  "request/method": "POST",
                  "request/url": "/api/data/v9.2/@{outputs('CONFIG')?['EntitySetName']}",
                  "request/headers": {
                    "OData-MaxVersion": "4.0",
                    "OData-Version": "4.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                  },
                  "request/body": "@string(first(body('Mapear_lote')))"
                },
                "host": {
                  "apiId": "/providers/Microsoft.PowerApps/apis/shared_webcontents",
                  "connection": "shared_webcontents",
                  "operationId": "InvokeHttp"
                }
              },
              "metadata": {
                "operationMetadataId": "00000000-0000-0000-0000-000000000157"
              }
            }
          }
        },
        "runAfter": {
          "Buscar_existente": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000158"
        }
      }
    },
    "else": {
      "actions": {}
    },
    "runAfter": {
      "Bloco_mapeamento": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000159"
    }
  },
  "allConnectionData": {
    "Buscar_existente": {
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
    "Atualizar_unitario": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_webcontents"
        },
        "connection": {
          "id": "<prefixo>_sharedwebcontents"
        },
        "connectionName": "<prefixo>_sharedwebcontents"
      },
      "referenceKey": "shared_webcontents"
    },
    "Criar_unitario": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_webcontents"
        },
        "connection": {
          "id": "<prefixo>_sharedwebcontents"
        },
        "connectionName": "<prefixo>_sharedwebcontents"
      },
      "referenceKey": "shared_webcontents"
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
| `ColunaChave1`, `ColunaChave2` | composite key in `CONFIG` | adjust the `$filter` to the number of key columns and to the type (text in quotes, number without) |
| `/api/data/v9.2` | API version | the version the environment accepts |
| connection `shared_webcontents` | `<prefixo>_sharedwebcontents` | the environment's HTTP connector with Entra ID |

## runAfter

The root depends on `Mapear_lote`. When pasting inside the branch, delete the `runAfter`.

## Pitfalls

- `If-Match: *` on the `PATCH` prevents **creating** (404 if it does not exist): it only updates. `If-None-Match: *` would be the inverse.
- A key value that goes into `$filter` gets a doubled apostrophe.
- The `No` branch is where you paste `target-key-index` and `batch-upsert-changeset`; the envelope's `else` comes empty.
- The query returns 0 or 1 row; more than one means a non-unique business key: treat it as a data error.

## Variations

- With an alternate key active on the table: a direct `PATCH` on the key URL, with no prior query `[unverified: URL syntax with composite key]`.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/single-upsert.json
```

Expected result: `0 error(s), 9 warning(s)`.

Intrinsic warnings of the component on its own:

- `F006` (reference to an action outside the pasted snippet): `CONFIG`, `Mapear_lote`. These are the block's **inputs**: they exist in the target flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

# Batch upsert via $batch with changeset

> **File**: `batch-upsert-changeset.json` · **Frequency**: occasional · **Maturity**: stable in structure; CRLF, status per part and concurrency 5 [unverified]
> **Depends on**: `target-key-index`; `inbound-config`; variables `Erros_lote` and `Linhas_com_erro` at the root; HTTP connector with Entra ID

## Purpose

`Batch_update` (PATCH) and `Batch_create` (POST): `Query` splits the batch by `GuidKey`, one part template per action, `Foreach` over `chunk()` with limited concurrency, `Select` applies the template, `SendBatch` sends the `$batch`, the status of **each part** is read from the body and the rows with errors are counted.

## When to use / when not to use

**Use**

- Inbound batch.

**Do not use**

- N = 1 or a few rows: `single-upsert` (`$batch` adds complexity with no gain).
- Screen write with business rules: `flow-anatomy`.

## Where to paste

Inside `Condicao_unitario`, `No` branch, after `Bloco_indice`. Before that, **by hand, at the flow root**: two `Initialize variable` actions.

## Inputs and outputs

**Reads**

- `body('Lote_com_guid')`, `CONFIG` (`EntitySetName`, `TamanhoLote`).

**Exposes**

- Variables `Erros_lote` (text) and `Linhas_com_erro` (number) read by `run-log`.

## JSON

Destination: `Ctrl+V` at the designer's insertion point (clipboard scope envelope, `nodeId` `Escopo_batch`; the same content is in `batch-upsert-changeset.json`). Fictitious GUIDs; connections: `<prefixo>_sharedwebcontents`.


```json
{
  "nodeId": "Escopo_batch",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Ids_lote": {
        "type": "Compose",
        "description": "Once per run: the two multipart boundary identifiers.",
        "inputs": {
          "batch": "@guid()",
          "changeset": "@guid()"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000169"
        }
      },
      "Batch_update": {
        "type": "Scope",
        "actions": {
          "Filtrar_update": {
            "type": "Query",
            "inputs": {
              "from": "@body('Lote_com_guid')",
              "where": "@not(equals(item()['GuidKey'],null))"
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000170"
            }
          },
          "Modelo_update": {
            "type": "Compose",
            "inputs": "@concat('--changeset_',outputs('Ids_lote')?['changeset'],decodeUriComponent('%0D%0A'),'Content-Type: application/http',decodeUriComponent('%0D%0A'),'Content-Transfer-Encoding: binary',decodeUriComponent('%0D%0A'),'Content-ID: |ID|',decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),'PATCH /api/data/v9.2/',outputs('CONFIG')?['EntitySetName'],'(|GuidKey|) HTTP/1.1',decodeUriComponent('%0D%0A'),'OData-MaxVersion: 4.0',decodeUriComponent('%0D%0A'),'OData-Version: 4.0',decodeUriComponent('%0D%0A'),'Content-Type: application/json',decodeUriComponent('%0D%0A'),'If-Match: *',decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),'|RowData|',decodeUriComponent('%0D%0A'))",
            "runAfter": {
              "Filtrar_update": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000171"
            }
          },
          "Lotes_update": {
            "type": "Foreach",
            "foreach": "@chunk(body('Filtrar_update'),outputs('CONFIG')?['TamanhoLote'])",
            "actions": {
              "Partes_update": {
                "type": "Select",
                "inputs": {
                  "from": "@range(0,length(items('Lotes_update')))",
                  "select": "@replace(replace(replace(outputs('Modelo_update'),'|RowData|',string(removeProperty(items('Lotes_update')[item()],'GuidKey'))),'|GuidKey|',string(items('Lotes_update')[item()]['GuidKey'])),'|ID|',string(add(item(),1)))"
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000172"
                }
              },
              "Enviar_lote_update": {
                "type": "OpenApiConnection",
                "inputs": {
                  "parameters": {
                    "request/method": "POST",
                    "request/url": "/api/data/v9.2/$batch",
                    "request/headers": {
                      "OData-MaxVersion": "4.0",
                      "OData-Version": "4.0",
                      "Accept": "application/json",
                      "Content-Type": "@concat('multipart/mixed; boundary=batch_',outputs('Ids_lote')?['batch'])"
                    },
                    "request/body": "@concat('--batch_',outputs('Ids_lote')?['batch'],decodeUriComponent('%0D%0A'),'Content-Type: multipart/mixed; boundary=changeset_',outputs('Ids_lote')?['changeset'],decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),join(body('Partes_update'),decodeUriComponent('%0D%0A')),'--changeset_',outputs('Ids_lote')?['changeset'],'--',decodeUriComponent('%0D%0A'),'--batch_',outputs('Ids_lote')?['batch'],'--',decodeUriComponent('%0D%0A'))"
                  },
                  "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_webcontents",
                    "connection": "shared_webcontents",
                    "operationId": "InvokeHttp"
                  }
                },
                "runAfter": {
                  "Partes_update": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000173"
                }
              },
              "Status_partes_update": {
                "type": "Select",
                "inputs": {
                  "from": "@skip(split(base64ToString(body('Enviar_lote_update')['$content']),'HTTP/1.1 '),1)",
                  "select": "@int(substring(item(),0,3))"
                },
                "runAfter": {
                  "Enviar_lote_update": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000174"
                }
              },
              "Falhas_update": {
                "type": "Query",
                "inputs": {
                  "from": "@body('Status_partes_update')",
                  "where": "@greaterOrEquals(item(),400)"
                },
                "runAfter": {
                  "Status_partes_update": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000175"
                }
              },
              "Contar_falhas_update": {
                "type": "IncrementVariable",
                "inputs": {
                  "name": "Linhas_com_erro",
                  "value": "@if(greater(length(body('Falhas_update')),0),length(items('Lotes_update')),0)"
                },
                "runAfter": {
                  "Falhas_update": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000176"
                }
              },
              "Anexar_erro_update": {
                "type": "AppendToStringVariable",
                "inputs": {
                  "name": "Erros_lote",
                  "value": "@if(greater(length(body('Falhas_update')),0),take(base64ToString(body('Enviar_lote_update')['$content']),2000),'')"
                },
                "runAfter": {
                  "Contar_falhas_update": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000177"
                }
              }
            },
            "runtimeConfiguration": {
              "concurrency": {
                "repetitions": 5
              }
            },
            "runAfter": {
              "Modelo_update": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000178"
            }
          }
        },
        "runAfter": {
          "Ids_lote": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000179"
        }
      },
      "Batch_create": {
        "type": "Scope",
        "actions": {
          "Filtrar_create": {
            "type": "Query",
            "inputs": {
              "from": "@body('Lote_com_guid')",
              "where": "@equals(item()['GuidKey'],null)"
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000180"
            }
          },
          "Modelo_create": {
            "type": "Compose",
            "inputs": "@concat('--changeset_',outputs('Ids_lote')?['changeset'],decodeUriComponent('%0D%0A'),'Content-Type: application/http',decodeUriComponent('%0D%0A'),'Content-Transfer-Encoding: binary',decodeUriComponent('%0D%0A'),'Content-ID: |ID|',decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),'POST /api/data/v9.2/',outputs('CONFIG')?['EntitySetName'],' HTTP/1.1',decodeUriComponent('%0D%0A'),'OData-MaxVersion: 4.0',decodeUriComponent('%0D%0A'),'OData-Version: 4.0',decodeUriComponent('%0D%0A'),'Content-Type: application/json;type=entry',decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),'|RowData|',decodeUriComponent('%0D%0A'))",
            "runAfter": {
              "Filtrar_create": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000181"
            }
          },
          "Lotes_create": {
            "type": "Foreach",
            "foreach": "@chunk(body('Filtrar_create'),outputs('CONFIG')?['TamanhoLote'])",
            "actions": {
              "Partes_create": {
                "type": "Select",
                "inputs": {
                  "from": "@range(0,length(items('Lotes_create')))",
                  "select": "@replace(replace(outputs('Modelo_create'),'|RowData|',string(removeProperty(items('Lotes_create')[item()],'GuidKey'))),'|ID|',string(add(item(),1)))"
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000182"
                }
              },
              "Enviar_lote_create": {
                "type": "OpenApiConnection",
                "inputs": {
                  "parameters": {
                    "request/method": "POST",
                    "request/url": "/api/data/v9.2/$batch",
                    "request/headers": {
                      "OData-MaxVersion": "4.0",
                      "OData-Version": "4.0",
                      "Accept": "application/json",
                      "Content-Type": "@concat('multipart/mixed; boundary=batch_',outputs('Ids_lote')?['batch'])"
                    },
                    "request/body": "@concat('--batch_',outputs('Ids_lote')?['batch'],decodeUriComponent('%0D%0A'),'Content-Type: multipart/mixed; boundary=changeset_',outputs('Ids_lote')?['changeset'],decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),join(body('Partes_create'),decodeUriComponent('%0D%0A')),'--changeset_',outputs('Ids_lote')?['changeset'],'--',decodeUriComponent('%0D%0A'),'--batch_',outputs('Ids_lote')?['batch'],'--',decodeUriComponent('%0D%0A'))"
                  },
                  "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_webcontents",
                    "connection": "shared_webcontents",
                    "operationId": "InvokeHttp"
                  }
                },
                "runAfter": {
                  "Partes_create": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000183"
                }
              },
              "Status_partes_create": {
                "type": "Select",
                "inputs": {
                  "from": "@skip(split(base64ToString(body('Enviar_lote_create')['$content']),'HTTP/1.1 '),1)",
                  "select": "@int(substring(item(),0,3))"
                },
                "runAfter": {
                  "Enviar_lote_create": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000184"
                }
              },
              "Falhas_create": {
                "type": "Query",
                "inputs": {
                  "from": "@body('Status_partes_create')",
                  "where": "@greaterOrEquals(item(),400)"
                },
                "runAfter": {
                  "Status_partes_create": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000185"
                }
              },
              "Contar_falhas_create": {
                "type": "IncrementVariable",
                "inputs": {
                  "name": "Linhas_com_erro",
                  "value": "@if(greater(length(body('Falhas_create')),0),length(items('Lotes_create')),0)"
                },
                "runAfter": {
                  "Falhas_create": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000186"
                }
              },
              "Anexar_erro_create": {
                "type": "AppendToStringVariable",
                "inputs": {
                  "name": "Erros_lote",
                  "value": "@if(greater(length(body('Falhas_create')),0),take(base64ToString(body('Enviar_lote_create')['$content']),2000),'')"
                },
                "runAfter": {
                  "Contar_falhas_create": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000187"
                }
              }
            },
            "runtimeConfiguration": {
              "concurrency": {
                "repetitions": 5
              }
            },
            "runAfter": {
              "Modelo_create": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000188"
            }
          }
        },
        "runAfter": {
          "Batch_update": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000189"
        }
      }
    },
    "runAfter": {
      "Bloco_indice": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000190"
    }
  },
  "allConnectionData": {
    "Enviar_lote_update": {
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
    "Enviar_lote_create": {
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
| `Inicializar_erros_lote` | `Initialize variable` `Erros_lote`, text type, empty value | create it at the root; the variable name is referenced in the actions |
| `Inicializar_linhas_com_erro` | `Initialize variable` `Linhas_com_erro`, integer type, 0 | create it at the root |
| `repetitions` | `5` | `Foreach` concurrency; start low and raise it until a 429 appears |
| `/api/data/v9.2` | version | the environment's |
| `TamanhoLote` | `CONFIG` | up to 1000 requests per `$batch` |

## runAfter

The root depends on `Bloco_indice`; `Batch_create` depends on `Batch_update`; inside the `Foreach`, the actions chain in order.

## Pitfalls

- `$batch` body with **CRLF**: the reference project used `\n` (LF) and Learn requires CRLF `[unverified: run with LF or CRLF]`. Test with a 2-row batch before raising the volume.
- Each part carries `Content-Type: application/http` and `Content-Transfer-Encoding: binary`; the `$batch` header does not apply to each part.
- A changeset is atomic: one failure rolls back the rows of the whole part. Independent rows call for `Prefer: odata.continue-on-error` and parts without a changeset.
- The reference project detected errors by substring (`'400 Bad Request'`...) and left 429, 500, 503 and 504 out. Here the status of each part is read (`HTTP/1.1 NNN`) and `>= 400` counts `[unverified: split on a real response]`: validate with a batch that has one deliberately invalid row.
- Count rows, not parts: the count increments by the chunk size only when there is a failure.
- 429: excess requests return `Retry-After`; limit the concurrency and start with 10 requests. The retry policy of the `InvokeHttp` connector `[unverified]` in the designer's JSON.
- A `Foreach` with concurrency cannot use `Set variable`; `Increment` and `Append` are the ones used here.
- The response body comes in `$content` as base64 (`base64ToString`).

## Variations

- Independent rows: add `Prefer: odata.continue-on-error` and remove the changeset.
- Update only or create only: delete the other scope and the dependency.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/batch-upsert-changeset.json
```

Expected result: `0 error(s), 6 warning(s)`.

Intrinsic warnings of the component on its own:

- `F006` (reference to an action outside the pasted snippet): `CONFIG`, `Lote_com_guid`. These are the block's **inputs**: they exist in the target flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

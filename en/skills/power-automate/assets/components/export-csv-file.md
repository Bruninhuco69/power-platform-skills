# Export CSV to file storage and return the link

> **File**: `export-csv-file.json` · **Frequency**: occasional · **Maturity**: designed [unverified]: generated, never returned by the designer
> **Depends on**: `config` (`pastaSaida`); a prior read `Ler_dados_exportacao`; Microsoft cloud file connector (connector id in the JSON)

## Purpose

Warns when there are no rows, builds each CSV line with `,` (separator, escape of `,` and line breaks), writes the file with a UTF-8 BOM, creates the sharing link, and replies `success` with a download `url`.

## When to use / when not to use

**Use**

- Exporting the result of a procedure or query.

**Do not use**

- A very large file: the file connector and the app have limits; filter or paginate.

## Where to paste

Inside the `Caso_csv` of `Switch_formato` (or of `Try_pedido`), after the data read.

## Inputs and outputs

**Reads**

- `body('Ler_dados_exportacao')?['ResultSets']?['Table1']` (list of objects), `CONFIG.pastaSaida`.

**Exposes**

- `body('Linhas_csv')` (list of lines), file in the output folder, response with `url`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_exportar_csv`; the same content is in `export-csv-file.json`). Fictitious GUIDs; connections: `<prefixo>_sharedonedriveforbusiness`.


```json
{
  "nodeId": "Bloco_exportar_csv",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Se_exportacao_vazia": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(coalesce(body('Ler_dados_exportacao')?['ResultSets']?['Table1'],json('[]')))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Avisa_exportacao_vazia": {
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
                "description": "No records match the filters. Nothing was generated.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000123"
            }
          },
          "Avisa_exportacao_vazia_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Avisa_exportacao_vazia": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000124"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000125"
        }
      },
      "Linhas_csv": {
        "type": "Select",
        "inputs": {
          "from": "@coalesce(body('Ler_dados_exportacao')?['ResultSets']?['Table1'],json('[]'))",
          "select": "@concat(replace(replace(replace(coalesce(string(item()?['Pedido']),''),',',';'),decodeUriComponent('%0D'),' '),decodeUriComponent('%0A'),' '),',',replace(replace(replace(coalesce(string(item()?['Descricao']),''),',',';'),decodeUriComponent('%0D'),' '),decodeUriComponent('%0A'),' '),',',replace(replace(replace(coalesce(string(item()?['Unidade']),''),',',';'),decodeUriComponent('%0D'),' '),decodeUriComponent('%0A'),' '))"
        },
        "runAfter": {
          "Se_exportacao_vazia": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000126"
        }
      },
      "Gravar_csv": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "folderPath": "@outputs('CONFIG')?['pastaSaida']",
            "name": "Orders_@{formatDateTime(utcNow(),'yyyyMMdd-HHmm')}.csv",
            "body": "@concat(decodeUriComponent('%EF%BB%BF'),'Order,Description,Unit',decodeUriComponent('%0D%0A'),join(body('Linhas_csv'),decodeUriComponent('%0D%0A')))"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness",
            "connection": "shared_onedriveforbusiness",
            "operationId": "CreateFile"
          }
        },
        "runAfter": {
          "Linhas_csv": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000127"
        }
      },
      "Link_csv": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "id": "@coalesce(body('Gravar_csv')?['Id'],'')",
            "type": "View",
            "scope": "Organization"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness",
            "connection": "shared_onedriveforbusiness",
            "operationId": "CreateShareLinkV2"
          }
        },
        "runAfter": {
          "Gravar_csv": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000128"
        }
      },
      "Responder_csv": {
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
            "status": "success",
            "description": "@{concat(string(length(body('Linhas_csv'))),' record(s) exported.')}",
            "id": "",
            "url": "@{if(empty(coalesce(body('Link_csv')?['WebUrl'],'')),'',concat(body('Link_csv')?['WebUrl'],if(contains(body('Link_csv')?['WebUrl'],'?'),'&','?'),'download=1'))}"
          }
        },
        "runAfter": {
          "Link_csv": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000129"
        }
      }
    },
    "runAfter": {
      "Bloco_filtros": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000130"
    }
  },
  "allConnectionData": {
    "Gravar_csv": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness"
        },
        "connection": {
          "id": "<prefixo>_sharedonedriveforbusiness"
        },
        "connectionName": "<prefixo>_sharedonedriveforbusiness"
      },
      "referenceKey": "shared_onedriveforbusiness"
    },
    "Link_csv": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness"
        },
        "connection": {
          "id": "<prefixo>_sharedonedriveforbusiness"
        },
        "connectionName": "<prefixo>_sharedonedriveforbusiness"
      },
      "referenceKey": "shared_onedriveforbusiness"
    }
  },
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

## Parameters to change

| Item | Value in the JSON | Replace with |
|---|---|---|
| `Ler_dados_exportacao` | prior read action | the procedure/query that produces the rows |
| `Pedido`, `Descricao`, `Unidade` | columns (the header line is `Order,Description,Unit`) | export columns, in header order |
| `pastaSaida` | `CONFIG` | output folder of the file connector |
| `scope: Organization` | link reach | the narrowest that works |

## runAfter

The root depends on `Bloco_filtros`; the actions chain in order.

## Pitfalls

- `Select` returns an envelope in `outputs()`: use `body('Linhas_csv')` in the `join` (F011).
- BOM `decodeUriComponent('%EF%BB%BF')` at the start so Excel opens accents correctly; CRLF line break.
- Escape `,`, CR and LF inside the data (here `,` becomes `;`); a field that starts with `=`, `+`, `-` or `@` becomes a formula in Excel: prefix it with an apostrophe if the data comes from a user `[unverified]`.
- The link returns `WebUrl`; append `download=1` (or `&download=1`) to download instead of opening.
- The export runs with the connector's connection, not the user's: unit scope must have filtered beforehand.

## Variations

- Count before exporting (procedure `contar`) to warn about an empty result without reading everything.
- Dataverse: `ListRecords` with native pagination (`native-pagination`) feeds the same `Select`.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/export-csv-file.json
```

Expected result: `0 error(s), 3 warning(s)`.

Warnings intrinsic to the component on its own:

- `F006` (reference to an action outside the pasted snippet): `CONFIG`, `Ler_dados_exportacao`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

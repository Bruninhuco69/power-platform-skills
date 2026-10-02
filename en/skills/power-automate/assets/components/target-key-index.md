# {key -> GUID} index of the target table

> **File**: `target-key-index.json` · **Frequency**: occasional · **Maturity**: stable
> **Depends on**: `map-batch`; `inbound-config`; `native-pagination` (the read already brings pagination)

## Purpose

Computes limits (`first(sort())`/`last(sort())`), builds the filter, reads **only the batch range** from the target table with native pagination, builds the `{key: row}` object and adds `GuidKey` to each batch row.

## When to use / when not to use

**Use**

- Batch with more than one row and a target table without an alternate key.

**Do not use**

- N = 1: `single-upsert`.
- Table with an alternate key: direct `PATCH`.

## Where to paste

Inside `Condicao_unitario`, in the `No` branch, before `batch-upsert-changeset`.

## Inputs and outputs

**Reads**

- `body('Mapear_lote')`, `CONFIG`.

**Exposes**

- `body('Lote_com_guid')`: the batch with `GuidKey` (null = create).

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_indice`; the same content is in `target-key-index.json`). Fictitious GUIDs; connections: `<prefixo>_sharedcommondataserviceforapps`.

```json
{
  "nodeId": "Bloco_indice",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Limites": {
        "type": "Compose",
        "description": "Replaces one minimum Compose and one maximum Compose per key.",
        "inputs": {
          "MinChave1": "@first(sort(body('Mapear_lote'),outputs('CONFIG')?['ColunaChave1']))?[outputs('CONFIG')?['ColunaChave1']]",
          "MaxChave1": "@last(sort(body('Mapear_lote'),outputs('CONFIG')?['ColunaChave1']))?[outputs('CONFIG')?['ColunaChave1']]",
          "MinChave2": "@first(sort(body('Mapear_lote'),outputs('CONFIG')?['ColunaChave2']))?[outputs('CONFIG')?['ColunaChave2']]",
          "MaxChave2": "@last(sort(body('Mapear_lote'),outputs('CONFIG')?['ColunaChave2']))?[outputs('CONFIG')?['ColunaChave2']]"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000160"
        }
      },
      "Clausulas_chave1": {
        "type": "Select",
        "inputs": {
          "from": "@body('Mapear_lote')",
          "select": "@concat(outputs('CONFIG')?['ColunaChave1'],' eq ',string(item()?[outputs('CONFIG')?['ColunaChave1']]))"
        },
        "runAfter": {
          "Limites": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000161"
        }
      },
      "Filtro_chave1": {
        "type": "Compose",
        "description": "Up to 10 keys: exact list (no duplicates). Above that: minimum-maximum range.",
        "inputs": "@if(greater(length(body('Mapear_lote')),10),concat(outputs('CONFIG')?['ColunaChave1'],' ge ',outputs('Limites')?['MinChave1'],' and ',outputs('CONFIG')?['ColunaChave1'],' le ',outputs('Limites')?['MaxChave1']),concat('(',join(union(body('Clausulas_chave1'),body('Clausulas_chave1')),' or '),')'))",
        "runAfter": {
          "Clausulas_chave1": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000162"
        }
      },
      "Ler_destino": {
        "type": "OpenApiConnection",
        "description": "Native pagination (Settings > Pagination) brings all pages in a single action.",
        "inputs": {
          "parameters": {
            "entityName": "@outputs('CONFIG')?['EntitySetName']",
            "$select": "@concat(outputs('CONFIG')?['ColunaGuid'],',',outputs('CONFIG')?['ColunaChave1'],',',outputs('CONFIG')?['ColunaChave2'])",
            "$filter": "@concat('(',outputs('Filtro_chave1'),') and ',outputs('CONFIG')?['ColunaChave2'],' ge ''',outputs('Limites')?['MinChave2'],''' and ',outputs('CONFIG')?['ColunaChave2'],' le ''',outputs('Limites')?['MaxChave2'],'''')"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "runtimeConfiguration": {
          "paginationPolicy": {
            "minimumItemCount": 100000
          }
        },
        "runAfter": {
          "Filtro_chave1": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000163"
        }
      },
      "Chaves_destino": {
        "type": "Select",
        "inputs": {
          "from": "@body('Ler_destino')?['value']",
          "select": {
            "@{outputs('CONFIG')?['ColunaGuid']}": "@item()?[outputs('CONFIG')?['ColunaGuid']]",
            "@{outputs('CONFIG')?['ColunaChave1']}": "@item()?[outputs('CONFIG')?['ColunaChave1']]",
            "@{outputs('CONFIG')?['ColunaChave2']}": "@item()?[outputs('CONFIG')?['ColunaChave2']]"
          }
        },
        "runAfter": {
          "Ler_destino": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000164"
        }
      },
      "Indice_chaves": {
        "type": "Select",
        "inputs": {
          "from": "@body('Chaves_destino')",
          "select": {
            "@{concat(string(item()?[outputs('CONFIG')?['ColunaChave1']]),string(item()?[outputs('CONFIG')?['ColunaChave2']]))}": "@item()"
          }
        },
        "runAfter": {
          "Chaves_destino": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000165"
        }
      },
      "Indice_objeto": {
        "type": "Compose",
        "description": "Single {key: row} object. Guarded for an empty index (json('') throws).",
        "inputs": "@json(if(empty(body('Indice_chaves')),'{}',replace(replace(replace(string(body('Indice_chaves')),'[',''),']',''),'},{',',')))",
        "runAfter": {
          "Indice_chaves": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000166"
        }
      },
      "Lote_com_guid": {
        "type": "Select",
        "description": "Adds GuidKey to each row from the index. The Z suffix makes the date format match on both sides.",
        "inputs": {
          "from": "@body('Mapear_lote')",
          "select": "@addProperty(item(),'GuidKey',outputs('Indice_objeto')?[concat(string(item()?[outputs('CONFIG')?['ColunaChave1']]),string(item()?[outputs('CONFIG')?['ColunaChave2']]),'Z')]?[outputs('CONFIG')?['ColunaGuid']])"
        },
        "runAfter": {
          "Indice_objeto": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000167"
        }
      }
    },
    "runAfter": {
      "Mapear_lote": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000168"
    }
  },
  "allConnectionData": {
    "Ler_destino": {
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
| `ColunaChave1`, `ColunaChave2` | composite key from `CONFIG` | extend the `Select` actions if there are more key columns |
| `10` | exact-list limit | above it, the minimum-maximum range is used |
| `100000` | pagination limit | maximum expected size of the read |
| quotes around `ColunaChave2` | column as text | remove the quotes if the column is Date/DateTime `[unverified]` |

## runAfter

The root depends on `Mapear_lote`; the `Select` and `Compose` actions chain.

## Pitfalls

- Index by the **concatenated** key in the same format on both sides; the batch's `Z` suffix makes the date format match the one Dataverse returns. Without it no row finds its id and everything becomes a duplicate `create`.
- `replace` of `[`, `]` and `},{` to merge the objects into one breaks if any data contains a bracket: validate or escape first `[unverified]`.
- Empty index: `json('')` throws; the `Compose` returns `{}` if `empty(body(...))`.
- Reducing the read is the gain: filter by the batch range instead of reading the whole table.
- Pagination by `Do_until` + skiptoken (the project's old version) means more actions and more failures; the native one brings everything in a single action.

## Variations

- Single-column key: `Select` and `concat` with a single term.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/target-key-index.json
```

Expected result: `0 error(s), 20 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted snippet): `CONFIG`, `Mapear_lote`. These are the block's **inputs**: they exist in the target flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

# Native paginated read (List rows)

> **File**: `native-pagination.json` · **Frequency**: occasional (native in most; `Do_until` only in old flows) · **Maturity**: stable
> **Depends on**: `config`; Dataverse connector

## Purpose

`ListRecords` with `runtimeConfiguration.paginationPolicy.minimumItemCount` (Settings > Pagination) brings all pages in one action, up to the limit.

## When to use / when not to use

**Use**

- Large read for an index, report or export.

**Do not use**

- Reads that fit in one page (`$top`).

## Where to paste

In any scope, at the read point.

## Inputs and outputs

**Reads**

- `$select`, `$filter`, `$orderby`.

**Exposes**

- `body('Ler_todos_pedidos')?['value']`: all the rows, and `outputs('Total_lidos')`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_paginacao`; the same content is in `native-pagination.json`). Fictitious GUIDs; connections: `<prefixo>_sharedcommondataserviceforapps`.


```json
{
  "nodeId": "Bloco_paginacao",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Ler_todos_pedidos": {
        "type": "OpenApiConnection",
        "description": "Settings > Pagination: brings all pages in one action, up to the limit.",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_pedidos",
            "$select": "<prefixo>_pedidoid,<prefixo>_numero",
            "$filter": "<prefixo>_ativo eq true",
            "$orderby": "<prefixo>_numero"
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
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000191"
        }
      },
      "Total_lidos": {
        "type": "Compose",
        "inputs": "@length(coalesce(body('Ler_todos_pedidos')?['value'],json('[]')))",
        "runAfter": {
          "Ler_todos_pedidos": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000192"
        }
      }
    },
    "runAfter": {
      "Bloco_config": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000193"
    }
  },
  "allConnectionData": {
    "Ler_todos_pedidos": {
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

| Item | Value in the JSON | Change to |
|---|---|---|
| `<prefixo>_pedidos` | entity set | AS-BUILT |
| `100000` | item limit | the expected ceiling; pagination stops when it is reached |
| `$select`, `$filter` | columns and filter | only the columns needed; filter by the range |

## runAfter

The root depends on `Bloco_config`.

## Pitfalls

- Always use `$select`: without it the read brings all columns and blows up time and memory.
- Narrow the read by the batch key range, instead of reading the whole table.
- The limit belongs to the connector, not Dataverse: above it the read is cut **without an error**; compare `Total_lidos` with the expected count.
- Old alternative: `Do_until` + `@odata.nextLink`/skiptoken in a variable: more actions, more points of failure.

## Variations

- `Do_until` with skiptoken: only when native pagination does not fit (`[unverified]` in this catalog, no block).

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/native-pagination.json
```

Expected result: `0 error(s), 0 warning(s)`.

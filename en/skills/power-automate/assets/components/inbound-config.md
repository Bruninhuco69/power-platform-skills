# Batch inbound CONFIG

> **File**: `inbound-config.json` · **Frequency**: occasional (inbound flows only); the role of `config` is very common · **Maturity**: stable
> **Depends on**: none

## Purpose

The same role as `config`, with the batch keys. The name stays `CONFIG`; no other action carries an environment literal.

## When to use / when not to use

**Use**

- HTTP flow that writes to Dataverse.

**Do not use**

- Flow called by the app: use `config`.

## Where to paste

Inside `Escopo_Principal`, before the mapping (or at the root, before the scope).

## Inputs and outputs

**Reads**

- Nothing.

**Exposes**

- `EntitySetName`, `TamanhoLote`, `ColunaGuid`, `ColunaChave1`, `ColunaChave2`, `origemToken`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_config`; the same content is in `inbound-config.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Bloco_config",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "CONFIG": {
        "type": "Compose",
        "inputs": {
          "EntitySetName": "<prefixo>_pedidos",
          "TamanhoLote": 50,
          "ColunaGuid": "<prefixo>_pedidoid",
          "ColunaChave1": "<prefixo>_numero",
          "ColunaChave2": "<prefixo>_dataevento",
          "origemToken": "<origem-do-token>"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000003"
        }
      }
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000004"
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
| `EntitySetName` | `<prefixo>_pedidos` | **entity set name** (plural), not the logical name; via environment variable, not a test literal |
| `TamanhoLote` | `50` | start small (for example 10) and raise it until 429 appears; maximum 1000 |
| `ColunaGuid` | `<prefixo>_pedidoid` | primary key |
| `ColunaChave1`, `ColunaChave2` | business key | numeric and date/text; extendable |
| `origemToken` | `<origem-do-token>` | value of the `name` column of the cache row |

## runAfter

Root depends on nothing (first action of the scope).

## Pitfalls

- `TableLogicalName` in the reference project was the entity set name and contained a literal `dev`: promoting to production meant editing the flow. Use an environment variable (F5).
- An environment variable read in `parameters()` is frozen until the flow is saved or reconnected: fine for a table, not for a token cache.
- More key columns: add `ColunaChave3`... and extend the index (`target-key-index`).

## Variations

- Upsert by alternate key: the key columns become the `PATCH` URL and the index goes away (see the `dataverse-batch-upsert` reference).

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/inbound-config.json
```

Expected result: `0 error(s), 0 warning(s)`.

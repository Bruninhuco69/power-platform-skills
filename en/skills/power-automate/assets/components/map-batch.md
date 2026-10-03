# Map the received batch (mapping Select)

> **File**: `map-batch.json` · **Frequency**: occasional · **Maturity**: stable
> **Depends on**: `inbound-config`; body `{ dados: [...] }`

## Purpose

A `Select` with the logical name on the left and the value on the right converts each batch item: null-date sentinel, boolean to integer, number to text-or-null and protected numeric text.

## When to use / when not to use

**Use**

- Receiving a batch from an external system.

**Do not use**

- Two mappings of the same batch (one for update, one for create): there is a single copy.

## Where to paste

Inside `Escopo_Principal`; without the token's `runAfter` (runs in parallel with `Scope_Token`) or after `CONFIG`.

## Inputs and outputs

**Reads**

- `triggerBody()?['dados']`: list of records from the source system.

**Exposes**

- `body('Mapear_lote')`: list of objects ready for Dataverse.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_mapeamento`; the same content is in `map-batch.json`). Fictitious GUIDs; connections: none.

```json
{
  "nodeId": "Bloco_mapeamento",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Mapear_lote": {
        "type": "Select",
        "description": "Single copy of the mapping: logical name on the left, value on the right.",
        "inputs": {
          "from": "@coalesce(triggerBody()?['dados'],json('[]'))",
          "select": {
            "<prefixo>_numero": "@item()?['Num_Pedido']",
            "<prefixo>_descricao": "@item()?['Des_Pedido']",
            "<prefixo>_dataevento": "@if(equals(item()?['Dat_Evento'],'0001-01-01T00:00:00'),'1753-01-01T00:00:00Z',item()?['Dat_Evento'])",
            "<prefixo>_prazo": "@if(equals(item()?['Dat_Prazo'],'0001-01-01T00:00:00'),'1753-01-01T00:00:00Z',item()?['Dat_Prazo'])",
            "<prefixo>_ativo": "@if(equals(item()?['Flg_Ativo'],true),1,0)",
            "<prefixo>_codigo": "@if(equals(item()?['Cod_Item'],null),null,string(item()?['Cod_Item']))",
            "<prefixo>_rota": "@if(empty(trim(coalesce(item()?['Cod_Rota'],''))),0,int(trim(coalesce(item()?['Cod_Rota'],''))))"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000153"
        }
      }
    },
    "runAfter": {
      "Bloco_config": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000154"
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
| `Num_Pedido`, `Des_Pedido`... | source fields | names of the fields in the caller's contract |
| `<prefixo>_numero`... | target columns | AS-BUILT logical names |
| `0001-01-01T00:00:00` | source null date | the source system's real sentinel |
| `1753-01-01T00:00:00Z` | target minimum date | value accepted by the column |

## runAfter

The root depends on `Bloco_config`.

## Pitfalls

- `if()` evaluates both branches: `trim(null)` throws even when that branch is not chosen; use `trim(coalesce(x,''))`.
- Number that the target stores as text: `if(equals(x,null),null,string(x))` keeps null (`string(null)` would be `''`).
- The name in the flow and in OData is the logical one, not the Power Fx display name.
- The date must come out in the **same format** on both sides of the index (`target-key-index`), otherwise everything becomes a duplicate `create`.
- Batches of 1 and of N use the same mapping: the single-item branch reads `first(body('Mapear_lote'))`.

## Variations

- List coming from a spreadsheet: filter out empty rows before the `Select`.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/map-batch.json
```

Expected result: `0 error(s), 0 warning(s)`.

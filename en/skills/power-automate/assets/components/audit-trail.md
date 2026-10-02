# Field-by-field audit trail

> **File**: `audit-trail.json` · **Frequency**: occasional · **Maturity**: unique: only one flow's template was returned by the designer
> **Depends on**: `state-before`; `normalize-input`

## Purpose

One `Compose` per field compares the previous and new value and sets `incluir`. `Query` keeps the changed ones, `Select` projects the history columns and `Trilha_gravar_campos` counts them. The result goes to the procedure.

## When to use / when not to use

**Use**

- Edit with per-field history.

**Do not use**

- Create (there is no previous value).

## Where to paste

Inside `Caso_<acao>`, after validation and before `if-nothing-changed` and `write-via-procedure`.

## Inputs and outputs

**Reads**

- `body('Estado_antes_gravar')`, `outputs('Normalizar_gravar')`.

**Exposes**

- `body('Trilha_gravar')` (list for the procedure: `@string(body('Trilha_gravar'))`) and `outputs('Trilha_gravar_campos')` (number).

## JSON

Destination: `Ctrl+V` at the designer's insertion point (scope clipboard envelope, `nodeId` `Bloco_trilha`; the same content is in `audit-trail.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Bloco_trilha",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Linha_gravar_01": {
        "type": "Compose",
        "inputs": {
          "ordem": "1",
          "tp_evento": "EDICAO",
          "campo": "Des_Pedido",
          "valor_anterior": "@take(if(empty(string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido'])),'(empty)',string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido'])),200)",
          "valor_novo": "@take(if(empty(string(outputs('Normalizar_gravar')?['descricao'])),'(empty)',string(outputs('Normalizar_gravar')?['descricao'])),200)",
          "resumo": "@take(concat('Des_Pedido changed from ''',take(if(empty(string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido'])),'(empty)',string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido'])),200),''' to ''',take(if(empty(string(outputs('Normalizar_gravar')?['descricao'])),'(empty)',string(outputs('Normalizar_gravar')?['descricao'])),200),''''),400)",
          "incluir": "@if(equals(string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido']),string(outputs('Normalizar_gravar')?['descricao'])),'0','1')"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000062"
        }
      },
      "Linha_gravar_02": {
        "type": "Compose",
        "inputs": {
          "ordem": "2",
          "tp_evento": "EDICAO",
          "campo": "Qtd_Pedido",
          "valor_anterior": "@take(if(empty(string(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido'])),'(empty)',string(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido'])),200)",
          "valor_novo": "@take(if(empty(string(outputs('Normalizar_gravar')?['quantidade'])),'(empty)',string(outputs('Normalizar_gravar')?['quantidade'])),200)",
          "resumo": "@take(concat('Qtd_Pedido changed from ''',take(if(empty(string(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido'])),'(empty)',string(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido'])),200),''' to ''',take(if(empty(string(outputs('Normalizar_gravar')?['quantidade'])),'(empty)',string(outputs('Normalizar_gravar')?['quantidade'])),200),''''),400)",
          "incluir": "@if(equals(string(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido']),string(outputs('Normalizar_gravar')?['quantidade'])),'0','1')"
        },
        "runAfter": {
          "Linha_gravar_01": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000063"
        }
      },
      "Trilha_gravar_todas": {
        "type": "Compose",
        "inputs": "@createArray(outputs('Linha_gravar_01'),outputs('Linha_gravar_02'))",
        "runAfter": {
          "Linha_gravar_02": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000064"
        }
      },
      "Trilha_gravar_ativas": {
        "type": "Query",
        "inputs": {
          "from": "@outputs('Trilha_gravar_todas')",
          "where": "@equals(item()?['incluir'],'1')"
        },
        "runAfter": {
          "Trilha_gravar_todas": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000065"
        }
      },
      "Trilha_gravar": {
        "type": "Select",
        "inputs": {
          "from": "@body('Trilha_gravar_ativas')",
          "select": {
            "ordem": "@item()?['ordem']",
            "tp_evento": "@item()?['tp_evento']",
            "campo": "@item()?['campo']",
            "valor_anterior": "@item()?['valor_anterior']",
            "valor_novo": "@item()?['valor_novo']",
            "resumo": "@item()?['resumo']"
          }
        },
        "runAfter": {
          "Trilha_gravar_ativas": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000066"
        }
      },
      "Trilha_gravar_campos": {
        "type": "Compose",
        "inputs": "@length(body('Trilha_gravar_ativas'))",
        "runAfter": {
          "Trilha_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000067"
        }
      }
    },
    "runAfter": {
      "Bloco_validar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000068"
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
| `Linha_gravar_01`, `_02` | two sample fields | one `Compose` per audited field: duplicate and change the field, column and new value |
| `Trilha_gravar_todas` | `createArray` with the two rows | include all the rows |
| `take(..., 200)` and `400` | value and summary sizes | the size of the history columns |
| `tp_evento` | `EDICAO` | the project's event vocabulary (Choice integer: read it from the environment, do not assume) |

## runAfter

The root depends on `Bloco_validar`; the `Linha_*` actions chain to each other; the rest chains in order.

## Pitfalls

- `outputs('Trilha')` of a `Select` returns the envelope: `outputs('Trilha')?['campos']` gives `null`, `string(null)` gives `''` and the response comes out as ' field(s) changed.' with no number and no error. Use `body()` and `length()` (F011).
- An empty value becomes `(empty)` on both sides so the comparison does not depend on null vs text.
- Choice values as an integer never read from the environment save without error with the label swapped.
- Each row repeats the value expression: the 8,192-character limit is per expression; keep one action per field.

## Variations

- Dataverse: instead of `Select` + procedure, one history `CreateRecord` per field inside a change `If` (the form used in the Dataverse trail: more actions, more points of failure).

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/audit-trail.json
```

Expected result: `0 error(s), 12 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted snippet): `Estado_antes_gravar`, `Normalizar_gravar`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

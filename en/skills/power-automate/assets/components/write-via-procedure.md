# Write through a procedure and read the one-row return

> **File**: `write-via-procedure.json` · **Frequency**: common · **Maturity**: stable
> **Depends on**: `normalize-input`; SQL connector; `<procedure_gravar_pedido>`

## Purpose

`Execute stored procedure (V2)` with typed parameters and a `Compose` `Codigo_gravar` that reads the `description` (ASCII code) of the single row returned. Translating the code into a sentence is the job of `translate-code-and-respond`.

## When to use / when not to use

**Use**

- A write with a rule, transaction or trigger on the server.

**Do not use**

- `Insert row`/`Update row` on a table with a server-side trigger: it does not work.
- Dataverse writes: `CreateRecord`/`UpdateRecord` actions.

## Where to paste

Inside `Caso_<acao>`, after `Se_nada_mudou_gravar` (or after the last block).

## Inputs and outputs

**Reads**

- `outputs('Normalizar_gravar')`, the caller's `Id_Usuario`.

**Exposes**

- `body('Gravar_pedido')?['ResultSets']?['Table1']?[0]` (1 row: `status`, `description` = code, `id`, `url`) and `outputs('Codigo_gravar')`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_gravar`; the same content is in `write-via-procedure.json`). Fictitious GUIDs; connections: `<prefixo>_sharedsql`.

```json
{
  "nodeId": "Bloco_gravar",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Gravar_pedido": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "server": "default",
            "database": "default",
            "procedure": "[dbo].[<procedure_gravar_pedido>]",
            "parameters/Id_Pedido": "@outputs('Normalizar_gravar')?['idNumero']",
            "parameters/Des_Pedido": "@outputs('Normalizar_gravar')?['descricao']",
            "parameters/Qtd_Pedido": "@outputs('Normalizar_gravar')?['quantidade']",
            "parameters/Nom_Unidade": "@outputs('Normalizar_gravar')?['unidade']",
            "parameters/Id_UsuarioChamador": "@int(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Id_Usuario'],0))"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sql",
            "connection": "shared_sql",
            "operationId": "ExecuteProcedure_V2"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000078"
        }
      },
      "Codigo_gravar": {
        "type": "Compose",
        "inputs": "@coalesce(body('Gravar_pedido')?['ResultSets']?['Table1']?[0]?['description'],'')",
        "runAfter": {
          "Gravar_pedido": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000079"
        }
      }
    },
    "runAfter": {
      "Se_nada_mudou_gravar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000080"
    }
  },
  "allConnectionData": {
    "Gravar_pedido": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_sql"
        },
        "connection": {
          "id": "<prefixo>_sharedsql"
        },
        "connectionName": "<prefixo>_sharedsql"
      },
      "referenceKey": "shared_sql"
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
| `<procedure_gravar_pedido>` | name in brackets | AS-BUILT name of the procedure |
| `parameters/Id_Pedido` ... `parameters/Nom_Unidade` | sample parameters | those of the AS-BUILT signature, in the same order and type |
| `parameters/Id_UsuarioChamador` | `@int(coalesce(...,0))` | id of the user read in `Ler_chamador` |

## runAfter

The root depends on `Se_nada_mudou_gravar`; `Codigo_gravar` depends on `Gravar_pedido`.

## Pitfalls

- A numeric column parameter goes as a **raw** `@expr`: `@{expr}` forces text and the `INT` column receives a string (F018, R5).
- `int(coalesce(string(x),'0'))` blows up: `string(null)` is `''`. Use `int(coalesce(x,0))` (R12, F012).
- `server` and `database` stay `default`: the expression form was refused (R4); the real server belongs to the connection reference.
- The procedure name comes from the environment (`sys.procedures`), never from the document: assumed names cost pastes (R9).
- The connector limits the size of a text parameter; truncate with `take()` to the column size.
- If the procedure accepts the caller id as a parameter, whoever holds the connection reference writes as anyone they like; the defense-in-depth decision belongs to the `sql-procedures` skill.

## Variations

- Two writes in sequence: a single procedure (transaction on the server); in the flow, two calls are not atomic.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/write-via-procedure.json
```

Expected result: `0 error(s), 5 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted snippet): `Ler_chamador`, `Normalizar_gravar`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

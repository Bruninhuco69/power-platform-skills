# Authorize by the action's own flag

> **File**: `authorize-by-flag.json` · **Frequency**: very common · **Maturity**: stable
> **Depends on**: `read-caller-sql` (or `-dataverse`); `deny-response-terminate`

## Purpose

An `If` that denies (a `Nega_perm_<acao>` pair) when the action's flag is not on in the role. Reading the `bit` accepts `1` and `true`; a missing column denies.

## When to use / when not to use

**Use**

- Every action that writes or exports, once per `Caso_<acao>`.
- Single-action flow (no `Switch`): right after `Se_chamador_desconhecido`.

**Do not use**

- As a single gate before the `Switch`: it only knows whether the role has any permission, not which branch will run. A role that registers would end up able to do an irreversible write-off.

## Where to paste

First action of each `Caso_<acao>`; or, in a single-action flow, after `Se_chamador_desconhecido` inside `Try_pedido`. Inside a `Caso` the first node has no `runAfter`: delete the `runAfter` key of the root node before pasting.

## Inputs and outputs

**Reads**

- The caller row (`body('Ler_chamador')`).

**Exposes**

- None: it denies and ends, or continues.

## JSON

Destination: `Ctrl+V` at the designer's insertion point (clipboard scope envelope, `nodeId` `Autorizar_gravar`; the same content is in `authorize-by-flag.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Autorizar_gravar",
  "serializedValue": {
    "type": "If",
    "expression": {
      "and": [
        {
          "equals": [
            "@not(or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'true')))",
            "@true"
          ]
        }
      ]
    },
    "actions": {
      "Nega_perm_gravar": {
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
            "status": "error",
            "description": "Your role does not allow this action.",
            "id": "",
            "url": ""
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000022"
        }
      },
      "Nega_perm_gravar_fim": {
        "type": "Terminate",
        "inputs": {
          "runStatus": "Succeeded"
        },
        "runAfter": {
          "Nega_perm_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000023"
        }
      }
    },
    "else": {
      "actions": {}
    },
    "runAfter": {
      "Se_chamador_desconhecido": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000024"
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
| `Autorizar_gravar`, `Nega_perm_gravar` | names | `Autorizar_<acao>` and `Nega_perm_<acao>`, unique in the flow |
| `Flg_Gravar` | the action's flag column | the AS-BUILT flag column for this action |
| sentence | role denial | the same sentence across the whole project |

## runAfter

In a single-action flow it depends on `Se_chamador_desconhecido`. Inside the `Caso`, none.

## Pitfalls

- A `bit` arrives as `true`/`false`: `equals(true, 1)` is false. The expression compares the lowercase text with `'1'` and `'true'`.
- Comparing `toLower(string(x))` with the boolean `true` (no quotes) is always false and inverts the rule.
- `coalesce` goes **inside** `string()` (`string(coalesce(x,'0'))`), the opposite of what applies to `int()`.
- A permission flag starts off in the role: nobody gets a permission by default.

## Variations

- Role in Dataverse: replace the expression with `equals(first(body('Ler_perfil')?['value'])?['<prefixo>_podegravar'],true)` (see `read-caller-dataverse`).

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/authorize-by-flag.json
```

Expected result: `0 error(s), 1 warning(s)`.

Intrinsic warnings of the component on its own:

- `F006` (reference to an action outside the pasted snippet): `Ler_chamador`. These are the block's **inputs**: they exist in the target flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

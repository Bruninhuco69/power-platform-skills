# Unit scope (SQL track)

> **File**: `unit-scope.json` · **Frequency**: common · **Maturity**: stable
> **Depends on**: `config` (`cfgEscopoUnidade`); `state-before`; `read-caller-sql`

## Purpose

A boolean `Compose` `Escopo_ok_gravar` and an `If` that denies. Passes whoever has the all-units flag, or whoever has the same unit as the real record **and** the record has a unit. Switch off lets everyone through.

## When to use / when not to use

**Use**

- Action on an existing record in a system with unit scope.

**Do not use**

- As a substitute for the gallery filter: the app filter is UX; only the flow blocks.
- Create with no prior record: compare `outputs('Normalizar_gravar')?['unidade']`.

## Where to paste

Inside `Caso_<acao>`, after `Bloco_estado_antes`.

## Inputs and outputs

**Reads**

- `CONFIG.cfgEscopoUnidade`, flag `Flg_TodasUnidades` and the caller's unit, the real record's unit.

**Exposes**

- `outputs('Escopo_ok_gravar')` (boolean); denies with `Nega_escopo_gravar`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_escopo_unidade`; the same content is in `unit-scope.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Bloco_escopo_unidade",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Escopo_ok_gravar": {
        "type": "Compose",
        "inputs": "@or(equals(outputs('CONFIG')?['cfgEscopoUnidade'],false),or(or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_TodasUnidades'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_TodasUnidades'],'0'))),'true')),and(not(empty(toUpper(trim(coalesce(first(body('Estado_antes_gravar')?['value'])?['Nom_Unidade'],''))))),equals(toUpper(trim(coalesce(first(body('Estado_antes_gravar')?['value'])?['Nom_Unidade'],''))),toUpper(trim(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Nom_Unidade'],'')))))))",
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000041"
        }
      },
      "Se_fora_do_escopo_gravar": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@not(outputs('Escopo_ok_gravar'))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Nega_escopo_gravar": {
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
                "description": "You do not have access to this unit.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000042"
            }
          },
          "Nega_escopo_gravar_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_escopo_gravar": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000043"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Escopo_ok_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000044"
        }
      }
    },
    "runAfter": {
      "Bloco_estado_antes": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000045"
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
| `Flg_TodasUnidades` | global profile flag | AS-BUILT column |
| `Nom_Unidade` | unit on the record and on the caller | AS-BUILT columns |
| `cfgEscopoUnidade` | `CONFIG` key | keep it on |

## runAfter

The root depends on `Bloco_estado_antes`; the `If` depends on `Escopo_ok_gravar`.

## Pitfalls

- A missing switch reads `null`: `equals(key, false)` only lets everyone through with an explicit `false` (fail-closed).
- An empty unit on the record **blocks** anyone who is not global; missing data acting as a wildcard is the opposite of scope.
- The global profile is the first term of the `or`: whoever sees everything needs no link. Do not count on short-circuiting to protect the other terms: each one is already valid on its own (`coalesce`, `?[]`).
- The message does not say the record's unit.
- One project shipped the scope as a switched-off flag: any profile saved to any unit.

## Variations

- Dataverse: `dataverse-units-scope` (several units per user).
- Instead of a separate block, the rule can go in as the first clause of `Validar_*`; that is one action fewer, but the message disappears from the middle of the chain.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/unit-scope.json
```

Expected result: `0 error(s), 3 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted snippet): `CONFIG`, `Estado_antes_gravar`, `Ler_chamador`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.

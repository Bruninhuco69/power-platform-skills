# Identify the caller (MyProfile_V2)

> **File**: `identify-caller.json` · **Frequency**: very common · **Maturity**: stable
> **Depends on**: `config`; Office 365 Users connector

## Purpose

Reads the profile of the user running the flow (`MyProfile_V2`) and normalizes the identifier to lowercase in a `Compose` named `Chamador`. Whoever calls from outside the screen does not choose who they are.

## When to use / when not to use

**Use**

- Every flow that authorizes by role.

**Do not use**

- An HTTP inbound flow (no human user).
- When the user identifier arrives as a trigger parameter: never do that.

## Where to paste

Root of the flow scope, after `CONFIG`.

## Inputs and outputs

**Reads**

- The connection context of the user running the flow.

**Exposes**

- `outputs('Chamador')`: e-mail (or UPN) in lowercase, used by `read-caller-sql` and `read-caller-dataverse`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_chamador`; the same content is in `identify-caller.json`). Fictitious GUIDs; connections: `<prefixo>_sharedoffice365users`.

```json
{
  "nodeId": "Bloco_chamador",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Perfil_do_chamador": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "$select": "mail,userPrincipalName,displayName"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365users",
            "connection": "shared_office365users",
            "operationId": "MyProfile_V2"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000005"
        }
      },
      "Chamador": {
        "type": "Compose",
        "inputs": "@toLower(trim(coalesce(outputs('Perfil_do_chamador')?['body/mail'],outputs('Perfil_do_chamador')?['body/userPrincipalName'],'')))",
        "runAfter": {
          "Perfil_do_chamador": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000006"
        }
      }
    },
    "runAfter": {
      "Bloco_config": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000007"
    }
  },
  "allConnectionData": {
    "Perfil_do_chamador": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_office365users"
        },
        "connection": {
          "id": "<prefixo>_sharedoffice365users"
        },
        "connectionName": "<prefixo>_sharedoffice365users"
      },
      "referenceKey": "shared_office365users"
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
| `shared_office365users` connection | `<prefixo>_sharedoffice365users` | logical name of the connection reference in the target environment (`power-platform` skill) |
| order in `coalesce` | `mail`, then `userPrincipalName` | the order that matches the value stored in the identity column (see pitfalls) |

## runAfter

The root depends on `Bloco_config`. Inside the block, `Chamador` depends on `Perfil_do_chamador`.

## Pitfalls

- The `mail` x `userPrincipalName` order must match what the identity column stores. A mismatch denies **everyone**, with no error. One-minute test: run with a test user and compare `outputs('Chamador')` in the run history with the column.
- One project ended up with the order inverted between flows. Standardize the order in a single place in the project.
- `$select` limits what the connector returns; if `mail` is missing, the `coalesce` silently falls to the UPN.
- Data from the context needs no escaping, but whoever builds an OData `$filter` with it must double the apostrophe (see `read-caller-dataverse`).

## Variations

- UPN-first identity: swap the two `coalesce` arguments.
- Another identity system (e.g. a directory group): replace `MyProfile_V2` with `UserProfile_V2`/`MemberOf`; the `Chamador` contract does not change.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/identify-caller.json
```

Expected result: `0 error(s), 0 warning(s)`.

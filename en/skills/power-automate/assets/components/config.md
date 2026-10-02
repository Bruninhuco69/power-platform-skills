# CONFIG: environment flags and texts

> **File**: `config.json` · **Frequency**: very common (`CONFIG` in flows called by the app; `settings` in the inbound flow, see `inbound-config`) · **Maturity**: stable
> **Depends on**: none

## Purpose

A single `Compose` named `CONFIG` holds the switches and texts that change per environment (support e-mail, output folder, access group). No other action in the flow carries an environment literal. The verifier knows the name `CONFIG` and does not flag a literal inside it (F014).

## When to use / when not to use

**Use**

- Every flow called by the screen.
- Inbound flow that needs simple flags (use `inbound-config` for the batch keys).

**Do not use**

- To store a SQL server or database: they stay `default` and come from the connection reference (R4).
- For a secret or token: use a secret-type environment variable.

## Where to paste

Root of the flow scope, as the first action (right after the hand-typed trigger). First node: no `runAfter`.

## Inputs and outputs

**Reads**

- Nothing. It is a constant.

**Exposes**

- `outputs('CONFIG')?['<key>']`, read by `unit-scope`, `export-csv-file`, `support-email-with-partial` and `token-cache-and-http-response`.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_config`; the same content is in `config.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Bloco_config",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "CONFIG": {
        "type": "Compose",
        "inputs": {
          "mailSuporte": "suporte@contoso.com",
          "cfgEscopoUnidade": true,
          "cfgDescricaoObrigatoria": true,
          "pastaSaida": "/Exportacoes",
          "grupoAcesso": "<grupo-de-acesso>"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000001"
        }
      }
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000002"
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
| `mailSuporte` | `suporte@contoso.com` | the environment's support mailbox |
| `cfgEscopoUnidade` | `true` | keep `true`: a security switch starts on (F3) |
| `cfgDescricaoObrigatoria` | `true` | other switchable rules; every security switch starts `true` |
| `pastaSaida` | `/Exportacoes` | output folder of the file connector, for generated files |
| `grupoAcesso` | `<grupo-de-acesso>` | directory group name, if the flow requests access by e-mail |

## runAfter

Root with empty `runAfter`. The next component (`identify-caller`) points to `Bloco_config`.

## Pitfalls

- A security flag born `false` let any role write to any unit; the product decision was never closed. Turn it on by default.
- Do not mix them up: a role **permission** flag (`Flg_PodeX`) starts off; a **security** switch in `CONFIG` starts on.
- A missing key reads as `null`. Test `equals(key, false)` (fail-closed), never `not(key)`: `not(null)` is not false.
- Promoting an environment means editing the `CONFIG` value; if an environment literal shows up in another action, the verifier warns (F014).

## Variations

- Inbound HTTP flow: replace this block with `inbound-config`.
- A value that must change without editing the flow: an environment variable read in `parameters()`. It does not work for a token cache: the value is frozen until the flow is saved.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/config.json
```

Expected result: `0 error(s), 0 warning(s)`.

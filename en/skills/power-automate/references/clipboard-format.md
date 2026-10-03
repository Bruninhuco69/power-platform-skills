# Designer clipboard format

What the new Power Automate designer puts on the clipboard on `Ctrl+C` of an action, and accepts
back on `Ctrl+V` -- including coming from another flow, another tab or a file. It is the
equivalent of the pasteable `.pa.yaml` for screens: **the flow becomes a file**.

> Authority: real samples copied from the designer (a `Compose` and a `Condition`) and a whole
> flow pasted and returned by the designer. Everything they show is marked as confirmed; the
> rest is `[unverified]`. [verified: reference project]

## Contents

1. [How to copy and paste](#1-how-to-copy-and-paste)
2. [Two envelopes, not one](#2-two-envelopes-not-one)
3. [Scope envelope](#3-scope-envelope)
4. [Leaf-node envelope](#4-leaf-node-envelope)
5. [Inputs: segments and rawInputs](#5-inputs-segments-and-rawinputs)
6. [Language and the trigger nodeId](#6-language-and-the-trigger-nodeid)
7. [Symptoms when pasting](#7-symptoms-when-pasting)
8. [Generation rules](#8-generation-rules)
9. [What is not confirmed](#9-what-is-not-confirmed)

---

## 1. How to copy and paste

- **Copy:** in the new designer, select the action (or scope) and press `Ctrl+C`. The clipboard
  content is the JSON below (one line).
- **Paste:** click the insertion point in the target flow and press `Ctrl+V`. Paste **top to
  bottom**: `nodeTokenData.upstreamNodeIds` cites nodes that must already exist.
- **File:** save the JSON in a `.json` file -- or in a `.md` that contains **only** the JSON (the
  delivery format of one of the reference projects) -- and paste the whole content.
- **Check before pasting:** `python <skill-folder>/scripts/verificar-fluxo.py <file>`. The designer
  validates nothing before pasting: a repeated name, an orphan token or an invented column pastes
  "successfully" and only breaks at run time.

## 2. Two envelopes, not one

| | Scope node | Leaf node |
|---|---|---|
| Top-level keys | **6**: `nodeId`, `serializedValue`, `allConnectionData`, `staticResults`, `isScopeNode: true`, `mslaNode: true` | **7**: `nodeId`, `nodeData`, `nodeTokenData`, `nodeOperationInfo`, `nodeConnectionData`, `isScopeNode: false`, `mslaNode: true` |
| Carries | the **raw Logic Apps definition** in `serializedValue`, with the whole subtree | the designer's parameter model in `nodeData` |
| Children | come inside, in full | has none |
| Connection | `allConnectionData` | `nodeConnectionData` |

Consequences:

1. **A whole flow fits in a `Scope` and therefore in a single paste** (dozens of nodes at once). A
   scope is transparent at run time; it costs one indentation level in the designer.
2. `runAfter` travels in the normal form of the definition, inside `serializedValue` -- including
   the one on `Catch` with `["Failed","TimedOut","Skipped"]`. There is no manual "configure run
   after" step.
3. A scope has **no** segment model and no GUID per segment: it is the literal definition. The rest
   of this file about segments applies only to a leaf node.
4. `mslaNode` is the new designer's marker; without it the node is not recognized.

Any action with children (`Scope`, `If`, `Switch`, `Foreach`) can be pasted as a scope envelope.

## 3. Scope envelope

Minimum valid (a `Compose` inside a scope), pasteable and approved by the verifier:

```json
{
  "nodeId": "Escopo_exemplo",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Compor_exemplo": {
        "type": "Compose",
        "inputs": "@toLower(trim(coalesce(triggerBody()['text'], '')))",
        "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000006" }
      }
    },
    "runAfter": {},
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000007" }
  },
  "allConnectionData": {},
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

Destination: `Ctrl+V` at the insertion point of a flow that already has the Power Apps (V2) trigger.

- `allConnectionData` has **one entry per `OpenApiConnection` action** in the scope, keyed by the
  action name, with the connection reference of the target environment (R1 in
  [designer-baseline.md](designer-baseline.md)); when empty, the action pastes without a
  connection and the run is blocked (F017). Entry format:

```json
{
  "Ler_chamador": {
    "connectionReference": {
      "api": { "id": "/providers/Microsoft.PowerApps/apis/shared_sql" },
      "connection": { "id": "<prefixo>_sharedsql" },
      "connectionName": "<prefixo>_sharedsql"
    },
    "referenceKey": "shared_sql"
  }
}
```

  Destination: value of `allConnectionData` in the envelope. `<prefixo>_sharedsql` is the logical
  name of the connection reference in the **target environment** (the `power-platform` skill
  creates and versions it); never copy the name from another environment.
- The first node in the scope has no `runAfter`; the root scope keeps `"runAfter": {}`. When
  pasting a fragment, the root's `runAfter` points to a node that **already exists** at the
  insertion point (the verifier does not check that name; references to actions outside the
  snippet become warning F006).

## 4. Leaf-node envelope

`Compose` with a trigger token (the GUIDs are fictitious: generate a new one per field, per
segment and per `operationMetadataId`). The sample is a capture from a pt-BR designer, so the
labels read `Entradas` ("Inputs"); an en-US designer emits its own labels `[unverified]`:

```json
{
  "nodeId": "Compor_exemplo",
  "nodeData": {
    "id": "Compor_exemplo",
    "nodeInputs": {
      "dynamicLoadStatus": "Succeeded",
      "parameterGroups": {
        "default": {
          "id": "default",
          "description": "",
          "parameters": [
            {
              "id": "00000000-0000-0000-0000-0000000000a1",
              "info": { "isDynamic": false },
              "hideInUI": false,
              "label": "Entradas",
              "parameterKey": "inputs.$",
              "parameterName": "Entradas",
              "placeholder": "Entradas",
              "required": true,
              "schema": { "title": "Entradas", "description": "Entradas", "properties": {} },
              "showErrors": false,
              "showTokens": true,
              "suppressCasting": true,
              "type": "any",
              "value": [
                {
                  "id": "00000000-0000-0000-0000-0000000000a2",
                  "type": "token",
                  "token": {
                    "source": "outputs",
                    "name": "body.text",
                    "key": "outputs.$.body.text",
                    "required": true,
                    "tokenType": "outputs",
                    "title": "acao",
                    "value": "triggerBody()['text']",
                    "type": "string",
                    "schema": {
                      "title": "acao",
                      "type": "string",
                      "x-ms-dynamically-added": true,
                      "description": "Insira sua entrada",
                      "x-ms-content-hint": "TEXT"
                    },
                    "description": "Insira sua entrada",
                    "icon": "https://content.powerapps.com/resource/makerx/static/pauto/images/designeroperations/PowerApps2.05e0cdd0.png",
                    "brandColor": "#742774",
                    "isSecure": false
                  },
                  "value": "triggerBody()['text']"
                }
              ],
              "visibility": "",
              "validationErrors": []
            }
          ],
          "rawInputs": [
            {
              "description": "Entradas",
              "key": "inputs.$",
              "name": "Entradas",
              "required": true,
              "schema": { "title": "Entradas", "description": "Entradas", "properties": {} },
              "summary": "",
              "suppressCasting": true,
              "title": "Entradas",
              "type": "any",
              "visibility": "",
              "hideInUI": false,
              "value": "@triggerBody()['text']"
            }
          ]
        }
      }
    },
    "nodeOutputs": {
      "outputs": {
        "outputs.$": {
          "key": "outputs.$",
          "type": "any",
          "isAdvanced": false,
          "name": "key-outputs-output",
          "title": "Saídas",
          "schema": {},
          "source": "outputs",
          "required": true
        }
      }
    },
    "nodeDependencies": { "inputs": {}, "outputs": {} },
    "operationMetadata": {
      "iconUri": "https://content.powerapps.com/resource/makerx/static/pauto/images/designeroperations/dataoperationedit.2c8a4d5e.png",
      "brandColor": "#8C6CFF",
      "isConnectToSystemsOperation": false
    },
    "settings": {
      "asynchronous": { "isSupported": false, "value": false },
      "correlation": { "isSupported": false },
      "secureInputs": { "isSupported": true },
      "secureOutputs": { "isSupported": false },
      "disableAsyncPattern": { "isSupported": false, "value": false },
      "disableAutomaticDecompression": { "isSupported": false },
      "splitOn": { "isSupported": false, "value": { "enabled": false } },
      "retryPolicy": { "isSupported": false },
      "requestOptions": { "isSupported": false },
      "sequential": false,
      "suppressWorkflowHeaders": { "isSupported": false },
      "suppressWorkflowHeadersOnResponse": { "isSupported": false, "value": false },
      "concurrency": { "isSupported": false },
      "singleInstance": false,
      "timeout": { "isSupported": false },
      "paging": { "isSupported": false, "value": { "enabled": false } },
      "uploadChunk": { "isSupported": false, "value": {} },
      "downloadChunkSize": { "isSupported": false },
      "trackedProperties": { "isSupported": true },
      "requestSchemaValidation": { "isSupported": false, "value": false },
      "conditionExpressions": { "isSupported": false },
      "runAfter": { "isSupported": false, "value": [] },
      "invokerConnection": { "isSupported": false, "value": { "enabled": false } },
      "statelessFlow": { "isSupported": false, "value": { "enabled": false } }
    },
    "actionMetadata": { "operationMetadataId": "00000000-0000-0000-0000-0000000000a3" },
    "repetitionInfo": { "repetitionReferences": [] }
  },
  "nodeTokenData": {
    "tokens": [
      {
        "key": "outputs.$",
        "brandColor": "#8C6CFF",
        "icon": "https://content.powerapps.com/resource/makerx/static/pauto/images/designeroperations/dataoperationedit.2c8a4d5e.png",
        "title": "Saídas",
        "name": "key-outputs-output",
        "type": "any",
        "isAdvanced": false,
        "outputInfo": {
          "type": "outputs",
          "required": true,
          "source": "outputs",
          "isSecure": false,
          "actionName": "Compor_exemplo",
          "schema": {}
        }
      }
    ],
    "upstreamNodeIds": ["Quando_o_Power_Apps_chama_um_fluxo_(V2)"]
  },
  "nodeOperationInfo": { "connectorId": "DataOperation", "operationId": "Compose", "type": "Compose" },
  "nodeConnectionData": null,
  "isScopeNode": false,
  "mslaNode": true
}
```

Destination: `Ctrl+V` in a flow whose trigger is named `Quando_o_Power_Apps_chama_um_fluxo_(V2)`
(pt-BR environment; see §6). A leaf node only suits an isolated action; **prefer the scope
envelope**, which does without the segment model.

| `nodeData` | Content |
|---|---|
| `id` | Repeats `nodeId`; a mismatch renames the node on paste |
| `nodeInputs` | Inputs in two parallel views (§5) |
| `nodeOutputs` | What the action publishes, keyed by `key` |
| `settings` | 24 keys `{isSupported, value?}`. This is where the `runAfter` configured in the designer lives |
| `actionMetadata` | `operationMetadataId`: a new GUID per node |

## 5. Inputs: segments and rawInputs

`parameterGroups.default` has two parallel lists for the same field:

- `parameters[]`: the **editor** view. `value` is a **list of segments**, never a string:
  `literal` (`{"type":"literal","value":"text","valueType":"string"}`) or `token` (cites an earlier
  output by action name).
- `rawInputs[]`: the **definition** view. `value` is the expression string with `@`.

Rebuild rule (`parameters[].value` -> `rawInputs[].value`):

| Segments | `rawInputs[].value` |
|---|---|
| 1 token only | `@<expression>` |
| 1 literal only | `<text>` |
| mix | `@{<expr>}<text>@{<expr>}...` -- each token between `@{ }`, literal raw |

In one sample copied from the designer the two views came out **out of sync** (the editor changed
the segments and did not rewrite `rawInputs`), which suggests the designer regenerates `rawInputs`
on paste. Do not bet on it: generate both consistent. The verifier warns about the mismatch (F019,
warning) and flags a GUID repeated across fields/segments, `token.value` different from `value`,
and a non-empty `validationErrors` (F019, error).

## 6. Language and the trigger nodeId

The trigger `nodeId` is the **label in the environment's language**: in a pt-BR environment it is
`Quando_o_Power_Apps_chama_um_fluxo_(V2)`; in an English environment it would be
`When_Power_Apps_calls_a_flow_(V2)` `[unverified: English name deduced, no sample]`, and every
token that cites it is generated differently. Declare the environment's language in the flow
contract and redo the sample if the language changes. In a scope envelope this does not matter
(the tokens are `triggerBody()` expressions).

## 7. Symptoms when pasting

Seen when pasting a script-generated scope into the new designer. The verifier flags each one
(F020-F023).

| Symptom | Cause | Rule | Status |
|---|---|---|---|
| The flow does not save | `Initialize variable` inside the scope: it only works at the flow root, and the envelope is **one** scope | create the variables at the root before pasting, or generate them as the first actions in the scope and drag them out (between the trigger and the scope) before saving (F021) | seen |
| `If` condition blank (`{"and":[{"equals":["",""]}]}`), on every `If` | condition written as text (`"@not(equals(…))"`): the designer only reads an object | `{"and": [{"equals": ["@<expression>", "@true"]}]}`, always with `and` or `or` at the root (F020). `Switch` with text is fine | seen |
| Required field blank ("'From' is required") | `@variables('x')` alone becomes a **variable token**; with the variable inside the pasted snippet, the token does not resolve | never a variable alone in a field: `@skip(variables('x'), 0)`, `@equals(variables('x'), true)`, `@coalesce(variables('x')?['a'], 0)`. An expression with a function pastes whole (F022) | symptom seen; the replacement has not been pasted yet |
| `Set variable` and `Append to variable` without the name | same cause; the name field does not accept an expression | after pasting, pick the name by hand in each one; list those actions in the flow instructions | seen with the variable inside the snippet; with the variable already at the root, unverified |
| `Do until` with the condition as text | the usual form of the export, not yet seen pasting | if it comes blank: advanced mode, the same expression (F023) | unverified |

[verified: reference project] on the rows marked "seen".

## 8. Generation rules

| # | Rule | Why |
|--:|---|---|
| 1 | `nodeId` == `nodeData.id` == `tokens[].outputInfo.actionName` (F003) | A mismatch renames or detaches the token |
| 2 | `nodeId` unique in the flow, no spaces (F003, F004) | A repeat silently becomes `_1`; tokens keep pointing at the original |
| 3 | New GUID per field, segment and `operationMetadataId` (F019) | A collision corrupts the editor |
| 4 | `validationErrors: []` (F019) | A node copied with an error propagates the error |
| 5 | `rawInputs` rebuilt from the segments (F019) | Do not bet on regeneration |
| 6 | Column name in the environment's **logical** name (in Power Fx it is the display name; in flow and OData it is the logical one) | An OData filter with a wrong name gives no error: it returns an empty list, indistinguishable from "no duplicates" |
| 7 | Zero literal GUID/server of the environment outside `CONFIG` (F014) | A literal points to DEV after promotion |
| 8 | Paste top to bottom | `upstreamNodeIds` must exist |

## 9. What is not confirmed

| Item | Status |
|---|---|
| Scope envelope (6 keys) and leaf envelope (7 keys) | confirmed |
| A scope carries the children and the raw `runAfter` | confirmed |
| `allConnectionData` per `OpenApiConnection` action | confirmed (whole flow pasted and returned by the designer) |
| `nodeConnectionData` of a **leaf** connector action (the sample only has `null`) | `[unverified]`: prefer a scope |
| `nodeOperationInfo` (`connectorId`/`operationId`/`type`) of actions other than `Compose` | `[unverified]` in a leaf envelope; use a scope |
| Pasteable trigger | it is not: type it by hand |
| `If` with the condition as an object and `and`/`or` at the root | confirmed (§7) |
| Variable read by an expression with a function in a pasted field | `[unverified]`: the replacement has not been pasted yet |
| Name on variable actions when the variable already exists at the root before pasting | `[unverified]` |

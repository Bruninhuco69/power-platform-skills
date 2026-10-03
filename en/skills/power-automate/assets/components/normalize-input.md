# Normalize the trigger input

> **File**: `normalize-input.json` · **Frequency**: common · **Maturity**: stable
> **Depends on**: `action-switch` (or a single-action flow); trigger parameters

## Purpose

A `Compose` that applies `trim`, `take`, `toUpper` and a protected text-to-number conversion, and returns an object. The following actions read `outputs('Normalizar_gravar')?['field']`, never `triggerBody()`.

## When to use / when not to use

**Use**

- Every case that receives fields from the app.

**Do not use**

- To validate a business rule: that is `validate-with-message`.

## Where to paste

Inside `Caso_<acao>`, after `Autorizar_<acao>`.

## Inputs and outputs

**Reads**

- `triggerBody()['text_1']` ... `['text_5']` (positional, always text).

**Exposes**

- `outputs('Normalizar_gravar')`: `id`, `idNumero`, `descricao`, `unidade`, `quantidade`, `prazo` (null when empty).

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Bloco_normalizar`; the same content is in `normalize-input.json`). Fictitious GUIDs; connections: none.


```json
{
  "nodeId": "Bloco_normalizar",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Normalizar_gravar": {
        "type": "Compose",
        "inputs": {
          "id": "@trim(coalesce(triggerBody()['text_1'],''))",
          "idNumero": "@int(if(and(not(empty(trim(coalesce(triggerBody()['text_1'],'')))),equals(length(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(trim(coalesce(triggerBody()['text_1'],'')),'0',''),'1',''),'2',''),'3',''),'4',''),'5',''),'6',''),'7',''),'8',''),'9','')),0),less(length(trim(coalesce(triggerBody()['text_1'],''))),10)),trim(coalesce(triggerBody()['text_1'],'')),'0'))",
          "descricao": "@take(trim(coalesce(triggerBody()['text_2'],'')),200)",
          "unidade": "@toUpper(trim(coalesce(triggerBody()['text_3'],'')))",
          "quantidade": "@int(if(and(not(empty(trim(coalesce(triggerBody()['text_4'],'')))),equals(length(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(trim(coalesce(triggerBody()['text_4'],'')),'0',''),'1',''),'2',''),'3',''),'4',''),'5',''),'6',''),'7',''),'8',''),'9','')),0),less(length(trim(coalesce(triggerBody()['text_4'],''))),10)),trim(coalesce(triggerBody()['text_4'],'')),'0'))",
          "prazo": "@if(empty(trim(coalesce(triggerBody()['text_5'],''))),null,trim(coalesce(triggerBody()['text_5'],'')))"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000034"
        }
      }
    },
    "runAfter": {
      "Autorizar_gravar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000035"
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
| `text_1`...`text_5` | parameter position | position according to the trigger contract (`trigger-power-apps-v2`) |
| `take(..., 200)` | character limit | the size of the target column |
| `toUpper` | unit in uppercase | the normalization the comparison requires |
| name `Normalizar_gravar` | action suffix | `Normalizar_<acao>`, unique in the flow |

## runAfter

The root depends on `Autorizar_gravar`; replace it with the previous node of your case.

## Pitfalls

- `if()` evaluates both branches: `if(isNumber, int(t), 0)` blows up with text. Protect the argument: `int(if(isNumber, t, '0'))`.
- WDL has no regex: the 'digits only' test removes the ten digits and checks that nothing is left; limit of 9 characters to fit in `int`.
- `take(x, N)` is safe with text shorter than N; it replaces `substring(x, 0, min(length(x), N))` and saves characters from the 8,192 limit.
- A deliberately `null` value (optional date) does not go through `coalesce` or truncation: `''` matches nothing and becomes an empty column, not null.
- A new parameter goes **at the end** of the trigger; inserting it in the middle makes the values slide and the flow writes the wrong field without an error.

## Variations

- Decimal or date: convert in the flow and validate with a message; never trust the format the app sends.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/normalize-input.json
```

Expected result: `0 error(s), 0 warning(s)`.

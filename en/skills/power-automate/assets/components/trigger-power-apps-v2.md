# Power Apps (V2) trigger: positional parameters

> **File**: `trigger-power-apps-v2.md` (descriptive: no pasteable JSON) · **Frequency**: very common · **Maturity**: stable
> **Depends on**: none

## Purpose

Declares the parameters the app sends in `.Run()`. This is the delivery's **highest-risk** step: the trigger does not travel on the
clipboard, and the parameter order is the contract with the screen.

## When to use / when not to use

- Use in every flow called by a Power Apps screen.
- Do not use for an external system: the trigger is different (`trigger-http-inbound`).
- Do not use when the caller is another flow: the contract is different.

## Where to paste

It is not pasted. Create the instant flow, choose the **Power Apps (V2)** trigger and type the parameters in the designer, in
the order of the table, **before** pasting `config`. The scope envelope of the other components does not carry the trigger.

## Inputs and outputs

- Input: one text field per row. The app passes them by **position**.
- Output: `triggerBody()['text']`, `['text_1']`, `['text_2']`... in declaration order. All text.
- The response to the app is the 4-field `Response` (`deny-response-terminate`, `translate-code-and-respond`).

## Parameter table (example from the save flow)

| # | Name in the designer | `triggerBody()` | Content | Note |
|--:|---|---|---|---|
| 1 | `acao` | `['text']` | `gravar`, `excluir` | `Switch` value; the app sends it in lowercase |
| 2 | `pedido_id` | `['text_1']` | record id | number as text; empty on create |
| 3 | `descricao` | `['text_2']` | free text | the flow truncates it |
| 4 | `unidade` | `['text_3']` | the record's unit | compared with the one on the role |
| 5 | `quantidade` | `['text_4']` | number as text | the flow converts it |
| 6 | `prazo` | `['text_5']` | ISO date as text | empty = no deadline |
| 7 | `situacao` | `['text_6']` | `aberto`, `fechado` | used by `derive-value-switch` |

Other contracts the components assume: **export** (`acao`, `filtros` as JSON in text, in `['text_1']`,
used by `screen-filters-json`) and **access request** (`acao`, `email_alvo` in `['text_1']`, `id_diretorio` in
`['text_2']`, used by `resolve-directory-id` and `support-email-with-partial`).

## Steps in the designer (en-US environment)

1. **Create** > **Instant cloud flow** > trigger **Power Apps (V2)** (node name: `When_Power_Apps_calls_a_flow_(V2)`).
2. Under **Add an input**, choose **Text** and type the parameter name `acao`.
3. Repeat for each row of the table, **in the same order**. Do not reorder after publishing.
4. Save the empty flow once; only then paste `Bloco_config`, `Bloco_chamador` and the other components.
5. Check in the editor that the pasted `Response` shows 4 text outputs: `status`, `description`, `id`, `url`.
6. In the app, `.Run()` takes **exactly** the same number of arguments, in the same order. Number as text with `Text(id, "[$-en-US]0")`.

## Parameters to change

| Item | Value in the example | Change to |
|---|---|---|
| parameter names | table above | those in your flow's contract (`assets/flow-contract-template.md`) |
| number of parameters | 7 | your flow's; the screen and the flow agree |

## runAfter

Does not apply: the trigger is the root. The first component (`config`) has an empty `runAfter`.

## Pitfalls

- **A new parameter always goes at the end.** Inserting in the middle shifts the values and the flow saves the wrong field, with no error.
- Number, date and boolean arrive as **text**: convert in the flow (`normalize-input`) with a protected argument.
- The trigger node name depends on the environment language. In a pt-BR environment it would be `Quando_o_Power_Apps_chama_um_fluxo_(V2)` `[unverified: deduced, no sample]`. In a scope envelope this does not matter (the tokens are `triggerBody()` expressions).
- The user identifier never comes as a parameter: use `identify-caller`.
- When the contract changes: update the trigger **and** the `.Run()` in the same commit; the number of `.Run()` arguments must equal the number of trigger parameters: missing or extra, the app formula reports an error (optional parameter: the app sends `""`).

## Variations

- Optional parameter: the app sends `""` and the flow treats empty as absent.
- Many parameters: one of them can be a JSON object in text (`screen-filters-json`), with key validation.

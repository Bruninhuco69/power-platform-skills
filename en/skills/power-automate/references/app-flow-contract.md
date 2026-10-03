# App ↔ flow contract (flow side)

Decisions C1–C4 and C6 of [default-decisions.md](../../power-platform/references/default-decisions.md).
This file is the **flow** side; the `.Run()` call in the app (loading, toast, `IfError`,
`Refresh`) belongs to the `powerapps-canvas` skill.

## Contents

1. [Power Apps trigger (V2): positional parameters](#1-power-apps-trigger-v2-positional-parameters)
2. [Response: always four fields](#2-response-always-four-fields)
3. [Write code to message](#3-write-code-to-message)
4. [A new parameter goes at the end](#4-a-new-parameter-goes-at-the-end)
5. [The call as seen from the app](#5-the-call-as-seen-from-the-app)
6. [Long operation](#6-long-operation)
7. [Contract document](#7-contract-document)

---

## 1. Power Apps trigger (V2): positional parameters

The app passes the arguments **by position**, not by name. The trigger's first text parameter is
read as `triggerBody()['text']`, the second as `triggerBody()['text_1']`, and so on
(`text_N`). [verified: reference project]

| # | Name in the trigger | Read in the flow | Content |
|--:|---|---|---|
| 1 | `acao` | `triggerBody()['text']` | `gravar` |
| 2 | `id` | `triggerBody()['text_1']` | record id, as text |
| 3 | `descricao` | `triggerBody()['text_2']` | free text |
| 4 | `unidade` | `triggerBody()['text_3']` | unit abbreviation |

- **All text.** Number, date and boolean travel as text and are converted in `Normalizar`.
- **The order is the signature.** Inserting a parameter in the middle shifts the values one slot and the
  flow writes the wrong field without complaining.
- **Identity never comes through a parameter** (`upn`, the user's e-mail): whoever calls would say who they are. It
  comes from `MyProfile_V2` ([authorization-in-flow.md](authorization-in-flow.md)). An identity
  parameter is only justified to stamp authorship of **another** user (the target of the action).
- The trigger's `nodeId` depends on the environment language (see [clipboard-format.md](clipboard-format.md)).

## 2. Response: always four fields

```json
{
  "status": "success",
  "description": "Record saved.",
  "id": "123",
  "url": ""
}
```

| Field | Type | Values |
|---|---|---|
| `status` | text | `success`, `warning` or `error` |
| `description` | text | ready-made sentence for the user, en-US, no jargon, built **in the flow** |
| `id` | text | id of the created/changed record; empty on error |
| `url` | text | only on export; empty otherwise |

- **All four are always returned, even empty.** A screen that reads `ret.url` from a flow that does not export
  gets `""`, not a missing-property error. The verifier flags a `Response` with a missing
  field (F010).
- `Response` with `kind: PowerApp`, `statusCode: 200` and `schema` with `additionalProperties: {}`
  (R6 in [designer-baseline.md](designer-baseline.md)). A business error is also 200: the app
  decides by `status`.
- **`warning` is not decoration.** When the operation **wrote** but with a caveat (e.g. a registration
  with a duplicate enters as pending), returning `error` makes the user think nothing happened and
  repeat it. The app closes the modal on `warning` (C3).
- **The denial is generic on purpose.** "Your role does not allow this action" does not say which unit
  or record; saying it would answer, to whoever is probing, a question they could not ask.

## 3. Write code to message

The procedure (or the write step) returns an ASCII **code** from a closed vocabulary; the flow
translates it. Keep the code in a `Compose` and translate with a nested `if()` (messages in single
quotes; text with a value uses `concat()`, never `@{}` inside an `if()` literal):

```text
Codigo_gravar  = @coalesce(body('Gravar_registro')?['ResultSets']?['Table1']?[0]?['description'],'')
status         = @{if(equals(outputs('Codigo_gravar'),'GRAVADO'),'success',if(equals(outputs('Codigo_gravar'),'NAO_APLICADO'),'warning','error'))}
description    = @{if(equals(outputs('Codigo_gravar'),'GRAVADO'),'Record saved.',if(equals(outputs('Codigo_gravar'),'NAO_APLICADO'),'Nothing was changed.',concat('Unexpected system response: ',outputs('Codigo_gravar'),'.')))}
```

Destination: the `body.status` and `body.description` fields of a `Response` action (a text field's value,
hence `@{...}`); the `Compose` uses a bare `@expr`. The template `assets/flow-write-template.json` brings
exactly this.

Rules:

1. **An unknown code responds `error` naming the code** and forces `status` to `error`, even
   if the write said `success`. A new code in the procedure with no translation in the flow never becomes
   a silent success.
2. Closed vocabulary: the code -> sentence table lives in the contract document
   ([assets/flow-contract-template.md](../assets/flow-contract-template.md)), not scattered.
3. The procedure returns 1 row with `status, description, id, url`
   (decision B1; the `sql-procedures` skill defines the procedure). Zero rows becomes `''` in the
   `coalesce` and falls into the "unknown" case.

## 4. A new parameter goes at the end

- New parameter: **always at the end** of the trigger and of the call.
- A dead parameter becomes `naoUsado<N>` and keeps occupying the position.
- Keep the `# / name / token / content` table in the contract and a count test: the number of
  `.Run()` arguments in the app must equal the number of trigger parameters.
- Changing the order of a flow in use requires updating **all** the calls in the same deploy; without
  that, the values shift with no error.

## 5. The call as seen from the app

So the flow author knows what the app sends (this call belongs to `powerapps-canvas`):

```text
// formula bar (en-US: , and ;)
IfError(Set(varRet, 'flow-gravar'.Run("gravar", Text(varSel.id, "[$-en-US]0"), txtDescricao.Text, varSel.Unidade)), Set(varRet, Blank()))
```

Destination: the Studio formula bar in an en-US locale (e.g. the button's `OnSelect`). The numeric id
goes with `Text(id, "[$-en-US]0")`: without a format, a pt-BR locale generates `"1.234"` and the flow receives the dot
(C4). The call stays inside `IfError` in the app (C3). The unit to write comes from the **record**
(`varSel.Unidade`), not from a global variable.

## 6. Long operation

If the operation can exceed the synchronous response time limit, do not hold the `Response`
(the exact limit of the Power Apps trigger is `[unverified]` here; confirm in the environment).
**Asynchronous job** pattern [verified: reference project]:

1. The app generates a correlation GUID and sends it as a parameter.
2. The flow creates a status row (`jobId`, `codstatus`: processing / success / partial / failure,
   count of items with success and with error, notes) and responds `success` with `id` = jobId.
3. The app polls the row with backoff and a **stop condition**, and shows the toast
   according to the final state.

The `dataverse` skill decides the status table; the polling in the app belongs to `powerapps-canvas`.

## 7. Contract document

One document per flow, **generated from the artifact whenever possible** (a hand-written document
gets stale the next day). Template: [assets/flow-contract-template.md](../assets/flow-contract-template.md).
When it diverges from the flow, the contract is the bug.

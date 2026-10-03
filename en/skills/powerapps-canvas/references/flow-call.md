# Calling a flow from the app side

The button that writes: loading, `IfError(.Run(...))`, toast, `If(status <> "error", close the modal,
Refresh, recount)` (YAML). The **flow side** (skeleton, per-action authorization, `Try/Catch`, `Response`,
log) belongs to the `power-automate` skill; the procedure, to `sql-procedures`. Here is only what the screen does.

## Contents

1. [The contract](#1-the-contract)
2. [The button skeleton](#2-the-button-skeleton)
3. [Why each step](#3-why-each-step)
4. [Parameters](#4-parameters)
5. [Batch and long operation](#5-batch-and-long-operation)
6. [What never to do](#6-what-never-to-do)
7. [Button review checklist](#7-button-review-checklist)
8. [Sources](#8-sources)

---

## 1. The contract

Decisions C1 to C5 of [default-decisions.md](../../power-platform/references/default-decisions.md):

- Flow response: **`{ status, description, id, url }`**, all text. `status` is `success`,
  `warning` or `error`. `description` is the sentence ready for the user (built in the flow, the
  procedure returns only a code). The flow's `Response` needs a **JSON schema**; without it the app
  does not know the fields and `varRet.status` does not compile.
- Success is **`status <> "error"`**: `warning` (partial success) also closes the modal.
- Every `.Run()` call goes inside `IfError`. A call without `IfError` is the most common gap in
  a real app: if the transport fails (timeout, 401, flow turned off), the
  result is undefined and, without handling, a blank `status` would pass the `<> "error"` test
  as success. `[unverified: exact behavior of .Run() on timeout or HTTP error; confirm
  in the Monitor]`
- Power Apps (V2) trigger parameters are **positional and text**; a new parameter goes
  **always at the end**.
- After writing: `Refresh(source)` and recount the screen's counters.
- The screen **does not authorize**: the flow revalidates the caller's permission and scope. What the
  screen does with the role flag (`Visible`, `DisplayMode`) is UX
  ([scope-and-permission.md](scope-and-permission.md)).

## 2. The button skeleton

Confirmation button of a modal. The `OnSelect` is in the dialect of pasted YAML (`,` and `;`). The
full block, with the surrounding modal, is in [screen-template.md](../assets/screen-template.md).

Destination: pasted YAML (`,` and `;`).

```yaml
# xx-mod-confirmar-btn-confirmar
DisplayMode: =If(varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
Text: =If(varShowLoading, fxTxtProcessando, fxTxtEncerrar)
OnSelect: |-
  =Set(varShowLoading, true);
  Set(varLoadingMessage, "Closing...");
  IfError(
    Set(
      varRet,
      'app-flow-pedido-acao'.Run(
        "encerrar",
        Text(varPedidoSel.Id_Pedido, "[$-en-US]0")
      )
    ),
    Trace("Flow transport failure: " & FirstError.Message);
    Set(varRet, Blank())
  );
  Set(varShowLoading, false);
  Set(varToastType, Coalesce(varRet.status, "error"));
  Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
  Set(varShowToast, true);
  If(
    varToastType <> "error",
    Set(varMostrarConfirmar, false);
    Set(varPedidoSel, Blank());
    Refresh(Pedido);
    Set(
      varPedidoTotal,
      CountRows(Filter(Pedido, StartsWith(Unidade, varUnidadeFiltro)))
    )
  )
```

The same sequence in four beats:

1. **Prepare**: turn the loading on (`varShowLoading`, `varLoadingMessage`).
2. **Call inside `IfError`**: a transport failure resets `varRet`.
3. **Close the loading on every path** and **translate** the result into `varToastType` and
   `varToastMessage`. `Coalesce(varRet.status, "error")` treats a blank response as an error;
   `Coalesce(varRet.description, fxMsgFalhaFlow)` gives a message even with no response.
4. **If it is not an error**: close the modal, clear the selection, `Refresh` and recount.

## 3. Why each step

| Step | Reason |
|---|---|
| `Set(varShowLoading, true)` before everything | `.Run()` is synchronous and blocking; without an overlay the user clicks again and writes twice |
| button `DisplayMode` and `Text` bound to `varShowLoading` | prevents a double click and gives feedback on the button itself; applies to **every** button that calls a flow |
| `IfError(Set(varRet, ...Run(...)), ...)` | separates **transport failure** from **business failure**; the second arrives through `status` |
| `Set(varRet, Blank())` in the error branch | avoids reusing the **stale** return of the previous call |
| `Set(varShowLoading, false)` outside the `If` | the overlay closes on every path; a stuck overlay is the most common support ticket |
| `Coalesce(varRet.status, "error")` | `Blank() <> "error"` is true and would close the modal as success |
| toast for a flow return | `Notify()` is kept for form validation; a flow return is a toast |
| `Refresh(source)` after writing | the app caches the query; without `Refresh` the gallery shows the old state |
| recount of the counters | a counter set only in `OnStart` freezes and drifts from the gallery all day |
| `Trace(...)` | the transport failure shows up in the Monitor with the error text |

The outcome has **three** states in the toast (`success`, `warning`, `error`), in color and
title tokens (`fxTxtToast*`). `warning` is a batch with partial success and **closes** the modal: do not
paint partial success red. Toast block in [ux-feedback.md](ux-feedback.md).

## 4. Parameters

- **All text, in the trigger's order.** The first parameter is the action; the business ones follow the trigger's order;
  a new parameter goes at the end (C4). Identity never travels as a parameter — the flow reads it from the context.
  A parameter that does not apply goes as `""`.
- **Numeric id: `Text(id, "[$-en-US]0")`.** `Text(1234)` in a pt-BR locale is `"1.234"` and the flow does not find the
  row: edit and close failed for every id from 1,000 up, and closing was irreversible.
  `[verified: reference project]`
- **Date**: `yyyy-mm-dd` text (or ISO 8601), never a raw date.
- **Foreign key** goes as the id (`Text(Selected.Id_Categoria, "[$-en-US]0")`), not the
  display name; changing the meaning of a parameter **without changing its position** requires updating the
  contract (`CONTRATOS`, `power-automate` skill) in the same commit.
- **The write unit is a field of the record**, not global state: on create it comes from the
  form control; on edit and close, from the record itself (`varPedidoSel.Unidade`). See
  [scope-and-permission.md](scope-and-permission.md).
- **Identity**: the app does **not** send an e-mail or identity; the flow gets the caller from the context
  (`Office 365 Users — MyProfile_V2`) and revalidates the permission per action.
- **A named constant** (`fxCodigo...`) in place of a magic number (`12`, `-300`) in `.Run(...)`.
- **Flow name** `<app>-flow-<entity>-<verb>` and **one** return variable per app
  (`varRet`), declared in `OnStart`. Two variables (`varRet`, `varRetg`) for the same thing only
  breed doubt.

## 5. Batch and long operation

**Batch.** Send the whole collection as JSON in a **single** call, not `.Run()` inside
`ForAll` (N calls, N × ~0.6 s just in instantiation):

Destination: pasted YAML (`,` and `;`).

```yaml
# xx-mod-lote-btn-confirmar
OnSelect: |-
  =Set(varShowLoading, true);
  IfError(
    Set(
      varRet,
      'app-flow-pedido-lote'.Run(
        "encerrar",
        JSON(
          ForAll(colSelecionados, { id: Text(ThisRecord.Id_Pedido, "[$-en-US]0") }),
          JSONFormat.Compact
        )
      )
    ),
    Set(varRet, Blank())
  );
  Set(varShowLoading, false);
  Set(varToastType, Coalesce(varRet.status, "error"));
  Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
  Set(varShowToast, true)
```

The flow returns `status: "warning"` with an aggregated `description` ("12 closed, 3 with errors") and the app
shows **one** toast. `colSelecionados` comes from a per-row `Collect` (checkbox), not from
`Filter(gal.AllItems, ...)`: `AllItems` only sees what has already loaded.

**Long operation** (above the connector timeout, usually ~120 s
`[unverified: confirm the limit in your environment]`): the flow answers "accepted" and records
progress in a table; the app polls with backoff and a cap
([timers-async.md](timers-async.md) §6). State in the contract whether the response is **synchronous**
(processed) or **accepted** (processing); with accepted, the screen needs a status query.

## 6. What never to do

- `.Run()` in a gallery's `Items`, in `Visible` or in any UI property.
- `.Run()` without `IfError` (validator: T018).
- `Text(<id>)` without `[$-en-US]0` in a parameter or JSON.
- `If(status = "200", ...)`: the contract is `success`, `warning`, `error`; `"200"` as text is
  a fragile dependency.
- Automatic retry of an operation that writes, without an idempotency key.
- `Notify()` for a flow return.
- Closing the loading only in the success branch.
- Trusting `DisplayMode` or the screen to prevent duplicates or self-action: the duplicate guard goes
  **inside the transaction**, on the server (read-then-write on the screen loses the race).
- Validating permission only on the screen. The screen hides; the flow denies.

## 7. Button review checklist

- [ ] `varShowLoading` turns on before and off on every path; button disabled and showing
      "Processing...".
- [ ] `.Run()` inside `IfError`; `varRet` reset in the failure branch.
- [ ] Blank `status` treated as an error; success by `<> "error"`.
- [ ] Toast with the 3 types; no `Notify()` for a flow return.
- [ ] Ids with `[$-en-US]0`; dates as text; a new parameter only at the end.
- [ ] `Refresh(source)` and recount on success; the modal closes only if it is not an error.
- [ ] No permission decided on the screen alone; the write unit comes from the record.
- [ ] Tested with the flow **turned off** (red toast, overlay closes) and with partial success.

## 8. Sources

- [Run a flow from Power Apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/using-logic-flows)
- [Error, IfError](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-iferror)
- [Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)

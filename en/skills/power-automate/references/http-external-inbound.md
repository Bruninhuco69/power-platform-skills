# Inbound from an external system (HTTP trigger)

Decision C6 of [default-decisions.md](../../power-platform/references/default-decisions.md): an
external system enters through its own **Request (HTTP)** trigger, **separate** from the flows
called by the app (Power Apps V2). The contract is different: HTTP code + `{code, message}`, not the
4-field one. Origin: the "cached token + response by the real status" inbound pattern of a
reference project; its defects became the rules below
([field-lessons.md](field-lessons.md)).

## Contents

1. [External contract](#1-external-contract)
2. [Skeleton](#2-skeleton)
3. [Credential](#3-credential)
4. [Response by the real status](#4-response-by-the-real-status)
5. [Synchronous or accept](#5-synchronous-or-accept)
6. [N=1 x batch](#6-n1-x-batch)
7. [Validation with cache](#7-validation-with-cache)

---

## 1. External contract

| Situation | `statusCode` | Body |
|---|---|---|
| Processed | 200 | `{"code": "Success", "message": "Received successfully."}` |
| Accepted to process later | 202 | `{"code": "Accepted", "message": "...", "runId": "<workflow().run.name>"}` |
| Credential missing or invalid | 401 | `{"error": {"code": "TokenInvalido", "message": "The token sent is not valid."}}` |
| Invalid body | 400 | `{"error": {"code": "PayloadInvalido", "message": "..."}}` |
| Write failure (synchronous mode) | 500 | `{"error": {"code": "FalhaAoGravar", "message": "..."}}` |

The envelope has two shapes, by design: **success** (200/202) is a flat `{code, message}`; **error**
(4xx/5xx) is `{"error": {code, message}}`. The caller tells them apart by `statusCode` and, in the
body, by the presence of the `error` key.

Publish the table to the calling system. Input body: `{ "dados": [ ... ] }` (a list of records
from the source system).

## 2. Skeleton

```
Request (HTTP) trigger   POST method; body schema
Escopo_Principal
  Valida_credencial      Compose: does the header match? (see §3 and §7)
  Se_credencial_ok       If
    Yes: normalize (mapping Select) -> write (see dataverse-batch-upsert.md) -> Response 200
    No: Response 401 + Terminate
Log                      scope outside the main one (run-log.md)
```

Two items of the skeleton come from the reference project: the 1:1 mapping in a single `Select`
(logical name on the left, value on the right; the **only copy** of the mapping) and the log as a
sibling scope that reads `result('Escopo_Principal')`.

## 3. Credential

- **`Authorization` header**, never in the body. The reference project received the token in
  `triggerBody()['headers']['token']` (inside the body): it shows up in payload logs and in
  `inputpayloadsize`/the JSON sent.
- Read it from the header with `triggerOutputs()?['headers']?['Authorization']`
  `[unverified: confirm the exact property name in the run history of your environment]`.
- **Never store the token in clear text** in a cache table, a log or a visible `Compose` (turn on
  "Secure inputs/outputs" on the action that reads it).
- Prefer validating against a **secret** kept as a Secret-type environment variable or in Key Vault
  over keeping a copy of the token in a table `[unverified: behavior of a secret variable in a
  flow; confirm in the Learn page on environment variables]`.
- The HTTP trigger accepts Power Automate's own authentication (per tenant user)
  `[unverified]`; when it is not used, credential validation is **yours**.

## 4. Response by the real status

The costliest defect of the reference project: the `Condition` compared **constants**
(`equals(200, 200)`), the invalid-token branch was dead code and the flow answered 200 even when
the token validation failed (because the `Response` ran after `Succeeded, Failed, Skipped,
TimedOut`). The verifier flags a constant condition (F016) and an early HTTP `Response` (F015,
warning).

Rules:

1. **The HTTP code is derived from the real result of the validation**, never from a constant.
2. `Response` 200 with `runAfter` only on `Succeeded` of the validation; `Response` 401 on
   `Failed`/`TimedOut` (or the `else` branch of an `If` whose condition is the result of the check).
3. A rejection test is **mandatory**: call with a wrong token and with a missing token and check
   the 401.
4. An HTTP `Response` also **does not end** the flow: the same rule as the `Terminate` in
   [flow-anatomy.md](flow-anatomy.md) applies to the 401 branch.

## 5. Synchronous or accept

State in the contract which of the two the flow is:

| Mode | When | Cost |
|---|---|---|
| **Synchronous** (responds after writing) | Small batches; the caller needs to know about the error | The caller waits; response time limit of the trigger `[unverified: value]` |
| **Accept** (200/202 before writing) | Large batches; the caller cannot wait | The caller **never** learns of a write error |

The reference project answered 200 before processing **without declaring** that it was an accept:
only the log knew about the failure. If it is an accept: (a) answer **202** with `runId`, (b)
expose a status query or notify, (c) the `Log` marks the run as `Failed` when something broke
([run-log.md](run-log.md)).

## 6. N=1 x batch

| Size | Path |
|---|---|
| N = 1 | Lookup by exact key (`$top 1`) -> `PATCH` by id (`If-Match: *`: update only) or `POST` |
| N > 1 | Index {key -> id} of the target table + split those that exist from those that do not + `$batch` in parts ([dataverse-batch-upsert.md](dataverse-batch-upsert.md)) |

The single-record branch avoids reading the whole table to write one row. [verified: reference
project]

## 7. Validation with cache

Validating the credential on every call against an external service costs time and quota. Pattern
of the reference project, in a reusable scope pasted as the **first action inside the main scope**
(not at the root: the `Log` reads `result('Escopo_Principal')` and has to see the credential
failure there):

1. Reads the source's cache row (token + `modifiedon`).
2. If there is no token, or it differs from the cache, or `modifiedon` is 1 h old or more: validates
   for real and rewrites the cache.
3. Scope status: `Succeeded` = accepted; `Failed` = refused. `Response` 200 on `Succeeded`, 401 on
   `Failed`/`TimedOut`.
4. A failure to **write the cache** must not bring down the inbound call: an absorption action on
   `runAfter [Failed, TimedOut]` of `Criar_cache`, **without** `Skipped` (otherwise it masks the
   validation failure). Document this in the action's description.
5. Actions independent of the credential (mapping) **without** `runAfter`, so they run in parallel.
6. **Do not use an environment variable as a cache**: the value is frozen until the flow is saved or
   turned back on
   ([Learn: limitations](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables-power-automate#limitations)).

Improvements the reference project did not make: a **generic** cache table per source (the `name`
key already exists), the table name in an environment variable, and not storing the token in clear
(hash: see the caveat in [wdl-expression-pitfalls.md](wdl-expression-pitfalls.md) §9).

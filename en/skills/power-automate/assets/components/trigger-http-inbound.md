# Inbound HTTP trigger: body, variables and flow root

> **File**: `trigger-http-inbound.md` (descriptive: no pasteable JSON) · **Frequency**: occasional · **Maturity**: stable
> **Depends on**: none

## Purpose

Declares the external-system entry point: its own **Request (HTTP)** trigger, separate from the flows the app calls (C6),
with an HTTP status code + `{code, message}` contract instead of the 4 fields.

## When to use / when not to use

- Use to receive a batch from an external system.
- Do not use for a screen action: `trigger-power-apps-v2`.

## Where to paste

It is not pasted. Create the flow, choose the trigger **When an HTTP request is received** (Request), method `POST`, and
paste the body schema. After the trigger, create the two variables **by hand, at the root** (`Initialize variable` only works at the
root) and paste `token-cache-and-http-response` with `runAfter` on the second variable.

## Inputs and outputs

- Input: body `{ "dados": [ ... ] }` (list of records from the source system); credential in the `Authorization` header.
- Trigger output: `triggerBody()`, `triggerOutputs()?['headers']`.
- Response: `Response` with `kind: Http` (200, 202, 400, 401, 500).

## Body schema ("Request Body JSON Schema" field)

```text
{
  "type": "object",
  "properties": {
    "dados": { "type": "array", "items": { "type": "object" } }
  },
  "required": ["dados"]
}
```

Destination: schema field of the HTTP trigger. Validate the format of each item later, in `map-batch`.

## Flow root

```text
Trigger Request (HTTP)               POST; schema above
Inicializar_erros_lote               Initialize variable  Erros_lote           string   (empty)
Inicializar_linhas_com_erro          Initialize variable  Linhas_com_erro      integer  0
Escopo_Principal                     token-cache-and-http-response
  CONFIG                             inbound-config
  Scope_Token ... Resposta_sucesso / Resposta_token_invalido
  (hanging from Resposta_sucesso) map-batch, single-upsert, target-key-index, batch-upsert-changeset
Log                                  run-log (sibling of the main scope)
```

## Response contract

| Situation | `statusCode` | Body |
|---|---|---|
| Processed | 200 | `{"code": "Success", "message": "Received successfully."}` |
| Accepted for later processing | 202 | `{"code": "Accepted", "message": "...", "runId": "<workflow().run.name>"}` |
| Missing or invalid credential | 401 | `{"error": {"code": "TokenInvalido", "message": "The token sent is not valid."}}` |
| Invalid body | 400 | `{"error": {"code": "PayloadInvalido", "message": "..."}}` |
| Write failure (synchronous mode) | 500 | `{"error": {"code": "FalhaAoGravar", "message": "..."}}` |

Success is a flat `{code, message}`; error is `{"error": {code, message}}`. The caller tells them apart by `statusCode`.

## Parameters to change

| Item | Value | Change to |
|---|---|---|
| method | `POST` | what the caller uses |
| body schema | `dados` | the contract published to the calling system |
| variable names | `Erros_lote`, `Linhas_com_erro` | keep: `batch-upsert-changeset` and `run-log` reference them |

## runAfter

The first `Initialize variable` depends on the trigger. `Escopo_Principal` depends on `Inicializar_linhas_com_erro`.

## Pitfalls

- **Synchronous or accepted**: answering 200 before writing, without saying so, hides write failures: only the log knows. If it is accept-only, answer **202** with `runId`, offer a status lookup and let the `Log` mark the run as `Failed`.
- Credential in the **header**, never in the body (the body shows up in payload logs). The reference project received the token in the body.
- Who can fire the HTTP trigger and the generated URL: `[unverified: confirm the trigger's access options in your environment]`; credential validation is **yours**.
- The trigger URL is a secret: do not put it in a document, ticket or code.
- Publish the response table and the body format to the calling system.

## Variations

- Accept mode: `Resposta_sucesso` with 202 and `runId`.
- Body with a batch header (`{ "lote": "...", "dados": [...] }`): adjust the schema and `Mapear_lote`.

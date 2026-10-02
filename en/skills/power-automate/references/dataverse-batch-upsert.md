# Dataverse: `$batch`, upsert and pagination

Writing a batch to Dataverse from a flow. Structure inherited from a reference inbound flow
(the community "Dataverse Batch Upsert" pattern) with the fixes it did not make
([field-lessons.md](field-lessons.md)). Tables, alternate keys and Security
Roles belong to the `dataverse` skill.

## Contents

1. [When to use `$batch`](#1-when-to-use-batch)
2. [Platform facts](#2-platform-facts)
3. [Upsert: alternate key or index](#3-upsert-alternate-key-or-index)
4. [Building the batch](#4-building-the-batch)
5. [Handling per part](#5-handling-per-part)
6. [429 and 5xx errors](#6-429-and-5xx-errors)
7. [Pagination of the read](#7-pagination-of-the-read)
8. [Atomicity](#8-atomicity)

---

## 1. When to use `$batch`

- **N = 1 or a few**: the connector's `Add/Update row` action, per row. `$batch` complicates things with no gain.
- **Batch**: `$batch` reduces calls, but costs execution time in the API (see §2): start with
  small parts and increase.
- A write with a business rule called from the **screen** does not belong here: that is the design in
  [flow-anatomy.md](flow-anatomy.md). This file is for **receiving a batch** (integration).

## 2. Platform facts

Source: [Learn: batch](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/execute-batch-operations-using-web-api)
and [Learn: protection limits](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/api-limits).

| Fact | Value |
|---|---|
| Requests per `$batch` | up to 1,000; does not nest another batch |
| Order | executed in sequence, in the order sent |
| Changeset | **atomic**: if one fails, the completed ones are rolled back; `GET` cannot go in a changeset |
| Error in a part, with no preference | the batch **stops** at the first failure and returns its error |
| `Prefer: odata.continue-on-error` | processes the rest; a 200 response with the errors **inside** the body |
| Line break in the body | **CRLF** required; other breaks can cause a deserialization error |
| Boundary | only parts whose identifier matches the one in the header execute |
| `Content-ID` | references an entity created earlier in the same changeset (`$1`); a reference to an id not yet seen = 400 |
| Service protection (per user, per server) | 6,000 requests/5 min; 20 min of execution time/5 min; 52 concurrent (default values, they vary) |
| Excess | **429** with `Retry-After` in seconds |
| Advice | Start with small batches (for example 10) and raise concurrency until a 429 appears `[unverified: official citation]` |

## 3. Upsert: alternate key or index

Two ways to decide between create and update:

| Way | When | Note |
|---|---|---|
| **Alternate key** in the `PATCH` URL (`<set>(<key>='x')`) | The table has an active alternate key for the business key | One `PATCH` per row, without reading the table. Syntax and key composition: `[unverified: confirm the "Use alternate keys" page on Learn]` |
| **{key -> id} index** built from a read of the destination table | No alternate key | It is the reference flow's design (below): reads the keys, separates whoever **has** an id (update) from whoever **does not** (create) |

`PATCH` conditionals with an id ([Learn: conditional operations](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/perform-conditional-operations-using-web-api)):
`If-Match: *` prevents **creating** (404 if it does not exist: update only); `If-None-Match: *` prevents
**updating** (412 if it already exists: create only).

Index by the **concatenated composite key** (`numero & unidade & data`), with the same
format on both sides. Watch the date: the index and the row must concatenate the **same**
text (suffix `Z` included), otherwise no row finds the id and everything becomes a duplicate `create`.
[verified: reference project]

## 4. Building the batch

Parameters in a `Compose` (`settings`), with the table name from an **environment variable**, not a
DEV literal (decision F5):

```json
{
  "settings": {
    "type": "Compose",
    "description": "EntitySetName is the set name (plural), not the logical name. BatchSize maximum 1000; start small.",
    "inputs": {
      "EntitySetName": "<prefixo>_tabelasdestino",
      "BatchSize": 50,
      "KeyColumns": ["<prefixo>_numero", "<prefixo>_unidade", "<prefixo>_data"]
    },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000010" }
  }
}
```

Destination: an action of the main scope; `settings` is this flow's `CONFIG`. The verifier **warns**
(F014) about an environment literal outside an action named `CONFIG`: name it that or handle the warning.

Flow: `Mapear_lote` (mapping Select) -> index -> split -> `chunk()` ->
`Select` applying the template -> `SendBatch`.

```text
Partes   = @chunk(body('Select_ComId'), outputs('settings')?['BatchSize'])
Corpo    = @concat('--batch_', variables('lote'), decodeUriComponent('%0D%0A'), 'Content-Type: multipart/mixed; boundary=changeset_', variables('cs'), decodeUriComponent('%0D%0A%0D%0A'), join(body('Select_Partes'), decodeUriComponent('%0D%0A')), decodeUriComponent('%0D%0A'), '--changeset_', variables('cs'), '--', decodeUriComponent('%0D%0A'), '--batch_', variables('lote'), '--', decodeUriComponent('%0D%0A'))
```

Destination: `chunk()` in the `foreach` field of a `Foreach`; `Corpo` in `request/body` of the HTTP action
(`InvokeHttp`). POST headers: `OData-MaxVersion: 4.0`, `OData-Version: 4.0`,
`Accept: application/json`, `Content-Type: multipart/mixed; boundary=batch_<id>`, and **each part
carries its own `Content-Type: application/http` and `Content-Transfer-Encoding: binary`**
(the `$batch` headers do not apply to each part).

Note: the reference flow builds the body with `\n` (LF) and Learn requires **CRLF**; I did not
verify its execution. Use `decodeUriComponent('%0D%0A')` as above and test with a 2-row batch
before raising the volume. `[unverified: execution with LF or CRLF in the flow]`.

## 5. Handling per part

The reference flow detected an error by **substring** (`contains(texto, '400 Bad Request')`...) and
left out 500, 503, 504 and 429. Read the **status of each part**:

In actions, `Statuses` is a `Select` with `from` = `@skip(split(base64ToString(body('SendBatch')['$content']), 'HTTP/1.1 '), 1)` and
`select` = `@int(substring(item(), 0, 3))`; then `Query` (Filter array) with `from` =
`@body('Statuses')` and `where` = `@greaterOrEquals(item(), 400)`. Batch failure =
`@greater(length(body('Falhas')), 0)`. The response body comes in `$content` in base64
(usage verified in the reference flow). `[unverified: the split by 'HTTP/1.1 ' on a real
response]`; validate on a batch with one deliberately invalid row.

- With `odata.continue-on-error` the good parts write and the bad ones show up in `Falhas`.
- Without it, the first failure stops the batch: return `warning`/partial failure and **count** the rows
  that were not processed.
- Count **rows**, not parts: the reference flow incremented by chunk size
  (pessimistic).

## 6. 429 and 5xx errors

- Too many requests: **429** with `Retry-After`
  ([Learn](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/api-limits)).
- The HTTP action has a default retry policy: exponential, up to 4 attempts, for 408, 429 and
  5xx ([Learn](https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling)).
  For Power Automate's `InvokeHttp` connector, how the policy appears in the designer JSON is `[unverified]`.
- Even with retry, **limit the concurrency** of the sending `Foreach` (the reference flow
  used 10) and raise it gradually.

## 7. Pagination of the read

Reading the destination table to build the index is the expensive part. Two options:

| Option | Note |
|---|---|
| **Native pagination** of the `List rows` action (Settings -> Pagination, limit) | A single action, no `Do_until` or skiptoken variable. The reference flow used a limit of 100,000 (`paginationPolicy.minimumItemCount`) [verified: reference project] |
| `Do_until` + `@odata.nextLink`/manual skiptoken | More actions, more points of failure; only if native pagination does not fit |

**Reduce the read**: filter by the batch's range (`min`/`max` of the keys, computed with
`first(sort(...))`/`last(sort(...))` in a single `Compose`), instead of reading the whole table.

## 8. Atomicity

A changeset of 800 rows **rolls back all 800** if one fails. Choose consciously:

| Design | When |
|---|---|
| Changeset per part (all-or-nothing per part) | The part is a business unit (e.g. a document with its lines) |
| No changeset + `continue-on-error` | Independent rows; an error in one row must not bring down the others |

For screen-to-table writes with a business rule and compensation, see
[flow-anatomy.md](flow-anatomy.md): Dataverse gives no transaction to an ordinary flow (each
`Add a new row` is a commit); compensate in **reverse order** in the `Catch`, or use a changeset.

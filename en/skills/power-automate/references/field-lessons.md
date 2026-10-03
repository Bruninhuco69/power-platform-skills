# Field lessons: flows

Defects and decisions that showed up in real flows and did not yet fit an isolated rule in the
other references. Each lesson gives what happened, in generic terms, and the rule or file that
prevents it. It is not a rule by itself: what counts is in the files cited.

## Contents

1. [A "nothing changed" condition that is never true](#1-a-nothing-changed-condition-that-is-never-true)
2. [The flow has no permission: the human request is a legitimate design](#2-the-flow-has-no-permission-the-human-request-is-a-legitimate-design)
3. [File generation in the flow has a ceiling](#3-file-generation-in-the-flow-has-a-ceiling)
4. [A product decision with an accepted consequence gets written down](#4-a-product-decision-with-an-accepted-consequence-gets-written-down)
5. [An integer domain constant comes from capturing the environment](#5-an-integer-domain-constant-comes-from-capturing-the-environment)
6. [Verify a pasted snippet, not the whole flow](#6-verify-a-pasted-snippet-not-the-whole-flow)
7. [Defects of an inbound flow that the usual design does not prevent](#7-defects-of-an-inbound-flow-that-the-usual-design-does-not-prevent)

---

## 1. A "nothing changed" condition that is never true

| | |
|---|---|
| **What happened** | An edit with "no changes" was never detected: the list of audit-trail rows had an unconditional item, so `length(list) = 0` never occurred and the "nothing changed" branch was dead code. Fixing the `If` was not enough: the error was in how the list was built. |
| **Prevented by** | `wdl-expression-pitfalls.md` §7 (empty lists and index) and `verificar-fluxo.py` F016 (constant condition). When reviewing a condition, review **what it tests**, not just the `If`: build the list with only the conditional items. |

## 2. The flow has no permission: the human request is a legitimate design

| | |
|---|---|
| **What happened** | An access provisioning flow (grant and revoke) had no permission to write to the tenant directory group. The design adopted was to send the request by e-mail to support, who makes the change, instead of forcing a broad permission on the connector account. |
| **Prevented by** | `authorization-in-flow.md` (the flow refuses what the caller cannot do) and `default-decisions.md` A2/A3. The flow records the request in the log and answers `warning` ("request sent"), never `success` as if the effect had already happened. |

## 3. File generation in the flow has a ceiling

| | |
|---|---|
| **What happened** | An export flow generated CSV and labels with a fixed-width identifier built in pure WDL expressions; the file converter refused HTML above about 2 MB. |
| **Prevented by** | `sql-in-flow.md` §5 (connector limits: 8 MB response and 2 MB request behind a gateway): a large export needs pagination or partitioning into smaller files, and the count procedure runs **before** the export to decide. |

## 4. A product decision with an accepted consequence gets written down

| | |
|---|---|
| **What happened** | The "all units" scope collapsed into a single role flag and started to apply **also to writes**. The decision was recorded with the accepted consequence: whoever has the flag closes in any unit (the action's permission flag still applies). The role came to have more than a dozen per-action permission flags. |
| **Prevented by** | `authorization-in-flow.md` §3 and §4: scope and permission are different things (*what* x *where*); what is accepted as lost goes into the project's ADR, so nobody "fixes" it later without knowing it was deliberate. |

## 5. An integer domain constant comes from capturing the environment

| | |
|---|---|
| **What happened** | The integers of the audit-trail event types were guesses until the environment was captured; so were the real procedure names (only a fraction was confirmed when the baseline was closed). |
| **Prevented by** | `designer-baseline.md` R9 and `sql-procedures/references/deploy-and-dba.md` §7: names and constants come from the environment (`sys.procedures`, a dated extract), and what was not read is marked as a hypothesis. |

## 6. Verify a pasted snippet, not the whole flow

| | |
|---|---|
| **What happened** | Run read-only over the delivery files of an inbound flow (one `.md` per clipboard scope node, one-line JSON), the verifier flagged 1 error (F016, the constant `Condition`) in the old version and **0 errors** in the new one, with the expected warnings (F014 DEV table, F015 early `Response`, F018). The reusable validation scope came out clean; the `Log` scope got F009 (no `Skipped`, intentional: F4) and F006 (reference to `Escopo_Principal`, which is outside the snippet). The initialization of the errors variable was not in the delivered file, and the initial value was assumed. |
| **Prevented by** | `clipboard-format.md` (F006 becomes a warning for an action outside the snippet) and `default-decisions.md` F4. Before trusting the result, have the inventory of the whole flow: the snippet does not carry the trunk's initialization. |

## 7. Defects of an inbound flow that the usual design does not prevent

| | |
|---|---|
| **What happened** | In an HTTP inbound flow with `$batch`, even after a rewrite, these remained: the DEV table name fixed in the configuration, in the single-record lookup and in the paginated read; the token in the body and in clear in the cache table; the 200 returned before processing; the `$batch` error detected by substring (`'400 Bad Request'`), without handling 500/503/504/429; the failure count by chunk rows, not by part (pessimistic failure); the `$batch` body built with `\n` when the documentation requires CRLF; the log status only 0/1, with fixed flow type and retries; a read filter with sentinels (`or ... eq 99`) so the filter is never empty. |
| **Prevented by** | `default-decisions.md` F5, `http-external-inbound.md` §3 and §5, `dataverse-batch-upsert.md` §4 and §5, `run-log.md` §1. The verifier flags F014 (environment literal) and F015 (early `Response`). When a flow is born from a community template, rewrite the list above as a review checklist. |

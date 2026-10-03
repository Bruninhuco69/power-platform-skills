# Run log

Decision F4 of [default-decisions.md](../../power-platform/references/default-decisions.md): every
flow has a `Log` scope. The `Catch` only returns "the system did not respond"; without a log,
nobody knows which action broke, for whom, or how long it took. Pattern inherited from a reference
inbound flow ([field-lessons.md](field-lessons.md)).

## Contents

1. [Parent/child model](#1-parentchild-model)
2. [The Log scope](#2-the-log-scope)
3. [Failing the run after logging](#3-failing-the-run-after-logging)
4. [Tension with Response + Terminate](#4-tension-with-response--terminate)
5. [Where to write when the data is in SQL](#5-where-to-write-when-the-data-is-in-sql)
6. [Correlation with support](#6-correlation-with-support)

---

## 1. Parent/child model

| Table | One row per | Columns |
|---|---|---|
| **Monitored flow** (parent) | flow | `flowid` (`workflow()['name']`), `flowdisplayname`, `lastrunstatus`, `lastruntime`, `totalruns`, `totalfailedruns`, `consecutivefailures`, `isactive` |
| **Run** (child) | run | `runidentifier` (`workflow()['run']['name']`), `flowidentifier`, `starttime`, `endtime`, `durationseconds`, `runstatus`, `triggername`, `rowsreceived`, `rowsprocessed`, `rowsfailed`, `inputpayloadsize`, `errorcode` (**name of the action** that failed), `errormessage` |

- `errorcode` holds the action name, not a code: whoever consumes it (report, Power BI) treats it as
  "action with an error".
- **Never** write a token, password or the raw body to the log. `inputpayloadsize` yes; the JSON
  sent only without credentials.
- Standardize which columns **every** flow fills in; old flows filling different columns leave the
  HTTP error report null for the new ones.
- The tables belong to the `dataverse` skill; `<prefixo>_...` names of the environment.

## 2. The Log scope

A **sibling** scope of the main one (outside it), `runAfter` on `Succeeded`, `Failed` and
`TimedOut`:

```json
{
  "nodeId": "Log",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Filter_FailedActions": {
        "type": "Query",
        "description": "First-level actions of Escopo_Principal with status Failed. result() only accepts Scope/Foreach/Until, not If.",
        "inputs": {
          "from": "@result('Escopo_Principal')",
          "where": "@equals(item()?['status'], 'Failed')"
        },
        "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000011" }
      },
      "Compose_Log": {
        "type": "Compose",
        "description": "One Compose in place of one variable per field. Expressions safe with an empty list and null (if() evaluates both branches).",
        "inputs": {
          "RunId": "@workflow()?['run']?['name']",
          "StartTime": "@trigger()?['startTime']",
          "EndTime": "@utcNow()",
          "DurationSeconds": "@div(sub(ticks(utcNow()), ticks(trigger()?['startTime'])), 10000000)",
          "Status": "@if(empty(body('Filter_FailedActions')), 0, 1)",
          "FailedAction": "@if(empty(body('Filter_FailedActions')), null, last(body('Filter_FailedActions'))?['name'])",
          "ErrorMessage": "@if(empty(body('Filter_FailedActions')), null, take(string(last(body('Filter_FailedActions'))?['error']?['message']), 4000))",
          "PayloadSize": "@length(string(triggerBody()))",
          "TriggerName": "@trigger()?['name']",
          "FlowId": "@workflow()?['name']"
        },
        "runAfter": { "Filter_FailedActions": ["Succeeded"] },
        "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000012" }
      },
      "Add_FlowRun": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_flowruns",
            "item/<prefixo>_runidentifier": "@outputs('Compose_Log')?['RunId']",
            "item/<prefixo>_flowidentifier": "@outputs('Compose_Log')?['FlowId']",
            "item/<prefixo>_starttime": "@outputs('Compose_Log')?['StartTime']",
            "item/<prefixo>_endtime": "@outputs('Compose_Log')?['EndTime']",
            "item/<prefixo>_durationseconds": "@outputs('Compose_Log')?['DurationSeconds']",
            "item/<prefixo>_runstatus": "@outputs('Compose_Log')?['Status']",
            "item/<prefixo>_triggername": "@outputs('Compose_Log')?['TriggerName']",
            "item/<prefixo>_inputpayloadsize": "@outputs('Compose_Log')?['PayloadSize']",
            "item/<prefixo>_errorcode": "@outputs('Compose_Log')?['FailedAction']",
            "item/<prefixo>_errormessage": "@outputs('Compose_Log')?['ErrorMessage']"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "CreateRecord"
          }
        },
        "runAfter": { "Compose_Log": ["Succeeded"] },
        "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000013" }
      }
    },
    "runAfter": { "Escopo_Principal": ["Succeeded", "Failed", "TimedOut"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000014" }
  },
  "allConnectionData": {
    "Add_FlowRun": {
      "connectionReference": {
        "api": { "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps" },
        "connection": { "id": "<prefixo>_shared_commondataserviceforapps" },
        "connectionName": "<prefixo>_shared_commondataserviceforapps"
      },
      "referenceKey": "shared_commondataserviceforapps"
    }
  },
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

Destination: `Ctrl+V` **after** a scope called `Escopo_Principal` (the root's `runAfter` points to
it; adjust to the name of your root scope); reduced version (child only). The parent part (upsert of
the run and consecutive-failure counters) follows the same design with `List`, `If` and
`Update`/`Add`. For a batch inbound flow add `RowsReceived/Processed/Failed`; for a SQL flow, the
rows affected by the procedure.

Points of attention:

- `Escopo_Principal` is the root of the logic; the `Log` has to **see the failure there** (which is
  why the credential validation stays inside the main scope:
  [http-external-inbound.md](http-external-inbound.md)).
- `result()` returns only the **first level**: a failure inside `If`/`Switch` shows up as a failure
  of the first-level action that contains it.
- The verifier gives warning F009 on this scope (no `Skipped`) and F006 (`Escopo_Principal` is
  outside the snippet): expected. `Skipped` is left out on purpose -- with the main scope `Skipped`
  there is no failure to record, and the filter would return status 0.
- The log itself can fail: it must not bring down the response to the caller.

## 3. Failing the run after logging

A flow that handles the error and answers "normally" ends up as `Succeeded` in the Power Automate
history, which hides the failure from whoever monitors through the history. Mark it as a failure
**after** writing the log:

```json
{
  "Falhar_execucao": {
    "type": "If",
    "expression": { "and": [{ "equals": ["@outputs('Compose_Log')?['Status']", 1] }] },
    "actions": {
      "Terminate": {
        "type": "Terminate",
        "inputs": {
          "runStatus": "Failed",
          "runError": { "code": "FluxoFalhou", "message": "@coalesce(outputs('Compose_Log')?['ErrorMessage'], 'Failure without a message')" }
        },
        "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000015" }
      }
    },
    "else": { "actions": {} },
    "runAfter": { "Add_FlowRun": ["Succeeded"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000016" }
  }
}
```

Destination: an action inside the `Log` scope, after `Add_FlowRun`. [verified: reference project]

## 4. Tension with Response + Terminate

The pattern in [flow-anatomy.md](flow-anatomy.md) responds and **terminates** in each `Nega_*`. A
`Terminate` ends the run immediately, so a `Log` scope **after** the main one does not run in those
branches `[unverified: confirm in your environment that the run ends without running the Log]`. In
the HTTP inbound flow (which does not terminate in the branches) the sibling `Log` works as
described. For a flow called by the app there are three ways out, none tested in the reference
projects:

1. **Single response**: each branch only `Compose`s the result and there is one `Response` at the
   end, after the `Log` (loses the `Terminate`; rewrites the anatomy).
2. **Log per branch**: the `Log` scope (or a child log flow) inside the branches that matter
   (`Catch`, write failure), before the `Response`; authorization/validation denials do not log.
3. **Only the `Catch` logs**: denials are a normal response, a connector failure is what support
   wants. It is the minimum viable and the initial recommendation.

Record the choice in a project ADR.

## 5. Where to write when the data is in SQL

**Open** (F4): Dataverse (recommended: it already feeds Power BI) even with data in SQL, or a log
table in SQL itself via a procedure (self-contained, but it requires new DDL and the database tends
to freeze). Decide in the project ADR before writing the first flow.

## 6. Correlation with support

Include `workflow()['run']['name']` in the `description` of **infrastructure error** responses
(`Nega_conector`), for example `concat('... Code: ', workflow()?['run']?['name'])`: the user pastes
the code in the ticket and support finds the run. Do not put the code in business denials (noise).

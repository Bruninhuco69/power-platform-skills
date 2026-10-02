# Anatomy of a flow called by the app

The skeleton that decides the design of any write flow called by a screen (decisions F1–F3
in [default-decisions.md](../../power-platform/references/default-decisions.md)). The pasteable
template that implements all of this is in `assets/flow-write-template.json` and passes
`scripts/verificar-fluxo.py`.

## Contents

1. [The tree](#1-the-tree)
2. [Why each block exists](#2-why-each-block-exists)
3. [Nega and Terminate](#3-nega-and-terminate)
4. [Catch listens for Failed, TimedOut and Skipped](#4-catch-listens-for-failed-timedout-and-skipped)
5. [Switch per action](#5-switch-per-action)
6. [Naming rules](#6-naming-rules)
7. [What stays outside the pasteable scope](#7-what-stays-outside-the-pasteable-scope)

---

## 1. The tree

```
Power Apps trigger (V2)                    typed by hand, not pasteable
Escopo_<flow>                              1 root Scope = 1 paste
  CONFIG                 Compose           environment flags and texts (security flags are born ON)
  Perfil_do_chamador     Office 365 Users  MyProfile_V2: identity comes from the context, never from a parameter
  Chamador               Compose           e-mail/UPN normalized to lowercase
  Try_<flow>             Scope
    Ler_chamador         procedure/query returns role and flags; ZERO rows = deny
    Se_chamador_desconhecido   If -> Nega_chamador + Terminate
    Switch_acao          Switch over toLower(trim(triggerBody()['text']))
      Caso_<acao>
        Autorizar_<acao>   If not(the action's OWN flag) -> Nega_perm_x + Terminate
        Normalizar_x       Compose  (trim, take, toUpper, number as text)
        [Estado_antes_x]   read of the real record, when the scope depends on it
        Validar_x          Compose  if() chain returns the 1st message or ''
        Se_invalido_x      If -> Nega_x + Terminate
        Gravar_x           procedure (see sql-in-flow.md) or Dataverse
        Codigo_x           Compose  code returned by the write
        Responder_x        Response translates code -> {status, description, id, url}
      default              Nega_acao + Terminate   (names the received value)
  Catch_<flow>           Scope  runAfter Try [Failed, TimedOut, Skipped] -> Nega_conector + Terminate
```

The order inside the `Try` is the order of risk: **authorize -> normalize -> validate -> write ->
respond**. Nothing that writes comes before any `Nega_*`. [verified: reference project]

## 2. Why each block exists

| Block | Function | Why |
|---|---|---|
| `CONFIG` | Single place for environment text and flags | A scattered literal carries a DEV e-mail/server into production. The verifier flags a literal outside it (F014) |
| `Perfil_do_chamador` + `Chamador` | Who is calling | The trigger parameter can be forged; the execution context cannot. Details in [authorization-in-flow.md](authorization-in-flow.md) |
| `Try` / `Catch` | Isolate a connector failure | Without `Catch` the app gets a timeout instead of a message |
| `Switch_acao` | One business action per case | Each case authorizes and validates its own action; a single gate before the `Switch` does not know which branch will run |
| `Validar_x` as an `if()` chain | First error message or `''` | One expression, one message, testable without running the write |
| `Codigo_x` | Keep the code once | Avoids repeating the long read expression in `status` and `description` (8,192-character limit) |

## 3. Nega and Terminate

`Response` only exists in a flow with an HTTP (Request) or Power Apps trigger, and it **does not end** the flow: the next action runs with the response already sent. That is why every
`Nega_*` is a `Response` + `Terminate` pair (`runStatus: Succeeded`), and the verifier flags a
`Response` without `Terminate` when the flow continues after it (F015). The rule also holds for a
`Response` inside an `If`: the `If` ends and the flow moves on to the next action of the parent block.
[verified: reference project]

```json
{
  "Nega_perm_grv": {
    "type": "Response",
    "kind": "PowerApp",
    "inputs": {
      "schema": {
        "type": "object",
        "properties": {
          "status": { "title": "status", "x-ms-dynamically-added": true, "type": "string" },
          "description": { "title": "description", "x-ms-dynamically-added": true, "type": "string" },
          "id": { "title": "id", "x-ms-dynamically-added": true, "type": "string" },
          "url": { "title": "url", "x-ms-dynamically-added": true, "type": "string" }
        },
        "additionalProperties": {}
      },
      "statusCode": 200,
      "body": { "status": "error", "description": "Your role does not allow this action.", "id": "", "url": "" }
    },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000001" }
  },
  "Nega_perm_grv_fim": {
    "type": "Terminate",
    "inputs": { "runStatus": "Succeeded" },
    "runAfter": { "Nega_perm_grv": ["Succeeded"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000002" }
  }
}
```

Destination: inside the `actions` of an `If` (pasted as part of a scope, see
[clipboard-format.md](clipboard-format.md)). `statusCode` stays `200` even on a business error:
the app reads `status`, not the HTTP code (see [app-flow-contract.md](app-flow-contract.md)).

## 4. Catch listens for Failed, TimedOut and Skipped

When an action fails, the following ones become `Skipped`
([Learn: run after](https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling)).
`CONFIG`, `Perfil_do_chamador` and `Chamador` are **siblings** of the `Try`: if the profile
connector goes down, the `Try` becomes `Skipped`, and a `Catch` that only listens for `Failed` is
also `Skipped` -- the run ends **without a `Response`** and the app waits until the timeout. That
is why the `Catch`'s `runAfter` carries all three states. The verifier flags the omission (F009).

```json
{
  "Catch_gravar": {
    "type": "Scope",
    "runAfter": { "Try_gravar": ["Failed", "TimedOut", "Skipped"] },
    "actions": {},
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000003" }
  }
}
```

To get the connector's error text (log, support) use
`result('Try_gravar')` filtered by `status = 'Failed'`; `result()` returns only the **first-level**
actions of the scope, not the ones nested in `If`/`Switch`
([Learn](https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling)). See
[run-log.md](run-log.md).

Legitimate exception: an **absorbing** action (e.g. writing a cache that must not bring the flow
down) may omit `Skipped` on purpose, so it does not mask another action's failure -- document that
in the action's description.

## 5. Switch per action

- `Switch` value: `@toLower(trim(triggerBody()['text']))` (the action is the 1st parameter).
- Cases are named `Caso_<acao>`. The designer puts **cases and actions in the same namespace**:
  a case with the same name as an action overwrites the other and the paste dies with `Required property
  'case' not found`, pointing at a case that **has** `case`. The verifier flags it (F008).
  [verified: reference project]
- `default` responds `error` **naming the received value**; it never silently falls into a default
  value (SQL's silent `CASE ... ELSE` was the same trap).
- Derivation with a nested `Switch`: each case is a `Compose` with its own name (`Local_x_base`),
  never equal to the case name.

## 6. Naming rules

| Element | Rule |
|---|---|
| Action | Unique in the whole flow (at any level); no space in the `nodeId`. A duplicate silently becomes `_1` (F004) |
| Switch case | `Caso_*`; must not repeat an action name |
| Denial Response | `Nega_<reason>`; followed by `Nega_<reason>_fim` (`Terminate`) |
| Scopes | `Try_<flow>`, `Catch_<flow>`, `Escopo_<flow>` |
| Action reference | By the exact name. Renaming without rewriting the tokens breaks everything below it, with no designer warning (F006) |

## 7. What stays outside the pasteable scope

- **The trigger.** `Power Apps (V2)` and its parameters are typed by hand, in the order of the
  [contract](app-flow-contract.md). It is the riskiest step of the delivery.
- **The connection.** The paste needs the connection reference created beforehand; `allConnectionData`
  rebinds it (R1 in [designer-baseline.md](designer-baseline.md)). Creating the reference per
  environment is a matter for the `power-platform` skill (ALM).
- **The log.** The template does not bring the `Log` scope; see [run-log.md](run-log.md) for the
  design and the tension with `Terminate`.
- **`Initialize variable`.** Only valid at the flow's root level; inside a scope use `Compose` with
  `coalesce`. [verified: reference project]

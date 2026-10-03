# Authorization and scope inside the flow

Decisions A2, A3, F2, F3 and T8 of [default-decisions.md](../../power-platform/references/default-decisions.md).
The flow is the control; the screen only hides a button. The procedure (`sql-procedures` skill) and
the role tables (`dataverse` skill) have their own owners -- here is only what the flow does.

## Contents

1. [Who is the caller](#1-who-is-the-caller)
2. [Role: flag per action](#2-role-flag-per-action)
3. [Unit scope](#3-unit-scope)
4. [Security flags are born on](#4-security-flags-are-born-on)
5. [Does the procedure authorize too?](#5-does-the-procedure-authorize-too)

---

## 1. Who is the caller

```json
{
  "Perfil_do_chamador": {
    "type": "OpenApiConnection",
    "inputs": {
      "parameters": { "$select": "mail,userPrincipalName,displayName" },
      "host": {
        "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365users",
        "connection": "shared_office365users",
        "operationId": "MyProfile_V2"
      }
    },
    "runAfter": { "CONFIG": ["Succeeded"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000004" }
  },
  "Chamador": {
    "type": "Compose",
    "inputs": "@toLower(coalesce(outputs('Perfil_do_chamador')?['body/mail'],outputs('Perfil_do_chamador')?['body/userPrincipalName'],''))",
    "runAfter": { "Perfil_do_chamador": ["Succeeded"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000005" }
  }
}
```

Destination: inside the `actions` of the root scope, after `CONFIG` (pasted through the designer; see
[clipboard-format.md](clipboard-format.md)).

- **Identity comes from the execution context** (`MyProfile_V2`), which the client cannot forge.
  Whoever calls the flow from outside the screen does not choose who they are. [verified: reference project]
- The caller identifier is wired into **a single node** (`Ler_chamador`), always through
  `outputs('Chamador')`, never through `triggerBody()`.
- **The `mail` x `userPrincipalName` order depends on which value the identity column stores.**
  Normalize the load (`LOWER/TRIM`) and do the 1-minute test: run the flow with a test user and
  compare `outputs('Chamador')` in the run history with the identity column. A mismatch
  denies **everyone** without an error. In reference projects the order ended up swapped between flows
  (see [field-lessons.md](field-lessons.md)).

## 2. Role: flag per action

1. `Ler_chamador` reads the user's row **once**, already joined to the role (active user, active
   role) and returns all the flags. **Zero rows = deny** (unknown or inactive user).
2. Each `Caso_<acao>` checks **that action's flag** (`Autorizar_<acao>`), before any
   write. A single gate before the `Switch` can only cut out whoever has **no** permission
   in the flow; it does not know which branch will run. The classic defect: the role that registers also
   closes irreversibly because the gate only checked "can register".
3. Flag, never role name (T8). No resolved role = no access (fail-closed).
4. The denial is the same generic sentence in every case ([app-flow-contract.md](app-flow-contract.md)).

Reading a SQL `bit` (the connector delivers `true`/`false`, not `1`) and a safe comparison:

```text
@not(or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'true')))
```

Destination: the `expression` field of an `If` (`equals` with `@true`) -- see the template. Missing denies.
Details of the trap in [wdl-expression-pitfalls.md](wdl-expression-pitfalls.md).

## 3. Unit scope

Permission answers *what*; scope answers *where*. Rules:

| Rule | Why |
|---|---|
| Compare the unit of the **real record** (read again in `Estado_antes_x`), not the parameter's, in actions that change an existing record | The parameter is ignored outside registration; checking it would let the caller choose their own authorization |
| In **registration**, compare the parameter (it is what will be written) | The record does not exist yet |
| An action that writes to **two** records checks both | Nothing forces both to be in the same unit |
| The "all units" role is the **first** term of the `or` that grants access; the other terms remain valid on their own (do not rely on short-circuiting) | Someone who sees everything does not need a link row |
| An empty unit on the record **blocks** whoever is not global | Missing data turning into a wildcard is the opposite of scope |
| Empty set of allowed units: test `empty(trim(join(<list>,'')))`, not `empty(<list>)` | With no assignment the list arrives as `['']`, an array of **one** item, which `empty()` treats as full |
| Optional filter where "all" = `null`: wire the **raw** `null`, without `coalesce` or `truncar` | `''` matches nothing; a generic `coalesce` "improvement" already undid this decision and the report came out empty for whoever sees everything |
| The denial message does not state the record's unit | It would answer the question of whoever is probing |

Scope in the app's gallery is UX (A3); only the flow blocks. The template carries the unit validation
inside `Validar_gravar`, switched by `CONFIG.cfgEscopoUnidade`.

## 4. Security flags are born on

`CONFIG` holds the behavior switches (`cfgEscopoUnidade`, `cfgCampoObrigatorio`...).
Every **security** switch is born `true`; turning it off requires a recorded decision. One project
shipped the unit scope as a flag turned off: by default any role wrote to any
unit, and the product decision was never closed. [verified: reference project]

Do not confuse the two kinds of flag: the **role's permission flag** (`Flg_PodeX`) is born
**0/false**, because nobody gets permission by default; the **security switch in `CONFIG`**
is born **on**, because turning it off is what opens access.

## 5. Does the procedure authorize too?

If the procedure only receives "ready" values from the flow and accepts the caller's id as a parameter, whoever
has the connection reference calls the procedure and writes whatever they want, and the audit trail
proves what/when, not who. Two legitimate ways out, both with a cost:

- **Authorization in the procedure too** (defense in depth): more code in the procedure, one
  rule in two places.
- **`GRANT EXECUTE` as the only lock**, risk accepted **in writing**.

The decision and the defensive block belong to the `sql-procedures` skill; the flow does not stop authorizing in
either case. In Dataverse, the Security Role plays the part of the `GRANT` (`dataverse` skill).

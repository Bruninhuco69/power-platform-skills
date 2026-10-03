---
name: power-automate
description: "Use when the work involves a Power Automate flow: designing or reviewing a flow called by the app (Power Apps V2 trigger, 4-field Response, Try/Catch, Switch per action), pasting that flow into the designer (clipboard, pasteable scope, allConnectionData), authorization and unit scope inside the flow, calling a SQL procedure (Execute stored procedure), receiving a batch from an external system over HTTP with a token, writing to Dataverse through $batch/upsert, the log scope, an expression that blows up at run time (if does not short-circuit, string(null), Select outputs), the screen-flow-procedure contract, or verifying a flow JSON. Do not use for the app-side .Run() call (use `powerapps-canvas`), the procedure and DDL (use `sql-procedures`), tables and Security Roles (use `dataverse`), nor environments, solutions and connection references in general (use `power-platform`)."
argument-hint: "[design|paste|verify|contract|http|batch|log] [flow]"
user-invocable: true
---

# power-automate

Produces Power Automate flows that are **pasteable into the designer and verifiable**: the JSON
scope with the standard anatomy (authorize -> normalize -> validate -> write -> respond, complete
`Catch`), the contract with the screen, the design of SQL, HTTP, `$batch` and log, and
`scripts/verificar-fluxo.py`, which flags the defects that only blow up at run time. The decided
standards (F1-F6, C1-C6, A1-A4) are in
[default-decisions.md](../power-platform/references/default-decisions.md) -- this skill implements
them, it does not redefine them.

## Non-negotiable rules

1. **The flow decides; the procedure executes.** The flow normalizes, validates, authorizes and
   translates the write code into a message. Why: a rule on the client can be bypassed and the
   connector account is shared.
2. **The caller's identity comes from the context** (`MyProfile_V2`), never from a trigger
   parameter. Why: whoever calls from outside the screen would say who they are.
3. **Authorization per action**: each `Caso_<acao>` checks its own action's flag before the first
   write; zero role rows = deny. Why: a single gate before the `Switch` let the person who
   registers close records irreversibly.
4. **A security flag is born on** in `CONFIG`. Why: a unit scope was born off and any role wrote
   to any unit.
5. **The response always carries the 4 fields** `{status, description, id, url}` (text), `status`
   in `success|warning|error`. Why: the screen reads `ret.url` from a flow that does not export it.
6. **Every `Nega_*` is a `Response` + `Terminate` pair.** Why: `Response` does not end the flow;
   the next node runs with the response already sent.
7. **`Catch` listens for `Failed`, `TimedOut` and `Skipped`.** Why: when the `Try` siblings (role,
   caller) fail, the `Try` is `Skipped` and the run ends without a `Response`.
8. **Trigger parameters are positional and text; a new parameter goes at the end.** Why:
   inserting in the middle shifts the values and the flow writes the wrong field without an error.
9. **SQL writes only through `Execute stored procedure (V2)`**; procedure and connection reference
   names come from the environment, never from the document. Why: `Insert/Update row` does not work
   with a server-side trigger and assumed names cost pastes.
10. **No literal environment name outside `CONFIG`** (server, GUID, `dev*` table): environment
    variable and connection reference. Why: promoting to production becomes editing the flow.
11. **Protect the argument, not the condition**: `if()` evaluates both branches, and
    `string(null)` is `''`. Why: both blew up at run time, in places that "had already been fixed".
12. **The file the designer returned is the baseline; a generator writes only to `dist/`.** Why:
    regenerating over the baseline erased a fix that existed only on disk.
13. **External input through a separate HTTP trigger**, credential in the header, response derived
    from the real validation result. Why: a `Condition` of constants left the 401 branch dead.

## Workflow

1. **Start with the catalog** (`assets/components/INDEX.md`): if a block exists for the piece, use
   it instead of writing from scratch. Then classify the task and load only what it needs:

| Task | Load |
|---|---|
| Design or review a flow called by the screen | `references/flow-anatomy.md`, `references/app-flow-contract.md`, `assets/flow-write-template.json` |
| Assemble a flow from pieces (CONFIG, caller, Switch, authorize, write, Catch, log, HTTP, `$batch`…) | `assets/components/INDEX.md` — 34 pasteable blocks, each validated, with an assembly order |
| Permission, role, unit scope | `references/authorization-in-flow.md` |
| Deliver/paste into the designer, build the JSON | `references/clipboard-format.md`, `references/designer-baseline.md` |
| Expression that fails only at run time | `references/wdl-expression-pitfalls.md` |
| Flow that writes to SQL | `references/sql-in-flow.md` (the procedure belongs to `sql-procedures`) |
| Receive a batch from an external system | `references/http-external-inbound.md`, `references/dataverse-batch-upsert.md` |
| Create tables and a mockup load in Dataverse through the Web API (ready-made flow, `$batch`) | `skills/power-platform/references/dataverse-builder.md` (from the orchestrator) |
| Run log, support | `references/run-log.md` |
| Generate flows by script, pipeline | `references/generator-and-baseline.md` |
| Contract document | `assets/flow-contract-template.md` |
| Understand where a standard came from | `references/field-lessons.md` |

2. **Map before writing:** environment and designer language; the connection references that exist
   (`power-platform`); the AS-BUILT name of the procedure or table (`sql-procedures`,
   `dataverse`); which actions the flow has and each one's flag; the log destination (ADR).
3. **Write the contract first** (`assets/flow-contract-template.md`): call, positional parameter
   table, authorization per action, code -> message table.
4. **Start from the template** `assets/flow-write-template.json`: replace `<procedure_...>`,
   `<prefixo>_...` and the action names; keep the structure. The trigger is **typed by hand** in
   the contract's order (it is not pasteable).
5. **Verify before pasting** (and again on what the designer returns): `python <skill-folder>/scripts/verificar-fluxo.py <file-or-folder>`.
6. **Paste** (`Ctrl+V` at the designer's insertion point, top to bottom; the trigger must already
   exist), rebind the connections, run with a test user **without** permission, one with
   permission and one from another unit, and check the run history.
7. **Return what the designer returned** to the baseline (read-only file) and, if you generate,
   bring the differences back to the generator before the second flow (`generator-and-baseline.md`).

## References

| File | When to read |
|---|---|
| `references/flow-anatomy.md` | Before designing any flow called by the screen; Nega/Terminate and Catch |
| `references/app-flow-contract.md` | Trigger, 4-field Response, code -> message, new parameter, async job |
| `references/authorization-in-flow.md` | Role, flag per action, unit scope, fail-closed |
| `references/clipboard-format.md` | Scope and leaf envelopes, how to paste, `allConnectionData`, trigger language |
| `references/designer-baseline.md` | R1-R13: what the designer returns, what blocks and what only normalizes |
| `references/wdl-expression-pitfalls.md` | `if()`, `string(null)`, `outputs()` x `body()`, `bit`, 8,192 characters, `@{}` |
| `references/sql-in-flow.md` | `Execute stored procedure (V2)`, reading the return, connector limits |
| `references/http-external-inbound.md` | Request trigger, token in the header, real status, accept x synchronous, N=1 x batch |
| `references/dataverse-batch-upsert.md` | `$batch`, changeset, upsert, 429, pagination |
| `references/run-log.md` | `Log` scope, parent/child tables, `workflow().run.name`, tension with `Terminate` |
| `references/generator-and-baseline.md` | Safe generator, immutable baseline, round-trip |
| `references/field-lessons.md` | Real flow defects (SQL, HTTP + `$batch`) and the rule that prevents each one |
| `assets/components/INDEX.md` | Catalog of pasteable blocks (explained `.md` + validated `.json`), maturity and assembly order |
| `assets/flow-write-template.json` | Starting pasteable scope (passes the verifier) |
| `assets/flow-contract-template.md` | Screen <-> flow <-> procedure contract template |

## Scripts

`<skill-folder>` is the *Base directory* shown when the skill is loaded. Run **from the project root** (the script looks for `power-platform.config.json` from the current directory upward) or pass `--config`.

| Command | What it checks | Exit |
|---|---|---|
| `python <skill-folder>/scripts/verificar-fluxo.py <file\|folder>` | F001 JSON; F002 envelope; F003/F019 node identity and segments; F004 duplicate name; F005 orphan `runAfter`; F006 reference to a missing action; F007 `items()`; F008 `Switch` case; F009 `Catch` without `Skipped`; F010 `Response` without the 4 fields; F011 `outputs()` of `Select`/`Query`; F012 `coalesce(string())`; F013 expression > 8,192; F014 environment literal; F015 `Response` without `Terminate`; F016 constant condition; F017 missing connection; F018 `@{}` in a parameter; F020 `If` condition as text or without `and`/`or`; F021 `Initialize variable` outside the root; F022 a variable alone in a pasted field; F023 `Do until` as pasted text | 0 no errors, 1 with errors, 2 incorrect usage |
| `python <skill-folder>/scripts/verificar-fluxo.py --estrito <...>` | also `coalesce(string(x), '')` (F012) | same |
| `python <skill-folder>/scripts/verificar-fluxo.py --config <file>` | uses `pastas.flows` and `ignorar` from `power-platform.config.json` | same |

Formats read: clipboard scope and leaf envelopes (`.json`, or `.md` with only the JSON) and the
`definition` of an exported solution. Read-only; output `path:place: ERROR|WARNING Fnnn message`.

## Definition of done

Commands from the project root (see the note under Scripts).

- [ ] `python <skill-folder>/scripts/verificar-fluxo.py <flow>` -> `0 error(s)` (warnings read and justified in the contract).
- [ ] Flow contract filled in; number of `.Run()` arguments == number of trigger parameters.
- [ ] Denial test run: a user without the action's flag receives `error` and **nothing** is written.
- [ ] Connector failure test: with the connection reference turned off, the app receives the
      `Catch` message (never a timeout).
- [ ] No environment literal outside `CONFIG` (F014 clean or warning justified).
- [ ] The JSON returned by the designer is in `baseline/` (read-only) and no generator writes over
      it.
- [ ] A task marked done carries the Evidence column: command, output and date (P2).

## Pitfalls

1. `if()` does not protect the call inside it: protect the argument --
   [wdl-expression-pitfalls.md](references/wdl-expression-pitfalls.md) §1.
2. `coalesce(string(x), '0')` never falls back -- same file, §2.
3. `outputs('Select')` returns the envelope; use `body()` -- §3.
4. SQL `bit` arrives as `true`/`false`; comparing with `1` or with the boolean `true` inverts the rule -- §4.
5. A `Switch` case named like an action breaks the paste --
   [flow-anatomy.md](references/flow-anatomy.md) §5.
6. `Catch` without `Skipped`: a run without a `Response` -- same file, §4.
7. `Response` without `Terminate` responds twice -- same file, §3.
8. Swapped `mail`/`userPrincipalName` order denies everyone --
   [authorization-in-flow.md](references/authorization-in-flow.md) §1.
9. Running the generator with a manual edit on disk erases the fix --
   [generator-and-baseline.md](references/generator-and-baseline.md) §2.
10. 200 before writing without declaring it is an accept --
    [http-external-inbound.md](references/http-external-inbound.md) §5.

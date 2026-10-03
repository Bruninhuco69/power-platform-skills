# GOAL — <PROJECT>

**Single objective:** <one sentence: what exists when this is done>.

**Target:** <date> · **Fallback:** <date and what ships> · **Data track:** <sql-server | dataverse>
(same as `power-platform.config.json` and `00-READ-ME-FIRST.md`).

This is the project's **single execution queue**. Decisions are in `docs/decisions/` (ADR) and are
not reopened without an ADR. The *how* is in the skills `power-platform`, `powerapps-canvas`,
`power-automate`, `sql-procedures` and `dataverse`. Here you only find **what to do, in what order
and who does it**.

---

## 1. The three layers

| Layer | Who | What it is |
|---|---|---|
| **File** | Claude | Screen YAML, flows, scripts, specs, validations. Can be produced and verified without an environment |
| **Environment** | Human | Sign in, create a table, apply a script to the database, paste a screen/flow, turn on a flow. Requires credentials |
| **Gate** | Both | The proof that the step worked. Without a closed gate, the next wave does not start |

There is no "run everything end to end": Claude produces all the material and the human performs
the 🔴 points.

## 2. Decisions and open items

| # | Decision / open item | Blocks | Owner | Deadline | If missed |
|---|---|---|---|---|---|
| D-01 | <compliance / permission / frozen database assumption> | <tasks> | <role> | <date> | <consequence> |

## 3. Legend

🟢 Claude produces the file · 🔴 human performs it in the environment · ⬜ pending · ✅ done **with evidence** ·
⛔ blocked by D-xx

## 4. Queue

### Wave 0 — Foundation (gate G0)

| ID | Status | Task | Files | Done when | Evidence (command → output, date) |
|---|---|---|---|---|---|
| T-01 | ⬜ | `git init`, `power-platform.config.json`, `00-READ-ME-FIRST.md` | the three, at the root | active track declared in all three | |
| T-02a | 🔴 | Create the tables with the mockup load (Dataverse: run the builder with `dataverse-plan.json`, or import the `.xlsx`; SQL: DDL and `mockup-load.sql` in DEV) | `Backend/<track>/mockup-load.*`, `dataverse-plan.json` | Dataverse: `montar-carga-mockup.py <spec> --conferir <export.json>` with 0 error(s) (Dataverse gets the typing wrong: check before real data); SQL: the script runs without error | |
| T-02 | 🔴 | Capture `AS-BUILT-NAMES` from the real environment | `AS-BUILT-ENVIRONMENT/AS-BUILT-NAMES.md` | tables, columns, types, procedures, connections with dated capture | |
| T-03 | ⬜ | ADRs for the decisions already made | `docs/decisions/ADR-*.md` | one ADR per decision outside the standard | |

**Gate G0:** <command/proof for each foundation item>. **Does not cover:** <what is left out>.

### Wave 1 — <feature or layer> (gate G1)

| ID | Status | Task | Files | Done when | Evidence (command → output, date) |
|---|---|---|---|---|---|
| T-10 | ⬜ | Flow contract: `.Run()` parameters and return | `docs/planning/architecture.md` §4 | positional parameters listed; return `{status, description, id, url}` | |
| T-11 | ⬜ | Flow `<name>` | `<flows folder>/<name>.json` | `verificar-fluxo.py` with 0 error(s) | |
| T-12 | ⬜ | Screen `<name>` | `<screens folder>/<Screen>.pa.yaml` | `validar-telas.py` with 0 error(s) | |
| T-13 | 🔴 | Paste the flow into the designer and the screen into Studio | — | runs without error with test data | |
| T-14 | ⬜ | Feature QA | — | full cycle on the data, not just on the screen | |

**Gate G1:** <proof>. **Does not cover:** <...>.

## 5. How Claude moves forward

In the pipeline, `/pp-en:build` walks this queue: **one wave per session**, the Canvas and
Automate agents in parallel, and `STATE.md` says when the build is done.

1. Take the next undone 🟢 whose previous wave closed its gate.
2. Load only what is needed (domain skill + the relevant part of the spec).
3. Execute; validate with the final gate of the `power-platform` skill.
4. Mark ✅ **only with the Evidence column filled in**; update the table in section 7.
5. On reaching a 🔴: stop there, say what the human does in the environment, and carry on with the
   independent 🟢 tasks.

Do not ask permission between 🟢 tasks. Ask only if a mistake would invalidate all the work.
Reducing scope is the user's decision.

## 6. Stop conditions

| Condition | Why |
|---|---|
| Compliance/IT assumption comes back negative | there is no architecture plan B |
| Gate fails twice for the same cause | planning error: reopen the decision |
| Column/procedure name does not exist in the environment | writing on a guessed name is the #1 cause of rework |
| Wave blows the deadline without a gate | trigger the cut ladder, do not cut silently |
| Property the app does not use on that control | Studio rejects the block (PA2108) |

**Cut ladder (what goes first → last):** <1> → <2> → <3>.
**Never cut:** audit trail; per-action authorization in the flow; <main cycle>.

## 6.1 Dead proposals

| Proposal | Died at | Why |
|---|---|---|

## 7. Fixes made to the queue — Was → Is

| Where | Was | Is | Why (evidence) |
|---|---|---|---|

## 8. Status

| Wave | Status | Latest evidence (command, date) |
|---|---|---|
| 0 | ⬜ | |

Every metric in this table carries the command that measures it and the date of the measurement.

# Work protocol

Map → Plan → Execute → Validate → Report. Applies to every task with more than one step on an
existing app. A new app follows the `/pp-en:*` pipeline (`pipeline.md`), which already embeds these phases.
Each phase has an **exit criterion**: without it the phase is not finished.

## Dependency order between layers

```
data (table / procedure / environment)  →  ( frontend  ∥  automation )  →  QA
```

- **Data first.** Table, column, procedure and connection reference exist and are in
  `AS-BUILT-NAMES` before any screen or flow that uses them.
- **Frontend and automation in parallel** when the app↔flow contract is closed (positional
  parameters, `{ status, description, id, url }` format — see `default-decisions.md` §2).
- **QA per delivery**, not only at the end: each screen and each flow passes the gate before the next wave.
- If the data layer is not ready, the screen task becomes 🔴 (depends on the environment) in the queue.

## Phase 1 — Map

Always do it. It produces a short map, not an opinion.

- Identify: screen and name prefix, data source and columns, flows called, procedures,
  environment (DEV/HML/PRD) where the data lives.
- Locate with `Grep` (`output_mode: content`) and read with `offset`/`limit`. A large screen file
  is never read whole.
- Check names against `AS-BUILT-NAMES`. Before stating that a column does not exist, open the table's
  schema — never a filtered extract (N3).
- Look for what already exists before creating: canonical block, template, component.

**Output:** list of files/controls/actions involved, each with the command that found it; list of
what is inferred and not confirmed.

## Phase 2 — Plan

- At most 5 steps, in dependency order.
- Say what will **not** be done and why.
- Ambiguity that changes the result: decide, **state the assumption** and go on. Ask only if being wrong
  would make the work useless.
- Mark each step as 🟢 (you produce a file) or 🔴 (human executes in the environment).
- If it changes the track, contract or standard: write the ADR first (`assets/adr-template.md`).

**Output:** numbered plan + assumptions + out of scope. A project that came in without the pipeline: `GOAL.md`
from `assets/goal-template.md` and ADRs for the decisions already made.

### Planning a new project (kickoff)

Before the first screen, settle and record (ADR or `00-READ-ME-FIRST.md`):

1. Data track (`sql-server` **or** `dataverse`) and why.
2. Environments (DEV/HML/PRD), publisher/prefix, who creates tables and who is the DBA.
3. Roles and scope per unit; where authorization is decided (in the flow — A3).
4. Compliance, license and gateway assumptions; each with an owner and deadline.
5. When the database freezes and what still fits afterwards (a calculated column usually fits; a new table does not).
6. Real team capacity and what is 🔴 (environment) — the plan has to fit it.
7. `git init` on day 0 and `power-platform.config.json` at the root.

## Phase 3 — Execute

- One layer at a time, in dependency order.
- Reuse templates and canonical blocks from the domain skills before writing from scratch.
- Respect the destination of each code block: formula bar or pasted YAML (in en-US both use `,`
  between arguments and `;` to chain) — `default-decisions.md` §3.
- Generator output only in `dist/`; a manual fix goes into the generator's input or becomes a baseline.
- A change that breaks a contract (`.Run()` parameter, flow return): new parameter **at the end**;
  update screen and flow in the same task.

**Output:** changed files listed; nothing generated over a baseline.

## Phase 4 — Validate (mandatory gate)

Run `references/final-gate.md`. In short:

1. All the validators of the skills involved, not just one.
2. Each with `0 error(s)` — and you know what it does **not** cover.
3. Manual checklist (delegation declared, names checked, loading/empty/error, no environment literal).
4. Screen or flow: paste into Studio/the designer, or record 🔴.

If it failed: fix it and run again. **Two failures from the same cause** = planning error; stop, say what
changed in the hypothesis and reopen Phase 2.

**Output:** literal output of each validator (last line) + checklist result.

## Phase 5 — Report

Four items, in this order:

1. What changed, in one sentence.
2. **How to apply:** formula bar / pasted YAML into which parent control / designer / solution.
3. Warnings: delegation, 500/2,000 cap, uninitialized variable, call cost.
4. What was left out and why; what is 🔴 and with whom.

Report what failed with the evidence (validator that flagged, agent that erred, data that does not exist).
An optimistic report costs a lot later.

**Output:** report with evidence; queue updated if there is a `GOAL.md`.

## End-to-end feature delivery

1. **Data:** do the table/procedure and columns exist? If not, it is 🔴 or a request to the DBA; do not invent a name.
2. **Contract:** define the `.Run()` parameters and the return before screen and flow.
3. **Formula/source:** does the query delegate? Resolve it now (calculated column, `Ref_*`), not after the screen.
4. **Flow and screen in parallel**, each through its domain skill.
5. **State and error:** loading, empty, error, toast tied to `status`.
6. **Final gate.**

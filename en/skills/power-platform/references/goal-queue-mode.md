# The `GOAL.md` queue

The build runs on **a single queue**: the project's `GOAL.md`, written by
`pp-en:architecture-agent` and walked by `/pp-en:build`, one wave per session. Outside the pipeline
(an existing app with a queue), the orchestrator walks the queue the same way. Claude Code's native `/goal`
("keep going until condition X") can go along with it, using a verifiable condition such as "all
🟢 tasks of wave 2 in `GOAL.md` are ✅ with evidence".
Four parallel queues (frontend, flows, procedures, root) diverged in the reference projects.
One queue per project; the waves separate the layers.

## Contents

1. [How to advance](#how-to-advance)
2. [Queue format](#queue-format)
3. [States](#states)
4. [Evidence column](#evidence-column)
5. [Was → Is table](#was--is-table)
6. [Gates per wave](#gates-per-wave)
7. [Stop criteria](#stop-criteria)
8. [Project state](#project-state)

## How to advance

1. Take the **next 🟢 not done** whose previous wave closed its gate.
2. Load only what that task needs (domain skill + the relevant part of the specification).
3. Execute; validate (`final-gate.md`).
4. Mark ✅ **only with the Evidence filled in**. Update "Was → Is" if anything in the queue changed.
5. On reaching a 🔴: **stop at it**, say exactly what the human does in the environment (command,
   screen, what to paste, what to return), and keep going on the 🟢 tasks that do not depend on it.

Autonomy: do not ask permission between 🟢 tasks; decide and state the assumption. Ask only if
answering wrong would invalidate all the work. Finish what can be finished; a blocked part
delivers the rest complete and says what was left out. **Reducing scope is the user's decision.**
Report failures (validator flagging, missing data, failing test) with evidence.

## Queue format

`GOAL.md` header (ready-made template: `assets/goal-template.md`):

- **Single objective** and date target.
- **The three layers:** *File* (you produce and verify without the environment), *Environment* (an
  authenticated human creates the table, publishes the flow, pastes the screen), *Gate* (the proof the stage
  worked). There is no "run everything end to end": what exists is producing all the material and
  asking for the human at the 🔴 points.
- **Pending decisions** `D-xx`: what blocks, who decides, deadline and the consequence of missing it.
- **Queue per wave**, in a table:

| ID | State | Task | Files | Done when | Evidence |
|---|---|---|---|---|---|
| T-01 | 🟢 | Specify the write flow contract | `docs/planning/architecture.md` §4 | Contract with parameters and return reviewed | `<command>` → `<output>` (YYYY-MM-DD) |

**Files** are the ones the task creates or changes, with the path: it is what lets the build split the
wave among agents in parallel without two on the same file. **Done when** states the command that proves it.

Pattern repeated per feature: spec (🟢) → screen/flow file (🟢) → paste/connect in the environment
(🔴) → QA (🟢). Wave per layer or per feature; each one ends in a gate.

## States

| Mark | Meaning |
|---|---|
| 🟢 | you produce the file; verifiable without the environment |
| 🔴 | the human executes in the authenticated environment (create table, import, paste, publish) |
| ⬜ | pending, not yet classified |
| ✅ | done **with evidence** |
| ⛔ | blocked by decision `D-xx` (say which) |

A task that **regressed** goes back to 🟢 with a note in the "Was → Is" table. An item that depends on the
environment stays 🔴 until there is a dated capture of the environment.

## Evidence column

Mandatory for ✅. Format: **command + relevant output + date** (or commit hash).

Valid examples:

- `python <validator> <folder>` → `0 error(s), 2 warning(s)` (2026-10-01)
- `git grep -c "RGBA(" -- screens/` → `0` (2026-10-01)
- Studio capture pasted into the environment, file name and date (for a completed 🔴)

Invalid: "done", "validated", "ok", a link to the edited file itself. Evidence **expires**: if the
file or the upstream generator changed after the date, the task is no longer proven — re-verify.

For a regression task (one that already broke once), also record the **re-verification command**
and run it when closing each wave.

## Was → Is table

Records each correction made **in the queue itself** during execution, instead of striking text inline:

| Where | Was | Is | Why |
|---|---|---|---|
| T-14 · period filter | 30-day default | starts empty with an `IsBlank` guard | the cut-off hid items open for months |

Rules: one row per change; cite the point by **control/action name**, not by line number;
the "Why" column cites the evidence. Control document over ~400 lines: move the history
to `CHANGELOG` and keep only the current state.

## Gates per wave

Each wave ends in a numbered gate (G0, G1…). Without a closed gate the next wave does not start.
The gate lists: the command of each validator, the expected result, the business rule test
**executed on the data, not only on the screen**, and what the gate does **not** cover.

Gate examples per layer:

| Gate | Proof |
|---|---|
| Foundation | tables/procedures created, `AS-BUILT-NAMES` filled in with a dated capture, row count checked |
| Feature | full cycle executed (register → validate → save → check) with test data |
| Report | total displayed == count on the server (no silent truncation) |
| Delivery | a real operator runs the cycle; minutes and `GO-LIVE-CHECKLIST` attached |

## Stop criteria

Stop and report, even in the middle of a wave, when:

| Condition | Why |
|---|---|
| A compliance/IT assumption comes back negative | there may be no architecture plan B |
| The gate fails twice for the same cause | planning error, not execution error: reopen the decision |
| A column/procedure name does not exist in the environment | writing on a guessed name is the #1 cause of rework |
| A wave's deadline passed without a closed gate | trigger the pre-approved cut ladder, do not cut silently |
| Needs a property/control the app does not use for that type | Studio rejects the whole block (PA2108): check first |
| A new IT restriction invalidates the assumption behind already planned tasks | record it under "dead proposals" and replan |

## Project state

Keep at the end of `GOAL.md` a `Wave | Status | Latest evidence` table. It is what the next
session reads to know where it stopped. Every metric there ("N variables", "X of Y screens") carries the command that
measures it and the date of the measurement.

# Process safeguards

Each safeguard was born from a real failure in the reference projects. Format: **rule → why →
how to verify**. The failures are described without project, person or environment names.

## Contents

1. [Single track](#1-single-track)
2. [Environment first](#2-environment-first)
3. [Generator × baseline](#3-generator--baseline)
4. [Executable evidence](#4-executable-evidence)
5. [Document × disk](#5-document--disk)
6. [ADR on track change](#6-adr-on-track-change)
7. [Git on day 0](#7-git-on-day-0)
8. [IT and compliance assumptions](#8-it-and-compliance-assumptions)
9. [Product decision and cut scope](#9-product-decision-and-cut-scope)
10. [Document size and hygiene](#10-document-size-and-hygiene)
11. [Capacity and cut ladder](#11-capacity-and-cut-ladder)

## 1. Single track

**Rule.** Each layer has **one** active track, declared in `00-READ-ME-FIRST.md` (with a date) and in
`power-platform.config.json` (`trilha_dados`). The old track goes to `_archive/` with an
"obsolete" banner; it does not stay alongside.

**Why.** A document declared a folder "frozen — never edit"; later it was
edited with a whole overhaul, while the track that was actually active fell behind. The
project skill only knew the wrong track and there were four execution queues at the same time.

**How to verify.**

```bash
git log -1 --format=%cs -- <track-A-folder>
git log -1 --format=%cs -- <track-B-folder>
```

If the "frozen" folder has a newer commit than the "active" one, the document is lying: stop and resolve (ADR).
Before editing, check that the target folder is the active one **on disk**, not only in the text.

## 2. Environment first

**Rule.** No screen or flow before `AS-BUILT-NAMES` (environment, tables, columns, types,
procedures, connections) is filled in from the **real environment**, with a dated capture. The
dictionary, the creation script and the plan **lose** to it (N1, N2).

**Why.** A screen written against the dictionary needed batch corrections in Studio; a flow wrote to
columns that did not exist; procedures documented with one prefix had another in the database; documented connection
references differed from the real ones; a truncated column name spread through the whole repo.

**How to verify.** For each new name: `grep -n "<name>" <nomes_as_built>`. Absent = inferred,
mark "inferred" and open a pending item. Before stating "the column does not exist", open the **table
schema** (N3). Truncated name = open pending item, never "complete it from memory".

**Environment proofs before writing a procedure body:** compatibility level, collation,
caller identity (does `User().Email` return what is expected?), `OUTPUT INTO` with a trigger. Verify with
`SET PARSEONLY ON` first and throwaway DDL in DEV.

## 3. Generator × baseline

**Rule.** (a) Generator output only in `dist/`, with a "generated — do not edit" header. (b) What was
**pasted into the environment** and worked is the **baseline**: immutable `baseline/` folder. (c) A manual fix
goes into the generator's **input**, never into its output. (d) Before regenerating, tag in Git. (e) The
regeneration gate compares generated × `dist/`, never generated × baseline.

**Why.** A gate said to run the generator, which would open the file in write mode and erase the
only environment evidence. A delivered fix was erased when the generator was rewritten and
nobody noticed; the generator was older than the output and regenerating would silently erase several fixes,
with both gates still at `0 error(s)`.

**How to verify.**

```bash
git status --short -- baseline/ dist/     # baseline: no change without an ADR
git log --oneline -3 -- baseline/
```

Generator older than the output, or generator missing from disk (only bytecode): treat the output as the
baseline and **do not** regenerate. Do a round-trip: generate into a temporary folder and compare with `dist/`.

## 4. Executable evidence

**Rule.** ✅ requires command + output + date (`goal-queue-mode.md`). A validator without a test that plants the
error proves nothing (P4): every gate has a fixture that passes and a fixture that fails with the expected code.
Evidence **expires** when the file changes after it.

**Why.** A task marked ✅ "done" had regressed and the execution sheet did not know; another
was left with items out on purpose so as not to mark a defect closed when it was not. A
flow with unquoted literals passed three gates because nothing interpreted the expression.

**How to verify.** Pick 3 ✅ at random and run the command in the Evidence column. If it diverged, the queue
is not reliable; re-verify the whole wave.

## 5. Document × disk

**Rule.** A document that declares a number (screen count, error baseline, "N variables") carries
the command that measures it and the date (P5). A cited path must exist. Cite by **control/action
name**, not by line number.

**Why.** Counts in control documents were corrected several times (variable
count, coverage percentages); claims such as "the folder is empty" and "two identical files" stayed
in the document after they were false; script paths moved to another folder and the orchestrator still pointed to
the old one.

**How to verify.**

```bash
# cited paths that do not exist (adjust the pattern to the project's convention)
grep -ohE "[A-Za-z0-9_./-]+\.(md|py|json|sql|yaml)" 00-READ-ME-FIRST.md GOAL.md | sort -u | while read f; do [ -e "$f" ] || echo "MISSING: $f"; done
```

A number without a command beside it: ask for the command or run it and replace it. Old baseline: measure again and note the date.

## 6. ADR on track change

**Rule.** A change of data track, app↔flow contract, layout or any item in
`default-decisions.md` requires an ADR (`assets/adr-template.md`) **before** touching anything, and updates in the same commit:
`00-READ-ME-FIRST.md`, `power-platform.config.json`, the project skill and the queue.

**Why.** The technology changed several times, none with a record: nobody knew the
current track or why the previous ones died. "Right" proposals were invalidated by an
IT restriction that arrived later, and the queue did not record the dead proposals.

**How to verify.** `git log -- docs/decisions/` shows one ADR per change; the config and
`00-READ-ME-FIRST.md` agree on the track.

## 7. Git on day 0

**Rule.** `git init` before the first line; branch per wave; tag per delivery; `.gitignore` for
`dist/` when generated, load data, `.venv` and files with real data. No `.rar`/`_before/` as
backup. Before any mass regeneration or refactor, tag.

**Why.** Without a repository, backups were manually zipped files and an empty `_before/` folder;
regressions like the one in section 3 could not be detected by diff.

**How to verify.** `git rev-parse --is-inside-work-tree` → `true`; `git tag` lists the deliveries.

## 8. IT and compliance assumptions

**Rule.** A compliance, license, gateway, tenant permission or database freeze assumption
goes into the decisions table and `D-xx` pending items of `GOAL.md` (section 2) with an **owner, deadline and consequence of missing it**. Blocking questions
(security, IT/DBA/license) come **before** designing. The first question of a correction is "does this fit
in what is still allowed?".

**Why.** A compliance assumption appeared as "blocks the whole project" in several documents
and still had no recorded answer. Denied tenant permission and a frozen database arrived late and
invalidated proposals; the freeze later gave way only for a calculated column.

**How to verify.** Each pending item has the three fields; overdue ones show in the queue state.

## 9. Product decision and cut scope

**Rule.** An item that changes what the user sees is a "product decision" and needs approval from a
business owner; deleting dependent code requires the approval reference in the commit. Every
non-goal records **who uses it today** and **who accepted the cut**; check the live data before cutting.

**Why.** A module was cut from scope in four documents without agreeing with operations — it was
the highest-volume resource of the pilot unit. Data of extra units was deleted before the
approval the plan itself required.

**How to verify.** `grep -n "approv" GOAL.md` and the non-goal row with "who uses it / who accepted".

## 10. Document size and hygiene

**Rule.** Control document under ~400 lines; history in `CHANGELOG`; obsolete goes
to `_archive/` with a banner; "Was → Is" in place of inline struck-through text. Specification and
history do not mix.

**Why.** Huge documents mixed specification and history, and files that
declared themselves obsolete stayed in the tree being read as a reference.

**How to verify.** `wc -l 00-READ-ME-FIRST.md GOAL.md` and `grep -rl "obsolete\|superseded" .`

## 11. Capacity and cut ladder

**Rule.** Declare the real capacity (who, how many hours, how many environment 🔴 and the time of
each). Have a **pre-approved cut ladder** (what goes first) and the list of what is **never**
cut (audit trail, permission revalidation in the flow, the main cycle).

**Why.** The deadline was planned for a team and executed by one AI session and one human
for the environment; the 🔴 became a bottleneck with no owner and no estimated time.

**How to verify.** The queue lists, for each 🔴, an owner and an estimate; the schedule cites the ladder.

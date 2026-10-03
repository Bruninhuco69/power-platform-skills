# Final gate

How to prove it is ready. A gate only counts if it (1) ran, (2) covers the format of what changed and
(3) has already flagged a planted error. This page says which commands to run and which greens mislead.

## Contents

1. [Procedure](#1-procedure)
2. [Validators per skill](#2-validators-per-skill)
3. [What a real green is](#3-what-a-real-green-is)
4. [Known false greens](#4-known-false-greens)
5. [Manual checklist](#5-manual-checklist)
6. [Final proof: paste into Studio or the designer](#6-final-proof-paste-into-studio-or-the-designer)
7. [Gate report](#7-gate-report)

## 1. Procedure

1. List the layers touched (screen, flow, procedure, table, ALM).
2. For each layer, run **all** the validators in the table below, from the project root, with
   `power-platform.config.json` present (without it the script uses defaults and **says so** — read the line).
3. Paste the **last line** of each output (`N error(s), M warning(s)`) into the report, with the date.
4. Check that each validator **read** something: the output lists the files, or the total of items
   analyzed is greater than zero. `0 error(s)` over zero files is a false green.
5. Run the manual checklist (section 5).
6. Do the final proof (section 6) or record 🔴.
7. If it failed: fix it and run **all** of them again. Two failures from the same cause: reopen the plan.

## 2. Validators per skill

| Layer | Skill | Command (from the project root) | Covers | Exit |
|---|---|---|---|---|
| Screens | `powerapps-canvas` | `python <skills>/powerapps-canvas/scripts/validar-telas.py <screens-folder>` | YAML parsing (plain and fenced), PA2108, literal `RGBA(`, `Control:` without a version, `;;` inside YAML (T007 — `;` as an argument separator is **not** flagged), names | 0/1/2 |
| Flows | `power-automate` | `python <skills>/power-automate/scripts/verificar-fluxo.py <flows-folder>` | envelope and node identity (F002/F003/F019), orphan references, `Catch` with `Skipped` (F009), 4-field `Response` (F010) and `Terminate` (F015), environment literal (F014), conditions and variables that paste blank (F020–F022). **Does not cover** per-action authorization: that is a denial test | 0/1/2 |
| Procedures | `sql-procedures` | `python <skills>/sql-procedures/scripts/lint-procedure.py <procedures-folder>` | `NOCOUNT`, `XACT_ABORT`, transaction, return with the 4 columns (heuristic by alias; WARNING P004) | 0/1/2 |
| Prototype | `power-platform` | `python <skills>/power-platform/scripts/verificar-prototipo.py <folder> --mockups <spec>` | prototype mark, canvas, screens traced to the mockups, catalog components, offline, color only in `:root` (V001–V013). **Does not cover** visual fidelity: that is the user's acceptance | 0/1/2 |
| Skill (if you edited a skill) | plugin repository | `python tools/lint_skills.py skills/<name>` | pattern and sanitization | 0/1 |
| Script tests | plugin repository | `python -m pytest tests -q` | fixtures that pass and that fail | 0/1 |

`<skills>` is the folder where the plugin is installed; the scripts also read the `config` folders
when called without arguments. Each script has `--help`; exit `0` = no error, `1` = found an error,
`2` = incorrect usage. Output per finding: `path:line: ERROR|WARNING CODE message`.

If you changed only one layer: run its validators **and** those of the layers that consume it (a screen that calls the
changed flow is affected by the contract).

## 3. What a real green is

A `0 error(s)` counts when all four conditions are met:

| Condition | How to check |
|---|---|
| The validator understands the **format** | the output shows files read / items analyzed > 0 |
| It has already **flagged** a planted error | a failing fixture exists in `tests/<skill>/`, or you plant an error and the validator exits 1 |
| It ran on the **right folder** (active track) | the path analyzed is the one from `config`, not the archived track |
| It ran **after** the last edit | run date ≥ date of the changed file |

If a condition fails, the report says "validator X does not prove Y" and the layer has no verdict.

## 4. Known false greens

| False green | Cause | Defense |
|---|---|---|
| `0 error(s)` on plain-YAML screens | the validator only read YAML blocks fenced in Markdown; unfenced screens become zero files | `telas_formato` in the config; check the total of files analyzed |
| False errors on the wrong track | a validator for one track run over the other | the folder comes from `config`; check `trilha_dados` |
| "Self-consistent" gate | wrong generator + wrong output = equal, hence green | compare with the **environment baseline**, not generated × generated |
| Regenerating to "pass" the gate | the generator overwrites a baseline fixed by hand | never regenerate over a baseline (`safeguards.md` §3) |
| Unquoted literals in a flow expression | no gate interpreted the expression | pasting into the designer is the proof; expression lint when it exists |
| Plausible but nonexistent column name | the schema "looks right"; no compile error, just an empty gallery | manual check against `AS-BUILT-NAMES` and the open schema (no script compares names yet; T014 only checks the prefix) |
| Property accepted by the validator, rejected by Studio (PA2108) | the validator did not have the list of properties per control type | paste into Studio |
| Stale numeric baseline ("0 error(s)/9 warnings") | the document declares it, nobody ran it | run it and note the date |
| Validator never flagged anything | never tested with a planted error | failing fixture (P4) |

## 5. Manual checklist

- [ ] Every table function had **delegation verified and declared in writing** (T7); `2,000+` cap
      displayed wherever there is a count over SQL (B3).
- [ ] Table/column/procedure names checked in `AS-BUILT-NAMES` or marked "inferred".
- [ ] `.Run()` inside `IfError`; success = `status <> "error"`; `Refresh` + recount after saving (C3, C5).
- [ ] Numeric id sent with `Text(id, "[$-en-US]0")`; new parameter at the **end** (C4).
- [ ] Every global variable is born in `OnStart`; a named formula does not depend on a global variable (T6).
- [ ] A long operation has loading; a gallery has an empty state; an error has a message to the user.
- [ ] A timer has a stop rule and does not run on an invisible screen.
- [ ] Color/font/size only through an `fx*` token (T3); no new `RGBA(`.
- [ ] Authorization **per action** in the flow, security flag born on (F2, F3); scope on the screen is UX (A3).
- [ ] `Catch` listens for `Failed`, `TimedOut` **and** `Skipped`; `Log` in every flow (F1, F4).
- [ ] No `dev*`, server, environment URL or literal GUID (`alm-environments.md` §11).
- [ ] The code block states its **destination** (formula bar × pasted YAML).
- [ ] No real data, absolute path or real e-mail in a versioned artifact.

## 6. Final proof: paste into Studio or the designer

A static validator does not replace the environment. For a changed screen or flow:

| Change | Proof | Record |
|---|---|---|
| Control/screen | paste into Studio (Code view); open **with no formula error**, no PA2108, no new delegation warning | capture or text "pasted into <screen>, 0 errors, <date>" |
| `App.OnStart`/named formulas | type into the property; the app runs, variables initialize | same |
| Flow | paste into the designer; save with no error; run with test input; check output and history | run result (status, failed action, duration) |
| Procedure | `EXEC` with test data in DEV; 1 row `status, description, id, url` | `EXEC` output |
| Solution | import into HML; smoke test (`alm-environments.md` §10) | imported version + result |

Without access to the environment: the task does **not** become ✅; it stays 🔴 with the exact step (what to paste, where, what to
check, what to return). Deliver the rest ready.

## 7. Gate report

```
Final gate — <project> — <date>
Layers: screen | flow | procedure | ...
validar-telas.py        → N error(s), M warning(s)   (files read: X; proof it flags: <fixture or planted error>)
verificar-fluxo.py      → N error(s), M warning(s)   (...)
lint-procedure.py       → N error(s), M warning(s)   (...)
Manual checklist        → items ok / items with reservations (list)
Proof in the environment → pasted into <where>: <result> | 🔴 <step>
Not covered             → <what no gate covers this time>
```

Approved: no ERROR, no touched layer without a validator, proof in the environment done or 🔴 recorded.
Blocked: any ERROR, a validator that did not read the format, a layer without a validator, an open critical finding.

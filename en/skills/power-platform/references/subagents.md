# Subagents

Who the pipeline's agents are, when to open a subagent outside it, how to split work, what to
require on return and how to judge the deliverable. The prompt templates for auditing an existing
app are in `prompts/`.

**The session is the head, the agent is the hand.** The stage session defines the request, gathers
the context, judges what comes back and decides with the user. The agent does the heavy work
(writing a screen, flow, procedure, prototype, spec) and proves what it did. The head does not do
the hand's work: what is wrong in the agent's file goes back to it, with the evidence. The
**records** of the stage belong to the head (`STATE.md`, `GOAL.md`, `docs/qa/`, adjustment rounds),
and so do the **requests**: the app↔flow contract that is missing before building, the spec of a
change, a one-line adjustment to a spec that the user asked for (e.g. a screen's description in
`mockups.json`). The **built artifacts** belong to the hand: screen, flow, procedure, DDL,
prototype, inventory.

## Contents

0. [Pipeline agents](#pipeline-agents)
1. [When to open one (and when not to)](#when-to-open-one-and-when-not-to)
2. [Disjoint scopes](#disjoint-scopes)
3. [How to launch](#how-to-launch)
4. [Mandatory output format](#mandatory-output-format)
5. [Standard deliverable for every agent](#standard-deliverable-for-every-agent)
6. [Completion contract](#completion-contract)
7. [Verify before reporting](#verify-before-reporting)
8. [Judging the deliverable](#judging-the-deliverable)
9. [Consolidating](#consolidating)
10. [Prompt templates](#prompt-templates)

## Pipeline agents

Defined in the plugin's `agents/` and called by the `/pp-en:*` stages with `subagent_type`
`pp-en:<name>`. Each one receives `RAIZ` (project root) and `KIT` (plugin folder, the stage's
`${CLAUDE_PLUGIN_ROOT}`), reads the project files and returns a deliverable in a fixed format.

| Agent | Stage | Tools | Writes to |
|---|---|---|---|
| `mockups-agent` | `/pp-en:mockups` | read + write, **no Bash** (does not call the image API) | `screen-inventory.md`, `mockups/mockups.json` |
| `prototype-agent` | `/pp-en:prototype` | read, write, Bash (verifier) | `prototype/index.html` |
| `architecture-agent` | `/pp-en:architecture` | read, write, Bash | `architecture.md` (with the procedures spec), ADR, DDL or Dataverse model, `GOAL.md`, config |
| `sql-agent` | `/pp-en:architecture` (one per group, in parallel), `/pp-en:build` (fix) | read, write, Bash (`lint-procedure.py`) | procedures folder, only those of its group |
| `canvas-agent` | `/pp-en:build` (`app`; one per group of up to 3 screens) | read, write, Bash (`validar-telas.py`) | the screens of its group |
| `automate-agent` | `/pp-en:build` (`flows`; one per group of up to 3 flows) | read, write, Bash (`verificar-fluxo.py`) | the flows of its group |
| `qa-agent` | `/pp-en:test` | read only + Bash for validators | nothing: the stage writes the report |
| `research-agent` | `/pp-en:brainstorm`, `/pp-en:architecture`, `/pp-en:build`, `/pp-en:change`, audit | read only + web search (no Bash, no write) | nothing: returns findings with sources |

**Research** is the decision-maker's hand: when the stage needs a fact (does the connector exist?
does it require a premium license? what does this error message mean? what already exists in this
folder?), the session asks the `research-agent` instead of reading everything or guessing. It
returns a finding with a source.

Brainstorm and Designer Branding are **not** subagents: a subagent does not talk to the user
(Claude Code removes the ask tool from it), so the stage session takes the role.

Canvas, Automate and SQL run **in parallel**, in the same message, writing to disjoint files: the
Files column of `GOAL.md` (and the groups of section 4.1 of the architecture) is what divides
them. At most 5 agents per message.
The calling stage always judges the deliverable (section "Judging the deliverable").

## When to open one (and when not to)

Open one **only** if both conditions hold:

1. The work is **independent** (one does not need the other's result).
2. It requires **broad reading** (several large screens, many procedures, a sweep of a whole app).

| Situation | Decision |
|---|---|
| One screen, one flow, one procedure | do it directly; an agent wastes context |
| Pipeline stage | the agent the stage says to call, nothing more |
| Audit the whole app (≥ 3 screens) | fan-out by **discipline** (ux, dev, performance, data) |
| Feature that touches screen + flow + database | one agent per layer, **after** the contract is closed |
| Investigate "the number doesn't match" | you drive the chain; an agent only to sweep sources or flows in parallel |
| Task already the size of one agent | **do not re-delegate**: whoever received it does it |

Do not use an agent to decide, to write the final report or to validate its own work.

## Disjoint scopes

Two agents on the same file and the same topic burn context and produce conflicting conclusions.
Split by **topic** or by **file**, never by both overlapping:

| Agent | Covers | Does not cover |
|---|---|---|
| `ux` | color, typography, spacing, hierarchy, accessibility | code convention, query cost |
| `dev` | naming, YAML structure, Power Fx anti-patterns, duplication | delegation, cost, column names |
| `performance` | delegation, number of requests, what loads when, timers | code style |
| `data` | where the data comes from, right source, columns, integrity | query cost |
| `flow` | flow skeleton, Try/Catch, authorization, contract, log | screen |
| `sql` | procedure, transaction, return, SQL delegation | flow, screen |

## How to launch

- **All in one message**, so they run in parallel.
- **Each agent's model:** `python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/modelos.py" de <agent>`.
  If it prints a name (`opus`, `sonnet`...): pass it as `model` in the call. If it prints an empty
  line: do not pass `model` (the agent inherits the session's). Profiles and swaps: `models.md`.
- Fill in the template: `{{PROJETO}}`, `{{RAIZ}}` (project root, relative or supplied at runtime —
  never a user's absolute path written to a file), `{{ESCOPO}}`, `{{OBJETIVO}}`,
  `{{ACHADOS_CONHECIDOS}}` (what is already known, with the command that verifies it — avoids
  rediscovery).
- Hand over the context the agent does not have: active track, path of `AS-BUILT-NAMES`, size of the
  large files, what is generated vs baseline.
- An agent **only reads** by default. Writing requires an explicit instruction and a disjoint file.
- **Questions first, in one round.** A subagent does not ask: what it would need to know
  (environment fact, pending decision, preference) the session asks the user **before** launching,
  all together. A question that comes back as "open" after the work is done usually costs a revision.
- **The request is a spec:** the exact files the agent may touch, what "done" means without
  ambiguity, the command that proves it and what is left out. Two requests that touch the same file
  run one after the other.

## Mandatory output format

Every finding comes with **reproducible evidence**: `file:line` **and** the command that finds it
again (`grep`, control/action name). A finding without evidence does not enter the report.

```
Severity | file:line | command that finds it again | Problem | Fix (before → after)
```

Mandatory sections on return: **confirmed** (with evidence), **inferred/unconfirmed**, **what was
not covered and why**. At most 25 lines of summary.

## Standard deliverable for every agent

Each pipeline agent has its own deliverable (files, tables, paste steps) and **always** closes with
the same four sections, so the judge reads them all the same way:

```
## How I verified
- <command that ran> → <the last line it printed>   (what did not run: "not verified")
## Compliance with the request
- Met | Partial | Deviation: <which item, and why>
## Alerts for the judge
- risks, poorly specified request, what to look at carefully
## Confidence
- high | medium | low, and why
```

Rules that apply to every agent:

- **"It should work" is not verification.** Only what was run and observed counts.
- **Never invent** a name, data, command output or a test that passed.
- **Do what the request says, nothing more.** Do not improve what was not asked; when in doubt
  about deleting something, take the narrowest reading.
- **Flawed or incomplete request:** do the safe part and state the rest in the alerts. Do not
  redesign silently.
- **Locate, read the excerpt, act.** Reading a whole file you do not need burns context.

## Completion contract

Applies to whoever delegates, at any depth:

1. **Your final message is the deliverable.** Never end the turn with "waiting for the agents": a
   pending agent does not notify someone who has already finished; its result is lost.
2. **Whoever delegates collects.** Wait, integrate and only then return. Delegating and leaving is
   forbidden.
3. **Decompose only when the work does not fit in one context.** Depth is a consequence, not a plan.
4. A child **executes** and returns; it does not open grandchildren for a task that already fit in it.

## Verify before reporting

Agents make mistakes. Reopen the strongest findings yourself (those that change the decision, those
of high severity and those that contradict what you knew):

- "empty file/folder" → list the folder.
- "variable never initialized" → count the assignments in **all** files (initializing in `OnSelect`
  is not absence).
- "column does not exist" → open the table schema.
- "N occurrences" → run the count command.

A finding you could not reproduce enters as **not verified**, not as fact.

## Judging the deliverable

Read the deliverable as a skeptic, not to rubber-stamp it:

1. **Proof, not promise.** Only what is in "How I verified" with command and output counts. Run the
   layer's validator again (the last line must match) and reopen 2 or 3 claims that change the
   decision (previous section).
2. **Request × deliverable.** Every item in the request (wave task, fix item, inventory screen) has
   an answer. Read first what came back "Partial" or "Deviation".
3. **Alerts** become a conscious acceptance, a revision or a question to the user. None is left
   without a destination.
4. **Verdict per agent:**

| Verdict | When | What to do |
|---|---|---|
| ✓ accepted | request met and proven | the stage continues |
| ↻ revision | something is missing that the agent can do | call the **same** agent with a tighter request: the missing item, the file, the criterion that failed and the validator output. Never "improve this" |
| ⚠ escalated | a decision or information from the user is missing, the request was wrong, or two revisions did not close it | checkpoint with the user: what was asked, what came back, the options |

5. **At most two revisions** per agent and per request in the same session; the third is escalated.
6. **Record each verdict**, one line per agent:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/estado.py" veredito <stage> \
     --agente <name> --resultado aceito|revisao|escalado --motivo "<one sentence>"
   ```

   `/pp-en:progress` shows how many revisions each stage needed: it is the proof that the judging
   ran, and the number that tells whether the executor's model is up to the job (`models.md`).
7. **Show the verdict** to the user in one line (`output-format.md` §4).

## Consolidating

Deduplicate, order by severity, attribute each finding to the agent that brought it, and state what
each agent did **not** cover. Conflict between agents: resolve it with the evidence, not by vote.

## Prompt templates

Each prompt runs as `pp-en:research-agent` (read only), with the model from
`modelos.py de research-agent`; the session consolidates and judges.

| File | When |
|---|---|
| `prompts/ux.md` | visual/accessibility review on ≥ 3 screens |
| `prompts/dev.md` | conventions, Power Fx, YAML, anti-patterns over a broad scope |
| `prompts/performance.md` | slowness, delegation, timers, loading |
| `prompts/data.md` | data source, columns, integrity, "the number doesn't match" |
| `prompts/flow.md` | flow audit |
| `prompts/sql.md` | procedure and SQL delegation audit |

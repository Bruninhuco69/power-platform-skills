# Output format of the `/pp-en:*` stages

All stages talk to the user the same way: someone who has never used the kit needs to know, on
any screen, **where they are, what to do now and what the next command is**. This is the standard.

## 1. Skeleton of every stage

1. `estado.py comecar <stage>`: checks the order and prints the banner. Exit 1 = stage out of order:
   show the script output and **stop** (it already carries the right command).
2. One sentence saying what will happen in this session and how much it asks of the user.
3. The stage's work (questions, agents, scripts).
4. Checkpoints whenever the user needs to decide, check or act in the environment (section 3).
5. Stage exit gate: what proves it finished (each stage skill says which).
6. `estado.py concluir <stage> --nota "<what is ready>"` (or `dispensar`/`reabrir`).
7. **Closing:** the stage summary (below) + the "Next step" block **exactly as the
   script printed it**. Do not invent another command: the script is the source of the next step.

Stage summary, short and without celebration. A line with no content does not appear:

```
**Delivered:** <files and what is ready>
**Verified:** <command → last line>, <what the user checked>
**Reviewed:** <agent: what came back and why>
**With you:** <what was escalated or left to decide>
**Not verified:** <what only the environment proves, or what could not be run>
```

If nothing was verified, the line says so in plain words.

Script command (Bash, from the project root):

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/estado.py" <command> [stage] [options]
```

## 2. Banner

`comecar` prints it. For transitions inside the stage, use the same format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PP ► IMAGE MOCKUPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 3. Checkpoints

Every stop that requires the user uses a 62-column box and ends with the expected action.
A closed decision goes through `AskUserQuestion` (recommended option first, with "(Recommended)").

```
╔══════════════════════════════════════════════════════════════╗
║  CHECKPOINT: Action in the environment                       ║
╚══════════════════════════════════════════════════════════════╝

<numbered step by step: where to click, what to paste, what to check>

──────────────────────────────────────────────────────────────
→ Type "done" when finished, or describe the error that appeared
──────────────────────────────────────────────────────────────
```

| Type | When | Expected action |
|---|---|---|
| `CHECKPOINT: Decision` | a choice that changes the result (data track, generating images) | pick an option |
| `CHECKPOINT: Review` | the user needs to see something (prototype, mockups, report) | "approved" or the adjustment |
| `CHECKPOINT: Action in the environment` | 🔴: only the human does it (create a table, paste into Studio, publish) | "done" or the error |

Rules: one open question at a time; closed choices that are independent of each other can go together
in one `AskUserQuestion` call (up to 4), and what an agent will need to know is asked before
calling it, in a single round; step by step with a real menu path; never ask for a password, key or token
in the conversation.

## 4. Agents

Before opening an agent, say who will work and what they deliver:

```
◆ Calling the Image Mockups Agent...
  → screen inventory, frame and image spec
✓ Image Mockups Agent finished: 7 screens, 12 images planned
```

Two agents in parallel go in the **same message**. An agent's finding or file is a hypothesis until you
judge it (run the validator, open the file): `references/subagents.md`, section "Judging the deliverable".
The verdict comes out on one line per agent:

```
✓ Power Apps Canvas Agent: accepted (validar-telas.py → 0 error(s), 4 files)
↻ Power Automate Agent: revision 1 — the delete flow does not return `id` in the Response
⚠ Architecture Agent: escalated — the PRD does not say who approves the return
```

## 5. Symbols

| Symbol | Meaning |
|---|---|
| ✓ | done, approved, verified |
| ✗ | failed, missing, blocked |
| ◆ | in progress |
| ○ | pending |
| ⊘ | skipped, with reason |
| ↺ | reopened (adjustment or fix) |
| ⚠ | attention |
| 🔴 | only the human does it, in the environment |

## 6. Error

```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

<what happened, in one sentence>

**To fix it:** <steps>
```

## 7. What not to do

- End the stage without the "Next step" block.
- Move on to the next stage in the same session: each stage starts in a new session (`/clear`),
  because it reads everything from disk and a clean context keeps stale decisions from leaking into the next one.
- Ask permission for obvious internal steps; ask only what changes the result.
- Jargon without explanation: the first time, say in one sentence what it is (e.g., "delegation: Power Apps
  sends the filter to the database instead of downloading everything").

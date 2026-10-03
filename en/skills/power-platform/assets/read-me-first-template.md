# <PROJECT> — read me first

**Idea:** <the idea in one sentence>
**Where the project stands:** `STATE.md` (updated at every stage). To continue, open Claude Code
in this folder and run `/pp-en:progress`: it shows the next command.

## Active track per layer

| Layer | Track | Folder | Since |
|---|---|---|---|
| Data | <to be defined in the architecture: `sql-server` or `dataverse`> | <folder> | <date> |
| Screens | Power Apps Canvas (`.pa.yaml`) | <`pastas.telas` from the config> | <date> |
| Flows | Power Automate (designer clipboard) | <`pastas.flows` from the config> | <date> |

One track per layer. Changing it requires an ADR in `docs/decisions/` and updates this table,
`power-platform.config.json` and `GOAL.md` in the same commit.

## Reading order

1. `STATE.md` — current stage and next command.
2. `docs/planning/prd.md` — what the app does and the MVP.
3. `docs/planning/architecture.md` and `docs/decisions/` — how and why (after stage 6).
4. `GOAL.md` — the build queue (after stage 6).
5. `AS-BUILT-ENVIRONMENT/AS-BUILT-NAMES.md` — real environment names; it wins over any plan.

## Folders

| Folder | Contents |
|---|---|
| `docs/planning/` | brainstorm, PRD, design system, screen inventory, mockups, prototype, architecture |
| `docs/decisions/` | ADRs |
| `docs/qa/` | test and UAT reports |
| `docs/delivery/` | user manual, technical guide, go-live checklist |

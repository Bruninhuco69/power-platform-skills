# Architecture — <PROJECT>

> Stage 6 (`/pp-en:architecture`), written by `pp-en:architecture-agent`. Record only what would conflict if two people decided alone; the rest lives in the code.
> Decisions have a stable id (AR-nn) so the stories can cite them. Standards already decided:
> `references/default-decisions.md` — diverging requires an ADR.

## 1. Data track
- **Track:** `sql-server` or `dataverse` (same as `power-platform.config.json`).
- **ADR:** `docs/decisions/ADR-001.md` (template `assets/adr-template.md`), with the criteria from
  `references/technology-matrix.md` and the answers to blocks 4, 7 and 8 of the brainstorm.
- **Reopened when:** <objective condition>.

## 2. As-built environment (N2 — before any screen or flow)
| Item | Source (command or capture, date) | Status |
|---|---|---|
| DEV/HML/PRD environments, publisher and prefix | | ⬜ |
| Real tables, columns and types (`AS-BUILT-NAMES`) | | ⬜ |
| Procedures (name, parameters, return) | | ⬜ |
| Connection references and environment variables | | ⬜ |
| Gateway, compatibility level, collation | | ⬜ |

## 3. Data model
Entities (`Order`, `Unit`, …), business keys, relationships, calculated columns, audit. Every
column the screens require (`screen-inventory.md`) is here.

## 4. Flows and app ↔ flow contract
| Flow | Called by | Parameters (positional, text) | Authorizes per action (flag) | Writes to |
|---|---|---|---|---|

Return contract: `{status, description, id, url}`; success is `status <> "error"`; `.Run()` inside
`IfError` (C1–C5). External input: its own HTTP trigger (C6).

### 4.1 Procedures (SQL track)
Spec of each procedure: it is the request to `pp-en:sql-agent` (one agent per group, in parallel).

| Procedure | Called by flow | Parameters (order, type) | What it does and rules | Possible `description` values | Scope and transaction | Group |
|---|---|---|---|---|---|---|

## 5. Security and scope
- Who blocks access by `Unit`: flow or security role; the screen only filters (A3).
- Roles and flags (T8); no resolved role, no access.
- Formally accepted risks (owner and date).

## 6. ALM
Solution(s), environment variables, connection references, the DEV → HML → PRD path, what goes by
paste and what goes by solution (`references/alm-environments.md`). No environment literals (F5).

## 7. Validators and gates
Which validators run (`validar-telas.py`, `verificar-fluxo.py`, `lint-procedure.py`) and what each
one **does not** cover (`references/final-gate.md`).

## 8. Decisions
| Id | Decision | Discarded alternative | ADR |
|---|---|---|---|
| AR-01 | | | |

## Exit gate
- [ ] Track ADR accepted; config and `00-READ-ME-FIRST.md` agree.
- [ ] Every column in the screen inventory exists in the model; real names, or marked "inferred".
- [ ] App↔flow contract closed for every write.

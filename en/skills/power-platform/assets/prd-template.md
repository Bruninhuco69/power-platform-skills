# PRD — <PROJECT>

> Stage 2 (`/pp-en:brainstorm`, Brainstorm Agent). Input: the log `docs/planning/brainstorm.md`.
> Every requirement has a stable id; the screen inventory, the architecture and `GOAL.md` cite these ids.
> An assumption goes in as `[ASSUMPTION: who confirms, by when]`. Examples: `Order`, units `AAA`, `BBB`.

- **Date:** YYYY-MM-DD · **Process owner:** <role> · **Requester:** <role>

## 0. Vision (one page)

- **Problem:** how the process runs today (who, with what tool, how often) and the 3 pain points.
- **Who uses it:** roles, number of users and of `Unit`s (pilot: `AAA`).
- **Expected outcome:** one sentence; is the delivery a full replacement or a parallel pilot?
- **How it was gathered:** brainstorm mode (guided interview, people focus, problem focus or
  round table).
- **Main role's journey** (people-focus mode): today → with the app, in 5 to 8 steps.
- **Problem with a number and main causes** (problem-focus mode): "X happens N times a
  month and costs Y"; causes outside the app go to assumptions or out of scope.

## 0.1 MVP scope

| Feature | MVP / Later / Won't do | Requirements | Who decided |
|---|---|---|---|
| <register `Order`> | MVP | FR-01 | <role> |

The MVP is the smallest set that already solves the main pain. Everything in the MVP becomes a P0
requirement.

## 1. Goal and success metrics
| Metric | How it is measured (command, report or query) | Target |
|---|---|---|

## 2. Roles and permissions
Permission by role **flag** (T8), never by name. No resolved role = no access.

| Action | Operator | Supervisor | Analyst | Admin |
|---|---|---|---|---|
| view `Order` | | | | |
| create `Order` | | | | |
| edit `Order` | | | | |
| export | | | | |
| manage users | | | | |

Intentional asymmetries (they look like errors, but are rules): <list>.

## 3. Scope by unit
- Scope: one, several or all `Unit`s per user; does "see all" apply to reading or also to
  writing?
- Is the scope **access control** or **screen convenience**? If control, who blocks (flow or
  security role) — A3.
- Test user per role, one from another unit (`BBB`), one multi-unit.

## 4. Functional requirements
| Id | Requirement | Role | Priority (P0/P1/P2) | Associated rule |
|---|---|---|---|---|
| FR-01 | The operator registers an `Order` for their `Unit` | operator | P0 | BR-01 |

## 5. Business rules
| Id | Rule | Source (person interviewed or code read) | Owner who confirms |
|---|---|---|---|
| BR-01 | | | |

Defects of the current system that are **not** copied: <list>.

## 6. Non-functional requirements
Volume per `Unit` and growth; acceptable response time; audit (what to prove: who, when, what);
retention; accessibility; devices; availability and support.

## 7. Integrations and files
System, direction (reads or writes), medium (file, API, database), real format, frequency, owner.

## 8. Compliance, license and infra (assumptions)
| Assumption | Approved by | Date | Document |
|---|---|---|---|

## 9. Out of scope
Item, reason, who agreed.

## 10. Open items

| # | Open item | Blocks | Owner | Deadline | If missed |
|---|---|---|---|---|---|
| D-01 | <does compliance accept cloud data, in writing?> | <stage or requirement> | <role> | <date> | <consequence> |

## 11. Traceability
FR-xx → screens (`screen-inventory.md`) → `GOAL.md` tasks. A requirement without a screen or task is
a gap; a screen or task without a requirement is hidden scope.

## Exit gate
- [ ] Every requirement has an id, role and priority; every rule has an owner.
- [ ] Permission matrix complete; scope by unit decided (A3).
- [ ] Compliance, license and infra assumptions with approver and date, or `D-xx` with an owner.
- [ ] User approved the MVP summary (sentence and date in the log).

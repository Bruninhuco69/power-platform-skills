# Power Platform project brainstorm

How the Brainstorm Agent (`/pp-en:brainstorm`, pipeline stage 2) runs the session, and the question
script that turns it into `prd.md`. The facilitation style is inspired by the BMAD Method's
`bmad-brainstorming` (see `pipeline.md` §7); the question script is specific to Power Platform. The
four ways to open the conversation (guided interview, people focus, problem focus, round table) and
the personas that lead them are in `references/brainstorm-modes.md`; the rules below apply to all
of them.

## Contents

1. [How to facilitate](#1-how-to-facilitate)
2. [Techniques](#2-techniques)
3. [Log](#3-log)
4. [Question script](#4-question-script)
5. [The questions that cost a lot if they come late](#5-the-questions-that-cost-a-lot-if-they-come-late)
6. [Session output](#6-session-output)

---

## 1. How to facilitate

1. **One question at a time.** No wall of questions. An **open** question (problem, pain, how it
   works today, ideas) goes in plain text, so the user can think; a **closed** question (MVP or
   later, yes or no, "I don't know") goes in `AskUserQuestion`, with the recommended option first:
   that is what makes the session easy for someone who has never done a requirements session.
2. **Diverge, then converge.** First generate a lot (ideas, possible screens, risks, rules) without
   judging; only then narrow down. Do not summarize early: the urge to wrap up is the enemy of
   divergence.
3. **The facilitator does not hand out the answers.** Ask, dig deeper, challenge. If the user asks
   for a suggestion, offer one recommendation and the reason — just one.
4. **An assumption does not become a fact.** "I think so" goes in as `[ASSUMPTION]` with an owner
   and a date to confirm.
5. **Start with the why.** The session goal in one sentence changes which techniques and questions
   are worth using.
6. **A blocker does not wait.** Security, infrastructure and license blocks that come back without
   an answer become a D-xx pending item with an owner and a deadline right then; without a formal
   answer, modeling does not start.
7. **An idea that dies cheaply is a win.** If the problem does not justify the app, record it and
   stop.

## 2. Techniques

Catalog from `bmad-brainstorming` (categories: creative, deep, collaborative, constraints,
speculative future, absurdist, biomimetic, quantum, cultural, introspective). The ones that pay off
most for Power Platform, in batches of 3 or 4:

| When | Technique | Use here |
|---|---|---|
| understand the real pain | Five Whys, Laddering | "why doesn't the current spreadsheet work?" until you reach the cause |
| find what breaks | Reverse Brainstorming, Failure Analysis, pre-mortem | "how would we make this app fail at Go Live?" |
| test premises | Assumption Reversal, First Principles | "what if the data could not leave the network?" |
| cut scope | One Feature Only, Ship in 60 Minutes, $0 Mandate | what is left in the pilot for one `Unit` |
| see from the other side | Role Playing | operator, supervisor, DBA, security, whoever pays for the license |
| derive rules | Question Storming, Morphological Analysis | role × action × unit combinations |

Converge (after the divergence): **affinity grouping** (many loose ideas), **impact × effort** (when
the goal is to act), **MoSCoW** (scope: must, should, could, not now), **forced ranking** (top N, no
ties), **PMI** (test one strong candidate).

## 3. Log

Keep a single session log in `docs/planning/brainstorm.md`, one line per item, with a type:
`mode` (choice or change of mode), `idea`, `insight`, `question`, `decision`, `direction`,
`technique` (technique change), `assumption`, `pending` (D-xx). In the round table, the line carries
the icon of the persona who raised the item: `idea (👤): …`. What is not in the log is lost; the PRD
is born from it, and it is what lets you stop and resume the session. At the end, write a short
synthesis with only the decisions and the directions chosen.

## 4. Question script

Each question has a code (`1.2`) so it can become a PRD item. Blocks 7 and 8 are **blockers**;
block 9 closes with an ADR.

### Block 0 — Identification and governance
| Code | Question |
|---|---|
| 0.1 | Name, acronym, pilot unit, process owner (who decides the rules) and requester? |
| 0.2 | Who is the IT focal point, DBA, security/compliance, support and change board? Are they named? |
| 0.3 | Target date, and **where does it come from**? Is there an irrevocable cutoff date? |
| 0.4 | How many people work in parallel (data and flows × screens)? |
| 0.5 | Is there a sibling project to use as a template? Which screen? |
| 0.6 | The owner's success criterion in 1 sentence; is "delivered" a full replacement or a parallel pilot? |

### Block 1 — Business and problem
| Code | Question |
|---|---|
| 1.1 | How does the process run today (spreadsheet, legacy app, e-mail)? Who does it, how much, how often? |
| 1.2 | What are the 3 pains that justify the project? Which operational error is the most expensive? |
| 1.3 | Which business rules exist today? List and number them `BR-xx` with their source (code read or person interviewed). |
| 1.4 | Which defects of the current system must **not** be copied? |
| 1.5 | Are there dead fields or structures? Who confirms they can be dropped? |
| 1.6 | What is out of scope and who agreed? Who uses what we cut? |
| 1.7 | Is there a controlled vocabulary, with accents or synonyms across systems? |

### Block 2 — Users, roles and scope
| Code | Question |
|---|---|
| 2.1 | Which roles exist? For each action (view, create, edit, download, approve, export, administer), who can do it? (permission matrix) |
| 2.2 | Are there asymmetries that look like mistakes but are intentional? |
| 2.3 | Is data scoped by `Unit`, region or area? Does a user have more than one unit? An arbitrary subset? |
| 2.4 | Does "see all units" apply only to reading, or to writing as well? |
| 2.5 | How does the user get access (group, role in a table, both)? Who provisions it and how fast? |
| 2.6 | How many users, in how many units, with what concurrency? |
| 2.7 | Who administers users? What does a user with no registration see? |
| 2.8 | Do DEV test users exist: one per role, one from another unit, one multi-unit? |

### Block 3 — Screens and UX
| Code | Question |
|---|---|
| 3.1 | Which screens exist today, in what order should they be delivered, and which can be cut (cut ladder)? |
| 3.2 | Target resolution and devices (desktop, tablet, phone)? |
| 3.3 | Brand and palette: colors in hex, or reference images to take them from; a single theme or light/dark? |
| 3.4 | Is there a template screen or canonical blocks (toast, loading, modal, menu) from the same team? |
| 3.5 | List screens: which filters, and how many rows are expected per filter? |
| 3.6 | Accessibility requirements; do color-coded states always come with text? |
| 3.7 | Which numbers appear as a KPI or counter, and what tolerance is there for "2,000+"? |
| 3.8 | Does the app need its own login or does it use the corporate identity? |
| 3.9 | Mockups (`/pp-en:mockups`): is there an OpenAI API key? Who provides it, in which account and with what cost cap? |

### Block 4 — Data and volumes
| Code | Question |
|---|---|
| 4.1 | Entities, relationships and business keys: what is truly unique? Is duplication allowed anywhere? |
| 4.2 | Current and projected volume per unit and per table; monthly growth; does any unit go over 2,000 rows? |
| 4.3 | Are there corporate tables the app only reads? Key, CHAR padding, columns, approved filter? |
| 4.4 | Where do calculated fields live (status, due date)? |
| 4.5 | Audit trail: which events, which fields, who reads it? |
| 4.6 | Legacy data: where is it, in what format and quality, who supplies it? Does it violate the new constraints? |
| 4.7 | Retention; logical or physical deletion; what does each status flag mean? |
| 4.8 | Is there a corporate standard for table, column and procedure names? |
| 4.9 | Time zone, date format and locale (thousands and decimal separators)? |
| 4.10 | Is there a dictionary **and** an as-built? Who checks one against the other? |

### Block 5 — Business rules and transactions
| Code | Question |
|---|---|
| 5.1 | Which operations write to 2 or more tables and must be "all or nothing"? |
| 5.2 | Who decides the rule: screen, flow, procedure or constraint? (one copy only) |
| 5.3 | Concurrency: two users on the same record; double click; idempotency? |
| 5.4 | Messages to the user: who writes them? Is there a closed vocabulary of result codes? |
| 5.5 | Which actions are irreversible? Who can do them? Is there an undo? |
| 5.6 | Which operations are long-running or batch (import, export)? Payload limit? |

### Block 6 — Integrations and files
| Code | Question |
|---|---|
| 6.1 | External systems: read, write, by file, API or database? |
| 6.2 | Imports: actual format, encoding, separator, sheet; full sync or append? |
| 6.3 | Exports: CSV (columns, separator), PDF or label (which converter?) |
| 6.4 | Who consumes the data outside the app (Excel, Power Query, Power BI), and with which identity? |
| 6.5 | E-mail and notifications: sender, list, recipients? |
| 6.6 | Identity: what is the user key (e-mail, UPN, table field)? |

### Block 7 — Security and compliance (**blocker**)
| Code | Question |
|---|---|
| 7.1 | Is there a premise that no data leaves the internal network? Who approved it? Is cloud accepted, in writing? |
| 7.2 | Data classification (personal, e-mails, financial)? Do the migration artifacts contain real data? |
| 7.3 | Is isolation by unit **access control** or a convenience? If control, is row-level enforcement mandatory? |
| 7.4 | Does the connector use a shared service account? Does the data layer know who the caller is? |
| 7.5 | Which tenant permissions (Graph, Entra) will be denied? Ask **before** designing. |
| 7.6 | What does the audit need to prove (authorship, when, what)? |
| 7.7 | Which risks does the owner formally accept? (record as accepted risk, with name and date) |
| 7.8 | Encryption at rest, backup, retention, disaster recovery? |
| 7.9 | Can the screen descriptions and the palette, with no real data, be sent to the OpenAI API to generate the mockups? Who approves? |

### Block 8 — Infrastructure, IT, DBA and licenses (**blocker**)
| Code | Question |
|---|---|
| 8.1 | Power Platform DEV/HML/PRD environments; publisher and prefix; solution; who creates them? |
| 8.2 | Database: on-premises SQL Server or Azure SQL? Server, instance and database per environment? **Is there a gateway?** |
| 8.3 | Version and compatibility level (>= 130 for `OPENJSON`), collation, isolation? |
| 8.4 | Who runs DDL, how fast, with what approval? **When does the database freeze**, and what still fits afterward (calculated column, new object)? |
| 8.5 | The DBA's standard for procedures (name, schema, `GRANT EXECUTE`, service account)? |
| 8.6 | Licenses: Power Apps (per app or per user), Power Automate, Premium connectors (SQL, Dataverse, converters), Dataverse capacity, AI Builder? |
| 8.7 | ALM: solution, connection references, environment variables; are `pac` and `az` available? |
| 8.8 | Change process: board, deployment window, approvers, lead time? |
| 8.9 | Post-Go Live support: who answers, SLA, channel? |
| 8.10 | Have captures of the real environment been taken (tables, columns, connection references, procedures)? |

### Block 9 — Technology choice (**decision with an ADR**)
9.1 Dataverse, SQL Server or something else (criteria in `technology-matrix.md`)? 9.2 Does Power BI
come in, and for what? 9.3 Canvas or model-driven (and why)? 9.4 Writes by `Patch`, flow or
procedure? 9.5 What stays **outside** Power Platform?

### Block 10 — QA, UAT and Go Live
| Code | Question |
|---|---|
| 10.1 | Acceptance criterion: a complete end-to-end cycle, with real data, by a real operator? |
| 10.2 | Who does UAT, in which environment, with what data set, when; who signs off? |
| 10.3 | Does the legacy system run in parallel? Until when? Shutdown plan? |
| 10.4 | Rollback plan (data and app) and communication plan? |
| 10.5 | Hypercare, training, user manual? |
| 10.6 | Is there a synthetic data set above 2,000 rows to test delegation? |

### Block 11 — Planning
11.1 Breakdown into waves with gates and criteria; 11.2 non-goals and cut ladder; 11.3 risks with a
warning sign and an action; 11.4 🔴 environment pending items: who, when, how long it takes; 11.5
definition of done per delivery.

## 5. The questions that cost a lot if they come late

Ask them on **day one**; each one, answered after the screen is done, usually means a redesign.

| Question | Code | If it comes late |
|---|---|---|
| Will tenant permissions (groups, Graph) be denied? | 7.5 | access design redone; the flow becomes an IT ticket |
| Publisher prefix and real environment names | 8.1, 8.10 | batch fixes across screens; creation script useless |
| Does compliance accept cloud data, in writing? | 7.1 | risk of stopping the whole project |
| Is there a gateway between the cloud and the database? limits | 8.2 | large exports and procedure returns break |
| Will the DBA freeze the database? when? | 8.4 | correct proposals become impossible |
| Premium connector license and capacity | 8.6 | the app cannot be used by the people who should use it |
| Who uses what will be cut from the legacy system? | 1.6 | scope in dispute during Go Live week |
| Scope by unit: one, several or all? | 2.3 | data model and filters redone |
| Real data vocabulary (accents, statuses, types) | 1.7, 4.6 | empty combo boxes and stuck buttons |
| Real names of procedures and connection references | 8.10 | flow queue rewritten by hand |

## 6. Session output

- `docs/planning/brainstorm.md` (log + decision synthesis).
- List of D-xx pending items with owner and date (goes into section 2 of `GOAL.md`).
- `docs/planning/prd.md` from the template `assets/prd-template.md`, with the MVP scope approved by the user.
- Gate: blockers 7, 8 and 9 answered formally, or a D-xx with an owner and an open deadline.

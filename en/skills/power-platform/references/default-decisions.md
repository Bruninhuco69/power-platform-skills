# Default decisions

Single source of the defaults that apply to every project. The other skills point here instead of
repeating them. A project may diverge, but only with an ADR that says which decision changes and why.

Origin: the analysis of two reference projects in production, one on SQL Server + procedures and
the other on Dataverse.

## Contents

1. [Architecture](#1-architecture)
2. [App ↔ flow contract](#2-app--flow-contract)
3. [Separators and Power Fx dialect](#3-separators-and-power-fx-dialect)
4. [Screens](#4-screens)
5. [Flows](#5-flows)
6. [Database](#6-database)
7. [Environment and names](#7-environment-and-names)
8. [Process](#8-process)

---

## 1. Architecture

| # | Decision | Why |
|---|---|---|
| A1 | **The screen does not write directly to the source.** A write with business rules goes through a flow; the flow calls the procedure (SQL) or writes to Dataverse. | A client-side rule can be bypassed and ends up duplicated on every screen. |
| A2 | **The flow decides; the procedure executes.** The flow normalizes, validates, authorizes and translates the result code into a message. The procedure opens the transaction, writes and returns a code. | Concentrates the rule in one place editable without a DBA; the database tends to freeze in production. |
| A3 | **Scope on the screen is UX, not access control.** The per-unit filter on the gallery helps navigation; the flow is what blocks. | The connector's service account is shared; the client can be tampered with. |
| A4 | **One data track per project** (`sql-server` **or** `dataverse`), declared in `power-platform.config.json` and in `00-READ-ME-FIRST.md`. Switching tracks requires an ADR. | Two live tracks with documents pointing to the wrong one cost days of rework. |

## 2. App ↔ flow contract

| # | Decision |
|---|---|
| C1 | Flow response to the app: **`{ status, description, id, url }`**, all text. `status` ∈ `success` \| `warning` \| `error`. |
| C2 | `description` is the sentence ready for the user, built in the flow. The procedure returns a **code** (ASCII, closed vocabulary); the flow translates it. |
| C3 | In the app, **success is `status <> "error"`** (`warning` also closes the modal) and every `.Run()` call sits inside `IfError`. |
| C4 | Power Apps V2 trigger parameters are **positional and text**. A new parameter **always goes at the end**. A numeric id goes as `Text(id, "[$-en-US]0")`. |
| C5 | After writing: `Refresh(<source>)` + recount of the screen's counters. |
| C6 | Input from an external system uses its own **HTTP** trigger, separate from the flows called by the app. Token in the header (validation and cache: `power-automate/references/http-external-inbound.md`); response derived from the real validation status. |

## 3. Separators and Power Fx dialect

| Where the code goes | Argument | Chain | Decimal |
|---|---|---|---|
| Studio **formula bar** in a pt-BR locale (e.g. `App.OnStart` typed in) | `;` | `;;` | `,` |
| **Pasted YAML** in Studio (`.pa.yaml`, screens and components) | `,` | `;` | `.` |

Mixing the two does not parse. Every code block in a skill or a document states its destination.
`[verified: reference projects]`

## 4. Screens

| # | Decision |
|---|---|
| T1 | **ManualLayout + Classic controls** layout, fixed canvas (1920×1080 in the reference projects). AutoLayout/Modern stay outside the default until a project proves it in Studio. |
| T2 | `Control: Type@version` **with** the exact version already used in the app. |
| T3 | Color, font and size only through `fx*` tokens (named formulas). No literal `RGBA(` on a screen. |
| T4 | A new property only if the app already uses it on that control type (Studio rejects the whole block with PA2108). |
| T5 | Control name `<screen-prefix>-<type>-<module>-<element>` in kebab-case; unique in the app. |
| T6 | Every global variable is born in `OnStart`. A named formula does not depend on a global variable. |
| T7 | Delegation declared in writing in each screen's header (what delegates, what does not, the cap). |
| T8 | Permission by role **flag** (`Flg_PodeX` / `pode_x`), never by role name. No resolved role = no access (fail-closed). |

## 5. Flows

| # | Decision |
|---|---|
| F1 | Skeleton: `CONFIG` → identify the caller → `Try { authorize per action → normalize → validate → write → respond }` → `Catch` listening for `Failed`, `TimedOut` **and** `Skipped` → `Response`. |
| F2 | Authorization **per action** (each `Switch` case checks its own flag), never a single gate. |
| F3 | The safety switch is born **on** in the flow's `CONFIG`. Not to be confused with the role's **permission flag** (`Flg_PodeX`), which is born **off**: nobody gets permission by default. |
| F4 | **Execution log in every flow** (`Log` scope with `runAfter` on Succeeded/Failed/TimedOut). Intentional exception to F1: `Log` does not listen for `Skipped`. Log destination when the data is in SQL: **open** — see the project's ADR. |
| F5 | No literal environment, server or `dev*` table name: environment variable + connection reference. |
| F6 | Delivery by paste in the designer: the pasted file is the **baseline**; a generator never writes over it (it writes to `dist/`). |

## 6. Database

| # | Decision |
|---|---|
| B1 | Write procedure: `SET NOCOUNT ON; SET XACT_ABORT ON;`, a transaction, returns **1 row** with `status, description, id, url`. |
| B2 | Date filtered by the app through an integer computed column `Ref_<col> AS DATEDIFF(day, 0, <col>) PERSISTED` (a direct date filter does not delegate behind a gateway). Never `CAST(... AS INT)` — it rounds. |
| B3 | Counting in the app over SQL: `CountRows` does not delegate; show a cap (`2,000+`) or count on the server. |
| B4 | A production database tends to freeze: a new table and a signature change go through the DBA; a computed column is usually accepted. Plan the schema before the first deploy. |

## 7. Environment and names

| # | Decision |
|---|---|
| N1 | **`AS-BUILT-NAMES.md` is the authority on names** — tables, columns, types and procedures read from the real environment. The dictionary, the creation script and the plan lose to it. |
| N2 | No screen or flow before `AS-BUILT-ENVIRONMENT/` is filled in (project folder with environments, connections and `AS-BUILT-NAMES.md`). |
| N3 | Before claiming a column does not exist, open the table's schema — never a filtered extract. |

## 8. Process

| # | Decision |
|---|---|
| P1 | Git from day 0. |
| P2 | A single queue (`GOAL.md`); every ✅ task has an **Evidence** column (command + output + date). |
| P3 | Generator output marked "generated — do not edit"; a manual fix goes to the generator's input. |
| P4 | A validator that never flagged anything has not proved it validates: every gate has a test that plants the error. |
| P5 | A document that states a number (count, baseline) carries the command that measures it. |

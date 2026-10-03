# Contract · dbo.usp_<SIGLA>_<Entidade>_<Acao>

> Template. Copy it into each procedure's contract and fill it in. Delete what does not apply, do
> **not** leave a field empty. When there is a generator, this file is **generated** from the `.sql`
> and the flow; written by hand it goes stale the day it is written. Procedure name: the **real** one
> in the environment (`sys.procedures`).
>
> Standards: `power-platform/references/default-decisions.md` (A2, C1, C2, B1).
> How the procedure is written: `sql-procedures/references/procedure-standard.md`.

| | |
|---|---|
| Procedure (as-built) | `[dbo].[<real name>]` verified on `<YYYY-MM-DD>` |
| Variant | declarative / classic (see `procedure-standard.md` §5) |
| Called by | flow `<flow name>`, action `<action name>`, case `<action>` |
| Irreversible operation? | yes / no |
| Minimum SQL Server version | `<e.g. 2016 SP1, COMPATIBILITY_LEVEL >= 130 if using OPENJSON>` |
| State | draft / on hold (`<reason>`) / handed to the DBA on `<date>` / in production |

## 1. Origin

Which screen/flow action it replaces or serves. Use the **control and action** name, never a line
number (line numbers go stale). If a command finds the snippet again, write it down.

| Item | Value |
|---|---|
| Screen / control | `<control name>`, property `<OnSelect>` |
| Flow action | `<name>` |
| Business rule it carries | `<BR-xx or short text>` |

## 2. Signature

Class: (a) target PK · (b) column value already normalized and validated by the flow · (c)
`@Id_UsuarioChamador` · (d) trail row value · (e) conditional `BIT` flag.

| # | Parameter | Type | Class | Required | Content / origin | Who validates |
|--:|---|---|:--:|:--:|---|---|
| 1 | `@Id_<Entidade>` | `INT` | a | yes | target PK | flow (exists and is active) |
| 2 | `@Des_<Coluna>` | `NVARCHAR(<n>)` | b | yes | `<origin>`; type and size = the column's | flow (domain, size) |
| 3 | `@Tp_Evento` | `NVARCHAR(30)` | d | yes | built by the flow | flow |
| 4 | `@Id_UsuarioChamador` | `INT` | c | yes | from the `Id_Usuario` returned by the caller resolution | flow |

Parameters the procedure **deliberately does not have**: `<e-mail, message, audit date,
unit viewed, ...>`, and why.

Literals that stay **in the body** (never in a parameter): `<expected state in the WHERE, fixed origin>`.

Count: `<N>` parameters. The flow must bind `<N>`, **in the same order**; a new parameter goes
**at the end**.

## 3. Return

1 result set, 1 row, `status` / `description` (code) / `id` (text) / `url` (`''`), in **every**
outcome, including zero rows written.

| status | description (code) | Meaning in the database | Sentence (owner: the flow) |
|---|---|---|---|
| success | `<OK_CODE>` | wrote | `<sentence with the id>` |
| warning | `NAO_APLICADO` | the state predicate did not match: 0 rows | flow **re-reads** and explains |
| error | `<REFUSAL_CODE>` | only the lock knows (duplicate under `UPDLOCK, HOLDLOCK`) | `<sentence>` |

Infrastructure failure (deadlock 1205, timeout, constraint, `THROW`): the **connector action fails**;
the flow's `Catch` builds the message. There is no code for this.

## 4. Rules applied

| Rule | Where it lives | What it rejects | Before which write |
|---|---|---|---|
| `<BR-xx>` | flow / `WHERE` predicate / database | `<what>` | `<statement>` |

A rule that **moved up to the flow** and that the database does not repeat: list it, with the reason
and the matching flow obligation (`proc-flow-contract.md` §3). **This is what keeps the rule from
disappearing with no owner.**

## 5. Sequence

Inside the transaction: mark what is transactional.

1. `SET NOCOUNT ON; SET XACT_ABORT ON;`
2. **[tx]** `UPDATE ... WHERE <PK> AND <expected state> OUTPUT ... INTO @sink`
3. **[tx]** `INSERT <trail> ... SELECT ... FROM @sink` (empty sink: zero rows)
4. `COMMIT`
5. `SELECT TOP (1) ... FROM (VALUES ...)`: return

## 6. Tables touched

| Order | Table | Operation | Note |
|--:|---|---|---|
| 1 | `dbo.<SIGLA>_<Entidade>` | UPDATE | `Dt_Alteracao` trigger active: `OUTPUT` with `INTO` |
| 2 | `dbo.<SIGLA>_<Entidade>Trilha` | INSERT | same transaction |

Concurrency: `<state predicate / UPDLOCK+HOLDLOCK on ... with index ...>`.
Idempotency: `<what happens on double click and on retry>`.

## 7. Flow obligations

Check the ones that apply (full list in `proc-flow-contract.md` §3):

- [ ] resolve the caller in the trunk and send the `Id_Usuario` as `@Id_UsuarioChamador`
- [ ] authorize by **this** action's flag: `<Flg_...>`
- [ ] normalize, validate and derive `<fields>`; cut text to the column size
- [ ] send the **record's** unit; resolve `@Unidade_Escopo` (`null` ≠ `''`)
- [ ] translate the code in a `Switch` with a `default` that responds `error` naming the code
- [ ] `Catch` with `Failed`, `TimedOut`, `Skipped`; rerun 1205 with a limit
- [ ] do not call when there is nothing to write

## 8. Open items for the DBA

| Tag | Open item | Blocks |
|---|---|---|
| ⬜ DECIDE | `<business or environment question with no answer>` | `<this object>` |
| ⚠ | `<live blocker>` | `<...>` |

DDL needed (request in `dba-ddl-request-template.md`): `<computed column, index, FK, trigger>`.
Environment proofs it depends on: `<compat level, OUTPUT INTO with trigger, collation>`.

## 9. Acceptance tests

| # | Input | Expected |
|--:|---|---|
| 1 | happy path | 1 result set, 1 row, 4 columns; `status = success`; trail with 1 row |
| 2 | identical second call (double click) | `warning` / `NAO_APLICADO`; zero writes |
| 3 | `<value that violates the state predicate>` | `warning` / `NAO_APLICADO` |
| 4 | `<race: two sessions>` | exactly one writes; the other receives `<REFUSAL_CODE>` |
| 5 | error forced mid-batch | `@@TRANCOUNT = 0`, nothing written, and the connector action **fails** |

Command that runs the lint: `python <skill-folder>/scripts/lint-procedure.py <folder>` → `0 error(s)`.

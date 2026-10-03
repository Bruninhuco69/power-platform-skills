# Field lessons: SQL Server backend

Defects and decisions that showed up in real projects and that did not yet fit a rule on their own in
the other references. Each lesson says what happened, in generic terms, and the rule or file that
prevents it. It is not a rule by itself: what counts is in the files cited.

## Contents

1. [Adversarial review finds gate defects, not logic defects](#1-adversarial-review-finds-gate-defects-not-logic-defects)
2. [A deliberate divergence disappears if it is not written where the next person reads](#2-a-deliberate-divergence-disappears-if-it-is-not-written-where-the-next-person-reads)
3. [Migration package written for the proposed schema](#3-migration-package-written-for-the-proposed-schema)
4. [A new lint: classify the false positives and prove it flags](#4-a-new-lint-classify-the-false-positives-and-prove-it-flags)
5. [The cost of the declarative decision, measured](#5-the-cost-of-the-declarative-decision-measured)

---

## 1. Adversarial review finds gate defects, not logic defects

| | |
|---|---|
| **What happened** | Reviewers instructed to **break** the bodies of the declarative procedures found defects that no functional test caught, because the procedure *works*. None required going back to `IF` or `TRY/CATCH`: all were closed with one more predicate, one more `OUTPUT` column or a DDL. |
| **The patterns** | (a) Two chained writes that pointed to different rows of the same link: the `OUTPUT` returns the **written** link and the next statement matches by it. (b) `NULL` in a parameter corrupts the column **and** silences the trail that would record it: `IS NOT NULL` in the gate (fails closed, nothing is written). (c) An "irreversible" operation reverted by another: the terminal state goes into the predicate (`<> N'encerrado'`). (d) Writing to a child record of a nonexistent target returned success without writing: `EXISTS` of the target in the gate, or a `FOREIGN KEY` (checking the load's orphans first). (e) A duplicate guard blind to `NULL` and `''`: the predicate handles both explicitly (a product decision built in). (f) Two edits that swap values between rows caused a deadlock (1205): the flow treats it as transient. (g) A probe that excludes itself through a raw parameter: closing it required a new lock order, with deadlock risk; it stayed as a flow obligation. |
| **Prevents** | `procedure-standard.md` §6 (the predicate plays the role of the `IF`), §8 (guard and lock), §10 (parameters), §12 (retry and idempotency); `proc-flow-contract.md` §3 (flow obligations). Before delivering, run the adversarial review by thirds of the package. |

## 2. A deliberate divergence disappears if it is not written where the next person reads

| | |
|---|---|
| **What happened** | The property "the procedure body is identical to the source, byte for byte" stopped holding for some bodies after the review patches. The divergence was recorded only in the letter to the DBA. When a record like that disappears from there, the next person "fixes it back" and reopens the defect. A test also changed result (from success to `NAO_APLICADO`): it was the fix, not a regression, and went in as a declared behavior change. |
| **Prevents** | `deploy-and-dba.md` §1 and §7 and `assets/procedure-contract-template.md` §4/§8: the divergence goes in the procedure contract, not only in the letter; a behavior change by fix is declared as such. |

## 3. Migration package written for the proposed schema

| | |
|---|---|
| **What happened** | The load package was written for the **proposed** schema (`snake_case` names, its own schema), and the DBA built another (`dbo`, corporate prefixes). The bridge between the two, how the final load file was generated, was not documented. The problems that only appeared against the real schema: accents (`Disponivel` × `Disponível`), a different status vocabulary, two text fields **swapped**, empty identity, a role seed retyped by hand with wrong cells. |
| **Prevents** | `data-migration.md` §1 (map against the real environment) and §6 (collation and accents). The layer of names and vocabularies is a versioned part of the package, and the reconciliation runs against the real schema, not the proposed one. |

## 4. A new lint: classify the false positives and prove it flags

| | |
|---|---|
| **What happened** | The lint run read-only over the procedures folder of a project (`.md` with `sql` blocks and deploy `.sql`) gave, on the first pass, **zero errors and a few warnings, all false positives**: documentation fragments that show only the signature (`CREATE ... AS` with no body) and names with a placeholder (`usp_<SIGLA>_<Entidade>_<Acao>`). The lint now treats both as documentation. Against migration scripts, `P009` (dynamic SQL) is a documented false positive: internal metadata names via `QUOTENAME`, dismissible with `-- lint-ok P009` and a one-sentence justification. `P005` found a real error: a staging helper procedure with the `sp_` prefix, reserved by the product. |
| **Prevents** | `SKILL.md` (Scripts section: `-- lint-ok` with a justification) and rule P4 of `default-decisions.md`: to prove the validator flags, make a mutation (remove `SET XACT_ABORT ON` from a procedure) and check that `P002` appears. |

## 5. The cost of the declarative decision, measured

| | |
|---|---|
| **What happened** | When the procedures were rewritten in the declarative form (no `IF`, `WHILE`, `TRY/CATCH`, cursor, rule `CASE` or `SCOPE_IDENTITY()`), the code shrank to a fraction and the flow `Catch` compensations (undo `DELETE`s) ceased to exist: `XACT_ABORT ON` rolls back by itself. In exchange, the procedure stopped being the last control point, the trail stopped proving **who**, infrastructure errors began to arrive as a connector action failure, and distinct sentences became `NAO_APLICADO`. A single domain rule stayed in the database, as a predicate of an `AND` clause, with the caveat that it can be spoofed. The first proposal to reduce the code vocabulary to a few values was not the one implemented: one code per outcome that the user needs to tell apart was kept. |
| **Prevents** | `procedure-standard.md` §4 (vocabulary), §5 (declarative vs classic, the cost without softening) and `security-and-permissions.md` §5 (the limit of the caller by parameter). |

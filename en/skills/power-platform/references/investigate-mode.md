# Investigate mode — "the number doesn't match"

Use before proposing any code for: a number that differs between screens, a KPI different from the
gallery, "it's slow", "it doesn't refresh", "it saved but doesn't show up". One rule: **root cause
proven before the fix**. Don't guess; if the evidence doesn't close the case, say what is missing.

## Contents

1. [The chain](#the-chain)
2. [Method](#method)
3. [Suspects by symptom](#suspects-by-symptom)
4. [Proofs that close a hypothesis](#proofs-that-close-a-hypothesis)
5. [Investigation report](#investigation-report)

## The chain

Walk from the consumer back to the source. Each link has a question and a proof.

| Link | Question | Proof |
|---|---|---|
| 1. Screen | Which control shows the number and which property calculates it? | `Grep` for the control name; exact formula quoted |
| 2. Formula | Does it delegate? Does it use a global variable, a named formula or a collection? When does it recalculate? | delegation table (skill `powerapps-canvas`); Monitor |
| 3. Source | Does the screen read the right source? Are there two sources (dev × production, table × view)? | list of the sources used by the two numbers, side by side |
| 4. Flow | Did the flow write? Did the contract really return `success`? Did the app redo `Refresh` + recount? | run history; response of `.Run()` |
| 5. Procedure | Did it return the expected code? Did it write inside the transaction? | `EXEC` with test data; result |
| 6. Data | Does the record exist, with the expected value and unit? | direct query to the database/Dataverse |

## Method

1. **Reproduce it from the code.** Find the exact formula behind each disputed number and cite the
   control/action and the command that locates it (not just `file:line`, which goes stale).
2. **Compare the competing paths.** The same data read in two places with different filters,
   sources or calculation moments is the most common cause of divergence.
3. **List hypotheses** (max. 5), from the cheapest to prove to the most expensive. For each one:
   what would confirm it, what would knock it down.
4. **Prove one at a time.** Record the result (confirmed / ruled out / inconclusive) with the
   evidence.
5. **Separate cause from symptom.** A "wrong" formula is often a symptom of a wrong source, silent
   delegation or a counter not recalculated after the flow.
6. **Only then propose the fix**, as before → after, and say how to prove it (the command or the
   Studio step that shows the number matching).
7. Ask yourself: "does this cause explain **all** the symptoms?" If it explains only part, there is
   a second one.

## Suspects by symptom

Check these before opening the code; start with the ones that cost the least to rule out.

**KPI/counter different from the gallery**

- Two sources (development environment × production): compare the source name in the two
  formulas. It is not a formula bug.
- `CountRows`/`CountIf` over SQL does not delegate: the number truncates at the cap (500/2,000)
  with no warning.
- A named formula that depends on a global variable only recalculates when the variable changes;
  `Refresh()` does not re-run it. A counter like that goes in `Screen.OnVisible`.
- Missing `Refresh(<source>)` + recount after writing (C5).
- `IfError(..., <number>)` that swaps the error for a "plausible" value (e.g., the aggregation cap).

**Date filter doesn't match or drops rows**

- A date filter applied directly over SQL behind a gateway does not delegate; use an integer
  calculated column (B2).
- Time zone: UTC in the database × local time on the screen.
- Comparing a date with a time (end-of-day limit) and a missing `ne null`.

**Empty gallery / incomplete list with no error**

- `SearchFields`/`SortByColumns`/`DisplayFields` with a column name that **exists in the source but
  is not the intended one**, or a **display name instead of the logical name** (a quoted string =
  logical; see `dataverse/references/names-and-types.md`): it raises no error, it gives an empty
  gallery (N3).
- Choice compared as text, Lookup as text, text as Choice.
- `in`/`Search` over a data source does not delegate: it truncates silently.
- Uninitialized filter variable (`Blank() = 0` is false).

**"Saved but doesn't show up" / "doesn't refresh"**

- `.Run()` without `IfError`; success tested as `= "success"` when `warning` also closes the modal
  (C3).
- Numeric id sent without `Text(id, "[$-en-US]0")`: in the pt-BR locale it becomes `"1.234"`.
- Trigger parameter out of order (parameters are positional).
- The flow failed and the `Catch` doesn't listen for `Skipped`; a generic response hides the cause.
- Scope by unit: the flow blocked it (authorization per action) and the screen only showed a generic
  message.

**Slowness**

- Timer with `Repeat` and no stop condition; chained `Refresh()`.
- Query in `Visible`/`Text` of a control inside a gallery.
- `OnStart` loads everything before it is needed; missing `Concurrent`.
- Measure in Monitor before claiming a bottleneck: it is the only reliable way to prove data cost.

## Proofs that close a hypothesis

- Power Apps Monitor: which calls, how many rows, how long.
- Direct database query (`SELECT COUNT(*)` with the same predicate as the screen).
- Flow run history (inputs, outputs, which action failed).
- `EXEC` of the procedure with test data; a 1-row result.
- Table schema opened in full (not a filtered extract) to confirm column name and type.

A claim about the platform needs a documentation link; if the documentation doesn't say, write
"[unverified]" and say how to verify.

## Investigation report

| Hypothesis | Proof | Result |
|---|---|---|
| H1 … | command/capture | confirmed / ruled out / inconclusive |

Then: **root cause** (1 sentence), **why the symptoms appear**, **fix** (before → after), **how to
prove it** and **what was not investigated**. With the fix applied, run the final gate
(`final-gate.md`) and show the number matching.

# Field lessons: Canvas

Patterns that showed up in real apps and did not yet fit an isolated rule in the other
references. Each lesson gives what happened, in generic terms, and the rule or file that
prevents it. It is not a rule by itself: what counts is in the files cited.

## Contents

1. [Batch migration to tokens has a remainder that cannot be automated](#1-batch-migration-to-tokens-has-a-remainder-that-cannot-be-automated)
2. [A unified pattern across screens: apply the decision sheet and record the exceptions](#2-a-unified-pattern-across-screens-apply-the-decision-sheet-and-record-the-exceptions)
3. [An app that grows without a decision sheet diverges on every axis](#3-an-app-that-grows-without-a-decision-sheet-diverges-on-every-axis)
4. [A claim about the disk, repeated across several files, goes stale](#4-a-claim-about-the-disk-repeated-across-several-files-goes-stale)
5. [The validator on an existing project: what to expect](#5-the-validator-on-an-existing-project-what-to-expect)
6. [Unifying separators without looking at the file's destination](#6-unifying-separators-without-looking-at-the-files-destination)
7. [A text-catalog rule with no automatic check gets lost](#7-a-text-catalog-rule-with-no-automatic-check-gets-lost)

---

## 1. Batch migration to tokens has a remainder that cannot be automated

| | |
|---|---|
| **What happened** | In a large app, replacing `RGBA()` literals with `fx*` tokens removed more than half of the literals by script. What was left was inside multi-line formulas (status `Switch`/`If`), where automatic replacement is not safe. In the same app, almost all automatic control names stayed as they were: renaming in batch is only safe with Studio open to check the references, and only one control was renamed (the timer that was being fixed). Of the flow returns that used `Notify()`, a fraction became a toast; the rest was form validation, correct use. |
| **Prevents** | `design-tokens.md` §1 item 4 (what remains in a multi-line formula migrates to `fxBadge*`, checked by hand), `naming.md` (name from creation, so there is no need to rename later) and `flow-call.md` (`Notify()` is for form validation). |

## 2. A unified pattern across screens: apply the decision sheet and record the exceptions

| | |
|---|---|
| **What happened** | The flow-return toast, loading overlay, modal button pair, filter buttons, column header, selection counter and empty state became **identical blocks across screens**, with geometry and color coming from a token. The decision sheet was applied with few documented exceptions, where the ideal option would require repositioning each control at an absolute `X`/`Y`: the modal card's default size, closing by clicking the scrim, the gallery row height. On two screens, the z-order was also fixed (modal above the toast; modal above the loading). |
| **Prevents** | `ux-components.md` and `ux-feedback.md` (canonical blocks), `app-formulas-tokens.md` (geometry and color by token) and `validar-telas.py` T016 (z-order). In ManualLayout, what depends on absolute position is a declared exception, not an oversight. |

## 3. An app that grows without a decision sheet diverges on every axis

| | |
|---|---|
| **What happened** | The screen-by-screen visual audit of an app without a decision sheet found: a single accessibility control among hundreds of controls; no use of `Live` or `Role`; positive `TabIndex` values scattered around; more than ten color pairs failing contrast (placeholder, badge, white on green and on amber, input borders and divider below 3:1); several side margins, several header variants and gutters of very different widths; two type families with no rule; `TemplateSize` disconnected from the content (hundreds of pixels for a line of tens); a cleanup screen with its own loading language; three different greens for "positive action"; the destructive confirm button painted green; and a screen with hundreds of controls that should have been three. |
| **Prevents** | `design-tokens.md` (token families and measured contrast), `accessibility.md`, `ux-components.md` and `ux-feedback.md` (destructive confirmation uses `fxColorError`), `performance.md` §7 (controls per screen) and `anti-patterns.md` (U9, large screen). Use this list as an audit script. |

## 4. A claim about the disk, repeated across several files, goes stale

| | |
|---|---|
| **What happened** | A project's documentation repeated, in almost a dozen files, three claims about the disk that were out of date: that two screens were byte-identical (false, with different sizes and hashes; the serious effect was telling the agents to **ignore** the more up-to-date screen), that a polling "never stopped" (already fixed) and that a folder was empty (it already had files). |
| **Prevents** | `anti-patterns.md` P2 and P4 and `default-decisions.md` P5: every claim about the disk carries **the command that measures it** (for example `md5sum a.md b.md`) and the date; `file:line` is not permanent evidence. |

## 5. The validator on an existing project: what to expect

| | |
|---|---|
| **What happened** | Run read-only over two real apps, the validator gave **zero errors on the screens**. The few "errors" came from generic Microsoft plugin guides copied into the screens folder (illustrative snippets with a `Control` without a version and repeated keys): documentation false positives. The typical warnings of a large app: mass literal `RGBA(`, names not in kebab-case (Studio's automatic ones and shared blocks with a `_1` suffix), `.Run(` without `IfError`, `Search`/`in` in `Filter`, `CountRows` over SQL already labeled with a cap, columns with no prefix in `DisplayFields`, and documentation or formula-bar files ignored (T020). A validator that only reads fenced blocks gives `0/0` on plain YAML (false green); this one reads both formats. |
| **Prevents** | `SKILL.md` (Scripts section): keep guides out of the screens folder or mark the block with `# validador: ignorar`; treat each warning as a written decision, not as noise. |

## 6. Unifying separators without looking at the file's destination

| | |
|---|---|
| **What happened** | In a data contract, the App object (pt-BR formula bar: `;` and `;;`) was treated with the same separator as the screens (YAML: `,` and `;`), and several pages were converted wrongly. The first version of the contract got this wrong, and the fix required checking against the previous track. |
| **Prevents** | `default-decisions.md` §3 and `pa-yaml-format.md` §2: the separator belongs to the **destination**, not the project; before "unifying" a batch of files, check each one's destination. |

## 7. A text-catalog rule with no automatic check gets lost

| | |
|---|---|
| **What happened** | Despite the text-catalog rule, an app's screens kept literal strings (`"Cancel"`, `"Save"`, modal titles, placeholders). Save and confirm buttons were also left with no loading state (a double click writes twice), and the same blocks (counters, menu, loading, toast) were replicated by hand across several screens. |
| **Prevents** | `design-tokens.md` §1 item 6 (text by `fxTxt*`/`fxMsg*` token) and `flow-call.md` (every button that writes turns on `varShowLoading`). The validator does not catch a literal string: run `grep -n 'Text: ="'` in the definition of done and centralize repeated blocks (user-defined function or component library) when possible. |

# Safe generator and immutable baseline

Decision F6 of [default-decisions.md](../../power-platform/references/default-decisions.md):
delivery is by pasting into the designer; the pasted file is the **baseline**; a generator never
writes over it. This file explains why and how to build the pipeline without repeating the
accident that motivated it ([field-lessons.md](field-lessons.md)).

## Contents

1. [When a generator is worth it](#1-when-a-generator-is-worth-it)
2. [The accident](#2-the-accident)
3. [Folders and direction](#3-folders-and-direction)
4. [Write lock](#4-write-lock)
5. [Round-trip](#5-round-trip)
6. [Gates](#6-gates)

---

## 1. When a generator is worth it

A flow is written by hand in the designer, or pasted from hand-written JSON. A generator pays off
when **several** actions repeat the same rule and the rule has already diverged between copies (a
validation rule across several flows, spelled two ways). "Every business rule becomes ONE
expression in ONE function" removes the divergence. With a single flow, write the scope by hand
(use `assets/flow-write-template.json`) and do **not** build a generator (YAGNI).

## 2. The accident

1. The generator emitted the scope; the designer returned it different (rules R1-R13 of
   [designer-baseline.md](designer-baseline.md)); the returned file was fixed by hand and became
   the baseline on disk.
2. The generator **never absorbed** the designer's rules.
3. The "source x disk" gate (regenerates in memory and compares with disk) started flagging the
   baseline as "stale" and told people to **regenerate**. Regenerating opens the file in write
   mode and **erases the baseline**, returning it to its pre-designer state.
4. In the same week, a scope refactor rewrote the generator and erased a track fix that only
   existed in the pasted file (the task was marked "done" with no evidence).

The gate was right about the fact (source != disk) and wrong about the **direction**: after the
real paste, the disk is right and the source is stale. [verified: reference project]

Lesson: **after the first real paste, bring every difference into the generator before generating
the second flow.** While the generator does not reproduce the baseline, do not run the generator.

## 3. Folders and direction

```
flows/
  source/       names.json (the only place for names, messages, gates), rules in modules
  generate.py   reads source/, writes ONLY to dist/
  dist/         generator output. Marked "generated - do not edit". Can be deleted freely
  baseline/     what the designer returned. IMMUTABLE (read-only by convention and by lock)
  verify        scripts/verificar-fluxo.py runs over baseline/ AND dist/
```

Direction of information flow: **environment -> baseline -> generator source -> dist**. Never
`dist -> baseline`. A manual fix goes to the generator's **input** (P3 in
[default-decisions.md](../../power-platform/references/default-decisions.md)), not to the
generated file.

## 4. Write lock

A generator writes to `dist/` and **refuses** any other destination:

```python
from pathlib import Path

PASTAS_PROTEGIDAS = ("baseline", "clipboard")


def destino_seguro(destino: Path, raiz_dist: Path) -> Path:
    """Accept only a path inside dist/ and never inside a protected folder."""
    destino = destino.resolve()
    raiz = raiz_dist.resolve()
    if raiz not in destino.parents:
        raise PermissionError(f"generator only writes to {raiz}: refused {destino}")
    if any(parte in PASTAS_PROTEGIDAS for parte in destino.parts):
        raise PermissionError(f"protected folder: {destino}")
    return destino
```

Destination: a function at the top of the generator; every write goes through it. Complement it
with a second lock outside the code: mark `baseline/` as read-only in the file system and have Git
from day 0 (P1), so that any deletion is a `git checkout`.

## 5. Round-trip

To prove the generator reproduces the designer:

1. Generate the already-pasted flow into `dist/`.
2. **Normalize** both (key order R7, empty `runAfter` R3, `else` R8) and compare with the baseline
   node by node.
3. Divergence = the rule that is missing from the generator **or** a deliberate manual edit in the
   designer. A manual edit must be **declared** (a list of nodes that diverge on purpose, with the
   reason); a divergence with no explanation is an error.
4. Only with zero unexplained divergence is the generator "aligned" and allowed to generate the
   next flow.

In one project this was done with a post-processor that applied R1-R9/R11-R13 to the raw output and
compared it with the baseline: most of the nodes in common matched with the rules alone, the rest
diverged because of declared manual edits, and none diverged without an explanation. The
post-processor is a **bridge**; the goal is for the rules to live in the generator and for the
post-processor to become a regression test.

## 6. Gates

| Gate | Correct direction |
|---|---|
| Source x `dist/` | Regenerates in memory and compares with `dist/`. **Never** with `baseline/` |
| Generator x baseline | The round-trip of §5 |
| Generator x procedure signature | Emitted parameters == signature read from the `CREATE PROCEDURE` (missing/extra = error). Without this gate, dozens of specifications were rewritten without anything flagging it |
| `verificar-fluxo.py` | Over the **artifact actually pasted** (`baseline/`), not just the generator output: in one project the expression gates only ran over `dist/`, and the baseline carried two defects that no gate caught |
| Proof that it flags | A fixture that fails per rule ([default-decisions.md](../../power-platform/references/default-decisions.md) P4) |
| Versioned toolchain | `.gitignore` for `__pycache__`; the `.py` in the repository. One project ended up with the generator "gone" (only `.pyc` on disk) |
| Contract | Generated from the artifact ([app-flow-contract.md](app-flow-contract.md) §7) |

When the generator exists, the **error message of every gate** states the file and the action
(`file.json:Action_X:`), because an error with no location costs more than the defect.

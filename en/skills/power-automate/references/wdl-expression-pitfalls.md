# Expressions (WDL): pitfalls that blow up only at runtime

The designer accepts and saves an expression that fails on the first real run. Each section is a
defect that cost a run. Examples use `@expr` (connector field, `expression` of
`If`/`Switch`, `inputs` of `Compose`); inside the text of `Response.body` the same value goes as
`@{expr}`.

## Contents

1. [`if()` does not short-circuit](#1-if-does-not-short-circuit)
2. [`string(null)` is `''`](#2-stringnull-is-)
3. [`outputs()` x `body()`](#3-outputs-x-body)
4. [`bit` arrives as `true`/`false`](#4-bit-arrives-as-truefalse)
5. [The 8,192-character limit](#5-the-8192-character-limit)
6. [`@{}` vs `@expr` and quotes](#6--vs-expr-and-quotes)
7. [Empty lists and index](#7-empty-lists-and-index)
8. [JSON built as text](#8-json-built-as-text)
9. [Others](#9-others)

---

## 1. `if()` does not short-circuit

`if(cond, then, else)` evaluates **both branches** before choosing. This **protects nothing**:

```text
@if(greater(length(x), 400), substring(x, 0, 400), x)
@if(isNumero, int(t), 0)
```

With a 12-character `x` the `substring` runs anyway and blows up; with a non-numeric `t` the `int`
runs anyway and throws. The action fails, falls into the `Catch` and the user reads "the system did not respond"
instead of the validation message. [verified: reference project]

Fix: make the call **valid on its own**, protecting the **argument**:

```text
@take(coalesce(x, ''), 400)
@int(if(isNumero, t, '0'))
```

Destination: connector parameter field / `Compose`. The first returns up to 400 characters of
any text; the second keeps the `if()` on the **inside**, with two plain-text branches.

## 2. `string(null)` is `''`

`coalesce` only skips **null**. `string(null)` returns `''`, which is not null; the fallback never applies and
`int('')` is left, which blows up.

```text
wrong:   @int(coalesce(string(first(body('Registro_antes')?['value'])?['Id_Origem']), '0'))
right:   @int(coalesce(first(body('Registro_antes')?['value'])?['Id_Origem'], '0'))
```

Destination: connector parameter. `Id_Origem` is a numeric column, which the connector delivers as a number or JSON
null; null -> `'0'` -> `int('0')`. With a `''` fallback `coalesce(string(x), '')` is harmless
(the result is the same); with a **non-empty** fallback it is a bug (R12). `verificar-fluxo.py` flags the
second (F012); `--estrito` flags both. [verified: reference project]

## 3. `outputs()` x `body()`

| Action | `outputs('X')` | `body('X')` |
|---|---|---|
| `Compose` | the value itself | the value itself |
| `Select` / `Query` (Filter array) | **envelope** `{"body": [...]}` | the list |
| Connector | envelope; use `outputs('X')?['body/field']` (the designer's token form) | the body |

`join(outputs('Conteudo_csv'), ...)` with `Conteudo_csv` being a `Select` failed with "join expects
its first parameter to be an array... Object". Worse is the **silent** form:
`outputs('Trilha')?['campos']` over a `Select` gives `null`, `string(null)` gives `''` and the response
comes out as `" field(s) changed."` with no number, no error and no gate to flag it. The verifier flags
`outputs()` of `Select`/`Query` outside the `?['body...` form (F011). [verified: reference
project]

## 4. `bit` arrives as `true`/`false`

The SQL connector types a `bit` column as a boolean; `equals(true, 1)` is **false**. Safe read
(missing denies):

```text
@or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_X'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_X'],'0'))),'true'))
```

Destination: `expression` of `If` / `Compose`. Three cautions:

- An OData `$filter` over `bit` uses `true`/`false`, not `1`/`0`.
- The reverse is equally false: `toLower(string(x))` is **text**; comparing it with the boolean `true`
  (no quotes) is always false and inverts the rule (the scope starts to apply to everyone).
- `string(coalesce(x,'0'))`: here the `coalesce` stays **inside** the `string()` (the opposite of §2).

## 5. The 8,192-character limit

An expression cannot exceed 8,192 characters ([Learn: limits](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-limits-and-config)).
`@concat()`, `@base64()` and `@string()` evaluate up to 131,072 characters. The designer refuses with
"the input parameters contain invalid expressions", which says nothing about size and sends you
looking for a syntax error where there is none. Two constructs blow up without looking large:

- A nested `if(contains(o,'k'), removeProperty(o,'k'), o)`: each key **repeats** the inside;
  8 keys = 2^8 copies.
- `substring(x, 0, sub(length(x), 1))`: `x` appears 3 times.

Fix: put the subexpression in a `Compose` and refer to it through `outputs()`. Chaining is linear;
nesting is exponential. The verifier flags anything above 8,192 and warns above 80% (F013), because
these expressions **grow** with each new validation rule.

## 6. `@{}` vs `@expr` and quotes

| Where | Form |
|---|---|
| Connector parameter, `expression` of `Switch`/`If` | **bare** `@expr` (`@{}` forces text: an `INT` column receives a string) -- F018 |
| Text field inside `Response.body` | interpolated `@{expr}` |
| Fixed message in `if()` | text **in single quotes**: `'Enter the description.'` |
| Apostrophe in the text | doubled: `'Can''t save'` |

An en-US message **without** quotes inside `if()` kept none of the flows from saving (`InvalidTemplate`).
A value inside a message uses `concat('text ', value, '.')`, never `@{}` inside an `if()`
literal. [verified: reference project]

## 7. Empty lists and index

- Reading one result row: `body('X')?['ResultSets']?['Table1']?[0]?['col']` --
  an index with `?[0]` does not blow up on an empty list. `first()` is also safe.
- `empty(coalesce(body('X')?['ResultSets']?['Table1'], json('[]')))`: the `json('[]')` covers
  `null`.
- `empty(list)` of a `['']` list (one empty item) is **false**: use
  `empty(trim(join(list, '')))`.
- A deliberately `null` value (e.g. "all units") does **not** go through `coalesce`/truncate
  (in full in [authorization-in-flow.md](authorization-in-flow.md) §3).

## 8. JSON built as text

Building JSON with `concat` breaks with a quote, backslash, TAB, CR, LF or control character in the data.
Prefer an object `Select`/`Compose`. If you have to use `concat`, escape `\`, `"`, CR, LF, TAB and
controls **and run** the result in a test (does `json()` open it?). [verified: reference
project]

## 9. Others

- `Initialize variable` only at the root level; inside a scope use `Compose` (F021). When pasting, a
  variable alone in a field becomes a token and may come out blank (F022, `clipboard-format.md` §7).
- `Set variable` does not read the variable itself in the value: build it in a `Compose`
  (`setProperty(variables('x'), 'key', value)`) and set the variable to its output.
- A key that comes from an empty field (`variables('x')?['']`): use a sentinel (`'-'`) in place of the empty.
- `contains(x, '')`: do not count on the result. If the needle can arrive empty, decide beforehand:
  `or(empty(needle), contains(x, needle))`.
- Object with dynamic keys: `json(concat('{', join(pairs, ','), '}'))`, escaping the `"` and `\` of the
  labels (§8).
- `item()` works in `Select`/`Query`/`Filter`; `items('<Foreach>')` only **inside** the named
  `Foreach` (F007).
- `result('Scope')` accepts `Scope`/`Foreach`/`Until`, not `If`, and returns only the first level
  ([Learn](https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling)).
- The hash function is not on the list used in these flows `[unverified: confirm in the
  function reference before promising a token hash in WDL]`.
- `and()`/`or()` may also evaluate all arguments: do not protect one term with another `[unverified: and/or short-circuiting]`; make each term valid on its own.
- A nonexistent function (`select`, `filter`, `map`, `sum` are not WDL) only fails on save/run.

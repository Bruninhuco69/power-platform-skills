# Unit scope

How the database **obeys** a unit scope (store, branch, region) without being the one that decides it.
The decision and the refusal belong to the flow (A3); the screen only helps navigation. Here: the
scope parameter, the list filter via JSON, the unit codes and the traps of `StartsWith`/`LIKE` and
`NULL`.

## Contents

1. [Who does what](#1-who-does-what)
2. [The three scope states](#2-the-three-scope-states)
3. [Scope × the filter's unit list](#3-scope--the-filters-unit-list)
4. [More than one unit per role](#4-more-than-one-unit-per-role)
5. [Unit codes: prefix-free](#5-unit-codes-prefix-free)
6. [StartsWith, LIKE and NULL](#6-startswith-like-and-null)
7. [Writes: the record's unit](#7-writes-the-records-unit)
8. [Tests](#8-tests)

---

## 1. Who does what

| Layer | Role |
|---|---|
| Screen | **UX.** The unit filter on the gallery helps navigation; the client can be tampered with. Formula and variables in `powerapps-canvas` |
| Flow | **Control.** Resolves the role's scope, refuses when there is no unit, authorizes the write against the record's unit. In `power-automate` |
| Procedure / function | **Obeys.** Receives `@Unidade_Escopo` and applies it with `AND` alongside the rest; does not decide the value |

The connector account is shared: SQL does not see the end user. That is why the scope becomes a
**parameter** resolved by the flow, and not `SUSER_NAME()`.

## 2. The three scope states

`@Unidade_Escopo VARCHAR(3)` (same type as the column):

| Value | Meaning | Who generates it |
|---|---|---|
| `NULL` | role that sees everything: no restriction | flow, when the "all units" flag is true |
| `'AAA'` | only its own unit | flow, with the caller's unit |
| `''` | **third state:** matches no unit, on purpose | mapping accident; the database fails **closed** |

`''` is only "none" if the column is `NOT NULL` with
`CHECK (LEN(LTRIM(RTRIM(Nom_Abvd_Unidade))) > 0)`: SQL Server's `=` ignores trailing spaces, so
without the `CHECK` `''` matches the row whose unit is `''` or blank.

```sql
(@Unidade_Escopo IS NULL OR s.Nom_Abvd_Unidade = @Unidade_Escopo)
```

Rules:

1. **Do not normalize `''` to `NULL` in T-SQL.** A `NULLIF(@Unidade_Escopo, N'')` would turn a role
   with no unit into a role that sees **everything**. Today's fail-closed (zero rows, no error) is the
   right one; the cost is that it looks like "there is no data". What is missing is the **test** of the
   third state (§8).
2. **The flow cannot pass `NULL` through `coalesce(x, '')` or generic truncation:** the `NULL` becomes
   `''` and the report comes back empty for the one who sees everything. Full text in
   [authorization-in-flow.md](../../power-automate/references/authorization-in-flow.md) §3.
3. When the role does **not** see everything and the unit in the record comes empty, the flow
   **refuses** before calling. It is the lock that keeps `NULL` from meaning "all" by data defect.
4. **A `CONFIG` security flag is born on** (full text in
   [authorization-in-flow.md](../../power-automate/references/authorization-in-flow.md) §4).

## 3. Scope × the filter's unit list

Two concepts that look the same and are not:

| | Comes from | Changes on every query? | Can widen access? |
|---|---|---|---|
| **Scope** (`@Unidade_Escopo`) | role, resolved by the flow | no | it is the limit |
| **Filter list** (`@Filtros.unidades`) | the user's choice on the screen | yes | **never** |

Both enter with **`AND`**: the list narrows within the scope. The function in
`assets/read-function-template.sql` applies both; the list arrives in a JSON
`{"unidades":["AAA","BBB"]}` opened by `OPENJSON` (requires `COMPATIBILITY_LEVEL >= 130`,
https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql). A missing key, `null`
or a scalar in place of an array becomes "predicate not applied", never an error.

The `CONVERT(VARCHAR(3), value)` stays **on the list side**: on the other side the `VARCHAR` column
would be promoted to `NVARCHAR` and lose the seek. The list has at most a few dozen items.

## 4. More than one unit per role

`Flg_TodasUnidades` on the role only expresses "all or one". A user with 3 of the dozens of units is
**not representable**. Options, cheapest first:

1. **Accept the limit and record it** (product decision, in the ADR).
2. **A link table** `user × unit` (a new object: a request to the DBA, and the database may be
   frozen). The flow reads the caller's units and sends the **list** to the function.
3. **Scope as a JSON list in the parameter**, with no new object:

```sql
CREATE OR ALTER FUNCTION dbo.tvf_APP_Pedido_Visiveis
(
    @Unidades_Permitidas NVARCHAR(4000)   -- NULL = all; '[]' = none (fail-closed)
)
RETURNS TABLE
AS
RETURN
(
    SELECT s.Id_Pedido,
           s.Nom_Abvd_Unidade
      FROM dbo.APP_Pedido AS s
     WHERE s.Flg_Situacao = 1
       AND (@Unidades_Permitidas IS NULL
            OR s.Nom_Abvd_Unidade IN (SELECT CONVERT(VARCHAR(3), LTRIM(RTRIM(j.value)))
                                        FROM OPENJSON(@Unidades_Permitidas) AS j))
);
GO
```

An empty array returns zero rows (fails closed); malformed JSON makes the action fail. The flow is the
one that lists the caller's permitted units; the database only obeys. The rule in §2.2 still holds:
do not pass this parameter through `coalesce`.

## 5. Unit codes: prefix-free

When the app uses **a single token** for both modes ("one unit" and "all") through
`StartsWith(column, token)`, the token `"AAA"` matches equality **only if no code is a prefix of
another**: with the codes `AA` and `AAA`, the token `AA` would leak `AAA`. The empty token `""` matches
everything, which is the "all" mode.

Check that the set of codes is **prefix-free** (it must come back empty):

```sql
SELECT a.Nom_Abvd_Unidade AS Codigo, b.Nom_Abvd_Unidade AS E_Prefixo_De
  FROM dbo.APP_Unidade AS a
  JOIN dbo.APP_Unidade AS b
    ON b.Id_Unidade <> a.Id_Unidade
   AND b.Nom_Abvd_Unidade LIKE a.Nom_Abvd_Unidade + '%';
```

(`dbo.APP_Unidade` is the project's units table; it can be a read-only corporate table.) Record in
`AS-BUILT-NAMES` that the property was **checked**, and the date. A new code that violates the
property breaks the scope on every screen without an error: ask the owner of the unit registry to
preserve it.

In the database, **use `=`**, never `LIKE`: `StartsWith` is an app feature (UX).

## 6. StartsWith, LIKE and NULL

- `StartsWith(column, text)` delegates to SQL Server and becomes `LIKE 'text%'`, sargable
  (https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview,
  note 6: only with the column as the first argument).
- **`LIKE '%'` does not match `NULL`.** In "all" mode, the row with a `NULL` unit **silently
  disappears** from both ends of the filter. Without DDL to require `NOT NULL` there is no way to
  prevent it; so:
  - count the orphan rows and record them (query below);
  - ask the DBA for `NOT NULL` if possible;
  - or accept that a record without a unit only shows up by another path (a procedure report, where
    `@Unidade_Escopo IS NULL` does **not** exclude `NULL`).
- Padding: a `CHAR(n)` column stores trailing blanks; Power Fx does not ignore them. Use `VARCHAR(3)`
  on your own tables and `Trim()` when loading the collection read from corporate `CHAR`
  (`data-model.md` §5).
- Text comparison with `<`/`>` does not delegate on text; `=` and `<>` delegate.

```sql
-- rows that the "all units" mode does not see or sees wrong (must return 0, or decide what to do)
SELECT COUNT_BIG(*) AS Sem_Unidade   FROM dbo.APP_Pedido WHERE Nom_Abvd_Unidade IS NULL;
SELECT COUNT_BIG(*) AS Com_Brancos   FROM dbo.APP_Pedido
 WHERE Nom_Abvd_Unidade <> LTRIM(RTRIM(Nom_Abvd_Unidade));
```

## 7. Writes: the record's unit

- The unit written to the trail and to child records is **the record's** (`DELETED.<column>` in the
  `OUTPUT`, or a validated parameter in `INSERT`), **never** the one the screen is viewing. Flow
  obligation: `proc-flow-contract.md` §3, item 4. The template's `Editar` procedure takes no unit
  parameter: the rule is enforced **by the absence of a parameter**.
- The flow authorizes the write by comparing the **record's** unit with the caller's scope.
- Defense in depth, cheap and with no `IF`: the scope becomes an `AND` clause in the `UPDATE`'s
  `WHERE`:

  ```sql
  AND (@Unidade_Escopo IS NULL OR s.Nom_Abvd_Unidade = @Unidade_Escopo)
  ```

  Effect: out of scope, zero rows and `NAO_APLICADO`. It is a net, not the source of the message: the
  flow checks first to give the right sentence. Since the parameter comes from the caller, it is **not**
  a control against someone who lies about the scope (`security-and-permissions.md`).
- **Native RLS** (`SESSION_CONTEXT`) does not solve it with a shared service account: the context would
  have to be set by a parameter, with the same trust limit. `[unverified]`

## 8. Tests

The four cases that close the scope, against the template function (they must give the results in the
comments):

```sql
SELECT COUNT_BIG(*) AS Todas       FROM dbo.tvf_APP_Pedido_Filtrar(N'{}', NULL);    -- total of live rows
SELECT COUNT_BIG(*) AS Uma         FROM dbo.tvf_APP_Pedido_Filtrar(N'{}', 'AAA');   -- only unit AAA
SELECT COUNT_BIG(*) AS Nenhuma     FROM dbo.tvf_APP_Pedido_Filtrar(N'{}', '');      -- 0: third state
SELECT COUNT_BIG(*) AS Interseccao FROM dbo.tvf_APP_Pedido_Filtrar(N'{"unidades":["BBB"]}', 'AAA');  -- 0: the filter does not widen the scope
```

And the flow tests, on the `power-automate` side: a role without "all" and an empty unit is refused; a
record unit outside the scope is refused; `NULL` reaches the database as `null`, not as `''`.

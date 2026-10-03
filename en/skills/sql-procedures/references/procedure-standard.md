# Procedure standard

How to write the procedure the flow calls. Decisions that hold for every project are in
`power-platform/references/default-decisions.md` (A1, A2, C1, C2, B1); here is the **how**: envelope,
return, the two variants and when to use each, concurrency and the complete code.

## Contents

1. [When a procedure exists](#1-when-a-procedure-exists)
2. [Envelope](#2-envelope)
3. [One-row return](#3-one-row-return)
4. [Closed vocabulary of codes](#4-closed-vocabulary-of-codes)
5. [Declarative vs classic: which to choose](#5-declarative-vs-classic-which-to-choose)
6. [Declarative variant](#6-declarative-variant)
7. [Classic variant: TRY/CATCH + THROW](#7-classic-variant-trycatch--throw)
8. [Duplicates: UPDLOCK and HOLDLOCK](#8-duplicates-updlock-and-holdlock)
9. [Variants by operation type](#9-variants-by-operation-type)
10. [Parameters](#10-parameters)
11. [OUTPUT, clock and trail](#11-output-clock-and-trail)
12. [Concurrency, retry and idempotency](#12-concurrency-retry-and-idempotency)
13. [Review checklist](#13-review-checklist)

---

## 1. When a procedure exists

| Situation | Path |
|---|---|
| A write with a business rule, more than one effect (row + trail) or that must be atomic | **procedure**, called by the flow (A1) |
| A read for a gallery, filter, lookup | table/view directly in the app, if the filter delegates (see `computed-columns-delegation.md`) |
| A read with many filters, scope or exact count | inline function + read procedure (§9) |
| A simple write, one table, no rule | still goes through the flow; the procedure can be a single statement |

The screen does **not** `Patch` a table that has a rule. For that to hold in the database (and not
only by discipline), the connector account cannot have DML: see `security-and-permissions.md`.

## 2. Envelope

Every write procedure starts like this, in this order:

```sql
CREATE OR ALTER PROCEDURE dbo.usp_APP_Entidade_Acao
    @Id_Entidade INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    -- body
END
GO
```

| Element | Rule | Source |
|---|---|---|
| `SET NOCOUNT ON` | first line, in **every** procedure and in **every trigger** | `[unverified: the exact effect on the connector was not measured]`. Command semantics: https://learn.microsoft.com/en-us/sql/t-sql/statements/set-nocount-transact-sql |
| `SET XACT_ABORT ON` | a procedure that writes: a runtime error ends and rolls back the whole transaction | https://learn.microsoft.com/en-us/sql/t-sql/statements/set-xact-abort-transact-sql |
| `BEGIN TRANSACTION` … `COMMIT` | only where there is more than one write statement; a single statement is already atomic | same |
| Schema | always `dbo.` on creation and in every reference | avoids per-user resolution and bad plan reuse |
| No `sp_` | prefix reserved by the product; SQL Server looks in `master` first | product documentation; the lint default accepts `SP_` because the real name comes from the environment; lowercase `sp_` is flagged (P005, warning: the pattern is *case-sensitive*) |

**The name comes from the environment.** The documented pattern (`usp_<SIGLA>_<Entidade>_<Acao>`)
diverged from the real name created by the DBA (`SP_<SIGLA>_<VERBO>_<OBJETO>`) in the reference
project. Before writing a flow call, read the name in `sys.procedures` and record it in
`AS-BUILT-NAMES` (N1). The lint accepts `usp_` and `SP_` by default; change it in
`power-platform.config.json` (`padrao_nome_procedure`) or with `--padrao-nome`.

One business action = one procedure. No `@Acao` routing an `IF`: a parameter that the branch ignores
is a disguised defect. The `Switch` stays in the flow.

## 3. One-row return

A write procedure returns **one result set, of one row, with four columns** (C1):

| Column | Content |
|---|---|
| `status` | `success` \| `warning` \| `error` |
| `description` | result **code**, ASCII without accents, closed vocabulary (C2) |
| `id` | record id as **text**; `N''` when nothing was written |
| `url` | `N''` (reserved; the flow fills it if needed) |

Hard rules:

1. The four columns always come out, **never `NULL`** (`N''`, not `NULL`): the screen reads `ret.url` in
   a flow that does not use a url and must receive `""`.
2. `id` is `NVARCHAR` via `CONVERT(NVARCHAR(20), ...)`: the flow contract is text, and the implicit
   conversion in the flow is where the locale `"1.234"` comes back.
3. **A single data `SELECT` at the end.** A debug `SELECT` in the middle becomes a result set.
4. Every DML `OUTPUT` uses `INTO` (§11).
5. Only the **first** result set reaches the flow; with a gateway, `OUTPUT` parameters do not come
   back, and the result set schema needs unique, non-empty column names.
   Source: https://learn.microsoft.com/en-us/connectors/sql/ (connector limitations).
6. `warning` is not decoration: it wrote and there is something the user needs to know (e.g. it
   registered as pending because of a duplicate). `error` is kept for the refusal that **only the lock**
   can issue.

### A return that guarantees one row by construction

The trick of the declarative variant: a derived table with **one row per possible outcome** and a
`WHERE` that matches exactly one, comparing against the cardinality of the `OUTPUT` sink:

```sql
SELECT TOP (1)
       v.status       AS status,
       v.description  AS description,
       v.id           AS id,
       N''            AS url
  FROM (VALUES (1, 'success', N'ALTERADO',      CONVERT(NVARCHAR(20), @Id_Entidade)),
               (0, 'warning', N'NAO_APLICADO', N'')
       ) AS v (Gravou, status, description, id)
 WHERE v.Gravou = (SELECT COUNT(*) FROM @Alterado);
```

When the `id` comes from an `INSERT` (it does not exist before writing), use `OUTER APPLY` over the
sink and `ISNULL(w.id, N'')`; `CROSS APPLY` would empty the result set in the refusal branch. Full
example in `assets/write-procedure-template.sql` (`usp_APP_Pedido_Criar`).

## 4. Closed vocabulary of codes

The code is a contract with the flow. Rules:

- **Closed:** a code that is not in the table does not exist. The flow has a `default` that answers
  `error` **naming** the received code (it never passes a raw code on to the user).
- ASCII without accents, `NVARCHAR(40)`, `UPPER_SNAKE`.
- **The procedure only returns what the transaction knows and the flow cannot know beforehand.**
  Format validation, authorization and domain never reach the procedure (declarative variant) or become
  codes of their own (classic).
- One code per distinct outcome **that the user needs to tell apart**. `NAO_APLICADO` (zero rows
  matched the predicate) is ambiguous by nature: "changed state", "does not exist", "precondition never
  held". Whoever needs the right sentence rereads the record **in the flow, before** calling.

Template table (keep one per project, in the procedure contract):

| status | description | Meaning in the database | Who writes the sentence |
|---|---|---|---|
| success | `CRIADA` | row created | flow |
| error | `PROTOCOLO_DUPLICADO` | another live row has the same protocol (only the lock knows) | flow |
| success | `ENCERRADO` | state changed from `aberto` to `encerrado` | flow |
| warning | `NAO_APLICADO` | state predicate did not match: 0 rows | flow rereads and explains |
| success | `CONTAGEM_OK` | `id` = total, no thousands separator | no sentence: feeds a flow decision |

The translation (`Switch` with `default`) belongs to the flow: see `power-automate` and
`proc-flow-contract.md`.

## 5. Declarative vs classic: which to choose

Two legitimate ways to write the same procedure.

| | **Declarative** | **Classic** |
|---|---|---|
| Idea | the procedure **does not decide**: it writes the batch and returns a code | the procedure **validates, authorizes and decides**, with `IF` and `TRY/CATCH` |
| Business rule | in the flow, in a single copy | in the database (and, in general, repeated in the flow to give the message) |
| `IF`, `WHILE`, `TRY/CATCH` | none | yes |
| Branching | state predicate in the `WHERE` + empty source in the next `INSERT` | explicit `IF` |
| Runtime error | `XACT_ABORT` rolls back; **the connector action fails** and the flow handles it in the `Catch` | `CATCH` rolls back and rethrows with `THROW`; the connector action fails the same way |
| Business refusal | `warning` + code | `error`/`warning` + code, more granular |
| Size | far fewer lines (the rule leaves the database) | larger, with copies of the rule |
| Who edits the rule | whoever maintains the flow (no DBA) | whoever has database access (the DBA, if the database is frozen) |

**Recommendation.** Start with **declarative**: it is the kit standard (A2: the flow decides, the
procedure executes) and the only one that survives the database freeze, because the rule changes in
the flow. Switch to **classic** (or add the defensive authorization block) when **any** of these is
true:

1. The procedure can be called by something that is not your flow (another app, another flow, an ETL,
   anyone with access to the connection reference). See `security-and-permissions.md`.
2. The operation is irreversible or financial and a late refusal, in the database, is worth more than a
   nice message in the flow.
3. The rule has to hold even if the flow is replaced.
4. The DBA owns the logic and does not accept a "dumb" procedure.
5. You need numbered error messages from the database itself (`THROW` with a number).

Diverging from A2 requires an ADR in the project (adding the defensive authorization block already
counts as a divergence): record which rule moves to the database and the residual risk that remains.

### The cost of declarative, without softening

A reference project recorded a dozen losses when adopting it. The ones that hurt most:

| Loss | Consequence | Mitigation |
|---|---|---|
| The procedure stops being the last control point | whoever has the connection reference writes whatever they want | minimal `GRANT EXECUTE`, one account per app; defensive block (§7, `security-and-permissions.md`) |
| `@Id_UsuarioChamador` comes by parameter | the trail stops proving **who**; it still proves what and when | state it in the contract; resolve the caller in the flow, by PK |
| No validation in the database | a flow that does not normalize silently writes garbage | flow obligations in the contract (`proc-flow-contract.md`) |
| Infrastructure error does not come back as a code | only the connector text | the flow `Catch` is **mandatory** |
| Ambiguous `NAO_APLICADO` | generic sentence | the flow rereads before calling |
| The transaction opens even on refusal | one extra transaction, empty commit | cost accepted; no partial record |

Detail and evidence: `field-lessons.md`.

## 6. Declarative variant

Seven rules, all encoded in `assets/write-procedure-template.sql`:

1. `SET NOCOUNT ON` on the first line.
2. `SET XACT_ABORT ON` in place of `TRY/CATCH` (the error rises and rolls back).
3. `OUTPUT ... INTO @sink`, always with `INTO` (§11); `DELETED.<col>` feeds the previous value of the
   trail, read atomically by the `UPDATE` itself.
4. **A state predicate in the `WHERE` plays the role of the `IF`:** `UPDATE ... WHERE <PK> AND <expected
   state>` is optimistic concurrency; zero rows = precondition failed.
5. **The source cardinality plays the role of the `IF`** in the following writes: `INSERT ... SELECT FROM
   @sink`; empty sink, no rows.
6. **No scalar working variable.** The only `DECLARE` is the typed `OUTPUT` sink: it holds the result
   of the previous statement, it is not state.
7. **Return** by `SELECT TOP (1)` over `VALUES` with an exact-match `WHERE` (§3).

What stays out of the body, on purpose: `IF`, `WHILE`, `TRY/CATCH`, cursor, rule `CASE`,
`SCOPE_IDENTITY()`, `THROW`/`RAISERROR`, explicit `ROLLBACK`, e-mail, reading the role.

State literals (`N'aberto'`) **stay in the body**, never in a parameter: as a parameter, the caller
turns off the lock by sending another string. The **written** state is a parameter (already validated
by the flow).

`Dt_Inclusao` and other audit dates come from `SYSUTCDATETIME()` inside the procedure, **never by
parameter**; `Dt_Alteracao` comes from a trigger (`data-model.md`).

## 7. Classic variant: TRY/CATCH + THROW

Use it when the procedure has to decide (§5). Each path returns exactly **one** row; an unexpected
error rethrows with `THROW` and the flow handles it in the `Catch`. `THROW` respects `XACT_ABORT`;
`RAISERROR` does not, and the documentation says to use `THROW` in new code
(https://learn.microsoft.com/en-us/sql/t-sql/statements/set-xact-abort-transact-sql).

It depends on `dbo.APP_Usuario`, `dbo.APP_Perfil` and the tables of the write template
(`data-model.md` §6 has the DDL for user and role).

```sql
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Cancelar
    @Id_Pedido      INT,
    @Des_Motivo          NVARCHAR(200),
    @Id_UsuarioChamador  INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @Status_Antes NVARCHAR(20);
    DECLARE @Agora        DATETIME2(3) = SYSUTCDATETIME();

    -- 1) defensive authorization: the ACTION's flag, read from the caller's role.
    --    Limit: @Id_UsuarioChamador arrives by parameter; this blocks error and
    --    misuse, not a caller who lies about the id (see security-and-permissions.md).
    IF NOT EXISTS (SELECT 1
                     FROM dbo.APP_Usuario AS u
                     JOIN dbo.APP_Perfil  AS p ON p.Id_Perfil = u.Id_Perfil
                    WHERE u.Id_Usuario   = @Id_UsuarioChamador
                      AND u.Flg_Situacao = 1
                      AND p.Flg_Situacao = 1
                      AND p.Flg_Cancelar = 1)
    BEGIN
        SELECT 'error' AS status, N'SEM_PERMISSAO' AS description, N'' AS id, N'' AS url;
        RETURN;
    END;

    -- 2) input validation (the flow also validates, to give the sentence)
    IF @Des_Motivo IS NULL OR LEN(LTRIM(RTRIM(@Des_Motivo))) < 10
    BEGIN
        SELECT 'error' AS status, N'MOTIVO_INVALIDO' AS description, N'' AS id, N'' AS url;
        RETURN;
    END;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- read that decides the write: UPDLOCK + HOLDLOCK until COMMIT (section 8)
        SELECT @Status_Antes = s.Des_Status
          FROM dbo.APP_Pedido AS s WITH (UPDLOCK, HOLDLOCK)
         WHERE s.Id_Pedido = @Id_Pedido
           AND s.Flg_Situacao   = 1;

        IF @Status_Antes IS NULL OR @Status_Antes <> N'aberto'
        BEGIN
            ROLLBACK TRANSACTION;
            SELECT 'warning' AS status, N'NAO_APLICADO' AS description, N'' AS id, N'' AS url;
            RETURN;
        END;

        UPDATE dbo.APP_Pedido
           SET Des_Status = N'cancelado'
         WHERE Id_Pedido = @Id_Pedido;

        INSERT dbo.APP_PedidoTrilha
              (Id_Pedido, Tp_Evento, Des_Resumo, Des_ValorAnterior, Des_ValorNovo,
               Id_UsuarioChamador, Dt_Inclusao)
        VALUES (@Id_Pedido, N'CANCELAMENTO', @Des_Motivo, @Status_Antes, N'cancelado',
                @Id_UsuarioChamador, @Agora);

        COMMIT TRANSACTION;

        SELECT 'success' AS status, N'CANCELADO' AS description,
               CONVERT(NVARCHAR(20), @Id_Pedido) AS id, N'' AS url;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        THROW;   -- the flow handles it in the Catch; do not return ERROR_MESSAGE() in the description field
    END CATCH;
END
GO
```

Cautions for the classic variant:

- **Every early exit (`RETURN`) inside the transaction does a `ROLLBACK` first.** The lint's `P003`
  catches `BEGIN TRAN` without `COMMIT`, not `RETURN` without `ROLLBACK`: review it.
- Do not return `ERROR_MESSAGE()` in the `description`: it leaks schema detail to the user and breaks
  the closed vocabulary. Let the error rise (`THROW`) and let the flow build the generic message.
- Each branch returns one row; the `CATCH` does not return a result set.
- The validation the database repeats **does not replace** the flow's: the flow still needs the
  sentence.

## 8. Duplicates: UPDLOCK and HOLDLOCK

Two cases, different behaviors:

| Pattern | Window between checking and writing? | Needs a hint? |
|---|---|---|
| `UPDATE ... WHERE <expected state>` (predicate) | no: the `UPDATE` blocks and reevaluates the `WHERE` against committed data | **no** |
| `SELECT`, then decide and write | **yes** | **yes:** `WITH (UPDLOCK, HOLDLOCK)` on the `SELECT`, until `COMMIT` |
| `INSERT ... SELECT ... WHERE NOT EXISTS (... UPDLOCK, HOLDLOCK)` | no: guard and write are **one** statement | the hint goes inside the `NOT EXISTS` |

`UPDLOCK` avoids the deadlock of two shared reads trying to escalate; `HOLDLOCK` holds the range until
`COMMIT`. Without both, two sessions pass the check and write the duplicate the rule exists to prevent.

Requirements:

- **A supporting index** on the checked column (a filtered `UNIQUE` works). Without it, `HOLDLOCK`
  escalates to a range/table lock and serializes every registration.
- Hints in **a few known places**; list them in the contract (a reference project had a handful and
  verified them by `grep`).
- A cross swap can cause a deadlock (error 1205): two edits that swap the values of two rows. The flow
  treats 1205 as transient and reruns (§12).
- Under `READ_COMMITTED_SNAPSHOT`, a `SELECT` without a hint does not protect; the predicate `UPDATE`
  stays correct. Confirm the database configuration (`deploy-and-dba.md`, proofs).

## 9. Variants by operation type

| Type | Where the complete code is | Points of attention |
|---|---|---|
| **State UPDATE** + trail | `assets/write-procedure-template.sql` (`Encerrar`) | state predicate in the `WHERE`; `OUTPUT ... INTO`; return by `VALUES` |
| **INSERT** with a duplicate guard | `assets/write-procedure-template.sql` (`Criar`) | guard inside the `INSERT ... SELECT`; `OUTER APPLY` in the return; filtered `UNIQUE` index |
| **Read** (function + `@Filtros` JSON + scope) | `assets/read-function-template.sql` | inline function, `OPTION (RECOMPILE)`, scope in `AND` with the filter, `COUNT_BIG` to count |
| **Caller resolution** (read) | below | **zero rows = deny**; filters active user **and** role |
| **JSON parameter** (N trail rows) | `proc-flow-contract.md` §5 | `OPENJSON ... WITH`; silent truncation; an empty array is valid |

### Caller resolution: zero rows means deny

The flow calls this procedure **once**, in the trunk, with the e-mail from the run context (never from
the trigger parameter), tests `empty(...ResultSets/Table1)` and denies before any write. It returns
the permission flags; the flow compares them, per action.

```sql
CREATE OR ALTER PROCEDURE dbo.usp_APP_Chamador_Obter
    @Email_Chamador NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    -- the only procedure that receives an e-mail. Pure read, zero writes.
    -- Unknown, inactive or inactive role: ZERO rows.
    -- The column and the parameter must use the SAME normalization (LOWER/TRIM) at load and here.
    SELECT u.Id_Usuario,
           u.Nom_Usuario,
           LTRIM(RTRIM(u.Nom_Abvd_Unidade)) AS Nom_Abvd_Unidade,
           u.Id_Perfil,
           p.Des_Perfil,
           p.Flg_Consultar,
           p.Flg_Encerrar,
           p.Flg_Cancelar,
           p.Flg_TodasUnidades,
           p.Flg_Adm
      FROM dbo.APP_Usuario AS u
      JOIN dbo.APP_Perfil  AS p ON p.Id_Perfil = u.Id_Perfil
     WHERE u.Email_Usuario = LOWER(LTRIM(RTRIM(@Email_Chamador)))
       AND u.Flg_Situacao  = 1
       AND p.Flg_Situacao  = 1;
END
GO
```

Three requirements that this procedure **cannot** guarantee on its own:

1. A filtered `UNIQUE` on `Email_Usuario`: with a duplicate it returns two rows and the flow reads
   `[0]` (role and unit become a lottery).
2. Flags `BIT NOT NULL DEFAULT 0`: a `NULL` in a flag becomes "deny everything" (via
   `p.Flg_Situacao = 1`) or, in the flow, a null value traveling up to a condition.
3. Column and parameter normalized the same way: a **leading** space in the column is not protected by
   any collation; the `LTRIM` only protects the parameter. Dirty data denies that person's entire
   system access, indistinguishable from "does not exist". Prove it with the two real users
   (`deploy-and-dba.md`).

## 10. Parameters

The signature of a write procedure has **five classes**, and nothing else:

| Class | What it is |
|---|---|
| (a) | PK of the target, when it is an `UPDATE` |
| (b) | each column value the procedure writes, **already normalized, validated and derived by the flow** |
| (c) | `@Id_UsuarioChamador INT`, resolved by the flow by PK |
| (d) | values of the trail rows of that operation |
| (e) | `BIT` flags for conditional writes |

No `@Email_Chamador`, no message text, no parameter that the procedure uses to **decide**.
Exceptions (the rule is "literal in the body"): `WHERE` states and the origin of system-generated rows.

- Parameter name = column name; **type equal to the column's**, with the real `n`. `NVARCHAR(MAX)` out
  of laziness prevents an index and inflates the plan; the exception is a transport parameter (JSON).
- **Silent truncation on assignment.** A parameter the exact size of the value (`NVARCHAR(36)` for a
  GUID) loses the last character if a leading blank arrives, **before** the body runs; nothing in the
  body recovers it. Leave slack and apply `LTRIM(RTRIM())` in the body. `[verified: reference project]`
- `= NULL` as a default only on a genuinely optional parameter.
- A procedure parameter is **not** validated against the column: a value larger than the column blows up
  on the `INSERT` with `ANSI_WARNINGS ON` and is silently truncated with `OFF` `[verified: reference
  project]`. Turn on `SET ANSI_WARNINGS ON` in a load script and have the flow cut the text at the
  limit.
- **A column's spelling cannot be repaired.** The connector is case-sensitive on the column name:
  getting it wrong raises no flag when editing, it fails at run time, silently. Use exactly the
  environment's name.
- Watch `NULL` in a predicate: `col <> @p` with a null `col` is `UNKNOWN`, and the row is never
  changed. Use `ISNULL(col, N'') <> ISNULL(@p, N'')` when the column admits `NULL`.

## 11. OUTPUT, clock and trail

- **Always `OUTPUT ... INTO @table`.** `OUTPUT` without `INTO` returns rows to the client (it becomes
  `Table1` and steals the return) and is not allowed when the target table has a trigger enabled for
  the action. Source: https://learn.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql
- `INSERTED.*` reflects the data **after** the statement and **before** the triggers: do not read, via
  `OUTPUT`, a column that the trigger writes (`Dt_Alteracao`); reread after the `COMMIT`. Same source.
- The **order** in which `OUTPUT` captures the rows is not guaranteed; the trail's chronological order
  comes from an explicit column (`ordem`, `Dt_Evento`), never from `IDENTITY` order. Same source.
- `OUTPUT` returns rows to the client even if the statement fails and rolls back; that is why the sink
  is a table variable and the final `SELECT` only runs after the `COMMIT`. Same source.
- **A single clock for the batch:** materialize `SYSUTCDATETIME()` in the first `OUTPUT`
  (`... , SYSUTCDATETIME() INTO @sink`) and propagate it. All rows of the batch carry the same stamp.
  On the `INSERT`, use `INSERTED.Dt_Inclusao`.
- **Trail in the same transaction.** A trail outside the transaction lies when the rollback happens. The
  "previous value" column comes from `DELETED.<col>`; "who" is `@Id_UsuarioChamador` (and it is the
  caller's declaration, not proof: `security-and-permissions.md`).
- A field that did not change generates no row: that is a `WHERE`, not an `IF` (compare with `ISNULL`
  on both sides).

## 12. Concurrency, retry and idempotency

| Situation | Handling |
|---|---|
| Double click | the 2nd call changes zero rows (state predicate) and returns `NAO_APLICADO` |
| Re-entry (close again, resolve again) | the state predicate no longer matches |
| Two sessions creating the same record | guard in the `INSERT` under `UPDLOCK, HOLDLOCK` + unique index |
| Deadlock (1205) | the flow treats it as transient and **reruns**, with a limit |
| Retry of a procedure whose `UPDATE` always matches | **reapplies the trail**: give the `UPDATE` a "changed" predicate or offer an idempotency key |
| Connection drops after the `COMMIT` | the flow does not know whether it wrote: reread by id before resending |

A registration operation (`INSERT`) with no unique natural key is the one that suffers most from retry;
prefer an idempotency key per request (a `UNIQUE` column filled by the flow) over trusting the single
click.

## 13. Review checklist

Each item is checkable; the ones marked `lint` are caught by `lint-procedure.py`.

- [ ] `SET NOCOUNT ON` on the first line (`lint P001`), also in triggers (query in `deploy-and-dba.md`)
- [ ] `SET XACT_ABORT ON` in a procedure that writes (`lint P002`)
- [ ] `BEGIN TRAN` with `COMMIT` and, in the classic variant, `ROLLBACK` at every early `RETURN` (`lint P003`)
- [ ] 4-column, 1-row return in **every** outcome, including zero rows written (`lint P004`)
- [ ] every `OUTPUT` with `INTO` (`lint P011`)
- [ ] no dynamic SQL by concatenation (`lint P009`), no `NOLOCK` (`lint P010`), no `SELECT *` (`lint P007`)
- [ ] `dbo.` everywhere (`lint P008`); name according to the environment (`lint P005`)
- [ ] filter dates by `DATEDIFF`, never `CAST(... AS INT)` (`lint P006`)
- [ ] `UPDLOCK, HOLDLOCK` only where the `SELECT` decides the write, with a supporting index
- [ ] no scalar working `DECLARE` (declarative) / no `ERROR_MESSAGE()` in the return (classic)
- [ ] code vocabulary the same as the contract's and the flow `Switch`
- [ ] the connector account has no DML (`security-and-permissions.md`)

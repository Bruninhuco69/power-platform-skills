# Scope and permission on the app side

Flags per role, fail-closed, `""` = "all" with a guard, and the write unit that comes from the
record. **Everything here is UX**: what decides is the flow (`power-automate` skill) and, in Dataverse, the
Security Role (`dataverse` skill). This file says how the screen behaves to help the
user and to **not leak** data by oversight.

## Contents

1. [What the screen is and is not](#1-what-the-screen-is-and-is-not)
2. [Role by flags](#2-role-by-flags)
3. [No access: fail-closed](#3-no-access-fail-closed)
4. [Scope by unit: three roles, three variables](#4-scope-by-unit-three-roles-three-variables)
5. [The predicate goes in every `Filter`](#5-the-predicate-goes-in-every-filter)
6. [Write unit](#6-write-unit)
7. [Golden tests](#7-golden-tests)
8. [Decisions the project must make early](#8-decisions-the-project-must-make-early)

---

## 1. What the screen is and is not

Decision A3 of [default-decisions.md](../../power-platform/references/default-decisions.md): **scope
on the screen is UX, not access control.** The unit filter helps navigation; the flow is what blocks.
Reasons: the connector account is shared (reading is **not isolated** in the database), and the client
can be manipulated. Therefore:

- hiding a button or menu item by flag is not authorization;
- every write goes through a flow that **revalidates** the role, the action flag and the caller's scope;
- the app does not send identity as a parameter: the flow reads the caller from the context
  (`Office 365 Users — MyProfile_V2`): see [flow-call.md](flow-call.md).

A read filter without isolation in the database is a **declared, accepted risk** of the project, not a
detail: the choice between real isolation (RLS in SQL, business unit or owner team in Dataverse)
and "every sensitive read through a flow" is in §8.

## 2. Role by flags

**Decision T8**: permission by role **flag** (`Flg_PodeX`, `pode_x`), never by role
name. Comparing `varPerfil.Nome = "Supervisor"` breaks the day the role is renamed or
a new role is born.

- `varPerfil` is a **record** read by an explicit `LookUp`, by the user's **foreign key**
  (`Id_Perfil`) and with the status predicate (`Flg_Situacao = true`) in the **same argument**, with
  `&&`: the third argument of `LookUp` is the result column, not a second predicate.
  Without the status predicate, a deactivated role assembled the whole menu and the flow denied every
  write with no explanation. `[verified: reference project]`
- The SQL connector **does not expand FKs**: `varUsuario.Id_Perfil.Flg_Encerrar` does not exist; use
  `varPerfil.Flg_Encerrar`.
- A role resolved by a **Choice label** (Dataverse) is fragile: a different accent or space and
  `varPerfil` becomes `Blank()`, every button disappears, with no message. An FK eliminates this class of failure.
- A flag is a pure boolean (`Flg_* BIT NOT NULL DEFAULT 0`). With `NULL`, `<> true` and `= true` behave
  differently on the server and on the client (a request to the database owner).
- Use on the screen:

Destination: pasted YAML (`,` and `;`).

```yaml
# xx-btn-gal-encerrar
Visible: =varPerfil.Flg_Encerrar
DisplayMode: =If(varShowLoading || ThisItem.Status = "completed", DisplayMode.Disabled, DisplayMode.Edit)
```

Do not tie the menu to a **query** flag that some legitimate roles lack (the user would land on an
empty screen, not knowing why): tie it to `!varSemAcesso`.

## 3. No access: fail-closed

No resolved role = **no access**. `OnStart` calculates `varSemAcesso` **after**
`varPerfil` and the scope (order in [app-onstart-template.md](../assets/app-onstart-template.md)) and
starts it at `true`:

Destination: formula bar of the App object, `OnStart` property (en-US: `,` and `;`).

```powerfx
Set(
    varSemAcesso,
    IsBlank(varUsuario)
    || varUsuario.Flg_Situacao <> true
    || IsBlank(varPerfil)
    || (!varTodasUnidades && IsBlank(varUnidadeLotacao))
)
```

- `IsBlank(varPerfil)`: with no role, every menu `Visible` turns false and the app would open empty, with no
  error; that is what the "no access" panel is for.
- `(!varTodasUnidades && IsBlank(varUnidadeLotacao))`: `""` stopped being "absence of value" and
  now **means "all"**. A record with an empty unit would give `varUnidadeFiltro = ""` and the
  user would read the whole network. Whoever has no unit does not get in.
- Declared **before** `varPerfil`, `IsBlank(varPerfil)` is always true and everyone lands
  in "no access": fail closed, but total.
- Every content container has `Visible: =!varSemAcesso`, **including the menu**. A "no
  access" panel on each screen, with `fxMsgSemAcessoTitulo` and `fxMsgSemAcessoHint` (block in
  [screen-template.md](../assets/screen-template.md)).

## 4. Scope by unit: three roles, three variables

A unit is the store, the branch, the region or whatever the project calls it. **Three distinct roles, three
variables; do not merge them again.**

| Variable | Role | Rule |
|---|---|---|
| `varUnidadeLotacao` | unit from the user's record | never changes and **never empty** (guaranteed by fail-closed) |
| `varTodasUnidades` | the role sees the whole network | comes from the role flag |
| `varUnidadeFiltro` | **read** scope | **`""` means "all"** and is only reachable with `varTodasUnidades`; `If(varTodasUnidades, "", varUnidadeLotacao)` (YAML) |

- `""` is **screen** state and never travels as scope: the flow resolves the scope from the
  caller's role (`NULL` = all, for a global role; otherwise the caller's unit). The user's choice
  goes in the filter (`@Filtros.unidades`), and `""` becomes an **absent** key — never `''`, which in the database
  means *none*. See `sql-procedures/references/unit-scope.md` §2.
- A global role opens on "all" and filters later, if it wants. The others open on their home unit. No
  persistence between sessions: every login starts over here.
- **Emptying the header combo returns to the home unit, never to the whole database**:

Destination: pasted YAML (`,` and `;`).

```yaml
# xx-cbo-header-unidade
OnChange: |-
  =Set(
    varUnidadeFiltro,
    If(
      IsBlank(Self.Selected),
      If(varTodasUnidades, "", varUnidadeLotacao),
      Self.Selected.Sigla
    )
  )
```

- `colUnidadesEscopo` (what the user **may choose**) is keyed by the **home unit**, not by the
  filter: if it depended on the filter, choosing one unit would empty the list and trap the
  user in it. Combo visibility: `varTodasUnidades || CountRows(colUnidadesEscopo) > 1`.
- **A collection of records has no `.Value`**: `Self.Selected.Sigla`, not `Self.Selected.Value`
  (it returns blank and the gallery opens empty when the unit changes).
- `Trim()` at load on any padded `CHAR(n)` (`'AAA    '` vs `'AAA'`): in SQL the
  `=` ignores trailing space, in Power Fx it does not match. Once, in `OnStart`.
- A combo with dozens of items needs `IsSearchable` on; off, it is unusable.

## 5. The predicate goes in every `Filter`

**Every `Filter` on a source with organizational scope carries the scope predicate.** A filter without
scope **delegates perfectly and never emits a delegation warning**: the leak passes every
gate. It has happened: a total and a report preview without the unit predicate
let the supervisor see the whole network with the combo empty.
`[verified: reference project]`

Destination: pasted YAML (`,` and `;`).

```yaml
# Items of any gallery, and the card count, with the SAME token
Items: =Filter(Pedido, StartsWith(Unidade, varUnidadeFiltro))
```

A single token (`StartsWith(column, varUnidadeFiltro)`) covers both modes and delegates (becomes
`LIKE 'x%'`): with an abbreviation it is equality; with `""` it matches everything. The card and the gallery read the same source with the
same predicate and agree **by construction**.

**Three conditions that authorize `StartsWith` and that the database must guarantee** (require them from the
database owner; do not inherit "3-letter codes" as if it were a rule):

1. the unit code is **fixed-length and prefix-free** (none is a prefix of another): otherwise
   `StartsWith` becomes a real prefix match and **leaks between units**;
2. the scope column is **`NOT NULL`**: `LIKE '%'` (what `StartsWith(col, "")` becomes) **does not match
   `NULL`**, and in "all" mode the row without a unit silently disappears;
3. the invariant is **checked by a constraint or an automated test**, not by inspecting a CSV.

## 6. Write unit

The **write** unit does not live in global state: it is a **form field** (`xx-cbo-form-unidade`).
On create it comes from the combo; on edit and close it comes **from the record itself**
(`varPedidoSel.Unidade`). Editing never transfers between units; the unit is a property of the
record. When the flow can derive the unit from the parent record, the screen does not even send it.
Sending "the unit I am looking at" (`varUnidadeFiltro`) as the write unit writes to the wrong
place when a global role is filtering another unit.

## 7. Golden tests

1. **Emptying the combo returns to the home unit** (and a global role returns to "all").
2. **Card matches gallery** in both modes (home unit and all).
3. A user **with no role**, with a **deactivated role**, **with no unit** (and no "all" flag):
   only the "no access" panel appears, menu included.
4. Two accounts, two units: neither sees the other with the combo empty.
5. A unit with padding (`CHAR`): the filter matches after the load `Trim`.
6. A row with a `NULL` unit: appears where it should (and §5 records it if the database does not prevent it).
7. Grep the screen's `Filter` and `CountRows(Filter`: **all** carry the scope predicate.

## 8. Decisions the project must make early

- **Real read isolation** (SESSION_CONTEXT/RLS in SQL; business unit and owner team in
  Dataverse) **or** "every sensitive read through a flow or procedure". Without deciding, the project
  inherits the §1 risk without knowing it.
- **Multi-unit per user** ("3 of dozens"): an "all or one" flag cannot represent this. If it is a
  requirement, the link table and the read object go into the design from the start.
- **A unique identity key** (Entra UPN) with a `UNIQUE` index and a populated load: without
  uniqueness the `LookUp` returns whatever row SQL delivers, with no `ORDER BY`, and role and unit
  become a per-session lottery.
- Time zone and day cutoff (UTC in the database, conversion in a single place).

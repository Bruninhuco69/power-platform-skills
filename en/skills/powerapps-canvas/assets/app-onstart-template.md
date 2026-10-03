# Template: `App.OnStart` in dependency order

`OnStart` holds only what is **mutable** and what depends on identity. Constants, theme and
derived values go to `App.Formulas` ([app-formulas-tokens.md](app-formulas-tokens.md)).

**How to apply.** Select `App` in Studio, property `OnStart`, and type or paste the block into the
formula bar. The App object has no Code view. Destination: **formula bar, en-US locale
(`,` between arguments, `;` chains, `.` decimal)**.

## Contents

1. [Rules](#rules)
2. [The block](#the-block)
3. [Why this order](#why-this-order)
4. [What stays out of OnStart](#what-stays-out-of-onstart)

## Rules

1. **Every global used on any screen is created here**, with a neutral value. An uninitialized
   variable is `Blank()`, and `Blank() = 0` is false: a filter compared to 0 leaves the gallery
   empty, with no error. `[verified: reference project]`
2. **Dependency order.** Whatever reads `varPerfil` comes after `varPerfil`. Reversing it makes
   `IsBlank(varPerfil)` always true and every user lands on "no access".
3. **Fail-closed from the first line.** `OnStart` is not blocking by default: a screen can
   render and become interactive before it finishes
   ([App object](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)).
   That is why `varSemAcesso` starts as `true` and only becomes `false` after access is proven.
   `[unverified: exact moment of the first render in your app]`
4. **No `Navigate`.** The start screen is the `StartScreen` property (it only sees named
   formulas, not globals).
5. **Screen counter** (`varPedidoTotal`) is created here with 0 and is **recalculated** in
   `OnVisible` and after every flow that writes; a counter calculated only in `OnStart` freezes
   and drifts from the gallery all day.
6. Change the names `Usuario`, `Perfil`, `Unidade` to the environment's real sources
   (`AS-BUILT-NAMES`, skill `dataverse`).

## The block

Destination: formula bar of the App object, property `OnStart` (en-US: `,` and `;`).

```powerfx
// ---------- 0. fail-closed while OnStart runs ----------
Set(varSemAcesso, true);

// ---------- 1. identity (unique key: Entra UPN) ----------
Set(varUsuario, LookUp(Usuario, Upn_Entra = Lower(User().Email)));

// ---------- 2. role: by FK, whole record, active role only ----------
// Both conditions go with && in the SAME argument: the 3rd argument of LookUp
// is the result column, not a second predicate.
Set(varPerfil, LookUp(Perfil, Id_Perfil = varUsuario.Id_Perfil && Flg_Situacao = true));

// ---------- 3. scope: three roles, three variables ----------
// home unit: the unit on the user record (never changes); all: the role sees the whole network;
// filter: READ scope ("" means all, only for those with varTodasUnidades).
Set(varTodasUnidades, varPerfil.Flg_TodasUnidades = true);
Set(varUnidadeLotacao, Trim(varUsuario.Cod_Unidade));
Set(varUnidadeFiltro, If(varTodasUnidades, "", varUnidadeLotacao));

// ---------- 4. no access: only after role and scope ----------
Set(
    varSemAcesso,
    IsBlank(varUsuario)
    || varUsuario.Flg_Situacao <> true
    || IsBlank(varPerfil)
    || (!varTodasUnidades && IsBlank(varUnidadeLotacao))
);

// ---------- 5. small domains in collections (avoids LookUp per gallery row) ----------
Concurrent(
    ClearCollect(
        colUnidades,
        Sort(
            AddColumns(Filter(Unidade, Flg_Situacao = true), "Sigla", Trim(Cod_Unidade), "Nome", Trim(Nom_Unidade)),
            Sigla
        )
    ),
    ClearCollect(colPerfis, Sort(Filter(Perfil, Flg_Situacao = true), Nv_Perfil))
);

// what the user CAN choose: keyed by home unit, not by the filter
ClearCollect(
    colUnidadesEscopo,
    If(varTodasUnidades, colUnidades, Filter(colUnidades, Sigla = varUnidadeLotacao))
);

// ---------- 6. navigation ----------
Set(varTelaAtiva, "pedidos");

// ---------- 7. feedback (contract of the canonical blocks) ----------
Set(varShowLoading, false);
Set(varLoadingMessage, "");
Set(varShowToast, false);
Set(varToastType, "success");
Set(varToastMessage, "");
Set(varRet, Blank());

// ---------- 8. selection, modals and screen counters (neutral value) ----------
Set(varPedidoSel, Blank());
Set(varMostrarConfirmar, false);
Set(varPedidoTotal, 0)
```

Replace `Concurrent` with sequential calls if one collection starts to depend on another:
`Concurrent` runs only independent branches, in unpredictable order
([Concurrent](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-concurrent)).

## Why this order

```text
varUsuario
  |-> varPerfil --> varTodasUnidades --+
  |-> varUnidadeLotacao ---------------+--> varSemAcesso
  |                                    +--> varUnidadeFiltro
  +-- colUnidades (independent) ------------> colUnidadesEscopo
```

- `AddColumns` + `Sort` do not delegate (see [delegation.md](../references/delegation.md)); here
  that is deliberate: the inner `Filter` delegates, returns few rows and the rest runs only once,
  below the 500/2,000-row cap.
- `Trim()` at load time, once, on every padded `CHAR(n)`: SQL ignores trailing spaces in `=`,
  Power Fx does not. Never scatter `Trim` across the screens.
- `varPerfil` is a **record**, read with an explicit `LookUp`. The SQL connector does not expand
  the FK (`varUsuario.Id_Perfil.Flg_Encerrar` does not exist).
- Permission is always a role **flag** (`varPerfil.Flg_Encerrar`), never a comparison with the
  role name. Details in [scope-and-permission.md](../references/scope-and-permission.md).

## What stays out of OnStart

| The value... | Goes to |
|---|---|
| never changes (color, measure, text, `fxLimiteLinhas`) | `App.Formulas` |
| depends on a user action and only exists on one screen | `UpdateContext` or `Set` in the screen's `OnVisible` |
| is a filter date window (`varXDe`, `varXAte`) | the screen's `OnVisible` (and the Clear button rewrites it together with the `Reset`) |
| is a heavy load used on one screen only | that screen's `OnVisible` or on-demand load (see [performance.md](../references/performance.md)) |

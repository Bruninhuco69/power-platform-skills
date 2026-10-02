# Naming

Control, variable, collection, token, data source and flow. Decision T5 of
[default-decisions.md](../../power-platform/references/default-decisions.md). The name of a **column and
table** comes from the real environment (`AS-BUILT-NAMES`, skill `dataverse`); this file does not define them.

## Contents

1. [Controls](#1-controls)
2. [Variables, collections and tokens](#2-variables-collections-and-tokens)
3. [Data sources and flows](#3-data-sources-and-flows)
4. [What the validator checks](#4-what-the-validator-checks)

---

## 1. Controls

```text
<screen-prefix>-<type>-<module>-<element>[-<qualifier>]
```

Everything in **lowercase kebab-case, no accents**, **unique across the whole app** (Studio appends `_1`,
`_2` on duplicating, and that suffix is not semantic: rename it). A 2-letter screen prefix, defined
at the start (`pd` orders, `mn` menu). Examples: `pd-lbl-header-titulo`, `pd-btn-filtro-limpar`,
`pd-mod-confirmar-btn-voltar`, `pd-gal-pedidos`.

| Abbreviation | Control | Abbreviation | Control |
|---|---|---|---|
| `lbl` | Label | `gal` | Gallery |
| `btn` | button, tab, rounded shape | `img` | Image |
| `mod` | modal (scrim and card) | `ico` | icon |
| `con` | GroupContainer | `dtp` | DatePicker |
| `cmb`, `cbo` | ComboBox (pick **one** per project) | `chk` | CheckBox |
| `txt` | TextInput | `tim` | Timer |
| `hdr` | column header | `spn` | Spinner |
| `rec`, `shp` | Rectangle, decorative shape | `cmp` | root of a shared block |

- A **shared block** (toast, loading, no access) comes out **already prefixed** with the screen:
  `pd-cmp-toast`, `pd-cmp-loading`. Pasting a block without a prefix makes Studio rename it to `_1`.
- An **automatic name** (`Button1_38`, `Label3_2`, `Timer1_3`) is debt that is only paid with Studio
  open: name at creation. In a real app, nearly a third of the controls had an automatic name and
  formulas referenced `Checkbox1_7` with no one knowing what it was.
- **Another screen's prefix inside the screen** is a leftover from copy and paste: a control's prefix is
  that of the screen where it lives (legitimate exception: the menu replicated on every screen, with its
  own prefix).
- An omitted type (`toast-title`, `loading-card`) is a loose variant to avoid: use the type token.
- **A reference to a control with a hyphen always goes in single quotes** in a formula: `'pd-gal-pedidos'.AllItemsCount`.

## 2. Variables, collections and tokens

| Pattern | Use | Example |
|---|---|---|
| `var<Prefix><Subject>` (PascalCase) | screen or module global | `varPDFiltroAplicado`, `varPedidoSel` |
| `varShow*`, `varMostrar*` | visibility of overlay, toast, modal | `varShowLoading`, `varMostrarConfirmar` |
| `varToast*` | toast state | `varToastType`, `varToastMessage` |
| `varRet` | **one** flow-return variable per app | `varRet.status` |
| `ctx*` | **context** variable (`UpdateContext`) | `ctxModo` |
| `col<Content>` | collection | `colUnidades`, `colSelecionados` |
| `fx*` | theme, size, text token (named formula) | `fxColorPrimary`, `fxMsgFalhaFlow` |
| `frm*` | data named formula (KPI, list) | `frmKPIAbertos` |
| `Flg_*`, `pode_*` | role flag (column), read from `varPerfil` | `varPerfil.Flg_Encerrar` |

- **Lowercase `var`**, always (Power Fx does not distinguish case, but search and reading do): `Var`
  with a capital V shows up in real apps and breaks search.
- **No global without a prefix** (`BarraSecao`, `Tabela`, `CorFundoBotao`): a generic name with no
  scope is the worst case. Active tab: `var<Prefix>Tab`.
- **`ctx*` for context and `var*` for global**: the collision becomes impossible to write (a
  context shadows the global of the same name).
- Loop counter: `vari` only inside `ForAll`/`With`; never global.
- A **date window** variable holds an integer: `varPDFiltroDe`, `varPDFiltroAte`.

## 3. Data sources and flows

- The connector name in the app is an identifier: no quotes if it has no hyphen (`Pedido`), in single
  quotes if it does (`'app-pedido'`). Prefer a **single** pattern per project and record it in
  `AS-BUILT-NAMES`; a singular and a plural nearly equal for the same table (two connections) are
  a defect.
- Flow: `<app>-flow-<entity>-<verb>` (`app-flow-pedido-acao`), kebab-case; the app shows the name
  the flow has **in the solution**. Do not create `<app>-sql-flow-*` and `<app>-flow-*` for the same thing.
- No literal `dev` in a table, source or flow name (the environment is an environment variable and
  connection reference, skill `power-platform`).

## 4. What the validator checks

| Code | Rule |
|---|---|
| T010 | control name not in kebab-case (also flags Studio's automatic-name pattern) |
| T006 | duplicate control name in the validated set |

Screen prefix, allowed type, `var*` and `col*` are **not** checked (review): an open item of the
validator. Column name against the real environment: T014, only on the Dataverse track and only with
`prefixo_publisher` in `power-platform.config.json`.

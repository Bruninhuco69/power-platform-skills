# Dataverse table and column names and types in Power Fx

What the table and the column are called in each place, how Power Fx resolves them and how each type is
compared, filtered and written. The examples use a fictional domain: table `Pedidos` (Orders), with
the columns `situacao` (Choice), `cliente` (Lookup to `Clientes`), `unidade` (text) and `ativo` (Yes/No).

## Contents

1. [Publisher and prefix](#1-publisher-and-prefix)
2. [The four names](#2-the-four-names)
3. [Which name in each context](#3-which-name-in-each-context)
4. [Row scope: Power Fx resolves by display name](#4-row-scope-power-fx-resolves-by-display-name)
5. [Data source name and primary key](#5-data-source-name-and-primary-key)
6. [Choice, Lookup, text, Yes/No: what changes](#6-choice-lookup-text-yesno-what-changes)
7. [Decision table by type](#7-decision-table-by-type)

---

## 1. Publisher and prefix

Every **custom** table and column carries the prefix of the *publisher* of the solution it was
created in (`<prefixo>_`). The prefix belongs to the publisher, not to the project:

- Created in the maker **outside your own solution**, the component lands in the tenant's or environment's
  default publisher, whose prefix is generated and is not the one the plan expected.
- Through the Web API the prefix is **not** applied automatically: it must come in the `SchemaName`.
- Importing an Excel file into a new table creates columns with the active publisher's prefix.

Practical consequence: the plan's prefix may not be the environment's. What counts is the one in
`AS-BUILT-NAMES.md`. Declare it in `power-platform.config.json` (`prefixo_publisher`).
`[verified: reference projects]` — the real environment used the tenant's default publisher,
with a prefix different from the planned one.

## 2. The four names

| Name | Example | Who defines it | Where it appears |
|---|---|---|---|
| **Display** (`DisplayName`) | `situacao` | Whoever created the column | Maker, Studio, identifiers in formulas |
| **Logical** (`LogicalName`) | `<prefixo>_situacaodopedido` | Generated at creation, lowercase | Strings in `SortByColumns`/`DisplayFields`, OData, Web API, flow (expressions) |
| **Schema** (`SchemaName`) | `<prefixo>_SituacaoDoPedido` | Generated at creation, with capitals | Creation body through the Web API; in practice the logical name is the schema name in lowercase |
| **EntitySet** | `<prefixo>_pedidos` | Plural of the table's logical name; read the environment's `EntitySetName` | Web API and `$batch` URL |

**The logical name does not follow from the display name by a rule.** Two examples from the same environment: `nome_completo`
became `<prefixo>_nomecompleto` (lost the `_`) and `nome_curto` became `<prefixo>_nome_curto` (kept it).
It depends on how the column was created. It has to be read from the environment (`references/as-built-names.md`).
`[verified: reference project]`

Other facts about logical names:

- The name can be **truncated** in maker captures (`<prefixo>_dataprevistadeencerramentod…`). The Web API
  returns the full name; screenshots do not.
- A column with a **repeated** display name in the table is ambiguous in Power Fx. The extractor flags it (D001).
- System columns (`createdon`, `ownerid`, `statecode`) have no prefix.

## 3. Which name in each context

| Context | Name | Example |
|---|---|---|
| Identifier in a formula (`Filter`, `LookUp`, `Sort`, `ThisItem.col`, record key in `Patch`) | **Display** | `Filter(Pedidos, unidade = "AAA")` |
| Text in double quotes: `SortByColumns`, `DisplayFields`, ComboBox `SearchFields`, and other functions that take the column name as a string | **Logical** | `SortByColumns(Pedidos, "<prefixo>_datadopedido", SortOrder.Descending)` |
| Unquoted identifier in `ShowColumns`/`RenameColumns`/`AddColumns` | **Display** | `ShowColumns(Pedidos, unidade)` |
| In-memory collection (`ClearCollect`, `Table`) | The name the collection itself defines (`Value`, etc.); the prefix does **not** apply | `DisplayFields: =["Value"]` |
| Non-Dataverse connector (Office 365 Users, etc.) | The connector's field (`DisplayName`, `Mail`) | `DisplayFields: =["DisplayName"]` |
| Flow: dynamic content in the designer | Display | — |
| Flow: expression (`outputs()?['…']`), Web API, `$select`/`$filter`, `$batch` body | **Logical** | `"<prefixo>_unidade": "@item()?['Cod_Unidade']"` |
| `$batch`/Web API URL | **EntitySet** | `POST /api/data/v9.2/<prefixo>_pedidos` |

Rule of thumb: **identifier = display; string = logical.** `[verified: reference project]` — the
`SortByColumns(…, "nome_completo", …)` written with the display name was fixed to the logical one in Studio. The
functions that take a column name as a string (`SortByColumns`, `GroupBy`, `AddColumns`, `ShowColumns`,
`RenameColumns` with a string, `DisplayFields`, `SearchFields`) require the logical name.

Source for the Dataverse connector's behavior in Power Apps:
[Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service).

## 4. Row scope: Power Fx resolves by display name

Inside `Filter`, `LookUp`, `Sort`, `AddColumns` and the other functions that open the row scope, the
column identifier is resolved against the columns **of that scope's table**, by **display** name. A logical
name — above all one from *another* table — does not resolve and the formula does not compile.

Real case `[verified: reference project]`: the `OnStart` had a chain with `Distinct(…, <prefixo>_unidade)`,
where `<prefixo>_unidade` was the logical name of a column of another table. The block did not compile and
**took down every global variable** defined after it: every screen opened in error. Fix:
use the display name of the scope table's column and, for a column of another table, rename it first
(`RenameColumns`) or fetch the record (`LookUp`) and read the field.

```
// formula bar (en-US: , and ;)
// Wrong: logical name of a column of another table inside the row scope
ClearCollect(
  colUnidades,
  Sort(Distinct(Pedidos, <prefixo>_unidade), Value)
);

// Right: display name of the scope's column
ClearCollect(
  colUnidades,
  Sort(Distinct(Pedidos, unidade), Value)
);
```

Two consequences:

1. An error in `OnStart` is not local: a formula that does not compile in `OnStart` takes the following
   globals with it. Run `OnStart` (app menu → *Run OnStart*) and check the variables pane.
2. `DisplayFields`/`SearchFields` are **not** row scope: they are strings the control evaluates against the
   source, and there the logical name is the right one. Mixing the two rules is the most common mistake.

> `Distinct` does not delegate in Dataverse (`references/dataverse-delegation.md`); the example is only about
> the name. On a large table the list of values comes from a domain table or a flow.

## 5. Data source name and primary key

- The **data source** name in the app is the name the table was added with in the app's data
  pane — normally the table's display name, but it can come with an alias (singular/plural) different
  from the table's. Read the data pane, do not assume. `[verified: reference projects]`
- A name with a hyphen, a space or starting with a digit requires **single quotes**: `'pedidos-unidade'`.
  Single quotes inside the name are doubled (`'o''brien'`).
- The **primary key** (`PrimaryIdAttribute`, `<table>id`) has the table's own name as its display name.
  In a formula this collides and needs quotes: `varPedidoSel.'pedidos-unidade'` returns the GUID.
  When sending the GUID to a flow, convert it with `Text(...)`. `[verified: reference project]`
- The **primary name** (`PrimaryNameAttribute`) is required on every table and is the label Dataverse
  uses in grids and Lookups — it is not necessarily the "descriptive" column the screen shows.

## 6. Choice, Lookup, text, Yes/No: what changes

Official type mapping of the connector (Dataverse → Power Apps): Choice and Yes/No → *Choice*; Date
and time and Date only → *DateTime*; Whole number/Decimal/Float/Currency → *Number*; Single line of text, Email, URL and Multiple lines of text →
*Text*; Unique identifier → *Guid*
([source](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service)).

### 6.1 Choice

The Choice's name in Power Fx is `'<column> (<table>)'`; the options are properties of it.
`[verified: reference project]`

Destination: Studio formula bar in en-US locale (`,` and `;`).

```
// Filter by a known option
Filter(Pedidos, situacao = 'situacao (Pedidos)'.Aberto)

// Filter by what the user chose in a ComboBox whose Items is Choices('situacao (Pedidos)').
// Two If branches OUTSIDE the Filter: IsBlank(...) || ... inside the Filter breaks delegation
// (dataverse-delegation.md §4)
If(
    IsBlank(cboSituacao.Selected),
    Pedidos,
    Filter(Pedidos, situacao = cboSituacao.Selected.Value)
)

// Write: needs the option RECORD, not the text
Patch(Pedidos, Defaults(Pedidos), { situacao: 'situacao (Pedidos)'.Aberto })

// Display as text
Text(ThisItem.situacao)
```

Destination: ComboBox properties in the pasted YAML (`,` between arguments).

```yaml
Items: =Choices('situacao (Pedidos)')
DisplayFields: =["Value"]
SearchFields: =["Value"]
```

Points of attention:

- Comparing the Choice with `.Selected` (a record) fails; `.Selected.Value` works when `Items`
  comes from `Choices(...)`. Comparing with a literal text (`situacao = "Aberto"`) does not compile.
  `[verified: reference project]`
- Writing text to a Choice does not compile: use the option object, or a `Switch` that translates the label
  into the option.
- Delegation: `=` and `<>` delegate on Choice; `<`, `<=`, `>`, `>=` and `IsBlank` **do not**
  ([Learn](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service)).
  For "no value", note 9 of the official table accepts `col = Blank()` in general, but the Choice
  row marks `IsBlank` as not delegable: test `situacao = Blank()` with `Data row limit = 1`
  before relying on it `[unverified]`.
- `Choices(...)` does not delegate and returns the list of options: it serves a ComboBox, not a large table.
- If the column **is not** a Choice in the environment, `Choices()` does not exist for it and the domain lives in the app
  (a literal table in `Items`) — see §7.
- A **global** Choice shares the options across tables; the name in Power Fx remains
  `'<column> (<table>)'`. [unverified] whether the name changes to a plain global one in every environment.
- Integer values of the options: Dataverse prefixes them per publisher (e.g. `<n>0000001`). Do not assume
  `1, 2, 3` in a load CSV or in a contract with an external system; read the environment's options
  (`GlobalOptionSetDefinitions(Name='…')`, see `references/as-built-names.md`).

### 6.2 Lookup

```
// formula bar (en-US: , and ;)
// Compare with the record
Filter(Pedidos, cliente = varClienteSel)

// Write: pass the record
Patch(Pedidos, Defaults(Pedidos), { cliente: LookUp(Clientes, nome = "Customer A") })

// Read a field of the related record
ThisItem.cliente.nome
```

`[unverified in the environment]`: the reference projects swapped every Lookup for text/Choice
before writing these formulas; the syntax above is the documented one for Lookup, with no field
evidence. Cautions that hold regardless:

- Filtering by a **column of the related table** (`cliente.nome = "X"`) forces a join on the server. The
  connector's structural limits (lookup levels, entities per query) are in
  `references/dataverse-delegation.md`. For a hot filter, **denormalize**: copy the column to the
  child table as text (`references/modeling.md`).
- `DefaultSelectedItems` wants **rows from the same source as `Items`**; `Table(<text>)` does not work.
  `[verified: reference project]`

### 6.3 Text that stores a code (the "fake lookup")

A text column that stores the abbreviation, name or code of another table. It compares text with text:

```
// formula bar (en-US: , and ;)
Filter(Pedidos, unidade = cboUnidade.Selected.sigla)   // Selected.sigla, not Selected
ThisItem.unidade                                       // already text
```

It delegates like any text equality. What is lost: **referential integrity** (an invalid
value gets in, a homonym collides) and the automatic join. See `references/modeling.md`.

### 6.4 Yes/No

`ativo = true` works and delegates; `'ativo (Pedidos)'.Yes` also exists (the en-US label). Prefer
`true`/`false`. `[verified: reference project]`

### 6.5 Date

`DateOnly` and `DateAndTime` map to DateTime. A direct date filter delegates in Dataverse, **except**
`Now()` and `Today()` applied as a date function (note 3 of the official table, in conflict with the delegation
page; see `references/dataverse-delegation.md`): compute the date in a variable first. Unlike
the SQL connector, where a direct date does not delegate behind a gateway (`default-decisions.md` B2).

## 7. Decision table by type

| Real type (`AttributeType`) | Compare | Write | ComboBox `Items` | Attention |
|---|---|---|---|---|
| `Picklist` (Choice) | `col = 'col (Table)'.Option` or `col = cbo.Selected.Value` | option object | `Choices('col (Table)')` | `<`/`IsBlank` do not delegate |
| `Boolean` (Yes/No) | `col = true` | `true`/`false` | — | — |
| `Lookup` | `col = record` | record (`LookUp`/`.Selected`) | `Filter(TargetTable, …)` | filtering by a column of the related table: denormalize |
| `String` storing a code | `col = cbo.Selected.<column>` | text | domain table or literal | no integrity; the domain lives in the app |
| `String` storing a fixed domain | `col = "Text"` | text | `["A", "B"]` (exposes `Value`) | the domain lives on the screen; nothing stops the flow from writing outside it |
| `Integer`/`Decimal` | `col = n` | number | — | arithmetic on the column does not delegate |
| `DateTime` | `col >= dateVar` | date | — | `Today()`/`Now()` in a variable |
| `Uniqueidentifier` | `col = GUID(...)` | — | — | `Text(...)` when sending to the flow |

The question that decides the syntax is always the same: **what is this column's `AttributeType` in the
as-built?** If the as-built says `?`, the formula is not written until someone reads the type.

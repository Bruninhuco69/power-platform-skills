# AS-BUILT-NAMES: the authority on names and types

`AS-BUILT-NAMES.md` is the contract of names **from the real environment**: tables, columns, types,
keys, Choices and connectors, read from where the data lives. When it diverges from the data
dictionary, the creation script or the plan, **it wins** (`default-decisions.md` N1). Template in
`assets/as-built-names-template.md`.

## Contents

1. [Why it is the authority](#1-why-it-is-the-authority)
2. [What it must contain](#2-what-it-must-contain)
3. [How to extract from the environment](#3-how-to-extract-from-the-environment)
4. [How to generate the file](#4-how-to-generate-the-file)
5. [How to maintain](#5-how-to-maintain)
6. [What to do about divergence](#6-what-to-do-about-divergence)

---

## 1. Why it is the authority

Three sources *seem* to give a column's name, and only one is the environment:

| Source | Describes | Reliable for name/type? |
|---|---|---|
| Data dictionary / plan | What was **intended** to be created | No |
| Creation script | What would **be attempted** | Only if it is what created the environment |
| Environment (maker, Web API) | What **exists** | Yes |

In a reference project, a user-registration screen was written against the dictionary and had to be
fixed in several places in Studio. None was syntax; all were name or type: tables with another name,
a prefix different from the planned one, `perfil` became a Choice (not a Lookup), `unidade` became
text (not a Lookup). The environment had been created by hand (or by Excel) with the tenant's default
publisher, **not** by the script. `[verified: reference project]` -- detail in
`references/field-lessons.md`.

Rules that follow from this:

- **No screen or flow before the as-built is filled in** (N2).
- **Before claiming a column does not exist, open the whole table schema** -- not a filtered extract,
  not a data sample (N3). A Dataverse data export to Excel carries few rows per table and can leave
  out tables the app uses: absence in the export is not absence in the environment.
- The dictionary remains useful as **intent**; when the divergence is deliberate, it becomes a
  recorded decision, not a silent deviation (`references/modeling.md`).

## 2. What it must contain

| Section | Content | Why |
|---|---|---|
| Header | Publisher prefix, environment (`<environment>`), **date and command of the extraction** | P5: a number or fact without the command that measures it goes stale |
| Tables | Source name in the app, logical name, EntitySet, primary key, primary name | Formula, flow and `$batch` each use a different name |
| Columns | Display, logical, real `AttributeType`, type in Power Fx, notes | Decides the filter and `Patch` syntax |
| Choices | Name in Power Fx and options with integer value | Contract with the load CSV and with the external system |
| Alternate keys | Columns and `EntityKeyIndexStatus` | Upsert and import |
| Connectors | Connector name **in the environment's language** | In a pt-BR environment the connector object is translated (`UsuáriosdoOffice365`) |
| Gaps | Columns marked `?` or "not confirmed", and why they do not block | A formula that depends on a gap says so |

A schema name or type not read stays **`?`**, never invented and never copied from the dictionary.

## 3. How to extract from the environment

Preferred: the Web API `EntityDefinitions`, because it returns whole names (maker screenshots
truncate long names) and real types. Source:
[Query table definitions using the Web API](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query-metadata-web-api).

### 3.1 Through the browser (what the reference projects used)

The environment host session (`<org>.crm.dynamics.com`) is separate from the maker session: opening
`/api/data/...` directly returns **HTTP 401**. Open `https://<org>.crm.dynamics.com/main.aspx` once,
complete the sign-in, and the URLs below answer JSON in the browser itself. `[verified: reference project]`
Save each response to a `.json` file.

**Tables and columns in a single call** (script input):

```
https://<org>.crm.dynamics.com/api/data/v9.2/EntityDefinitions?$select=LogicalName,SchemaName,EntitySetName,PrimaryIdAttribute,PrimaryNameAttribute,DisplayName&$filter=startswith(LogicalName,'<prefixo>_')&$expand=Attributes($select=LogicalName,SchemaName,AttributeType,AttributeTypeName,DisplayName)
```

`$expand=Attributes` only brings the **common** properties: `OptionSet` and `Targets` do not fit in
the inner `$select` (Learn, page above). For them, a call with a cast **per table**:

```
# Choice options (and global Choice)
https://<org>.crm.dynamics.com/api/data/v9.2/EntityDefinitions(LogicalName='<prefixo>_<tabela>')/Attributes/Microsoft.Dynamics.CRM.PicklistAttributeMetadata?$select=LogicalName&$expand=OptionSet,GlobalOptionSet

# Lookup target
https://<org>.crm.dynamics.com/api/data/v9.2/EntityDefinitions(LogicalName='<prefixo>_<tabela>')/Attributes/Microsoft.Dynamics.CRM.LookupAttributeMetadata?$select=LogicalName,Targets
```

**A global Choice by name** (does not accept `$filter`):

```
https://<org>.crm.dynamics.com/api/data/v9.2/GlobalOptionSetDefinitions(Name='<choice name>')
```

Metadata has no paging and no row limit: the first response brings everything. In an environment with
several languages, add `&LabelLanguages=<LCID>` to shorten it (pt-BR = 1046).

### 3.2 Through the maker (manual check)

In `make.powerapps.com` -> *Tables* -> the table -> *Columns*: shows the display name, **name** (logical)
and type. Useful to check a single column; it is **not** an extraction, because the grid truncates
long names (`<prefixo>_dataprevistadeencerramentod…`). A name truncated in the screenshot goes into
the as-built as "truncated -- do not use in `SortByColumns`/`DisplayFields`/`SearchFields` until read in full".

### 3.3 Through Studio

The app's data panel shows the name **under which the table was added** (the data source in Power
Fx), which can differ from the table's display name. The connector appears in the connections panel
with the translated name. These two names can only be read in the app, not in the Web API.

### 3.4 Through `pac` and an exported solution

`[unverified]`: the reference projects did not have `pac` installed and did not use this path.
Candidates for an environment that has it: export the solution and read `customizations.xml`; or
`pac modelbuilder build`, which generates classes with the logical names. If you use it, record the
command and the result in the as-built, as with the Web API.

## 4. How to generate the file

```
python <skill-folder>/scripts/extrair-nomes-as-built.py <export.json> --prefixo <prefix>_ `
    --complemento <prefix>_<table>=<table-choices.json> `
    --saida <path of AS-BUILT-NAMES.md>
```

(The backtick line continuation is PowerShell; in bash use `\`.) (`--complemento` is repeatable;
without `--saida` the script only validates.) The script reads only a local file, with no network,
and writes only to `--saida`; never over the input. It:

- filters tables and columns by the prefix (system columns and the primary key come in as the case requires);
- translates `AttributeType` into the type in Power Fx and the comparison rule (`references/names-and-types.md` §7);
- flags the primary key whose display name collides with the table's (quotes required);
- reports a table without attributes (`E002`), a Choice without options (`A003`), a repeated display name (`D001`).

The generated file is **generator output** (P3): mark it "generated -- do not edit", and take a manual
correction to the input (redo the export). The parts the Web API does not give -- the source name in
the app, the connector name, modeling decisions -- go in a separate, hand-written section that the
generator does not touch (copy the template and keep the two sections in separate files if you prefer).

## 5. How to maintain

- **Version it in Git** next to the app; the as-built diff is the best warning that the environment changed.
- **Re-extract** on every schema change, every new table and before any wave of screens.
  Whoever changes the environment (maker or script) is who re-extracts.
- **Write the date and the command** in the header. A document that states a number or fact carries
  the command that measures it (P5).
- **Point to the path in `power-platform.config.json`** (`nomes_as_built`) for humans and agents. The
  `validar-telas.py` only checks the publisher prefix (T014); checking a name against the as-built is
  manual (or with `extrair-nomes-as-built.py` + reading).
- Do not fill a gap by inference: if a screen depends on a `?` column, the pending item is recorded
  and the screen avoids the dependency (e.g. sort with `Sort(...)` instead of `SortByColumns(...)` until the
  logical name is read). `[verified: reference project]` -- that defense nullified the only wrong
  name guess in a round of screens.

## 6. What to do about divergence

When the as-built differs from the dictionary, decide and write it down -- do not leave the deviation as a fact of life:

| Option | Cost | When |
|---|---|---|
| **Keep the as-built** | Fast; loses the integrity the dictionary foresaw (Lookup -> text) | Small table, low risk, short deadline |
| **Realign the environment to the dictionary** | Recreate tables and re-import | When integrity or a closed domain is a requirement |
| **Update the dictionary** | Cheap | When the environment is right and the paper was wrong |

The decision applies to each table, and it changes the filter and `Patch` syntax of the following
screens -- which is why it is a prerequisite for them. Record it in a project ADR (`default-decisions.md`, A4 and §8).

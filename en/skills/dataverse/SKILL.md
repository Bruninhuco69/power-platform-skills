---
name: dataverse
description: "Use when the Power Apps app or the flow reads or writes Dataverse tables: writing or fixing a formula that filters, sorts, compares or writes a Dataverse column; finding the right table or column name (logical, display, schema, publisher prefix); deciding Choice, Lookup or text; building or updating the AS-BUILT-NAMES; delegation on the Dataverse connector (what delegates, 500/2,000); designing a security role, business unit, owner team or column security; modeling a table, relationship, alternate key or calculated column; importing CSV or Excel. Terms: \"what is the column name\", \"Choice or text\", \"user sees all units\", \"import a spreadsheet\". Do not use for screen YAML, Power Fx outside Dataverse, combo boxes and UX (use `powerapps-canvas`), flows, `$batch` and HTTP (use `power-automate`), procedures and SQL Server (use `sql-procedures`), solutions, environments and connection references (use `power-platform`)."
argument-hint: "[names|types|delegation|security|model|import|as-built] [table or column]"
user-invocable: true
---

# Dataverse in Power Apps apps

This skill delivers what the app and the flow need to know about Dataverse to avoid mistakes: the
right name of each table and column **in the real environment**, the real type (Choice, Lookup or
text) and the syntax it requires, what delegates, who can read which rows, how to model and how to
import. The central artifact is the project's `AS-BUILT-NAMES.md`.

Boundaries: what lives here is *how the Dataverse column shows up in Power Fx*, the alternate key
and the table. The rest of Power Fx belongs to `powerapps-canvas`; `$batch` and the flow belong to
`power-automate`; ALM (solution, environment, environment variable) belongs to `power-platform`.
Decided standards (N1-N3, A3, A4) are in `skills/power-platform/references/default-decisions.md` --
this skill points to them, it does not repeat them.

## Non-negotiable rules

1. **Read the project's `AS-BUILT-NAMES.md` before writing or judging any formula or flow that
   touches Dataverse.** The data dictionary, the creation script and the plan lose to it (N1). Path
   in `power-platform.config.json` -> `nomes_as_built`. If the file does not exist, the first step is
   to extract it (`references/as-built-names.md`), not to guess.
   Why: a screen written against the dictionary needed several fixes in Studio; all were name and
   type, none was syntax.
2. **One name per context.** An identifier in a formula = **display** name; text between double
   quotes (`SortByColumns`, `DisplayFields`, `SearchFields`), OData, Web API and `$batch` =
   **logical** name; the `$batch` URL = **EntitySet** (plural). Never derive one name from another.
   Why: the logical name does not follow from the display name by any rule, and a column error in a
   string fails silently.
3. **Real type before syntax.** Choice compares with an option, Lookup with a record, text with text.
   Confirm the `AttributeType` in the as-built before writing the `Filter` or the `Patch`.
   Why: the real environment swapped Lookup for Choice and for text; the syntax changes in each case.
4. **Before saying a column does not exist, open the whole table schema** -- never a filtered
   extract or a sample (N3).
   Why: an extract with `$filter` or a sample export omits columns and produces a false "does not exist".
5. **Every query declares what delegates**, and the test is `Data row limit = 1` in Studio. The
   absence of a yellow triangle does not prove delegation.
   Why: a non-delegated query downloads 500 (up to 2,000) rows and filters on the client, with no error.
6. **A screen filter is not access control** (A3). A Security Role at Organization scope lets any
   user with access to the table read all units through Excel, Power BI or the Web API.
   Row isolation requires Owner Team + Business Unit, or the accepted risk is written down.
   Why: the unit scope in the gallery is a convenience; whoever reads straight from the API ignores the gallery.
7. **A single owner of schema creation per environment**: script *or* maker, never both. Once the
   schema is created, extract the as-built and write against it.
   Why: the real environment was created by hand with the tenant's default publisher, with a prefix
   and types different from the script's.
8. **Upsert and `$batch` by business key require an alternate key in `Active` state.**
   Why: a `Pending` key resolves neither Lookup on import nor upsert, and the error is silent.
9. **Text does not become Choice or Lookup later.** Decide the type before importing; importing
   first and adjusting later means rebuilding the table.
   Why: the import wizard creates text columns and Dataverse does not convert them. The mockup load
   of `/pp-en:architecture` exists to get the type wrong on the mockup, where recreating is free.
10. **Never claim "✅ done" about a name or type without the command that finds the evidence again**
    (a dated extraction from the environment). Why: P2 and P5 in `default-decisions.md`.

## Workflow

1. **Classify the task and load only what is needed:**

   | Task | Load |
   |---|---|
   | Write/fix a formula or flow that reads or writes a Dataverse column | `references/names-and-types.md` + the project's `AS-BUILT-NAMES.md` |
   | "What is the right name of...", build or update the as-built | `references/as-built-names.md`, `assets/as-built-names-template.md`, `scripts/extrair-nomes-as-built.py` |
   | Audit delegation, counter, truncating gallery | `references/dataverse-delegation.md` |
   | "Any user sees all units", role, BU, owner team | `references/security.md` |
   | Create table, relationship, key, calculated column, auditing | `references/modeling.md` |
   | Import CSV/Excel, migrate legacy data, load with Lookup | `references/data-import.md` |
   | Create the tables from the `.xlsx` mockup load; check the types Dataverse inferred | `skills/power-platform/references/mockup-load.md` and `scripts/montar-carga-mockup.py --conferir` (from the orchestrator) |
   | Create tables, typed columns, relationships and the mockup load straight through the Web API, by a flow | `skills/power-platform/references/dataverse-builder.md` (`montar-carga-mockup.py --flow`) |
   | "Has this happened before?" (field lessons) | `references/field-lessons.md` |

2. **Confirm the track.** The project's `trilha_dados` must be `dataverse` (A4). If the question is
   "Dataverse or SQL Server?", do not decide here: point to the technology matrix
   (`skills/power-platform/references/technology-matrix.md`) and to the project's ADR. Signs that
   push toward SQL: corporate data already in SQL, a DBA who owns the schema, a strong multi-table
   transaction, gallery volume above the delegation cap. Switching tracks requires an ADR.
3. **Read the as-built** (rule 1). Note what is marked `?` or "not confirmed": those are gaps, and a
   formula that depends on them says so in writing.
4. **Write or audit** using the reference for the task. A delivered formula carries its destination
   (`formula bar (en-US: , and ;)` or `pasted YAML (, and ;)`, see `default-decisions.md` §3) and
   its declared delegability (T7).
5. **Close** with the definition of done below. Did a name or type change in the environment?
   Re-extract the as-built *before* moving on.

## References

| File | When to read |
|---|---|
| `references/names-and-types.md` | Publisher and prefix; logical × display × schema × EntitySet; how Power Fx resolves in each context (row scope!); Choice × Lookup × text: compare, filter, write |
| `references/as-built-names.md` | Why it is the authority; how to extract (maker, Web API, pac); how to maintain and version |
| `references/dataverse-delegation.md` | What delegates in Dataverse, difference from the SQL connector, 500/2,000, 50,000, `In`, `StartsWith`, `CountRows` |
| `references/security.md` | Security role, BU, owner team, row scope, column security, the risk of Organization scope |
| `references/modeling.md` | Tables, ownership, relationships, alternate keys, calculated and rollup columns, auditing |
| `references/data-import.md` | CSV/Excel/dataflow, load order with Lookup, how to avoid script × environment divergence |
| `references/field-lessons.md` | Field lessons: what has already gone wrong in real projects and which rule prevents it |
| `assets/as-built-names-template.md` | Copyable template of `AS-BUILT-NAMES.md` |

## Scripts

`<skill-folder>` is the *Base directory* shown when the skill is loaded. Run **from the project root** (the script looks for `power-platform.config.json` from the current directory upward) or pass `--config`.

| Command | What it checks | Exit |
|---|---|---|
| `python <skill-folder>/scripts/extrair-nomes-as-built.py <export.json> --prefixo <prefix>_` | Validates the Web API JSON (`EntityDefinitions` + `Attributes`): E001 JSON/format, E002 table without attributes, E003 prefix without a table, A001 column without a display name, A003 Choice without options, D001 repeated display name | 0 no error · 1 with error · 2 usage |
| `… --complemento <prefix>_<table>=<choices.json>` (repeatable) | Merges Choice options and Lookup targets coming from the queries with a cast; E004 table does not exist, E005 unreadable file | 0 / 1 / 2 |
| `python <skill-folder>/scripts/extrair-nomes-as-built.py <export.json> --prefixo <prefix>_ --saida AS-BUILT-NAMES.md` | Same, and **generates** the markdown in the template's format. Writes only with `--saida` (`-` prints); refuses to overwrite the input; no network | 0 / 1 / 2 |

The script only reads a local file; the export itself (one query to the Web API) is done by you in
the authenticated browser -- step by step in `references/as-built-names.md`.

## Definition of done

Commands from the project root (note under Scripts); the repository lint runs from the repository root.

- [ ] The as-built exists, is from the current environment and carries the extraction date.
  Evidence: `python <skill-folder>/scripts/extrair-nomes-as-built.py <export.json> --prefixo <prefix>_ --saida <as-built path>` -> `0 error(s)`.
- [ ] Every table and column cited in the formula or flow appears in the as-built with the same name.
  Evidence: `rg -n "SortByColumns|DisplayFields|SearchFields|ShowColumns" <screens folder>`; each
  listed string is a logical name present in the as-built.
- [ ] Every `Filter`/`Patch` on Choice, Lookup or text uses the syntax of the real type.
  Evidence: `rg -n "\.Selected\b" <screens folder>` with no `.Value` where the column is Choice.
- [ ] Delegation declared and tested. Evidence: Studio with `Data row limit = 1`, gallery and
  counters checked; result noted in the screen header (T7).
- [ ] Security: isolation was tested outside the app. Evidence: with a test account from another
  unit, `GET <org>/api/data/v9.2/<EntitySet>?$top=5` returns only the permitted rows -- or the
  accepted risk is recorded in writing.
- [ ] If there is an upsert by key: `GET .../EntityDefinitions(LogicalName='<table>')/Keys?$select=SchemaName,EntityKeyIndexStatus` -> `Active`.
- [ ] `python tools/lint_skills.py skills/dataverse` -> `0 error(s)`.

## Pitfalls

1. Writing against the dictionary instead of the environment -- [as-built-names](references/as-built-names.md).
2. Schema name in a formula, or display name in `SortByColumns` -- [names-and-types](references/names-and-types.md).
3. In row scope Power Fx resolves a column by its **display** name; `Distinct(…, <prefix>_column)` in `OnStart` took down all the globals -- [names-and-types](references/names-and-types.md).
4. Comparing Choice with text or with a record; writing text into a Choice -- [names-and-types](references/names-and-types.md).
5. Primary key whose display name equals the table's (`'table'` needs quotes) -- [names-and-types](references/names-and-types.md).
6. Trusting the absence of the delegation triangle; `With`/`Set` over a source -- [dataverse-delegation](references/dataverse-delegation.md).
7. `CountRows` with no filter is approximate (cache); a counter that shows 50000 may be the broken query -- [dataverse-delegation](references/dataverse-delegation.md).
8. A Security Role at Organization scope treated as isolation -- [security](references/security.md).
9. Lookup swapped for text with no integrity: an invalid unit gets in, a homonym collides -- [modeling](references/modeling.md).
10. Importing before creating Choice, Lookup and key -- [data-import](references/data-import.md).
11. Trusting the type Dataverse inferred from Excel: it is often wrong; check with `--conferir` before the real data, or create through the builder, which sends the spec's type -- `skills/power-platform/references/mockup-load.md`, `dataverse-builder.md`.

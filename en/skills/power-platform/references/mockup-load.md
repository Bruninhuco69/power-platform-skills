# Mockup load for the tables: `.xlsx` for Dataverse, `INSERT` for SQL

`/pp-en:architecture` produces a **mockup load** together with the data model: made-up data for
every table, in an `.xlsx` with one sheet per table. On Dataverse, it creates all the tables at once
and helps type inference get it right. On SQL Server, it comes with an `INSERT` script for the DEV
database. `scripts/montar-carga-mockup.py` generates it from the `mockup-load.json` spec.

Dataverse has a second path, with no type inference: with `--flow`, the script also generates the plan
for the **Dataverse Builder**, a flow that creates the tables, columns, relationships and mockup rows
through the Web API ([dataverse-builder.md](dataverse-builder.md)). The user picks in `/pp-en:architecture`.

## Contents

1. [What it is for](#1-what-it-is-for)
2. [The `mockup-load.json` spec](#2-the-mockup-loadjson-spec)
3. [Generate](#3-generate)
4. [Dataverse: import everything at once](#4-dataverse-import-everything-at-once)
5. [Dataverse: check the types before real data](#5-dataverse-check-the-types-before-real-data)
6. [SQL Server: load into the DEV database](#6-sql-server-load-into-the-dev-database)
7. [Codes](#7-codes)
8. [Sources](#8-sources)

---

## 1. What it is for

- **Dataverse.** When you create a table from an Excel file, Dataverse **infers** each column's name
  and type from the data. Microsoft itself warns that the inference "may not be 100% accurate". That
  is why the mockup load is built so the inference gets it right:
  - a date is a date in the cell;
  - a code has a letter;
  - a decimal has a fraction;
  - a long text goes past 100 characters;
  - a Choice shows all its options.
- **Even so, Dataverse often gets the typing wrong.** Always warn the user: after importing, they
  check column by column (§5) before loading any real data. Anyone who wants the right type without
  inference uses the builder ([dataverse-builder.md](dataverse-builder.md)).
  - A mistake in the mockup is cheap: you recreate the column.
  - A mistake in real data becomes a migration.
  - Text does not turn into a Choice or a Lookup later (rule 9 of the `dataverse` skill).
- **SQL Server.** The type comes from the DDL, so there is no inference. The load serves three purposes:
  - having data in DEV to test screens, procedures and delegation;
  - proving the DDL accepts the model's values: size, required columns and foreign keys in the right
    order;
  - reviewing with the process owner through the same `.xlsx`.
- **Made-up data only.** E-mail and URL use a fictitious domain (`contoso.com`, `example.com`). No
  real person, customer or unit names. On Dataverse, the uploaded file goes through Copilot and is
  kept in the environment's *File Upload* table, and it is not deleted on its own.

## 2. The `mockup-load.json` spec

Template: `assets/mockup-load-template.json`, with `Unit` and `Order` and the codes `AAA`/`BBB`/`CCC`.
`pp-en:architecture-agent` writes the spec, at the same time as the data model, in this track folder:
- `Backend/Dataverse/carga-mockup.json`;
- `Backend/SQL Server/carga-mockup.json`, outside `pastas.procedures`.

| Field | Required | Content |
|---|---|---|
| `trilha` | no | `dataverse` or `sql-server`. `--trilha` wins, then `trilha_dados` from the config; if the spec says otherwise, it is an ERROR |
| `linhas` | no (10) | rows per table, from 1 to 200. The table's `linhas` > `--linhas` > this > 10 |
| `data_base` | no (`2026-01-13`) | first generated date (`YYYY-MM-DD`); generated dates skip days 1 to 12 (§4) |
| `tabelas[].nome` | yes | table **display** name; becomes the sheet name. Up to 31 characters, without `: \ / ? * [ ]` |
| `tabelas[].sql`, `pk` | SQL | `schema.Table` from the DDL; `pk` is the IDENTITY column the foreign keys use |
| `tabelas[].logico` | no | logical name in Dataverse (`<prefix>_order`); `--conferir` finds the table by it |
| `tabelas[].colunas[].nome` | yes | **display** name; becomes the column header |
| `colunas[].tipo` | yes | one from the table below |
| `colunas[].primaria` | Dataverse | one per table: the primary name. The Lookup finds the row by it during import, and it cannot change once created |
| `colunas[].chave` | no | alternate key (one per table). On SQL, the foreign key finds the row by it |
| `colunas[].obrigatoria`, `tamanho`, `casas` | no | required; maximum text length; decimal places of the decimal and currency (2) |
| `colunas[].opcoes` | Choice | option labels, no repeats |
| `colunas[].alvo` | Lookup | `nome` of the target table |
| `colunas[].exemplos` | no | fictitious values; without them, the script generates some. Key and primary need one per row |
| `colunas[].sql`, `logico` | SQL / no | column name in the DDL; logical name in Dataverse |

| `tipo` | Dataverse | SQL (value in the `INSERT`) | Generated value |
|---|---|---|---|
| `texto` | Single line of text | `N'…'` | `<column> 01` (`<table> 01` on the primary) |
| `texto_longo` | Multiple lines of text | `N'…'` | sentence of more than 100 characters |
| `codigo` | Text (never number) | `N'…'` | `PRO001`: has a letter, so it does not become a number |
| `inteiro` | Whole number | `3` | multiples of 3 |
| `decimal`, `moeda` | Decimal number, Currency | `150.90` | with a fraction, so it does not become a whole number |
| `data` | Date and time, Date only behavior | `'20260113'` | every 3 days from `data_base`, only on day 13 or later |
| `data_hora` | Date and time | `'2026-01-13T08:30:00'` | one day (13 or later) and one hour per row |
| `sim_nao` | Yes/No | `1` / `0` | alternates |
| `choice` | Choice | the label, `N'Open'` | cycles through all options |
| `lookup` | Lookup | subquery by the target's key | cycles through the target's rows |
| `email`, `telefone`, `url` | Text with format | `N'…'` | `usuario01@contoso.com`, `(11) 90000-0001`, `https://contoso.com/…` |
| `autonumero` | Autonumber | outside the `INSERT` (IDENTITY) | `PRO001` |
| `escolhas`, `imagem`, `arquivo` | create by hand | outside the `INSERT` | outside the spreadsheet (C010) |
| `calculada` | create by hand | outside the `INSERT` (computed column) | outside the spreadsheet |

On SQL, the Choice stores the label as text. If the DDL uses a code, model the column as `inteiro` with
`exemplos`, or as a `lookup` to the domain table.

## 3. Generate

Run from the project root (the script looks upward for `power-platform.config.json`):

```bash
# validates and shows the load order, without writing
python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json
# writes mockup-load.xlsx (and mockup-load.sql on the SQL track)
python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json --saida Backend/Dataverse
# also one file per table, for the assistant that reads only the 1st sheet
python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json --saida Backend/Dataverse --uma-por-tabela
# Dataverse through the builder: also the plan and the flow (dataverse-builder.md)
python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json --saida Backend/Dataverse --flow
```

What comes out:
- **One sheet per table, in load order.** Whatever a Lookup points to comes first, for example
  `Unit → Order`.
- **Each sheet is an Excel table**, with a frozen header.
- **On the Dataverse track, the last sheet is `Type check`.** For each column it shows:
  - the model's type;
  - what to pick in Dataverse;
  - what usually goes wrong;
  - the "Came as" and "Checked" columns, to fill in.
- **The output is deterministic:** the same spec produces the same bytes.
- **On the Dataverse track, every run without errors ends with warning C013 (check the typing).** Each
  Choice or Lookup column also gets a C014 (arrives as text). Repeat the warnings to the user in the
  script's words. `--conferir` does not repeat these warnings: it is already the check. With `--flow`,
  C013 and C014 give way to a single C018 (prove it with `--conferir` after the builder).

## 4. Dataverse: import everything at once

If the user chose the builder, follow [dataverse-builder.md](dataverse-builder.md) and skip to §5. The
rest of this section is the spreadsheet path.

**Before importing, set the preferred solution** with the project's publisher (Power Apps ›
Solutions › *Set preferred solution*). Without it, the tables are born in the default solution, with
the default publisher's random prefix (`cr8a3_…`), and not with the project's `prefixo_publisher`.
This really happened: the reference project's environment was created that way
`[verified: reference project]`.

**Path A: Power Query, everything at once** (recommended).
1. Tables › Import › Import data › Excel workbook; upload `mockup-load.xlsx`.
2. In the navigator, tick **all the table sheets**. Leave `Type check` out.
3. In the editor, check the type icon in each column header. Power Query also infers the type from
   the rows. Fix the type here: it is free.
4. Next › **Load to new table**, for each query:
   - **Unique primary name column** = the spec's `primaria`;
   - long text = *Multiple lines of text*.
5. Publish.

The steps are the ones from Learn, where "Load to new table" is still in preview. This path requires the
Power Apps per-user or per-app license.

**Path B: one table per file, with Copilot.**
1. Tables › New table › Create with external data › File. This assistant reads **only the first range
   of the first sheet**, so generate with `--uma-por-tabela`.
2. Upload the files in `mockup-load-tables/` in number order (`01-…`, `02-…`).
3. In the preview, **before Create**, open each column (Edit column) and fix the type. For the Choice,
   fill in the options and the default. Also check the primary name and the row ownership.

**On both paths, check a date after importing.** The import once swapped day and month in a reference
project. That is why generated dates have day 13 or later: if the import swaps them, the month is
invalid and the row is rejected, instead of going in with the wrong date. The spec's `exemplos` with a day
up to 12 do not have this protection. The import also does not write owner or creation date.

**On both paths, the Lookup is not created:** the column arrives as text. For each Lookup:
1. Create the relationship: in the data workspace, drag from the child table to the parent, or create
   a Lookup column.
2. Delete the text column.
3. Create the alternate keys (the spec's `chave`) and wait for `EntityKeyIndexStatus = Active`
   (`dataverse` skill, `references/modeling.md`).

## 5. Dataverse: check the types before real data

1. **Export the schema:** the same `EntityDefinitions` + `$expand=Attributes` query from
   `references/as-built-names.md` of the `dataverse` skill, saved as `export.json`.
2. **Compare:**
   `python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json --conferir export.json`
   - **C103:** the type came out wrong. Recreate the column while there are only mockup rows.
   - **C105:** the primary name came out wrong. Recreate the table, because it cannot change later.
   - **C101/C102:** the table or column was not found by display name. Fix the name, or give
     `logico` in the spec.
   - **C104:** the export does not prove this point. Check it in the maker: date behavior, Choice
     options, Lookup target, text format.
3. Repeat until `0 error(s)`. Fill in "Came as" and "Checked" on the check sheet, with the date.
4. Extract the `AS-BUILT-NAMES` (`extrair-nomes-as-built.py`). From here on, it is the authority.
5. **Mockup rows.**
   - They stay in DEV only: delete them before the real load or keep them for tests.
   - The solution does not carry data to UAT and PROD.
   - The real load follows `references/data-import.md` of the `dataverse` skill, for tables that
     already exist.

## 6. SQL Server: load into the DEV database

1. Apply the DDL to the DEV database, in the package's order (`sql-procedures` skill).
2. Run `mockup-load.sql` (SSMS, or `sqlcmd -S <server> -d <database> -i mockup-load.sql`).
   - **Transaction:** a single one, with `XACT_ABORT`. An error rolls everything back.
   - **Order:** the foreign keys' order. The Lookup becomes a subquery by the target's `chave` when the
     target has an IDENTITY `pk`; without `pk`, it writes the literal key.
   - **Re-run:** a `THROW` guard stops the script if the first mockup row already exists. To reload,
     delete the mockup rows first.
   - **Formats:** date as `YYYYMMDD` and date and time as ISO with `T`, which do not depend on
     `SET DATEFORMAT`; the file comes out as UTF-8 with BOM, so SSMS reads the accents.
3. A size, `NOT NULL` or foreign key error here is a **DDL or spec defect**: fix the model, never the
   generated script.
4. **Never run it in UAT or PROD.** The script does not go into the DBA package.

## 7. Codes

| Code | Level | Cause | What to do |
|---|---|---|---|
| C001 | ERROR | root without `tabelas`, `linhas` outside 1–200, invalid `data_base` | fix the spec |
| C002 | ERROR | track undefined or different from the config's | `--trilha`, `trilha_dados` or `trilha` in the spec, just one |
| C003 | ERROR | table without a name or columns, repeated, invalid or reserved sheet name | rename it |
| C004 | ERROR | column without a name, repeated, unknown type, `tamanho`/`casas` outside the type | fix the column |
| C005 | ERROR | Dataverse without exactly one `primaria`; primary or key with a type that does not accept it; more than one `chave` | adjust the marks |
| C006 | ERROR | Choice without `opcoes`; Lookup without `alvo`, with a missing target or with a target that has no key or primary | complete the model |
| C007 | ERROR | Lookups in a cycle between tables | load one without the Lookup and fill it in later, or break the cycle |
| C008 | ERROR | example invalid for the type, outside `tamanho`, outside the options, with no match in the target; repeated or short key | fix the `exemplos` |
| C009 | ERROR | SQL track without a valid `sql` on the table or column; invalid `pk`; Lookup by a key the database generates | complete with the DDL names |
| C010 | WARNING | `escolhas`, `imagem`, `arquivo` (and `calculada` on Dataverse) stay out of the load; with `--flow`, only `calculada` | create the column by hand |
| C011 | WARNING | Choice with more options than rows | raise `linhas` or create the missing options |
| C012 | WARNING | e-mail or URL on a non-fictitious domain | replace it with `contoso.com` |
| C013 | WARNING | always on Dataverse: type inference gets it wrong | §5 before real data |
| C014 | WARNING | Choice or Lookup on Dataverse arrives as text | recreate it with the right type (§4, §5) |
| C015 | ERROR | could not write (file open in Excel, folder without permission) | close the file and run again |
| C016 | ERROR | `--flow`: logical name that cannot be derived, repeated or equal to the primary key | give `logico` |
| C017 | ERROR | `--flow`: Dataverse limit (currency decimal places, text length, value larger than the column, number outside the type, date before 1753, `{{` in the value, Lookup to a later row of the same table) | adjust the spec |
| C018 | WARNING | `--flow`: prove it with `--conferir` after running the builder | §5 |
| C101–C105 | ERROR/WARNING | `--conferir`: missing table, missing column, different type, point the export does not prove, primary name | §5 |

## 8. Sources

- Create a table with external data (Excel, 20-row preview, Copilot):
  <https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-edit-entities-portal>
- What the inference does and the "first sheet" limit, "may not be 100% accurate":
  <https://learn.microsoft.com/en-us/power-apps/maker/common/faqs-excel-to-table-app>
- Power Query, Load to new table, primary name column:
  <https://learn.microsoft.com/en-us/power-query/dataflows/add-data-power-query>
- Import into an existing table, types not supported on import:
  <https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-import-export>
- Preferred solution and the default publisher's prefix:
  <https://learn.microsoft.com/en-us/power-apps/maker/data-platform/preferred-solution>

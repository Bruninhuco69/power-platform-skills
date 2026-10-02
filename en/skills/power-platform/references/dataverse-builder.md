# Dataverse Builder: the flow that creates the tables and the mockup load through the Web API

The alternative to the spreadsheet on the Dataverse track. `montar-carga-mockup.py --flow` compiles
`carga-mockup.json` into a **plan** (`dataverse-plan.json`), and a fixed flow, the **Dataverse Builder**,
runs the plan through the Web API:
- creates the tables, each with its primary name;
- creates the columns with the spec's type, including Choice with its options, Email, URL, Phone,
  Autonumber, Choices, Image and File;
- creates the relationships (the Lookups);
- loads the mockup rows, already pointing to the right parent;
- creates the alternate keys.

Nothing is inferred: the type is what the spec says. The spreadsheet is still always produced, as a
reference.

> Status: the plan and the package are tested in the kit (generated, validated by `verificar-fluxo.py`).
> Running in a real environment has **not been confirmed** yet: see §9 before the first use.

## Contents

1. [Spreadsheet or builder](#1-spreadsheet-or-builder)
2. [Prerequisites](#2-prerequisites)
3. [Generate](#3-generate)
4. [Install the flow (once per environment)](#4-install-the-flow-once-per-environment)
5. [Run](#5-run)
6. [Read the result](#6-read-the-result)
7. [After the builder](#7-after-the-builder)
8. [The plan inside](#8-the-plan-inside)
9. [What has not been verified yet](#9-what-has-not-been-verified-yet)
10. [Sources](#10-sources)

---

## 1. Spreadsheet or builder

In `/pp-en:architecture`, Dataverse track, the user chooses how the tables are born:

| | Builder (recommended) | Spreadsheet only |
|---|---|---|
| Column type | the spec's | inferred from the data, and often wrong |
| Choice and Lookup | born right, with options and relationship | arrive as text and are recreated by hand |
| Alternate key | created | by hand |
| Requires | premium connector allowed and a customization role (§2) | Power Apps license |
| Effort | install the flow once, then one click per plan | import and check column by column |

Without the prerequisites in §2, use the spreadsheet (`mockup-load.md` §4).

## 2. Prerequisites

- **"HTTP with Microsoft Entra ID (preauthorized)" connector** (`shared_webcontents`). It is premium,
  and the environment's data policy (DLP) has to allow it. There is a newer version of the connector
  that requires administrator consent; the builder uses the preauthorized one.
- **Role of whoever runs it** (the connection owner): System Administrator or System Customizer.
  Creating a table and a column is a customization privilege.
- **An unmanaged solution with the project's publisher.** It gives the table prefix and the option
  value prefix. It is the same preferred solution as for the spreadsheet. A `crNNN` prefix usually
  belongs to the environment's default publisher: the first line of the report shows the prefix read.
- **DEV environment.** The mockup rows stay in DEV only, and the solution does not carry data to UAT
  and PROD.

## 3. Generate

```bash
python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json --flow --saida Backend/Dataverse
```

Besides the spreadsheet, this produces:

| File | What it is |
|---|---|
| `dataverse-plan.json` | the Web API requests, in order, with nothing from the environment. Changes with every spec |
| `dataverse-builder/ConstrutorDataverse_1_0_0_0.zip` | unmanaged solution with the flow, to import. The same in every project |
| `dataverse-builder/builder-scope.json` | the same flow as a scope, to paste into the designer if the import refuses the `.zip` |

- **`--idioma <code>`**: language of the `.zip` solution (default `1046`, pt-BR). Use the
  environment's base language (`1033` if it is English). The table labels do not depend on this: the
  flow reads the base language.
- **Findings specific to `--flow`** (besides C001–C015):
  - **C016** (ERROR): logical name that cannot be derived, repeated or that collides with the primary
    key; give `logico` in the spec.
  - **C017** (ERROR): Dataverse limit. Currency with more than 4 decimal places, single line of text
    with more than 4000 characters, value larger than the column created (without `tamanho`, the
    builder creates text with 100, phone with 50, URL with 200 and long text with 2000), number outside
    the type's range, date before 1753, `{{` or a control character in a name, option or value, or a
    Lookup to the table itself pointing to a later row.
  - **C018** (WARNING): after running, prove it with `--conferir`. With `--flow`, it replaces the import
    warnings (C011, C013, C014), and C010 only shows up for `calculada`.
- **Without `--saida`**, it only validates and shows the summary (`# builder: N step(s)…`).

## 4. Install the flow (once per environment)

**Path A: import the solution** (recommended).
1. Power Apps › Solutions › Import solution › upload `ConstrutorDataverse_1_0_0_0.zip`.
2. On the connection reference "Dataverse Builder - HTTP with Microsoft Entra ID", create the connection:
   - **Base Resource URL** = the environment URL, `https://<org>.crm.dynamics.com`;
   - **Microsoft Entra ID Resource URI** = the same URL.
3. Import. Open the **Dataverse Builder (kit)** flow and **turn it on**: once imported, it comes turned
   off.

The import creates the `kitpowerplatform` publisher (prefix `kitpp`), only for the flow. The tables do
not use this publisher: they go into the solution you give when you run it.

**Path B: paste the scope**, if the import refuses the package.
1. Create an instant cloud flow, **Manually trigger a flow**, with two inputs, in this order: **File**
   named `Plan` and **Text** named `Solution`.
2. Create three **Initialize variable** actions at the root: `Falhou` (Boolean, `false`), `Ja_existe`
   (Boolean, `false`) and `Relatorio` (Array, `[]`).
3. Below them, `Ctrl+V` with the contents of `builder-scope.json` (`power-automate` skill,
   `references/clipboard-format.md`). Then check in "Configure run after" that the `Construtor` scope
   runs after the last variable, and not in parallel with them.
4. In the four HTTP actions (`Consultar_solucao`, `Consultar_idioma`, `Consultar`, `Enviar`), choose the
   HTTP with Microsoft Entra ID connection from §4 A, step 2.
5. Open the variable actions. If any came without the name (`power-automate` skill,
   `references/clipboard-format.md` §7), choose:
   - `Falhou` in `Marcar_lote`, `Marcar_falha` and `Marcar_ambiente`;
   - `Ja_existe` in `Zerar` and `Marcar_existe`;
   - `Relatorio` in `Anotar_solucao`, `Anotar_lote`, `Anotar_ok`, `Anotar_falha`, `Anotar_pulado` and
     `Anotar_ambiente`.

The scope already comes in the shapes that paste (condition as an object with `and`/`or`, no variable
alone in a field); `verificar-fluxo.py` checks both (F020, F022).

## 5. Run

Run the flow and give:
- **Plan**: the `dataverse-plan.json`;
- **Solution**: the **unique name** of the unmanaged solution (Solutions, Name column).

What it does:
1. **Checks the environment.** Reads the solution, which gives the publisher prefix and the option value
   prefix, and the base language. Stops if the solution does not exist, if it is managed or if the file
   is not a kit plan.
2. **Swaps the placeholders** (`{{prefixo}}`, `{{opcao}}`, `{{idioma}}`) for the environment's, one step
   at a time: the whole plan in a single expression would go over the flow's size limit.
3. **Runs the steps one at a time**, in order: tables, columns, relationships, publish, data, keys.
   - **Before each step**, it checks whether what the step creates already exists. If it does, it skips.
   - **Data:** one `$batch` per batch (up to 100 rows and about 60 thousand characters), in a single
     changeset: the batch goes in whole or not at all. The batch is skipped if its first row already
     exists.
   - **2 s pause between steps**, because the connector accepts 100 calls per minute per connection.
     With 6 tables and about 50 columns, the run takes a few minutes.
4. **Stops at the first error.** The remaining steps are skipped and show up in the report as `not run`.

**Running again is safe.** What already exists is skipped, so you can fix the spec, generate the plan
again and repeat. To reload a table's data, delete its mockup rows first.

## 6. Read the result

- **The first line of the report** is the environment: the solution, prefix, option prefix and language
  read. If the prefix is not the project's, the solution given is the wrong one.
- **Successful run:** the `Resumo` action shows each step as `done` or `already existed`.
- **Failed run:** the error message is the first failure in the report: the step number, the label
  (`Order.Status`, `Order: 10 row(s)`) and the detail returned by the Web API. The following steps
  show up as `not run`. The action that failed is in the run history (`Enviar` or `Consultar`, inside
  `Passos`).
- **Error in the data batch:** the rejected batch usually comes back as an error of the call itself
  (`Enviar` fails, and the report carries the status and the already decoded `$batch` response). If it
  returns 200, the flow looks for `HTTP/1.1 4xx` or `5xx` inside the response and keeps the excerpt.
- **"Already exists" right after a timeout:** the HTTP action retries by itself on errors 408, 429 and
  5xx. A table `POST` that went past 120 s may have finished on the server, and the retry gets
  "already exists". Run again: the step's check sees it exists and skips it.

Fix it in the spec, never in the plan: the plan is generated.

## 7. After the builder

1. **Prove the types:** export the schema and run
   `montar-carga-mockup.py <spec> --conferir export.json` until `0 error(s)` (`mockup-load.md` §5). The
   builder sends the right type, and the check proves the environment accepted it.
2. **Extract the `AS-BUILT-NAMES`** (`extrair-nomes-as-built.py`, `dataverse` skill). From here on, it is
   the authority for the logical names.
3. **Columns the builder does not create:** `calculada` (C010), by hand in the maker, after the columns it
   uses.
4. **Mockup rows:** they stay in DEV, as with the spreadsheet.

## 8. The plan inside

```json
{
  "formato": "plano-dataverse/1",
  "resumo": { "tabelas": 2, "colunas": 13, "relacionamentos": 1, "lotes": 2, "linhas": 13, "chaves": 2 },
  "passos": [
    { "n": 1, "fase": "tabela", "rotulo": "Unit",
      "existe": "/api/data/v9.2/EntityDefinitions?$select=LogicalName&$filter=LogicalName%20eq%20'{{prefixo}}_unit'",
      "metodo": "POST", "url": "/api/data/v9.2/EntityDefinitions",
      "tipo": "application/json; charset=utf-8", "corpo": "{\"@odata.type\":\"Microsoft.Dynamics.CRM.EntityMetadata\", …}" }
  ]
}
```

Destination: `dataverse-plan.json`, generated; the excerpt shows the shape of a step.

| Phase | Request | What the body carries |
|---|---|---|
| `tabela` | `POST EntityDefinitions` | `SchemaName`, explicit `EntitySetName`, labels, `UserOwned`, the primary column with `IsPrimaryName` |
| `coluna` | `POST EntityDefinitions(LogicalName='…')/Attributes` | the type's `@odata.type` (`StringAttributeMetadata` with `FormatName`, `MemoAttributeMetadata`, `DecimalAttributeMetadata`…), required level |
| `relacionamento` | `POST RelationshipDefinitions` | `OneToManyRelationshipMetadata` with the `Lookup`; navigation pinned; `Restrict` delete if the Lookup is required, `RemoveLink` if not |
| `publicar` | `POST PublishXml` | the plan's tables; always runs |
| `dados` | `POST $batch` | one changeset per batch, with one `POST` per row, CRLF, fixed row ID, Lookup in `@odata.bind` |
| `chave` | `POST EntityDefinitions(LogicalName='…')/Keys` | `EntityKeyMetadata`. Index creation is asynchronous; check `EntityKeyIndexStatus = Active` before using the key |

Rules the compiler follows:
- **Logical name.** It comes from the spec's `logico`, which is the name after the prefix, or from the
  display name without accents in PascalCase (`Expected date` → `{{prefixo}}_ExpectedDate`, logical
  `{{prefixo}}_expecteddate`). The prefix is always the solution's.
- **Placeholders.** The plan carries nothing from the environment. The flow swaps `{{prefixo}}`,
  `{{opcao}}` and `{{idioma}}` before reading the JSON. The Choice uses the publisher's value prefix:
  `{{opcao}}0000`, `{{opcao}}0001`…
- **Fixed ID per row** (uuid5 of the table and the row number). The child points to the parent's ID
  already in the plan, and the same spec always generates the same plan.
- **Lookup to the table itself** uses `$n` (the `Content-ID` of the earlier row in the same batch); if
  the row pointed to was in an earlier batch, already written, it uses its fixed ID.
- **Batches:** up to 100 rows and about 60 thousand characters each, so each step fits the flow
  expressions' limit of 131,072 characters.
- **Language:** if the base language read comes back empty, the flow uses `1046`.
- **Date and time** goes in UTC (`…T08:30:00Z`) and shows in the user's time zone (05:30 in Brasília). In
  the mockup it does not matter.
- **What does not go in the rows:** autonumber (Dataverse generates it), image and file (binary).
- **ASCII body:** the accent is escaped (`ç`), so it does not depend on the connector's encoding.

The flow (`assets/dataverse-builder.json`) is fixed: `Construtor` scope, `Foreach` with concurrency 1,
`Tentar`/`Capturar` per step and a `Terminate` with failure at the end if anything went wrong. Changed the
flow? Run `verificar-fluxo.py` on it and the kit's tests before publishing.

## 9. What has not been verified yet

Check on first use, in a DEV environment, and record what you find:

| Point | Why it matters |
|---|---|
| Import of the generated `.zip` (format built from the reference project, with no confirmed import) | if it refuses, use §4 B |
| Solution language different from the base language | the import may refuse: generate with `--idioma` |
| Preauthorized connector accepted by the tenant | without it, no call goes through |
| `FormatName` `Phone` and `Url` | the Learn format table shows `PhoneNumber` and `URL`; the kit sends `Phone` and `Url`, the `StringFormatName` values |
| `DateTimeBehavior: DateOnly` accepted on creation | the Learn example only sets `Format` |
| Currency without `transactioncurrencyid` on the row | the platform should use the user's default currency |
| `$1` in `@odata.bind` to the table itself | documented for `$batch`, with no test in the kit |
| Image and file created through `/Attributes` | no test in the kit |
| Creation time and customization lock in sequence | the 2 s pause may be too short |
| Connector GET body as an object or as text | the flow reads it with `json(string(...))`, which serves both |
| `$batch` status when a changeset fails (error on the call or 200 with the error inside) | the flow handles both; Learn only shows the case without a changeset |
| `POST .../Keys` through the Web API | Learn shows key creation through the SDK |
| `AssociatedMenuConfiguration` and `IsPrimaryImage` | the plan sends the menu and does not send `IsPrimaryImage`, which throws an exception with `false` |
| Type `10037` of the connection reference in `solution.xml` and `host.connectionName` in the solution's flow | the type code varies by environment; the import may resolve by name |
| Large plan (hundreds of KB) in `base64ToString` and in the `json()` at the start | each step is small, but the file is read whole |
| Pasting the scope (§4 B) | the conditions and fields follow the shapes seen when pasting another flow; the name on the variable actions, with the variables already created at the root, has not been seen yet |
| `file` key of the trigger's File input | holds for the first file input; another flow uses the same shape, also with no run |

## 10. Sources

- Create and update a table through the Web API (required fields, `MSCRM.SolutionUniqueName`, `PublishXml`):
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-entity-definitions-using-web-api>
- Create a column through the Web API:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-column-definitions-using-web-api>
- Column types, text formats, date behavior, currency precision:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/entity-attribute-metadata>
- Relationships through the Web API:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-entity-relationships-using-web-api>
- `$batch`, changeset, `Content-ID`, CRLF:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/execute-batch-operations-using-web-api>
- Alternate key and `EntityKeyIndexStatus`:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/define-alternate-keys-entity>
- HTTP with Microsoft Entra ID connector (premium, limit of 100 calls per minute):
  <https://learn.microsoft.com/en-us/connectors/webcontents/>
- Power Automate limits (120 s per synchronous action):
  <https://learn.microsoft.com/en-us/power-automate/limits-and-config>
- `EntitySetName` set on creation:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/customize-entity-metadata>

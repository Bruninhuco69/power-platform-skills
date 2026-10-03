# ALM and environments

Owner: skill `power-platform`. The `power-automate` and `dataverse` skills point here.
Covers DEV/HML/PRD environments, solutions, environment variables, connection references, the `pac`
CLI, export/import, Git, and what ships by **paste** vs. by **solution**.

Source marks: Microsoft Learn link (accessed 2026-10), `[verified: reference projects]` or
`[unverified]`.

## Contents

1. [Environments](#1-environments)
2. [Solutions](#2-solutions)
3. [Environment variables](#3-environment-variables)
4. [Connection references](#4-connection-references)
5. [Paste × solution](#5-paste--solution)
6. [pac CLI](#6-pac-cli)
7. [Deployment settings file](#7-deployment-settings-file)
8. [Git and pipelines](#8-git-and-pipelines)
9. [Canvas: .msapp and pac canvas](#9-canvas-msapp-and-pac-canvas)
10. [Promotion procedure](#10-promotion-procedure)
11. [No `dev*` in names](#11-no-dev-in-names)
12. [Known gaps](#12-known-gaps)

## 1. Environments

| Environment | Purpose | Solution | Who changes it |
|---|---|---|---|
| DEV | build; the only origin of **changes** (the source of truth is Git) | **unmanaged** | whoever develops |
| HML | UAT with test data | **managed** | import only |
| PRD | operation | **managed** | import only, after HML is approved |

- Every environment that takes part in ALM needs a **Dataverse database**, even when the business
  data lives in SQL Server — the solution, the variables and the connection references live in
  Dataverse. [Microsoft Learn — ALM overview](https://learn.microsoft.com/en-us/power-platform/alm/overview-alm)
- Golden rule: **nothing is edited directly in HML/PRD**. A fix starts in DEV, is versioned,
  exported, imported.
- Declare in the project's `00-READ-ME-FIRST.md`: the logical URL of each environment (no secrets),
  who has access, and which database/server each one uses. Real values stay out of the plugin repository.
- A test source is never the production source in disguise: HML points to the HML source.

## 2. Solutions

- **A solution is the ALM mechanism**: it distributes components (tables, Canvas apps, flows,
  environment variables, connection references) between environments by export/import.
  [Microsoft Learn — ALM overview](https://learn.microsoft.com/en-us/power-platform/alm/overview-alm)
- Exporting/importing the Canvas app package on its own (`.msapp`/package) **does not support ALM**:
  it is only for basic moves. Every app and flow of a project lives **inside a solution**.
- **One solution per project** (or per deployment domain), with the project's publisher and the
  prefix declared in `prefixo_publisher`. Avoid the default publisher.
- **Managed** in HML/PRD, **unmanaged** in DEV; the managed solution is a build artifact (export the
  unmanaged one as managed) and is not imported into the environment it came from. When you
  **uninstall** a managed solution, the data in the tables and columns it created is lost.
  Source: https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm (accessed 2026-10).
- A **version** on every export (`pac solution version` or `online-version`); the version goes into
  the file name and the project's `CHANGELOG`.
- Components created **outside** the solution (a flow under "My flows", a loose app) do not travel: add
  them to the solution before exporting. A flow outside a solution uses direct connections, not a
  connection reference.
  [Microsoft Learn — connection reference](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-connection-reference)
- Custom connectors go in a **separate solution**, imported before the one with the flows/connection
  references that use them (same doc, "Known issues").
- Maximum solution size: 95 MB (environment variables doc, FAQ).

## 3. Environment variables

Everything that changes between DEV, HML and PRD leaves the code and goes into an environment variable.
[Microsoft Learn — environment variables](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables)

| Type | Use |
|---|---|
| Text, Decimal number, Yes/No, JSON | simple parameters: table name, flag, limit, URL |
| Data source | connector parameters (e.g. server and database, site and list) |
| Secret | value kept in Azure Key Vault (requires setting up the vault) |

Behavior that matters:

- **Default value** is part of the definition and is used when there is no current value. **Current
  value** belongs to the environment and takes precedence. The definition travels in the solution; the
  current value is an **unmanaged** record of the target environment.
- **Remove the current value from the solution before exporting** ("Remove from this solution"): this
  way the DEV value does not go along and the import asks for the target's value. Check before every export.
- On import the UI (and the pipelines) ask for the value; a variable with no default and no value
  **blocks use** and raises a notification — fill it in before turning flows on and releasing the app.
- Propagation: a changed value can take **up to 1 hour** to reach apps and flows.
- In a managed solution the value only shows in the environment's **Default** solution.
- Limit: **2,000 characters** per value; no validation in Dataverse (validate in the consumer).
- The names `$authentication` and `$connection` are reserved in flows; avoid them. Use a unique,
  descriptive name.
- An environment variable **is not a cache**: the value only changes on save/re-turn-on; do not use it
  for a rotating token.
- SQL Server: with a Microsoft Entra connection, use separate **server** and **database** variables.
  With SQL authentication (shared connection) do **not** use a data source variable: server and
  database come from the connection itself — use a connection reference. (environment variables doc, "SQL Server")
- Dataverse in the same environment does not need a variable (the app looks the table up by name).

What becomes an environment variable in this kit: server/database (when applicable), log table name,
external service URL, limits and flags from the flow's `CONFIG`, support mailbox email/group,
group identifiers. **Never** a token or password in plain text — use the Secret type.

## 4. Connection references

[Microsoft Learn — connection reference](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-connection-reference)

- A connection reference = a solution component that points to a **connection** of a connector.
  Solution flows bind to it, never to the direct connection; on import the target supplies the connection.
- **Flows** use a connection reference for every connector; **Canvas** only for implicitly shared
  connections (not OAuth), such as SQL Server with SQL authentication.
- To turn a flow on, whoever turns it on must own the connections or have permission to use them.
  Error `ConnectionAuthorizationFailed` = the user turning it on has no access to at least one
  connection: the owner shares it ("Can use") or turns it on themselves. An OAuth connection is only
  shared explicitly with a service principal.
- Ownership of a connection reference is not transferred through the maker's Solutions area.
- Canvas and custom connector: the connection reference is **not** recognized; after importing, edit
  the app, remove and re-add the custom connector's connection (creates an unmanaged layer if the
  solution is managed).
- Copying an environment breaks the connection references of custom connectors (recreate them).
- Name: unique and descriptive (`<connector>-<function>`); the generated default carries a random suffix.
- **Never** copy the real ID of a connection reference or a connection into the repository:
  `00000000-0000-0000-0000-000000000000` in the template, the real value only in the local deployment file.

## 5. Paste × solution

| Artifact | Delivery by paste (Studio/designer) | Delivery by solution |
|---|---|---|
| Canvas control/screen (YAML) | **yes**: Code view → paste; only a unique control name | the whole app goes in the solution |
| `App.OnStart` / named formulas | **manual**: there is no paste for the App object | goes with the app |
| Flow (definition) | **yes**: paste nodes in the designer (clipboard); the pasted file is the **baseline** | the flow goes in the solution; connection reference and environment variables resolve the environment |
| Connection reference, environment variable | **no** (create in the environment) | **yes** (definition travels; value belongs to the target) |
| Table/column/Choice/security role | no | **yes** (Dataverse) |
| SQL procedure/DDL | script on the database (DBA) | does **not** travel in a solution; goes in as a versioned script |
| Turn a flow on, grant a connection | human in the environment | human in the environment |

Rule: **DEV receives by paste; HML/PRD receive only by solution.** Pasting directly into HML/PRD
creates divergence that the next import overwrites or conflicts with.

Each paste is a 🔴 step in the queue: name the parent control, what to paste and what to check.

## 6. pac CLI

Source: [pac solution](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/solution)
(authenticate first with `pac auth`; confirm the active environment with `pac org who` `[unverified]`).

| Command | Purpose |
|---|---|
| `pac solution list` | solutions of the active environment (`--json`) |
| `pac solution export --name <solucao> --path <arquivo.zip> [--managed] [--async]` | export (managed with `--managed`); `--overwrite` overwrites the zip |
| `pac solution import --path <arquivo.zip> [--settings-file <json>] [--async] [--publish-changes] [--stage-and-upgrade]` | import; `--settings-file` fills variables and connection references |
| `pac solution create-settings --solution-zip <zip> --settings-file <json>` | generate the deployment settings file from the solution |
| `pac solution unpack --zipfile <zip> --folder <pasta>` / `pack` | open/close the solution for version control (SolutionPackager) |
| `pac solution clone --name <solucao>` | solution project in a folder (to add components) |
| `pac solution sync` | update the folder with the environment's state |
| `pac solution online-version --solution-name <n> --solution-version 1.0.0.2` | read/set the online version |
| `pac solution version --strategy gittags` | version by strategy |
| `pac solution check --path <zip>` | Solution Checker (Power Apps Checker) before promoting |
| `pac solution upgrade --solution-name <n>` | apply a managed solution upgrade |

`unpack`/`pack` have a **XML format (legacy)** and a **YAML format** (native Git integration); the
format is detected by the `solutions/` folder. Solution `pack`/`unpack` **are** supported; `pac canvas
pack`/`unpack`, however, are deprecated (section 9).

Use `--async` on a large solution and prefer `unpack` of the `.zip` through the CLI over opening the zip by hand.

## 7. Deployment settings file

Always generate it with the command, then edit the HML/PRD values:

```powershell
pac solution create-settings --solution-zip .\dist\Solucao_1.0.0.2.zip --settings-file .\implantacao\hml.json
```

Expected structure (the field names come from the generated file; **trust the generated one**, not this
template `[unverified]`):

```json
{
  "EnvironmentVariables": [
    { "SchemaName": "<prefixo>_NomeDaVariavel", "Value": "<valor-do-ambiente>" }
  ],
  "ConnectionReferences": [
    { "LogicalName": "<prefixo>_conexao-sql", "ConnectionId": "00000000-0000-0000-0000-000000000000", "ConnectorId": "/providers/Microsoft.PowerApps/apis/shared_sql" }
  ]
}
```

- One file per target environment (`hml.json`, `prd.json`), **outside the plugin repository** and, in
  the project repository, only if it has no real ID or secret (`.gitignore` by default).
- Import with: `pac solution import --path <zip> --settings-file .\implantacao\hml.json`.
- Never a secret in the file: Secret type + Key Vault.

## 8. Git and pipelines

- **Git from day 0.** One branch per wave, one tag per delivery, `.gitignore` for data and outputs.
- **The source of truth is version control**, not the DEV environment.
  [Microsoft Learn — ALM overview](https://learn.microsoft.com/en-us/power-platform/alm/overview-alm)
- For a Canvas app, the supported way for external editing, merge and conflict is Power Platform's
  **Git integration**. [Git integration](https://learn.microsoft.com/en-us/power-platform/alm/git-integration/overview)
- In-product **Pipelines in Power Platform** (Dataverse) do DEV → HML → PRD with approval and show the
  environment variable fields at deployment.
  [Set up pipelines](https://learn.microsoft.com/en-us/power-platform/alm/set-up-pipelines)
  `[unverified: license and enablement per tenant]`
- External CI/CD (Azure DevOps, GitHub Actions) with Power Platform Build Tools: optional; the tasks
  do not manage data source environment variables (variables doc, "limitations").

## 9. Canvas: .msapp and pac canvas

[verified: reference projects] and [Microsoft Learn — pa.yaml](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml)

- `.msapp` is a zip; only `*.pa.yaml` in `\Src` works as source code.
- Extract: `Expand-Archive` or `pac canvas download --name "<app>" -d .\src -o`.
- **`pac canvas pack` and `unpack` are deprecated** (Preview, no longer in development); the
  `Experimental` layout (`*.fx.yaml`) is deprecated and will be removed. If you use it, `--layout SourceCode`.
  [pac canvas](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas)
- Merging two Studio sessions: unique control names; normal merge in `\Src\*.pa.yaml`; on conflict it
  is safe to delete `\src\editorstate\*.json` and `\other\entropy.json`; conflict in
  `\Connections\*`, `\DataSources\*`, `\pkgs\*` or `CanvasManifest.json`: **do not merge**, resolve
  in Studio.
- **Code view**: copies/pastes controls; it does **not** cover the App object (OnStart, Formulas) nor
  edit in place. [Code view](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/code-view)

## 10. Promotion procedure

DEV → HML → PRD. Each step that needs an environment is 🔴.

1. **Freeze the scope** of the delivery; confirm in DEV that the queue has ✅ with evidence.
2. Run the **final gate** (`final-gate.md`) on what is going out.
3. In DEV: remove the **current value** of the environment variables; bump the **version**.
4. `pac solution check` (or Solution Checker) — fix critical errors.
5. `pac solution export --managed --async` → `dist/<solution>_<version>.zip`; `unpack` and commit; tag.
6. `pac solution create-settings` → the target environment's file with the **target's values**.
7. Make sure on the target: database/server exist, connections created and **shared** with whoever turns
   the flows on, groups/mailboxes exist, database scripts applied by the DBA (procedures do not travel).
8. `pac solution import --path <zip> --settings-file <json> --async --publish-changes`.
9. **Turn the flows on** and confirm the connection references (a human who owns the connections).
10. **Smoke test on the target:** open the app, run the minimum cycle, check the flow history, confirm that
    the source is the environment's own (no `dev*`).
11. Record in the queue: command, version, output, date. Rollback = re-import the previous state
    repackaged with a version number **higher** than the installed one (plan it before HML) and revert the
    database script `[unverified: behavior when importing a lower version]`.

## 11. No `dev*` in names

- No table, column, variable, flow, connection reference or code folder carries `dev`, `hml` or
  `prd` **in its name** (e.g. `dev-clientes`). Environment is a property of the **environment**, not of the name.
- No literal server, database, environment URL or production GUID in a formula, flow or delivery
  document: use an environment variable + connection reference.
- Quick audit (run from the project root; the expected result is empty):

```bash
grep -rniE "dev[-_]|\bdev[a-z]+\b|\.database\.windows|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}" telas/ flows/
```

  Adjust the folders to `power-platform.config.json`; each result is a justified false positive
  or a defect. Why: a development source read by one screen and production by another made the menu
  KPI diverge from the gallery with no formula bug `[verified: reference project]`.

## 12. Known gaps

- A real DEV → PRD pipeline, flow contract versioning and a procedure rollback strategy do not yet
  have a baseline in this kit `[unverified]`.
- Enablement of in-product pipelines and the Premium license for connectors vary by tenant: confirm
  with administration before promising.
- The exact format of the deployment settings file must be checked against the `pac` version in use.

# SQL inside the flow

How the flow calls and reads the procedure. **The procedure itself (DDL, transaction, code
vocabulary, `GRANT`) belongs to the `sql-procedures` skill.** Connector facts checked against
[Learn: SQL Server connector](https://learn.microsoft.com/en-us/connectors/sql/) and confirmed in
the reference project.

## Contents

1. [Write only through a procedure](#1-write-only-through-a-procedure)
2. [Call: Execute stored procedure (V2)](#2-call-execute-stored-procedure-v2)
3. [Read the 1-row return](#3-read-the-1-row-return)
4. [Read records: Get rows (V2)](#4-read-records-get-rows-v2)
5. [Limits that size the design](#5-limits-that-size-the-design)

---

## 1. Write only through a procedure

| Why | Source |
|---|---|
| `Insert row (V2)`/`Update row (V2)` **do not work** on a table with a server-side trigger ("Insert and update to a table won't work if you defined a SQL server-side trigger on the table") | Learn |
| `Execute a SQL query (V2)` is not supported with a gateway / on-premises SQL | Learn |
| Loose writes cost ~6x more calls and have 1/5 of the throughput ceiling (Native 500 calls/10 s x CRUD 100/10 s per connection) | Learn |
| There is no transaction action for SQL (Dataverse has a changeset) | verified: reference project |
| The connector account is left with only `EXECUTE`, no DML on the tables: it closes by construction the path that `Patch` in the app opened | decision A1 |

So: **one business action = one procedure = one `Execute stored procedure (V2)` action**.

## 2. Call: Execute stored procedure (V2)

```json
{
  "Gravar_registro": {
    "type": "OpenApiConnection",
    "inputs": {
      "parameters": {
        "server": "default",
        "database": "default",
        "procedure": "[dbo].[<procedure_gravar>]",
        "parameters/Id_Registro": "@outputs('Normalizar_gravar')?['id']",
        "parameters/Des_Registro": "@outputs('Normalizar_gravar')?['descricao']",
        "parameters/Id_UsuarioChamador": "@int(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Id_Usuario'],0))"
      },
      "host": {
        "apiId": "/providers/Microsoft.PowerApps/apis/shared_sql",
        "connection": "shared_sql",
        "operationId": "ExecuteProcedure_V2"
      }
    },
    "runAfter": { "Se_invalido_gravar": ["Succeeded"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000008" }
  }
}
```

Destination: an action inside a `Caso_<acao>` of the scope (pasted as part of the scope envelope,
with the matching entry in `allConnectionData`).

- `server` and `database` = the literal `"default"` (R4); the server and database come from the
  environment's connection reference, not from the flow.
- Parameters `parameters/<NameInTheProcedure>`, **bare `@expr`** (R5). Name and type identical to
  the signature; changing the procedure signature is changing the contract (a gate compares the
  two).
- The procedure name is the environment's **AS-BUILT** one (check `sys.procedures`); never the
  document's (R9).
- Text goes through `take(coalesce(x,''), N)` with N = column size (R10).
- A semantic `null` (e.g. "all units") connects to the node's raw output, without `coalesce`.
- A caller passed as a parameter records authorship, it does **not** authorize
  ([authorization-in-flow.md](authorization-in-flow.md)).

## 3. Read the 1-row return

The procedure returns **one row, four columns** (`status`, `description` = code, `id`, `url`). In
the flow:

```text
@coalesce(body('Gravar_registro')?['ResultSets']?['Table1']?[0]?['description'],'')
```

Destination: `Compose` `Codigo_<acao>`; the `Response` translates it
([app-flow-contract.md](app-flow-contract.md)).

Connector rules that make the procedure "fail silently" if violated:

| Rule | Consequence |
|---|---|
| `SET NOCOUNT ON` on the 1st line (procedure **and** trigger) | Without it the rowcount of each DML is read as `Table1` and the return disappears |
| **Only the first result set** is read (with a gateway) | A return of 2 `SELECT`s loses the second |
| `OUTPUT` parameter values **do not come back** (with a gateway) | Return them through a `SELECT` |
| Result set columns with a unique, non-empty name | Otherwise the schema does not resolve |
| 110 s timeout per query/procedure | Sizes export and count |
| 8 MB response and 2 MB request behind a gateway | A large export needs pagination/partitioning |
| A runtime error in the procedure **fails the action** | The `Catch` is mandatory |

Zero rows in a **caller read** procedure is the "unknown" signal: the flow tests
`empty(coalesce(body('Ler_chamador')?['ResultSets']?['Table1'], json('[]')))`.

## 4. Read records: Get rows (V2)

To read the state of **one** record before deciding (scope, before/after):

```json
{
  "Estado_antes_gravar": {
    "type": "OpenApiConnection",
    "inputs": {
      "parameters": {
        "server": "default",
        "database": "default",
        "table": "[dbo].[<Tabela>]",
        "$filter": "@concat('Id_Registro eq ', string(int(coalesce(outputs('Normalizar_gravar')?['id'],'0'))))",
        "$top": 1
      },
      "host": {
        "apiId": "/providers/Microsoft.PowerApps/apis/shared_sql",
        "connection": "shared_sql",
        "operationId": "GetItems_V2"
      }
    },
    "runAfter": { "Autorizar_gravar": ["Succeeded"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000009" }
  }
}
```

Destination: an action inside the `Caso`. Use `GetItems_V2` with `$top 1` and **not** `GetItem_V2`:
the latter gives 404 for a nonexistent key and brings down the `Try` instead of producing "record
not found". (`int()` of non-numeric text blows up: validate the id in `Validar_x` **before** the
read, or protect the argument -- see [wdl-expression-pitfalls.md](wdl-expression-pitfalls.md).)

| `$filter` limitation | Source |
|---|---|
| Does not accept `date`, `datetime`, `datetime2`, `smalldatetime` | Learn |
| `bit` compares with `true`/`false` | verified: reference project |
| No `$expand`/JOIN: authorization (user x role) needs a procedure or a view | verified: reference project |
| A complex filter blows up at ~100 OData nodes (report with lists) | verified: reference project |
| No `COLLATE`/lock hint in `Get rows`: uniqueness under concurrency stays in the procedure | verified: reference project |

## 5. Limits that size the design

| Limit | Value | Implication |
|---|---|---|
| Native throughput (procedure/query) | 500 calls/10 s per connection (200 concurrent) | One procedure per action fits comfortably |
| CRUD throughput | 100 calls/10 s per connection (125 concurrent) | Avoid `Get rows` in a loop |
| Time | 110 s per procedure | A long operation becomes an asynchronous job ([app-flow-contract.md](app-flow-contract.md) §6) |
| Size (gateway) | 8 MB response / 2 MB request | Export in parts |

Source of all: Learn (SQL Server connector).

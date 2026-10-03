# Field lessons: Dataverse

Patterns that showed up in real projects and did not yet fit a single rule in the other
references. Each lesson gives what happened, in generic terms, and the rule or file that prevents it.
It is not a rule by itself: what holds is in the files cited.

## Contents

1. [A workaround that makes the error disappear is not a fix](#1-a-workaround-that-makes-the-error-disappear-is-not-a-fix)
2. [A profile read from a Choice returns the label, not the record](#2-a-profile-read-from-a-choice-returns-the-label-not-the-record)
3. [A data export is read from the zip, not opened](#3-a-data-export-is-read-from-the-zip-not-opened)
4. [A column without an owner is a dead column](#4-a-column-without-an-owner-is-a-dead-column)
5. [The app source → table map belongs to the app, not to the environment](#5-the-app-source--table-map-belongs-to-the-app-not-to-the-environment)
6. [Null date and the platform's minimum limit](#6-null-date-and-the-platforms-minimum-limit)
7. [Metadata and load through the Web API](#7-metadata-and-load-through-the-web-api)
8. [The spreadsheet import swapped day and month](#8-the-spreadsheet-import-swapped-day-and-month)

---

## 1. A workaround that makes the error disappear is not a fix

| | |
|---|---|
| **What happened** | When fixing a screen written against the dictionary, three adjustments made the error disappear without touching the cause: a combo box started listing the link table instead of the catalog table (with a tautological filter `X = X`); a label was "flipped" for debugging because `Items` pointed to the wrong table; a person picker started displaying an arbitrary field (`DisplayFields: ["City"]`) instead of the name, because the Office 365 connector fields (`DisplayName`, `Mail`) carry no prefix and the name used did not resolve. |
| **Why it is dangerous** | The screen stops reporting, but starts showing the wrong data, and the workaround becomes a copied pattern. |
| **Prevented by** | `references/as-built-names.md` (the right column comes from the environment) and `references/names-and-types.md` §3 (a connector that is not Dataverse uses the connector's field). If the error goes away after swapping the source or the column, go back to the as-built before accepting it. |

## 2. A profile read from a Choice returns the label, not the record

| | |
|---|---|
| **What happened** | `Set(varPerfil, varUsuario.perfil)` over a **Choice** column returns the option's label, not the record of the profiles table. Every `varPerfil.pode_*` in the menu and screens read a property of a text. The fix was to resolve the profile with `LookUp(<profiles table>, nome = Text(varUsuario.perfil))`. The same fragile point, a different accent between the label and the profile name, made the app open empty, with no error. |
| **Prevented by** | `references/names-and-types.md` §6.1 (Choice is not a record) and `references/security.md` §6 (permission by flag, no resolved profile = no access). In `powerapps-canvas`, `references/scope-and-permission.md`. |

## 3. A data export is read from the zip, not opened

| | |
|---|---|
| **What happened** | The only "schema" source was a Dataverse data export to Excel, hundreds of MB, one sheet per table, with a few sample rows. Opening the whole file froze the usual reader. The header of each sheet (the logical names) was read straight from `xl/workbook.xml` and from the first row of each `xl/worksheets/sheetN.xml` inside the zip. The export also omitted tables the app used, and did not carry the type (Choice or text). |
| **Prevented by** | `references/as-built-names.md` §1 and §3: a data export is not a dictionary; use `scripts/extrair-nomes-as-built.py`, which starts from the metadata. If only the export exists, treat every column it does not show as a gap (`?`), stated as an inference. |

## 4. A column without an owner is a dead column

| | |
|---|---|
| **What happened** | In a flow-monitoring table, several columns of the parent record were always null, and a new version of the flow stopped filling columns the previous one filled (failed action, JSON sent and received, message): the HTTP indicator was null in the report for the runs of the new version. |
| **Prevented by** | `references/modeling.md` §10: define which columns **every** flow fills and document who fills each one. |

## 5. The app source → table map belongs to the app, not to the environment

| | |
|---|---|
| **What happened** | The name of the data source in Power Fx (alias) differs from the logical name and the display name, and the map between them was built by hand, by name correlation. Two sources, one singular and one plural, pointed to the same table. |
| **Prevented by** | `references/names-and-types.md` §5. The map counts as the **app's** as-built, not the environment's: read the app's data panel and record the date. |

## 6. Null date and the platform's minimum limit

| | |
|---|---|
| **What happened** | An inbound flow replaced the source's null date (`0001-01-01`) with `1753-01-01` before writing. The likely reason is the platform's minimum date limit `[unverified: the cause was not recorded]`. |
| **Prevented by** | When receiving a date from an external system, decide and record how the null date is written (empty or a sentinel) instead of letting the source's minimum value through without criteria. See `skills/power-automate/references/dataverse-batch-upsert.md`. |

## 7. Metadata and load through the Web API

A flow that creates the schema and loads the rows through the Web API (a plan read by an interpreter,
the same design as the kit's builder) collected these points before the first run. The Source column
says where each one comes from: Learn, or what was seen in the reference project.

| Point | Rule | Source |
|---|---|---|
| Component outside the solution | `MSCRM.SolutionUniqueName` on every metadata creation | Learn |
| Column `PUT` | replaces the whole definition: `GET` the column, change the field, `PUT` everything without `@odata.context`, with `MSCRM.MergeLabels: true` so the label of another language is not erased | Learn |
| Autonumbering on a column with data | the column is born text, the load writes the codes, then `PUT` with `AutoNumberFormat` and `SetAutoNumberSeed` above the last code | Learn; `PUT` acceptance not verified |
| Choice option with `Value: null` | the platform numbers by the publisher's value prefix. Whoever does not pin the integer reads the Choice (`$expand=OptionSet,GlobalOptionSet`: the local one answers in one, the global in the other) and matches by label | Learn; numbering not verified |
| Column over a global Choice | `GlobalOptionSet@odata.bind: "/GlobalOptionSetDefinitions(Name='x')"` | Learn |
| Alternate key | the index is asynchronous: `EntityKeyIndexStatus` goes through `Pending`/`InProgress` until `Active` or `Failed`; `Failed` calls for `ReactivateEntityKey`. When searching for the key by name in a text, include the quotes, so it does not match a key with a longer name | Learn |
| Publisher | look it up by prefix before creating; `crNNN` is usually the environment's default publisher: check before running | reference project |
| Row that can run again | fixed ID (uuid5 of the table and the natural key) and `PATCH` with `If-None-Match: *`: only creates; `412` = already exists. `If-Match: *` only updates (`skills/power-automate/references/dataverse-batch-upsert.md`) | Learn |
| Circular Lookup | the row is born without the Lookup, and a later `PATCH` links the two | reference project |
| Real owner and creation date | `ownerid@odata.bind: /systemusers(<id>)`, with the user found by `internalemailaddress` (e-mail encoded in the URL, `'` doubled); `overriddencreatedon` for the opening date | Learn; not verified for the account that runs |

The kit's builder (`skills/power-platform/references/dataverse-builder.md`) already follows the points
on solution, key, fixed ID and local Choice. The others apply to whoever writes another load.

## 8. The spreadsheet import swapped day and month

| | |
|---|---|
| **What happened** | The spreadsheet import into Dataverse swapped day and month in the dates. It also does not write owner, sharing or creation date, and that is why that project's load went to the Web API. [verified: reference project] |
| **Prevented by** | `references/data-import.md` §4. The kit's mockup load generates dates only with day 13 or later: if the import swaps them, the month is invalid and the row is rejected, instead of going in with the wrong date. After importing, check one date in the table. Owner and creation date call for the Web API (§7). |

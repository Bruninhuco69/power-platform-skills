# Technology matrix — Dataverse × SQL Server

Criteria for the data track decision (decision A4: one track per project; switching requires an ADR
— `assets/adr-template.md`). Applies to a new project; in an existing project, the track is already
declared in `power-platform.config.json`.

## Contents

1. [Matrix](#1-matrix)
2. [When to choose each one](#2-when-to-choose-each-one)
3. [Power BI](#3-power-bi)
4. [SharePoint](#4-sharepoint)
5. [Outside Power Platform, and never](#5-outside-power-platform-and-never)
6. [How to record the decision](#6-how-to-record-the-decision)

---

## 1. Matrix

Origin: two reference projects in production, one on each track. Items marked `[external]` were not
measured in those projects; confirm in the documentation or in the environment.

| Criterion | Dataverse | SQL Server + procedures + Power Automate |
|---|---|---|
| Who creates the schema | the maker, fast; the as-built diverges from any script (publisher prefix) | the DBA, with a request cycle and a freeze in production |
| Time to start | short, no DBA | longer: DDL requests, column rounds, environment proofs |
| `CountRows(Filter(...))` | delegates (up to the aggregation cap) | **does not delegate**: counts on the client up to the 500/2,000 cap; show `2,000+` or count on the server |
| Date filter | delegates | does not delegate behind a gateway: integer computed column (B2) |
| `in`, `Search`, `Upper/Lower` in `Filter` | does not delegate | does not delegate |
| Transaction across several tables | no (compensation in `Catch`) | **yes** (`XACT_ABORT ON` in the procedure) |
| Typing | native Choice and Lookup | `BIT NOT NULL`, mandatory PK (without a PK, read-only), filtered UNIQUE |
| Row-level isolation | Security Role limits the table, not the row; Owner Team/Business Unit costs effort | RLS by session context is unworkable with a shared service account; authorization goes to the flow (A3) |
| Corporate data already in SQL | copying loses integrity | reads directly, read-only |
| Compliance "data only on the internal network" | cloud: the premise breaks | can stay on-premises with a gateway (payload limits; procedure `OUTPUT` does not come back) |
| Licensing | premium and capacity `[external]` | premium SQL connector `[external]` |
| Change after production | edit in the maker | the database freezes; only screen and flow; a computed column usually fits |
| Large export | the flow reads the table; aggregation cap | procedure with a count before exporting |
| Power BI and Excel directly | reads everything with no row-level isolation | reads with the consumer's identity; needs a view and `GRANT` |

## 2. When to choose each one

**Dataverse** when: a new, self-contained app; no corporate table to reuse; volume per query below
2,000 rows after the filter; you need native Choice and Lookup; no DBA available in the time frame;
compliance accepts the cloud **in writing**; and isolation by `Unit` is a convenience (or there is
budget for an Owner Team).

**SQL Server + procedures + Power Automate** when: the corporate data is already in SQL; the DBA
requires a standard and owns the schema; the gallery may exceed 2,000 rows; the operation requires a
strong transaction across several tables; or compliance requires local data. Prerequisites: a PK on
every table, `BIT NOT NULL`, a filtered UNIQUE on the identity key, `NVARCHAR` with accents,
compatibility level >= 130, the real procedure names captured, gateway confirmed.

Warning signs of the wrong track: a screen counter showing "2,000+" that the owner does not accept; a
rule that requires "all or nothing" in Dataverse; a DBA saying "frozen" in the middle of the project; a
corporate table being copied into Dataverse.

Decide early, whichever the track: **caller identity** (the flow resolves who it is; the data layer
does not authorize) and **where the rule lives** (a single copy: the flow decides, the procedure
executes — A2).

## 3. Power BI

For analysis and consolidation across units, series and aggregations above 2,000 rows, dashboards that
do not fit in the app. **Never** for writing or operation. Conditions: a view or dataset scoped to the
unit, the consumer's identity; if the source is Dataverse with Security Role at Organization scope,
treat it as a formally accepted risk.

## 4. SharePoint

Does not fit when: there is a transactional rule, volume above the list threshold (view and
delegation limits), referential integrity or row-level isolation as access control. Acceptable for
attachments and documents linked to a record that lives in Dataverse or SQL. `[external: list limits
on Microsoft Learn — confirm in the current version]`

## 5. Outside Power Platform, and never

- **Outside:** PDF or label generation without a proven converter; bulk import with preview over a
  whole database. Keep it in the current system or use a premium connector; a business decision.
- **Never:** `Patch` directly in an operation with a business rule; exporting from a gallery; a gallery
  filter as the only access control without an accepted risk on record.

## 6. How to record the decision

An ADR (`assets/adr-template.md`) with: the chosen track, the answers from blocks 4, 7 and 8 of
`brainstorm.md` that support it, the discarded alternative and the condition that reopens it ("the DBA
releases a new table", "volume goes over N"). Reflect it in `power-platform.config.json` and `00-READ-ME-FIRST.md`.

# CONTRACTS -- <app>

> Screen <-> flow <-> procedure contract. When it diverges from the flow, **the contract is the bug**.
> Generate this document from the artifact whenever possible; written by hand, it goes stale the day
> it is written. Every numeric claim carries the command that measures it.
> Template from the `power-automate` skill: copy it, fill it in, delete the italic instructions.

## 1. Invariants (apply to every flow)

| # | Rule | Check |
|--:|---|---|
| 1 | Response with 4 fields: `status`, `description`, `id`, `url`, all text, always present | `python <skill-folder>/scripts/verificar-fluxo.py <folder>` (F010) |
| 2 | `status` ∈ `success` \| `warning` \| `error`; `warning` = saved with a caveat | review |
| 3 | Trigger parameters are **positional and text**; a new parameter goes at the end; a dead parameter becomes `naoUsado<N>` and keeps its position | argument count of `.Run()` == trigger parameters |
| 4 | The flow revalidates permission and scope on every call; identity comes from the context, not from a parameter | review + denial fixture |
| 5 | The procedure code is a closed vocabulary; the flow translates it | table in §2.6 |

## 2. `<flow>` -- <N> nodes

### 2.1 Call

*Paste the call as the app makes it. Destination: en-US formula bar (`,` and `;`), e.g. `OnSelect`
of the button; the call sits inside `IfError` (C3).*

```text
IfError(Set(varRet, '<flow>'.Run("<action>", <p1>, <p2>)), Set(varRet, Blank()))
```

| # | Parameter | Token in the flow | Type/format | Who validates |
|--:|---|---|---|---|
| 1 | `action` | `triggerBody()['text']` | text, vocabulary: `<action1>`, `<action2>` | `Switch_acao` (default responds `error` naming the value) |
| 2 | `<name>` | `triggerBody()['text_1']` | text; numeric id via `Text(id, "[$-en-US]0")` | `Validar_<acao>` |

### 2.2 Authorization

| Action | Flag read in `Ler_chamador` | Unit scope | `CONFIG` flag | Evidence |
|---|---|---|---|---|
| `<action>` | `<Flg_Acao>` | compares `<unit of the real record / of the parameter>` | `<cfgEscopoUnidade>` (starts `true`) | action name `Autorizar_<acao>` |

### 2.3 Procedures called

| Node | Procedure (AS-BUILT) | Parameters (in signature order) | Class |
|---|---|---|---|
| `Gravar_<acao>` | `[dbo].[<procedure>]` | `<Id_Registro>`, `<Des_X>`, `<Id_UsuarioChamador>` | key / column / caller |

### 2.4 Rules the flow rejects, in evaluation order

| # | Node | Condition | Message |
|--:|---|---|---|
| 1 | `Validar_<acao>` | `<empty description>` | `<en-US sentence>` |

### 2.5 Every response this flow can give

| Branch | Node | `status` | `description` | `id` |
|---|---|---|---|---|
| Unknown caller | `Nega_chamador` | `error` | Your profile does not allow this action. | empty |
| No permission | `Nega_perm_<x>` | `error` | Your profile does not allow this action. | empty |
| Unknown action | `Nega_acao` | `error` | Unknown action. | empty |
| Connector failure | `Nega_conector` | `error` | The system did not respond. No changes were made. | empty |
| Success | `Responder_<x>` | `success` | `<sentence>` | `<id>` |

### 2.6 Procedure codes (CLOSED vocabulary)

| Procedure | `status` | Code | Sentence in the flow | Meaning |
|---|---|---|---|---|
| `<procedure>` | `success` | `GRAVADO` | Record saved. | saved |
| `<procedure>` | `warning` | `NAO_APLICADO` | Nothing was changed. | state predicate did not match |

*A new code in the procedure without a row here responds `error` naming the code.*

### 2.7 Tests that close the contract

| Case | Setup | Check | Label |
|---|---|---|---|
| Profile without the action's flag | test user without `<Flg_Acao>` | `error` response, no row written | FLOW |
| Empty parameter | `descricao = ""` | message from `Validar_<acao>` | FLOW |
| User from another unit | `cfgEscopoUnidade = true` | `error` | FLOW |
| Connector failure | turn off the connection reference | `Nega_conector`, no run without a `Response` | FLOW |

Labels: `STATIC` (read from the artifact), `SQL` (run in the database), `FLOW` (run in the flow).

## 3. Gates

```text
python <skill-folder>/scripts/verificar-fluxo.py <flows folder>      # 0 error(s)
```

## 4. Appendix: AS-BUILT names

Single table, **authority over the generator and over the document**: procedure, connection
reference (logical name per environment), table and column. Source: `sys.procedures` and the
environment's connection reference list, with the capture date.

| Object | Name in the environment | Captured on |
|---|---|---|
| Write procedure | `<procedure>` | `<YYYY-MM-DD>` |
| SQL connection reference | `<prefixo>_sharedsql` | `<YYYY-MM-DD>` |

# SQL dentro do flow

Como o flow chama e lê a procedure. **A procedure em si (DDL, transação, vocabulário de códigos,
`GRANT`) é da skill `sql-procedures`.** Fatos do conector conferidos em
[Learn: conector SQL Server](https://learn.microsoft.com/en-us/connectors/sql/) e confirmados
no projeto de referência.

## Sumário

1. [Escrita só por procedure](#1-escrita-só-por-procedure)
2. [Chamar: Execute stored procedure (V2)](#2-chamar-execute-stored-procedure-v2)
3. [Ler o retorno de 1 linha](#3-ler-o-retorno-de-1-linha)
4. [Ler registros: Get rows (V2)](#4-ler-registros-get-rows-v2)
5. [Limites que dimensionam o desenho](#5-limites-que-dimensionam-o-desenho)

---

## 1. Escrita só por procedure

| Por quê | Fonte |
|---|---|
| `Insert row (V2)`/`Update row (V2)` **não funcionam** em tabela com trigger no servidor ("Insert and update to a table won't work if you defined a SQL server-side trigger on the table") | Learn |
| `Execute a SQL query (V2)` não é suportada com gateway / SQL on-premises | Learn |
| Escrita solta custa ~6x mais chamadas e tem 1/5 do teto de vazão (Native 500 chamadas/10 s x CRUD 100/10 s por conexão) | Learn |
| Não existe ação de transação para SQL (o Dataverse tem changeset) | verificado: projeto de referência |
| A conta do conector fica só com `EXECUTE`, sem DML nas tabelas: fecha por construção o caminho que `Patch` no app abria | decisão A1 |

Então: **uma ação de negócio = uma procedure = uma ação `Execute stored procedure (V2)`**.

## 2. Chamar: Execute stored procedure (V2)

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

Destino: ação dentro de um `Caso_<acao>` do escopo (colada como parte do envelope de escopo,
com a entrada correspondente em `allConnectionData`).

- `server` e `database` = literal `"default"` (R4); servidor e banco vêm da connection
  reference do ambiente, não do flow.
- Parâmetros `parameters/<NomeNaProcedure>`, **`@expr` crua** (R5). Nome e tipo iguais aos da
  assinatura; troca de assinatura da procedure é troca de contrato (um portão compara as duas).
- Nome da procedure é o **AS-BUILT** do ambiente (consulte `sys.procedures`); nunca o do
  documento (R9).
- Texto passa por `take(coalesce(x,''), N)` com N = tamanho da coluna (R10).
- `null` semântico (ex.: "todas as unidades") liga na saída crua do nó, sem `coalesce`.
- Chamador por parâmetro grava autoria, **não** autoriza ([autorizacao-no-flow.md](autorizacao-no-flow.md)).

## 3. Ler o retorno de 1 linha

A procedure devolve **uma linha, quatro colunas** (`status`, `description` = código, `id`,
`url`). No flow:

```text
@coalesce(body('Gravar_registro')?['ResultSets']?['Table1']?[0]?['description'],'')
```

Destino: `Compose` `Codigo_<acao>`; o `Response` traduz ([contrato-app-flow.md](contrato-app-flow.md)).

Regras do conector que fazem a procedure "falhar calada" se violadas:

| Regra | Consequência |
|---|---|
| `SET NOCOUNT ON` na 1ª linha (procedure **e** trigger) | Sem ele o rowcount de cada DML é lido como `Table1` e o retorno some |
| **Só o primeiro result set** é lido (com gateway) | Retorno de 2 `SELECT` perde o segundo |
| Valores de parâmetro `OUTPUT` **não voltam** (com gateway) | Devolva por `SELECT` |
| Colunas do result set com nome único e não vazio | Senão o schema não resolve |
| Timeout de 110 s por consulta/procedure | Dimensiona export e contagem |
| Resposta 8 MB e requisição 2 MB atrás de gateway | Exportação grande pede paginação/partição |
| Erro de runtime da procedure **falha a ação** | O `Catch` é obrigatório |

Zero linha em procedure de **leitura de chamador** é o sinal de "desconhecido": o flow testa
`empty(coalesce(body('Ler_chamador')?['ResultSets']?['Table1'], json('[]')))`.

## 4. Ler registros: Get rows (V2)

Para ler o estado de **um** registro antes de decidir (escopo, antes/depois):

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

Destino: ação dentro do `Caso`. Use `GetItems_V2` com `$top 1` e **não** `GetItem_V2`: este dá
404 para chave inexistente e derruba o `Try` em vez de produzir "registro não encontrado".
(O `int()` de texto não numérico estoura: valide o id em `Validar_x` **antes** da leitura, ou
proteja o argumento -- ver [expressoes-wdl-armadilhas.md](expressoes-wdl-armadilhas.md).)

| Limitação do `$filter` | Fonte |
|---|---|
| Não aceita `date`, `datetime`, `datetime2`, `smalldatetime` | Learn |
| `bit` compara com `true`/`false` | verificado: projeto de referência |
| Sem `$expand`/JOIN: autorização (usuário x perfil) pede procedure ou view | verificado: projeto de referência |
| Filtro complexo estoura em ~100 nós OData (relatório com listas) | verificado: projeto de referência |
| Sem `COLLATE`/lock hint em `Get rows`: unicidade sob concorrência fica na procedure | verificado: projeto de referência |

## 5. Limites que dimensionam o desenho

| Limite | Valor | Implicação |
|---|---|---|
| Vazão Native (procedure/query) | 500 chamadas/10 s por conexão (200 concorrentes) | Uma procedure por ação cabe folgado |
| Vazão CRUD | 100 chamadas/10 s por conexão (125 concorrentes) | Evite `Get rows` em laço |
| Tempo | 110 s por procedure | Operação longa vira job assíncrono ([contrato-app-flow.md](contrato-app-flow.md) §6) |
| Tamanho (gateway) | 8 MB resposta / 2 MB requisição | Exportação por partes |

Fonte de todos: Learn (conector SQL Server).

# Delegação: SQL Server e Dataverse do lado do app

O tópico que mais produz bug silencioso em Canvas: o app não erra, não avisa, só devolve
resultado incompleto. Aqui está o que delega, o que não delega, os tetos, os truques e a forma de
provar. O lado do banco (coluna calculada, procedure, collation) é da skill `sql-procedures`; o
esquema do Dataverse, da skill `dataverse`.

## Sumário

1. [A regra de ouro e o teto](#1-a-regra-de-ouro-e-o-teto)
2. [Conector SQL Server](#2-conector-sql-server)
3. [Contagem](#3-contagem)
4. [Datas](#4-datas)
5. [Dataverse](#5-dataverse)
6. [Busca, `in` e `LookUp`](#6-busca-in-e-lookup)
7. [Coluna errada falha calada](#7-coluna-errada-falha-calada)
8. [O que quebra a delegação sem aviso](#8-o-que-quebra-a-delegação-sem-aviso)
9. [Quando não delega: alternativas](#9-quando-não-delega-alternativas)
10. [Como provar](#10-como-provar)
11. [Declarar por escrito (T7)](#11-declarar-por-escrito-t7)
12. [Fontes](#12-fontes)

---

## 1. A regra de ouro e o teto

> "If any part of a query expression is nondelegable, Power Apps doesn't delegate any part of
> the query." ([Understand delegation](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview))

Não existe delegação parcial. Uma função não delegável no meio derruba tudo, e o app passa a
baixar as primeiras **500** linhas (ajustável até **2.000** em *Settings > General > Data row
limit*) e filtra no cliente. O registro 501 não é encontrado e nada avisa.

- O aviso de delegação (triângulo) só aparece em fórmulas sobre **fonte delegável**.
  **Ausência de aviso não prova delegação.**
- `With`, `UpdateContext` e `Set` criam coleções internamente; coleção não participa de
  delegação **e não gera aviso** (ver §8).
- O que não consta na tabela do **seu** conector não delega, mesmo que delegue em outro.

## 2. Conector SQL Server

Tabela oficial, por tipo de dado
([SQL Server connector](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview),
página atualizada em 2025-03, lida em 2026-10). Expressões ligadas por `And`, `Or` e `Not`
delegam.

| Operação ou função | Número | Texto | Booleano | Data e hora | Guid |
|---|---|---|---|---|---|
| `*`, `+`, `-`, `/` | sim | - | - | não | - |
| `<`, `<=`, `>`, `>=` | sim | **não** | **não** | sim | - |
| `=`, `<>` | sim | sim | sim | sim | sim |
| `Filter` | sim | sim | sim | sim [2] | sim |
| `LookUp` | sim | sim | sim | sim | sim |
| `Sort`, `SortByColumns` | sim | sim | sim | sim | - |
| `Sum`, `Average` | sim | - | - | - | - |
| `Min`, `Max` | sim | - | - | não | - |
| `StartsWith` | - | sim [6] | - | - | - |
| `EndsWith` | - | sim [1] | - | - | - |
| `Search` | não | sim | não | não | - |
| `in` (substring) | - | sim [3] | - | - | - |
| `Len` | - | sim [5] | - | - | - |
| `IsBlank` | **não** [4] | não | não | não | não |

Notas oficiais, resumidas:

1. `EndsWith(coluna, "x")` delega; `EndsWith("x", coluna)` não. Em `CHAR(10)`, `"hello"` tem 10
   caracteres: `EndsWith(coluna, "llo")` dá falso, por desenho.
2. **Filtro de data direto não funciona com SQL Server atrás de gateway on-premises.** A saída
   documentada é uma coluna calculada numérica e filtrar por ela (§4).
3. `"texto" in coluna` delega; `coluna in "texto"` não. A lista literal (`coluna in ["a", "b"]`)
   **não consta** na tabela do SQL: trate como não delegável.
4. `!IsBlank(coluna)` não delega; `coluna <> Blank()` delega e é semanticamente próximo (não trata
   `""` como vazio). Não serve para Guid.
5. `Len` delega, mas o Power Apps trata `CHAR(10)` com `"hello"` como tamanho 5 e o SQL como 10.
   Use `VARCHAR`/`NVARCHAR`, não `CHAR`/`NCHAR`.
6. `StartsWith(coluna, "x")` delega; `StartsWith("x", coluna)` não.

Mais regras do lado do app: comparação de coluna com variável que é `Blank()` não se resolve no
servidor; use o idioma `IsBlank(variável) || coluna = variável` (o lado esquerdo é constante do
cliente e é dobrado antes da consulta, então delega)
`[verificado: projeto de referência]` (verificado no conector SQL; no Dataverse ver
`delegacao-dataverse.md`).

Destino: YAML colado.

```yaml
# xx-gal-pedidos
Items: |-
  =Sort(
    Filter(
      Pedido,
      StartsWith(Unidade, varUnidadeFiltro),
      IsBlank(varStatusFiltro) || Status = varStatusFiltro
    ),
    Dt_Inclusao,
    SortOrder.Descending
  )
```

(Ilustração de propriedade; a tela completa está em [tela-molde.md](../assets/tela-molde.md).)

## 3. Contagem

**`CountRows` e `CountIf` não delegam no conector SQL**: a tabela do §2 não os lista. O `Filter`
interno delega e vira `WHERE`; só a contagem roda no cliente, sobre as até 2.000 linhas que
desceram. O defeito clássico é o card exibir `2.000` como se fosse o total.
`[verificado: projeto de referência]`

Saídas, da mais barata para a mais exata:

| Saída | Quando | Custo |
|---|---|---|
| **Teto na UI**: se `n >= fxLimiteLinhas`, mostre `fxTxtTeto` (`2.000+`) | cartão e rótulo informativo | zero; o número é exato ou se declara incompleto, nunca mente |
| **`Sum` de coluna que vale 1** (coluna calculada `1`, ou `Flg_*` numérica) | contagem exata sem procedure | `Sum` delega no SQL (Número) |
| **Contar no servidor**: procedure com `COUNT_BIG` devolvida pelo flow | número exato acima do teto (relatório, exportação) | um flow por contagem |

Destino: YAML colado.

```yaml
# xx-lbl-total
Text: |-
  =If(
    varPedidoTotal >= fxLimiteLinhas,
    fxTxtTeto,
    Text(varPedidoTotal)
  )
```

Quando card e galeria leem a **mesma fonte com o mesmo predicado**, concordam por construção:
foi o que fechou o defeito de "o número do card não bate com a lista". Mantenha o predicado
(inclusive o de escopo) num só lugar. `[verificado: projeto de referência]`

Contador **recalcula** no `OnVisible` e depois de cada flow que grava. Contador calculado só no
`OnStart` congela e diverge da galeria.

## 4. Datas

Filtro de data direto não delega atrás de gateway on-premises. A nota [2] da própria tabela dá a
saída: coluna calculada numérica no banco e filtro por ela.

**No banco** (pedido à skill `sql-procedures`): uma coluna inteira `Ref_<coluna>` igual ao
número de dias desde 1900-01-01, persistida:
`Ref_DtInclusao AS DATEDIFF(day, 0, Dt_Inclusao) PERSISTED`. **Nunca `CAST(... AS INT)`**: o
`CAST` arredonda, não trunca; um evento às 13:00 do dia-limite vira o dia seguinte e some da
janela, errado num registro a cada dois, em silêncio.

**No Power Fx**: o `DatePicker` converte no `OnChange` e a variável guarda **inteiro**, não data.
`36524` é a distância de 1900-01-01 até 2000-01-01 (Power Fx não tem literal de 1900).

Destino: YAML colado.

```yaml
# xx-dtp-filtro-de
OnChange: |-
  =Set(
    varPedidoDe,
    If(
      IsBlank(Self.SelectedDate),
      Blank(),
      36524 + DateDiff(Date(2000, 1, 1), Self.SelectedDate, TimeUnit.Days)
    )
  )
```

O `If` existe porque `DatePicker` vazio entrega `SelectedDate` em branco: sem ele a variável vira
número, o `IsBlank` do `Filter` deixa de reconhecer "sem filtro" e a galeria abre vazia.

Destino: YAML colado.

```yaml
# xx-gal-pedidos-janela
Items: |-
  =Filter(
    Pedido,
    IsBlank(varPedidoDe) || Ref_DtInclusao >= varPedidoDe,
    IsBlank(varPedidoAte) || Ref_DtInclusao <= varPedidoAte
  )
```

- **Sem `DateAdd(+1)` no limite superior.** `Ref_*` é número do dia: `<=` já inclui o dia todo.
  O padrão antigo somava 1 dia a uma data e usava `<=`, incluindo também a meia-noite do dia
  seguinte (um dia a mais, calado).
- **`Reset()` de `DatePicker` não dispara `OnChange`.** O botão Limpar reescreve a variável com o
  **mesmo** valor do `OnVisible`; senão o controle mostra uma janela e o `Filter` usa outra.
- Variáveis de janela nascem no `OnVisible` da tela, não no `OnStart`.

**Fuso.** `Ref_<col>` é o dia **no fuso em que a coluna foi gravada** (normalmente UTC). O
`DatePicker` devolve data local: com UTC−3, registros das 21h às 23h59 caem no dia seguinte e o
filtro por dia erra calado. Registre no `NOMES-AS-BUILT` se o `Ref_` é dia UTC ou local e use a
mesma regra nos dois lados; a coluna em dia local é DDL (ver
`sql-procedures/references/colunas-calculadas-delegacao.md`).
- Não vale para o que viaja ao flow: data em **texto** `yyyy-mm-dd`; quem filtra lá é a
  procedure, em T-SQL, não o conector.

## 5. Dataverse

Esta skill é dona da delegação **SQL**; a delegação do **Dataverse** é da skill `dataverse`. A
diferença em uma frase: no Dataverse o conector aceita mais funções e agregações, com teto próprio
de 50.000, e o `Filter` com variável, `Today()` e `CountRows(Filter(...))` têm regras distintas das
do SQL. Matriz, tetos e ressalvas: ver `dataverse/references/delegacao-dataverse.md`.

## 6. Busca, `in` e `LookUp`

- **`StartsWith` primeiro** (usa índice, vira `LIKE 'x%'`). `Search` e `"x" in coluna` viram
  `LIKE '%x%'`: sem índice, lentos em tabela grande. A Microsoft recomenda `StartsWith` ou
  `Filter` em vez de `in`
  ([Optimized query data patterns](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/optimized-query-data-patterns)).
- **`coluna in [lista]` sobre fonte SQL não delega**: o app baixa o teto e filtra no cliente, sem
  erro. Alternativas: igualdades ligadas por `Or` (poucos valores), coluna calculada de grupo,
  ou procedure via flow. O validador acusa `Search(`/`in` dentro de `Filter(` sobre fonte que não
  é `col*` (T011); no SQL, `Search` em coluna de texto delega (tabela do §2), então o aviso
  pede **conferência**, não é condenação.
- **Nunca `LookUp(<fonte>, ...)` dentro de galeria**: uma consulta por linha renderizada (N+1;
  50 linhas = 51 requisições). Resolva rótulo por **coleção** carregada no `OnStart`
  (`LookUp(colCategorias, ...)` é de graça). O mesmo vale para `AddColumns` com `LookUp` dentro.
- **Funil em 3 estágios** quando for preciso juntar domínios: reduzir no servidor
  (`Filter` delegável), juntar com `in` sobre coleção pequena, buscar por nome já em memória.
  `Distinct` e `With` no estágio 1 truncam: ver §8.

## 7. Coluna errada falha calada

`SearchFields`, `DisplayFields` e `SortByColumns` recebem **nomes de coluna entre aspas**. Nome
inexistente **não dá erro**: `DisplayFields` devolve campo vazio no `ComboBox`, `SearchFields`
não acha nada e `SortByColumns` simplesmente não ordena. Isso acontece porque `AddColumns`
preserva as colunas de origem, então o nome errado continua "resolvendo".
`[verificado: projeto de referência]`

- O nome lógico (Dataverse) / nome da coluna na fonte (SQL) vem do ambiente (`NOMES-AS-BUILT`, skill `dataverse`), não do nome de
  exibição nem do dicionário. No conector SQL o nome é **case-sensitive**; errar a grafia não
  acusa em edição e falha em runtime, calado.
- **Extrato filtrado não prova esquema.** Antes de afirmar que uma coluna não existe (ou que
  existe), abra o esquema da tabela, não uma amostra (decisão N3).
- `DisplayFields` precisa do nome da coluna na fonte: SQL não tem *primary name column*; `[""]` não serve.
- Teste digitando no controle e olhando o resultado. O validador acusa só o que dá para ver sem
  o ambiente: T014 (prefixo, na trilha Dataverse).

## 8. O que quebra a delegação sem aviso

| Padrão | Efeito | Saída |
|---|---|---|
| `With({x: ...}, Filter(fonte, ...))` | a fonte vira coleção; sem aviso | `With` só para escalar, fora do `Filter` |
| `Distinct(Filter(fonte, ...), col)` | `Distinct` não delega: trunca em 500/2.000 | coluna de agrupamento ou tabela de junção no banco |
| `AddColumns`/`ShowColumns` em consulta grande | o argumento delega, a **saída** trunca | usar sobre conjunto já reduzido |
| `FirstN(Sort(Filter(...)), 50)` | `FirstN` não delega; se o `Filter` também não, vira "top 50 das primeiras 500 arbitrárias" | paginação ou "carregar mais" sobre `Items` delegável |
| `Gallery.AllItems` como fonte | só o já carregado | `AllItemsCount` ou predicado delegável |
| `UpdateIf`/`RemoveIf` sobre fonte grande | simula delegação até 500/2.000 | operação no servidor |
| `If(...)` dentro de `Filter` | não delega | resolva o `If` na variável, antes |
| 50 variáveis escalares + `Or` para simular `in` | delega, mas custa 150 `Set` | coluna de agrupamento |

## 9. Quando não delega: alternativas

Em ordem de preferência:

1. **View ou coluna calculada no servidor** (a recomendação mais forte da Microsoft; view
   desliga agregação no Dataverse).
2. **Coluna desnormalizada** + `=` ou `StartsWith` (usa índice), preenchida por flow ou procedure.
3. **Flow/procedure** que devolve o conjunto já resolvido (custa ~0,6 s para instanciar o flow).
4. **`Or` de igualdades**: delega, mas caminha para o teto de condições e some a leitura.
5. **Filtro local com *Data row limit* alto**: resultado **incorreto** acima de 2.000 linhas.
   Último recurso, e só com o teto declarado na UI.

Domínios pequenos e estáveis (poucos milhares de linhas, usados por 4 telas ou mais) vão para
**coleção ou named formula**, carregados uma vez. Dado transacional que outro usuário altera em
paralelo, não: o cache vira decisão sobre dado velho.

## 10. Como provar

1. **Data row limit = 1** num clone do app (*Settings > General*): toda consulta não delegável
   devolve uma linha, e a lista que "some" aparece em segundos. É a técnica recomendada pela
   Microsoft. Faça antes de entregar tela nova.
2. **App checker**: conte os avisos de delegação e anote o controle de cada um.
3. **Live monitor**: abra a tela e leia a consulta enviada (`WHERE`/`$filter`). Uma requisição
   por página da galeria é bom; uma por linha é N+1.
4. Teste com **volume acima do teto** (carga sintética): o `2.000+` e o comportamento de
   delegação só se provam assim.
5. `[não verificado]` `in [lista]` sobre fonte SQL: confirme no Monitor se o seu app envia o
   `WHERE` ou baixa e filtra.

## 11. Declarar por escrito (T7)

No topo de cada arquivo de tela, em comentário `#` (o arquivo é YAML puro; `//` quebra o parse
fora de fórmula): para cada função de tabela, se delega e qual é o teto.

Destino: comentário no topo do arquivo `.pa.yaml` (não é fórmula).

```text
# DELEGACAO desta tela (fonte SQL, teto fxLimiteLinhas = 2000)
#   Filter + StartsWith + Sort ............ delega (WHERE / ORDER BY)
#   CountRows(Filter(...)) ................ NAO delega; rotulo mostra fxTxtTeto
#   Filtro de data ........................ por Ref_DtInclusao (inteiro), delega
#   coluna in [lista] ..................... nao usado
```

Comentário YAML (`#`) fora de fórmula é permitido no arquivo-fonte, mas **não é preservado** pelo
Studio ao reexportar: a declaração vive no repositório, não no app.

## 12. Fontes

- [Understand delegation in a canvas app](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview)
- [Connect to SQL Server from Power Apps overview](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview)
- [Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service)
- [Count, CountA, CountIf, CountRows](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-table-counts)
- [AddColumns, DropColumns, RenameColumns, ShowColumns](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-table-shaping)
- [Optimized query data patterns](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/optimized-query-data-patterns)
- [Top performance issues (N+1)](https://learn.microsoft.com/en-us/power-platform/architecture/key-concepts/performance/top-issues)

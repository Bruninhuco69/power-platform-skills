# Delegação no conector Dataverse

O que o Dataverse delega, o que não delega, os limites e como testar. O lado do app (como escrever
a galeria, `OnStart`, contadores) é de `powerapps-canvas`; esta referência cobre o que é **específico
do conector Dataverse** e a diferença para o conector SQL Server.

## Sumário

1. [A regra e o limite](#1-a-regra-e-o-limite)
2. [Matriz do conector Dataverse](#2-matriz-do-conector-dataverse)
3. [Contagem e agregação](#3-contagem-e-agregação)
4. [In, StartsWith, Search](#4-in-startswith-search)
5. [Datas](#5-datas)
6. [Armadilhas silenciosas](#6-armadilhas-silenciosas)
7. [Dataverse × SQL Server](#7-dataverse--sql-server)
8. [Quando não delega: saídas](#8-quando-não-delega-saídas)
9. [Como testar](#9-como-testar)

---

## 1. A regra e o limite

- Se **qualquer parte** da expressão não delega, **nenhuma** parte delega: o app baixa as primeiras
  **500** linhas (configurável até **2.000**, em *Configurações → Geral → Limite de linhas de dados*)
  e filtra no cliente, **sem erro**.
  Fonte: [Understand delegation](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview).
- O aviso (triângulo amarelo) só aparece em fórmula sobre fonte delegável e não cobre tudo. **Ausência
  de aviso não prova delegação.** Teste com limite 1 (§9).
- O resultado errado "parece certo": é o truncamento silencioso (a classe de defeito mais cara de um app Canvas). Toda consulta
  declara por escrito o que delega (`decisoes-padrao.md` T7).

## 2. Matriz do conector Dataverse

Transcrita da tabela do conector
([Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service),
consultada em 2026-10). A tabela do conector é a autoridade: o que **não** está nela não delega.

| Operação | Número | Texto | Choice | DateTime | GUID |
|---|---|---|---|---|---|
| `<` `<=` `>` `>=` | sim | sim | **não** | sim | — |
| `=` `<>` | sim | sim | sim | sim | sim |
| `And` / `Or` / `Not` | sim | sim | sim | sim | sim |
| `Filter`, `LookUp`, `Sort`, `SortByColumns` | sim | sim | sim | sim | `Filter`/`LookUp`: sim |
| `First` | sim | sim | sim | sim | sim |
| `In` (pertence a lista) | sim | sim | sim | sim | sim |
| `In` (substring) | — | sim | — | — | — |
| `IsBlank` | sim | sim | **não** | sim | sim |
| `Search` | não | **sim** | não | não | — |
| `StartsWith` | — | sim | — | — | — |
| `CountRows`, `CountIf` | sim | sim | sim | sim | sim |
| `Sum`, `Min`, `Max`, `Avg` | sim | — | — | **não** | — |

Notas da tabela oficial que mudam fórmulas:

1. **Número**: expressão aritmética na coluna (`Filter(t; col + 10 > 100)`) não delega; cast para
   número também não; coluna que o app vê como número mas o backend não é número simples (moeda) não delega.
2. **Texto**: `Trim`, `Trim[Ends]` e `Len` não são suportados; `Left`, `Mid`, `Right`, `Upper`,
   `Lower`, `Replace` e `Substitute` constam como suportados na nota oficial; `Text(col)` não.
   Um projeto de referência registrou `Upper`/`Lower`/`Left`/`Mid` sobre coluna como **não** delegáveis na
   prática `[verificado: projeto de referência, divergência com a nota oficial]` — **teste antes de usar**.
3. **DateTime** delega, **exceto** as funções `Now()` e `Today()` (ver §5).
4. `CountRows` usa **valor em cache** (ver §3).
5. Para `CountRows`, o usuário precisa de permissão para obter totais da tabela.
6. Toda agregação é limitada a **50.000** linhas e **não funciona em views**.
7. **`FirstN` não é suportada.**
8. `In` está sujeito ao limite de **15 tabelas** por consulta do Dataverse (nota do conector). Outra
   fonte de um projeto de referência cita 20 entidades por consulta em outra página; a documentação é
   inconsistente `[não verificado qual vale]`.
9. `IsBlank` aceita comparações (`col = Blank()`), mas **não** em Choice.
10. `UpdateIf`/`RemoveIf` só simulam delegação até 500/2.000 registros.

Fora da tabela e, portanto, **não delegam**: `EndsWith`, `Distinct`, `GroupBy`/`Ungroup`, `ForAll`,
`Concat`, `Collect`/`ClearCollect`, `Choices`, `With`, `If` dentro do predicado, `Left`/`Mid`/`Right`
sobre coluna (conforme um projeto de referência), `exactin`, `StdevP`/`VarP`, coleções locais como fonte.
`EndsWith` aparece na lista geral de delegação mas não na tabela do conector Dataverse: trate como não
delegável e valide no Monitor `[verificado: projeto de referência]`.

Limites estruturais de consulta (citados por um projeto de referência a partir do Learn, **não reconfirmados**):
condições por consulta OData ≈ 500 (`TooManyConditionsInQuery`), níveis de lookup/expand = 2,
cláusulas `$expand` = 10, strings num `In` ≈ 850 caracteres no total
([Filter rows using OData](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query/filter-rows))
`[não verificado]`. Para reduzir condições, use `In`/`NotIn` em vez de uma cadeia de `Or`.

## 3. Contagem e agregação

Diferente do SQL Server, **o Dataverse delega contagem**, com três ressalvas:

| Uso | Delega | Teto | Exatidão |
|---|---|---|---|
| `CountRows(Tabela)` sem filtro | sim | sem teto duro | **aproximada** (valor em cache) |
| `CountRows(Filter(Tabela; …))` | sim | 50.000 | exata até o teto `[não verificado: um projeto de referência cita que exige a opção "Enhanced delegation for Microsoft Dataverse"; a página do conector não a menciona]` |
| `CountIf(Tabela; cond)` | sim | 50.000 | exata até o teto |
| `CountIf(Tabela; true)` | sim | 50.000 | exata — contorna o cache do `CountRows` |

Fonte: nota 4 do conector e [Count, CountA, CountIf, CountRows](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-table-counts).

Consequências:

- `CountRows` sem filtro serve a "mais ou menos quantos"; para conferência de carga use
  `CountIf(Tabela; true)` (`references/importacao-dados.md`).
- **Contador que mostra `50000` pode ser a consulta quebrada, não o volume.** `IfError(...; 50000)`
  mascara falha com o número exato do teto. Mostre o erro, ou `—`, nunca um número plausível.
  `[verificado: projeto de referência]`
- Agregação em **view** não funciona; view resolve filtro no servidor, mas desliga `Sum`/`CountIf`.
- Acima de 50.000, agregue no servidor (flow, view materializada, coluna de resumo/rollup).

## 4. In, StartsWith, Search

- `col in [lista]` e `col in colecao` (coluna da **tabela base**) delegam; o doc só exemplifica
  `in` com array literal, e a delegação contra **coleção variável** é demonstrada por blog de terceiro
  (não por documentação). **Valide com limite 1** `[não verificado]`.
- `col in [lista]` sobre coluna de **outra tabela** (via relacionamento) não delega.
- `"texto" in col` (substring) delega em Text, mas equivale a `LIKE '%x%'` e **não usa índice**: a
  Microsoft prefere `StartsWith`
  ([Optimized query data patterns](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/optimized-query-data-patterns)).
  Não confunda os dois `in`.
- `StartsWith(coluna; texto)` delega e usa índice; a **coluna fica à esquerda**. Igualdade também:
  `coluna = variavel`, não `variavel = coluna`, ou a expressão não delega `[verificado: projeto de referência]`.
- `Search` delega só em colunas de texto; `SearchFields` com nome errado **falha calado**
  (`references/nomes-e-tipos.md` §3).

```
// barra de fórmulas (pt-BR: ; e ;;)
// Delega: coluna à esquerda, texto, StartsWith
Filter(
  Pedidos;
  StartsWith(unidade; varUnidadeFiltro);
  situacao = 'situacao (Pedidos)'.Aberto
)
```

Cuidado com o filtro de escopo `""` = "todas": `StartsWith(unidade; "")` é verdadeiro para toda
linha com valor, e **deixa de fora linha com `unidade` vazia**. Se vazio precisa significar "todas",
trate o caso (`IsBlank(varUnidadeFiltro) || …` quebra a delegação — prefira dois ramos de `If`
*fora* do `Filter`, ou garanta coluna obrigatória). `[não verificado em Dataverse; no SQL o idioma delega — verificado]`

## 5. Datas

DateTime delega no Dataverse. A exceção é a função `Now()`/`Today()` (nota 3 do conector), que **conflita**
com a página geral de delegação (esta diz que `Today()` "dobra para constante" e não bloqueia).
**Trate como risco** e elimine a dúvida:

```
// barra de fórmulas (pt-BR: ; e ;;)
// OnStart ou OnVisible: calcula a data uma vez
Set(varLimite; DateAdd(Today(); -30; TimeUnit.Days));;

// Filtro: a variável é constante, a coluna fica sozinha à esquerda
Filter(Pedidos; data_pedido >= varLimite)
```

Cuidado ao ir para o outro extremo: **`With(…)` em volta da fonte quebra a delegação sem aviso**
(§6). A variável deve ser **escalar** (`Set`), não um `With` que envolva a tabela.

## 6. Armadilhas silenciosas

| Armadilha | Efeito | Saída |
|---|---|---|
| `With`, `Set` ou `UpdateContext` sobre **fonte** | Criam coleção em memória: não delegam, **sem aviso** | Use `With` só para escalares e constantes; deixe a tabela fora |
| `AddColumns`/`ShowColumns` | Os argumentos delegam, a **saída trunca** em 500/2.000 | Projete só colunas necessárias; não use como join de tabela grande |
| `AddColumns` com `LookUp` dentro | Uma chamada de rede **por linha** (N+1) | Desnormalize a coluna ou carregue o mestre pequeno numa coleção |
| `Distinct(Filter(…))` | Não delega; lista de filtros trunca | Tabela de domínio, ou flow que devolve os valores |
| Constante dentro do `Filter` (`!varFlag && col = x`) | A cláusula constante não delega no Dataverse | `If(varFlag; Blank(); Filter(…))` fora do `Filter` |
| `Choices()` como fonte de galeria | Não delega | Só para ComboBox de poucas opções |
| `IfError(…; 50000)` | Falha vira número plausível | Mostre erro |
| Consulta Dataverse dentro de `Visible` ou `Timer.Start` | Rede a cada avaliação | Variável atualizada em evento |

Fonte do primeiro item: [Delegation overview](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview).

## 7. Dataverse × SQL Server

A mesma fórmula delega de um jeito num conector e de outro no outro. Mudança de trilha invalida a
auditoria de delegação.

| Aspecto | Dataverse | SQL Server |
|---|---|---|
| `CountRows`/`CountIf` | delega (≤ 50.000; sem filtro é aproximado) | **não delega**: mostre teto (`2.000+`) ou conte no servidor (B3) |
| Filtro de data direto | delega | **não delega** atrás de gateway: coluna calculada inteira `Ref_<col>` (B2) |
| `Sum`/`Min`/`Max`/`Avg` | delega em Número (≤ 50.000) | delega em Número |
| `EndsWith`, `Len` | não | sim (texto) |
| `In` (pertence) | sim | não (só substring) |
| `Search` | só texto | só texto |
| `*` `/` sobre coluna | não | sim (número) |
| View como saída | resolve filtro no servidor; **sem agregação** | idem (view) |
| Tipos | Choice/Lookup/Yes/No nativos | `bit`, texto, número |

Origem: matriz de `decisoes-padrao.md` B2/B3 e tabela de conectores de um projeto de referência
(`[verificado: projeto de referência]` para a coluna SQL; a coluna Dataverse segue o Learn acima).

## 8. Quando não delega: saídas

Em ordem de preferência para Dataverse:

1. **View** pré-filtrada no servidor (a Microsoft é a que mais recomenda): filtro e junção rodam no
   servidor e o payload cai. Preço: sem agregação.
2. **`Filter(tabela; col in colValores)`**, respeitando ≈ 850 caracteres de strings por consulta.
3. **Coluna desnormalizada** + `=` ou `StartsWith` (usa índice), preenchida por flow, plugin ou
   gravação do app (`references/modelagem.md`).
4. **Flow** que devolve o resultado já agregado/filtrado (volume acima de 50.000; export).
5. **Aceitar o teto** e mostrá-lo (`2.000+`), se a regra de negócio permitir.

Nunca: exportar a partir de galeria ou coleção (perde dado sem erro); usar o filtro de galeria como
único controle de acesso (`references/seguranca.md`).

## 9. Como testar

1. *Configurações → Geral → Limite de linhas de dados* = **1**. Toda consulta não delegada passa a
   devolver uma linha, o que é fácil de ver. Recomendação da própria documentação.
2. Percorra a tela: galeria, contadores, combos de filtro, `LookUp` de identidade. Linha única onde
   deveria haver lista = não delega.
3. Abra o **Monitor** (*Avançado → Abrir Monitor*) e confira a consulta enviada ao servidor: o
   `$filter` deve conter o predicado. Predicado ausente = filtro no cliente.
4. Devolva o limite a 500 (ou 2.000) e anote no cabeçalho da tela o que delega, o que não e o teto.

A auditoria não termina no Studio: o dado de produção tem mais linhas que o de teste. Teste com a
massa maior que o limite.

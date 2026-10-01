# Colunas calculadas para delegação

Quando o app Power Apps filtra, ordena ou conta uma fonte SQL, o que **não delega** roda no cliente,
sobre as primeiras N linhas (o teto de dados do app), e dá resposta errada sem erro. Colunas
calculadas no banco resolvem três casos sem criar dado novo. O lado do app (a fórmula `Filter`, os
tetos, as variáveis) é da skill `powerapps-canvas`; aqui está a coluna.

## Sumário

1. [Por que isso existe](#1-por-que-isso-existe)
2. [Ref_ de data](#2-ref_-de-data)
3. [Por que nunca CAST AS INT](#3-por-que-nunca-cast-as-int)
4. [Contagem](#4-contagem)
5. [Status derivado](#5-status-derivado)
6. [Índice e requisitos](#6-índice-e-requisitos)
7. [Entrega ao DBA](#7-entrega-ao-dba)

---

## 1. Por que isso existe

A tabela de funções delegáveis ao SQL Server (fonte:
https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview)
diz, entre outras coisas:

- `CountRows` e `CountIf` **não** estão na lista de delegáveis; `Sum`, `Min`, `Max`, `Average`,
  `Filter`, `LookUp`, `Sort`, `SortByColumns`, `StartsWith`, `EndsWith` estão.
- **Filtro de data direto não funciona com SQL Server atrás de gateway on-premises.** A própria nota
  da documentação sugere "uma coluna calculada" numérica e filtrar por ela.
- `IsBlank(coluna)` não delega; `coluna <> Blank()` delega (e não trata `""` como vazio).

O conector também cobra o formato: `bit` vira Boolean, datas viram DateTime, e tipos como
`rowversion`/`xml`/espaciais não são suportados. Detalhe em `modelo-de-dados.md` §2.

| Problema no app | Saída no banco |
|---|---|
| Filtro por faixa de data atrás de gateway | coluna `Ref_<col>` inteira (§2) |
| `CountRows(Filter(...))` exibindo número errado acima do teto | contar no servidor (§4) ou `Sum` de coluna constante |
| Predicado composto repetido em 20 fórmulas (ex.: "atrasado", "a vencer") | coluna de status derivado (§5) |

## 2. Ref_ de data

```sql
ALTER TABLE dbo.APP_Pedido
    ADD Ref_DtInclusao AS (DATEDIFF(day, 0, Dt_Inclusao)) PERSISTED;
GO
```

`DATEDIFF(day, 0, x)`: o `0` convertido para `datetime` é `1900-01-01`; o resultado é o **número do
dia** desde essa data, inteiro, determinístico, `PERSISTED` e indexável.
`[verificado: projeto de referência]`

No app, o seletor de data converte para o **mesmo número** (a diferença de dias até `1900-01-01`) e
a variável guarda inteiro, não data. A fórmula e a armadilha do `Reset()` de `DatePicker` estão em
`powerapps-canvas`. Dois pontos que dependem do banco:

- **`Ref_` é número do dia: `<=` já inclui o dia inteiro.** Não some `+1` ao limite superior (o padrão
  antigo, com `DateAdd(+1)` e data, incluía também a meia-noite do dia seguinte: um dia a mais na
  janela, em silêncio).
- A tela e o **JSON de filtros enviado ao flow** são coisas diferentes: o JSON viaja data em texto
  (`"yyyy-mm-dd"`) porque quem filtra ali é o T-SQL (função de leitura), não o conector.

**Fuso.** `Ref_<col>` é o dia **no fuso em que a coluna foi gravada** (normalmente UTC,
`SYSUTCDATETIME()`). O `DatePicker` do app devolve data local: com UTC−3, registros das 21h às
23h59 caem no dia seguinte e o filtro erra calado. Decida e registre no `NOMES-AS-BUILT` se o
`Ref_` é dia UTC ou local. Para dia local com gravação em UTC, use deslocamento fixo, que é
determinístico e persistível:

```sql
ALTER TABLE dbo.APP_Pedido
    ADD Ref_DtInclusaoLocal AS (DATEDIFF(day, 0, DATEADD(hour, -3, Dt_Inclusao))) PERSISTED;
```

`[não verificado: deslocamento fixo só vale sem horário de verão]`. `AT TIME ZONE` **não** serve
aqui: a Microsoft o classifica como não determinístico, porque as regras de fuso vivem fora do
SQL Server (https://learn.microsoft.com/en-us/sql/t-sql/queries/at-time-zone-transact-sql), e coluna
calculada indexável ou `PERSISTED` exige expressão determinística
(https://learn.microsoft.com/en-us/sql/relational-databases/indexes/indexes-on-computed-columns).

Alternativa documentada pela Microsoft (mesma fonte): `YEAR(c)*10000 + MONTH(c)*100 + DAY(c)`, número
no formato `yyyymmdd`. Funciona igual; escolha **uma** por projeto e registre no `NOMES-AS-BUILT`
(a conversão do app tem de bater com a do banco).

Aplique a coluna em **cada** tabela cujo filtro de data o app usa, e exponha-a nas views que o app
lê (a view precisa listar a coluna nova).

## 3. Por que nunca CAST AS INT

`CAST(<datetime> AS INT)` **arredonda**: um registro às 13:00 vira o dia seguinte e some da janela
quando o filtro é `<=` o dia limite, errado em cerca de um registro a cada dois, e calado.
`DATEDIFF` **trunca**. `[verificado: projeto de referência]`

Prove no seu banco (as duas colunas diferem em 1 para qualquer horário a partir do meio-dia):

```sql
SELECT CAST(CAST('2026-03-10T13:00:00' AS datetime) AS int)              AS Cast_Int,
       DATEDIFF(day, 0, CAST('2026-03-10T13:00:00' AS datetime))         AS Datediff_Dia,
       CAST(CAST('2026-03-10T09:00:00' AS datetime) AS int)              AS Cast_Int_Manha;
```

O `lint-procedure.py` acusa `CAST(<coluna ou função de data> AS INT)` e `CONVERT(INT, <data>)` com
`P006`.

## 4. Contagem

`CountRows(Filter(fonte; ...))` roda o `Filter` no servidor, mas **conta no cliente**, sobre o que
desceu (até o teto). O número é exato abaixo do teto e **errado em silêncio** acima dele.

Três saídas, da mais simples à mais cara:

1. **Teto declarado na tela.** O rótulo mostra `2.000+` quando a contagem atinge o teto, e nunca
   finge que o teto é o total. O que fecha o defeito não é o número ser sempre exato; é nunca ser
   errado calado. (Fórmula em `powerapps-canvas`.)
2. **`Sum` de coluna constante** (a coluna é uma contagem disfarçada de soma, e `Sum` delega):
   `[verificado: projeto de referência]`

   ```sql
   ALTER TABLE dbo.APP_Pedido ADD Ref_Contador AS (CAST(1 AS INT));
   GO
   ```

   No app, `Sum(Filter(fonte; ...); Ref_Contador)` entrega o total exato. A coluna é calculada, não
   guarda dado e não precisa de `PERSISTED`.
3. **Contar no servidor**, por procedure de contagem chamada pelo flow
   (`assets/funcao-leitura-molde.sql`, `usp_APP_Pedido_Contar`). É o único caminho quando o
   filtro usa a função de leitura com JSON, e o que o botão de exportar deve usar.

Não crie **view agregada** para contador: view nova é objeto novo, e a view e a galeria precisam
concordar o tempo todo. Contador e galeria sobre a mesma tabela e o mesmo predicado concordam por
construção.

## 5. Status derivado

Predicado que aparece em muitas fórmulas vira coluna calculada:

```sql
ALTER TABLE dbo.APP_Pedido ADD Des_StatusPrazo AS (
    CASE
        WHEN Dt_Inclusao IS NULL THEN NULL
        WHEN Dt_Inclusao < DATEADD(day, -30, CAST(GETUTCDATE() AS DATE)) THEN 'Atrasado'
        WHEN Dt_Inclusao < DATEADD(day, -20, CAST(GETUTCDATE() AS DATE)) THEN 'A vencer'
        ELSE 'No prazo'
    END
);
GO
```

- Depende de `GETUTCDATE()`, que **não é determinística**: a coluna **não pode** ser `PERSISTED`
  nem indexada; filtro por ela faz varredura. Aceitável no volume atual; registre o limite.
- **A fronteira (30, 20 dias) é regra de negócio**, e raramente está escrita em documento. Confirme
  com a operação antes de criar a coluna; é o número que separa as faixas na tela inteira.
- Para o conector é uma coluna comum de texto: `=` e `<>` delegam.
- Se a regra mudar, muda no DDL (pedido ao DBA). Por isso, regra que muda toda semana fica no flow e
  não numa coluna.

## 6. Índice e requisitos

Índice sobre coluna calculada exige (fonte:
https://learn.microsoft.com/en-us/sql/relational-databases/indexes/indexes-on-computed-columns):

- expressão **determinística** e **precisa** (sem `float`/`real`); funções do mesmo dono da tabela;
  `PERSISTED` permite indexar expressão determinística mas imprecisa;
- na criação e em **todas as conexões que gravam**, `ANSI_NULLS`, `ANSI_PADDING`, `ANSI_WARNINGS`,
  `ARITHABORT`, `CONCAT_NULL_YIELDS_NULL`, `QUOTED_IDENTIFIER` em `ON` e `NUMERIC_ROUNDABORT` em
  `OFF`; o otimizador ignora o índice para o `SELECT` de uma conexão sem essas opções;
- `QUOTED_IDENTIFIER ON` ao criar ou alterar o índice (scripts gerados por ferramentas às vezes
  trazem `OFF`);
- não existe índice **filtrado** sobre coluna calculada.

```sql
CREATE NONCLUSTERED INDEX IX_APP_Pedido_Ref_DtInclusao
    ON dbo.APP_Pedido (Ref_DtInclusao)
    INCLUDE (Nom_Abvd_Unidade, Des_Status);
GO
```

Confirme o uso do índice no plano de uma consulta real (`Index Seek`), sem confiar na intuição. Em
tabela grande, `ALTER TABLE ... ADD ... PERSISTED` grava a coluna em todas as linhas: peça janela ao
DBA `[não verificado: custo no seu volume]`.

## 7. Entrega ao DBA

Banco congelado em produção costuma recusar tabela nova, coluna que guarda dado, view nova e mudança
de assinatura, e **aceitar coluna calculada**. O critério real não é "é DDL?", é **"o objeto guarda
dado próprio?"**: a coluna calculada deriva de outra e não carrega informação nova.
`[verificado: projeto de referência]`

Peça junto, no mesmo pedido, todas as colunas calculadas do projeto (`Ref_*`, contador, status), com
a justificativa de delegação e a consulta que prova o efeito. Molde: `assets/pedido-ddl-dba-molde.md`.
Quem decide o que entra no banco é o DBA; a tela e o flow sempre podem absorver o que ele recusar,
com o custo de desempenho ou de exatidão declarado.

# Pedido de DDL ao DBA · <projeto> · <AAAA-MM-DD>

> Molde. Um pedido por conjunto de mudanças relacionadas. Preencha com o que o **ambiente real**
> mostrou (consulta colada), não com o que o plano supõe. Banco congelado em produção? Leia a seção 2
> antes de pedir qualquer coisa.
>
> Como entregar o pacote: `sql-procedures/references/deploy-e-dba.md`.

| | |
|---|---|
| Solicitante | `<nome da equipe, não da pessoa>` |
| Banco / instância | `<banco>` em `<servidor>\<instancia>` (no pedido real; **não** neste repositório) |
| Ambiente | DEV / HML / PRD |
| Banco congelado? | sim, desde `<data>` / não |
| Prazo e impacto de não ter | `<quando precisa e o que quebra sem isso>` |

## 1. Resumo em uma tabela

| # | Objeto | Tipo | Novo ou altera? | Guarda dado próprio? | Por que o app precisa | Alternativa sem o DBA |
|--:|---|---|---|---|---|---|
| 1 | `dbo.<SIGLA>_<Entidade>.Ref_<Dt>` | coluna calculada `PERSISTED` | altera tabela | **não** | filtro de data não delega atrás de gateway | filtrar no cliente: resposta errada acima do teto |
| 2 | `dbo.<SIGLA>_<Entidade>.Ref_Contador` | coluna calculada | altera tabela | **não** | `Sum` delega, `CountRows` não | teto `2.000+` na tela |
| 3 | `IX_<...>` | índice | novo | não (estrutura) | sustenta o `HOLDLOCK` e o escopo | lock de tabela / varredura |
| 4 | `FK_<...>` | FK | altera tabela | não | impede registro órfão | registro filho fantasma com sucesso |

## 2. Critério

Em banco congelado, o que costuma ser aceito é o que **não guarda dado próprio** (coluna calculada);
índice de apoio e FK dependem do DBA (justifique com a prova de plano ou o órfão medido); o que costuma ser recusado é tabela nova, coluna que guarda dado, view nova e
mudança de assinatura de procedure existente. Para cada item, a coluna "Guarda dado próprio?" da
seção 1 responde a pergunta do DBA antes de ele fazer.

## 3. Estado atual do ambiente

Resultado das consultas **rodadas pelo solicitante** (ou pelo DBA, se o solicitante não tem acesso):

```sql
SELECT SERVERPROPERTY('ProductMajorVersion') AS Versao_Major,
       compatibility_level                   AS Nivel,
       DATABASEPROPERTYEX(DB_NAME(), 'Collation') AS Collation_Banco,
       is_read_committed_snapshot_on         AS Rcsi,
       is_recursive_triggers_on              AS Triggers_Recursivos
  FROM sys.databases
 WHERE name = DB_NAME();
```

| Item | Valor encontrado | Exigido |
|---|---|---|
| Versão major | `<n>` | `>= 13` se usar `OPENJSON` |
| `COMPATIBILITY_LEVEL` | `<n>` | `>= 130` se usar `OPENJSON` |
| Collation | `<nome>` | `_CI_AI` assumida em vários portões: **confirmar** |
| `RCSI` | `<0/1>` | informativo |
| `RECURSIVE_TRIGGERS` | `<0/1>` | `0` |

## 3.1 O que já existe

```sql
SELECT o.name, o.type_desc, o.create_date, o.modify_date
  FROM sys.objects AS o
 WHERE o.name LIKE '<prefixo>%';
```

Cole a saída. Para cada procedure que será **substituída** por `CREATE OR ALTER`, guarde a definição
atual antes (`sys.sql_modules`) e diga se a assinatura muda.

## 4. DDL pedido

Um bloco por item, idempotente, com a consulta que prova o efeito logo abaixo.

```sql
-- Item 1: numero do dia para filtro de data (derivada; nao guarda dado)
ALTER TABLE dbo.<SIGLA>_<Entidade>
    ADD Ref_<Dt> AS (DATEDIFF(day, 0, <Dt>)) PERSISTED;
GO

-- prova: tem de voltar 0 linhas (a coluna calculada bate com a derivacao manual)
SELECT COUNT_BIG(*) AS Divergentes
  FROM dbo.<SIGLA>_<Entidade>
 WHERE Ref_<Dt> <> DATEDIFF(day, 0, <Dt>);
GO
```

Substitua `<...>` pelos nomes reais **antes** de enviar. Pedido com placeholder não é pedido.

## 5. Risco e janela

| Item | Risco | Janela sugerida | Rollback |
|--:|---|---|---|
| 1 | `ALTER TABLE ... ADD ... PERSISTED` grava a coluna em todas as linhas; bloqueia a tabela durante a operação (custo proporcional ao volume: `<n linhas>`) | `<fora do horário de uso>` | `ALTER TABLE ... DROP COLUMN Ref_<Dt>` (e o índice antes) |
| 3 | custo de manutenção do índice na escrita | idem | `DROP INDEX` |

## 6. O que este pedido **não** pede

Liste o que foi considerado e deixado de fora (tabela nova, view, mudança de assinatura) e a
alternativa em tela ou flow que o projeto adotou no lugar. É o que evita o DBA ter de adivinhar o que
você aceitou perder.

## 7. Perguntas que só o DBA responde

| # | Pergunta | Bloqueia |
|--:|---|---|
| 1 | Elevar o `COMPATIBILITY_LEVEL` para `>= 130` é aceito? | parâmetros em JSON, funções de leitura |
| 2 | Collation do banco e das tabelas do projeto? | portões de reentrada e guardas de identidade |
| 3 | `<pergunta de negócio ou de ambiente>` | `<objeto em hold>` |

## 8. Conferência depois de aplicado

Rode e cole a saída no `NOMES-AS-BUILT` (`deploy-e-dba.md` §8): PKs existem; nenhum `Flg_*` anulável;
sem duplicata de identidade; `RECURSIVE_TRIGGERS = 0`; `SET NOCOUNT ON` em toda procedure e trigger;
conta do conector sem DML; retorno de cada procedure de escrita com 1 result set, 1 linha, 4 colunas.

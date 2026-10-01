# Deploy e entrega ao DBA

Como montar o pacote que o DBA (quem tem permissão no banco) roda, em que ordem, com que provas de
ambiente, e o que esperar depois que o banco congela em produção. Peça DDL com
`assets/pedido-ddl-dba-molde.md`.

## Sumário

1. [Princípios do pacote](#1-princípios-do-pacote)
2. [Ordem de execução](#2-ordem-de-execução)
3. [Provas de ambiente](#3-provas-de-ambiente)
4. [Antes de substituir o que já existe](#4-antes-de-substituir-o-que-já-existe)
5. [Validar sem executar](#5-validar-sem-executar)
6. [Depois do congelamento](#6-depois-do-congelamento)
7. [Nomes as-built e o que não regerar](#7-nomes-as-built-e-o-que-não-regerar)
8. [Conferência final](#8-conferência-final)

---

## 1. Princípios do pacote

- **Scripts numerados e idempotentes** (`CREATE OR ALTER`, `IF NOT EXISTS`); o DBA pode rodar de novo
  sem medo.
- **O DDL não é extraído automaticamente.** Um documento de DDL tem *probes*, alternativas
  mutuamente exclusivas, `DROP COLUMN` comentado de propósito e perguntas sem resposta: extrair
  produziria um script que roda e destrói coisa certa. Monte o DDL **à mão**, seção por seção,
  e entregue as procedures (que são `CREATE OR ALTER`, seguras) separadas.
- **`.sql` gerado a partir da fonte** (o contrato em `.md`) traz no cabeçalho "gerado, não
  editar" e a origem. Correção vai para a fonte (P3).
- **Uma carta ao DBA** (`_LEIA-PRIMEIRO`): o que não está na pasta e por quê, a ordem, as provas que
  param o plano, o que está em *hold*, as perguntas que só ele responde.
- **Nada foi compilado** é uma afirmação que o pacote precisa fazer quando for verdade: sem instância
  SQL Server à mão, só resta pedir `PARSEONLY` ao DBA. Tenha uma instância de DEV (ou um container)
  para compilar **antes** de enviar.
- Cada procedure traz a versão mínima do SQL Server que exige (`OPENJSON`: 2016,
  `COMPATIBILITY_LEVEL >= 130`; `STRING_AGG`: 2017, `ProductMajorVersion >= 14`;
  `CREATE OR ALTER`: 2016 SP1).

## 2. Ordem de execução

| # | Item | Nota |
|--:|---|---|
| 1 | DDL de pré-requisito: PKs, `Flg_*` como `BIT NOT NULL DEFAULT 0`, colunas calculadas, índices únicos, FKs, triggers de `Dt_Alteracao` | à mão; cada bloco com a consulta que prova o efeito |
| 2 | **Provas de ambiente** (§3) | rode **antes** das procedures; as que reprovam **param o plano** |
| 3 | Função de leitura e índices de apoio | a função **antes** das procedures que a chamam |
| 4 | Procedure de resolução do chamador | destrava o tronco de todos os flows |
| 5 | Procedures de escrita, **por onda** (usuário → entidade principal → registros dependentes → relatório) | a de contagem **antes** da de exportação |
| 6 | Normalização da carga (`LOWER`/`TRIM` de identidade, siglas sem padding, vocabulário) | só esse script limpa o que já está na tabela |
| 7 | `GRANT EXECUTE` e `REVOKE` de DML (`seguranca-e-permissoes.md` §2) | **por último** |
| 8 | Conferência final (§8) | cole a saída no `NOMES-AS-BUILT` |

Marque no pacote o que está em **HOLD**: o objeto que depende de pergunta de negócio sem resposta
(ex.: "usuário sem e-mail pode existir?"). O resto sobe sem ele.

## 3. Provas de ambiente

Quatro provas. Tragam resposta do ambiente **real**, não do que se supõe dele.

**3.1 Versão e nível de compatibilidade** (para `OPENJSON` e `STRING_AGG`):

```sql
SELECT SERVERPROPERTY('ProductMajorVersion') AS Versao_Major,   -- >= 13 (OPENJSON), >= 14 (STRING_AGG)
       compatibility_level                   AS Nivel,          -- >= 130
       DB_NAME()                             AS Banco
  FROM sys.databases
 WHERE name = DB_NAME();
```

Se o nível for menor que 130 **e** o DBA recusar elevar, parâmetros em JSON morrem e a saída é uma
assinatura com dezenas de parâmetros escalares: muda a assinatura **e** o flow. Pare e reporte.
(`OPENJSON` só existe em nível 130+:
https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql.)

**3.2 `OUTPUT ... INTO` numa tabela com trigger ativo** (condição de parada: sem isto, as procedures
que encadeiam escrita não têm corpo válido). A documentação já responde (a forma com `INTO` é a
suportada), mas **prove no seu banco** com o trigger real ativo, em DEV:

```sql
DECLARE @tv TABLE (Id_Pedido INT NOT NULL);

UPDATE dbo.APP_Pedido
   SET Nom_Abvd_Unidade = Nom_Abvd_Unidade      -- no-op deliberado
OUTPUT INSERTED.Id_Pedido INTO @tv (Id_Pedido)
 WHERE Id_Pedido = <id existente>;

SELECT Id_Pedido FROM @tv;
```

Portão: 1 linha em `@tv`, sem erro e **um único** result set. Qualquer erro de "target table of the
OUTPUT INTO clause cannot have any enabled triggers" ou dois result sets: pare.

**3.3 A identidade do app casa com a coluna do banco?** Se não casar, a procedure de resolução
devolve zero linha e o flow nega toda escrita do sistema. No app, `User().Email` de dois usuários
reais; no banco:

```sql
SELECT TOP (5) Id_Usuario, Email_Usuario, Upn_Entra, Flg_Situacao
  FROM dbo.APP_Usuario
 ORDER BY Id_Usuario;

-- espaco a ESQUERDA nao e protegido por collation nenhuma; tem de voltar vazio
SELECT Id_Usuario, '[' + Email_Usuario + ']' AS Email_Com_Delimitador
  FROM dbo.APP_Usuario
 WHERE Email_Usuario <> LTRIM(RTRIM(Email_Usuario));
```

`User().Email` costuma ser igual ao UPN, **mas não em todos os tenants**: compare os dois valores.

**3.4 Collation, isolamento e triggers recursivos:**

```sql
SELECT DATABASEPROPERTYEX(DB_NAME(), 'Collation') AS Collation_Banco,
       is_read_committed_snapshot_on              AS Rcsi,
       is_recursive_triggers_on                   AS Triggers_Recursivos   -- tem que ser 0
  FROM sys.databases
 WHERE name = DB_NAME();
```

- Collation `_CS_AS` quebra portões de reentrada (`<> N'encerrado'` não barra `'Encerrado'`) e
  guardas de identidade: registre o que o banco tem.
- `RCSI` ligado: `SELECT` sem hint **não** protege uma decisão; `UPDATE`-como-predicado continua
  correto (`padrao-procedure.md` §8).
- `Triggers_Recursivos` em `1`: o trigger de `Dt_Alteracao` dispara a si mesmo dentro da transação.

## 4. Antes de substituir o que já existe

`CREATE OR ALTER` **substitui** procedure em uso, não cria ao lado. Se uma versão anterior existe,
as assinaturas podem ter mudado. Antes de rodar qualquer coisa, **salve o que está lá**:

```sql
-- 1) o que ja existe
SELECT o.name, o.type_desc, o.create_date, o.modify_date
  FROM sys.objects AS o
 WHERE o.name LIKE 'usp[_]APP[_]%' OR o.name LIKE 'tvf[_]APP[_]%';

-- 2) o plano de volta: guarde a saida ANTES do primeiro CREATE OR ALTER
SELECT OBJECT_NAME(m.object_id) AS objeto, m.definition
  FROM sys.sql_modules AS m
 WHERE OBJECT_NAME(m.object_id) LIKE 'usp[_]APP[_]%'
    OR OBJECT_NAME(m.object_id) LIKE 'tvf[_]APP[_]%';
```

Troque o padrão pelos nomes reais. Objeto **novo** (função que não existe) é uma conversa diferente de
**alterar** um existente; o pedido diz qual é qual.

## 5. Validar sem executar

Sintaxe, sem criar nada:

```sql
SET PARSEONLY ON;
GO
-- cole aqui o conteudo de cada .sql, um por vez
GO
SET PARSEONLY OFF;
GO
```

`PARSEONLY` valida **sintaxe** e não resolve nomes. Para validar também as colunas, use
`SET NOEXEC ON` depois que o DDL da etapa 1 estiver aplicado. Nenhum dos dois substitui compilar numa
instância de DEV.

No repositório, antes de enviar: `python <pasta-da-skill>/scripts/lint-procedure.py <pasta>` (zero erro) e a
checagem de divergência de `contrato-proc-flow.md` §4.

## 6. Depois do congelamento

Em produção, o DBA costuma congelar o banco após o Go Live: "toda correção tem de caber em tela ou
flow". Aprenda a pergunta certa **antes** de propor qualquer DDL:

| Objeto | Costuma ser aceito? | Critério |
|---|---|---|
| Coluna **calculada** (`Ref_*`, contador, status derivado) | **sim** | não guarda dado próprio |
| Tabela nova | não | guarda dado próprio |
| Coluna nova que **guarda** dado | não | guarda dado próprio |
| View nova | não | objeto novo |
| Mudança de assinatura de procedure existente | não | quebra o flow já colado |
| Índice de apoio | depende; peça com a prova de plano | custo de manutenção na escrita |
| Procedure nova substituindo `CREATE OR ALTER` | conversa com o DBA | objeto novo × alteração |

`[verificado: projeto de referência]` para a primeira linha (a coluna calculada foi aceita
depois do congelamento). **O teste é "o objeto guarda dado próprio?", não "é DDL?".**

Estratégia: planeje o schema **antes** do primeiro deploy; peça de uma vez tudo o que pode ser
necessário (colunas `Ref_*`, índices, FKs); e, para cada correção pós-congelamento, pergunte primeiro
se cabe em tela ou flow. Quando precisar de objeto novo, abra um pedido com a justificativa mensurável
e a saída que a tela/flow teria sem ele (o DBA recusa mais facilmente o que não vê custo evitado).

## 7. Nomes as-built e o que não regerar

- Antes de montar qualquer chamada de flow, **leia o nome real** do ambiente:

  ```sql
  SELECT s.name AS Schema_, p.name AS Procedure_, p.create_date, p.modify_date
    FROM sys.procedures AS p
    JOIN sys.schemas    AS s ON s.schema_id = p.schema_id
   ORDER BY p.name;
  ```

  O padrão documentado (`usp_<SIGLA>_<Entidade>_<Acao>`) divergiu do nome real
  (`SP_<SIGLA>_<VERBO>_<OBJETO>`) no projeto de referência, e o nome real **não é deduzível por
  regra**. Registre o de-para num bloco de dados com a data da verificação; marque como hipótese
  o que não foi confirmado.
- Se a toolchain **gera** flows ou `.sql` a partir da fonte, o gabarito já colado e corrigido à mão é
  a única evidência de ambiente que existe: o gerador escreve só em `dist/`, nunca sobre ele (F6, P3).
  Rodar o gerador "porque o portão manda" apagou correções reais no projeto de referência.
- Permissão de conta: `GRANT EXECUTE` por último, `REVOKE` de DML; reconferir depois de cada onda.

## 8. Conferência final

| # | Conferir | Resultado esperado |
|--:|---|---|
| 1 | PKs existem em todas as tabelas | consulta de `modelo-de-dados.md` §10 vazia |
| 2 | Nenhum `Flg_*` anulável | consulta de `modelo-de-dados.md` §4 vazia |
| 3 | Sem duplicata de identidade | `GROUP BY ... HAVING COUNT(*) > 1` vazio |
| 4 | `RECURSIVE_TRIGGERS` | `0` |
| 5 | `SET NOCOUNT ON` em toda procedure e trigger | consulta (b) de `seguranca-e-permissoes.md` §7 vazia |
| 6 | A conta do conector sem DML | consulta (a) vazia |
| 7 | `UPDATE ... OUTPUT ... INTO` com trigger ativo | 1 linha, um result set |
| 8 | `COMPATIBILITY_LEVEL >= 130` | número na tela |
| 9 | **Teste do retorno** de cada procedure de escrita | **1** result set · **1** linha · **4** colunas, **inclusive** nos desfechos de zero linha gravada |

O item 9 é o que reprova calado: nenhum teste funcional o pega, porque a procedure *funciona*; só o
retorno é que some. Execute cada procedure de escrita e confira o que o conector recebe. Procedure
de leitura de dado não devolve as quatro colunas: o que se confere ali é a lista de colunas.

# Migração de dados para SQL Server

Playbook de carga **inicial única** de um legado (planilha, banco local, outro banco) para o SQL Server de
um app Power Apps. O método é agnóstico ao destino: extrair → staging → validar → mapear → carregar →
reconciliar, com o mapeamento de nomes e vocabulários isolado. O código vem de um projeto de referência;
**compile cada script numa instância de DEV antes de entregar**:
os trechos abaixo seguem o padrão do projeto, mas não foram executados por esta skill
`[não verificado: execução em instância]`.

## Sumário

1. [Escopo e desenho](#1-escopo-e-desenho)
2. [Os passos](#2-os-passos)
3. [Staging tudo NVARCHAR](#3-staging-tudo-nvarchar)
4. [Validação dirigida por metadados](#4-validação-dirigida-por-metadados)
5. [Guarda e ação no mesmo batch](#5-guarda-e-ação-no-mesmo-batch)
6. [A carga: trigger, IDENTITY e transação](#6-a-carga-trigger-identity-e-transação)
7. [Reseed e reconciliação](#7-reseed-e-reconciliação)
8. [Rollback](#8-rollback)
9. [Arquivos gerados e codificação](#9-arquivos-gerados-e-codificação)
10. [Normalização do que já existe](#10-normalização-do-que-já-existe)
11. [Segurança da carga](#11-segurança-da-carga)
12. [Lições](#12-lições)

---

## 1. Escopo e desenho

- Carga **única**, não sincronização incremental. Volume típico de app departamental (milhares de
  linhas) roda em segundos; não otimize.
- **Staging antes do destino.** O transporte do dado (`stg`, tudo texto) é separado da conversão e
  validação (destino tipado). Se falha, você sabe em qual das duas metades.
- **Valide tudo de uma vez**: a fase de validação escreve a **lista completa** de problemas numa tabela
  e só então aborta, em vez de parar no primeiro `CHECK` violado.
- **Geração tudo-ou-nada**: se um gerador falha no meio, apague o que já escreveu. Pacote incompleto
  no disco tem a aparência exata de um pacote pronto.
- A origem é aberta **somente leitura**; os segredos (hash de senha) ficam fora dos artefatos por
  padrão.
- **Mapeie contra o ambiente real**, não contra o plano. O pacote do projeto de referência foi
  escrito para um schema proposto; o DBA construiu outro (`dbo`, prefixos corporativos), e a ponte
  entre os dois não estava documentada. A lógica é 100% reutilizável; o que muda é a camada de nomes
  (`NOMES-AS-BUILT`, N1).

## 2. Os passos

Numeração do pacote de referência; cada script verifica o pré-requisito e aborta com mensagem
específica se algo estiver fora de ordem.

| Passo | Arquivo | Função | Salvaguarda |
|---|---|---|---|
| 01 | `01_staging_ddl.sql` | schema `stg`, tudo `NVARCHAR` | `DENY` de leitura/escrita a `db_datareader`/`db_datawriter`; o passo 30 reconfere |
| 02 | `02_staging_dados.sql` (gerado) | `INSERT` do dado da origem, em ASCII puro | imune a codepage errada; `03_bulk_insert_alternativo.sql` como plano B |
| 04 | `04_metadados_validacao.sql` (gerado) | tabelas de metadados: tipo, vocabulário, tamanho, FK, formato, obrigatoriedade | mesma definição Python da validação pré-carga; nenhum SQL guardado como dado |
| 10 | `10_pre_carga_ajustes.sql` | remove seed que colide com os IDs da origem; round-trip de collation | recusa se já houver registro referenciando o seed |
| 20 | `20_carga.sql` | validação completa → desabilita trigger → carga em transação → reabilita | guarda e ação no mesmo batch |
| 21 | `21_reseed_identity.sql` (gerado) | reposiciona `IDENTITY` | pelo contador da origem, não por `MAX(id)` |
| 30 | `30_validacao_pos_carga.sql` | constraints confiáveis, trigger de volta, `DENY` no lugar | toda linha `OK` |
| 31 | `31_reconciliacao.sql` (gerado) | contagem por tabela, `MIN/MAX` de datas, canários de acento, manifesto | tudo deve dar `OK` |
| 90 | `90_rollback.sql` | devolve o destino ao estado pós-DDL; o staging permanece | pode recarregar a partir do passo 10 |

`MANIFESTO.json` e `RELATORIO_PRE_CARGA.md` trazem contagens, `SHA-256` por tabela, achados e o
veredito `LIBERADO`/`BLOQUEADO`. O gerador devolve exit `0` (sem bloqueio), `1` (há bloqueios, não
carregue), `2` (erro de execução).

**Decisões de negócio** que mudam o resultado (região de uma unidade que diverge entre origem e
seed, descartar uma classificação que o código não lê, login local × Entra) são levantadas
**antes** de rodar, com padrão marcado e dono da decisão. Nenhuma é do DBA.

## 3. Staging tudo NVARCHAR

Colunas idênticas às da origem, **todas** texto, **zero** constraint: qualquer restrição abortaria o
transporte antes de a validação poder reportar o problema. Preserve também o que o destino não porta
(a decisão de descartar é de negócio; o dado fica disponível).

```sql
IF SCHEMA_ID('stg') IS NULL
    EXEC (N'CREATE SCHEMA stg');
GO

DROP TABLE IF EXISTS stg.itens;
DROP TABLE IF EXISTS stg.erros_validacao;
DROP TABLE IF EXISTS stg.regra_coluna;
GO

CREATE TABLE stg.itens (
    id           NVARCHAR(400) NULL,
    protocolo    NVARCHAR(400) NULL,
    status_item  NVARCHAR(400) NULL,
    unidade      NVARCHAR(400) NULL,
    criado_em    NVARCHAR(400) NULL
);

CREATE TABLE stg.erros_validacao (
    tabela   NVARCHAR(128)  NOT NULL,
    regra    NVARCHAR(200)  NOT NULL,
    chave    NVARCHAR(400)  NULL,
    detalhe  NVARCHAR(1000) NULL
);

-- metadados da validacao: uma linha por coluna tipada
CREATE TABLE stg.regra_coluna (
    tabela  NVARCHAR(128) NOT NULL,
    coluna  NVARCHAR(128) NOT NULL,
    tipo    NVARCHAR(30)  NOT NULL,     -- texto | int | date | datetime2 | bit
    limite  INT           NULL
);
GO
```

## 4. Validação dirigida por metadados

As fases de validação (tipo, vocabulário, tamanho, FK, formato, obrigatoriedade) saem das tabelas de
metadados que o passo 04 popula, **geradas da mesma definição** que a validação pré-carga usa. Não
existe cópia manual de vocabulário para sair de sincronia. A checagem de obrigatoriedade cobre toda
coluna `NOT NULL` do destino, em vez de uma lista escrita à mão.

Detalhes que mordem:

- `TRY_CONVERT` devolvendo `NULL` para valor **não nulo** significa que a conversão real falharia.
- **Comprimento em unidades UTF-16**, como `NVARCHAR(n)` conta: use `DATALENGTH(col) / 2`, não `LEN()`,
  que desconta espaço à direita (51 caracteres terminando em espaço passariam como 50 e o `INSERT`
  truncaria).
- Toda checagem filtra `IS NOT NULL` antes de comparar (`NULL NOT LIKE padrão` é `NULL`); a
  obrigatoriedade é uma fase **própria**, senão coluna nula passa a validação inteira e estoura no
  `INSERT` com erro cru.
- Vocabulário é comparado **com acento** (collation accent-sensitive): um valor que chegou com
  codepage errado não casa e aparece como erro.
- `ANSI_WARNINGS ON` **explícito** nos scripts de carga: com `OFF` o SQL Server trunca string longa
  demais em silêncio, em vez de falhar.

Uma fase gerada (validação de conversão de tipo). O SQL dinâmico usa só **nomes de coluna vindos de
metadado interno, passados por `QUOTENAME`**, nunca valor da origem; por isso o `lint-procedure.py`
(P009) é dispensado com justificativa:

```sql
SET ANSI_WARNINGS ON;
GO

DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql = @sql
    + N'INSERT INTO stg.erros_validacao (tabela, regra, chave, detalhe) '
    + N'SELECT ' + QUOTENAME(r.tabela, '''') + N', '
    + N'N''tipo/' + REPLACE(r.coluna, '''', '''''') + N' -> ' + r.tipo + N''', t.id, '
    + N'CONCAT(N''valor nao conversivel: ['', t.' + QUOTENAME(r.coluna) + N', N'']'') '
    + N'FROM stg.' + QUOTENAME(r.tabela) + N' AS t '
    + N'WHERE t.' + QUOTENAME(r.coluna) + N' IS NOT NULL AND TRY_CONVERT('
    + CASE r.tipo
          WHEN 'date'      THEN N'date, t.'         + QUOTENAME(r.coluna) + N', 23'
          WHEN 'datetime2' THEN N'datetime2(0), t.' + QUOTENAME(r.coluna) + N', 120'
          WHEN 'int'       THEN N'int, t.'          + QUOTENAME(r.coluna)
          ELSE N'bit, t.' + QUOTENAME(r.coluna)
      END
    + N') IS NULL;' + CHAR(10)
  FROM stg.regra_coluna AS r
 WHERE r.tipo <> 'texto';

EXEC sp_executesql @sql;   -- lint-ok P009: nomes de metadado interno via QUOTENAME, sem valor externo
GO
```

## 5. Guarda e ação no mesmo batch

**Erro num batch não interrompe os batches seguintes**, nem no SSMS nem no `sqlcmd` sem `-b`. Se a
porta de saída da validação estiver num batch e a carga em outro, um `THROW` ali aborta aquele batch
e a carga roda **mesmo assim**, com dado reprovado. Regra:

- A porta de saída da validação, o `DISABLE TRIGGER` e todos os `INSERT` ficam em **um batch só**,
  com as guardas **repetidas** (se alguém ignorou o erro do batch anterior, este aborta antes de
  tocar no destino).
- Rode por linha de comando com `sqlcmd -b -f 65001`: `-b` aborta no primeiro erro; `-f 65001` evita
  qualquer dúvida de codepage.

## 6. A carga: trigger, IDENTITY e transação

O trigger de `Dt_Alteracao` (ou de data de atualização) **sobrescreve a data real** de cada linha
carregada pela data da migração, **sem erro, sem aviso, sem nada no log**. É o único passo cuja
omissão causa perda silenciosa de dado. Desabilite na carga e reabilite **fora** da transação:

```sql
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

IF EXISTS (SELECT 1 FROM stg.erros_validacao)
    THROW 50023, 'Validacao reprovada. Nada foi carregado. Veja stg.erros_validacao.', 1;

IF EXISTS (SELECT 1 FROM dbo.APP_Pedido)
    THROW 50025, 'Destino ja tem dado: carga inicial. Rode o rollback antes de repetir.', 1;

ALTER TABLE dbo.APP_Pedido DISABLE TRIGGER TR_APP_Pedido_Dt_Alteracao;

BEGIN TRANSACTION;

SET IDENTITY_INSERT dbo.APP_Pedido ON;

INSERT INTO dbo.APP_Pedido
      (Id_Pedido, Nr_Protocolo, Des_Status, Nom_Abvd_Unidade, Flg_Situacao, Dt_Inclusao)
SELECT CAST(i.id AS INT), i.protocolo, i.status_item, i.unidade, 1,
       CONVERT(datetime2(3), i.criado_em, 120)
  FROM stg.itens AS i
 ORDER BY CAST(i.id AS INT);

SET IDENTITY_INSERT dbo.APP_Pedido OFF;

COMMIT TRANSACTION;
GO

-- batch proprio e SEM guarda de erro, de proposito: se a carga abortou no meio, o trigger ficou
-- desabilitado, e deixa-lo assim silenciaria a regra em producao. Idempotente.
IF EXISTS (SELECT 1 FROM sys.triggers
            WHERE name = N'TR_APP_Pedido_Dt_Alteracao' AND is_disabled = 1)
    ALTER TABLE dbo.APP_Pedido ENABLE TRIGGER TR_APP_Pedido_Dt_Alteracao;
GO
```

- `IDENTITY_INSERT` quando outras tabelas referenciam o id (trilha, registros filhos): perder o id desfaz a
  trilha de auditoria. Só um por sessão e **sempre desligado** ao final.
- Conversões **explícitas** (`CONVERT(..., 120)` para datetime, `23` para date, `CAST` para
  uniqueidentifier, `CASE` para bit): nada de conversão implícita de texto para data.
- As datas da origem já estão em UTC? Confirme e documente; sem conversão de fuso na carga.
- Seed do destino que **colide com os IDs da origem** (ex.: tabela de domínio semeada com poucas linhas,
  origem com mais, em ordem diferente) reatribuiria o dado em silêncio. Remova o seed com guarda, carregue
  com `IDENTITY_INSERT`.
- **Collation e acento:** coluna `VARCHAR` com vocabulário acentuado, em collation de codepage
  incompatível, grava `?` e o `CHECK` aceita. O passo 10 faz o round-trip `NVARCHAR → VARCHAR →
  NVARCHAR` de cada valor do vocabulário com a collation **real** e aborta se algum não voltar
  idêntico.

## 7. Reseed e reconciliação

**Reseed pelo contador da origem, não por `MAX(id)`.** Se a origem apaga ids (sincronização que
remove linhas), o contador está à frente do `MAX`; reciclar os ids faria linhas do histórico apontarem
para o registro de outro:

```sql
DBCC CHECKIDENT ('dbo.APP_Pedido', RESEED, 1305) WITH NO_INFOMSGS;
```

(`1305` é o valor do contador da **sua** origem; o gerador o escreve no passo 21.)

**Reconciliação** (passo 31): tudo deve dar `OK`.

```sql
SELECT 'APP_Pedido'                             AS Tabela,
       (SELECT COUNT_BIG(*) FROM dbo.APP_Pedido) AS No_Destino,
       1200                                           AS Na_Origem,   -- numero do MANIFESTO
       CASE WHEN (SELECT COUNT_BIG(*) FROM dbo.APP_Pedido) = 1200 THEN 'OK' ELSE 'FALHA' END AS Situacao;

-- datas reais preservadas: MIN/MAX contra os valores da origem
SELECT MIN(Dt_Inclusao) AS Menor, MAX(Dt_Inclusao) AS Maior FROM dbo.APP_Pedido;

-- canario de acento: um por valor acentuado efetivamente presente
SELECT COUNT_BIG(*) AS Canario_Acento
  FROM dbo.APP_Pedido
 WHERE Des_Status = N'Em An' + NCHAR(0x00E1) + N'lise';
```

O `31` traz, comentados, os `SHA-256` do manifesto: reproduza a qualquer momento com o comando de
checksum do gerador; se bater, a origem não mudou desde a geração.

Passo 30, antes: constraints **confiáveis** (`is_not_trusted = 0`; carga com `NOCHECK` as deixa não
confiáveis), o trigger de volta (`is_disabled = 0`) e o `DENY` no schema `stg` no lugar.

## 8. Rollback

`90_rollback.sql` devolve o destino ao estado imediatamente posterior ao DDL: apaga na **ordem
inversa de FK**, em transação, faz `RESEED` para zero e confirma o trigger habilitado. **Não** apaga o
schema `stg`: ele é a prova documental do que veio da origem e permite recarregar sem repetir o
passo 02 (há uma seção final, comentada, para derrubá-lo na virada).

Cuidado: se o sistema já estiver em uso, o rollback apaga dado criado no destino, não só o migrado.
O script mostra o volume atual antes de apagar e manda **parar** se existir data posterior à da
migração.

## 9. Arquivos gerados e codificação

- **ASCII puro.** Vocabulário com acento (`Em Análise`) comparado por `CHECK` contra literal exato
  quebra se o `.sql` for lido com codepage errado (`sqlcmd` sem `-f 65001`, editor legado, arquivo que
  passou por e-mail): `Em Análise` vira `Em AnÃ¡lise`. O gerador emite todo caractere não ASCII
  como `NCHAR(0xXXXX)` (como no canário acima), e os arquivos ficam idênticos em qualquer ferramenta.
- `INSERT` gerado é o caminho principal; `BULK INSERT` fica como alternativa: cobra caminho acessível
  pelo **serviço** do SQL Server, permissão `ADMINISTER BULK OPERATIONS` e codepage certo.
- Literal de texto escapa o apóstrofo (`'` → `''`): sem isso o literal fecha antes da hora e o resto
  do valor vira SQL. Cubra esse gerador de literais com testes desproporcionais ao tamanho: é onde um
  erro não aparece como erro.
- Valide na origem: quebra de linha, TAB, aspas, byte NUL e string vazia (indistinguível de `NULL`
  no CSV). `NCHAR(0)` anula o campo inteiro.

## 10. Normalização do que já existe

A procedure **não limpa dado existente**: só grava o que recebe. Carga suja (e-mail em caixa mista,
sigla com padding, vocabulário com outro acento, campos invertidos) é limpa por **script próprio de
normalização**, antes de criar o índice único e antes de abrir o app. Normalizar na procedure esconde o
problema: a tela lê a tabela direto e continua quebrada. Lista típica: `LOWER(LTRIM(RTRIM()))` de
identidade; `LTRIM(RTRIM())` de siglas; vocabulários; conferência de campos trocados.
Ver `modelo-de-dados.md` §8.

Não infira tipo nem domínio de linhas de teste da carga (`Teste1`), e não as promova a produção.

## 11. Segurança da carga

- Os scripts usam `CREATE SCHEMA`, `IDENTITY_INSERT`, `DISABLE TRIGGER`, `DBCC CHECKIDENT` e
  `ALTER TABLE`: na prática, `db_owner` **do banco**. Trate como sessão: login de DBA dedicado e
  temporário; **nunca** para a conta de serviço do app (ela precisa de `EXECUTE`, `SELECT`, e mais
  nada). Depois do passo 31 fechar `OK`, desabilite o login.
- Os artefatos **contêm dado real**. `saida/` fica no `.gitignore` e é **apagada** depois da carga;
  regerar é um comando. Entregue ao DBA por canal interno, não por e-mail.
- Hash de senha e outro dado sensível ficam fora por padrão e só saem com flag explícita.

## 12. Lições

1. Carga e DDL do **destino real** primeiro; script escrito contra o plano vira retrabalho.
2. Valide **vocabulário e acento** contra o destino real, não contra o plano.
3. Marque no pacote quais passos o DBA roda e quais o time roda (e com qual permissão).
4. O que o destino não porta continua no `stg` e nos CSVs: "decidimos não carregar" não é "perdemos".
5. Reconciliação sem número do manifesto não reconcilia nada: o documento que declara contagem traz o
   comando que a mede (P5).

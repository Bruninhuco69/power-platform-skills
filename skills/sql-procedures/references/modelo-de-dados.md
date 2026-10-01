# Modelo de dados

Convenções de tabela e coluna para um backend SQL Server consumido por Power Apps e procedures.
O **nome real** de tudo vem do ambiente (N1: `NOMES-AS-BUILT`); o que está aqui é o padrão a pedir
ao DBA e o que verificar no que já existe. Tabelas Dataverse são da skill `dataverse`.

## Sumário

1. [Prefixos de coluna](#1-prefixos-de-coluna)
2. [Chaves e o que o conector exige](#2-chaves-e-o-que-o-conector-exige)
3. [Auditoria: Dt_Inclusao e Dt_Alteracao](#3-auditoria-dt_inclusao-e-dt_alteracao)
4. [Flags: BIT NOT NULL DEFAULT 0](#4-flags-bit-not-null-default-0)
5. [Texto: tipo, collation e padding](#5-texto-tipo-collation-e-padding)
6. [Perfil e usuário: flags de permissão](#6-perfil-e-usuário-flags-de-permissão)
7. [Índices únicos filtrados e FKs](#7-índices-únicos-filtrados-e-fks)
8. [Vocabulários](#8-vocabulários)
9. [Grafia não se conserta](#9-grafia-não-se-conserta)
10. [O que verificar no que já existe](#10-o-que-verificar-no-que-já-existe)

---

## 1. Prefixos de coluna

Padrão corporativo observado no projeto de referência. Adote o do seu DBA; o importante é **um** e
documentado no `NOMES-AS-BUILT`.

| Prefixo | Uso | Exemplo |
|---|---|---|
| `Id_` | PK ou FK inteira. `Id_Legado*` guarda o id da origem na migração | `Id_Pedido` |
| `Nr_` | número de negócio (texto com formato fixo quando é código) | `Nr_Protocolo` |
| `Nom_` | nome. `Nom_Abvd_` = sigla abreviada (unidade) | `Nom_Abvd_Unidade` |
| `Des_` | descrição, status, item de vocabulário | `Des_Status` |
| `Tp_` | tipo | `Tp_Evento` |
| `Flg_` | indicador sim/não, `BIT NOT NULL DEFAULT 0` | `Flg_Situacao` |
| `Dt_` | data/hora, em UTC | `Dt_Inclusao` |
| `Nv_` | nível | `Nv_Perfil` |
| `Cod_` | código de tabela corporativa | `Cod_Grupo` |
| `Ref_` | **coluna calculada** de apoio a filtro (não guarda dado próprio) | `Ref_DtInclusao` |
| `Upn_`, `Email_`, `Objectid_` | identidade | `Email_Usuario` |

Tabelas: `<SIGLA>_<Entidade>` no singular. Funções inline: `tvf_<SIGLA>_<Entidade>_<Nome>`. Se o banco
já tem outra convenção, a do banco vence.

## 2. Chaves e o que o conector exige

- **PK declarada em toda tabela.** Sem PK, o conector SQL abre a tabela como somente leitura e
  `Patch`/`Defaults` desaparecem `[verificado: projeto de referência]`.
- `tinyint` e `smallint` não são suportados como PK; tipos como `binary`, `varbinary`, `image`,
  `rowversion`, `hierarchyid`, `sql_variant`, `xml` e tipos espaciais não são suportados.
  Fonte: https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview
- Mapeamento de tipos para o app: numéricos → Number, `char`/`varchar`/`nvarchar` → Text, `bit` →
  Boolean, datas → DateTime, `uniqueidentifier` → Guid (mesma fonte).
- Chave de negócio de unidade é a **sigla** quando ela é única e estável; códigos numéricos de
  tabela corporativa costumam **não** ser únicos sozinhos (a identidade é um par). Confirme com
  `SELECT sigla, COUNT(*) ... HAVING COUNT(*) > 1` antes de usar como chave.
- FK **real** no banco sempre que a relação existe. FK ausente deixa gravar registro órfão e devolver
  sucesso; o projeto de referência só descobriu na revisão.

## 3. Auditoria: Dt_Inclusao e Dt_Alteracao

| Coluna | Quem escreve | Valor |
|---|---|---|
| `Dt_Inclusao` | a procedure, na criação | `SYSUTCDATETIME()` do **banco** |
| `Dt_Alteracao` | **trigger** `AFTER UPDATE`, nunca procedure | `SYSUTCDATETIME()` |
| quem fez | a procedure, de `@Id_UsuarioChamador` | declaração do chamador (`seguranca-e-permissoes.md`) |

Nenhuma procedure aceita data de auditoria **por parâmetro**: a data do cliente é o relógio local,
e uma linha nasce horas adiante das demais. Tudo em UTC; conversão de fuso é da camada de exibição. Consequência para filtro por dia: `Ref_<col>`
é o dia UTC, e o `DatePicker` devolve data local (ver `colunas-calculadas-delegacao.md` §2).

A tabela tem mais de um escritor (procedure, carga, correção manual); a coluna não pode depender de
todos lembrarem, por isso trigger:

```sql
CREATE OR ALTER TRIGGER dbo.TR_APP_Pedido_Dt_Alteracao
ON dbo.APP_Pedido AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;   -- obrigatorio: o trigger roda DENTRO da transacao da procedure
    IF NOT EXISTS (SELECT 1 FROM inserted) RETURN;

    UPDATE s
       SET Dt_Alteracao = SYSUTCDATETIME()
      FROM dbo.APP_Pedido AS s
      JOIN inserted AS i ON i.Id_Pedido = s.Id_Pedido;
END
GO
```

Cuidados:

- **`SET NOCOUNT ON` também no trigger.** Sem ele o rowcount do `UPDATE` interno sobe com o
  resultado da procedure. Falha silenciosa, a mais provável da entrega.
- `RECURSIVE_TRIGGERS` tem de estar `OFF` (padrão do produto; restauração de backup e scripts de
  criação às vezes trazem outro valor), senão o trigger dispara a si mesmo dentro da transação.
  Prova em `deploy-e-dba.md`.
- Tabela com trigger **exige `OUTPUT ... INTO`** nas procedures; `OUTPUT` sem `INTO` falha.
  `INSERTED.Dt_Alteracao` no `OUTPUT` sai com o valor **de antes** do trigger: não leia por ali.
  Fonte: https://learn.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql
- Carga em massa de dado histórico com o trigger ativo **sobrescreve** a data real: desabilite na
  carga (`migracao-dados.md`).
- Trigger e `Dt_Alteracao` só estão onde a tabela tem `Dt_Alteracao`; não invente para tabela de log.

## 4. Flags: BIT NOT NULL DEFAULT 0

Toda coluna `Flg_*` é `BIT NOT NULL` com `DEFAULT`. Duas famílias, com padrões opostos: **flag de
permissão** do perfil nasce `DEFAULT 0` (ninguém ganha permissão por omissão); **interruptor de
segurança do `CONFIG` do flow** nasce **ligado** (ver `autorizacao-no-flow.md` §4 em `power-automate`).
Por quê o `NOT NULL`, em ordem de dano:

1. **Permissão:** o flow lê a flag da ação numa condição. `NULL` vira valor nulo trafegando até o
   `Switch`; com a autorização no flow não há segunda linha de defesa no banco.
2. **Resolução do chamador:** `p.Flg_Situacao = 1` com `NULL` é `UNKNOWN`: a linha some e **toda
   escrita daquele perfil é negada**, calada.
3. **Tipagem:** com parâmetro tipado, coluna `INT` que o app trata como booleano vira conversão
   implícita silenciosa (o `Patch` que não compilava passa a gravar).

Migrar coluna existente (ordem importa: `UPDATE`, `ALTER COLUMN`, `DEFAULT`):

```sql
UPDATE dbo.APP_Perfil SET Flg_Encerrar = 0 WHERE Flg_Encerrar IS NULL;
GO
ALTER TABLE dbo.APP_Perfil ALTER COLUMN Flg_Encerrar BIT NOT NULL;
GO
ALTER TABLE dbo.APP_Perfil ADD CONSTRAINT DF_APP_Perfil_Flg_Encerrar DEFAULT 0 FOR Flg_Encerrar;
GO
```

Atenção ao **default que não é 0**: "ativo" costuma nascer `1` (o registro novo precisa aparecer).
Confirme a semântica da coluna antes de rodar e anote a exceção no `NOMES-AS-BUILT`.

Consulta de conferência (tem de voltar **vazia**):

```sql
SELECT OBJECT_NAME(c.object_id) AS Tabela, c.name AS Coluna
  FROM sys.columns AS c
 WHERE c.name LIKE 'Flg[_]%'
   AND c.is_nullable = 1;
```

## 5. Texto: tipo, collation e padding

- **`NVARCHAR` para texto com acento.** `VARCHAR` com codepage incompatível grava `?` no lugar do
  caractere, sem erro, e um `CHECK` pode aceitar porque compara depois da conversão. O round-trip
  `NVARCHAR → VARCHAR → NVARCHAR` de cada valor de vocabulário, com a collation real do banco,
  prova (`migracao-dados.md`).
- **Collation.** O projeto de referência assumiu `_CI_AI` em várias premissas e **nunca verificou**:
  com `_CS_AS`, um portão `<> N'encerrado'` não barra `'Encerrado'` vindo da carga, e guarda e índice
  de identidade deixam de casar. Peça a collation do banco **e** das tabelas ao DBA; ver
  `deploy-e-dba.md`. Collation diferente entre bancos derruba `JOIN` entre eles (erro 468).
- **Power Fx é insensível a maiúsculas e sensível a acento**, e a maior parte das comparações roda no
  cliente: nenhuma collation resolve. Vocabulário com acento tem de estar **normalizado na carga**.
- **`CHAR(n)` carrega padding.** `CHAR(7)` com `'AAA'` guarda `'AAA    '`. No SQL Server o `=` ignora
  brancos à direita `[não verificado: confirme com SELECT 1 WHERE 'a' = 'a ']`; no Power Fx a
  comparação de texto é literal e **não** casa. Duas saídas: `VARCHAR(n)` nas tabelas que você
  controla, e `Trim()` na carga de qualquer coleção lida de coluna `CHAR` de tabela corporativa
  (nunca depois, nunca na tela).
  A documentação do conector recomenda `varchar`/`nvarchar` em vez de `char`/`nchar`, porque `Len`
  delega mas conta o padding do SQL, não o do Power Apps. Fonte: sql-connection-overview, nota 5.
- Espaço à **esquerda** não é protegido por collation alguma: normalize com `LTRIM(RTRIM())` na
  carga e na procedure, dos **dois** lados da comparação.
- Comparação de identidade (e-mail) sempre `LOWER(LTRIM(RTRIM()))` do parâmetro **e** coluna
  normalizada na carga, para o índice ser usado.

## 6. Perfil e usuário: flags de permissão

Permissão é **flag por ação** na tabela de perfil, não nome de perfil (T8). Exemplo mínimo, usado
pelos códigos de `padrao-procedure.md`:

```sql
IF OBJECT_ID(N'dbo.APP_Perfil', N'U') IS NULL
    CREATE TABLE dbo.APP_Perfil (
        Id_Perfil           INT IDENTITY(1, 1) NOT NULL CONSTRAINT PK_APP_Perfil PRIMARY KEY,
        Des_Perfil          NVARCHAR(50) NOT NULL,
        Nv_Perfil           INT          NOT NULL CONSTRAINT DF_APP_Perfil_Nv DEFAULT 0,
        Flg_Consultar       BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Consultar DEFAULT 0,
        Flg_Encerrar        BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Encerrar DEFAULT 0,
        Flg_Cancelar        BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Cancelar DEFAULT 0,
        Flg_TodasUnidades   BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Todas DEFAULT 0,
        Flg_Adm             BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Adm DEFAULT 0,
        Flg_Situacao        BIT          NOT NULL CONSTRAINT DF_APP_Perfil_Situacao DEFAULT 0
    );
GO

IF OBJECT_ID(N'dbo.APP_Usuario', N'U') IS NULL
    CREATE TABLE dbo.APP_Usuario (
        Id_Usuario          INT IDENTITY(1, 1) NOT NULL CONSTRAINT PK_APP_Usuario PRIMARY KEY,
        Nom_Usuario         NVARCHAR(100) NOT NULL,
        Email_Usuario       NVARCHAR(100) NULL,
        Upn_Entra           NVARCHAR(100) NULL,
        Id_Perfil           INT           NOT NULL
                            CONSTRAINT FK_APP_Usuario_Perfil
                            FOREIGN KEY REFERENCES dbo.APP_Perfil (Id_Perfil),
        Nom_Abvd_Unidade    VARCHAR(3)    NULL,
        Flg_Situacao        BIT           NOT NULL CONSTRAINT DF_APP_Usuario_Situacao DEFAULT 0,
        Dt_Inclusao         DATETIME2(3)  NOT NULL,
        Dt_Alteracao        DATETIME2(3)  NULL
    );
GO
```

- **Uma coluna de identidade** para "quem é você": a que o app usa em `LookUp(... = Lower(User().Email))`,
  a que a procedure de resolução usa e a que o flow envia **têm de ser a mesma**. Divergência (e-mail
  no app, UPN na procedure) faz o app achar o usuário e o flow não: toda escrita volta "sem
  permissão". `User().Email` nem sempre é igual ao UPN; teste com dois usuários reais antes do
  primeiro deploy (prova em `deploy-e-dba.md`).
- **Escopo de unidade** como atributo do perfil (`Flg_TodasUnidades`) só expressa "tudo ou uma". Usuário
  com 3 das dezenas de unidades **não é representável**: registre como limite ou modele uma tabela de vínculo
  (ver `escopo-por-unidade.md`).
- Perfil inativo ou usuário inativo **não autoriza nada**, inclusive a si mesmo; as duas condições
  entram no `WHERE` da resolução.

## 7. Índices únicos filtrados e FKs

```sql
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = N'UX_APP_Usuario_Email'
                 AND object_id = OBJECT_ID(N'dbo.APP_Usuario'))
    CREATE UNIQUE NONCLUSTERED INDEX UX_APP_Usuario_Email
        ON dbo.APP_Usuario (Email_Usuario)
        WHERE Email_Usuario IS NOT NULL AND Email_Usuario <> '';
GO
```

- O filtro exclui `NULL` e vazio **de propósito** (usuário ainda não provisionado), o que também
  significa que `NULL` e `''` **não são protegidos**: a guarda de cadastro da procedure precisa tratar
  os dois explicitamente (decisão de produto: usuário sem e-mail pode existir?).
- **Normalize antes de criar o índice** (`LOWER(LTRIM(RTRIM()))`), senão ele reprova; confira duplicata
  antes (`GROUP BY ... HAVING COUNT(*) > 1`).
- O índice único sustenta o `UPDLOCK, HOLDLOCK` das guardas (`padrao-procedure.md` §8).
- Sem o índice, `LookUp` por e-mail devolve "a linha que o SQL entregar", sem `ORDER BY`: perfil e
  unidade viram sorteio por sessão.

## 8. Vocabulários

Domínio fechado de texto (`Des_Status`, `Tp_Evento`) é `CHECK` **ou** tabela de domínio, escolha do
DBA; o que não pode é vocabulário só no app. Registre os valores canônicos no contrato e confira a
carga: acento, caixa e espaço divergentes (`ANDAMENTO` × `Em Andamento`) fazem filtro de tela não
casar e contador contar zero. Normalize no **script de carga**, não na procedure: normalizar na
procedure esconde o problema e a tela, que lê a tabela direto, continua quebrada.

Valor gravado fora do vocabulário (ex.: um estado "arquivado" que não existe no domínio dos filtros) é
decisão de produto: ou entra no vocabulário e no filtro, ou a operação grava outro valor.

## 9. Grafia não se conserta

O conector SQL é **sensível a maiúsculas** no nome de coluna e tabela. Se o ambiente tem
`Nom_Abvd_UNidade` numa tabela e `Nom_Abvd_UnidadeOrig` noutra, **não uniformize**: telas e flows já
estão escritos contra esses nomes e errar não acusa na edição, falha em runtime, calado. Registre a
grafia real por tabela no `NOMES-AS-BUILT` e deixe o lint de nomes do projeto conferir.
`[verificado: projeto de referência]`

## 10. O que verificar no que já existe

Antes de escrever a primeira procedure, rode e cole no `NOMES-AS-BUILT` (N1, N3):

```sql
-- colunas, tipo, tamanho, nulidade e collation de cada tabela do projeto
SELECT t.name AS Tabela, c.name AS Coluna, ty.name AS Tipo, c.max_length, c.is_nullable,
       c.is_computed, c.collation_name
  FROM sys.tables AS t
  JOIN sys.columns AS c  ON c.object_id = t.object_id
  JOIN sys.types   AS ty ON ty.user_type_id = c.user_type_id
 WHERE t.name LIKE 'APP[_]%'
 ORDER BY t.name, c.column_id;

-- tabelas sem PK (abrem somente leitura no conector)
SELECT t.name AS Tabela_Sem_PK
  FROM sys.tables AS t
 WHERE NOT EXISTS (SELECT 1 FROM sys.key_constraints AS k
                    WHERE k.parent_object_id = t.object_id AND k.type = 'PK')
   AND t.name LIKE 'APP[_]%';
```

Antes de afirmar que uma coluna **não existe**, abra o esquema completo da tabela; nunca um extrato
filtrado (N3).

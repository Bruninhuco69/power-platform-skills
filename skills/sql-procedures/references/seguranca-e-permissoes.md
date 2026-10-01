# Segurança e permissões

O que o banco realmente garante quando o app e o flow falam com ele por uma **conta de serviço
compartilhada**, o que a procedure autoriza (e o que não), e quando discordar do padrão "a procedure
não autoriza" (A2). A autorização **dentro do flow** (gate por ação, escopo) é da skill
`power-automate`.

## Sumário

1. [Modelo de ameaça](#1-modelo-de-ameaça)
2. [A conta de serviço: GRANT EXECUTE e nada mais](#2-a-conta-de-serviço-grant-execute-e-nada-mais)
3. [O que a procedure autoriza](#3-o-que-a-procedure-autoriza)
4. [Quando discordar de "a procedure não autoriza"](#4-quando-discordar-de-a-procedure-não-autoriza)
5. [Limite que nenhum código fecha: o chamador por parâmetro](#5-limite-que-nenhum-código-fecha-o-chamador-por-parâmetro)
6. [Injeção e vazamento por erro](#6-injeção-e-vazamento-por-erro)
7. [Consultas de verificação](#7-consultas-de-verificação)

---

## 1. Modelo de ameaça

O conector SQL conecta como **uma** conta, não como o usuário final. Para o banco, todo chamador é a
mesma pessoa. Quem pode fazer a conta executar uma procedure com parâmetros à escolha?

- qualquer pessoa que edite o **app** ou o **flow** que usa a connection reference, ou crie outro
  com ela;
- qualquer outro consumidor da mesma conta (ETL, outro app, script de suporte).

Consequências: a regra "o escopo na tela é UX, não controle de acesso" (A3) vale **também** para o
próprio flow: ele é a barreira **contra o usuário final**, não contra quem edita o flow ou usa a conta.
O banco só consegue impor o que está **estruturalmente** na conta e nos objetos.

## 2. A conta de serviço: GRANT EXECUTE e nada mais

O que fecha por construção o caminho do `Patch` direto na tabela:

```sql
-- Conta de servico do conector. Troque pelo nome real, lido do ambiente.
GRANT EXECUTE ON SCHEMA::dbo TO [<conta_do_conector>];
GO

-- E NENHUM DML nas tabelas. Se ja houver grant, revogue.
REVOKE INSERT, UPDATE, DELETE ON dbo.APP_Pedido        FROM [<conta_do_conector>];
REVOKE INSERT, UPDATE, DELETE ON dbo.APP_PedidoTrilha  FROM [<conta_do_conector>];
GO

-- SELECT continua necessario onde o app le a tabela direto (galeria, filtros).
GRANT SELECT ON dbo.APP_Pedido TO [<conta_do_conector>];
GO
```

- **Sem DML na conta, o `Patch` não volta**, nem por esquecimento nem por um app novo na mesma
  conexão. O caminho fecha por construção, não por disciplina.
- `GRANT EXECUTE ON SCHEMA::dbo` cobre todo objeto **presente e futuro** do schema. Cômodo, mas toda
  procedure auxiliar que nascer ali já é chamável. Para projeto novo, prefira **um schema só das
  procedures expostas** (`CREATE SCHEMA app` e `GRANT EXECUTE ON SCHEMA::app`), ou `GRANT EXECUTE` por
  procedure. O lint exige schema qualificado, não `dbo` em particular.
- **Uma conta por app e por ambiente.** Conta compartilhada entre apps é a pior situação para
  rastrear e para revogar.
- Tabela em **outro banco** (ex.: cadastro corporativo): o encadeamento de propriedade (*ownership
  chaining*) não atravessa bancos por padrão; a procedure precisa de permissão explícita, e a
  collation diferente derruba o `JOIN` (erro 468). Confirme onde a tabela vive antes de escrever a
  procedure que a lê. `[não verificado: confirme no seu ambiente]`
- O que este `GRANT` **não** fecha: o **conteúdo** da escrita. Com validação e autorização no flow,
  quem chama a procedure grava o que quiser. Declare isso no contrato; é a perda maior da variante
  declarativa e é o que o §4 trata.

## 3. O que a procedure autoriza

| Postura | Onde mora a regra | O que o banco barra |
|---|---|---|
| **A. O flow autoriza** (padrão do kit, A2) | flow | só a escrita direta em tabela. Qualquer um com a conta chama a procedure |
| **B. O flow autoriza + bloco defensivo na procedure** | flow **e** procedure | chamador desconhecido/inativo/sem a flag da ação, **desde que** o id informado seja real |
| **C. A procedure autoriza** (clássica) | procedure (e o flow repete para dar a frase) | idem B, com recusa também de negócio no banco |

A, B e C **não** impedem quem mente o `@Id_UsuarioChamador` (§5). B e C reduzem erro, regressão de
flow e uso indevido por quem não conhece a regra. Código da postura B/C: `padrao-procedure.md` §7.

## 4. Quando discordar de "a procedure não autoriza"

O padrão do kit é a postura A porque concentra a regra num lugar editável sem DBA e o banco tende a
congelar. **Discorde** (e registre no ADR do projeto) quando **qualquer** destas for verdade:

| Sinal | Por quê |
|---|---|
| A conexão/conta é usada por **mais de um app ou flow**, ou por gente que não é a equipe do flow | a regra no flow protege só um dos caminhos |
| A operação é **irreversível ou financeira** (encerramento, estorno, pagamento) | uma recusa tardia no banco vale mais que a mensagem bonita |
| A auditoria exige **autoria confiável** | a trilha por parâmetro não prova quem; só resolver o chamador na procedure (ainda assim com o limite do §5) melhora |
| O DBA é dono da lógica e recusa procedure "burra" | o congelamento tem um custo: mudar regra vira pedido ao DBA |
| A regra tem de valer mesmo se o flow for **trocado** ou regerado | o flow é substituível; o banco costuma ser o que dura |

O que **não** vale como argumento: "fica mais seguro" sem dizer contra quem. Diga o ator (usuário
final, editor do flow, outro consumidor da conta) e o que o bloco impede.

Custos da postura B/C, para decidir com os olhos abertos: a regra passa a existir em **duas cópias**
(banco e flow) que podem divergir; a procedure lê a tabela de perfil (dependência nova entre
objetos); mudança de regra vira mudança de procedure (pedido ao DBA se o banco congelou); mais
códigos no vocabulário (`SEM_PERMISSAO`) e uma recusa a mais para o flow traduzir.

Uma combinação de custo baixo: **postura A** + `GRANT EXECUTE` mínimo + um **bloco defensivo só nas
operações irreversíveis** (a flag da ação, lida do perfil, e a situação do chamador). O resto fica
declarativo.

## 5. Limite que nenhum código fecha: o chamador por parâmetro

`@Id_UsuarioChamador` chega **por parâmetro**. Uma regra do tipo "o administrador não se
auto-inativa", escrita como `Id_Usuario <> @Id_UsuarioChamador`, compara a PK real contra um valor
que **o chamador escolhe**: passar outro id desarma a regra. Não fecha em SQL sem devolver a
resolução de identidade para dentro da procedure, o que contraria o desenho.
`[verificado: projeto de referência]`

Consequências para o contrato:

- A **trilha prova o quê e quando; não prova quem.** Escreva isso no contrato e na documentação de
  auditoria.
- Regra de domínio no banco é **rede** (impede o erro honesto); a fonte da mensagem e o controle
  contra o usuário final continuam no flow.
- Mitigações que reduzem o risco sem mudar o desenho: conta por app; `GRANT` por procedure; restringir
  quem edita o flow (ALM, solução gerenciada); log de execução do flow com chamador e parâmetros
  (F4); revisão periódica de quem tem acesso à connection reference.
- Um token assinado entre flow e procedure ou `EXECUTE AS` por usuário **não** são soluções
  prontas com conta compartilhada; trate como projeto próprio `[não verificado]`.

**Uma coluna de identidade, normalizada.** A coluna que o app usa em `LookUp(... = Lower(User().Email))`, a
que a procedure de resolução usa e a que o flow envia têm de ser a **mesma**, normalizada
(`LOWER(LTRIM(RTRIM()))`) na carga. Divergência: o app acha o usuário, o flow não, e toda escrita volta
"sem permissão". Teste de um minuto com dois usuários reais antes do primeiro deploy
(`deploy-e-dba.md`).

## 6. Injeção e vazamento por erro

- **SQL dinâmico por concatenação** é injeção em potencial: o `lint-procedure.py` acusa `P009`
  (`EXEC (@sql)` e `sp_executesql` com `+`). Use `sp_executesql` com parâmetros e `QUOTENAME` para nome
  de objeto. Metadado interno controlado (script de carga) pode ser dispensado com `-- lint-ok P009`
  **e uma frase dizendo por quê**.
- Parâmetro de procedure nunca vira nome de coluna ou tabela sem lista branca.
- `ERROR_MESSAGE()` no retorno vaza esquema ao usuário: deixe o erro subir (`THROW`) e o flow
  monte a frase genérica. O `Catch` do flow é obrigatório.
- Cadeia de conexão, senha e usuário **não** entram no repositório nem no `CONFIG` literal do flow
  (variável de ambiente + connection reference, F5).
- Artefatos de migração contêm dado real (nomes, e-mails): ficam fora do repositório, com
  `.gitignore`, e são apagados depois da carga (`migracao-dados.md`).
- Escopo mínimo para operação de carga: `db_owner` **temporário**, dedicado, no banco, nunca para a
  conta do conector.

## 7. Consultas de verificação

As consultas (a), (a2), (b) e (c) **voltam vazias** quando está certo; a (d) é conferência por leitura.
Rode depois de cada onda de deploy e guarde a saída.

```sql
-- (a) a conta do conector nao tem DML
SELECT p.permission_name, p.class_desc, p.major_id,
       CASE WHEN p.class_desc = 'OBJECT_OR_COLUMN' THEN OBJECT_NAME(p.major_id) END AS Objeto
  FROM sys.database_permissions AS p
  JOIN sys.database_principals  AS d ON d.principal_id = p.grantee_principal_id
 WHERE d.name = '<conta_do_conector>'
   AND p.permission_name IN ('INSERT', 'UPDATE', 'DELETE');

-- (a2) a conta do conector nao esta em papel com DML (a consulta (a) so le permissao direta)
SELECT r.name AS Papel, m.name AS Membro
  FROM sys.database_role_members AS rm
  JOIN sys.database_principals   AS r ON r.principal_id = rm.role_principal_id
  JOIN sys.database_principals   AS m ON m.principal_id = rm.member_principal_id
 WHERE m.name = '<conta_do_conector>'
   AND r.name IN ('db_datawriter', 'db_owner', 'db_ddladmin');

-- (b) SET NOCOUNT ON em toda procedure e todo trigger do projeto
SELECT o.name AS Objeto_Sem_NoCount, o.type_desc
  FROM sys.sql_modules AS m
  JOIN sys.objects     AS o ON o.object_id = m.object_id
 WHERE o.type IN ('P', 'TR')
   AND o.name LIKE '%APP[_]%'
   AND m.definition NOT LIKE '%SET NOCOUNT ON%';

-- (c) procedures de escrita com SQL dinamico (revisar uma a uma)
SELECT o.name AS Procedure_Com_Sql_Dinamico
  FROM sys.sql_modules AS m
  JOIN sys.objects     AS o ON o.object_id = m.object_id
 WHERE o.type = 'P'
   AND o.name LIKE '%APP[_]%'
   AND (m.definition LIKE '%sp[_]executesql%' OR m.definition LIKE '%EXEC (@%' OR m.definition LIKE '%EXEC(@%');

-- (d) quem tem EXECUTE no schema (confira que so a conta do app esta na lista)
SELECT d.name AS Principal, p.permission_name, p.state_desc
  FROM sys.database_permissions AS p
  JOIN sys.database_principals  AS d ON d.principal_id = p.grantee_principal_id
 WHERE p.class_desc = 'SCHEMA'
   AND p.permission_name = 'EXECUTE';
```

O que o `lint-procedure.py` cobre **no repositório** (antes do deploy) e o que só estas consultas
cobrem **no banco** (depois): o lint não vê o que o DBA alterou à mão em produção; a consulta (b)
vê. Use as duas.

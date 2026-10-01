# Padrão de procedure

Como escrever a procedure que o flow chama. Decisões que valem para todo projeto estão em
`power-platform/references/decisoes-padrao.md` (A1, A2, C1, C2, B1); aqui está o **como**: envelope,
retorno, as duas variantes e quando usar cada uma, concorrência e o código completo.

## Sumário

1. [Quando existe procedure](#1-quando-existe-procedure)
2. [Envelope](#2-envelope)
3. [Retorno de uma linha](#3-retorno-de-uma-linha)
4. [Vocabulário fechado de códigos](#4-vocabulário-fechado-de-códigos)
5. [Declarativa × clássica: o que escolher](#5-declarativa--clássica-o-que-escolher)
6. [Variante declarativa](#6-variante-declarativa)
7. [Variante clássica: TRY/CATCH + THROW](#7-variante-clássica-trycatch--throw)
8. [Duplicidade: UPDLOCK e HOLDLOCK](#8-duplicidade-updlock-e-holdlock)
9. [Variantes por tipo de operação](#9-variantes-por-tipo-de-operação)
10. [Parâmetros](#10-parâmetros)
11. [OUTPUT, relógio e trilha](#11-output-relógio-e-trilha)
12. [Concorrência, retry e idempotência](#12-concorrência-retry-e-idempotência)
13. [Checklist de revisão](#13-checklist-de-revisão)

---

## 1. Quando existe procedure

| Situação | Caminho |
|---|---|
| Escrita com regra de negócio, mais de um efeito (linha + trilha) ou que precisa ser atômica | **procedure**, chamada pelo flow (A1) |
| Leitura para galeria, filtro, lookup | tabela/view direto no app, se o filtro delega (ver `colunas-calculadas-delegacao.md`) |
| Leitura com muitos filtros, escopo ou contagem exata | função inline + procedure de leitura (§9) |
| Escrita simples, uma tabela, sem regra | ainda passa pelo flow; a procedure pode ser de um statement |

A tela **não** faz `Patch` em tabela com regra. Para isso valer no banco (e não só por disciplina),
a conta do conector não pode ter DML: ver `seguranca-e-permissoes.md`.

## 2. Envelope

Toda procedure de escrita começa assim, nesta ordem:

```sql
CREATE OR ALTER PROCEDURE dbo.usp_APP_Entidade_Acao
    @Id_Entidade INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    -- corpo
END
GO
```

| Elemento | Regra | Fonte |
|---|---|---|
| `SET NOCOUNT ON` | primeira linha, em **toda** procedure e em **todo trigger** | `[não verificado: o efeito exato no conector não foi medido]`. Semântica do comando: https://learn.microsoft.com/en-us/sql/t-sql/statements/set-nocount-transact-sql |
| `SET XACT_ABORT ON` | procedure que grava: erro de runtime encerra e desfaz a transação inteira | https://learn.microsoft.com/en-us/sql/t-sql/statements/set-xact-abort-transact-sql |
| `BEGIN TRANSACTION` … `COMMIT` | só onde há mais de um statement de escrita; um statement único já é atômico | idem |
| Schema | sempre `dbo.` na criação e em toda referência | evita resolução por usuário e reúso de plano ruim |
| Sem `sp_` | prefixo reservado do produto; o SQL Server procura em `master` primeiro | documentação do produto; o default do lint aceita `SP_` porque o nome real vem do ambiente; `sp_` minúsculo é acusado (P005, aviso: o padrão é *case-sensitive*) |

**Nome vem do ambiente.** O padrão documentado (`usp_<SIGLA>_<Entidade>_<Acao>`) divergiu do nome
real criado pelo DBA (`SP_<SIGLA>_<VERBO>_<OBJETO>`) no projeto de referência. Antes de escrever uma
chamada de flow, leia o nome em `sys.procedures` e registre no `NOMES-AS-BUILT` (N1). O lint aceita
`usp_` e `SP_` por padrão; mude em `power-platform.config.json` (`padrao_nome_procedure`) ou
`--padrao-nome`.

Uma ação de negócio = uma procedure. Nada de `@Acao` roteando um `IF`: parâmetro que o ramo ignora
é defeito disfarçado. O `Switch` fica no flow.

## 3. Retorno de uma linha

Procedure de escrita devolve **um result set, de uma linha, com quatro colunas** (C1):

| Coluna | Conteúdo |
|---|---|
| `status` | `success` \| `warning` \| `error` |
| `description` | **código** de resultado, ASCII sem acento, vocabulário fechado (C2) |
| `id` | id do registro como **texto**; `N''` quando não gravou |
| `url` | `N''` (reservada; o flow preenche se precisar) |

Regras duras:

1. As quatro colunas sempre saem, **nunca `NULL`** (`N''`, não `NULL`): a tela lê `ret.url` num flow
   que não usa url e tem de receber `""`.
2. `id` é `NVARCHAR` via `CONVERT(NVARCHAR(20), ...)`: o contrato do flow é texto e a conversão
   implícita no flow é onde o `"1.234"` de locale pt-BR volta.
3. **Um único `SELECT` de dado no fim.** `SELECT` de depuração no meio vira result set.
4. Todo `OUTPUT` de DML usa `INTO` (§11).
5. Só o **primeiro** result set chega ao flow; com gateway, `OUTPUT` parameters não voltam, e o
   schema do result set precisa de nomes de coluna únicos e não vazios.
   Fonte: https://learn.microsoft.com/en-us/connectors/sql/ (limitações do conector).
6. `warning` não é enfeite: gravou e há algo que o usuário precisa saber (ex.: cadastrou como
   pendente por duplicidade). `error` fica para a recusa que **só o lock** sabe emitir.

### Retorno que garante uma linha por construção

O truque da variante declarativa: uma tabela derivada com **uma linha por desfecho possível** e um
`WHERE` que casa exatamente uma, comparando com a cardinalidade do sink de `OUTPUT`:

```sql
SELECT TOP (1)
       v.status       AS status,
       v.description  AS description,
       v.id           AS id,
       N''            AS url
  FROM (VALUES (1, 'success', N'ALTERADO',      CONVERT(NVARCHAR(20), @Id_Entidade)),
               (0, 'warning', N'NAO_APLICADO', N'')
       ) AS v (Gravou, status, description, id)
 WHERE v.Gravou = (SELECT COUNT(*) FROM @Alterado);
```

Quando o `id` vem de um `INSERT` (não existe antes de gravar), use `OUTER APPLY` sobre o sink e
`ISNULL(w.id, N'')`; `CROSS APPLY` zeraria o result set no ramo de recusa. Exemplo completo em
`assets/procedure-escrita-molde.sql` (`usp_APP_Pedido_Criar`).

## 4. Vocabulário fechado de códigos

O código é contrato com o flow. Regras:

- **Fechado:** código que não está na tabela não existe. O flow tem `default` que responde `error`
  **nomeando** o código recebido (nunca repassa código cru ao usuário).
- ASCII sem acento, `NVARCHAR(40)`, `UPPER_SNAKE`.
- **A procedure só devolve o que a transação sabe e o flow não pode saber antes.** Validação de
  formato, autorização e domínio nunca chegam à procedure (variante declarativa) ou viram códigos
  próprios (clássica).
- Um código por desfecho distinto **que o usuário precisa distinguir**. `NAO_APLICADO` (zero linha
  casou o predicado) é ambíguo por natureza: "mudou de estado", "não existe", "pré-condição nunca
  valeu". Quem precisa da frase certa relê o registro **no flow, antes** de chamar.

Tabela-modelo (mantenha uma por projeto, no contrato da procedure):

| status | description | Significado no banco | Quem escreve a frase |
|---|---|---|---|
| success | `CRIADA` | linha criada | flow |
| error | `PROTOCOLO_DUPLICADO` | outra linha viva tem o mesmo protocolo (só o lock sabe) | flow |
| success | `ENCERRADO` | estado mudou de `aberto` para `encerrado` | flow |
| warning | `NAO_APLICADO` | predicado de estado não casou: 0 linhas | flow relê e explica |
| success | `CONTAGEM_OK` | `id` = total, sem separador de milhar | sem frase: alimenta decisão do flow |

A tradução (`Switch` com `default`) é do flow: ver `power-automate` e `contrato-proc-flow.md`.

## 5. Declarativa × clássica: o que escolher

Duas formas legítimas de escrever a mesma procedure.

| | **Declarativa** | **Clássica** |
|---|---|---|
| Ideia | a procedure **não decide**: grava o lote e devolve um código | a procedure **valida, autoriza e decide**, com `IF` e `TRY/CATCH` |
| Regra de negócio | no flow, em uma cópia só | no banco (e, em geral, repetida no flow para dar mensagem) |
| `IF`, `WHILE`, `TRY/CATCH` | nenhum | sim |
| Ramificação | predicado de estado no `WHERE` + fonte vazia no `INSERT` seguinte | `IF` explícito |
| Erro em runtime | `XACT_ABORT` desfaz; **a ação do conector falha** e o flow trata no `Catch` | `CATCH` desfaz e relança com `THROW`; a ação do conector falha do mesmo jeito |
| Recusa de negócio | `warning` + código | `error`/`warning` + código, mais granular |
| Tamanho | muito menos linhas (a regra sai do banco) | maior, com cópias de regra |
| Quem edita a regra | quem mantém o flow (sem DBA) | quem tem acesso ao banco (DBA, se o banco estiver congelado) |

**Recomendação.** Comece pela **declarativa**: é o padrão do kit (A2: o flow decide, a procedure
executa) e a única que sobrevive ao congelamento do banco, porque a regra muda no flow. Troque para a
**clássica** (ou acrescente o bloco de autorização defensiva) quando **qualquer** destas for
verdadeira:

1. A procedure pode ser chamada por algo que não é o seu flow (outra app, outro flow, ETL, alguém com
   acesso à connection reference). Ver `seguranca-e-permissoes.md`.
2. A operação é irreversível ou financeira e uma recusa tardia, no banco, vale mais que uma mensagem
   bonita no flow.
3. A regra tem de valer mesmo se o flow for trocado.
4. O DBA é dono da lógica e não aceita uma procedure "burra".
5. Você precisa de mensagens de erro numeradas do próprio banco (`THROW` com número).

Divergir de A2 exige ADR no projeto (acrescentar o bloco de autorização defensiva já conta como
divergência): registre qual regra passa ao banco e o risco residual que continua.

### O custo da declarativa, sem suavizar

Um projeto de referência registrou uma dezena de perdas ao adotá-la. As que mais machucam:

| Perda | Consequência | Mitigação |
|---|---|---|
| A procedure deixa de ser o último ponto de controle | quem tem a connection reference grava o que quiser | `GRANT EXECUTE` mínimo, conta por app; bloco defensivo (§7, `seguranca-e-permissoes.md`) |
| `@Id_UsuarioChamador` vem por parâmetro | a trilha deixa de provar **quem**; continua provando o quê e quando | declarar no contrato; resolver o chamador no flow, por PK |
| Sem validação no banco | o flow que não normaliza grava lixo calado | obrigações do flow no contrato (`contrato-proc-flow.md`) |
| Erro de infraestrutura não volta como código | só o texto do conector | `Catch` do flow é **obrigatório** |
| `NAO_APLICADO` ambíguo | frase genérica | flow relê antes de chamar |
| A transação abre mesmo na recusa | uma transação a mais, commit vazio | custo aceito; sem registro parcial |

Detalhe e evidência: `licoes-de-campo.md`.

## 6. Variante declarativa

Sete regras, todas codificadas em `assets/procedure-escrita-molde.sql`:

1. `SET NOCOUNT ON` na primeira linha.
2. `SET XACT_ABORT ON` no lugar do `TRY/CATCH` (erro sobe e desfaz).
3. `OUTPUT ... INTO @sink`, sempre com `INTO` (§11); `DELETED.<col>` alimenta o valor anterior da
   trilha, lido atomicamente pelo próprio `UPDATE`.
4. **Predicado de estado no `WHERE` faz o papel do `IF`:** `UPDATE ... WHERE <PK> AND <estado
   esperado>` é concorrência otimista; zero linha = pré-condição falhou.
5. **Cardinalidade da fonte faz o papel do `IF`** nas escritas seguintes: `INSERT ... SELECT FROM
   @sink`; sink vazio, nenhuma linha.
6. **Sem variável escalar de trabalho.** O único `DECLARE` é o sink tipado do `OUTPUT`: ele guarda o
   resultado do statement anterior, não é estado.
7. **Retorno** por `SELECT TOP (1)` sobre `VALUES` com `WHERE` de casamento exato (§3).

O que fica de fora do corpo, de propósito: `IF`, `WHILE`, `TRY/CATCH`, cursor, `CASE` de regra,
`SCOPE_IDENTITY()`, `THROW`/`RAISERROR`, `ROLLBACK` explícito, e-mail, leitura de perfil.

Literais de estado (`N'aberto'`) **ficam no corpo**, nunca em parâmetro: como parâmetro, o chamador
desliga a trava mandando outra string. O estado **gravado** é parâmetro (já validado pelo flow).

`Dt_Inclusao` e outras datas de auditoria vêm de `SYSUTCDATETIME()` dentro da procedure, **nunca por
parâmetro**; `Dt_Alteracao` vem de trigger (`modelo-de-dados.md`).

## 7. Variante clássica: TRY/CATCH + THROW

Use quando a procedure precisa decidir (§5). Cada caminho devolve exatamente **uma** linha; o erro
inesperado relança com `THROW` e o flow trata no `Catch`. `THROW` respeita `XACT_ABORT`; `RAISERROR`
não, e a documentação manda usar `THROW` em código novo
(https://learn.microsoft.com/en-us/sql/t-sql/statements/set-xact-abort-transact-sql).

Depende de `dbo.APP_Usuario`, `dbo.APP_Perfil` e das tabelas do molde de escrita
(`modelo-de-dados.md` §6 traz o DDL de usuário e perfil).

```sql
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Cancelar
    @Id_Pedido      INT,
    @Des_Motivo          NVARCHAR(200),
    @Id_UsuarioChamador  INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @Status_Antes NVARCHAR(20);
    DECLARE @Agora        DATETIME2(3) = SYSUTCDATETIME();

    -- 1) autorizacao defensiva: a flag DA ACAO, lida do perfil do chamador.
    --    Limite: @Id_UsuarioChamador chega por parametro; isto barra erro e uso
    --    indevido, nao um chamador que minta o id (ver seguranca-e-permissoes.md).
    IF NOT EXISTS (SELECT 1
                     FROM dbo.APP_Usuario AS u
                     JOIN dbo.APP_Perfil  AS p ON p.Id_Perfil = u.Id_Perfil
                    WHERE u.Id_Usuario   = @Id_UsuarioChamador
                      AND u.Flg_Situacao = 1
                      AND p.Flg_Situacao = 1
                      AND p.Flg_Cancelar = 1)
    BEGIN
        SELECT 'error' AS status, N'SEM_PERMISSAO' AS description, N'' AS id, N'' AS url;
        RETURN;
    END;

    -- 2) validacao de entrada (o flow tambem valida, para dar a frase)
    IF @Des_Motivo IS NULL OR LEN(LTRIM(RTRIM(@Des_Motivo))) < 10
    BEGIN
        SELECT 'error' AS status, N'MOTIVO_INVALIDO' AS description, N'' AS id, N'' AS url;
        RETURN;
    END;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- leitura que decide a escrita: UPDLOCK + HOLDLOCK ate o COMMIT (secao 8)
        SELECT @Status_Antes = s.Des_Status
          FROM dbo.APP_Pedido AS s WITH (UPDLOCK, HOLDLOCK)
         WHERE s.Id_Pedido = @Id_Pedido
           AND s.Flg_Situacao   = 1;

        IF @Status_Antes IS NULL OR @Status_Antes <> N'aberto'
        BEGIN
            ROLLBACK TRANSACTION;
            SELECT 'warning' AS status, N'NAO_APLICADO' AS description, N'' AS id, N'' AS url;
            RETURN;
        END;

        UPDATE dbo.APP_Pedido
           SET Des_Status = N'cancelado'
         WHERE Id_Pedido = @Id_Pedido;

        INSERT dbo.APP_PedidoTrilha
              (Id_Pedido, Tp_Evento, Des_Resumo, Des_ValorAnterior, Des_ValorNovo,
               Id_UsuarioChamador, Dt_Inclusao)
        VALUES (@Id_Pedido, N'CANCELAMENTO', @Des_Motivo, @Status_Antes, N'cancelado',
                @Id_UsuarioChamador, @Agora);

        COMMIT TRANSACTION;

        SELECT 'success' AS status, N'CANCELADO' AS description,
               CONVERT(NVARCHAR(20), @Id_Pedido) AS id, N'' AS url;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        THROW;   -- o flow trata no Catch; nao devolva ERROR_MESSAGE() no campo description
    END CATCH;
END
GO
```

Cuidados da clássica:

- **Toda saída cedo (`RETURN`) dentro da transação faz `ROLLBACK` antes.** O `P003` do lint pega
  `BEGIN TRAN` sem `COMMIT`, não o `RETURN` sem `ROLLBACK`: revise.
- Não devolva `ERROR_MESSAGE()` no `description`: vaza detalhe de esquema ao usuário e quebra o
  vocabulário fechado. Deixe o erro subir (`THROW`) e o flow monte a mensagem genérica.
- Cada ramo devolve uma linha; o `CATCH` não devolve result set.
- A validação que o banco repete **não substitui** a do flow: o flow ainda precisa da frase.

## 8. Duplicidade: UPDLOCK e HOLDLOCK

Dois casos, comportamentos diferentes:

| Padrão | Janela entre checar e gravar? | Precisa de hint? |
|---|---|---|
| `UPDATE ... WHERE <estado esperado>` (predicado) | não: o `UPDATE` bloqueia e reavalia o `WHERE` contra o dado confirmado | **não** |
| `SELECT` e depois decide e grava | **sim** | **sim:** `WITH (UPDLOCK, HOLDLOCK)` no `SELECT`, até o `COMMIT` |
| `INSERT ... SELECT ... WHERE NOT EXISTS (... UPDLOCK, HOLDLOCK)` | não: guarda e gravação são **um** statement | o hint fica dentro do `NOT EXISTS` |

`UPDLOCK` evita o deadlock de duas leituras compartilhadas querendo escalar; `HOLDLOCK` segura a
faixa até o `COMMIT`. Sem os dois, duas sessões passam pela checagem e gravam a duplicata que a regra
existe para impedir.

Requisitos:

- **Índice de apoio** na coluna da checagem (`UNIQUE` filtrado serve). Sem ele, `HOLDLOCK` escala
  para lock de faixa/tabela e serializa todo cadastro.
- Hint em **poucos lugares conhecidos**; liste-os no contrato (um projeto de referência tinha
  um punhado e verificava por `grep`).
- Troca cruzada pode gerar deadlock (erro 1205): duas edições que trocam o valor de duas linhas.
  O flow trata 1205 como transitório e reexecuta (§12).
- Sob `READ_COMMITTED_SNAPSHOT`, `SELECT` sem hint não protege; o `UPDATE`-predicado continua
  correto. Confirme a configuração do banco (`deploy-e-dba.md`, provas).

## 9. Variantes por tipo de operação

| Tipo | Onde está o código completo | Pontos de atenção |
|---|---|---|
| **UPDATE de estado** + trilha | `assets/procedure-escrita-molde.sql` (`Encerrar`) | predicado de estado no `WHERE`; `OUTPUT ... INTO`; retorno por `VALUES` |
| **INSERT** com guarda de duplicidade | `assets/procedure-escrita-molde.sql` (`Criar`) | guarda dentro do `INSERT ... SELECT`; `OUTER APPLY` no retorno; índice `UNIQUE` filtrado |
| **Leitura** (função + `@Filtros` JSON + escopo) | `assets/funcao-leitura-molde.sql` | função inline, `OPTION (RECOMPILE)`, escopo em `AND` com o filtro, `COUNT_BIG` para contar |
| **Resolução do chamador** (read) | abaixo | **zero linha = negar**; filtra usuário **e** perfil ativos |
| **Parâmetro em JSON** (N linhas de trilha) | `contrato-proc-flow.md` §5 | `OPENJSON ... WITH`; truncamento silencioso; array vazio é válido |

### Resolução do chamador: zero linha é negar

O flow chama esta procedure **uma vez**, no tronco, com o e-mail do contexto de execução (nunca do
parâmetro do gatilho), testa `empty(...ResultSets/Table1)` e nega antes de qualquer escrita. Devolve
as flags de permissão; quem compara é o flow, por ação.

```sql
CREATE OR ALTER PROCEDURE dbo.usp_APP_Chamador_Obter
    @Email_Chamador NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    -- unica procedure que recebe e-mail. Leitura pura, zero escrita.
    -- Desconhecido, inativo ou perfil inativo: ZERO linha.
    -- A coluna e o parametro tem de usar a MESMA normalizacao (LOWER/TRIM) na carga e aqui.
    SELECT u.Id_Usuario,
           u.Nom_Usuario,
           LTRIM(RTRIM(u.Nom_Abvd_Unidade)) AS Nom_Abvd_Unidade,
           u.Id_Perfil,
           p.Des_Perfil,
           p.Flg_Consultar,
           p.Flg_Encerrar,
           p.Flg_Cancelar,
           p.Flg_TodasUnidades,
           p.Flg_Adm
      FROM dbo.APP_Usuario AS u
      JOIN dbo.APP_Perfil  AS p ON p.Id_Perfil = u.Id_Perfil
     WHERE u.Email_Usuario = LOWER(LTRIM(RTRIM(@Email_Chamador)))
       AND u.Flg_Situacao  = 1
       AND p.Flg_Situacao  = 1;
END
GO
```

Três requisitos que esta procedure **não** consegue garantir sozinha:

1. `UNIQUE` filtrado em `Email_Usuario`: com duplicata ela devolve duas linhas e o flow lê a `[0]`
   (perfil e unidade viram sorteio).
2. Flags `BIT NOT NULL DEFAULT 0`: um `NULL` em flag vira "negar tudo" (via `p.Flg_Situacao = 1`)
   ou, no flow, valor nulo trafegando até uma condição.
3. Coluna e parâmetro normalizados do mesmo jeito: espaço **à esquerda** na coluna não é protegido
   por collation alguma; o `LTRIM` só protege o parâmetro. Dado sujo nega o sistema inteiro daquela
   pessoa, indistinguível de "não existe". Prove com os dois usuários reais (`deploy-e-dba.md`).

## 10. Parâmetros

A assinatura de uma procedure de escrita tem **cinco classes**, e nada mais:

| Classe | O que é |
|---|---|
| (a) | PK do alvo, quando é `UPDATE` |
| (b) | cada valor de coluna que a procedure grava, **já normalizado, validado e derivado pelo flow** |
| (c) | `@Id_UsuarioChamador INT`, resolvido pelo flow por PK |
| (d) | valores das linhas de trilha daquela operação |
| (e) | flags `BIT` de escrita condicional |

Sem `@Email_Chamador`, sem texto de mensagem, sem parâmetro que a procedure use para **decidir**.
Exceções (a regra é "literal no corpo"): estados do `WHERE` e a origem de linhas geradas pelo sistema.

- Nome do parâmetro = nome da coluna; **tipo igual ao da coluna**, com o `n` real. `NVARCHAR(MAX)` por
  preguiça impede índice e infla plano; a exceção é parâmetro de transporte (JSON).
- **Truncamento silencioso na atribuição.** Parâmetro do tamanho exato do valor (`NVARCHAR(36)` para
  GUID) perde o último caractere se chegar um branco à esquerda, **antes** de o corpo rodar; nada no
  corpo recupera. Dê folga e aplique `LTRIM(RTRIM())` no corpo. `[verificado: projeto de referência]`
- `= NULL` como default só em parâmetro genuinamente opcional.
- Parâmetro de procedure **não** é validado contra a coluna: valor maior que a coluna estoura no
  `INSERT` com `ANSI_WARNINGS ON` e é truncado em silêncio com `OFF` `[verificado: projeto de
  referência]`. Ligue `SET ANSI_WARNINGS ON` em script de carga e faça o flow cortar o texto
  no limite.
- **Grafia de coluna não se conserta.** O conector é sensível a maiúsculas no nome de coluna: errar
  não acusa ao editar, falha em runtime, calado. Use exatamente o nome do ambiente.
- Atenção a `NULL` em predicado: `col <> @p` com `col` nulo é `UNKNOWN`, e a linha nunca é alterada.
  Use `ISNULL(col, N'') <> ISNULL(@p, N'')` quando a coluna admite `NULL`.

## 11. OUTPUT, relógio e trilha

- **Sempre `OUTPUT ... INTO @tabela`.** `OUTPUT` sem `INTO` devolve linhas ao cliente (vira o
  `Table1` e rouba o retorno) e não é permitido quando a tabela alvo tem trigger habilitado para a
  ação. Fonte: https://learn.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql
- `INSERTED.*` reflete o dado **depois** do statement e **antes** dos triggers: não leia por
  `OUTPUT` uma coluna que o trigger escreve (`Dt_Alteracao`); releia depois do `COMMIT`. Mesma fonte.
- A **ordem** em que o `OUTPUT` captura as linhas não é garantida; ordem cronológica da trilha vem de
  coluna explícita (`ordem`, `Dt_Evento`), nunca da ordem do `IDENTITY`. Mesma fonte.
- O `OUTPUT` devolve linhas ao cliente mesmo se o statement falhar e fizer rollback; por isso o sink
  é variável de tabela e o `SELECT` final só roda depois do `COMMIT`. Mesma fonte.
- **Relógio único do lote:** materialize `SYSUTCDATETIME()` no primeiro `OUTPUT`
  (`... , SYSUTCDATETIME() INTO @sink`) e propague. Todas as linhas do lote carregam a mesma marca.
  No `INSERT`, use `INSERTED.Dt_Inclusao`.
- **Trilha na mesma transação.** Trilha fora da transação mente quando o desfazimento acontece. A
  coluna de "valor anterior" vem de `DELETED.<col>`; "quem" é o `@Id_UsuarioChamador` (e é
  declaração do chamador, não prova: `seguranca-e-permissoes.md`).
- Campo que não mudou não gera linha: isso é `WHERE`, não `IF` (compare com `ISNULL` dos dois lados).

## 12. Concorrência, retry e idempotência

| Situação | Tratamento |
|---|---|
| Duplo clique | a 2ª chamada altera zero linhas (predicado de estado) e devolve `NAO_APLICADO` |
| Reentrada (encerrar de novo, resolver de novo) | o predicado de estado já não casa |
| Duas sessões criando o mesmo registro | guarda no `INSERT` sob `UPDLOCK, HOLDLOCK` + índice único |
| Deadlock (1205) | o flow trata como transitório e **reexecuta**, com limite |
| Retry de uma procedure cujo `UPDATE` sempre casa | **reaplica a trilha**: faça o `UPDATE` ter predicado de "mudou" ou ofereça chave de idempotência |
| Conexão cai depois do `COMMIT` | o flow não sabe se gravou: releia pelo id antes de reenviar |

Operação de cadastro (`INSERT`) sem chave natural única é a que mais sofre com retry; prefira uma
chave de idempotência por requisição (coluna `UNIQUE` preenchida pelo flow) a confiar no clique único.

## 13. Checklist de revisão

Cada item é conferível; os marcados com `lint` o `lint-procedure.py` pega.

- [ ] `SET NOCOUNT ON` na primeira linha (`lint P001`), também nos triggers (consulta em `deploy-e-dba.md`)
- [ ] `SET XACT_ABORT ON` em procedure que grava (`lint P002`)
- [ ] `BEGIN TRAN` com `COMMIT` e, na clássica, `ROLLBACK` em todo `RETURN` cedo (`lint P003`)
- [ ] retorno de 4 colunas, 1 linha, em **todos** os desfechos, inclusive zero linha gravada (`lint P004`)
- [ ] todo `OUTPUT` com `INTO` (`lint P011`)
- [ ] sem SQL dinâmico por concatenação (`lint P009`), sem `NOLOCK` (`lint P010`), sem `SELECT *` (`lint P007`)
- [ ] `dbo.` em tudo (`lint P008`); nome conforme o ambiente (`lint P005`)
- [ ] datas de filtro por `DATEDIFF`, nunca `CAST(... AS INT)` (`lint P006`)
- [ ] `UPDLOCK, HOLDLOCK` só onde o `SELECT` decide a escrita, com índice de apoio
- [ ] nenhum `DECLARE` escalar de trabalho (declarativa) / nenhum `ERROR_MESSAGE()` no retorno (clássica)
- [ ] vocabulário de códigos igual ao do contrato e ao `Switch` do flow
- [ ] a conta do conector não tem DML (`seguranca-e-permissoes.md`)

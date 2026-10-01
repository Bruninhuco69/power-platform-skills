# Contrato procedure ↔ flow

O que a procedure devolve, o que o flow tem de fazer com isso, e como os dois lados evitam divergir.
O **lado do flow** (expressões, `Switch`, `Catch`, `Response`, autorização) é da skill
`power-automate`; aqui está o que o **banco** promete. Padrões decididos: `power-platform/references/decisoes-padrao.md`
(A2, C1, C2, C4).

## Sumário

1. [O que a procedure promete](#1-o-que-a-procedure-promete)
2. [Como o flow lê o retorno](#2-como-o-flow-lê-o-retorno)
3. [Obrigações do flow](#3-obrigações-do-flow)
4. [Checklist de divergência antes do deploy](#4-checklist-de-divergência-antes-do-deploy)
5. [Parâmetro em JSON](#5-parâmetro-em-json)
6. [Retorno que não é o contrato de quatro colunas](#6-retorno-que-não-é-o-contrato-de-quatro-colunas)
7. [Como manter o contrato sem deixá-lo envelhecer](#7-como-manter-o-contrato-sem-deixá-lo-envelhecer)

---

## 1. O que a procedure promete

| Tipo | Retorno | Quem consome |
|---|---|---|
| Escrita | 1 result set, 1 linha, `status`/`description`/`id`/`url`, em todos os desfechos | `Response` do flow, depois de traduzir o código |
| Leitura de dado | result set **é** o dado (lista de colunas fixa) | flow, que transforma em corpo/arquivo |
| Contagem | contrato de 4 colunas; `id` = total, texto, sem separador de milhar | decisão do flow antes de listar/exportar |
| Resolução do chamador | 1 linha com identidade + flags, ou **zero linha** | gate do flow |

Falha de infraestrutura (deadlock, timeout, violação de constraint, `THROW`) **não** volta como
código: a ação do conector falha e o flow trata no `Catch`. Por isso o `Catch` é obrigatório.

Limites do conector com gateway que afetam o contrato
(https://learn.microsoft.com/en-us/connectors/sql/): `OUTPUT` parameters e valor de retorno não
voltam; só o **primeiro** result set; `ResultSets` sem tipo; requisição até 2 MB e resposta até 8 MB;
a ação expira em 110 s.

## 2. Como o flow lê o retorno

Nome do result set e caminho de leitura: `[verificado: projeto de referência]`

```
body('<nome da acao>')?['ResultSets']?['Table1']?[0]?['status']
body('<nome da acao>')?['ResultSets']?['Table1']?[0]?['description']
```

- **Zero linha** é caso de primeira classe: `empty(body(...)?['ResultSets']?['Table1'])` é o teste de
  "chamador desconhecido".
- Coluna `BIT` chega ao flow como booleano (`true`/`false`), não `1`/`0`; condição e `$filter` têm de
  tratar os dois `[verificado: projeto de referência]`. A expressão exata é da skill
  `power-automate`.
- `id` chega como **texto**, que é o tipo do contrato C1.
- Código desconhecido → `error` nomeando o código (não repassar cru).

Coluna calculada devolvida pelo `SELECT` final deve ter nome único e não vazio, ou o conector
rejeita o schema do result set.

## 3. Obrigações do flow

A procedure declarativa **não confere nada além do que o `WHERE` exige**: ela grava o que receber. Estas obrigações são o
contrato do outro lado; cada uma tem um modo de falha **silencioso**. Copie a lista para o contrato
de cada procedure e marque a que se aplica.

| # | Obrigação | Se não cumprir |
|--:|---|---|
| 1 | Resolver o chamador **uma vez**, no tronco, e usar o `Id_Usuario` devolvido como `@Id_UsuarioChamador`; nunca valor do gatilho | quem chama diz quem é; trilha com autoria falsa |
| 2 | Autorizar **por ação**: cada ramo lê a flag **daquela** ação | uma flag de "cadastrar" volta a dar direito de editar e encerrar |
| 3 | Normalizar, validar e derivar tudo antes de chamar: zero-fill, `UPPER`/`LOWER`, trim, domínio, FK, mínimos de tamanho, escopo | a procedure grava lixo sem reclamar |
| 4 | Mandar a unidade **do registro**, nunca a que a tela está visualizando | trilha e registros filhos registram a unidade errada |
| 5 | Cortar texto no limite da coluna (e do JSON) antes de chamar | truncamento silencioso ou erro de estouro |
| 6 | Montar **todo** texto de trilha e título | linhas migradas e novas deixam de se ler na mesma coluna |
| 7 | Não chamar quando não há o que gravar (diff vazio) | `UPDATE` inútil carimba `Dt_Alteracao` a cada Salvar |
| 8 | Resolver o escopo (`NULL` = tudo; `''` casa nada) e **recusar** quando o perfil não vê tudo e a unidade vem vazia | `NULL` vira "todas as unidades", calado |
| 9 | Não passar `NULL` semântico por `coalesce`/truncagem genérica | o `NULL` vira `''` e o relatório volta vazio, sem erro |
| 10 | Chamar a **contagem antes** de listar/exportar, com o mesmo `@Filtros` e o mesmo escopo | não há de onde tirar o total |
| 11 | Traduzir o código num `Switch` com `default` que responde `error` nomeando o código | código cru no toast |
| 12 | `Catch` escutando `Failed`, `TimedOut` e `Skipped` | usuário recebe erro genérico do Power Automate, ou nenhuma resposta |
| 13 | Tratar deadlock (1205) como transitório, com limite de reexecução | falha intermitente em corrida real |
| 14 | Ligar o e-mail do chamador **só** na saída do passo de perfil, nunca no gatilho | some a única invariante de identidade |

## 4. Checklist de divergência antes do deploy

Rode antes de entregar ao DBA e antes de regerar qualquer flow. Qualquer diferença é bug, no flow
ou na procedure; decida qual lado está certo e corrija **no outro**, não nos dois "para empatar".

| # | Confira | Onde quebra se divergir |
|--:|---|---|
| 1 | Número e **ordem** dos parâmetros: flow × `CREATE PROCEDURE` | em runtime, calado: a posição errada grava na coluna errada |
| 2 | Tipo de cada parâmetro (texto × inteiro × bit) | conversão do conector falha, ou acerta o alvo errado |
| 3 | Quais procedures recebem `@Id_UsuarioChamador` e quais não | parâmetro ausente quebra a chamada; sobrando, é parâmetro ignorado |
| 4 | Nome real da procedure no ambiente (`sys.procedures`) × o nome no flow | a ação falha ao executar |
| 5 | Vocabulário de códigos: procedure × `Switch` do flow × contrato | código cru ou `error` indevido |
| 6 | Grafia exata de tabela/coluna (case-sensitive no conector) | a coluna "não existe", em runtime |
| 7 | Contagem de parâmetros do contrato × do flow, por procedure | qualquer número diferente é divergência |
| 8 | Tamanho dos parâmetros de texto × coluna | truncamento silencioso na atribuição |

Automatize o item 1/4 sempre que possível: a assinatura lida do `.sql` (ou de `sys.sql_modules`) é a
fonte; o flow é o que se compara. Doc de contrato escrita à mão envelhece no dia em que é escrita;
gere o que puder.

## 5. Parâmetro em JSON

`Execute stored procedure (V2)` só liga parâmetros **escalares**: tabela como parâmetro (TVP) não
atravessa o conector. Para N linhas (por exemplo as linhas de trilha de uma edição), mande **um
array JSON em `NVARCHAR(MAX)`** e abra com `OPENJSON ... WITH`. Requer `COMPATIBILITY_LEVEL >= 130`
(https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql).

Schema do JSON (chaves em `snake_case`, uma entrada por linha de trilha):

| Chave | Tipo no `WITH` | Coluna de destino | Obrigatória |
|---|---|---|---|
| `ordem` | `INT` | só o `ORDER BY` | sim |
| `tp_evento` | `NVARCHAR(30)` | `Tp_Evento` | sim |
| `resumo` | `NVARCHAR(400)` | `Des_Resumo` | sim |
| `valor_anterior` | `NVARCHAR(200)` | `Des_ValorAnterior` | sim (pode ser `null`) |
| `valor_novo` | `NVARCHAR(200)` | `Des_ValorNovo` | sim (pode ser `null`) |

```sql
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Editar
    @Id_Pedido           INT,
    @Nr_Protocolo        VARCHAR(12),
    @Trilha_Json         NVARCHAR(MAX),
    @Id_UsuarioChamador  INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @Alterado TABLE (
        Id_Pedido  INT          NOT NULL,
        Dt_Evento  DATETIME2(3) NOT NULL
    );

    BEGIN TRANSACTION;

    -- Nr_Protocolo <> @Nr_Protocolo: sem mudanca, zero linha (sem carimbo inutil de Dt_Alteracao)
    UPDATE s
       SET s.Nr_Protocolo = @Nr_Protocolo
    OUTPUT INSERTED.Id_Pedido, SYSUTCDATETIME()
      INTO @Alterado (Id_Pedido, Dt_Evento)
      FROM dbo.APP_Pedido AS s
     WHERE s.Id_Pedido    = @Id_Pedido
       AND s.Flg_Situacao = 1
       AND s.Nr_Protocolo <> @Nr_Protocolo;

    -- N linhas de trilha num INSERT so; array vazio ('[]') grava o UPDATE e zero trilha
    INSERT dbo.APP_PedidoTrilha
          (Id_Pedido, Tp_Evento, Des_Resumo, Des_ValorAnterior, Des_ValorNovo,
           Id_UsuarioChamador, Dt_Inclusao)
    SELECT a.Id_Pedido, j.tp_evento, j.resumo, j.valor_anterior, j.valor_novo,
           @Id_UsuarioChamador, a.Dt_Evento
      FROM @Alterado AS a
     CROSS JOIN OPENJSON(@Trilha_Json)
           WITH (ordem          INT           '$.ordem',
                 tp_evento      NVARCHAR(30)  '$.tp_evento',
                 resumo         NVARCHAR(400) '$.resumo',
                 valor_anterior NVARCHAR(200) '$.valor_anterior',
                 valor_novo     NVARCHAR(200) '$.valor_novo') AS j
     ORDER BY j.ordem;

    COMMIT TRANSACTION;

    SELECT TOP (1)
           v.status AS status, v.description AS description, v.id AS id, N'' AS url
      FROM (VALUES (1, 'success', N'EDITADA',      CONVERT(NVARCHAR(20), @Id_Pedido)),
                   (0, 'warning', N'NAO_APLICADO', N'')
           ) AS v (Gravou, status, description, id)
     WHERE v.Gravou = (SELECT COUNT(*) FROM @Alterado);
END
GO
```

Regras do JSON:

1. **JSON malformado faz a ação do conector falhar** e nada é gravado: a validação do JSON é do flow.
2. **`OPENJSON ... WITH` pode truncar em silêncio** valor maior que o tipo declarado (a coerção é
   estilo `CAST`): o estouro que um parâmetro direto acusaria não existe neste caminho. O flow valida
   tamanho (400/200/50) **antes** de montar o JSON. `[não verificado em ambiente; apontado em
   revisão do projeto de referência]`
3. `ORDER BY` no `INSERT ... SELECT` é melhor esforço para a ordem do `IDENTITY`: não conte com ele
   para nada além de leitura cronológica; a ordem real vem de coluna explícita.
4. Chave que só se conhece **dentro** da transação (ex.: "esta edição criou duplicidade?") vira par
   de flags no próprio JSON (`so_com_duplicidade`, `so_sem_duplicidade`), e o `WHERE` do `INSERT`
   escolhe a variante que sobrevive; assim a procedure nunca aprende a regra.
5. Retry reaplica a trilha pré-calculada (o `UPDATE` casa de novo): ver idempotência em
   `padrao-procedure.md` §12.

## 6. Retorno que não é o contrato de quatro colunas

Leitura de dado devolve o dado. Documente no contrato: a **lista de colunas** e a **ordem** (o flow
mapeia por nome, mas o CSV/arquivo gerado a partir dela depende da ordem), o teto de linhas
(`@Limite`) e a procedure de contagem que o flow chama antes. Contagem e listagem **compartilham a
mesma função** de filtro: duas cópias do `WHERE` divergem. Teste de aceite: `id` da contagem == número
de linhas da listagem, com o mesmo `@Filtros` e o mesmo escopo.

## 7. Como manter o contrato sem deixá-lo envelhecer

- Cada procedure tem um contrato no molde `assets/contrato-procedure-molde.md`, **gerado ou
  conferido** contra o `.sql`.
- O `.sql` que o DBA roda é gerado a partir da fonte e marcado "gerado, não editar"; correção vai
  para a fonte.
- Mudou assinatura? Parâmetro novo entra **no fim** (o `.Run()` do app é posicional; ver C4) e o
  contrato e o flow mudam no mesmo commit.
- Achou defeito num corpo já entregue? Não "conserte em silêncio": registre o desvio (o que mudou e
  por quê), senão a próxima pessoa conserta de volta.

# Escopo por unidade

Como o banco **obedece** a um escopo de unidade (loja, agência, região) sem ser quem o decide. A
decisão e a recusa são do flow (A3); a tela só ajuda a navegar. Aqui: o parâmetro de escopo, o filtro
por lista via JSON, os códigos de unidade e as armadilhas de `StartsWith`/`LIKE` e `NULL`.

## Sumário

1. [Quem faz o quê](#1-quem-faz-o-quê)
2. [Os três estados do escopo](#2-os-três-estados-do-escopo)
3. [Escopo × lista de unidades do filtro](#3-escopo--lista-de-unidades-do-filtro)
4. [Mais de uma unidade por perfil](#4-mais-de-uma-unidade-por-perfil)
5. [Códigos de unidade: prefix-free](#5-códigos-de-unidade-prefix-free)
6. [StartsWith, LIKE e NULL](#6-startswith-like-e-null)
7. [Escrita: a unidade do registro](#7-escrita-a-unidade-do-registro)
8. [Testes](#8-testes)

---

## 1. Quem faz o quê

| Camada | Papel |
|---|---|
| Tela | **UX.** O filtro de unidade na galeria ajuda a navegar; o cliente pode ser manipulado. Fórmula e variáveis em `powerapps-canvas` |
| Flow | **Controle.** Resolve o escopo do perfil, recusa quando não há unidade, autoriza a escrita contra a unidade do registro. Em `power-automate` |
| Procedure / função | **Obedece.** Recebe `@Unidade_Escopo` e o aplica em `AND` com o resto; não decide o valor |

A conta do conector é compartilhada: o SQL não enxerga o usuário final. Por isso o escopo vira
**parâmetro** resolvido pelo flow, e não `SUSER_NAME()`.

## 2. Os três estados do escopo

`@Unidade_Escopo VARCHAR(3)` (tipo igual ao da coluna):

| Valor | Significado | Quem gera |
|---|---|---|
| `NULL` | perfil que vê tudo: sem restrição | flow, quando a flag de "todas as unidades" é verdadeira |
| `'AAA'` | só a própria unidade | flow, com a unidade do chamador |
| `''` | **terceiro estado:** casa unidade nenhuma, de propósito | acidente de mapeamento; o banco falha **fechado** |

`''` só é "nenhuma" se a coluna for `NOT NULL` com
`CHECK (LEN(LTRIM(RTRIM(Nom_Abvd_Unidade))) > 0)`: o `=` do SQL Server ignora espaços à direita,
então sem o `CHECK` `''` casa a linha cuja unidade é `''` ou branco.

```sql
(@Unidade_Escopo IS NULL OR s.Nom_Abvd_Unidade = @Unidade_Escopo)
```

Regras:

1. **Não normalize `''` para `NULL` no T-SQL.** Um `NULLIF(@Unidade_Escopo, N'')` transformaria um
   perfil sem unidade em um perfil que vê **tudo**. O fail-closed de hoje (zero linha, sem erro) é o
   certo; o custo é que parece "não há dados". O que falta é o **teste** do terceiro estado (§8).
2. **O flow não pode passar `NULL` por `coalesce(x, '')` nem por truncagem genérica:** o `NULL`
   vira `''` e o relatório volta vazio para quem vê tudo. Texto completo em
   [autorizacao-no-flow.md](../../power-automate/references/autorizacao-no-flow.md) §3.
3. Quando o perfil **não** vê tudo e a unidade do cadastro vem vazia, o flow **recusa** antes de
   chamar. É a trava que impede `NULL` de significar "todas" por defeito de dado.
4. **Flag de segurança do `CONFIG` nasce ligada** (completo em
   [autorizacao-no-flow.md](../../power-automate/references/autorizacao-no-flow.md) §4).

## 3. Escopo × lista de unidades do filtro

Dois conceitos que parecem iguais e não são:

| | Vem de | Muda a cada consulta? | Pode ampliar o acesso? |
|---|---|---|---|
| **Escopo** (`@Unidade_Escopo`) | perfil, resolvido pelo flow | não | é o limite |
| **Lista do filtro** (`@Filtros.unidades`) | escolha do usuário na tela | sim | **nunca** |

Os dois entram em **`AND`**: a lista restringe dentro do escopo. A função de
`assets/funcao-leitura-molde.sql` aplica as duas coisas; a lista chega num JSON `{"unidades":["AAA","BBB"]}`
aberto por `OPENJSON` (requer `COMPATIBILITY_LEVEL >= 130`,
https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql). Chave ausente, `null`
ou escalar no lugar de array vira "predicado não aplicado", nunca erro.

O `CONVERT(VARCHAR(3), valor)` fica **do lado da lista**: do outro lado a coluna `VARCHAR` seria
promovida a `NVARCHAR` e perderia o seek. A lista tem no máximo algumas dezenas de itens.

## 4. Mais de uma unidade por perfil

`Flg_TodasUnidades` no perfil só expressa "tudo ou uma". Usuário com 3 das dezenas de unidades **não é
representável**. Opções, da mais barata:

1. **Aceitar o limite e registrá-lo** (decisão de produto, no ADR).
2. **Tabela de vínculo** `usuário × unidade` (objeto novo: pedido ao DBA, e o banco pode estar
   congelado). O flow lê as unidades do chamador e manda a **lista** à função.
3. **Escopo como lista JSON no parâmetro**, sem objeto novo:

```sql
CREATE OR ALTER FUNCTION dbo.tvf_APP_Pedido_Visiveis
(
    @Unidades_Permitidas NVARCHAR(4000)   -- NULL = tudo; '[]' = nada (fail-closed)
)
RETURNS TABLE
AS
RETURN
(
    SELECT s.Id_Pedido,
           s.Nom_Abvd_Unidade
      FROM dbo.APP_Pedido AS s
     WHERE s.Flg_Situacao = 1
       AND (@Unidades_Permitidas IS NULL
            OR s.Nom_Abvd_Unidade IN (SELECT CONVERT(VARCHAR(3), LTRIM(RTRIM(j.value)))
                                        FROM OPENJSON(@Unidades_Permitidas) AS j))
);
GO
```

Array vazio devolve zero linha (falha fechada); JSON malformado faz a ação falhar. O flow é quem
lista as unidades permitidas do chamador; o banco só obedece. Continua valendo a regra do §2.2: não
passe esse parâmetro por `coalesce`.

## 5. Códigos de unidade: prefix-free

Quando o app usa **um único token** para os dois modos ("uma unidade" e "todas") por meio de
`StartsWith(coluna; token)`, o token `"AAA"` casa igualdade **somente se nenhum código for prefixo de
outro**: com os códigos `AA` e `AAA`, o token `AA` vazaria `AAA`. O token vazio `""` casa tudo, que é
o modo "todas".

Confira que o conjunto de códigos é **livre de prefixo** (tem de voltar vazio):

```sql
SELECT a.Nom_Abvd_Unidade AS Codigo, b.Nom_Abvd_Unidade AS E_Prefixo_De
  FROM dbo.APP_Unidade AS a
  JOIN dbo.APP_Unidade AS b
    ON b.Id_Unidade <> a.Id_Unidade
   AND b.Nom_Abvd_Unidade LIKE a.Nom_Abvd_Unidade + '%';
```

(`dbo.APP_Unidade` é a tabela de unidades do projeto; pode ser uma tabela
corporativa somente leitura.) Registre no `NOMES-AS-BUILT`
que a propriedade foi **conferida** e a data. Um código novo que viole a propriedade quebra o
escopo de todas as telas sem erro: peça ao dono do cadastro de unidades que a preserve.

No banco, **use `=`**, nunca `LIKE`: `StartsWith` é recurso do app (UX).

## 6. StartsWith, LIKE e NULL

- `StartsWith(coluna; texto)` delega ao SQL Server e vira `LIKE 'texto%'`, sargável
  (https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview,
  nota 6: só com a coluna no primeiro argumento).
- **`LIKE '%'` não casa `NULL`.** No modo "todas", a linha com unidade `NULL` **some calada** das
  duas pontas do filtro. Sem DDL para exigir `NOT NULL` não há como impedir; então:
  - conte as linhas órfãs e registre (consulta abaixo);
  - peça `NOT NULL` ao DBA se possível;
  - ou aceite que registro sem unidade só aparece por outro caminho (relatório em procedure, onde
    `@Unidade_Escopo IS NULL` **não** exclui `NULL`).
- Padding: coluna `CHAR(n)` guarda brancos à direita; o Power Fx não os ignora. Use `VARCHAR(3)` nas
  tabelas suas e `Trim()` na carga da coleção lida de `CHAR` corporativo (`modelo-de-dados.md` §5).
- Comparação de texto com `<`/`>` não delega em texto; `=` e `<>` delegam.

```sql
-- linhas que o modo "todas as unidades" nao enxerga ou enxerga errado (tem de voltar 0, ou decida o que fazer)
SELECT COUNT_BIG(*) AS Sem_Unidade   FROM dbo.APP_Pedido WHERE Nom_Abvd_Unidade IS NULL;
SELECT COUNT_BIG(*) AS Com_Brancos   FROM dbo.APP_Pedido
 WHERE Nom_Abvd_Unidade <> LTRIM(RTRIM(Nom_Abvd_Unidade));
```

## 7. Escrita: a unidade do registro

- A unidade gravada em trilha e em registros filhos é a **do registro** (`DELETED.<coluna>` no `OUTPUT`, ou
  parâmetro validado em `INSERT`), **nunca** a que a tela está visualizando. Obrigação do flow:
  `contrato-proc-flow.md` §3, item 4. A procedure `Editar` do molde não recebe parâmetro de unidade:
  a regra é imposta **por ausência de parâmetro**.
- O flow autoriza a escrita comparando a unidade do **registro** com o escopo do chamador.
- Defesa em profundidade, barata e sem `IF`: o escopo vira uma cláusula `AND` no `WHERE` do `UPDATE`:

  ```sql
  AND (@Unidade_Escopo IS NULL OR s.Nom_Abvd_Unidade = @Unidade_Escopo)
  ```

  Efeito: fora do escopo, zero linha e `NAO_APLICADO`. É rede, não fonte da mensagem: o flow checa
  antes para dar a frase certa. Como o parâmetro vem do chamador, **não** é controle contra quem
  minta o escopo (`seguranca-e-permissoes.md`).
- **RLS nativa** (`SESSION_CONTEXT`) não resolve com conta de serviço compartilhada: o contexto teria
  de ser definido por parâmetro, com o mesmo limite de confiança. `[não verificado]`

## 8. Testes

Os quatro casos que fecham o escopo, contra a função do molde (tem de dar os resultados dos
comentários):

```sql
SELECT COUNT_BIG(*) AS Todas       FROM dbo.tvf_APP_Pedido_Filtrar(N'{}', NULL);    -- total de linhas vivas
SELECT COUNT_BIG(*) AS Uma         FROM dbo.tvf_APP_Pedido_Filtrar(N'{}', 'AAA');   -- so a unidade AAA
SELECT COUNT_BIG(*) AS Nenhuma     FROM dbo.tvf_APP_Pedido_Filtrar(N'{}', '');      -- 0: terceiro estado
SELECT COUNT_BIG(*) AS Interseccao FROM dbo.tvf_APP_Pedido_Filtrar(N'{"unidades":["BBB"]}', 'AAA');  -- 0: o filtro nao amplia o escopo
```

E os testes de flow, do lado de `power-automate`: perfil sem "todas" e unidade vazia é recusado;
unidade do registro fora do escopo é recusada; `NULL` chega ao banco como `null`, não como `''`.

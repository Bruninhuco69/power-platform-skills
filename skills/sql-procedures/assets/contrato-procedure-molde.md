# Contrato · dbo.usp_<SIGLA>_<Entidade>_<Acao>

> Molde. Copie para o contrato de cada procedure e preencha. Apague o que não se aplica, **não**
> deixe campo vazio. Quando houver gerador, este arquivo é **gerado** do `.sql` e do flow; à mão
> envelhece no dia em que é escrito. Nome da procedure: o **real** do ambiente (`sys.procedures`).
>
> Padrões: `power-platform/references/decisoes-padrao.md` (A2, C1, C2, B1).
> Como a procedure é escrita: `sql-procedures/references/padrao-procedure.md`.

| | |
|---|---|
| Procedure (as-built) | `[dbo].[<nome real>]` verificada em `<AAAA-MM-DD>` |
| Variante | declarativa / clássica (ver `padrao-procedure.md` §5) |
| Chamada por | flow `<nome do flow>`, ação `<nome da ação>`, caso `<acao>` |
| Operação irreversível? | sim / não |
| Versão mínima do SQL Server | `<ex.: 2016 SP1, COMPATIBILITY_LEVEL >= 130 se usar OPENJSON>` |
| Estado | rascunho / em hold (`<motivo>`) / entregue ao DBA em `<data>` / em produção |

## 1. Origem

Qual ação da tela/flow ela substitui ou atende. Nome de **controle e de ação**, nunca número de linha
(linha envelhece). Se houver comando que reencontra o trecho, escreva-o.

| Item | Valor |
|---|---|
| Tela / controle | `<nome do controle>`, propriedade `<OnSelect>` |
| Ação do flow | `<nome>` |
| Regra de negócio que carrega | `<RN-xx ou texto curto>` |

## 2. Assinatura

Classe: (a) PK do alvo · (b) valor de coluna já normalizado e validado pelo flow · (c)
`@Id_UsuarioChamador` · (d) valor de linha de trilha · (e) flag `BIT` condicional.

| # | Parâmetro | Tipo | Classe | Obrigatório | Conteúdo / origem | Quem valida |
|--:|---|---|:--:|:--:|---|---|
| 1 | `@Id_<Entidade>` | `INT` | a | sim | PK do alvo | flow (existe e está ativo) |
| 2 | `@Des_<Coluna>` | `NVARCHAR(<n>)` | b | sim | `<origem>`; tipo e tamanho = os da coluna | flow (domínio, tamanho) |
| 3 | `@Tp_Evento` | `NVARCHAR(30)` | d | sim | montado pelo flow | flow |
| 4 | `@Id_UsuarioChamador` | `INT` | c | sim | de `Id_Usuario` devolvido pela resolução do chamador | flow |

Parâmetros que a procedure **deliberadamente não tem**: `<e-mail, mensagem, data de auditoria,
unidade visualizada, ...>`, e por quê.

Literais que ficam **no corpo** (nunca em parâmetro): `<estado esperado no WHERE, origem fixa>`.

Contagem: `<N>` parâmetros. O flow tem de ter `<N>` ligados, **na mesma ordem**; parâmetro novo entra
**no fim**.

## 3. Retorno

1 result set, 1 linha, `status` / `description` (código) / `id` (texto) / `url` (`''`), em **todos** os
desfechos, inclusive zero linha gravada.

| status | description (código) | Significado no banco | Frase (dona: o flow) |
|---|---|---|---|
| success | `<CODIGO_OK>` | gravou | `<frase com o id>` |
| warning | `NAO_APLICADO` | o predicado de estado não casou: 0 linhas | flow **relê** e explica |
| error | `<CODIGO_RECUSA>` | só o lock sabe (duplicidade sob `UPDLOCK, HOLDLOCK`) | `<frase>` |

Falha de infraestrutura (deadlock 1205, timeout, constraint, `THROW`): a **ação do conector falha**;
o `Catch` do flow monta a mensagem. Não existe código para isso.

## 4. Regras aplicadas

| Regra | Onde mora | O que rejeita | Antes de qual escrita |
|---|---|---|---|
| `<RN-xx>` | flow / predicado do `WHERE` / banco | `<o que>` | `<statement>` |

Regra que **subiu para o flow** e que o banco não repete: liste, com o motivo e a obrigação do flow
correspondente (`contrato-proc-flow.md` §3). **É o que impede a regra de sumir sem dono.**

## 5. Sequência

Dentro da transação: marque o que é transacional.

1. `SET NOCOUNT ON; SET XACT_ABORT ON;`
2. **[tx]** `UPDATE ... WHERE <PK> AND <estado esperado> OUTPUT ... INTO @sink`
3. **[tx]** `INSERT <trilha> ... SELECT ... FROM @sink` (sink vazio: zero linha)
4. `COMMIT`
5. `SELECT TOP (1) ... FROM (VALUES ...)`: retorno

## 6. Tabelas tocadas

| Ordem | Tabela | Operação | Observação |
|--:|---|---|---|
| 1 | `dbo.<SIGLA>_<Entidade>` | UPDATE | trigger de `Dt_Alteracao` ativo: `OUTPUT` com `INTO` |
| 2 | `dbo.<SIGLA>_<Entidade>Trilha` | INSERT | mesma transação |

Concorrência: `<predicado de estado / UPDLOCK+HOLDLOCK em ... com o índice ...>`.
Idempotência: `<o que acontece em duplo clique e em retry>`.

## 7. Obrigações do flow

Marque as que se aplicam (lista completa em `contrato-proc-flow.md` §3):

- [ ] resolver o chamador no tronco e mandar o `Id_Usuario` como `@Id_UsuarioChamador`
- [ ] autorizar pela flag **desta** ação: `<Flg_...>`
- [ ] normalizar, validar e derivar `<campos>`; cortar texto no tamanho da coluna
- [ ] mandar a unidade **do registro**; resolver `@Unidade_Escopo` (`null` ≠ `''`)
- [ ] traduzir o código num `Switch` com `default` que responde `error` nomeando o código
- [ ] `Catch` com `Failed`, `TimedOut`, `Skipped`; reexecutar 1205 com limite
- [ ] não chamar quando não há o que gravar

## 8. Pendências para o DBA

| Tag | Pendência | Bloqueia |
|---|---|---|
| ⬜ DECIDIR | `<pergunta de negócio ou de ambiente sem resposta>` | `<este objeto>` |
| ⚠ | `<bloqueador vivo>` | `<...>` |

DDL necessário (pedido em `pedido-ddl-dba-molde.md`): `<coluna calculada, índice, FK, trigger>`.
Provas de ambiente de que depende: `<compat level, OUTPUT INTO com trigger, collation>`.

## 9. Testes de aceite

| # | Entrada | Esperado |
|--:|---|---|
| 1 | caso feliz | 1 result set, 1 linha, 4 colunas; `status = success`; trilha com 1 linha |
| 2 | segunda chamada idêntica (duplo clique) | `warning` / `NAO_APLICADO`; zero escrita |
| 3 | `<valor que viola o predicado de estado>` | `warning` / `NAO_APLICADO` |
| 4 | `<corrida: duas sessões>` | exatamente uma grava; a outra recebe `<CODIGO_RECUSA>` |
| 5 | erro forçado no meio do lote | `@@TRANCOUNT = 0`, nada gravado, e a ação do conector **falha** |

Comando que roda o lint: `python <pasta-da-skill>/scripts/lint-procedure.py <pasta>` → `0 erro(s)`.

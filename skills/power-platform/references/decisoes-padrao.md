# Decisões-padrão

Fonte única dos padrões que valem para todo projeto. As outras skills apontam para cá em vez
de repetir. Um projeto pode divergir, mas só com um ADR que diga qual decisão muda e por quê.

Origem: a análise de dois projetos de referência em produção, um em SQL Server + procedures e
outro em Dataverse.

## Sumário

1. [Arquitetura](#1-arquitetura)
2. [Contrato app ↔ flow](#2-contrato-app--flow)
3. [Separadores e dialeto Power Fx](#3-separadores-e-dialeto-power-fx)
4. [Telas](#4-telas)
5. [Flows](#5-flows)
6. [Banco](#6-banco)
7. [Ambiente e nomes](#7-ambiente-e-nomes)
8. [Processo](#8-processo)

---

## 1. Arquitetura

| # | Decisão | Por quê |
|---|---|---|
| A1 | **A tela não grava direto na fonte.** Escrita com regra de negócio passa por um flow; o flow chama a procedure (SQL) ou grava no Dataverse. | Regra no cliente é contornável e fica duplicada em cada tela. |
| A2 | **O flow decide; a procedure executa.** O flow normaliza, valida, autoriza e traduz o código de resultado em mensagem. A procedure abre a transação, grava e devolve um código. | Concentra a regra num lugar editável sem DBA; o banco tende a congelar em produção. |
| A3 | **O escopo na tela é UX, não controle de acesso.** O filtro por unidade na galeria ajuda a navegar; quem barra é o flow. | A conta de serviço do conector é compartilhada; o cliente pode ser manipulado. |
| A4 | **Uma trilha de dados por projeto** (`sql-server` **ou** `dataverse`), declarada em `power-platform.config.json` e em `00-LEIA-PRIMEIRO.md`. Trocar de trilha exige ADR. | Duas trilhas vivas com documentos apontando para a errada custaram dias de retrabalho. |

## 2. Contrato app ↔ flow

| # | Decisão |
|---|---|
| C1 | Resposta do flow para o app: **`{ status, description, id, url }`**, todos texto. `status` ∈ `success` \| `warning` \| `error`. |
| C2 | `description` é a frase pronta para o usuário, montada no flow. A procedure devolve **código** (ASCII, vocabulário fechado); o flow traduz. |
| C3 | No app, **sucesso é `status <> "error"`** (`warning` também fecha o modal) e toda chamada `.Run()` fica dentro de `IfError`. |
| C4 | Parâmetros do trigger Power Apps V2 são **posicionais e texto**. Parâmetro novo entra **sempre no fim**. Id numérico vai como `Text(id; "[$-en-US]0")`. |
| C5 | Depois de gravar: `Refresh(<fonte>)` + recontagem dos contadores da tela. |
| C6 | Entrada de sistema externo usa trigger **HTTP** próprio, separado dos flows chamados pelo app. Token no header (validação e cache: `power-automate/references/http-entrada-externa.md`); resposta derivada do status real da validação. |

## 3. Separadores e dialeto Power Fx

| Onde o código vai | Argumento | Encadear | Decimal |
|---|---|---|---|
| **Barra de fórmulas** do Studio em locale pt-BR (ex.: `App.OnStart` digitado) | `;` | `;;` | `,` |
| **YAML colado** no Studio (`.pa.yaml`, telas e componentes) | `,` | `;` | `.` |

Misturar os dois não parseia. Todo bloco de código numa skill ou num documento diz o destino.
`[verificado: projetos de referência]`

## 4. Telas

| # | Decisão |
|---|---|
| T1 | Layout **ManualLayout + controles Classic**, canvas fixo (1920×1080 nos projetos de referência). AutoLayout/Modern ficam fora do padrão até um projeto provar no Studio. |
| T2 | `Control: Tipo@versão` **com** a versão exata já usada no app. |
| T3 | Cor, fonte e tamanho só por token `fx*` (named formulas). Nada de `RGBA(` literal em tela. |
| T4 | Propriedade nova só se o app já a usa naquele tipo de controle (o Studio recusa o bloco inteiro com PA2108). |
| T5 | Nome de controle `<prefixo-tela>-<tipo>-<módulo>-<elemento>` em kebab-case; único no app. |
| T6 | Toda variável global nasce no `OnStart`. Named formula não depende de variável global. |
| T7 | Delegação declarada por escrito no cabeçalho de cada tela (o que delega, o que não, o teto). |
| T8 | Permissão por **flag** do perfil (`Flg_PodeX` / `pode_x`), nunca por nome de perfil. Sem perfil resolvido = sem acesso (fail-closed). |

## 5. Flows

| # | Decisão |
|---|---|
| F1 | Esqueleto: `CONFIG` → identificar chamador → `Try { autorizar por ação → normalizar → validar → gravar → responder }` → `Catch` escutando `Failed`, `TimedOut` **e** `Skipped` → `Response`. |
| F2 | Autorização **por ação** (cada caso do `Switch` checa a sua flag), nunca um portão único. |
| F3 | Interruptor de segurança nasce **ligado** no `CONFIG` do flow. Não confundir com **flag de permissão** do perfil (`Flg_PodeX`), que nasce **desligada**: ninguém ganha permissão por omissão. |
| F4 | **Log de execução em todo flow** (escopo `Log` com `runAfter` em Succeeded/Failed/TimedOut). Exceção intencional a F1: o `Log` não escuta `Skipped`. Destino do log quando os dados estão em SQL: **em aberto** — ver ADR do projeto. |
| F5 | Nada de nome de ambiente, servidor ou tabela `dev*` literal: variável de ambiente + connection reference. |
| F6 | Entrega por colagem no designer: o arquivo colado é **gabarito**; gerador nunca escreve sobre ele (escreve em `dist/`). |

## 6. Banco

| # | Decisão |
|---|---|
| B1 | Procedure de escrita: `SET NOCOUNT ON; SET XACT_ABORT ON;`, transação, retorno de **1 linha** com `status, description, id, url`. |
| B2 | Data filtrada pelo app via coluna calculada inteira `Ref_<col> AS DATEDIFF(day, 0, <col>) PERSISTED` (filtro de data direto não delega atrás de gateway). Nunca `CAST(... AS INT)` — arredonda. |
| B3 | Contagem no app sobre SQL: `CountRows` não delega; mostrar teto (`2.000+`) ou contar no servidor. |
| B4 | Banco em produção tende a congelar: tabela nova e mudança de assinatura passam pelo DBA; coluna calculada costuma ser aceita. Planeje o schema antes do primeiro deploy. |

## 7. Ambiente e nomes

| # | Decisão |
|---|---|
| N1 | **`NOMES-AS-BUILT.md` é a autoridade de nomes** — tabelas, colunas, tipos e procedures lidos do ambiente real. Dicionário, script de criação e plano perdem para ele. |
| N2 | Nada de tela ou flow antes de `AMBIENTE-AS-BUILT/` preenchido (pasta do projeto com ambientes, conexões e o `NOMES-AS-BUILT.md`). |
| N3 | Antes de afirmar que uma coluna não existe, abrir o esquema da tabela — nunca um extrato filtrado. |

## 8. Processo

| # | Decisão |
|---|---|
| P1 | Git desde o dia 0. |
| P2 | Uma fila só (`GOAL.md`); toda tarefa ✅ tem coluna **Evidência** (comando + saída + data). |
| P3 | Saída de gerador marcada "gerado — não editar"; correção manual vai para a entrada do gerador. |
| P4 | Validador que nunca acusou nada não provou que valida: todo portão tem um teste que planta o erro. |
| P5 | Documento que declara número (contagem, baseline) traz o comando que o mede. |

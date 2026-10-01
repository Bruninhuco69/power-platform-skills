# Subagentes

Quem são os agentes do pipeline, quando abrir um subagente fora dele, como dividir e o que exigir
na volta. Os modelos de prompt para auditoria de app existente estão em `prompts/`.

## Sumário

0. [Agentes do pipeline](#agentes-do-pipeline)
1. [Quando abrir (e quando não)](#quando-abrir-e-quando-não)
2. [Escopos disjuntos](#escopos-disjuntos)
3. [Como lançar](#como-lançar)
4. [Formato de saída obrigatório](#formato-de-saída-obrigatório)
5. [Contrato de conclusão](#contrato-de-conclusão)
6. [Verificar antes de reportar](#verificar-antes-de-reportar)
7. [Consolidar](#consolidar)
8. [Modelos de prompt](#modelos-de-prompt)

## Agentes do pipeline

Definidos em `agents/` do plugin e chamados pelas etapas `/pp:*` com `subagent_type` `pp:<nome>`.
Cada um recebe `RAIZ` (raiz do projeto) e `KIT` (pasta do plugin, o `${CLAUDE_PLUGIN_ROOT}` da
etapa), lê os arquivos do projeto e devolve uma entrega com formato fixo.

| Agente | Etapa | Ferramentas | Escreve em |
|---|---|---|---|
| `agente-mockups` | `/pp:mockups` | leitura + escrita, **sem Bash** (não chama a API de imagens) | `inventario-telas.md`, `mockups/mockups.json` |
| `agente-prototipo` | `/pp:prototipo` | leitura, escrita, Bash (verificador) | `prototipo/index.html` |
| `agente-arquitetura` | `/pp:arquitetura` | leitura, escrita, Bash (lint de procedure) | `arquitetura.md`, ADR, scripts de dados, `GOAL.md`, config |
| `agente-canvas` | `/pp:construir` (`app`) | leitura, escrita, Bash (`validar-telas.py`) | pastas de tela |
| `agente-automate` | `/pp:construir` (`flows`) | leitura, escrita, Bash (`verificar-fluxo.py`) | pastas de fluxo (e procedure em correção) |
| `agente-qa` | `/pp:testar` | só leitura + Bash para validadores | nada: a etapa escreve o relatório |

Brainstorm e Designer Branding **não** são subagentes: subagente não conversa com o usuário (o
Claude Code tira dele a ferramenta de perguntar), então a sessão da etapa assume o papel.

Canvas e Automate rodam **em paralelo**, na mesma mensagem, com escritas em pastas disjuntas.
A etapa que chama sempre confere a entrega (seção "Verificar antes de reportar").

## Quando abrir (e quando não)

Abra **somente** se as duas condições valem:

1. O trabalho é **independente** (um não precisa do resultado do outro).
2. Exige **leitura ampla** (várias telas grandes, muitas procedures, varredura de um app inteiro).

| Situação | Decisão |
|---|---|
| Uma tela, um flow, uma procedure | faça direto; agente é desperdício de contexto |
| Etapa do pipeline | o agente que a etapa manda chamar, nada além |
| Auditar o app inteiro (≥ 3 telas) | fan-out por **disciplina** (ux, dev, performance, dados) |
| Feature que toca tela + flow + banco | um agente por camada, **depois** que o contrato está fechado |
| Investigar "o número não bate" | você conduz a cadeia; agente só para varrer fonte ou flows em paralelo |
| Tarefa já do tamanho de um agente | **não re-delegue**: quem recebeu faz |

Não use agente para decidir, para escrever o relatório final nem para validar o próprio trabalho.

## Escopos disjuntos

Dois agentes no mesmo arquivo e no mesmo tema gastam contexto e produzem conclusões conflitantes.
Divida por **tema** ou por **arquivo**, nunca pelos dois sobrepostos:

| Agente | Fala de | Não fala de |
|---|---|---|
| `ux` | cor, tipografia, espaçamento, hierarquia, acessibilidade | convenção de código, custo de consulta |
| `dev` | nome, estrutura YAML, anti-padrão de Power Fx, duplicação | delegação, custo, nomes de coluna |
| `performance` | delegação, nº de requisições, o que carrega quando, timers | estilo de código |
| `dados` | de onde vem o dado, fonte certa, colunas, integridade | custo de consulta |
| `flow` | esqueleto do flow, Try/Catch, autorização, contrato, log | tela |
| `sql` | procedure, transação, retorno, delegação do SQL | flow, tela |

## Como lançar

- **Todos numa só mensagem**, para rodarem em paralelo.
- Preencha o modelo: `{{PROJETO}}`, `{{RAIZ}}` (raiz do projeto, relativa ou informada em runtime —
  nunca caminho absoluto de usuário gravado em arquivo), `{{ESCOPO}}`, `{{OBJETIVO}}`,
  `{{ACHADOS_CONHECIDOS}}` (o que já se sabe, com o comando que verifica — evita redescobrir).
- Entregue o contexto que o agente não tem: trilha ativa, caminho do `NOMES-AS-BUILT`, tamanho dos
  arquivos grandes, o que é gerado × gabarito.
- Agente **só lê** por padrão. Escrita exige instrução explícita e arquivo disjunto.

## Formato de saída obrigatório

Todo achado vem com **evidência reproduzível**: `arquivo:linha` **e** o comando que o reencontra
(`grep`, nome de controle/ação). Achado sem evidência não entra no relatório.

```
Severidade | arquivo:linha | comando que reencontra | Problema | Correção (antes → depois)
```

Seções obrigatórias na volta: **confirmado** (com evidência), **inferido/não confirmado**, **o que
não foi coberto e por quê**. Máximo de 25 linhas de resumo.

## Contrato de conclusão

Vale para quem delega, em qualquer profundidade:

1. **A sua mensagem final é a entrega.** Nunca termine o turno com "aguardando os agentes": um
   agente pendente não notifica quem já encerrou; o resultado dele se perde.
2. **Quem delega coleta.** Espere, integre e só então devolva. Delegar e sair é proibido.
3. **Decomponha só quando o trabalho não cabe num contexto.** Profundidade é consequência, não plano.
4. Um filho **executa** e devolve; não abre netos para tarefa que já coube nele.

## Verificar antes de reportar

Agentes erram. Reabra você mesmo os achados mais fortes (os que mudam a decisão, os de severidade
alta e os que contradizem o que você sabia):

- "arquivo/pasta vazia" → liste a pasta.
- "variável nunca inicializada" → conte as atribuições em **todos** os arquivos (inicialização em
  `OnSelect` não é ausência).
- "coluna não existe" → abra o esquema da tabela.
- "N ocorrências" → rode o comando de contagem.

Achado que você não conseguiu reproduzir entra como **não verificado**, não como fato.

## Consolidar

Deduplique, ordene por severidade, atribua cada achado ao agente que o trouxe, e declare o que cada
agente **não** cobriu. Conflito entre agentes: resolva com a evidência, não por votação.

## Modelos de prompt

| Arquivo | Quando |
|---|---|
| `prompts/ux.md` | revisão visual/acessibilidade em ≥ 3 telas |
| `prompts/dev.md` | convenções, Power Fx, YAML, anti-padrões em escopo amplo |
| `prompts/performance.md` | lentidão, delegação, timers, carregamento |
| `prompts/dados.md` | fonte do dado, colunas, integridade, "o número não bate" |
| `prompts/flow.md` | auditoria de flows |
| `prompts/sql.md` | auditoria de procedures e delegação SQL |

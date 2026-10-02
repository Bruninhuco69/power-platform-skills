# Subagentes

Quem são os agentes do pipeline, quando abrir um subagente fora dele, como dividir, o que exigir
na volta e como julgar a entrega. Os modelos de prompt para auditoria de app existente estão em
`prompts/`.

**A sessão é a cabeça, o agente é a mão.** A sessão da etapa define o pedido, junta o contexto,
julga o que volta e decide com o usuário. O agente faz o trabalho pesado (escrever tela, fluxo,
procedure, protótipo, spec) e prova o que fez. A cabeça não faz o trabalho da mão: o que está
errado no arquivo do agente volta para ele, com a evidência. Registros da etapa (`ESTADO.md`,
`GOAL.md`, `docs/qa/`, rodadas de ajuste) são da cabeça.

## Sumário

0. [Agentes do pipeline](#agentes-do-pipeline)
1. [Quando abrir (e quando não)](#quando-abrir-e-quando-não)
2. [Escopos disjuntos](#escopos-disjuntos)
3. [Como lançar](#como-lançar)
4. [Formato de saída obrigatório](#formato-de-saída-obrigatório)
5. [Entrega padrão de todo agente](#entrega-padrão-de-todo-agente)
6. [Contrato de conclusão](#contrato-de-conclusão)
7. [Verificar antes de reportar](#verificar-antes-de-reportar)
8. [Julgar a entrega](#julgar-a-entrega)
9. [Consolidar](#consolidar)
10. [Modelos de prompt](#modelos-de-prompt)

## Agentes do pipeline

Definidos em `agents/` do plugin e chamados pelas etapas `/pp:*` com `subagent_type` `pp:<nome>`.
Cada um recebe `RAIZ` (raiz do projeto) e `KIT` (pasta do plugin, o `${CLAUDE_PLUGIN_ROOT}` da
etapa), lê os arquivos do projeto e devolve uma entrega com formato fixo.

| Agente | Etapa | Ferramentas | Escreve em |
|---|---|---|---|
| `agente-mockups` | `/pp:mockups` | leitura + escrita, **sem Bash** (não chama a API de imagens) | `inventario-telas.md`, `mockups/mockups.json` |
| `agente-prototipo` | `/pp:prototipo` | leitura, escrita, Bash (verificador) | `prototipo/index.html` |
| `agente-arquitetura` | `/pp:arquitetura` | leitura, escrita, Bash | `arquitetura.md` (com o spec das procedures), ADR, DDL ou modelo Dataverse, `GOAL.md`, config |
| `agente-sql` | `/pp:arquitetura` (um por grupo, em paralelo), `/pp:construir` (correção) | leitura, escrita, Bash (`lint-procedure.py`) | pasta de procedures, só as do seu grupo |
| `agente-canvas` | `/pp:construir` (`app`; um por grupo de até 3 telas) | leitura, escrita, Bash (`validar-telas.py`) | as telas do seu grupo |
| `agente-automate` | `/pp:construir` (`flows`; um por grupo de até 3 fluxos) | leitura, escrita, Bash (`verificar-fluxo.py`) | os fluxos do seu grupo |
| `agente-qa` | `/pp:testar` | só leitura + Bash para validadores | nada: a etapa escreve o relatório |
| `agente-pesquisa` | `/pp:brainstorm`, `/pp:arquitetura`, `/pp:construir`, `/pp:mudanca`, auditoria | só leitura + busca na web (sem Bash, sem escrita) | nada: devolve achados com fonte |

**Pesquisa** é a mão de quem decide: quando a etapa precisa de um fato (o conector existe? exige
licença premium? o que significa esta mensagem de erro? o que já existe nesta pasta?), a sessão
pergunta ao `agente-pesquisa` em vez de ler tudo ou de chutar. Ele devolve achado com fonte.

Brainstorm e Designer Branding **não** são subagentes: subagente não conversa com o usuário (o
Claude Code tira dele a ferramenta de perguntar), então a sessão da etapa assume o papel.

Canvas, Automate e SQL rodam **em paralelo**, na mesma mensagem, com escritas em arquivos
disjuntos: a coluna Arquivos do `GOAL.md` (e os grupos da seção 4.1 da arquitetura) é o que
divide. No máximo 5 agentes por mensagem.
A etapa que chama sempre julga a entrega (seção "Julgar a entrega").

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
- **Modelo de cada agente:** `python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/modelos.py" de <agente>`.
  Saiu um nome (`opus`, `sonnet`...): passe como `model` na chamada. Saiu linha vazia: não passe
  `model` (o agente herda o da sessão). Perfis e trocas: `modelos.md`.
- Preencha o modelo: `{{PROJETO}}`, `{{RAIZ}}` (raiz do projeto, relativa ou informada em runtime —
  nunca caminho absoluto de usuário gravado em arquivo), `{{ESCOPO}}`, `{{OBJETIVO}}`,
  `{{ACHADOS_CONHECIDOS}}` (o que já se sabe, com o comando que verifica — evita redescobrir).
- Entregue o contexto que o agente não tem: trilha ativa, caminho do `NOMES-AS-BUILT`, tamanho dos
  arquivos grandes, o que é gerado × gabarito.
- Agente **só lê** por padrão. Escrita exige instrução explícita e arquivo disjunto.
- **Perguntas antes, numa rodada só.** Subagente não pergunta: o que ele precisaria saber (fato do
  ambiente, decisão pendente, preferência) a sessão pergunta ao usuário **antes** de lançar, tudo
  junto. Pergunta que volta como "aberta" depois do trabalho feito costuma custar uma revisão.
- **O pedido é um spec:** os arquivos exatos que o agente pode tocar, o que é "pronto" sem
  ambiguidade, o comando que prova e o que fica de fora. Dois pedidos que tocam o mesmo arquivo
  rodam um depois do outro.

## Formato de saída obrigatório

Todo achado vem com **evidência reproduzível**: `arquivo:linha` **e** o comando que o reencontra
(`grep`, nome de controle/ação). Achado sem evidência não entra no relatório.

```
Severidade | arquivo:linha | comando que reencontra | Problema | Correção (antes → depois)
```

Seções obrigatórias na volta: **confirmado** (com evidência), **inferido/não confirmado**, **o que
não foi coberto e por quê**. Máximo de 25 linhas de resumo.

## Entrega padrão de todo agente

Cada agente do pipeline tem a sua entrega (arquivos, tabelas, passo a passo de colagem) e fecha
**sempre** com as mesmas quatro seções, para quem julga ler todas do mesmo jeito:

```
## Como verifiquei
- <comando que rodou> → <a última linha que saiu>   (o que não rodou: "não verificado")
## Conformidade com o pedido
- Cumprido | Parcial | Desvio: <qual item, e por quê>
## Alertas para quem julga
- riscos, pedido mal especificado, o que olhar com cuidado
## Confiança
- alta | média | baixa, e por quê
```

Regras que valem para todo agente:

- **"Deve funcionar" não é verificação.** Só conta o que foi rodado e observado.
- **Nunca invente** nome, dado, saída de comando ou teste que passou.
- **Faça o que o pedido diz, nada além.** Não melhore o que não foi pedido; na dúvida sobre apagar
  algo, a leitura mais estreita.
- **Pedido falho ou incompleto:** faça a parte segura e diga o resto nos alertas. Não redesenhe em
  silêncio.
- **Localize, leia o trecho, aja.** Ler arquivo inteiro que não precisa gasta o contexto.

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

## Julgar a entrega

Leia a entrega como cético, não para carimbar:

1. **Prova, não promessa.** Só vale o que está em "Como verifiquei" com comando e saída. Rode de
   novo o validador da camada (a última linha tem de bater) e reabra 2 ou 3 afirmações que mudam a
   decisão (seção anterior).
2. **Pedido × entrega.** Cada item do pedido (tarefa da onda, item de correção, tela do inventário)
   tem resposta. Leia primeiro o que veio "Parcial" ou "Desvio".
3. **Alertas** viram aceite consciente, revisão ou pergunta ao usuário. Nenhum fica sem destino.
4. **Veredito por agente:**

| Veredito | Quando | O que fazer |
|---|---|---|
| ✓ aceito | pedido cumprido e provado | segue a etapa |
| ↻ revisão | faltou algo que o agente consegue fazer | chame o **mesmo** agente com um pedido mais apertado: o item que faltou, o arquivo, o critério que falhou e a saída do validador. Nunca "melhore isso" |
| ⚠ escalado | falta decisão ou informação do usuário, o pedido estava errado, ou duas revisões não fecharam | checkpoint com o usuário: o que se pediu, o que voltou, as opções |

5. **No máximo duas revisões** por agente e por pedido na mesma sessão; a terceira é escalada.
6. **Registre cada veredito**, uma linha por agente:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/estado.py" veredito <etapa> \
     --agente <nome> --resultado aceito|revisao|escalado --motivo "<uma frase>"
   ```

   O `/pp:progresso` mostra quantas revisões cada etapa precisou: é a prova de que o julgamento
   rodou, e o número que diz se o modelo de quem executa está dando conta (`modelos.md`).
7. **Mostre o veredito** ao usuário numa linha (`formato-saida.md` §4).

## Consolidar

Deduplique, ordene por severidade, atribua cada achado ao agente que o trouxe, e declare o que cada
agente **não** cobriu. Conflito entre agentes: resolva com a evidência, não por votação.

## Modelos de prompt

Cada prompt roda como `pp:agente-pesquisa` (só lê), com o modelo de
`modelos.py de agente-pesquisa`; a sessão consolida e julga.

| Arquivo | Quando |
|---|---|
| `prompts/ux.md` | revisão visual/acessibilidade em ≥ 3 telas |
| `prompts/dev.md` | convenções, Power Fx, YAML, anti-padrões em escopo amplo |
| `prompts/performance.md` | lentidão, delegação, timers, carregamento |
| `prompts/dados.md` | fonte do dado, colunas, integridade, "o número não bate" |
| `prompts/flow.md` | auditoria de flows |
| `prompts/sql.md` | auditoria de procedures e delegação SQL |

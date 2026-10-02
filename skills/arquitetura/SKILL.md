---
name: arquitetura
description: "Use quando o protótipo do app Power Apps foi aprovado e é hora da etapa 6 do pipeline: decidir com o usuário a trilha de dados (Dataverse ou SQL Server) e chamar o Agente de Arquitetura, que escreve o modelo de dados, as permissões, as integrações, o contrato app↔flow, os scripts de dados e a fila de construção GOAL.md. Não use antes de o protótipo ser aprovado, nem para uma procedure ou tabela isolada (use `sql-procedures` ou `dataverse`)."
user-invocable: true
disable-model-invocation: true
---

# /pp:arquitetura — Agente de Arquitetura

Etapa 6 do pipeline, bloco **3. Construção na Power Platform**. Você leva ao usuário a única decisão
grande da etapa (onde moram os dados) e chama o agente `pp:agente-arquitetura`, que transforma PRD,
inventário e protótipo em modelo de dados, permissões, integrações e a fila de construção.

`KIT` = `${CLAUDE_PLUGIN_ROOT}`. Formato de saída: `KIT/skills/power-platform/references/formato-saida.md`.
Script de estado: `python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/estado.py"`.
Modelos: `python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/modelos.py"`.

## Antes de começar

1. `estado.py comecar arquitetura`. Exit 1: mostre a saída e pare.
2. Leia `docs/planejamento/prd.md`, `inventario-telas.md`, os blocos 4, 7 e 8 de `brainstorm.md`,
   e `KIT/skills/power-platform/references/matriz-tecnologia.md` e `decisoes-padrao.md`.

## Passos

0. **Pesquisa, se faltar fato** para a trilha: o PRD cita fonte que já existe (planilha, banco,
   sistema) com arquivos no projeto, ou há dúvida de licença ou limite. Chame
   `pp:agente-pesquisa` com `ONDE: os dois`, `PARA QUE: escolher a trilha de dados` (modelo:
   `modelos.py de agente-pesquisa`). Julgue e use os achados com fonte entre os fatos do passo 1.
1. **Trilha de dados** (checkpoint `Decisão`). Aplique a matriz às respostas do brainstorm e
   recomende **uma** trilha, com os 3 fatos que pesaram (volume acima de 2.000, banco SQL que já
   existe, compliance, DBA, transação em várias tabelas). `AskUserQuestion`, a recomendada primeiro:
   - "SQL Server + procedures";
   - "Dataverse";
   - "Preciso confirmar com a TI".
   A terceira vira `D-xx` com dono e data no `prd.md`; a etapa fica em andamento. Diga o que
   perguntar e a quem, e pare: rodar `/pp:arquitetura` de novo retoma daqui.
2. **Fatos do ambiente** que o usuário já sabe, em perguntas curtas e com "Não sei": prefixo do
   publisher (Dataverse), servidor e banco **só pelo papel** ("banco de DEV"; nunca nome real no
   arquivo), quem cria tabela, se há ambientes DEV/HML/PRD.
3. **Agente.** Mostre `◆ Chamando o Agente de Arquitetura...` e chame `pp:agente-arquitetura` com
   `RAIZ`, `KIT` (o valor de `${CLAUDE_PLUGIN_ROOT}`), `TRILHA` e os fatos do passo 2.
   Modelo: `modelos.py de agente-arquitetura` (linha vazia: não passe `model`).
4. **Julgue a entrega** (`KIT/skills/power-platform/references/subagentes.md`, "Julgar a entrega"):
   - `power-platform.config.json` com `trilha_dados` (e `prefixo_publisher` no Dataverse);
   - `GOAL.md` com onda 0 (ambiente, 🔴) e as ondas de construção, cada tarefa com "pronto quando";
   - trilha SQL: `python "${CLAUDE_PLUGIN_ROOT}/skills/sql-procedures/scripts/lint-procedure.py"`
     sobre a pasta de procedures, `0 erro(s)`;
   - todo `RF-xx` P0 aparece em pelo menos uma tarefa do `GOAL.md` (rastreabilidade).
   Falta ou erro: revisão. Pergunta aberta que só o usuário responde: escalado. Registre com
   `estado.py veredito arquitetura --agente agente-arquitetura --resultado <...> --motivo "..."`.
5. **Preparar o ambiente** (checkpoint `Ação no ambiente`, 🔴). Mostre a onda 0 do `GOAL.md` como
   passo a passo:
   - SQL: entregar o pacote ao DBA ou rodar os scripts no banco de DEV, na ordem do pacote;
   - Dataverse: criar as tabelas e colunas no maker conforme o modelo;
   - nos dois: capturar os nomes reais no `AMBIENTE-AS-BUILT/NOMES-AS-BUILT.md`. No Dataverse, o
     export de `EntityDefinitions` + `extrair-nomes-as-built.py` da skill `dataverse` gera o arquivo.
   Diga que isso pode levar dias (DBA, TI) e que **a construção só começa com o `NOMES-AS-BUILT`
   preenchido**: o `/pp:construir` confere antes de escrever qualquer tela.

## Portão de saída

- [ ] ADR da trilha em `docs/decisoes/ADR-001.md`; config e `00-LEIA-PRIMEIRO.md` com a mesma trilha.
- [ ] `arquitetura.md` com modelo de dados, matriz de permissões (flags), integrações e o contrato
      de cada fluxo (parâmetros posicionais e retorno `{status, description, id, url}`).
- [ ] Scripts de dados prontos (SQL com `lint-procedure.py` em `0 erro(s)`; Dataverse com o modelo
      de tabelas e security roles).
- [ ] `GOAL.md` em ondas, com rastreabilidade de todo RF P0.

## Encerrar

1. `estado.py concluir arquitetura --nota "trilha <trilha>; <N> ondas no GOAL.md"`.
2. Commit se `git_commit_por_etapa`: `pp(arquitetura): modelo, contrato e fila de construção`.
3. Resumo (trilha, ondas, o que o humano precisa fazer no ambiente e com quem) e o bloco "Próximo
   passo" que o script imprimiu.

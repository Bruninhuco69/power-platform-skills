# Protocolo de trabalho

Mapear → Planejar → Executar → Validar → Reportar. Vale para toda tarefa com mais de um passo em
app existente. App novo segue o pipeline `/pp:*` (`pipeline.md`), que já embute estas fases.
Cada fase tem um **critério de saída**: sem ele a fase não terminou.

## Ordem de dependência entre camadas

```
dados (tabela / procedure / ambiente)  →  ( frontend  ∥  automação )  →  QA
```

- **Dados primeiro.** Tabela, coluna, procedure e connection reference existem e estão em
  `NOMES-AS-BUILT` antes de qualquer tela ou flow que as use.
- **Frontend e automação em paralelo** quando o contrato app↔flow está fechado (parâmetros
  posicionais, formato `{ status, description, id, url }` — ver `decisoes-padrao.md` §2).
- **QA por entrega**, não só no fim: cada tela e cada flow passa pelo portão antes da próxima onda.
- Se a camada de dados não está pronta, a tarefa de tela vira 🔴 (depende de ambiente) na fila.

## Fase 1 — Mapear

Faça sempre. Produz um mapa curto, não uma opinião.

- Identifique: tela e prefixo de nomes, fonte de dados e colunas, flows chamados, procedures,
  ambiente (DEV/HML/PRD) em que o dado vive.
- Localize com `Grep` (`output_mode: content`) e leia com `offset`/`limit`. Arquivo de tela grande
  nunca é lido inteiro.
- Confira nomes contra `NOMES-AS-BUILT`. Antes de afirmar que uma coluna não existe, abra o esquema da
  tabela — nunca um extrato filtrado (N3).
- Procure o que já existe antes de criar: bloco canônico, molde, componente.

**Saída:** lista de arquivos/controles/ações envolvidos, cada um com o comando que o achou; lista do
que é inferido e não confirmado.

## Fase 2 — Planejar

- No máximo 5 passos, em ordem de dependência.
- Diga o que **não** será feito e por quê.
- Ambiguidade que muda o resultado: decida, **declare a suposição** e siga. Pergunte só se errar
  tornar o trabalho inútil.
- Marque cada passo como 🟢 (você produz arquivo) ou 🔴 (humano executa no ambiente).
- Se muda trilha, contrato ou padrão: escreva o ADR antes (`assets/adr-molde.md`).

**Saída:** plano numerado + suposições + fora de escopo. Projeto que entrou sem o pipeline: `GOAL.md`
a partir de `assets/goal-molde.md` e ADRs das decisões já tomadas.

### Planejar um projeto novo (kickoff)

Antes da primeira tela, feche e registre (ADR ou `00-LEIA-PRIMEIRO.md`):

1. Trilha de dados (`sql-server` **ou** `dataverse`) e por quê.
2. Ambientes (DEV/HML/PRD), publisher/prefixo, quem cria tabela e quem é o DBA.
3. Perfis e escopo por unidade; onde a autorização é decidida (no flow — A3).
4. Premissas de compliance, licença e gateway; cada uma com dono e data-limite.
5. Quando o banco congela e o que ainda cabe depois (coluna calculada costuma caber; tabela nova, não).
6. Capacidade real da equipe e o que é 🔴 (ambiente) — o plano precisa caber nela.
7. `git init` no dia 0 e `power-platform.config.json` na raiz.

## Fase 3 — Executar

- Uma camada por vez, na ordem de dependência.
- Reutilize molde e bloco canônico das skills de domínio antes de escrever do zero.
- Respeite o destino de cada bloco de código: barra de fórmulas pt-BR (`;` `;;`) ou YAML colado
  (`,` `;`) — `decisoes-padrao.md` §3.
- Saída de gerador só em `dist/`; correção manual vai para a entrada do gerador ou vira gabarito.
- Mudança que quebra contrato (parâmetro de `.Run()`, retorno do flow): parâmetro novo **no fim**;
  atualize tela e flow na mesma tarefa.

**Saída:** arquivos alterados listados; nada gerado sobre gabarito.

## Fase 4 — Validar (portão obrigatório)

Rode `references/portao-final.md`. Em resumo:

1. Todos os validadores das skills envolvidas, não só um.
2. Cada um com `0 erro(s)` — e você sabe o que ele **não** cobre.
3. Checklist manual (delegação declarada, nomes conferidos, loading/vazio/erro, sem literal de ambiente).
4. Tela ou flow: colar no Studio/designer, ou registrar 🔴.

Falhou: corrija e rode de novo. **Duas falhas pela mesma causa** = erro de plano; pare, diga o que
mudou na hipótese e reabra a Fase 2.

**Saída:** saída literal de cada validador (última linha) + resultado do checklist.

## Fase 5 — Reportar

Quatro itens, nesta ordem:

1. O que mudou, em uma frase.
2. **Como aplicar:** barra de fórmulas / YAML colado em qual controle-pai / designer / solução.
3. Avisos: delegação, teto 500/2000, variável não inicializada, custo de chamadas.
4. O que ficou de fora e por quê; o que está 🔴 e com quem.

Relate o que falhou com a evidência (validador que acusou, agente que errou, dado que não existe).
Relatório otimista custa caro depois.

**Saída:** relatório com evidência; fila atualizada se houver `GOAL.md`.

## Entrega de feature de ponta a ponta

1. **Dados:** a tabela/procedure e as colunas existem? Se não, é 🔴 ou pedido ao DBA; não invente nome.
2. **Contrato:** defina parâmetros do `.Run()` e o retorno antes de tela e flow.
3. **Fórmula/fonte:** a consulta delega? Resolva agora (coluna calculada, `Ref_*`), não depois da tela.
4. **Flow e tela em paralelo**, cada um pela sua skill de domínio.
5. **Estado e erro:** loading, vazio, erro, toast ligado ao `status`.
6. **Portão final.**

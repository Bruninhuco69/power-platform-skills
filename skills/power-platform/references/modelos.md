# Modelos: quem pensa e quem executa

O pipeline separa **a cabeça** (a sessão de cada etapa: conversa com o usuário, define o pedido,
julga o que volta) **das mãos** (os agentes: escrevem tela, fluxo, protótipo e spec, e provam o que
fizeram). Pensar, julgar e segurar a régua é a fatia pequena do trabalho; escrever, rodar e corrigir
é a fatia grande. Por isso a cabeça pode ficar no modelo mais forte e as mãos num mais rápido e
barato, sem perder qualidade, **desde que o julgamento rode** (`subagentes.md`, "Julgar a entrega").

O perfil é escolhido no `/pp:novo` e gravado pelo `scripts/modelos.py`.

## 1. Perfis

| Perfil | Sessão de cada etapa | Arquitetura e QA | Mockups, protótipo, telas e fluxos | Quando |
|---|---|---|---|---|
| **Equilibrado** (recomendado) | Opus | Opus | Sonnet | quase sempre: o forte pensa e julga, o rápido executa |
| **Máximo** | `best` | Opus | Opus | app crítico ou time sem paciência para revisão; custa mais |
| **Econômico** | Sonnet | Sonnet | Sonnet | protótipo descartável, cota apertada; espere mais revisões |
| **Herdar** | o modelo em que a sessão abrir | idem | idem | quem já controla o modelo por conta própria |

`best` usa o Fable se a conta tem acesso, senão o Opus. Só vale para a sessão: agente aceita
`fable`, `opus`, `sonnet` e `haiku`.

`python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/modelos.py" perfis` imprime os perfis
no formato da prévia do `/pp:novo`.

## 2. Como é aplicado

| Onde | Como | Quem passa por cima |
|---|---|---|
| Sessão de cada etapa | `"model"` no `.claude/settings.local.json` do projeto: o Claude Code lê ao abrir a sessão na pasta. Como cada etapa é sessão nova, a escolha vale sozinha | `/model` na sessão, `--model` e a variável `ANTHROPIC_MODEL` |
| Cada agente | a etapa roda `modelos.py de <agente>` e passa a resposta como `model` na chamada; linha vazia = não passe `model` (herda a sessão) | nada: o `model` da chamada vence o frontmatter do agente |
| Esforço de raciocínio | `effort: high` no frontmatter de `agente-arquitetura` e `agente-qa` (planejam e julgam); os outros herdam o da sessão | `effort` da sessão não vence o do agente |

O plugin **não troca o modelo no meio de uma sessão**: o `model:` de uma skill vale só para o turno.
Por isso o "Próximo passo" lembra o modelo e o `/model` certo.

O `settings.local.json` é pessoal (cada um tem a sua conta e o seu acesso): o `modelos.py` põe a
linha no `.gitignore`. A escolha do time fica no `power-platform.config.json` (`modelos`).

## 3. Trocar depois

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/modelos.py" aplicar equilibrado --execucao opus
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/modelos.py" mostrar
```

`--sessao`, `--planejamento` e `--execucao` trocam um papel por cima do perfil. Vale a partir da
próxima sessão (a atual continua no modelo em que abriu; `/model` troca na hora).

## 4. Medir: o perfil está dando conta?

A coluna **Julgamento** do `ESTADO.md` (e do `/pp:progresso`) conta os vereditos por etapa: `✓`
aceito, `↻` revisão, `⚠` escalado.

| Sinal | O que fazer |
|---|---|
| construção com mais de uma revisão por onda, em média | `aplicar <perfil> --execucao opus` |
| revisões pela mesma causa (ex.: propriedade que o Studio recusa) | o problema é o pedido ou a skill, não o modelo: corrija o pedido |
| `⚠` frequente na arquitetura | falta decisão no PRD: volte ao usuário, não troque modelo |
| nenhuma revisão em várias ondas | o perfil pode descer (`economico`) se custo pesa |

## 5. Cuidados

- O YAML de tela é o arquivo mais frágil do kit: é onde um modelo menor erra primeiro. Os
  validadores pegam a sintaxe; o julgamento e a colagem no Studio pegam o resto.
- Modelo forte na mão não substitui o julgamento: a sessão julga em qualquer perfil.
- Nenhum perfil muda o que vai para fora: a API de imagens dos mockups continua só com o "pode gerar".

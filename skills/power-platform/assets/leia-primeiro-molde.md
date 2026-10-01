# <PROJETO> — leia primeiro

**Ideia:** <a ideia em uma frase>
**Onde o projeto está:** `ESTADO.md` (atualizado a cada etapa). Para continuar, abra o Claude Code
nesta pasta e rode `/pp:progresso`: ele mostra o próximo comando.

## Trilha ativa por camada

| Camada | Trilha | Pasta | Desde |
|---|---|---|---|
| Dados | <a definir na arquitetura: `sql-server` ou `dataverse`> | <pasta> | <data> |
| Telas | Power Apps Canvas (`.pa.yaml`) | <`pastas.telas` do config> | <data> |
| Fluxos | Power Automate (clipboard do designer) | <`pastas.flows` do config> | <data> |

Uma trilha por camada. Trocar exige ADR em `docs/decisoes/` e atualiza esta tabela,
`power-platform.config.json` e o `GOAL.md` no mesmo commit.

## Ordem de leitura

1. `ESTADO.md` — etapa atual e próximo comando.
2. `docs/planejamento/prd.md` — o que o app faz e o MVP.
3. `docs/planejamento/arquitetura.md` e `docs/decisoes/` — como e por quê (depois da etapa 6).
4. `GOAL.md` — a fila de construção (depois da etapa 6).
5. `AMBIENTE-AS-BUILT/NOMES-AS-BUILT.md` — nomes reais do ambiente; ganha de qualquer plano.

## Pastas

| Pasta | Conteúdo |
|---|---|
| `docs/planejamento/` | brainstorm, PRD, design system, inventário de telas, mockups, protótipo, arquitetura |
| `docs/decisoes/` | ADRs |
| `docs/qa/` | relatórios de teste e de homologação |
| `docs/entrega/` | manual do usuário, guia técnico, checklist de go-live |

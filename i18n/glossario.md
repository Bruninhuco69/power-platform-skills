# Glossário pt-BR → en-US

O mesmo nome em todo o kit en-US: skills, agentes, scripts, README, site e PDF. Caminho de arquivo do
kit está em `i18n/mapa.json`; aqui ficam os nomes que não são arquivo do kit.

## Comandos e agentes

| pt-BR | en-US |
|---|---|
| plugin `pp`, `/pp:*` | plugin `pp-en`, `/pp-en:*` |
| `/pp:novo`, `brainstorm`, `design`, `mockups`, `prototipo`, `arquitetura` | `/pp-en:new`, `brainstorm`, `design`, `mockups`, `prototype`, `architecture` |
| `/pp:construir [app\|flows]`, `testar`, `homologar`, `publicar` | `/pp-en:build [app\|flows]`, `test`, `uat`, `publish` |
| `/pp:progresso`, `/pp:mudanca` | `/pp-en:progress`, `/pp-en:change` |
| `pp:agente-mockups`, `agente-prototipo`, `agente-arquitetura`, `agente-sql` | `pp-en:mockups-agent`, `prototype-agent`, `architecture-agent`, `sql-agent` |
| `pp:agente-canvas`, `agente-automate`, `agente-qa`, `agente-pesquisa` | `pp-en:canvas-agent`, `automate-agent`, `qa-agent`, `research-agent` |
| skills de domínio `power-platform`, `powerapps-canvas`, `power-automate`, `sql-procedures`, `dataverse` | os mesmos nomes |

## Arquivos que o kit cria no projeto do usuário

| pt-BR | en-US |
|---|---|
| `ESTADO.md` | `STATE.md` |
| `power-platform.config.json` (chaves iguais) | `power-platform.config.json` (chaves iguais) |
| `00-LEIA-PRIMEIRO.md` | `00-READ-ME-FIRST.md` |
| `docs/planejamento/` | `docs/planning/` |
| `ideia-bruta.md`, `brainstorm.md`, `prd.md` | `raw-idea.md`, `brainstorm.md`, `prd.md` |
| `ux-design-system.md`, `identidade.html` | `ux-design-system.md`, `identity.html` |
| `inventario-telas.md`, `mockups.json`, `mockups/`, `mockups.md` | `screen-inventory.md`, `mockups.json`, `mockups/`, `mockups.md` |
| `docs/planejamento/prototipo/index.html`, `ajustes-prototipo.md` | `docs/planning/prototype/index.html`, `prototype-adjustments.md` |
| `arquitetura.md`, `GOAL.md` | `architecture.md`, `GOAL.md` |
| `NOMES-AS-BUILT.md` | `AS-BUILT-NAMES.md` |
| `carga-mockup.json`, `.xlsx`, `.sql`, `carga-mockup-tabelas/` | `mockup-load.json`, `.xlsx`, `.sql`, `mockup-load-tables/` |
| `construtor-dataverse/` (`plano-dataverse.json`, `construtor-escopo.json`) | `dataverse-builder/` (`dataverse-plan.json`, `builder-scope.json`) |
| `docs/qa/QA-<data>.md`, `docs/qa/UAT-<data>.md`, `docs/qa/correcoes.md` | `docs/qa/QA-<date>.md`, `docs/qa/UAT-<date>.md`, `docs/qa/fixes.md` |
| `docs/mudancas/MUD-<NNN>.md` | `docs/changes/CHG-<NNN>.md` |
| `docs/entrega/` (`manual-usuario.md`, `guia-tecnico.md`, `GO-LIVE-CHECKLIST.md`) | `docs/delivery/` (`user-manual.md`, `technical-guide.md`, `GO-LIVE-CHECKLIST.md`) |

## Termos

| pt-BR | en-US |
|---|---|
| etapa, bloco, sessão, onda | stage, block, session, wave |
| Próximo passo, Também disponível | Next step, Also available |
| unidade, perfil (de acesso), escopo | unit, role, scope |
| homologação | user acceptance (UAT) |
| protótipo navegável, mockup em imagem | clickable prototype, image mockup |
| trilha de dados | data track |
| carga mockup, construtor (Dataverse) | mockup load, builder (Dataverse) |
| veredito: aceito, revisão, escalado | verdict: accepted, revision, escalated |
| entrega, molde, gabarito, lições de campo | delivery, template, baseline, field lessons |
| concluída, em andamento, pendente, dispensada, reaberta | done, in progress, pending, skipped, reopened |
| N erro(s), M aviso(s) | N error(s), M warning(s) |

## Código

- Power Fx en-US: `,` separa argumento, `;` encadeia, `.` decimal. YAML colado (`.pa.yaml`) é igual
  nos dois idiomas.
- Nome de coluna, tabela, variável, chave de JSON e código fica igual; traduzem comentário e texto.
- Scripts: um só código (`_idioma.py`). Subcomando, opção e valor de opção ficam como no pt-BR
  (`estado.py concluir`, `--motivo`, `--resultado aceito`); o `estado.py` aceita também o id en-US da
  etapa (`estado.py comecar new`).

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
| `NOMES-AS-BUILT.md`, `AMBIENTE-AS-BUILT/` | `AS-BUILT-NAMES.md`, `AS-BUILT-ENVIRONMENT/` |
| `docs/decisoes/ADR-<NNN>.md` | `docs/decisions/ADR-<NNN>.md` |
| `Backend/Dataverse/modelo-tabelas.md` | `Backend/Dataverse/table-model.md` |
| `ajustes-prototipo.md`: classes `identidade`, `tela`, `comportamento`; situação `feito` | classes `identity`, `screen`, `behavior`; status `done` |
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
| requisito `RF-xx`, regra de negócio `RN-xx`, `[SUPOSIÇÃO]` | requirement `FR-xx`, business rule `BR-xx`, `[ASSUMPTION]` |
| entidades de exemplo `Pedido`, `Unidade` (no texto e nos moldes) | `Order`, `Unit` (o nome físico SQL fica: `dbo.Unidade`) |

## Código

- Power Fx en-US: `,` separa argumento, `;` encadeia, `.` decimal. YAML colado (`.pa.yaml`) é igual
  nos dois idiomas.
- Nome de coluna, tabela, variável, chave de JSON e código fica igual; traduzem comentário e texto.
- Código colado (JSON de flow, YAML de tela, SQL) é o mesmo do pt-BR: dentro dele, o marcador
  (`<prefixo>_`, `<SIGLA>_<Entidade>`, `<conta_do_conector>`) e o nome de exemplo (`Pedidos`,
  `situacao`, `dbo.Unidade`) ficam; muda só comentário e texto ao usuário. Literal que é código
  (`'GRAVADO'`, `N'aberto'`, `'TokenInvalido'`) fica. Na prosa, marcador descritivo vai para o inglês
  (`<YYYY-MM-DD>`, `<environment>`). Os testes `tests/_i18n/` conferem JSON, YAML e SQL contra o pt-BR.
- Componente do catálogo Canvas tem nome en-US, o do arquivo do catálogo (`cabecalho-tela` →
  `screen-header`; a lista é o `_CATALOGO_EN` do `verificar-prototipo.py`). Ficam como no pt-BR, porque
  script lê: id de padrão de navegação (`lateral-fixo`, `gaveta`, `inicio-cartoes`…), chave de perfil
  (`gestor`, `operador`, `?perfil=`) e chave de `modelos.agentes` no config (`agente-*`). Fica também,
  por ser nome de coluna, a convenção de flag de permissão `Flg_Pode<X>`.
- Entrada da etapa para o agente: a chave fica (`RAIZ`, `KIT`, `TRILHA`, `TELAS`, `FLUXOS`,
  `CORRECOES`, `MUDANCA`, `MODO`, `TOKENS`, `ONDE`, `PARA QUE`), o valor é em inglês (`TOKENS: yes`,
  `MODO: new | adjustment`, `ONDE: project | web | both`). Nos scripts, o agente pelo nome en-US
  (`modelos.py de qa-agent`, `estado.py veredito test --agente qa-agent`) e a etapa pelo id en-US.
- Scripts: um só código (`_idioma.py`). Subcomando, opção e valor de opção ficam como no pt-BR
  (`estado.py concluir`, `--motivo`, `--resultado aceito`); o `estado.py` aceita também o id en-US da
  etapa (`estado.py comecar new`).

# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Versão: semver.

## [0.2.0] — 2026-10-01

Pipeline guiado: da ideia ao app publicado, um comando por etapa, uma sessão nova por etapa, no
estilo do GSD. O plugin passa a se chamar `pp` (comandos `/pp:*`).

### Adicionado
- **11 skills de etapa**, só invocadas pelo usuário (`disable-model-invocation`): `/pp:novo`,
  `/pp:brainstorm`, `/pp:design`, `/pp:mockups`, `/pp:prototipo`, `/pp:arquitetura`,
  `/pp:construir [app|flows]`, `/pp:testar`, `/pp:homologar`, `/pp:publicar` e `/pp:progresso`.
- **6 agentes do pipeline** em `agents/`: `agente-mockups`, `agente-prototipo`, `agente-arquitetura`,
  `agente-canvas`, `agente-automate` (os dois em paralelo na construção) e `agente-qa`. Ferramentas
  mínimas por agente: o de mockups não tem Bash (não chega à API de imagens), o de QA não escreve.
- `power-platform/scripts/estado.py` + testes: o `ESTADO.md` do projeto (etapas feitas, em
  andamento, reabertas, dispensadas), a ordem das etapas e o bloco "Próximo passo", que manda abrir
  uma sessão nova. As voltas do desenho: protótipo com ajuste → `/pp:design`; teste ou homologação
  com falha → `/pp:construir app` ou `flows`.
- `references/pipeline.md` (desenho, etapas, voltas, arquivos) e `references/formato-saida.md`
  (banner, checkpoints, próximo passo).
- Protótipo navegável no fluxo: `assets/prototipo-molde.html` + `scripts/verificar-prototipo.py`
  (V001–V013), agora ligados à etapa `/pp:prototipo` e documentados.
- **Quatro modos de brainstorm** com personas (`references/brainstorm-modos.md`): entrevista guiada
  (🧠 Facilitador), foco nas pessoas (🎨 design thinking), foco no problema (🔬 causa raiz) e mesa
  redonda (várias personas debatem, uma pergunta por rodada). A abertura muda; o fechamento (MVP,
  regras, bloqueadores, `prd.md`) é o mesmo. Inspirados no módulo criativo e no *party mode* do BMAD.
- `assets/leia-primeiro-molde.md`; chaves `pastas.prototipo` e `git_commit_por_etapa` no config.

### Mudado
- Plugin renomeado de `power-platform-kit` para `pp` (o marketplace continua `power-platform-kit`:
  `/plugin install pp@power-platform-kit`).
- O orquestrador `power-platform` coordena o pipeline e mantém os modos de app existente
  (investigar, auditar, feature, promover, portão final).
- Brainstorm, brief e PRD viram uma etapa só (`/pp:brainstorm`): o PRD ganhou visão e escopo do MVP.
  Perguntas fechadas por `AskUserQuestion`, com a opção recomendada primeiro.
- O design system virou etapa de conversa com amostra visual (`identidade.html`).
- `/goal` deixou de ser modo do kit (é comando nativo do Claude Code): a fila `GOAL.md` é andada pelo
  `/pp:construir`, uma onda por sessão.
- `nomes_as_built` padrão em `AMBIENTE-AS-BUILT/NOMES-AS-BUILT.md`.
- README, site (`docs/index.html`, GitHub Pages) e descrições do plugin em **pt-BR**, como as
  skills; a versão em inglês fica para depois.
- Licença MIT (`LICENSE`), também declarada no `plugin.json`.

### Removido
- Agente `arquiteto-telas` (virou `agente-mockups`).
- Prompts de papel `analista`, `pm`, `arquiteto`, `sm`, `qa` e o modo "definir" do `ux` (viraram
  skills de etapa e agentes). Ficam os prompts de auditoria: `ux`, `dev`, `performance`, `dados`,
  `flow`, `sql`.
- `references/metodo-bmad.md` (o essencial foi para `pipeline.md` §7), `assets/brief-molde.md`,
  `historia-molde.md` e `readiness-checklist.md` (a prontidão é conferida pelo `agente-arquitetura`).

## [0.1.0] — 2026-10-01

Primeira versão. Consolida em skills genéricas o que dois projetos Power Platform em produção
aprenderam sobre Canvas, Power Automate, SQL Server e Dataverse.

### Adicionado
- Estrutura do plugin (`.claude-plugin/plugin.json`, `marketplace.json`).
- `docs/PADRAO-SKILL.md` (padrão de toda skill) e `docs/CONFIG.md` (`power-platform.config.json`).
- `tools/lint_skills.py` — padrão + sanitização, com testes em `tests/_lint/`.
- `power-platform` — orquestrador: roteador, protocolo, modo investigar, fila `/goal`, subagentes,
  ALM/ambientes, salvaguardas, portão final; `references/decisoes-padrao.md` como fonte única dos padrões.
- `powerapps-canvas` — YAML colável, Power Fx, delegação, chamada de flow, escopo/permissão, UX,
  tokens, acessibilidade, PA2108; `scripts/validar-telas.py` (20 regras, T001–T022 sem T019/T021), que lê YAML puro e cercado.
- `power-automate` — anatomia do flow, contrato com o app, autorização, clipboard do designer, R1–R13,
  armadilhas de WDL, SQL, HTTP, `$batch`, log; `scripts/verificar-fluxo.py` (F001–F019).
- `sql-procedures` — padrão de procedure (declarativa × clássica), contrato com o flow, modelo de dados,
  colunas calculadas, escopo, segurança, DBA, migração; `scripts/lint-procedure.py` (P001–P011).
- `dataverse` — nomes e tipos, NOMES-AS-BUILT, delegação, segurança, modelagem, importação;
  `scripts/extrair-nomes-as-built.py`.
- Ciclo de projeto novo **inspirado no BMAD** no `power-platform`: brainstorm → brief → PRD → design
  system → inventário de telas → arquitetura → histórias → readiness; roteiro de brainstorm de Power
  Platform, matriz Dataverse × SQL Server, 7 moldes de artefato e prompts de papel (analista, PM, UX,
  arquiteto, SM, QA). Usa os agentes do BMAD quando ele está instalado no projeto.
- Catálogo de componentes Canvas (`powerapps-canvas/assets/componentes/`, 23) e de blocos de flow
  (`power-automate/assets/componentes/`, 34), cada um colável e validado por teste.
- `references/licoes-de-campo.md` nas skills de domínio.
- **Fase 4 com mockups:**
  - O agente do plugin `agents/arquiteto-telas.md` (arquiteto de sistemas) elenca as páginas e a
    moldura do app: header, navegação, notificações, pop-ups, loading e estados.
  - O script `power-platform/scripts/desenhar-mockups.py` gera uma imagem por tela com a API de
    imagens da OpenAI e a paleta do design system.
    - Exige `OPENAI_API_KEY`.
    - O modelo é variável: `--modelo` > `OPENAI_IMAGE_MODEL` > `mockups.modelo` > `gpt-image-2`.
    - `--simular` roda sem chave e sem rede.
    - Teto de imagens por execução.
    - Recusa e-mail real no spec.
  - Novos: `references/mockups.md`, `assets/mockups-molde.json` e o bloco `mockups` no config.
  - Atualizados: inventário com moldura, mapa de navegação e mockup por tela; perguntas 3.9 e 7.9
    do brainstorm; item 18 da readiness.
  - Testes em `tests/power-platform/`.

### Mudado
- Conteúdo 100% genérico: sem empresa, projeto, domínio de negócio, telas, siglas, contagens ou datas
  de origem; exemplos com a entidade neutra `Pedido` e o escopo `Unidade`. Paleta do molde trocada pela
  rampa azul padrão do Fluent 2, com o contraste recalculado.
- Lint: `OneDrive` só é acusado como caminho; anotação OData (`x@odata.bind`) não é e-mail.
- README e descrições do plugin em inglês, com passo a passo de instalação, ciclo de projeto novo,
  construção, validação e `/goal`.
- Repassada de qualidade nas 5 skills:
  - **Fatos corrigidos com a Microsoft Learn:**
    - `$count` do Dataverse satura em 5.000;
    - limites de alternate key;
    - `Mod` não delega no SQL;
    - o rollback de solução gerenciada exige versão maior;
    - `Response` só existe em flow com gatilho HTTP ou Power Apps.
  - **Canvas:**
    - `exportar` passa data ao flow como texto ISO;
    - `Text()` de contagem usa `[$-en-US]` no formato;
    - `fxFont` em vez de `Font.'Segoe UI'` literal;
    - contraste do placeholder corrigido.
  - **Power Automate:** autorização não depende de curto-circuito de `and`/`or`; nomes de connection
    reference unificados (`<prefixo>_sharedsql`).
  - **Orquestrador:**
    - primeiro passo de projeto novo explícito;
    - linha de delegação no roteador;
    - `AMBIENTE-AS-BUILT/` sem prefixo numérico.
  - **Generalização:**
    - frequência dos catálogos sem contagem de projeto (`muito comum`/`comum`/`ocasional`/`rara`);
    - marcas `[verificado: projeto de referência]` sem data;
    - "filial" → "unidade".


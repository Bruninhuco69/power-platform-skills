# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Versão: semver.

## [Não lançado]

### Adicionado
- **Base bilíngue pt-BR/en-US.**
  - **Plugin `pp-en`** na pasta `en/` (`en/.claude-plugin/plugin.json`, mesma versão do `pp`), listado
    no `marketplace.json` ao lado do `pp`. Ainda sem skills.
  - **`i18n/mapa.json`:** cada arquivo de `skills/` e `agents/`, mais README, site, diagrama e PDF, com
    o caminho en-US (nomes em inglês: `/pp-en:new`, `research-agent`, `references/field-lessons.md`…)
    e a situação, `feito` ou `pendente`.
  - **Lint L014** (paridade): arquivo pt-BR sem entrada no mapa ou entrada `feito` sem o arquivo
    en-US é erro; `pendente` é aviso, e o lint imprime `N pendente(s) de tradução` antes do total.
  - **`README.en.md`**, tradução do README com Power Fx en-US; os dois READMEs apontam um para o
    outro no topo, e a instalação do `pp-en` fica "coming soon" até o plugin ter skills.
  - **`CLAUDE.md`** na raiz: toda alteração nas duas línguas, o mapa, Power Fx por idioma e as três
    checagens antes de commitar.
- **Site, diagrama 3D e PDF em en-US.**
  - **`docs/en/index.html`:** o site traduzido, com o mesmo layout, tokens e temas claro/escuro. Os
    dois sites ganham um seletor de idioma (PT · EN) no menu e `hreflang`; no celular (abaixo de
    480 px) o botão do GitHub sai do menu, que o herói já tem o link.
  - **Diagrama 3D:** `docs/diagrama/index.html?lang=en` troca rótulos, estampas
    (`new` … `publish`), voltas (`/pp-en:design`, `build`, `/pp-en:change`), legenda e título. Sem o
    parâmetro, a imagem é a mesma de antes, pixel a pixel. Imagens novas `docs/img/pipeline-en-claro.webp`
    e `pipeline-en-escuro.webp` no topo do `README.en.md`.
  - **`docs/Power-Platform-Kit.en.pdf`:** a apresentação de 4 páginas A4 em inglês, com miniaturas
    `docs/img/pdf-en-1.jpg` a `-4.jpg` no `README.en.md`.
  - O `README.en.md` aponta para o site, o diagrama e o PDF em inglês; o mapa marca os três como
    `feito`.
- **Scripts em en-US** (parte a do plugin `pp-en`).
  - **Um código só:** cada script das skills escreve as mensagens em `tr("pt", "en")` e escolhe o
    idioma pelo `plugin.json` acima dele (`pp` fala pt-BR, `pp-en` fala inglês) ou pela variável
    `PP_LANG` (`_idioma.py`, igual nas cinco skills). No en-US o resumo é `0 error(s), 0 warning(s)`,
    o nível aparece como `ERROR`/`WARNING` e os arquivos gerados têm nome em inglês (`STATE.md`,
    `mockup-load.sql`, `dataverse-builder/`…). Subcomando, opção e chave de JSON ficam iguais; o
    `estado.py` aceita também o id en-US da etapa (`comecar new`).
  - **`tools/sincronizar_en.py`** copia `skills/*/scripts/*.py`, idênticos, para a pasta en-US de cada
    skill e marca o mapa; `--conferir` só confere. O teste falha se uma cópia dessincronizar.
  - **`i18n/glossario.md`:** comandos, agentes, arquivos que o kit cria e termos em en-US.
  - Testes novos em `tests/_i18n/`: cópias idênticas, idioma por plugin e por `PP_LANG`, `--help`
    de cada script sem português e a saída en-US dos validadores, do `estado.py`, da carga mockup e
    dos nomes as-built. A saída pt-BR não muda.
- **Skill `power-platform` em en-US** (parte b do plugin `pp-en`).
  - **`en/skills/power-platform/`:** o `SKILL.md`, as 20 referências, os 6 prompts de revisão e os
    14 moldes em inglês, com os nomes do mapa (`references/mockup-load.md`,
    `assets/prd-template.md`…), comandos `/pp-en:*`, agentes `pp-en:*-agent` e os arquivos do projeto
    em inglês (`STATE.md`, `docs/planning/`, `AS-BUILT-ENVIRONMENT/`).
  - **Moldes que os scripts leem:** o `assets/dataverse-builder.json` tem o mesmo código do
    construtor pt-BR e só troca título, descrição e o texto do relatório (`done`, `already existed`,
    `not run`); o `mockup-load-template.json`, o `mockups-template.json` e o `prototype-template.html`
    passam limpos nos scripts en-US, com os componentes do catálogo Canvas pelo nome en-US
    (`screen-header`…). Chave de config, id de padrão de navegação e chave de perfil ficam como no
    pt-BR, porque script lê.
  - **`i18n/glossario.md`:** `AMBIENTE-AS-BUILT/`, `docs/decisoes/`, `RF-`/`RN-`, entidades de
    exemplo e o que fica igual no código.
  - **Testes novos** em `tests/_i18n/test_skills_en.py`: cada skill en-US no padrão (description
    "Use when … Do not use", até 250 linhas, links que existem), todo arquivo en-US é par `feito` do
    mapa, nenhum `/pp:` nem agente pt no texto en-US, o construtor com o mesmo código do pt-BR e os
    moldes en-US nos scripts.
- **Etapas e agentes em en-US** (parte c do plugin `pp-en`).
  - **As 12 skills de etapa** (`en/skills/new`, `brainstorm`, `design`, `mockups`, `prototype`,
    `architecture`, `build`, `test`, `uat`, `publish`, `progress`, `change`): os comandos
    `/pp-en:*`, com o `estado.py` chamado pelo id en-US da etapa.
  - **Os 8 agentes** (`en/agents/*-agent.md`): o mesmo cabeçalho do pt-BR (`tools`, `color`,
    `effort`, que o `modelos.py` lê) e `skills` do `pp-en`.
  - **Entrada da etapa para o agente:** a chave fica (`RAIZ`, `TELAS`, `TOKENS`, `ONDE`…), o valor
    é em inglês (`TOKENS: yes`, `ONDE: both`); classes da rodada de ajustes `identity`, `screen`,
    `behavior`. O glossário registra.
  - Teste novo: cada agente en-US com o cabeçalho do pt-BR.
- **Skill `powerapps-canvas` em en-US** (parte d do plugin `pp-en`).
  - **`en/skills/powerapps-canvas/`:** o `SKILL.md`, as 16 referências, o molde de tela
    (`assets/screen-template.md`), o OnStart, os tokens e o catálogo de 25 componentes
    (`assets/components/`, com o nome en-US de cada um, o mesmo do `verificar-prototipo.py`).
  - **Power Fx por destino:** o que vai na barra de fórmulas (App.Formulas, App.OnStart, fórmula no
    texto) está em en-US (`,` separa, `;` encadeia, `.` decimal); o YAML colado tem o mesmo código do
    pt-BR e só troca texto visível e comentário (datas `mm/dd/yyyy`, `[$-en-US]`).
  - Tudo passa no `validar-telas.py` en-US como o pt-BR passa no pt-BR: o catálogo sem achado, o molde
    de tela sem achado e, na trilha SQL, só o T013.
  - Teste novo `tests/_i18n/test_powerapps_canvas_en.py`: o catálogo é o do `verificar-prototipo.py`,
    estrutura de cada componente, índice, erro plantado, tokens, e cada bloco YAML en-US com as
    mesmas chaves, controles, tipos e fórmulas do pt-BR.
- **Skill `power-automate` em en-US** (parte e do plugin `pp-en`).
  - **`en/skills/power-automate/`:** o `SKILL.md`, as 12 referências, o contrato e o molde de flow
    (`assets/flow-write-template.json`) e os 32 componentes (`.json` + `.md`) e 2 gatilhos
    descritivos em `assets/components/`, com o índice `INDEX.md`.
  - **O JSON colado tem o mesmo código do pt-BR:** nomes de ação, variável, parâmetro, coluna, os
    códigos (`GRAVADO`, `TokenInvalido`…) e as ações do switch (`gravar`/`excluir`) ficam; muda só a
    mensagem ao usuário, `description` e o sentinela `'(unresolved)'`. O CSV exportado usa `,` como
    separador (Excel en-US). Moldes de expressão Power Fx do app em en-US.
  - Tudo passa no `verificar-fluxo.py` en-US com os mesmos códigos do pt-BR (`0 error(s)`); o molde
    de gravação dá `0 error(s), 0 warning(s)`.
  - Teste novo `tests/_i18n/test_power_automate_en.py` (com `tests/_i18n/_fluxo.py`): mesmos
    componentes do pt-BR, cada um limpo no verificador en-US, `.md` com o mesmo JSON e as seções,
    índice completo, e cada JSON en-US com as mesmas chaves, tipos, expressões e GUIDs do pt-BR.
- **Skills `sql-procedures` e `dataverse` em en-US** (parte f; o plugin `pp-en` fica completo).
  - **`en/skills/sql-procedures/`:** o `SKILL.md`, as 9 referências e os 4 moldes (procedure de
    gravação, função de leitura, contrato e pedido de DDL ao DBA). O SQL é o mesmo do pt-BR: muda
    só comentário e texto; nomes, marcadores e códigos (`N'NAO_APLICADO'`) ficam. Tudo passa no
    `lint-procedure.py` en-US com `0 error(s), 0 warning(s)` e os mesmos objetos do pt-BR.
  - **`en/skills/dataverse/`:** o `SKILL.md`, as 7 referências e o molde `AS-BUILT-NAMES`, com o
    cabeçalho que o `extrair-nomes-as-built.py` en-US gera. A fórmula da barra está em en-US (`,`
    separa, `;` encadeia).
  - Teste novo `tests/_i18n/test_sql_dataverse_en.py` (com `tests/_i18n/_sql.py`): lint en-US limpo,
    cada arquivo com o mesmo SQL do pt-BR, fórmula do Dataverse sem `;` de argumento nem `;;`, e o
    molde as-built com o cabeçalho do script nos dois idiomas.
  - **`i18n/glossario.md`:** a regra do código colado (marcador e nome de exemplo ficam).
  - **READMEs e site:** sai o "em breve" do `pp-en`; o `README.en.md` instala com
    `/plugin install pp-en@power-platform-kit` e aponta o `pp` como a edição pt-BR.
- **Carga mockup das tabelas** (`skills/power-platform/scripts/montar-carga-mockup.py`,
  `references/carga-mockup.md`, `assets/carga-mockup-molde.json`), nas duas trilhas, no
  `/pp:arquitetura`.
  - **O que gera:** a partir do `carga-mockup.json`, um `.xlsx` com uma aba por tabela, na ordem de
    carga. Cada aba é uma tabela do Excel com o valor no tipo certo na célula: data como data, código
    com letra, decimal com fração, todas as opções da Choice.
  - **Dataverse:** a planilha cria as tabelas de uma vez pelo Power Query. A aba
    `Conferência de tipos` lista o que escolher e o que costuma vir errado. Toda execução avisa
    (C013, C014) que o Dataverse erra a tipagem e que Choice e Lookup chegam como texto.
    `--conferir <export.json>` compara os tipos criados com o modelo (C101–C105) antes do dado real.
    `--uma-por-tabela` grava um arquivo por tabela, para o assistente que lê só a primeira aba.
  - **SQL Server:** também o `carga-mockup.sql`, com `INSERT` em transação, guarda de reexecução e
    chave estrangeira por subconsulta, só para o banco de DEV.
  - **Onde entra:** o agente de arquitetura escreve o spec; a onda 0 do `GOAL.md` ganha a tarefa
    T-02a; as skills `dataverse` e `sql-procedures` apontam para a referência.
- **Construtor Dataverse** (`montar-carga-mockup.py --flow`, `references/construtor-dataverse.md`,
  `assets/construtor-dataverse.json`): a alternativa à planilha, sem dedução de tipo.
  - **O plano:** o spec vira o `plano-dataverse.json`, os pedidos à Web API na ordem: tabelas com o
    nome principal, colunas com o tipo do spec (Choice com as opções, Email, URL, Telefone, Numeração
    automática, Escolhas, Imagem, Arquivo), relacionamentos com a navegação fixada, publicação, as
    linhas mockup em `$batch` (lotes de até 100 linhas, um changeset cada, o filho já apontando para o ID fixo do pai) e
    as chaves alternativas. O plano não leva nada do ambiente: prefixo, valor de opção e idioma o flow
    lê da solução.
  - **O flow:** fixo, um por ambiente. Sai como solução não gerenciada (`.zip`, para importar) e como
    escopo para colar no designer. Roda um passo de cada vez, pula o que já existe (rodar de novo é
    seguro) e para no primeiro erro com o passo e o detalhe da Web API.
  - **Achados novos:** C016 (nome lógico), C017 (limite do Dataverse), C018 (prove com `--conferir`
    depois de rodar). No `/pp:arquitetura`, o usuário escolhe entre o construtor e a planilha.
  - **Ainda não verificado num ambiente real:** a importação do `.zip` e a execução (lista no §9 da
    referência).
  - **Relatório:** abre com o ambiente lido (solução, prefixo, prefixo de opção, idioma), tem uma linha
    por passo (`não executado` depois da falha), e a mensagem do erro é a primeira falha. O idioma cai
    para `1046` se a leitura vier vazia.
- **`verificar-fluxo.py` acusa o que cola em branco no designer novo**:
  - F020: condição de `If` em texto (ERRO) ou sem `and`/`or` na raiz (AVISO);
  - F021: `Inicializar variável` fora da raiz (ERRO na definição, AVISO no escopo colado);
  - F022: `@variables('x')` sozinho num campo colado (ERRO se a variável nasce no trecho);
  - F023: `Fazer até` com a condição em texto, no escopo colado.

  Os sintomas estão em `formato-clipboard.md` §7. O escopo do construtor passou a colar nessas
  formas.
- **Lições de Web API e importação** na skill `dataverse` (`licoes-de-campo.md` §7 e §8): `PUT` de
  coluna substitui a definição, `MergeLabels`, numeração de Choice pelo publisher, chave em `Failed`,
  `If-None-Match`, dono e data de criação; a importação da planilha trocou dia e mês.
- **Diagrama 3D em blocos** (`docs/diagrama/`, three.js, no site em `/diagrama/`): as dez etapas
  numa trilha de tabuleiro, com o orquestrador, os oito agentes, os pinos de onde você age no
  ambiente e as três voltas. O README mostra a cena como imagem, nos temas claro e escuro.
- **Apresentação em PDF** (`docs/Power-Platform-Kit.pdf`, 4 páginas), com miniaturas no README.

### Mudado
- **PDF en-US sem o aviso de `pp-en` em tradução** (página 1) e miniaturas `pdf-en-*.jpg` de novo;
  o site pt-BR ganha a regra que o en-US já tinha (`.install > * { min-width: 0; }`): o bloco de
  instalação rola por dentro em vez de alargar a página no celular (546 px → 390 px).
- **Datas da carga mockup só com dia 13 ou mais** (`data_base` padrão `2026-01-13`): se a importação
  trocar dia e mês, a linha é recusada em vez de entrar com a data errada.
- README com nova capa: diagrama, links rápidos, "Em 30 segundos", por que o kit existe e os
  problemas que ele evita. O Mermaid fica recolhido em "o mesmo diagrama em texto"; a skill de
  Power BI abre os próximos passos; "Como contribuir" convida a mandar pull request.
- **Duas línguas:** o kit passa a ser mantido em pt-BR e en-US, e toda alteração entra nas duas
  (README, "Como contribuir"). A versão en-US está em construção.

## [0.3.0] — 2026-10-02

Quem pensa não é quem executa: a sessão de cada etapa define o pedido e julga; os agentes fazem e
provam. Inspirado no guia ["The Fable Loop"](https://thomaslentine.com/fable-guide.html).

### Adicionado
- **Entrega padrão e veredito.** Todo agente fecha com Como verifiquei / Conformidade / Alertas /
  Confiança; a etapa dá um veredito por agente (aceito, revisão com pedido mais apertado, no
  máximo duas, ou escalado) e registra com `estado.py veredito`, que soma na coluna Julgamento do
  `ESTADO.md`. Erro no arquivo do agente volta para ele; a sessão não edita tela nem fluxo.
- **Perfis de modelo no `/pp:novo`** (`scripts/modelos.py`, `references/modelos.md`):
  equilibrado (Opus pensa, Sonnet executa), máximo, econômico e herdar. A sessão abre no modelo
  do `.claude/settings.local.json`; cada agente recebe o seu na chamada; arquitetura e QA com
  `effort: high`. Pasta, commits e modelos numa rodada só de perguntas.
- **`agente-pesquisa`**: só lê (projeto e documentação oficial) e devolve achado com fonte; usado
  no brainstorm (viabilidade, licença), na arquitetura, em erro de colagem desconhecido, no
  `/pp:mudanca` e na auditoria de app existente.
- **Verificação visual**: `scripts/capturar-telas.py` fotografa o protótipo (por tela, por padrão
  de navegação, por perfil) ou a amostra do design com o Chrome/Edge sem janela;
  `references/verificacao-visual.md` diz o que olhar. O protótipo aceita `?perfil=&nav=` na URL.
- **Ideia do jeito que vier**: o `/pp:novo` guarda frase, lista, texto ou print em
  `ideia-bruta.md`, e o brainstorm confirma em vez de perguntar do zero.
- **`agente-sql`**: escreve as procedures do spec da seção 4.1 da arquitetura, um por grupo, em
  paralelo. A construção divide a onda pela nova coluna Arquivos do `GOAL.md`: um agente Canvas
  por grupo de até 3 telas, um Automate por grupo de até 3 fluxos, no máximo 5 por mensagem.
- **`/pp:mudanca`**: lista de mudanças num app publicado, com escopo, perguntas numa rodada,
  pesquisa, um spec por frente (`docs/mudancas/MUD-<NNN>.md`), agentes em paralelo, julgamento,
  QA da mudança e a homologação reaberta para uma versão nova.

### Mudado
- O `agente-arquitetura` escreve o spec das procedures, não o corpo; o `agente-automate` não mexe
  mais em procedure.
- O resumo de toda etapa segue um formato só: entregue, verificado, revisado, com você, não
  verificado.

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
- **Escolha da navegação no `/pp:design`** (`references/navegacao.md`): menu lateral fixo,
  recolhível ou gaveta (hambúrguer), barra no topo ou tela inicial com cartões, perguntados em
  duas partes com prévia ASCII de cada opção. A decisão vai para o `ux-design-system.md` §2.1 e
  segue para mockups, protótipo (seletor "Navegação" para comparar ao vivo), construção e testes.
- Catálogo Canvas: variação **gaveta** no `menu-lateral` e dois componentes novos, `menu-topo` e
  `inicio-cartoes` (25 no total), com os tokens `fxTopNavHeight`, `fxTopNavItemWidth`,
  `fxHubCardWidth`, `fxHubCardHeight` e `fxFontSizeCardTitle`. Nível de maturidade novo,
  `novo` (ainda não visto em produção: confirme na colagem).

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


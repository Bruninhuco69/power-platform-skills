<div align="center">

🇧🇷 Português · [🇺🇸 English](README.en.md)

<a href="https://stage2dev.github.io/power-platform-skills/diagrama/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/img/pipeline-escuro.webp">
    <img src="docs/img/pipeline-claro.webp" width="100%" alt="O pipeline /pp montado em blocos: dez etapas numeradas em quatro blocos (definição, identidade, construção e entrega), o orquestrador de boné, os oito agentes de gorro colorido, os pinos vermelhos onde você age no ambiente e as três voltas: ajuste do protótipo, correção de teste e mudança com o app no ar">
  </picture>
</a>

# Power Platform Kit para Claude Code

**Da ideia em uma linha ao app publicado.**<br>
Power Apps Canvas + Power Automate, com SQL Server ou Dataverse: um comando guiado por etapa,
agentes que constroem e provam o que fizeram, e você só onde precisa de gente.

![versão](https://img.shields.io/badge/vers%C3%A3o-0.3.0-2563eb)
![comandos](https://img.shields.io/badge/comandos-%2Fpp%3A*-2563eb)
![claude code](https://img.shields.io/badge/Claude_Code-plugin-d97757)
![idioma](https://img.shields.io/badge/idioma-pt--BR-6b7280)
![licença](https://img.shields.io/badge/licen%C3%A7a-MIT-16a34a)

[**Site**](https://stage2dev.github.io/power-platform-skills/) ·
[**Diagrama 3D**](https://stage2dev.github.io/power-platform-skills/diagrama/) ·
[**Apresentação em PDF**](docs/Power-Platform-Kit.pdf) ·
[**Instalação**](#instalação) ·
[**Contribuir**](#como-contribuir)

</div>

---

## Em 30 segundos

```text
/plugin marketplace add stage2dev/power-platform-skills
/plugin install pp@power-platform-kit
/pp:novo um app para acompanhar pedidos entre as unidades
```

Depois é só seguir o bloco **Próximo passo** que fecha cada etapa. Requisitos e outras formas de
instalar estão em [Instalação](#instalação).

> **Idioma.** O kit é mantido em **português do Brasil (pt-BR)** e **inglês (en-US)**, e toda
> alteração entra nas duas línguas. As duas edições estão completas: `pp` (pt-BR, `/pp:novo` …) e
> `pp-en` (en-US, `/pp-en:new` …), com as mesmas etapas, regras, moldes e validadores; o README, o
> site, o diagrama 3D e o PDF existem nas duas línguas. O Power Fx segue a barra de fórmulas de cada
> idioma: no pt-BR, `;` separa argumentos e `;;` encadeia; no en-US, `,` e `;`.

## Por que existe

Comecei no Power BI e fui para Power Apps, Power Automate, RPA e automação de processos. Em todo
projeto os mesmos problemas voltavam, e quase sempre se resolviam do mesmo jeito. Transformei esse
jeito em regra, e as regras num kit que o Claude Code segue do começo ao fim: menos retrabalho, o
mesmo padrão em todos os apps e cada entrega com prova de que funciona.

| O problema de sempre | O que o kit faz |
|---|---|
| Tela construída antes de entender o problema | Brainstorm, requisitos e um protótipo navegável aprovado antes da primeira fórmula |
| Fórmula que não delega e some com registro | Padrões de delegação na skill de Canvas, e o QA confere antes de você testar |
| Fluxo sem tratamento de erro | Try/Catch, autorização por ação, log e resposta de 4 campos; a tela chama dentro de `IfError` |
| Usuário de uma unidade vendo dado de outra | O bloqueio fica no fluxo e na procedure (ou no security role); a tela só filtra, e o teste nega por perfil e por unidade |

## Apresentação em PDF

Quatro páginas para mandar ao time: o que é, as dez etapas, quem pensa e quem executa, e as
convenções. [**Baixar o PDF**](docs/Power-Platform-Kit.pdf).

<table>
  <tr>
    <td><a href="docs/Power-Platform-Kit.pdf"><img src="docs/img/pdf-1.jpg" alt="Página 1: capa, por que existe e como começar"></a></td>
    <td><a href="docs/Power-Platform-Kit.pdf"><img src="docs/img/pdf-2.jpg" alt="Página 2: as dez etapas em quatro blocos e as voltas"></a></td>
    <td><a href="docs/Power-Platform-Kit.pdf"><img src="docs/img/pdf-3.jpg" alt="Página 3: quem pensa e quem executa, os agentes e os perfis de modelo"></a></td>
    <td><a href="docs/Power-Platform-Kit.pdf"><img src="docs/img/pdf-4.jpg" alt="Página 4: app que já existe, convenções, código aberto e requisitos"></a></td>
  </tr>
</table>

<details>
<summary><strong>Sumário</strong></summary>

- [Como funciona](#como-funciona)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Seu primeiro app, passo a passo](#seu-primeiro-app-passo-a-passo)
- [Os agentes](#os-agentes)
- [Trabalhando num app que já existe](#trabalhando-num-app-que-já-existe)
- [Catálogos de componentes](#catálogos-de-componentes)
- [Convenções que o kit garante](#convenções-que-o-kit-garante)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Como contribuir](#como-contribuir)
- [Próximos passos](#próximos-passos)
- [Créditos e marcas](#créditos-e-marcas)
- [Licença](#licença)

</details>

---

## Como funciona

O diagrama do topo é o pipeline inteiro: dez etapas em quatro blocos, da ideia (`1`) ao app
publicado (`10`). Os gorros coloridos são os agentes, os pinos vermelhos marcam onde você age no
ambiente, e as mangueiras são as voltas. [Abra a versão em 3D](https://stage2dev.github.io/power-platform-skills/diagrama/)
para girar e aproximar.

<details>
<summary>O mesmo diagrama em texto (Mermaid)</summary>

```mermaid
flowchart TD
    IDEIA["Ideia inicial do app"] --> O["Orquestrador · /pp:novo"]

    subgraph DEFINICAO["1. Definição do produto"]
        B["Agente Brainstorm · /pp:brainstorm"]
        R["Requisitos, funcionalidades e escopo do MVP"]
        B --> R
    end

    subgraph DESIGN["2. Identidade e experiência"]
        D["Agente Designer Branding · /pp:design"]
        V["Cores, fontes, componentes e identidade visual"]
        M["Agente de Mockups em Imagem · /pp:mockups"]
        T["Telas, navegação, loading, erros e estados vazios"]
        H["Agente Gerador de Mockup HTML · /pp:prototipo"]
        PROTO["Protótipo navegável"]
        AP{"Protótipo aprovado?"}
        D --> V --> M --> T --> H --> PROTO --> AP
        AP -->|Ajustar| D
    end

    subgraph CONSTRUCAO["3. Construção na Power Platform"]
        ARQ["Agente de Arquitetura · /pp:arquitetura"]
        ESP["Modelo de dados, permissões e integrações"]
        P["Agente Power Apps Canvas · /pp:construir app"]
        A["Agente Power Automate · /pp:construir flows"]
        APP["Telas, componentes e fórmulas Power Fx"]
        FLUXO["Fluxos, aprovações, notificações e tratamento de erros"]
        INT["App e automações integrados"]
        ARQ --> ESP
        ESP --> P --> APP --> INT
        ESP --> A --> FLUXO --> INT
    end

    subgraph ENTREGA["4. Validação e entrega"]
        QA["Agente de Testes e Qualidade · /pp:testar"]
        OK{"Testes aprovados?"}
        HOM["Homologação com o usuário · /pp:homologar"]
        PUB["Publicação e documentação · /pp:publicar"]
        FINAL["App final no Power Apps"]
        QA --> OK
        OK -->|Sim| HOM --> PUB --> FINAL
    end

    O --> B
    R --> D
    AP -->|Sim| ARQ
    INT --> QA
    OK -->|Corrigir app| P
    OK -->|Corrigir automações| A
    O -.->|Coordena e acompanha · /pp:progresso| DESIGN
    O -.->|Coordena e acompanha · /pp:progresso| CONSTRUCAO
    O -.->|Coordena e acompanha · /pp:progresso| ENTREGA
```

</details>

Quatro ideias deixam o caminho fácil de seguir:

1. **Um comando por etapa.** São dez etapas, de `/pp:novo` a `/pp:publicar`. Cada uma confere se a
   anterior terminou; se você rodar fora de ordem, ela diz qual rodar no lugar.
2. **Uma sessão nova por etapa.** Tudo o que uma etapa produz fica gravado em disco, então a próxima
   começa com o contexto limpo. Toda etapa termina com um bloco **Próximo passo** como este:

   ```text
   ## ▶ Próximo passo

   **Etapa 3 de 10 · Identidade visual** — Agente Designer Branding: cores, fontes, componentes e identidade visual

   `/pp:design`

   Abra uma nova sessão antes: digite `/clear` (ou feche e abra o Claude Code na pasta do projeto).
   ```

3. **Você só para onde precisa de gente:** aprovar o MVP, a identidade visual e o protótipo; criar
   tabelas, colar telas e fluxos, rodar a homologação e publicar. O resto é produzido e validado
   para você.
4. **Quem pensa não é quem executa.** A sessão de cada etapa define o pedido e julga; os agentes
   escrevem e provam o que fizeram. Cada entrega recebe um veredito (aceito, revisão ou levada a
   você) antes de chegar até você, e o modelo de cada papel é escolhido no `/pp:novo`.

Perdeu o fio? `/pp:progresso` mostra a qualquer momento onde o projeto está e o próximo comando. O
estado fica no `ESTADO.md`, na raiz do projeto.

## Requisitos

| O quê | Para quê |
|---|---|
| [Claude Code](https://github.com/anthropics/claude-code) com suporte a plugins | tudo |
| Python 3.10+ | o estado do projeto e os validadores (só biblioteca padrão) |
| `pip install pyyaml` | o `validar-telas.py` e o lint do repositório |
| Um ambiente Power Platform (Power Apps Studio, Power Automate) | colar, testar e publicar |
| *Opcional:* uma [chave da API da OpenAI](https://platform.openai.com/api-keys) em `OPENAI_API_KEY` | os mockups em imagem da etapa 4, a única que chama uma API externa. Sem a chave, a etapa segue sem imagens |

## Instalação

Dentro do Claude Code:

```text
/plugin marketplace add stage2dev/power-platform-skills
/plugin install pp@power-platform-kit
```

Ou pelo terminal:

```bash
claude plugin marketplace add stage2dev/power-platform-skills
claude plugin install pp@power-platform-kit
```

Digite `/pp:` no Claude Code: os onze comandos de etapa devem aparecer. Se não aparecerem numa
sessão que já estava aberta, reinicie o Claude Code.

**A partir de um clone local** (para testar mudanças antes de publicar):

```bash
git clone https://github.com/stage2dev/power-platform-skills.git
claude plugin marketplace add ./power-platform-skills
claude plugin install pp@power-platform-kit
```

Para atualizar depois: `claude plugin marketplace update power-platform-kit` e, em seguida,
`claude plugin update pp`.

## Seu primeiro app, passo a passo

Abra o Claude Code numa pasta vazia e digite:

```text
/pp:novo um app para acompanhar pedidos entre as unidades
```

Depois é só seguir o bloco **Próximo passo** no fim de cada etapa. Em resumo:

| # | Comando | Quem trabalha | O que você faz | O que sai |
|---|---|---|---|---|
| 1 | `/pp:novo` | Orquestrador | conta a ideia do jeito que tiver (frase, lista, print); escolhe pasta, commits e modelos numa rodada | repositório git, `power-platform.config.json`, `ideia-bruta.md`, `00-LEIA-PRIMEIRO.md`, `ESTADO.md` |
| 2 | `/pp:brainstorm` | Agente Brainstorm (conversa com você) | confirma o que a ideia já trouxe; escolhe o modo; responde ao que falta; decide o que entra no MVP | `docs/planejamento/brainstorm.md`, `prd.md` |
| 3 | `/pp:design` | Agente Designer Branding (conversa com você) | escolhe cores, estilo, fonte e o jeito de navegar; aprova uma amostra visual | `ux-design-system.md`, `identidade.html` |
| 4 | `/pp:mockups` | Agente de Mockups em Imagem + script | confere a lista de telas; autoriza as imagens | `inventario-telas.md`, `mockups/*.png` |
| 5 | `/pp:prototipo` | Agente Gerador de Mockup HTML | navega pelo protótipo; aprova ou pede ajustes | `prototipo/index.html` |
| 6 | `/pp:arquitetura` | Agente de Arquitetura, depois Agentes SQL em paralelo | escolhe SQL Server ou Dataverse; cria as tabelas 🔴 (no Dataverse, pelo flow construtor ou importando a carga mockup, e confere os tipos) | `arquitetura.md`, ADR, DDL e procedures (ou modelo Dataverse), carga mockup `.xlsx` (e `.sql` no SQL; no Dataverse, o plano e o flow construtor), `GOAL.md` |
| 7 | `/pp:construir` | Agentes Canvas ∥ Power Automate, um por grupo de telas ou fluxos | cola telas e fluxos 🔴; uma onda por sessão | telas `.pa.yaml`, JSON dos fluxos |
| 8 | `/pp:testar` | Agente de Testes e Qualidade | roda o roteiro de teste no ambiente 🔴 | `docs/qa/QA-<data>.md` |
| 9 | `/pp:homologar` | Orquestrador, com você | faz a homologação com usuários reais 🔴 | `docs/qa/UAT-<data>.md` |
| 10 | `/pp:publicar` | Orquestrador | publica em produção 🔴 | manual do usuário, guia técnico, checklist de go-live |

🔴 marca o que só uma pessoa pode fazer no ambiente. Nesses pontos o Claude mostra um passo a passo
numerado (onde clicar, o que colar, o que conferir) e espera você digitar "feito" ou colar o erro.

### Quatro jeitos de fazer o brainstorm

A etapa 2 começa perguntando como você quer pensar. Cada modo é conduzido por uma persona; eles só
mudam o começo da conversa. Os quatro terminam do mesmo jeito: corte do MVP, regras de negócio,
bloqueadores e `prd.md`. Por isso as etapas seguintes não dependem do modo escolhido.

| Modo | Escolha quando | Quem conduz |
|---|---|---|
| Entrevista guiada | você já sabe o que quer e precisa de ajuda para fechar | 🧠 Facilitador |
| Foco nas pessoas (design thinking) | o app muda o dia a dia de muita gente, em perfis diferentes | 🎨 Designer de experiência: mapa de empatia, um dia na vida, "Como poderíamos…?" |
| Foco no problema (causa raiz) | algo está quebrado (retrabalho, erro, atraso) e você quer a causa | 🔬 Investigador: 5 porquês, espinha de peixe, gargalo, brainstorm reverso |
| Mesa redonda | a ideia ainda está vaga e você quer ouvir vários pontos de vista | 🧠 modera 👤 usuário da ponta, 💼 negócio e 😈 advogado do diabo, e chama 🎨 🔬 🛠️ 🛡️ quando precisa |

Dá para trocar de modo no meio ("trocar de modo") sem perder nada do log. As personas perguntam e
propõem; quem decide é você. Elas foram inspiradas no módulo criativo e no *party mode* do BMAD
Method.

### Cinco jeitos de navegar

Na etapa 3 o designer pergunta como o app leva de uma área para outra, mostrando um desenho de
cada opção. A escolha vale para os mockups, o protótipo e a construção.

| Padrão | Bom para |
|---|---|
| Menu lateral sempre aberto | uso diário no desktop, 3 ou mais áreas |
| Menu lateral recolhível (☰ alterna) | telas com tabela larga |
| Gaveta que abre por cima (hambúrguer) | tablet, tela estreita, uso eventual |
| Barra no topo | 2 a 6 áreas com nome curto |
| Tela inicial com cartões | uso eventual, uma tarefa por visita |

No protótipo, o seletor "Navegação" troca o padrão ao vivo para comparar; se preferir outro, é
um item de ajuste e o pipeline volta ao `/pp:design`.

### Quem pensa e quem executa

A sessão de cada etapa é a cabeça: conversa com você, escreve o pedido de cada agente e julga o
que volta. Os agentes são as mãos: escrevem telas, fluxos, procedures e o protótipo, e fecham a
entrega dizendo **como verificaram** (o comando e o que saiu), o que cumpriram, o que acham
arriscado e a confiança que têm. A sessão roda o validador de novo e dá um veredito por agente:
**aceito**, **revisão** (o mesmo agente, com um pedido mais preciso; no máximo duas) ou
**escalado** (vem para você decidir). O `/pp:progresso` mostra quantas revisões cada etapa
precisou. Antes de mostrar a amostra do design ou o protótipo, o Claude fotografa as telas e olha
(texto cortado, sobreposição, contraste).

Como pensar e julgar é a parte pequena do trabalho, a cabeça pode usar um modelo mais forte e as
mãos um mais rápido. No `/pp:novo` você escolhe o perfil:

| Perfil | Sessão de cada etapa | Arquitetura e QA | Telas, fluxos, SQL, mockups, protótipo | Pesquisa |
|---|---|---|---|---|
| **Equilibrado** (recomendado) | Opus | Opus | Sonnet | Sonnet |
| Máximo | Fable, se a conta tem (senão Opus) | Opus | Opus | Sonnet |
| Econômico | Sonnet | Sonnet | Sonnet | Haiku |
| Herdar | o modelo em que a sessão abrir | idem | idem | idem |

A sessão abre no modelo escolhido pelo `.claude/settings.local.json` do projeto (pessoal, fora do
Git), e cada agente recebe o seu na chamada. Dá para trocar um papel depois:
`modelos.py aplicar equilibrado --execucao opus`. Detalhes em
[`references/modelos.md`](skills/power-platform/references/modelos.md).

### As voltas

- **Protótipo não aprovado:** os pedidos de ajuste vão para `ajustes-prototipo.md` e o próximo passo
  é `/pp:design` de novo. Ele classifica cada pedido em identidade, tela ou comportamento, e os
  mockups e o protótipo refazem só o que mudou.
- **Teste ou homologação com falha:** cada falha vai para `docs/qa/correcoes.md`, marcada como app
  ou fluxos, e o próximo passo é `/pp:construir app` ou `/pp:construir flows`. Depois da correção, o
  teste roda de novo.
- **Depois de publicado:** mande a lista de mudanças com `/pp:mudanca`. Cada pedido vira um spec em
  `docs/mudancas/MUD-<NNN>.md`, os agentes fazem em paralelo, o QA da mudança roda e a homologação
  e a publicação reabrem para uma versão nova. Mudança grande (perfil ou entidade nova) reabre o
  pipeline no brainstorm.

### Mockups (chave da OpenAI opcional)

A etapa 4 pode transformar cada tela numa imagem com a API de imagens da OpenAI, usando a sua
paleta. O Claude sempre valida o spec antes (`--simular`: sem chave, sem rede), mostra quantas
imagens e qual modelo, avisa que a descrição das telas vai para a OpenAI e só gera depois que você
autoriza. Os dados de exemplo são sempre fictícios.

Configure a chave **fora do chat** e reabra o Claude Code num terminal novo:

```powershell
setx OPENAI_API_KEY "<sua-chave>"        # Windows, permanente (abra um terminal novo)
```

```bash
export OPENAI_API_KEY="<sua-chave>"      # macOS/Linux; coloque no ~/.bashrc ou ~/.zshrc
```

O modelo é uma variável: `--modelo` > `OPENAI_IMAGE_MODEL` > `mockups.modelo` no config >
`gpt-image-2`. Sem chave, ou sem aprovação da segurança? Escolha "não gerar": o protótipo é montado
só a partir do inventário de telas. Detalhes em
[`references/mockups.md`](skills/power-platform/references/mockups.md).

## Os agentes

| Agente | Etapa | Roda como | Ferramentas |
|---|---|---|---|
| Brainstorm | `/pp:brainstorm` | na própria sessão da etapa (precisa conversar com você), na pele da persona do modo escolhido | — |
| Designer Branding | `/pp:design` | na própria sessão da etapa | — |
| `pp:agente-mockups` | `/pp:mockups` | subagente | lê e escreve; **sem shell**, então não consegue chamar a API de imagens |
| `pp:agente-prototipo` | `/pp:prototipo` | subagente | lê, escreve, shell (verificador do protótipo) |
| `pp:agente-arquitetura` | `/pp:arquitetura` | subagente | lê, escreve, shell; escreve o spec das procedures, não o corpo |
| `pp:agente-sql` | `/pp:arquitetura`, correções | subagente, um por grupo de procedures, em paralelo | lê, escreve, shell (`lint-procedure.py`) |
| `pp:agente-canvas` | `/pp:construir` | subagente, um por grupo de até 3 telas, em paralelo | lê, escreve, shell (`validar-telas.py`) |
| `pp:agente-automate` | `/pp:construir` | subagente, um por grupo de até 3 fluxos, em paralelo | lê, escreve, shell (`verificar-fluxo.py`) |
| `pp:agente-qa` | `/pp:testar` | subagente | só lê, mais shell para os validadores |
| `pp:agente-pesquisa` | brainstorm, arquitetura, construção, `/pp:mudanca` | subagente, quando falta um fato | só lê, mais busca na documentação oficial; nada do projeto vai para a web |

Subagente não consegue fazer perguntas a você, por isso os dois agentes que conversam rodam na
própria sessão da etapa. A etapa que chama um subagente julga o trabalho dele (roda o validador de
novo, confere o pedido item a item) e dá o veredito antes de seguir.

## Trabalhando num app que já existe

| Você diz | O que o Claude faz |
|---|---|
| "O KPI não bate com a galeria" / "está lento" / "não atualiza" | **Modo investigar.** Percorre a cadeia tela → fórmula → fonte → fluxo → procedure → dado, testa uma hipótese por vez e prova a causa raiz antes de propor código. |
| "Um usuário de uma unidade vê dados de outra" | Confere a camada que de fato bloqueia o acesso: fluxo + procedure no SQL, ou papéis de segurança no Dataverse. A tela só filtra. |
| "Audite o app inteiro" | Roda revisores em paralelo por disciplina (UX, desenvolvimento, performance, dados, fluxos, SQL) e confere de novo os achados mais fortes antes de relatar. |
| "Coloque um filtro de status nesta tela" | Vai direto para o `powerapps-canvas`, sem o protocolo completo. |
| Uma lista de mudanças num app publicado pelo kit | `/pp:mudanca <lista>`: escopo de cada pedido, um spec por frente, agentes em paralelo, julgamento, QA e reabertura da homologação. |
| "Promova para HML/PRD" | Cobre soluções, variáveis de ambiente, connection references e o CLI `pac`, e diz o que vai por colagem e o que vai por solução. |
| "Está pronto?" | Roda o portão final: todos os validadores que se aplicam, mais o checklist. |

## Catálogos de componentes

**Canvas — [`powerapps-canvas/assets/componentes/`](skills/powerapps-canvas/assets/componentes/INDICE.md)**
(25 componentes em YAML pronto para colar)

| Grupo | Componentes |
|---|---|
| Layout e navegação | cabeçalho de tela, menu lateral (fixo, recolhível ou gaveta), menu no topo, tela inicial com cartões, abas, seletor de unidade |
| Dados | galeria em tabela, linha expansível, ordenação por coluna, paginação por cursor, rodapé com contagem, seleção em lote, badge de status, card de KPI |
| Filtros e ações | barra de filtros, botões, exportação |
| Modais | confirmação, formulário, informativo, destrutivo com motivo |
| Feedback | overlay de carregamento, toast, estado vazio, painel sem acesso |

**Power Automate — [`power-automate/assets/componentes/`](skills/power-automate/assets/componentes/INDICE.md)**
(34 blocos: JSON de área de transferência mais notas)

| Grupo | Blocos |
|---|---|
| Gatilhos (digitados à mão) | Power Apps (V2), entrada HTTP |
| Núcleo do fluxo chamado pelo app | config, identificar quem chama, ler quem chama (SQL), switch por ação, autorizar por flag, negar + Terminate, normalizar entrada, derivar valor, estado antes da mudança, escopo por unidade, validar com mensagem, trilha de auditoria, guarda "nada mudou", gravar via stored procedure, traduzir código e responder, captura do conector |
| Variantes Dataverse | ler quem chama (Dataverse), escopo multiunidade, compensação quando não há transação |
| Efeitos colaterais e relatórios | resolver ID do diretório, e-mail de suporte com resultado parcial, filtros da tela como JSON, exportação CSV, HTML para PDF |
| Entrada HTTP e lote | config de entrada, cache de token + resposta HTTP, mapear lote, upsert de uma linha, índice de chave do destino, changeset de upsert `$batch` no Dataverse, paginação nativa |
| Observabilidade | log de execução |

Cada `INDICE.md` traz as dependências e a maturidade de cada item. O índice do Power Automate
acrescenta a ordem de montagem para cada tipo de fluxo. O do Canvas lista as variáveis que cada
componente espera no `OnStart`, e os tokens já estão em `app-formulas-tokens.md`.

## Convenções que o kit garante

São os padrões. Estão registrados em
[`decisoes-padrao.md`](skills/power-platform/references/decisoes-padrao.md), e mudar qualquer um
exige um ADR.

- **Uma trilha de dados por projeto:** SQL Server *ou* Dataverse.
- **O nome real vence.** Fórmulas e fluxos são escritos com os nomes lidos do ambiente
  (`NOMES-AS-BUILT`), nunca com os do plano.
- **Toda tabela nasce com carga mockup.** Um `.xlsx` com dados fictícios, uma aba por tabela na ordem
  de carga; no SQL, também o `INSERT` para o banco de DEV. O Dataverse deduz o tipo de cada coluna
  pelos dados e erra com frequência: o kit avisa e confere (`montar-carga-mockup.py --conferir`)
  antes de qualquer dado real. Ou, no Dataverse, o **construtor**: um flow que cria as tabelas, as
  colunas com o tipo do modelo, os relacionamentos e a carga mockup direto pela Web API (`--flow`).
- **Escrita sempre passa por um fluxo,** com a resposta de 4 campos e `.Run()` dentro de `IfError`.
- **O fluxo lê a identidade do usuário do próprio contexto** e autoriza cada ação. Os parâmetros do
  fluxo são posicionais, e um novo entra sempre no fim.
- **O separador depende de onde a fórmula vai:** `;` / `;;` na barra de fórmulas pt-BR, `,` / `;` no
  YAML colado.
- **Nenhum literal de ambiente nas entregas:** nada de servidor, tabela `dev*` ou GUID. Use
  variáveis de ambiente e connection references.
- **Gerador nunca sobrescreve o que foi colado.** O arquivo colado é a fonte da verdade, e o que é
  gerado vai para `dist/`.
- **✅ exige evidência:** comando, saída e data. A evidência vence quando o arquivo muda.

## Estrutura do repositório

```text
.claude-plugin/          plugin.json + marketplace.json
agents/                  agente-mockups, agente-prototipo, agente-arquitetura, agente-sql,
                         agente-canvas, agente-automate, agente-qa, agente-pesquisa
skills/
  novo/ brainstorm/ design/ mockups/ prototipo/ arquitetura/
  construir/ testar/ homologar/ publicar/ progresso/ mudanca/
                         os comandos /pp:* de cada etapa (finos: apontam para as skills abaixo)
  power-platform/        orquestrador: pipeline, estado, roteamento, protocolo, portões, ALM
    references/  assets/  prompts/
    scripts/estado.py  modelos.py  desenhar-mockups.py  verificar-prototipo.py
            capturar-telas.py  montar-carga-mockup.py (+ _carga_*.py)
  powerapps-canvas/      references/  assets/componentes/  scripts/validar-telas.py
  power-automate/        references/  assets/componentes/  scripts/verificar-fluxo.py
  sql-procedures/        references/  assets/  scripts/lint-procedure.py
  dataverse/             references/  assets/  scripts/extrair-nomes-as-built.py
docs/
  index.html             o site (GitHub Pages)
  diagrama/              o diagrama 3D em blocos (three.js), também no site
  img/                   as imagens do README (diagrama nos temas claro e escuro, páginas do PDF)
  Power-Platform-Kit.pdf a apresentação de 4 páginas
  PADRAO-SKILL.md        o padrão que toda skill segue
  CONFIG.md              referência do power-platform.config.json
tests/                   testes pytest de cada script, dos catálogos e do lint
tools/lint_skills.py     lint de estrutura + sanitização
```

## Como contribuir

O kit é aberto para quem quiser somar: melhorar uma etapa, adicionar um componente, corrigir uma
regra que não bate com o seu dia a dia. Abra uma issue ou mande um pull request: eu acompanho e
reviso cada um.

Toda skill segue o [`docs/PADRAO-SKILL.md`](docs/PADRAO-SKILL.md). As regras principais:

- o frontmatter tem uma descrição que diz quando usar a skill e quando não usar;
- o `SKILL.md` fica com 250 linhas ou menos;
- detalhe vai em `references/`, arquivos prontos para copiar em `assets/`;
- scripts aceitam `--help` e retornam exit code 0, 1 ou 2;
- todo script tem testes.

**Toda alteração entra em pt-BR e en-US.** O kit é mantido nas duas línguas: skill, agente,
referência, molde, catálogo, mensagem de script, teste, README e site. Cada pull request traz a
mudança nas duas versões, com o mesmo conteúdo; mudança numa língua só não entra. Na versão en-US,
o Power Fx da barra de fórmulas usa `,` para separar argumentos e `;` para encadear.

Antes de abrir um pull request:

```bash
pip install pyyaml pytest
python tools/lint_skills.py        # estrutura + sanitização; precisa imprimir 0 erro(s)
python -m pytest tests -q          # scripts, catálogos e lint
claude plugin validate .           # manifesto e frontmatter
```

**Sanitização.** Este repositório não pode conter nada disto, e o lint barra:

- caminhos de máquina, nomes de servidor, IDs de tenant ou de ambiente, GUIDs reais;
- endereços de e-mail, exceto os de exemplo no estilo `@contoso.com`;
- dados de negócio ou nomes de empresa.

Para barrar também os nomes internos da sua organização, crie `tools/sanitizacao.local.txt`
(ignorado pelo git) com um regex por linha.

## Próximos passos

- **Skill `power-bi` completa**, no mesmo nível desta: modelo estrela, Power Query M e DAX. É a próxima.
- Um `gate.py` único que roda todos os validadores das camadas que uma onda tocou.
- Um conferidor de nomes que compara telas e fluxos com o `NOMES-AS-BUILT`.
- Avaliações de gatilho para a descrição de cada skill.

O histórico de versões está no [`CHANGELOG.md`](CHANGELOG.md).

## Créditos e marcas

- O ciclo de planejamento e as personas do brainstorm são **inspirados no
  [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)** (código sob licença MIT, de BMad
  Code, LLC). Este projeto não é afiliado nem endossado pela BMad Code, LLC. "BMad" e "BMad Method"
  são marcas deles, citadas aqui só para descrever compatibilidade.
- A separação entre quem pensa e quem executa (cabeça julga, mãos fazem e provam, veredito por
  entrega) é inspirada no guia ["The Fable Loop"](https://thomaslentine.com/fable-guide.html), de Thomas Lentine.
- O diagrama em blocos foi montado em three.js com a técnica de blocos da
  [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) (MIT, LemoLab). O Clawd é o mascote do
  Claude; o desenho de referência é da [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase)
  (MIT, John Heibel). Uso de fã: não é material oficial da Anthropic.
- Power Apps, Power Automate, Power Platform, Dataverse e SQL Server são marcas do grupo de
  empresas Microsoft. Claude e Claude Code são marcas da Anthropic. Este projeto não é afiliado a
  nenhuma das duas.

## Licença

[MIT](LICENSE). Pode usar, copiar, modificar e distribuir, inclusive em projetos comerciais,
desde que mantenha o aviso de copyright e a licença. O software vem sem garantia.

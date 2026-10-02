# Design system e inventário de telas

Etapa entre o PRD e a arquitetura. Três artefatos:

| Artefato | Molde | Fase | Quem conduz |
|---|---|---|---|
| design system do projeto | `assets/ux-design-system-molde.md` | 3 | papel UX (`prompts/ux.md`) |
| inventário de telas, com a moldura do app | `assets/inventario-telas-molde.md` | 4 | `pp:agente-mockups` (`/pp:mockups`) |
| mockups | `assets/mockups-molde.json` | 4 | `pp:agente-mockups` + `scripts/desenhar-mockups.py` |
| protótipo navegável | `assets/prototipo-molde.html` | 5 | `pp:agente-prototipo` (`/pp:prototipo`) |

O design system é decidido em conversa pelo Agente Designer Branding (`/pp:design`, etapa 3);
inventário, mockups e protótipo saem dos agentes do plugin (`pipeline.md`).

## Sumário

1. [Entradas](#1-entradas)
2. [Design system](#2-design-system)
3. [Componentes do catálogo](#3-componentes-do-catálogo)
4. [Inventário de telas](#4-inventário-de-telas)
5. [Mockups](#5-mockups)
6. [Portão de saída](#6-portão-de-saída)

---

## 1. Entradas

- PRD (visão, perfis, escopo por unidade, regras, volumes, MVP).
- Respostas do bloco 3 de `brainstorm.md` (resolução, marca, tela molde, acessibilidade).
- Se existe app irmão: o `app-formulas-tokens.md` dele é o ponto de partida; parta do mesmo, não de
  uma paleta nova.

## 2. Design system

Não se desenha tela sem isso. Decida e registre no molde:

| Item | O que decidir | Onde está o padrão |
|---|---|---|
| Tokens | família `fx*` de cor, tipografia, layout, componente e texto, como named formulas do App | `powerapps-canvas/references/design-tokens.md`; valores em `powerapps-canvas/assets/app-formulas-tokens.md` |
| Cor | marca, neutros, semântica (sucesso, aviso, erro, info), tema único ou claro/escuro | idem; contraste mínimo WCAG AA 4,5:1 para texto normal |
| Tipografia | fonte, escala de tamanhos, pesos; nada fora da escala | idem |
| Grid e layout | resolução do canvas (T1: layout manual, canvas fixo), margens, colunas, espaçamentos | `powerapps-canvas/references/ux-componentes.md` |
| Estados | normal, foco, desabilitado, carregando, vazio, erro, sucesso; estado nunca só por cor | `ux-componentes.md`, `ux-feedback.md`, `acessibilidade.md` |
| Feedback | toast, loading, confirmação de ação irreversível | `ux-feedback.md`; contrato do `.Run()` em `chamada-flow.md` |
| Acessibilidade | rótulo acessível, ordem de tabulação, foco visível, alvo de toque, ordem de leitura | `acessibilidade.md` |

Regra T3: cor, fonte e tamanho só por token `fx*`. Valor novo é token novo, decidido aqui, nunca
`RGBA(` solto numa tela. O validador `validar-telas.py` acusa literal.

## 3. Componentes do catálogo

Escolha, para cada padrão de interface do projeto, o componente do catálogo da skill
`powerapps-canvas` (`assets/componentes/`) em vez de desenhar do zero: menu, cabeçalho, galeria com
filtros, formulário, modal de confirmação, toast, estado vazio, indicador de carregamento, contador
(KPI). Liste no design system os escolhidos e as variações permitidas.

- Componente que o catálogo não tem: registre como lacuna; vira história própria (molde novo
  também alimenta o catálogo depois).
- Propriedade só se o app já a usa naquele tipo de controle (T4); versão exata do controle (T2).
- Nomes de controle: T5 (`<prefixo-tela>-<tipo>-<módulo>-<elemento>`).

## 4. Inventário de telas

Quem elenca as páginas é o `pp:agente-mockups`. Ele parte dos RF do
PRD e soma as telas transversais (inicial, sem acesso, detalhe, gestão de acesso, exportação).
Antes das telas, ele fecha a **moldura do app**, igual em todas:

- header;
- navegação, no padrão que o usuário escolheu no `/pp:design` (`ux-design-system.md`
  §2.1, `references/navegacao.md`);
- seletor de unidade;
- notificações (toast);
- pop-ups (confirmação, formulário, destrutivo, informativo);
- loading;
- estados vazio e sem acesso;
- rodapé.

Uma tabela mestre, a moldura, o mapa de navegação e, para cada tela, uma ficha curta (molde em
`assets/`). Campos da ficha:

| Campo | Conteúdo |
|---|---|
| Tela | nome e prefixo de controles |
| Objetivo | a decisão ou ação que ela permite, em uma frase |
| Perfis | quem vê, quem age (por flag, T8) |
| Componentes | do catálogo; blocos canônicos usados |
| Fontes de dados | tabelas e colunas lidas; volume esperado por filtro |
| Flows chamados | ações de escrita e seus parâmetros (contrato C1–C6) |
| Delegação esperada | o que delega, o que não, e o teto (T7); contadores com "2.000+"? |
| Estados | vazio, carregando, erro, sem acesso |
| Pop-ups e notificações | modais que a tela abre; toast de cada ação (toda escrita: loading + toast) |
| Mockup | `docs/planejamento/mockups/<id>.png` e o aceite do dono |
| Prioridade/corte | P0 ciclo principal, P1, P2; posição na escada de corte |

Regras:
- Toda tela do PRD aparece; toda tela do inventário rastreia um requisito (RF-xx).
- O inventário **nomeia as colunas que precisa** — é a entrada da arquitetura (modelo de dados) e
  fica à espera do `AMBIENTE-AS-BUILT` para virar nome real.
- Tela que escreve sem passar por flow viola A1: corrija no inventário.
- A escada de corte do inventário vira a escada do `GOAL.md`.

## 5. Mockups

Uma imagem por tela e por estado relevante, gerada pela API de imagens da OpenAI a partir do spec
`docs/planejamento/mockups/mockups.json`. A paleta vem do design system. Exige `OPENAI_API_KEY`, e o
modelo é variável (`OPENAI_IMAGE_MODEL`, default `gpt-image-2`).

- Passo a passo, chave, modelo e erros: `references/mockups.md`.
- Validar sem custo: `scripts/desenhar-mockups.py <spec> --simular`.
- Gerar só depois do aceite do usuário: custa por imagem, e o texto do spec sai para um serviço externo.
- O mockup é referência para aprovar estrutura e fluxo. Não é fonte de cor nem de medida.

**Protótipo navegável** (`/pp:prototipo`, etapa 5): o `pp:agente-prototipo` reproduz cada mockup
num `index.html` que abre offline, com os componentes do catálogo, os tokens e um seletor de
perfil. É ele que o usuário aprova; ajuste volta ao `/pp:design`. Contrato do arquivo: comentário
do topo de `assets/prototipo-molde.html`; verificador: `scripts/verificar-prototipo.py`.

## 6. Portão de saída

- Design system completo: nenhum item "a definir"; contraste dos pares texto/fundo calculado.
- Inventário fechado: cada tela com perfis, fontes, flows, delegação e prioridade.
- Dono do processo viu o inventário (uma frase de aceite registrada) — telas cortadas depois sem
  combinar com quem as usa viram disputa de escopo.
- Lacunas do catálogo listadas.
- Mockups gerados, ou a dispensa registrada com quem decidiu e a data (sem chave ou sem aprovação
  de segurança).
- Protótipo aprovado pelo usuário, com quem aprovou e a data registrados no inventário.

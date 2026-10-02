# Design system e UX — <PROJETO>

> Etapa 3 (`/pp:design`, Agente Designer Branding). Referências: `powerapps-canvas/references/design-tokens.md`, `ux-componentes.md`,
> `ux-feedback.md`, `acessibilidade.md`; valores em `powerapps-canvas/assets/app-formulas-tokens.md`.
> Nenhum valor de cor, fonte ou tamanho fora de token `fx*` (T3).

## 1. Princípios (3 a 5)
<ex.: o ciclo principal em no máximo 3 toques; todo número na tela diz se é parcial>

## 2. Canvas e grid
Resolução fixa: <largura×altura> · layout manual com controles Classic (T1) · margens <n> ·
espaçamento base <n> · colunas <n>.

## 2.1 Navegação
Escolhida pelo usuário no `/pp:design`, com prévia (`power-platform/references/navegacao.md`).

| Item | Decisão |
|---|---|
| Padrão | <`lateral-fixo` · `lateral-recolhivel` · `gaveta` · `topo` · `inicio-cartoes`> |
| Por quê | <dispositivo, frequência de uso, número de áreas> |
| Componente do catálogo | <`menu-lateral` (variação) · `menu-topo` · `inicio-cartoes`> |
| Áreas de 1º nível previstas | <do PRD; o inventário de telas confirma na etapa 4> |
| Estado inicial | <recolhível: fechado ou aberto; gaveta: fechada> |
| Frase do usuário | <"…", data> |

## 3. Tokens
| Família | Token | Valor | Uso |
|---|---|---|---|
| cor marca | `fxColorPrimary`, `fxColorPrimaryDark`, `fxColorPrimaryLight` | <hex> | ações principais, menu, cabeçalho de tabela |
| cor semântica | `fxColorSuccess`, `fxColorWarning`, `fxColorError` | <hex> | estados |
| cor neutra | `fxColorBackground`, `fxColorSurface`, `fxColorTextPrimary`, `fxColorTextSecondary`, `fxColorBorder` | <hex> | base |
| tipografia | `fxFont`, `fxFontSize*` | <fonte>, escala <n> | texto |
| layout | `fxLayoutMargin`, `fxLayoutGutter` | <n> | espaçamento |

Nomes e valores-base em `powerapps-canvas/assets/app-formulas-tokens.md`; aqui entra o **hex** decidido
para o projeto. É dessa coluna que o `pp:agente-mockups` copia a paleta para os mockups (etapa 4).

Tema: único ou claro/escuro. Contraste (texto × fundo efetivo, mínimo 4,5:1):

| Par | Contraste | Passa AA? |
|---|---|---|

## 4. Componentes escolhidos (catálogo `powerapps-canvas/assets/componentes/`)
| Padrão de interface | Componente do catálogo | Variações permitidas | Lacuna? |
|---|---|---|---|
| navegação (seção 2.1) | | | |
| galeria com filtros | | | |
| formulário | | | |
| modal de confirmação | | | |
| toast | | | |
| estado vazio | | | |
| carregando | | | |
| contador (KPI) | | | |

## 5. Estados
Para cada componente interativo: normal, foco, desabilitado, carregando, vazio, erro, sucesso. O
estado nunca depende só de cor (texto ou ícone junto).

## 6. Feedback
Toast de sucesso, aviso e erro (`status` do contrato C1), confirmação para ação irreversível,
indicador de carregamento durante `.Run()`.

## 7. Acessibilidade
Rótulo acessível em todo controle, ordem de tabulação, foco visível, alvo de toque mínimo, ordem de
leitura, contraste, estado não só por cor.

## 8. Fluxos principais
Para cada fluxo P0: passos, telas, estados de erro, o que o usuário vê sem permissão.

## 9. Insumos para os mockups (etapa 4)
- Paletas e referências visuais trazidas no brainstorm (bloco 3.3): de onde veio cada cor da seção 3.
- Estilo em uma frase (ex.: "Fluent 2, corporativo, alta densidade de informação, ícones de linha").
- Idioma da interface e o que nunca pode aparecer em imagem (logo de terceiro, dado real).

## Portão de saída
- [ ] Nenhum item "a definir"; contraste calculado.
- [ ] Componentes escolhidos do catálogo; lacunas listadas.
- [ ] Tela molde (se houver) e blocos canônicos indicados.

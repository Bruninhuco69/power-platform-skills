# Tokens de design `fx*`

Cor, tipografia, layout, componente e texto como **named formulas** do objeto App. Os valores
estão em [app-formulas-tokens.md](../assets/app-formulas-tokens.md) (fonte única); aqui estão as
famílias, as regras de uso e o raciocínio. Decisão T3 de
[decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md): cor, fonte e tamanho só
por token; nada de `RGBA(` literal em tela (validador: T009).

## Sumário

1. [Regras](#1-regras)
2. [Famílias de token](#2-famílias-de-token)
3. [Cor e contraste](#3-cor-e-contraste)
4. [Badge com contraste](#4-badge-com-contraste)
5. [Tipografia](#5-tipografia)
6. [Layout e grid](#6-layout-e-grid)
7. [Catálogo de mensagens `fxMsg*`](#7-catálogo-de-mensagens-fxmsg)
8. [Como evoluir os tokens](#8-como-evoluir-os-tokens)

---

## 1. Regras

1. **Token é named formula em `App.Formulas`**, nunca `Set()` no `OnStart`. Tema como global só
   existe depois que o `OnStart` termina, atrasa a carga e não pode ser usado em outra named
   formula. `[verificado: projeto de referência]`
2. **Token não lê variável global** (T6). `fxIsCompact = App.Width < 1600` pode; `fxCor = varTema`
   não pode.
3. **Um nome, um papel.** Token definido e nunca usado é dívida; token usado para dois papéis
   (a mesma borda para card decorativo e para input interativo) é erro de contraste esperando
   acontecer: separe (`fxColorBorder` e `fxColorBorderInteractive`).
4. **Zero `RGBA(` literal em tela nova.** O transparente também é token
   (`fxColorTransparent`). O que restar dentro de fórmula multilinha (`Switch` de status) migra
   para `fxBadge*`.
5. **Sem alfa fora do intervalo**: `RGBA(255; 255; 255; 100)` é inválido (o alfa vai de 0 a 1).
6. **Texto visível vem do catálogo** (`fxTxt*`, `fxMsg*`), não literal na tela: placeholder,
   título de modal e rótulo de botão incluídos. Título de tela e rótulo de coluna específicos do
   domínio podem ser literais.
7. Valor muda em um lugar só: se alguém precisar editar a mesma cor em duas telas, falta um token.

## 2. Famílias de token

| Prefixo | Conteúdo | Exemplos |
|---|---|---|
| `fxColor*` | paleta de marca, superfície, texto, borda, estado, botão, aba, tabela, toast | `fxColorPrimary`, `fxColorTextOnPrimary`, `fxColorBorderInteractive` |
| `fxBadge*` | par texto/fundo por semântica | `fxBadgeSuccessText`, `fxBadgeSuccessBg` |
| `fxIsCompact` | o único breakpoint | `App.Width < 1600` |
| `fxLayout*`, `fxRowHeight`, `fxFilterHeight`, `fxKPI*`, `fxTableHeaderHeight` | medidas que dependem de `fxIsCompact` | `fxRowHeight = If(fxIsCompact; 40; 50)` |
| `fxFont` | a família tipográfica única (`Font.'Segoe UI'`); todo controle usa `Font: =fxFont` | `fxFont` |
| `fxFontSize*` | escala tipográfica | `fxFontSizeTitle`, `fxFontSizeTable`, `fxFontSizeToast` |
| `fxBtn*`, `fxModal*`, `fxLoading*`, `fxToast*` | geometria e tempo dos componentes | `fxBtnHeight`, `fxToastDurationError` |
| `fxLimiteLinhas`, `fxTxtTeto`, `fxPageSize` | limites do conector e da paginação | `fxLimiteLinhas = 2000` |
| `fxTxt*` | rótulos reutilizáveis | `fxTxtVoltar`, `fxTxtProcessando` |
| `fxMsg*` | mensagens, em pares `...Error` e `...Hint` | `fxMsgFalhaFlow`, `fxMsgFalhaFlowHint` |
| `frm*` | named formula de **dado** (KPI, lista) | `frmKPIAbertos` |

`fx*` é tema e texto; `frm*` é dado derivado. Não misture.

## 3. Cor e contraste

Meta WCAG 2.x: texto normal >= 4,5:1, texto grande >= 3:1, borda e ícone de componente
interativo >= 3:1 contra a cor externa. Valores da paleta neutra do molde (rampa azul do Fluent 2), medidos pela fórmula de
luminância relativa `[verificado: cálculo próprio]`:

| Par | Razão | Uso |
|---|---:|---|
| branco sobre `fxColorPrimary` (15, 108, 189) | 5,38 | botão primário |
| branco sobre `fxColorPrimaryDark` (12, 59, 94) | 11,65 | cabeçalho, menu |
| `fxColorTableHeaderText` (17, 94, 163) sobre `fxColorTableHeaderBg` (235, 243, 252) | 5,95 | cabeçalho de tabela |
| branco sobre `fxColorSuccess` (21, 128, 61) | 5,02 | confirmação de **estado** |
| branco sobre `fxColorError` (200, 35, 51) | 5,61 | ação destrutiva |
| branco sobre `fxColorButtonCancel` (108, 117, 125) | 4,69 | secundário |
| `fxColorTextOnWarning` sobre `fxColorWarning` (255, 193, 7) | 10,88 | texto sobre âmbar |
| `fxColorTextSecondary` sobre branco | 8,45 | rótulo, aba inativa |
| `fxColorToastText` sobre `fxColorToastBg` | 7,43 | mensagem do toast |
| `fxColorBorderInteractive` (117, 117, 117) sobre branco | 4,61 | borda de input |

Reprovações comuns a evitar: **branco sobre âmbar** (1,63; por isso `fxColorTextOnWarning`),
branco sobre o verde `(40, 167, 69)` (3,13), borda de input `(209, 213, 219)` (1,47) e
placeholder `(156, 163, 175)` (2,54). `fxColorBorder` (166, 166, 166) é só decorativa (card):
3:1 só vale para controle interativo.

Revisão: abra o Accessibility checker do Studio depois de trocar a paleta
([acessibilidade.md](acessibilidade.md)).

## 4. Badge com contraste

Padrão: **texto escuro sobre pastel da mesma matiz**, com texto ou sublinhado junto (nunca só
cor). Pares do molde, todos acima de 4,5:1:

| Semântica | Texto | Fundo | Razão |
|---|---|---|---:|
| sucesso | (22, 101, 52) | (220, 252, 231) | 6,49 |
| informação | (15, 84, 140) | (207, 228, 250) | 6,05 |
| atenção | (146, 64, 14) | (255, 218, 185) | 5,40 |
| perigo | (139, 0, 0) | (255, 182, 193) | 6,06 |
| em andamento | (133, 77, 14) | (255, 230, 100) | 5,47 |
| neutro | (52, 58, 64) | (206, 212, 218) | 7,70 |

Pares comuns que **reprovam** (já corrigidos no molde): ativar `(8, 145, 158)` sobre `(175, 236, 239)`
(2,89, passa a `(6, 95, 103)`, 5,66); revisar `(180, 83, 9)` sobre `(255, 218, 185)` (3,82, passa a
`(146, 64, 14)`); vincular `(25, 115, 42)` sobre `(163, 228, 179)` (4,06) e processar
`(0, 85, 187)` sobre `(162, 210, 255)` (4,37).

## 5. Tipografia

Uma família: **`Font.'Segoe UI'`**, declarada uma vez como o token `fxFont` e usada como `Font: =fxFont` (nativa do Fluent 2, em todos os clientes). Duas famílias
sem regra (cabeçalho em uma, formulário em outra) é defeito. Hierarquia por **peso e tamanho**:
usar só `Semibold` e `Bold` achata a hierarquia.

| Papel | Tamanho | Peso | Token |
|---|---|---|---|
| título de tela | 35 (compacto 28) | Semibold | `fxFontSizeTitle` |
| valor de KPI | 25 (compacto 20) | Bold | `fxFontSizeKPI` |
| título de seção ou modal | 16 a 18 | Bold | `fxModalTitleSize` (16) |
| corpo, input, mensagem | 14 | Normal | `fxFontSizeBody` |
| linha de tabela | 13 (compacto 11) | Normal | `fxFontSizeTable` |
| cabeçalho de coluna | 13 (compacto 11) | Bold | `fxFontSizeHeader` |
| caption, badge | 12 (compacto 11) | Normal ou Semibold | `fxFontSizeTableSmall` |
| rótulo de KPI | 11 | Semibold | `fxFontSizeKPITitle` |
| toast: ícone, título, mensagem | 18, 15, 12 | Bold, Bold, Normal | `fxFontSizeToastIcon`, `fxFontSizeToastTitle`, `fxFontSizeToast` |
| aviso de acesso negado | 20 | Bold | `fxFontSizeSemAcesso` |

Piso para rótulo de formulário: 12. Rótulo menor que o valor do campo inverte a hierarquia.

## 6. Layout e grid

Canvas fixo **1920 por 1080**, ManualLayout (decisão T1). Faixas verticais típicas:

| Faixa | Y | Altura |
|---|---:|---:|
| cabeçalho | 0 | 100 |
| KPIs | 110 | 85 (65) |
| filtros | 120 a 220 | 100 |
| abas | 250 | 46 mais traço de 3 |
| cabeçalho de tabela | 196 | 50 (35) |
| galeria | ~246 | `fxRowHeight * 12` |
| rodapé | 1040 | 40 |

- **Margem lateral única** (`fxLayoutMargin`): é comum as telas terem margens
  diferentes entre si e o token não ser usado por nenhuma. Defina o token **igual ao que
  as telas usam** (aqui 100 no modo normal) e use-o.
- **Gutter** entre cards: `fxLayoutGutter`, igual em todas as réguas de KPI.
- `X` de elementos repetidos por **fórmula** (`base + (largura + gutter) * n`), nunca digitado.
- `fxIsCompact = App.Width < 1600` é o único breakpoint; responsividade é token condicional, não
  AutoLayout. Se o projeto for responsivo de verdade, a recomendação oficial é desligar *Scale
  to fit*, usar `Parent.*` e containers, e é **outra decisão** (T1 muda; precisa de ADR).
  Arrastar ou redimensionar um controle no Studio **sobrescreve** as fórmulas de `X`, `Y`, `Width`
  e `Height` por constantes
  ([Create responsive layout](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-responsive-layout)).

## 7. Catálogo de mensagens `fxMsg*`

- Mensagem em **pares**: `fxMsgXError` (o que houve) e `fxMsgXHint` (o que fazer). É o padrão
  que a orientação oficial de erro recomenda.
- **Com acentuação.** Um catálogo sem acentos (`"Voce nao tem permissao"`) lê como falha de
  encoding num app inteiro em pt-BR.
- Mensagem **do domínio** (de uma regra de negócio) fica no catálogo do projeto, não no molde
  genérico. Mensagem **de regra** que vem do flow chega pronta em `description`.
- Toda string visível por token, também placeholder e título de modal; checagem automática de
  literais é item aberto do validador.

## 8. Como evoluir os tokens

1. Edite **só** [app-formulas-tokens.md](../assets/app-formulas-tokens.md) (ou o equivalente do
   projeto) e cole de novo na propriedade `Formulas`.
2. Fonte única entre projetos: mantenha um arquivo de tokens e injete no bloco `Formulas` de cada projeto
   por script, em vez de copiar à mão; cópia manual diverge.
3. Tema moderno (`App.Theme`, paleta de 16 tons gerada de `BasePaletteColor`, preview) é
   alternativa para app com controles modernos; aplicar tema moderno em controle Classic não
   alinha visualmente com o Fluent v9 e **ligar "Lock primary color" pode quebrar contraste**
   ([Modern theming](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/modern-controls/modern-theming)).
   Fora do padrão v1.
4. Ao trocar a marca, recalcule o contraste de todos os pares da §3 e §4 antes de colar.

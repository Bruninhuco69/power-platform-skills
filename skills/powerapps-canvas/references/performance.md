# Desempenho e carregamento

Cada padrão vem como **problema, sintoma, solução, quando não usar**. Delegação (o que baixa e o
que roda no servidor) está em [delegacao.md](delegacao.md); timers e auto-refresh, em
[timers-async.md](timers-async.md). Achados de diagnóstico de apps reais estão em
[licoes-de-campo.md](licoes-de-campo.md).

## Sumário

1. [`OnStart` mínimo e named formulas](#1-onstart-mínimo-e-named-formulas)
2. [`Concurrent`](#2-concurrent)
3. [Carga adiada de telas](#3-carga-adiada-de-telas)
4. [Carga adiada de dados](#4-carga-adiada-de-dados)
5. [Paginação](#5-paginação)
6. [Cache de domínio](#6-cache-de-domínio)
7. [Controles por tela](#7-controles-por-tela)
8. [`With` e recomputação](#8-with-e-recomputação)
9. [Imagens e mídia](#9-imagens-e-mídia)
10. [Consulta em propriedade de UI](#10-consulta-em-propriedade-de-ui)
11. [Fanout de `Set` global](#11-fanout-de-set-global)
12. [Limite de conectores](#12-limite-de-conectores)
13. [Cobertura de loading](#13-cobertura-de-loading)
14. [Como medir](#14-como-medir)
15. [Fontes](#15-fontes)

Anti-padrões nomeados pela Microsoft: "loading too much data, turning everything into
collections, and overloading OnStart"
([Create performant apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-performant-apps-overview)).

---

## 1. `OnStart` mínimo e named formulas

**Problema.** O `OnStart` roda em sequência antes do app ficar utilizável, mesmo que 90% do que
ele carrega só seja usado na quinta tela. **Sintoma.** Spinner de abertura longo, Studio lento
para abrir, aviso "Inefficient Delay Loading" no App checker.

**Solução.** Mover para `App.Formulas` tudo o que é constante ou derivado. A Microsoft relata
queda do tempo de carga do Studio de até 80% só com essa troca
([Working with large apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/working-with-large-apps)).
Named formula tem quatro propriedades que o `OnStart` não tem: sempre disponível, sempre
atualizada, definição imutável e cálculo adiável. E *"There's no penalty for including a formula
definition that isn't used"*: uma named formula pesada que nenhuma tela lê custa zero; o mesmo
cálculo num `Set` do `OnStart` custa uma consulta em todo boot
([App object](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)).

| O valor... | Vai para |
|---|---|
| nunca muda depois de calculado (tema, `User()`, derivados, listas de referência) | `App.Formulas` |
| muda por ação do usuário | `OnStart` (só inicialização) ou `OnVisible` |
| só existe numa tela | `UpdateContext` no `OnVisible` |
| depende de uma ação (`Patch`, `.Run()`) | nunca em `Formulas` |

**Quando não usar.** Qualquer coisa com `Set`, `Collect`, `Patch`, `Notify`, `Navigate`,
`Reset`; valor que o usuário edita; referência circular. `StartScreen` não enxerga global nem
coleção, só named formula. Molde: [app-onstart-molde.md](../assets/app-onstart-molde.md).

## 2. `Concurrent`

**Problema.** Uma cadeia de `ClearCollect` sequenciais paga a latência de rede n vezes.
**Solução.** `Concurrent(a; b; c)` para chamadas **independentes**.

Contratos documentados: a ordem de início e término é imprevisível; em alguns dispositivos só
parte das fórmulas roda de fato em paralelo; se uma falha, as outras continuam
([Concurrent](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-concurrent)).

**Quando não usar.** Há dependência entre os ramos (use `Concurrent` separados e sequenciais);
são `Set` triviais (CPU pura, sem I/O, só adiciona overhead); mais de ~10 chamadas simultâneas
(risco de throttling, [Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)).

## 3. Carga adiada de telas

1. Deixe **Delayed load** ligado (padrão em app novo).
2. **Nunca referencie controle de outra tela**: uma referência cruzada anula a carga adiada da
   tela referenciada (aparece como "Inefficient Delay Loading").
3. **A primeira tela deve ser leve**: ela é empacotada com a lógica de inicialização
   ([Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)).
   Um menu inicial que renderiza três agregações já no primeiro paint paga três consultas antes
   de qualquer clique; mova os KPIs para carga sob demanda (botão, ou `Visible` ligado a uma
   flag) ou use `StartScreen` para uma tela leve.
4. Controle **inicialmente invisível não é renderizado** (apps novos desde dez/2022). Vale só
   para o estado inicial: depois que o usuário troca de aba, tudo foi instanciado e permanece.
   Aba pesada precisa estar oculta no estado inicial.

**Quando não usar.** Só desligue Delayed load se `ConfirmExit` precisar referenciar controle
fora da primeira tela (senão o app publicado não abre).

## 4. Carga adiada de dados

Hierarquia de custo, do mais barato:

| Técnica | Quando | Custo |
|---|---|---|
| consulta direta no `Gallery.Items` | lista que o usuário só lê e rola | zero até a galeria renderizar |
| named formula | valor derivado lido em 1 ou mais telas | zero até alguém ler |
| `ClearCollect` no `Screen.OnVisible` | dado filtrado ou ordenado localmente na tela | 1 ida ao servidor ao entrar |
| `ClearCollect` sob demanda (abrir aba ou modal) | detalhes, listas dependentes | 1 ida no clique |
| `ClearCollect` no `App.OnStart` | quase nunca | penaliza todo boot |

Padrão "carregar ao abrir a aba", com a coleção como cache da sessão:

Destino: YAML colado.

```yaml
# xx-btn-tab-referencias.OnSelect
OnSelect: |-
  =Set(varXXTab, 2);
  If(
    IsEmpty(colReferencias),
    Set(varShowLoading, true);
    Set(varLoadingMessage, fxMsgLoadingDefault);
    ClearCollect(colReferencias, ShowColumns(Referencia, "Id_Referencia", "Descricao"));
    Set(varShowLoading, false)
  )
```

`ShowColumns` não é opcional: com *Explicit column selection* ligada, só as colunas declaradas
sobrevivem à coleção ([Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)).
Telas bem comportadas têm `OnVisible` só com estado (`Set`/`Clear`), sem I/O; os dados vêm do
`Items`.

**Quando não usar.** Lista de referência **pequena e estável** usada por 4 telas ou mais: carregue
uma vez (ou named formula). Dado exigido pelo `StartScreen`.

## 5. Paginação

**Problema.** Galeria cujo `Items` devolve milhares de linhas, ou que compensa com um `FirstN` fixo
que **esconde** registros do usuário. **Sintoma.** Rolagem travada; "o registro existe mas não
aparece".

A galeria pagina em incrementos de ~100 linhas; mire 100 a 200 na consulta padrão
([Small data payloads](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/small-data-payloads)).
`FirstN` não delega: sobre filtro não delegável vira "top N das primeiras 500 arbitrárias".

**Solução A: "carregar mais"** (sobre `Items` delegável):

Destino: YAML colado.

```yaml
# botão xx-btn-carregar-mais
Visible: ='xx-gal-pedidos'.AllItemsCount >= varLinhasVisiveis
OnSelect: =Set(varLinhasVisiveis, varLinhasVisiveis + fxPageSize)
Text: ="Carregar mais (" & 'xx-gal-pedidos'.AllItemsCount & " carregadas)"
```

**Solução B: página fixa sobre coleção**: `LastN(FirstN(colDados, varPagina * fxPageSize), fxPageSize)`;
próxima página só `If(varPagina * fxPageSize < CountRows(colDados), Set(varPagina, varPagina + 1))`.

**`TemplateSize` nunca 0**: use `Max(20, ...)`. `MaxTemplateSize` alto demais (50.000) permite
linha de 50.000 px e tira a previsibilidade da virtualização; use o maior valor real esperado.

**Quando não usar.** `Items` já delegado e abaixo de 200 linhas. Se o usuário precisa de
**agregado do conjunto todo**, pagine a exibição e calcule o agregado separadamente
(ver [delegacao.md](delegacao.md) §3); nunca com `CountRows(gal.AllItems)`.

## 6. Cache de domínio

**Problema.** Tabela de domínio (unidades, tipos) consultada dezenas de vezes por sessão.
**Solução A, named formula** (para o que não muda na sessão): uma consulta por sessão,
avaliada quando o primeiro controle a lê, compartilhada entre telas.

Destino: barra de fórmulas do objeto App, propriedade `Formulas` (pt-BR: `;` e `;;`).

```powerfx
frmUnidades = SortByColumns(ShowColumns(Unidade; "Cod_Unidade"; "Nom_Unidade"); "Nom_Unidade"; SortOrder.Ascending);;
```

**Solução B, coleção com invalidação explícita** (quando o próprio app edita o domínio):

Destino: YAML colado.

```yaml
# Screen.OnVisible
OnVisible: |-
  =If(
    IsEmpty(colUnidades) || varUnidadesVelhas,
    ClearCollect(colUnidades, ShowColumns(Unidade, "Cod_Unidade", "Nom_Unidade"));
    Set(varUnidadesVelhas, false)
  )
```

Depois de qualquer `Patch` no domínio: `Set(varUnidadesVelhas, true)`.

**Quando não cachear.** Dado transacional que outro usuário altera em paralelo; tabela acima de
2.000 linhas (a coleção trunca). Se já é named formula, ela **já é** o cache: não copie para
coleção.

## 7. Controles por tela

**Problema.** Cada controle é um nó no motor de dependência; cada propriedade é uma fórmula
reavaliada. **Sintoma.** Tela demora a pintar; interação com lag sem rede.

- Não há limite oficial de controles por tela; a diretriz é qualitativa. A métrica comum de
  revisão (Power CAT Code Review Tool) sinaliza acima de ~300 controles por tela
  ([CODE_REVIEW.md](https://github.com/microsoft/Power-CAT-Tools/blob/main/CODE_REVIEW.md)).
  Os números "500 por app / 300 por tela" são recomendação de comunidade.
- Dentro do **template de galeria**, mais de ~10 controles pede revisão: com 30 linhas visíveis,
  40 controles por linha são ~1.200 instâncias.
- **Colapse rótulo e valor num só controle**; um `HtmlViewer` agregado por bloco no lugar de
  vários pares. `HtmlViewer` **não** substitui `Label` por desempenho (é mais caro): para par
  simples use `Label` com `FontWeight`.
- **Container por bloco visual, com `Visible` no container**, não em cada filho: centenas de
  `Visible` individuais são centenas de fórmulas reavaliadas a cada troca de aba.
- Tela com 300+ controles costuma ser três telas; mas não divida se isso criar referência entre
  telas (o remédio mata a carga adiada).
- Containers aninhados: no máximo 3 a 4 níveis; galeria, no máximo 2 níveis de aninhamento
  ([Gallery](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-gallery)).

## 8. `With` e recomputação

`With` evita avaliar a mesma subexpressão cinco vezes (e `LookUp` repetido, N+1 disfarçado). Use
para **escalar e constante**, nunca para envolver fonte de dados esperando delegação (ver
[delegacao.md](delegacao.md) §8). Valor lido por vários controles: named formula, não `With`.

Destino: YAML colado.

```yaml
# Gallery.Items sobre coleção já carregada
Items: |-
  =With(
    {
      fTipo: Coalesce('xx-cbo-filtro-tipo'.Selected.Value, "Todos"),
      fCodigo: varCodigoSelecionado
    },
    Filter(
      colDados,
      (fTipo = "Todos" || Tipo = fTipo) && (IsBlank(fCodigo) || Codigo = fCodigo)
    )
  )
```

## 9. Imagens e mídia

Prefira `.svg` a `.png` para ícone e logo. Use thumbnail do Dataverse (~1 KB, vem na resposta); a
imagem completa exige chamada separada e **nunca vai numa galeria**
([Efficient calculations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/efficient-calculations)).
`User().Image` repetido no cabeçalho de toda tela é uma chamada ao Graph por tela: valor imutável
na sessão é named formula (`frmUsuarioFoto = User().Image`).

## 10. Consulta em propriedade de UI

**Problema.** `Visible`, `Text`, `Fill`, `DisplayMode` e `Start` são reavaliadas a cada mudança
de dependência: consulta nelas é rede por render (N+1 invisível; 429 de throttling).
**Solução.** Calcule uma vez como named formula e leia dela.

Destino: barra de fórmulas do objeto App, propriedade `Formulas` (pt-BR).

```powerfx
frmTemHistorico = !IsEmpty(Historico);;
```

`CountIf(t; cond) > 0` é mais barato que `CountRows(Filter(t; cond)) > 0` onde `CountIf`
delega (Dataverse): o primeiro agrega no servidor, o segundo materializa. Aceitável só em
propriedade de **um** controle (fora de galeria) lido uma vez por sessão, e mesmo assim a named
formula é melhor.

## 11. Fanout de `Set` global

Cada `Set` de global invalida todo controle que a referencia: 150 `Set` numa transação são 150
ondas de invalidação (congelamento de 1 a 3 s sem rede no Monitor). **Uma lista de valores é uma
coleção, não N variáveis numeradas.** `Set` global é certo para estado de UI compartilhado, de
baixa cardinalidade e poucos leitores (`varShowLoading`, `varShowToast`).

## 12. Limite de conectores

Mantenha **no máximo 10 conectores e 20 connection references** por app; acima disso o carregamento
fica mais lento e salvar pode falhar
([Connections list](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections-list)).
A cifra "30" que circula na comunidade vem de documentação antiga.
Consolidar flows de contrato parecido num só, com parâmetro `acao`, reduz conectores; não
consolide flows de segurança ou SLA muito diferentes. Instanciar um flow custa ~0,6 s
([Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)).
Duas tabelas com nomes quase iguais (singular e plural) podem ser a mesma tabela adicionada
duas vezes: cada uma conta como conexão.

## 13. Cobertura de loading

**Problema.** Operação longa sem feedback: o usuário clica de novo e dispara duas vezes.
**Solução.** Todo botão que chama flow, ou que roda cadeia pesada, liga `varShowLoading` antes e
desliga **em todos os caminhos de saída**, e se desabilita enquanto isso:
`DisplayMode: =If(varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)`. Fluxo completo em
[chamada-flow.md](chamada-flow.md); bloco do overlay em [ux-feedback.md](ux-feedback.md).

**Quando não usar overlay bloqueante.** Operação abaixo de ~300 ms (o piscar incomoda mais que a
espera) e operação em que o usuário pode continuar trabalhando: indicador local no botão.

## 14. Como medir

- **Live monitor** (*Advanced tools > Open live monitor*; no app publicado, menu do app >
  Live monitor > Play published app): cada chamada, linhas, duração. Exige Environment Admin ou
  Maker. É a única forma confiável de provar gargalo de dados
  ([Monitor](https://learn.microsoft.com/en-us/power-apps/maker/monitor-overview)).
- `Settings > Debug published app` mostra as fórmulas no Monitor do app publicado, mas
  *"has a detrimental impact on the performance of your app for all your users"*: ligue, meça,
  desligue.
- Métricas de tenant (Managed Environments): taxa de abertura, tempo até interativo (TTI), tempo
  até carga completa (TTFL), latência de dados; percentil 75, recalculado a cada 24 h
  ([Monitor app performance](https://learn.microsoft.com/en-us/power-apps/maker/common/monitor-app-performance)).
- Cronômetro dentro do app: `Set(varT0, Now())` antes e
  `DateDiff(varT0, Now(), TimeUnit.Milliseconds)` depois.

Checklist de diagnóstico (cada item é binário):

1. **Data row limit = 1** num clone: lista que some tem consulta não delegável.
2. App checker: há "Inefficient Delay Loading"? Há aviso de delegação? Anote controle e fórmula.
3. Live monitor no boot: requisições **antes** do primeiro paint (meta: 0 a 2).
4. Live monitor com 60 s parado na tela: há requisição recorrente (timer ou consulta em UI)?
5. Live monitor ao rolar a galeria: uma por página (bom) ou uma por linha (N+1)?
6. Controles por tela (acima de ~300) e por template de galeria (acima de ~10).
7. `OnStart` tem `ClearCollect`? Migre.
8. Alguma fórmula passa de 256.000 caracteres? Quase todo app de carga lenta tem uma
   ([Working with large apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/working-with-large-apps)).
9. Conectores no máximo 10; connection references no máximo 20.
10. Cada `IfError` tem fallback que não se confunde com dado válido.

## 15. Fontes

- [How to create performant Power Apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-performant-apps-overview)
- [Small data payloads](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/small-data-payloads)
- [Efficient calculations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/efficient-calculations)
- [Fast app/page load](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/fast-app-page-load)
- [Working with large apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/working-with-large-apps)
- [Top performance issues](https://learn.microsoft.com/en-us/power-platform/architecture/key-concepts/performance/top-issues)
- [Monitor canvas apps](https://learn.microsoft.com/en-us/power-apps/maker/monitor-canvasapps)

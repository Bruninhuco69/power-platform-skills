# Nomes e tipos de coluna Dataverse no Power Fx

Como a tabela e a coluna se chamam em cada lugar, como o Power Fx as resolve e como se
compara, filtra e grava cada tipo. Os exemplos usam um domínio fictício: tabela `Pedidos`, com a
coluna `situacao` (Choice), `cliente` (Lookup para `Clientes`), `unidade` (texto) e `ativo` (Yes/No).

## Sumário

1. [Publisher e prefixo](#1-publisher-e-prefixo)
2. [Os quatro nomes](#2-os-quatro-nomes)
3. [Qual nome em cada contexto](#3-qual-nome-em-cada-contexto)
4. [Row scope: o Power Fx resolve pelo nome de exibição](#4-row-scope-o-power-fx-resolve-pelo-nome-de-exibição)
5. [Nome da fonte de dados e chave primária](#5-nome-da-fonte-de-dados-e-chave-primária)
6. [Choice, Lookup, texto, Yes/No: o que muda](#6-choice-lookup-texto-yesno-o-que-muda)
7. [Tabela de decisão por tipo](#7-tabela-de-decisão-por-tipo)

---

## 1. Publisher e prefixo

Toda tabela e coluna **customizada** carrega o prefixo do *publisher* da solução em que foi
criada (`<prefixo>_`). O prefixo é do publisher, não do projeto:

- Criado no maker **fora de uma solução própria**, o componente cai no publisher padrão do
  tenant ou do ambiente, cujo prefixo é gerado e não é o que o plano previu.
- Pela Web API o prefixo **não** é aplicado sozinho: precisa vir no `SchemaName`.
- Importar um Excel para tabela nova cria colunas com o prefixo do publisher ativo.

Consequência prática: o prefixo do plano pode não ser o do ambiente. O que vale é o do
`NOMES-AS-BUILT.md`. Declare-o em `power-platform.config.json` (`prefixo_publisher`).
`[verificado: projetos de referência]` — o ambiente real usava o publisher padrão
do tenant, com prefixo diferente do planejado.

## 2. Os quatro nomes

| Nome | Exemplo | Quem define | Onde aparece |
|---|---|---|---|
| **Exibição** (`DisplayName`) | `situacao` | Quem criou a coluna | Maker, Studio, identificadores em fórmula |
| **Lógico** (`LogicalName`) | `<prefixo>_situacaodopedido` | Gerado na criação, minúsculo | Strings em `SortByColumns`/`DisplayFields`, OData, Web API, flow (expressões) |
| **Schema** (`SchemaName`) | `<prefixo>_SituacaoDoPedido` | Gerado na criação, com maiúsculas | Corpo de criação via Web API; na prática o lógico é o schema em minúsculas |
| **EntitySet** | `<prefixo>_pedidos` | Plural do lógico da tabela; leia o `EntitySetName` do ambiente | URL da Web API e do `$batch` |

**O lógico não sai do de exibição por regra.** Dois exemplos do mesmo ambiente: `nome_completo`
virou `<prefixo>_nomecompleto` (perdeu o `_`) e `nome_curto` virou `<prefixo>_nome_curto` (manteve).
Depende de como a coluna foi criada. Tem que ser lido do ambiente (`references/nomes-as-built.md`).
`[verificado: projeto de referência]`

Outros fatos sobre nomes lógicos:

- O nome pode estar **truncado** em capturas do maker (`<prefixo>_dataprevistadeencerramentod…`). A Web API
  devolve o nome inteiro; capturas de tela, não.
- Coluna com nome de exibição **repetido** na tabela é ambígua em Power Fx. O extrator acusa (D001).
- Colunas de sistema (`createdon`, `ownerid`, `statecode`) não têm prefixo.

## 3. Qual nome em cada contexto

| Contexto | Nome | Exemplo |
|---|---|---|
| Identificador numa fórmula (`Filter`, `LookUp`, `Sort`, `ThisItem.col`, chave de registro em `Patch`) | **Exibição** | `Filter(Pedidos; unidade = "AAA")` |
| Texto entre aspas duplas: `SortByColumns`, `DisplayFields`, `SearchFields` de ComboBox, e demais funções que recebem o nome da coluna como string | **Lógico** | `SortByColumns(Pedidos; "<prefixo>_datadopedido"; SortOrder.Descending)` |
| Identificador sem aspas em `ShowColumns`/`RenameColumns`/`AddColumns` | **Exibição** | `ShowColumns(Pedidos; unidade)` |
| Coleção em memória (`ClearCollect`, `Table`) | O nome que a própria coleção define (`Value`, etc.); prefixo **não** se aplica | `DisplayFields: =["Value"]` |
| Conector que não é Dataverse (Office 365 Usuários, etc.) | Campo do conector (`DisplayName`, `Mail`) | `DisplayFields: =["DisplayName"]` |
| Flow: conteúdo dinâmico no designer | Exibição | — |
| Flow: expressão (`outputs()?['…']`), Web API, `$select`/`$filter`, corpo do `$batch` | **Lógico** | `"<prefixo>_unidade": "@item()?['Cod_Unidade']"` |
| URL do `$batch`/Web API | **EntitySet** | `POST /api/data/v9.2/<prefixo>_pedidos` |

Regra prática: **identificador = exibição; string = lógico.** `[verificado: projeto de referência]` — o
`SortByColumns(…; "nome_completo"; …)` escrito com exibição foi corrigido para o lógico no Studio. As
funções que recebem nome de coluna como string (`SortByColumns`, `GroupBy`, `AddColumns`, `ShowColumns`,
`RenameColumns` com string, `DisplayFields`, `SearchFields`) exigem o lógico.

Fonte para o comportamento do conector Dataverse no Power Apps:
[Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service).

## 4. Row scope: o Power Fx resolve pelo nome de exibição

Dentro de `Filter`, `LookUp`, `Sort`, `AddColumns` e demais funções que abrem o escopo de linha, o
identificador de coluna é resolvido contra as colunas **da tabela daquele escopo**, pelo nome de
**exibição**. Um nome lógico — sobretudo de *outra* tabela — não resolve e a fórmula não compila.

Caso real `[verificado: projeto de referência]`: o `OnStart` tinha uma cadeia com `Distinct(…; <prefixo>_unidade)`,
onde `<prefixo>_unidade` era o nome lógico de uma coluna de outra tabela. O bloco não compilou e
**derrubou todas as variáveis globais** definidas depois dele: toda tela abriu em erro. Correção:
usar o nome de exibição da coluna da tabela do escopo e, para coluna de outra tabela, renomear antes
(`RenameColumns`) ou buscar o registro (`LookUp`) e ler o campo.

```
// barra de fórmulas (pt-BR: ; e ;;)
// Errado: nome lógico de coluna de outra tabela dentro do escopo de linha
ClearCollect(
  colUnidades;
  Sort(Distinct(Pedidos; <prefixo>_unidade); Value)
);;

// Certo: nome de exibição da coluna do escopo
ClearCollect(
  colUnidades;
  Sort(Distinct(Pedidos; unidade); Value)
);;
```

Duas consequências:

1. Erro em `OnStart` não é local: uma fórmula que não compila no `OnStart` leva junto as globais
   seguintes. Execute o `OnStart` (menu do app → *Executar OnStart*) e confira o painel de variáveis.
2. `DisplayFields`/`SearchFields` **não** são row scope: são strings avaliadas pelo controle contra a
   fonte, e aí o lógico é o certo. Misturar as duas regras é o erro mais comum.

> `Distinct` não delega no Dataverse (`references/delegacao-dataverse.md`); o exemplo é só sobre
> nome. Em tabela grande a lista de valores vem de uma tabela de domínio ou de um flow.

## 5. Nome da fonte de dados e chave primária

- O nome da **fonte de dados** no app é o nome com que a tabela foi adicionada no painel de dados do
  app — normalmente o nome de exibição da tabela, mas pode vir com alias (singular/plural) diferente
  do da tabela. Leia o painel de dados, não suponha. `[verificado: projetos de referência]`
- Nome com hífen, espaço ou que comece com dígito exige **aspas simples**: `'pedidos-unidade'`.
  Aspas simples dentro do nome são dobradas (`'d''ouro'`).
- A **chave primária** (`PrimaryIdAttribute`, `<tabela>id`) tem como nome de exibição o próprio nome
  da tabela. Em fórmula isso colide e pede aspas: `varPedidoSel.'pedidos-unidade'` devolve o GUID.
  Ao enviar o GUID a um flow, converta com `Text(...)`. `[verificado: projeto de referência]`
- O **nome principal** (`PrimaryNameAttribute`) é obrigatório em toda tabela e é o rótulo que o
  Dataverse usa em grade e Lookup — não é necessariamente a coluna "descritiva" que a tela mostra.

## 6. Choice, Lookup, texto, Yes/No: o que muda

Mapeamento oficial de tipos do conector (Dataverse → Power Apps): Choice e Yes/No → *Choice*; Date
Time e Date Only → *DateTime*; Whole/Decimal/Float/Currency → *Number*; Text, Email, URL e Memo →
*Text*; Unique Identifier → *Guid*
([fonte](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service)).

### 6.1 Choice

O nome da Choice em Power Fx é `'<coluna> (<tabela>)'`; as opções são propriedades dele.
`[verificado: projeto de referência]`

Destino: barra de fórmulas do Studio em locale pt-BR (`;` e `;;`).

```
// Filtrar por uma opção conhecida
Filter(Pedidos; situacao = 'situacao (Pedidos)'.Aberto)

// Filtrar pelo que o usuário escolheu num ComboBox cujo Items é Choices('situacao (Pedidos)').
// Dois ramos de If FORA do Filter: IsBlank(...) || ... dentro do Filter quebra a delegação
// (delegacao-dataverse.md §4)
If(
    IsBlank(cboSituacao.Selected);
    Pedidos;
    Filter(Pedidos; situacao = cboSituacao.Selected.Value)
)

// Gravar: precisa do REGISTRO da opção, não do texto
Patch(Pedidos; Defaults(Pedidos); { situacao: 'situacao (Pedidos)'.Aberto })

// Exibir como texto
Text(ThisItem.situacao)
```

Destino: propriedades do ComboBox no YAML colado (`,` entre argumentos).

```yaml
Items: =Choices('situacao (Pedidos)')
DisplayFields: =["Value"]
SearchFields: =["Value"]
```

Pontos de atenção:

- Comparar a Choice com `.Selected` (registro) falha; `.Selected.Value` funciona quando o `Items`
  vem de `Choices(...)`. Comparar com texto literal (`situacao = "Aberto"`) não compila.
  `[verificado: projeto de referência]`
- Gravar texto numa Choice não compila: use o objeto da opção, ou um `Switch` que traduz o rótulo
  na opção.
- Delegação: `=` e `<>` delegam em Choice; `<`, `<=`, `>`, `>=` e `IsBlank` **não**
  ([Learn](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service)).
  Para "sem valor", a nota 9 da tabela oficial aceita `col = Blank()` em geral, mas a linha de
  Choice marca `IsBlank` como não delegável: teste `situacao = Blank()` com `Data row limit = 1`
  antes de confiar `[não verificado]`.
- `Choices(...)` não delega e devolve a lista de opções: serve a ComboBox, não a tabela grande.
- Se a coluna **não é** Choice no ambiente, `Choices()` não existe para ela e o domínio vive no app
  (tabela literal em `Items`) — ver §7.
- Choice **global** compartilha as opções entre tabelas; o nome em Power Fx continua
  `'<coluna> (<tabela>)'`. [não verificado] se o nome muda para global puro em todo ambiente.
- Valores inteiros das opções: o Dataverse prefixa por publisher (ex.: `<n>0000001`). Não presuma
  `1, 2, 3` em CSV de carga ou em contrato com sistema externo; leia as opções do ambiente
  (`GlobalOptionSetDefinitions(Name='…')`, ver `references/nomes-as-built.md`).

### 6.2 Lookup

```
// barra de fórmulas (pt-BR: ; e ;;)
// Comparar com o registro
Filter(Pedidos; cliente = varClienteSel)

// Gravar: passar o registro
Patch(Pedidos; Defaults(Pedidos); { cliente: LookUp(Clientes; nome = "Cliente A") })

// Ler um campo do relacionado
ThisItem.cliente.nome
```

`[não verificado no ambiente]`: os projetos de referência trocaram todos os Lookup por texto/Choice
antes de escrever essas fórmulas; a sintaxe acima é a documentada para Lookup, sem evidência de
campo. Cuidados que valem independente disso:

- Filtrar por **coluna do relacionado** (`cliente.nome = "X"`) obriga a junção no servidor. Os
  limites estruturais do conector (níveis de lookup, entidades por consulta) estão em
  `references/delegacao-dataverse.md`. Para filtro quente, **desnormalize**: copie a coluna para a
  tabela filha como texto (`references/modelagem.md`).
- `DefaultSelectedItems` quer **linhas da mesma fonte de `Items`**; `Table(<texto>)` não serve.
  `[verificado: projeto de referência]`

### 6.3 Texto que guarda código (o "lookup de mentira")

Coluna de texto que guarda a sigla, o nome ou o código de outra tabela. Compara texto com texto:

```
// barra de fórmulas (pt-BR: ; e ;;)
Filter(Pedidos; unidade = cboUnidade.Selected.sigla)   // Selected.sigla, não Selected
ThisItem.unidade                                       // já é texto
```

Delega igual a qualquer igualdade de texto. O que se perde: **integridade referencial** (valor
inválido entra, homônimo colide) e a junção automática. Ver `references/modelagem.md`.

### 6.4 Yes/No

`ativo = true` funciona e delega; também existe `'ativo (Pedidos)'.Sim` (rótulo pt-BR). Prefira
`true`/`false`. `[verificado: projeto de referência]`

### 6.5 Data

`DateOnly` e `DateAndTime` mapeiam para DateTime. Filtro de data direto delega no Dataverse, **exceto**
`Now()` e `Today()` aplicados como função de data (nota 3 da tabela oficial, em conflito com a página
de delegação; ver `references/delegacao-dataverse.md`): calcule a data numa variável antes. Diferente
do conector SQL, onde a data direta não delega atrás de gateway (`decisoes-padrao.md` B2).

## 7. Tabela de decisão por tipo

| Tipo real (`AttributeType`) | Comparar | Grava | `Items` do ComboBox | Atenção |
|---|---|---|---|---|
| `Picklist` (Choice) | `col = 'col (Tabela)'.Opção` ou `col = cbo.Selected.Value` | objeto da opção | `Choices('col (Tabela)')` | `<`/`IsBlank` não delegam |
| `Boolean` (Yes/No) | `col = true` | `true`/`false` | — | — |
| `Lookup` | `col = registro` | registro (`LookUp`/`.Selected`) | `Filter(TabelaAlvo; …)` | filtrar por coluna do relacionado: desnormalizar |
| `String` guardando código | `col = cbo.Selected.<coluna>` | texto | tabela de domínio ou literal | sem integridade; domínio no app |
| `String` guardando domínio fixo | `col = "Texto"` | texto | `["A"; "B"]` (expõe `Value`) | domínio vive na tela; nada impede o flow de gravar fora dele |
| `Integer`/`Decimal` | `col = n` | número | — | aritmética na coluna não delega |
| `DateTime` | `col >= dataVar` | data | — | `Today()`/`Now()` em variável |
| `Uniqueidentifier` | `col = GUID(...)` | — | — | `Text(...)` ao enviar ao flow |

A pergunta que decide a sintaxe é sempre a mesma: **qual é o `AttributeType` desta coluna no
as-built?** Se o as-built diz `?`, a fórmula não é escrita até alguém ler o tipo.

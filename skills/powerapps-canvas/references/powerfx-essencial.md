# Power Fx essencial

Referência acionável para escrever Power Fx num app Canvas. Delegação: [delegacao.md](delegacao.md).
Chamada de flow: [chamada-flow.md](chamada-flow.md). Desempenho: [performance.md](performance.md).

Todo bloco diz o **destino**. Blocos `yaml` estão no dialeto do YAML colado (`,` argumento,
`;` encadeia, `.` decimal) e são validados por `scripts/validar-telas.py`. Blocos `powerfx` estão
no dialeto da barra de fórmulas em pt-BR (`;` argumento, `;;` encadeia, `,` decimal).

## Sumário

1. [Separadores por destino](#1-separadores-por-destino)
2. [Variáveis e escopo](#2-variáveis-e-escopo)
3. [Coleções](#3-coleções)
4. [Erro](#4-erro)
5. [Datas e fuso](#5-datas-e-fuso)
6. [Texto, número e máscara](#6-texto-número-e-máscara)
7. [Navegação](#7-navegação)
8. [Gravação: flow, Patch e formulário](#8-gravação-flow-patch-e-formulário)
9. [Consulta rápida](#9-consulta-rápida)
10. [Fontes](#10-fontes)

---

## 1. Separadores por destino

O Power Fx adapta a sintaxe ao idioma de quem edita; o arquivo salvo é invariante.

| Destino | Argumento | Encadeia | Decimal |
|---|---|---|---|
| **YAML colado** (`.pa.yaml`, Code view) | `,` | `;` | `.` |
| **Barra de fórmulas** em pt-BR (inclui `App.OnStart`, `App.Formulas`) | `;` | `;;` | `,` |

Nome de função (`If`, `Filter`), propriedade (`Screen.Fill`), enum (`FontWeight.Bold`) e o
operador `.` de seleção são sempre em inglês, em qualquer idioma
([Global support in Power Fx](https://learn.microsoft.com/en-us/power-platform/power-fx/global)).
Misturar os dois dialetos num bloco não compila em nenhum. A regra do kit está em
[decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md) §3.

Em `Text()` com formato, o prefixo de locale é explícito e não depende de quem edita:

Destino: YAML colado.

```yaml
# Formatos
Data: =Text(Now(), "[$-pt-BR]dd/mm/yyyy hh:mm")
IdParaFlow: =Text(varPedido.Id_Pedido, "[$-en-US]0")
```

Sem o prefixo, o formato é interpretado no idioma de quem editou a fórmula. **`Text(<inteiro>)`
em pt-BR gera `"1.234"`**: id enviado a flow ou JSON usa sempre `[$-en-US]0`
`[verificado: projeto de referência]`.
Separador de milhar dentro do formato é ambíguo entre locales; para exibir contagem com ponto
use `Substitute(Text(n, "[$-en-US]#,##0"), ",", ".")` e teste no seu Studio `[não verificado]`.

## 2. Variáveis e escopo

| | `Set()` global | `UpdateContext()` de tela | Named formula (`App.Formulas`) |
|---|---|---|---|
| Alcance | app | uma tela | app |
| Quem escreve | qualquer fórmula | só a tela dona | ninguém (imutável) |
| Quando calcula | no `Set` | no `UpdateContext` | **quando alguém lê** |
| Atualiza sozinha | não | não | sim, reativa às dependências |
| Efeito colateral | permitido | permitido | **proibido** |
| Existe antes do `OnStart` | não | não | sim |

Prefixos: `var*` global, `ctx*` contexto, `col*` coleção, `fx*` token/named formula. Global e
contexto com o mesmo nome são **duas variáveis**: na tela, a de contexto sombreia a global e o
`Set` escreve onde ninguém lê. O prefixo `ctx*` impede a colisão.

### 2.1 Named formula

Vantagens documentadas: o valor está sempre disponível e atualizado, a definição é a fonte
única e o cálculo pode ser adiado até alguém ler. Limites: sem função de comportamento (`Set`,
`Collect`, `Patch`, `Notify`, `Navigate`), sem referência circular
([App object](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)).

**Regra do kit (T6): named formula nunca lê variável global.** Ela só recalcula quando um
insumo dela muda; `Refresh()` não a reexecuta e o número fica velho (foi a causa de KPI que não
batia nos projetos de referência). `[verificado: projeto de referência]`

Destino: barra de fórmulas do objeto App, propriedade `Formulas` (pt-BR).

```powerfx
fxColorPrimary = RGBA(15; 108; 189; 1);;
fxIsCompact = App.Width < 1600;;
fxRowHeight = If(fxIsCompact; 40; 50);;
frmUsuarioFoto = User().Image;;
```

### 2.2 Migrar do `OnStart` para `Formulas`

Recomendação da Microsoft: o `OnStart` pode causar problemas de carga; para cachear dado ou
criar variável global, use named formula; para a primeira tela, `StartScreen` em vez de
`Navigate`; para lógica de tela, `OnVisible`
([App object](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)).
Com o `OnStart` **não bloqueante** (padrão atual), variável inicializada nele pode não estar
pronta quando outra regra a lê, e uma tela pode renderizar antes de ele terminar.
`StartScreen` não enxerga global nem coleção; só named formula.

| O valor... | Vai para |
|---|---|
| nunca muda depois de calculado (tema, `User()`, derivados) | `App.Formulas` |
| muda por ação do usuário | `App.OnStart` (inicialização) ou `OnVisible` |
| só existe numa tela | `UpdateContext` no `OnVisible` |
| depende de ação (`Patch`, `.Run()`) | nunca em `Formulas` |

Molde: [app-onstart-molde.md](../assets/app-onstart-molde.md).

### 2.3 Função definida pelo usuário

`App.Formulas` aceita função com tipo, útil para o predicado de escopo ou a cor por status.

Destino: barra de fórmulas do objeto App, propriedade `Formulas` (pt-BR).

```powerfx
CorDoStatus(status: Text): Color =
    Switch(
        status;
        "aberto"; fxBadgeInfoText;
        "encerrado"; fxBadgeSuccessText;
        fxBadgeNeutralText
    );;
```

`[não verificado: disponibilidade de funções definidas pelo usuário no seu tenant]`

## 3. Coleções

Destino: YAML colado.

```yaml
# Colecoes
Carregar: =ClearCollect(colUnidades, ShowColumns(Unidade, "Cod_Unidade", "Nom_Unidade"))
Acrescentar: =Collect(colSelecionados, ThisItem)
Remover: =RemoveIf(colSelecionados, Id_Pedido = ThisItem.Id_Pedido)
```

- `ClearCollect` sempre baixa para a memória: **nunca delega** (teto 500/2.000 linhas).
- **Coleção de registros não tem `.Value`.** `Self.Selected.Value` devolve vazio; use o nome da
  coluna (`Self.Selected.Sigla`). A galeria que filtra por ele abre vazia sem erro.
- **Inverta `ForAll` + `Collect`**: `Collect(destino, ForAll(origem, {...}))` notifica os
  dependentes uma vez; `ForAll(origem, Collect(destino, {...}))` notifica a cada iteração
  ([Efficient calculations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/efficient-calculations)).
- `ThisRecord` desambigua escopo dentro de `ForAll`, `Filter`, `With`; qualifique quando o nome
  da coluna puder colidir com variável.
- `Concurrent(...)` só para chamadas **independentes**; a ordem de início e término é
  imprevisível e, com dependência entre ramos, o resultado é indeterminado
  ([Concurrent](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-concurrent)).
  Não serve para `Set` triviais (CPU pura, sem I/O).
- **`Gallery.AllItems` é caro**: gera uma tabela nova a cada leitura. Para contar, use
  `Gallery.AllItemsCount`. `AllItems` só enxerga o que já foi carregado (a paginação da galeria é
  de ~100 linhas): "marcar todos" numa galeria não rolada pega só a primeira página.

## 4. Erro

### 4.1 `IfError`

Destino: YAML colado.

```yaml
# Erro
Fluxo: |-
  =IfError(
    Set(varRet, 'app-flow-pedido-acao'.Run("encerrar", "1")),
    Trace("Falha: " & FirstError.Message);
    Set(varRet, Blank())
  )
```

`FirstError` e `AllErrors` trazem `Kind`, `Message`, `Source`, `Observed` e
`Details.HttpStatusCode`. `IfError` exige a feature **Formula-level error management**
(*Settings > Updates > Retired*): se estiver desligada, `IfError` não funciona direito
([IfError](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-iferror)).
Confira antes de confiar em `IfError` num app legado.

### 4.2 Por que valor mágico é errado

- O valor de fallback é **coagido para o tipo do primeiro argumento**; `IfError(1/x, "#DIV/0!")`
  vira outro erro.
- `IsError` e `IsBlankOrError` consomem o erro: nada chega ao `App.OnError`, ao log ou ao Monitor.
- `Blank()` reintroduz a ambiguidade que o tratamento de erro resolveu (nulo do banco x erro).
- `OnError` só controla o **relato**; não substitui o valor.

Regra: fallback só é aceitável se for impossível confundir com resultado real **e** a UI
sinalizar o estado degradado. `IfError(contagem, 50000)` falha nos dois (50.000 é o teto de
agregação do Dataverse). `Blank()` + `If(IsBlank(x), "-", x)` + cor de erro passa.

### 4.3 Repasse o erro inesperado

Destino: YAML colado.

```yaml
# Erro2
Dividir: =IfError(a / b, If(FirstError.Kind <> ErrorKind.Div0, Error(FirstError), -1))
```

### 4.4 `App.OnError`

Destino: barra de fórmulas do objeto App, propriedade `OnError` (pt-BR).

```powerfx
Trace($"Erro {FirstError.Message} em {FirstError.Source}");;
Error(FirstError)
```

`OnError` é avaliado em concorrência; use `With` para valores locais.

## 5. Datas e fuso

- Construção: `Today()`, `Now()`, `Date(2026, 7, 29)`, `DateValue("29/07/2026", "pt-BR")`.
- Aritmética: `DateAdd(x, n, TimeUnit.Days)`, `DateDiff(a, b, TimeUnit.Days)`.
- **Aritmética de data sempre do lado da constante, nunca do lado da coluna**: `DateAdd(coluna, ...)`
  não delega. Filtro de data atrás de gateway tem regra própria (coluna inteira `Ref_*`):
  [delegacao.md](delegacao.md) §Datas.
- Fuso: coluna *User local* é convertida na exibição; *Date only* e *Time-zone independent* não.
  `TimeZoneOffset()` não delega; converta a **variável** antes de filtrar.
- Dado vindo de UTC e `DatePicker` local deslocam o corte do dia em até algumas horas: decida
  **uma** regra (UTC no banco, conversão num só lugar) `[verificado: projeto de referência]`.
- Para flow, envie **texto com formato explícito** (`yyyy-mm-dd` ou ISO 8601), nunca data crua.

Destino: YAML colado.

```yaml
# Datas
ParaFlow: =Text('xx-dtp-filtro'.SelectedDate, "yyyy-mm-dd")
ParaTela: =Text(ThisItem.Dt_Inclusao, "[$-pt-BR]dd/mm/yyyy")
HaTrintaDias: =DateAdd(Today(), -30, TimeUnit.Days)
```

## 6. Texto, número e máscara

- Texto no Power Fx é **case-insensitive e accent-sensitive**; nenhuma collation do banco
  resolve o lado cliente. Normalize o domínio (acento, caixa) **na carga**, não na tela.
- `TextInput.Text` devolve `""`, não `Blank()`: filtro opcional testa os dois
  (`IsBlank(x) || x = ""`) ou usa `StartsWith(col, "")`.
- `Trim()` na carga de qualquer `CHAR(n)`: o SQL ignora o espaço à direita no `=`, o Power Fx
  compara literalmente.
- Booleano do SQL (`BIT`) é booleano no Power Fx: `Flg_Encerrar` é `true`/`false`, nunca `= 1`.
  Dentro de `Filter` delegado, `= true` e `<> true` excluem linha `NULL`; por isso o `BIT` deve
  ser `NOT NULL DEFAULT 0` (pedido ao dono do banco, skill `sql-procedures`).
- Nunca `Choices()` em fonte SQL: não há option set. Lista literal para domínio fixo
  (`["A", "B"]`) ou coleção para domínio de tabela.

**Máscara nunca vai para o filtro**: normalize a **variável**, compare a coluna crua.

Destino: YAML colado.

```yaml
# Mascara
Limpar: =Substitute(Substitute(Substitute(varBusca, ".", ""), "/", ""), "-", "")
Validar: =IsMatch(varCNPJ, "^\d{14}$")
FiltroDelegavel: =Filter(Cliente, Cod_Documento = varDocumentoLimpo)
```

Aplicar máscara de CNPJ (só exibição):

Destino: YAML colado.

```yaml
# Mascara2
Exibir: |-
  =With(
    { d: Substitute(Substitute(Substitute(varDocumento, ".", ""), "/", ""), "-", "") },
    If(
      Len(d) <> 14,
      varDocumento,
      Mid(d, 1, 2) & "." & Mid(d, 3, 3) & "." & Mid(d, 6, 3) & "/" & Mid(d, 9, 4) & "-" & Mid(d, 13, 2)
    )
  )
```

Busca de texto: prefira `StartsWith(coluna, termo)` (usa índice) a `Search` ou `termo in coluna`
(`LIKE '%x%'`, sem índice) e ligue `DelayOutput: =true` no campo para não consultar a cada tecla
([Optimized query data patterns](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/optimized-query-data-patterns)).

## 7. Navegação

Destino: YAML colado.

```yaml
# Navegar
Simples: =Navigate(Pedidos, ScreenTransition.Fade)
ComContexto: '=Navigate(Detalhe, ScreenTransition.CoverRight, { ctxPedido: ThisItem, ctxModo: "edicao" })'
```

- `Navigate` em `App.OnStart` está aposentado: força o `OnStart` a terminar antes da primeira
  tela. Use `App.StartScreen` (só named formula).
- `Reset(controle)` volta o controle ao `Default`; **não dispara `OnChange`** do `DatePicker`
  (todo botão Limpar reescreve a variável junto com o `Reset`).

## 8. Gravação: flow, Patch e formulário

Decisão A1 ([decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md)): **a tela
não grava direto na fonte quando há regra de negócio.** Escrita com regra passa por um flow
(que chama a procedure ou grava no Dataverse); o flow decide, valida e autoriza. Regra no
cliente é contornável e se duplica em cada tela. Chamada do lado do app:
[chamada-flow.md](chamada-flow.md).

| Situação | Caminho |
|---|---|
| operação com regra, mais de um efeito, ou que precisa de autorização | flow |
| registro **sem** regra de negócio e sem autorização (preferência do próprio usuário, rascunho) | `Patch` com `IfError` |
| formulário padrão | `SubmitForm`; `OnSuccess` recebe `Self.LastSubmit`, `OnFailure` mostra `Self.Error` |

Se usar `Patch`: `Defaults(fonte)` cria, `LookUp(fonte, chave)` atualiza, o retorno é o registro
gravado (capture com `Set`). `Patch` sobre registro lido antes sobrescreve os campos informados
sem checar mudança alheia; para operação sensível, releia e compare o estado antes.
`ForAll(col, Patch(...))` faz uma chamada por linha; prefira o `Patch` com tabela de registros.
Em fonte SQL, deixe a conta do conector sem `INSERT/UPDATE/DELETE` (só `EXECUTE`) para tornar a
regra estrutural, não só convenção (skill `sql-procedures`).

Depois de gravar: `Refresh(fonte)` e **recontagem** dos contadores da tela (decisão C5).

## 9. Consulta rápida

| Preciso de... | Use |
|---|---|
| estado que atravessa telas | `Set(varX, ...)` |
| estado só desta tela | `UpdateContext({ ctxX: ... })` |
| constante ou valor derivado | named formula em `App.Formulas` |
| valor antes do `OnStart` terminar | named formula (obrigatório) |
| contar sobre SQL | `CountRows(Filter())` + teto `fxTxtTeto`, ou contar no servidor |
| contar sobre Dataverse com filtro | `CountIf` (teto 50.000; ver `dataverse/references/delegacao-dataverse.md`) |
| buscar texto | `StartsWith(coluna, termo)` + `DelayOutput` |
| detectar truncagem | *Data row limit* = 1 num clone |
| falha de flow x erro de negócio | `IfError` + `status` do retorno |
| fallback de erro | `Blank()` + `If(IsBlank(x), "-", x)`; nunca número mágico |
| enviar data a flow | `Text(d, "yyyy-mm-dd")` |
| enviar id a flow | `Text(id, "[$-en-US]0")` |
| contar linhas da galeria | `Gallery.AllItemsCount` |
| paralelizar cargas independentes | `Concurrent(...)` |

## 10. Fontes

- [Understand delegation in a canvas app](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview)
- [App object (OnStart, Formulas, StartScreen, OnError)](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)
- [Error, IfError, IsError](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-iferror)
- [Concurrent](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-concurrent)
- [Global support in Power Fx](https://learn.microsoft.com/en-us/power-platform/power-fx/global)
- [Efficient calculations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/efficient-calculations)
- [Operators and identifiers](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/operators)
- [Create performant apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-performant-apps-overview)

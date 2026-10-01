# Expressões (WDL): armadilhas que estouram só em runtime

O designer aceita e salva expressão que falha na primeira execução real. Cada seção é um
defeito que custou uma execução. Exemplos usam `@expr` (campo de conector, `expression` de
`If`/`Switch`, `inputs` de `Compose`); dentro de texto de `Response.body` o mesmo valor vai como
`@{expr}`.

## Sumário

1. [`if()` não curto-circuita](#1-if-não-curto-circuita)
2. [`string(null)` é `''`](#2-stringnull-é-)
3. [`outputs()` x `body()`](#3-outputs-x-body)
4. [`bit` chega como `true`/`false`](#4-bit-chega-como-truefalse)
5. [Limite de 8.192 caracteres](#5-limite-de-8192-caracteres)
6. [`@{}` x `@expr` e aspas](#6-x-expr-e-aspas)
7. [Listas vazias e índice](#7-listas-vazias-e-índice)
8. [JSON montado como texto](#8-json-montado-como-texto)
9. [Outras](#9-outras)

---

## 1. `if()` não curto-circuita

`if(cond, entao, senao)` avalia **os dois ramos** antes de escolher. Isto **não protege nada**:

```text
@if(greater(length(x), 400), substring(x, 0, 400), x)
@if(isNumero, int(t), 0)
```

Com `x` de 12 caracteres o `substring` roda assim mesmo e estoura; com `t` não numérico o `int`
roda assim mesmo e levanta. A ação falha, cai no `Catch` e o usuário lê "o sistema não respondeu"
no lugar da mensagem de validação. [verificado: projeto de referência]

Conserto: torne a chamada **válida sozinha**, protegendo o **argumento**:

```text
@take(coalesce(x, ''), 400)
@int(if(isNumero, t, '0'))
```

Destino: campo de parâmetro de conector / `Compose`. O primeiro devolve até 400 caracteres de
qualquer texto; o segundo mantém o `if()` por **dentro**, com dois ramos de texto puro.

## 2. `string(null)` é `''`

`coalesce` só pula **nulo**. `string(null)` devolve `''`, que não é nulo; o fallback nunca entra e
sobra `int('')`, que estoura.

```text
errado:  @int(coalesce(string(first(body('Registro_antes')?['value'])?['Id_Origem']), '0'))
certo:   @int(coalesce(first(body('Registro_antes')?['value'])?['Id_Origem'], '0'))
```

Destino: parâmetro de conector. `Id_Origem` é coluna numérica, que o conector entrega como número ou nulo
JSON; nulo -> `'0'` -> `int('0')`. Com fallback `''` o `coalesce(string(x), '')` é inofensivo
(o resultado é o mesmo); com fallback **não vazio** é bug (R12). `verificar-fluxo.py` acusa o
segundo (F012); `--estrito` acusa os dois. [verificado: projeto de referência]

## 3. `outputs()` x `body()`

| Ação | `outputs('X')` | `body('X')` |
|---|---|---|
| `Compose` | o próprio valor | o próprio valor |
| `Select` / `Query` (Filtrar matriz) | **envelope** `{"body": [...]}` | a lista |
| Conector | envelope; use `outputs('X')?['body/campo']` (forma de token do designer) | o corpo |

`join(outputs('Conteudo_csv'), ...)` com `Conteudo_csv` sendo `Select` falhou com "join expects
its first parameter to be an array... Object". Pior é a forma **silenciosa**:
`outputs('Trilha')?['campos']` sobre um `Select` dá `null`, `string(null)` dá `''` e a resposta
sai `" campo(s) alterado(s)."` sem número, sem erro e sem portão que acuse. O verificador acusa
`outputs()` de `Select`/`Query` fora da forma `?['body...` (F011). [verificado: projeto de
referência]

## 4. `bit` chega como `true`/`false`

O conector SQL tipa coluna `bit` como booleano; `equals(true, 1)` é **falso**. Leitura segura
(ausente nega):

```text
@or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_X'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_X'],'0'))),'true'))
```

Destino: `expression` de `If` / `Compose`. Três cuidados:

- `$filter` OData sobre `bit` usa `true`/`false`, não `1`/`0`.
- O inverso é igualmente falso: `toLower(string(x))` é **texto**; comparar com o booleano `true`
  (sem aspas) é sempre falso e inverte a regra (o escopo passa a valer para todos).
- `string(coalesce(x,'0'))`: aqui o `coalesce` fica **dentro** do `string()` (o inverso da §2).

## 5. Limite de 8.192 caracteres

Uma expressão não passa de 8.192 caracteres ([Learn: limites](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-limits-and-config)).
`@concat()`, `@base64()` e `@string()` avaliam até 131.072 caracteres. O designer recusa com
"os parâmetros de entrada contêm expressões inválidas", que não fala em tamanho e manda
procurar erro de sintaxe onde não há. Duas construções estouram sem parecer grandes:

- `if(contains(o,'k'), removeProperty(o,'k'), o)` aninhado: cada chave **repete** o interior;
  8 chaves = 2^8 cópias.
- `substring(x, 0, sub(length(x), 1))`: `x` aparece 3 vezes.

Conserto: ponha a subexpressão num `Compose` e refira por `outputs()`. Encadear é linear;
aninhar é exponencial. O verificador acusa acima de 8.192 e avisa acima de 80% (F013), porque
estas expressões **crescem** a cada regra de validação nova.

## 6. `@{}` x `@expr` e aspas

| Onde | Forma |
|---|---|
| Parâmetro de conector, `expression` de `Switch`/`If` | `@expr` **crua** (`@{}` força texto: coluna `INT` recebe string) -- F018 |
| Campo de texto dentro de `Response.body` | `@{expr}` interpolado |
| Mensagem fixa em `if()` | texto **entre aspas simples**: `'Informe a descrição.'` |
| Apóstrofo no texto | duplicado: `'Nao e''possivel'` |

Mensagem pt-BR **sem** aspas dentro de `if()` fez nenhum dos flows salvar (`InvalidTemplate`).
Valor dentro de mensagem usa `concat('texto ', valor, '.')`, nunca `@{}` dentro de literal de
`if()`. [verificado: projeto de referência]

## 7. Listas vazias e índice

- Leitura de uma linha de resultado: `body('X')?['ResultSets']?['Table1']?[0]?['col']` --
  índice com `?[0]` não estoura em lista vazia. `first()` também é seguro.
- `empty(coalesce(body('X')?['ResultSets']?['Table1'], json('[]')))`: o `json('[]')` cobre o
  `null`.
- `empty(lista)` de uma lista `['']` (um item vazio) é **falso**: use
  `empty(trim(join(lista, '')))`.
- Valor deliberadamente `null` (ex.: "todas as unidades") **não** passa por `coalesce`/truncar
  (completo em [autorizacao-no-flow.md](autorizacao-no-flow.md) §3).

## 8. JSON montado como texto

Montar JSON com `concat` abre com aspa, barra, TAB, CR, LF ou caractere de controle no dado.
Prefira `Select`/`Compose` de objeto. Se tiver que usar `concat`, escape `\`, `"`, CR, LF, TAB e
controles **e execute** o resultado num teste (`json()` abre?). [verificado: projeto de
referência]

## 9. Outras

- `Initialize variable` só no nível raiz; dentro de escopo use `Compose`.
- `item()` serve em `Select`/`Query`/`Filter`; `items('<Foreach>')` só **dentro** do `Foreach`
  nomeado (F007).
- `result('Escopo')` aceita `Scope`/`Foreach`/`Until`, não `If`, e devolve só o primeiro nível
  ([Learn](https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling)).
- A função de hash não consta da lista usada nestes flows `[não verificado: confirme na
  referência de funções antes de prometer hash de token em WDL]`.
- `and()`/`or()` também podem avaliar todos os argumentos: não proteja um termo com outro `[não verificado: curto-circuito de and/or]`; torne cada termo válido sozinho.
- Função inexistente (`select`, `filter`, `map`, `sum` não são WDL) só falha ao salvar/executar.

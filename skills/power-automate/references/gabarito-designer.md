# Gabarito do designer: o que ele devolve e o que um gerador deve reproduzir

Um flow gerado por script e colado no designer volta **diferente**. Cada diferença medida entre
o que o script emitiu e o que o designer devolveu é uma regra. Treze foram medidas
(R1-R13); aqui ficam as genéricas e o porquê. O que é de um projeto (nomes de procedure,
connection references reais, valores de `CONFIG`) fica
no gabarito de cada projeto. [verificado: projeto de referência]

## Sumário

1. [Método](#1-método)
2. [As regras](#2-as-regras)
3. [O que o verificador cobre e o que não cobre](#3-o-que-o-verificador-cobre-e-o-que-não-cobre)
4. [Como virar regra nova](#4-como-virar-regra-nova)

---

## 1. Método

1. Cole o flow gerado no designer, salve, copie o escopo de volta.
2. Compare o JSON devolvido com o emitido, regra a regra, **com contagem por flow**.
3. Cada diferença sistemática vira regra; cada regra entra **na fonte do gerador**
   ([gerador-e-gabarito.md](gerador-e-gabarito.md)), não num pós-processador permanente.
4. O arquivo devolvido pelo designer é o **gabarito**: imutável. Quando ele diverge de qualquer
   documento ou gerador, o gabarito vence -- é a única evidência de ambiente que existe.

## 2. As regras

"Bloqueia" = o flow cola mas falha em execução, ou nem salva. "Normaliza" = o designer aceita sem
a regra, mas o arquivo deixa de ser comparável com o que ele devolve e o próximo diff vira ruído.

| Regra | Conteúdo | Efeito | Por quê |
|---|---|---|---|
| **R1** | `allConnectionData` com **uma entrada por ação `OpenApiConnection`**, com o id da connection reference **do ambiente destino** | **bloqueia** | Sem a entrada a colagem não religa a conexão. Verificado por F017 |
| **R2** | Sem `"authentication": "@parameters('$authentication')"` em `inputs` | normaliza | O designer não o devolve |
| **R3** | `runAfter` vazio é **omitido** (exceto no escopo raiz, que mantém `{}`) | normaliza | Idem |
| **R4** | Ação de SQL com `server` e `database` = o literal `"default"` | **bloqueia** | A forma com expressão (`@{outputs('CONFIG')...}`) foi recusada; o servidor real vem da connection reference. `CONFIG` perde essas chaves |
| **R5** | Parâmetro de conector é `@expr` **crua**, nunca `@{expr}` | **bloqueia** | `@{}` força texto: parâmetro de coluna `INT` recebe string. Campo de texto dentro de `Response.body` continua interpolado. Verificado por F018 |
| **R6** | `Response.inputs` na ordem `schema, statusCode, body` e `schema.additionalProperties = {}` | normaliza | Forma devolvida |
| **R7** | Ordem das chaves da ação: `type, [kind], inputs\|expression, [actions/else/cases/default], runAfter, metadata` | normaliza | `runAfter` **antes** de `metadata` |
| **R8** | Todo `If` com `else: {"actions": {}}` explícito | normaliza | Forma devolvida |
| **R9** | Nome do objeto de banco (procedure) é o **AS-BUILT** do ambiente, não o do documento | **bloqueia** | Mecanismo genérico: bloco de dados `procedures_as_built` + de-para verificado contra `sys.procedures`; nunca invente nome. Os valores são do projeto |
| **R10** | `take(x, N)` no lugar de `substring(x, 0, min(length(x), N))` | opcional | Reduz o tamanho e dá folga contra o limite de 8.192; `take()` já é seguro para texto menor que N |
| **R11** | `CONFIG` com valores reais, não `SUBSTITUIR-*` | projeto | Valores são do projeto; a chave não deve ficar sem leitura |
| **R12** | `int(coalesce(string(X),'0'))` estoura em runtime: `string(null)` é `''` | **bloqueia (runtime)** | Ver [expressoes-wdl-armadilhas.md](expressoes-wdl-armadilhas.md). F012 |
| **R13** | `outputs()` de `Select`/`Query` devolve o envelope; use `body()` | **bloqueia (runtime)** | Idem. F011 |

Placar real ao medir vários flows contra o gabarito: R1, R4, R5 e R9 bloqueavam execução; R2, R3,
R6, R7 e R8 eram só normalização.

## 3. O que o verificador cobre e o que não cobre

| Regra | `verificar-fluxo.py` |
|---|---|
| R1 | F017 |
| R5 | F018 |
| R12 | F012 |
| R13 | F011 |
| R2, R3, R6, R7, R8, R10 | **fora de propósito**: não bloqueiam execução; sinalizá-las geraria ruído em todo flow que veio do designer |
| R4 | fora: depende do tipo de conexão (com gateway/conexão padrão); registre no gabarito do projeto |
| R9, R11 | fora: dependem do ambiente; ficam no `NOMES-AS-BUILT` do projeto (skill `dataverse`/`sql-procedures`) |

Portões da família "WDL/Logic Apps" que o verificador também cobre porque nenhuma regra de
negócio é necessária: nome duplicado (F004), `runAfter` órfão (F005), referência a ação
inexistente (F006), `items()` fora do `Foreach` (F007), caso x ação (F008), `Catch` sem `Skipped`
(F009), `Response` sem os 4 campos (F010), `Response` sem `Terminate` (F015), condição constante
(F016), expressão acima de 8.192 caracteres (F013).

## 4. Como virar regra nova

Um defeito que só aparece na colagem ou na primeira execução **volta** se ficar corrigido num
ponto isolado. Os três vazamentos de `string(null)` (em `substring`, em `data_curta` e em
`int()`) foram corrigidos cada um num sítio e reapareceram. Então:

1. Corrija **todo o arquivo**, não só a ocorrência que estourou (varredura por regex).
2. Escreva o portão (função que acusa o padrão) e a fixture que falha (P4 em
   [decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md)).
3. Se o padrão for da família "armadilha de runtime", acrescente em
   [expressoes-wdl-armadilhas.md](expressoes-wdl-armadilhas.md) e ao verificador.

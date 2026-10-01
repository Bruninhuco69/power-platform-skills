# Trigger Power Apps (V2): parâmetros posicionais

> **Arquivo**: `trigger-power-apps-v2.md` (descritivo: sem JSON colável) · **Frequência**: muito comum · **Maturidade**: estável
> **Depende de**: nenhum

## Propósito

Declara os parâmetros que o app envia em `.Run()`. É o passo de **maior risco** da entrega: o trigger não vai no
clipboard, e a ordem dos parâmetros é o contrato com a tela.

## Quando usar / quando não usar

- Use em todo flow chamado por uma tela Power Apps.
- Não use para sistema externo: o trigger é outro (`trigger-http-recebimento`).
- Não use quando o chamador é outro flow: o contrato é outro.

## Onde colar

Não se cola. Crie o flow instantâneo, escolha o gatilho **Power Apps (V2)** e digite os parâmetros no designer, na
ordem da tabela, **antes** de colar `config`. O envelope de escopo dos demais componentes não carrega o trigger.

## Entradas e saídas

- Entrada: um campo de texto por linha. O app passa por **posição**.
- Saída: `triggerBody()['text']`, `['text_1']`, `['text_2']`... na ordem da declaração. Todos texto.
- A resposta ao app é o `Response` de 4 campos (`nega-resposta-terminate`, `traduzir-codigo-e-responder`).

## Tabela de parâmetros (exemplo do flow de gravar)

| # | Nome no designer | `triggerBody()` | Conteúdo | Observação |
|--:|---|---|---|---|
| 1 | `acao` | `['text']` | `gravar`, `excluir` | valor do `Switch`; o app envia em minúsculas |
| 2 | `pedido_id` | `['text_1']` | id do registro | número como texto; vazio no cadastro |
| 3 | `descricao` | `['text_2']` | texto livre | o flow trunca |
| 4 | `unidade` | `['text_3']` | unidade do registro | comparada com a do perfil |
| 5 | `quantidade` | `['text_4']` | número como texto | o flow converte |
| 6 | `prazo` | `['text_5']` | data ISO como texto | vazio = sem prazo |
| 7 | `situacao` | `['text_6']` | `aberto`, `fechado` | usado por `derivar-valor-switch` |

Outros contratos que os componentes pressupõem: **exportação** (`acao`, `filtros` como JSON em texto, em `['text_1']`,
usado por `filtros-json-da-tela`) e **pedido de acesso** (`acao`, `email_alvo` em `['text_1']`, `id_diretorio` em
`['text_2']`, usados por `resolver-id-diretorio` e `email-suporte-com-parcial`).

## Passos no designer (ambiente pt-BR)

1. **Criar** > **Fluxo de nuvem instantâneo** > gatilho **Power Apps (V2)** (nome do nó: `Quando_o_Power_Apps_chama_um_fluxo_(V2)`).
2. Em **Adicionar uma entrada**, escolha **Texto** e digite o nome do parâmetro `acao`.
3. Repita para cada linha da tabela, **na mesma ordem**. Não reordene depois de publicado.
4. Salve o flow vazio uma vez; só então cole `Bloco_config`, `Bloco_chamador` e os demais componentes.
5. Confira no editor que o `Response` colado mostra 4 saídas de texto: `status`, `description`, `id`, `url`.
6. No app, o `.Run()` leva **exatamente** o mesmo número de argumentos, na mesma ordem. Número em texto com `Text(id; "[$-en-US]0")`.

## Parâmetros a trocar

| Item | Valor no exemplo | Trocar por |
|---|---|---|
| nomes dos parâmetros | tabela acima | os do contrato do seu flow (`assets/contrato-flow-molde.md`) |
| quantidade de parâmetros | 7 | a do seu flow; a tela e o flow concordam |

## runAfter

Não se aplica: o trigger é a raiz. O primeiro componente (`config`) tem `runAfter` vazio.

## Armadilhas

- **Parâmetro novo entra sempre no fim.** Inserir no meio faz os valores deslizarem e o flow grava o campo errado, sem erro.
- Número, data e booleano chegam como **texto**: converta no flow (`normalizar-entrada`) com argumento protegido.
- O nome do nó do trigger depende do idioma do ambiente. Em ambiente em inglês seria `When_Power_Apps_calls_a_flow_(V2)` `[não verificado: deduzido, sem amostra]`. Em envelope de escopo isso não importa (os tokens são expressões `triggerBody()`).
- Identificador do usuário nunca vem por parâmetro: use `identificar-chamador`.
- Mudou o contrato: atualize o trigger **e** o `.Run()` no mesmo commit; o número de argumentos do `.Run()` tem de ser igual ao de parâmetros do trigger: faltando ou sobrando, a fórmula do app acusa erro (parâmetro opcional: o app envia `""`).

## Variações

- Parâmetro opcional: o app envia `""` e o flow trata vazio como ausente.
- Muitos parâmetros: um deles pode ser um objeto JSON em texto (`filtros-json-da-tela`), com validação de chaves.

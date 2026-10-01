# Dataverse: `$batch`, upsert e paginação

Gravar lote no Dataverse a partir de um flow. Estrutura herdada de um flow de recebimento de
referência (padrão comunitário "Dataverse Batch Upsert") com as correções que ele não fez
([licoes-de-campo.md](licoes-de-campo.md)). Tabelas, alternate keys e Security
Role são da skill `dataverse`.

## Sumário

1. [Quando usar `$batch`](#1-quando-usar-batch)
2. [Fatos da plataforma](#2-fatos-da-plataforma)
3. [Upsert: chave alternativa ou índice](#3-upsert-chave-alternativa-ou-índice)
4. [Montar o batch](#4-montar-o-batch)
5. [Tratamento por parte](#5-tratamento-por-parte)
6. [429 e erros 5xx](#6-429-e-erros-5xx)
7. [Paginação da leitura](#7-paginação-da-leitura)
8. [Atomicidade](#8-atomicidade)

---

## 1. Quando usar `$batch`

- **N = 1 ou poucos**: ação `Add/Update row` do conector, por linha. `$batch` complica sem ganho.
- **Lote**: `$batch` reduz chamadas, mas custa tempo de execução na API (ver §2): comece com
  partes pequenas e aumente.
- Escrita com regra de negócio chamada pela **tela** não vem aqui: é o desenho de
  [anatomia-flow.md](anatomia-flow.md). Este arquivo é para **recebimento de lote** (integração).

## 2. Fatos da plataforma

Fonte: [Learn: batch](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/execute-batch-operations-using-web-api)
e [Learn: limites de proteção](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/api-limits).

| Fato | Valor |
|---|---|
| Requisições por `$batch` | até 1.000; não aninha outro batch |
| Ordem | executadas em sequência, na ordem enviada |
| Changeset | **atômico**: se uma falha, as concluídas são revertidas; `GET` não entra em changeset |
| Erro numa parte, sem preferência | o batch **para** na primeira falha e devolve o erro dela |
| `Prefer: odata.continue-on-error` | processa as demais; resposta 200 com os erros **dentro** do corpo |
| Quebra de linha no corpo | **CRLF** obrigatório; outras quebras podem dar erro de desserialização |
| Boundary | só partes cujo identificador casa com o do cabeçalho executam |
| `Content-ID` | referencia entidade criada antes no mesmo changeset (`$1`); referência a id ainda não visto = 400 |
| Proteção de serviço (por usuário, por servidor) | 6.000 requisições/5 min; 20 min de tempo de execução/5 min; 52 concorrentes (valores padrão, variam) |
| Excesso | **429** com `Retry-After` em segundos |
| Conselho | Comece com lotes pequenos (por exemplo 10) e aumente a concorrência até aparecer 429 `[não verificado: citação oficial]` |

## 3. Upsert: chave alternativa ou índice

Duas formas de decidir entre criar e atualizar:

| Forma | Quando | Nota |
|---|---|---|
| **Alternate key** na URL do `PATCH` (`<conjunto>(<chave>='x')`) | A tabela tem alternate key ativa para a chave de negócio | Um `PATCH` por linha, sem ler a tabela. Sintaxe e composição de chaves: `[não verificado: confirme a página "Use alternate keys" do Learn]` |
| **Índice {chave -> id}** montado a partir de uma leitura da tabela destino | Sem alternate key | É o desenho do flow de referência (abaixo): lê as chaves, separa quem **tem** id (update) de quem **não tem** (create) |

Condicionais de `PATCH` com id ([Learn: operações condicionais](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/perform-conditional-operations-using-web-api)):
`If-Match: *` impede **criar** (404 se não existe: só atualiza); `If-None-Match: *` impede
**atualizar** (412 se já existe: só cria).

Indexe pela **chave composta concatenada** (`numero & unidade & data`), com o mesmo
formato dos dois lados. Cuidado com a data: o índice e a linha precisam concatenar o **mesmo**
texto (sufixo `Z` incluído), senão nenhuma linha acha o id e tudo vira `create` duplicado.
[verificado: projeto de referência]

## 4. Montar o batch

Parâmetros em um `Compose` (`settings`), com o nome da tabela por **variável de ambiente**, não
literal de DEV (decisão F5):

```json
{
  "settings": {
    "type": "Compose",
    "description": "EntitySetName é o nome do conjunto (plural), não o nome lógico. BatchSize máximo 1000; comece pequeno.",
    "inputs": {
      "EntitySetName": "<prefixo>_tabelasdestino",
      "BatchSize": 50,
      "KeyColumns": ["<prefixo>_numero", "<prefixo>_unidade", "<prefixo>_data"]
    },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000010" }
  }
}
```

Destino: ação do escopo principal; `settings` é o `CONFIG` deste flow. O verificador **avisa**
(F014) literal de ambiente fora de uma ação chamada `CONFIG`: nomeie assim ou trate o aviso.

Fluxo: `Mapear_lote` (Select de mapeamento) -> índice -> separar -> `chunk()` ->
`Select` aplicando o molde -> `SendBatch`.

```text
Partes   = @chunk(body('Select_ComId'), outputs('settings')?['BatchSize'])
Corpo    = @concat('--batch_', variables('lote'), decodeUriComponent('%0D%0A'), 'Content-Type: multipart/mixed; boundary=changeset_', variables('cs'), decodeUriComponent('%0D%0A%0D%0A'), join(body('Select_Partes'), decodeUriComponent('%0D%0A')), decodeUriComponent('%0D%0A'), '--changeset_', variables('cs'), '--', decodeUriComponent('%0D%0A'), '--batch_', variables('lote'), '--', decodeUriComponent('%0D%0A'))
```

Destino: `chunk()` no campo `foreach` de um `Foreach`; `Corpo` em `request/body` da ação HTTP
(`InvokeHttp`). Cabeçalhos do POST: `OData-MaxVersion: 4.0`, `OData-Version: 4.0`,
`Accept: application/json`, `Content-Type: multipart/mixed; boundary=batch_<id>`, e **cada parte
leva o próprio `Content-Type: application/http` e `Content-Transfer-Encoding: binary`**
(cabeçalhos do `$batch` não valem para cada parte).

Atenção: o flow de referência monta o corpo com `\n` (LF) e o Learn exige **CRLF**; não
verifiquei a execução dele. Use `decodeUriComponent('%0D%0A')` como acima e teste com um lote
de 2 linhas antes de subir volume. `[não verificado: execução com LF ou CRLF no flow]`.

## 5. Tratamento por parte

O flow de referência detectava erro por **substring** (`contains(texto, '400 Bad Request')`...) e
deixava de fora 500, 503, 504 e 429. Leia o **status de cada parte**:

Em ações, `Statuses` é um `Select` com `from` = `@skip(split(base64ToString(body('SendBatch')['$content']), 'HTTP/1.1 '), 1)` e
`select` = `@int(substring(item(), 0, 3))`; depois `Query` (Filtrar matriz) com `from` =
`@body('Statuses')` e `where` = `@greaterOrEquals(item(), 400)`. Falha do lote =
`@greater(length(body('Falhas')), 0)`. O corpo de resposta vem em `$content` em base64
(uso verificado no flow de referência). `[não verificado: a divisão por 'HTTP/1.1 ' em resposta
real]`; valide num lote com uma linha inválida de propósito.

- Com `odata.continue-on-error` as partes boas gravam e as ruins aparecem em `Falhas`.
- Sem ele, a primeira falha para o batch: devolva `warning`/falha parcial e **conte** as linhas
  que não foram processadas.
- Conte **linhas**, não partes: o flow de referência incrementava por tamanho de chunk
  (pessimista).

## 6. 429 e erros 5xx

- Excesso de requisições: **429** com `Retry-After`
  ([Learn](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/api-limits)).
- Ação HTTP tem política de retentativa padrão: exponencial, até 4 tentativas, para 408, 429 e
  5xx ([Learn](https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling)).
  Para o conector `InvokeHttp` do Power Automate, como a política aparece no JSON do designer está `[não verificado]`.
- Mesmo com retentativa, **limite a concorrência** do `Foreach` de envio (o flow de referência
  usou 10) e aumente aos poucos.

## 7. Paginação da leitura

Ler a tabela destino para montar o índice é a parte cara. Duas opções:

| Opção | Nota |
|---|---|
| **Paginação nativa** da ação `List rows` (Configurações -> Paginação, limite) | Uma ação só, sem `Do_until` nem variável de skiptoken. O flow de referência usou limite 100.000 (`paginationPolicy.minimumItemCount`) [verificado: projeto de referência] |
| `Do_until` + `@odata.nextLink`/skiptoken manual | Mais ações, mais pontos de falha; só se a paginação nativa não servir |

**Reduza a leitura**: filtre pelo intervalo do lote (`min`/`max` das chaves, calculados com
`first(sort(...))`/`last(sort(...))` num único `Compose`), em vez de ler a tabela inteira.

## 8. Atomicidade

Um changeset de 800 linhas **reverte as 800** se uma falhar. Escolha conscientemente:

| Desenho | Quando |
|---|---|
| Changeset por parte (tudo-ou-nada por parte) | A parte é uma unidade de negócio (ex.: um documento com suas linhas) |
| Sem changeset + `continue-on-error` | Linhas independentes; erro numa linha não pode derrubar as outras |

Para escrita tela-a-tabela com regra de negócio e compensação, ver
[anatomia-flow.md](anatomia-flow.md): o Dataverse não dá transação a um flow comum (cada
`Add a new row` é um commit); compense na **ordem inversa** no `Catch`, ou use changeset.

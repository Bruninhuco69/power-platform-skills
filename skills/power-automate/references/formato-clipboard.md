# Formato do clipboard do designer

O que o designer novo do Power Automate põe na área de transferência no `Ctrl+C` de uma ação, e
aceita de volta no `Ctrl+V` -- inclusive vindo de outro flow, de outra aba ou de um arquivo. É o
equivalente do `.pa.yaml` colável das telas: **o flow vira arquivo**.

> Autoridade: amostras reais copiadas do designer (um `Compor` e uma `Condição`) e um flow
> inteiro colado e devolvido pelo designer. Tudo que elas mostram está marcado como confirmado;
> o resto é `[não verificado]`. [verificado: projeto de referência]

## Sumário

1. [Como copiar e colar](#1-como-copiar-e-colar)
2. [Dois envelopes, não um](#2-dois-envelopes-não-um)
3. [Envelope de escopo](#3-envelope-de-escopo)
4. [Envelope de nó folha](#4-envelope-de-nó-folha)
5. [Entradas: segmentos e rawInputs](#5-entradas-segmentos-e-rawinputs)
6. [Idioma e o nodeId do trigger](#6-idioma-e-o-nodeid-do-trigger)
7. [Regras de geração](#7-regras-de-geração)
8. [O que não está confirmado](#8-o-que-não-está-confirmado)

---

## 1. Como copiar e colar

- **Copiar:** no designer novo, selecione a ação (ou escopo) e `Ctrl+C`. O conteúdo da área de
  transferência é o JSON abaixo (uma linha).
- **Colar:** clique no ponto de inserção do flow de destino e `Ctrl+V`. Cole **de cima para
  baixo**: `nodeTokenData.upstreamNodeIds` cita nós que precisam existir.
- **Arquivo:** salve o JSON em `.json` -- ou em `.md` que contenha **só** o JSON (o formato de
  entrega de um dos projetos de referência) -- e cole o conteúdo inteiro.
- **Conferir antes de colar:** `python <pasta-da-skill>/scripts/verificar-fluxo.py <arquivo>`. O designer não
  valida nada antes de colar: nome repetido, token órfão ou coluna inventada cola "com sucesso"
  e só quebra na execução.

## 2. Dois envelopes, não um

| | Nó de escopo | Nó folha |
|---|---|---|
| Chaves de topo | **6**: `nodeId`, `serializedValue`, `allConnectionData`, `staticResults`, `isScopeNode: true`, `mslaNode: true` | **7**: `nodeId`, `nodeData`, `nodeTokenData`, `nodeOperationInfo`, `nodeConnectionData`, `isScopeNode: false`, `mslaNode: true` |
| Carrega | a **definição Logic Apps crua** em `serializedValue`, com a subárvore inteira | o modelo de parâmetros do designer em `nodeData` |
| Filhos | vêm dentro, na íntegra | não tem |
| Conexão | `allConnectionData` | `nodeConnectionData` |

Consequências:

1. **Um flow inteiro cabe num `Scope` e portanto numa colagem** (dezenas de nós de uma vez). Escopo é
   transparente em execução; custa um nível de indentação no designer.
2. `runAfter` viaja na forma normal da definição, dentro do `serializedValue` -- inclusive o do
   `Catch` com `["Failed","TimedOut","Skipped"]`. Não há passo manual de "configurar execução
   após".
3. Escopo **não** tem modelo de segmentos nem GUID por segmento: é a definição literal. O resto
   deste arquivo sobre segmentos vale só para nó folha.
4. `mslaNode` é o marcador do designer novo; sem ele o nó não é reconhecido.

Qualquer ação com filhos (`Scope`, `If`, `Switch`, `Foreach`) é colável como envelope de escopo.

## 3. Envelope de escopo

Mínimo válido (um `Compose` dentro de um escopo), colável e aprovado pelo verificador:

```json
{
  "nodeId": "Escopo_exemplo",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Compor_exemplo": {
        "type": "Compose",
        "inputs": "@toLower(trim(coalesce(triggerBody()['text'], '')))",
        "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000006" }
      }
    },
    "runAfter": {},
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000007" }
  },
  "allConnectionData": {},
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

Destino: `Ctrl+V` no ponto de inserção de um flow que já tenha o trigger Power Apps (V2).

- `allConnectionData` tem **uma entrada por ação `OpenApiConnection`** do escopo, indexada pelo
  nome da ação, com a connection reference do ambiente destino (R1 em
  [gabarito-designer.md](gabarito-designer.md)); vazio, a ação cola sem conexão e a execução é
  bloqueada (F017). Formato da entrada:

```json
{
  "Ler_chamador": {
    "connectionReference": {
      "api": { "id": "/providers/Microsoft.PowerApps/apis/shared_sql" },
      "connection": { "id": "<prefixo>_sharedsql" },
      "connectionName": "<prefixo>_sharedsql"
    },
    "referenceKey": "shared_sql"
  }
}
```

  Destino: valor de `allConnectionData` do envelope. `<prefixo>_sharedsql` é o nome lógico da
  connection reference no **ambiente de destino** (a skill `power-platform` cria e versiona);
  nunca copie o nome de outro ambiente.
- Primeiro nó do escopo sem `runAfter`; o escopo raiz mantém `"runAfter": {}`. Em colagem de
  fragmento, o `runAfter` da raiz aponta para um nó que **já existe** no ponto de inserção (o
  verificador não cobra esse nome; as referências a ações fora do trecho viram aviso F006).

## 4. Envelope de nó folha

`Compose` com um token do trigger (os GUIDs são fictícios: gere um novo por campo, por segmento
e por `operationMetadataId`):

```json
{
  "nodeId": "Compor_exemplo",
  "nodeData": {
    "id": "Compor_exemplo",
    "nodeInputs": {
      "dynamicLoadStatus": "Succeeded",
      "parameterGroups": {
        "default": {
          "id": "default",
          "description": "",
          "parameters": [
            {
              "id": "00000000-0000-0000-0000-0000000000a1",
              "info": { "isDynamic": false },
              "hideInUI": false,
              "label": "Entradas",
              "parameterKey": "inputs.$",
              "parameterName": "Entradas",
              "placeholder": "Entradas",
              "required": true,
              "schema": { "title": "Entradas", "description": "Entradas", "properties": {} },
              "showErrors": false,
              "showTokens": true,
              "suppressCasting": true,
              "type": "any",
              "value": [
                {
                  "id": "00000000-0000-0000-0000-0000000000a2",
                  "type": "token",
                  "token": {
                    "source": "outputs",
                    "name": "body.text",
                    "key": "outputs.$.body.text",
                    "required": true,
                    "tokenType": "outputs",
                    "title": "acao",
                    "value": "triggerBody()['text']",
                    "type": "string",
                    "schema": {
                      "title": "acao",
                      "type": "string",
                      "x-ms-dynamically-added": true,
                      "description": "Insira sua entrada",
                      "x-ms-content-hint": "TEXT"
                    },
                    "description": "Insira sua entrada",
                    "icon": "https://content.powerapps.com/resource/makerx/static/pauto/images/designeroperations/PowerApps2.05e0cdd0.png",
                    "brandColor": "#742774",
                    "isSecure": false
                  },
                  "value": "triggerBody()['text']"
                }
              ],
              "visibility": "",
              "validationErrors": []
            }
          ],
          "rawInputs": [
            {
              "description": "Entradas",
              "key": "inputs.$",
              "name": "Entradas",
              "required": true,
              "schema": { "title": "Entradas", "description": "Entradas", "properties": {} },
              "summary": "",
              "suppressCasting": true,
              "title": "Entradas",
              "type": "any",
              "visibility": "",
              "hideInUI": false,
              "value": "@triggerBody()['text']"
            }
          ]
        }
      }
    },
    "nodeOutputs": {
      "outputs": {
        "outputs.$": {
          "key": "outputs.$",
          "type": "any",
          "isAdvanced": false,
          "name": "key-outputs-output",
          "title": "Saídas",
          "schema": {},
          "source": "outputs",
          "required": true
        }
      }
    },
    "nodeDependencies": { "inputs": {}, "outputs": {} },
    "operationMetadata": {
      "iconUri": "https://content.powerapps.com/resource/makerx/static/pauto/images/designeroperations/dataoperationedit.2c8a4d5e.png",
      "brandColor": "#8C6CFF",
      "isConnectToSystemsOperation": false
    },
    "settings": {
      "asynchronous": { "isSupported": false, "value": false },
      "correlation": { "isSupported": false },
      "secureInputs": { "isSupported": true },
      "secureOutputs": { "isSupported": false },
      "disableAsyncPattern": { "isSupported": false, "value": false },
      "disableAutomaticDecompression": { "isSupported": false },
      "splitOn": { "isSupported": false, "value": { "enabled": false } },
      "retryPolicy": { "isSupported": false },
      "requestOptions": { "isSupported": false },
      "sequential": false,
      "suppressWorkflowHeaders": { "isSupported": false },
      "suppressWorkflowHeadersOnResponse": { "isSupported": false, "value": false },
      "concurrency": { "isSupported": false },
      "singleInstance": false,
      "timeout": { "isSupported": false },
      "paging": { "isSupported": false, "value": { "enabled": false } },
      "uploadChunk": { "isSupported": false, "value": {} },
      "downloadChunkSize": { "isSupported": false },
      "trackedProperties": { "isSupported": true },
      "requestSchemaValidation": { "isSupported": false, "value": false },
      "conditionExpressions": { "isSupported": false },
      "runAfter": { "isSupported": false, "value": [] },
      "invokerConnection": { "isSupported": false, "value": { "enabled": false } },
      "statelessFlow": { "isSupported": false, "value": { "enabled": false } }
    },
    "actionMetadata": { "operationMetadataId": "00000000-0000-0000-0000-0000000000a3" },
    "repetitionInfo": { "repetitionReferences": [] }
  },
  "nodeTokenData": {
    "tokens": [
      {
        "key": "outputs.$",
        "brandColor": "#8C6CFF",
        "icon": "https://content.powerapps.com/resource/makerx/static/pauto/images/designeroperations/dataoperationedit.2c8a4d5e.png",
        "title": "Saídas",
        "name": "key-outputs-output",
        "type": "any",
        "isAdvanced": false,
        "outputInfo": {
          "type": "outputs",
          "required": true,
          "source": "outputs",
          "isSecure": false,
          "actionName": "Compor_exemplo",
          "schema": {}
        }
      }
    ],
    "upstreamNodeIds": ["Quando_o_Power_Apps_chama_um_fluxo_(V2)"]
  },
  "nodeOperationInfo": { "connectorId": "DataOperation", "operationId": "Compose", "type": "Compose" },
  "nodeConnectionData": null,
  "isScopeNode": false,
  "mslaNode": true
}
```

Destino: `Ctrl+V` num flow cujo trigger se chame `Quando_o_Power_Apps_chama_um_fluxo_(V2)`
(ambiente pt-BR; ver §6). Nó folha só serve para uma ação isolada; **prefira o envelope de
escopo**, que dispensa o modelo de segmentos.

| `nodeData` | Conteúdo |
|---|---|
| `id` | Repete o `nodeId`; divergir renomeia o nó na colagem |
| `nodeInputs` | Entradas em duas visões paralelas (§5) |
| `nodeOutputs` | O que a ação publica, indexado por `key` |
| `settings` | 24 chaves `{isSupported, value?}`. É onde mora o `runAfter` configurado no designer |
| `actionMetadata` | `operationMetadataId`: GUID novo por nó |

## 5. Entradas: segmentos e rawInputs

`parameterGroups.default` tem duas listas paralelas do mesmo campo:

- `parameters[]`: visão do **editor**. `value` é uma **lista de segmentos**, nunca string:
  `literal` (`{"type":"literal","value":"texto","valueType":"string"}`) ou `token` (cita uma
  saída anterior pelo nome da ação).
- `rawInputs[]`: visão da **definição**. `value` é a string de expressão com `@`.

Regra de reconstrução (`parameters[].value` -> `rawInputs[].value`):

| Segmentos | `rawInputs[].value` |
|---|---|
| 1 token só | `@<expressão>` |
| 1 literal só | `<texto>` |
| mistura | `@{<expr>}<texto>@{<expr>}...` -- cada token entre `@{ }`, literal cru |

Numa amostra copiada do designer as duas visões vieram **dessincronizadas** (o editor mudou os
segmentos e não reescreveu `rawInputs`), o que indica que o designer regenera `rawInputs` na
colagem. Não aposte: gere os dois coerentes. O verificador avisa a divergência (F019, aviso) e
acusa GUID repetido entre campos/segmentos, `token.value` diferente de `value` e
`validationErrors` não vazio (F019, erro).

## 6. Idioma e o nodeId do trigger

O `nodeId` do trigger é o **rótulo do idioma do ambiente**: num ambiente pt-BR é
`Quando_o_Power_Apps_chama_um_fluxo_(V2)`; num ambiente em inglês seria
`When_Power_Apps_calls_a_flow_(V2)` `[não verificado: nome em inglês deduzido, sem amostra]`, e
todo token que o cita gera diferente. Declare o idioma do ambiente no contrato do flow e
refaça a amostra se o idioma mudar. Em envelope de escopo isso não importa (os tokens são
expressões `triggerBody()`).

## 7. Regras de geração

| # | Regra | Por quê |
|--:|---|---|
| 1 | `nodeId` == `nodeData.id` == `tokens[].outputInfo.actionName` (F003) | Divergir renomeia ou desliga o token |
| 2 | `nodeId` único no flow, sem espaço (F003, F004) | Repetido vira `_1` em silêncio; tokens seguem apontando para o original |
| 3 | GUID novo em campo, segmento e `operationMetadataId` (F019) | Colisão corrompe o editor |
| 4 | `validationErrors: []` (F019) | Nó copiado com erro propaga o erro |
| 5 | `rawInputs` reconstruído dos segmentos (F019) | Não se aposta na regeneração |
| 6 | Nome de coluna no **lógico** do ambiente (em Power Fx é o nome de exibição; em flow e OData é o lógico) | Filtro OData com nome errado não dá erro: devolve lista vazia, indistinguível de "nenhuma duplicata" |
| 7 | Zero GUID/servidor literal de ambiente fora do `CONFIG` (F014) | Literal aponta para DEV depois de promovido |
| 8 | Colar de cima para baixo | `upstreamNodeIds` precisa existir |

## 8. O que não está confirmado

| Item | Estado |
|---|---|
| Envelope de escopo (6 chaves) e de folha (7 chaves) | confirmado |
| Escopo leva os filhos e o `runAfter` cru | confirmado |
| `allConnectionData` por ação `OpenApiConnection` | confirmado (flow inteiro colado e devolvido pelo designer) |
| `nodeConnectionData` de **folha** de ação de conector (a amostra só tem `null`) | `[não verificado]`: prefira escopo |
| `nodeOperationInfo` (`connectorId`/`operationId`/`type`) de ações que não sejam `Compose` | `[não verificado]` em envelope de folha; use escopo |
| Trigger colável | não é: digite à mão |

# Upsert em lote por $batch com changeset

> **Arquivo**: `batch-upsert-changeset.json` · **Frequência**: ocasional · **Maturidade**: estável na estrutura; CRLF, status por parte e concorrência 5 [não verificado]
> **Depende de**: `indice-chaves-destino`; `config-recebimento`; variáveis `Erros_lote` e `Linhas_com_erro` na raiz; conector HTTP com Entra ID

## Propósito

`Batch_update` (PATCH) e `Batch_create` (POST): `Query` separa o lote por `GuidKey`, um modelo de parte por ação, `Foreach` sobre `chunk()` com concorrência limitada, `Select` aplica o modelo, `SendBatch` envia o `$batch`, o status de **cada parte** é lido do corpo e as linhas com erro são contadas.

## Quando usar / quando não usar

**Usar**

- Recebimento de lote.

**Não usar**

- N = 1 ou poucas linhas: `upsert-unitario` (`$batch` complica sem ganho).
- Escrita da tela com regra de negócio: `anatomia-flow`.

## Onde colar

Dentro de `Condicao_unitario`, ramo `Não`, depois de `Bloco_indice`. Antes, **à mão, na raiz do flow**: dois `Initialize variable`.

## Entradas e saídas

**Lê**

- `body('Lote_com_guid')`, `CONFIG` (`EntitySetName`, `TamanhoLote`).

**Expõe**

- Variáveis `Erros_lote` (texto) e `Linhas_com_erro` (número) lidas pelo `log-execucao`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Escopo_batch`; o mesmo conteúdo está em `batch-upsert-changeset.json`). GUIDs fictícios; conexões: `<prefixo>_sharedwebcontents`.


```json
{
  "nodeId": "Escopo_batch",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Ids_lote": {
        "type": "Compose",
        "description": "Uma vez por execução: os dois identificadores de fronteira do multipart.",
        "inputs": {
          "batch": "@guid()",
          "changeset": "@guid()"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000169"
        }
      },
      "Batch_update": {
        "type": "Scope",
        "actions": {
          "Filtrar_update": {
            "type": "Query",
            "inputs": {
              "from": "@body('Lote_com_guid')",
              "where": "@not(equals(item()['GuidKey'],null))"
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000170"
            }
          },
          "Modelo_update": {
            "type": "Compose",
            "inputs": "@concat('--changeset_',outputs('Ids_lote')?['changeset'],decodeUriComponent('%0D%0A'),'Content-Type: application/http',decodeUriComponent('%0D%0A'),'Content-Transfer-Encoding: binary',decodeUriComponent('%0D%0A'),'Content-ID: |ID|',decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),'PATCH /api/data/v9.2/',outputs('CONFIG')?['EntitySetName'],'(|GuidKey|) HTTP/1.1',decodeUriComponent('%0D%0A'),'OData-MaxVersion: 4.0',decodeUriComponent('%0D%0A'),'OData-Version: 4.0',decodeUriComponent('%0D%0A'),'Content-Type: application/json',decodeUriComponent('%0D%0A'),'If-Match: *',decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),'|RowData|',decodeUriComponent('%0D%0A'))",
            "runAfter": {
              "Filtrar_update": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000171"
            }
          },
          "Lotes_update": {
            "type": "Foreach",
            "foreach": "@chunk(body('Filtrar_update'),outputs('CONFIG')?['TamanhoLote'])",
            "actions": {
              "Partes_update": {
                "type": "Select",
                "inputs": {
                  "from": "@range(0,length(items('Lotes_update')))",
                  "select": "@replace(replace(replace(outputs('Modelo_update'),'|RowData|',string(removeProperty(items('Lotes_update')[item()],'GuidKey'))),'|GuidKey|',string(items('Lotes_update')[item()]['GuidKey'])),'|ID|',string(add(item(),1)))"
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000172"
                }
              },
              "Enviar_lote_update": {
                "type": "OpenApiConnection",
                "inputs": {
                  "parameters": {
                    "request/method": "POST",
                    "request/url": "/api/data/v9.2/$batch",
                    "request/headers": {
                      "OData-MaxVersion": "4.0",
                      "OData-Version": "4.0",
                      "Accept": "application/json",
                      "Content-Type": "@concat('multipart/mixed; boundary=batch_',outputs('Ids_lote')?['batch'])"
                    },
                    "request/body": "@concat('--batch_',outputs('Ids_lote')?['batch'],decodeUriComponent('%0D%0A'),'Content-Type: multipart/mixed; boundary=changeset_',outputs('Ids_lote')?['changeset'],decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),join(body('Partes_update'),decodeUriComponent('%0D%0A')),'--changeset_',outputs('Ids_lote')?['changeset'],'--',decodeUriComponent('%0D%0A'),'--batch_',outputs('Ids_lote')?['batch'],'--',decodeUriComponent('%0D%0A'))"
                  },
                  "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_webcontents",
                    "connection": "shared_webcontents",
                    "operationId": "InvokeHttp"
                  }
                },
                "runAfter": {
                  "Partes_update": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000173"
                }
              },
              "Status_partes_update": {
                "type": "Select",
                "inputs": {
                  "from": "@skip(split(base64ToString(body('Enviar_lote_update')['$content']),'HTTP/1.1 '),1)",
                  "select": "@int(substring(item(),0,3))"
                },
                "runAfter": {
                  "Enviar_lote_update": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000174"
                }
              },
              "Falhas_update": {
                "type": "Query",
                "inputs": {
                  "from": "@body('Status_partes_update')",
                  "where": "@greaterOrEquals(item(),400)"
                },
                "runAfter": {
                  "Status_partes_update": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000175"
                }
              },
              "Contar_falhas_update": {
                "type": "IncrementVariable",
                "inputs": {
                  "name": "Linhas_com_erro",
                  "value": "@if(greater(length(body('Falhas_update')),0),length(items('Lotes_update')),0)"
                },
                "runAfter": {
                  "Falhas_update": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000176"
                }
              },
              "Anexar_erro_update": {
                "type": "AppendToStringVariable",
                "inputs": {
                  "name": "Erros_lote",
                  "value": "@if(greater(length(body('Falhas_update')),0),take(base64ToString(body('Enviar_lote_update')['$content']),2000),'')"
                },
                "runAfter": {
                  "Contar_falhas_update": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000177"
                }
              }
            },
            "runtimeConfiguration": {
              "concurrency": {
                "repetitions": 5
              }
            },
            "runAfter": {
              "Modelo_update": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000178"
            }
          }
        },
        "runAfter": {
          "Ids_lote": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000179"
        }
      },
      "Batch_create": {
        "type": "Scope",
        "actions": {
          "Filtrar_create": {
            "type": "Query",
            "inputs": {
              "from": "@body('Lote_com_guid')",
              "where": "@equals(item()['GuidKey'],null)"
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000180"
            }
          },
          "Modelo_create": {
            "type": "Compose",
            "inputs": "@concat('--changeset_',outputs('Ids_lote')?['changeset'],decodeUriComponent('%0D%0A'),'Content-Type: application/http',decodeUriComponent('%0D%0A'),'Content-Transfer-Encoding: binary',decodeUriComponent('%0D%0A'),'Content-ID: |ID|',decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),'POST /api/data/v9.2/',outputs('CONFIG')?['EntitySetName'],' HTTP/1.1',decodeUriComponent('%0D%0A'),'OData-MaxVersion: 4.0',decodeUriComponent('%0D%0A'),'OData-Version: 4.0',decodeUriComponent('%0D%0A'),'Content-Type: application/json;type=entry',decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),'|RowData|',decodeUriComponent('%0D%0A'))",
            "runAfter": {
              "Filtrar_create": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000181"
            }
          },
          "Lotes_create": {
            "type": "Foreach",
            "foreach": "@chunk(body('Filtrar_create'),outputs('CONFIG')?['TamanhoLote'])",
            "actions": {
              "Partes_create": {
                "type": "Select",
                "inputs": {
                  "from": "@range(0,length(items('Lotes_create')))",
                  "select": "@replace(replace(outputs('Modelo_create'),'|RowData|',string(removeProperty(items('Lotes_create')[item()],'GuidKey'))),'|ID|',string(add(item(),1)))"
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000182"
                }
              },
              "Enviar_lote_create": {
                "type": "OpenApiConnection",
                "inputs": {
                  "parameters": {
                    "request/method": "POST",
                    "request/url": "/api/data/v9.2/$batch",
                    "request/headers": {
                      "OData-MaxVersion": "4.0",
                      "OData-Version": "4.0",
                      "Accept": "application/json",
                      "Content-Type": "@concat('multipart/mixed; boundary=batch_',outputs('Ids_lote')?['batch'])"
                    },
                    "request/body": "@concat('--batch_',outputs('Ids_lote')?['batch'],decodeUriComponent('%0D%0A'),'Content-Type: multipart/mixed; boundary=changeset_',outputs('Ids_lote')?['changeset'],decodeUriComponent('%0D%0A'),decodeUriComponent('%0D%0A'),join(body('Partes_create'),decodeUriComponent('%0D%0A')),'--changeset_',outputs('Ids_lote')?['changeset'],'--',decodeUriComponent('%0D%0A'),'--batch_',outputs('Ids_lote')?['batch'],'--',decodeUriComponent('%0D%0A'))"
                  },
                  "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_webcontents",
                    "connection": "shared_webcontents",
                    "operationId": "InvokeHttp"
                  }
                },
                "runAfter": {
                  "Partes_create": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000183"
                }
              },
              "Status_partes_create": {
                "type": "Select",
                "inputs": {
                  "from": "@skip(split(base64ToString(body('Enviar_lote_create')['$content']),'HTTP/1.1 '),1)",
                  "select": "@int(substring(item(),0,3))"
                },
                "runAfter": {
                  "Enviar_lote_create": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000184"
                }
              },
              "Falhas_create": {
                "type": "Query",
                "inputs": {
                  "from": "@body('Status_partes_create')",
                  "where": "@greaterOrEquals(item(),400)"
                },
                "runAfter": {
                  "Status_partes_create": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000185"
                }
              },
              "Contar_falhas_create": {
                "type": "IncrementVariable",
                "inputs": {
                  "name": "Linhas_com_erro",
                  "value": "@if(greater(length(body('Falhas_create')),0),length(items('Lotes_create')),0)"
                },
                "runAfter": {
                  "Falhas_create": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000186"
                }
              },
              "Anexar_erro_create": {
                "type": "AppendToStringVariable",
                "inputs": {
                  "name": "Erros_lote",
                  "value": "@if(greater(length(body('Falhas_create')),0),take(base64ToString(body('Enviar_lote_create')['$content']),2000),'')"
                },
                "runAfter": {
                  "Contar_falhas_create": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000187"
                }
              }
            },
            "runtimeConfiguration": {
              "concurrency": {
                "repetitions": 5
              }
            },
            "runAfter": {
              "Modelo_create": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000188"
            }
          }
        },
        "runAfter": {
          "Batch_update": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000189"
        }
      }
    },
    "runAfter": {
      "Bloco_indice": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000190"
    }
  },
  "allConnectionData": {
    "Enviar_lote_update": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_webcontents"
        },
        "connection": {
          "id": "<prefixo>_sharedwebcontents"
        },
        "connectionName": "<prefixo>_sharedwebcontents"
      },
      "referenceKey": "shared_webcontents"
    },
    "Enviar_lote_create": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_webcontents"
        },
        "connection": {
          "id": "<prefixo>_sharedwebcontents"
        },
        "connectionName": "<prefixo>_sharedwebcontents"
      },
      "referenceKey": "shared_webcontents"
    }
  },
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

## Parâmetros a trocar

| Item | Valor no JSON | Trocar por |
|---|---|---|
| `Inicializar_erros_lote` | `Initialize variable` `Erros_lote`, tipo texto, valor vazio | crie na raiz; nome da variável é referenciado nas ações |
| `Inicializar_linhas_com_erro` | `Initialize variable` `Linhas_com_erro`, tipo inteiro, 0 | crie na raiz |
| `repetitions` | `5` | concorrência do `Foreach`; comece baixa e aumente até aparecer 429 |
| `/api/data/v9.2` | versão | a do ambiente |
| `TamanhoLote` | `CONFIG` | até 1000 requisições por `$batch` |

## runAfter

Raiz depende de `Bloco_indice`; `Batch_create` depende de `Batch_update`; dentro do `Foreach`, as ações encadeiam em ordem.

## Armadilhas

- Corpo do `$batch` com **CRLF**: o projeto de referência usava `\n` (LF) e o Learn exige CRLF `[não verificado: execução com LF ou CRLF]`. Teste com um lote de 2 linhas antes de subir volume.
- Cada parte leva `Content-Type: application/http` e `Content-Transfer-Encoding: binary`; o cabeçalho do `$batch` não vale para cada parte.
- Changeset é atômico: uma falha reverte as linhas da parte inteira. Linhas independentes pedem `Prefer: odata.continue-on-error` e partes sem changeset.
- O projeto de referência detectava erro por substring (`'400 Bad Request'`...) e deixava 429, 500, 503 e 504 de fora. Aqui o status de cada parte é lido (`HTTP/1.1 NNN`) e `>= 400` conta `[não verificado: divisão em resposta real]`: valide num lote com uma linha inválida de propósito.
- Conte linhas, não partes: a contagem incrementa pelo tamanho do chunk só quando há falha.
- 429: o excesso de requisições devolve `Retry-After`; limite a concorrência e comece com 10 requisições. A política de retentativa do conector `InvokeHttp` `[não verificado]` no JSON do designer.
- `Foreach` com concorrência não pode usar `Set variable`; `Increment` e `Append` são os usados aqui.
- O corpo da resposta vem em `$content` em base64 (`base64ToString`).

## Variações

- Linhas independentes: acrescente `Prefer: odata.continue-on-error` e tire o changeset.
- Só update ou só create: apague o outro escopo e a dependência.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/batch-upsert-changeset.json
```

Resultado esperado: `0 erro(s), 6 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `CONFIG`, `Lote_com_guid`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

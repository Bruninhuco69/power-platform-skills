# E-mail ao suporte com tratamento de escrita parcial

> **Arquivo**: `email-suporte-com-parcial.json` · **Frequência**: ocasional · **Maturidade**: desenhado [não verificado]: gerado, nunca devolvido pelo designer
> **Depende de**: `resolver-id-diretorio`; conectores de e-mail do Office 365 e SQL

## Propósito

`Try_email` envia o e-mail e registra o envio. `Catch_email` descobre se o e-mail **saiu** (`result()` filtrado por nome e status) e responde `warning` 'não clique de novo' ou `error` 'nada foi alterado'. `Responder_email` responde o sucesso.

## Quando usar / quando não usar

**Usar**

- Pedido de acesso/provisionamento por e-mail seguido de registro.

**Não usar**

- E-mail informativo sem escrita depois: `Catch` comum.

## Onde colar

Dentro do `Try_pedido`, depois de `Bloco_resolver_id`. O envelope traz o seu próprio Try/Catch/Response.

## Entradas e saídas

**Lê**

- `CONFIG.mailSuporte`, `outputs('Chamador')`, `outputs('Id_diretorio_final')`, parâmetros do trigger.

**Expõe**

- Resposta `success`, `warning` (parcial) ou `error`; fim nos dois últimos.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Escopo_email_suporte`; o mesmo conteúdo está em `email-suporte-com-parcial.json`). GUIDs fictícios; conexões: `<prefixo>_sharedoffice365`, `<prefixo>_sharedsql`.


```json
{
  "nodeId": "Escopo_email_suporte",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Try_email": {
        "type": "Scope",
        "actions": {
          "Enviar_email_ao_suporte": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "emailMessage/To": "@outputs('CONFIG')?['mailSuporte']",
                "emailMessage/Subject": "@concat('Solicitação de acesso: ',toLower(trim(coalesce(triggerBody()['text_1'],''))))",
                "emailMessage/Body": "@concat('Ação: ',toLower(trim(coalesce(triggerBody()['text'],''))),decodeUriComponent('%0D%0A'),'Alvo: ',toLower(trim(coalesce(triggerBody()['text_1'],''))),decodeUriComponent('%0D%0A'),'Id no diretório: ',outputs('Id_diretorio_final'),decodeUriComponent('%0D%0A'),'Solicitado por: ',outputs('Chamador'),decodeUriComponent('%0D%0A'),'Quando: ',formatDateTime(utcNow(),'dd/MM/yyyy HH:mm'),' UTC')",
                "emailMessage/Importance": "Normal"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365",
                "connection": "shared_office365",
                "operationId": "SendEmail_V2"
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000102"
            }
          },
          "Registrar_envio": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "server": "default",
                "database": "default",
                "procedure": "[dbo].[<procedure_registrar_envio>]",
                "parameters/Id_Alvo": "@int(coalesce(first(body('Estado_antes_gravar')?['value'])?['Id_Pedido'],0))",
                "parameters/Id_DiretorioAlvo": "@if(equals(outputs('Id_diretorio_final'),'(não resolvido)'),'',outputs('Id_diretorio_final'))"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_sql",
                "connection": "shared_sql",
                "operationId": "ExecuteProcedure_V2"
              }
            },
            "runAfter": {
              "Enviar_email_ao_suporte": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000103"
            }
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000104"
        }
      },
      "Catch_email": {
        "type": "Scope",
        "actions": {
          "Email_saiu": {
            "type": "Query",
            "inputs": {
              "from": "@result('Try_email')",
              "where": "@and(equals(item()?['name'],'Enviar_email_ao_suporte'),equals(item()?['status'],'Succeeded'))"
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000105"
            }
          },
          "Se_email_ja_saiu": {
            "type": "If",
            "expression": {
              "and": [
                {
                  "greater": [
                    "@length(body('Email_saiu'))",
                    0
                  ]
                }
              ]
            },
            "actions": {
              "Avisa_parcial": {
                "type": "Response",
                "kind": "PowerApp",
                "inputs": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "status": {
                        "title": "status",
                        "x-ms-dynamically-added": true,
                        "type": "string"
                      },
                      "description": {
                        "title": "description",
                        "x-ms-dynamically-added": true,
                        "type": "string"
                      },
                      "id": {
                        "title": "id",
                        "x-ms-dynamically-added": true,
                        "type": "string"
                      },
                      "url": {
                        "title": "url",
                        "x-ms-dynamically-added": true,
                        "type": "string"
                      }
                    },
                    "additionalProperties": {}
                  },
                  "statusCode": 200,
                  "body": {
                    "status": "warning",
                    "description": "Solicitação enviada ao suporte, mas o cadastro não registrou o pedido. Não clique de novo: avise o suporte.",
                    "id": "",
                    "url": ""
                  }
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000106"
                }
              },
              "Avisa_parcial_fim": {
                "type": "Terminate",
                "inputs": {
                  "runStatus": "Succeeded"
                },
                "runAfter": {
                  "Avisa_parcial": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000107"
                }
              }
            },
            "else": {
              "actions": {
                "Nega_email": {
                  "type": "Response",
                  "kind": "PowerApp",
                  "inputs": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "status": {
                          "title": "status",
                          "x-ms-dynamically-added": true,
                          "type": "string"
                        },
                        "description": {
                          "title": "description",
                          "x-ms-dynamically-added": true,
                          "type": "string"
                        },
                        "id": {
                          "title": "id",
                          "x-ms-dynamically-added": true,
                          "type": "string"
                        },
                        "url": {
                          "title": "url",
                          "x-ms-dynamically-added": true,
                          "type": "string"
                        }
                      },
                      "additionalProperties": {}
                    },
                    "statusCode": 200,
                    "body": {
                      "status": "error",
                      "description": "Não foi possível abrir o chamado no suporte. Nada foi alterado: tente de novo.",
                      "id": "",
                      "url": ""
                    }
                  },
                  "metadata": {
                    "operationMetadataId": "00000000-0000-0000-0000-000000000108"
                  }
                },
                "Nega_email_fim": {
                  "type": "Terminate",
                  "inputs": {
                    "runStatus": "Succeeded"
                  },
                  "runAfter": {
                    "Nega_email": [
                      "Succeeded"
                    ]
                  },
                  "metadata": {
                    "operationMetadataId": "00000000-0000-0000-0000-000000000109"
                  }
                }
              }
            },
            "runAfter": {
              "Email_saiu": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000110"
            }
          }
        },
        "runAfter": {
          "Try_email": [
            "Failed",
            "TimedOut",
            "Skipped"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000111"
        }
      },
      "Responder_email": {
        "type": "Response",
        "kind": "PowerApp",
        "inputs": {
          "schema": {
            "type": "object",
            "properties": {
              "status": {
                "title": "status",
                "x-ms-dynamically-added": true,
                "type": "string"
              },
              "description": {
                "title": "description",
                "x-ms-dynamically-added": true,
                "type": "string"
              },
              "id": {
                "title": "id",
                "x-ms-dynamically-added": true,
                "type": "string"
              },
              "url": {
                "title": "url",
                "x-ms-dynamically-added": true,
                "type": "string"
              }
            },
            "additionalProperties": {}
          },
          "statusCode": 200,
          "body": {
            "status": "success",
            "description": "Solicitação enviada ao suporte.",
            "id": "",
            "url": ""
          }
        },
        "runAfter": {
          "Try_email": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000112"
        }
      }
    },
    "runAfter": {
      "Bloco_resolver_id": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000113"
    }
  },
  "allConnectionData": {
    "Enviar_email_ao_suporte": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_office365"
        },
        "connection": {
          "id": "<prefixo>_sharedoffice365"
        },
        "connectionName": "<prefixo>_sharedoffice365"
      },
      "referenceKey": "shared_office365"
    },
    "Registrar_envio": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_sql"
        },
        "connection": {
          "id": "<prefixo>_sharedsql"
        },
        "connectionName": "<prefixo>_sharedsql"
      },
      "referenceKey": "shared_sql"
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
| `<procedure_registrar_envio>` | procedure | nome AS-BUILT |
| `emailMessage/To` | `CONFIG.mailSuporte` | mantenha vindo do `CONFIG` |
| assunto e corpo | texto neutro | texto do pedido; sem dado sensível além do necessário |

## runAfter

`Catch_email` depende de `Try_email` com `Failed`, `TimedOut`, `Skipped`; `Responder_email` com `Succeeded`.

## Armadilhas

- O projeto de referência marcava o envio numa variável dentro do `Try` e a lia no `Catch`; o `Catch` lê `outputs()` de ação possivelmente não executada. Aqui o `Catch` consulta `result('Try_email')`, que lista todas as ações de primeiro nível com status.
- `warning` 'não clique de novo' é o único caminho honesto: o e-mail saiu e não dá para desfazer.
- Corpo com quebra de linha: `decodeUriComponent('%0D%0A')`.
- Inicializar variável só funciona na raiz do flow; dentro de escopo use `Compose`.
- Catch dentro do Try do flow: ele termina a execução (`Terminate`), então o `Catch_pedido` externo não roda.

## Variações

- Duas etapas externas: um filtro `Email_saiu` por etapa e uma mensagem por combinação.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/email-suporte-com-parcial.json
```

Resultado esperado: `0 erro(s), 5 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `CONFIG`, `Chamador`, `Estado_antes_gravar`, `Id_diretorio_final`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

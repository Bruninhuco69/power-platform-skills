# Compensar no Dataverse (apagar o que ficou órfão)

> **Arquivo**: `compensacao-dataverse.json` · **Frequência**: rara · **Maturidade**: desenhado [não verificado]: base de um flow gerado, nunca devolvido pelo designer
> **Depende de**: `normalizar-entrada`; conector Dataverse; `nega-resposta-terminate`

## Propósito

`Try_criar` cria o pedido e o item. Se algo falha, `Compensar_criar` descobre por `result('Try_criar')` se o pedido chegou a ser criado e, só então, o apaga; responde `error` e termina. No sucesso, `Responder_criar` responde.

## Quando usar / quando não usar

**Usar**

- Cada `Add a new row` do Dataverse é um commit; sem changeset, a compensação em ordem inversa é o desfazer.

**Não usar**

- Linhas independentes em lote: use `$batch` (`batch-upsert-changeset`).
- Escrita em SQL: a procedure abre a transação.

## Onde colar

Dentro do `Caso_<acao>` (ou de `Try_pedido`), no lugar de `gravar-via-procedure`.

## Entradas e saídas

**Lê**

- `outputs('Normalizar_gravar')`.

**Expõe**

- Resposta de sucesso com o GUID do pedido; ou `Nega_criacao` e fim.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_criar_com_compensacao`; o mesmo conteúdo está em `compensacao-dataverse.json`). GUIDs fictícios; conexões: `<prefixo>_sharedcommondataserviceforapps`.

```json
{
  "nodeId": "Bloco_criar_com_compensacao",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Try_criar": {
        "type": "Scope",
        "actions": {
          "Criar_pedido": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "entityName": "<prefixo>_pedidos",
                "item/<prefixo>_descricao": "@outputs('Normalizar_gravar')?['descricao']",
                "item/<prefixo>_unidade": "@outputs('Normalizar_gravar')?['unidade']"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                "connection": "shared_commondataserviceforapps",
                "operationId": "CreateRecord"
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000087"
            }
          },
          "Criar_item": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "entityName": "<prefixo>_itenspedido",
                "item/<prefixo>_Pedido@odata.bind": "@concat('/<prefixo>_pedidos(',body('Criar_pedido')?['<prefixo>_pedidoid'],')')",
                "item/<prefixo>_quantidade": "@outputs('Normalizar_gravar')?['quantidade']"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                "connection": "shared_commondataserviceforapps",
                "operationId": "CreateRecord"
              }
            },
            "runAfter": {
              "Criar_pedido": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000088"
            }
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000089"
        }
      },
      "Compensar_criar": {
        "type": "Scope",
        "actions": {
          "Filtrar_pedido_criado": {
            "type": "Query",
            "inputs": {
              "from": "@result('Try_criar')",
              "where": "@and(equals(item()?['name'],'Criar_pedido'),equals(item()?['status'],'Succeeded'))"
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000090"
            }
          },
          "Se_pedido_criado": {
            "type": "If",
            "expression": {
              "and": [
                {
                  "greater": [
                    "@length(body('Filtrar_pedido_criado'))",
                    0
                  ]
                }
              ]
            },
            "actions": {
              "Apagar_pedido_orfao": {
                "type": "OpenApiConnection",
                "inputs": {
                  "parameters": {
                    "entityName": "<prefixo>_pedidos",
                    "recordId": "@body('Criar_pedido')?['<prefixo>_pedidoid']"
                  },
                  "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                    "connection": "shared_commondataserviceforapps",
                    "operationId": "DeleteRecord"
                  }
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000091"
                }
              }
            },
            "else": {
              "actions": {}
            },
            "runAfter": {
              "Filtrar_pedido_criado": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000092"
            }
          },
          "Nega_criacao": {
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
                "description": "Não foi possível registrar o pedido. Tente de novo; se persistir, avise o suporte.",
                "id": "",
                "url": ""
              }
            },
            "runAfter": {
              "Se_pedido_criado": [
                "Succeeded",
                "Failed",
                "Skipped",
                "TimedOut"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000093"
            }
          },
          "Nega_criacao_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_criacao": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000094"
            }
          }
        },
        "runAfter": {
          "Try_criar": [
            "Failed",
            "TimedOut"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000095"
        }
      },
      "Responder_criar": {
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
            "description": "Pedido registrado.",
            "id": "@{body('Criar_pedido')?['<prefixo>_pedidoid']}",
            "url": ""
          }
        },
        "runAfter": {
          "Try_criar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000096"
        }
      }
    },
    "runAfter": {
      "Bloco_normalizar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000097"
    }
  },
  "allConnectionData": {
    "Criar_pedido": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
        },
        "connection": {
          "id": "<prefixo>_sharedcommondataserviceforapps"
        },
        "connectionName": "<prefixo>_sharedcommondataserviceforapps",
        "impersonation": {}
      },
      "referenceKey": "shared_commondataserviceforapps"
    },
    "Criar_item": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
        },
        "connection": {
          "id": "<prefixo>_sharedcommondataserviceforapps"
        },
        "connectionName": "<prefixo>_sharedcommondataserviceforapps",
        "impersonation": {}
      },
      "referenceKey": "shared_commondataserviceforapps"
    },
    "Apagar_pedido_orfao": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
        },
        "connection": {
          "id": "<prefixo>_sharedcommondataserviceforapps"
        },
        "connectionName": "<prefixo>_sharedcommondataserviceforapps",
        "impersonation": {}
      },
      "referenceKey": "shared_commondataserviceforapps"
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
| `<prefixo>_pedidos`, `<prefixo>_itenspedido` | conjuntos de entidade | nomes AS-BUILT |
| `item/<prefixo>_Pedido` + sufixo `@odata.bind` | lookup do item para o pedido | nome da propriedade de navegação do lookup (respeita maiúsculas) |
| `<prefixo>_pedidoid` | chave primária | coluna de chave AS-BUILT |

## runAfter

`Compensar_criar` depende de `Try_criar` com `Failed` e `TimedOut`; `Responder_criar` com `Succeeded`.

## Armadilhas

- `Compensar_criar` **não** inclui `Skipped` de propósito: com `Skipped` ela apagaria sem nada criado. É o inverso da regra do `Catch` e o verificador avisa (F009); o aviso é esperado.
- Apagar o órfão só se `Criar_pedido` terminou `Succeeded` (filtro sobre `result()`): sem o filtro, o `DeleteRecord` roda com `recordId` vazio e falha.
- A compensação pode falhar também: o `Nega_criacao` roda em qualquer estado do apagar, e a frase manda avisar o suporte se persistir. Registre no `log-execucao`.
- `result()` devolve só ações de primeiro nível do escopo: `Criar_pedido` e `Criar_item` precisam ser filhos diretos de `Try_criar`.
- Se a criação do item for repetível, prefira alternate key e upsert a compensar.

## Variações

- Mais de dois passos: compense na ordem inversa, um filtro e um `If` por passo criado.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/compensacao-dataverse.json
```

Resultado esperado: `0 erro(s), 4 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Normalizar_gravar`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.
- `F009` em `Compensar_criar`: esperado, ver *Armadilhas*.

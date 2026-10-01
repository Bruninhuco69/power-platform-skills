# Escopo por várias unidades (trilha Dataverse)

> **Arquivo**: `escopo-unidades-dataverse.json` · **Frequência**: ocasional · **Maturidade**: desenhado [não verificado]: gerado, nunca devolvido pelo designer
> **Depende de**: `ler-chamador-dataverse`; tabela de vínculo usuário-unidade

## Propósito

Monta a lista de unidades permitidas (vínculos mais a unidade primária), calcula `Pode_todas_unidades` pela flag do perfil e nega usuário sem unidade ou com unidade alheia ao registro.

## Quando usar / quando não usar

**Usar**

- Perfil com várias unidades, em Dataverse.

**Não usar**

- Uma unidade só e dado em SQL: `escopo-unidade`.

## Onde colar

Dentro de `Try_pedido` (flow de ação única) ou do `Caso`, depois de `Ler_perfil`.

## Entradas e saídas

**Lê**

- `outputs('Chamador')`, `body('Ler_chamador')`, `body('Ler_perfil')`, parâmetro de unidade do trigger.

**Expõe**

- `outputs('Unidades_permitidas')`, `outputs('Pode_todas_unidades')`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_escopo_unidades`; o mesmo conteúdo está em `escopo-unidades-dataverse.json`). GUIDs fictícios; conexões: `<prefixo>_sharedcommondataserviceforapps`.


```json
{
  "nodeId": "Bloco_escopo_unidades",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Minhas_unidades": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_usuariounidades",
            "$filter": "@concat('<prefixo>_upn eq ''',replace(outputs('Chamador'),'''',''''''),'''')"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000046"
        }
      },
      "Lista_minhas_unidades": {
        "type": "Select",
        "inputs": {
          "from": "@coalesce(body('Minhas_unidades')?['value'],json('[]'))",
          "select": "@trim(string(item()?['<prefixo>_unidade']))"
        },
        "runAfter": {
          "Minhas_unidades": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000047"
        }
      },
      "Unidades_permitidas": {
        "type": "Compose",
        "inputs": "@union(body('Lista_minhas_unidades'),if(empty(trim(string(first(body('Ler_chamador')?['value'])?['<prefixo>_unidade']))),json('[]'),createArray(trim(string(first(body('Ler_chamador')?['value'])?['<prefixo>_unidade'])))))",
        "runAfter": {
          "Lista_minhas_unidades": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000048"
        }
      },
      "Pode_todas_unidades": {
        "type": "Compose",
        "inputs": "@equals(first(body('Ler_perfil')?['value'])?['<prefixo>_todasunidades'],true)",
        "runAfter": {
          "Unidades_permitidas": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000049"
        }
      },
      "Se_sem_unidade": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@outputs('Pode_todas_unidades')",
                false
              ]
            },
            {
              "equals": [
                "@empty(trim(join(outputs('Unidades_permitidas'),'')))",
                true
              ]
            }
          ]
        },
        "actions": {
          "Nega_sem_unidade": {
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
                "description": "Seu usuário não está vinculado a nenhuma unidade. Procure o suporte.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000050"
            }
          },
          "Nega_sem_unidade_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_sem_unidade": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000051"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Pode_todas_unidades": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000052"
        }
      },
      "Se_unidade_alheia": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@outputs('Pode_todas_unidades')",
                false
              ]
            },
            {
              "or": [
                {
                  "equals": [
                    "@empty(trim(coalesce(triggerBody()['text_3'],'')))",
                    true
                  ]
                },
                {
                  "equals": [
                    "@contains(outputs('Unidades_permitidas'),toUpper(trim(coalesce(triggerBody()['text_3'],''))))",
                    false
                  ]
                }
              ]
            }
          ]
        },
        "actions": {
          "Nega_unidade_alheia": {
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
                "description": "Você não tem acesso à unidade deste registro.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000053"
            }
          },
          "Nega_unidade_alheia_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_unidade_alheia": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000054"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Se_sem_unidade": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000055"
        }
      }
    },
    "runAfter": {
      "Ler_perfil": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000056"
    }
  },
  "allConnectionData": {
    "Minhas_unidades": {
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
| `<prefixo>_usuariounidades` | tabela de vínculo | nome AS-BUILT |
| `<prefixo>_unidade`, `<prefixo>_todasunidades` | colunas | nomes lógicos AS-BUILT |
| `param(3)` (`text_3`) | unidade do trigger | posição do parâmetro de unidade |

## runAfter

Raiz depende de `Ler_perfil`; os `If` encadeiam em `Pode_todas_unidades`.

## Armadilhas

- Sem lotação a lista chega como `['']`, array de um item, que `empty()` considera cheio: teste `empty(trim(join(lista,'')))`.
- Filtro opcional em que 'todas' = `null`: ligue o `null` cru, sem `coalesce` (`''` casa nada e o relatório sai vazio para quem vê tudo).
- Em ação sobre registro existente, compare com a unidade do registro lido, não com o parâmetro.
- Valor do usuário que vai para `$filter` leva apóstrofo duplicado.

## Variações

- Lista de unidades pedidas (relatório): `intersection(pedidas, permitidas)` e negue se o resultado for menor que o pedido.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/escopo-unidades-dataverse.json
```

Resultado esperado: `0 erro(s), 3 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Chamador`, `Ler_chamador`, `Ler_perfil`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

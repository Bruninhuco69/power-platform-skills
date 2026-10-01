# Ler o chamador e o perfil no Dataverse

> **Arquivo**: `ler-chamador-dataverse.json` · **Frequência**: comum · **Maturidade**: desenhado [não verificado]: gerado, nunca devolvido pelo designer
> **Depende de**: `identificar-chamador`; conector Dataverse; tabelas `<prefixo>_usuarios` e `<prefixo>_perfis`

## Propósito

Cria `Try_pedido`, busca o usuário ativo pelo UPN, nega quando não existe e lê a linha do perfil (flags de permissão) pelo lookup do usuário.

## Quando usar / quando não usar

**Usar**

- Projeto na trilha Dataverse; perfil como tabela com colunas Boolean de permissão.

**Não usar**

- Perfil em SQL: use `ler-chamador-sql`.

## Onde colar

Raiz do escopo do flow, depois de `Bloco_chamador`. Os demais componentes entram dentro de `Try_pedido`.

## Entradas e saídas

**Lê**

- `outputs('Chamador')`.

**Expõe**

- `body('Ler_chamador')?['value']` (usuário) e `body('Ler_perfil')?['value']` (perfil e flags).

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Try_pedido`; o mesmo conteúdo está em `ler-chamador-dataverse.json`). GUIDs fictícios; conexões: `<prefixo>_sharedcommondataserviceforapps`.


```json
{
  "nodeId": "Try_pedido",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Ler_chamador": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_usuarios",
            "$filter": "@concat('<prefixo>_upn eq ''',replace(outputs('Chamador'),'''',''''''),''' and <prefixo>_ativo eq true')",
            "$top": 1
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000013"
        }
      },
      "Se_chamador_desconhecido": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(coalesce(body('Ler_chamador')?['value'],json('[]')))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Nega_chamador": {
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
                "description": "Seu perfil não permite esta ação.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000014"
            }
          },
          "Nega_chamador_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_chamador": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000015"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Ler_chamador": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000016"
        }
      },
      "Ler_perfil": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_perfis",
            "$filter": "@concat('<prefixo>_perfilid eq ',coalesce(first(body('Ler_chamador')?['value'])?['_<prefixo>_perfil_value'],'null'))",
            "$top": 1
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "runAfter": {
          "Se_chamador_desconhecido": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000017"
        }
      }
    },
    "runAfter": {
      "Bloco_chamador": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000018"
    }
  },
  "allConnectionData": {
    "Ler_chamador": {
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
    "Ler_perfil": {
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
| `<prefixo>_usuarios`, `<prefixo>_perfis` | conjuntos de entidade | nomes AS-BUILT lidos do ambiente (NOMES-AS-BUILT) |
| `<prefixo>_upn`, `<prefixo>_ativo` | colunas lógicas | nomes lógicos reais (em flow e OData vale o lógico, não o de exibição) |
| `_<prefixo>_perfil_value` | lookup do usuário para o perfil | nome do lookup; se o perfil for Choice, filtre pelo valor formatado |

## runAfter

Raiz depende de `Bloco_chamador`; `Ler_perfil` depende de `Se_chamador_desconhecido`.

## Armadilhas

- Filtro com nome de coluna errado não dá erro: devolve lista vazia, indistinguível de 'nenhum registro'. Confira o esquema da tabela, nunca um extrato filtrado.
- O UPN entra no `$filter` com apóstrofo duplicado (`replace(x,'''','''''')`): sem isso um nome com apóstrofo quebra a consulta.
- Sem perfil resolvido, `$filter` vira `eq null` e devolve vazio: a autorização nega (fail-closed). Mantenha assim.
- Perfil guardado como Choice vem como número; o texto está em `<coluna>@OData.Community.Display.V1.FormattedValue`.

## Variações

- Flag de permissão para `autorizar-por-flag` neste desenho:

```text
@not(equals(first(body('Ler_perfil')?['value'])?['<prefixo>_podegravar'],true))
```

Destino: `expression` de um `If` (`equals` com `@true`). Coluna Boolean do Dataverse chega `true`/`false`; ausente nega.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/ler-chamador-dataverse.json
```

Resultado esperado: `0 erro(s), 1 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Chamador`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

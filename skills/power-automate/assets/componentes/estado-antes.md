# Ler o estado real do registro antes de escrever

> **Arquivo**: `estado-antes.json` · **Frequência**: comum · **Maturidade**: estável
> **Depende de**: `normalizar-entrada`; conector SQL; `<tabela_pedido>`

## Propósito

Lê o registro (`GetItems_V2`, `$top 1`) pelo id normalizado e nega com `Nega_inexistente` quando não vem linha. É a fonte de verdade para escopo por unidade e para 'nada mudou'.

## Quando usar / quando não usar

**Usar**

- Editar, baixar, resolver: toda ação sobre registro que já existe.

**Não usar**

- Cadastro (o registro ainda não existe): compare o parâmetro que será gravado.

## Onde colar

Dentro do `Caso_<acao>`, depois de `Bloco_normalizar`.

## Entradas e saídas

**Lê**

- `outputs('Normalizar_gravar')?['idNumero']`.

**Expõe**

- `body('Estado_antes_gravar')?['value']`: lista de 0 ou 1 linha; `first(...)` lê o registro.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_estado_antes`; o mesmo conteúdo está em `estado-antes.json`). GUIDs fictícios; conexões: `<prefixo>_sharedsql`.


```json
{
  "nodeId": "Bloco_estado_antes",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Estado_antes_gravar": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "server": "default",
            "database": "default",
            "table": "[dbo].[<tabela_pedido>]",
            "$filter": "@concat('Id_Pedido eq ',string(outputs('Normalizar_gravar')?['idNumero']))",
            "$top": 1
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sql",
            "connection": "shared_sql",
            "operationId": "GetItems_V2"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000036"
        }
      },
      "Se_pedido_inexistente_gravar": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(coalesce(body('Estado_antes_gravar')?['value'],json('[]')))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Nega_inexistente_gravar": {
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
                "description": "Pedido não encontrado.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000037"
            }
          },
          "Nega_inexistente_gravar_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_inexistente_gravar": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000038"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Estado_antes_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000039"
        }
      }
    },
    "runAfter": {
      "Bloco_normalizar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000040"
    }
  },
  "allConnectionData": {
    "Estado_antes_gravar": {
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
| `<tabela_pedido>` | tabela entre colchetes | nome AS-BUILT da tabela |
| `Id_Pedido` | coluna do id | coluna AS-BUILT |
| `$top` | `1` | mantenha |
| nomes `*_gravar` | sufixo da ação | troque pelo sufixo do seu caso |

## runAfter

Raiz depende de `Bloco_normalizar`; `Se_pedido_inexistente_gravar` depende de `Estado_antes_gravar`.

## Armadilhas

- Compare a unidade do **registro real**, não a do parâmetro: o parâmetro é ignorado fora do cadastro e conferi-lo deixaria o chamador escolher a própria autorização.
- Ação que escreve em dois registros lê e confere os dois.
- `$filter` sobre `bit` usa `true`/`false`, não `1`/`0`.
- Nome de coluna errado no `$filter` devolve lista vazia, que parece 'não encontrado'.

## Variações

- Dataverse: `GetItem` por `recordId` (quando o app tem o GUID) ou `ListRecords` com `$top 1`; a leitura `first(body(...)?['value'])` é a mesma.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/estado-antes.json
```

Resultado esperado: `0 erro(s), 1 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Normalizar_gravar`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

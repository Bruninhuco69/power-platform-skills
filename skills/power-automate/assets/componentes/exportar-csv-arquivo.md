# Exportar CSV para o armazenamento de arquivos e devolver o link

> **Arquivo**: `exportar-csv-arquivo.json` · **Frequência**: ocasional · **Maturidade**: desenhado [não verificado]: gerado, nunca devolvido pelo designer
> **Depende de**: `config` (`pastaSaida`); uma leitura anterior `Ler_dados_exportacao`; conector de arquivos de nuvem da Microsoft (id do conector no JSON)

## Propósito

Avisa se não há linhas, monta cada linha de CSV com `;` (separador, escape de `;` e quebras de linha), grava o arquivo com BOM UTF-8, cria o link de compartilhamento e responde `success` com `url` de download.

## Quando usar / quando não usar

**Usar**

- Exportação de resultado de procedure ou consulta.

**Não usar**

- Arquivo muito grande: o conector de arquivo e o app têm limite; filtre ou pagine.

## Onde colar

Dentro do `Caso_csv` do `Switch_formato` (ou de `Try_pedido`), depois da leitura dos dados.

## Entradas e saídas

**Lê**

- `body('Ler_dados_exportacao')?['ResultSets']?['Table1']` (lista de objetos), `CONFIG.pastaSaida`.

**Expõe**

- `body('Linhas_csv')` (lista de linhas), arquivo na pasta de saída, resposta com `url`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_exportar_csv`; o mesmo conteúdo está em `exportar-csv-arquivo.json`). GUIDs fictícios; conexões: `<prefixo>_sharedonedriveforbusiness`.

```json
{
  "nodeId": "Bloco_exportar_csv",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Se_exportacao_vazia": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(coalesce(body('Ler_dados_exportacao')?['ResultSets']?['Table1'],json('[]')))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Avisa_exportacao_vazia": {
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
                "description": "Nenhum registro atende aos filtros. Nada foi gerado.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000123"
            }
          },
          "Avisa_exportacao_vazia_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Avisa_exportacao_vazia": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000124"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000125"
        }
      },
      "Linhas_csv": {
        "type": "Select",
        "inputs": {
          "from": "@coalesce(body('Ler_dados_exportacao')?['ResultSets']?['Table1'],json('[]'))",
          "select": "@concat(replace(replace(replace(coalesce(string(item()?['Pedido']),''),';',','),decodeUriComponent('%0D'),' '),decodeUriComponent('%0A'),' '),';',replace(replace(replace(coalesce(string(item()?['Descricao']),''),';',','),decodeUriComponent('%0D'),' '),decodeUriComponent('%0A'),' '),';',replace(replace(replace(coalesce(string(item()?['Unidade']),''),';',','),decodeUriComponent('%0D'),' '),decodeUriComponent('%0A'),' '))"
        },
        "runAfter": {
          "Se_exportacao_vazia": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000126"
        }
      },
      "Gravar_csv": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "folderPath": "@outputs('CONFIG')?['pastaSaida']",
            "name": "Pedidos_@{formatDateTime(utcNow(),'yyyyMMdd-HHmm')}.csv",
            "body": "@concat(decodeUriComponent('%EF%BB%BF'),'Pedido;Descricao;Unidade',decodeUriComponent('%0D%0A'),join(body('Linhas_csv'),decodeUriComponent('%0D%0A')))"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness",
            "connection": "shared_onedriveforbusiness",
            "operationId": "CreateFile"
          }
        },
        "runAfter": {
          "Linhas_csv": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000127"
        }
      },
      "Link_csv": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "id": "@coalesce(body('Gravar_csv')?['Id'],'')",
            "type": "View",
            "scope": "Organization"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness",
            "connection": "shared_onedriveforbusiness",
            "operationId": "CreateShareLinkV2"
          }
        },
        "runAfter": {
          "Gravar_csv": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000128"
        }
      },
      "Responder_csv": {
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
            "description": "@{concat(string(length(body('Linhas_csv'))),' registro(s) exportado(s).')}",
            "id": "",
            "url": "@{if(empty(coalesce(body('Link_csv')?['WebUrl'],'')),'',concat(body('Link_csv')?['WebUrl'],if(contains(body('Link_csv')?['WebUrl'],'?'),'&','?'),'download=1'))}"
          }
        },
        "runAfter": {
          "Link_csv": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000129"
        }
      }
    },
    "runAfter": {
      "Bloco_filtros": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000130"
    }
  },
  "allConnectionData": {
    "Gravar_csv": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness"
        },
        "connection": {
          "id": "<prefixo>_sharedonedriveforbusiness"
        },
        "connectionName": "<prefixo>_sharedonedriveforbusiness"
      },
      "referenceKey": "shared_onedriveforbusiness"
    },
    "Link_csv": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness"
        },
        "connection": {
          "id": "<prefixo>_sharedonedriveforbusiness"
        },
        "connectionName": "<prefixo>_sharedonedriveforbusiness"
      },
      "referenceKey": "shared_onedriveforbusiness"
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
| `Ler_dados_exportacao` | ação de leitura anterior | a procedure/consulta que produz as linhas |
| `Pedido`, `Descricao`, `Unidade` | colunas e cabeçalho | colunas da exportação, na ordem do cabeçalho |
| `pastaSaida` | `CONFIG` | pasta de saída do conector de arquivos |
| `scope: Organization` | alcance do link | o mais restrito que atenda |

## runAfter

Raiz depende de `Bloco_filtros`; as ações encadeiam em ordem.

## Armadilhas

- `Select` devolve envelope em `outputs()`: use `body('Linhas_csv')` no `join` (F011).
- BOM `decodeUriComponent('%EF%BB%BF')` no início para o Excel abrir acentos; quebra de linha CRLF.
- Escape de `;`, CR e LF dentro do dado; campo que começa com `=`, `+`, `-` ou `@` vira fórmula no Excel: prefixe com apóstrofo se o dado vem de usuário `[não verificado]`.
- O link devolve `WebUrl`; acrescente `download=1` (ou `&download=1`) para baixar em vez de abrir.
- A exportação roda com a conexão do conector, não com o usuário: o escopo de unidade precisa ter filtrado antes.

## Variações

- Contagem antes de exportar (procedure `contar`) para avisar vazio sem ler tudo.
- Dataverse: `ListRecords` com paginação nativa (`paginacao-nativa`) alimenta o mesmo `Select`.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/exportar-csv-arquivo.json
```

Resultado esperado: `0 erro(s), 3 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `CONFIG`, `Ler_dados_exportacao`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

# Gerar PDF a partir de HTML (armazenamento de arquivos)

> **Arquivo**: `html-para-pdf.json` · **Frequência**: ocasional · **Maturidade**: desenhado [não verificado]: gerado, nunca devolvido pelo designer
> **Depende de**: `exportar-csv-arquivo` (mesma pasta); `Linhas_html`; conector de arquivos de nuvem da Microsoft (id do conector no JSON)

## Propósito

Grava o HTML temporário, converte para PDF (`ConvertFile`), apaga o HTML mesmo se a conversão falhar, nega se o PDF não veio, grava o PDF, cria o link e responde.

## Quando usar / quando não usar

**Usar**

- Páginas simples geradas por `Select` + `join`.

**Não usar**

- Documento grande: o conversor aceita até 2 MB por arquivo.

## Onde colar

Dentro de `Caso_pdf` do `Switch_formato`, depois de `Linhas_html`.

## Entradas e saídas

**Lê**

- `body('Linhas_html')`: lista de fragmentos HTML (um `Select` anterior).

**Expõe**

- Arquivo PDF na pasta de saída e resposta com `url`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_html_para_pdf`; o mesmo conteúdo está em `html-para-pdf.json`). GUIDs fictícios; conexões: `<prefixo>_sharedonedriveforbusiness`.

```json
{
  "nodeId": "Bloco_html_para_pdf",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Html_pagina": {
        "type": "Compose",
        "inputs": "@concat('<html><head><meta charset=\"utf-8\"></head><body>',join(coalesce(body('Linhas_html'),json('[]')),''),'</body></html>')",
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000131"
        }
      },
      "Gravar_html": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "folderPath": "@outputs('CONFIG')?['pastaSaida']",
            "name": "Etiquetas_@{formatDateTime(utcNow(),'yyyyMMdd-HHmm')}.html",
            "body": "@outputs('Html_pagina')"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness",
            "connection": "shared_onedriveforbusiness",
            "operationId": "CreateFile"
          }
        },
        "runAfter": {
          "Html_pagina": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000132"
        }
      },
      "Converter_pdf": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "id": "@coalesce(body('Gravar_html')?['Id'],'')",
            "type": "PDF"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness",
            "connection": "shared_onedriveforbusiness",
            "operationId": "ConvertFile"
          }
        },
        "runAfter": {
          "Gravar_html": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000133"
        }
      },
      "Limpar_html": {
        "type": "OpenApiConnection",
        "description": "Absorção intencional: apagar o HTML temporário não pode mascarar a falha da conversão.",
        "inputs": {
          "parameters": {
            "id": "@coalesce(body('Gravar_html')?['Id'],'')"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness",
            "connection": "shared_onedriveforbusiness",
            "operationId": "DeleteFile"
          }
        },
        "runAfter": {
          "Converter_pdf": [
            "Succeeded",
            "Failed",
            "Skipped"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000134"
        }
      },
      "Se_pdf_falhou": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(coalesce(string(body('Converter_pdf')),''))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Nega_pdf": {
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
                "description": "Não foi possível gerar o PDF. O conversor aceita até 2 MB por arquivo: filtre o período ou a unidade e tente de novo, ou exporte em CSV.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000135"
            }
          },
          "Nega_pdf_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_pdf": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000136"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Limpar_html": [
            "Succeeded",
            "Failed",
            "Skipped",
            "TimedOut"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000137"
        }
      },
      "Gravar_pdf": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "folderPath": "@outputs('CONFIG')?['pastaSaida']",
            "name": "Etiquetas_@{formatDateTime(utcNow(),'yyyyMMdd-HHmm')}.pdf",
            "body": "@body('Converter_pdf')"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_onedriveforbusiness",
            "connection": "shared_onedriveforbusiness",
            "operationId": "CreateFile"
          }
        },
        "runAfter": {
          "Se_pdf_falhou": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000138"
        }
      },
      "Link_pdf": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "id": "@coalesce(body('Gravar_pdf')?['Id'],'')",
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
          "Gravar_pdf": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000139"
        }
      },
      "Responder_pdf": {
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
            "description": "PDF gerado.",
            "id": "",
            "url": "@{if(empty(coalesce(body('Link_pdf')?['WebUrl'],'')),'',concat(body('Link_pdf')?['WebUrl'],if(contains(body('Link_pdf')?['WebUrl'],'?'),'&','?'),'download=1'))}"
          }
        },
        "runAfter": {
          "Link_pdf": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000140"
        }
      }
    },
    "runAfter": {
      "Bloco_filtros": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000141"
    }
  },
  "allConnectionData": {
    "Gravar_html": {
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
    "Converter_pdf": {
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
    "Limpar_html": {
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
    "Gravar_pdf": {
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
    "Link_pdf": {
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
| `Linhas_html` | `Select` de fragmentos | a ação que produz o HTML de cada item |
| `pastaSaida` | `CONFIG` | pasta |
| limite | 2 MB | ajuste a mensagem se o conversor mudar |

## runAfter

Raiz depende de `Bloco_filtros`. `Limpar_html` depende de `Converter_pdf` em `Succeeded`, `Failed`, `Skipped`.

## Armadilhas

- `Limpar_html` roda também quando a conversão falha: é absorção deliberada para não deixar HTML solto.
- `Se_pdf_falhou` testa se `body('Converter_pdf')` veio vazio; a falha do conector é tratada por esse teste, e a mensagem manda reduzir o conjunto.
- Uma ação `Failed` dentro do `Try` marca o `Try` como `Failed` mesmo se tratada depois: termine com `Terminate` (a negação já termina), ou o `Catch` dispara.
- O HTML deve declarar `<meta charset="utf-8">`.
- Identificador de largura fixa (ex.: código de barras) em WDL só é possível com comprimento fixo de entrada (sem laço); fora desse caso, Office Script ou serviço externo.

## Variações

- Sem conversão (só HTML): pule `Converter_pdf` e devolva o link do HTML.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/html-para-pdf.json
```

Resultado esperado: `0 erro(s), 3 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `CONFIG`, `Linhas_html`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

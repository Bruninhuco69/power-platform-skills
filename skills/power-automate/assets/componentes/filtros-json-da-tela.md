# Filtros enviados como JSON em um parâmetro de texto

> **Arquivo**: `filtros-json-da-tela.json` · **Frequência**: ocasional · **Maturidade**: desenhado [não verificado]: gerado, nunca devolvido pelo designer
> **Depende de**: `autorizar-por-flag`; parâmetro de filtros no trigger

## Propósito

Lê o texto como objeto (`Filtros`), remove uma a uma as chaves conhecidas (`Filtros_resto_N`) e confere que o resíduo é `{}`: chave desconhecida nega. Valida a forma das listas e nega com a mensagem.

## Quando usar / quando não usar

**Usar**

- Relatório ou exportação com filtros opcionais.

**Não usar**

- Poucos filtros fixos: um parâmetro posicional por filtro é mais simples.

## Onde colar

Dentro do `Try_pedido`, depois de `Autorizar_exportar`.

## Entradas e saídas

**Lê**

- `triggerBody()['text_1']`: objeto JSON como texto.

**Expõe**

- `outputs('Filtros')` (objeto) e `outputs('Validar_filtros')` (mensagem ou vazio).

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_filtros`; o mesmo conteúdo está em `filtros-json-da-tela.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_filtros",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Filtros": {
        "type": "Compose",
        "inputs": "@json(if(and(startsWith(trim(coalesce(triggerBody()['text_1'],'')),'{'),endsWith(trim(coalesce(triggerBody()['text_1'],'')),'}')),trim(coalesce(triggerBody()['text_1'],'')),'{}'))",
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000114"
        }
      },
      "Filtros_resto_1": {
        "type": "Compose",
        "inputs": "@if(contains(outputs('Filtros'),'unidades'),removeProperty(outputs('Filtros'),'unidades'),outputs('Filtros'))",
        "runAfter": {
          "Filtros": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000115"
        }
      },
      "Filtros_resto_2": {
        "type": "Compose",
        "inputs": "@if(contains(outputs('Filtros_resto_1'),'status'),removeProperty(outputs('Filtros_resto_1'),'status'),outputs('Filtros_resto_1'))",
        "runAfter": {
          "Filtros_resto_1": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000116"
        }
      },
      "Filtros_resto_3": {
        "type": "Compose",
        "inputs": "@if(contains(outputs('Filtros_resto_2'),'data_de'),removeProperty(outputs('Filtros_resto_2'),'data_de'),outputs('Filtros_resto_2'))",
        "runAfter": {
          "Filtros_resto_2": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000117"
        }
      },
      "Validar_filtros": {
        "type": "Compose",
        "inputs": "@if(not(equals(trim(string(outputs('Filtros_resto_3'))),'{}')),'Filtro desconhecido. Avise o suporte.',if(and(not(empty(coalesce(string(outputs('Filtros')?['unidades']),''))),not(startsWith(trim(string(outputs('Filtros')?['unidades'])),'['))),'Filtro inválido. Refaça a seleção e tente de novo.',''))",
        "runAfter": {
          "Filtros_resto_3": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000118"
        }
      },
      "Se_filtros_invalidos": {
        "type": "If",
        "expression": {
          "and": [
            {
              "greater": [
                "@length(outputs('Validar_filtros'))",
                0
              ]
            }
          ]
        },
        "actions": {
          "Nega_filtros": {
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
                "description": "@{outputs('Validar_filtros')}",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000119"
            }
          },
          "Nega_filtros_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_filtros": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000120"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Validar_filtros": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000121"
        }
      }
    },
    "runAfter": {
      "Autorizar_exportar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000122"
    }
  },
  "allConnectionData": {},
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

## Parâmetros a trocar

| Item | Valor no JSON | Trocar por |
|---|---|---|
| `unidades`, `status`, `data_de` | chaves conhecidas | uma linha `Filtros_resto_N` por chave; troque o número do último na validação |
| `text_1` | posição do parâmetro | posição no trigger |

## runAfter

Raiz depende de `Autorizar_exportar`; as `Filtros_resto_N` encadeiam.

## Armadilhas

- `json()` de texto que começa com `{` e termina com `}` mas está malformado estoura; o app deve montar o texto com `JSON()`.
- Remover chaves com `if(contains(o,'k'), removeProperty(o,'k'), o)` **aninhado** dobra a expressão a cada chave (2^8 cópias com 8 chaves): um `Compose` por chave encadeia em linear. Limite 8.192 caracteres (F013).
- Lista vem como texto que começa com `[`; confira a forma antes de usar em `join`.
- Valor de filtro que vai para `$filter` leva apóstrofo duplicado; data só em formato validado.
- Em vez de `ISJSON`, que não existe em WDL, a validação de chave desconhecida é o resíduo `{}`.

## Variações

- Data: valide ano, mês e dia separados (`substring` com protetores) antes de montar `$filter` ou chamar a procedure.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/filtros-json-da-tela.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

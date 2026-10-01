# Derivar um valor com Switch aninhado

> **Arquivo**: `derivar-valor-switch.json` · **Frequência**: rara · **Maturidade**: único: gabarito de um flow; leitura `coalesce` de casos não executados [não verificado]
> **Depende de**: `normalizar-entrada`

## Propósito

Um `Switch` em que cada caso é um `Compose` com nome **próprio** (`Destino_<valor>`). Os consumidores leem o resultado com `coalesce(outputs('Destino_aberto'), outputs('Destino_fechado'))`.

## Quando usar / quando não usar

**Usar**

- Derivação por tabela de combinações, em vez de `if()` aninhado de 8 níveis.

**Não usar**

- Dois estados só: um `if()` simples basta.

## Onde colar

Dentro do `Caso_<acao>`, depois de `Bloco_normalizar`.

## Entradas e saídas

**Lê**

- Valor de decisão normalizado (aqui, `situacao`, 7º parâmetro).

**Expõe**

- Um dos `Destino_*` executa; `default` nega com `Nega_situacao`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_derivar_destino`; o mesmo conteúdo está em `derivar-valor-switch.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_derivar_destino",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Derivar_destino_gravar": {
        "type": "Switch",
        "expression": "@toLower(trim(coalesce(trim(coalesce(triggerBody()['text_6'],'')),'')))",
        "cases": {
          "Caso_destino_aberto": {
            "case": "aberto",
            "actions": {
              "Destino_aberto": {
                "type": "Compose",
                "inputs": "Em atendimento",
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000072"
                }
              }
            }
          },
          "Caso_destino_fechado": {
            "case": "fechado",
            "actions": {
              "Destino_fechado": {
                "type": "Compose",
                "inputs": "Arquivado",
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000073"
                }
              }
            }
          }
        },
        "default": {
          "actions": {
            "Nega_situacao": {
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
                  "description": "Situação desconhecida.",
                  "id": "",
                  "url": ""
                }
              },
              "metadata": {
                "operationMetadataId": "00000000-0000-0000-0000-000000000074"
              }
            },
            "Nega_situacao_fim": {
              "type": "Terminate",
              "inputs": {
                "runStatus": "Succeeded"
              },
              "runAfter": {
                "Nega_situacao": [
                  "Succeeded"
                ]
              },
              "metadata": {
                "operationMetadataId": "00000000-0000-0000-0000-000000000075"
              }
            }
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000076"
        }
      }
    },
    "runAfter": {
      "Bloco_normalizar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000077"
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
| `aberto`, `fechado` | valores de decisão | os do seu domínio |
| `Em atendimento`, `Arquivado` | valores derivados | o texto/código gravado |
| `Destino_*` | `Compose` de cada caso | nome próprio por caso |

## runAfter

Raiz depende de `Bloco_normalizar`.

## Armadilhas

- Caso e ação dividem o espaço de nomes do designer: `Caso_destino_aberto` ≠ `Destino_aberto` (F008).
- Ler `outputs()` de um `Compose` que não executou: o projeto de referência usa `coalesce` sobre todos os casos e o designer aceitou; o comportamento em execução com casos não executados não foi registrado `[não verificado]`. Teste com cada valor.
- `default` obrigatório: valor desconhecido nega, nunca cai num destino padrão.

## Variações

- Combinação de dois estados: `Switch` externo por um e `Switch` interno por outro, cada folha com `Compose` de nome próprio.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/derivar-valor-switch.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

# Switch por ação, com autorização por caso

> **Arquivo**: `switch-acao.json` · **Frequência**: comum · **Maturidade**: estável
> **Depende de**: `ler-chamador-sql`; `autorizar-por-flag`; `nega-resposta-terminate`

## Propósito

`Switch` sobre `toLower(trim(triggerBody()['text']))`, um `Caso_<acao>` por ação (cada um começa com a própria autorização) e um `default` que responde `error` **nomeando** o valor recebido.

## Quando usar / quando não usar

**Usar**

- Flow com 2 ou mais ações (cadastrar, editar, baixar...).

**Não usar**

- Flow de ação única: use `autorizar-por-flag` direto.
- Para derivar um valor: use `derivar-valor-switch`.

## Onde colar

Dentro de `Try_pedido`, depois de `Se_chamador_desconhecido`.

## Entradas e saídas

**Lê**

- `triggerBody()['text']`: o nome da ação (1º parâmetro do trigger).

**Expõe**

- O ramo escolhido executa os blocos colados em cada `Caso_`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Switch_acao`; o mesmo conteúdo está em `switch-acao.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Switch_acao",
  "serializedValue": {
    "type": "Switch",
    "expression": "@toLower(trim(coalesce(triggerBody()['text'],'')))",
    "cases": {
      "Caso_gravar": {
        "case": "gravar",
        "actions": {
          "Autorizar_gravar": {
            "type": "If",
            "expression": {
              "and": [
                {
                  "equals": [
                    "@not(or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'true')))",
                    "@true"
                  ]
                }
              ]
            },
            "actions": {
              "Nega_perm_gravar": {
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
                  "operationMetadataId": "00000000-0000-0000-0000-000000000025"
                }
              },
              "Nega_perm_gravar_fim": {
                "type": "Terminate",
                "inputs": {
                  "runStatus": "Succeeded"
                },
                "runAfter": {
                  "Nega_perm_gravar": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000026"
                }
              }
            },
            "else": {
              "actions": {}
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000027"
            }
          }
        }
      },
      "Caso_excluir": {
        "case": "excluir",
        "actions": {
          "Autorizar_excluir": {
            "type": "If",
            "expression": {
              "and": [
                {
                  "equals": [
                    "@not(or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Excluir'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Excluir'],'0'))),'true')))",
                    "@true"
                  ]
                }
              ]
            },
            "actions": {
              "Nega_perm_excluir": {
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
                  "operationMetadataId": "00000000-0000-0000-0000-000000000028"
                }
              },
              "Nega_perm_excluir_fim": {
                "type": "Terminate",
                "inputs": {
                  "runStatus": "Succeeded"
                },
                "runAfter": {
                  "Nega_perm_excluir": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000029"
                }
              }
            },
            "else": {
              "actions": {}
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000030"
            }
          }
        }
      }
    },
    "default": {
      "actions": {
        "Nega_acao": {
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
              "description": "@{concat('Ação desconhecida: ',toLower(trim(coalesce(triggerBody()['text'],''))),'.')}",
              "id": "",
              "url": ""
            }
          },
          "metadata": {
            "operationMetadataId": "00000000-0000-0000-0000-000000000031"
          }
        },
        "Nega_acao_fim": {
          "type": "Terminate",
          "inputs": {
            "runStatus": "Succeeded"
          },
          "runAfter": {
            "Nega_acao": [
              "Succeeded"
            ]
          },
          "metadata": {
            "operationMetadataId": "00000000-0000-0000-0000-000000000032"
          }
        }
      }
    },
    "runAfter": {
      "Se_chamador_desconhecido": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000033"
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
| `Caso_gravar`, `Caso_excluir` | nomes dos casos | `Caso_<acao>`: **nunca** igual ao nome de uma ação |
| `case` | `gravar`, `excluir` | valor da ação em minúsculas, igual ao que o app envia |
| `Autorizar_*`, `Nega_perm_*` | nomes | um par por caso; troque a flag |
| `default` | mensagem com o valor | mantenha: nunca cair calado num valor padrão |

## runAfter

Raiz depende de `Se_chamador_desconhecido`. Dentro de cada caso o primeiro nó não tem `runAfter`.

## Armadilhas

- O designer põe casos e ações no mesmo espaço de nomes: caso com o mesmo nome de uma ação derruba a colagem com `Required property 'case' not found` apontando para um caso que **tem** `case` (F008 acusa).
- Nome de ação duplicado em casos diferentes vira `_1` em silêncio e os tokens seguem no original: sufixe por ação (`_gravar`, `_excluir`).
- A ação vem do app: normalize com `toLower(trim())` e trate o `default` como erro de contrato, não como ação padrão.
- Cada caso autoriza a **própria** flag; copiar o `Autorizar` de outro caso sem trocar a coluna reabre o defeito do portão único.

## Variações

- Mais casos: duplique o par `Caso_*` e troque nomes, `case` e flag.
- Derivação de valor por tipo: aninhe com `derivar-valor-switch`, cada caso com `Compose` de nome próprio.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/switch-acao.json
```

Resultado esperado: `0 erro(s), 2 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Ler_chamador`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

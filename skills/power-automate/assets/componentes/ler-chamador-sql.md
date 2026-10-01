# Ler o chamador por procedure e negar desconhecido

> **Arquivo**: `ler-chamador-sql.json` · **Frequência**: comum · **Maturidade**: estável
> **Depende de**: `identificar-chamador`; conector SQL; `<procedure_obter_chamador>`

## Propósito

Cria o escopo `Try_pedido` (raiz do trabalho do flow), chama a procedure que devolve a linha do usuário já unida ao perfil e às flags, e nega com `Response` + `Terminate` quando não vem linha (usuário desconhecido ou inativo).

## Quando usar / quando não usar

**Usar**

- Flow cujo perfil mora em SQL.

**Não usar**

- Perfil em Dataverse: use `ler-chamador-dataverse`.
- Quando o chamador não precisa de perfil (flow aberto): não existe.

## Onde colar

Raiz do escopo do flow, depois de `Bloco_chamador`. Todos os componentes seguintes (switch, autorizar...) são colados **dentro** de `Try_pedido`.

## Entradas e saídas

**Lê**

- `outputs('Chamador')`.

**Expõe**

- `body('Ler_chamador')?['ResultSets']?['Table1']?[0]`: linha do chamador (flags `Flg_*`, `Id_Usuario`, unidade). Zero linha nega e termina.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Try_pedido`; o mesmo conteúdo está em `ler-chamador-sql.json`). GUIDs fictícios; conexões: `<prefixo>_sharedsql`.


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
            "server": "default",
            "database": "default",
            "procedure": "[dbo].[<procedure_obter_chamador>]",
            "parameters/Email_Chamador": "@outputs('Chamador')"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sql",
            "connection": "shared_sql",
            "operationId": "ExecuteProcedure_V2"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000008"
        }
      },
      "Se_chamador_desconhecido": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(coalesce(body('Ler_chamador')?['ResultSets']?['Table1'],json('[]')))",
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
              "operationMetadataId": "00000000-0000-0000-0000-000000000009"
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
              "operationMetadataId": "00000000-0000-0000-0000-000000000010"
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
          "operationMetadataId": "00000000-0000-0000-0000-000000000011"
        }
      }
    },
    "runAfter": {
      "Bloco_chamador": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000012"
    }
  },
  "allConnectionData": {
    "Ler_chamador": {
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
| `<procedure_obter_chamador>` | nome entre colchetes, `[dbo].[...]` | nome AS-BUILT da procedure no ambiente (skill `sql-procedures`); nunca o do documento |
| `parameters/Email_Chamador` | `@outputs('Chamador')` | nome real do parâmetro da procedure |
| `server` e `database` | `default` | mantenha: o servidor real vem da connection reference (R4) |
| `Try_pedido` | nome do escopo | `Try_<flow>`; o `Catch` aponta para ele |
| mensagem do `Nega_chamador` | frase genérica de perfil | a mesma frase de toda negação de perfil |

## runAfter

Raiz depende de `Bloco_chamador`. `Se_chamador_desconhecido` depende de `Ler_chamador`. O `Catch` (`catch-conector`) depende de `Try_pedido` com `Failed`, `TimedOut`, `Skipped`.

## Armadilhas

- A mensagem de negação é a mesma para usuário desconhecido e sem permissão: não revele qual dos dois.
- `bit` do SQL chega `true`/`false`, não `1`: as flags são lidas comparando o texto em minúsculas com `'1'` e `'true'` (ver `autorizar-por-flag`).
- Zero linha = negar. Nunca trate ausência de perfil como perfil padrão.
- Esta ação é a mais cara do flow em tempo: uma só leitura por execução, todas as flags de uma vez.

## Variações

- Leitura direto da tabela (`GetItems_V2`) quando não existe procedure: perde o join de perfil; faça a unidade e as flags em uma view.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/ler-chamador-sql.json
```

Resultado esperado: `0 erro(s), 1 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Chamador`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

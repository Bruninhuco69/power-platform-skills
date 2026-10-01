# Upsert de uma linha (N = 1)

> **Arquivo**: `upsert-unitario.json` · **Frequência**: rara · **Maturidade**: único
> **Depende de**: `mapear-lote`; `config-recebimento`; conector HTTP com Entra ID (`InvokeHttp`) e Dataverse

## Propósito

`Condicao_unitario` testa `length(body('Mapear_lote')) = 1`. No ramo `Sim`: consulta exata pela chave (`$top 1`, só o GUID), `PATCH` por id com `If-Match: *` quando existe, `POST` quando não existe. O ramo `Não` fica para o lote (índice + `$batch`).

## Quando usar / quando não usar

**Usar**

- Recebimento em que muitos envios trazem um registro.

**Não usar**

- Lote grande: o ramo `Não`.

## Onde colar

Dentro de `Escopo_Principal`, pendurado em `Resposta_sucesso`.

## Entradas e saídas

**Lê**

- `body('Mapear_lote')`, `CONFIG`.

**Expõe**

- Linha criada ou atualizada; nenhuma resposta (o 200 já foi dado).

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Condicao_unitario`; o mesmo conteúdo está em `upsert-unitario.json`). GUIDs fictícios; conexões: `<prefixo>_sharedcommondataserviceforapps`, `<prefixo>_sharedwebcontents`.


```json
{
  "nodeId": "Condicao_unitario",
  "serializedValue": {
    "type": "If",
    "expression": {
      "and": [
        {
          "equals": [
            "@length(body('Mapear_lote'))",
            1
          ]
        }
      ]
    },
    "actions": {
      "Buscar_existente": {
        "type": "OpenApiConnection",
        "description": "N=1: uma consulta exata pela chave de negócio, só o GUID.",
        "inputs": {
          "parameters": {
            "entityName": "@outputs('CONFIG')?['EntitySetName']",
            "$select": "@outputs('CONFIG')?['ColunaGuid']",
            "$filter": "@concat(outputs('CONFIG')?['ColunaChave1'],' eq ',string(first(body('Mapear_lote'))?[outputs('CONFIG')?['ColunaChave1']]),' and ',outputs('CONFIG')?['ColunaChave2'],' eq ''',replace(string(first(body('Mapear_lote'))?[outputs('CONFIG')?['ColunaChave2']]),'''',''''''),'''')",
            "$top": 1
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000155"
        }
      },
      "Se_existe": {
        "type": "If",
        "expression": {
          "and": [
            {
              "greater": [
                "@length(body('Buscar_existente')?['value'])",
                0
              ]
            }
          ]
        },
        "actions": {
          "Atualizar_unitario": {
            "type": "OpenApiConnection",
            "description": "PATCH por GUID; If-Match * = só atualiza, nunca cria.",
            "inputs": {
              "parameters": {
                "request/method": "PATCH",
                "request/url": "/api/data/v9.2/@{outputs('CONFIG')?['EntitySetName']}(@{first(body('Buscar_existente')?['value'])?[outputs('CONFIG')?['ColunaGuid']]})",
                "request/headers": {
                  "OData-MaxVersion": "4.0",
                  "OData-Version": "4.0",
                  "Accept": "application/json",
                  "Content-Type": "application/json",
                  "If-Match": "*"
                },
                "request/body": "@string(first(body('Mapear_lote')))"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_webcontents",
                "connection": "shared_webcontents",
                "operationId": "InvokeHttp"
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000156"
            }
          }
        },
        "else": {
          "actions": {
            "Criar_unitario": {
              "type": "OpenApiConnection",
              "inputs": {
                "parameters": {
                  "request/method": "POST",
                  "request/url": "/api/data/v9.2/@{outputs('CONFIG')?['EntitySetName']}",
                  "request/headers": {
                    "OData-MaxVersion": "4.0",
                    "OData-Version": "4.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                  },
                  "request/body": "@string(first(body('Mapear_lote')))"
                },
                "host": {
                  "apiId": "/providers/Microsoft.PowerApps/apis/shared_webcontents",
                  "connection": "shared_webcontents",
                  "operationId": "InvokeHttp"
                }
              },
              "metadata": {
                "operationMetadataId": "00000000-0000-0000-0000-000000000157"
              }
            }
          }
        },
        "runAfter": {
          "Buscar_existente": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000158"
        }
      }
    },
    "else": {
      "actions": {}
    },
    "runAfter": {
      "Bloco_mapeamento": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000159"
    }
  },
  "allConnectionData": {
    "Buscar_existente": {
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
    "Atualizar_unitario": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_webcontents"
        },
        "connection": {
          "id": "<prefixo>_sharedwebcontents"
        },
        "connectionName": "<prefixo>_sharedwebcontents"
      },
      "referenceKey": "shared_webcontents"
    },
    "Criar_unitario": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_webcontents"
        },
        "connection": {
          "id": "<prefixo>_sharedwebcontents"
        },
        "connectionName": "<prefixo>_sharedwebcontents"
      },
      "referenceKey": "shared_webcontents"
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
| `ColunaChave1`, `ColunaChave2` | chave composta no `CONFIG` | ajuste o `$filter` ao número de colunas de chave e ao tipo (texto entre aspas, número sem) |
| `/api/data/v9.2` | versão da API | a versão que o ambiente aceita |
| conexão `shared_webcontents` | `<prefixo>_sharedwebcontents` | conector HTTP com Entra ID do ambiente |

## runAfter

Raiz depende de `Mapear_lote`. Ao colar dentro do ramo, apague o `runAfter`.

## Armadilhas

- `If-Match: *` no `PATCH` impede **criar** (404 se não existe): só atualiza. `If-None-Match: *` seria o inverso.
- Valor de chave que vai para `$filter` leva apóstrofo duplicado.
- O ramo `Não` é onde cola `indice-chaves-destino` e `batch-upsert-changeset`; o `else` do envelope vem vazio.
- A consulta devolve 0 ou 1 linha; mais de uma indica chave de negócio não única: trate como erro de dado.

## Variações

- Com alternate key ativa na tabela: um `PATCH` direto na URL da chave, sem consulta prévia `[não verificado: sintaxe da URL com chave composta]`.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/upsert-unitario.json
```

Resultado esperado: `0 erro(s), 9 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `CONFIG`, `Mapear_lote`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

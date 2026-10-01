# Índice {chave -> GUID} da tabela destino

> **Arquivo**: `indice-chaves-destino.json` · **Frequência**: ocasional · **Maturidade**: estável
> **Depende de**: `mapear-lote`; `config-recebimento`; `paginacao-nativa` (a leitura já traz a paginação)

## Propósito

Calcula limites (`first(sort())`/`last(sort())`), monta o filtro, lê **só o intervalo** do lote na tabela destino com paginação nativa, constrói o objeto `{chave: linha}` e acrescenta `GuidKey` a cada linha do lote.

## Quando usar / quando não usar

**Usar**

- Lote com mais de uma linha e tabela destino sem alternate key.

**Não usar**

- N = 1: `upsert-unitario`.
- Tabela com alternate key: `PATCH` direto.

## Onde colar

Dentro de `Condicao_unitario`, no ramo `Não`, antes de `batch-upsert-changeset`.

## Entradas e saídas

**Lê**

- `body('Mapear_lote')`, `CONFIG`.

**Expõe**

- `body('Lote_com_guid')`: o lote com `GuidKey` (nulo = create).

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_indice`; o mesmo conteúdo está em `indice-chaves-destino.json`). GUIDs fictícios; conexões: `<prefixo>_sharedcommondataserviceforapps`.


```json
{
  "nodeId": "Bloco_indice",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Limites": {
        "type": "Compose",
        "description": "Substitui um Compose de mínimo e de máximo por chave.",
        "inputs": {
          "MinChave1": "@first(sort(body('Mapear_lote'),outputs('CONFIG')?['ColunaChave1']))?[outputs('CONFIG')?['ColunaChave1']]",
          "MaxChave1": "@last(sort(body('Mapear_lote'),outputs('CONFIG')?['ColunaChave1']))?[outputs('CONFIG')?['ColunaChave1']]",
          "MinChave2": "@first(sort(body('Mapear_lote'),outputs('CONFIG')?['ColunaChave2']))?[outputs('CONFIG')?['ColunaChave2']]",
          "MaxChave2": "@last(sort(body('Mapear_lote'),outputs('CONFIG')?['ColunaChave2']))?[outputs('CONFIG')?['ColunaChave2']]"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000160"
        }
      },
      "Clausulas_chave1": {
        "type": "Select",
        "inputs": {
          "from": "@body('Mapear_lote')",
          "select": "@concat(outputs('CONFIG')?['ColunaChave1'],' eq ',string(item()?[outputs('CONFIG')?['ColunaChave1']]))"
        },
        "runAfter": {
          "Limites": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000161"
        }
      },
      "Filtro_chave1": {
        "type": "Compose",
        "description": "Até 10 chaves: lista exata (sem repetidas). Acima disso: intervalo mínimo-máximo.",
        "inputs": "@if(greater(length(body('Mapear_lote')),10),concat(outputs('CONFIG')?['ColunaChave1'],' ge ',outputs('Limites')?['MinChave1'],' and ',outputs('CONFIG')?['ColunaChave1'],' le ',outputs('Limites')?['MaxChave1']),concat('(',join(union(body('Clausulas_chave1'),body('Clausulas_chave1')),' or '),')'))",
        "runAfter": {
          "Clausulas_chave1": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000162"
        }
      },
      "Ler_destino": {
        "type": "OpenApiConnection",
        "description": "Paginação nativa (Configurações > Paginação) traz todas as páginas em uma ação só.",
        "inputs": {
          "parameters": {
            "entityName": "@outputs('CONFIG')?['EntitySetName']",
            "$select": "@concat(outputs('CONFIG')?['ColunaGuid'],',',outputs('CONFIG')?['ColunaChave1'],',',outputs('CONFIG')?['ColunaChave2'])",
            "$filter": "@concat('(',outputs('Filtro_chave1'),') and ',outputs('CONFIG')?['ColunaChave2'],' ge ''',outputs('Limites')?['MinChave2'],''' and ',outputs('CONFIG')?['ColunaChave2'],' le ''',outputs('Limites')?['MaxChave2'],'''')"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "connection": "shared_commondataserviceforapps",
            "operationId": "ListRecords"
          }
        },
        "runtimeConfiguration": {
          "paginationPolicy": {
            "minimumItemCount": 100000
          }
        },
        "runAfter": {
          "Filtro_chave1": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000163"
        }
      },
      "Chaves_destino": {
        "type": "Select",
        "inputs": {
          "from": "@body('Ler_destino')?['value']",
          "select": {
            "@{outputs('CONFIG')?['ColunaGuid']}": "@item()?[outputs('CONFIG')?['ColunaGuid']]",
            "@{outputs('CONFIG')?['ColunaChave1']}": "@item()?[outputs('CONFIG')?['ColunaChave1']]",
            "@{outputs('CONFIG')?['ColunaChave2']}": "@item()?[outputs('CONFIG')?['ColunaChave2']]"
          }
        },
        "runAfter": {
          "Ler_destino": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000164"
        }
      },
      "Indice_chaves": {
        "type": "Select",
        "inputs": {
          "from": "@body('Chaves_destino')",
          "select": {
            "@{concat(string(item()?[outputs('CONFIG')?['ColunaChave1']]),string(item()?[outputs('CONFIG')?['ColunaChave2']]))}": "@item()"
          }
        },
        "runAfter": {
          "Chaves_destino": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000165"
        }
      },
      "Indice_objeto": {
        "type": "Compose",
        "description": "Objeto único {chave: linha}. Guardado para índice vazio (json('') estoura).",
        "inputs": "@json(if(empty(body('Indice_chaves')),'{}',replace(replace(replace(string(body('Indice_chaves')),'[',''),']',''),'},{',',')))",
        "runAfter": {
          "Indice_chaves": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000166"
        }
      },
      "Lote_com_guid": {
        "type": "Select",
        "description": "Acrescenta GuidKey a cada linha pelo índice. O sufixo Z iguala o formato de data dos dois lados.",
        "inputs": {
          "from": "@body('Mapear_lote')",
          "select": "@addProperty(item(),'GuidKey',outputs('Indice_objeto')?[concat(string(item()?[outputs('CONFIG')?['ColunaChave1']]),string(item()?[outputs('CONFIG')?['ColunaChave2']]),'Z')]?[outputs('CONFIG')?['ColunaGuid']])"
        },
        "runAfter": {
          "Indice_objeto": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000167"
        }
      }
    },
    "runAfter": {
      "Mapear_lote": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000168"
    }
  },
  "allConnectionData": {
    "Ler_destino": {
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
| `ColunaChave1`, `ColunaChave2` | chave composta do `CONFIG` | estenda os `Select` se houver mais colunas de chave |
| `10` | limite da lista exata | acima disso usa intervalo mínimo-máximo |
| `100000` | limite da paginação | tamanho máximo esperado da leitura |
| aspas em `ColunaChave2` | coluna como texto | tire as aspas se a coluna for Date/DateTime `[não verificado]` |

## runAfter

Raiz depende de `Mapear_lote`; os `Select` e `Compose` encadeiam.

## Armadilhas

- Indexe pela chave **concatenada** com o mesmo formato dos dois lados; o sufixo `Z` do lote iguala o formato de data devolvido pelo Dataverse. Sem isso nenhuma linha acha o id e tudo vira `create` duplicado.
- `replace` de `[`, `]` e `},{` para fundir os objetos num só quebra se algum dado tiver colchete: valide ou escape antes `[não verificado]`.
- Índice vazio: `json('')` estoura; o `Compose` devolve `{}` se `empty(body(...))`.
- Reduzir a leitura é o ganho: filtre pelo intervalo do lote em vez de ler a tabela inteira.
- Paginação por `Do_until` + skiptoken (versão antiga do projeto) é mais ações e mais falhas; a nativa traz tudo numa ação.

## Variações

- Chave de uma só coluna: `Select` e `concat` com um só termo.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/indice-chaves-destino.json
```

Resultado esperado: `0 erro(s), 20 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `CONFIG`, `Mapear_lote`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

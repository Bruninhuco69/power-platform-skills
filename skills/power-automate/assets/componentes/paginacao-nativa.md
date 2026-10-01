# Leitura paginada nativa (List rows)

> **Arquivo**: `paginacao-nativa.json` · **Frequência**: ocasional (nativa na maioria; `Do_until` só em flow antigo) · **Maturidade**: estável
> **Depende de**: `config`; conector Dataverse

## Propósito

`ListRecords` com `runtimeConfiguration.paginationPolicy.minimumItemCount` (Configurações > Paginação) traz todas as páginas numa ação, até o limite.

## Quando usar / quando não usar

**Usar**

- Leitura grande para índice, relatório ou exportação.

**Não usar**

- Leituras que cabem numa página (`$top`).

## Onde colar

Em qualquer escopo, no ponto da leitura.

## Entradas e saídas

**Lê**

- `$select`, `$filter`, `$orderby`.

**Expõe**

- `body('Ler_todos_pedidos')?['value']`: todas as linhas, e `outputs('Total_lidos')`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_paginacao`; o mesmo conteúdo está em `paginacao-nativa.json`). GUIDs fictícios; conexões: `<prefixo>_sharedcommondataserviceforapps`.


```json
{
  "nodeId": "Bloco_paginacao",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Ler_todos_pedidos": {
        "type": "OpenApiConnection",
        "description": "Configurações > Paginação: traz todas as páginas em uma ação, até o limite.",
        "inputs": {
          "parameters": {
            "entityName": "<prefixo>_pedidos",
            "$select": "<prefixo>_pedidoid,<prefixo>_numero",
            "$filter": "<prefixo>_ativo eq true",
            "$orderby": "<prefixo>_numero"
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
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000191"
        }
      },
      "Total_lidos": {
        "type": "Compose",
        "inputs": "@length(coalesce(body('Ler_todos_pedidos')?['value'],json('[]')))",
        "runAfter": {
          "Ler_todos_pedidos": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000192"
        }
      }
    },
    "runAfter": {
      "Bloco_config": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000193"
    }
  },
  "allConnectionData": {
    "Ler_todos_pedidos": {
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
| `<prefixo>_pedidos` | conjunto | AS-BUILT |
| `100000` | limite de itens | o teto esperado; a paginação para ao atingi-lo |
| `$select`, `$filter` | colunas e filtro | só as colunas necessárias; filtre pelo intervalo |

## runAfter

Raiz depende de `Bloco_config`.

## Armadilhas

- Sempre use `$select`: sem ele a leitura traz todas as colunas e estoura tempo e memória.
- Reduza a leitura pelo intervalo de chaves do lote, em vez de ler a tabela inteira.
- O limite é do conector, não do Dataverse: acima dele a leitura é cortada **sem erro**; compare `Total_lidos` com o esperado.
- Alternativa antiga: `Do_until` + `@odata.nextLink`/skiptoken em variável: mais ações, mais pontos de falha.

## Variações

- `Do_until` com skiptoken: só quando a paginação nativa não servir (`[não verificado]` neste catálogo, sem bloco).

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/paginacao-nativa.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

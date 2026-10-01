# CONFIG de recebimento em lote

> **Arquivo**: `config-recebimento.json` · **Frequência**: ocasional (só flow de recebimento); o papel de `config` é muito comum · **Maturidade**: estável
> **Depende de**: nenhum

## Propósito

O mesmo papel do `config`, com as chaves do lote. O nome continua `CONFIG`; nenhuma outra ação carrega literal de ambiente.

## Quando usar / quando não usar

**Usar**

- Flow HTTP que grava em Dataverse.

**Não usar**

- Flow chamado pelo app: use `config`.

## Onde colar

Dentro de `Escopo_Principal`, antes do mapeamento (ou na raiz, antes do escopo).

## Entradas e saídas

**Lê**

- Nada.

**Expõe**

- `EntitySetName`, `TamanhoLote`, `ColunaGuid`, `ColunaChave1`, `ColunaChave2`, `origemToken`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_config`; o mesmo conteúdo está em `config-recebimento.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_config",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "CONFIG": {
        "type": "Compose",
        "inputs": {
          "EntitySetName": "<prefixo>_pedidos",
          "TamanhoLote": 50,
          "ColunaGuid": "<prefixo>_pedidoid",
          "ColunaChave1": "<prefixo>_numero",
          "ColunaChave2": "<prefixo>_dataevento",
          "origemToken": "<origem-do-token>"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000003"
        }
      }
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000004"
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
| `EntitySetName` | `<prefixo>_pedidos` | **nome do conjunto** (plural), não o nome lógico; por variável de ambiente, não literal de teste |
| `TamanhoLote` | `50` | comece pequeno (por exemplo 10) e aumente até aparecer 429; máximo 1000 |
| `ColunaGuid` | `<prefixo>_pedidoid` | chave primária |
| `ColunaChave1`, `ColunaChave2` | chave de negócio | numérica e data/texto; ampliável |
| `origemToken` | `<origem-do-token>` | valor da coluna `name` da linha de cache |

## runAfter

Raiz depende de nada (primeira ação do escopo).

## Armadilhas

- `TableLogicalName` no projeto de referência era o nome do conjunto e continha `dev` literal: promover para produção virou editar o flow. Use variável de ambiente (F5).
- Variável de ambiente lida em `parameters()` é congelada até salvar ou religar o flow: serve para tabela, não para cache de token.
- Mais colunas de chave: acrescente `ColunaChave3`... e estenda o índice (`indice-chaves-destino`).

## Variações

- Upsert por alternate key: as colunas de chave viram a URL do `PATCH` e o índice some (ver a referência `dataverse-batch-upsert`).

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/config-recebimento.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

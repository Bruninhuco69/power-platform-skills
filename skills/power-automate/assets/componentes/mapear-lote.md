# Mapear o lote recebido (Select de mapeamento)

> **Arquivo**: `mapear-lote.json` · **Frequência**: ocasional · **Maturidade**: estável
> **Depende de**: `config-recebimento`; corpo `{ dados: [...] }`

## Propósito

Um `Select` com nome lógico à esquerda e valor à direita converte cada item do lote: sentinela de data nula, booleano em inteiro, número em texto-ou-nulo e texto numérico protegido.

## Quando usar / quando não usar

**Usar**

- Recebimento de lote de sistema externo.

**Não usar**

- Dois mapeamentos do mesmo lote (um para update, outro para create): é uma cópia só.

## Onde colar

Dentro de `Escopo_Principal`; sem `runAfter` do token (roda em paralelo com `Scope_Token`) ou depois de `CONFIG`.

## Entradas e saídas

**Lê**

- `triggerBody()?['dados']`: lista de registros do sistema de origem.

**Expõe**

- `body('Mapear_lote')`: lista de objetos prontos para o Dataverse.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_mapeamento`; o mesmo conteúdo está em `mapear-lote.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_mapeamento",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Mapear_lote": {
        "type": "Select",
        "description": "Única cópia do mapeamento: nome lógico à esquerda, valor à direita.",
        "inputs": {
          "from": "@coalesce(triggerBody()?['dados'],json('[]'))",
          "select": {
            "<prefixo>_numero": "@item()?['Num_Pedido']",
            "<prefixo>_descricao": "@item()?['Des_Pedido']",
            "<prefixo>_dataevento": "@if(equals(item()?['Dat_Evento'],'0001-01-01T00:00:00'),'1753-01-01T00:00:00Z',item()?['Dat_Evento'])",
            "<prefixo>_prazo": "@if(equals(item()?['Dat_Prazo'],'0001-01-01T00:00:00'),'1753-01-01T00:00:00Z',item()?['Dat_Prazo'])",
            "<prefixo>_ativo": "@if(equals(item()?['Flg_Ativo'],true),1,0)",
            "<prefixo>_codigo": "@if(equals(item()?['Cod_Item'],null),null,string(item()?['Cod_Item']))",
            "<prefixo>_rota": "@if(empty(trim(coalesce(item()?['Cod_Rota'],''))),0,int(trim(coalesce(item()?['Cod_Rota'],''))))"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000153"
        }
      }
    },
    "runAfter": {
      "Bloco_config": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000154"
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
| `Num_Pedido`, `Des_Pedido`... | campos de origem | nomes dos campos do contrato do chamador |
| `<prefixo>_numero`... | colunas de destino | nomes lógicos AS-BUILT |
| `0001-01-01T00:00:00` | data nula da origem | sentinela real do sistema de origem |
| `1753-01-01T00:00:00Z` | data mínima do destino | valor aceito pela coluna |

## runAfter

Raiz depende de `Bloco_config`.

## Armadilhas

- `if()` avalia os dois ramos: `trim(null)` estoura mesmo quando o ramo não é escolhido; `trim(coalesce(x,''))`.
- Número que o destino guarda como texto: `if(equals(x,null),null,string(x))` mantém nulo (`string(null)` seria `''`).
- Nome lógico no flow e em OData é o lógico, não o de exibição do Power Fx.
- A data tem de sair no **mesmo formato** nos dois lados do índice (`indice-chaves-destino`), senão tudo vira `create` duplicado.
- Lote de 1 e de N usam o mesmo mapeamento: o ramo unitário lê `first(body('Mapear_lote'))`.

## Variações

- Lista vinda de planilha: filtre linhas vazias antes do `Select`.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/mapear-lote.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

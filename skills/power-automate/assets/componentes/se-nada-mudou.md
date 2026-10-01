# Idempotência: nada mudou, avise e termine

> **Arquivo**: `se-nada-mudou.json` · **Frequência**: comum · **Maturidade**: estável
> **Depende de**: `estado-antes`; `normalizar-entrada`; `nega-resposta-terminate`

## Propósito

Compara o registro real com o normalizado e responde `warning` 'Nenhuma alteração a registrar.' com `Terminate`.

## Quando usar / quando não usar

**Usar**

- Edição e mudança de situação repetíveis.

**Não usar**

- Quando mesmo sem mudança o histórico deve registrar a tentativa.

## Onde colar

Dentro do `Caso_<acao>`, depois de `Bloco_validar` (ou da trilha).

## Entradas e saídas

**Lê**

- `body('Estado_antes_gravar')`, `outputs('Normalizar_gravar')`.

**Expõe**

- Resposta `warning` e fim, ou segue para a escrita.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Se_nada_mudou_gravar`; o mesmo conteúdo está em `se-nada-mudou.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Se_nada_mudou_gravar",
  "serializedValue": {
    "type": "If",
    "expression": {
      "and": [
        {
          "equals": [
            "@and(equals(trim(string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido'])),outputs('Normalizar_gravar')?['descricao']),equals(string(coalesce(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido'],0)),string(outputs('Normalizar_gravar')?['quantidade'])))",
            "@true"
          ]
        }
      ]
    },
    "actions": {
      "Avisa_nada_mudou": {
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
            "status": "warning",
            "description": "Nenhuma alteração a registrar.",
            "id": "@{outputs('Normalizar_gravar')?['id']}",
            "url": ""
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000069"
        }
      },
      "Avisa_nada_mudou_fim": {
        "type": "Terminate",
        "inputs": {
          "runStatus": "Succeeded"
        },
        "runAfter": {
          "Avisa_nada_mudou": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000070"
        }
      }
    },
    "else": {
      "actions": {}
    },
    "runAfter": {
      "Bloco_validar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000071"
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
| `Des_Pedido`, `Qtd_Pedido` | colunas comparadas | as colunas editáveis do seu registro |
| mensagem | `Nenhuma alteração a registrar.` | frase do projeto |

## runAfter

Raiz depende de `Bloco_validar`. Com `trilha-de-auditoria`, aponte para `Bloco_trilha`.

## Armadilhas

- `warning` fecha o modal no app (sucesso é `status <> 'error'`); use `warning`, não `success`, para o usuário ver que nada foi gravado.
- Idempotência decidida **no flow**: a procedure pode devolver `warning` por outro motivo (ex.: usuário recém-criado nasce já ativo). Pare só em `error` depois da escrita.
- Compare texto normalizado com texto normalizado (`trim`, caixa) para não acusar mudança que o usuário não fez.
- `string(coalesce(x,0))` (coalesce dentro de `string`) para comparar número que pode vir nulo.

## Variações

- Com a trilha: `equals(outputs('Trilha_gravar_campos'), 0)` mais a comparação do campo que a trilha não audita (ex.: observação).
- Mudança de situação (conceder/revogar): compare o estado desejado com o atual; ver `email-suporte-com-parcial`.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/se-nada-mudou.json
```

Resultado esperado: `0 erro(s), 3 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Estado_antes_gravar`, `Normalizar_gravar`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

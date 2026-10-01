# Catch: falha de conector vira mensagem

> **Arquivo**: `catch-conector.json` · **Frequência**: comum · **Maturidade**: estável
> **Depende de**: `ler-chamador-sql` (cria `Try_pedido`); `nega-resposta-terminate`

## Propósito

`Catch_pedido` escuta `Failed`, `TimedOut` **e** `Skipped` de `Try_pedido` e responde com mensagem de infraestrutura + código da execução, depois termina.

## Quando usar / quando não usar

**Usar**

- Todo flow chamado pelo app.

**Não usar**

- Dentro do `Try`: o `Catch` é irmão dele.

## Onde colar

Raiz do escopo do flow, depois de `Try_pedido`.

## Entradas e saídas

**Lê**

- Status de `Try_pedido`; `workflow()?['run']?['name']`.

**Expõe**

- Resposta `error` com o código da execução; fim.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Catch_pedido`; o mesmo conteúdo está em `catch-conector.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Catch_pedido",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Nega_conector": {
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
            "description": "@{concat('O sistema não respondeu. Tente de novo em instantes. Código: ',workflow()?['run']?['name'])}",
            "id": "",
            "url": ""
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000084"
        }
      },
      "Nega_conector_fim": {
        "type": "Terminate",
        "inputs": {
          "runStatus": "Succeeded"
        },
        "runAfter": {
          "Nega_conector": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000085"
        }
      }
    },
    "runAfter": {
      "Try_pedido": [
        "Failed",
        "TimedOut",
        "Skipped"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000086"
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
| `Try_pedido` | nome do Try | `Try_<flow>` |
| frase | o sistema não respondeu | frase do projeto; o código da execução fica no fim |

## runAfter

Raiz depende de `Try_pedido` com `Failed`, `TimedOut`, `Skipped`.

## Armadilhas

- `CONFIG`, `Perfil_do_chamador` e `Chamador` são irmãos do `Try`: se o conector de perfil cair, o `Try` fica `Skipped`, e um `Catch` só com `Failed` também fica `Skipped`: execução sem `Response` e o app espera o timeout (F009 acusa).
- A frase não promete 'nada foi alterado': uma falha depois da escrita deixaria a promessa falsa. Use texto neutro e o código da execução.
- O código vem em `workflow()['run']['name']`: o usuário o cola no chamado e o suporte acha a execução. Só em erro de infraestrutura, não em negação de negócio.
- `result('Try_pedido')` só devolve ações de primeiro nível; para o texto do erro use um filtro por `status = 'Failed'` (ver `log-execucao`).
- Exceção legítima ao `Skipped`: ação de absorção (gravar cache que não pode derrubar o fluxo) — documente na descrição.

## Variações

- Flow com escrita parcial possível: use `email-suporte-com-parcial` ou `compensacao-dataverse` em vez de prometer 'nada foi feito'.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/catch-conector.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

# Traduzir código em mensagem e responder (4 campos)

> **Arquivo**: `traduzir-codigo-e-responder.json` · **Frequência**: muito comum · **Maturidade**: estável na forma; mapa por objeto [não verificado]
> **Depende de**: `gravar-via-procedure`; `nega-resposta-terminate` (mesmo contrato)

## Propósito

Um `Compose` com o mapa `código -> {status, description}` e um `Response` de 4 campos que consulta o mapa pelo código e cai em `error` com 'Resposta inesperada do sistema: <código>.' quando o código não existe.

## Quando usar / quando não usar

**Usar**

- Resposta de sucesso/aviso/erro de uma escrita.

**Não usar**

- Negações antes da escrita: `nega-resposta-terminate`.

## Onde colar

Dentro do `Caso_<acao>`, depois de `Bloco_gravar`. Último nó do caso (não precisa de `Terminate`).

## Entradas e saídas

**Lê**

- `outputs('Codigo_gravar')`, `body('Gravar_pedido')`.

**Expõe**

- Resposta `{status, description, id, url}`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_responder`; o mesmo conteúdo está em `traduzir-codigo-e-responder.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_responder",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Mensagens_gravar": {
        "type": "Compose",
        "inputs": {
          "GRAVADO": {
            "status": "success",
            "description": "Pedido gravado."
          },
          "NAO_APLICADO": {
            "status": "warning",
            "description": "Nada foi alterado."
          },
          "DUPLICADO": {
            "status": "warning",
            "description": "Já existe um pedido com este número."
          },
          "NAO_ENCONTRADO": {
            "status": "error",
            "description": "Pedido não encontrado."
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000081"
        }
      },
      "Responder_gravar": {
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
            "status": "@{coalesce(outputs('Mensagens_gravar')?[outputs('Codigo_gravar')]?['status'],'error')}",
            "description": "@{coalesce(outputs('Mensagens_gravar')?[outputs('Codigo_gravar')]?['description'],concat('Resposta inesperada do sistema: ',outputs('Codigo_gravar'),'.'))}",
            "id": "@{coalesce(body('Gravar_pedido')?['ResultSets']?['Table1']?[0]?['id'],'')}",
            "url": ""
          }
        },
        "runAfter": {
          "Mensagens_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000082"
        }
      }
    },
    "runAfter": {
      "Bloco_gravar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000083"
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
| `GRAVADO`, `NAO_APLICADO`, `DUPLICADO`, `NAO_ENCONTRADO` | vocabulário de códigos | o vocabulário **fechado** da procedure; um código novo exige linha nova |
| frases | texto pt-BR | frases prontas para o usuário |
| `id` | `...?['id']` | `id` devolvido pela procedure (texto) |

## runAfter

Raiz depende de `Bloco_gravar`; o `Response` depende de `Mensagens_gravar`.

## Armadilhas

- No projeto de referência a tradução era uma cadeia de `if(equals(...))` com 16 códigos repetida em `status` e em `description`: perto do limite de 8.192 caracteres. O mapa por objeto lê o código **uma vez** (`Codigo_*`) e cada código é uma linha. Acesso por chave dinâmica `outputs('Mapa')?[chave]` foi usado no flow de recebimento; neste uso o formato é `[não verificado]`.
- O mesmo código pode precisar de `status` diferente por ação; mantenha um mapa por flow, não um global.
- Um `description` sem mapa (`''`) cai em 'Resposta inesperada': melhor ver o código no app do que mensagem vazia.
- Nunca devolva o texto de exceção do conector ao usuário.

## Variações

- Código que muda o texto com número (campos alterados): `concat(string(length(body('Trilha_gravar'))), ' campo(s) alterado(s).')` no `description`; lembre `body()` e não `outputs()`.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/traduzir-codigo-e-responder.json
```

Resultado esperado: `0 erro(s), 3 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Codigo_gravar`, `Gravar_pedido`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

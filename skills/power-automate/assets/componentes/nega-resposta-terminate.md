# Nega: Response de 4 campos + Terminate

> **Arquivo**: `nega-resposta-terminate.json` · **Frequência**: muito comum (vários pares por flow) · **Maturidade**: estável
> **Depende de**: nenhum

## Propósito

O par `Nega_<motivo>` (`Response` para o Power Apps com `status`, `description`, `id`, `url`) e `Nega_<motivo>_fim` (`Terminate` com `Succeeded`). `Response` não encerra o flow: sem o `Terminate` o próximo nó roda com a resposta já enviada.

## Quando usar / quando não usar

**Usar**

- Dentro do ramo `Sim` de qualquer `If` que nega (perfil, validação, escopo, idempotência).

**Não usar**

- Resposta de sucesso final do flow: o último `Response` não precisa de `Terminate` (nada vem depois dele).
- Flow de recebimento HTTP: o contrato é outro (`kind: Http`, código HTTP real).

## Onde colar

Dentro de `actions` de um `If` ou de um `Caso`. Este envelope é só o par; cole-o no ramo e renomeie `motivo`.

## Entradas e saídas

**Lê**

- Texto da mensagem (`description`) e, quando houver, `id` e `url`.

**Expõe**

- Resposta `{status, description, id, url}` (texto) e fim da execução com `Succeeded`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_nega`; o mesmo conteúdo está em `nega-resposta-terminate.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_nega",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Nega_motivo": {
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
          "operationMetadataId": "00000000-0000-0000-0000-000000000019"
        }
      },
      "Nega_motivo_fim": {
        "type": "Terminate",
        "inputs": {
          "runStatus": "Succeeded"
        },
        "runAfter": {
          "Nega_motivo": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000020"
        }
      }
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000021"
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
| `Nega_motivo`, `Nega_motivo_fim` | nomes das duas ações | `Nega_<motivo>`: único no flow inteiro (F004) |
| `status` | `error` | `success`, `warning` ou `error` |
| `description` | frase de perfil | frase pronta para o usuário, montada no flow |
| `statusCode` | `200` | mantenha 200: o app lê `status`, não o código HTTP |

## runAfter

Primeira ação do ramo sem `runAfter`; o `Terminate` depende do `Response` com `Succeeded`.

## Armadilhas

- `Response` sem `Terminate` responde duas vezes e continua gravando (F015 acusa).
- Os 4 campos saem sempre, mesmo vazios; faltando um, a tela lê `ret.url` num flow que não exporta (F010 acusa).
- `Terminate` com `Succeeded`: a negação é resposta normal. Para o histórico marcar falha, use o `Falhar_execucao` do `log-execucao`.
- Mensagem de negação não diz a unidade nem o nome do registro alheio: responderia a quem sonda.

## Variações

- Erro de infraestrutura: acrescente o id da execução à frase, `concat('... Código: ', workflow()?['run']?['name'])`, para o suporte achar a execução (ver `catch-conector`).

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/nega-resposta-terminate.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

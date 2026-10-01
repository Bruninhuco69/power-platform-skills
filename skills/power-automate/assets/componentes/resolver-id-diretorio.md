# Resolver o id no diretório quando o app não mandou

> **Arquivo**: `resolver-id-diretorio.json` · **Frequência**: ocasional · **Maturidade**: desenhado [não verificado]: gerado, nunca devolvido pelo designer
> **Depende de**: `validar-com-mensagem`; conector de usuários do Office 365

## Propósito

Se o parâmetro de id veio vazio, consulta `UserProfile_V2` pelo e-mail; `Id_diretorio_final` fica com o id devolvido ou com `(não resolvido)`. A falha da consulta não derruba o flow: o pedido sai mesmo assim.

## Quando usar / quando não usar

**Usar**

- Pedido de acesso por e-mail ao suporte, antes de `email-suporte-com-parcial`.

**Não usar**

- Quando o id é obrigatório: valide e negue.

## Onde colar

Dentro do `Try_pedido`, depois de `Bloco_validar`.

## Entradas e saídas

**Lê**

- `text_1` (e-mail do alvo) e `text_2` (id opcional).

**Expõe**

- `outputs('Id_diretorio_final')`: id ou `(não resolvido)`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_resolver_id`; o mesmo conteúdo está em `resolver-id-diretorio.json`). GUIDs fictícios; conexões: `<prefixo>_sharedoffice365users`.


```json
{
  "nodeId": "Bloco_resolver_id",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Se_id_diretorio_vazio": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@empty(trim(coalesce(triggerBody()['text_2'],'')))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Obter_perfil_do_alvo": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "userId": "@toLower(trim(coalesce(triggerBody()['text_1'],'')))"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365users",
                "connection": "shared_office365users",
                "operationId": "UserProfile_V2"
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000098"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000099"
        }
      },
      "Id_diretorio_final": {
        "type": "Compose",
        "inputs": "@if(empty(trim(coalesce(triggerBody()['text_2'],''))),coalesce(body('Obter_perfil_do_alvo')?['id'],'(não resolvido)'),trim(coalesce(triggerBody()['text_2'],'')))",
        "runAfter": {
          "Se_id_diretorio_vazio": [
            "Succeeded",
            "Failed",
            "Skipped",
            "TimedOut"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000100"
        }
      }
    },
    "runAfter": {
      "Bloco_validar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000101"
    }
  },
  "allConnectionData": {
    "Obter_perfil_do_alvo": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_office365users"
        },
        "connection": {
          "id": "<prefixo>_sharedoffice365users"
        },
        "connectionName": "<prefixo>_sharedoffice365users"
      },
      "referenceKey": "shared_office365users"
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
| `text_1`, `text_2` | e-mail do alvo e id | posições do contrato do trigger |
| `(não resolvido)` | marcador | o texto que o suporte reconhece; vira `''` ao gravar |

## runAfter

Raiz depende de `Bloco_validar`; `Id_diretorio_final` depende de `Se_id_diretorio_vazio` em todos os estados.

## Armadilhas

- `Id_diretorio_final` roda em `Succeeded, Failed, Skipped, TimedOut`: é absorção deliberada. Se a consulta falhar, o `Try` fica `Failed` mesmo assim; use `Terminate` antes do `Catch` ou aceite o `Catch`.
- Ler `body('Obter_perfil_do_alvo')` quando a ação não executou depende de o designer devolver nulo `[não verificado]`.
- O marcador `(não resolvido)` não pode ir para a base: converta para `''`.

## Variações

- Id obrigatório: troque a absorção por `Nega_` e `Terminate` quando a consulta falhar.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/resolver-id-diretorio.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

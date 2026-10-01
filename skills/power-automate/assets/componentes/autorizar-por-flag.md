# Autorizar por flag da própria ação

> **Arquivo**: `autorizar-por-flag.json` · **Frequência**: muito comum · **Maturidade**: estável
> **Depende de**: `ler-chamador-sql` (ou `-dataverse`); `nega-resposta-terminate`

## Propósito

Um `If` que nega (par `Nega_perm_<acao>`) quando a flag da ação não está ligada no perfil. A leitura do `bit` aceita `1` e `true`; coluna ausente nega.

## Quando usar / quando não usar

**Usar**

- Toda ação que escreve ou exporta, uma vez por `Caso_<acao>`.
- Flow de ação única (sem `Switch`): logo depois de `Se_chamador_desconhecido`.

**Não usar**

- Como portão único antes do `Switch`: ele só sabe se o perfil tem alguma permissão, não qual ramo vai rodar. Um perfil que cadastra passou a dar baixa irreversível.

## Onde colar

Primeira ação de cada `Caso_<acao>`; ou, em flow de ação única, depois de `Se_chamador_desconhecido` dentro de `Try_pedido`. Dentro de um `Caso` o primeiro nó não tem `runAfter`: apague a chave `runAfter` do nó raiz antes de colar.

## Entradas e saídas

**Lê**

- Linha do chamador (`body('Ler_chamador')`).

**Expõe**

- Nenhuma: nega e termina, ou segue.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Autorizar_gravar`; o mesmo conteúdo está em `autorizar-por-flag.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Autorizar_gravar",
  "serializedValue": {
    "type": "If",
    "expression": {
      "and": [
        {
          "equals": [
            "@not(or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'true')))",
            "@true"
          ]
        }
      ]
    },
    "actions": {
      "Nega_perm_gravar": {
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
          "operationMetadataId": "00000000-0000-0000-0000-000000000022"
        }
      },
      "Nega_perm_gravar_fim": {
        "type": "Terminate",
        "inputs": {
          "runStatus": "Succeeded"
        },
        "runAfter": {
          "Nega_perm_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000023"
        }
      }
    },
    "else": {
      "actions": {}
    },
    "runAfter": {
      "Se_chamador_desconhecido": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000024"
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
| `Autorizar_gravar`, `Nega_perm_gravar` | nomes | `Autorizar_<acao>` e `Nega_perm_<acao>`, únicos no flow |
| `Flg_Gravar` | coluna de flag da ação | coluna AS-BUILT da flag desta ação |
| frase | negação de perfil | mesma frase em todo o projeto |

## runAfter

Em flow de ação única depende de `Se_chamador_desconhecido`. Dentro do `Caso`, nenhum.

## Armadilhas

- `bit` chega `true`/`false`: `equals(true, 1)` é falso. A expressão compara o texto em minúsculas com `'1'` e `'true'`.
- Comparar `toLower(string(x))` com o booleano `true` (sem aspas) é sempre falso e inverte a regra.
- `coalesce` fica **dentro** do `string()` (`string(coalesce(x,'0'))`), o inverso do que vale para `int()`.
- Flag de permissão nasce desligada no perfil: ninguém ganha permissão por omissão.

## Variações

- Perfil em Dataverse: troque a expressão por `equals(first(body('Ler_perfil')?['value'])?['<prefixo>_podegravar'],true)` (ver `ler-chamador-dataverse`).

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/autorizar-por-flag.json
```

Resultado esperado: `0 erro(s), 1 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Ler_chamador`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

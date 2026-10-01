# Escopo por unidade (trilha SQL)

> **Arquivo**: `escopo-unidade.json` · **Frequência**: comum · **Maturidade**: estável
> **Depende de**: `config` (`cfgEscopoUnidade`); `estado-antes`; `ler-chamador-sql`

## Propósito

Um `Compose` booleano `Escopo_ok_gravar` e um `If` que nega. Passa quem tem a flag de todas as unidades, ou quem tem a mesma unidade do registro real **e** o registro tem unidade. Interruptor desligado libera.

## Quando usar / quando não usar

**Usar**

- Ação sobre registro existente em sistema com escopo por unidade.

**Não usar**

- Como substituto do filtro da galeria: o filtro do app é UX; só o flow barra.
- Cadastro sem registro prévio: compare `outputs('Normalizar_gravar')?['unidade']`.

## Onde colar

Dentro do `Caso_<acao>`, depois de `Bloco_estado_antes`.

## Entradas e saídas

**Lê**

- `CONFIG.cfgEscopoUnidade`, flag `Flg_TodasUnidades` e unidade do chamador, unidade do registro real.

**Expõe**

- `outputs('Escopo_ok_gravar')` (booleano); nega com `Nega_escopo_gravar`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_escopo_unidade`; o mesmo conteúdo está em `escopo-unidade.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_escopo_unidade",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Escopo_ok_gravar": {
        "type": "Compose",
        "inputs": "@or(equals(outputs('CONFIG')?['cfgEscopoUnidade'],false),or(or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_TodasUnidades'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_TodasUnidades'],'0'))),'true')),and(not(empty(toUpper(trim(coalesce(first(body('Estado_antes_gravar')?['value'])?['Nom_Unidade'],''))))),equals(toUpper(trim(coalesce(first(body('Estado_antes_gravar')?['value'])?['Nom_Unidade'],''))),toUpper(trim(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Nom_Unidade'],'')))))))",
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000041"
        }
      },
      "Se_fora_do_escopo_gravar": {
        "type": "If",
        "expression": {
          "and": [
            {
              "equals": [
                "@not(outputs('Escopo_ok_gravar'))",
                "@true"
              ]
            }
          ]
        },
        "actions": {
          "Nega_escopo_gravar": {
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
                "description": "Você não tem acesso a esta unidade.",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000042"
            }
          },
          "Nega_escopo_gravar_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_escopo_gravar": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000043"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Escopo_ok_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000044"
        }
      }
    },
    "runAfter": {
      "Bloco_estado_antes": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000045"
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
| `Flg_TodasUnidades` | flag do perfil global | coluna AS-BUILT |
| `Nom_Unidade` | unidade no registro e no chamador | colunas AS-BUILT |
| `cfgEscopoUnidade` | chave do `CONFIG` | mantenha ligada |

## runAfter

Raiz depende de `Bloco_estado_antes`; o `If` depende de `Escopo_ok_gravar`.

## Armadilhas

- Interruptor ausente lê `null`: `equals(chave, false)` só libera com `false` explícito (fail-closed).
- Unidade vazia no registro **barra** quem não é global; dado faltante virando curinga é o oposto de escopo.
- Perfil global é o primeiro termo do `or`: quem vê tudo não precisa de vínculo. Não conte com curto-circuito para proteger os outros termos: cada um já é válido sozinho (`coalesce`, `?[]`).
- A mensagem não diz a unidade do registro.
- Um projeto entregou o escopo como flag desligada: qualquer perfil gravou em qualquer unidade.

## Variações

- Dataverse: `escopo-unidades-dataverse` (várias unidades por usuário).
- Em vez de bloco separado, a regra pode entrar como primeira cláusula do `Validar_*`; fica menos uma ação, mas a mensagem some do meio da cadeia.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/escopo-unidade.json
```

Resultado esperado: `0 erro(s), 3 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `CONFIG`, `Estado_antes_gravar`, `Ler_chamador`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

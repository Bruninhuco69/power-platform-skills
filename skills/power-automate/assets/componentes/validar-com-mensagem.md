# Validar com a primeira mensagem de erro

> **Arquivo**: `validar-com-mensagem.json` · **Frequência**: comum · **Maturidade**: estável
> **Depende de**: `normalizar-entrada`; `nega-resposta-terminate`

## Propósito

`Validar_gravar` é um `Compose` com cadeia de `if()` que devolve a primeira mensagem aplicável ou `''`; `Se_invalido_gravar` nega com essa mensagem. Uma expressão, uma mensagem, testável sem executar a escrita.

## Quando usar / quando não usar

**Usar**

- Antes de toda escrita ou exportação.

**Não usar**

- Para checar permissão ou escopo (negam com mensagem própria, antes).

## Onde colar

Dentro do `Caso_<acao>`, depois do escopo.

## Entradas e saídas

**Lê**

- `outputs('Normalizar_gravar')`, registros lidos antes.

**Expõe**

- `outputs('Validar_gravar')`: texto, vazio quando válido.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_validar`; o mesmo conteúdo está em `validar-com-mensagem.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_validar",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Validar_gravar": {
        "type": "Compose",
        "inputs": "@if(empty(outputs('Normalizar_gravar')?['descricao']),'Informe a descrição.',if(less(outputs('Normalizar_gravar')?['quantidade'],1),'Informe uma quantidade maior que zero.',''))",
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000057"
        }
      },
      "Se_invalido_gravar": {
        "type": "If",
        "expression": {
          "and": [
            {
              "greater": [
                "@length(outputs('Validar_gravar'))",
                0
              ]
            }
          ]
        },
        "actions": {
          "Nega_gravar": {
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
                "description": "@{outputs('Validar_gravar')}",
                "id": "",
                "url": ""
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000058"
            }
          },
          "Nega_gravar_fim": {
            "type": "Terminate",
            "inputs": {
              "runStatus": "Succeeded"
            },
            "runAfter": {
              "Nega_gravar": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000059"
            }
          }
        },
        "else": {
          "actions": {}
        },
        "runAfter": {
          "Validar_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000060"
        }
      }
    },
    "runAfter": {
      "Bloco_escopo_unidade": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000061"
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
| mensagens | `Informe a descrição.` e `Informe uma quantidade maior que zero.` | regras e frases do seu domínio |
| `Validar_gravar`, `Se_invalido_gravar` | nomes | sufixo da ação |

## runAfter

Raiz depende de `Bloco_escopo_unidade`; `Se_invalido_gravar` depende de `Validar_gravar`.

## Armadilhas

- Mensagem em português **sem aspas** dentro de `if()` fez nenhum dos flows salvar (`InvalidTemplate`): texto fixo entre aspas simples; apóstrofo duplicado.
- Valor dentro da mensagem usa `concat('texto ', valor, '.')`, nunca `@{}` dentro de literal de `if()`.
- A cadeia **cresce** a cada regra: o limite é 8.192 caracteres por expressão e o designer recusa com 'expressões inválidas', sem falar em tamanho. O verificador avisa acima de 80% (F013).
- Cada ramo do `if()` é avaliado: a regra seguinte não pode depender de a anterior ter passado.

## Variações

- Cadeia longa demais: divida em dois `Compose` (`Validar_a`, `Validar_b`) e junte com `coalesce` das mensagens não vazias.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/validar-com-mensagem.json
```

Resultado esperado: `0 erro(s), 1 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Normalizar_gravar`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

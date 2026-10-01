# Trilha de auditoria campo a campo

> **Arquivo**: `trilha-de-auditoria.json` · **Frequência**: ocasional · **Maturidade**: único: só o gabarito de um flow foi devolvido pelo designer
> **Depende de**: `estado-antes`; `normalizar-entrada`

## Propósito

Um `Compose` por campo compara valor anterior e novo e marca `incluir`. `Query` fica com os alterados, `Select` projeta as colunas do histórico e `Trilha_gravar_campos` conta. O resultado vai para a procedure.

## Quando usar / quando não usar

**Usar**

- Edição com histórico por campo.

**Não usar**

- Cadastro (não há valor anterior).

## Onde colar

Dentro do `Caso_<acao>`, depois da validação e antes de `se-nada-mudou` e `gravar-via-procedure`.

## Entradas e saídas

**Lê**

- `body('Estado_antes_gravar')`, `outputs('Normalizar_gravar')`.

**Expõe**

- `body('Trilha_gravar')` (lista para a procedure: `@string(body('Trilha_gravar'))`) e `outputs('Trilha_gravar_campos')` (número).

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_trilha`; o mesmo conteúdo está em `trilha-de-auditoria.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_trilha",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Linha_gravar_01": {
        "type": "Compose",
        "inputs": {
          "ordem": "1",
          "tp_evento": "EDICAO",
          "campo": "Des_Pedido",
          "valor_anterior": "@take(if(empty(string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido'])),'(vazio)',string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido'])),200)",
          "valor_novo": "@take(if(empty(string(outputs('Normalizar_gravar')?['descricao'])),'(vazio)',string(outputs('Normalizar_gravar')?['descricao'])),200)",
          "resumo": "@take(concat('Des_Pedido alterado de ''',take(if(empty(string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido'])),'(vazio)',string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido'])),200),''' para ''',take(if(empty(string(outputs('Normalizar_gravar')?['descricao'])),'(vazio)',string(outputs('Normalizar_gravar')?['descricao'])),200),''''),400)",
          "incluir": "@if(equals(string(first(body('Estado_antes_gravar')?['value'])?['Des_Pedido']),string(outputs('Normalizar_gravar')?['descricao'])),'0','1')"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000062"
        }
      },
      "Linha_gravar_02": {
        "type": "Compose",
        "inputs": {
          "ordem": "2",
          "tp_evento": "EDICAO",
          "campo": "Qtd_Pedido",
          "valor_anterior": "@take(if(empty(string(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido'])),'(vazio)',string(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido'])),200)",
          "valor_novo": "@take(if(empty(string(outputs('Normalizar_gravar')?['quantidade'])),'(vazio)',string(outputs('Normalizar_gravar')?['quantidade'])),200)",
          "resumo": "@take(concat('Qtd_Pedido alterado de ''',take(if(empty(string(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido'])),'(vazio)',string(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido'])),200),''' para ''',take(if(empty(string(outputs('Normalizar_gravar')?['quantidade'])),'(vazio)',string(outputs('Normalizar_gravar')?['quantidade'])),200),''''),400)",
          "incluir": "@if(equals(string(first(body('Estado_antes_gravar')?['value'])?['Qtd_Pedido']),string(outputs('Normalizar_gravar')?['quantidade'])),'0','1')"
        },
        "runAfter": {
          "Linha_gravar_01": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000063"
        }
      },
      "Trilha_gravar_todas": {
        "type": "Compose",
        "inputs": "@createArray(outputs('Linha_gravar_01'),outputs('Linha_gravar_02'))",
        "runAfter": {
          "Linha_gravar_02": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000064"
        }
      },
      "Trilha_gravar_ativas": {
        "type": "Query",
        "inputs": {
          "from": "@outputs('Trilha_gravar_todas')",
          "where": "@equals(item()?['incluir'],'1')"
        },
        "runAfter": {
          "Trilha_gravar_todas": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000065"
        }
      },
      "Trilha_gravar": {
        "type": "Select",
        "inputs": {
          "from": "@body('Trilha_gravar_ativas')",
          "select": {
            "ordem": "@item()?['ordem']",
            "tp_evento": "@item()?['tp_evento']",
            "campo": "@item()?['campo']",
            "valor_anterior": "@item()?['valor_anterior']",
            "valor_novo": "@item()?['valor_novo']",
            "resumo": "@item()?['resumo']"
          }
        },
        "runAfter": {
          "Trilha_gravar_ativas": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000066"
        }
      },
      "Trilha_gravar_campos": {
        "type": "Compose",
        "inputs": "@length(body('Trilha_gravar_ativas'))",
        "runAfter": {
          "Trilha_gravar": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000067"
        }
      }
    },
    "runAfter": {
      "Bloco_validar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000068"
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
| `Linha_gravar_01`, `_02` | dois campos de exemplo | um `Compose` por campo auditado: duplique e troque campo, coluna e valor novo |
| `Trilha_gravar_todas` | `createArray` com as duas linhas | inclua todas as linhas |
| `take(..., 200)` e `400` | tamanhos de valor e resumo | tamanho das colunas do histórico |
| `tp_evento` | `EDICAO` | vocabulário de eventos do projeto (inteiro de Choice: leia do ambiente, não suponha) |

## runAfter

Raiz depende de `Bloco_validar`; `Linha_*` encadeiam entre si; o resto encadeia em ordem.

## Armadilhas

- `outputs('Trilha')` de um `Select` devolve o envelope: `outputs('Trilha')?['campos']` dá `null`, `string(null)` dá `''` e a resposta sai ' campo(s) alterado(s).' sem número e sem erro. Use `body()` e `length()` (F011).
- Valor vazio vira `(vazio)` nos dois lados para a comparação não depender de nulo x texto.
- Valores de Choice como inteiro nunca lidos do ambiente gravam sem erro com o rótulo trocado.
- Cada linha repete a expressão do valor: o limite de 8.192 caracteres é por expressão; mantenha uma ação por campo.

## Variações

- Dataverse: em vez de `Select` + procedure, um `CreateRecord` de histórico por campo dentro de `If` de mudança (forma usada na trilha Dataverse: mais ações, mais pontos de falha).

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/trilha-de-auditoria.json
```

Resultado esperado: `0 erro(s), 12 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Estado_antes_gravar`, `Normalizar_gravar`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

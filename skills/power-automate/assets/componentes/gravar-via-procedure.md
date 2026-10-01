# Gravar por procedure e ler o retorno de uma linha

> **Arquivo**: `gravar-via-procedure.json` · **Frequência**: comum · **Maturidade**: estável
> **Depende de**: `normalizar-entrada`; conector SQL; `<procedure_gravar_pedido>`

## Propósito

`Execute stored procedure (V2)` com parâmetros tipados e um `Compose` `Codigo_gravar` que lê o `description` (código ASCII) da linha única devolvida. A tradução para frase é de `traduzir-codigo-e-responder`.

## Quando usar / quando não usar

**Usar**

- Escrita com regra, transação ou trigger no servidor.

**Não usar**

- `Insert row`/`Update row` em tabela com trigger no servidor: não funciona.
- Escrita Dataverse: ações `CreateRecord`/`UpdateRecord`.

## Onde colar

Dentro do `Caso_<acao>`, depois de `Se_nada_mudou_gravar` (ou do último bloqueio).

## Entradas e saídas

**Lê**

- `outputs('Normalizar_gravar')`, `Id_Usuario` do chamador.

**Expõe**

- `body('Gravar_pedido')?['ResultSets']?['Table1']?[0]` (1 linha: `status`, `description` = código, `id`, `url`) e `outputs('Codigo_gravar')`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_gravar`; o mesmo conteúdo está em `gravar-via-procedure.json`). GUIDs fictícios; conexões: `<prefixo>_sharedsql`.


```json
{
  "nodeId": "Bloco_gravar",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Gravar_pedido": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "server": "default",
            "database": "default",
            "procedure": "[dbo].[<procedure_gravar_pedido>]",
            "parameters/Id_Pedido": "@outputs('Normalizar_gravar')?['idNumero']",
            "parameters/Des_Pedido": "@outputs('Normalizar_gravar')?['descricao']",
            "parameters/Qtd_Pedido": "@outputs('Normalizar_gravar')?['quantidade']",
            "parameters/Nom_Unidade": "@outputs('Normalizar_gravar')?['unidade']",
            "parameters/Id_UsuarioChamador": "@int(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Id_Usuario'],0))"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sql",
            "connection": "shared_sql",
            "operationId": "ExecuteProcedure_V2"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000078"
        }
      },
      "Codigo_gravar": {
        "type": "Compose",
        "inputs": "@coalesce(body('Gravar_pedido')?['ResultSets']?['Table1']?[0]?['description'],'')",
        "runAfter": {
          "Gravar_pedido": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000079"
        }
      }
    },
    "runAfter": {
      "Se_nada_mudou_gravar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000080"
    }
  },
  "allConnectionData": {
    "Gravar_pedido": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_sql"
        },
        "connection": {
          "id": "<prefixo>_sharedsql"
        },
        "connectionName": "<prefixo>_sharedsql"
      },
      "referenceKey": "shared_sql"
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
| `<procedure_gravar_pedido>` | nome entre colchetes | nome AS-BUILT da procedure |
| `parameters/Id_Pedido` ... `parameters/Nom_Unidade` | parâmetros de exemplo | os da assinatura AS-BUILT, na mesma ordem e tipo |
| `parameters/Id_UsuarioChamador` | `@int(coalesce(...,0))` | id do usuário lido em `Ler_chamador` |

## runAfter

Raiz depende de `Se_nada_mudou_gravar`; `Codigo_gravar` depende de `Gravar_pedido`.

## Armadilhas

- Parâmetro de coluna numérica vai como `@expr` **crua**: `@{expr}` força texto e a coluna `INT` recebe string (F018, R5).
- `int(coalesce(string(x),'0'))` estoura: `string(null)` é `''`. Use `int(coalesce(x,0))` (R12, F012).
- `server` e `database` ficam `default`: a forma com expressão foi recusada (R4); o servidor real é da connection reference.
- Nome de procedure vem do ambiente (`sys.procedures`), nunca do documento: nomes supostos custaram colagens (R9).
- O conector limita o tamanho de parâmetro de texto; trunque com `take()` no tamanho da coluna.
- Se a procedure aceita o id do chamador por parâmetro, quem tem a connection reference grava como quem quiser; decisão de defesa em profundidade é da skill `sql-procedures`.

## Variações

- Duas escritas em sequência: uma procedure só (transação no servidor); no flow, duas chamadas não são atômicas.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/gravar-via-procedure.json
```

Resultado esperado: `0 erro(s), 5 aviso(s)`.

Avisos intrínsecos ao componente isolado:

- `F006` (referência a ação fora do trecho colado): `Ler_chamador`, `Normalizar_gravar`. São as **entradas** do bloco: existem no flow de destino (ver *Entradas e saídas*). Num flow montado, o mesmo trecho passa sem esse aviso.

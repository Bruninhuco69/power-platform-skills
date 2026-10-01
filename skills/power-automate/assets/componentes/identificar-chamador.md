# Identificar o chamador (MyProfile_V2)

> **Arquivo**: `identificar-chamador.json` · **Frequência**: muito comum · **Maturidade**: estável
> **Depende de**: `config`; conector de usuários do Office 365

## Propósito

Lê o perfil do usuário que está executando o flow (`MyProfile_V2`) e normaliza o identificador em minúsculas num `Compose` chamado `Chamador`. Quem chama por fora da tela não escolhe quem é.

## Quando usar / quando não usar

**Usar**

- Todo flow que autoriza por perfil.

**Não usar**

- Flow de recebimento HTTP (sem usuário humano).
- Quando o identificador do usuário chega por parâmetro do trigger: nunca faça isso.

## Onde colar

Raiz do escopo do flow, depois de `CONFIG`.

## Entradas e saídas

**Lê**

- Contexto da conexão do usuário que executa o flow.

**Expõe**

- `outputs('Chamador')`: e-mail (ou UPN) em minúsculas, usado por `ler-chamador-sql` e `ler-chamador-dataverse`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_chamador`; o mesmo conteúdo está em `identificar-chamador.json`). GUIDs fictícios; conexões: `<prefixo>_sharedoffice365users`.


```json
{
  "nodeId": "Bloco_chamador",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Perfil_do_chamador": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "$select": "mail,userPrincipalName,displayName"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365users",
            "connection": "shared_office365users",
            "operationId": "MyProfile_V2"
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000005"
        }
      },
      "Chamador": {
        "type": "Compose",
        "inputs": "@toLower(trim(coalesce(outputs('Perfil_do_chamador')?['body/mail'],outputs('Perfil_do_chamador')?['body/userPrincipalName'],'')))",
        "runAfter": {
          "Perfil_do_chamador": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000006"
        }
      }
    },
    "runAfter": {
      "Bloco_config": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000007"
    }
  },
  "allConnectionData": {
    "Perfil_do_chamador": {
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
| conexão `shared_office365users` | `<prefixo>_sharedoffice365users` | nome lógico da connection reference do ambiente destino (skill `power-platform`) |
| ordem em `coalesce` | `mail`, depois `userPrincipalName` | a ordem que casa com o valor guardado na coluna de identidade (ver armadilhas) |

## runAfter

Raiz depende de `Bloco_config`. Dentro do bloco, `Chamador` depende de `Perfil_do_chamador`.

## Armadilhas

- A ordem `mail` x `userPrincipalName` tem de casar com o que a coluna de identidade guarda. Divergência nega **todo mundo**, sem erro. Teste de 1 minuto: rode com um usuário de teste e compare `outputs('Chamador')` no histórico com a coluna.
- Um projeto ficou com a ordem invertida entre os flows. Padronize a ordem num único lugar do projeto.
- `$select` limita o que o conector devolve; se faltar `mail`, o `coalesce` cai no UPN calado.
- Dado vindo do contexto não precisa de escape, mas quem monta `$filter` OData com ele deve duplicar apóstrofo (ver `ler-chamador-dataverse`).

## Variações

- Identidade por UPN primeiro: inverta os dois argumentos do `coalesce`.
- Outro sistema de identidade (ex.: grupo do diretório): troque `MyProfile_V2` por `UserProfile_V2`/`MemberOf`; o contrato do `Chamador` não muda.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/identificar-chamador.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

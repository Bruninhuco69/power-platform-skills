# Normalizar a entrada do trigger

> **Arquivo**: `normalizar-entrada.json` · **Frequência**: comum · **Maturidade**: estável
> **Depende de**: `switch-acao` (ou flow de ação única); parâmetros do trigger

## Propósito

Um `Compose` que aplica `trim`, `take`, `toUpper` e conversão protegida de número em texto, e devolve um objeto. As ações seguintes leem `outputs('Normalizar_gravar')?['campo']`, nunca `triggerBody()`.

## Quando usar / quando não usar

**Usar**

- Todo caso que recebe campos do app.

**Não usar**

- Para validar regra de negócio: isso é `validar-com-mensagem`.

## Onde colar

Dentro do `Caso_<acao>`, depois de `Autorizar_<acao>`.

## Entradas e saídas

**Lê**

- `triggerBody()['text_1']` ... `['text_5']` (posicionais, sempre texto).

**Expõe**

- `outputs('Normalizar_gravar')`: `id`, `idNumero`, `descricao`, `unidade`, `quantidade`, `prazo` (nulo quando vazio).

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_normalizar`; o mesmo conteúdo está em `normalizar-entrada.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_normalizar",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Normalizar_gravar": {
        "type": "Compose",
        "inputs": {
          "id": "@trim(coalesce(triggerBody()['text_1'],''))",
          "idNumero": "@int(if(and(not(empty(trim(coalesce(triggerBody()['text_1'],'')))),equals(length(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(trim(coalesce(triggerBody()['text_1'],'')),'0',''),'1',''),'2',''),'3',''),'4',''),'5',''),'6',''),'7',''),'8',''),'9','')),0),less(length(trim(coalesce(triggerBody()['text_1'],''))),10)),trim(coalesce(triggerBody()['text_1'],'')),'0'))",
          "descricao": "@take(trim(coalesce(triggerBody()['text_2'],'')),200)",
          "unidade": "@toUpper(trim(coalesce(triggerBody()['text_3'],'')))",
          "quantidade": "@int(if(and(not(empty(trim(coalesce(triggerBody()['text_4'],'')))),equals(length(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(trim(coalesce(triggerBody()['text_4'],'')),'0',''),'1',''),'2',''),'3',''),'4',''),'5',''),'6',''),'7',''),'8',''),'9','')),0),less(length(trim(coalesce(triggerBody()['text_4'],''))),10)),trim(coalesce(triggerBody()['text_4'],'')),'0'))",
          "prazo": "@if(empty(trim(coalesce(triggerBody()['text_5'],''))),null,trim(coalesce(triggerBody()['text_5'],'')))"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000034"
        }
      }
    },
    "runAfter": {
      "Autorizar_gravar": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000035"
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
| `text_1`...`text_5` | posição do parâmetro | posição conforme o contrato do trigger (`trigger-power-apps-v2`) |
| `take(..., 200)` | limite de caracteres | o tamanho da coluna de destino |
| `toUpper` | unidade em maiúsculas | a normalização que a comparação exige |
| nome `Normalizar_gravar` | sufixo da ação | `Normalizar_<acao>`, único no flow |

## runAfter

Raiz depende de `Autorizar_gravar`; troque pelo nó anterior do seu caso.

## Armadilhas

- `if()` avalia os dois ramos: `if(ehNumero, int(t), 0)` estoura com texto. Proteja o argumento: `int(if(ehNumero, t, '0'))`.
- WDL não tem regex: o teste de 'só dígitos' remove os dez dígitos e confere que sobrou vazio; limite de 9 caracteres para caber em `int`.
- `take(x, N)` é seguro com texto menor que N; substitui `substring(x, 0, min(length(x), N))` e poupa caracteres do limite de 8.192.
- Valor deliberadamente `null` (data opcional) não passa por `coalesce` nem por truncar: `''` casa nada e vira coluna vazia, não nula.
- Parâmetro novo entra **no fim** do trigger; inserir no meio faz os valores deslizarem e o flow grava o campo errado sem erro.

## Variações

- Decimal ou data: converta no flow e valide com mensagem; nunca confie no formato que o app envia.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/normalizar-entrada.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

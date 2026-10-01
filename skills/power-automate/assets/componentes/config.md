# CONFIG: flags e textos do ambiente

> **Arquivo**: `config.json` · **Frequência**: muito comum (`CONFIG` nos flows chamados pelo app; `settings` no recebimento, ver `config-recebimento`) · **Maturidade**: estável
> **Depende de**: nenhum

## Propósito

Um único `Compose` chamado `CONFIG` guarda os interruptores e os textos que mudam de ambiente (e-mail do suporte, pasta de saída, grupo de acesso). Nenhuma outra ação do flow carrega literal de ambiente. O verificador conhece o nome `CONFIG` e não acusa literal dentro dele (F014).

## Quando usar / quando não usar

**Usar**

- Todo flow chamado pela tela.
- Flow de recebimento que precise de flags simples (use `config-recebimento` para as chaves de lote).

**Não usar**

- Para guardar servidor ou banco SQL: eles ficam `default` e vêm da connection reference (R4).
- Para segredo ou token: use variável de ambiente do tipo secreto.

## Onde colar

Raiz do escopo do flow, como primeira ação (logo depois do trigger digitado à mão). Primeiro nó: sem `runAfter`.

## Entradas e saídas

**Lê**

- Nada. É constante.

**Expõe**

- `outputs('CONFIG')?['<chave>']`, lido por `escopo-unidade`, `exportar-csv-arquivo`, `email-suporte-com-parcial` e `token-cache-e-resposta-http`.

## JSON

Destino: `Ctrl+V` no ponto de inserção do designer (envelope de escopo do clipboard, `nodeId` `Bloco_config`; o mesmo conteúdo está em `config.json`). GUIDs fictícios; conexões: nenhuma.


```json
{
  "nodeId": "Bloco_config",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "CONFIG": {
        "type": "Compose",
        "inputs": {
          "mailSuporte": "suporte@contoso.com",
          "cfgEscopoUnidade": true,
          "cfgDescricaoObrigatoria": true,
          "pastaSaida": "/Exportacoes",
          "grupoAcesso": "<grupo-de-acesso>"
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000001"
        }
      }
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000002"
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
| `mailSuporte` | `suporte@contoso.com` | caixa do suporte do ambiente |
| `cfgEscopoUnidade` | `true` | mantenha `true`: interruptor de segurança nasce ligado (F3) |
| `cfgDescricaoObrigatoria` | `true` | outras regras ligáveis; todo interruptor de segurança nasce `true` |
| `pastaSaida` | `/Exportacoes` | pasta de saída do conector de arquivos, para os arquivos gerados |
| `grupoAcesso` | `<grupo-de-acesso>` | nome do grupo de diretório, se o flow pede acesso por e-mail |

## runAfter

Raiz com `runAfter` vazio. O componente seguinte (`identificar-chamador`) aponta para `Bloco_config`.

## Armadilhas

- Flag de segurança nascida `false` deixou qualquer perfil gravar em qualquer unidade; a decisão de produto nunca foi fechada. Ligue por padrão.
- Não confunda: flag de **permissão** do perfil (`Flg_PodeX`) nasce desligada; interruptor de **segurança** no `CONFIG` nasce ligado.
- Chave ausente lê como `null`. Teste `equals(chave, false)` (fail-closed), nunca `not(chave)`: `not(null)` não é falso.
- Promover de ambiente é editar o valor do `CONFIG`; se aparecer literal de ambiente em outra ação, o verificador avisa (F014).

## Variações

- Flow de recebimento HTTP: troque este bloco por `config-recebimento`.
- Valor que precisa mudar sem editar o flow: variável de ambiente lida em `parameters()`. Para cache de token não serve: o valor é congelado até salvar o flow.

## Verificação

Destino: terminal, da raiz do repositório.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/config.json
```

Resultado esperado: `0 erro(s), 0 aviso(s)`.

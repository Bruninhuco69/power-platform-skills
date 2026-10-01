# Trigger HTTP de recebimento: corpo, variáveis e raiz do flow

> **Arquivo**: `trigger-http-recebimento.md` (descritivo: sem JSON colável) · **Frequência**: ocasional · **Maturidade**: estável
> **Depende de**: nenhum

## Propósito

Declara a entrada de sistema externo: trigger **Request (HTTP)** próprio, separado dos flows chamados pelo app (C6),
com contrato de código HTTP + `{code, message}` em vez dos 4 campos.

## Quando usar / quando não usar

- Use para receber lote de sistema externo.
- Não use para ação da tela: `trigger-power-apps-v2`.

## Onde colar

Não se cola. Crie o flow, escolha o gatilho **Quando uma solicitação HTTP é recebida** (Request), método `POST`, e
cole o schema do corpo. Depois do trigger, crie **à mão, na raiz**, as duas variáveis (o `Initialize variable` só vale na
raiz) e cole `token-cache-e-resposta-http` com `runAfter` na segunda variável.

## Entradas e saídas

- Entrada: corpo `{ "dados": [ ... ] }` (lista de registros do sistema de origem); credencial no cabeçalho `Authorization`.
- Saída do trigger: `triggerBody()`, `triggerOutputs()?['headers']`.
- Resposta: `Response` com `kind: Http` (200, 202, 400, 401, 500).

## Schema do corpo (campo "Esquema JSON do corpo da solicitação")

```text
{
  "type": "object",
  "properties": {
    "dados": { "type": "array", "items": { "type": "object" } }
  },
  "required": ["dados"]
}
```

Destino: campo de esquema do trigger HTTP. Valide o formato de cada item mais adiante, no `mapear-lote`.

## Raiz do flow

```text
Trigger Request (HTTP)               POST; esquema acima
Inicializar_erros_lote               Initialize variable  Erros_lote           string   (vazio)
Inicializar_linhas_com_erro          Initialize variable  Linhas_com_erro      integer  0
Escopo_Principal                     token-cache-e-resposta-http
  CONFIG                             config-recebimento
  Scope_Token ... Resposta_sucesso / Resposta_token_invalido
  (pendurado em Resposta_sucesso) mapear-lote, upsert-unitario, indice-chaves-destino, batch-upsert-changeset
Log                                  log-execucao (irmão do principal)
```

## Contrato de resposta

| Situação | `statusCode` | Corpo |
|---|---|---|
| Processado | 200 | `{"code": "Success", "message": "Recebido com sucesso."}` |
| Aceito para processar depois | 202 | `{"code": "Accepted", "message": "...", "runId": "<workflow().run.name>"}` |
| Credencial ausente ou inválida | 401 | `{"error": {"code": "TokenInvalido", "message": "O token enviado não é válido."}}` |
| Corpo inválido | 400 | `{"error": {"code": "PayloadInvalido", "message": "..."}}` |
| Falha de gravação (modo síncrono) | 500 | `{"error": {"code": "FalhaAoGravar", "message": "..."}}` |

Sucesso é `{code, message}` plano; erro é `{"error": {code, message}}`. O chamador distingue pelo `statusCode`.

## Parâmetros a trocar

| Item | Valor | Trocar por |
|---|---|---|
| método | `POST` | o que o chamador usa |
| esquema do corpo | `dados` | contrato publicado ao sistema chamador |
| nomes das variáveis | `Erros_lote`, `Linhas_com_erro` | mantenha: `batch-upsert-changeset` e `log-execucao` as referenciam |

## runAfter

O primeiro `Initialize variable` depende do trigger. `Escopo_Principal` depende de `Inicializar_linhas_com_erro`.

## Armadilhas

- **Síncrono ou aceite**: responder 200 antes de gravar, sem declarar, esconde falhas de gravação: só o log sabe. Se for aceite, responda **202** com `runId`, ofereça consulta de status e deixe o `Log` marcar a execução como `Failed`.
- Credencial no **cabeçalho**, nunca no corpo (o corpo aparece em log de payload). O projeto de referência recebia o token no corpo.
- Quem pode disparar o trigger HTTP e a URL gerada: `[não verificado: confirme as opções de acesso do trigger no seu ambiente]`; a validação de credencial é **sua**.
- A URL do trigger é segredo: não a coloque em documento, ticket ou código.
- Publique ao sistema chamador a tabela de respostas e o formato do corpo.

## Variações

- Modo aceite: `Resposta_sucesso` com 202 e `runId`.
- Corpo com cabeçalho de lote (`{ "lote": "...", "dados": [...] }`): ajuste o esquema e o `Mapear_lote`.

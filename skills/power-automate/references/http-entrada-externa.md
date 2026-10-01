# Entrada de sistema externo (trigger HTTP)

Decisão C6 de [decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md): sistema
externo entra por trigger **Request (HTTP)** próprio, **separado** dos flows chamados pelo app
(Power Apps V2). O contrato é outro: código HTTP + `{code, message}`, não o de 4 campos.
Origem: padrão de recebimento "token em cache + resposta pelo status real" de um projeto de
referência; os defeitos dele viraram as regras abaixo
([licoes-de-campo.md](licoes-de-campo.md)).

## Sumário

1. [Contrato externo](#1-contrato-externo)
2. [Esqueleto](#2-esqueleto)
3. [Credencial](#3-credencial)
4. [Resposta pelo status real](#4-resposta-pelo-status-real)
5. [Síncrono ou aceite](#5-síncrono-ou-aceite)
6. [N=1 x lote](#6-n1-x-lote)
7. [Validação com cache](#7-validação-com-cache)

---

## 1. Contrato externo

| Situação | `statusCode` | Corpo |
|---|---|---|
| Processado | 200 | `{"code": "Success", "message": "Recebido com sucesso."}` |
| Aceito para processar depois | 202 | `{"code": "Accepted", "message": "...", "runId": "<workflow().run.name>"}` |
| Credencial ausente ou inválida | 401 | `{"error": {"code": "TokenInvalido", "message": "O token enviado não é válido."}}` |
| Corpo inválido | 400 | `{"error": {"code": "PayloadInvalido", "message": "..."}}` |
| Falha de gravação (modo síncrono) | 500 | `{"error": {"code": "FalhaAoGravar", "message": "..."}}` |

O envelope tem dois formatos, por desenho: **sucesso** (200/202) é `{code, message}` plano;
**erro** (4xx/5xx) é `{"error": {code, message}}`. O chamador distingue pelo `statusCode` e, no
corpo, pela presença da chave `error`.

Publique a tabela ao sistema chamador. Corpo de entrada: `{ "dados": [ ... ] }` (lista de
registros do sistema de origem).

## 2. Esqueleto

```
Trigger Request (HTTP)   Método POST; schema do corpo
Escopo_Principal
  Valida_credencial      Compose: o cabeçalho confere? (ver §3 e §7)
  Se_credencial_ok       If
    Sim: normalizar (Select de mapeamento) -> gravar (ver dataverse-batch-upsert.md) -> Response 200
    Não: Response 401 + Terminate
Log                      escopo fora do principal (log-execucao.md)
```

Dois itens do esqueleto vêm do projeto de referência: o mapeamento 1:1 num único `Select`
(nome lógico à esquerda, valor à direita; **única cópia** do mapeamento) e o log como escopo
irmão que lê `result('Escopo_Principal')`.

## 3. Credencial

- **Cabeçalho `Authorization`**, nunca no corpo. O projeto de referência recebia o token em
  `triggerBody()['headers']['token']` (dentro do corpo): ele aparece em logs de payload e
  `inputpayloadsize`/JSON enviado.
- Leia do cabeçalho com `triggerOutputs()?['headers']?['Authorization']`
  `[não verificado: confirme o nome exato da propriedade no histórico de execução do seu ambiente]`.
- **Nunca grave o token em texto claro** em tabela de cache, log ou `Compose` visível
  (ative "Entradas/Saídas seguras" na ação que o lê).
- Prefira validar contra um **segredo** guardado como variável de ambiente do tipo Secret ou
  Key Vault a manter cópia do token em tabela `[não verificado: comportamento de variável
  secreta em flow; confirme no Learn de variáveis de ambiente]`.
- O gatilho HTTP aceita autenticação do próprio Power Automate (por usuário do tenant)
  `[não verificado]`; quando não for usada, a validação de credencial é **sua**.

## 4. Resposta pelo status real

O defeito mais caro do projeto de referência: a `Condição` comparava **constantes**
(`equals(200, 200)`), o ramo de token inválido era código morto e o flow respondia 200 mesmo com
a validação do token falhando (porque o `Response` rodava depois de `Succeeded, Failed, Skipped,
TimedOut`). O verificador acusa condição constante (F016) e `Response` HTTP antecipada (F015,
aviso).

Regras:

1. **O código HTTP é derivado do resultado real da validação**, nunca de constante.
2. `Response` 200 com `runAfter` só em `Succeeded` da validação; `Response` 401 em
   `Failed`/`TimedOut` (ou ramo `else` de um `If` cuja condição é o resultado da conferência).
3. Teste de rejeição **obrigatório**: chame com token errado e com token ausente e confira o 401.
4. `Response` HTTP também **não encerra** o flow: a mesma regra do `Terminate` de
   [anatomia-flow.md](anatomia-flow.md) vale para o ramo 401.

## 5. Síncrono ou aceite

Declare no contrato qual dos dois o flow é:

| Modo | Quando | Custo |
|---|---|---|
| **Síncrono** (responde depois de gravar) | Lotes pequenos; o chamador precisa saber do erro | O chamador espera; limite de tempo de resposta do trigger `[não verificado: valor]` |
| **Aceite** (200/202 antes de gravar) | Lotes grandes; chamador não pode esperar | O chamador **nunca** sabe de erro de gravação |

O projeto de referência respondia 200 antes de processar **sem declarar** que era aceite: só o
log sabia da falha. Se for aceite: (a) responda **202** com `runId`, (b) exponha consulta de
status ou notifique, (c) o `Log` marca a execução como `Failed` quando algo quebrou
([log-execucao.md](log-execucao.md)).

## 6. N=1 x lote

| Tamanho | Caminho |
|---|---|
| N = 1 | Busca por chave exata (`$top 1`) -> `PATCH` por id (`If-Match: *`: só atualiza) ou `POST` |
| N > 1 | Índice {chave -> id} da tabela destino + separar quem existe de quem não existe + `$batch` em partes ([dataverse-batch-upsert.md](dataverse-batch-upsert.md)) |

O ramo unitário evita ler a tabela inteira para gravar uma linha. [verificado: projeto de
referência]

## 7. Validação com cache

Validar credencial por chamada em serviço externo custa tempo e cota. Padrão do projeto de
referência, em escopo reutilizável colado como **primeira ação dentro do escopo principal** (não
na raiz: o `Log` lê `result('Escopo_Principal')` e precisa ver a falha de credencial lá):

1. Lê a linha do cache da origem (token + `modifiedon`).
2. Se não há token, ou difere do cache, ou `modifiedon` tem 1 h ou mais: valida de verdade e
   regrava o cache.
3. Status do escopo: `Succeeded` = aceito; `Failed` = recusado. `Response` 200 em `Succeeded`,
   401 em `Failed`/`TimedOut`.
4. Falha ao **gravar o cache** não pode derrubar o recebimento: ação de absorção em
   `runAfter [Failed, TimedOut]` do `Criar_cache`, **sem** `Skipped` (senão mascara a falha da
   validação). Documente isso na descrição da ação.
5. Ações independentes da credencial (mapeamento) **sem** `runAfter`, para rodarem em paralelo.
6. **Não use variável de ambiente como cache**: o valor é congelado até salvar ou religar o flow
   ([Learn: limitações](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables-power-automate#limitations)).

Melhorias que o projeto de referência não fez: tabela de cache **genérica** por origem (a chave
`name` já existe), nome da tabela por variável de ambiente, e não guardar o token em claro
(hash: ver a ressalva em [expressoes-wdl-armadilhas.md](expressoes-wdl-armadilhas.md) §9).

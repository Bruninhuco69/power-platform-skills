# Contrato app ↔ flow (lado do flow)

Decisões C1–C4 e C6 de [decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md).
Este arquivo é o lado do **flow**; a chamada `.Run()` no app (loading, toast, `IfError`,
`Refresh`) é da skill `powerapps-canvas`.

## Sumário

1. [Trigger Power Apps (V2): parâmetros posicionais](#1-trigger-power-apps-v2-parâmetros-posicionais)
2. [Resposta: sempre quatro campos](#2-resposta-sempre-quatro-campos)
3. [Código da escrita para mensagem](#3-código-da-escrita-para-mensagem)
4. [Parâmetro novo entra no fim](#4-parâmetro-novo-entra-no-fim)
5. [Chamada vista do app](#5-chamada-vista-do-app)
6. [Operação longa](#6-operação-longa)
7. [Documento de contrato](#7-documento-de-contrato)

---

## 1. Trigger Power Apps (V2): parâmetros posicionais

O app passa os argumentos **por posição**, não por nome. O primeiro parâmetro de texto do
trigger é lido como `triggerBody()['text']`, o segundo como `triggerBody()['text_1']`, e assim
por diante (`text_N`). [verificado: projeto de referência]

| # | Nome no trigger | Leitura no flow | Conteúdo |
|--:|---|---|---|
| 1 | `acao` | `triggerBody()['text']` | `gravar` |
| 2 | `id` | `triggerBody()['text_1']` | id do registro, em texto |
| 3 | `descricao` | `triggerBody()['text_2']` | texto livre |
| 4 | `unidade` | `triggerBody()['text_3']` | sigla da unidade |

- **Todos texto.** Número, data e booleano viajam como texto e são convertidos no `Normalizar`.
- **A ordem é a assinatura.** Inserir um parâmetro no meio faz os valores deslizarem uma casa e o
  flow grava o campo errado sem reclamar.
- **Identidade nunca vem por parâmetro** (`upn`, e-mail do usuário): quem chama diria quem é. Ela
  vem de `MyProfile_V2` ([autorizacao-no-flow.md](autorizacao-no-flow.md)). Parâmetro de
  identidade só se justifica para carimbar autoria de **outro** usuário (o alvo da ação).
- O `nodeId` do trigger depende do idioma do ambiente (ver [formato-clipboard.md](formato-clipboard.md)).

## 2. Resposta: sempre quatro campos

```json
{
  "status": "success",
  "description": "Registro gravado.",
  "id": "123",
  "url": ""
}
```

| Campo | Tipo | Valores |
|---|---|---|
| `status` | texto | `success`, `warning` ou `error` |
| `description` | texto | frase pronta para o usuário, pt-BR, sem jargão, montada **no flow** |
| `id` | texto | id do registro criado/alterado; vazio no erro |
| `url` | texto | só em exportação; vazio nos demais |

- **Os quatro saem sempre, mesmo vazios.** A tela que lê `ret.url` num flow que não exporta
  recebe `""`, não erro de propriedade inexistente. O verificador acusa `Response` com campo
  faltando (F010).
- `Response` com `kind: PowerApp`, `statusCode: 200` e `schema` com `additionalProperties: {}`
  (R6 em [gabarito-designer.md](gabarito-designer.md)). Erro de negócio também é 200: o app
  decide por `status`.
- **`warning` não é enfeite.** Quando a operação **gravou** mas com ressalva (ex.: cadastro com
  duplicidade entra como pendente), devolver `error` faz o usuário achar que nada aconteceu e
  repetir. O app fecha o modal em `warning` (C3).
- **A negação é genérica de propósito.** "Seu perfil não permite esta ação" não diz qual unidade
  ou registro; dizer responderia, a quem está sondando, uma pergunta que ele não podia fazer.

## 3. Código da escrita para mensagem

A procedure (ou o passo de escrita) devolve **código** ASCII de vocabulário fechado; o flow
traduz. Guarde o código em um `Compose` e traduza com `if()` aninhado (mensagens entre aspas
simples; texto com valor usa `concat()`, nunca `@{}` dentro de literal de `if()`):

```text
Codigo_gravar  = @coalesce(body('Gravar_registro')?['ResultSets']?['Table1']?[0]?['description'],'')
status         = @{if(equals(outputs('Codigo_gravar'),'GRAVADO'),'success',if(equals(outputs('Codigo_gravar'),'NAO_APLICADO'),'warning','error'))}
description    = @{if(equals(outputs('Codigo_gravar'),'GRAVADO'),'Registro gravado.',if(equals(outputs('Codigo_gravar'),'NAO_APLICADO'),'Nada foi alterado.',concat('Resposta inesperada do sistema: ',outputs('Codigo_gravar'),'.')))}
```

Destino: campos `body.status` e `body.description` de uma ação `Response` (valor de campo de texto,
por isso `@{...}`); o `Compose` usa `@expr` crua. O molde `assets/flow-gravar-molde.json` traz
exatamente isto.

Regras:

1. **Código desconhecido responde `error` nomeando o código** e força `status` a `error`, mesmo
   que a escrita tenha dito `success`. Código novo na procedure sem tradução no flow nunca vira
   sucesso silencioso.
2. Vocabulário fechado: a tabela código -> frase vive no documento de contrato
   ([assets/contrato-flow-molde.md](../assets/contrato-flow-molde.md)), não espalhada.
3. Procedure devolve 1 linha com `status, description, id, url`
   (decisão B1; quem define a procedure é a skill `sql-procedures`). Zero linha vira `''` no
   `coalesce` e cai no caso "desconhecido".

## 4. Parâmetro novo entra no fim

- Parâmetro novo: **sempre no fim** do trigger e da chamada.
- Parâmetro morto vira `naoUsado<N>` e continua ocupando a posição.
- Mantenha no contrato a tabela `# / nome / token / conteúdo` e um teste de contagem: o número de
  argumentos do `.Run()` no app deve ser igual ao número de parâmetros do trigger.
- Mudar a ordem de um flow em uso exige atualizar **todas** as chamadas no mesmo deploy; sem
  isso, os valores deslizam sem erro.

## 5. Chamada vista do app

Para o autor do flow saber o que o app envia (o dono desta chamada é `powerapps-canvas`):

```text
// barra de fórmulas (pt-BR: ; e ;;)
IfError(Set(varRet; 'flow-gravar'.Run("gravar"; Text(varSel.id; "[$-en-US]0"); txtDescricao.Text; varSel.Unidade)); Set(varRet; Blank()))
```

Destino: barra de fórmulas do Studio em locale pt-BR (ex.: `OnSelect` do botão). O id numérico
vai com `Text(id; "[$-en-US]0")`: sem formato, o pt-BR gera `"1.234"` e o flow recebe o ponto
(C4). A chamada fica dentro de `IfError` no app (C3). A unidade de gravação vem do **registro**
(`varSel.Unidade`), não de variável global.

## 6. Operação longa

Se a operação pode passar do limite de tempo de resposta síncrona, não segure o `Response`
(o limite exato do trigger Power Apps está `[não verificado]` aqui; confirme no ambiente).
Padrão de **job assíncrono** [verificado: projeto de referência]:

1. O app gera um GUID de correlação e o envia como parâmetro.
2. O flow cria uma linha de status (`jobId`, `codstatus`: processando / sucesso / parcial / falha,
   contagem de itens com sucesso e com erro, observações) e responde `success` com `id` = jobId.
3. O app consulta a linha por polling com backoff e **condição de parada**, e mostra o toast
   conforme o estado final.

Quem decide a tabela de status é a skill `dataverse`; o polling no app é de `powerapps-canvas`.

## 7. Documento de contrato

Um documento por flow, **gerado a partir do artefato quando possível** (documento escrito à mão
envelhece no dia seguinte). Molde: [assets/contrato-flow-molde.md](../assets/contrato-flow-molde.md).
Quando divergir do flow, o contrato é o bug.

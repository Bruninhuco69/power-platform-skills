# Timers e operações assíncronas

Auto-refresh, debounce, toast, timeout, polling e as armadilhas do controle `Timer`. Todo YAML
está no dialeto do YAML colado (`,` e `;`) e usa só propriedades **atestadas** em `Timer@2.1.0`
(`Duration`, `OnTimerEnd`, `Start`, `Repeat`, `Reset`, `Visible`, `Height`, `Width`, `X`, `Y`).
`AutoStart`, `AutoPause` e `OnTimerStart` constam na documentação do controle, mas **não foram
atestadas no Studio dos projetos de referência**: se quiser usá-las, teste num bloco pequeno
(PA2108 recusa o bloco inteiro) `[não verificado]`. Aqui a parada fora da tela é garantida por
**guarda explícita no `Start`**.

## Sumário

1. [Anatomia](#1-anatomia)
2. [Auto-refresh de KPI](#2-auto-refresh-de-kpi)
3. [Debounce de busca](#3-debounce-de-busca)
4. [Timer do toast](#4-timer-do-toast)
5. [Timeout e retry](#5-timeout-e-retry)
6. [Polling com backoff e parada](#6-polling-com-backoff-e-parada)
7. [Armadilhas](#7-armadilhas)
8. [Alternativas ao timer](#8-alternativas-ao-timer)
9. [Fontes](#9-fontes)

---

## 1. Anatomia

Fonte única: [Timer control](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-timer)
(lida em 2026-10).

| Propriedade | Descrição documentada | Consequência |
|---|---|---|
| `Duration` | ms; máximo 24 h; padrão 60 s (`60000`) | se sobrescrita por variável, inicialize a variável |
| `Repeat` | reinicia sozinho ao terminar | `Repeat` sem regra de parada é polling infinito |
| `OnTimerEnd` | ações ao terminar | mantenha barato (§7.8) |
| `Start` | se o timer roda | precisa de **transição** `false` para `true`; ficar `true` não reinicia |
| `Reset` | volta ao valor inicial | também por transição; é o que permite reiniciar um timer rodando |
| `Visible` | timer de fundo: `false` | timer visível e rodando é anunciado pelo leitor de tela a cada 5 s |
| `.Value` | ms decorridos (leitura) | usado nos exemplos oficiais, mas não consta na tabela de propriedades |

- **Timers só rodam em Preview** (`F5`) no Studio: testar no canvas de edição dá "não funciona"
  falso.
- **A documentação não diz** que o timer para quando a tela sai de foco ou o app vai para
  segundo plano; só documenta a propriedade `AutoPause`. Não confie em comportamento implícito:
  amarre o `Start` ao estado da tela. Cada tela grava `Set(varTelaAtiva, "<tela>")` no
  `OnVisible`; ao navegar para outra, a variável muda e o `Start` cai.
- Acessibilidade: se o timer dispara mudança visível, ofereça cancelar, ajustar ou avisar 20 s
  antes (WCAG 2.0, limite de tempo); mudança relevante pede *live region*
  (ver [acessibilidade.md](acessibilidade.md)).

Esqueleto de timer de fundo:

Destino: YAML colado (`,` e `;`).

```yaml
xx-tim-exemplo:
  Control: Timer@2.1.0
  Properties:
    Duration: =60000
    OnTimerEnd: |-
      =Set(varTimerRodando, false);
      Set(varCondicao, false)
    Repeat: =false
    Reset: =!varCondicao
    Start: =varCondicao && varTelaAtiva = "pedidos"
    Visible: =false
```

## 2. Auto-refresh de KPI

**Problema.** KPI que reflete o banco sem o usuário apertar nada, mas `Refresh()` periódico
vezes N usuários vezes M tabelas vira tempestade. **Sintoma.** 429 de throttling, rajadas
idênticas no Monitor.

**Solução.** Timer com **quatro guardas**: tela visível, usuário não está editando, intervalo
humano (60 s ou mais) e botão de parada.

Destino: YAML colado (`,` e `;`).

```yaml
xx-tim-autorefresh:
  Control: Timer@2.1.0
  Properties:
    Duration: =120000
    OnTimerEnd: |-
      =Refresh(Pedido);
      Set(varUltimoRefresh, Now())
    Repeat: =true
    Start: =varTelaAtiva = "pedidos" && varAutoRefreshLigado && !varEditando
    Visible: =false
```

`Refresh(fonte)` invalida o cache da fonte e faz named formulas e `Gallery.Items` dependentes
recalcularem, sem materializar coleção nem sofrer o *Data row limit*
([Refresh](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-refresh)).
O controle de parada (exigência de acessibilidade) é um `Classic/Toggle@2.1.0` com `OnCheck` e
`OnUncheck` ligando `varAutoRefreshLigado`; um rótulo mostra "Atualizado às hh:mm:ss".

| Criticidade do dado | Intervalo | Requisições por usuário por hora (3 tabelas) |
|---|--:|--:|
| "preciso ver agora" (SLA em minutos) | 60.000 ms | 180 |
| operacional normal | 120.000 a 300.000 ms | 36 a 90 |
| informativo | 900.000 ms | 12 |

Multiplique pelos usuários simultâneos antes de decidir: 50 operadores a 180 req/h são 9.000
requisições por hora só de refresh.

**Quando não usar.** Usuário editando (o refresh troca `ThisItem` por baixo dele; some
`&& !varEditando` no `Start`); dado que só muda por ação do próprio app (chame `Refresh` depois
da gravação); push disponível (§8); intervalo desejado abaixo de 30 s (use polling com backoff,
§6).

## 3. Debounce de busca

**Problema.** `OnChange` dispara consulta por tecla. **Solução A, `DelayOutput`** (nativa; use
primeiro): "When set to true, user input is registered after half a second delay"
([Text input](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-text-input)).
A página *Efficient calculations* diz "one second"; a referência do controle é mais específica.

Destino: YAML colado (`,` e `;`).

```yaml
xx-txt-busca:
  Control: Classic/TextInput@2.3.2
  Properties:
    DelayOutput: =true
    HintText: ="Buscar por código"
```

O `Items` da galeria lê `'xx-txt-busca'.Text` direto, sem `OnChange`, sem variável e sem timer:
`Filter(Pedido, StartsWith(Codigo, 'xx-txt-busca'.Text))`. É a otimização de melhor custo e
benefício: uma propriedade por controle. Atenção: no controle **moderno**, `OnChange` passou a
disparar só no *blur*; busca ao vivo lê `.Text` direto
([Modern control updates](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/modern-controls/modern-control-updates)).

**Solução B, timer**: quando 500 ms não bastam ou o gatilho não é um `TextInput` (o `ComboBox` e
o `DatePicker` não têm `DelayOutput`).

Destino: YAML colado (`,` e `;`).

```yaml
xx-tim-debounce:
  Control: Timer@2.1.0
  Properties:
    Duration: =900
    OnTimerEnd: |-
      =Set(varBuscaPendente, false);
      Set(varBuscaAplicada, varBuscaTexto)
    Repeat: =false
    Reset: =!varBuscaPendente
    Start: =varBuscaPendente
    Visible: =false
```

O `OnChange` do campo reinicia o ciclo forçando a transição:

Destino: YAML colado (`,` e `;`).

```yaml
# OnChange do campo de busca
OnChange: |-
  =Set(varBuscaTexto, Self.Text);
  // força a transição false -> true: sem isto o timer não reinicia
  Set(varBuscaPendente, false);
  Set(varBuscaPendente, true)
```

`Reset: =!varBuscaPendente` é obrigatório: `Start` só reage à transição, então digitar a 8ª
letra com o timer da 7ª rodando viraria "espera fixa desde a 1ª tecla".
`[verificado: projeto de referência]`

**Quando não usar.** Quando `DelayOutput` resolve; em busca sobre coleção local pequena (menos
de 500 linhas: filtrar por tecla é instantâneo); em validação síncrona de campo obrigatório.

## 4. Timer do toast

**Problema.** Mensagem de sucesso ou erro precisa sumir sozinha; duas mensagens em sequência não
podem herdar o tempo restante da primeira. O bloco completo do toast está em
[ux-feedback.md](ux-feedback.md) §11; o que o timer precisa:

- `Start: =varShowToast` **e** `Reset: =!varShowToast`: sem o `Reset`, um segundo toast herda o
  tempo restante do primeiro e pode sumir em 200 ms.
- `Duration` por severidade: 6.000 ms (sucesso curto), 12.000 ms (aviso ou mensagem acima de 100
  caracteres), 15.000 ms (erro). Quem lê mais precisa de mais tempo; o `✕` fecha antes.
  Valores em tokens `fxToastDuration*`.
- O chamador força a transição quando já há um toast no ar:

Destino: YAML colado (`,` e `;`).

```yaml
# OnSelect de quem dispara o toast
OnSelect: |-
  =Set(varShowToast, false);
  Set(varToastMessage, fxMsgSalvoComSucesso);
  Set(varToastType, "success");
  Set(varShowToast, true)
```

- Barra de progresso que anda: `Width: =Parent.Width * (1 - 'xx-tim-toast'.Value / Max('xx-tim-toast'.Duration, 1))`.
  Nome com hífen **entre aspas simples**. `[não verificado: depende de Timer.Value recalcular com
  Visible: =false]`; se não animar, use `=Parent.Width`.
- Erro que exige ação do usuário não é toast: use modal com botão "Entendi". Um erro que some
  sozinho é um erro perdido. Em loop, agregue ("12 encerrados, 3 com erro") em vez de empilhar toasts.
- Para validação de formulário, `Notify()` nativo é o uso correto; **retorno de flow é toast**.

## 5. Timeout e retry

**Problema.** Um `.Run()` que nunca volta deixa o overlay para sempre na tela
(`varShowLoading` preso em `true`).

**Solução, watchdog.** O timer **vigia** a operação, não a executa.

Destino: YAML colado (`,` e `;`).

```yaml
xx-tim-watchdog:
  Control: Timer@2.1.0
  Properties:
    Duration: =45000
    OnTimerEnd: |-
      =If(
        varShowLoading,
        Set(varShowLoading, false);
        Set(varOperacaoTimeout, true);
        Set(varToastType, "error");
        Set(varToastMessage, fxMsgTimeoutError & " " & fxMsgTimeoutHint);
        Set(varShowToast, false);
        Set(varShowToast, true)
      )
    Repeat: =false
    Reset: =!varShowLoading
    Start: =varShowLoading
    Visible: =false
```

Sem guarda de tela de propósito: se o usuário navegar durante a operação, o loading ainda deve
morrer.

**Retry com teto**: botão "Tentar novamente (n restantes)" visível só com
`varOperacaoTimeout && varTentativas < 3`; ao esgotar, rótulo de falha definitiva.
**Regra de ouro: nunca refaça sozinho uma operação que grava** sem chave de idempotência: guarde
os ids enviados numa coleção (`colEnviados`) e desabilite o botão da linha enquanto o id estiver
nela, e deixe o flow recusar duplicata dentro da transação (skill `power-automate`). Um timeout
no app **não prova** que o flow falhou: confira o resultado na lista antes de repetir.

## 6. Polling com backoff e parada

Para lote que demora mais que o timeout do conector: o flow grava o progresso numa tabela de
status; o app consulta por um **GUID de correlação gerado no cliente**. Anatomia correta:

1. correlação (GUID no cliente, enviado ao flow e gravado na tabela de status);
2. guarda de execução (só roda com `varLoteEmProcessamento`);
3. **backoff** (o intervalo cresce a cada ciclo);
4. **teto de tentativas** (para para sempre, mesmo se o backend nunca responder);
5. desligamento explícito em **todos** os caminhos de saída.

Destino: YAML colado (`,` e `;`).

```yaml
xx-tim-polling:
  Control: Timer@2.1.0
  Properties:
    Duration: =Min(60000, 5000 * Power(2, varPollTentativas))
    OnTimerEnd: |-
      =Set(varPollTentativas, varPollTentativas + 1);
      Set(varPollRegistro, LookUp(StatusProcesso, Id_Correlacao = Text(varLoteGuid)));
      If(
        !IsBlank(varPollRegistro) && varPollRegistro.Cod_Status >= 3,
        // caminho 1: concluido (3 sucesso, 4 parcial, 5 falha)
        Set(varLoteEmProcessamento, false);
        Set(varToastType, If(varPollRegistro.Cod_Status = 3, "success", If(varPollRegistro.Cod_Status = 4, "warning", "error")));
        Set(varToastMessage, varPollRegistro.Descricao);
        Set(varShowToast, true);
        Clear(colEnviados);
        Refresh(Pedido),
        varPollTentativas >= 10,
        // caminho 2: teto estourado
        Set(varLoteEmProcessamento, false);
        Set(varToastType, "error");
        Set(varToastMessage, fxMsgTimeoutError & " " & fxMsgTimeoutHint);
        Set(varShowToast, true),
        // caminho 3: continua; reinicia o ciclo com a nova Duration
        Set(varLoteEmProcessamento, false);
        Set(varLoteEmProcessamento, true)
      )
    Repeat: =false
    Reset: =!varLoteEmProcessamento
    Start: =varLoteEmProcessamento
    Visible: =false
```

Disparo (sempre zera o contador): `Set(varLoteGuid, GUID())`, `Set(varPollTentativas, 0)`, chamada do
flow com o GUID como parâmetro **dentro de `IfError`**
([chamada-flow.md](chamada-flow.md)), e por fim `Set(varLoteEmProcessamento, false)` seguido de
`Set(varLoteEmProcessamento, true)`. Backoff: 5 s, 10 s, 20 s, 40 s, 60 s, 60 s... O reinício por
`Set(false)` seguido de `Set(true)` e o `Reset` amarrado à negação são o mecanismo
`[verificado: projeto de referência]`.

**Quando não fazer polling.** Se o flow responde síncrono dentro do timeout do conector, espere a
resposta; se a operação passa de ~5 minutos, avise por e-mail ou Teams pelo próprio flow. O
polling por `LookUp` numa tabela é bem mais barato que polling que chama flow (cada instanciação
custa ~0,6 s).

## 7. Armadilhas

### 7.1 Timer que nunca para

`Start` ligado a uma variável que ninguém volta a `false`, com `Repeat: =true` e `OnTimerEnd` com
`Refresh()` incondicional: depois do primeiro disparo da sessão o app faz refresh a cada ciclo
**até o usuário fechar** (com 50 operadores, milhares de requisições por hora de puro
desperdício). Todo timer tem **regra de parada** no `OnTimerEnd`, `Reset: =!<flag>` e `Start`
amarrado ao **estado real** do que ele observa, não a uma variável ad hoc.
`[verificado: projeto de referência]`

### 7.2 `Duration` sem inicialização

Variável usada em `Duration` que não nasce no `OnStart` é `Blank()` no primeiro render:
comportamento indefinido. Use `Coalesce(varDuracao, 60000)` ou derive a duração do backoff.

### 7.3 Falta de `Reset`

Sem `Reset: =!varX` e sem forçar `false` e `true` no chamador, o timer vira disparo único por
ciclo de vida da variável. Cliques em menos do que a `Duration` são engolidos.

### 7.4 Consulta dentro de `Start`

`Start` é reavaliado a cada mudança de dependência: consulta ali é rede em propriedade de UI
(N+1). Use named formula (ver [performance.md](performance.md) §10).

### 7.5 `Repeat` permanente

`Repeat: =true` ligado o tempo todo, mais `Start` sempre verdadeiro, é loop infinito que começa
sozinho. Animação cosmética por `Set` global a cada 1,5 s paga recomputação do grafo 2.400 vezes
por hora: não anime, ou anime com CSS dentro de `HtmlViewer` (zero reavaliação de Power Fx).

### 7.6 Timers disputando variáveis

Um timer por responsabilidade; nenhum timer escreve variável que outro timer também escreve. Se
precisar coordenar, use variável de posse (`If(!varToastAtivo, Set(...))`).

### 7.7 `#` em bloco de fórmula

Dentro de `|-`, `#` é texto da fórmula, não comentário: o Power Fx rejeita. Comentário é `//`.
(Validador: T015 para o caso de linha única.)

### 7.8 Precisão e custo

`Duration` é intenção, não garantia: o motor é single-threaded e, com `OnTimerEnd` pesado e
`Repeat`, o intervalo real é `Duration + tempo do corpo`. `OnTimerEnd` deve ser barato; trabalho
pesado vai num botão ou num flow. Para medir tempo, use `DateDiff(varT0, Now(), ...)`.

### 7.9 Hífen sem aspas

`'xx-tim-toast'.Value` com aspas simples; sem elas, `a-b` é subtração.

## 8. Alternativas ao timer

Antes de criar um, veja se um destes resolve (todos mais baratos):

- **Named formula** para "última atualização": `frmUltimaAtualizacao = Text(...)` lida de uma
  variável gravada pelo botão. `Now()` **não** é relógio que anda sozinho; segundos correndo na
  tela pedem timer, e a pergunta é se o app precisa disso.
- **`Refresh()` manual**: botão "Atualizar" (zero requisição com ninguém olhando) mais rótulo de
  idade do dado que fica amarelo (`DateDiff(varUltimoRefresh, Now(), TimeUnit.Minutes) > 5`).
- **Flow que sinaliza**: o flow grava o resultado numa tabela; o app lê com `Gallery.Items` ou
  named formula e um `Refresh()` por evento do usuário. Push nativo (`SendPushNotificationV2`)
  ou e-mail/Teams para lote longo.
- **`DelayOutput`** no lugar de timer de debounce (§3).
- **CSS em `HtmlViewer`** no lugar de timer de pulso.

## 9. Fontes

- [Timer control](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-timer)
- [Refresh function](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-refresh)
- [Text input control](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-text-input)
- [Monitor canvas apps](https://learn.microsoft.com/en-us/power-apps/maker/monitor-canvasapps)
- [Accessibility guidelines for timers (WCAG 2.0 time limits)](https://www.w3.org/TR/WCAG20/#time-limits)

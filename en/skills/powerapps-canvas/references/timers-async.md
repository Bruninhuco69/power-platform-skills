# Timers and asynchronous operations

Auto-refresh, debounce, toast, timeout, polling and the pitfalls of the `Timer` control. All YAML
is in the pasted-YAML dialect (`,` and `;`) and uses only properties **attested** in `Timer@2.1.0`
(`Duration`, `OnTimerEnd`, `Start`, `Repeat`, `Reset`, `Visible`, `Height`, `Width`, `X`, `Y`).
`AutoStart`, `AutoPause` and `OnTimerStart` appear in the control's documentation, but were **not
attested in Studio in the reference projects**: if you want to use them, test in a small block
(PA2108 rejects the whole block) `[unverified]`. Here, stopping when off screen is guaranteed by
an **explicit guard in `Start`**.

## Contents

1. [Anatomy](#1-anatomy)
2. [KPI auto-refresh](#2-kpi-auto-refresh)
3. [Search debounce](#3-search-debounce)
4. [Toast timer](#4-toast-timer)
5. [Timeout and retry](#5-timeout-and-retry)
6. [Polling with backoff and a stop](#6-polling-with-backoff-and-a-stop)
7. [Pitfalls](#7-pitfalls)
8. [Alternatives to a timer](#8-alternatives-to-a-timer)
9. [Sources](#9-sources)

---

## 1. Anatomy

Single source: [Timer control](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-timer)
(read 2026-10).

| Property | Documented description | Consequence |
|---|---|---|
| `Duration` | ms; maximum 24 h; default 60 s (`60000`) | if overridden by a variable, initialize the variable |
| `Repeat` | restarts by itself when it ends | `Repeat` without a stop rule is infinite polling |
| `OnTimerEnd` | actions when it ends | keep it cheap (§7.8) |
| `Start` | whether the timer runs | needs a **transition** from `false` to `true`; staying `true` does not restart it |
| `Reset` | returns to the initial value | also by transition; it is what lets you restart a running timer |
| `Visible` | background timer: `false` | a visible, running timer is announced by the screen reader every 5 s |
| `.Value` | elapsed ms (read) | used in the official examples, but not in the property table |

- **Timers only run in Preview** (`F5`) in Studio: testing on the editing canvas gives a false
  "does not work".
- **The documentation does not say** that the timer stops when the screen loses focus or the app
  goes to the background; it only documents the `AutoPause` property. Do not rely on implicit
  behavior: tie `Start` to the screen state. Each screen writes `Set(varTelaAtiva, "<screen>")` in
  `OnVisible`; when navigating to another, the variable changes and `Start` drops.
- Accessibility: if the timer triggers a visible change, offer cancel, adjust, or a warning 20 s
  beforehand (WCAG 2.0, time limit); a relevant change calls for a *live region*
  (see [accessibility.md](accessibility.md)).

Background timer skeleton:

Destination: YAML pasted into Studio (`,` and `;`).

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

## 2. KPI auto-refresh

**Problem.** A KPI that reflects the database without the user pressing anything, but a periodic
`Refresh()` times N users times M tables becomes a storm. **Symptom.** 429 throttling, identical
bursts in the Monitor.

**Solution.** A timer with **four guards**: screen visible, user not editing, human-scale
interval (60 s or more) and a stop button.

Destination: YAML pasted into Studio (`,` and `;`).

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

`Refresh(source)` invalidates the source cache and makes dependent named formulas and
`Gallery.Items` recalculate, without materializing a collection or being subject to the *Data row limit*
([Refresh](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-refresh)).
The stop control (an accessibility requirement) is a `Classic/Toggle@2.1.0` with `OnCheck` and
`OnUncheck` setting `varAutoRefreshLigado`; a label shows "Updated at hh:mm:ss".

| Data criticality | Interval | Requests per user per hour (3 tables) |
|---|--:|--:|
| "I need to see it now" (SLA in minutes) | 60,000 ms | 180 |
| normal operational | 120,000 to 300,000 ms | 36 to 90 |
| informational | 900,000 ms | 12 |

Multiply by simultaneous users before deciding: 50 operators at 180 req/h are 9,000
requests per hour of refresh alone.

**When not to use it.** A user who is editing (the refresh swaps `ThisItem` from under them; add
`&& !varEditando` to `Start`); data that only changes by the app's own action (call `Refresh` after
the write); push available (§8); a desired interval below 30 s (use polling with backoff,
§6).

## 3. Search debounce

**Problem.** `OnChange` fires a query per keystroke. **Solution A, `DelayOutput`** (native; use it
first): "When set to true, user input is registered after half a second delay"
([Text input](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-text-input)).
The *Efficient calculations* page says "one second"; the control reference is more specific.

Destination: YAML pasted into Studio (`,` and `;`).

```yaml
xx-txt-busca:
  Control: Classic/TextInput@2.3.2
  Properties:
    DelayOutput: =true
    HintText: ="Search by code"
```

The gallery's `Items` reads `'xx-txt-busca'.Text` directly, with no `OnChange`, no variable and no
timer: `Filter(Pedido, StartsWith(Codigo, 'xx-txt-busca'.Text))`. It is the best cost-benefit
optimization: one property per control. Note: in the **modern** control, `OnChange` now fires only
on *blur*; live search reads `.Text` directly
([Modern control updates](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/modern-controls/modern-control-updates)).

**Solution B, timer**: when 500 ms is not enough or the trigger is not a `TextInput` (`ComboBox`
and `DatePicker` have no `DelayOutput`).

Destination: YAML pasted into Studio (`,` and `;`).

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

The field's `OnChange` restarts the cycle by forcing the transition:

Destination: YAML pasted into Studio (`,` and `;`).

```yaml
# OnChange of the search field
OnChange: |-
  =Set(varBuscaTexto, Self.Text);
  // forces the false -> true transition: without this the timer does not restart
  Set(varBuscaPendente, false);
  Set(varBuscaPendente, true)
```

`Reset: =!varBuscaPendente` is mandatory: `Start` only reacts to the transition, so typing the 8th
letter while the 7th's timer is running would become "fixed wait since the 1st keystroke".
`[verified: reference project]`

**When not to use it.** When `DelayOutput` solves it; on a search over a small local collection
(fewer than 500 rows: filtering per keystroke is instant); on synchronous required-field
validation.

## 4. Toast timer

**Problem.** A success or error message must disappear on its own; two messages in a row cannot
inherit the remaining time of the first. The full toast block is in
[ux-feedback.md](ux-feedback.md) §11; what the timer needs:

- `Start: =varShowToast` **and** `Reset: =!varShowToast`: without the `Reset`, a second toast
  inherits the remaining time of the first and may vanish in 200 ms.
- `Duration` by severity: 6,000 ms (short success), 12,000 ms (warning or message over 100
  characters), 15,000 ms (error). Whoever reads more needs more time; the `✕` closes it earlier.
  Values in `fxToastDuration*` tokens.
- The caller forces the transition when there is already a toast on screen:

Destination: YAML pasted into Studio (`,` and `;`).

```yaml
# OnSelect of whoever triggers the toast
OnSelect: |-
  =Set(varShowToast, false);
  Set(varToastMessage, fxMsgSalvoComSucesso);
  Set(varToastType, "success");
  Set(varShowToast, true)
```

- Moving progress bar: `Width: =Parent.Width * (1 - 'xx-tim-toast'.Value / Max('xx-tim-toast'.Duration, 1))`.
  The hyphenated name goes **in single quotes**. `[unverified: depends on Timer.Value recalculating with
  Visible: =false]`; if it does not animate, use `=Parent.Width`.
- An error that requires user action is not a toast: use a modal with an "Understood" button. An
  error that disappears on its own is a lost error. In a loop, aggregate ("12 closed, 3 with an error")
  instead of stacking toasts.
- For form validation, the native `Notify()` is the right use; **a flow return is a toast**.

## 5. Timeout and retry

**Problem.** A `.Run()` that never returns leaves the overlay on screen forever
(`varShowLoading` stuck at `true`).

**Solution, watchdog.** The timer **watches** the operation, it does not run it.

Destination: YAML pasted into Studio (`,` and `;`).

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

No screen guard, on purpose: if the user navigates during the operation, the loading must still
die.

**Retry with a cap**: a "Try again (n left)" button visible only with
`varOperacaoTimeout && varTentativas < 3`; once exhausted, a final-failure label.
**Golden rule: never redo an operation that writes on its own** without an idempotency key: keep
the ids sent in a collection (`colEnviados`) and disable the row's button while the id is in it,
and let the flow refuse a duplicate inside the transaction (`power-automate` skill). A timeout in
the app **does not prove** the flow failed: check the result in the list before repeating.

## 6. Polling with backoff and a stop

For a batch that takes longer than the connector timeout: the flow writes progress to a status
table; the app queries it by a **correlation GUID generated on the client**. Correct anatomy:

1. correlation (GUID on the client, sent to the flow and written to the status table);
2. run guard (only runs with `varLoteEmProcessamento`);
3. **backoff** (the interval grows on every cycle);
4. **attempt cap** (stops for good, even if the backend never answers);
5. explicit shutdown on **every** exit path.

Destination: YAML pasted into Studio (`,` and `;`).

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
        // path 1: finished (3 success, 4 partial, 5 failure)
        Set(varLoteEmProcessamento, false);
        Set(varToastType, If(varPollRegistro.Cod_Status = 3, "success", If(varPollRegistro.Cod_Status = 4, "warning", "error")));
        Set(varToastMessage, varPollRegistro.Descricao);
        Set(varShowToast, true);
        Clear(colEnviados);
        Refresh(Pedido),
        varPollTentativas >= 10,
        // path 2: cap exceeded
        Set(varLoteEmProcessamento, false);
        Set(varToastType, "error");
        Set(varToastMessage, fxMsgTimeoutError & " " & fxMsgTimeoutHint);
        Set(varShowToast, true),
        // path 3: keeps going; restarts the cycle with the new Duration
        Set(varLoteEmProcessamento, false);
        Set(varLoteEmProcessamento, true)
      )
    Repeat: =false
    Reset: =!varLoteEmProcessamento
    Start: =varLoteEmProcessamento
    Visible: =false
```

Trigger (always resets the counter): `Set(varLoteGuid, GUID())`, `Set(varPollTentativas, 0)`, the
flow call with the GUID as a parameter **inside `IfError`**
([flow-call.md](flow-call.md)), and finally `Set(varLoteEmProcessamento, false)` followed by
`Set(varLoteEmProcessamento, true)`. Backoff: 5 s, 10 s, 20 s, 40 s, 60 s, 60 s... The restart by
`Set(false)` followed by `Set(true)` and the `Reset` tied to the negation are the mechanism
`[verified: reference project]`.

**When not to poll.** If the flow responds synchronously within the connector timeout, wait for the
response; if the operation goes past ~5 minutes, notify by email or Teams from the flow itself.
Polling by `LookUp` on a table is much cheaper than polling that calls a flow (each instantiation
costs ~0.6 s).

## 7. Pitfalls

### 7.1 A timer that never stops

`Start` tied to a variable that nobody sets back to `false`, with `Repeat: =true` and an `OnTimerEnd`
with an unconditional `Refresh()`: after the first trigger in the session the app refreshes every
cycle **until the user closes it** (with 50 operators, thousands of requests per hour of pure
waste). Every timer has a **stop rule** in `OnTimerEnd`, `Reset: =!<flag>` and `Start`
tied to the **real state** of what it observes, not to an ad hoc variable.
`[verified: reference project]`

### 7.2 `Duration` without initialization

A variable used in `Duration` that is not born in `OnStart` is `Blank()` on the first render:
undefined behavior. Use `Coalesce(varDuracao, 60000)` or derive the duration from the backoff.

### 7.3 Missing `Reset`

Without `Reset: =!varX` and without forcing `false` and `true` in the caller, the timer becomes a
one-shot per variable lifetime. Clicks in less than the `Duration` are swallowed.

### 7.4 Query inside `Start`

`Start` is re-evaluated on every dependency change: a query there is network in a UI property
(N+1). Use a named formula (see [performance.md](performance.md) §10).

### 7.5 Permanent `Repeat`

`Repeat: =true` on all the time, plus an always-true `Start`, is an infinite loop that starts by
itself. A cosmetic animation by global `Set` every 1.5 s pays graph recomputation 2,400 times
per hour: do not animate, or animate with CSS inside an `HtmlViewer` (zero Power Fx re-evaluation).

### 7.6 Timers fighting over variables

One timer per responsibility; no timer writes a variable that another timer also writes. If you
need to coordinate, use an ownership variable (`If(!varToastAtivo, Set(...))`).

### 7.7 `#` in a formula block

Inside `|-`, `#` is formula text, not a comment: Power Fx rejects it. A comment is `//`.
(Validator: T015 for the single-line case.)

### 7.8 Precision and cost

`Duration` is intent, not a guarantee: the engine is single-threaded and, with a heavy `OnTimerEnd`
and `Repeat`, the real interval is `Duration + body time`. `OnTimerEnd` must be cheap; heavy work
goes in a button or a flow. To measure time, use `DateDiff(varT0, Now(), ...)`.

### 7.9 Hyphen without quotes

`'xx-tim-toast'.Value` with single quotes; without them, `a-b` is subtraction.

## 8. Alternatives to a timer

Before creating one, see whether one of these solves it (all cheaper):

- **Named formula** for "last updated": `frmUltimaAtualizacao = Text(...)` read from a variable
  written by the button. `Now()` is **not** a clock that ticks on its own; seconds running on screen
  need a timer, and the question is whether the app needs that.
- **Manual `Refresh()`**: an "Update" button (zero requests with nobody looking) plus a data-age
  label that turns yellow (`DateDiff(varUltimoRefresh, Now(), TimeUnit.Minutes) > 5`).
- **A flow that signals**: the flow writes the result to a table; the app reads it with
  `Gallery.Items` or a named formula and one `Refresh()` per user event. Native push
  (`SendPushNotificationV2`) or email/Teams for a long batch.
- **`DelayOutput`** instead of a debounce timer (§3).
- **CSS in `HtmlViewer`** instead of a pulse timer.

## 9. Sources

- [Timer control](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-timer)
- [Refresh function](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-refresh)
- [Text input control](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-text-input)
- [Monitor canvas apps](https://learn.microsoft.com/en-us/power-apps/maker/monitor-canvasapps)
- [Accessibility guidelines for timers (WCAG 2.0 time limits)](https://www.w3.org/TR/WCAG20/#time-limits)

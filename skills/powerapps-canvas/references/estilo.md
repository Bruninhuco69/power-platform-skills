# Estilo de telas Canvas

Regras de estilo extraídas de um app de referência com várias telas e mais de mil controles (parse
completo do YAML), generalizadas. O objetivo: tela nova **parece escrita pela mesma mão**. Complementa
[nomenclatura.md](nomenclatura.md), [design-tokens.md](design-tokens.md) e
[ux-componentes.md](ux-componentes.md).

## Sumário

1. [Golden files](#1-golden-files)
2. [Anatomia do arquivo de tela](#2-anatomia-do-arquivo-de-tela)
3. [Layout](#3-layout)
4. [Controles](#4-controles)
5. [Cores e texto](#5-cores-e-texto)
6. [Feedback de operação](#6-feedback-de-operação)
7. [O que não fazer](#7-o-que-não-fazer)
8. [Gate de verificação](#8-gate-de-verificação)
9. [Decisão registrada: Classic + ManualLayout](#9-decisão-registrada-classic--manuallayout)

---

## 1. Golden files

Todo projeto escolhe poucos arquivos-exemplares e **começa tela nova copiando um deles**, nunca
da folha em branco:

| Exemplar | O que demonstra |
|---|---|
| a tela mais enxuta e completa do projeto | anatomia inteira (molde de tela nova) |
| o shell de navegação | menu e "sem acesso", reaproveitável quase inteiro |
| o bloco `Formulas` do objeto App | catálogo de tokens e de mensagens |

O molde do kit é [tela-molde.md](../assets/tela-molde.md). Registre os golden files do projeto
no `00-LEIA-PRIMEIRO.md`.

## 2. Anatomia do arquivo de tela

Ordem de `Children`, que **é** o z-order:

```text
1. cabeçalho (título, usuário, divisor)
2. abas (se houver)
3. filtros
4. KPIs
5. cabeçalhos de coluna + galeria + estado vazio + truncado
6. painel de sem acesso
7. modais
8. loading
9. toast  (sempre o último)
```

Propriedades de tela: `Fill`, `Height`, `Width`, `LoadingSpinnerColor`, `OnVisible`. O `OnVisible`
**limpa o que a tela anterior deixou** (modal, seleção, loading, toast) e recalcula contadores,
sem I/O pesado. Cabeçalho de comentário do arquivo declara a delegação
([delegacao.md](delegacao.md) §11).

Convenções do arquivo-fonte (`.pa.yaml` em `.md`):

- Comentário no topo em `#` (o arquivo é YAML puro; `//` fora de fórmula quebra o parse);
  dentro de fórmula valem `//` e `/* */`.
- Marcadores de comentário padronizados ajudam revisão: `[FIX]` (defeito pré-existente corrigido)
  e `DECIDIR:`. **Nunca apague uma `NOTA:` sem substituir**: ela documenta
  armadilha; se a armadilha sumiu, vira `resolvido: <o quê>`.
- Propriedades em ordem alfabética e sem repetir o padrão do controle (o Studio reordena e apaga
  na primeira colagem).
- Todo valor de propriedade começa com `=`; fórmula de várias linhas em `|-`.

## 3. Layout

- **ManualLayout com `X`/`Y` absolutos, canvas 1920 por 1080.** Não é preferência: é o que os
  blocos canônicos assumem (`X: =Parent.Width - Self.Width - 20`).
- Responsividade por **token condicional** (`fxIsCompact`), não por AutoLayout.
- Centralização por fórmula: `X: =(Parent.Width - Self.Width) / 2`.
- Par de botões de modal se dimensiona sozinho: `Width: =(Parent.Width - fxModalPadding * 3) / 2`.
  Nunca largura mágica.
- `Wrap: =false` em todo `Label` de uma linha (navegação, aba, cabeçalho de coluna, badge, KPI) e
  padding explícito (o padrão 5 desalinha); ver [yaml-pa-formato.md](yaml-pa-formato.md) §9 para o
  que está atestado.

## 4. Controles

Use o que o app **já usa**, **sempre com `@versão`** (T2):

| Função | Controle |
|---|---|
| texto | `Label@2.5.1` |
| botão, aba, forma arredondada | `Classic/Button@2.2.0` |
| container, modal, véu | `GroupContainer@1.5.0` |
| entrada de texto | `Classic/TextInput@2.3.2` |
| seleção | `Classic/ComboBox@2.4.0` |
| lista | `Gallery@2.15.0` |
| data | `Classic/DatePicker@2.6.0` |
| loading | `Spinner@1.4.6` |

Misturar controle moderno e Classic sem plano gera ilhas (botões modernos no menu convivendo
com centenas de clássicos no corpo) e fórmulas que mudam de propriedade (`FontSize` para `Size`).

## 5. Cores e texto

- **Zero `RGBA()` literal em tela nova.** Migrar literais para token é trabalho caro e
  parcialmente manual: não recrie a dívida.
- Ação primária `fxColorPrimary`; destrutiva `fxColorError`; **nunca verde para confirmar
  cancelamento** (defeito real já visto em vários modais).
- Par de botões de modal: esquerdo `fxTxtVoltar` cinza, direito = **verbo da ação**. Raio 8,
  altura 45.
- Toda string visível vem do catálogo `fxMsg*` e `fxTxt*`.

## 6. Feedback de operação

| Situação | Mecanismo |
|---|---|
| retorno de flow ou procedure | **toast** (`varShowToast`, `varToastType`, `varToastMessage`) |
| validação de formulário | `Notify()` |
| operação em andamento | `varShowLoading` + `varLoadingMessage` + overlay |
| botão durante o processamento | `DisplayMode` e `Text` ligados a `varShowLoading` |

`varToastType` é `"success"`, `"warning"` (lote parcial) ou `"error"`; duração por token
(6.000, 12.000 e 15.000 ms), nunca no controle.

## 7. O que não fazer

Resumo; cada item com o porquê e a correção em [anti-padroes.md](anti-padroes.md).

1. `RGBA()` literal em tela.
2. Emoji como semântica (`✅ Sim, Cancelar`).
3. Verde em ação destrutiva.
4. `Notify()` para retorno de flow.
5. Nome automático (`Button1_38`).
6. Propriedade não atestada (PA2108 derruba o bloco).
7. `Timer` com `Repeat` sem regra de parada.
8. Filtro de galeria como controle de acesso.
9. `Patch` direto para operação com regra de negócio.
10. `in` e `Search()` em `Filter` sobre tabela grande.

## 8. Gate de verificação

Antes de dar a tela por pronta (nenhum item é "✅" declarativo: cada um tem comando):

1. `python <pasta-da-skill>/scripts/validar-telas.py <tela>`: parse do arquivo **inteiro** (indentação quebrada
   morre aqui), `;;`, PA2108, `Control` sem versão, `RGBA(` literal, z-order.
2. Grep de `RGBA(` fora de fórmula: zero em tela nova.
3. Grep das propriedades recusadas ([propriedades-inexistentes.md](propriedades-inexistentes.md)):
   zero.
4. `Wrap: =false` nos rótulos de uma linha; padding explícito.
5. Ordem final de `Children`: conteúdo, modais, loading, toast (T016).
6. **Colar no Studio** e conferir que não voltou `PA2108`.
7. *Data row limit* = 1 num clone: a lista continua listando.
8. Fluxo com o flow desligado: toast de erro e overlay fechado.

O `compile_canvas` do MCP não pega o que quebra em runtime, e o validador não substitui o Studio:
o portão é **script mais colar no Studio**.

## 9. Decisão registrada: Classic + ManualLayout

Os guias genéricos da plataforma (DesignGuide e TechnicalGuide do plugin `canvas-apps`) recomendam
controles modernos e AutoLayout responsivo. O código real dos projetos de referência faz o oposto, com
folga (Classic muito à frente do moderno; ManualLayout em todas as telas). **Decidido: seguir o código
real**, porque os blocos canônicos, os tokens e o gate de PA2108 foram construídos sobre Classic
e ManualLayout; adotar o guia genérico reabriria uma classe de erro já fechada e custaria reescrever
o catálogo. Reverter é decisão de ADR (T1), não de preferência. O guia genérico de "estética
ousada" também **não** vale como regra num design system corporativo.

# Anti-padrões: os mais caros

Cada um com o **sintoma silencioso**, o **porquê** e a **correção**. Ordenados por custo. A maioria
dos itens é de falha **calada**: o app não dá erro, só faz a coisa errada. Código `T0xx` =
o que o validador acusa (`python <pasta-da-skill>/scripts/validar-telas.py --codigos`).

## Sumário

1. [Dados e delegação](#1-dados-e-delegação)
2. [Power Fx](#2-power-fx)
3. [Escopo e permissão](#3-escopo-e-permissão)
4. [Interface](#4-interface)
5. [YAML e Studio](#5-yaml-e-studio)
6. [Processo](#6-processo)
7. [Códigos do validador](#7-códigos-do-validador)

---

## 1. Dados e delegação

**D1. `CountRows`/`CountIf` sobre SQL sem declarar o teto.** O card exibe `2.000` como se fosse
o total. *Porquê:* não delegam no conector SQL; o `Filter` delega, a contagem roda no cliente
sobre o que desceu. *Correção:* `If(n >= fxLimiteLinhas, fxTxtTeto, Text(n))`, ou `Sum` de coluna
que vale 1, ou contar no servidor. [delegacao.md](delegacao.md) §3. **T013** (trilha sql-server).

**D2. Filtro de data direto atrás de gateway.** A galeria baixa o teto e filtra no cliente.
*Porquê:* limitação documentada do conector SQL. *Correção:* coluna inteira `Ref_*` no banco;
variável inteira `36524 + DateDiff(Date(2000, 1, 1), x, TimeUnit.Days)`; limite superior `<=`
sem `DateAdd(+1)`; o Limpar reescreve a variável. Nunca `CAST(... AS INT)` (arredonda).
[delegacao.md](delegacao.md) §4.

**D3. `in`/`Search` em `Filter` sobre fonte, e `LookUp(fonte)` em galeria.** Prefira `StartsWith`. `Search` e
`"x" in coluna` delegam só em texto (viram `LIKE '%x%'`, sem índice); `coluna in [lista]`/coleção
não delega no SQL; nunca `LookUp(fonte)` dentro de galeria (consulta por linha, N+1).
*Correção:* `StartsWith`, igualdades, coluna de grupo; rótulo por **coleção** do `OnStart`. **T011**.

**D4. `SearchFields`/`DisplayFields`/`SortByColumns` com coluna que não existe.** Combo vazio,
busca sem resultado, lista sem ordem, sem erro. *Porquê:* `AddColumns` preserva as colunas de
origem. *Correção:* nome lógico (Dataverse) / nome da coluna na fonte (SQL), vindo do ambiente; testar digitando; extrato filtrado **não** prova
esquema. **T014** (Dataverse com prefixo).

**D5. `With`, `Distinct`, `FirstN` entre a fonte e o `Filter`.** Trunca em 500/2.000, sem aviso.
*Correção:* [delegacao.md](delegacao.md) §8.

**D6. `IfError(contagem, 50000)`.** O valor de erro é o teto de agregação: indistinguível de
resultado real. *Correção:* `Blank()` e rótulo de estado degradado.

**D7. Dado de domínio sujo (acento, caixa, `CHAR` com espaço).** Power Fx é accent-sensitive e
nenhuma collation resolve o cliente. *Correção:* normalizar na carga; `Trim` uma vez no `OnStart`.

## 2. Power Fx

**F1. `.Run()` sem `IfError`.** Timeout, 401 ou flow desligado deixa o resultado indefinido; um
`status` em branco passa em `<> "error"` como sucesso. *Correção:* o esqueleto de
[chamada-flow.md](chamada-flow.md) §2 (loading, `IfError`, `Coalesce`, toast). **T018**.

**F2. Overlay de loading preso.** O `Set(varShowLoading, false)` só estava no ramo de sucesso.
*Correção:* fora do `If`, depois do `IfError`; watchdog para o pior caso
([timers-async.md](timers-async.md) §5).

**F3. `Text(<id>)` em parâmetro de flow.** `"1.234"` em pt-BR; o flow não acha o registro (o
encerramento era irreversível). *Correção:* `Text(id, "[$-en-US]0")`.

**F4. Global usada e nunca declarada no `OnStart`.** `Blank() = 0` é falso: filtro comparado a 0
abre a galeria vazia sem erro. *Correção:* toda global nasce no `OnStart`
([app-onstart-molde.md](../assets/app-onstart-molde.md)).

**F5. Named formula que lê variável global.** Não recalcula com `Refresh()`; o KPI não bate.
*Correção:* named formula só de constante e de fonte de dados.

**F6. Global e contexto com o mesmo nome.** O contexto sombreia; o `Set` escreve onde ninguém lê.
*Correção:* `ctx*` para contexto, `var*` para global.

**F7. Dezenas de variáveis numeradas para simular uma lista.** Centenas de `Set` e de `CountRows` por filtro.
*Correção:* coleção (e coluna de agrupamento no banco quando `in` não delega).

**F8. `Set`/`Collect` dentro de named formula, `Navigate` no `OnStart`.** Proibido / aposentado.
*Correção:* `StartScreen`, `OnVisible`.

**F9. `Gallery.AllItems` para contar ou selecionar.** Tabela nova a cada leitura; só enxerga o
carregado. *Correção:* `AllItemsCount`; `colSelecionados` por checkbox.

**F10. `Reset()` de `DatePicker` achando que limpa o filtro.** Não dispara `OnChange`: o controle
mostra uma janela e o `Filter` usa outra. *Correção:* Limpar reescreve a variável.

**F11. `.Value` sobre coleção de registros.** Devolve vazio; a galeria abre vazia ao trocar a
unidade. *Correção:* o nome da coluna (`.Sigla`).

## 3. Escopo e permissão

**E1. `Filter` com escopo organizacional sem o predicado.** Delega perfeitamente, nunca avisa e
**vaza** a rede inteira. *Correção:* o mesmo token (`StartsWith(col, varUnidadeFiltro)`) em toda
galeria e em todo contador. [escopo-e-permissao.md](escopo-e-permissao.md) §5.

**E2. `""` = "todas" sem guarda fail-closed.** Cadastro sem unidade lê a rede inteira; combo
esvaziado cai em "todas". *Correção:* `varSemAcesso` com `(!varTodasUnidades && IsBlank(lotação))`
e `OnChange` que volta à lotação.

**E3. Autorização só na tela.** O menu e o filtro são UX; o cliente pode ser manipulado e a conta
do conector é compartilhada. *Correção:* o flow revalida por ação; o flow lê o chamador do contexto (a tela não envia identidade).

**E4. Permissão por nome de perfil.** Quebra no renome. *Correção:* flag do perfil (`Flg_*`).

**E5. Unidade de gravação = "a unidade que estou olhando".** Grava na unidade errada com perfil
global. *Correção:* a unidade é campo do registro.

**E6. `Patch` para operação com regra de negócio.** Regra no cliente, contornável e duplicada.
*Correção:* flow (decisão A1); conta do conector só com `EXECUTE`.

## 4. Interface

**U1. `RGBA(` literal.** Dívida de cor que só cresce. *Correção:* token `fx*`. **T009**.

**U2. Verde em ação destrutiva; emoji como rótulo.** Confunde e não escala para leitor de tela.
*Correção:* `fxColorError` e verbo explícito; sem emoji.

**U3. `Notify()` para retorno de flow.** Trunca e some. *Correção:* toast de 3 tipos; `Notify`
só para validação de formulário.

**U4. Botão que chama flow sem estado de loading.** Duplo clique grava duas vezes. *Correção:*
`DisplayMode` e `Text` ligados a `varShowLoading`.

**U5. Modal acima do toast ou do loading.** *Correção:* ordem `conteúdo, modais, loading, toast`.
**T016**.

**U6. Timer com `Repeat` e sem parada.** Refresh a cada ciclo até o usuário fechar o app.
*Correção:* regra de parada, `Reset: =!flag`, `Start` amarrado ao estado real e à tela
([timers-async.md](timers-async.md) §7). Toast sem `Reset`: o segundo herda o tempo do primeiro.

**U7. `PressedFill` e `PressedColor` invertidos.** Texto invisível ao pressionar. *Correção:*
`ColorFade(Self.Fill, -30%)`.

**U8. Contraste reprovado** (placeholder cinza claro, branco sobre âmbar, badge pastel com texto
médio). *Correção:* pares de [design-tokens.md](design-tokens.md) §3 e §4.

**U9. Lista truncada sem aviso, galeria `TemplateSize` desconectada do conteúdo, 300+ controles
por tela, 18 `HtmlViewer` por linha.** *Correção:* [performance.md](performance.md) §5 e §7.

**U10. Margens e gutters diferentes por tela; duas famílias tipográficas.** *Correção:* tokens
únicos de layout e de fonte.

## 5. YAML e Studio

**Y1. Propriedade não atestada.** PA2108 derruba o bloco inteiro. *Correção:*
[propriedades-inexistentes.md](propriedades-inexistentes.md). **T008**.

**Y2. `;;` dentro de `.pa.yaml`.** O dialeto da barra de fórmulas colado no YAML não parseia.
*Correção:* `,` e `;` no YAML; `;;` só na barra. **T007**.

**Y3. Propriedade sem `=`, `Control` sem `@versão`, `Control` com fórmula, chave repetida, nome
duplicado.** O Studio recusa. **T002, T004, T005, T012, T006**.

**Y4. Fórmula de linha única com `: ` ou ` #`, ou record literal `{a: 1}` sem aspas.** Quebra o
parse ou **trunca a fórmula em silêncio**. *Correção:* aspas simples do YAML em volta da fórmula
inteira, ou `|-`. **T001, T015**.

**Y5. `#` como comentário dentro de `|-`.** Vira texto e o Power Fx rejeita. *Correção:* `//`.

**Y6. Colar bloco sem renomear o prefixo.** O Studio renomeia para `_1`, `_2`.

**Y7. Validar só com o script.** O validador não é portão suficiente: script **e** colar no
Studio **e** *Data row limit* = 1.

## 6. Processo

**P1. Escrever contra o dicionário em vez do ambiente real.** Nome, tipo e prefixo de coluna
divergem do que existe. *Correção:* `NOMES-AS-BUILT` primeiro (skill `dataverse`).

**P2. "FEITO" sem evidência.** Marcar tarefa pronta sem comando e saída: a regressão volta
(uma correção de escopo foi apagada por um gerador que reescreveu o arquivo). *Correção:* coluna
Evidência (skill `power-platform`).

**P3. Blocos replicados à mão que divergem** (contadores idênticos, menu e loading e
toast repetidos em várias telas). *Correção:* um só lugar quando der (função definida pelo usuário, component
library) e, enquanto replicados, marcar `BLOCO n de N`.

**P4. Documentação desatualizada convivendo com a vigente.** *Correção:* um índice "o que vale" por
pasta e data de revisão.

**P5. Duas trilhas de dados vivas** (SQL e Dataverse) com doc apontando para a errada. *Correção:*
uma trilha ativa por camada, declarada em `trilha_dados` (decisão A4).

## 7. Códigos do validador

| Código | Nível | O que acusa |
|---|---|---|
| T001 | ERRO | YAML não parseia (linha do erro) |
| T002 | ERRO | propriedade sem `=` |
| T003 | ERRO | controle sem `Control:` |
| T004 | ERRO | `Control:` sem `@versão` |
| T005 | ERRO | `Control`/`Variant` com fórmula |
| T006 | ERRO | nome de controle duplicado no conjunto |
| T007 | ERRO | `;;` no YAML |
| T008 | ERRO ou AVISO | propriedade recusada (PA2108); AVISO em outra versão do controle |
| T009 | AVISO | `RGBA(` literal |
| T010 | AVISO | nome fora de kebab-case |
| T011 | AVISO | `Search(`/`in` em `Filter(` sobre fonte que não é `col*` |
| T012 | ERRO | chave duplicada |
| T013 | AVISO | `CountRows`/`CountIf` sobre fonte SQL (trilha `sql-server`) |
| T014 | AVISO | coluna sem prefixo em `DisplayFields`/`SearchFields`/`SortByColumns` (trilha `dataverse`) |
| T015 | AVISO | ` #` após fórmula de linha única |
| T016 | AVISO | z-order de `Children` da tela |
| T017 | ERRO | estrutura inválida (`Properties`/`Children`) |
| T018 | AVISO | `.Run(` sem `IfError(` |
| T020 | AVISO | não é tela YAML, ignorado |
| T022 | ERRO | chave de topo fora do schema |

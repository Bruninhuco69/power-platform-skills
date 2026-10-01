# Modo investigar — "o número não bate"

Use antes de propor qualquer código para: número que diverge entre telas, KPI diferente da galeria,
"está lento", "não atualiza", "gravou mas não aparece". Regra única: **causa raiz provada antes da
correção**. Não chute; se a evidência não fecha, diga o que falta.

## Sumário

1. [A cadeia](#a-cadeia)
2. [Método](#método)
3. [Suspeitos por sintoma](#suspeitos-por-sintoma)
4. [Provas que fecham uma hipótese](#provas-que-fecham-uma-hipótese)
5. [Relatório da investigação](#relatório-da-investigação)

## A cadeia

Percorra do consumidor à origem. Cada elo tem uma pergunta e uma prova.

| Elo | Pergunta | Prova |
|---|---|---|
| 1. Tela | Que controle mostra o número e qual propriedade o calcula? | `Grep` do nome do controle; fórmula exata citada |
| 2. Fórmula | Delega? Usa variável global, named formula ou coleção? Quando reavalia? | tabela de delegação (skill `powerapps-canvas`); Monitor |
| 3. Fonte | A tela lê a fonte certa? Há duas fontes (dev × produção, tabela × view)? | lista das fontes usadas pelos dois números, lado a lado |
| 4. Flow | O flow gravou? O contrato devolveu `success` de verdade? O app refez `Refresh` + recontagem? | histórico de execução; resposta do `.Run()` |
| 5. Procedure | Retornou o código esperado? Gravou na transação? | `EXEC` com dado de teste; resultado |
| 6. Dado | O registro existe, com o valor e a unidade esperados? | consulta direta ao banco/Dataverse |

## Método

1. **Reproduza pelo código.** Ache a fórmula exata de cada número em disputa e cite controle/ação e
   o comando que a localiza (não só `arquivo:linha`, que envelhece).
2. **Compare os caminhos concorrentes.** O mesmo dado lido em dois lugares com filtros, fontes ou
   momentos de cálculo diferentes é a causa mais comum de divergência.
3. **Liste hipóteses** (máx. 5), da mais barata de provar à mais cara. Para cada uma: o que a
   confirmaria, o que a derrubaria.
4. **Prove uma por vez.** Registre resultado (confirmada / derrubada / inconclusiva) com a evidência.
5. **Separe causa de sintoma.** Fórmula "errada" costuma ser sintoma de fonte errada, delegação
   silenciosa ou contador não recalculado depois do flow.
6. **Só então proponha a correção**, com antes → depois, e diga como prová-la (o comando ou o
   passo no Studio que mostra o número batendo).
7. Pergunte-se: "esta causa explica **todos** os sintomas?" Se explica só parte, há uma segunda.

## Suspeitos por sintoma

Consulte antes de abrir o código; comece pelos que custam menos para descartar.

**KPI/contador diferente da galeria**

- Duas fontes (ambiente de desenvolvimento × produção): compare o nome da fonte nas duas
  fórmulas. Não é bug de fórmula.
- `CountRows`/`CountIf` sobre SQL não delega: o número trunca no teto (500/2000) sem aviso.
- Named formula que depende de variável global só reavalia quando a variável muda; `Refresh()`
  não a reexecuta. Contador assim vai para `Screen.OnVisible`.
- Falta `Refresh(<fonte>)` + recontagem depois de gravar (C5).
- `IfError(...; <número>)` que troca o erro por um valor "plausível" (ex.: o teto de agregação).

**Filtro de data não bate ou some linha**

- Filtro de data direto sobre SQL atrás de gateway não delega; use coluna calculada inteira (B2).
- Fuso: UTC no banco × horário local na tela.
- Comparação de data com hora (limite do dia) e `ne null` ausente.

**Galeria vazia / lista incompleta sem erro**

- `SearchFields`/`SortByColumns`/`DisplayFields` com nome de coluna que **existe na fonte mas não é a
  desejada**, ou **nome de exibição em vez do nome lógico** (string entre aspas = lógico; ver `dataverse/references/nomes-e-tipos.md`): não gera erro, gera galeria vazia (N3).
- Choice comparado como texto, Lookup como texto, texto como Choice.
- `in`/`Search` sobre fonte de dados não delega: trunca em silêncio.
- Variável de filtro não inicializada (`Blank() = 0` é falso).

**"Gravou mas não aparece" / "não atualiza"**

- `.Run()` sem `IfError`; sucesso testado como `= "success"` quando `warning` também fecha o modal (C3).
- Id numérico enviado sem `Text(id; "[$-en-US]0")`: no locale pt-BR vira `"1.234"`.
- Parâmetro do trigger fora da ordem (parâmetros são posicionais).
- Flow falhou e o `Catch` não escuta `Skipped`; resposta genérica esconde a causa.
- Escopo por unidade: o flow barrou (autorização por ação) e a tela só mostrou mensagem genérica.

**Lentidão**

- Timer com `Repeat` sem condição de parada; `Refresh()` em cadeia.
- Consulta em `Visible`/`Text` de controle dentro de galeria.
- `OnStart` carrega tudo antes de ser necessário; falta `Concurrent`.
- Medir no Monitor antes de afirmar gargalo: é a única forma confiável de provar custo de dados.

## Provas que fecham uma hipótese

- Monitor do Power Apps: quais chamadas, quantas linhas, quanto tempo.
- Consulta direta no banco (`SELECT COUNT(*)` com o mesmo predicado da tela).
- Histórico de execução do flow (entradas, saídas, qual ação falhou).
- `EXEC` da procedure com dado de teste; resultado de 1 linha.
- Esquema da tabela aberto (não extrato filtrado) para confirmar nome e tipo de coluna.

Afirmação sobre plataforma precisa de link da documentação; se a documentação não diz, escreva
"[não verificado]" e diga como verificar.

## Relatório da investigação

| Hipótese | Prova | Resultado |
|---|---|---|
| H1 … | comando/captura | confirmada / derrubada / inconclusiva |

Depois: **causa raiz** (1 frase), **por que os sintomas aparecem**, **correção** (antes → depois),
**como provar** e **o que não foi investigado**. Com a correção aplicada, rode o portão final
(`portao-final.md`) e mostre o número batendo.

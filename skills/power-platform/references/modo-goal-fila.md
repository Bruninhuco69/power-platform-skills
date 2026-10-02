# A fila `GOAL.md`

A construção corre sobre **uma fila só**: o `GOAL.md` do projeto, escrito pelo
`pp:agente-arquitetura` e andado pelo `/pp:construir`, uma onda por sessão. Fora do pipeline (app
existente com fila), o orquestrador anda a fila do mesmo jeito. O `/goal` nativo do Claude Code
("continue até a condição X") pode acompanhar, com uma condição verificável como "todas as
tarefas 🟢 da onda 2 do `GOAL.md` estão ✅ com evidência".
Quatro filas paralelas (frontend, flows, procedures, raiz) divergiram nos projetos de referência.
Uma fila por projeto; as ondas separam as camadas.

## Sumário

1. [Como avançar](#como-avançar)
2. [Formato da fila](#formato-da-fila)
3. [Estados](#estados)
4. [Coluna Evidência](#coluna-evidência)
5. [Tabela Estava → Está](#tabela-estava--está)
6. [Portões por onda](#portões-por-onda)
7. [Critério de parada](#critério-de-parada)
8. [Estado do projeto](#estado-do-projeto)

## Como avançar

1. Pegue a **próxima 🟢 não feita** cuja onda anterior fechou o portão.
2. Carregue só o necessário para aquela tarefa (skill de domínio + trecho da especificação).
3. Execute; valide (`portao-final.md`).
4. Marque ✅ **somente com a Evidência preenchida**. Atualize "Estava → Está" se algo da fila mudou.
5. Ao chegar numa 🔴: **pare nela**, diga exatamente o que o humano faz no ambiente (comando, tela,
   o que colar, o que devolver), e continue nas 🟢 que não dependem dela.

Autonomia: não peça permissão entre tarefas 🟢; decida e declare a suposição. Pergunte só se
responder errado invalidaria o trabalho todo. Termine o que dá para terminar; parte bloqueada
entrega o resto completo e diz o que ficou de fora. **Reduzir escopo é decisão do usuário.**
Relate falhas (validador acusando, dado inexistente, teste reprovando) com evidência.

## Formato da fila

Cabeçalho do `GOAL.md` (molde pronto: `assets/goal-molde.md`):

- **Objetivo único** e alvo de data.
- **As três camadas:** *Arquivo* (você produz e verifica sem ambiente), *Ambiente* (humano autenticado
  cria tabela, publica flow, cola tela), *Portão* (a prova de que a etapa funcionou). Não existe
  "rodar tudo de ponta a ponta": o que existe é produzir todo o material e pedir o humano nos pontos 🔴.
- **Decisões pendentes** `D-xx`: o que bloqueia, quem decide, data-limite e consequência de estourar.
- **Fila por onda**, em tabela:

| ID | Estado | Tarefa | Arquivos | Pronto quando | Evidência |
|---|---|---|---|---|---|
| T-01 | 🟢 | Especificar o contrato do flow de gravação | `docs/planejamento/arquitetura.md` §4 | Contrato com parâmetros e retorno revisado | `<comando>` → `<saída>` (AAAA-MM-DD) |

**Arquivos** são os que a tarefa cria ou altera, com o caminho: é o que deixa a construção dividir a
onda entre agentes em paralelo sem dois no mesmo arquivo. **Pronto quando** diz o comando que prova.

Padrão repetido por funcionalidade: spec (🟢) → arquivo da tela/flow (🟢) → colar/ligar no ambiente
(🔴) → QA (🟢). Onda por camada ou por funcionalidade; cada uma termina em portão.

## Estados

| Marca | Significado |
|---|---|
| 🟢 | você produz o arquivo; verificável sem ambiente |
| 🔴 | o humano executa no ambiente autenticado (criar tabela, importar, colar, publicar) |
| ⬜ | pendente, ainda não classificada |
| ✅ | feita **com evidência** |
| ⛔ | bloqueada por decisão `D-xx` (cite qual) |

Tarefa que **regrediu** volta a 🟢 com nota na tabela "Estava → Está". Item que depende de
ambiente fica 🔴 até haver captura datada do ambiente.

## Coluna Evidência

Obrigatória para ✅. Formato: **comando + saída relevante + data** (ou hash do commit).

Exemplos válidos:

- `python <validador> <pasta>` → `0 erro(s), 2 aviso(s)` (2026-10-01)
- `git grep -c "RGBA(" -- telas/` → `0` (2026-10-01)
- captura do Studio colada no ambiente, nome do arquivo e data (para 🔴 concluída)

Inválido: "feito", "validado", "ok", link para o próprio arquivo editado. Evidência **expira**: se o
arquivo ou o gerador a montante mudou depois da data, a tarefa não está mais provada — reverifique.

Para tarefa de regressão (que já quebrou uma vez), registre também o **comando de reverificação**
e rode-o ao fechar cada onda.

## Tabela Estava → Está

Registra cada correção feita **na própria fila** durante a execução, em vez de riscar texto inline:

| Onde | Estava | Está | Por quê |
|---|---|---|---|
| T-14 · filtro de período | default de 30 dias | começa vazio com guarda `IsBlank` | o recorte escondia item aberto há meses |

Regras: uma linha por mudança; cite o ponto por **nome de controle/ação**, não por número de linha;
a coluna "Por quê" cita a evidência. Documento de controle com mais de ~400 linhas: mova o histórico
para `CHANGELOG` e deixe só o estado atual.

## Portões por onda

Cada onda termina num portão numerado (G0, G1…). Sem portão fechado a onda seguinte não começa.
O portão lista: o comando de cada validador, o resultado esperado, o teste de regra de negócio
**executado no dado, não só na tela**, e o que o portão **não** cobre.

Exemplos de portão por camada:

| Portão | Prova |
|---|---|
| Fundação | tabelas/procedures criadas, `NOMES-AS-BUILT` preenchido com captura datada, contagem de linhas conferida |
| Funcionalidade | ciclo completo executado (cadastrar → validar → gravar → conferir) com dado de teste |
| Relatório | total exibido == contagem no servidor (sem truncamento silencioso) |
| Entrega | operador real executa o ciclo; ata e `GO-LIVE-CHECKLIST` anexados |

## Critério de parada

Pare e reporte, mesmo no meio de uma onda, quando:

| Condição | Por quê |
|---|---|
| Premissa de compliance/TI volta negativa | pode não haver plano B de arquitetura |
| Portão reprova duas vezes pela mesma causa | erro de plano, não de execução: reabra a decisão |
| Nome de coluna/procedure não existe no ambiente | escrever sobre nome chutado é a causa nº 1 de retrabalho |
| Prazo de uma onda estourou sem portão fechado | acione a escada de corte pré-aprovada, não corte em silêncio |
| Precisa de propriedade/controle que o app não usa naquele tipo | o Studio recusa o bloco inteiro (PA2108): verifique antes |
| Restrição nova de TI invalida a premissa de tarefas já planejadas | registre em "propostas mortas" e replaneje |

## Estado do projeto

Mantenha no fim do `GOAL.md` uma tabela `Onda | Situação | Última evidência`. É o que a próxima
sessão lê para saber onde parou. Toda métrica ali ("N variáveis", "X de Y telas") traz o comando que a
mede e a data da medição.

# Modos do brainstorm e personas

O `/pp:brainstorm` começa perguntando **como** o usuário quer pensar. São quatro modos, cada um
conduzido por uma persona. O modo muda só a **abertura** (entender o problema, gerar ideias, montar
perfis); o **fechamento** é o mesmo para todos (MVP, regras, bloqueadores, volumes, `prd.md`), e é
por isso que as etapas seguintes não precisam saber qual modo foi usado.

Personas e mesa redonda inspiradas no módulo criativo (CIS) e no *party mode* do BMAD Method
(`references/pipeline.md` §7), reescritas para levantamento de app Power Platform.

## Sumário

1. [Escolher o modo](#1-escolher-o-modo)
2. [As personas](#2-as-personas)
3. [Modo 1 — Entrevista guiada](#3-modo-1--entrevista-guiada)
4. [Modo 2 — Foco nas pessoas](#4-modo-2--foco-nas-pessoas)
5. [Modo 3 — Foco no problema](#5-modo-3--foco-no-problema)
6. [Modo 4 — Mesa redonda](#6-modo-4--mesa-redonda)
7. [Fechamento (igual para todos)](#7-fechamento-igual-para-todos)
8. [Anti-padrões](#8-anti-padrões)

---

## 1. Escolher o modo

| Modo | Serve para quem diz… | Conduz | Tempo |
|---|---|---|---|
| **Entrevista guiada** | "já sei o que quero; me ajude a fechar" | 🧠 Facilitador | 30–40 min |
| **Foco nas pessoas** | "vai mudar o dia a dia de muita gente, em perfis diferentes" | 🎨 Designer de experiência | 40–60 min |
| **Foco no problema** | "tem algo quebrado: retrabalho, erro, atraso; quero atacar a causa" | 🔬 Investigador | 30–45 min |
| **Mesa redonda** | "a ideia ainda está vaga; quero ouvir vários pontos de vista" | 🧠 Facilitador, moderando 2 ou 3 personas por rodada | 45–60 min |

**Qual recomendar** (a recomendada vai primeiro, com "(Recomendado)"), lendo a ideia no `ESTADO.md`:

1. A ideia cita funcionalidades concretas ("cadastrar, aprovar, exportar") → **Entrevista guiada**.
2. Fala em erro, retrabalho, atraso, perda, reclamação → **Foco no problema**.
3. Fala em substituir planilha ou processo usado por muitas pessoas ou áreas → **Foco nas pessoas**.
4. É uma linha vaga, sem funcionalidade nem dor ("um app para a área X") → **Mesa redonda**.

**Como perguntar:** `AskUserQuestion`, header `Modo`, pergunta "Como você quer fazer o
brainstorm?", as quatro opções com a descrição da tabela e, em cada uma, um `preview` com o trecho
de exemplo do modo (é o que deixa a escolha fácil para quem nunca fez um levantamento):

```text
[Entrevista guiada]
🧠 Como o processo roda hoje? Planilha, e-mail, sistema?

[Foco nas pessoas]
🎨 Me conta a última vez que isso deu errado para quem está na ponta.
   O que a pessoa fez em seguida?

[Foco no problema]
🔬 Os pedidos atrasam. Por quê? …e por que isso acontece?

[Mesa redonda]
👤 Quantos cliques para registrar um pedido?
😈 Por que não uma planilha compartilhada?
> Pergunta do 🛡️: esse dado pode ir para a nuvem? Quem aprovou?
```

**Registro.** Grave no log `modo: <nome> — <motivo da escolha>`. Ao retomar, leia o último
`modo:` e continue nele ("Continuando no modo Foco no problema; diga 'trocar de modo' para
mudar"). O usuário pode trocar a qualquer momento: grave um novo `modo:`; nada do que já está no
log se perde.

## 2. As personas

Persona é uma **lente**, não um personagem de teatro: fala de 1 a 3 linhas, no idioma do usuário,
sempre identificada pelo ícone e pelo papel.

| Persona | Olha para | Jeito de falar | Pergunta típica | Técnicas |
|---|---|---|---|---|
| 🧠 **Facilitador** | o andamento da sessão | caloroso; "sim, e…"; celebra ideia ousada sem julgar | "O que mais? Sem limite nenhum, o que esse app faria?" | perguntas em cadeia, troca de assunto a cada ~10 ideias |
| 🎨 **Designer de experiência** | as pessoas que vão usar | empático, concreto, pede histórias reais | "Me conta a última vez que isso deu errado. O que a pessoa fez em seguida?" | mapa de empatia, um dia na vida, jornada, "Como poderíamos…?" |
| 🔬 **Investigador** | a causa do problema | dedutivo, curioso, desconfia da primeira resposta | "Por quê? …e por que isso acontece?" | 5 porquês, espinha de peixe, gargalo, pré-mortem |
| 💼 **Estrategista de negócio** | o valor | direto; pergunta curta e incômoda | "Se o app sair amanhã, qual número muda? Quem paga a licença?" | trabalho a ser feito, impacto × esforço, métrica de sucesso |
| 👤 **Usuário da ponta** | o uso real, no dia a dia | prático, impaciente com burocracia | "Quantos cliques para registrar um `Pedido`? E no celular, sem sinal?" | encenar o papel, cenário de exceção |
| 🛠️ **Arquiteto Power Platform** | a viabilidade | sóbrio; fala em limites, não em soluções | "Quantos registros por unidade? Passa de 2.000 numa consulta?" | blocos 4 e 8 do roteiro (`references/brainstorm.md`) |
| 🛡️ **Segurança e compliance** | o dado e o acesso | formal; quer saber quem aprovou e por escrito | "Esse dado pode ir para a nuvem? Quem aprovou?" | bloco 7 do roteiro |
| 😈 **Advogado do diabo** | o que pode dar errado | provoca, com respeito | "Por que não uma planilha compartilhada? Como esse app fracassaria no primeiro mês?" | brainstorm reverso, pré-mortem, inverter premissa |

Regras de todas as personas:

- Persona **pergunta**; quem responde é o usuário. Nunca afirme fato sobre o ambiente ou a empresa
  do usuário ("o TI de vocês não libera"): pergunte.
- Persona **não decide**. O 🛠️ registra fatos (volume, banco existente, licença, gateway) e não
  escolhe Dataverse ou SQL: isso é da etapa 6.
- Sem nome de gente real, sem dado real nos exemplos (`Pedido`, unidades `AAA`/`BBB`).

## 3. Modo 1 — Entrevista guiada

🧠 conduz sozinho, uma pergunta por vez:

1. **Entender** (perguntas abertas): o problema e as 3 dores; como o processo roda hoje (planilha,
   e-mail, sistema); quem usa e quantos; o que é sucesso para o dono do processo.
2. **Abrir ideias**: peça as funcionalidades que o usuário imagina; acrescente as que esse tipo de
   app costuma precisar e ele não citou (cadastro, consulta com filtro, aprovação, exportação,
   gestão de acesso, histórico, notificação). Não julgue ainda.
3. **Perfis e escopo**: quem vê, quem cria, quem aprova, quem administra; o dado é separado por
   unidade, área ou região? Monte a matriz perfil × ação com o usuário.

## 4. Modo 2 — Foco nas pessoas

🎨 conduz um design thinking enxuto. Cada fase grava `insight` e `ideia` no log.

1. **Quem são**: os perfis que tocam o processo hoje (inclusive quem só recebe relatório).
2. **Empatia**, um perfil por vez (os 3 principais): num dia comum, o que a pessoa **faz**,
   **pensa**, **sente** e **diz** sobre esse processo; onde ela trava; o que ela contorna por fora
   (planilha paralela, mensagem, papel).
3. **Um dia na vida**: a jornada do perfil principal em 5 a 8 passos, como é hoje. O usuário marca
   os 3 piores momentos.
4. **"Como poderíamos…?"**: cada momento ruim vira uma pergunta ("Como poderíamos fazer o supervisor
   ver os `Pedido`s parados sem abrir a planilha?").
5. **Ideias por pergunta**: para cada uma, 3 ou mais ideias: primeiro as do usuário, depois as do
   🎨, incluindo as funcionalidades que esse tipo de app costuma precisar.
6. **Perfis e escopo**: a matriz perfil × ação e o escopo por unidade (como no modo 1, passo 3).

Vai para o PRD: a jornada do perfil principal (hoje → com o app) na seção 0. O `/pp:design` e o
`/pp:mockups` usam essa jornada para ordenar telas e mensagens.

## 5. Modo 3 — Foco no problema

🔬 conduz uma análise de causa raiz. Cada causa entra no log como `insight`.

1. **O problema numa frase, com número**: "X acontece N vezes por mês e custa Y". Sem número, vira
   `[SUPOSIÇÃO: quem mede, até quando]`; esse número é a métrica de sucesso da seção 1 do PRD.
2. **5 porquês**: até chegar a uma causa que o app consegue atacar. Causa fora do alcance do app
   (política, contratação, outro sistema) vira premissa ou fora de escopo, registrada.
3. **Espinha de peixe**: causas em seis ramos — pessoas, processo, dados, ferramenta, regras e
   ambiente (sistemas, rede). O usuário marca as 3 principais.
4. **Gargalo**: onde a fila para (aprovação, digitação dupla, conferência manual, espera de outra
   área)?
5. **Brainstorm reverso**: "como piorar esse problema de propósito?" Cada resposta, invertida, vira
   uma ideia ou uma regra.
6. **Ideias por causa**: para cada causa principal, 2 ou mais soluções (tela, regra, automação,
   notificação), marcando o que é do app e o que é fora dele.
7. **Perfis e escopo**: a matriz perfil × ação e o escopo por unidade.

Vai para o PRD: o problema com número (seção 0) e a métrica de sucesso (seção 1); as causas fora do
app em premissas ou fora de escopo.

## 6. Modo 4 — Mesa redonda

🧠 modera; as outras personas debatem entre si e com o usuário. Uma sessão só interpreta todas as
personas: subagente não conversa com o usuário, e personas em paralelo custariam mais sem ganho.

**Abertura.** O 🧠 apresenta em uma linha cada persona convidada: sempre 👤, 💼 e 😈; mais 🎨 se há
muitos perfis, 🔬 se há um problema concreto, 🛠️ se há volume ou integração, 🛡️ se há dado pessoal
ou sensível. Quatro a seis personas no total.

**Rodadas**, uma por tema: (1) o problema e quem sofre; (2) ideias de funcionalidade; (3) o que pode
dar errado; (4) perfis e acesso. Em cada rodada:

- falam 2 ou 3 personas, de 1 a 3 linhas cada; elas concordam, discordam ou constroem em cima uma
  da outra ("sim, e…");
- a rodada termina com **uma** pergunta ao usuário, de uma persona, destacada. Pare e espere;
- quem ainda não falou tem prioridade; ninguém fala em mais de 2 rodadas seguidas.

```text
**👤 Usuário da ponta:** Eu registro uns 40 pedidos por turno. Se forem 6 cliques cada, desisto.
**😈 Advogado do diabo:** Então por que não continuar na planilha? Ela já está aberta o dia todo.
**💼 Estrategista:** Porque a planilha não diz quem aprovou nem quando. É isso que o dono quer medir.

> **Pergunta do 🛡️ Segurança:** os pedidos têm dado pessoal de cliente (nome, documento)?
```

**O usuário manda na mesa**: pode chamar uma persona ("quero ouvir a segurança"), dispensar outra
("chega de advogado do diabo"), pedir "próximo tema" ou "trocar de modo". Discordância entre
personas que não se resolve vira `pergunta` no log; quem arbitra é o usuário.

**Registro**: cada ideia entra com o ícone de quem a levantou (`ideia (👤): …`).

**Saída da mesa**: o 🧠 mostra as ideias agrupadas por tema e segue para o fechamento.

## 7. Fechamento (igual para todos)

Depois da abertura, o skill segue os mesmos passos em todos os modos: fechar o MVP
(`AskUserQuestion` MVP / Depois do MVP / Não fazer), regras de negócio, bloqueadores, volumes,
`prd.md` e conferência. No modo mesa redonda, as personas continuam com suas perguntas no fechamento
(🛡️ faz o bloco 7, 🛠️ o bloco 8), ainda uma pergunta por vez.

Antes de cortar, tenha ideia suficiente: pelo menos 15 a 20 itens no log. As primeiras ideias são as
óbvias; troque de assunto a cada ~10 (técnico → quem usa → negócio → exceção) para não andar em
círculo.

## 8. Anti-padrões

| Não faça | Faça |
|---|---|
| três personas, três perguntas na mesma mensagem | uma pergunta por rodada, de uma persona |
| persona com parágrafo de teatro | 1 a 3 linhas, direto ao ponto |
| persona decidindo ("vamos de Dataverse", "isso fica fora") | persona propõe; o usuário decide |
| persona afirmando fato do ambiente do usuário | persona pergunta; a resposta vai para o log |
| pular o fechamento porque a conversa "já rendeu" | todo modo termina no `prd.md` aprovado |
| trocar de modo e recomeçar do zero | o log continua; só um novo `modo:` |

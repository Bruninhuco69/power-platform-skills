# Brainstorm de projeto Power Platform

Como o Agente Brainstorm (`/pp:brainstorm`, etapa 2 do pipeline) conduz a sessão e o roteiro de
perguntas que a transforma no `prd.md`. Condução inspirada no `bmad-brainstorming` do BMAD Method
(ver `pipeline.md` §7); o roteiro de perguntas é específico de Power Platform. Os quatro modos de
abrir a conversa (entrevista guiada, foco nas pessoas, foco no problema, mesa redonda) e as
personas que os conduzem estão em `references/brainstorm-modos.md`; as regras abaixo valem para
todos.

## Sumário

1. [Como conduzir](#1-como-conduzir)
2. [Técnicas](#2-técnicas)
3. [Registro](#3-registro)
4. [Roteiro de perguntas](#4-roteiro-de-perguntas)
5. [As perguntas que custam caro se vierem tarde](#5-as-perguntas-que-custam-caro-se-vierem-tarde)
6. [Saída da sessão](#6-saída-da-sessão)

---

## 1. Como conduzir

1. **Uma pergunta por vez.** Sem parede de perguntas. Pergunta **aberta** (problema, dor, como é
   hoje, ideias) vai em texto, para o usuário pensar; pergunta **fechada** (MVP ou depois, sim ou
   não, "não sei") vai em `AskUserQuestion`, com a opção recomendada primeiro: é o que deixa a
   sessão fácil para quem nunca fez um levantamento.
2. **Divergir, depois convergir.** Primeiro gere muito (ideias, telas possíveis, riscos, regras),
   sem julgar; só então reduza. Não resuma cedo: a vontade de concluir é o inimigo da divergência.
3. **O facilitador não entrega as respostas.** Pergunte, aprofunde, desafie. Se o usuário pede
   sugestão, ofereça uma recomendada e a razão — uma só.
4. **Suposição não vira fato.** "Acho que" entra como `[SUPOSIÇÃO]` com dono e data para confirmar.
5. **Comece pelo porquê.** Objetivo da sessão em uma frase muda quais técnicas e perguntas valem.
6. **Bloqueador não espera.** Blocos de segurança, infra e licença que voltam sem resposta viram
   pendência D-xx com dono e prazo na hora; sem resposta formal não se começa a modelar.
7. **Ideia que morre barato é vitória.** Se o problema não justifica o app, registre e pare.

## 2. Técnicas

Catálogo do `bmad-brainstorming` (categorias: criativas, profundas, colaborativas, restrições,
futuro especulativo, absurdistas, biomiméticas, quânticas, culturais, introspectivas). As que mais
rendem para Power Platform, em lote de 3 ou 4:

| Quando | Técnica | Uso aqui |
|---|---|---|
| entender a dor real | Five Whys, Laddering | "por que a planilha atual não serve?" até a causa |
| achar o que quebra | Reverse Brainstorming, Failure Analysis, pré-mortem | "como faríamos este app falhar no Go Live?" |
| testar premissas | Assumption Reversal, First Principles | "e se o dado não pudesse sair da rede?" |
| cortar escopo | One Feature Only, Ship in 60 Minutes, $0 Mandate | o que sobra no piloto de uma `Unidade` |
| ver pelo outro lado | Role Playing | operador, supervisor, DBA, segurança, quem paga a licença |
| derivar regras | Question Storming, Morphological Analysis | combinações de perfil × ação × unidade |

Convergir (depois da divergência): **agrupar por afinidade** (muitas ideias soltas), **impacto ×
esforço** (quando o objetivo é agir), **MoSCoW** (escopo: deve, deveria, poderia, não agora),
**ranking forçado** (top N sem empate), **PMI** (testar uma candidata forte).

## 3. Registro

Mantenha um log único da sessão em `docs/planejamento/brainstorm.md`, uma linha por item, com tipo:
`modo` (escolha ou troca de modo), `ideia`, `insight`, `pergunta`, `decisão`, `direção`, `técnica`
(troca de técnica), `suposição`, `pendência` (D-xx). Na mesa redonda, a linha leva o ícone da
persona que levantou o item: `ideia (👤): …`. O que não está no log se perde; o PRD nasce dele, e é ele que permite parar e
retomar a sessão. Ao fim, escreva uma síntese curta só com as decisões e as direções escolhidas.

## 4. Roteiro de perguntas

Cada pergunta tem código (`1.2`) para virar item do PRD. Blocos 7 e 8 são **bloqueadores**; o
bloco 9 fecha com ADR.

### Bloco 0 — Identificação e governança
| Cód. | Pergunta |
|---|---|
| 0.1 | Nome, sigla, unidade piloto, dono do processo (quem decide regra) e solicitante? |
| 0.2 | Quem é o ponto focal de TI, DBA, segurança/compliance, suporte e comitê de mudança? Estão nomeados? |
| 0.3 | Data-alvo e **de onde ela vem**? Há data de corte irrevogável? |
| 0.4 | Quantas pessoas executam em paralelo (dados e flows × telas)? |
| 0.5 | Existe projeto-irmão a usar de molde? Qual tela? |
| 0.6 | Critério de sucesso do dono em 1 frase; "entregue" é substituição total ou piloto em paralelo? |

### Bloco 1 — Negócio e problema
| Cód. | Pergunta |
|---|---|
| 1.1 | Como o processo roda hoje (planilha, app legado, e-mail)? Quem faz, quanto, com que frequência? |
| 1.2 | Quais as 3 dores que justificam o projeto? Qual erro operacional é o mais caro? |
| 1.3 | Quais regras de negócio existem hoje? Liste e numere `RN-xx` com origem (código lido ou pessoa entrevistada). |
| 1.4 | Que defeitos do sistema atual **não** devem ser copiados? |
| 1.5 | Há campos ou estruturas mortas? Quem confirma o descarte? |
| 1.6 | O que está fora de escopo e quem concordou? Quem usa o que cortamos? |
| 1.7 | Há vocabulário controlado, com acento ou sinônimos entre sistemas? |

### Bloco 2 — Usuários, perfis e escopo
| Cód. | Pergunta |
|---|---|
| 2.1 | Quais perfis existem? Para cada ação (ver, criar, editar, baixar, aprovar, exportar, administrar), quem pode? (matriz de permissões) |
| 2.2 | Há assimetrias que parecem erro mas são intencionais? |
| 2.3 | Escopo de dados é por `Unidade`, regional ou área? Um usuário tem mais de uma unidade? Um subconjunto arbitrário? |
| 2.4 | "Ver todas as unidades" vale só para leitura ou também para escrita? |
| 2.5 | Como o usuário ganha acesso (grupo, perfil em tabela, ambos)? Quem provisiona e em quanto tempo? |
| 2.6 | Quantos usuários, em quantas unidades, com que concorrência? |
| 2.7 | Quem administra usuários? Usuário sem cadastro vê o quê? |
| 2.8 | Existem em DEV usuários de teste: um por perfil, um de outra unidade, um multi-unidade? |

### Bloco 3 — Telas e UX
| Cód. | Pergunta |
|---|---|
| 3.1 | Quais telas existem hoje, em que ordem entregar e quais podem ser cortadas (escada de corte)? |
| 3.2 | Resolução alvo e dispositivos (desktop, tablet, celular)? |
| 3.3 | Marca e paleta: cores em hex, ou imagens de referência de onde tirá-las; tema único ou claro/escuro? |
| 3.4 | Há tela molde ou blocos canônicos (toast, loading, modal, menu) do mesmo time? |
| 3.5 | Telas de lista: quais filtros, e quantas linhas esperadas por filtro? |
| 3.6 | Requisitos de acessibilidade; estados por cor sempre têm texto junto? |
| 3.7 | Quais números aparecem como KPI ou contador e que tolerância há a "2.000+"? |
| 3.8 | O app precisa de login próprio ou usa a identidade corporativa? |
| 3.9 | Mockups (`/pp:mockups`): há chave da API da OpenAI? Quem fornece, em que conta e com que teto de custo? |

### Bloco 4 — Dados e volumes
| Cód. | Pergunta |
|---|---|
| 4.1 | Entidades, relacionamentos e chaves de negócio: o que é único de verdade? Há duplicidade permitida? |
| 4.2 | Volume atual e projetado por unidade e por tabela; crescimento mensal; alguma unidade passa de 2.000 linhas? |
| 4.3 | Há tabelas corporativas que o app só lê? Chave, padding de CHAR, colunas, filtro homologado? |
| 4.4 | Onde moram campos calculados (status, vencimento)? |
| 4.5 | Trilha de auditoria: quais eventos, quais campos, quem lê? |
| 4.6 | Dados legados: onde estão, formato, qualidade, quem fornece? Violam constraints novas? |
| 4.7 | Retenção; exclusão lógica ou física; o que significa cada flag de situação? |
| 4.8 | Existe padrão corporativo de nomes de tabela, coluna e procedure? |
| 4.9 | Fuso, formato de data e locale (separador de milhar e decimal)? |
| 4.10 | Existe dicionário **e** as-built? Quem confere um contra o outro? |

### Bloco 5 — Regras de negócio e transações
| Cód. | Pergunta |
|---|---|
| 5.1 | Quais operações escrevem em 2 ou mais tabelas e precisam ser "tudo ou nada"? |
| 5.2 | Quem decide a regra: tela, flow, procedure ou constraint? (uma cópia só) |
| 5.3 | Concorrência: dois usuários no mesmo registro; duplo clique; idempotência? |
| 5.4 | Mensagens ao usuário: quem as escreve? Há vocabulário fechado de códigos de resultado? |
| 5.5 | Quais ações são irreversíveis? Quem pode? Há desfazer? |
| 5.6 | Quais operações são longas ou em lote (importar, exportar)? Limite de payload? |

### Bloco 6 — Integrações e arquivos
| Cód. | Pergunta |
|---|---|
| 6.1 | Sistemas externos: leitura, escrita, por arquivo, API ou banco? |
| 6.2 | Importações: formato real, encoding, separador, aba; sincronização total ou acréscimo? |
| 6.3 | Exportações: CSV (colunas, separador), PDF ou etiqueta (qual conversor?) |
| 6.4 | Quem consome os dados fora do app (Excel, Power Query, Power BI) e com qual identidade? |
| 6.5 | E-mail e notificações: remetente, lista, destinatários? |
| 6.6 | Identidade: qual é a chave do usuário (e-mail, UPN, campo da tabela)? |

### Bloco 7 — Segurança e compliance (**bloqueador**)
| Cód. | Pergunta |
|---|---|
| 7.1 | Existe premissa de que nenhum dado sai da rede interna? Quem a aprovou? Nuvem é aceita, por escrito? |
| 7.2 | Classificação dos dados (pessoais, e-mails, financeiros)? Os artefatos de migração contêm dado real? |
| 7.3 | Isolamento por unidade é **controle de acesso** ou conveniência? Se controle, linha a linha é obrigatória? |
| 7.4 | O conector usa conta de serviço compartilhada? A camada de dados sabe quem é o chamador? |
| 7.5 | Quais permissões de tenant (Graph, Entra) serão negadas? Perguntar **antes** de desenhar. |
| 7.6 | O que a auditoria precisa provar (autoria, quando, o quê)? |
| 7.7 | Quais riscos o dono aceita formalmente? (registrar como risco aceito, com nome e data) |
| 7.8 | Criptografia em repouso, backup, retenção, recuperação de desastre? |
| 7.9 | Pode enviar à API da OpenAI a descrição das telas e a paleta, sem nenhum dado real, para gerar os mockups? Quem aprova? |

### Bloco 8 — Infra, TI, DBA e licenças (**bloqueador**)
| Cód. | Pergunta |
|---|---|
| 8.1 | Ambientes DEV/HML/PRD de Power Platform; publisher e prefixo; solução; quem cria? |
| 8.2 | Banco: SQL Server local ou Azure SQL? Servidor, instância e banco por ambiente? **Há gateway?** |
| 8.3 | Versão e nível de compatibilidade (>= 130 para `OPENJSON`), collation, isolamento? |
| 8.4 | Quem faz DDL, em quanto tempo, com que aprovação? **Quando o banco congela** e o que ainda cabe depois (coluna calculada, objeto novo)? |
| 8.5 | Padrão do DBA para procedures (nome, schema, `GRANT EXECUTE`, conta de serviço)? |
| 8.6 | Licenças: Power Apps (por app ou usuário), Power Automate, conectores Premium (SQL, Dataverse, conversores), capacidade Dataverse, AI Builder? |
| 8.7 | ALM: solução, connection references, variáveis de ambiente; `pac` e `az` disponíveis? |
| 8.8 | Processo de mudança: comitê, janela de deploy, aprovadores, antecedência? |
| 8.9 | Suporte pós Go Live: quem atende, SLA, canal? |
| 8.10 | Já foram tiradas capturas do ambiente real (tabelas, colunas, connection references, procedures)? |

### Bloco 9 — Escolha de tecnologia (**decisão com ADR**)
9.1 Dataverse, SQL Server ou outro (critérios em `matriz-tecnologia.md`)? 9.2 Power BI entra, para
quê? 9.3 Canvas ou model-driven (e por quê)? 9.4 Escrita por `Patch`, flow ou procedure? 9.5 O que
fica **fora** do Power Platform?

### Bloco 10 — QA, UAT e Go Live
| Cód. | Pergunta |
|---|---|
| 10.1 | Critério de aceite: ciclo completo ponta a ponta, com dado real, por operador real? |
| 10.2 | Quem faz UAT, em qual ambiente, com que massa, quando; quem assina? |
| 10.3 | O legado roda em paralelo? Até quando? Plano de desligamento? |
| 10.4 | Plano de rollback (dado e app) e de comunicação? |
| 10.5 | Hypercare, treinamento, manual de usuário? |
| 10.6 | Há massa sintética acima de 2.000 linhas para testar delegação? |

### Bloco 11 — Planejamento
11.1 Quebra em ondas com portões e critérios; 11.2 não-objetivos e escada de corte; 11.3 riscos com
sinal de alerta e ação; 11.4 pendências 🔴 de ambiente: quem, quando, quanto tempo leva; 11.5
definição de pronto por entrega.

## 5. As perguntas que custam caro se vierem tarde

Faça-as no **primeiro dia**; cada uma, respondida depois da tela pronta, costuma significar
redesenho.

| Pergunta | Cód. | Se vier tarde |
|---|---|---|
| Permissões de tenant (grupos, Graph) serão negadas? | 7.5 | desenho de acesso refeito; flow vira chamado de TI |
| Prefixo do publisher e nomes reais do ambiente | 8.1, 8.10 | correções em lote nas telas; script de criação inútil |
| Compliance aceita dado em nuvem, por escrito? | 7.1 | risco de parar o projeto inteiro |
| Há gateway entre a nuvem e o banco? limites | 8.2 | exportação grande e retorno de procedure quebram |
| O DBA vai congelar o banco? quando? | 8.4 | propostas corretas ficam impossíveis |
| Licença premium dos conectores e capacidade | 8.6 | o app não pode ser usado por quem deveria |
| Quem usa o que será cortado do legado? | 1.6 | escopo em disputa na semana do Go Live |
| Escopo por unidade: uma, várias ou todas? | 2.3 | modelo de dados e filtros refeitos |
| Vocabulário real dos dados (acento, status, tipos) | 1.7, 4.6 | combos vazios e botões travados |
| Nomes reais de procedures e connection references | 8.10 | fila de flows reescrita à mão |

## 6. Saída da sessão

- `docs/planejamento/brainstorm.md` (log + síntese de decisões).
- Lista de pendências D-xx com dono e data (entra na seção 2 do `GOAL.md`).
- `docs/planejamento/prd.md` no molde `assets/prd-molde.md`, com o escopo do MVP aprovado pelo usuário.
- Portão: bloqueadores 7, 8 e 9 respondidos formalmente, ou D-xx com dono e prazo aberto.

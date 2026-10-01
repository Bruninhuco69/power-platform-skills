# PRD — <PROJETO>

> Etapa 2 (`/pp:brainstorm`, Agente Brainstorm). Entrada: o log `docs/planejamento/brainstorm.md`.
> Cada requisito tem id estável; o inventário de telas, a arquitetura e o `GOAL.md` citam esses ids.
> Suposição entra como `[SUPOSIÇÃO: quem confirma, até quando]`. Exemplos: `Pedido`, unidades `AAA`, `BBB`.

- **Data:** AAAA-MM-DD · **Dono do processo:** <papel> · **Solicitante:** <papel>

## 0. Visão (uma página)

- **Problema:** como o processo roda hoje (quem, com que ferramenta, com que frequência) e as 3 dores.
- **Quem usa:** perfis, número de usuários e de `Unidade`s (piloto: `AAA`).
- **Resultado esperado:** uma frase; entrega é substituição total ou piloto em paralelo?
- **Como foi levantado:** modo do brainstorm (entrevista guiada, foco nas pessoas, foco no
  problema ou mesa redonda).
- **Jornada do perfil principal** (modo foco nas pessoas): hoje → com o app, em 5 a 8 passos.
- **Problema com número e causas principais** (modo foco no problema): "X acontece N vezes por
  mês e custa Y"; as causas fora do app vão para premissas ou fora de escopo.

## 0.1 Escopo do MVP

| Funcionalidade | MVP / Depois / Não fazer | Requisitos | Quem decidiu |
|---|---|---|---|
| <cadastrar `Pedido`> | MVP | RF-01 | <papel> |

O MVP é o menor conjunto que já resolve a dor principal. Tudo o que é MVP vira requisito P0.

## 1. Objetivo e métricas de sucesso
| Métrica | Como se mede (comando, relatório ou consulta) | Meta |
|---|---|---|

## 2. Perfis e permissões
Permissão por **flag** do perfil (T8), nunca por nome. Sem perfil resolvido = sem acesso.

| Ação | Operador | Supervisor | Analista | Admin |
|---|---|---|---|---|
| ver `Pedido` | | | | |
| criar `Pedido` | | | | |
| editar `Pedido` | | | | |
| exportar | | | | |
| administrar usuários | | | | |

Assimetrias intencionais (parecem erro, mas são regra): <lista>.

## 3. Escopo por unidade
- Escopo: uma, várias ou todas as `Unidade`s por usuário; "ver todas" vale para leitura ou também
  para escrita?
- O escopo é **controle de acesso** ou **conveniência de tela**? Se controle, quem barra (flow ou
  security role) — A3.
- Usuário de teste por perfil, um de outra unidade (`BBB`), um multi-unidade.

## 4. Requisitos funcionais
| Id | Requisito | Perfil | Prioridade (P0/P1/P2) | Regra associada |
|---|---|---|---|---|
| RF-01 | O operador registra um `Pedido` da sua `Unidade` | operador | P0 | RN-01 |

## 5. Regras de negócio
| Id | Regra | Origem (pessoa entrevistada ou código lido) | Dono que confirma |
|---|---|---|---|
| RN-01 | | | |

Defeitos do sistema atual que **não** se copiam: <lista>.

## 6. Requisitos não funcionais
Volume por `Unidade` e crescimento; tempo de resposta aceitável; auditoria (o que provar: autoria,
quando, o quê); retenção; acessibilidade; dispositivos; disponibilidade e suporte.

## 7. Integrações e arquivos
Sistema, direção (lê ou escreve), meio (arquivo, API, banco), formato real, frequência, dono.

## 8. Compliance, licença e infra (premissas)
| Premissa | Aprovada por | Data | Documento |
|---|---|---|---|

## 9. Fora de escopo
Item, motivo, quem concordou.

## 10. Pendências

| # | Pendência | Bloqueia | Dono | Data-limite | Se estourar |
|---|---|---|---|---|---|
| D-01 | <compliance aceita dado na nuvem, por escrito?> | <etapa ou requisito> | <papel> | <data> | <consequência> |

## 11. Rastreabilidade
RF-xx → telas (`inventario-telas.md`) → tarefas do `GOAL.md`. Requisito sem tela ou tarefa é
lacuna; tela ou tarefa sem requisito é escopo escondido.

## Portão de saída
- [ ] Todo requisito com id, perfil e prioridade; toda regra com dono.
- [ ] Matriz de permissões completa; escopo por unidade decidido (A3).
- [ ] Premissas de compliance, licença e infra com aprovador e data, ou `D-xx` com dono.
- [ ] Usuário aprovou o resumo do MVP (frase e data no log).

# Arquitetura — <PROJETO>

> Etapa 6 (`/pp:arquitetura`), escrita pelo `pp:agente-arquitetura`. Registre só o que conflitaria se duas pessoas decidissem sozinhas; o resto fica no código.
> Decisões têm id estável (AR-nn) para as histórias citarem. Padrões já decididos:
> `references/decisoes-padrao.md` — divergir exige ADR.

## 1. Trilha de dados
- **Trilha:** `sql-server` ou `dataverse` (igual a `power-platform.config.json`).
- **ADR:** `docs/decisoes/ADR-001.md` (molde `assets/adr-molde.md`), com os critérios de
  `references/matriz-tecnologia.md` e as respostas dos blocos 4, 7 e 8 do brainstorm.
- **Reabre-se quando:** <condição objetiva>.

## 2. Ambiente as-built (N2 — antes de qualquer tela ou flow)
| Item | Fonte (comando ou captura, data) | Estado |
|---|---|---|
| Ambientes DEV/HML/PRD, publisher e prefixo | | ⬜ |
| Tabelas, colunas e tipos reais (`NOMES-AS-BUILT`) | | ⬜ |
| Procedures (nome, parâmetros, retorno) | | ⬜ |
| Connection references e variáveis de ambiente | | ⬜ |
| Gateway, nível de compatibilidade, collation | | ⬜ |

## 3. Modelo de dados
Entidades (`Pedido`, `Unidade`, …), chaves de negócio, relacionamentos, colunas calculadas,
auditoria. Cada coluna que as telas exigem (`inventario-telas.md`) está aqui.

## 4. Flows e contrato app ↔ flow
| Flow | Chamado por | Parâmetros (posicionais, texto) | Autoriza por ação (flag) | Grava em |
|---|---|---|---|---|

Contrato de retorno: `{status, description, id, url}`; sucesso é `status <> "error"`; `.Run()` em
`IfError` (C1–C5). Entrada externa: trigger HTTP próprio (C6).

## 5. Segurança e escopo
- Quem barra o acesso por `Unidade`: flow ou security role; a tela só filtra (A3).
- Perfis e flags (T8); sem perfil resolvido, sem acesso.
- Riscos aceitos formalmente (dono e data).

## 6. ALM
Solução(ões), variáveis de ambiente, connection references, caminho DEV → HML → PRD, o que vai por
colagem e o que vai por solução (`references/alm-ambientes.md`). Nenhum literal de ambiente (F5).

## 7. Validadores e portões
Quais validadores rodam (`validar-telas.py`, `verificar-fluxo.py`, `lint-procedure.py`) e o que cada
um **não** cobre (`references/portao-final.md`).

## 8. Decisões
| Id | Decisão | Alternativa descartada | ADR |
|---|---|---|---|
| AR-01 | | | |

## Portão de saída
- [ ] ADR da trilha aceito; config e `00-LEIA-PRIMEIRO.md` concordam.
- [ ] Toda coluna do inventário de telas existe no modelo; nomes reais ou marcados "inferido".
- [ ] Contrato app↔flow fechado para cada escrita.

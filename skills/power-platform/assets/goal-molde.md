# GOAL — <PROJETO>

**Objetivo único:** <uma frase: o que existe quando isto termina>.

**Alvo:** <data> · **Fallback:** <data e o que sai> · **Trilha de dados:** <sql-server | dataverse>
(igual a `power-platform.config.json` e `00-LEIA-PRIMEIRO.md`).

Esta é a **única fila de execução** do projeto. As decisões estão em `docs/decisoes/` (ADR) e não se
reabrem sem ADR. O *como* está nas skills `power-platform`, `powerapps-canvas`, `power-automate`,
`sql-procedures` e `dataverse`. Aqui só fica **o que fazer, em que ordem e quem faz**.

---

## 1. As três camadas

| Camada | Quem | O que é |
|---|---|---|
| **Arquivo** | Claude | YAML de tela, flows, scripts, specs, validações. Produzível e verificável sem ambiente |
| **Ambiente** | Humano | Autenticar, criar tabela, aplicar script no banco, colar tela/flow, ligar flow. Exige credencial |
| **Portão** | Ambos | A prova de que a etapa funcionou. Sem portão fechado, a onda seguinte não começa |

Não existe "rodar tudo de ponta a ponta": o Claude produz todo o material e o humano executa os
pontos 🔴.

## 2. Decisões e pendências

| # | Decisão / pendência | Bloqueia | Dono | Data-limite | Se estourar |
|---|---|---|---|---|---|
| D-01 | <premissa de compliance / permissão / banco congelado> | <tarefas> | <papel> | <data> | <consequência> |

## 3. Legenda

🟢 Claude produz o arquivo · 🔴 humano executa no ambiente · ⬜ pendente · ✅ feito **com evidência** ·
⛔ bloqueada por D-xx

## 4. Fila

### Onda 0 — Fundação (portão G0)

| ID | Estado | Tarefa | Arquivos | Pronto quando | Evidência (comando → saída, data) |
|---|---|---|---|---|---|
| T-01 | ⬜ | `git init`, `power-platform.config.json`, `00-LEIA-PRIMEIRO.md` | os três, na raiz | trilha ativa declarada nos três | |
| T-02a | 🔴 | Criar as tabelas com a carga mockup (Dataverse: rodar o construtor com o `plano-dataverse.json`, ou importar o `.xlsx`; SQL: DDL e `carga-mockup.sql` no DEV) | `Backend/<trilha>/carga-mockup.*`, `plano-dataverse.json` | Dataverse: `montar-carga-mockup.py <spec> --conferir <export.json>` com 0 erro(s) (o Dataverse erra a tipagem: conferir antes do dado real); SQL: o script roda sem erro | |
| T-02 | 🔴 | Levantar `NOMES-AS-BUILT` do ambiente real | `AMBIENTE-AS-BUILT/NOMES-AS-BUILT.md` | tabelas, colunas, tipos, procedures, conexões com captura datada | |
| T-03 | ⬜ | ADR das decisões já tomadas | `docs/decisoes/ADR-*.md` | um ADR por decisão fora do padrão | |

**Portão G0:** <comando/prova de cada item da fundação>. **Não cobre:** <o que fica de fora>.

### Onda 1 — <funcionalidade ou camada> (portão G1)

| ID | Estado | Tarefa | Arquivos | Pronto quando | Evidência (comando → saída, data) |
|---|---|---|---|---|---|
| T-10 | ⬜ | Contrato do flow: parâmetros do `.Run()` e retorno | `docs/planejamento/arquitetura.md` §4 | parâmetros posicionais listados; retorno `{status, description, id, url}` | |
| T-11 | ⬜ | Flow `<nome>` | `<pasta de fluxos>/<nome>.json` | `verificar-fluxo.py` com 0 erro(s) | |
| T-12 | ⬜ | Tela `<nome>` | `<pasta de telas>/<Tela>.pa.yaml` | `validar-telas.py` com 0 erro(s) | |
| T-13 | 🔴 | Colar flow no designer e tela no Studio | — | executa sem erro com dado de teste | |
| T-14 | ⬜ | QA da funcionalidade | — | ciclo completo no dado, não só na tela | |

**Portão G1:** <prova>. **Não cobre:** <...>.

## 5. Como o Claude avança

No pipeline, quem anda esta fila é o `/pp:construir`: **uma onda por sessão**, os agentes Canvas e
Automate em paralelo, e o `ESTADO.md` diz quando a construção acabou.

1. Pegue a próxima 🟢 não feita cuja onda anterior fechou o portão.
2. Carregue só o necessário (skill de domínio + trecho da especificação).
3. Execute; valide com o portão final da skill `power-platform`.
4. Marque ✅ **só com a coluna Evidência preenchida**; atualize a tabela da seção 7.
5. Ao chegar numa 🔴: pare nela, diga o que o humano faz no ambiente e siga nas 🟢 independentes.

Não peça permissão entre tarefas 🟢. Pergunte só se errar invalidaria o trabalho todo. Reduzir
escopo é decisão do usuário.

## 6. Condições de parada

| Condição | Por quê |
|---|---|
| Premissa de compliance/TI volta negativa | não há plano B de arquitetura |
| Portão reprova duas vezes pela mesma causa | erro de plano: reabrir a decisão |
| Nome de coluna/procedure não existe no ambiente | escrever sobre nome chutado é a causa nº 1 de retrabalho |
| Onda estoura o prazo sem portão | acionar a escada de corte, não cortar em silêncio |
| Propriedade que o app não usa naquele controle | o Studio recusa o bloco (PA2108) |

**Escada de corte (o que sai primeiro → último):** <1> → <2> → <3>.
**Nunca corta:** trilha de auditoria; autorização por ação no flow; <ciclo principal>.

## 6.1 Propostas mortas

| Proposta | Morreu em | Por quê |
|---|---|---|

## 7. Correções feitas na fila — Estava → Está

| Onde | Estava | Está | Por quê (evidência) |
|---|---|---|---|

## 8. Estado

| Onda | Situação | Última evidência (comando, data) |
|---|---|---|
| 0 | ⬜ | |

Toda métrica desta tabela traz o comando que a mede e a data da medição.

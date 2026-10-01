# Nomes as-built do Dataverse

Contrato de nomes **do ambiente real**. Toda tela e todo flow lê este arquivo antes de escrever
qualquer fórmula. Dicionário de dados, script de criação e plano **perdem** para ele.

> Copie este molde para o caminho de `nomes_as_built` em `power-platform.config.json`. A **parte A**
> pode ser gerada por `skills/dataverse/scripts/extrair-nomes-as-built.py` (marque "gerado — não
> editar"); a **parte B** é escrita à mão. Nome ou tipo não lido fica `?`: nunca copie do dicionário.

## Cabeçalho

| | |
|---|---|
| Ambiente | `<ambiente>` |
| Prefixo do publisher | `<prefixo>_` |
| Extraído em | `AAAA-MM-DD` |
| Comando / consulta | `<URL da Web API ou comando que reencontra os dados>` |
| Quem extraiu | `<função, não nome de pessoa>` |
| Divergências do dicionário | ver parte C |

---

## Parte A — Ambiente (gerada)

### A.1 Tabelas

| Fonte de dados no Power Fx | Nome lógico | EntitySet (Web API/`$batch`) | Chave primária | Nome principal |
|---|---|---|---|---|
| `'<nome no app>'` | `<prefixo>_<tabela>` | `<prefixo>_<tabelas>` | `<prefixo>_<tabela>id` | `<prefixo>_<coluna>` |

Aspas simples são obrigatórias quando o nome tem hífen, espaço ou começa com dígito.

### A.2 Colunas de `<prefixo>_<tabela>`

| Exibição (Power Fx) | Nome lógico (string, OData) | AttributeType | Tipo no Power Fx | Como comparar | Notas |
|---|---|---|---|---|---|
| `<exibição>` | `<prefixo>_<coluna>` | String | Texto | texto = texto | nome principal |
| `<exibição>` | `<prefixo>_<coluna>` | Picklist | Choice | `col = 'col (Tabela)'.Opção` | opções: `Rótulo=valor` |
| `<exibição>` | `?` | `?` | `?` | — | **não lida**: não usar em `SortByColumns`/`DisplayFields` |

### A.3 Choices

| Power Fx | Global? | Opções (rótulo = valor inteiro) |
|---|---|---|
| `'<coluna> (<tabela>)'` | não | `<Rótulo>=<valor>` |

### A.4 Chaves alternativas

| Tabela | Colunas | `EntityKeyIndexStatus` | Verificado em |
|---|---|---|---|
| `<prefixo>_<tabela>` | `<prefixo>_<coluna>` | Active | `AAAA-MM-DD` |

---

## Parte B — Do app (à mão)

### B.1 Conectores (nome no idioma do ambiente)

| Genérico | Neste ambiente |
|---|---|
| `Office365Users` | `<nome traduzido, lido no painel de conexões>` |

### B.2 Alias da fonte no app × tabela

| Alias no app | Tabela (lógico) | Observação |
|---|---|---|
| `'<alias>'` | `<prefixo>_<tabela>` | `<singular/plural como foi adicionada>` |

---

## Parte C — Divergências e lacunas

### C.1 O que o ambiente tem e o dicionário não previa

| Dicionário | As-built | Efeito | Decisão (manter / realinhar / atualizar o dicionário) |
|---|---|---|---|
| `<coluna>` Lookup → `<tabela>` | Texto com `<código>` | Sem integridade; compara texto = texto | `<decisão e ADR>` |

### C.2 Lacunas (não bloqueiam hoje)

| Item | Estado | Como as telas escaparam | Vira bloqueio quando |
|---|---|---|---|
| `<tabela>.<coluna>` | nome lógico truncado / não lido | filtram por nome de exibição; ordenam por outra coluna | alguém precisar ordenar ou pesquisar por ela |

---

## Como atualizar

1. Refaça a exportação (`references/nomes-as-built.md` §3).
2. `python <pasta-da-skill>/scripts/extrair-nomes-as-built.py <export.json> --prefixo <prefixo>_ --saida <este arquivo>` — `0 erro(s)`.
3. Revise o `diff` no Git: toda linha alterada é uma fórmula ou um flow a reconferir.
4. Atualize a data do cabeçalho.

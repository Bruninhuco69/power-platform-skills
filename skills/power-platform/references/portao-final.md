# Portão final

Como provar que está pronto. Um portão só vale se (1) rodou, (2) cobre o formato do que mudou e
(3) já acusou um erro plantado. Esta página diz quais comandos rodar e quais verdes enganam.

## Sumário

1. [Procedimento](#1-procedimento)
2. [Validadores por skill](#2-validadores-por-skill)
3. [O que é verde de verdade](#3-o-que-é-verde-de-verdade)
4. [Verdes falsos conhecidos](#4-verdes-falsos-conhecidos)
5. [Checklist manual](#5-checklist-manual)
6. [Prova final: colar no Studio ou no designer](#6-prova-final-colar-no-studio-ou-no-designer)
7. [Relatório do portão](#7-relatório-do-portão)

## 1. Procedimento

1. Liste as camadas tocadas (tela, flow, procedure, tabela, ALM).
2. Para cada camada, rode **todos** os validadores da tabela abaixo, da raiz do projeto, com o
   `power-platform.config.json` presente (sem ele o script usa defaults e **diz isso** — leia a linha).
3. Cole a **última linha** de cada saída (`N erro(s), M aviso(s)`) no relatório, com a data.
4. Confira que cada validador **leu** algo: a saída lista os arquivos ou o total de itens analisados
   é maior que zero. `0 erro(s)` sobre zero arquivos é verde falso.
5. Rode o checklist manual (seção 5).
6. Faça a prova final (seção 6) ou registre 🔴.
7. Falhou: corrija e rode **todos** de novo. Duas falhas pela mesma causa: reabra o plano.

## 2. Validadores por skill

| Camada | Skill | Comando (da raiz do projeto) | Cobre | Exit |
|---|---|---|---|---|
| Telas | `powerapps-canvas` | `python <skills>/powerapps-canvas/scripts/validar-telas.py <pasta-telas>` | parse do YAML (puro e cercado), PA2108, `RGBA(` literal, `Control:` sem versão, `;;` dentro de YAML (T007 — `;` como separador de argumento **não** é acusado), nomes | 0/1/2 |
| Flows | `power-automate` | `python <skills>/power-automate/scripts/verificar-fluxo.py <pasta-flows>` | envelope e identidade do nó (F002/F003/F019), referências órfãs, `Catch` com `Skipped` (F009), `Response` de 4 campos (F010) e `Terminate` (F015), literal de ambiente (F014). **Não cobre** autorização por ação: isso é teste de negação | 0/1/2 |
| Procedures | `sql-procedures` | `python <skills>/sql-procedures/scripts/lint-procedure.py <pasta-procedures>` | `NOCOUNT`, `XACT_ABORT`, transação, retorno com as 4 colunas (heurística por alias; AVISO P004) | 0/1/2 |
| Protótipo | `power-platform` | `python <skills>/power-platform/scripts/verificar-prototipo.py <pasta> --mockups <spec>` | marca de protótipo, canvas, telas com origem nos mockups, componentes do catálogo, offline, cor só no `:root` (V001–V013). **Não cobre** fidelidade visual: isso é o aceite do usuário | 0/1/2 |
| Skill (se você editou skill) | repositório do plugin | `python tools/lint_skills.py skills/<nome>` | padrão e sanitização | 0/1 |
| Testes dos scripts | repositório do plugin | `python -m pytest tests -q` | fixtures que passam e que falham | 0/1 |

`<skills>` é a pasta onde o plugin está instalado; os scripts também leem as pastas do `config`
quando chamados sem argumento. Cada script tem `--help`; exit `0` = sem erro, `1` = achou erro,
`2` = uso incorreto. Saída por achado: `caminho:linha: ERRO|AVISO CÓDIGO mensagem`.

Mudou só uma camada: rode os validadores dela **e** os das camadas que a consomem (tela que chama o
flow alterado é afetada pelo contrato).

## 3. O que é verde de verdade

Um `0 erro(s)` vale quando as quatro condições se cumprem:

| Condição | Como conferir |
|---|---|
| O validador entende o **formato** | a saída mostra arquivos lidos / itens analisados > 0 |
| Já **acusou** um erro plantado | existe fixture que falha em `tests/<skill>/`, ou você planta um erro e o validador dá exit 1 |
| Rodou sobre a **pasta certa** (trilha ativa) | o caminho analisado é o do `config`, não a trilha arquivada |
| Rodou **depois** da última edição | data da execução ≥ data do arquivo alterado |

Se uma condição falha, o relatório diz "validador X não prova Y" e a camada fica sem veredicto.

## 4. Verdes falsos conhecidos

| Verde falso | Causa | Defesa |
|---|---|---|
| `0 erro(s)` em telas em YAML puro | validador só lia blocos YAML cercados em Markdown; telas sem cerca viram zero arquivos | `telas_formato` no config; confira o total de arquivos analisados |
| Erros falsos na trilha errada | validador de uma trilha rodado sobre a outra | pasta vem do `config`; confira `trilha_dados` |
| Portão "auto-consistente" | gerador errado + saída errada = igual, logo verde | compare com o **gabarito do ambiente**, não gerado × gerado |
| Regerar para "passar" o portão | gerador sobrescreve gabarito corrigido à mão | nunca regere sobre gabarito (`salvaguardas.md` §3) |
| Literais sem aspas em expressão do flow | nenhum portão interpretava a expressão | colar no designer é a prova; lint de expressão quando existir |
| Nome de coluna plausível mas inexistente | schema "parece certo"; não dá erro de compilação, dá galeria vazia | conferência manual contra `NOMES-AS-BUILT` e esquema aberto (nenhum script compara nomes ainda; o T014 só confere o prefixo) |
| Propriedade aceita pelo validador, recusada pelo Studio (PA2108) | validador não tinha a lista de propriedades por tipo de controle | colar no Studio |
| Baseline numérico velho ("0 erro(s)/9 avisos") | documento declara, ninguém rodou | rode e anote a data |
| Validador nunca acusou | nunca foi testado com erro plantado | fixture que falha (P4) |

## 5. Checklist manual

- [ ] Toda função de tabela teve **delegação verificada e declarada por escrito** (T7); teto `2.000+`
      exibido onde há contagem sobre SQL (B3).
- [ ] Nomes de tabela/coluna/procedure conferidos em `NOMES-AS-BUILT` ou marcados "inferido".
- [ ] `.Run()` dentro de `IfError`; sucesso = `status <> "error"`; `Refresh` + recontagem depois de gravar (C3, C5).
- [ ] Id numérico enviado com `Text(id; "[$-en-US]0")`; parâmetro novo no **fim** (C4).
- [ ] Toda variável global nasce no `OnStart`; named formula não depende de variável global (T6).
- [ ] Operação longa tem loading; galeria tem estado vazio; erro tem mensagem ao usuário.
- [ ] Timer tem regra de parada e não roda em tela invisível.
- [ ] Cor/fonte/tamanho só por token `fx*` (T3); nenhum `RGBA(` novo.
- [ ] Autorização **por ação** no flow, flag de segurança nasce ligada (F2, F3); escopo na tela é UX (A3).
- [ ] `Catch` escuta `Failed`, `TimedOut` **e** `Skipped`; `Log` em todo flow (F1, F4).
- [ ] Nenhum `dev*`, servidor, URL de ambiente ou GUID literal (`alm-ambientes.md` §11).
- [ ] Bloco de código diz o **destino** (barra de fórmulas pt-BR × YAML colado).
- [ ] Nenhum dado real, caminho absoluto ou e-mail real em artefato versionado.

## 6. Prova final: colar no Studio ou no designer

Validador estático não substitui o ambiente. Para tela ou flow alterado:

| Alteração | Prova | Registro |
|---|---|---|
| Controle/tela | colar no Studio (Code view); abrir **sem erro de fórmula**, sem PA2108, sem aviso de delegação novo | captura ou texto "colado em <tela>, 0 erros, <data>" |
| `App.OnStart`/named formulas | digitar na propriedade; app roda, variáveis inicializam | idem |
| Flow | colar no designer; salvar sem erro; executar com entrada de teste; conferir saída e histórico | resultado da execução (status, ação que falhou, duração) |
| Procedure | `EXEC` com dado de teste em DEV; 1 linha `status, description, id, url` | saída do `EXEC` |
| Solução | importar em HML; fumaça (`alm-ambientes.md` §10) | versão importada + resultado |

Sem acesso ao ambiente: a tarefa **não** vira ✅; fica 🔴 com o passo exato (o que colar, onde, o que
conferir, o que devolver). Entregue o resto pronto.

## 7. Relatório do portão

```
Portão final — <projeto> — <data>
Camadas: tela | flow | procedure | ...
validar-telas.py        → N erro(s), M aviso(s)   (arquivos lidos: X; prova de que acusa: <fixture ou erro plantado>)
verificar-fluxo.py      → N erro(s), M aviso(s)   (...)
lint-procedure.py       → N erro(s), M aviso(s)   (...)
Checklist manual        → itens ok / itens com ressalva (listar)
Prova no ambiente       → colado em <onde>: <resultado> | 🔴 <passo>
Não coberto             → <o que nenhum portão cobre desta vez>
```

Aprovado: nenhum ERRO, nenhuma camada tocada sem validador, prova no ambiente feita ou 🔴 registrada.
Bloqueado: qualquer ERRO, validador que não leu o formato, camada sem validador, achado crítico aberto.

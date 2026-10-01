# Salvaguardas de processo

Cada salvaguarda nasceu de uma falha real nos projetos de referência. Formato: **regra → por quê →
como verificar**. As falhas estão descritas sem nome de projeto, pessoa ou ambiente.

## Sumário

1. [Trilha única](#1-trilha-única)
2. [Ambiente primeiro](#2-ambiente-primeiro)
3. [Gerador × gabarito](#3-gerador--gabarito)
4. [Evidência executável](#4-evidência-executável)
5. [Documento × disco](#5-documento--disco)
6. [ADR em mudança de trilha](#6-adr-em-mudança-de-trilha)
7. [Git no dia 0](#7-git-no-dia-0)
8. [Premissas de TI e compliance](#8-premissas-de-ti-e-compliance)
9. [Decisão de produto e escopo cortado](#9-decisão-de-produto-e-escopo-cortado)
10. [Tamanho e higiene de documento](#10-tamanho-e-higiene-de-documento)
11. [Capacidade e escada de corte](#11-capacidade-e-escada-de-corte)

## 1. Trilha única

**Regra.** Cada camada tem **uma** trilha ativa, declarada em `00-LEIA-PRIMEIRO.md` (com data) e em
`power-platform.config.json` (`trilha_dados`). A trilha antiga vai para `_arquivo/` com banner
"obsoleta", não fica ao lado.

**Por quê.** Um documento declarava uma pasta "congelada — nunca editar"; depois ela foi
editada com uma reforma inteira, enquanto a trilha realmente ativa ficou para trás. A
skill de projeto só conhecia a trilha errada e havia quatro filas de execução simultâneas.

**Como verificar.**

```bash
git log -1 --format=%cs -- <pasta-da-trilha-A>
git log -1 --format=%cs -- <pasta-da-trilha-B>
```

Se a pasta "congelada" tem commit mais novo que a "ativa", o documento mente: pare e resolva (ADR).
Antes de editar, confira que a pasta alvo é a ativa **no disco**, não só no texto.

## 2. Ambiente primeiro

**Regra.** Nenhuma tela ou flow antes de `NOMES-AS-BUILT` (ambiente, tabelas, colunas, tipos,
procedures, conexões) estar preenchido a partir do **ambiente real**, com captura datada. O
dicionário, o script de criação e o plano **perdem** para ele (N1, N2).

**Por quê.** Tela escrita contra o dicionário exigiu correções em lote no Studio; um flow gravava em
colunas que não existiam; procedures documentadas com um prefixo tinham outro no banco; connection
references documentadas diferiam das reais; um nome de coluna truncado se espalhou por todo o repo.

**Como verificar.** Para cada nome novo: `grep -n "<nome>" <nomes_as_built>`. Ausente = inferido,
marque "inferido" e abra pendência. Antes de afirmar "a coluna não existe", abra o **esquema da
tabela** (N3). Nome truncado = pendência aberta, nunca "completar de cabeça".

**Provas de ambiente antes de escrever corpo de procedure:** nível de compatibilidade, collation,
identidade do chamador (`User().Email` retorna o esperado?), `OUTPUT INTO` com trigger. Verifique com
`SET PARSEONLY ON` primeiro e DDL descartável em DEV.

## 3. Gerador × gabarito

**Regra.** (a) Saída de gerador só em `dist/`, com cabeçalho "gerado — não editar". (b) O que foi
**colado no ambiente** e funcionou é **gabarito**: pasta `gabarito/` imutável. (c) Correção manual
vai para a **entrada** do gerador, nunca para a saída. (d) Antes de regerar, tag no Git. (e) O
portão de regeração compara gerado × `dist/`, nunca gerado × gabarito.

**Por quê.** Um portão mandava rodar o gerador, que abriria o arquivo em modo escrita e apagaria a
única evidência de ambiente. Uma correção entregue foi apagada quando o gerador foi reescrito e
ninguém percebeu; o gerador estava mais velho que a saída e regerar apagaria várias correções em
silêncio, com os dois portões ainda em `0 erro(s)`.

**Como verificar.**

```bash
git status --short -- gabarito/ dist/     # gabarito: nenhuma mudança sem ADR
git log --oneline -3 -- gabarito/
```

Gerador mais velho que a saída, ou gerador ausente do disco (só bytecode): trate a saída como
gabarito e **não** regere. Faça round-trip: gere em pasta temporária e compare com `dist/`.

## 4. Evidência executável

**Regra.** ✅ exige comando + saída + data (`modo-goal-fila.md`). Validador sem teste que planta o
erro não prova nada (P4): todo portão tem fixture que passa e fixture que falha com o código esperado.
Evidência **expira** quando o arquivo muda depois dela.

**Por quê.** Uma tarefa marcada ✅ "feita" tinha regredido e a folha de execução não sabia; outra
foi deixada com itens de fora de propósito para não marcar um defeito como fechado sem estar. Um
fluxo com literais sem aspas passou por três portões porque nada interpretava a expressão.

**Como verificar.** Escolha 3 ✅ ao acaso e rode o comando da coluna Evidência. Divergiu = a fila não
é confiável; reverifique a onda inteira.

## 5. Documento × disco

**Regra.** Documento que declara número (contagem de telas, baseline de erros, "N variáveis") traz
o comando que o mede e a data (P5). Citação de caminho precisa existir. Citação por **nome de
controle/ação**, não por número de linha.

**Por quê.** Contagens de documentos de controle foram corrigidas várias vezes (contagem de
variáveis, percentuais de cobertura); afirmações como "a pasta está vazia" e "dois arquivos idênticos" ficaram
no documento depois de falsas; caminhos de scripts mudaram de pasta e o orquestrador ainda apontava
o antigo.

**Como verificar.**

```bash
# caminhos citados que não existem (ajuste o padrão à convenção do projeto)
grep -ohE "[A-Za-z0-9_./-]+\.(md|py|json|sql|yaml)" 00-LEIA-PRIMEIRO.md GOAL.md | sort -u | while read f; do [ -e "$f" ] || echo "FALTA: $f"; done
```

Número sem comando ao lado: peça o comando ou rode-o e substitua. Baseline velho: meça de novo e anote a data.

## 6. ADR em mudança de trilha

**Regra.** Mudança de trilha de dados, contrato app↔flow, layout ou qualquer item de
`decisoes-padrao.md` exige ADR (`assets/adr-molde.md`) **antes** de mexer, e atualiza no mesmo commit:
`00-LEIA-PRIMEIRO.md`, `power-platform.config.json`, a skill de projeto e a fila.

**Por quê.** A tecnologia trocou várias vezes, nenhuma com registro: ninguém sabia a
trilha vigente nem por que as anteriores morreram. Propostas "certas" foram invalidadas por uma
restrição de TI que chegou depois, e a fila não registrava as propostas mortas.

**Como verificar.** `git log -- docs/decisoes/` mostra um ADR por mudança; o config e o
`00-LEIA-PRIMEIRO.md` concordam sobre a trilha.

## 7. Git no dia 0

**Regra.** `git init` antes da primeira linha; branch por onda; tag por entrega; `.gitignore` para
`dist/` quando gerado, dados de carga, `.venv` e arquivos com dado real. Nada de `.rar`/`_antes/` como
backup. Antes de qualquer regeração ou refatoração em massa, tag.

**Por quê.** Sem repositório, os backups eram arquivos compactados manuais e uma pasta `_antes/`
vazia; regressões como a da seção 3 não podiam ser detectadas por diff.

**Como verificar.** `git rev-parse --is-inside-work-tree` → `true`; `git tag` lista as entregas.

## 8. Premissas de TI e compliance

**Regra.** Premissa de compliance, licença, gateway, permissão de tenant e congelamento de banco
vai para a tabela de decisões e pendências `D-xx` do `GOAL.md` (seção 2) com **dono, data-limite e consequência de estourar**. Perguntas de bloqueio
(segurança, TI/DBA/licença) vêm **antes** de desenhar. A primeira pergunta de correção é "isso cabe
no que ainda é permitido?".

**Por quê.** Uma premissa de compliance apareceu como "bloqueia o projeto inteiro" em vários documentos
e continuou sem resposta registrada. Permissão de tenant negada e banco congelado chegaram tarde e
invalidaram propostas; o congelamento cedeu depois só para coluna calculada.

**Como verificar.** Cada pendência tem os três campos; as vencidas aparecem no estado da fila.

## 9. Decisão de produto e escopo cortado

**Regra.** Item que muda o que o usuário vê é "decisão de produto" e precisa de aprovação com
dono de negócio; apagar código dependente exige a referência da aprovação no commit. Todo
não-objetivo registra **quem usa hoje** e **quem aceitou o corte**; consulte o dado vivo antes de cortar.

**Por quê.** Um módulo foi cortado do escopo em quatro documentos sem combinar com a operação — era
o recurso de maior volume da unidade-piloto. Dados de unidades extras foram apagados antes da
aprovação exigida pelo próprio plano.

**Como verificar.** `grep -n "aprovad" GOAL.md` e a linha do não-objetivo com "quem usa/aceitou".

## 10. Tamanho e higiene de documento

**Regra.** Documento de controle abaixo de ~400 linhas; histórico em `CHANGELOG`; obsoleto vai
para `_arquivo/` com banner; "Estava → Está" no lugar de texto riscado inline. Especificação e
histórico não se misturam.

**Por quê.** Documentos enormes misturavam especificação e histórico, e arquivos que se
declaravam obsoletos continuaram na árvore sendo lidos como referência.

**Como verificar.** `wc -l 00-LEIA-PRIMEIRO.md GOAL.md` e `grep -rl "obsoleto\|superseded" .`

## 11. Capacidade e escada de corte

**Regra.** Declare a capacidade real (quem, quantas horas, quantos 🔴 de ambiente e o tempo de
cada). Tenha uma **escada de corte pré-aprovada** (o que sai primeiro) e a lista do que **nunca**
corta (trilha de auditoria, revalidação de permissão no flow, o ciclo principal).

**Por quê.** O prazo foi planejado para uma equipe e executado por uma sessão de IA e um humano
para o ambiente; os 🔴 viraram gargalo sem dono nem tempo estimado.

**Como verificar.** A fila lista, para cada 🔴, dono e estimativa; o cronograma cita a escada.

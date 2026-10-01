# Lições de campo: Canvas

Padrões que apareceram em apps reais e que ainda não cabiam numa regra isolada das outras
referências. Cada lição traz o que aconteceu, em termos genéricos, e a regra ou o arquivo que a
previne. Não é regra por si: o que vale está nos arquivos citados.

## Sumário

1. [Migração em lote para tokens tem um resto que não se automatiza](#1-migração-em-lote-para-tokens-tem-um-resto-que-não-se-automatiza)
2. [Padrão unificado entre telas: aplique a folha de decisão e registre as exceções](#2-padrão-unificado-entre-telas-aplique-a-folha-de-decisão-e-registre-as-exceções)
3. [Um app que cresce sem folha de decisão diverge em todos os eixos](#3-um-app-que-cresce-sem-folha-de-decisão-diverge-em-todos-os-eixos)
4. [Afirmação sobre o disco, repetida em vários arquivos, envelhece](#4-afirmação-sobre-o-disco-repetida-em-vários-arquivos-envelhece)
5. [O validador sobre um projeto existente: o que esperar](#5-o-validador-sobre-um-projeto-existente-o-que-esperar)
6. [Uniformizar separadores sem olhar o destino do arquivo](#6-uniformizar-separadores-sem-olhar-o-destino-do-arquivo)
7. [Regra de catálogo de texto sem checagem automática se perde](#7-regra-de-catálogo-de-texto-sem-checagem-automática-se-perde)

---

## 1. Migração em lote para tokens tem um resto que não se automatiza

| | |
|---|---|
| **O que aconteceu** | Num app grande, a troca de literais `RGBA()` por tokens `fx*` removeu mais da metade dos literais por script. O que sobrou estava dentro de fórmulas multilinha (`Switch`/`If` de status), onde a troca automática não é segura. No mesmo app, quase todos os nomes automáticos de controle ficaram como estavam: renomear em lote só é seguro com o Studio aberto para conferir as referências, e só um controle foi renomeado (o do timer que se corrigia). Dos retornos de flow que usavam `Notify()`, uma fração virou toast; o restante era validação de formulário, uso correto. |
| **Previne** | `design-tokens.md` §1 item 4 (o que restar em fórmula multilinha migra para `fxBadge*`, conferido à mão), `nomenclatura.md` (nome desde a criação, para não precisar renomear depois) e `chamada-flow.md` (`Notify()` é para validação de formulário). |

## 2. Padrão unificado entre telas: aplique a folha de decisão e registre as exceções

| | |
|---|---|
| **O que aconteceu** | Toast de retorno de flow, overlay de loading, par de botões de modal, botões de filtro, cabeçalho de coluna, contador de seleção e estado vazio viraram **blocos idênticos entre telas**, com geometria e cor vindas de token. A folha de decisão foi aplicada com poucas exceções documentadas, onde a opção ideal exigiria reposicionar cada controle em `X`/`Y` absoluto: tamanho padrão do card de modal, fechar por clique no véu, altura de linha da galeria. Em duas telas, o z-order também foi corrigido (modal acima do toast; modal acima do loading). |
| **Previne** | `ux-componentes.md` e `ux-feedback.md` (blocos canônicos), `app-formulas-tokens.md` (geometria e cor por token) e `validar-telas.py` T016 (z-order). Em ManualLayout, o que depende de posição absoluta é exceção declarada, não esquecimento. |

## 3. Um app que cresce sem folha de decisão diverge em todos os eixos

| | |
|---|---|
| **O que aconteceu** | A auditoria visual tela a tela de um app sem folha de decisão achou: um único controle de acessibilidade em centenas de controles; nenhum uso de `Live` ou `Role`; valores positivos de `TabIndex` espalhados; mais de dez pares de cor reprovando o contraste (placeholder, badge, branco sobre verde e sobre âmbar, bordas de input e divisor abaixo de 3:1); várias margens laterais, várias variantes de cabeçalho e gutters de larguras muito diferentes; duas famílias tipográficas sem regra; `TemplateSize` desconectado do conteúdo (centenas de pixels para uma linha de dezenas); uma tela de limpeza com linguagem de loading própria; três verdes diferentes para "ação positiva"; o botão de confirmação destrutiva pintado de verde; e uma tela com centenas de controles que deveria ser três. |
| **Previne** | `design-tokens.md` (famílias de token e contraste medido), `acessibilidade.md`, `ux-componentes.md` e `ux-feedback.md` (confirmação destrutiva usa `fxColorError`), `performance.md` §7 (controles por tela) e `anti-padroes.md` (U9, tela grande). Use esta lista como roteiro de auditoria. |

## 4. Afirmação sobre o disco, repetida em vários arquivos, envelhece

| | |
|---|---|
| **O que aconteceu** | A documentação de um projeto repetia, em quase uma dezena de arquivos, três afirmações sobre o disco que estavam desatualizadas: que duas telas eram byte-idênticas (falso, com tamanhos e hashes diferentes; o efeito grave era mandar os agentes **ignorarem** a tela mais atualizada), que um polling "nunca parava" (já corrigido) e que uma pasta estava vazia (já tinha arquivos). |
| **Previne** | `anti-padroes.md` P2 e P4 e `decisoes-padrao.md` P5: toda afirmação sobre o disco leva **o comando que a mede** (por exemplo `md5sum a.md b.md`) e a data; `arquivo:linha` não é evidência permanente. |

## 5. O validador sobre um projeto existente: o que esperar

| | |
|---|---|
| **O que aconteceu** | Rodado em modo só-leitura sobre dois apps reais, o validador deu **zero erros nas telas**. Os poucos "erros" vieram de guias genéricos do plugin da Microsoft copiados para a pasta de telas (snippets ilustrativos com `Control` sem versão e chaves repetidas): falsos positivos de documentação. Os avisos típicos de um app grande: `RGBA(` literal em massa, nomes fora de kebab-case (os automáticos do Studio e os blocos compartilhados com sufixo `_1`), `.Run(` sem `IfError`, `Search`/`in` em `Filter`, `CountRows` sobre SQL já com rótulo de teto, colunas sem prefixo em `DisplayFields`, e arquivos de documentação ou de barra de fórmulas ignorados (T020). Um validador que só lê blocos cercados dá `0/0` em YAML puro (verde falso); este lê os dois formatos. |
| **Previne** | `SKILL.md` (seção Scripts): mantenha guias fora da pasta de telas ou marque o bloco com `# validador: ignorar`; trate cada aviso como decisão escrita, não como ruído. |

## 6. Uniformizar separadores sem olhar o destino do arquivo

| | |
|---|---|
| **O que aconteceu** | Num contrato de dados, o objeto App (barra de fórmulas pt-BR: `;` e `;;`) foi tratado com o mesmo separador das telas (YAML: `,` e `;`), e várias páginas foram convertidas indevidamente. A primeira versão do contrato errou isso, e a correção exigiu conferir contra a trilha anterior. |
| **Previne** | `decisoes-padrao.md` §3 e `yaml-pa-formato.md` §2: o separador é do **destino**, não do projeto; antes de "uniformizar" um lote de arquivos, confira o destino de cada um. |

## 7. Regra de catálogo de texto sem checagem automática se perde

| | |
|---|---|
| **O que aconteceu** | Apesar da regra de catálogo de texto, as telas de um app continuaram com strings literais (`"Cancelar"`, `"Salvar"`, títulos de modal, placeholders). Botões de salvar e de confirmar também ficaram sem estado de loading (duplo clique grava duas vezes), e os mesmos blocos (contadores, menu, loading, toast) estavam replicados à mão em várias telas. |
| **Previne** | `design-tokens.md` §1 item 6 (texto por token `fxTxt*`/`fxMsg*`) e `chamada-flow.md` (todo botão que grava liga `varShowLoading`). O validador não pega string literal: faça `grep -n 'Text: ="'` na definição de pronto e centralize blocos repetidos (função definida pelo usuário ou component library) quando der. |

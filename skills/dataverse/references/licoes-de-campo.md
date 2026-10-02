# Lições de campo: Dataverse

Padrões que apareceram em projetos reais e que ainda não cabiam numa regra isolada das outras
referências. Cada lição traz o que aconteceu, em termos genéricos, e a regra ou o arquivo que a previne.
Não é regra por si: o que vale está nos arquivos citados.

## Sumário

1. [Contorno que faz o erro sumir não é correção](#1-contorno-que-faz-o-erro-sumir-não-é-correção)
2. [Perfil lido de uma Choice devolve o rótulo, não o registro](#2-perfil-lido-de-uma-choice-devolve-o-rótulo-não-o-registro)
3. [Export de dados é lido do zip, não aberto](#3-export-de-dados-é-lido-do-zip-não-aberto)
4. [Coluna sem dono é coluna morta](#4-coluna-sem-dono-é-coluna-morta)
5. [Mapa fonte do app → tabela é do app, não do ambiente](#5-mapa-fonte-do-app--tabela-é-do-app-não-do-ambiente)
6. [Data nula e o limite mínimo da plataforma](#6-data-nula-e-o-limite-mínimo-da-plataforma)
7. [Metadado e carga pela Web API](#7-metadado-e-carga-pela-web-api)
8. [A importação da planilha trocou dia e mês](#8-a-importação-da-planilha-trocou-dia-e-mês)

---

## 1. Contorno que faz o erro sumir não é correção

| | |
|---|---|
| **O que aconteceu** | Ao corrigir uma tela escrita contra o dicionário, três ajustes fizeram o erro desaparecer sem tocar na causa: um combo passou a listar a tabela de vínculo no lugar da de catálogo (com um filtro tautológico `X = X`); um rótulo foi "virado" para depuração porque o `Items` apontava para a tabela errada; um seletor de pessoa passou a exibir um campo qualquer (`DisplayFields: ["City"]`) no lugar do nome, porque os campos do conector Office 365 (`DisplayName`, `Mail`) não levam prefixo e o nome usado não resolvia. |
| **Por quê é perigoso** | A tela deixa de acusar, mas passa a mostrar o dado errado, e o contorno vira padrão copiado. |
| **Previne** | `references/nomes-as-built.md` (a coluna certa vem do ambiente) e `references/nomes-e-tipos.md` §3 (conector que não é Dataverse usa o campo do conector). Se o erro some depois de trocar a fonte ou a coluna, volte ao as-built antes de aceitar. |

## 2. Perfil lido de uma Choice devolve o rótulo, não o registro

| | |
|---|---|
| **O que aconteceu** | `Set(varPerfil; varUsuario.perfil)` sobre uma coluna **Choice** devolve o rótulo da opção, não o registro da tabela de perfis. Todo `varPerfil.pode_*` do menu e das telas lia propriedade de um texto. A correção foi resolver o perfil por `LookUp(<tabela de perfis>; nome = Text(varUsuario.perfil))`. O mesmo ponto frágil, um acento diferente entre o rótulo e o nome do perfil, deixou o app abrir vazio, sem erro. |
| **Previne** | `references/nomes-e-tipos.md` §6.1 (Choice não é registro) e `references/seguranca.md` §6 (permissão por flag, sem perfil resolvido = sem acesso). Em `powerapps-canvas`, `references/escopo-e-permissao.md`. |

## 3. Export de dados é lido do zip, não aberto

| | |
|---|---|
| **O que aconteceu** | A única fonte de "esquema" era um export de dados do Dataverse para Excel, de centenas de MB, uma planilha por tabela, com poucas linhas de amostra. Abrir o arquivo inteiro travava o leitor comum. O cabeçalho de cada planilha (os nomes lógicos) foi lido direto do `xl/workbook.xml` e da primeira linha de cada `xl/worksheets/sheetN.xml` dentro do zip. O export também omitia tabelas que o app usava, e não trazia o tipo (Choice ou texto). |
| **Previne** | `references/nomes-as-built.md` §1 e §3: o export de dados não é dicionário; use `scripts/extrair-nomes-as-built.py`, que parte do metadado. Se só o export existe, trate toda coluna que ele não mostra como lacuna (`?`), dita como inferência. |

## 4. Coluna sem dono é coluna morta

| | |
|---|---|
| **O que aconteceu** | Numa tabela de monitoramento de flow, várias colunas do registro pai estavam sempre nulas, e uma nova versão do flow deixou de preencher colunas que a anterior preenchia (ação com erro, JSON enviado e recebido, mensagem): o indicador de HTTP ficou nulo no relatório para as execuções da versão nova. |
| **Previne** | `references/modelagem.md` §10: defina quais colunas **todo** flow preenche e documente quem preenche cada uma. |

## 5. Mapa fonte do app → tabela é do app, não do ambiente

| | |
|---|---|
| **O que aconteceu** | O nome da fonte de dados no Power Fx (alias) difere do nome lógico e do de exibição, e o mapa entre eles foi montado à mão, por correlação de nome. Duas fontes, uma no singular e outra no plural, apontavam para a mesma tabela. |
| **Previne** | `references/nomes-e-tipos.md` §5. O mapa vale como as-built **do app**, não do ambiente: leia o painel de dados do app e registre a data. |

## 6. Data nula e o limite mínimo da plataforma

| | |
|---|---|
| **O que aconteceu** | Um flow de recebimento trocava a data nula de origem (`0001-01-01`) por `1753-01-01` antes de gravar. O motivo provável é o limite mínimo de data da plataforma `[não verificado: a causa não foi registrada]`. |
| **Previne** | Ao receber data de sistema externo, decida e registre como a data nula é gravada (vazio ou um sentinela) em vez de deixar o valor mínimo da origem passar sem critério. Ver `skills/power-automate/references/dataverse-batch-upsert.md`. |

## 7. Metadado e carga pela Web API

Um flow que cria o esquema e carrega as linhas pela Web API (um plano lido por um intérprete, o mesmo
desenho do construtor do kit) juntou estes pontos antes da primeira execução. A coluna Origem diz de
onde cada um vem: o Learn, ou o que se viu no projeto de referência.

| Ponto | Regra | Origem |
|---|---|---|
| Componente fora da solução | `MSCRM.SolutionUniqueName` em toda criação de metadado | Learn |
| `PUT` de coluna | substitui a definição inteira: `GET` da coluna, mude o campo, `PUT` de tudo sem `@odata.context`, com `MSCRM.MergeLabels: true` para não apagar o rótulo de outro idioma | Learn |
| Numeração automática numa coluna com dados | a coluna nasce texto, a carga grava os códigos, depois `PUT` com `AutoNumberFormat` e `SetAutoNumberSeed` acima do último código | Learn; aceitação do `PUT` não verificada |
| Opção de Choice com `Value: null` | a plataforma numera pelo prefixo de valor do publisher. Quem não fixa o inteiro lê a Choice (`$expand=OptionSet,GlobalOptionSet`: a local responde num, a global no outro) e casa pelo rótulo | Learn; numeração não verificada |
| Coluna sobre Choice global | `GlobalOptionSet@odata.bind: "/GlobalOptionSetDefinitions(Name='x')"` | Learn |
| Chave alternativa | o índice é assíncrono: `EntityKeyIndexStatus` passa por `Pending`/`InProgress` até `Active` ou `Failed`; `Failed` pede `ReactivateEntityKey`. Procurando a chave pelo nome num texto, inclua as aspas, para não casar com uma de nome mais longo | Learn |
| Publisher | procure pelo prefixo antes de criar; `crNNN` costuma ser o publisher padrão do ambiente: confira antes de rodar | projeto de referência |
| Linha que pode rodar de novo | ID fixo (uuid5 da tabela e da chave natural) e `PATCH` com `If-None-Match: *`: só cria; `412` = já existe. `If-Match: *` só atualiza (`skills/power-automate/references/dataverse-batch-upsert.md`) | Learn |
| Lookup circular | a linha nasce sem o Lookup, e um `PATCH` depois liga as duas | projeto de referência |
| Dono e data de criação reais | `ownerid@odata.bind: /systemusers(<id>)`, com o usuário achado por `internalemailaddress` (e-mail codificado na URL, `'` dobrado); `overriddencreatedon` para a data de abertura | Learn; não verificado para a conta que roda |

O construtor do kit (`skills/power-platform/references/construtor-dataverse.md`) já segue os pontos de
solução, chave, ID fixo e Choice local. Os outros valem para quem escrever outra carga.

## 8. A importação da planilha trocou dia e mês

| | |
|---|---|
| **O que aconteceu** | A importação da planilha no Dataverse trocou dia e mês das datas. Ela também não grava dono, compartilhamento nem data de criação, e por isso a carga daquele projeto foi para a Web API. [verificado: projeto de referência] |
| **Previne** | `references/importacao-dados.md` §4. A carga mockup do kit gera datas só com dia 13 ou mais: se a importação trocar, o mês fica inválido e a linha é recusada, em vez de entrar com a data errada. Depois de importar, confira uma data na tabela. Dono e data de criação pedem a Web API (§7). |

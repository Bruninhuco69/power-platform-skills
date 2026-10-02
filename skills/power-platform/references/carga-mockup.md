# Carga mockup das tabelas — `.xlsx` para o Dataverse, `INSERT` para o SQL

No `/pp:arquitetura`, junto com o modelo de dados, sai uma **carga mockup**: dados fictícios para
todas as tabelas, num `.xlsx` com uma aba por tabela. No Dataverse, ela cria as tabelas de uma vez e
ajuda a dedução de tipo a acertar. No SQL Server, ela vem acompanhada de um script de `INSERT` para o
banco de DEV. Quem gera é o `scripts/montar-carga-mockup.py`, a partir do spec `carga-mockup.json`.

No Dataverse há um segundo caminho, sem dedução de tipo: com `--flow`, o script gera também o plano do
**Construtor Dataverse**, um flow que cria as tabelas, as colunas, os relacionamentos e as linhas mockup
pela Web API ([construtor-dataverse.md](construtor-dataverse.md)). O usuário escolhe no `/pp:arquitetura`.

## Sumário

1. [Para que serve](#1-para-que-serve)
2. [O spec `carga-mockup.json`](#2-o-spec-carga-mockupjson)
3. [Gerar](#3-gerar)
4. [Dataverse: importar tudo de uma vez](#4-dataverse-importar-tudo-de-uma-vez)
5. [Dataverse: conferir os tipos antes do dado real](#5-dataverse-conferir-os-tipos-antes-do-dado-real)
6. [SQL Server: carga no banco de DEV](#6-sql-server-carga-no-banco-de-dev)
7. [Códigos](#7-códigos)
8. [Fontes](#8-fontes)

---

## 1. Para que serve

- **Dataverse.** Ao criar uma tabela a partir de um Excel, o Dataverse **deduz** o nome e o tipo de
  cada coluna pelos dados. A própria Microsoft avisa que a dedução "pode não ser 100% precisa". Por
  isso a carga mockup é feita para a dedução acertar:
  - a data é uma data na célula;
  - o código tem letra;
  - o decimal tem fração;
  - o texto longo passa de 100 caracteres;
  - a Choice mostra todas as opções.
- **Mesmo assim, o Dataverse erra a tipagem com frequência.** Avise o usuário sempre: depois de
  importar, ele confere coluna por coluna (§5) antes de carregar qualquer dado real. Quem quer o tipo
  certo sem dedução usa o construtor ([construtor-dataverse.md](construtor-dataverse.md)).
  - Errar no mockup é barato: você recria a coluna.
  - Errar no dado real vira migração.
  - Texto não vira Choice nem Lookup depois (regra 9 da skill `dataverse`).
- **SQL Server.** O tipo é o do DDL, então não há dedução. A carga serve para três coisas:
  - ter dado em DEV para testar telas, procedures e delegação;
  - provar que o DDL aceita os valores do modelo: tamanho, obrigatoriedade e chave estrangeira na
    ordem certa;
  - revisar com o dono do processo pelo mesmo `.xlsx`.
- **Só dado inventado.** E-mail e URL usam domínio fictício (`contoso.com`, `example.com`). Nome de
  pessoa, cliente ou unidade real não entra. No Dataverse, o arquivo enviado passa pelo Copilot e fica
  guardado na tabela *File Upload* do ambiente, e não é apagado sozinho.

## 2. O spec `carga-mockup.json`

Molde: `assets/carga-mockup-molde.json`, com `Unidade` e `Pedido` e as siglas `AAA`/`BBB`/`CCC`. Quem escreve o
spec é o `pp:agente-arquitetura`, ao mesmo tempo que o modelo de dados, nesta pasta da trilha:
- `Backend/Dataverse/carga-mockup.json`;
- `Backend/SQL Server/carga-mockup.json`, fora de `pastas.procedures`.

| Campo | Obrigatório | Conteúdo |
|---|---|---|
| `trilha` | não | `dataverse` ou `sql-server`. Prevalece o `--trilha` e depois o `trilha_dados` do config; se o spec disser outra, dá ERRO |
| `linhas` | não (10) | linhas por tabela, de 1 a 200. `linhas` da tabela > `--linhas` > este > 10 |
| `data_base` | não (`2026-01-13`) | primeira data gerada (`AAAA-MM-DD`); as geradas pulam os dias 1 a 12 (§4) |
| `tabelas[].nome` | sim | nome de **exibição** da tabela; vira o nome da aba. Até 31 caracteres, sem `: \ / ? * [ ]` |
| `tabelas[].sql`, `pk` | SQL | `schema.Tabela` do DDL; `pk` é a coluna IDENTITY que as chaves estrangeiras usam |
| `tabelas[].logico` | não | nome lógico no Dataverse (`<prefixo>_pedido`); o `--conferir` acha a tabela por ele |
| `tabelas[].colunas[].nome` | sim | nome de **exibição**; vira o cabeçalho da coluna |
| `colunas[].tipo` | sim | um da tabela abaixo |
| `colunas[].primaria` | Dataverse | uma por tabela: o nome principal. É por ele que o Lookup acha a linha na importação, e ele não muda depois de criado |
| `colunas[].chave` | não | chave alternativa (uma por tabela). No SQL, é por ela que a chave estrangeira acha a linha |
| `colunas[].obrigatoria`, `tamanho`, `casas` | não | obrigatoriedade; tamanho máximo do texto; casas do decimal e da moeda (2) |
| `colunas[].opcoes` | Choice | rótulos das opções, sem repetição |
| `colunas[].alvo` | Lookup | `nome` da tabela apontada |
| `colunas[].exemplos` | não | valores fictícios; sem eles, o script gera. Chave e primária precisam de um por linha |
| `colunas[].sql`, `logico` | SQL / não | nome da coluna no DDL; nome lógico no Dataverse |

| `tipo` | Dataverse | SQL (valor no `INSERT`) | Valor gerado |
|---|---|---|---|
| `texto` | Texto de linha única | `N'…'` | `<coluna> 01` (`<tabela> 01` na primária) |
| `texto_longo` | Várias linhas de texto | `N'…'` | frase com mais de 100 caracteres |
| `codigo` | Texto (nunca número) | `N'…'` | `PRO001`: tem letra, para não virar número |
| `inteiro` | Número inteiro | `3` | múltiplos de 3 |
| `decimal`, `moeda` | Número decimal, Moeda | `150.90` | com fração, para não virar inteiro |
| `data` | Data e hora, comportamento Somente data | `'20260113'` | de 3 em 3 dias a partir de `data_base`, só com dia 13 ou mais |
| `data_hora` | Data e hora | `'2026-01-13T08:30:00'` | um dia (13 ou mais) e uma hora por linha |
| `sim_nao` | Sim/Não | `1` / `0` | alterna |
| `choice` | Escolha | o rótulo, `N'Aberto'` | percorre todas as opções |
| `lookup` | Pesquisa | subconsulta pela chave do alvo | percorre as linhas do alvo |
| `email`, `telefone`, `url` | Texto com formato | `N'…'` | `usuario01@contoso.com`, `(11) 90000-0001`, `https://contoso.com/…` |
| `autonumero` | Numeração automática | fora do `INSERT` (IDENTITY) | `PRO001` |
| `escolhas`, `imagem`, `arquivo` | crie à mão | fora do `INSERT` | fora da planilha (C010) |
| `calculada` | crie à mão | fora do `INSERT` (coluna calculada) | fora da planilha |

No SQL, a Choice grava o rótulo como texto. Se o DDL usa código, modele a coluna como `inteiro` com
`exemplos`, ou como `lookup` para a tabela de domínio.

## 3. Gerar

Rode da raiz do projeto (o script procura o `power-platform.config.json` para cima):

```bash
# valida e mostra a ordem de carga, sem gravar
python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json
# grava carga-mockup.xlsx (e carga-mockup.sql na trilha SQL)
python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json --saida Backend/Dataverse
# também um arquivo por tabela, para o assistente que lê só a 1ª aba
python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json --saida Backend/Dataverse --uma-por-tabela
# Dataverse pelo construtor: também o plano e o flow (construtor-dataverse.md)
python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json --saida Backend/Dataverse --flow
```

O que sai:
- **Uma aba por tabela, na ordem de carga.** Quem é apontado por Lookup vem antes, por exemplo
  `Unidade → Pedido`.
- **Cada aba é uma tabela do Excel**, com o cabeçalho congelado.
- **Na trilha Dataverse, a última aba é a `Conferência de tipos`.** Ela mostra, por coluna:
  - o tipo do modelo;
  - o que escolher no Dataverse;
  - o que costuma vir errado;
  - as colunas "Veio como" e "Conferido", para preencher.
- **A saída é determinística:** o mesmo spec gera os mesmos bytes.
- **Na trilha Dataverse, toda geração sem erro termina com o aviso C013 (confira a tipagem).** Cada
  coluna Choice ou Lookup ganha também um C014 (chega como texto). Repita os avisos ao usuário com as
  palavras do script. O `--conferir` não repete esses avisos: ele já é a conferência. Com `--flow`, o
  C013 e o C014 dão lugar a um C018 só (prove com `--conferir` depois do construtor).

## 4. Dataverse: importar tudo de uma vez

Se o usuário escolheu o construtor, siga [construtor-dataverse.md](construtor-dataverse.md) e pule
para o §5. O resto desta seção é o caminho da planilha.

**Antes de importar, defina a solução preferida** com o publisher do projeto (Power Apps ›
Soluções › *Definir solução preferida*). Sem isso, as tabelas nascem na solução padrão, com o
prefixo aleatório do publisher padrão (`cr8a3_…`), e não com o `prefixo_publisher` do projeto.
Isso aconteceu de verdade: o ambiente do projeto de referência foi criado assim
`[verificado: projeto de referência]`.

**Caminho A: Power Query, tudo de uma vez** (recomendado).
1. Tabelas › Importar › Importar dados › Pasta de trabalho do Excel; envie o `carga-mockup.xlsx`.
2. No navegador, marque **todas as abas de tabela**. A `Conferência de tipos` fica de fora.
3. No editor, confira o ícone de tipo no cabeçalho de cada coluna. O Power Query também deduz o tipo
   pelas linhas. Corrija o tipo aqui: é de graça.
4. Avançar › **Carregar em nova tabela**, para cada consulta:
   - **Coluna de nome primário exclusiva** = a `primaria` do spec;
   - texto longo = *Texto de várias linhas*.
5. Publicar.

Os passos são os do Learn, onde o "Carregar em nova tabela" ainda é preview. O caminho exige a licença
Power Apps por usuário ou por app.

**Caminho B: uma tabela por arquivo, com o Copilot.**
1. Tabelas › Nova tabela › Criar com dados externos › Arquivo. Esse assistente lê **só a primeira
   faixa da primeira aba**, por isso gere com `--uma-por-tabela`.
2. Envie os arquivos de `carga-mockup-tabelas/` na ordem do número (`01-…`, `02-…`).
3. Na prévia, **antes de Criar**, abra cada coluna (Editar coluna) e acerte o tipo. Na Choice,
   preencha as opções e a padrão. Confira também o nome principal e a propriedade das linhas.

**Nos dois caminhos, confira uma data depois de importar.** A importação já trocou dia e mês num
projeto de referência. Por isso as datas geradas têm dia 13 ou mais: se a importação trocar, o mês
fica inválido e a linha é recusada, em vez de entrar com a data errada. Os `exemplos` do spec com dia
até 12 não têm essa proteção. A importação também não grava dono nem data de criação.

**Nos dois caminhos, o Lookup não nasce:** a coluna chega como texto. Para cada Lookup:
1. Crie o relacionamento: na área de trabalho de dados, arraste da tabela filha para a mãe, ou crie
   uma coluna Pesquisa.
2. Apague a coluna de texto.
3. Crie as chaves alternativas (`chave` do spec) e espere `EntityKeyIndexStatus = Active`
   (skill `dataverse`, `references/modelagem.md`).

## 5. Dataverse: conferir os tipos antes do dado real

1. **Exporte o esquema:** a mesma consulta `EntityDefinitions` + `$expand=Attributes` do
   `references/nomes-as-built.md` da skill `dataverse`, salva em `export.json`.
2. **Compare:**
   `python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json --conferir export.json`
   - **C103:** o tipo veio errado. Recrie a coluna enquanto só há linha mockup.
   - **C105:** o nome principal veio errado. Recrie a tabela, porque ele não muda depois.
   - **C101/C102:** a tabela ou a coluna não foi encontrada pelo nome de exibição. Corrija o nome, ou
     informe `logico` no spec.
   - **C104:** o export não prova este ponto. Confira no maker: comportamento da data, opções da
     Choice, destino da Pesquisa, formato do texto.
3. Repita até `0 erro(s)`. Preencha "Veio como" e "Conferido" na aba de conferência, com a data.
4. Extraia o `NOMES-AS-BUILT` (`extrair-nomes-as-built.py`). A partir daqui, ele é a autoridade.
5. **Linhas mockup.**
   - Ficam só em DEV: apague-as antes da carga real ou deixe-as para os testes.
   - A solução não leva dado para HML e PRD.
   - A carga real segue `references/importacao-dados.md` da skill `dataverse`, para tabelas que já
     existem.

## 6. SQL Server: carga no banco de DEV

1. Aplique o DDL no banco de DEV, na ordem do pacote (skill `sql-procedures`).
2. Rode o `carga-mockup.sql` (SSMS, ou `sqlcmd -S <servidor> -d <banco> -i carga-mockup.sql`).
   - **Transação:** é uma só, com `XACT_ABORT`. Um erro desfaz tudo.
   - **Ordem:** a das chaves estrangeiras. O Lookup vira subconsulta pela `chave` do alvo quando o
     alvo tem `pk` IDENTITY; sem `pk`, grava a chave literal.
   - **Reexecução:** uma guarda com `THROW` para o script se a primeira linha mockup já existe. Para
     recarregar, apague antes as linhas mockup.
   - **Formatos:** data em `AAAAMMDD` e data e hora em ISO com `T`, que não dependem do
     `SET DATEFORMAT`; o arquivo sai em UTF-8 com BOM, para o SSMS ler os acentos.
3. Erro de tamanho, de `NOT NULL` ou de chave estrangeira aqui é **defeito do DDL ou do spec**:
   corrija o modelo, nunca o script gerado.
4. **Nunca rode em HML nem em PRD.** O script não entra no pacote do DBA.

## 7. Códigos

| Código | Nível | Causa | O que fazer |
|---|---|---|---|
| C001 | ERRO | raiz sem `tabelas`, `linhas` fora de 1–200, `data_base` inválida | corrija o spec |
| C002 | ERRO | trilha indefinida ou diferente da do config | `--trilha`, `trilha_dados` ou `trilha` no spec, uma só |
| C003 | ERRO | tabela sem nome ou colunas, repetida, nome de aba inválido ou reservado | renomeie |
| C004 | ERRO | coluna sem nome, repetida, tipo desconhecido, `tamanho`/`casas` fora do tipo | corrija a coluna |
| C005 | ERRO | Dataverse sem exatamente uma `primaria`; primária ou chave com tipo que não aceita; mais de uma `chave` | ajuste as marcas |
| C006 | ERRO | Choice sem `opcoes`; Lookup sem `alvo`, com alvo inexistente ou com alvo sem chave nem primária | complete o modelo |
| C007 | ERRO | Lookups em ciclo entre tabelas | carregue uma sem o Lookup e preencha depois, ou quebre o ciclo |
| C008 | ERRO | exemplo inválido para o tipo, fora do `tamanho`, fora das opções, sem correspondência no alvo; chave repetida ou curta | corrija os `exemplos` |
| C009 | ERRO | trilha SQL sem `sql` válido na tabela ou coluna; `pk` inválida; Lookup pela chave que o banco gera | complete com os nomes do DDL |
| C010 | AVISO | `escolhas`, `imagem`, `arquivo` (e `calculada` no Dataverse) ficam fora da carga; com `--flow`, só `calculada` | crie a coluna à mão |
| C011 | AVISO | Choice com mais opções que linhas | aumente `linhas` ou crie as opções que faltarem |
| C012 | AVISO | e-mail ou URL de domínio não fictício | troque por `contoso.com` |
| C013 | AVISO | sempre no Dataverse: a dedução de tipo erra | §5 antes do dado real |
| C014 | AVISO | Choice ou Lookup no Dataverse chega como texto | recrie com o tipo certo (§4, §5) |
| C015 | ERRO | não gravou (arquivo aberto no Excel, pasta sem permissão) | feche o arquivo e rode de novo |
| C016 | ERRO | `--flow`: nome lógico que não dá para derivar, repetido ou igual à chave primária | informe `logico` |
| C017 | ERRO | `--flow`: limite do Dataverse (casas da moeda, tamanho do texto, valor maior que a coluna, número fora do tipo, data antes de 1753, `{{` no valor, Lookup para linha posterior da mesma tabela) | ajuste o spec |
| C018 | AVISO | `--flow`: prove com `--conferir` depois de rodar o construtor | §5 |
| C101–C105 | ERRO/AVISO | `--conferir`: tabela ausente, coluna ausente, tipo diferente, ponto que o export não prova, nome principal | §5 |

## 8. Fontes

- Criar tabela com dados externos (Excel, prévia de 20 linhas, Copilot):
  <https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-edit-entities-portal>
- O que a dedução faz e o limite "primeira aba", "pode não ser 100% precisa":
  <https://learn.microsoft.com/en-us/power-apps/maker/common/faqs-excel-to-table-app>
- Power Query, Carregar em nova tabela, coluna de nome primário:
  <https://learn.microsoft.com/en-us/power-query/dataflows/add-data-power-query>
- Importar para tabela existente, tipos não suportados na importação:
  <https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-import-export>
- Solução preferida e prefixo do publisher padrão:
  <https://learn.microsoft.com/en-us/power-apps/maker/data-platform/preferred-solution>

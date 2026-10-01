# NOMES-AS-BUILT: a autoridade de nomes e tipos

O `NOMES-AS-BUILT.md` é o contrato de nomes **do ambiente real**: tabelas, colunas, tipos, chaves,
Choices e conectores, lidos de onde o dado vive. Quando ele diverge do dicionário de dados, do
script de criação ou do plano, **ele vence** (`decisoes-padrao.md` N1). Molde em
`assets/nomes-as-built-molde.md`.

## Sumário

1. [Por que é a autoridade](#1-por-que-é-a-autoridade)
2. [O que ele precisa conter](#2-o-que-ele-precisa-conter)
3. [Como extrair do ambiente](#3-como-extrair-do-ambiente)
4. [Como gerar o arquivo](#4-como-gerar-o-arquivo)
5. [Como manter](#5-como-manter)
6. [O que fazer com divergência](#6-o-que-fazer-com-divergência)

---

## 1. Por que é a autoridade

Há três fontes que *parecem* dizer o nome de uma coluna, e só uma é o ambiente:

| Fonte | Descreve | Confiável para nome/tipo? |
|---|---|---|
| Dicionário de dados / plano | O que se **pretendia** criar | Não |
| Script de criação | O que se **tentaria** criar | Só se foi o que criou o ambiente |
| Ambiente (maker, Web API) | O que **existe** | Sim |

Num projeto de referência, uma tela de cadastro de usuários foi escrita contra o dicionário e teve de
ser corrigida em vários pontos no Studio. Nenhum foi de sintaxe; todos foram de nome ou tipo: tabelas
com outro nome, prefixo diferente do planejado, `perfil` virou Choice (não Lookup), `unidade` virou
texto (não Lookup). O ambiente fora criado à mão (ou por Excel) com o publisher padrão do tenant,
**não** pelo script. `[verificado: projeto de referência]` — detalhe em
`references/licoes-de-campo.md`.

Regras que decorrem disso:

- **Nada de tela ou flow antes do as-built preenchido** (N2).
- **Antes de afirmar que uma coluna não existe, abra o esquema da tabela inteira** — não um extrato
  filtrado, não uma amostra de dados (N3). Um export de dados do Dataverse para Excel traz poucas linhas por tabela e
  pode deixar de fora tabelas que o app usa: ausência no export não é ausência no ambiente.
- O dicionário continua útil como **intenção**; quando a divergência for deliberada, vira decisão
  registrada, não um desvio silencioso (`references/modelagem.md`).

## 2. O que ele precisa conter

| Seção | Conteúdo | Por quê |
|---|---|---|
| Cabeçalho | Prefixo do publisher, ambiente (`<ambiente>`), **data e comando da extração** | P5: número e fato sem o comando que o mede envelhecem |
| Tabelas | Nome da fonte no app, nome lógico, EntitySet, chave primária, nome principal | Fórmula, flow e `$batch` usam cada um um nome |
| Colunas | Exibição, lógico, `AttributeType` real, tipo no Power Fx, notas | Decide a sintaxe de filtro e de `Patch` |
| Choices | Nome em Power Fx e opções com valor inteiro | Contrato com CSV de carga e com sistema externo |
| Chaves alternativas | Colunas e `EntityKeyIndexStatus` | Upsert e importação |
| Conectores | Nome do conector **no idioma do ambiente** | Em ambiente pt-BR o objeto do conector é traduzido (`UsuáriosdoOffice365`) |
| Lacunas | Colunas com `?` ou "não confirmada", e por que não bloqueiam | Fórmula que depende de lacuna diz isso |

Nome de schema ou tipo não lido fica **`?`**, nunca inventado e nunca copiado do dicionário.

## 3. Como extrair do ambiente

Preferência: a Web API `EntityDefinitions`, porque devolve nomes inteiros (capturas de tela do maker
truncam nomes longos) e tipos reais. Fonte:
[Query table definitions using the Web API](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query-metadata-web-api).

### 3.1 Pelo navegador (o que os projetos de referência usaram)

Sessão do host do ambiente (`<org>.crm.dynamics.com`) é separada da sessão do maker: abrir
`/api/data/...` direto devolve **HTTP 401**. Abra `https://<org>.crm.dynamics.com/main.aspx` uma vez,
conclua o login, e as URLs abaixo respondem JSON no próprio navegador. `[verificado: projeto de referência]`
Salve cada resposta num arquivo `.json`.

**Tabelas e colunas numa só chamada** (entrada do script):

```
https://<org>.crm.dynamics.com/api/data/v9.2/EntityDefinitions?$select=LogicalName,SchemaName,EntitySetName,PrimaryIdAttribute,PrimaryNameAttribute,DisplayName&$filter=startswith(LogicalName,'<prefixo>_')&$expand=Attributes($select=LogicalName,SchemaName,AttributeType,AttributeTypeName,DisplayName)
```

`$expand=Attributes` só traz as propriedades **comuns**: não cabem `OptionSet` nem `Targets` no
`$select` interno (Learn, página acima). Para elas, uma chamada com cast **por tabela**:

```
# opções de Choice (e Choice global)
https://<org>.crm.dynamics.com/api/data/v9.2/EntityDefinitions(LogicalName='<prefixo>_<tabela>')/Attributes/Microsoft.Dynamics.CRM.PicklistAttributeMetadata?$select=LogicalName&$expand=OptionSet,GlobalOptionSet

# destino de Lookup
https://<org>.crm.dynamics.com/api/data/v9.2/EntityDefinitions(LogicalName='<prefixo>_<tabela>')/Attributes/Microsoft.Dynamics.CRM.LookupAttributeMetadata?$select=LogicalName,Targets
```

**Uma Choice global pelo nome** (não aceita `$filter`):

```
https://<org>.crm.dynamics.com/api/data/v9.2/GlobalOptionSetDefinitions(Name='<nome da choice>')
```

Metadado não tem paginação nem limite de linhas: a primeira resposta traz tudo. Em ambiente com
vários idiomas, acrescente `&LabelLanguages=<LCID>` para encurtar (pt-BR = 1046).

### 3.2 Pelo maker (conferência manual)

Em `make.powerapps.com` → *Tabelas* → a tabela → *Colunas*: mostra nome de exibição, **nome** (lógico)
e tipo. Serve para conferir uma coluna isolada; **não** serve como extração, porque a grade trunca
nomes longos (`<prefixo>_dataprevistadeencerramentod…`). Nome truncado na captura entra no as-built como
"truncado — não usar em `SortByColumns`/`DisplayFields`/`SearchFields` até ler inteiro".

### 3.3 Pelo Studio

O painel de dados do app mostra o nome **com que a tabela foi adicionada** (a fonte de dados em
Power Fx), que pode diferir do nome de exibição da tabela. O conector aparece no painel de conexões
com o nome traduzido. Esses dois nomes só se leem no app, não na Web API.

### 3.4 Por `pac` e por solução exportada

`[não verificado]`: os projetos de referência não tinham `pac` instalado e não usaram esse caminho.
Candidatos para um ambiente que o tenha: exportar a solução e ler o `customizations.xml`; ou
`pac modelbuilder build`, que gera classes com os nomes lógicos. Se usar, registre no as-built o
comando e o resultado, como na Web API.

## 4. Como gerar o arquivo

```
python <pasta-da-skill>/scripts/extrair-nomes-as-built.py <export.json> --prefixo <prefixo>_ `
    --complemento <prefixo>_<tabela>=<choices-tabela.json> `
    --saida <caminho do NOMES-AS-BUILT.md>
```

(Continuação de linha com crase é PowerShell; em bash use `\`.) (`--complemento` é repetível; sem `--saida` o script só valida.) O script lê só arquivo local, sem
rede, e escreve só em `--saida`; nunca sobre a entrada. Ele:

- filtra tabelas e colunas pelo prefixo (colunas de sistema e a chave primária entram conforme o caso);
- traduz `AttributeType` para o tipo no Power Fx e para a regra de comparação (`references/nomes-e-tipos.md` §7);
- marca a chave primária cujo nome de exibição colide com o da tabela (aspas obrigatórias);
- acusa tabela sem atributos (`E002`), Choice sem opções (`A003`), exibição repetida (`D001`).

O arquivo gerado é **saída de gerador** (P3): marque "gerado — não editar", e leve a correção manual
para a entrada (refazer a exportação). As partes que a Web API não dá — nome da fonte no app, nome do
conector, decisões de modelagem — vão numa seção separada, escrita à mão, que o gerador não toca
(copie o molde e mantenha as duas seções em arquivos distintos se preferir).

## 5. Como manter

- **Versione em Git** junto do app; o diff do as-built é o melhor aviso de que o ambiente mudou.
- **Reextraia** a cada mudança de schema, a cada nova tabela e antes de qualquer onda de telas.
  Quem altera o ambiente (maker ou script) é quem reextrai.
- **Escreva a data e o comando** no cabeçalho. Documento que declara número ou fato traz o comando
  que o mede (P5).
- **Aponte o caminho no `power-platform.config.json`** (`nomes_as_built`) para humanos e agentes. O
  `validar-telas.py` só confere o prefixo do publisher (T014); conferir nome contra o as-built é
  manual (ou com `extrair-nomes-as-built.py` + leitura).
- Não preencha lacuna por inferência: se uma tela depende de coluna `?`, a pendência fica registrada
  e a tela evita a dependência (ex.: ordenar com `Sort(...)` em vez de `SortByColumns(...)` até o
  nome lógico ser lido). `[verificado: projeto de referência]` — essa defesa anulou o único palpite errado de
  nome de uma rodada de telas.

## 6. O que fazer com divergência

Quando o as-built difere do dicionário, decida e escreva — não deixe o desvio como estado de fato:

| Opção | Custo | Quando |
|---|---|---|
| **Manter o as-built** | Rápido; perde a integridade que o dicionário previa (Lookup → texto) | Tabela pequena, risco baixo, prazo curto |
| **Realinhar o ambiente ao dicionário** | Recriar tabelas e reimportar | Quando a integridade ou o domínio fechado são requisito |
| **Atualizar o dicionário** | Barato | Quando o ambiente está certo e o papel estava errado |

A decisão vale para cada tabela, e muda a sintaxe de filtro e de `Patch` das telas seguintes — por
isso é pré-requisito delas. Registre num ADR do projeto (`decisoes-padrao.md`, A4 e §8).

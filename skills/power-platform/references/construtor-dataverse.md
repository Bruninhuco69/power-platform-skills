# Construtor Dataverse — o flow que cria as tabelas e a carga mockup pela Web API

A alternativa à planilha na trilha Dataverse. O `montar-carga-mockup.py --flow` compila o
`carga-mockup.json` num **plano** (`plano-dataverse.json`), e um flow fixo, o **Construtor Dataverse**,
executa o plano pela Web API:
- cria as tabelas, cada uma com o nome principal;
- cria as colunas com o tipo do spec, inclusive Choice com as opções, Email, URL, Telefone, Numeração
  automática, Escolhas, Imagem e Arquivo;
- cria os relacionamentos (os Lookups);
- carrega as linhas mockup, já apontando para o pai certo;
- cria as chaves alternativas.

Nada é deduzido: o tipo é o que o spec diz. A planilha continua saindo sempre, como referência.

> Estado: o plano e o pacote são testados no kit (gerados, validados pelo `verificar-fluxo.py`). A
> execução num ambiente real ainda **não foi confirmada**: veja §9 antes do primeiro uso.

## Sumário

1. [Planilha ou construtor](#1-planilha-ou-construtor)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Gerar](#3-gerar)
4. [Instalar o flow (uma vez por ambiente)](#4-instalar-o-flow-uma-vez-por-ambiente)
5. [Rodar](#5-rodar)
6. [Ler o resultado](#6-ler-o-resultado)
7. [Depois do construtor](#7-depois-do-construtor)
8. [O plano por dentro](#8-o-plano-por-dentro)
9. [O que ainda não foi verificado](#9-o-que-ainda-não-foi-verificado)
10. [Fontes](#10-fontes)

---

## 1. Planilha ou construtor

No `/pp:arquitetura`, trilha Dataverse, o usuário escolhe como as tabelas nascem:

| | Construtor (recomendado) | Só a planilha |
|---|---|---|
| Tipo das colunas | o do spec | deduzido pelos dados, e erra com frequência |
| Choice e Lookup | nascem certos, com opções e relacionamento | chegam como texto e são recriados à mão |
| Chave alternativa | criada | à mão |
| Exige | conector premium liberado e papel de personalização (§2) | licença Power Apps |
| Esforço | instalar o flow uma vez, depois um clique por plano | importar e conferir coluna por coluna |

Sem os pré-requisitos do §2, use a planilha (`carga-mockup.md` §4).

## 2. Pré-requisitos

- **Conector "HTTP com Microsoft Entra ID (pré-autorizado)"** (`shared_webcontents`). É premium, e a
  política de dados (DLP) do ambiente precisa permitir. Existe uma versão nova do conector que exige
  consentimento do administrador; o construtor usa a pré-autorizada.
- **Papel de quem roda** (o dono da conexão): Administrador do Sistema ou Personalizador do Sistema.
  Criar tabela e coluna é privilégio de personalização.
- **Uma solução não gerenciada com o publisher do projeto.** Ela dá o prefixo das tabelas e o prefixo
  de valor das opções. É a mesma solução preferida da planilha. Prefixo `crNNN` costuma ser do
  publisher padrão do ambiente: a primeira linha do relatório mostra o prefixo lido.
- **Ambiente de DEV.** As linhas mockup ficam só em DEV, e a solução não leva dado para HML e PRD.

## 3. Gerar

```bash
python <skills>/power-platform/scripts/montar-carga-mockup.py Backend/Dataverse/carga-mockup.json --flow --saida Backend/Dataverse
```

Sai, além da planilha:

| Arquivo | O que é |
|---|---|
| `plano-dataverse.json` | os pedidos à Web API, na ordem, sem nada do ambiente. Muda a cada spec |
| `construtor-dataverse/ConstrutorDataverse_1_0_0_0.zip` | solução não gerenciada com o flow, para importar. Igual em todo projeto |
| `construtor-dataverse/construtor-escopo.json` | o mesmo flow como escopo, para colar no designer se a importação recusar o `.zip` |

- **`--idioma <código>`**: idioma da solução do `.zip` (padrão `1046`, pt-BR). Use o idioma base do
  ambiente (`1033` se for inglês). Os rótulos das tabelas não dependem disso: o flow lê o idioma base.
- **Achados próprios do `--flow`** (além de C001–C015):
  - **C016** (ERRO): nome lógico que não dá para derivar, repetido ou que colide com a chave primária;
    informe `logico` no spec.
  - **C017** (ERRO): limite do Dataverse. Moeda com mais de 4 casas, texto de linha única com mais de
    4000 caracteres, valor maior que a coluna criada (sem `tamanho`, o construtor cria texto com 100,
    telefone com 50, URL com 200 e texto longo com 2000), número fora do intervalo do tipo, data antes
    de 1753, `{{` ou caractere de controle num nome, opção ou valor, ou Lookup para a própria tabela
    apontando para uma linha posterior.
  - **C018** (AVISO): depois de rodar, prove com `--conferir`. Com `--flow`, ele substitui os avisos da
    importação (C011, C013, C014), e o C010 só sai para `calculada`.
- **Sem `--saida`**, só valida e mostra o resumo (`# construtor: N passo(s)…`).

## 4. Instalar o flow (uma vez por ambiente)

**Caminho A: importar a solução** (recomendado).
1. Power Apps › Soluções › Importar solução › envie o `ConstrutorDataverse_1_0_0_0.zip`.
2. Na referência de conexão "Construtor Dataverse - HTTP com Microsoft Entra ID", crie a conexão:
   - **Base Resource URL** = a URL do ambiente, `https://<org>.crm.dynamics.com`;
   - **Microsoft Entra ID Resource URI** = a mesma URL.
3. Importe. Abra o flow **Construtor Dataverse (kit)** e **ative**: importado, ele vem desligado.

A importação cria o publisher `kitpowerplatform` (prefixo `kitpp`), só para o flow. As tabelas não
usam esse publisher: elas vão para a solução que você informar ao rodar.

**Caminho B: colar o escopo**, se a importação recusar o pacote.
1. Crie um flow de nuvem instantâneo, **Disparar um fluxo manualmente**, com duas entradas, nesta
   ordem: **Arquivo** com o nome `Plano` e **Texto** com o nome `Solução`.
2. Crie três **Inicializar variável** na raiz: `Falhou` (Booliano, `false`), `Ja_existe` (Booliano,
   `false`) e `Relatorio` (Matriz, `[]`).
3. Abaixo delas, `Ctrl+V` com o conteúdo do `construtor-escopo.json` (skill `power-automate`,
   `references/formato-clipboard.md`). Depois, confira em "Configurar execução após" que o escopo
   `Construtor` roda depois da última variável, e não em paralelo com elas.
4. Nas quatro ações HTTP (`Consultar_solucao`, `Consultar_idioma`, `Consultar`, `Enviar`), escolha a
   conexão HTTP com Microsoft Entra ID do §4 A, passo 2.
5. Abra as ações de variável. Se alguma vier sem o nome (skill `power-automate`,
   `references/formato-clipboard.md` §7), escolha:
   - `Falhou` em `Marcar_lote`, `Marcar_falha` e `Marcar_ambiente`;
   - `Ja_existe` em `Zerar` e `Marcar_existe`;
   - `Relatorio` em `Anotar_solucao`, `Anotar_lote`, `Anotar_ok`, `Anotar_falha`, `Anotar_pulado` e
     `Anotar_ambiente`.

O escopo já vem nas formas que colam (condição em objeto com `and`/`or`, nenhuma variável sozinha num
campo); o `verificar-fluxo.py` confere as duas (F020, F022).

## 5. Rodar

Execute o flow e informe:
- **Plano**: o `plano-dataverse.json`;
- **Solução**: o **nome exclusivo** da solução não gerenciada (Soluções, coluna Nome).

O que ele faz:
1. **Confere o ambiente.** Lê a solução, que dá o prefixo do publisher e o prefixo de valor de opção,
   e o idioma base. Para se a solução não existir, se for gerenciada ou se o arquivo não for um plano
   do kit.
2. **Troca os marcadores** (`{{prefixo}}`, `{{opcao}}`, `{{idioma}}`) pelos do ambiente, um passo
   por vez: o plano inteiro numa expressão só passaria do limite de tamanho do flow.
3. **Roda os passos um de cada vez**, na ordem: tabelas, colunas, relacionamentos, publicar, dados,
   chaves.
   - **Antes de cada passo**, consulta se o que ele cria já existe. Se existe, pula.
   - **Dados:** um `$batch` por lote (até 100 linhas e cerca de 60 mil caracteres), num changeset
     só: o lote entra inteiro ou não entra. O lote é pulado se a primeira linha dele já existe.
   - **Pausa de 2 s entre os passos**, porque o conector aceita 100 chamadas por minuto por conexão.
     Com 6 tabelas e cerca de 50 colunas, a execução leva alguns minutos.
4. **Para no primeiro erro.** O resto dos passos é pulado e aparece no relatório como `não executado`.

**Rodar de novo é seguro.** O que já existe é pulado, então dá para corrigir o spec, gerar o plano de
novo e repetir. Para recarregar os dados de uma tabela, apague antes as linhas mockup dela.

## 6. Ler o resultado

- **A primeira linha do relatório** é o ambiente: a solução, o prefixo, o prefixo de opção e o idioma
  lidos. Se o prefixo não é o do projeto, a solução informada é a errada.
- **Execução bem-sucedida:** a ação `Resumo` mostra cada passo como `feito` ou `já existia`.
- **Execução com falha:** a mensagem do erro é a primeira falha do relatório: o número do passo, o
  rótulo (`Pedido.Status`, `Pedido: 10 linha(s)`) e o detalhe devolvido pela Web API. Os passos
  seguintes aparecem como `não executado`. A ação que falhou
  está no histórico da execução (`Enviar` ou `Consultar`, dentro de `Passos`).
- **Erro no lote de dados:** o lote recusado costuma voltar como erro da própria chamada (o `Enviar`
  falha, e o relatório traz o status e a resposta do `$batch` já decodificada). Se voltar 200, o flow
  procura o `HTTP/1.1 4xx` ou `5xx` dentro da resposta e guarda o trecho.
- **"Já existe" logo depois de um tempo esgotado:** a ação HTTP repete sozinha em erro 408, 429 e
  5xx. Um `POST` de tabela que estourou os 120 s pode ter terminado no servidor, e a repetição recebe
  "já existe". Rode de novo: a consulta do passo vê que existe e pula.

Corrija no spec, nunca no plano: o plano é gerado.

## 7. Depois do construtor

1. **Prove os tipos:** exporte o esquema e rode
   `montar-carga-mockup.py <spec> --conferir export.json` até `0 erro(s)` (`carga-mockup.md` §5). O
   construtor manda o tipo certo, e a conferência prova que o ambiente aceitou.
2. **Extraia o `NOMES-AS-BUILT`** (`extrair-nomes-as-built.py`, skill `dataverse`). A partir daqui,
   ele é a autoridade dos nomes lógicos.
3. **Colunas que o construtor não cria:** `calculada` (C010), à mão no maker, depois das colunas que ela
   usa.
4. **Linhas mockup:** ficam em DEV, como na planilha.

## 8. O plano por dentro

```json
{
  "formato": "plano-dataverse/1",
  "resumo": { "tabelas": 2, "colunas": 13, "relacionamentos": 1, "lotes": 2, "linhas": 13, "chaves": 2 },
  "passos": [
    { "n": 1, "fase": "tabela", "rotulo": "Unidade",
      "existe": "/api/data/v9.2/EntityDefinitions?$select=LogicalName&$filter=LogicalName%20eq%20'{{prefixo}}_unidade'",
      "metodo": "POST", "url": "/api/data/v9.2/EntityDefinitions",
      "tipo": "application/json; charset=utf-8", "corpo": "{\"@odata.type\":\"Microsoft.Dynamics.CRM.EntityMetadata\", …}" }
  ]
}
```

Destino: `plano-dataverse.json`, gerado; o trecho mostra a forma de um passo.

| Fase | Pedido | O que o corpo leva |
|---|---|---|
| `tabela` | `POST EntityDefinitions` | `SchemaName`, `EntitySetName` explícito, rótulos, `UserOwned`, a coluna principal com `IsPrimaryName` |
| `coluna` | `POST EntityDefinitions(LogicalName='…')/Attributes` | o `@odata.type` do tipo (`StringAttributeMetadata` com `FormatName`, `MemoAttributeMetadata`, `DecimalAttributeMetadata`…), obrigatoriedade |
| `relacionamento` | `POST RelationshipDefinitions` | `OneToManyRelationshipMetadata` com o `Lookup`; navegação fixada; exclusão `Restrict` se o Lookup é obrigatório, `RemoveLink` se não |
| `publicar` | `POST PublishXml` | as tabelas do plano; roda sempre |
| `dados` | `POST $batch` | um changeset por lote, com um `POST` por linha, CRLF, ID fixo da linha, Lookup em `@odata.bind` |
| `chave` | `POST EntityDefinitions(LogicalName='…')/Keys` | `EntityKeyMetadata`. A criação do índice é assíncrona; confira `EntityKeyIndexStatus = Active` antes de usar a chave |

Regras que o compilador segue:
- **Nome lógico.** Vem de `logico` do spec, que é o nome depois do prefixo, ou do nome de exibição sem
  acento em PascalCase (`Data prevista` → `{{prefixo}}_DataPrevista`, lógico
  `{{prefixo}}_dataprevista`). O prefixo é sempre o da solução.
- **Marcadores.** O plano não leva nada do ambiente. O flow troca `{{prefixo}}`, `{{opcao}}` e
  `{{idioma}}` antes de ler o JSON. A Choice usa o prefixo de valor do publisher: `{{opcao}}0000`,
  `{{opcao}}0001`…
- **ID fixo por linha** (uuid5 da tabela e do número da linha). O filho aponta para o ID do pai já no
  plano, e o mesmo spec gera sempre o mesmo plano.
- **Lookup para a própria tabela** usa `$n` (o `Content-ID` da linha anterior no mesmo lote); se a
  linha apontada ficou num lote anterior, já gravado, usa o ID fixo dela.
- **Lotes:** até 100 linhas e cerca de 60 mil caracteres cada, para cada passo caber no limite de
  131.072 caracteres das expressões do flow.
- **Idioma:** se a leitura do idioma base vier vazia, o flow usa `1046`.
- **Data e hora** vai em UTC (`…T08:30:00Z`) e aparece no fuso do usuário (05:30 em Brasília). No
  mockup não importa.
- **O que não vai nas linhas:** numeração automática (o Dataverse gera), imagem e arquivo (binário).
- **Corpo em ASCII:** o acento vai escapado (`ç`), para não depender da codificação do conector.

O flow (`assets/construtor-dataverse.json`) é fixo: escopo `Construtor`, `Foreach` com concorrência 1,
`Tentar`/`Capturar` por passo e `Terminate` com falha no fim se algo deu errado. Mudou o flow? Rode o
`verificar-fluxo.py` nele e os testes do kit antes de publicar.

## 9. O que ainda não foi verificado

Confira no primeiro uso, num ambiente de DEV, e registre o que achar:

| Ponto | Por que importa |
|---|---|
| Importação do `.zip` gerado (formato montado a partir do projeto de referência, sem importação confirmada) | se recusar, use o §4 B |
| Idioma da solução diferente do idioma base | a importação pode recusar: gere com `--idioma` |
| Conector pré-autorizado aceito pelo tenant | sem ele, nenhuma chamada passa |
| `FormatName` `Phone` e `Url` | a tabela de formatos do Learn mostra `PhoneNumber` e `URL`; o kit manda `Phone` e `Url`, os valores de `StringFormatName` |
| `DateTimeBehavior: DateOnly` aceito na criação | o exemplo do Learn só define `Format` |
| Moeda sem `transactioncurrencyid` na linha | a plataforma deve usar a moeda padrão do usuário |
| `$1` em `@odata.bind` para a própria tabela | documentado no `$batch`, sem teste no kit |
| Imagem e arquivo criados por `/Attributes` | sem teste no kit |
| Tempo de criação e bloqueio de customização em sequência | a pausa de 2 s pode ser curta |
| Corpo do GET do conector como objeto ou como texto | o flow lê com `json(string(...))`, que serve aos dois |
| Status do `$batch` quando um changeset falha (erro na chamada ou 200 com o erro dentro) | o flow trata os dois; o Learn só mostra o caso sem changeset |
| `POST .../Keys` pela Web API | o Learn mostra a criação de chave pelo SDK |
| `AssociatedMenuConfiguration` e `IsPrimaryImage` | o plano manda o menu e não manda `IsPrimaryImage`, que dá exceção com `false` |
| Tipo `10037` da referência de conexão no `solution.xml` e `host.connectionName` no flow da solução | o código do tipo varia por ambiente; a importação pode resolver pelo nome |
| Plano grande (centenas de KB) no `base64ToString` e no `json()` do início | cada passo é pequeno, mas o arquivo é lido inteiro |
| Colagem do escopo (§4 B) | as condições e os campos seguem as formas vistas colando outro flow; o nome nas ações de variável, com as variáveis já criadas na raiz, ainda não foi visto |
| Chave `file` da entrada Arquivo do gatilho | vale para a primeira entrada de arquivo; outro flow usa a mesma forma, também sem execução |

## 10. Fontes

- Criar e atualizar tabela pela Web API (campos obrigatórios, `MSCRM.SolutionUniqueName`, `PublishXml`):
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-entity-definitions-using-web-api>
- Criar coluna pela Web API:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-column-definitions-using-web-api>
- Tipos de coluna, formatos de texto, comportamento de data, precisão da moeda:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/entity-attribute-metadata>
- Relacionamentos pela Web API:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-entity-relationships-using-web-api>
- `$batch`, changeset, `Content-ID`, CRLF:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/execute-batch-operations-using-web-api>
- Chave alternativa e `EntityKeyIndexStatus`:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/define-alternate-keys-entity>
- Conector HTTP com Microsoft Entra ID (premium, limite de 100 chamadas por minuto):
  <https://learn.microsoft.com/en-us/connectors/webcontents/>
- Limites do Power Automate (120 s por ação síncrona):
  <https://learn.microsoft.com/en-us/power-automate/limits-and-config>
- `EntitySetName` definido na criação:
  <https://learn.microsoft.com/en-us/power-apps/developer/data-platform/customize-entity-metadata>

# Modelagem Dataverse para apps Power Apps

Tabelas, propriedade, relacionamentos, tipos de coluna, alternate keys, colunas calculadas e
auditoria — o que decidir **antes** de criar, porque boa parte não se desfaz. Solução, ambiente e
variáveis de ambiente são ALM: `skills/power-platform/references/alm-ambientes.md`.

## Sumário

1. [Quem cria o schema](#1-quem-cria-o-schema)
2. [Nomes e convenção](#2-nomes-e-convenção)
3. [Tabela: propriedade e nome principal](#3-tabela-propriedade-e-nome-principal)
4. [Tipos de coluna: o que escolher](#4-tipos-de-coluna-o-que-escolher)
5. [Relacionamento: Lookup, Choice ou texto](#5-relacionamento-lookup-choice-ou-texto)
6. [Colunas desnormalizadas](#6-colunas-desnormalizadas)
7. [Alternate keys](#7-alternate-keys)
8. [Colunas calculadas e rollup](#8-colunas-calculadas-e-rollup)
9. [Obrigatoriedade](#9-obrigatoriedade)
10. [Auditoria e trilha](#10-auditoria-e-trilha)
11. [Checklist antes de criar](#11-checklist-antes-de-criar)

---

## 1. Quem cria o schema

Escolha **um** dono por ambiente e declare:

| Dono | Vantagem | Risco |
|---|---|---|
| **Maker à mão / Excel** | Rápido, sem pré-requisito | O as-built diverge de qualquer plano; publisher padrão; tipos errados |
| **Script (Web API)** | Reproduzível, idempotente, versionável | Precisa de credencial e de manutenção; o ambiente pode ser alterado por fora e divergir do script |
| **Solução importada** | Reprodutível entre ambientes (ALM) | O schema nasce no ambiente de origem |

Seja qual for, **depois de criar**, extraia o as-built (`references/nomes-as-built.md`) e passe a
escrever contra ele. Num projeto de referência, um script completo foi escrito (publisher, choices,
tabelas, colunas, Lookups, alternate keys, idempotente) e **nunca foi usado**: o ambiente foi montado
à mão antes. `[verificado: projeto de referência]` O script não se tornou autoridade só por existir.

Se for script: que ele leia o dicionário (não tenha o schema embutido), seja idempotente (pula o que
existe), confira o resultado (valores inteiros das Choices, `EntityKeyIndexStatus`) e **não** rode sobre
ambiente que já tenha tabelas criadas à mão sem antes extrair o as-built.

## 2. Nomes e convenção

- **Prefixo é do publisher**, não seu. Crie um publisher próprio (e a solução) **antes** das tabelas;
  tabela criada fora de solução cai no publisher padrão e não exporta limpa para outros ambientes.
- Premissa de um projeto de referência que **não se confirmou**: "sem prefixo nos nomes que geramos, o Dataverse aplica o do
  publisher". Pelo maker é verdade; pela Web API o prefixo **precisa** vir no `SchemaName`; e o
  publisher do ambiente real não era o planejado. Planeje com `<prefixo>_` explícito.
- **Nome de exibição = o nome que o Power Fx vai ler.** Se as fórmulas serão escritas com
  `status_cadastro`, a coluna deve ter **esse** nome de exibição; o rótulo humano vai na `Description`
  e nos tokens da tela. Misturar rótulo humano com nome de fórmula é fonte de erro.
  `[verificado: projeto de referência]` (decisão do script de criação).
- Nome lógico não é derivável do de exibição (`references/nomes-e-tipos.md` §2): não escreva
  documento que presuma isso.
- **Nada de nome de ambiente no nome da tabela** (`dev…`): cada ambiente teria tabela diferente e
  o ALM quebra (`decisoes-padrao.md` F5). `[verificado: projeto de referência]` — num projeto
  as tabelas de DEV tinham `dev` no nome lógico e as de produção não.
- Uma convenção só por projeto: `snake_case` em tudo ajuda a portar para SQL sem tradução.

## 3. Tabela: propriedade e nome principal

- **Propriedade** (`OwnershipType`): *UserOwned* (linha tem dono usuário/team — necessária para
  isolamento por owner team/BU) ou *OrganizationOwned* (sem dono; catálogos e tabelas de domínio).
  **Decida na criação:** o tipo não muda depois `[não verificado: afirmação de um projeto de referência; conferir
  no Learn]`. Tabela transacional que talvez precise de isolamento por unidade nasce UserOwned.
- **Nome principal** (`PrimaryNameAttribute`): obrigatório em toda tabela, é o rótulo em grade e
  Lookup. Escolha uma coluna curta e legível; **não** use a narrativa longa nem um campo que repete.
  Uma coluna "rótulo curto" e outra "descrição/observação" separadas evitam gambiarra de
  `Coalesce(observacao; resumo)` na tela. `[verificado: projeto de referência]`
- **Chave primária** é GUID gerado; o negócio usa chave própria (§7).
- Tabela sem uso por nenhuma tela ("tabela morta") custa manutenção; se a decisão de modelagem a
  deixou sem função, registre (caso de uma tabela de perfis quando `perfil` virou Choice).

## 4. Tipos de coluna: o que escolher

| Necessidade | Tipo | Observação |
|---|---|---|
| Domínio **fechado** (lista pequena e estável) | **Choice** (local ou global) | Valida no servidor; `Choices()` alimenta o ComboBox; opção nova é mudança de schema, não de tela |
| Domínio fechado compartilhado entre tabelas | **Choice global** | Valores inteiros prefixados pelo publisher: não presuma `1,2,3` |
| Domínio que muda sem schema (cadastro mantido por usuário) | **Tabela + Lookup** | Mantém integridade; custo: junção |
| Código curto que o negócio já usa como chave (sigla) | **Texto** + alternate key na tabela de origem | Perde integridade referencial |
| Sim/Não | **Yes/No** | `col = true` |
| Só data (prazo, nascimento) | **Date Only** | Elimina fuso e a classe de bug de comparar datas como texto |
| Instante (evento, auditoria) | **Date and Time**, comportamento de fuso explícito | `UserLocal` para o que o usuário vê; `TimeZoneIndependent` para o que não pode mudar |
| Identificador numérico de sistema legado | **Whole Number** | Candidato a alternate key para importar |
| Texto curto | **Text** com tamanho | Limite o tamanho; texto longo não filtra bem |

Regras:

- **Texto não vira Choice nem Lookup depois.** O Dataverse não converte. Trocar o tipo é recriar a
  coluna e migrar. Decida antes de importar (`references/importacao-dados.md`).
- **Choice sem uso**: Choice global criada e não ligada a coluna alguma não é enxergada por
  `Choices()`; o ComboBox daquela opção precisa de tabela literal. `[verificado: projeto de referência]`
- A fonte de tipos e mapeamento para o Power Apps está em
  [Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service).

## 5. Relacionamento: Lookup, Choice ou texto

| Opção | Integridade | Delegação | Importação | Quando |
|---|---|---|---|---|
| **Lookup** | Sim (Dataverse garante) | Filtrar pelo Lookup compara com registro; por coluna do relacionado: junção, evite | Resolve pela coluna de nome principal ou pela alternate key | Relação real 1:N que o negócio exige íntegra |
| **Choice** | Domínio fechado | `=` delega | Resolve pelo rótulo | Lista pequena, estável, sem atributos próprios |
| **Texto com código** | **Nenhuma** | `=` e `StartsWith` delegam | Trivial | Prazo curto; aceita-se o risco (§ abaixo) |

O que se perde ao trocar Lookup por texto `[verificado: projeto de referência]`:

- **Integridade referencial**: valor inválido entra (unidade que não existe); era um dos objetivos da migração.
- **Homônimo colide** quando o texto é nome de pessoa; o vínculo real passa a ser outro campo (ex.: UPN).
- **Join manual** (`LookUp`/`AddColumns`) em vez de `col.campo`.
- **Domínio fechado** some quando Choice vira texto: mudar uma opção vira editar a tela, e nada
  impede o flow de gravar fora do domínio.

Se o as-built já tem texto no lugar do Lookup, **registre a divergência** como decisão (manter ou
realinhar, `references/nomes-as-built.md` §6) e compense: validar o domínio **no flow** antes de gravar,
e conferir o texto contra a tabela de origem na tela de cadastro.

## 6. Colunas desnormalizadas

Filtro quente por coluna de tabela relacionada obriga junção e arrisca a delegação
(`references/delegacao-dataverse.md`). A saída é **copiar** a coluna para a tabela filha como texto:

| Distância até o dado | Solução |
|---|---|
| 0 níveis (coluna da própria tabela) | filtra direto |
| 1 nível (coluna do Lookup) | compara o Lookup com o registro |
| 2 níveis (Lookup do Lookup) | **coluna desnormalizada** na tabela filha |

`[não verificado: a premissa de que filtrar por coluna de Lookup "desiste da delegação" veio do plano de um projeto de referência; o Learn
fala em limite de níveis de lookup. Teste com limite 1 antes de dar a desnormalização por obrigatória.]`

Regras da desnormalização: documente **quem grava** a cópia (o flow, na mesma ação que cria a linha) e
**quando divergir é correto** (a trilha guarda o valor vigente no evento, não o atual).

## 7. Alternate keys

Chave alternativa = uma ou mais colunas que identificam uma linha **sem o GUID**. É o que permite
**upsert** e importação resolvendo Lookup por chave de negócio.
([Define alternate keys](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/define-alternate-keys-portal),
[para desenvolvedores](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/define-alternate-keys-entity)).

Fatos:

- A chave **não fica disponível na hora**: ao salvar, um job de sistema cria o índice. Estado:
  `Pending` → `In Progress` → `Active` (ou `Failed`). Pela Web API:
  `GET <org>/api/data/v9.2/EntityDefinitions(LogicalName='<tabela>')/Keys?$select=SchemaName,EntityKeyIndexStatus`.
  Chave em `Pending` **não resolve Lookup na importação e o erro é silencioso**. `[verificado: projeto de referência]`
- Se o dado da coluna da chave contém `/ # < > * % & : \ ? +`, `GET` e `PATCH` pela chave **não
  funcionam** (Learn, página acima). Só uniqueness, ok; para integração, escolha colunas sem esses
  caracteres.
- Chave pode ser **composta** (várias colunas). Limites do Learn: até 10 chaves por tabela, 16 colunas e
  900 bytes por chave; só colunas de texto de linha única, número inteiro ou decimal, data e hora,
  Lookup e Choice; coluna com segurança de coluna não entra em chave; chave não existe em tabela virtual
  ([Work with alternate keys](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/define-alternate-keys-entity)).
- Exemplo: o identificador de negócio do pedido (`id_pedido`) **não é único** pela regra de negócio, então o
  assistente de importação não resolveria o Lookup pelo nome principal; um `id_legado` numérico foi
  marcado como alternate key e a carga o usou como coluna de correspondência.
- Exemplo: o upsert por `$batch` depende de **chave composta** (várias colunas: unidade, tipo,
  data); o flow monta um índice `{chave → GUID}` para separar Update de Create.
  Com alternate key composta ativa, a busca pelo GUID pode ser substituída por endereçar a linha pela
  chave (upsert), `[não verificado: não testado]`; o formato do `$batch` é de `power-automate`.

Defina a alternate key **ao modelar**, ative-a e **espere `Active`** antes de importar ou subir o flow.

## 8. Colunas calculadas e rollup

- **Calculada**: fórmula avaliada na leitura, na própria linha
  ([Learn](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/define-calculated-fields)).
  Útil para exibição e para derivar um valor que a tela não deve montar.
- **Rollup**: agregação sobre linhas relacionadas, recalculada por job assíncrono
  ([Learn](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/define-rollup-fields)):
  o valor **não é em tempo real**.
- Não presuma que filtrar por coluna calculada delega: `[não verificado]` — confirme no Monitor.
  Quando precisar filtrar por derivado (ex.: "atrasado" calculado de uma data), **filtre pela coluna
  de origem** (a data) e use a calculada só para exibir. `[verificado: projeto de referência]` (a coluna de
  status de prazo é só exibição; o filtro usa a data).
- **Criação**: calculada com fórmula complexa costuma ser feita no maker; não presuma que script de
  Web API a cria (num projeto de referência foi um dos dois itens que continuaram manuais).
- Para SQL a coluna calculada e persistida é de `sql-procedures` (B2); não confunda com esta.

## 9. Obrigatoriedade

Níveis de exigência no Dataverse: opcional, **recomendado pelo negócio** e **obrigatório pelo negócio**.
Obrigatório derruba a carga de dado legado que não tem o campo.

| Situação | Decisão |
|---|---|
| Regra nova, sem legado | Obrigatório |
| Regra de negócio exige, mas o legado está vazio (ex.: a imensa maioria sem a data) | **Recomendado** no Dataverse + obrigatoriedade **no flow** de cadastro/edição |

Assim o legado entra como está (o vazio é informação) e a regra vale para 100% dos registros novos.
Antes de decidir, **meça** o legado: `[verificado: projeto de referência]` — a quase
totalidade das linhas vinha sem a data obrigatória pela regra; se fosse obrigatória no schema, a carga histórica inteira falharia.
Confirme com a operação antes: se a regra nunca foi praticada, tornar obrigatório no flow trava o
cadastro no primeiro dia.

## 10. Auditoria e trilha

Duas coisas diferentes:

- **Auditoria do Dataverse**: registro automático de quem mudou o quê, por tabela/coluna, habilitado
  no ambiente e na tabela
  ([Manage Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing)).
  Boa para conformidade; consome capacidade; **não** é a trilha de negócio mostrada ao usuário.
  `[não verificado]` se algum projeto de referência a ligou.
- **Tabela de trilha do app** (evento de negócio com tipo, valor anterior e novo, usuário): escrita
  pelo flow na mesma ação da mudança. É o que a tela de histórico lê. Desnormalize a unidade e o
  identificador de negócio nela (§6) e guarde o **valor vigente no momento** do evento.
- **Tabelas de log de execução de flow** (execução e flow pai) no próprio Dataverse: o desenho do log é
  de `power-automate`, mas as tabelas são desta skill. Defina quais colunas **todo** flow preenche
  (uma versão nova do flow que deixa nulas colunas que a anterior preenchia estraga o relatório).

## 11. Checklist antes de criar

- [ ] Publisher e solução próprios criados; prefixo anotado.
- [ ] Dono da criação do schema definido (script **ou** maker).
- [ ] Cada relação com decisão: Lookup, Choice ou texto, com o custo registrado.
- [ ] Cada tabela com propriedade (UserOwned/OrganizationOwned) decidida, considerando §3 e `references/seguranca.md`.
- [ ] Alternate keys definidas para tudo que for importado ou receber upsert; plano de esperar `Active`.
- [ ] Choices criadas **antes** das tabelas que as usam; valores inteiros anotados.
- [ ] Obrigatoriedade conferida contra a massa legada.
- [ ] Domínio fechado que ficou como texto tem validação no flow.
- [ ] Depois de criar: as-built extraído (`references/nomes-as-built.md`).

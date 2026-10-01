# ALM e ambientes

Dono: skill `power-platform`. As skills `power-automate` e `dataverse` apontam para cá.
Cobre ambientes DEV/HML/PRD, soluções, variáveis de ambiente, connection references, `pac` CLI,
export/import, Git e o que vai por **colagem** × por **solução**.

Marcas de fonte: link do Microsoft Learn (consultado em 2026-10), `[verificado: projetos de
referência]` ou `[não verificado]`.

## Sumário

1. [Ambientes](#1-ambientes)
2. [Soluções](#2-soluções)
3. [Variáveis de ambiente](#3-variáveis-de-ambiente)
4. [Connection references](#4-connection-references)
5. [Colagem × solução](#5-colagem--solução)
6. [pac CLI](#6-pac-cli)
7. [Arquivo de configuração de implantação](#7-arquivo-de-configuração-de-implantação)
8. [Git e pipelines](#8-git-e-pipelines)
9. [Canvas: .msapp e pac canvas](#9-canvas-msapp-e-pac-canvas)
10. [Procedimento de promoção](#10-procedimento-de-promoção)
11. [Nada de `dev*` em nome](#11-nada-de-dev-em-nome)
12. [Lacunas conhecidas](#12-lacunas-conhecidas)

## 1. Ambientes

| Ambiente | Para quê | Solução | Quem altera |
|---|---|---|---|
| DEV | construir; única origem das **alterações** (a fonte de verdade é o Git) | **não gerenciada** | quem desenvolve |
| HML | homologação/UAT com dado de teste | **gerenciada** | só por importação |
| PRD | operação | **gerenciada** | só por importação, depois de HML aprovada |

- Todo ambiente que participa de ALM precisa de **banco Dataverse**, mesmo quando os dados do
  negócio ficam em SQL Server — a solução, as variáveis e as connection references vivem no
  Dataverse. [Microsoft Learn — ALM overview](https://learn.microsoft.com/en-us/power-platform/alm/overview-alm)
- Regra de ouro: **nada se edita direto em HML/PRD**. Correção nasce em DEV, versiona, exporta, importa.
- Declare no `00-LEIA-PRIMEIRO.md` do projeto: URL lógica de cada ambiente (sem segredo), quem tem
  acesso, e qual banco/servidor cada um usa. Valores reais ficam fora do repositório do plugin.
- Fonte de teste nunca é a de produção disfarçada: HML aponta para fonte de HML.

## 2. Soluções

- **Solução é o mecanismo de ALM**: distribui componentes (tabelas, apps Canvas, flows,
  variáveis de ambiente, connection references) entre ambientes por export/import.
  [Microsoft Learn — ALM overview](https://learn.microsoft.com/en-us/power-platform/alm/overview-alm)
- Exportar/importar o pacote do app Canvas isolado (`.msapp`/pacote) **não suporta ALM**: serve só
  para movimentação básica. Todo app e flow de um projeto vive **dentro de uma solução**.
- **Uma solução por projeto** (ou por domínio de implantação), com publisher do projeto e
  prefixo declarado em `prefixo_publisher`. Evite o publisher padrão.
- **Gerenciada** em HML/PRD, **não gerenciada** em DEV; a gerenciada é artefato de build (exporte a
  não gerenciada como gerenciada) e não se importa no mesmo ambiente da origem. Ao **desinstalar** uma
  gerenciada, os dados das tabelas e colunas que ela criou são perdidos.
  Fonte: https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm (consultado 2026-10).
- **Versão** em toda exportação (`pac solution version` ou `online-version`); a versão entra no
  nome do arquivo e no `CHANGELOG` do projeto.
- Componentes criados **fora** da solução (flow "Meus flows", app solto) não viajam: adicione à
  solução antes de exportar. Um flow fora de solução usa conexões diretas, não connection reference.
  [Microsoft Learn — connection reference](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-connection-reference)
- Custom connectors vão em **solução separada**, importada antes da que tem flows/connection
  references que os usam (mesma doc, "Known issues").
- Tamanho máximo de solução: 95 MB (doc de variáveis de ambiente, FAQ).

## 3. Variáveis de ambiente

Tudo que muda entre DEV, HML e PRD sai do código e entra numa variável de ambiente.
[Microsoft Learn — environment variables](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables)

| Tipo | Uso |
|---|---|
| Texto, Número decimal, Dois valores (sim/não), JSON | parâmetros simples: nome de tabela, flag, limite, URL |
| Fonte de dados | parâmetros de conector (ex.: servidor e banco, site e lista) |
| Segredo | valor guardado em Azure Key Vault (exige configurar o cofre) |

Comportamento que importa:

- **Valor padrão** faz parte da definição e é usado se não houver valor atual. **Valor atual** é do
  ambiente e prevalece. A definição viaja na solução; o valor atual é um registro **não gerenciado**
  do ambiente de destino.
- **Remova o valor atual da solução antes de exportar** ("Remover desta solução"): assim o valor de
  DEV não vai junto e a importação pede o valor do destino. Verifique antes de cada export.
- Na importação a interface (e as pipelines) pedem o valor; variável sem padrão e sem valor
  **bloqueia o uso** e gera notificação — preencha antes de ligar flows e liberar o app.
- Propagação: valor alterado pode levar **até 1 hora** para chegar a apps e flows.
- Em solução gerenciada o valor só aparece na solução **Default** do ambiente.
- Limite: **2.000 caracteres** por valor; sem validação no Dataverse (valide no consumidor).
- Nomes `$authentication` e `$connection` são reservados em flows; evite. Nome único e descritivo.
- Variável de ambiente **não é cache**: valor só muda ao salvar/religar; não use para token rotativo.
- SQL Server: com conexão Microsoft Entra, use variáveis de **servidor** e de **banco** separadas.
  Com autenticação SQL (conexão compartilhada) **não** use variável de fonte de dados: servidor e
  banco vêm da própria conexão — use connection reference. (doc de variáveis de ambiente, "SQL Server")
- Dataverse no mesmo ambiente não precisa de variável (o app procura a mesma tabela pelo nome).

O que vira variável de ambiente neste kit: servidor/banco (quando aplicável), nome de tabela de
log, URL de serviço externo, limites e flags de `CONFIG` do flow, e-mail/grupo da caixa de suporte,
identificadores de grupo. **Nunca** token ou senha em texto — use o tipo Segredo.

## 4. Connection references

[Microsoft Learn — connection reference](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-connection-reference)

- Connection reference = componente de solução que aponta para uma **conexão** de um conector.
  Flows de solução ligam-se a ela, nunca à conexão direta; na importação o destino fornece a conexão.
- **Flows** usam connection reference para todo conector; **Canvas** só para conexões
  compartilhadas implicitamente (não OAuth), como SQL Server com autenticação SQL.
- Para ligar um flow, quem liga precisa ser dono das conexões ou ter permissão de uso. Erro
  `ConnectionAuthorizationFailed` = o usuário que liga não tem acesso a pelo menos uma conexão:
  o dono compartilha ("Pode usar") ou liga ele mesmo. Conexão OAuth só se compartilha
  explicitamente com principal de serviço.
- Propriedade da connection reference não se transfere pela área Soluções do maker.
- Canvas e conector customizado: connection reference **não** é reconhecida; após importar, edite o
  app, remova e readicione a conexão do conector customizado (cria camada não gerenciada se a
  solução for gerenciada).
- Copiar ambiente quebra connection references de conectores customizados (recriar).
- Nome: único e descritivo (`<conector>-<função>`); o padrão gerado traz sufixo aleatório.
- **Nunca** copie o ID real de uma connection reference ou de uma conexão para o repositório:
  `00000000-0000-0000-0000-000000000000` no molde, valor real só no arquivo de implantação local.

## 5. Colagem × solução

| Artefato | Entrega por colagem (Studio/designer) | Entrega por solução |
|---|---|---|
| Controle/tela Canvas (YAML) | **sim**: Code view → colar; só nome de controle único | o app inteiro vai na solução |
| `App.OnStart` / named formulas | **manual**: não há colagem do objeto App | vai com o app |
| Flow (definição) | **sim**: colar nós no designer (clipboard); o arquivo colado é o **gabarito** | o flow vai na solução; connection reference e variáveis de ambiente resolvem o ambiente |
| Connection reference, variável de ambiente | **não** (criar no ambiente) | **sim** (definição viaja; valor é do destino) |
| Tabela/coluna/Choice/security role | não | **sim** (Dataverse) |
| Procedure/DDL de SQL | script no banco (DBA) | **não** viaja em solução; entra por script versionado |
| Ligar flow, conceder conexão | humano no ambiente | humano no ambiente |

Regra: **DEV recebe por colagem; HML/PRD recebem só por solução.** Colar direto em HML/PRD cria
divergência que a próxima importação sobrescreve ou conflita.

Cada colagem é um passo 🔴 na fila: diga o controle-pai, o que colar e o que conferir.

## 6. pac CLI

Fonte: [pac solution](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/solution)
(autentique antes com `pac auth`; confirme o ambiente ativo com `pac org who` `[não verificado]`).

| Comando | Para quê |
|---|---|
| `pac solution list` | soluções do ambiente ativo (`--json`) |
| `pac solution export --name <solucao> --path <arquivo.zip> [--managed] [--async]` | exportar (gerenciada com `--managed`); `--overwrite` sobrescreve o zip |
| `pac solution import --path <arquivo.zip> [--settings-file <json>] [--async] [--publish-changes] [--stage-and-upgrade]` | importar; `--settings-file` preenche variáveis e connection references |
| `pac solution create-settings --solution-zip <zip> --settings-file <json>` | gerar o arquivo de configuração de implantação a partir da solução |
| `pac solution unpack --zipfile <zip> --folder <pasta>` / `pack` | abrir/fechar a solução para controle de versão (SolutionPackager) |
| `pac solution clone --name <solucao>` | projeto de solução em pasta (para adicionar componentes) |
| `pac solution sync` | atualizar a pasta com o estado do ambiente |
| `pac solution online-version --solution-name <n> --solution-version 1.0.0.2` | ler/definir versão online |
| `pac solution version --strategy gittags` | versionar por estratégia |
| `pac solution check --path <zip>` | Solution Checker (Power Apps Checker) antes de promover |
| `pac solution upgrade --solution-name <n>` | aplicar upgrade de solução gerenciada |

`unpack`/`pack` têm **formato XML (legado)** e **formato YAML** (Git integration nativa); o formato é
detectado pela pasta `solutions/`. `pack`/`unpack` de solução **são** suportados; já
`pac canvas pack`/`unpack` estão depreciados (seção 9).

Use `--async` em solução grande e prefira `unpack` do `.zip` via CLI a abrir o zip à mão.

## 7. Arquivo de configuração de implantação

Gere sempre pelo comando, depois edite os valores de HML/PRD:

```powershell
pac solution create-settings --solution-zip .\dist\Solucao_1.0.0.2.zip --settings-file .\implantacao\hml.json
```

Estrutura esperada (os nomes de campo vêm do arquivo gerado; **confie no gerado**, não neste molde
`[não verificado]`):

```json
{
  "EnvironmentVariables": [
    { "SchemaName": "<prefixo>_NomeDaVariavel", "Value": "<valor-do-ambiente>" }
  ],
  "ConnectionReferences": [
    { "LogicalName": "<prefixo>_conexao-sql", "ConnectionId": "00000000-0000-0000-0000-000000000000", "ConnectorId": "/providers/Microsoft.PowerApps/apis/shared_sql" }
  ]
}
```

- Um arquivo por ambiente de destino (`hml.json`, `prd.json`), **fora do repositório do plugin**
  e, no repositório do projeto, só se não tiver ID real nem segredo (`.gitignore` por padrão).
- Importe com: `pac solution import --path <zip> --settings-file .\implantacao\hml.json`.
- Segredo nunca no arquivo: tipo Segredo + Key Vault.

## 8. Git e pipelines

- **Git desde o dia 0.** Branch por onda, tag por entrega, `.gitignore` para dados e saídas.
- **Fonte de verdade é o controle de versão**, não o ambiente de DEV.
  [Microsoft Learn — ALM overview](https://learn.microsoft.com/en-us/power-platform/alm/overview-alm)
- Para app Canvas, a via suportada para edição externa, merge e conflito é a **Git integration** do
  Power Platform. [Git integration](https://learn.microsoft.com/en-us/power-platform/alm/git-integration/overview)
- **Pipelines** in-product do Power Platform (Dataverse) fazem DEV → HML → PRD com aprovação e
  mostram os campos de variáveis de ambiente na implantação.
  [Set up pipelines](https://learn.microsoft.com/en-us/power-platform/alm/set-up-pipelines)
  `[não verificado: licença e habilitação por tenant]`
- CI/CD externo (Azure DevOps, GitHub Actions) com Power Platform Build Tools: opcional; as tarefas
  não gerenciam variáveis de ambiente de fonte de dados (doc de variáveis, "limitações").

## 9. Canvas: .msapp e pac canvas

[verificado: projetos de referência] e [Microsoft Learn — pa.yaml](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml)

- `.msapp` é um zip; só `*.pa.yaml` em `\Src` serve como código-fonte.
- Extrair: `Expand-Archive` ou `pac canvas download --name "<app>" -d .\src -o`.
- **`pac canvas pack` e `unpack` estão depreciados** (Preview, fora de desenvolvimento); o layout
  `Experimental` (`*.fx.yaml`) está depreciado e será removido. Se usar, `--layout SourceCode`.
  [pac canvas](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas)
- Merge de duas sessões do Studio: nomes de controle únicos; merge normal em `\Src\*.pa.yaml`; em
  conflito é seguro apagar `\src\editorstate\*.json` e `\other\entropy.json`; conflito em
  `\Connections\*`, `\DataSources\*`, `\pkgs\*` ou `CanvasManifest.json`: **não faça merge**, resolva
  no Studio.
- **Code view**: copia/cola controles; **não** cobre o objeto App (OnStart, Formulas) nem edita no
  lugar. [Code view](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/code-view)

## 10. Procedimento de promoção

DEV → HML → PRD. Cada passo que exige ambiente é 🔴.

1. **Congele o escopo** da entrega; confirme no DEV que a fila tem ✅ com evidência.
2. Rode o **portão final** (`portao-final.md`) sobre o que vai sair.
3. Em DEV: remova o **valor atual** das variáveis de ambiente; incremente a **versão**.
4. `pac solution check` (ou Solution Checker) — corrija erros críticos.
5. `pac solution export --managed --async` → `dist/<solucao>_<versao>.zip`; `unpack` e commit; tag.
6. `pac solution create-settings` → arquivo do ambiente de destino com **valores do destino**.
7. Garanta no destino: banco/servidor existem, conexões criadas e **compartilhadas** com quem liga
   os flows, grupos/caixas existem, scripts de banco aplicados pelo DBA (procedures não viajam).
8. `pac solution import --path <zip> --settings-file <json> --async --publish-changes`.
9. **Ligue os flows** e confirme as connection references (humano dono das conexões).
10. **Fumaça no destino:** abrir o app, executar o ciclo mínimo, ver o histórico do flow, conferir que
    a fonte é a do ambiente (nenhum `dev*`).
11. Registre na fila: comando, versão, saída, data. Rollback = reimportar o estado anterior
    reempacotado com número de versão **maior** que o instalado (planeje antes de HML) e reverter o
    script de banco `[não verificado: comportamento ao importar versão menor]`.

## 11. Nada de `dev*` em nome

- Nenhuma tabela, coluna, variável, flow, connection reference ou pasta de código leva `dev`,
  `hml` ou `prd` **no nome** (ex.: `dev-clientes`). Ambiente é propriedade do **ambiente**, não do nome.
- Nenhum literal de servidor, banco, URL de ambiente ou GUID de produção em fórmula, flow ou
  documento de entrega: use variável de ambiente + connection reference.
- Auditoria rápida (rode da raiz do projeto; o resultado esperado é vazio):

```bash
grep -rniE "dev[-_]|\bdev[a-z]+\b|\.database\.windows|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}" telas/ flows/
```

  Ajuste as pastas ao `power-platform.config.json`; cada resultado é falso positivo justificado
  ou defeito. Por quê: fonte de desenvolvimento lida por uma tela e produção por outra fez o KPI do
  menu divergir da galeria sem bug de fórmula `[verificado: projeto de referência]`.

## 12. Lacunas conhecidas

- Pipeline DEV → PRD real, versionamento de contrato do flow e estratégia de rollback de procedure
  ainda não têm gabarito neste kit `[não verificado]`.
- Habilitação de pipelines in-product e licença Premium dos conectores variam por tenant: confirme
  com a administração antes de prometer.
- O formato exato do arquivo de implantação deve ser conferido com a versão do `pac` em uso.

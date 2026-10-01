# Catálogo de componentes do Power Automate

Blocos de ações **coláveis no designer**, um arquivo por componente, extraídos de flows de projetos de
referência e normalizados pelas regras da skill (R1-R13, `Catch` com `Skipped`, `Terminate` depois de `Nega`,
nenhum literal de ambiente fora do `CONFIG`, flags de segurança ligadas). Nomes, tabelas, procedures e conexões
são placeholders: `<prefixo>_...`, `<procedure_...>`, `<tabela_...>`; entidade de exemplo **Pedido**, escopo **Unidade**.

O molde completo, já montado, é `../flow-gravar-molde.json`. Os componentes são as **peças**; o molde é a **montagem**
e não é repetido aqui.

## Sumário

1. [Como ler este catálogo](#1-como-ler-este-catálogo)
2. [Tabela de componentes](#2-tabela-de-componentes)
3. [Ordem de montagem](#3-ordem-de-montagem)
4. [Regras de colagem comuns](#4-regras-de-colagem-comuns)
5. [O que ficou fora](#5-o-que-ficou-fora)
6. [Como validar](#6-como-validar)

---

## 1. Como ler este catálogo

Cada componente tem `<nome>.md` (explicação) e `<nome>.json` (o mesmo JSON do bloco do `.md`, para o verificador
e para colar). Os componentes descritivos (`trigger-*`) não têm `.json`: o trigger não é colável.

- **Frequência**: quanto o bloco (ou o seu equivalente) se repetiu nos flows de referência, trilhas SQL e Dataverse e
  flow de recebimento: `muito comum` (quase todo flow), `comum`, `ocasional` (poucos flows) ou `rara` (um flow só).
- **Maturidade**:
  - `estável`: aparece em flow colado e **devolvido pelo designer** (gabarito) ou em flow de recebimento em
    execução, e se repete em mais de um flow.
  - `único`: confirmado, mas num flow só (não generaliza sozinho).
  - `desenhado`: gerado por script a partir do projeto e **sem prova no designer**; marcado `[não verificado]`.
  Um componente `estável` pode trazer ajustes marcados `[não verificado]` no próprio arquivo (o que mudou em relação ao gabarito).
- **Conexões**: `<prefixo>_sharedsql`, `<prefixo>_sharedoffice365users`... são nomes lógicos de exemplo da connection
  reference (o padrão do ambiente é `<prefixo>_shared<conector>_<sufixo>`); vale o nome lógico do **seu** ambiente (skill `power-platform`).


## 2. Tabela de componentes

### 2.1 Triggers (digitados à mão)

| Componente | Arquivo | Quando usar | Depende de | Frequência | Maturidade |
|---|---|---|---|---|---|
| [trigger-power-apps-v2](./trigger-power-apps-v2.md) | `trigger-power-apps-v2.md` | Primeiro passo de todo flow chamado pelo app. Digitado à mão: o trigger não é colável. | nenhum | muito comum | estável |
| [trigger-http-recebimento](./trigger-http-recebimento.md) | `trigger-http-recebimento.md` | Primeiro passo do flow de recebimento de sistema externo. Digitado à mão: o trigger não é colável. | nenhum | ocasional | estável |

### 2.2 Núcleo do flow chamado pelo app

| Componente | Arquivo | Quando usar | Depende de | Frequência | Maturidade |
|---|---|---|---|---|---|
| [config](./config.md) | `config.md` + `config.json` | Primeiro bloco de todo flow chamado pelo app: flags de segurança e textos de ambiente num só lugar. | nenhum | muito comum (`CONFIG` nos flows chamados pelo app; `settings` no recebimento, ver `config-recebimento`) | estável |
| [identificar-chamador](./identificar-chamador.md) | `identificar-chamador.md` + `identificar-chamador.json` | Segundo bloco: descobre quem chamou pelo contexto de execução, nunca por parâmetro. | `config`; conector de usuários do Office 365 | muito comum | estável |
| [ler-chamador-sql](./ler-chamador-sql.md) | `ler-chamador-sql.md` + `ler-chamador-sql.json` | Abre o `Try`: lê perfil e flags do chamador numa chamada e nega quem não existe. | `identificar-chamador`; conector SQL; `<procedure_obter_chamador>` | comum | estável |
| [switch-acao](./switch-acao.md) | `switch-acao.md` + `switch-acao.json` | Um flow, várias ações de negócio escolhidas pelo primeiro parâmetro do trigger. | `ler-chamador-sql`; `autorizar-por-flag`; `nega-resposta-terminate` | comum | estável |
| [autorizar-por-flag](./autorizar-por-flag.md) | `autorizar-por-flag.md` + `autorizar-por-flag.json` | Primeira ação de cada ação de negócio: confere a flag daquela ação antes de qualquer escrita. | `ler-chamador-sql` (ou `-dataverse`); `nega-resposta-terminate` | muito comum | estável |
| [nega-resposta-terminate](./nega-resposta-terminate.md) | `nega-resposta-terminate.md` + `nega-resposta-terminate.json` | Átomo de toda negação: responde ao app e encerra o flow. | nenhum | muito comum (vários pares por flow) | estável |
| [normalizar-entrada](./normalizar-entrada.md) | `normalizar-entrada.md` + `normalizar-entrada.json` | Depois de autorizar: transforma o texto cru dos parâmetros em valores limpos e tipados. | `switch-acao` (ou flow de ação única); parâmetros do trigger | comum | estável |
| [derivar-valor-switch](./derivar-valor-switch.md) | `derivar-valor-switch.md` + `derivar-valor-switch.json` | O valor gravado depende de uma combinação de estados e uma cadeia de `if()` estouraria o limite. | `normalizar-entrada` | rara | único + ajustes [não verificado] |
| [estado-antes](./estado-antes.md) | `estado-antes.md` + `estado-antes.json` | Ação que altera registro existente: o escopo e a idempotência dependem do registro real. | `normalizar-entrada`; conector SQL; `<tabela_pedido>` | comum | estável |
| [escopo-unidade](./escopo-unidade.md) | `escopo-unidade.md` + `escopo-unidade.json` | Barra quem não é global de agir sobre registro de outra unidade. | `config` (`cfgEscopoUnidade`); `estado-antes`; `ler-chamador-sql` | comum | estável |
| [validar-com-mensagem](./validar-com-mensagem.md) | `validar-com-mensagem.md` + `validar-com-mensagem.json` | Depois de normalizar: uma expressão devolve a primeira mensagem de erro ou vazio. | `normalizar-entrada`; `nega-resposta-terminate` | comum | estável |
| [trilha-de-auditoria](./trilha-de-auditoria.md) | `trilha-de-auditoria.md` + `trilha-de-auditoria.json` | Edição em que cada campo alterado precisa virar uma linha de histórico. | `estado-antes`; `normalizar-entrada` | ocasional | único |
| [se-nada-mudou](./se-nada-mudou.md) | `se-nada-mudou.md` + `se-nada-mudou.json` | Evita gravar (e logar, e disparar e-mail) quando o pedido já está no estado desejado. | `estado-antes`; `normalizar-entrada`; `nega-resposta-terminate` | comum | estável |
| [gravar-via-procedure](./gravar-via-procedure.md) | `gravar-via-procedure.md` + `gravar-via-procedure.json` | Toda escrita em SQL: o flow decide, a procedure executa e devolve um código. | `normalizar-entrada`; conector SQL; `<procedure_gravar_pedido>` | comum | estável |
| [traduzir-codigo-e-responder](./traduzir-codigo-e-responder.md) | `traduzir-codigo-e-responder.md` + `traduzir-codigo-e-responder.json` | Último bloco do caso: o código devolvido pela escrita vira `status` e `description`. | `gravar-via-procedure`; `nega-resposta-terminate` (mesmo contrato) | muito comum | estável + ajustes [não verificado] |
| [catch-conector](./catch-conector.md) | `catch-conector.md` + `catch-conector.json` | Fecha o flow: sem ele o app recebe timeout em vez de mensagem. | `ler-chamador-sql` (cria `Try_pedido`); `nega-resposta-terminate` | comum | estável |

### 2.3 Variantes da trilha Dataverse

| Componente | Arquivo | Quando usar | Depende de | Frequência | Maturidade |
|---|---|---|---|---|---|
| [ler-chamador-dataverse](./ler-chamador-dataverse.md) | `ler-chamador-dataverse.md` + `ler-chamador-dataverse.json` | Variante do `ler-chamador-sql` quando usuário e perfil estão em Dataverse. | `identificar-chamador`; conector Dataverse; tabelas `<prefixo>_usuarios` e `<prefixo>_perfis` | comum | desenhado [não verificado] |
| [escopo-unidades-dataverse](./escopo-unidades-dataverse.md) | `escopo-unidades-dataverse.md` + `escopo-unidades-dataverse.json` | Usuário com mais de uma unidade, guardadas numa tabela de vínculo. | `ler-chamador-dataverse`; tabela de vínculo usuário-unidade | ocasional | desenhado [não verificado] |
| [compensacao-dataverse](./compensacao-dataverse.md) | `compensacao-dataverse.md` + `compensacao-dataverse.json` | Escrita em duas ou mais tabelas Dataverse sem transação: desfaz a primeira se a segunda falhar. | `normalizar-entrada`; conector Dataverse; `nega-resposta-terminate` | rara | desenhado [não verificado] |

### 2.4 Efeitos e relatórios

| Componente | Arquivo | Quando usar | Depende de | Frequência | Maturidade |
|---|---|---|---|---|---|
| [resolver-id-diretorio](./resolver-id-diretorio.md) | `resolver-id-diretorio.md` + `resolver-id-diretorio.json` | O pedido de acesso precisa do id do usuário no diretório e o app pode não ter. | `validar-com-mensagem`; conector de usuários do Office 365 | ocasional | desenhado [não verificado] |
| [email-suporte-com-parcial](./email-suporte-com-parcial.md) | `email-suporte-com-parcial.md` + `email-suporte-com-parcial.json` | Um efeito externo (e-mail) e uma escrita no mesmo caminho: o e-mail já saiu quando a escrita falha. | `resolver-id-diretorio`; conectores de e-mail do Office 365 e SQL | ocasional | desenhado [não verificado] |
| [filtros-json-da-tela](./filtros-json-da-tela.md) | `filtros-json-da-tela.md` + `filtros-json-da-tela.json` | O app envia vários filtros opcionais num único parâmetro (`JSON()` do Power Fx). | `autorizar-por-flag`; parâmetro de filtros no trigger | ocasional | desenhado [não verificado] |
| [exportar-csv-arquivo](./exportar-csv-arquivo.md) | `exportar-csv-arquivo.md` + `exportar-csv-arquivo.json` | Relatório que o usuário baixa: gera o arquivo e devolve o link no campo `url`. | `config` (`pastaSaida`); uma leitura anterior `Ler_dados_exportacao`; conector de arquivos de nuvem da Microsoft (id do conector no JSON) | ocasional | desenhado [não verificado] |
| [html-para-pdf](./html-para-pdf.md) | `html-para-pdf.md` + `html-para-pdf.json` | Documento ou etiqueta imprimível sem Excel nem Office Script. | `exportar-csv-arquivo` (mesma pasta); `Linhas_html`; conector de arquivos de nuvem da Microsoft (id do conector no JSON) | ocasional | desenhado [não verificado] |

### 2.5 Recebimento HTTP e lote

| Componente | Arquivo | Quando usar | Depende de | Frequência | Maturidade |
|---|---|---|---|---|---|
| [config-recebimento](./config-recebimento.md) | `config-recebimento.md` + `config-recebimento.json` | Primeiro bloco do flow de recebimento HTTP: tabela destino, tamanho do lote, colunas de chave e origem do token. | nenhum | ocasional (só flow de recebimento); o papel de `config` é muito comum | estável |
| [token-cache-e-resposta-http](./token-cache-e-resposta-http.md) | `token-cache-e-resposta-http.md` + `token-cache-e-resposta-http.json` | Esqueleto de todo flow de recebimento HTTP: valida a credencial e responde 200 ou 401 pelo resultado real. | `config-recebimento`; conector de validação de token; tabela de cache; 2 `Initialize variable` na raiz | cache: rara; resposta HTTP: ocasional | único + ajustes [não verificado] |
| [mapear-lote](./mapear-lote.md) | `mapear-lote.md` + `mapear-lote.json` | Única cópia do mapeamento origem -> colunas do destino, antes de qualquer gravação. | `config-recebimento`; corpo `{ dados: [...] }` | ocasional | estável |
| [upsert-unitario](./upsert-unitario.md) | `upsert-unitario.md` + `upsert-unitario.json` | Lote com uma linha só: evita ler a tabela inteira para gravar uma linha. | `mapear-lote`; `config-recebimento`; conector HTTP com Entra ID (`InvokeHttp`) e Dataverse | rara | único |
| [indice-chaves-destino](./indice-chaves-destino.md) | `indice-chaves-destino.md` + `indice-chaves-destino.json` | Lote sem alternate key: separa quem já existe (update) de quem não existe (create). | `mapear-lote`; `config-recebimento`; `paginacao-nativa` (a leitura já traz a paginação) | ocasional | estável |
| [batch-upsert-changeset](./batch-upsert-changeset.md) | `batch-upsert-changeset.md` + `batch-upsert-changeset.json` | Gravar muitas linhas com poucas chamadas: update de quem existe, create de quem não existe. | `indice-chaves-destino`; `config-recebimento`; variáveis `Erros_lote` e `Linhas_com_erro` na raiz; conector HTTP com Entra ID | ocasional | estável + ajustes [não verificado] |
| [paginacao-nativa](./paginacao-nativa.md) | `paginacao-nativa.md` + `paginacao-nativa.json` | Ler mais do que uma página de resultados sem `Do_until` nem variável de skiptoken. | `config`; conector Dataverse | ocasional (nativa na maioria; `Do_until` só em flow antigo) | estável |

### 2.6 Observabilidade

| Componente | Arquivo | Quando usar | Depende de | Frequência | Maturidade |
|---|---|---|---|---|---|
| [log-execucao](./log-execucao.md) | `log-execucao.md` + `log-execucao.json` | Todo flow de recebimento (F4): sem log ninguém sabe qual ação quebrou, para quem e quanto durou. | `token-cache-e-resposta-http` (`Escopo_Principal`); `batch-upsert-changeset` (variáveis); tabelas de monitoramento e de execução | rara | único |

## 3. Ordem de montagem

### 3.1 Flow chamado pelo app (trilha SQL; troque 4 e 9 na trilha Dataverse)

No escopo raiz (`Escopo_<flow>`), depois do trigger:

1. [`trigger-power-apps-v2`](./trigger-power-apps-v2.md): digitado à mão (parâmetros posicionais)
2. [`config`](./config.md): `Bloco_config`
3. [`identificar-chamador`](./identificar-chamador.md): `Bloco_chamador`
4. [`ler-chamador-sql`](./ler-chamador-sql.md): cria `Try_pedido` (ou `ler-chamador-dataverse`)
5. [`switch-acao`](./switch-acao.md): dentro do `Try`; um `Caso_<acao>` por ação

Dentro de cada `Caso_<acao>`, nesta ordem:

6. [`autorizar-por-flag`](./autorizar-por-flag.md): primeiro nó do caso (sem `runAfter`)
7. [`normalizar-entrada`](./normalizar-entrada.md): ou `filtros-json-da-tela` em exportação; `derivar-valor-switch` se há valor derivado
8. [`estado-antes`](./estado-antes.md): só em ação sobre registro existente
9. [`escopo-unidade`](./escopo-unidade.md): ou `escopo-unidades-dataverse`
10. [`validar-com-mensagem`](./validar-com-mensagem.md)
11. [`trilha-de-auditoria`](./trilha-de-auditoria.md): opcional; só em edição com histórico
12. [`se-nada-mudou`](./se-nada-mudou.md): opcional; com a trilha aponte para `Bloco_trilha`
13. [`gravar-via-procedure`](./gravar-via-procedure.md): ou `compensacao-dataverse` (Dataverse) ou `email-suporte-com-parcial` (efeito externo)
14. [`traduzir-codigo-e-responder`](./traduzir-codigo-e-responder.md): último nó do caso

Depois do `Try`:

15. [`catch-conector`](./catch-conector.md): fora do `Try`, irmão dele
16. [`log-execucao`](./log-execucao.md): opcional em flow chamado pelo app (ver armadilha de `Terminate`)

A montagem pronta, com um caso só, é o molde `../flow-gravar-molde.json`.

### 3.2 Flow de recebimento HTTP

1. [`trigger-http-recebimento`](./trigger-http-recebimento.md): digitado à mão; mais as duas variáveis de raiz
2. [`token-cache-e-resposta-http`](./token-cache-e-resposta-http.md): `Escopo_Principal` com `Scope_Token` e as duas respostas
3. [`config-recebimento`](./config-recebimento.md): dentro do escopo principal
4. [`mapear-lote`](./mapear-lote.md): pendurado em `Resposta_sucesso` (paralelo ao token)
5. [`upsert-unitario`](./upsert-unitario.md): ramo `Sim` para N = 1
6. [`indice-chaves-destino`](./indice-chaves-destino.md): ramo `Não`; usa `paginacao-nativa` na leitura
7. [`batch-upsert-changeset`](./batch-upsert-changeset.md): ramo `Não`, depois do índice
8. [`log-execucao`](./log-execucao.md): irmão do `Escopo_Principal`

### 3.3 Blocos de apoio por tipo de flow

a. [`resolver-id-diretorio`](./resolver-id-diretorio.md): antes do e-mail
b. [`email-suporte-com-parcial`](./email-suporte-com-parcial.md): efeito externo com escrita parcial
c. [`filtros-json-da-tela`](./filtros-json-da-tela.md): exportação: depois de autorizar
d. [`exportar-csv-arquivo`](./exportar-csv-arquivo.md): exportação em CSV
e. [`html-para-pdf`](./html-para-pdf.md): exportação em PDF

Átomos usados em todo lugar: [`nega-resposta-terminate`](./nega-resposta-terminate.md) e [`paginacao-nativa`](./paginacao-nativa.md).

## 4. Regras de colagem comuns

1. **Cole de cima para baixo**, na ordem da seção 3. O `runAfter` da raiz de cada envelope aponta para o nó anterior
   da ordem de montagem; confira o nome e ajuste ao seu flow.
2. **Primeiro nó de um ramo** (`Caso_`, `Sim`, `Não`) não tem `runAfter`: apague a chave `runAfter` do nó raiz antes de
   colar. O verificador lê o trecho como fragmento porque a raiz tem `runAfter`; sem ele, referências a ações de fora
   viram erro.
3. **Nomes são únicos no flow inteiro** (F004). Cada componente usa o sufixo `_gravar`; troque pelo sufixo da ação
   (`_excluir`...) em todas as ocorrências, inclusive dentro de `outputs('...')` e `body('...')`.
4. **Conexões**: cada envelope traz `allConnectionData` com uma entrada por ação de conector (R1). O `<prefixo>_shared...`
   é o nome lógico da connection reference do **ambiente destino**; nunca copie o de outro ambiente.
5. **Avisos esperados do verificador**: `F006` (a ação referida está fora do trecho colado: `CONFIG`, `Chamador`,
   `Normalizar_gravar`...) e, em dois componentes, `F009` (escopo sem `Skipped` de propósito). Cada arquivo lista os seus.
6. **Envelope de escopo**: um bloco de uma ação só vira `Scope` embrulhando; o escopo é transparente em execução e custa
   um nível de indentação no designer (`../../references/formato-clipboard.md` §2).
7. **Trigger e variáveis de raiz** (`Initialize variable`) são digitados à mão.
8. Depois de colar e salvar, **devolva** o que o designer devolveu ao gabarito do projeto (arquivo somente leitura); o
   que o designer normaliza é regra nova (`../../references/gabarito-designer.md`).

## 5. O que ficou fora

| Bloco | Por quê |
|---|---|
| Office Script / Excel (código de barras, planilha) | Nenhum flow de referência chama Office Script: o script existia como "plano B" e o desenho final gera o HTML dentro do flow. Sem uso em execução |
| Identificador de largura fixa (ex.: código de barras) em WDL | Depende de comprimento fixo de entrada; fica em `html-para-pdf` apenas como nota |
| `Select`, `Filter array` (`Query`), `Compose` soltos | Aparecem em quase todo componente (mapeamento, índice, trilha, CSV); sozinhos são ação trivial do designer |
| `Apply to each` com concorrência | Absorvido por `batch-upsert-changeset` (`chunk` + `concurrency`); fora do lote, o `Foreach` com contador é ação trivial |
| Variáveis (`Initialize/Increment/Append`) | `Initialize` só vale na raiz e é digitado à mão (`trigger-http-recebimento`); `Increment/Append` estão dentro do lote |
| Paginação por `Do_until` + skiptoken | Desenho antigo; a nativa (`paginacao-nativa`) a substitui |
| Notificação de usuário por Teams | Não aparece em nenhum dos flows de referência |
| Retentativa de 429 no conector `InvokeHttp` | `[não verificado]`: como a política aparece no JSON do designer; fica como armadilha em `batch-upsert-changeset` |

## 6. Como validar

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/componentes/<arquivo>.json
python -m pytest tests/power-automate -q -p no:cacheprovider
python tools/lint_skills.py skills/power-automate
```

Destino: terminal, da raiz do repositório. O teste `tests/power-automate/test_componentes_fluxo.py` roda o verificador sobre
**todos** os `.json` desta pasta e exige `0 erro(s)`; confere que o JSON do bloco de cada `.md` é igual ao do `.json`
ao lado e que todo componente está neste índice.

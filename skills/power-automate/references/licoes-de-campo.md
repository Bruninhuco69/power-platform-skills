# Lições de campo: flows

Defeitos e decisões que apareceram em flows reais e que ainda não cabiam numa regra isolada das
outras referências. Cada lição traz o que aconteceu, em termos genéricos, e a regra ou o arquivo que
a previne. Não é regra por si: o que vale está nos arquivos citados.

## Sumário

1. [Condição de "nada mudou" que nunca é verdadeira](#1-condição-de-nada-mudou-que-nunca-é-verdadeira)
2. [O flow não tem permissão: o pedido humano é um desenho legítimo](#2-o-flow-não-tem-permissão-o-pedido-humano-é-um-desenho-legítimo)
3. [Geração de arquivo no flow tem teto](#3-geração-de-arquivo-no-flow-tem-teto)
4. [Decisão de produto com consequência aceita fica escrita](#4-decisão-de-produto-com-consequência-aceita-fica-escrita)
5. [Constante de domínio por inteiro vem da captura do ambiente](#5-constante-de-domínio-por-inteiro-vem-da-captura-do-ambiente)
6. [Verificar um trecho colado, não o flow inteiro](#6-verificar-um-trecho-colado-não-o-flow-inteiro)
7. [Defeitos de um flow de recebimento que o desenho comum não evita](#7-defeitos-de-um-flow-de-recebimento-que-o-desenho-comum-não-evita)

---

## 1. Condição de "nada mudou" que nunca é verdadeira

| | |
|---|---|
| **O que aconteceu** | Uma edição "sem alterações" nunca era detectada: a lista de linhas de trilha tinha um item incondicional, então `length(lista) = 0` jamais ocorria e o ramo "nada mudou" era código morto. Corrigir o `If` não bastava: o erro estava em como a lista era montada. |
| **Previne** | `expressoes-wdl-armadilhas.md` §7 (listas vazias e índice) e `verificar-fluxo.py` F016 (condição constante). Ao revisar uma condição, revise **o que ela testa**, não só o `If`: monte a lista só com os itens condicionais. |

## 2. O flow não tem permissão: o pedido humano é um desenho legítimo

| | |
|---|---|
| **O que aconteceu** | Um flow de provisionamento de acesso (conceder e revogar) não tinha permissão para escrever no grupo do diretório do tenant. O desenho adotado foi enviar o pedido por e-mail ao suporte, que executa a mudança, em vez de forçar uma permissão ampla na conta do conector. |
| **Previne** | `autorizacao-no-flow.md` (o flow recusa o que o chamador não pode) e `decisoes-padrao.md` A2/A3. O flow registra o pedido no log e responde `warning` ("pedido enviado"), nunca `success` como se o efeito já tivesse ocorrido. |

## 3. Geração de arquivo no flow tem teto

| | |
|---|---|
| **O que aconteceu** | Um flow de exportação gerava CSV e etiquetas com identificador de largura fixa montado em expressões WDL puras; o conversor de arquivo recusava HTML acima de cerca de 2 MB. |
| **Previne** | `sql-no-flow.md` §5 (limites do conector: resposta 8 MB e requisição 2 MB atrás de gateway): exportação grande pede paginação ou partição em arquivos menores, e a procedure de contagem roda **antes** da exportação para decidir. |

## 4. Decisão de produto com consequência aceita fica escrita

| | |
|---|---|
| **O que aconteceu** | O escopo "todas as unidades" colapsou numa única flag do perfil e passou a valer **também para escrita**. A decisão foi registrada com a consequência aceita: quem tem a flag encerra em qualquer unidade (a flag de permissão da ação continua valendo). O perfil chegou a ter mais de uma dezena de flags de permissão por ação. |
| **Previne** | `autorizacao-no-flow.md` §3 e §4: escopo e permissão são coisas diferentes (*o quê* × *onde*); o que se aceita perder vai para o ADR do projeto, para ninguém "consertar" depois sem saber que era deliberado. |

## 5. Constante de domínio por inteiro vem da captura do ambiente

| | |
|---|---|
| **O que aconteceu** | Os inteiros dos tipos de evento da trilha eram palpite até a captura do ambiente; o nome real das procedures também (só uma fração estava confirmada quando o gabarito foi fechado). |
| **Previne** | `gabarito-designer.md` R9 e `sql-procedures/references/deploy-e-dba.md` §7: nome e constante vêm do ambiente (`sys.procedures`, extração datada), e o que não foi lido fica marcado como hipótese. |

## 6. Verificar um trecho colado, não o flow inteiro

| | |
|---|---|
| **O que aconteceu** | Rodado só-leitura sobre os arquivos de entrega de um flow de recebimento (um `.md` por nó de escopo do clipboard, JSON de uma linha), o verificador acusou 1 erro (F016, a `Condição` constante) na versão antiga e **0 erro** na nova, com os avisos esperados (F014 tabela de DEV, F015 `Response` antecipada, F018). O escopo de validação reutilizável passou limpo; o escopo `Log` recebeu F009 (sem `Skipped`, intencional: F4) e F006 (referência a `Escopo_Principal`, que está fora do trecho). A inicialização da variável de erros não estava no arquivo entregue, e o valor inicial foi presumido. |
| **Previne** | `formato-clipboard.md` (F006 vira aviso para ação fora do trecho) e `decisoes-padrao.md` F4. Antes de confiar no resultado, tenha o inventário do flow completo: o trecho não carrega a inicialização do tronco. |

## 7. Defeitos de um flow de recebimento que o desenho comum não evita

| | |
|---|---|
| **O que aconteceu** | Num flow de recebimento HTTP com `$batch`, mesmo depois de uma reescrita, ficaram: o nome da tabela de DEV fixo na configuração, na busca unitária e na leitura paginada; o token no corpo e em claro na tabela de cache; o 200 devolvido antes de processar; o erro do `$batch` detectado por substring (`'400 Bad Request'`), sem tratar 500/503/504/429; a contagem de falhas por linhas do chunk, não por parte (falha pessimista); o corpo do `$batch` montado com `\n` quando a documentação exige CRLF; o status do log só 0/1, com tipo de flow e retentativas fixos; um filtro de leitura com sentinelas (`or ... eq 99`) para o filtro nunca ficar vazio. |
| **Previne** | `decisoes-padrao.md` F5, `http-entrada-externa.md` §3 e §5, `dataverse-batch-upsert.md` §4 e §5, `log-execucao.md` §1. O verificador acusa F014 (literal de ambiente) e F015 (`Response` antecipada). Quando um flow nasce de um modelo comunitário, reescreva a lista acima como checklist de revisão. |

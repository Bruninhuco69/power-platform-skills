# Matriz de tecnologia — Dataverse × SQL Server

Critérios para a decisão de trilha de dados (decisão A4: uma trilha por projeto; trocar exige ADR
— `assets/adr-molde.md`). Vale para projeto novo; em projeto existente, a trilha já está
declarada no `power-platform.config.json`.

## Sumário

1. [Matriz](#1-matriz)
2. [Quando escolher cada uma](#2-quando-escolher-cada-uma)
3. [Power BI](#3-power-bi)
4. [SharePoint](#4-sharepoint)
5. [Fora do Power Platform e nunca](#5-fora-do-power-platform-e-nunca)
6. [Como registrar a decisão](#6-como-registrar-a-decisão)

---

## 1. Matriz

Origem: dois projetos de referência em produção, um em cada trilha. Itens `[externo]` não foram
medidos nesses projetos; confirme na documentação ou no ambiente.

| Critério | Dataverse | SQL Server + procedures + Power Automate |
|---|---|---|
| Quem cria o schema | o maker, rápido; o as-built diverge de qualquer script (prefixo do publisher) | o DBA, com ciclo de pedido e congelamento em produção |
| Prazo para começar | curto, sem DBA | maior: pedidos de DDL, rodadas de colunas, provas de ambiente |
| `CountRows(Filter(...))` | delega (até o teto de agregação) | **não delega**: conta no cliente até o teto de 500/2.000; mostrar `2.000+` ou contar no servidor |
| Filtro de data | delega | não delega atrás de gateway: coluna calculada inteira (B2) |
| `in`, `Search`, `Upper/Lower` em `Filter` | não delega | não delega |
| Transação em várias tabelas | não (compensação em `Catch`) | **sim** (`XACT_ABORT ON` na procedure) |
| Tipagem | Choice e Lookup nativos | `BIT NOT NULL`, PK obrigatória (sem PK, só leitura), UNIQUE filtrado |
| Isolamento por linha | Security Role limita tabela, não linha; Owner Team/Business Unit custa esforço | RLS por contexto de sessão é inviável com conta de serviço compartilhada; autorização vai para o flow (A3) |
| Dado corporativo já em SQL | copiar perde integridade | lê direto, somente leitura |
| Compliance "dado só na rede interna" | nuvem: a premissa quebra | pode ficar local com gateway (limites de payload; `OUTPUT` de procedure não volta) |
| Licenciamento | premium e capacidade `[externo]` | conector SQL premium `[externo]` |
| Mudança depois de produção | edita no maker | banco congela; só tela e flow; coluna calculada costuma caber |
| Exportação grande | o flow lê a tabela; teto de agregação | procedure com contagem antes de exportar |
| Power BI e Excel direto | lê tudo sem isolamento por linha | lê com a identidade do consumidor; precisa de view e `GRANT` |

## 2. Quando escolher cada uma

**Dataverse** quando: app novo e autocontido; sem tabela corporativa a reaproveitar; volume por
consulta abaixo de 2.000 linhas depois do filtro; precisa de Choice e Lookup nativos; DBA
indisponível no prazo; compliance aceita nuvem **por escrito**; e o isolamento por `Unidade` é
conveniência (ou há orçamento para Owner Team).

**SQL Server + procedures + Power Automate** quando: o dado corporativo já está em SQL; o DBA exige
padrão e é dono do schema; a galeria pode passar de 2.000 linhas; a operação exige transação forte
em várias tabelas; ou compliance exige dado local. Pré-requisitos: PK em toda tabela, `BIT NOT NULL`,
UNIQUE filtrado na chave de identidade, `NVARCHAR` com acento, nível de compatibilidade >= 130,
nomes reais das procedures capturados, gateway confirmado.

Sinais de alerta de trilha errada: contador da tela com "2.000+" que o dono não aceita; regra que
exige "tudo ou nada" em Dataverse; DBA dizendo "congelado" no meio do projeto; tabela corporativa
sendo copiada para Dataverse.

Decida cedo, qualquer que seja a trilha: **identidade do chamador** (o flow resolve quem é; a camada
de dados não autoriza) e **onde vive a regra** (uma cópia só: flow decide, procedure executa — A2).

## 3. Power BI

Para análise e consolidação entre unidades, séries e agregações acima de 2.000 linhas, painéis que
não cabem no app. **Nunca** para escrita ou operação. Condições: view ou dataset com escopo de
unidade, identidade do consumidor; se a fonte é Dataverse com Security Role em escopo Organization,
trate como risco aceito formal.

## 4. SharePoint

Não serve quando: há regra transacional, volume acima do limiar de lista (limites de visualização e
delegação), integridade referencial ou isolamento por linha como controle de acesso. Aceitável para
anexos e documentos ligados a um registro que mora em Dataverse ou SQL. `[externo: limites de lista
em Microsoft Learn — confirmar na versão atual]`

## 5. Fora do Power Platform e nunca

- **Fora:** geração de PDF ou etiqueta sem conversor provado; importação em massa com pré-visualização
  sobre base inteira. Mantenha no sistema atual ou use conector premium; decisão de negócio.
- **Nunca:** `Patch` direto em operação com regra de negócio; exportar a partir de galeria; filtro de
  galeria como único controle de acesso sem risco aceito registrado.

## 6. Como registrar a decisão

Um ADR (`assets/adr-molde.md`) com: trilha escolhida, as respostas dos blocos 4, 7 e 8 de
`brainstorm.md` que sustentam, alternativa descartada e a condição que reabre ("o DBA liberar tabela
nova", "a volumetria passar de N"). Reflita em `power-platform.config.json` e `00-LEIA-PRIMEIRO.md`.

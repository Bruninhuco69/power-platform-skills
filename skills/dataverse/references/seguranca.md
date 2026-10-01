# Segurança no Dataverse: quem lê quais linhas

Security role, business unit, owner team, escopo de linha e segurança de coluna, com o risco do
escopo Organização. Autorização *dentro do flow* é de `power-automate`; a regra de que o escopo na
tela é UX e não controle é `decisoes-padrao.md` A3 — aqui está o que fazer no Dataverse para a
barreira existir de verdade.

## Sumário

1. [O modelo em uma tabela](#1-o-modelo-em-uma-tabela)
2. [Security role e nível de acesso](#2-security-role-e-nível-de-acesso)
3. [O risco do escopo Organização](#3-o-risco-do-escopo-organização)
4. [Isolamento por linha: owner team + business unit](#4-isolamento-por-linha-owner-team--business-unit)
5. [Segurança de coluna](#5-segurança-de-coluna)
6. [Perfil de aplicação × security role](#6-perfil-de-aplicação--security-role)
7. [Como testar fora do app](#7-como-testar-fora-do-app)
8. [Decisão e registro do risco](#8-decisão-e-registro-do-risco)

---

## 1. O modelo em uma tabela

| Peça | O que controla | Granularidade |
|---|---|---|
| **Security role** | Privilégios (criar, ler, gravar, excluir, anexar, anexar a, atribuir, compartilhar) por tabela | Tabela × nível de acesso |
| **Nível de acesso** | De quais linhas o privilégio vale: Usuário, Unidade de negócios, Pai:filhas, Organização | Linha, por **dono** e por **BU** |
| **Business unit (BU)** | Hierarquia de isolamento: o dono da linha pertence a uma BU | Árvore de unidades |
| **Owner team / access team** | Grupo que pode **ser dono** de linha (owner team) ou receber acesso a linhas específicas (access team) | Conjunto de usuários |
| **Segurança de coluna** | Quem lê/escreve uma coluna específica (perfil de segurança de coluna) | Coluna |
| **Filtro na galeria** | Nada de segurança: só o que a tela mostra | — |

Fonte geral:
[Security roles and privileges](https://learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges)
e [Security concepts in Dataverse](https://learn.microsoft.com/en-us/power-platform/admin/wp-security-cds).
O detalhe de comportamento por nível de acesso e herança de BU não foi reconfirmado aqui
`[não verificado]`; a prática dos projetos de referência está registrada no Roteiro de §4.

## 2. Security role e nível de acesso

- A role diz **quais tabelas** e **qual verbo**; o **nível de acesso** diz **quais linhas**. Uma role
  com Leitura em *Organização* lê todas as linhas da tabela, de todas as BUs.
- Quem usa o app precisa de uma role com os privilégios das tabelas que o app toca, **incluindo
  Anexar/Anexar a** nas tabelas relacionadas por Lookup (para gravar Lookup).
- Princípio do menor privilégio: tabelas de domínio (catálogos, perfis) em Leitura; transacionais com
  Criar/Ler/Gravar; **Excluir desligado** quando o negócio não apaga (usa `ativo` ou o estado "encerrado").
  Uma segunda role (administração) com Criar/Gravar nas tabelas de usuário e vínculo, atribuída só a
  quem tem a permissão de aplicação correspondente.
- A role é atribuída ao **usuário ou a um team**; o grupo do Entra que provisiona o acesso é o mesmo
  que o flow de provisionamento manipula: combine o nome do grupo antes de criar a role.
- O **conector** de serviço de um flow roda como a conta da conexão, não como o usuário do app: a
  role dessa conta decide o que o flow consegue ler (`power-automate`).

## 3. O risco do escopo Organização

Security role em escopo **Organização** nas tabelas do app limita **quais tabelas** o usuário acessa,
**não quais linhas**. Efeito: qualquer usuário com acesso ao ambiente e à role consegue ler a tabela
inteira — todas as unidades — por **Excel, Power BI, Web API (OData)** ou qualquer outro
cliente do Dataverse, **independentemente do que a galeria do app mostra**.
`[verificado: projeto de referência]` — risco aceito formalmente por prazo e custo.

Pontos que a equipe costuma subestimar:

- O filtro de unidade na galeria **ajuda a navegar**; quem barra é o servidor. A tela é contornável.
- "Só quem tem o app" não é barreira: a role dá acesso à tabela, não ao app.
- Isso é uma **redução** de segurança em relação a uma arquitetura em que só a aplicação fala com o
  banco (SQL Server com conta de serviço e procedures).
- Power BI e Excel sobre Dataverse leem com a identidade de quem consulta e herdam o mesmo problema.

Se a operação **não** precisa de isolamento real (as unidades já se enxergam; o filtro é conveniência),
o escopo Organização é uma escolha legítima — **desde que registrada como risco aceito** (§8). Se
precisa, vá para §4.

## 4. Isolamento por linha: owner team + business unit

Recomendação para isolamento real por unidade: **Owner Teams + Business Unit**. Roteiro
(`[verificado: projeto de referência]` como plano e custo estimado; **não executado**, por decisão):

1. **Defina a granularidade.** Uma BU/owner team por **região** (poucas) é viável. Uma BU por
   **unidade** (dezenas) custa administração alta e foi descartada no projeto de referência; isolar
   unidade↔unidade dentro da mesma região exige uma BU por unidade.
2. **Crie os Owner Teams** (um por unidade de isolamento) e vincule cada um à sua BU.
3. **Troque o nível de acesso da role** de Organização para **Unidade de negócios** (ou Pai:filhas,
   se a região enxerga as suas unidades).
4. **Atribua o `ownerid` de cada linha** ao team da sua unidade, **no momento da gravação** — pelo
   flow de cadastro, que sabe a unidade da linha. Tabelas que vão sofrer esse isolamento precisam
   nascer como **UserOwned** (ver `references/modelagem.md`): o tipo de propriedade da tabela
   não muda depois de criada `[não verificado: afirmação de um script de criação; conferir no Learn antes
   de depender]`.
5. **Mantenha o filtro de tela**, agora como conveniência, não como controle.
6. **Teste fora do app** (§7).

Custos e riscos:

- Linha sem dono correto fica invisível (ou visível demais): o flow que atribui `ownerid` vira o ponto
  crítico. Linhas legadas importadas precisam receber o dono certo na carga (`references/importacao-dados.md`).
- Usuário que atende mais de uma unidade precisa de mais de um team.
- Tabelas de domínio compartilhadas (catálogo de unidades, perfis) ficam **OrganizationOwned** com
  Leitura em Organização — não são isoladas.

## 5. Segurança de coluna

Para esconder **uma coluna** (dado sensível dentro de tabela que todos leem), use
[segurança em nível de coluna](https://learn.microsoft.com/en-us/power-platform/admin/field-level-security):
marque a coluna como protegida e conceda a um **perfil de segurança de coluna** quem lê/cria/atualiza.

- Protege contra leitura direta pela API, ao contrário de ocultar o campo na tela.
- Não isola **linhas**; combine com owner team/BU quando o requisito é por unidade.
- Coluna protegida aparece como vazia/bloqueada para quem não tem o perfil: fórmula que depende dela
  deve tratar `Blank()`.
- `[não verificado]`: comportamento exato de coluna protegida em fórmula Canvas e em Power BI.

## 6. Perfil de aplicação × security role

São camadas diferentes e não se substituem:

| | Perfil de aplicação | Security role |
|---|---|---|
| Onde mora | Tabela do app (`perfis` + flags `pode_x`) | Dataverse |
| Quem aplica | O app e o **flow** | O servidor |
| Contorna-se pelo cliente? | Sim, se só o app aplica | Não |
| Serve para | Mostrar/ocultar botão; flag por ação no flow | Barrar acesso ao dado |

Permissão por **flag do perfil** (`pode_x`), nunca por nome de perfil (T8); sem perfil resolvido = sem
acesso (fail-closed). A flag decide o que o app oferece e o que o flow aceita; a role decide o que o
dado entrega a quem o consulta por outro caminho. Se só a flag existe, o controle é do app.

## 7. Como testar fora do app

O teste de que o isolamento existe **não pode ser feito pela tela**. Com uma conta de teste que tenha
**só** a role do app e pertença a **outra** unidade:

```
GET https://<org>.crm.dynamics.com/api/data/v9.2/<EntitySet>?$select=<coluna>&$top=50
```

(pelo navegador autenticado como essa conta, ou por Excel/Power BI conectado ao Dataverse com ela).
Resultado esperado: **só** linhas da unidade dessa conta. Devolver linhas de outras unidades =
escopo Organização efetivo. Registre o comando, a conta usada (sem dado pessoal) e a data.

Faça o mesmo para a **escrita** (tentar atualizar linha de outra unidade) e para a **coluna protegida**.

## 8. Decisão e registro do risco

Escolha e escreva no ADR do projeto (`decisoes-padrao.md` A3/A4):

| Situação | Decisão | Registro |
|---|---|---|
| Unidades já se enxergam; filtro é conveniência | Escopo Organização | **Risco aceito** formal: "qualquer usuário com a role lê todas as unidades por Excel/Power BI/Web API", com dono e data |
| Isolamento por região exigido | Owner Teams + BU | Plano de atribuição de `ownerid` no flow de cadastro e na carga |
| Isolamento por unidade exigido | Reavalie a trilha (SQL + procedures com autorização no flow) ou BU por unidade | ADR com custo de administração |
| Coluna sensível | Segurança de coluna | Perfil e lista de quem o recebe |

Nunca: filtro de galeria como único controle sem risco registrado; Power BI sobre Dataverse com
escopo Organização sem tratar o risco.

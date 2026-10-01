# Lições de campo: backend SQL Server

Defeitos e decisões que apareceram em projetos reais e que ainda não cabiam numa regra isolada
das outras referências. Cada lição traz o que aconteceu, em termos genéricos, e a regra ou o arquivo
que a previne. Não é regra por si: o que vale está nos arquivos citados.

## Sumário

1. [A revisão adversarial acha defeito de portão, não de lógica](#1-a-revisão-adversarial-acha-defeito-de-portão-não-de-lógica)
2. [A divergência deliberada some se não ficar escrita onde o próximo lê](#2-a-divergência-deliberada-some-se-não-ficar-escrita-onde-o-próximo-lê)
3. [Pacote de migração escrito para o schema proposto](#3-pacote-de-migração-escrito-para-o-schema-proposto)
4. [Lint novo: classifique os falsos positivos e prove que acusa](#4-lint-novo-classifique-os-falsos-positivos-e-prove-que-acusa)
5. [O custo da decisão declarativa, medido](#5-o-custo-da-decisão-declarativa-medido)

---

## 1. A revisão adversarial acha defeito de portão, não de lógica

| | |
|---|---|
| **O que aconteceu** | Revisores instruídos a **quebrar** os corpos das procedures declarativas acharam defeitos que nenhum teste funcional pegava, porque a procedure *funciona*. Nenhum exigiu voltar a `IF` ou `TRY/CATCH`: todos fecharam com um predicado a mais, uma coluna a mais no `OUTPUT` ou um DDL. |
| **Os padrões** | (a) Duas escritas encadeadas que apontavam para linhas diferentes do mesmo vínculo: o `OUTPUT` devolve o vínculo **gravado** e o statement seguinte casa por ele. (b) `NULL` num parâmetro corrompe a coluna **e** silencia a trilha que a registraria: `IS NOT NULL` no portão (falha fechada, nada é gravado). (c) Uma operação "irreversível" revertida por outra: o estado terminal entra no predicado (`<> N'encerrado'`). (d) Escrever em registro filho de um alvo inexistente devolvia sucesso sem gravar: `EXISTS` do alvo no portão, ou `FOREIGN KEY` (conferindo antes os órfãos da carga). (e) Guarda de duplicidade cega a `NULL` e a `''`: o predicado trata os dois explicitamente (decisão de produto embutida). (f) Duas edições que trocam valores entre linhas geraram deadlock (1205): o flow o trata como transitório. (g) Uma probe que se autoexclui por parâmetro cru: fechar exigia uma ordem de lock nova, com risco de deadlock; ficou como obrigação do flow. |
| **Previne** | `padrao-procedure.md` §6 (predicado faz o papel do `IF`), §8 (guarda e lock), §10 (parâmetros), §12 (retry e idempotência); `contrato-proc-flow.md` §3 (obrigações do flow). Antes de entregar, rode a revisão adversarial por terços do pacote. |

## 2. A divergência deliberada some se não ficar escrita onde o próximo lê

| | |
|---|---|
| **O que aconteceu** | A propriedade "o corpo da procedure é idêntico ao da fonte, byte a byte" deixou de valer para alguns corpos depois dos patches da revisão. A divergência ficou registrada só na carta ao DBA. Quando um registro assim some de lá, a próxima pessoa "conserta de volta" e reabre o defeito. Um teste também mudou de resultado (de sucesso para `NAO_APLICADO`): era a correção, não regressão, e entrou como mudança de comportamento declarada. |
| **Previne** | `deploy-e-dba.md` §1 e §7 e `assets/contrato-procedure-molde.md` §4/§8: a divergência vai no contrato da procedure, não só na carta; mudança de comportamento por correção é declarada como tal. |

## 3. Pacote de migração escrito para o schema proposto

| | |
|---|---|
| **O que aconteceu** | O pacote de carga foi escrito para o schema **proposto** (nomes em `snake_case`, schema próprio), e o DBA construiu outro (`dbo`, prefixos corporativos). A ponte entre os dois, como o arquivo de carga final foi gerado, não estava documentada. Os problemas que só apareceram contra o schema real: acento (`Disponivel` × `Disponível`), vocabulário de status diferente, dois campos de texto **invertidos**, identidade vazia, seed de perfis redigitado à mão com células erradas. |
| **Previne** | `migracao-dados.md` §1 (mapear contra o ambiente real) e §6 (collation e acento). A camada de nomes e vocabulários é parte versionada do pacote, e a reconciliação roda contra o schema real, não contra o proposto. |

## 4. Lint novo: classifique os falsos positivos e prove que acusa

| | |
|---|---|
| **O que aconteceu** | O lint rodado só-leitura sobre a pasta de procedures de um projeto (`.md` com blocos `sql` e `.sql` de deploy) deu, na primeira passada, **zero erro e alguns avisos, todos falsos positivos**: fragmentos de documentação que mostram só a assinatura (`CREATE ... AS` sem corpo) e nomes com placeholder (`usp_<SIGLA>_<Entidade>_<Acao>`). O lint passou a tratar os dois como documentação. Contra scripts de migração, o `P009` (SQL dinâmico) é falso positivo documentado: nomes de metadado interno via `QUOTENAME`, dispensável com `-- lint-ok P009` e uma frase de justificativa. O `P005` achou um erro real: uma procedure auxiliar de staging com prefixo `sp_`, reservado do produto. |
| **Previne** | `SKILL.md` (seção Scripts: `-- lint-ok` com justificativa) e a regra P4 de `decisoes-padrao.md`: para provar que o validador acusa, faça uma mutação (remova `SET XACT_ABORT ON` de uma procedure) e confira que o `P002` aparece. |

## 5. O custo da decisão declarativa, medido

| | |
|---|---|
| **O que aconteceu** | Ao reescrever as procedures de forma declarativa (sem `IF`, `WHILE`, `TRY/CATCH`, cursor, `CASE` de regra nem `SCOPE_IDENTITY()`), o código encolheu a uma fração e as compensações do `Catch` do flow (`DELETE` de desfazimento) deixaram de existir: `XACT_ABORT ON` desfaz sozinho. Em compensação, a procedure deixou de ser o último ponto de controle, a trilha deixou de provar **quem**, erros de infraestrutura passaram a vir como falha da ação do conector, e frases distintas viraram `NAO_APLICADO`. Uma só regra de domínio ficou no banco, como predicado de uma cláusula `AND`, com a ressalva de que é spoofável. A primeira proposta de reduzir o vocabulário de códigos a poucos valores não foi a implementada: manteve-se um código por desfecho que o usuário precisa distinguir. |
| **Previne** | `padrao-procedure.md` §4 (vocabulário), §5 (declarativa × clássica, o custo sem suavizar) e `seguranca-e-permissoes.md` §5 (o limite do chamador por parâmetro). |

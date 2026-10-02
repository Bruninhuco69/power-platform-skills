# Importação de dados no Dataverse

CSV, Excel e dataflow; ordem de carga com Lookup; conferência; e como não cair na divergência entre
o script e o ambiente. Origem dos fatos: o plano de dados e o pacote de CSV de um projeto de referência, e a forma como o
ambiente real acabou criado.

## Sumário

1. [A regra que decide tudo](#1-a-regra-que-decide-tudo)
2. [Escolha do caminho](#2-escolha-do-caminho)
3. [Ordem obrigatória](#3-ordem-obrigatória)
4. [Formato dos arquivos](#4-formato-dos-arquivos)
5. [Lookup e Choice na importação](#5-lookup-e-choice-na-importação)
6. [Preparar o legado antes de gerar o CSV](#6-preparar-o-legado-antes-de-gerar-o-csv)
7. [Conferência da carga](#7-conferência-da-carga)
8. [Como não cair na divergência script × ambiente](#8-como-não-cair-na-divergência-script--ambiente)

---

## 1. A regra que decide tudo

**O assistente "Importar dados" do maker cria colunas de TEXTO, e o Dataverse não converte texto em
Choice nem em Lookup depois.** Importar primeiro e ajustar depois é refazer as tabelas.
`[verificado: projeto de referência]` — também foi a origem da divergência do ambiente real: tabelas criadas
por importação de Excel têm colunas de texto onde o plano previa Choice e Lookup.

Para evitar: **crie Choices, tabelas, colunas, Lookups e alternate keys primeiro**; importe dados
**para** essa estrutura, mapeando cada coluna do arquivo para a coluna existente. Importar para
tabela nova gerada pelo assistente só vale quando todas as colunas **devem** ser texto.

Exceção: a **carga mockup** do `/pp:arquitetura` (`skills/power-platform/references/carga-mockup.md`) é feita para isso.
- Ela cria a estrutura **com dado fictício**, deixa a dedução de tipo errar ali e passa pela
  conferência (`montar-carga-mockup.py --conferir`) antes de qualquer dado real.
- Recriar uma coluna que só tem linha mockup é de graça.
- Ou, sem dedução: o construtor (`skills/power-platform/references/construtor-dataverse.md`) cria
  as tabelas, as colunas com o tipo do spec, os Lookups e as linhas mockup pela Web API.
- O dado real continua entrando por esta referência, para tabela que já existe.

## 2. Escolha do caminho

| Caminho | Quando | Atenção |
|---|---|---|
| **Importar de CSV/Excel** (maker, *Importar dados*) | Carga única ou rara, arquivo limpo, estrutura já criada | Mapeia para colunas existentes; resolve Choice pelo rótulo e Lookup pela coluna de nome principal ou chave alternativa |
| **Dataflow** (Power Query) | Carga recorrente, transformação (limpeza, junção, tipos), fonte externa | Mapeia e transforma; permite chave para atualizar linhas existentes `[não verificado]` — leia o Learn de dataflows antes de contar com upsert |
| **Flow** (`Add a new row`, `$batch`) | Carga programática, volume pequeno/médio, regra de negócio na entrada | Respeita as regras do flow; volume grande pede lote (`power-automate`) |
| **Conector/ferramenta de dados** | Migração grande, entre sistemas | Fora do escopo desta skill |

Fontes: [Import data](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/import-data) e
[Dataflows](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-and-use-dataflows).
Este documento descreve a prática dos projetos de referência (CSV); detalhes de dataflow
`[não verificado]` neste repositório.

## 3. Ordem obrigatória

```
1. Criar as Choices (globais, se compartilhadas)
2. Criar as tabelas e as colunas (Lookup incluído) — à mão, pela carga mockup ou pelo construtor, conferida com --conferir
3. Criar as alternate keys  →  esperar EntityKeyIndexStatus = Active
4. Extrair o as-built e conferir contra o plano            (references/nomes-as-built.md)
5. Importar, em ordem de dependência: catálogos → perfis/usuários → vínculos → transacionais → trilha
```

A ordem do passo 5 é a das **dependências de Lookup**: uma linha só pode apontar para algo que já
existe. Em dependência circular, importe sem o Lookup e preencha depois.

Passo 3 não é detalhe: chave `Pending` **não resolve Lookup na importação e o erro é silencioso**
(linha entra sem o vínculo, sem mensagem) `[verificado: projeto de referência]`.

## 4. Formato dos arquivos

`[verificado: projeto de referência]` salvo onde marcado:

| Item | Regra |
|---|---|
| Encoding | UTF-8 **com BOM** (o assistente do maker lê acento sem quebrar) |
| Separador | `,` — o import não aceita `;` de forma confiável. O CSV de **saída** para Excel pt-BR usa `;`: são arquivos de propósitos diferentes |
| Data | ISO: `AAAA-MM-DD` (data) e `AAAA-MM-DDTHH:MM:SSZ` (data e hora). A importação da planilha já trocou dia e mês: confira uma data depois de importar (`licoes-de-campo.md` §8) |
| Yes/No | Rótulo do ambiente (`Sim`/`Não` em pt-BR) |
| Choice | **Rótulo** da opção (não o valor inteiro) |
| Lookup | Valor da coluna de nome principal do alvo, ou da chave alternativa escolhida na etapa de mapeamento |
| Colunas de sistema | Nenhuma (`createdon`, `ownerid`, `statecode`, etc.) |
| Texto com zero à esquerda | Trate como texto na origem; Excel remove zeros. Padronize antes (ex.: código com zeros à esquerda) |
| Primeira linha | Cabeçalho com os **nomes de exibição** das colunas de destino, tal como no as-built |

Gere o cabeçalho **a partir do as-built**, não do dicionário (§8).

## 5. Lookup e Choice na importação

- **Choice**: o assistente resolve pelo **rótulo**. Rótulo com acento ou espaço diferente da opção
  do ambiente não casa; confira contra as opções do as-built.
- **Lookup**: resolve pela coluna de **nome principal** do alvo. Se o nome principal **não é único**
  (regra de negócio permite duplicidade), a resolução erra em silêncio ou falha na primeira duplicata.
  Use **alternate key** e escolha-a na etapa de mapeamento.
- Quando o alvo só tem chave de negócio **numérica** do sistema legado, inclua no arquivo da tabela
  filha uma **coluna auxiliar** com essa chave (ex.: `<alvo>_id_legado`) e use-a como correspondência.
  `[verificado: projeto de referência]` — foi assim que registros filhos e trilha apontaram para o pai.
- **Texto no lugar de Lookup** (as-built com texto): nada resolve; o valor entra como veio. Valide
  antes contra a tabela de origem (§6).

## 6. Preparar o legado antes de gerar o CSV

Rode a conferência de consistência **antes** de gerar os arquivos, não na véspera do go-live. Exemplos
de consulta (adapte a fonte; aqui em SQL ilustrativo, destino: o cliente SQL da origem):

```sql
-- linhas que violam uma regra de negócio e vão barrar na carga
SELECT COUNT(*) FROM <tabela>
 WHERE (<tipo> = 'A' AND <campo_b> <> 'X') OR (<tipo> <> 'A' AND <campo_b> = 'X');

-- valores de unidade inexistentes (o defeito que a falta de Lookup deixa entrar)
SELECT <unidade> FROM <tabela_usuarios>
 WHERE <unidade> NOT IN (SELECT <codigo> FROM <tabela_unidades>);

-- datas fora do formato ISO
SELECT <id>, <data> FROM <tabela> WHERE <data> NOT LIKE '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]';
```

Transformações típicas (`[verificado: projeto de referência]`):

| Campo | Transformação | Motivo |
|---|---|---|
| Data em texto | Converter para ISO e **validar o formato antes** | A coluna nunca teve restrição de formato; pode haver `05/01/2026` |
| Identificador numérico com zeros | Preencher com zero à esquerda | Excel remove |
| Código de referência | Caixa alta | Regra de negócio de normalização |
| Campos derivados na origem (região, etc.) | Descartar | Derivam da unidade; não duplique |
| Hash de senha | Descartar | A identidade é do Entra |

Meça o que o Dataverse vai exigir (§modelagem 9): campo obrigatório que o legado não preenche derruba
a carga inteira.

## 7. Conferência da carga

- **Contagem**: compare a quantidade de linhas do arquivo com a da tabela. Use
  `CountIf(<Tabela>; true)` (exato até 50.000), **não** `CountRows(<Tabela>)` sem filtro, que é
  aproximado (cache) — `references/delegacao-dataverse.md` §3. Acima de 50.000, conte por flow ou pela
  Web API: `$count=true` satura em **5.000** (padrão); `RetrieveTotalRecordCount` devolve um
  retrato das últimas 24 h, não o número exato do momento.
- **Vínculos**: linhas filhas sem o Lookup preenchido = chave alternativa não ativa ou correspondência errada.
  Conte: `Filter(<Filha>; IsBlank(<lookup>))` (o resultado deve ser 0 ou o número esperado).
- **Choices**: nenhuma coluna Choice ficou em branco por rótulo que não casou.
- **Amostra**: confira linhas de borda (acento, zero à esquerda, data limite).
- Guarde o comando e o resultado com a data (P5).

## 8. Como não cair na divergência script × ambiente

A causa raiz do retrabalho nos projetos de referência foi escrever contra o que *deveria* existir.

1. **Um dono da criação** (`references/modelagem.md` §1). Se o ambiente foi criado à mão, o script de
   criação **é descartado ou reconstruído a partir do as-built**, não reaproveitado.
2. **Extraia o as-built depois de criar** e antes de gerar qualquer CSV, tela ou flow.
3. **Gere o CSV e o mapeamento a partir do as-built**, nunca do dicionário. O cabeçalho do arquivo é o
   nome de exibição que o as-built diz.
4. **Reextraia depois de qualquer mudança** e compare (diff) com o as-built versionado.
5. **Registre divergência como decisão** (manter, realinhar, atualizar o dicionário;
   `references/nomes-as-built.md` §6).
6. **Reimportar não repara tipo errado**: se uma coluna nasceu texto e devia ser Choice, o caminho é
   recriar a coluna e recarregar, não "importar de novo por cima".
7. **Gerador de CSV é exemplo, não padrão.** O de um projeto de referência gerava os arquivos a partir do banco de origem e
   do dicionário; serve de modelo de *como validar antes de gerar*, mas o contrato é o as-built.

# `power-platform.config.json` — configuração por projeto

Os scripts das skills são genéricos. O que muda de um projeto para outro fica neste arquivo,
na raiz do projeto. Os scripts o procuram do diretório atual para cima, ou recebem
`--config <arquivo>`. Chave desconhecida é ignorada; chave ausente usa o default.

```json
{
  "projeto": "NOME",
  "trilha_dados": "sql-server",
  "prefixo_publisher": "abc_",
  "pastas": {
    "telas": ["Frontend"],
    "flows": ["Backend/PowerAutomate/nos"],
    "procedures": ["Backend/SQL Server/procedures"],
    "prototipo": ["docs/planejamento/prototipo"]
  },
  "nomes_as_built": "AMBIENTE-AS-BUILT/NOMES-AS-BUILT.md",
  "telas_formato": "yaml-puro",
  "padrao_nome_procedure": "^usp_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+$",
  "colunas_retorno_procedure": ["status", "description", "id", "url"],
  "ignorar": ["**/old/**", "**/backup-*/**", "**/_antes/**"],
  "mockups": {
    "modelo": "gpt-image-2",
    "tamanho": "1536x1024",
    "qualidade": "high",
    "pasta": "docs/planejamento/mockups"
  },
  "modelos": {
    "perfil": "equilibrado",
    "sessao": "opus",
    "agentes": { "agente-arquitetura": "opus", "agente-qa": "opus", "agente-canvas": "sonnet", "agente-pesquisa": "sonnet", "...": "..." }
  },
  "git_commit_por_etapa": true
}
```

| Chave | Tipo | Default | Usado por |
|---|---|---|---|
| `projeto` | texto | nome da pasta | todos (cabeçalho da saída) |
| `trilha_dados` | `sql-server` \| `dataverse` | — | `validar-telas.py` (liga as regras do conector: T013/T014); lido também pelo orquestrador |
| `prefixo_publisher` | texto | `""` | regras de nome de coluna Dataverse |
| `pastas.telas` | lista | `["."]` | `validar-telas.py` |
| `pastas.flows` | lista | `["."]` | `verificar-fluxo.py` |
| `pastas.procedures` | lista | `["."]` | `lint-procedure.py` |
| `pastas.prototipo` | lista ou caminho | `docs/planejamento/prototipo` | `verificar-prototipo.py` |
| `nomes_as_built` | caminho | — | lido por pessoas e agentes antes de escrever fórmula/flow; **nenhum script o consome ainda** |
| `telas_formato` | `yaml-puro` \| `markdown-cercado` \| `auto` | `auto` | `validar-telas.py` |
| `padrao_nome_procedure` | regex | `^(usp\|SP)_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+$` | `lint-procedure.py` (P005). Copie o padrão **real** do banco, não o do documento |
| `colunas_retorno_procedure` | lista ou texto `a,b,c` | `status, description, id, url` | `lint-procedure.py` (P004) |
| `ignorar` | lista de globs | `[]` | todos |
| `mockups.modelo` | texto | `gpt-image-2` | `desenhar-mockups.py`. Abaixo de `--modelo` e da variável `OPENAI_IMAGE_MODEL` |
| `mockups.tamanho` | `LARGURAxALTURA` \| `auto` | `1536x1024` | `desenhar-mockups.py` (abaixo de `--tamanho`) |
| `mockups.qualidade` | `low` \| `medium` \| `high` \| `auto` | `high` | `desenhar-mockups.py` (abaixo de `--qualidade`) |
| `mockups.pasta` | caminho | a pasta do spec | `desenhar-mockups.py`: onde gravar os `.png` e a galeria; `verificar-prototipo.py`: onde procurar os PNGs |
| `modelos.perfil` | texto | — | `modelos.py`: o perfil escolhido no `/pp:novo` (`equilibrado`, `maximo`, `economico`, `herdar`; `(ajustado)` se houve troca avulsa) |
| `modelos.sessao` | `best` \| `fable` \| `opus` \| `sonnet` \| `haiku` \| vazio | vazio | `modelos.py` grava em `.claude/settings.local.json`; `estado.py` lembra o `/model` no "Próximo passo" |
| `modelos.agentes.<agente>` | `fable` \| `opus` \| `sonnet` \| `haiku` \| vazio | vazio (herda a sessão) | etapas `/pp:*`: `modelos.py de <agente>` vira o `model` da chamada do agente |
| `git_commit_por_etapa` | booleano | `false` | etapas `/pp:*`: commit no fim de cada etapa (perguntado no `/pp:novo`) |

No pipeline `/pp:*`, o `/pp:novo` cria este arquivo **sem** `trilha_dados` e `prefixo_publisher`: quem
os grava é o `pp:agente-arquitetura`, depois que o usuário escolhe a trilha no `/pp:arquitetura`.

Regra: o projeto declara **uma** `trilha_dados`. Duas trilhas vivas ao mesmo tempo foi a
causa de retrabalho que este campo existe para impedir.

A chave da OpenAI **não** entra neste arquivo: `OPENAI_API_KEY` só no ambiente
(`skills/power-platform/references/mockups.md` §2).

## `ESTADO.md` — o estado do pipeline

Outro arquivo da raiz, separado do config: onde o projeto está no pipeline `/pp:*` (etapas feitas,
em andamento, reabertas) e o próximo comando. Quem escreve é só o
`skills/power-platform/scripts/estado.py`, chamado pelas etapas; o JSON no fim do arquivo é a
fonte, a tabela é reescrita a cada mudança. Editar à mão a tabela não muda nada; editar o JSON pode
corromper o arquivo (o script acusa com exit 2).

Os modelos (quem pensa e quem executa, como trocar e medir): `skills/power-platform/references/modelos.md`.

# CONTRATOS -- <app>

> Contrato tela <-> flow <-> procedure. Quando divergir do flow, **o contrato é o bug**.
> Gere este documento a partir do artefato sempre que possível; à mão, ele envelhece no dia em
> que foi escrito. Cada afirmação numérica traz o comando que a mede.
> Molde da skill `power-automate`: copie, preencha, apague as instruções em itálico.

## 1. Invariantes (valem para todos os flows)

| # | Regra | Verificação |
|--:|---|---|
| 1 | Resposta com 4 campos: `status`, `description`, `id`, `url`, todos texto, sempre presentes | `python <pasta-da-skill>/scripts/verificar-fluxo.py <pasta>` (F010) |
| 2 | `status` ∈ `success` \| `warning` \| `error`; `warning` = gravou com ressalva | revisão |
| 3 | Parâmetros do trigger são **posicionais e texto**; parâmetro novo entra no fim; parâmetro morto vira `naoUsado<N>` e mantém a posição | contagem de argumentos do `.Run()` == parâmetros do trigger |
| 4 | O flow revalida permissão e escopo em toda chamada; identidade vem do contexto, não de parâmetro | revisão + fixture de negação |
| 5 | Código da procedure é vocabulário fechado; o flow traduz | tabela do §2.6 |

## 2. `<flow>` -- <N> nós

### 2.1 Chamada

*Cole a chamada como o app a faz. Destino: barra de fórmulas pt-BR (`;` e `;;`), p. ex. `OnSelect`
do botão; a chamada fica dentro de `IfError` (C3).*

```text
IfError(Set(varRet; '<flow>'.Run("<acao>"; <p1>; <p2>)); Set(varRet; Blank()))
```

| # | Parâmetro | Token no flow | Tipo/formato | Quem valida |
|--:|---|---|---|---|
| 1 | `acao` | `triggerBody()['text']` | texto, vocabulário: `<acao1>`, `<acao2>` | `Switch_acao` (default responde `error` nomeando o valor) |
| 2 | `<nome>` | `triggerBody()['text_1']` | texto; id numérico via `Text(id; "[$-en-US]0")` | `Validar_<acao>` |

### 2.2 Autorização

| Ação | Flag lida em `Ler_chamador` | Escopo de unidade | Flag de `CONFIG` | Evidência |
|---|---|---|---|---|
| `<acao>` | `<Flg_Acao>` | compara `<unidade do registro real / do parâmetro>` | `<cfgEscopoUnidade>` (nasce `true`) | nome da ação `Autorizar_<acao>` |

### 2.3 Procedures chamadas

| Nó | Procedure (AS-BUILT) | Parâmetros (na ordem da assinatura) | Classe |
|---|---|---|---|
| `Gravar_<acao>` | `[dbo].[<procedure>]` | `<Id_Registro>`, `<Des_X>`, `<Id_UsuarioChamador>` | chave / coluna / chamador |

### 2.4 Regras que o flow reprova, na ordem de avaliação

| # | Nó | Condição | Mensagem |
|--:|---|---|---|
| 1 | `Validar_<acao>` | `<descrição vazia>` | `<frase pt-BR>` |

### 2.5 Toda resposta que este flow pode dar

| Ramo | Nó | `status` | `description` | `id` |
|---|---|---|---|---|
| Chamador desconhecido | `Nega_chamador` | `error` | Seu perfil não permite esta ação. | vazio |
| Sem permissão | `Nega_perm_<x>` | `error` | Seu perfil não permite esta ação. | vazio |
| Ação desconhecida | `Nega_acao` | `error` | Ação desconhecida. | vazio |
| Falha de conector | `Nega_conector` | `error` | O sistema não respondeu. Nenhuma alteração foi feita. | vazio |
| Sucesso | `Responder_<x>` | `success` | `<frase>` | `<id>` |

### 2.6 Códigos da procedure (vocabulário FECHADO)

| Procedure | `status` | Código | Frase no flow | Significado |
|---|---|---|---|---|
| `<procedure>` | `success` | `GRAVADO` | Registro gravado. | gravou |
| `<procedure>` | `warning` | `NAO_APLICADO` | Nada foi alterado. | predicado de estado não casou |

*Código novo na procedure sem linha aqui responde `error` nomeando o código.*

### 2.7 Testes que fecham o contrato

| Caso | Setup | Verificação | Rótulo |
|---|---|---|---|
| Perfil sem a flag da ação | usuário de teste sem `<Flg_Acao>` | resposta `error`, nenhuma linha gravada | FLOW |
| Parâmetro vazio | `descricao = ""` | mensagem de `Validar_<acao>` | FLOW |
| Usuário de outra unidade | `cfgEscopoUnidade = true` | `error` | FLOW |
| Falha de conector | desligar a connection reference | `Nega_conector`, sem execução sem `Response` | FLOW |

Rótulos: `ESTÁTICO` (lido do artefato), `SQL` (executado no banco), `FLOW` (executado no flow).

## 3. Portões

```text
python <pasta-da-skill>/scripts/verificar-fluxo.py <pasta dos flows>      # 0 erro(s)
```

## 4. Apêndice: nomes AS-BUILT

Tabela única, **autoridade sobre o gerador e sobre o documento**: procedure, connection
reference (nome lógico por ambiente), tabela e coluna. Origem: `sys.procedures` e a lista de
connection references do ambiente, com a data da captura.

| Objeto | Nome no ambiente | Capturado em |
|---|---|---|
| Procedure de gravação | `<procedure>` | `<AAAA-MM-DD>` |
| Connection reference SQL | `<prefixo>_sharedsql` | `<AAAA-MM-DD>` |

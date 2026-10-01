# Mockups em imagem (`/pp:mockups`) — API de imagens da OpenAI

Depois do design system, o `pp:agente-mockups` elenca as páginas e a moldura do app e escreve
um spec. O script `scripts/desenhar-mockups.py` transforma esse spec em uma imagem por tela, com a
paleta do projeto, para o dono do processo aprovar **antes** de qualquer YAML.

## Sumário

1. [O que o mockup é e o que não é](#1-o-que-o-mockup-é-e-o-que-não-é)
2. [Pré-requisitos: chave, aprovação, Python](#2-pré-requisitos-chave-aprovação-python)
3. [Modelo, tamanho e qualidade são variáveis](#3-modelo-tamanho-e-qualidade-são-variáveis)
4. [O spec `mockups.json`](#4-o-spec-mockupsjson)
5. [Passo a passo](#5-passo-a-passo)
6. [Erros comuns](#6-erros-comuns)
7. [Fontes](#7-fontes)

---

## 1. O que o mockup é e o que não é

- **É** uma referência visual para validar com quem vai usar o app:
  - quais telas existem;
  - o que cada uma mostra;
  - onde fica cada ação;
  - como aparecem pop-ups e notificações;
  - se a paleta funciona.
- **Não é** fonte. A tela real sai do catálogo de componentes e dos tokens `fx*` (skill
  `powerapps-canvas`). Ninguém mede pixel do mockup nem copia cor da imagem: cor vem do design system.
- O modelo de imagem ainda erra posição e nitidez de texto (a própria OpenAI avisa). Rótulo torto
  não é defeito do design: julgue estrutura, hierarquia e fluxo.

## 2. Pré-requisitos: chave, aprovação, Python

| Item | Detalhe |
|---|---|
| Chave `OPENAI_API_KEY` | conta da OpenAI com crédito. Alguns modelos GPT Image exigem a *Organization Verification* da organização (sem ela, HTTP 403) |
| Aprovação de segurança | o texto do spec (descrições, paleta, nomes de perfil) sai para a OpenAI. Pergunta 7.9 do `brainstorm.md`. Sem aprovação, a fase segue sem mockup e isso fica registrado |
| Python 3.10+ | o script usa só a biblioteca padrão |

**Defina a chave fora do chat**, no terminal de onde o Claude Code vai ser aberto:

```powershell
# PowerShell — só esta sessão
$env:OPENAI_API_KEY = "<sua-chave>"
# PowerShell — permanente (abra um terminal novo depois)
setx OPENAI_API_KEY "<sua-chave>"
```

```bash
# bash/zsh — ponha no ~/.bashrc ou ~/.zshrc para ficar permanente
export OPENAI_API_KEY="<sua-chave>"
```

Depois reabra o Claude Code a partir desse terminal. A chave **nunca** vai:

- para o `power-platform.config.json`;
- para um `.env` versionado;
- para o histórico do git;
- para a conversa.

Para conferir se ela está definida, sem mostrá-la:

```bash
python -c "import os; print('OPENAI_API_KEY definida' if os.environ.get('OPENAI_API_KEY') else 'OPENAI_API_KEY ausente')"
```

## 3. Modelo, tamanho e qualidade são variáveis

| Parâmetro | 1º `--opção` | 2º ambiente | 3º `power-platform.config.json` | Default |
|---|---|---|---|---|
| modelo | `--modelo` | `OPENAI_IMAGE_MODEL` | `mockups.modelo` | `gpt-image-2` |
| tamanho | `--tamanho` | — | `mockups.tamanho` | `1536x1024` |
| qualidade | `--qualidade` | — | `mockups.qualidade` | `high` |
| pasta das imagens | `--saida` | — | `mockups.pasta` | a pasta do spec |
| endpoint | — | `OPENAI_BASE_URL` | — | `https://api.openai.com/v1` |

`OPENAI_BASE_URL` serve para proxy corporativo compatível com a API da OpenAI.
- Precisa ser `https`. `http` só vale para `localhost`, porque a chave vai no cabeçalho.
- Redirecionamento não é seguido: ele levaria a chave para outro host.
- O Azure OpenAI usa outra URL e outro cabeçalho de autenticação, e este script não o suporta.

**Modelos** (documentação da OpenAI, consultada em 2026-10):

| Modelo | Situação |
|---|---|
| `gpt-image-2` | atual (snapshot `gpt-image-2-2026-04-21`); é o default do kit |
| `gpt-image-2.5-sunburst` | mais recente, o mais capaz para gerar e editar |
| `gpt-image-2.5-flare` | mais recente, rápido |
| `gpt-image-1` | desligado em 2026-10-23 |
| `gpt-image-1.5`, `gpt-image-1-mini` | desligados em 2026-12-01 |

Trocar de modelo é só mudar a variável. Confira na página de modelos da OpenAI antes de fixar um
nome no config.

**Tamanho:**
- Os seguros, aceitos por todos os modelos GPT Image, são `1024x1024`, `1536x1024` e `1024x1536`.
- O default `1536x1024` é paisagem, o mais perto do canvas 16:9.
- Os modelos 2.5 aceitam `LARGURAxALTURA` personalizado, por exemplo `1920x1088`, com estas regras:
  - largura e altura múltiplos de 16;
  - proporção até 3:1;
  - aresta até 3840.
- O script valida essas regras e dá `AVISO M005` em tamanho personalizado, porque nem todo modelo o
  aceita.

**Qualidade:**
- Valores: `low`, `medium`, `high` e `auto`. `xhigh` e `max` existem só nos modelos 2.5.
- Texto legível na tela pede `high`; `low` serve para um primeiro rascunho barato.
- O custo por imagem depende do modelo, do tamanho e da qualidade. Confira na página de preços da
  OpenAI, não estime de cabeça.

## 4. O spec `mockups.json`

Molde: `assets/mockups-molde.json` (entidade `Pedido`, unidades `AAA`/`BBB`). Lugar no projeto:
`docs/planejamento/mockups/mockups.json`.

| Campo | Obrigatório | Conteúdo |
|---|---|---|
| `app` | sim | nome do app |
| `idioma` | não (`pt-BR`) | idioma de todo texto visível na imagem |
| `canvas` | não (`1920x1080`) | resolução do canvas (T1); vai no prompt como referência |
| `design_system.paleta` | sim | `nome (token)` → `#RRGGBB`, copiado da seção 3 do `ux-design-system.md` |
| `design_system.fonte`, `raio`, `estilo` | não | fonte, raio dos cantos em px, estilo em uma frase |
| `moldura.header` | sim | o header, igual em todas as telas |
| `moldura.navegacao`, `notificacoes`, `popups`, `carregando`, `estados`, `rodape` | não | o resto da moldura |
| `telas[].id` | sim | `tl-NN-...`, minúsculas, dígitos e hífen; vira o nome do `.png` |
| `telas[].nome`, `descricao` | sim | nome da tela e o que aparece nela |
| `telas[].inventario`, `objetivo`, `perfil`, `componentes`, `estado` | não | ligação com o inventário, perfil logado, componentes do catálogo, estado mostrado (modal aberto, toast, vazio...) |

O script recusa (ERRO) o seguinte:
- cor fora de `#RRGGBB`;
- id repetido;
- campo obrigatório ausente;
- **e-mail que não seja de domínio fictício** (`@contoso.com`, `@example.com`), porque o texto vai
  para um serviço externo.

## 5. Passo a passo

1. **O agente faz o spec.** O `/pp:mockups` chama o `pp:agente-mockups` com a raiz do projeto e a
   pasta do plugin. O agente escreve o `inventario-telas.md` e o `mockups.json`; ele **não tem
   Bash**, então quem confere o spec é a etapa:
   `python <skills>/power-platform/scripts/desenhar-mockups.py docs/planejamento/mockups/mockups.json --simular`
   O `--simular` valida, mostra cada prompt e conta as imagens, sem chave e sem rede.
2. **O usuário aceita.** O orquestrador mostra ao usuário:
   - quantas imagens serão geradas;
   - o modelo, o tamanho e a qualidade;
   - que o texto dos prompts vai para a OpenAI.
   Sem o "pode gerar" do usuário, não chame a API.
3. **Confira a chave** com o comando da seção 2. Se estiver ausente, a tarefa fica 🔴: diga ao
   usuário como definir a chave (seção 2) e espere. Não peça a chave na conversa.
4. **Gere:** `python <skills>/power-platform/scripts/desenhar-mockups.py docs/planejamento/mockups/mockups.json`.
   - Imagem que já existe é pulada.
   - O teto padrão é de 20 imagens novas por execução (`--max-imagens`).
   - Sai um `.png` por tela e a galeria `mockups.md`, marcada "gerado — não editar".
   - Cada imagem é gravada num `.tmp` e só depois renomeada: uma interrupção não deixa PNG truncado.
   - `429` e `5xx` tentam de novo duas vezes, respeitando `Retry-After`.
   - Um erro que se repetiria em todas as telas interrompe a execução: `3xx`, `400`, `401`, `403`,
     `404`, rede ou gravação. A galeria sai mesmo assim, com o que já existe.
   - Prompt recusado pela moderação (`moderation_blocked`) só pula aquela tela.
5. **Aprove com o dono do processo** a partir da galeria. Registre o aceite (frase e data) no
   inventário de telas.
6. **Ajuste pelo spec, nunca pela imagem.**
   - Mudou a moldura ou a paleta: regere tudo com `--sobrescrever`.
   - Mudou uma tela: `--telas tl-02-novo-pedido --sobrescrever`.

## 6. Erros comuns

| Saída | Causa | O que fazer |
|---|---|---|
| exit 2 "defina OPENAI_API_KEY" | chave ausente no ambiente do Claude Code | seção 2; reabra o Claude Code pelo terminal que tem a variável |
| `M101 HTTP 401` | chave errada ou revogada | gere outra no painel da OpenAI e defina de novo |
| `M101 HTTP 403` | organização sem *Organization Verification* para GPT Image | faça a verificação no painel; ou troque de modelo |
| `M101 HTTP 404` ou `400` citando o modelo | nome de modelo inexistente para a conta | confira `OPENAI_IMAGE_MODEL`, `--modelo` e `mockups.modelo` |
| `M101 HTTP 400` citando `size` ou `quality` | tamanho ou qualidade que o modelo não aceita | volte para `1536x1024` e `high` |
| `M101 HTTP 429` | limite de taxa ou crédito | espere, ou confira o faturamento |
| `M101 sem conexão` | rede ou proxy | `OPENAI_BASE_URL` para o proxy, ou rode de outra rede |
| `M101 HTTP 3xx` | o endpoint redirecionou (a chave não segue para outro host) | aponte `OPENAI_BASE_URL` para o endereço final |
| exit 2 "precisa ser https" | `OPENAI_BASE_URL` em `http` fora do `localhost` | use `https` |
| exit 2 "caractere de controle" | chave colada com quebra de linha ou espaço no meio | defina a chave de novo |
| `M102` | resposta sem PNG: não é JSON, sem `b64_json` (modelo fora da família GPT Image), base64 inválido | rode de novo só aquela tela (`--telas`); confira o modelo |
| `M103` | não gravou o arquivo (bloqueado pela sincronização, antivírus, disco cheio) | libere a pasta ou use `--saida` em outra |
| exit 2 "passam de --max-imagens" | spec grande demais para uma execução | gere em partes com `--telas` ou suba o teto, de propósito |

## 7. Fontes

- Geração de imagem (parâmetros, tamanhos, qualidade, verificação da organização):
  <https://developers.openai.com/api/docs/guides/image-generation>
- Modelo `gpt-image-2`: <https://developers.openai.com/api/docs/models/gpt-image-2>
- Modelos e depreciações: <https://developers.openai.com/api/docs/models>,
  <https://developers.openai.com/api/docs/deprecations>

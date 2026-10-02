# Formato de saída das etapas `/pp:*`

Todas as etapas falam com o usuário do mesmo jeito: quem nunca usou o kit precisa saber, em
qualquer tela, **onde está, o que fazer agora e qual é o próximo comando**. Este é o padrão.

## 1. Esqueleto de toda etapa

1. `estado.py comecar <etapa>`: confere a ordem e imprime o banner. Exit 1 = etapa fora de ordem:
   mostre a saída do script e **pare** (ela já traz o comando certo).
2. Uma frase dizendo o que vai acontecer nesta sessão e quanto do usuário ela exige.
3. O trabalho da etapa (perguntas, agentes, scripts).
4. Checkpoints sempre que o usuário precisa decidir, conferir ou agir no ambiente (seção 3).
5. Portão de saída da etapa: o que prova que ela terminou (cada skill de etapa diz qual).
6. `estado.py concluir <etapa> --nota "<o que ficou pronto>"` (ou `dispensar`/`reabrir`).
7. **Encerramento:** o resumo da etapa (abaixo) + o bloco "Próximo passo" **exatamente como o
   script imprimiu**. Não invente outro comando: o script é a fonte do próximo passo.

Resumo da etapa, curto e sem comemoração. Linha sem conteúdo não aparece:

```
**Entregue:** <arquivos e o que ficou pronto>
**Verificado:** <comando → última linha>, <o que o usuário conferiu>
**Revisado:** <agente: o que voltou e por quê>
**Com você:** <o que foi escalado ou ficou para decidir>
**Não verificado:** <o que só o ambiente prova, ou o que não deu para rodar>
```

Se nada foi verificado, a linha diz isso com todas as letras.

Comando do script (Bash, da raiz do projeto):

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/estado.py" <comando> [etapa] [opções]
```

## 2. Banner

O `comecar` imprime. Para transições dentro da etapa, use o mesmo formato:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PP ► MOCKUPS EM IMAGEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 3. Checkpoints

Toda parada que exige o usuário usa uma caixa de 62 colunas e termina com a ação esperada.
Decisão fechada vai por `AskUserQuestion` (opção recomendada primeiro, com "(Recomendado)").

```
╔══════════════════════════════════════════════════════════════╗
║  CHECKPOINT: Ação no ambiente                                ║
╚══════════════════════════════════════════════════════════════╝

<passo a passo numerado: onde clicar, o que colar, o que conferir>

──────────────────────────────────────────────────────────────
→ Digite "feito" quando terminar, ou descreva o erro que apareceu
──────────────────────────────────────────────────────────────
```

| Tipo | Quando | Ação esperada |
|---|---|---|
| `CHECKPOINT: Decisão` | escolha que muda o resultado (trilha de dados, gerar imagens) | escolher uma opção |
| `CHECKPOINT: Conferência` | o usuário precisa ver algo (protótipo, mockups, relatório) | "aprovado" ou o ajuste |
| `CHECKPOINT: Ação no ambiente` | 🔴: só o humano faz (criar tabela, colar no Studio, publicar) | "feito" ou o erro |

Regras: uma pergunta aberta por vez; escolhas fechadas e independentes entre si podem ir juntas
numa chamada do `AskUserQuestion` (até 4), e o que um agente vai precisar saber se pergunta antes de
chamá-lo, numa rodada só; passo a passo com caminho de menu real; nunca peça senha, chave ou token
na conversa.

## 4. Agentes

Antes de abrir um agente, diga quem vai trabalhar e o que ele entrega:

```
◆ Chamando o Agente de Mockups em Imagem...
  → inventário de telas, moldura e spec das imagens
✓ Agente de Mockups em Imagem concluído: 7 telas, 12 imagens previstas
```

Dois agentes em paralelo vão na **mesma mensagem**. Achado ou arquivo de agente é hipótese até você
julgar (rodar o validador, abrir o arquivo): `references/subagentes.md`, seção "Julgar a entrega".
O veredito sai numa linha por agente:

```
✓ Agente Power Apps Canvas: aceito (validar-telas.py → 0 erro(s), 4 arquivos)
↻ Agente Power Automate: revisão 1 — o fluxo de exclusão não devolve `id` no Response
⚠ Agente de Arquitetura: escalado — o PRD não diz quem aprova a devolução
```

## 5. Símbolos

| Símbolo | Significado |
|---|---|
| ✓ | concluído, aprovado, verificado |
| ✗ | falhou, ausente, bloqueado |
| ◆ | em andamento |
| ○ | pendente |
| ⊘ | dispensado, com motivo |
| ↺ | reaberto (ajuste ou correção) |
| ⚠ | atenção |
| 🔴 | só o humano faz, no ambiente |

## 6. Erro

```
╔══════════════════════════════════════════════════════════════╗
║  ERRO                                                        ║
╚══════════════════════════════════════════════════════════════╝

<o que aconteceu, em uma frase>

**Para resolver:** <passos>
```

## 7. O que não fazer

- Encerrar a etapa sem o bloco "Próximo passo".
- Seguir para a etapa seguinte na mesma sessão: cada etapa começa numa sessão nova (`/clear`),
  porque lê tudo do disco e o contexto limpo evita decisão velha vazando para a próxima.
- Pedir permissão para passos internos óbvios; pergunte só o que muda o resultado.
- Jargão sem explicação: na primeira vez, diga em uma frase o que é (ex.: "delegação: o Power Apps
  manda o filtro para o banco em vez de baixar tudo").

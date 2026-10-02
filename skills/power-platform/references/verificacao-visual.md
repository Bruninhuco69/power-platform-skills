# Verificação visual: olhar antes de mostrar

Validador de arquivo prova estrutura (tokens, telas, componentes do catálogo), não aparência. Texto
cortado, botão sobre botão, contraste ruim e tela em branco passam em `0 erro(s)`. Por isso quem
entrega uma página ao usuário **fotografa e olha** antes: o agente que escreveu (autoconferência) e
a sessão que julga.

## 1. Fotografar

```bash
# protótipo: uma imagem por tela, no padrão de navegação do design
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/capturar-telas.py" docs/planejamento/prototipo/index.html
# a primeira tela nos cinco padrões de navegação
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/capturar-telas.py" docs/planejamento/prototipo/index.html --navegacoes
# outro perfil (chave de PERFIS do protótipo)
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/capturar-telas.py" docs/planejamento/prototipo/index.html --perfil operador
# a amostra do design
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/capturar-telas.py" docs/planejamento/identidade.html
```

As imagens vão para `capturas/` ao lado do HTML (fora do Git: `.gitignore` do projeto). O script
usa o Chrome ou o Edge sem janela, com um perfil temporário (não mexe no navegador aberto).
Sem navegador (exit 2): a verificação visual fica **não verificado** no resumo, nunca "ok".

## 2. Olhar

Abra cada imagem com a ferramenta de leitura e confira, nesta ordem:

| # | O quê | Falha típica |
|---|---|---|
| 1 | A tela renderizou | imagem em branco ou só a barra do protótipo: erro de script na página |
| 2 | Texto inteiro | rótulo cortado, "..." onde não devia, texto saindo do botão ou do cartão |
| 3 | Nada sobreposto | menu sobre o conteúdo, modal atrás do véu, dois controles no mesmo lugar |
| 4 | Alinhamento e respiro | colunas desalinhadas, margens diferentes entre telas, vazio grande de um lado só |
| 5 | Hierarquia | o título é o maior texto; uma ação primária por área; destrutivo em vermelho |
| 6 | Cor e contraste | cor fora da paleta do design system, texto claro sobre fundo claro |
| 7 | Navegação | o padrão da seção 2.1 do design system; item ativo certo; "‹ Início" com cartões |
| 8 | Fidelidade ao Canvas | nada que o Canvas não faz (sombra fina, gradiente, fonte de fora, layout que reflui) |

Cada falha vira um item com a imagem, a região e o que está errado (ex.: `tela-pedidos.png`, coluna
Ações: botão "Cancelar" cortado em 1920 px).

## 3. Quem faz o quê

| Quem | Quando | Com a falha |
|---|---|---|
| `agente-prototipo` | depois do `verificar-prototipo.py` limpo | corrige e fotografa de novo; o que não resolveu vai para os alertas |
| sessão do `/pp:prototipo` | ao julgar a entrega | revisão para o agente, com a imagem e a região |
| sessão do `/pp:design` | antes de mostrar a `identidade.html` | corrige a amostra (é arquivo da própria sessão) e fotografa de novo |

O usuário vê a página depois disso. A verificação visual não substitui a conferência dele; evita
que ele gaste a conferência com defeito que a máquina já podia ter visto.

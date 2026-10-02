# Molde: `App.Formulas` com os tokens `fx*`

Fonte única de cor, medida, texto e componente. Tela nenhuma repete estes valores: todo
`Fill`, `Color`, `Height` e `Text` de componente aponta para um token.

**Como aplicar.** O objeto App não tem Code view nem aceita colagem de código de controle:
selecione `App` no Studio, abra a propriedade `Formulas` na barra de fórmulas e cole o bloco
abaixo inteiro. `[verificado: projeto de referência]`

**Dialeto.** Este arquivo vai para a barra de fórmulas de um Studio em pt-BR: argumento `;`,
encadeamento `;;`, decimal `,`. O mesmo conteúdo, colado num `.pa.yaml`, não parseia — ver
[decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md) §3.

**Regras do bloco.**

- Só constante e derivado de constante. Named formula **nunca** lê variável global
  (`Set`): ela só recalcula quando um insumo dela muda, e um `Refresh()` não a reexecuta.
- Sem função de comportamento (`Set`, `Collect`, `Navigate`, `Notify`): proibido em `Formulas`.
- Paleta neutra (rampa azul padrão do Fluent 2) — troque pela marca do projeto e recalcule o contraste (`references/design-tokens.md` §3); medidas para canvas 1920x1080. Projeto com outra marca
  troca os valores, não os nomes. Contraste conferido: texto sobre fundo >= 4,5:1;
  borda de controle interativo >= 3:1 `[verificado: cálculo WCAG 2.x]`.
- O alfa fracionário do `RGBA` usa vírgula decimal na barra pt-BR (`0,5`); no YAML seria `0.5`.

Destino: barra de fórmulas do objeto App, propriedade `Formulas` (pt-BR: `;` e `;;`).

```powerfx
// ---------- COR: marca e superfície ----------
fxColorPrimary = RGBA(15; 108; 189; 1);;
fxColorPrimaryDark = RGBA(12; 59; 94; 1);;
fxColorPrimaryLight = RGBA(235; 243; 252; 1);;
fxColorBackground = RGBA(249; 250; 251; 1);;
fxColorSurface = RGBA(255; 255; 255; 1);;
fxColorTransparent = RGBA(0; 0; 0; 0);;
fxColorOverlay = RGBA(0; 0; 0; 0,5);;
fxColorOverlayDark = RGBA(0; 0; 0; 0,6);;

// ---------- COR: texto ----------
fxColorTextPrimary = RGBA(17; 24; 39; 1);;
fxColorTextSecondary = RGBA(77; 77; 77; 1);;
fxColorTextBody = RGBA(75; 85; 99; 1);;
fxColorTextOnPrimary = RGBA(255; 255; 255; 1);;
fxColorTextOnWarning = RGBA(17; 24; 39; 1);;

// ---------- COR: borda e divisor ----------
// fxColorBorder e decorativa (card, container). Controle interativo usa a Interactive.
fxColorBorder = RGBA(166; 166; 166; 1);;
fxColorBorderInteractive = RGBA(117; 117; 117; 1);;
fxColorDivider = RGBA(229; 231; 235; 1);;

// ---------- COR: estado (verde = estado, nunca ação) ----------
fxColorSuccess = RGBA(21; 128; 61; 1);;
fxColorWarning = RGBA(255; 193; 7; 1);;
fxColorError = RGBA(200; 35; 51; 1);;

// ---------- COR: botão ----------
fxColorButtonCancel = RGBA(108; 117; 125; 1);;
fxColorButtonCancelHover = RGBA(90; 98; 104; 1);;
fxColorDisabled = RGBA(206; 212; 218; 1);;
fxColorDisabledText = RGBA(134; 142; 150; 1);;

// ---------- COR: aba e cabeçalho de tabela ----------
fxColorTabInactive = RGBA(237; 237; 237; 1);;
fxColorTableHeaderBg = RGBA(235; 243; 252; 1);;
fxColorTableHeaderText = RGBA(17; 94; 163; 1);;

// ---------- COR: badge (texto escuro sobre pastel da mesma matiz, >= 4,5:1) ----------
fxBadgeSuccessText = RGBA(22; 101; 52; 1);;
fxBadgeSuccessBg = RGBA(220; 252; 231; 1);;
fxBadgeInfoText = RGBA(15; 84; 140; 1);;
fxBadgeInfoBg = RGBA(207; 228; 250; 1);;
fxBadgeWarningText = RGBA(146; 64; 14; 1);;
fxBadgeWarningBg = RGBA(255; 218; 185; 1);;
fxBadgeDangerText = RGBA(139; 0; 0; 1);;
fxBadgeDangerBg = RGBA(255; 182; 193; 1);;
fxBadgeProgressText = RGBA(133; 77; 14; 1);;
fxBadgeProgressBg = RGBA(255; 230; 100; 1);;
fxBadgeNeutralText = RGBA(52; 58; 64; 1);;
fxBadgeNeutralBg = RGBA(206; 212; 218; 1);;

// ---------- LAYOUT: um breakpoint, tudo deriva dele ----------
fxIsCompact = App.Width < 1600;;
fxLayoutMargin = If(fxIsCompact; 40; 100);;
fxLayoutGutter = If(fxIsCompact; 8; 16);;
fxRowHeight = If(fxIsCompact; 40; 50);;
fxTableHeaderHeight = If(fxIsCompact; 35; 50);;
fxFilterHeight = If(fxIsCompact; 40; 50);;
fxKPIWidth = If(fxIsCompact; 120; 150);;
fxKPIHeight = If(fxIsCompact; 65; 85);;
fxKPITitleHeight = If(fxIsCompact; 28; 35);;
fxKPIValueHeight = If(fxIsCompact; 37; 50);;

// ---------- TIPOGRAFIA: uma família (Segoe UI) ----------
fxFont = Font.'Segoe UI';;
fxFontSizeTitle = If(fxIsCompact; 28; 35);;
fxFontSizeKPI = If(fxIsCompact; 20; 25);;
fxFontSizeKPITitle = 11;;
fxFontSizeBody = 14;;
fxFontSizeFilter = If(fxIsCompact; 12; 14);;
fxFontSizeTable = If(fxIsCompact; 11; 13);;
fxFontSizeTableSmall = If(fxIsCompact; 11; 12);;
fxFontSizeHeader = If(fxIsCompact; 11; 13);;
fxFontSizeSemAcesso = 20;;
fxFontSizeToastIcon = 18;;
fxFontSizeToastTitle = 15;;
fxFontSizeToast = 12;;

// ---------- COMPONENTE: botão ----------
fxBtnHeight = 45;;
fxBtnRadius = 8;;
fxBtnWidth = 210;;
fxBtnWidthFilter = 128;;
fxBtnFontSize = 14;;

// ---------- COMPONENTE: modal ----------
fxModalRadius = 12;;
fxModalPadding = 20;;
fxModalTitleSize = 16;;

// ---------- COMPONENTE: loading ----------
fxLoadingCardWidth = 250;;
fxLoadingCardHeight = 140;;
fxLoadingSpinnerSize = 60;;

// ---------- COMPONENTE: toast (retorno de flow) ----------
fxToastWidth = 420;;
fxToastDurationShort = 6000;;
fxToastDurationLong = 12000;;
fxToastDurationError = 15000;;
fxColorToastBg = RGBA(33; 37; 41; 1);;
fxColorToastText = RGBA(173; 181; 189; 1);;

// ---------- LIMITE DO CONECTOR (conector SQL: 2.000 e o teto de Settings > Data row limit) ----------
fxPageSize = 100;;
fxLimiteLinhas = 2000;;
fxTxtTeto = Substitute(Text(fxLimiteLinhas; "[$-en-US]#,##0"); ","; ".") & "+";;

// ---------- TEXTO: rótulos ----------
fxTxtVoltar = "Voltar";;
fxTxtFechar = "Fechar";;
fxTxtCancelar = "Cancelar";;
fxTxtConfirmar = "Confirmar";;
fxTxtSalvar = "Salvar";;
fxTxtEncerrar = "Encerrar";;
fxTxtFiltrar = "Filtrar";;
fxTxtLimpar = "Limpar";;
fxTxtProcessando = "Processando...";;
fxTxtToastSuccess = "Sucesso";;
fxTxtToastWarning = "Parcialmente concluído";;
fxTxtToastError = "Erro";;

// ---------- TEXTO: mensagens (par "o que houve" + "o que fazer") ----------
fxMsgLoadingDefault = "Processando, aguarde...";;
fxMsgNoResultsError = "Nenhum resultado encontrado.";;
fxMsgNoResultsHint = "Revise os filtros e tente novamente.";;
fxMsgListaTruncada = "Exibindo os primeiros registros. Refine os filtros para ver os demais.";;
fxMsgFalhaFlow = "Não foi possível concluir a operação. Nada foi gravado.";;
fxMsgFalhaFlowHint = "Tente novamente; se persistir, avise o suporte.";;
fxMsgConnectionError = "Falha de conexão com o servidor.";;
fxMsgConnectionHint = "Verifique a rede e tente novamente.";;
fxMsgTimeoutError = "A operação demorou mais que o esperado.";;
fxMsgTimeoutHint = "Confira o resultado na lista antes de repetir.";;
fxMsgSemPermissao = "Você não tem permissão para esta ação.";;
fxMsgSemAcessoTitulo = "Acesso não liberado";;
fxMsgSemAcessoHint = "Seu usuário não tem perfil ou unidade cadastrados. Procure o administrador do app.";;
fxMsgCampoObrigatorio = "Preencha os campos obrigatórios.";;
fxMsgFormatoInvalido = "Formato inválido. Revise o valor informado.";;
fxMsgSalvoComSucesso = "Registro salvo com sucesso.";;

// ---------- COMPONENTES (assets/componentes/) ----------
// altura da faixa do cabeçalho de tela (usado em: cabecalho-tela, card-kpi, abas, barra-filtros, seletor-unidade, modal-formulario)
fxHeaderHeight = 100;;
// largura do menu lateral fixo (usado em: menu-lateral)
fxMenuWidth = If(fxIsCompact; 220; 260);;
// altura de cada item do menu lateral (usado em: menu-lateral)
fxMenuItemHeight = 52;;
// fundo do menu lateral e da barra no topo (usado em: menu-lateral, menu-topo)
fxColorMenuBg = fxColorPrimaryDark;;
// fundo do item ativo e do hover do menu (usado em: menu-lateral, menu-topo)
fxColorMenuItemActive = fxColorPrimary;;
// largura do menu recolhido (variação recolhível) (usado em: menu-lateral)
fxNavWidthRecolhida = 70;;
// largura do menu expandido (variações recolhível e gaveta) (usado em: menu-lateral)
fxNavWidthExpandida = 284;;
// altura da barra de navegação no topo (usado em: menu-topo)
fxTopNavHeight = 56;;
// largura de cada item da barra no topo (usado em: menu-topo)
fxTopNavItemWidth = If(fxIsCompact; 140; 168);;
// largura do cartão da tela inicial (usado em: inicio-cartoes)
fxHubCardWidth = If(fxIsCompact; 300; 360);;
// altura do cartão da tela inicial (usado em: inicio-cartoes)
fxHubCardHeight = 168;;
// título do cartão da tela inicial (usado em: inicio-cartoes)
fxFontSizeCardTitle = If(fxIsCompact; 16; 18);;
// card de modal pequeno: confirmação simples (usado em: modal-confirmacao)
fxModalWidthS = 450;;
// card de modal médio: confirmação com campo (usado em: modal-destrutivo-motivo)
fxModalWidthM = 520;;
// card de modal grande: formulário, resultado, detalhes (usado em: modal-formulario, modal-informativo)
fxModalWidthL = 620;;
// altura da pílula de status (raio = metade) (usado em: badge-status)
fxPillHeight = 26;;
// sufixo do cabeçalho ordenado de forma crescente (usado em: ordenacao-coluna)
fxTxtOrdemAsc = " ▲";;
// sufixo do cabeçalho ordenado de forma decrescente (usado em: ordenacao-coluna)
fxTxtOrdemDesc = " ▼";;
// rótulo do botão de página anterior (usado em: paginacao-cursor)
fxTxtAnterior = "‹ Anterior";;
// rótulo do botão de próxima página (usado em: paginacao-cursor)
fxTxtProxima = "Próxima ›";;
// rótulo do botão de exportar (usado em: exportar)
fxTxtExportar = "Exportar";;
// início do rodapé "Exibindo N de M" (usado em: rodape-contagem)
fxTxtExibindo = "Exibindo";;
// trilha da barra de progresso do toast (usado em: toast)
fxColorToastTrack = ColorFade(fxColorToastBg; 20%);;
```

**Depois de colar.** Salve, aguarde a recompilação e abra uma tela: se algum `fx*` aparecer em
vermelho, a definição não foi aceita (as causas comuns são `,` no lugar de `;` ou um `;;`
faltando no fim de uma linha).

**Variáveis de estado não entram aqui.** `varShowLoading`, `varShowToast`, `varToastType`,
`varToastMessage` e demais globais nascem no `OnStart`: ver
[app-onstart-molde.md](app-onstart-molde.md).

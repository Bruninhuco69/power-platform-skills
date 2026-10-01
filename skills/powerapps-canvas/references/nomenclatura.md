# Nomenclatura

Controle, variável, coleção, token, fonte de dados e flow. Decisão T5 de
[decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md). Nome de **coluna e
tabela** vem do ambiente real (`NOMES-AS-BUILT`, skill `dataverse`); este arquivo não os define.

## Sumário

1. [Controles](#1-controles)
2. [Variáveis, coleções e tokens](#2-variáveis-coleções-e-tokens)
3. [Fontes de dados e flows](#3-fontes-de-dados-e-flows)
4. [O que o validador checa](#4-o-que-o-validador-checa)

---

## 1. Controles

```text
<prefixo-tela>-<tipo>-<módulo>-<elemento>[-<qualificador>]
```

Tudo em **kebab-case minúsculo, sem acento**, **único no app inteiro** (o Studio acrescenta `_1`,
`_2` ao duplicar, e esse sufixo não é semântico: renomeie). Prefixo de tela de 2 letras, definido
no início (`pd` pedidos, `mn` menu). Exemplos: `pd-lbl-header-titulo`, `pd-btn-filtro-limpar`,
`pd-mod-confirmar-btn-voltar`, `pd-gal-pedidos`.

| Abreviação | Controle | Abreviação | Controle |
|---|---|---|---|
| `lbl` | Label | `gal` | Gallery |
| `btn` | botão, aba, forma arredondada | `img` | Image |
| `mod` | modal (véu e card) | `ico` | ícone |
| `con` | GroupContainer | `dtp` | DatePicker |
| `cmb`, `cbo` | ComboBox (escolha **uma** por projeto) | `chk` | CheckBox |
| `txt` | TextInput | `tim` | Timer |
| `hdr` | cabeçalho de coluna | `spn` | Spinner |
| `rec`, `shp` | Rectangle, forma decorativa | `cmp` | raiz de bloco compartilhado |

- **Bloco compartilhado** (toast, loading, sem acesso) sai **já prefixado** com a tela:
  `pd-cmp-toast`, `pd-cmp-loading`. Colar bloco sem prefixo faz o Studio renomear para `_1`.
- **Nome automático** (`Button1_38`, `Label3_2`, `Timer1_3`) é dívida que só se paga com o Studio
  aberto: nomeie na criação. Em app real, quase um terço dos controles tinha nome automático e
  fórmulas referenciavam `Checkbox1_7` sem que se soubesse o que era.
- **Prefixo de outra tela dentro da tela** é resíduo de copiar e colar: o prefixo do controle é o
  da tela onde ele mora (exceção legítima: o menu replicado em todas as telas, com prefixo
  próprio).
- Tipo omitido (`toast-title`, `loading-card`) é variante solta a evitar: use o token de tipo.
- **Referência a controle com hífen sempre entre aspas simples** em fórmula: `'pd-gal-pedidos'.AllItemsCount`.

## 2. Variáveis, coleções e tokens

| Padrão | Uso | Exemplo |
|---|---|---|
| `var<Prefixo><Assunto>` (PascalCase) | global de tela ou módulo | `varPDFiltroAplicado`, `varPedidoSel` |
| `varShow*`, `varMostrar*` | visibilidade de overlay, toast, modal | `varShowLoading`, `varMostrarConfirmar` |
| `varToast*` | estado do toast | `varToastType`, `varToastMessage` |
| `varRet` | **uma** variável de retorno de flow por app | `varRet.status` |
| `ctx*` | variável de **contexto** (`UpdateContext`) | `ctxModo` |
| `col<Conteúdo>` | coleção | `colUnidades`, `colSelecionados` |
| `fx*` | token de tema, medida, texto (named formula) | `fxColorPrimary`, `fxMsgFalhaFlow` |
| `frm*` | named formula de dado (KPI, lista) | `frmKPIAbertos` |
| `Flg_*`, `pode_*` | flag de perfil (coluna), lida de `varPerfil` | `varPerfil.Flg_Encerrar` |

- **`var` minúsculo**, sempre (Power Fx não diferencia caixa, mas a busca e a leitura sim): `Var`
  com V maiúsculo aparece em apps reais e quebra a busca.
- **Nenhuma global sem prefixo** (`BarraSecao`, `Tabela`, `CorFundoBotao`): nome genérico sem
  escopo é o pior caso. Aba ativa: `var<Prefixo>Tab`.
- **`ctx*` para contexto e `var*` para global**: a colisão fica impossível de escrever (um
  contexto sombreia a global de mesmo nome).
- Contador de laço: `vari` só dentro de `ForAll`/`With`; nunca global.
- Variável de **janela de data** guarda inteiro: `varPDFiltroDe`, `varPDFiltroAte`.

## 3. Fontes de dados e flows

- Nome do conector no app é identificador: sem aspas se não tiver hífen (`Pedido`), entre aspas
  simples se tiver (`'app-pedido'`). Prefira um padrão **único** por projeto e registre no
  `NOMES-AS-BUILT`; singular e plural quase iguais para a mesma tabela (duas conexões) são
  defeito.
- Flow: `<app>-flow-<entidade>-<verbo>` (`app-flow-pedido-acao`), kebab-case; o app mostra o nome
  que o flow tem **na solução**. Não crie `<app>-sql-flow-*` e `<app>-flow-*` para a mesma coisa.
- Nenhum `dev` literal em nome de tabela, fonte ou flow (ambiente é variável de ambiente e
  connection reference, skill `power-platform`).

## 4. O que o validador checa

| Código | Regra |
|---|---|
| T010 | nome de controle fora de kebab-case (acusa também o padrão de nome automático do Studio) |
| T006 | nome de controle duplicado no conjunto validado |

Prefixo de tela, tipo permitido, `var*` e `col*` **não** são checados (revisão): item aberto do
validador. Nome de coluna contra o ambiente real: T014, só na trilha Dataverse e só com
`prefixo_publisher` no `power-platform.config.json`.

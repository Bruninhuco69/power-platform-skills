# Padrões de navegação

Como o app leva o usuário de uma área para outra. Quem decide é o usuário, no `/pp:design`
(etapa 3), com prévia de cada opção. A decisão vai para o `ux-design-system.md` §2.1 e as etapas
seguintes só a aplicam: os mockups desenham, o protótipo mostra e a construção cola o componente
do catálogo correspondente.

## Sumário

1. [Os cinco padrões](#1-os-cinco-padrões)
2. [Qual recomendar](#2-qual-recomendar)
3. [Como perguntar](#3-como-perguntar)
4. [Prévias](#4-prévias)
5. [O que cada etapa faz com a decisão](#5-o-que-cada-etapa-faz-com-a-decisão)

---

## 1. Os cinco padrões

| Id | Padrão | Componente do catálogo Canvas | Bom para | Cuidado |
|---|---|---|---|---|
| `lateral-fixo` | menu lateral sempre aberto | `menu-lateral` | uso diário no desktop, 3 ou mais áreas | ocupa 220–260 px de largura |
| `lateral-recolhivel` | menu lateral que ☰ alterna entre só a inicial de cada item e o rótulo inteiro | `menu-lateral`, variação recolhível | telas com tabela larga | recolhido, mostra só a inicial: rótulos precisam começar por letras diferentes |
| `gaveta` | menu escondido; ☰ no cabeçalho abre por cima do conteúdo (hambúrguer) | `menu-lateral`, variação gaveta | tablet, tela estreita, uso eventual | um toque a mais para trocar de área; a área atual não fica visível |
| `topo` | barra horizontal no alto, com os itens lado a lado | `menu-topo` | 2 a 6 áreas com nome curto; largura toda para o conteúdo | não cabe mais de 6 itens nem rótulo longo |
| `inicio-cartoes` | tela inicial com um cartão por área; "‹ Início" nas demais telas | `inicio-cartoes` | uso eventual, uma tarefa por visita, gente pouco acostumada a menus | ida e volta pelo início a cada troca de área |

Em todos: a visibilidade de cada item vem da **flag** do perfil (nunca do nome), o item ativo tem
fundo **e** negrito, e sem perfil a navegação some (painel "sem acesso"). Esconder item não é
segurança: quem barra é o flow.

## 2. Qual recomendar

Leia a resposta 3.2 do `brainstorm.md` (dispositivos e resolução), o número de áreas de primeiro
nível que o PRD sugere (funcionalidades P0 agrupadas) e a frequência de uso.

| Situação | Recomende |
|---|---|
| tablet, celular ou janela estreita | `gaveta` |
| uso eventual, cada pessoa entra para uma tarefa | `inicio-cartoes` |
| 2 a 6 áreas com nome curto, telas com tabela larga | `topo` |
| uso diário, telas com tabela larga, 4 ou mais áreas | `lateral-recolhivel` |
| uso diário no desktop, 3 ou mais áreas (o caso comum) | `lateral-fixo` |
| uma ou duas telas só | nenhum menu: botão de voltar (registre `nenhum` e o motivo) |

Na dúvida entre dois, recomende o que deixa a área atual visível (`lateral-fixo` ou `topo`).

## 3. Como perguntar

`AskUserQuestion` aceita até 4 opções, então são duas perguntas, cada opção com a prévia da §4 no
campo `preview` e a recomendada primeiro, com "(Recomendado)":

1. **Onde fica a navegação?** (header `Navegação`): "Menu na lateral esquerda", "Barra no topo",
   "Tela inicial com cartões".
2. **Só se escolheu a lateral: como o menu se comporta?** (header `Menu lateral`): "Sempre aberto",
   "Recolhível (☰ alterna)", "Gaveta que abre por cima (☰)".

Depois, se for `lateral-recolhivel`, pergunte se ele começa aberto ou fechado (padrão: fechado,
para dar largura à tabela). Registre a frase do usuário no `ux-design-system.md` §2.1.

## 4. Prévias

Use estes desenhos no `preview` de cada opção (monoespaçado, até 40 colunas).

**Menu na lateral esquerda**

```text
┌────────┬─────────────────────────┐
│ ▣ App  │ Pedidos                 │
│        ├─────────────────────────┤
│ Início │                         │
│▌Pedidos│   conteúdo da tela      │
│ Relat. │                         │
│        │                         │
│ Ana    │                         │
└────────┴─────────────────────────┘
```

**Barra no topo**

```text
┌──────────────────────────────────┐
│ App  Início ▌Pedidos  Relat.  Ana│
├──────────────────────────────────┤
│ Pedidos                          │
├──────────────────────────────────┤
│                                  │
│   conteúdo com a largura toda    │
│                                  │
└──────────────────────────────────┘
```

**Tela inicial com cartões**

```text
┌──────────────────────────────────┐
│ Início                           │
├──────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌──────┐ │
│ │ Pedidos │ │ Relat.  │ │ Usu. │ │
│ │ Cadastre│ │ Veja os │ │ Dê   │ │
│ │ [Abrir] │ │ [Abrir] │ │[Abrir│ │
│ └─────────┘ └─────────┘ └──────┘ │
└──────────────────────────────────┘
 nas outras telas: [‹ Início] Pedidos
```

**Sempre aberto**

```text
┌────────┬─────────────────────────┐
│ ▣ App  │ Pedidos                 │
│ Início ├─────────────────────────┤
│▌Pedidos│                         │
│ Relat. │   conteúdo              │
└────────┴─────────────────────────┘
 o menu ocupa 260 px o tempo todo
```

**Recolhível (☰ alterna)**

```text
 fechado              aberto
┌──┬─────────────┐   ┌────────┬──────┐
│☰ │ Pedidos     │   │‹  Menu │Pedid.│
│ I├─────────────┤   │ Início ├──────┤
│▌P│ conteúdo    │   │▌Pedidos│ cont.│
│ R│ mais largo  │   │ Relat. │      │
└──┴─────────────┘   └────────┴──────┘
```

**Gaveta que abre por cima (☰)**

```text
 fechada              aberta
┌────────────────┐   ┌────────┬░░░░░░┐
│☰ Pedidos       │   │App   ✕ │░░░░░░│
├────────────────┤   │ Início │░ véu │
│ conteúdo com a │   │▌Pedidos│░░░░░░│
│ largura toda   │   │ Relat. │░░░░░░│
└────────────────┘   └────────┴░░░░░░┘
```

## 5. O que cada etapa faz com a decisão

| Etapa | O que faz |
|---|---|
| `/pp:design` | pergunta, registra no `ux-design-system.md` §2.1 (padrão, motivo, componente) e mostra a navegação na amostra `identidade.html` |
| `/pp:mockups` | o `pp:agente-mockups` copia o padrão para a moldura do inventário e para `moldura.navegacao` do spec; o mapa de navegação segue o padrão (com cartões, toda tela volta ao início) |
| `/pp:prototipo` | o `pp:agente-prototipo` põe o id em `NAVEGACAO`; o seletor "Navegação" da barra do protótipo deixa o usuário comparar os cinco padrões ao vivo. Trocar de padrão é item `identidade` do ajuste e volta ao `/pp:design` |
| `/pp:construir app` | o `pp:agente-canvas` cola o componente da tabela da §1, na variação certa, em toda tela (com `inicio-cartoes`, o botão "‹ Início" em cada tela que não é a inicial) |
| `/pp:testar` | o roteiro confere a navegação com cada perfil: item oculto por flag, item ativo, volta ao início, gaveta fechando ao trocar de tela |

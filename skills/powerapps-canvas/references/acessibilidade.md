# Acessibilidade (WCAG AA) em Canvas

Checklist e limites para app Canvas ManualLayout + Classic. Em conflito entre a documentação do
Learn e o Studio dos projetos de referência, **vale o que o Studio aceita**: várias propriedades
de acessibilidade do Learn são recusadas no YAML desses controles (PA2108); ver
[propriedades-inexistentes.md](propriedades-inexistentes.md).

## Sumário

1. [O que está atestado e o que não está](#1-o-que-está-atestado-e-o-que-não-está)
2. [Checklist](#2-checklist)
3. [Limitações que não dá para contornar](#3-limitações-que-não-dá-para-contornar)
4. [Ferramenta](#4-ferramenta)
5. [Fontes](#5-fontes)

---

## 1. O que está atestado e o que não está

Num app real, a rodada de acessibilidade foi **revertida inteira** (centenas de propriedades) porque o
Studio recusou o bloco (PA2108). `[verificado: projeto de referência]`

| Propriedade | Situação |
|---|---|
| `AccessibleLabel` | **recusada** em `Classic/Button@2.2.0` e `Button@0.0.45` (o nome acessível do botão vem do `Text`); **não atestada** nos demais: teste |
| `FocusedBorderThickness` | **recusada** em todos os controles do app de referência |
| `Live` | **recusada** em `Label@2.5.1` |
| `Role` (`Label.Role.Heading1`) | **não atestada**: teste antes de espalhar |
| `FocusedBorderColor` | atestada em `Classic/TextInput`, `Classic/ComboBox` e `Classic/DatePicker` |
| `Tooltip` | atestada (botões de ícone, como o `✕` do toast) |
| `TabIndex` | atestada (`0` participa, `-1` não participa) |
| `Underline` | atestada em `Label` e em botão de badge |

Consequência: o que o Learn pede e o Studio recusa vira **mitigação por desenho**: texto no
próprio controle, `Tooltip`, contraste, texto além de cor, ordem de tabulação limpa. Quando o seu
Studio aceitar uma propriedade a mais, registre-a na tabela e no validador.

## 2. Checklist

**Nome acessível**
- [ ] Botão: o `Text` descreve a ação. Botão de ícone: `Tooltip`. Nenhum `Classic/Button` com
      `Text: =""` participa da tabulação (fundo de linha e forma decorativa: `TabIndex: =-1`
      ou `DisplayMode.Disabled`).
- [ ] Checkbox de linha com `Text: =""` fica sem nome: limitação registrada; mitigue com o
      rótulo da coluna e o contador de seleção.

**Ordem de foco e teclado**
- [ ] Só `TabIndex: =0` ou `-1`. Valor positivo é desencorajado e pode quebrar leitores de tela
      ("Check the order of the screen items" no checker).
- [ ] Para reordenar o foco, use container no lugar de `TabIndex`; habilite *Simplified tab
      index*.
- [ ] Controle moderno: `AcceptsFocus` (não há `TabIndex`).

**Foco visível**
- [ ] `FocusedBorderColor` com pelo menos 3:1 contra o fundo nos inputs atestados.
- [ ] `FocusedBorderThickness` igual a 0 é erro no checker ("Focus isn't showing"), mas a
      propriedade é recusada no YAML: confirme no checker que o foco aparece com o padrão do
      controle `[não verificado]`.

**Contraste** (ver [design-tokens.md](design-tokens.md) §3 e §4)
- [ ] Texto normal >= 4,5:1; texto grande >= 3:1; borda e ícone interativos >= 3:1.
- [ ] Conferir também `Hover*` e `Pressed*` (`PressedColor` e `PressedFill` invertidos dão texto
      invisível).
- [ ] Texto desabilitado não tem requisito, mas precisa ser distinguível.

**Não depender só de cor**
- [ ] Estado por cor tem também texto, ícone ou sublinhado (badge com `Underline`, linha
      selecionada com badge textual, aba ativa com negrito e traço).

**Regiões dinâmicas**
- [ ] `Live` é recusada em `Label@2.5.1`: sem live region, mensagem que surge sem ação do
      usuário (toast, contador) não é anunciada. Mitigação: o toast é fechável, dura 6 a 15 s e
      erro que exige ação vai em modal (não toast); registre o limite ao cliente.

**Formulário**
- [ ] Obrigatório não só por `*`; erro **por campo**, não só no toast; rótulo >= 12; alvo
      interativo >= 24 por 24 px (WCAG 2.2, 2.5.8).

**Estrutura**
- [ ] Nome de tela descritivo (o leitor lê o nome da tela); conteúdo relacionado em
      `GroupContainer`.
- [ ] Um `Heading1` por tela via `Role`, **se** `Role` for atestada no seu Studio.

**Tempo**
- [ ] Timer que dispara mudança permite cancelar, ajustar ou avisar com 20 s de antecedência
      (auto-refresh com chave liga/desliga, [timers-async.md](timers-async.md) §2).

## 3. Limitações que não dá para contornar

Documentadas ([Accessibility limitations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessible-apps-limitations)):

| Limitação | Efeito no padrão do kit |
|---|---|
| diálogo e overlay não são suportados; use tela separada ou `Notify()` | todo modal; mitigue com botão `Voltar` e ordem de foco |
| aba só acessível via modern Tab list | abas Button + Rectangle; migração é a recomendação de médio prazo |
| tabela 2D só com Data Table clássico | galeria com labels |
| combo "caseiro" (TextInput + Gallery) não é acessível | use `Classic/ComboBox` |
| não há reação a teclas específicas (Esc, setas) | modal não fecha com Esc |
| `SetFocus` em cenários limitados | foco não vai ao modal ao abrir |
| não há equivalente a `aria-hidden` | conteúdo atrás do overlay continua na árvore |
| seção expansível: informe o estado no rótulo | `Text` do botão traz "Mostrar detalhes" ou "Ocultar detalhes" |

## 4. Ferramenta

**App checker > Accessibility** (canto superior direito do Studio). Resolva na ordem erros,
avisos, dicas. Regras relevantes: *Missing accessible label*, *Focus isn't showing*, *Check the
order of the screen items* (dispara com `TabIndex > 0`), *Add State indication text*,
*Revise screen name*, *HTML won't be accessible* (`HtmlViewer`). Rode depois de trocar paleta ou
adicionar bloco novo.

## 5. Fontes

- [Accessibility checker](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessibility-checker)
- [Accessibility properties](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/properties-accessibility)
- [Color contrast](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessible-apps-color)
- [Live regions](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessible-apps-live-regions)
- [Accessibility limitations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessible-apps-limitations)

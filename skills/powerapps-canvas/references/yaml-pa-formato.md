# Formato `.pa.yaml`: gramática, escape, indentação e colagem

Como escrever YAML que o Power Apps Studio aceita colar. Para Power Fx dentro das propriedades:
[powerfx-essencial.md](powerfx-essencial.md). Para os blocos prontos (modal, toast, galeria):
[ux-componentes.md](ux-componentes.md). Para a tela inteira: [tela-molde.md](../assets/tela-molde.md).

## Sumário

1. [Onde o YAML vive](#1-onde-o-yaml-vive)
2. [Dialeto: o YAML é invariante](#2-dialeto-o-yaml-é-invariante)
3. [Gramática](#3-gramática)
4. [Fórmulas de várias linhas](#4-fórmulas-de-várias-linhas)
5. [Escape de texto](#5-escape-de-texto)
6. [Indentação e nomes](#6-indentação-e-nomes)
7. [Como colar no Studio](#7-como-colar-no-studio)
8. [Controles e versões](#8-controles-e-versões)
9. [Layout: ManualLayout e AutoLayout](#9-layout-manuallayout-e-autolayout)
10. [Checklist antes de entregar YAML](#10-checklist-antes-de-entregar-yaml)
11. [Validação](#11-validação)
12. [Fontes](#12-fontes)

---

## 1. Onde o YAML vive

Um app Canvas é um `.msapp` (zip). Só os `*.pa.yaml` de `\Src` são código-fonte: um por tela,
mais `App.pa.yaml` e um por componente. Os `.json` do pacote não são estáveis entre salvar e
abrir e não vão para o controle de versão.
([Source code files for canvas apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml))

Extrair:

Destino: terminal (PowerShell), não é Power Fx.

```powershell
pac canvas list
pac canvas download --name "Nome do App" --extract-to-directory .\src --overwrite
```

`pac canvas pack` e `unpack` estão depreciados; o layout `Experimental` (`*.fx.yaml`) está
depreciado e será removido. Para versionar com edição externa e merge, a via suportada é a **Git Integration**
da Power Platform ([pac canvas](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas),
[Git Integration](https://learn.microsoft.com/en-us/power-platform/alm/git-integration/overview)).

Em projetos de referência as telas ficam como `.md` com **YAML puro** (sem cerca). O validador
lê esse formato inteiro; ver [SKILL.md](../SKILL.md) §Scripts.

## 2. Dialeto: o YAML é invariante

O arquivo em disco é salvo em locale invariante, qualquer que seja o idioma de quem edita
([Global support in Power Fx](https://learn.microsoft.com/en-us/power-platform/power-fx/global)).

| Destino | Argumento | Encadeia | Decimal |
|---|---|---|---|
| **YAML colado** (`.pa.yaml`, Code view) | `,` | `;` | `.` |
| **Barra de fórmulas** do Studio em pt-BR (inclui `App.OnStart` e `App.Formulas`) | `;` | `;;` | `,` |

Regra completa em [decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md) §3.
**Nunca escreva `;;` num arquivo YAML** (validador: T007). Depois de colar, o Studio em pt-BR
mostra `;` e `;;` na barra: é esperado, não "corrija".

## 3. Gramática

### 3.1 Estrutura do documento

Cinco chaves de topo e só elas (`additionalProperties: false` no schema
[pa.schema.yaml v3.0](https://raw.githubusercontent.com/microsoft/PowerApps-Tooling/refs/heads/master/schemas/pa-yaml/v3.0/pa.schema.yaml)):
`App`, `Screens`, `ComponentDefinitions`, `DataSources`, `EditorState`. Validador: T022.

### 3.2 Tela e controle

Destino: YAML colado (`,` e `;`).

```yaml
Screens:
  Exemplo:
    Properties:
      Fill: =fxColorBackground
      Height: =1080
      Width: =1920
      OnVisible: |-
        =Set(varTelaAtiva, "exemplo");
        Set(varShowLoading, false)
    Children:
      - ex-lbl-titulo:
          Control: Label@2.5.1
          Group: ex-con-header
          Properties:
            Text: ="Exemplo"
            Size: =fxFontSizeTitle
      - ex-con-corpo:
          Control: GroupContainer@1.5.0
          Variant: ManualLayout
          Properties:
            Fill: =fxColorSurface
            Height: =900
            Width: =1720
          Children:
            - ex-lbl-corpo-aviso:
                Control: Label@2.5.1
                Properties:
                  Text: ="Conteúdo"
```

- `Screens` aceita, por tela, só `Properties` e `Children`. Nome de tela com espaço e acento
  funciona sem aspas.
- `Children` é **lista**, e cada item tem **exatamente uma chave**: o nome do controle (T017).
- Chaves aceitas num controle nativo: `Control` (obrigatória), `Variant`, `MetadataKey`,
  `Layout`, `IsLocked`, `Group`, `Properties`, `Children`. Controle de terceiros exige
  `ComponentName` e `CanvasComponent` não aceita `Children`.
- `Group` é só organização no Studio: não cria hierarquia, não muda `Parent` nem posição.

### 3.3 A ordem de `Children` é o z-index

O primeiro filho fica no fundo; o último, por cima. Não existe propriedade `ZIndex`
([schema](https://raw.githubusercontent.com/microsoft/PowerApps-Tooling/refs/heads/master/schemas/pa-yaml/v3.0/pa.schema.yaml)).
Por isso o fim de `Children` de toda tela é: **conteúdo, modais, loading, toast** (T016).
Dentro de uma galeria, o primeiro filho é o fundo clicável da linha.

### 3.4 Toda propriedade começa com `=`

O schema tipa o valor como `^=.*` ou nulo. Motivos dados pela Microsoft: consistência com o
Excel; o `=` escapa a sintaxe do Power Fx para o YAML não tentar interpretá-la (`text: 1:00`
viraria minutos e segundos); e dá espaço para valor estático no futuro. O espaço entre `:` e `=`
é obrigatório
([Power Fx YAML formula grammar](https://learn.microsoft.com/en-us/power-platform/power-fx/yaml-formula-grammar)).

Destino: YAML colado.

```yaml
Controles:
  CertoTexto: ="Olá"
  CertoVazio: =
```

(O bloco acima é só ilustração das duas formas válidas; não é uma tela.)

Errado (validador: T002):

```yaml
# validador: ignorar
Text: "Olá"
```

### 3.5 `Control` e `Variant` não aceitam Power Fx

São metadados de instanciação ([Source code files](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml)).
`Control: =If(...)` é erro (T005).

## 4. Fórmulas de várias linhas

### 4.1 Use `|-`

`|-` remove a quebra final e é o que o Studio gera. `|` e `|+` são aceitos; **`>` dobra quebras
em espaços e destrói uma cadeia de comandos: nunca use**.

### 4.2 O `=` vai na primeira linha de conteúdo, não na do `|-`

Destino: YAML colado.

```yaml
ex-btn-atualizar:
  Control: Classic/Button@2.2.0
  Properties:
    OnSelect: |-
      =Set(varShowLoading, true);
      Set(varLoadingMessage, fxMsgLoadingDefault);
      Refresh(Pedido)
```

### 4.3 Comentários: `//` e `/* */`, nunca `#`

Comentário de linha do YAML (`#`) **não é preservado** pelo Studio. Dentro de um bloco `|-` um
`#` vira texto da fórmula e o Power Fx rejeita. Use `//` (preservado).
([Power Fx YAML formula grammar](https://learn.microsoft.com/en-us/power-platform/power-fx/yaml-formula-grammar))

### 4.4 Fórmula de uma linha: sem `#` e sem `: `

> "The number sign `#` and colon `:` aren't allowed anywhere in single-line formulas, even if
> they're in a quoted text string or identifier name. To use a number sign or colon, you must
> express the formula as a multiline formula." (mesma fonte)

Destino: YAML colado.

```yaml
Rotulos:
  CertoAspas: '="Unidade: " & varUnidade'
  CertoBloco: |-
    ="Pedido #" & varNumero
```

As aspas que resolvem são as do **YAML, em volta da fórmula inteira** (`'="Unidade: " & x'`);
aspas só em volta do texto, dentro de um valor que começa com `=`, não bastam: o valor continua
sendo um escalar simples e o `: ` quebra o parse (validador: T001). Um ` #` depois da fórmula, na mesma linha, é comentário YAML e trunca a fórmula em silêncio
(validador: T015).

## 5. Escape de texto

### 5.1 Record literal quebra em silêncio

`{Value: "Tab1"}` faz o YAML ler `Value:` como chave de mapa: a fórmula nunca roda.

Errado:

```yaml
# validador: ignorar
Default: ={Value: "Tab1"}
```

Certo (o mais seguro para fórmula longa é o bloco):

Destino: YAML colado.

```yaml
Padroes:
  AspasSimples: '={Value: "Tab1"}'
  Bloco: |-
    ={Value: "Tab1"}
```

Regra prática: se a fórmula contém `{`, `}` ou `: `, use aspas ou `|-`
([TechnicalGuide.md, plugin canvas-apps](https://github.com/microsoft/power-platform-skills/blob/main/plugins/canvas-apps/references/TechnicalGuide.md)).

### 5.2 Formas que o serializador gera (não escreva assim de propósito)

- `'=... '` (aspas simples): preserva o espaço final.
- `"=\r\n...\r\n..."` (aspas duplas com `\r\n`): usado quando a indentação interna não
  sobreviveria a um bloco. Funciona, mas é ilegível e concentra a pior lógica do app. Ao gerar
  código novo, sempre `|-`. `[verificado: projeto de referência]`

### 5.3 Identificadores com caractere especial

Aspas simples em volta de nome com espaço, hífen, ponto ou que começa com dígito; duas aspas
simples juntas para uma aspa no nome
([Operators and Identifiers](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/operators)).

Destino: YAML colado.

```yaml
Identificadores:
  Largura: ='xx-con-corpo'.Width
  Controle: ='xx-gal-pedidos'.AllItemsCount
  Aparencia: ='ButtonCanvas.Appearance'.Transparent
```

Referência a controle com hífen no nome **sempre** entre aspas simples. Sem aspas, `a-b` é uma
subtração.

### 5.4 Formato de data em minúsculas

`Text(x, "dd/mm/yyyy")` funciona; `"DD/MM/YYYY"` não.

## 6. Indentação e nomes

**2 espaços por nível, sem tabulação.** O ponto que mais quebra: o corpo de um item de lista
fica **4 colunas à direita do `-`**.

| Nível | `- nome:` | `Control:` | `Text:` |
|---|---|---|---|
| filho da tela | 6 | 10 | 12 |
| neto | 12 | 16 | 18 |
| bisneto | 18 | 22 | 24 |

Achatar a indentação é a causa mais comum de "não cola", sem mensagem útil (validador: T001
dá a linha).

- **Chave repetida é erro**, não sobrescrita silenciosa
  ([schema/doc](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml)):
  validador T012.
- **Nome de controle é único no app inteiro**
  ([pac canvas](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas)):
  validador T006. Colar bloco copiado de outra tela: renomeie **antes** (o Studio acrescenta
  `_1`, `_2`).
- Propriedades em ordem alfabética e sem repetir o padrão do controle: o Studio reordena e apaga
  o que é igual ao default na primeira colagem, poluindo o primeiro diff.
  `[verificado: projeto de referência]`

## 7. Como colar no Studio

**Copiar:** botão direito no controle > **View code** > **Copy code**.
**Colar:** botão direito na tela ou no controle-pai > **Paste code** (`Ctrl+V`).
O código é validado antes de criar o controle
([Use code view](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/code-view)).

| O que você entrega | Como aplicar |
|---|---|
| Bloco de controle(s), de `- nome:` em diante | Code view > Paste code, no controle-pai certo |
| Uma propriedade isolada | barra de fórmulas do controle (dialeto pt-BR) |
| `App.OnStart` e `App.Formulas` | digitar na barra do objeto App (dialeto pt-BR); **não há Code view do App** |

Limites oficiais: não dá para copiar nem ver o código do objeto App; não dá para editar no code
view; colar **cria** controle novo (para "editar", cole o novo, valide e apague o antigo); o
navegador precisa de permissão de área de transferência para `make.powerapps.com` (sem ela, o
`Ctrl+V` falha em silêncio). Sempre diga **qual das três vias** a entrega usa.

## 8. Controles e versões

### 8.1 Como ler `Tipo@versão`

Regex do schema: `^([A-Z][a-zA-Z0-9]*/)?[A-Z][a-zA-Z0-9]*(@\d+\.\d+\.\d+)?$`.

- `Classic/` é o namespace dos controles legados; o nome curto (`Button`, `TextInput`) foi
  reatribuído ao controle moderno (Fluent 2).
- A versão é opcional no schema e, sem ela, vale a mais recente. **Neste padrão ela é
  obrigatória** (decisão T2): a versão define como as propriedades são lidas, e o Studio recusa
  o bloco sem ela nos projetos de referência (validador: T004).
  `[verificado: projeto de referência]`
- A série `0.0.x` é a assinatura dos controles modernos; `1.x` é container e utilitário.
- O QAChecks do plugin da Microsoft manda **remover** o `@versão` (check 10). O Studio dos
  projetos de referência exporta e aceita **com** versão. A decisão do padrão é manter, e
  reescrever aquele check.

### 8.2 Versões em uso nos projetos de referência

Use a versão que **o seu app** já usa; esta tabela é o ponto de partida e o que o validador
reconhece como atestado.

| `Control:` | Uso |
|---|---|
| `Label@2.5.1` | todo texto, estático ou ligado |
| `Classic/Button@2.2.0` | botão, aba, cabeçalho de coluna, fundo de linha, forma arredondada |
| `GroupContainer@1.5.0` (`Variant: ManualLayout`) | card, modal, véu, agrupamento |
| `Gallery@2.15.0` (`Variant: BrowseLayout_Flexible_SocialFeed_ver5.0`) | listas |
| `Classic/TextInput@2.3.2` | filtro e formulário |
| `Classic/ComboBox@2.4.0` | seleção |
| `Classic/DatePicker@2.6.0` | datas |
| `Classic/CheckBox@2.1.0` | seleção de linha |
| `Classic/Toggle@2.1.0`, `Classic/Icon@2.5.0` | alternador, ícone vetorial |
| `Rectangle@2.3.0` | divisor e faixa (sem `Radius*`) |
| `Image@2.2.3` | logo e foto |
| `Timer@2.1.0` | toast, polling, debounce |
| `Spinner@1.4.6` | loading |
| `HtmlViewer@2.1.0` | HTML formatado (mais caro que `Label`) |
| `Button@0.0.45`, `Text@0.0.51`, `CheckBox@0.0.30`, `ModernTextInput@1.1.1`, `NumberInput@2.9.12`, `TextInput@0.0.54` | ilhas modernas |

A lista de controles de primeira parte é aberta (`ControlTypeId-1P-controls-enum: true`): o
catálogo de tipos e versões **não está versionado em lugar nenhum**. A forma canônica de
descobrir é o MCP server oficial (§11).

### 8.3 Propriedades atestadas por controle

Levantadas dos apps reais, por frequência. **Propriedade fora desta lista não entra sem teste no
Studio**: PA2108 recusa o bloco inteiro, não só a linha. Recusas confirmadas:
[propriedades-inexistentes.md](propriedades-inexistentes.md).

| Controle | Propriedades atestadas |
|---|---|
| `Label@2.5.1` | `Text`, `Font`, `Width`, `Height`, `Color`, `X`, `Y`, `Size`, `BorderColor`, `Align`, `FontWeight`, `Visible`, `OnSelect`, `TabIndex`, `Fill`, `PaddingBottom`, `PaddingLeft`, `VerticalAlign`, `AutoHeight`, `Tooltip`, `Underline`, `DisplayMode`, `Wrap` |
| `Classic/Button@2.2.0` | `Fill`, `Text`, `Color`, `Width`, `Height`, `Font`, `FontWeight`, `Size`, `X`, `Y`, `BorderColor`, `BorderThickness`, `Hover*` e `Pressed*` (`Fill`, `Color`, `BorderColor`), `Disabled*` (`Fill`, `Color`, `BorderColor`), `OnSelect`, `DisplayMode`, `Visible`, `TabIndex`, `AutoDisableOnSelect`, `Tooltip`, `Radius*`, `Underline` |
| `GroupContainer@1.5.0` | `Height`, `Width`, `X`, `Y`, `Fill`, `BorderColor`, `BorderThickness`, `DropShadow`, `Radius*`, `Visible` |
| `Gallery@2.15.0` | `Items`, `Height`, `Width`, `X`, `Y`, `TemplateSize`, `TemplatePadding`, `MaxTemplateSize`, `BorderColor`, `BorderThickness`, `Visible`, `TabIndex` |
| `Classic/ComboBox@2.4.0` | `Items`, `DisplayFields`, `SearchFields`, `SelectMultiple`, `InputTextPlaceholder`, `IsSearchable`, `OnChange`, `Color`, `Font`, `Fill`, `BorderColor`, `FocusedBorderColor`, `HoverBorderColor`, `SelectionColor`, `SelectionFill`, `Chevron*`, `Width`, `Height`, `X`, `Y`, `Visible` |
| `Classic/TextInput@2.3.2` | `Default`, `HintText`, `Font`, `Size`, `Color`, `BorderColor`, `FocusedBorderColor`, `HoverBorderColor`, `OnChange`, `Format`, `Mode`, `Disabled*`, `Hover*`, `Radius*`, `DelayOutput`, `TabIndex`, `Width`, `Height`, `X`, `Y`, `Visible` |
| `Classic/DatePicker@2.6.0` | `DefaultDate`, `Format`, `OnChange`, `IconBackground`, `IconFill`, `BorderColor`, `FocusedBorderColor`, `Font`, `InputTextPlaceholder`, `DisplayMode`, `Width`, `Height`, `X`, `Y`, `Visible`, `TabIndex` |
| `Classic/CheckBox@2.1.0` | `Default`, `Text`, `OnCheck`, `OnUncheck`, `OnSelect`, `CheckboxBorderColor`, `CheckmarkFill`, `Font`, `BorderColor`, `HoverColor`, `Width`, `Height`, `X`, `Y`, `Visible`, `TabIndex` |
| `Timer@2.1.0` | `Duration`, `OnTimerEnd`, `Start`, `Repeat`, `Reset`, `Visible`, `Height`, `Width`, `X`, `Y` |
| `Rectangle@2.3.0` | `Fill`, `Height`, `Width`, `X`, `Y`, `BorderColor`, `BorderStyle`, `DisplayMode`, `Visible`, `OnSelect` |
| `Image@2.2.3` | `Image`, `BorderColor`, `Height`, `Width`, `X`, `Y`, `OnSelect`, `HoverFill`, `Tooltip`, `TabIndex`, `Visible`, `DisplayMode` |
| `Spinner@1.4.6` | `Height`, `Width`, `X`, `Y` |
| `Classic/Icon@2.5.0` | `Icon`, `Color`, `BorderColor`, `Height`, `Width`, `X`, `Y`, `OnSelect`, `Visible` |
| `HtmlViewer@2.1.0` | `HtmlText`, `BorderColor`, `Color`, `Font`, `Height`, `Width`, `X`, `Y`, `OnSelect`, `PaddingTop`, `Visible` |

Na tela: `Fill`, `Height`, `Width`, `LoadingSpinnerColor`, `OnVisible`. `X` e `Y` só têm efeito
em `ManualLayout`. Regra anti-alucinação do plugin oficial da Microsoft: *"If you are uncertain
whether a property exists for a control, it does not exist."*

A documentação do Learn lista propriedades que o Studio **recusa** no YAML desses controles (ex.:
`FocusedBorderThickness`). Em conflito, vale o que o Studio aceita.

### 8.4 `GroupContainer` não tem `OnSelect`

Card clicável: `Classic/Button@2.2.0` transparente (`Fill: =fxColorTransparent`,
`Text: =""`) como **primeiro** filho da galeria, ocupando a linha
([TechnicalGuide.md](https://github.com/microsoft/power-platform-skills/blob/main/plugins/canvas-apps/references/TechnicalGuide.md)).
O padrão está em [ux-componentes.md](ux-componentes.md) §Galeria.

## 9. Layout: ManualLayout e AutoLayout

Padrão deste kit: **ManualLayout + controles Classic, canvas fixo 1920x1080** (decisão T1: foi o
que os apps de referência provaram no Studio). AutoLayout e controles modernos ficam fora até um projeto
prová-los. Responsividade vem de token (`fxIsCompact`), não de AutoLayout.

Centralização em `ManualLayout` é aritmética:

Destino: YAML colado.

```yaml
Posicao:
  X: =(Parent.Width - Self.Width) / 2
  Y: =(Parent.Height - Self.Height) / 2
```

Se um projeto optar por AutoLayout, os detectores do
[QAChecks.md](https://github.com/microsoft/power-platform-skills/blob/main/plugins/canvas-apps/references/QAChecks.md)
passam a valer: `LayoutMinWidth`/`LayoutMinHeight` explícitos em `=0` (o default 250/100 empurra
irmãos), `AlignInContainer`, `FillPortions` explícito, filho com `FillPortions: =1` dentro de
container de rolagem (corta em vez de rolar) e `Height` explícito junto de `FillPortions: =0`.
Dois valem em qualquer layout: **`Wrap: =false`** em todo `Label` de uma linha (aba, badge, KPI,
cabeçalho) e **padding explícito nos 4 lados** do `Label` (o padrão 5 desalinha). `Wrap` e
`PaddingLeft` estão atestados em `Label@2.5.1`; `PaddingTop` e `PaddingRight`, `[não verificado]`:
teste num bloco pequeno antes de espalhar.

## 10. Checklist antes de entregar YAML

- [ ] Dialeto do destino: `,` e `;` no YAML; nunca `;;`.
- [ ] `: =` em toda propriedade (espaço após os dois-pontos).
- [ ] Indentação de 2 espaços; corpo do item de lista +4 do `-`.
- [ ] `Control: Tipo@x.y.z` com a versão do app; nenhuma propriedade fora de §8.3 sem teste.
- [ ] Fórmula de várias linhas em `|-`, `=` na primeira linha de conteúdo, `//` para comentário.
- [ ] Sem `#` nem `: ` em fórmula de linha única; record literal entre aspas ou em `|-`.
- [ ] Nome `<prefixo-tela>-<tipo>-<módulo>-<elemento>`, kebab-case, único no app.
- [ ] Fim de `Children`: conteúdo, modais, loading, toast.
- [ ] Cor, fonte e medida por `fx*`; nenhum `RGBA(` literal.
- [ ] Galeria: `Items` delegável (ver [delegacao.md](delegacao.md)), `TemplateSize` diferente de 0,
      estado vazio por `AllItemsCount`.
- [ ] Classificado em uma das três vias de colagem (§7).

## 11. Validação

O schema **não valida nome de propriedade**: `Properties` aceita qualquer chave com valor
`^=.*`. Quem recusa propriedade inexistente é o Studio, na colagem (PA2108).

1. `python <pasta-da-skill>/scripts/validar-telas.py <arquivo>`: sintaxe, dialeto, nomes, PA2108 conhecido.
2. **Colar no Studio.** O validador não substitui isto.
3. Opcional, preview: o **MCP server oficial de authoring Canvas** lista e descreve controles e
   propriedades válidos (`list_controls`, `describe_control`), valida o YAML e sincroniza com a
   sessão de coautoria. Exige .NET SDK 10+ e Coauthoring ligado em *Settings > Updates*
   ([Create and edit canvas apps with AI code generation tools](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-canvas-external-tools)).
   `[não verificado: disponibilidade no seu tenant]`

## 12. Fontes

- [Source code files for canvas apps (pa.yaml)](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml)
- [Power Fx YAML formula grammar](https://learn.microsoft.com/en-us/power-platform/power-fx/yaml-formula-grammar)
- [Use code view for canvas app controls](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/code-view)
- [Global support in Power Fx](https://learn.microsoft.com/en-us/power-platform/power-fx/global)
- [pac canvas](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas)
- [Schema pa.yaml v3.0](https://raw.githubusercontent.com/microsoft/PowerApps-Tooling/refs/heads/master/schemas/pa-yaml/v3.0/pa.schema.yaml)

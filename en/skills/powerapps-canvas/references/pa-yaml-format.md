# `.pa.yaml` format: grammar, escaping, indentation and pasting

How to write YAML that Power Apps Studio accepts when pasted. For Power Fx inside the properties:
[powerfx-essentials.md](powerfx-essentials.md). For ready-made blocks (modal, toast, gallery):
[ux-components.md](ux-components.md). For the whole screen: [screen-template.md](../assets/screen-template.md).

## Contents

1. [Where the YAML lives](#1-where-the-yaml-lives)
2. [Dialect: the YAML is invariant](#2-dialect-the-yaml-is-invariant)
3. [Grammar](#3-grammar)
4. [Multi-line formulas](#4-multi-line-formulas)
5. [Text escaping](#5-text-escaping)
6. [Indentation and names](#6-indentation-and-names)
7. [How to paste into Studio](#7-how-to-paste-into-studio)
8. [Controls and versions](#8-controls-and-versions)
9. [Layout: ManualLayout and AutoLayout](#9-layout-manuallayout-and-autolayout)
10. [Checklist before delivering YAML](#10-checklist-before-delivering-yaml)
11. [Validation](#11-validation)
12. [Sources](#12-sources)

---

## 1. Where the YAML lives

A Canvas app is a `.msapp` (zip). Only the `*.pa.yaml` files in `\Src` are source code: one per
screen, plus `App.pa.yaml` and one per component. The package's `.json` files are not stable
between saving and opening and do not go into version control.
([Source code files for canvas apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml))

Extract:

Destination: terminal (PowerShell), not Power Fx.

```powershell
pac canvas list
pac canvas download --name "App Name" --extract-to-directory .\src --overwrite
```

`pac canvas pack` and `unpack` are deprecated; the `Experimental` layout (`*.fx.yaml`) is
deprecated and will be removed. To version with external editing and merge, the supported route is the Power Platform **Git Integration**
([pac canvas](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas),
[Git Integration](https://learn.microsoft.com/en-us/power-platform/alm/git-integration/overview)).

In reference projects the screens are kept as `.md` with **plain YAML** (no fence). The validator
reads that format whole; see [SKILL.md](../SKILL.md) §Scripts.

## 2. Dialect: the YAML is invariant

The file on disk is saved in the invariant locale, whatever the language of the person editing
([Global support in Power Fx](https://learn.microsoft.com/en-us/power-platform/power-fx/global)).

| Destination | Argument | Chain | Decimal |
|---|---|---|---|
| **Pasted YAML** (`.pa.yaml`, Code view) | `,` | `;` | `.` |
| Studio **formula bar** in en-US (includes `App.OnStart` and `App.Formulas`) | `,` | `;` | `.` |

A pt-BR Studio formula bar uses `;` between arguments, `;;` to chain and `,` as the decimal.
Full rule in [default-decisions.md](../../power-platform/references/default-decisions.md) §3.
**Never write `;;` in a YAML file** (validator: T007). After pasting, a pt-BR Studio
shows `;` and `;;` in the bar: that is expected, do not "fix" it.

## 3. Grammar

### 3.1 Document structure

Five top-level keys and only those (`additionalProperties: false` in the schema
[pa.schema.yaml v3.0](https://raw.githubusercontent.com/microsoft/PowerApps-Tooling/refs/heads/master/schemas/pa-yaml/v3.0/pa.schema.yaml)):
`App`, `Screens`, `ComponentDefinitions`, `DataSources`, `EditorState`. Validator: T022.

### 3.2 Screen and control

Destination: pasted YAML (`,` and `;`).

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
            Text: ="Example"
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
                  Text: ="Content"
```

- `Screens` accepts, per screen, only `Properties` and `Children`. A screen name with a space or
  an accent works without quotes.
- `Children` is a **list**, and each item has **exactly one key**: the control name (T017).
- Keys accepted on a native control: `Control` (required), `Variant`, `MetadataKey`,
  `Layout`, `IsLocked`, `Group`, `Properties`, `Children`. A third-party control requires
  `ComponentName` and `CanvasComponent` does not accept `Children`.
- `Group` is only organization in Studio: it does not create hierarchy, does not change `Parent`
  or position.

### 3.3 The order of `Children` is the z-index

The first child sits at the back; the last, on top. There is no `ZIndex` property
([schema](https://raw.githubusercontent.com/microsoft/PowerApps-Tooling/refs/heads/master/schemas/pa-yaml/v3.0/pa.schema.yaml)).
So the end of every screen's `Children` is: **content, modals, loading, toast** (T016).
Inside a gallery, the first child is the row's clickable background.

### 3.4 Every property starts with `=`

The schema types the value as `^=.*` or null. Reasons given by Microsoft: consistency with
Excel; the `=` escapes Power Fx syntax so YAML does not try to interpret it (`text: 1:00`
would become minutes and seconds); and it leaves room for a static value in the future. The space
between `:` and `=` is mandatory
([Power Fx YAML formula grammar](https://learn.microsoft.com/en-us/power-platform/power-fx/yaml-formula-grammar)).

Destination: pasted YAML.

```yaml
Controles:
  CertoTexto: ="Hello"
  CertoVazio: =
```

(The block above only illustrates the two valid forms; it is not a screen.)

Wrong (validator: T002):

```yaml
# validador: ignorar
Text: "Hello"
```

### 3.5 `Control` and `Variant` do not accept Power Fx

They are instantiation metadata ([Source code files](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml)).
`Control: =If(...)` is an error (T005).

## 4. Multi-line formulas

### 4.1 Use `|-`

`|-` strips the final line break and is what Studio generates. `|` and `|+` are accepted; **`>` folds line breaks
into spaces and destroys a command chain: never use it**.

### 4.2 The `=` goes on the first content line, not on the `|-` line

Destination: pasted YAML.

```yaml
ex-btn-atualizar:
  Control: Classic/Button@2.2.0
  Properties:
    OnSelect: |-
      =Set(varShowLoading, true);
      Set(varLoadingMessage, fxMsgLoadingDefault);
      Refresh(Pedido)
```

### 4.3 Comments: `//` and `/* */`, never `#`

The YAML line comment (`#`) is **not preserved** by Studio. Inside a `|-` block a
`#` becomes formula text and Power Fx rejects it. Use `//` (preserved).
([Power Fx YAML formula grammar](https://learn.microsoft.com/en-us/power-platform/power-fx/yaml-formula-grammar))

### 4.4 Single-line formula: no `#` and no `: `

> "The number sign `#` and colon `:` aren't allowed anywhere in single-line formulas, even if
> they're in a quoted text string or identifier name. To use a number sign or colon, you must
> express the formula as a multiline formula." (same source)

Destination: pasted YAML.

```yaml
Rotulos:
  CertoAspas: '="Unit: " & varUnidade'
  CertoBloco: |-
    ="Order #" & varNumero
```

The quotes that fix it are the **YAML ones, around the whole formula** (`'="Unit: " & x'`);
quotes only around the text, inside a value that starts with `=`, are not enough: the value is still
a plain scalar and the `: ` breaks the parse (validator: T001). A ` #` after the formula, on the same line, is a YAML comment and silently truncates the formula
(validator: T015).

## 5. Text escaping

### 5.1 A record literal breaks silently

`{Value: "Tab1"}` makes YAML read `Value:` as a map key: the formula never runs.

Wrong:

```yaml
# validador: ignorar
Default: ={Value: "Tab1"}
```

Right (the safest for a long formula is the block):

Destination: pasted YAML.

```yaml
Padroes:
  AspasSimples: '={Value: "Tab1"}'
  Bloco: |-
    ={Value: "Tab1"}
```

Rule of thumb: if the formula contains `{`, `}` or `: `, use quotes or `|-`
([TechnicalGuide.md, canvas-apps plugin](https://github.com/microsoft/power-platform-skills/blob/main/plugins/canvas-apps/references/TechnicalGuide.md)).

### 5.2 Forms the serializer generates (do not write them on purpose)

- `'=... '` (single quotes): preserves the trailing space.
- `"=\r\n...\r\n..."` (double quotes with `\r\n`): used when the inner indentation would not
  survive a block. It works, but it is unreadable and concentrates the worst logic of the app. When generating
  new code, always `|-`. `[verified: reference project]`

### 5.3 Identifiers with a special character

Single quotes around a name with a space, hyphen, period or that starts with a digit; two single
quotes together for a quote inside the name
([Operators and Identifiers](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/operators)).

Destination: pasted YAML.

```yaml
Identificadores:
  Largura: ='xx-con-corpo'.Width
  Controle: ='xx-gal-pedidos'.AllItemsCount
  Aparencia: ='ButtonCanvas.Appearance'.Transparent
```

A reference to a control with a hyphen in its name **always** goes in single quotes. Without quotes, `a-b` is a
subtraction.

### 5.4 Lowercase date format

`Text(x, "mm/dd/yyyy")` works; `"MM/DD/YYYY"` does not.

## 6. Indentation and names

**2 spaces per level, no tabs.** The point that breaks most: the body of a list item
sits **4 columns to the right of the `-`**.

| Level | `- name:` | `Control:` | `Text:` |
|---|---|---|---|
| child of the screen | 6 | 10 | 12 |
| grandchild | 12 | 16 | 18 |
| great-grandchild | 18 | 22 | 24 |

Flattening the indentation is the most common cause of "won't paste", with no useful message (validator: T001
gives the line).

- **A repeated key is an error**, not a silent overwrite
  ([schema/doc](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml)):
  validator T012.
- **A control name is unique across the whole app**
  ([pac canvas](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas)):
  validator T006. Pasting a block copied from another screen: rename **before** (Studio appends
  `_1`, `_2`).
- Properties in alphabetical order and without repeating the control's default: Studio reorders and deletes
  whatever equals the default on the first paste, polluting the first diff.
  `[verified: reference project]`

## 7. How to paste into Studio

**Copy:** right-click the control > **View code** > **Copy code**.
**Paste:** right-click the screen or the parent control > **Paste code** (`Ctrl+V`).
The code is validated before the control is created
([Use code view](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/code-view)).

| What you deliver | How to apply |
|---|---|
| Control block(s), from `- name:` onward | Code view > Paste code, on the right parent control |
| A single property | the control's formula bar (en-US dialect) |
| `App.OnStart` and `App.Formulas` | type into the App object's bar (en-US dialect); **there is no Code view for App** |

Official limits: you cannot copy or view the code of the App object; you cannot edit in
code view; pasting **creates** a new control (to "edit", paste the new one, validate and delete the old one); the
browser needs clipboard permission for `make.powerapps.com` (without it,
`Ctrl+V` fails silently). Always state **which of the three ways** the delivery uses.

## 8. Controls and versions

### 8.1 How to read `Type@version`

Schema regex: `^([A-Z][a-zA-Z0-9]*/)?[A-Z][a-zA-Z0-9]*(@\d+\.\d+\.\d+)?$`.

- `Classic/` is the namespace of the legacy controls; the short name (`Button`, `TextInput`) was
  reassigned to the modern control (Fluent 2).
- The version is optional in the schema and, without it, the latest applies. **In this standard it is
  mandatory** (decision T2): the version defines how properties are read, and Studio rejects
  the block without it in the reference projects (validator: T004).
  `[verified: reference project]`
- The `0.0.x` series is the signature of the modern controls; `1.x` is container and utility.
- The Microsoft plugin's QAChecks says to **remove** the `@version` (check 10). The Studio of the
  reference projects exports and accepts it **with** the version. The standard's decision is to keep it, and
  rewrite that check.

### 8.2 Versions in use in the reference projects

Use the version **your app** already uses; this table is the starting point and what the validator
recognizes as attested.

| `Control:` | Use |
|---|---|
| `Label@2.5.1` | all text, static or bound |
| `Classic/Button@2.2.0` | button, tab, column header, row background, rounded shape |
| `GroupContainer@1.5.0` (`Variant: ManualLayout`) | card, modal, scrim, grouping |
| `Gallery@2.15.0` (`Variant: BrowseLayout_Flexible_SocialFeed_ver5.0`) | lists |
| `Classic/TextInput@2.3.2` | filter and form |
| `Classic/ComboBox@2.4.0` | selection |
| `Classic/DatePicker@2.6.0` | dates |
| `Classic/CheckBox@2.1.0` | row selection |
| `Classic/Toggle@2.1.0`, `Classic/Icon@2.5.0` | toggle, vector icon |
| `Rectangle@2.3.0` | divider and strip (no `Radius*`) |
| `Image@2.2.3` | logo and photo |
| `Timer@2.1.0` | toast, polling, debounce |
| `Spinner@1.4.6` | loading |
| `HtmlViewer@2.1.0` | formatted HTML (more expensive than `Label`) |
| `Button@0.0.45`, `Text@0.0.51`, `CheckBox@0.0.30`, `ModernTextInput@1.1.1`, `NumberInput@2.9.12`, `TextInput@0.0.54` | modern islands |

The list of first-party controls is open (`ControlTypeId-1P-controls-enum: true`): the
catalog of types and versions **is not versioned anywhere**. The canonical way to
find out is the official MCP server (§11).

### 8.3 Attested properties per control

Collected from real apps, by frequency. **A property outside this list does not go in without a test in
Studio**: PA2108 rejects the whole block, not just the line. Confirmed rejections:
[nonexistent-properties.md](nonexistent-properties.md).

| Control | Attested properties |
|---|---|
| `Label@2.5.1` | `Text`, `Font`, `Width`, `Height`, `Color`, `X`, `Y`, `Size`, `BorderColor`, `Align`, `FontWeight`, `Visible`, `OnSelect`, `TabIndex`, `Fill`, `PaddingBottom`, `PaddingLeft`, `VerticalAlign`, `AutoHeight`, `Tooltip`, `Underline`, `DisplayMode`, `Wrap` |
| `Classic/Button@2.2.0` | `Fill`, `Text`, `Color`, `Width`, `Height`, `Font`, `FontWeight`, `Size`, `X`, `Y`, `BorderColor`, `BorderThickness`, `Hover*` and `Pressed*` (`Fill`, `Color`, `BorderColor`), `Disabled*` (`Fill`, `Color`, `BorderColor`), `OnSelect`, `DisplayMode`, `Visible`, `TabIndex`, `AutoDisableOnSelect`, `Tooltip`, `Radius*`, `Underline` |
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

On the screen: `Fill`, `Height`, `Width`, `LoadingSpinnerColor`, `OnVisible`. `X` and `Y` only take effect
in `ManualLayout`. Anti-hallucination rule from Microsoft's official plugin: *"If you are uncertain
whether a property exists for a control, it does not exist."*

The Learn documentation lists properties that Studio **rejects** in the YAML of these controls (e.g.
`FocusedBorderThickness`). In a conflict, what Studio accepts wins.

### 8.4 `GroupContainer` has no `OnSelect`

Clickable card: a transparent `Classic/Button@2.2.0` (`Fill: =fxColorTransparent`,
`Text: =""`) as the **first** child of the gallery, filling the row
([TechnicalGuide.md](https://github.com/microsoft/power-platform-skills/blob/main/plugins/canvas-apps/references/TechnicalGuide.md)).
The pattern is in [ux-components.md](ux-components.md) §Gallery.

## 9. Layout: ManualLayout and AutoLayout

This kit's standard: **ManualLayout + Classic controls, fixed 1920x1080 canvas** (decision T1: it was
what the reference apps proved in Studio). AutoLayout and modern controls stay out until a project
proves them. Responsiveness comes from a token (`fxIsCompact`), not from AutoLayout.

Centering in `ManualLayout` is arithmetic:

Destination: pasted YAML.

```yaml
Posicao:
  X: =(Parent.Width - Self.Width) / 2
  Y: =(Parent.Height - Self.Height) / 2
```

If a project opts for AutoLayout, the detectors in
[QAChecks.md](https://github.com/microsoft/power-platform-skills/blob/main/plugins/canvas-apps/references/QAChecks.md)
start to apply: explicit `LayoutMinWidth`/`LayoutMinHeight` at `=0` (the 250/100 default pushes
siblings), `AlignInContainer`, explicit `FillPortions`, a child with `FillPortions: =1` inside a
scrolling container (it clips instead of scrolling) and an explicit `Height` together with `FillPortions: =0`.
Two apply in any layout: **`Wrap: =false`** on every single-line `Label` (tab, badge, KPI,
header) and **explicit padding on all 4 sides** of the `Label` (the default 5 misaligns). `Wrap` and
`PaddingLeft` are attested on `Label@2.5.1`; `PaddingTop` and `PaddingRight`, `[unverified]`:
test in a small block before spreading.

## 10. Checklist before delivering YAML

- [ ] Destination dialect: `,` and `;` in YAML; never `;;`.
- [ ] `: =` on every property (space after the colon).
- [ ] 2-space indentation; list item body +4 from the `-`.
- [ ] `Control: Type@x.y.z` with the app's version; no property outside §8.3 without a test.
- [ ] Multi-line formula in `|-`, `=` on the first content line, `//` for comments.
- [ ] No `#` or `: ` in a single-line formula; record literal in quotes or in `|-`.
- [ ] Name `<screen-prefix>-<type>-<module>-<element>`, kebab-case, unique in the app.
- [ ] End of `Children`: content, modals, loading, toast.
- [ ] Color, font and size by `fx*`; no literal `RGBA(`.
- [ ] Gallery: delegable `Items` (see [delegation.md](delegation.md)), `TemplateSize` other than 0,
      empty state by `AllItemsCount`.
- [ ] Classified into one of the three ways of pasting (§7).

## 11. Validation

The schema **does not validate property names**: `Properties` accepts any key with a value
`^=.*`. What rejects a nonexistent property is Studio, on paste (PA2108).

1. `python <skill-folder>/scripts/validar-telas.py <file>`: syntax, dialect, names, known PA2108.
2. **Paste into Studio.** The validator does not replace this.
3. Optional, preview: the **official Canvas authoring MCP server** lists and describes valid controls and
   properties (`list_controls`, `describe_control`), validates the YAML and syncs with the
   co-authoring session. Requires .NET SDK 10+ and Coauthoring turned on in *Settings > Updates*
   ([Create and edit canvas apps with AI code generation tools](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-canvas-external-tools)).
   `[unverified: availability in your tenant]`

## 12. Sources

- [Source code files for canvas apps (pa.yaml)](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml)
- [Power Fx YAML formula grammar](https://learn.microsoft.com/en-us/power-platform/power-fx/yaml-formula-grammar)
- [Use code view for canvas app controls](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/code-view)
- [Global support in Power Fx](https://learn.microsoft.com/en-us/power-platform/power-fx/global)
- [pac canvas](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas)
- [Schema pa.yaml v3.0](https://raw.githubusercontent.com/microsoft/PowerApps-Tooling/refs/heads/master/schemas/pa-yaml/v3.0/pa.schema.yaml)

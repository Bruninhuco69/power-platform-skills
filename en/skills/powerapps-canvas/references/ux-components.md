# UX component catalog

Canonical ManualLayout blocks + Classic controls, ready to paste, with the `xx` prefix to be
replaced by the screen's prefix. Fixed against the two most common errors: **dialect** (all
YAML here uses `,` and `;`, never `;;`) and **PA2108** (no property that Studio rejects:
see [nonexistent-properties.md](nonexistent-properties.md)). Color, font and size come from a
token ([design-tokens.md](design-tokens.md), values in
[app-formulas-tokens.md](../assets/app-formulas-tokens.md)); the whole assembled screen is in
[screen-template.md](../assets/screen-template.md).

Each block has its canonical, complete and validated version in [INDEX.md](../assets/components/INDEX.md): start
there and use this reference for the rule and the why ([field-lessons.md](field-lessons.md)).

## Contents

1. [Common rules](#1-common-rules)
2. [Screen header](#2-screen-header)
3. [KPI card](#3-kpi-card)
4. [Tabs](#4-tabs)
5. [Filters](#5-filters)
6. [Gallery with column header](#6-gallery-with-column-header)
7. [Action badge](#7-action-badge)
8. [Buttons](#8-buttons)
9. [Modal, loading and toast](ux-feedback.md)
12. [Bulk selection](#12-bulk-selection)
13. [States: empty, truncated, error, disabled](#13-states-empty-truncated-error-disabled)
14. [Form: required and per-field error](#14-form-required-and-per-field-error)
15. [Z-order](#15-z-order)

---

## 1. Common rules

- **Destination of every block**: pasted YAML (Code view > Paste code), `,` between arguments, `;`
  chains. Rename `xx` before pasting: a control name is unique across the whole app.
- **Shared state contract**: `varShowLoading` and `varLoadingMessage` (loading);
  `varShowToast`, `varToastType` (`success`, `warning`, `error`) and `varToastMessage` (toast);
  `varMostrar<Acao>` (one modal). All of them are created in `OnStart`.
- **A single type family** (`fxFont`), one palette, one modal geometry:
  changing the token changes every screen.
- **Rounded-corner rectangle**: `Rectangle` and several inputs **do not have** `Radius*`. The
  standard for a rounded decorative shape is `Classic/Button@2.2.0` with
  `DisplayMode: =DisplayMode.Disabled` and `DisabledFill` (a disabled button also stays out of the
  tab order).
- **No emoji as semantics** (`✅ Yes`, `❌ Cancel`): it does not scale for screen readers and blocks
  translation. An icon is a separate control; a label is text. (The `✓`, `!` and `✕` of the toast are
  decorative glyphs next to the text, never the text.)
- **Green is state, never action**; a destructive action is always `fxColorError`.
- Before using a new property on a control type, look for it on a control of the **same type**
  already used in the app.

## 2. Screen header

On every screen, no exception; title, user and divider. Variation without a logo or with a logo: replace the
title `X` with `fxLayoutMargin + <logo width>`.

```yaml
- xx-con-header:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorSurface
      Height: =100
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-lbl-header-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =60
            Size: =fxFontSizeTitle
            Text: ="Screen title"
            VerticalAlign: =VerticalAlign.Middle
            Width: =700
            X: =fxLayoutMargin
            Y: =20
      - xx-lbl-header-usuario:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Right
            Color: =fxColorTextSecondary
            Font: =fxFont
            Height: =24
            Size: =fxFontSizeBody
            Text: =User().FullName
            Width: =320
            X: =Parent.Width - 420
            Y: =30
      - xx-rec-header-divisor:
          Control: Rectangle@2.3.0
          Properties:
            BorderStyle: =BorderStyle.None
            Fill: =fxColorDivider
            Height: =1
            Width: =Parent.Width
            X: =0
            Y: =99
```

Clock in the header: use a variable updated by a timer; **never `Now()` directly** (volatile,
re-evaluates on every recalculation). Header position: pick **one** (left or centered) per
app; it is a divergence that costs moving the whole strip to fix later.

## 3. KPI card

A row of counters right below the header; at most 5 or 6 cards. `X` always by formula
(`base + (fxKPIWidth + fxLayoutGutter) * n`), never typed. The value comes from a **counter variable**
(`varPedidoAbertos`, recalculated in `OnVisible` and after every write: a named formula does not read
`varUnidadeFiltro`), never from a query in a UI property
([performance.md](performance.md) §10). A count over SQL shows the ceiling
([delegation.md](delegation.md) §3). Title colors: a `fxBadge*` pair of the same hue (dark text
on pastel, contrast checked).

```yaml
- xx-con-kpi-abertos:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorBorder
      DropShadow: =DropShadow.Regular
      Fill: =fxColorSurface
      Height: =fxKPIHeight
      RadiusBottomLeft: =fxModalRadius
      RadiusBottomRight: =fxModalRadius
      RadiusTopLeft: =fxModalRadius
      RadiusTopRight: =fxModalRadius
      Width: =fxKPIWidth
      X: =fxLayoutMargin + (fxKPIWidth + fxLayoutGutter) * 0
      Y: =110
    Children:
      - xx-lbl-kpi-abertos-titulo:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxBadgeInfoText
            Fill: =fxBadgeInfoBg
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =fxKPITitleHeight
            Size: =fxFontSizeKPITitle
            Text: ="Open"
            VerticalAlign: =VerticalAlign.Middle
            Width: =Parent.Width
            X: =0
            Y: =0
      - xx-lbl-kpi-abertos-valor:
          Control: Label@2.5.1
          Properties:
            Align: =Align.Center
            Color: =fxColorTextPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Bold
            Height: =fxKPIValueHeight
            Size: =fxFontSizeKPI
            Text: =If(varPedidoAbertos >= fxLimiteLinhas, fxTxtTeto, Text(varPedidoAbertos, "[$-en-US]#,##0"))
            VerticalAlign: =VerticalAlign.Middle
            Width: =Parent.Width
            X: =0
            Y: =fxKPITitleHeight
```

## 4. Tabs

Button + stroke rectangle; the active tab has an `fxColorSurface` fill, bold text and a 3 px stroke. Up to
4 data sets on the same screen. **Official limitation**: a tab made of a button and a rectangle is not
accessible; the only accessible pattern is the modern Tab list control
([Accessibility limitations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessible-apps-limitations)).
The kit's decision (T1) is to keep Classic; the migration is an item in [accessibility.md](accessibility.md).
The active and inactive tab **must not** have the same `Fill`: a difference only in text color and a
3 px stroke is weak.

```yaml
- xx-btn-tab-abertos:
    Control: Classic/Button@2.2.0
    Properties:
      AutoDisableOnSelect: =false
      BorderThickness: =0
      Color: =If(varXXTab = 1, fxColorPrimary, fxColorTextSecondary)
      Fill: =If(varXXTab = 1, fxColorSurface, fxColorTabInactive)
      Font: =fxFont
      FontWeight: =If(varXXTab = 1, FontWeight.Bold, FontWeight.Semibold)
      Height: =46
      HoverColor: =fxColorPrimary
      HoverFill: =fxColorSurface
      OnSelect: =Set(varXXTab, 1)
      PressedColor: =fxColorPrimary
      PressedFill: =fxColorSurface
      RadiusBottomLeft: =0
      RadiusBottomRight: =0
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxFontSizeFilter
      TabIndex: =0
      Text: ="Open (" & varPedidoAbertos & ")"
      Width: =350
      X: =fxLayoutMargin
      Y: =252
- xx-shp-tab-abertos-traco:
    Control: Rectangle@2.3.0
    Properties:
      BorderStyle: =BorderStyle.None
      Fill: =If(varXXTab = 1, fxColorPrimary, fxColorTransparent)
      Height: =3
      Width: =350
      X: =fxLayoutMargin
      Y: =294
- xx-btn-tab-encerrados:
    Control: Classic/Button@2.2.0
    Properties:
      AutoDisableOnSelect: =false
      BorderThickness: =0
      Color: =If(varXXTab = 2, fxColorPrimary, fxColorTextSecondary)
      Fill: =If(varXXTab = 2, fxColorSurface, fxColorTabInactive)
      Font: =fxFont
      FontWeight: =If(varXXTab = 2, FontWeight.Bold, FontWeight.Semibold)
      Height: =46
      HoverColor: =fxColorPrimary
      HoverFill: =fxColorSurface
      OnSelect: =Set(varXXTab, 2)
      PressedColor: =fxColorPrimary
      PressedFill: =fxColorSurface
      RadiusBottomLeft: =0
      RadiusBottomRight: =0
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxFontSizeFilter
      TabIndex: =0
      Text: ="Completed (" & varPedidoEncerrados & ")"
      Width: =350
      X: =fxLayoutMargin + 358
      Y: =252
- xx-shp-tab-encerrados-traco:
    Control: Rectangle@2.3.0
    Properties:
      BorderStyle: =BorderStyle.None
      Fill: =If(varXXTab = 2, fxColorPrimary, fxColorTransparent)
      Height: =3
      Width: =350
      X: =fxLayoutMargin + 358
      Y: =294
```

## 5. Filters

Above any gallery with more than ~50 records. Four rules:

1. **`Filter` blue and `Clear` gray**, 128 by `fxFilterHeight`; never orange.
2. The input border changes from gray to blue when there is a value (an "active filter" feedback that takes no
   space).
3. **`Clear` rewrites the variable of each filter**, not just `Reset`: `Reset` on a
   `DatePicker` does not fire `OnChange`.
4. `DelayOutput: =true` on the text field; a combo with many items with `IsSearchable`.

The date stores an **integer** (`Ref_*`, see [delegation.md](delegation.md) §4), not a date.
`FocusedBorderColor` is the only focus property attested on the inputs; `Size`, `Radius*` and
`FocusedBorderThickness` **do not exist** on `ComboBox` and `DatePicker`.

```yaml
- xx-con-filtros:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorBorder
      BorderThickness: =1
      Fill: =fxColorSurface
      Height: =100
      RadiusBottomLeft: =fxModalRadius
      RadiusBottomRight: =fxModalRadius
      RadiusTopLeft: =fxModalRadius
      RadiusTopRight: =fxModalRadius
      Width: =1280
      X: =fxLayoutMargin
      Y: =120
    Children:
      - xx-cbo-filtro-unidade:
          Control: Classic/ComboBox@2.4.0
          Properties:
            BorderColor: =fxColorBorderInteractive
            ChevronBackground: =fxColorSurface
            ChevronFill: =fxColorTextSecondary
            Color: =fxColorTextPrimary
            DisplayFields: =["Sigla"]
            Fill: =fxColorSurface
            FocusedBorderColor: =fxColorPrimary
            Font: =fxFont
            Height: =fxFilterHeight
            InputTextPlaceholder: ="Unit"
            IsSearchable: =true
            Items: =colUnidadesEscopo
            OnChange: |-
              =Set(
                varUnidadeFiltro,
                If(
                  IsBlank(Self.Selected),
                  If(varTodasUnidades, "", varUnidadeLotacao),
                  Self.Selected.Sigla
                )
              )
            SearchFields: =["Sigla"]
            SelectMultiple: =false
            SelectionColor: =fxColorPrimary
            SelectionFill: =fxColorPrimaryLight
            TabIndex: =0
            Width: =200
            X: =16
            Y: =25
      - xx-dtp-filtro-de:
          Control: Classic/DatePicker@2.6.0
          Properties:
            BorderColor: =fxColorBorderInteractive
            FocusedBorderColor: =fxColorPrimary
            Font: =fxFont
            Format: =DateTimeFormat.ShortDate
            Height: =fxFilterHeight
            IconBackground: =fxColorSurface
            IconFill: =fxColorPrimary
            InputTextPlaceholder: ="From"
            OnChange: |-
              =Set(
                varPedidoDe,
                If(
                  IsBlank(Self.SelectedDate),
                  Blank(),
                  36524 + DateDiff(Date(2000, 1, 1), Self.SelectedDate, TimeUnit.Days)
                )
              )
            TabIndex: =0
            Width: =180
            X: =232
            Y: =25
      - xx-txt-filtro-busca:
          Control: Classic/TextInput@2.3.2
          Properties:
            BorderColor: =If(IsBlank(Self.Text), fxColorBorderInteractive, fxColorPrimary)
            Color: =fxColorTextPrimary
            Default: =""
            DelayOutput: =true
            FocusedBorderColor: =fxColorPrimary
            Font: =fxFont
            Height: =fxFilterHeight
            HintText: ="Search by code"
            Size: =fxFontSizeFilter
            TabIndex: =0
            Width: =280
            X: =428
            Y: =25
      - xx-btn-filtro-limpar:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =Self.Fill
            BorderThickness: =1
            Color: =fxColorTextOnPrimary
            Fill: =fxColorButtonCancel
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =fxFilterHeight
            HoverBorderColor: =fxColorButtonCancelHover
            HoverColor: =fxColorTextOnPrimary
            HoverFill: =fxColorButtonCancelHover
            OnSelect: |-
              =Reset('xx-cbo-filtro-unidade');
              Reset('xx-dtp-filtro-de');
              Reset('xx-txt-filtro-busca');
              Set(varUnidadeFiltro, If(varTodasUnidades, "", varUnidadeLotacao));
              // DatePicker Reset does not fire OnChange: rewrite the variable the same way OnVisible does
              Set(varPedidoDe, Blank())
            PressedBorderColor: =fxColorButtonCancelHover
            PressedColor: =fxColorTextOnPrimary
            PressedFill: =fxColorButtonCancelHover
            RadiusBottomLeft: =fxBtnRadius
            RadiusBottomRight: =fxBtnRadius
            RadiusTopLeft: =fxBtnRadius
            RadiusTopRight: =fxBtnRadius
            Size: =fxFontSizeFilter
            TabIndex: =0
            Text: =fxTxtLimpar
            Width: =fxBtnWidthFilter
            X: =724
            Y: =25
```

## 6. Gallery with column header

Three layers: filters, column header (fixed controls **outside** the gallery, aligned by
`X` and `Width` to the template) and gallery. The header is a `Classic/Button` with `DisplayMode.View` (not
focusable, not clickable), in a single palette.

- **`TemplateSize: =Max(20, fxRowHeight)`**, never 0 and never a fixed value disconnected from the
  content (a 658 px row with 75 px of content is wasted scrolling).
- **First child = the row's clickable background** (`GroupContainer` has no `OnSelect`).
- Inside the gallery use `Parent.TemplateWidth` and `Parent.TemplateHeight`, not `Parent.Width`.
- At most 2 levels of nesting; never `Patch` on the gallery's own source inside `OnChange`
  (patch and reload loop).
- Delegable `Items` ([delegation.md](delegation.md)); empty state by `AllItemsCount`.
- A row height that expands for inline detail: conditional `TemplateSize`, not a fixed
  number that breaks the panel.
- A 2D table is accessible only with the classic Data Table; a gallery with labels does not build a
  semantic table for a screen reader.

```yaml
- xx-hdr-gal-codigo:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      DisplayMode: =DisplayMode.View
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      Size: =fxFontSizeHeader
      Text: ="Code"
      Width: =160
      X: =fxLayoutMargin
      Y: =196
- xx-hdr-gal-descricao:
    Control: Classic/Button@2.2.0
    Properties:
      Color: =fxColorTableHeaderText
      DisplayMode: =DisplayMode.View
      Fill: =fxColorTableHeaderBg
      Font: =fxFont
      FontWeight: =FontWeight.Bold
      Height: =fxTableHeaderHeight
      Size: =fxFontSizeHeader
      Text: ="Description"
      Width: =640
      X: =fxLayoutMargin + 160
      Y: =196
- xx-gal-registros:
    Control: Gallery@2.15.0
    Variant: BrowseLayout_Flexible_SocialFeed_ver5.0
    Properties:
      BorderColor: =fxColorBorder
      Height: =fxRowHeight * 12
      Items: |-
        =Filter(colRegistros, StartsWith(Codigo, 'xx-txt-filtro-busca'.Text))
      TemplatePadding: =0
      TemplateSize: =Max(20, fxRowHeight)
      Width: =800
      X: =fxLayoutMargin
      Y: =196 + fxTableHeaderHeight
    Children:
      - xx-btn-gal-fundo-linha:
          Control: Classic/Button@2.2.0
          Properties:
            BorderColor: =fxColorDivider
            Color: =fxColorTransparent
            Fill: =If(varRegistroSel.Id = ThisItem.Id, fxColorPrimaryLight, fxColorSurface)
            Font: =fxFont
            Height: =Parent.TemplateHeight
            HoverFill: =fxColorPrimaryLight
            OnSelect: =Set(varRegistroSel, ThisItem)
            PressedFill: =fxColorPrimaryLight
            TabIndex: =0
            Text: =""
            Width: =Parent.TemplateWidth
            X: =0
            Y: =0
      - xx-lbl-gal-codigo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorPrimary
            Font: =fxFont
            FontWeight: =FontWeight.Semibold
            Height: =Parent.TemplateHeight
            Size: =fxFontSizeTable
            Text: =ThisItem.Codigo
            VerticalAlign: =VerticalAlign.Middle
            Width: =140
            X: =16
            Y: =0
      - xx-lbl-gal-descricao:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextBody
            Font: =fxFont
            Height: =Parent.TemplateHeight
            Size: =fxFontSizeTable
            Text: =ThisItem.Descricao
            VerticalAlign: =VerticalAlign.Middle
            Width: =630
            X: =160
            Y: =0
```

## 7. Action badge

An action button inside the row, with a color derived from its own label (`Self.Text`) via `fxBadge*`
tokens (all with a text contrast of at least 4.5:1). `Underline: =true` keeps the action
legible without depending on color alone. Hover **darkens** on every button (`ColorFade(Self.Fill, -12%)`),
never lightens on one and darkens on another.

```yaml
- xx-btn-gal-acao:
    Control: Classic/Button@2.2.0
    Properties:
      BorderStyle: =BorderStyle.None
      Color: |-
        =Switch(
          Self.Text,
          "Approve", fxBadgeSuccessText,
          "Review", fxBadgeWarningText,
          "Cancel", fxBadgeDangerText,
          fxBadgeNeutralText
        )
      DisabledBorderColor: =fxColorBorder
      DisplayMode: =If(ThisItem.Bloqueado, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: |-
        =Switch(
          Self.Text,
          "Approve", fxBadgeSuccessBg,
          "Review", fxBadgeWarningBg,
          "Cancel", fxBadgeDangerBg,
          fxBadgeNeutralBg
        )
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =35
      HoverFill: =ColorFade(Self.Fill, -12%)
      PressedFill: =ColorFade(Self.Fill, -24%)
      Size: =fxFontSizeTableSmall
      TabIndex: =0
      Text: ="Approve"
      Underline: =true
      Width: =88
      X: =1100
      Y: =8
```

## 8. Buttons

Four roles, same geometry (`fxBtnHeight`, `fxBtnRadius`):

| Role | Fill | Text | Use |
|---|---|---|---|
| primary | `fxColorPrimary` | action verb | the main action of the screen or modal |
| secondary | `fxColorButtonCancel` | `Back`, `Cancel`, `Close` | leave without acting |
| destructive | `fxColorError` | explicit verb (`Confirm cancellation`) | irreversible; enabled only with a reason |
| neutral | `fxColorPrimaryLight` | short label | quick filter, chip |

Rules: the primary takes the **same position** on every screen; in the modal, secondary on the left and
primary on the right, both with width `(Parent.Width - fxModalPadding * 3) / 2`. **Pressed never
inverts `Fill` and `Color`** (a white button on white leaves the text invisible when pressed);
use `ColorFade(Self.Fill, -30%)`. Always define the `Disabled*` colors. Every button that calls a
flow binds `DisplayMode` and `Text` to `varShowLoading` ([flow-call.md](flow-call.md)).

```yaml
- xx-btn-primario:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =Self.Fill
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      DisabledBorderColor: =fxColorDisabled
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      DisplayMode: =If(varShowLoading, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtConfirmar
      Width: =fxBtnWidth
      X: =20
      Y: =20
- xx-btn-secundario:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =Self.Fill
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      Fill: =fxColorButtonCancel
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =fxColorButtonCancelHover
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =fxColorButtonCancelHover
      PressedBorderColor: =fxColorButtonCancelHover
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =fxColorButtonCancelHover
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtCancelar
      Width: =fxBtnWidth
      X: =20
      Y: =20
- xx-btn-destrutivo:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =Self.Fill
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      DisabledBorderColor: =fxColorDisabled
      DisabledColor: =fxColorDisabledText
      DisabledFill: =fxColorDisabled
      DisplayMode: |-
        =If(
          Len(Trim('xx-txt-motivo'.Text)) < 5,
          DisplayMode.Disabled,
          DisplayMode.Edit
        )
      Fill: =fxColorError
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="Confirm cancellation"
      Width: =230
      X: =20
      Y: =20
- xx-btn-neutro:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =ColorFade(Self.Fill, -15%)
      Color: =fxColorTableHeaderText
      Fill: =fxColorPrimaryLight
      Font: =fxFont
      Height: =fxBtnHeight
      HoverFill: =ColorFade(Self.Fill, -10%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="System"
      Width: =90
      X: =20
      Y: =20
```

## 9. Modal, loading and toast

Moved to [ux-feedback.md](ux-feedback.md), to keep this file under 1,000 lines.

## 12. Bulk selection

A counter with singular and plural in a single formula. `colSelecionados` receives the item in `OnCheck` and
loses it in `OnUncheck`: do **not** use `Filter(gal.AllItems, ...)` (it only sees what is already loaded and
`AllItems` is expensive). An empty `Text` on the checkbox leaves the control without a name for a screen reader:
a limitation to record in [accessibility.md](accessibility.md).

```yaml
- xx-chk-gal-selecionar:
    Control: Classic/CheckBox@2.1.0
    Properties:
      CheckboxBorderColor: =fxColorBorderInteractive
      CheckmarkFill: =fxColorPrimary
      Default: =false
      Font: =fxFont
      Height: =40
      OnCheck: =Collect(colSelecionados, ThisItem)
      OnUncheck: =RemoveIf(colSelecionados, Id = ThisItem.Id)
      TabIndex: =0
      Text: =""
      Width: =40
      X: =4
      Y: =5
- xx-lbl-selecao-contador:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =28
      Size: =fxFontSizeFilter
      Text: |-
        =With(
          { n: CountRows(colSelecionados) },
          n & If(n = 1, " record selected", " records selected")
        )
      VerticalAlign: =VerticalAlign.Middle
      Visible: =CountRows(colSelecionados) > 0
      Width: =280
      X: =1000
      Y: =120
```

## 13. States: empty, truncated, error, disabled

- **Empty**: there is no native empty state in the gallery. One `Label` per gallery, bound to the
  gallery itself (`'gal'.X`, `.Width`, `.AllItemsCount = 0`) and using `fxMsgNoResultsError` +
  `fxMsgNoResultsHint` (what happened and what to do). Text color with contrast >= 4.5:1: the light
  gray placeholder fails (2.54:1).
- **Truncated**: when the counter hits the ceiling (`varPedidoTotal >= fxLimiteLinhas`), an
  amber label warns. A truncated list without a warning is a **UX** problem, not just a data one.
- **Error**: an `Error` + `Hint` pair per catalog message; a field error appears **on the field** (§14),
  not just in the global toast.
- **Disabled**: `DisplayMode` derived from a precondition (selection made, a reason with 5+
  characters, previous field chosen, `varShowLoading`); define `DisabledFill`, `DisabledColor`
  and `DisabledBorderColor`. Disabled text has no contrast requirement, but it must be
  distinguishable from the enabled one.
- **Hover, pressed, focus**: `HoverFill: =ColorFade(Self.Fill, -20%)`, `PressedFill: =ColorFade(Self.Fill, -30%)`;
  focus only through `FocusedBorderColor` on the attested inputs.
- **Gallery selection**: row background by data or by selection **plus** a text badge
  (never color alone).

```yaml
- xx-lbl-gal-vazio:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: =fxColorTextSecondary
      Font: =fxFont
      Height: =120
      Size: =fxFontSizeBody
      Text: =fxMsgNoResultsError & Char(10) & fxMsgNoResultsHint
      VerticalAlign: =VerticalAlign.Middle
      Visible: ='xx-gal-registros'.Visible && 'xx-gal-registros'.AllItemsCount = 0
      Width: ='xx-gal-registros'.Width
      X: ='xx-gal-registros'.X
      Y: ='xx-gal-registros'.Y + 80
- xx-lbl-gal-truncado:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: =fxBadgeWarningText
      Fill: =fxBadgeWarningBg
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =28
      Size: =fxFontSizeFilter
      Text: =fxMsgListaTruncada
      VerticalAlign: =VerticalAlign.Middle
      Visible: =varPedidoTotal >= fxLimiteLinhas
      Width: ='xx-gal-registros'.Width
      X: ='xx-gal-registros'.X
      Y: ='xx-gal-registros'.Y + 'xx-gal-registros'.Height + 8
```

## 14. Form: required and per-field error

Required is flagged unambiguously (a label with `*` **and** help text; `*` alone
is not enough), a label at least `fxFontSizeFilter` (a label smaller than the value inverts the
hierarchy) and a per-field error, visible after the first attempt to save
(`varTentouSalvar`). Form validation uses `Notify()`; a flow return, toast.

```yaml
- xx-lbl-form-email-rotulo:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorTextPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =20
      Size: =fxFontSizeFilter
      Text: ="Email *"
      Width: =300
      X: =fxModalPadding
      Y: =20
- xx-txt-form-email:
    Control: Classic/TextInput@2.3.2
    Properties:
      BorderColor: =If(varTentouSalvar && !IsMatch(Self.Text, Match.Email), fxColorError, fxColorBorderInteractive)
      Color: =fxColorTextPrimary
      Default: =""
      FocusedBorderColor: =fxColorPrimary
      Font: =fxFont
      Height: =fxFilterHeight
      HintText: ="user@contoso.com"
      Size: =fxFontSizeFilter
      TabIndex: =0
      Width: =300
      X: =fxModalPadding
      Y: =44
- xx-lbl-form-email-erro:
    Control: Label@2.5.1
    Properties:
      Color: =fxColorError
      Font: =fxFont
      Height: =20
      Size: =fxFontSizeFilter
      Text: ="Enter a valid email."
      Visible: =varTentouSalvar && !IsMatch('xx-txt-form-email'.Text, Match.Email)
      Width: =300
      X: =fxModalPadding
      Y: =44 + fxFilterHeight + 4
```

## 15. Z-order

The order in `Children` is the z-index. The end of every screen is:

```text
content -> no-access panel -> modals -> loading -> toast
```

The toast sits above the modal and the loading veil. Inverting it puts the modal above the toast (a common
defect, already seen on more than one screen). Validator: T016.

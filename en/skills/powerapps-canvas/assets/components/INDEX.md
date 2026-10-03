# Reusable component catalog

One file per Power Apps Canvas UX component, in ManualLayout with Classic controls, in the pasted-YAML dialect, with `fx*` tokens, names `xx-<type>-<module>-<element>` and only properties attested per type (PA2108). Data source and columns appear as placeholders (`'<source>'`, `<col-...>`); the sample domain is `Order` and `Unit`. Each file carries the **complete, pasteable** YAML block, is the canonical version of the component and was validated by `scripts/validar-telas.py`.

## Contents

1. [How to paste and how it is validated](#how-to-paste-and-how-it-is-validated)
2. [Components](#components)
3. [Tokens to add](#tokens-to-add)
4. [Variables and collections to add to OnStart](#variables-and-collections-to-add-to-onstart)
5. [Relation to the references](#relation-to-the-references)
6. [What was left out](#what-was-left-out)

## How to paste and how it is validated

Each block is a **fragment**: a list of controls (`- name:`), the same format as a screen's `Children:`. It is what Studio's Code view accepts in **Paste code** with the screen (or a container) selected; pasting **creates** new controls and does not replace existing ones. Rename the `xx` prefix first: a control name is unique across the whole app and Studio renames a duplicate to `_1`.

The validator classifies the block as a fragment and checks each control (`T001` to `T022`), without the `T020` warning ("not a YAML screen"), which only appears in a file with no `yaml` block at all. The minimal shape it validates:

```yaml
- xx-con-exemplo:
    Control: GroupContainer@1.5.0
    Variant: ManualLayout
    Properties:
      BorderColor: =fxColorTransparent
      Fill: =fxColorTransparent
      Height: =80
      Width: =Parent.Width
      X: =0
      Y: =0
    Children:
      - xx-lbl-exemplo-titulo:
          Control: Label@2.5.1
          Properties:
            Color: =fxColorTextPrimary
            Font: =fxFont
            Size: =fxFontSizeBody
            Text: ="Example"
            Width: =300
            X: =fxLayoutMargin
            Y: =20
```

For a complete screen, put the fragment under a screen's `Children:` in `Screens:` (see `assets/screen-template.md`). Commands:

```bash
python skills/powerapps-canvas/scripts/validar-telas.py skills/powerapps-canvas/assets/components
python -m pytest tests/powerapps-canvas -q -p no:cacheprovider
```

Destination of every YAML block: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). The tokens in the section below go into the App object's formula bar (en-US: `,` and `;`), never into the YAML. The validator does not replace Studio: paste into a test app and check for `PA2108` (property refused). Three properties used here are not in the attested table of `references/pa-yaml-format.md` §8.3 (they exist in Learn; confirm when pasting): `Align` and `BorderStyle` on `Classic/Button@2.2.0` and `MaxLength` on `Classic/TextInput@2.3.2`.

**Maturity.** `stable` = seen in production in more than one real project; `unique` = seen in only one; `new` = not yet seen in production (validated only by `validar-telas.py`: confirm when pasting, in a test app). **Frequency**: how often the component repeated across the reference screens: `very common` (almost every screen), `common`, `occasional` (a few screens), `rare` (one screen) or `to be measured` (`new` component).

## Components

| Component | File | When to use | Dependencies | Frequency | Maturity |
|---|---|---|---|---|---|
| [Screen header](screen-header.md) | `screen-header.md` | every content screen, no exception. | tokens from the `COMPONENTS` block: `fxHeaderHeight`; variables: `varAgora`, `varTelaAtiva`; existing `fx*` tokens: 11 | very common | stable |
| [Side menu](side-menu.md) | `side-menu.md` | the app has 3 or more first-level screens; fixed, collapsible or drawer (hamburger). | tokens from the `COMPONENTS` block: `fxColorMenuBg`, `fxMenuWidth`, `fxColorMenuItemActive`, `fxMenuItemHeight`, `fxNavWidthExpandida`, `fxNavWidthRecolhida`; variables: `varSemAcesso`, `varTelaAtiva`, `varPerfil`, `varUsuario`, `varUnidadeFiltro`, `varNavExpandida`; existing `fx*` tokens: 11 | very common | stable |
| [Top menu](top-menu.md) | `top-menu.md` | 2 to 6 first-level screens with a short label; wide table. | tokens from the `COMPONENTS` block: `fxColorMenuBg`, `fxColorMenuItemActive`, `fxTopNavHeight`, `fxTopNavItemWidth`; variables: `varSemAcesso`, `varTelaAtiva`, `varPerfil`, `varUsuario`; existing `fx*` tokens: 6 | to be measured | new |
| [Home screen with cards](home-cards.md) | `home-cards.md` | app used occasionally, one task per visit, narrow screen. | tokens from the `COMPONENTS` block: `fxHeaderHeight`, `fxHubCardWidth`, `fxHubCardHeight`, `fxFontSizeCardTitle`; variables: `varSemAcesso`, `varTelaAtiva`, `varPerfil`; existing `fx*` tokens: 15 | to be measured | new |
| [KPI card (counter with ceiling)](kpi-card.md) | `kpi-card.md` | summarize the list right below in up to 5 or 6 numbers. | tokens from the `COMPONENTS` block: `fxHeaderHeight`; variables: `varPedidoTotal`, `varPedidoAbertos`, `varPedidoAndamento`, `varPedidoEncerrados`; existing `fx*` tokens: 24 | common | stable |
| [Tabs (button and stroke)](tabs.md) | `tabs.md` | up to 4 sets of the same entity on the same screen. | tokens from the `COMPONENTS` block: `fxHeaderHeight`; variables: `varXXTab`, `varPedidoAbertos`, `varPedidoEncerrados`, `varPedidoTotal`; existing `fx*` tokens: 12 | common | stable |
| [Filter bar (combo, text, dates and clear)](filter-bar.md) | `filter-bar.md` | gallery with more than about 50 records. | tokens from the `COMPONENTS` block: `fxHeaderHeight`; variables: `varPedidoDe`, `varPedidoAte`, `varPedidoFiltroAplicado`, `varPedidoStatusAplicado`, `varPedidoBuscaAplicada`; existing `fx*` tokens: 22 | common | stable |
| [Unit selector](unit-selector.md) | `unit-selector.md` | the user can see more than one unit. | tokens from the `COMPONENTS` block: `fxHeaderHeight`; variables: `varUnidadeFiltro`, `varTodasUnidades`, `varUnidadeLotacao`, `varPedidoTotal`; collections: `colUnidadesEscopo`; existing `fx*` tokens: 8 | common | stable |
| [Table-style gallery](table-gallery.md) | `table-gallery.md` | list of records with 4 to 10 columns and one action per row. | variables: `varUnidadeFiltro`, `varPedidoDe`, `varPedidoAte`, `varPedidoSel`, `varMostrarDetalhes`; existing `fx*` tokens: 29 | very common | stable |
| [Sortable header](column-sort.md) | `column-sort.md` | the user needs to reorder the same list by more than one column. | tokens from the `COMPONENTS` block: `fxTxtOrdemAsc`, `fxTxtOrdemDesc`; variables: `varPedidoSortColuna`, `varPedidoSortAsc`; existing `fx*` tokens: 6 | rare | unique |
| [Empty state and truncated-list notice](empty-state.md) | `empty-state.md` | every filterable gallery. | variables: `varPedidoTotal`; existing `fx*` tokens: 10 | very common | stable |
| ["Showing N of M" footer](count-footer.md) | `count-footer.md` | the list has no pagination and the real total matters. | tokens from the `COMPONENTS` block: `fxTxtExibindo`; variables: `varPedidoTotal`, `varUnidadeFiltro`; existing `fx*` tokens: 6 | occasional | unique |
| [Status badge (pill)](status-badge.md) | `status-badge.md` | status column of a gallery or detail. | tokens from the `COMPONENTS` block: `fxPillHeight`; existing `fx*` tokens: 17 | common | stable |
| [Buttons: primary, secondary, destructive and neutral](buttons.md) | `buttons.md` | any action button: choose the role by the nature of the action, never by the text. | variables: `varShowLoading`, `varMostrarConfirmar`, `varMostrarCancelar`; existing `fx*` tokens: 16 | very common | stable |
| [Confirm modal](confirm-modal.md) | `confirm-modal.md` | action with a server-side effect that the user may want to undo right away. | tokens from the `COMPONENTS` block: `fxModalWidthS`; variables: `varMostrarConfirmar`, `varPedidoSel`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType` ...; existing `fx*` tokens: 24 | occasional | stable |
| [Form modal](form-modal.md) | `form-modal.md` | create or edit a record with few fields (up to about 8). | tokens from the `COMPONENTS` block: `fxModalWidthL`, `fxHeaderHeight`; variables: `varMostrarForm`, `varUnidadeFiltro`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType` ...; existing `fx*` tokens: 32 | common | stable |
| [Destructive modal with required reason](destructive-reason-modal.md) | `destructive-reason-modal.md` | cancel, delete or reverse something that does not come back. | tokens from the `COMPONENTS` block: `fxModalWidthM`; variables: `varMostrarCancelar`, `varPedidoSel`, `varShowLoading`, `varLoadingMessage`, `varRet`, `varToastType` ...; existing `fx*` tokens: 28 | occasional | stable |
| [Info modal (details and history)](info-modal.md) | `info-modal.md` | show the detail or history of a record without leaving the screen. | tokens from the `COMPONENTS` block: `fxModalWidthL`; variables: `varMostrarDetalhes`, `varPedidoSel`; existing `fx*` tokens: 28 | occasional | stable |
| [Loading overlay](loading-overlay.md) | `loading-overlay.md` | every flow `.Run()` call. | variables: `varShowLoading`, `varLoadingMessage`; existing `fx*` tokens: 12 | very common | stable |
| [Flow-return toast](toast.md) | `toast.md` | return of any flow call (the message arrives ready in `description`). | tokens from the `COMPONENTS` block: `fxColorToastTrack`; variables: `varShowToast`, `varToastType`, `varToastMessage`; existing `fx*` tokens: 20 | very common | stable |
| ["No access" panel](no-access-panel.md) | `no-access-panel.md` | every screen of an app with role control. | variables: `varSemAcesso`, `varPerfil`; existing `fx*` tokens: 11 | common | unique |
| [Export button](export.md) | `export.md` | the user needs the complete filtered set, not what fits on screen. | tokens from the `COMPONENTS` block: `fxTxtExportar`; variables: `varShowLoading`, `varLoadingMessage`, `varRet`, `varUnidadeFiltro`, `varPedidoDe`, `varPedidoAte` ...; existing `fx*` tokens: 13 | occasional | stable |
| [Cursor pagination](cursor-pagination.md) | `cursor-pagination.md` | the list goes beyond `fxLimiteLinhas` and the user needs to go through all of it. | tokens from the `COMPONENTS` block: `fxTxtAnterior`, `fxTxtProxima`; variables: `varPagina`, `varShowLoading`, `varCursorAtual`, `varPedidoTotal`; collections: `colCursores`; existing `fx*` tokens: 12 | rare | unique |
| [Bulk selection](bulk-selection.md) | `bulk-selection.md` | the same action applies to several records. | variables: `varMostrarConfirmarLote`, `varShowLoading`, `varPerfil`; collections: `colSelecionados`; existing `fx*` tokens: 11 | occasional | unique |
| [Expandable row](expandable-row.md) | `expandable-row.md` | the detail is short (2 to 4 fields) and the user compares several rows. | variables: `varLinhaExpandida`; existing `fx*` tokens: 11 | occasional | unique |

## Tokens to add

None at the moment: the tokens the components use are in [`../app-formulas-tokens.md`](../app-formulas-tokens.md), `COMPONENTS` block. When creating a new component, list here (`powerfx` block, destination en-US formula bar) the tokens that are missing and then move them into the template.

## Variables and collections to add to OnStart

Every global is born in `OnStart` with a neutral value (`assets/app-onstart-template.md`). These are used by the components and are not yet in the template:

| Variable | Components that read it | Initial value |
|---|---|---|
| `varAgora` | screen-header | `Now()` |
| `varCursorAtual` | cursor-pagination | `Blank()` |
| `varLinhaExpandida` | expandable-row | `Blank()` |
| `varMostrarCancelar` | buttons, destructive-reason-modal | `false` |
| `varMostrarConfirmarLote` | bulk-selection | `false` |
| `varMostrarDetalhes` | table-gallery, info-modal | `false` |
| `varMostrarForm` | form-modal | `false` |
| `varNavExpandida` | side-menu | `false` |
| `varPagina` | cursor-pagination | `1` |
| `varPedidoAbertos` | kpi-card, tabs | `0` |
| `varPedidoAndamento` | kpi-card | `0` |
| `varPedidoAte` | filter-bar, table-gallery, export | `Blank()` (reset in `OnVisible`) |
| `varPedidoBuscaAplicada` | filter-bar | `""` |
| `varPedidoDe` | filter-bar, table-gallery, export | `Blank()` (reset in `OnVisible`) |
| `varPedidoEncerrados` | kpi-card, tabs | `0` |
| `varPedidoFiltroAplicado` | filter-bar | `false` |
| `varPedidoSortAsc` | column-sort | `false` |
| `varPedidoSortColuna` | column-sort | `"<col-data>"` |
| `varPedidoStatusAplicado` | filter-bar | `""` |
| `varXXTab` | tabs | `1` |

Collections not yet declared in the template: `colCursores`, `colSelecionados` (all start empty with `Clear`/`ClearCollect`).

## Relation to the references

These files repeat, in canonical and normalized form, blocks that already exist in `references/ux-components.md`, `references/ux-feedback.md` and `assets/screen-template.md`. The reference explains the rule; the component is the pasteable version. The match by section:

| Reference | Section | Component |
|---|---|---|
| `ux-components.md` | 2. Screen header | `screen-header.md` |
| `ux-components.md` | 3. KPI card | `kpi-card.md` |
| `ux-components.md` | 4. Tabs | `tabs.md` |
| `ux-components.md` | 5. Filters | `filter-bar.md`, `unit-selector.md` |
| `ux-components.md` | 6. Gallery with column header | `table-gallery.md`, `column-sort.md` |
| `ux-components.md` | 7. Action badge | `status-badge.md` |
| `ux-components.md` | 8. Buttons | `buttons.md` |
| `ux-components.md` | 12. Bulk selection | `bulk-selection.md` |
| `ux-components.md` | 13. States | `empty-state.md`, `count-footer.md` |
| `ux-feedback.md` | 9. Modal | `confirm-modal.md`, `destructive-reason-modal.md`, `form-modal.md`, `info-modal.md` |
| `ux-feedback.md` | 10. Loading | `loading-overlay.md` |
| `ux-feedback.md` | 11. Toast | `toast.md` |
| `screen-template.md` | The screen (no access, modal, loading, toast) | `no-access-panel.md`, `confirm-modal.md`, `loading-overlay.md`, `toast.md` |

Differences from the references: every `Font` is `fxFont`, as in the references; the leftover `RGBA(...)` colors of the toast became a token (`fxColorToastTrack`); the modal and loading veil gained a transparent blocking button as its first child.

## What was left out

- **Auto-refresh, search debounce and polling**: already complete in `references/timers-async.md`.
- **Version and copyright footer of the screen**: static label with no logic, not worth a file.
- **"All" toggle** (rare): one line of `Classic/Toggle@2.1.0` with `OnChange`; no pattern to extract.
- **Header clock**: became a variation of `screen-header.md`.
- **Search field**: became part of `filter-bar.md` (`DelayOutput`).
- **Two-column form and editor on a dedicated screen**: vary too much between screens; only the form modal repeats.

# Template: `App.Formulas` with the `fx*` tokens

Single source of color, size, text and component values. No screen repeats these values: every
component `Fill`, `Color`, `Height` and `Text` points to a token.

**How to apply.** The App object has no Code view and does not accept pasted control code:
select `App` in Studio, open the `Formulas` property in the formula bar and paste the whole
block below. `[verified: reference project]`

**Dialect.** This file goes into the formula bar of an en-US Studio: argument `,`,
chaining `;`, decimal `.`. A pt-BR Studio expects `;` between arguments, `;;` to chain and `,` as
decimal, so the same text does not parse there; see
[default-decisions.md](../../power-platform/references/default-decisions.md) §3.

**Block rules.**

- Only constants and values derived from constants. A named formula **never** reads a global
  variable (`Set`): it only recalculates when one of its inputs changes, and a `Refresh()` does not re-run it.
- No behavior function (`Set`, `Collect`, `Navigate`, `Notify`): forbidden in `Formulas`.
- Neutral palette (default Fluent 2 blue ramp): swap in the project brand and recalculate the contrast (`references/design-tokens.md` §3); sizes for a 1920x1080 canvas. A project with another brand
  changes the values, not the names. Contrast checked: text on background >= 4.5:1;
  border of an interactive control >= 3:1 `[verified: WCAG 2.x calculation]`.
- The fractional alpha of `RGBA` uses a decimal point in the en-US bar (`0.5`); a pt-BR bar would need a decimal comma (`0,5`).

Destination: formula bar of the App object, `Formulas` property (en-US: `,` and `;`).

```powerfx
// ---------- COLOR: brand and surface ----------
fxColorPrimary = RGBA(15, 108, 189, 1);
fxColorPrimaryDark = RGBA(12, 59, 94, 1);
fxColorPrimaryLight = RGBA(235, 243, 252, 1);
fxColorBackground = RGBA(249, 250, 251, 1);
fxColorSurface = RGBA(255, 255, 255, 1);
fxColorTransparent = RGBA(0, 0, 0, 0);
fxColorOverlay = RGBA(0, 0, 0, 0.5);
fxColorOverlayDark = RGBA(0, 0, 0, 0.6);

// ---------- COLOR: text ----------
fxColorTextPrimary = RGBA(17, 24, 39, 1);
fxColorTextSecondary = RGBA(77, 77, 77, 1);
fxColorTextBody = RGBA(75, 85, 99, 1);
fxColorTextOnPrimary = RGBA(255, 255, 255, 1);
fxColorTextOnWarning = RGBA(17, 24, 39, 1);

// ---------- COLOR: border and divider ----------
// fxColorBorder is decorative (card, container). An interactive control uses Interactive.
fxColorBorder = RGBA(166, 166, 166, 1);
fxColorBorderInteractive = RGBA(117, 117, 117, 1);
fxColorDivider = RGBA(229, 231, 235, 1);

// ---------- COLOR: state (green = state, never action) ----------
fxColorSuccess = RGBA(21, 128, 61, 1);
fxColorWarning = RGBA(255, 193, 7, 1);
fxColorError = RGBA(200, 35, 51, 1);

// ---------- COLOR: button ----------
fxColorButtonCancel = RGBA(108, 117, 125, 1);
fxColorButtonCancelHover = RGBA(90, 98, 104, 1);
fxColorDisabled = RGBA(206, 212, 218, 1);
fxColorDisabledText = RGBA(134, 142, 150, 1);

// ---------- COLOR: tab and table header ----------
fxColorTabInactive = RGBA(237, 237, 237, 1);
fxColorTableHeaderBg = RGBA(235, 243, 252, 1);
fxColorTableHeaderText = RGBA(17, 94, 163, 1);

// ---------- COLOR: badge (dark text on a pastel of the same hue, >= 4.5:1) ----------
fxBadgeSuccessText = RGBA(22, 101, 52, 1);
fxBadgeSuccessBg = RGBA(220, 252, 231, 1);
fxBadgeInfoText = RGBA(15, 84, 140, 1);
fxBadgeInfoBg = RGBA(207, 228, 250, 1);
fxBadgeWarningText = RGBA(146, 64, 14, 1);
fxBadgeWarningBg = RGBA(255, 218, 185, 1);
fxBadgeDangerText = RGBA(139, 0, 0, 1);
fxBadgeDangerBg = RGBA(255, 182, 193, 1);
fxBadgeProgressText = RGBA(133, 77, 14, 1);
fxBadgeProgressBg = RGBA(255, 230, 100, 1);
fxBadgeNeutralText = RGBA(52, 58, 64, 1);
fxBadgeNeutralBg = RGBA(206, 212, 218, 1);

// ---------- LAYOUT: one breakpoint, everything derives from it ----------
fxIsCompact = App.Width < 1600;
fxLayoutMargin = If(fxIsCompact, 40, 100);
fxLayoutGutter = If(fxIsCompact, 8, 16);
fxRowHeight = If(fxIsCompact, 40, 50);
fxTableHeaderHeight = If(fxIsCompact, 35, 50);
fxFilterHeight = If(fxIsCompact, 40, 50);
fxKPIWidth = If(fxIsCompact, 120, 150);
fxKPIHeight = If(fxIsCompact, 65, 85);
fxKPITitleHeight = If(fxIsCompact, 28, 35);
fxKPIValueHeight = If(fxIsCompact, 37, 50);

// ---------- TYPOGRAPHY: one family (Segoe UI) ----------
fxFont = Font.'Segoe UI';
fxFontSizeTitle = If(fxIsCompact, 28, 35);
fxFontSizeKPI = If(fxIsCompact, 20, 25);
fxFontSizeKPITitle = 11;
fxFontSizeBody = 14;
fxFontSizeFilter = If(fxIsCompact, 12, 14);
fxFontSizeTable = If(fxIsCompact, 11, 13);
fxFontSizeTableSmall = If(fxIsCompact, 11, 12);
fxFontSizeHeader = If(fxIsCompact, 11, 13);
fxFontSizeSemAcesso = 20;
fxFontSizeToastIcon = 18;
fxFontSizeToastTitle = 15;
fxFontSizeToast = 12;

// ---------- COMPONENT: button ----------
fxBtnHeight = 45;
fxBtnRadius = 8;
fxBtnWidth = 210;
fxBtnWidthFilter = 128;
fxBtnFontSize = 14;

// ---------- COMPONENT: modal ----------
fxModalRadius = 12;
fxModalPadding = 20;
fxModalTitleSize = 16;

// ---------- COMPONENT: loading ----------
fxLoadingCardWidth = 250;
fxLoadingCardHeight = 140;
fxLoadingSpinnerSize = 60;

// ---------- COMPONENT: toast (flow return) ----------
fxToastWidth = 420;
fxToastDurationShort = 6000;
fxToastDurationLong = 12000;
fxToastDurationError = 15000;
fxColorToastBg = RGBA(33, 37, 41, 1);
fxColorToastText = RGBA(173, 181, 189, 1);

// ---------- CONNECTOR LIMIT (SQL connector: 2,000 is the Settings > Data row limit ceiling) ----------
fxPageSize = 100;
fxLimiteLinhas = 2000;
fxTxtTeto = Text(fxLimiteLinhas, "[$-en-US]#,##0") & "+";

// ---------- TEXT: labels ----------
fxTxtVoltar = "Back";
fxTxtFechar = "Close";
fxTxtCancelar = "Cancel";
fxTxtConfirmar = "Confirm";
fxTxtSalvar = "Save";
fxTxtEncerrar = "Complete";
fxTxtFiltrar = "Filter";
fxTxtLimpar = "Clear";
fxTxtProcessando = "Processing...";
fxTxtToastSuccess = "Success";
fxTxtToastWarning = "Partially completed";
fxTxtToastError = "Error";

// ---------- TEXT: messages ("what happened" + "what to do" pair) ----------
fxMsgLoadingDefault = "Processing, please wait...";
fxMsgNoResultsError = "No results found.";
fxMsgNoResultsHint = "Review the filters and try again.";
fxMsgListaTruncada = "Showing the first records. Refine the filters to see the rest.";
fxMsgFalhaFlow = "The operation could not be completed. Nothing was saved.";
fxMsgFalhaFlowHint = "Try again; if it persists, contact support.";
fxMsgConnectionError = "Connection to the server failed.";
fxMsgConnectionHint = "Check the network and try again.";
fxMsgTimeoutError = "The operation took longer than expected.";
fxMsgTimeoutHint = "Check the result in the list before repeating.";
fxMsgSemPermissao = "You do not have permission for this action.";
fxMsgSemAcessoTitulo = "Access not granted";
fxMsgSemAcessoHint = "Your user has no role or unit registered. Contact the app administrator.";
fxMsgCampoObrigatorio = "Fill in the required fields.";
fxMsgFormatoInvalido = "Invalid format. Review the value entered.";
fxMsgSalvoComSucesso = "Record saved successfully.";

// ---------- COMPONENTS (assets/components/) ----------
// height of the screen header strip (used in: screen-header, kpi-card, tabs, filter-bar, unit-selector, form-modal)
fxHeaderHeight = 100;
// width of the fixed side menu (used in: side-menu)
fxMenuWidth = If(fxIsCompact, 220, 260);
// height of each side menu item (used in: side-menu)
fxMenuItemHeight = 52;
// background of the side menu and the top bar (used in: side-menu, top-menu)
fxColorMenuBg = fxColorPrimaryDark;
// background of the active menu item and hover (used in: side-menu, top-menu)
fxColorMenuItemActive = fxColorPrimary;
// width of the collapsed menu (collapsible variation) (used in: side-menu)
fxNavWidthRecolhida = 70;
// width of the expanded menu (collapsible and drawer variations) (used in: side-menu)
fxNavWidthExpandida = 284;
// height of the top navigation bar (used in: top-menu)
fxTopNavHeight = 56;
// width of each item in the top bar (used in: top-menu)
fxTopNavItemWidth = If(fxIsCompact, 140, 168);
// width of the home screen card (used in: home-cards)
fxHubCardWidth = If(fxIsCompact, 300, 360);
// height of the home screen card (used in: home-cards)
fxHubCardHeight = 168;
// title of the home screen card (used in: home-cards)
fxFontSizeCardTitle = If(fxIsCompact, 16, 18);
// small modal card: simple confirmation (used in: confirm-modal)
fxModalWidthS = 450;
// medium modal card: confirmation with a field (used in: destructive-reason-modal)
fxModalWidthM = 520;
// large modal card: form, result, details (used in: form-modal, info-modal)
fxModalWidthL = 620;
// height of the status pill (radius = half) (used in: status-badge)
fxPillHeight = 26;
// suffix of a header sorted ascending (used in: column-sort)
fxTxtOrdemAsc = " ▲";
// suffix of a header sorted descending (used in: column-sort)
fxTxtOrdemDesc = " ▼";
// label of the previous page button (used in: cursor-pagination)
fxTxtAnterior = "‹ Previous";
// label of the next page button (used in: cursor-pagination)
fxTxtProxima = "Next ›";
// label of the export button (used in: export)
fxTxtExportar = "Export";
// start of the "Showing N of M" footer (used in: count-footer)
fxTxtExibindo = "Showing";
// track of the toast progress bar (used in: toast)
fxColorToastTrack = ColorFade(fxColorToastBg, 20%);
```

**After pasting.** Save, wait for the recompile and open a screen: if any `fx*` shows up in
red, the definition was not accepted (the common causes are `;` in place of `,` or a
missing `;` at the end of a line).

**State variables do not go here.** `varShowLoading`, `varShowToast`, `varToastType`,
`varToastMessage` and the other globals are born in `OnStart`: see
[app-onstart-template.md](app-onstart-template.md).

# Export button

Maturity: **stable** · Frequency: **occasional** (delivery by download or by email).

## Purpose

Button that asks the flow for a file with **all** the records of the current filter (the flow reads on the server, not the truncated gallery) and delivers it by `Download(varRet.url)` or by email.

## When to use / when not to use

**Use when**

- the user needs the full set for the filter, not what fits on the screen;
- the file is generated on the server.

**Do not use when**

- exporting only what is in the gallery (the gallery is truncated by the connector limit);
- generating a file on the client with `Concat` and `JSON`: it does not scale and loses accents.

## Anatomy

Tree of the main block (the order of `Children` is the z-index):

```text
xx-btn-exportar  (Button)
```

## Dependencies

- **Existing `fx*` tokens** in `assets/app-formulas-tokens.md`: `fxColorTextOnPrimary`, `fxColorPrimary`, `fxFont`, `fxBtnRadius`, `fxColorDisabled`, `fxColorDisabledText`, `fxBtnFontSize`, `fxMsgFalhaFlow`, `fxLayoutMargin`, `fxBtnWidth`, `fxBtnHeight`, `fxColorButtonCancel`, `fxColorButtonCancelHover`.
- **Tokens from the `COMPONENTS` block** (already in `assets/app-formulas-tokens.md`): `fxTxtExportar`.
- **Global variables** (born in `OnStart`, `assets/app-onstart-template.md`): `varShowLoading`, `varLoadingMessage`, `varRet`, `varUnidadeFiltro`, `varPedidoDe`, `varPedidoAte`, `varToastType`, `varToastMessage`, `varShowToast`.
- **Collections**: none.
- **Flows**: `app-flow-pedido-exportar`.
- The flow reads on the server with the filters received and returns `{ status, description, id, url }`.

## YAML

Destination: YAML pasted into Studio (`,` between arguments, `;` chains, `.` decimal). Paste in Code view > Paste code, with the screen (or a container) as the parent; change the `xx` prefix before pasting, because a control name is unique across the whole app.

```yaml
- xx-btn-exportar:
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
          varShowLoading || 'xx-gal-pedidos'.AllItemsCount = 0,
          DisplayMode.Disabled,
          DisplayMode.Edit
        )
      Fill: =fxColorPrimary
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =ColorFade(Self.Fill, -20%)
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =ColorFade(Self.Fill, -20%)
      OnSelect: |-
        =Set(varShowLoading, true);
        Set(varLoadingMessage, "Generating file...");
        IfError(
          Set(
            varRet,
            'app-flow-pedido-exportar'.Run(
              "csv",
              JSON(
                {
                  unidade: varUnidadeFiltro,
                  de: If(IsBlank(varPedidoDe), "", Text(DateAdd(Date(2000, 1, 1), varPedidoDe - 36524, TimeUnit.Days), "yyyy-mm-dd")),
                  ate: If(IsBlank(varPedidoAte), "", Text(DateAdd(Date(2000, 1, 1), varPedidoAte - 36524, TimeUnit.Days), "yyyy-mm-dd")),
                  status: Coalesce('xx-cbo-filtro-status'.Selected.Value, "")
                },
                JSONFormat.IgnoreUnsupportedTypes
              )
            )
          ),
          Trace("Flow transport failure: " & FirstError.Message);
          Set(varRet, Blank())
        );
        Set(varShowLoading, false);
        Set(varToastType, Coalesce(varRet.status, "error"));
        Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
        Set(varShowToast, true);
        If(
          varToastType = "success" && !IsBlank(varRet.url),
          Download(varRet.url)
        )
      PressedBorderColor: =ColorFade(Self.Fill, -30%)
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =ColorFade(Self.Fill, -30%)
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: =fxTxtExportar
      Tooltip: ="Generates the file with all the records of the current filter, read on the server."
      Width: =fxBtnWidth
      X: =fxLayoutMargin + 1180 - 210
      Y: =16
```

### Variation: delivery by email

The flow generates the file and sends it to the signed-in user; the toast confirms. Useful when the file is large or the browser blocks the download.

```yaml
- xx-btn-exportar-email:
    Control: Classic/Button@2.2.0
    Properties:
      BorderColor: =fxColorButtonCancel
      BorderThickness: =1
      Color: =fxColorTextOnPrimary
      DisplayMode: =If(varShowLoading || 'xx-gal-pedidos'.AllItemsCount = 0, DisplayMode.Disabled, DisplayMode.Edit)
      Fill: =fxColorButtonCancel
      Font: =fxFont
      FontWeight: =FontWeight.Semibold
      Height: =fxBtnHeight
      HoverBorderColor: =fxColorButtonCancelHover
      HoverColor: =fxColorTextOnPrimary
      HoverFill: =fxColorButtonCancelHover
      OnSelect: |-
        =Set(varShowLoading, true);
        Set(varLoadingMessage, "Generating file and sending...");
        IfError(
          Set(
            varRet,
            'app-flow-pedido-exportar'.Run("email", JSON(
              {
                unidade: varUnidadeFiltro,
                de: If(IsBlank(varPedidoDe), "", Text(DateAdd(Date(2000, 1, 1), varPedidoDe - 36524, TimeUnit.Days), "yyyy-mm-dd")),
                ate: If(IsBlank(varPedidoAte), "", Text(DateAdd(Date(2000, 1, 1), varPedidoAte - 36524, TimeUnit.Days), "yyyy-mm-dd")),
                status: Coalesce('xx-cbo-filtro-status'.Selected.Value, "")
              },
              JSONFormat.IgnoreUnsupportedTypes
            ))
          ),
          Trace("Flow transport failure: " & FirstError.Message);
          Set(varRet, Blank())
        );
        Set(varShowLoading, false);
        Set(varToastType, Coalesce(varRet.status, "error"));
        Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
        Set(varShowToast, true)
      PressedBorderColor: =fxColorButtonCancelHover
      PressedColor: =fxColorTextOnPrimary
      PressedFill: =fxColorButtonCancelHover
      RadiusBottomLeft: =fxBtnRadius
      RadiusBottomRight: =fxBtnRadius
      RadiusTopLeft: =fxBtnRadius
      RadiusTopRight: =fxBtnRadius
      Size: =fxBtnFontSize
      TabIndex: =0
      Text: ="Send by email"
      Width: =fxBtnWidth
      X: =fxLayoutMargin + 1180 - 210 - 220
      Y: =16
```

## Parameters to change

| In the block | Replace with | Note |
|---|---|---|
| `'app-flow-pedido-exportar'` | flow name in the app | return contract `{ status, description, id, url }`, all text |
| `"csv"` | format | closed vocabulary of the flow (`csv`, `xlsx`, `pdf`, `email`) |
| `unidade`, `de`, `ate`, `status` | the screen's real filters | the flow **revalidates** the scope: the screen only sends what the user sees; `de` and `ate` go as `yyyy-mm-dd` text (the screen variable is the `Ref_*` integer, which the flow does not understand) |
| `fxTxtExportar` | label | new token |

## Behavior

Destination of the formulas below: same as the YAML (`,` between arguments, `;` chains).

**`xx-btn-exportar`.DisplayMode**: disables with no records or while processing is under way

```powerfx
If(
  varShowLoading || 'xx-gal-pedidos'.AllItemsCount = 0,
  DisplayMode.Disabled,
  DisplayMode.Edit
)
```

**`xx-btn-exportar`.OnSelect**: builds the filters, calls the flow inside `IfError`, shows the toast and downloads the file only on success

```powerfx
Set(varShowLoading, true);
Set(varLoadingMessage, "Generating file...");
IfError(
  Set(
    varRet,
    'app-flow-pedido-exportar'.Run(
      "csv",
      JSON(
        {
          unidade: varUnidadeFiltro,
          de: If(IsBlank(varPedidoDe), "", Text(DateAdd(Date(2000, 1, 1), varPedidoDe - 36524, TimeUnit.Days), "yyyy-mm-dd")),
          ate: If(IsBlank(varPedidoAte), "", Text(DateAdd(Date(2000, 1, 1), varPedidoAte - 36524, TimeUnit.Days), "yyyy-mm-dd")),
          status: Coalesce('xx-cbo-filtro-status'.Selected.Value, "")
        },
        JSONFormat.IgnoreUnsupportedTypes
      )
    )
  ),
  Trace("Flow transport failure: " & FirstError.Message);
  Set(varRet, Blank())
);
Set(varShowLoading, false);
Set(varToastType, Coalesce(varRet.status, "error"));
Set(varToastMessage, Coalesce(varRet.description, fxMsgFalhaFlow));
Set(varShowToast, true);
If(
  varToastType = "success" && !IsBlank(varRet.url),
  Download(varRet.url)
)
```

## Accessibility

- Clear text label (`Export`); the `Tooltip` explains what comes out.
- The result is announced by the toast: consider reinforcing the error notice.

## Pitfalls

- `Download()` only opens in the browser; in the mobile app the behavior is different: test on each client.
- Without `IfError`, a transport failure leaves the overlay stuck.
- The returned URL expires: use a short-lived link and check that `status = "success"` before downloading.
- Sending the screen scope as authorization is useless: the flow derives what the user may export.

## Variations

- Multiple formats: one button per format (`csv`, `pdf`), same function.
- Batch export of a selection: send the ids from `colSelecionados`.

# Properties Studio rejects (PA2108)

Pasting a block with **one** property that the control type does not have brings down the **whole** block
(`PA2108`), without pointing to which one. The `pa.yaml` schema does not validate property names; what rejects
is Studio, on paste. This table is what `validar-telas.py` applies (T008).

## Contents

1. [Table of confirmed rejections](#1-table-of-confirmed-rejections)
2. [How to verify in Studio](#2-how-to-verify-in-studio)
3. [Alternatives](#3-alternatives)
4. [How to extend](#4-how-to-extend)

---

## 1. Table of confirmed rejections

`[verified: reference project]`: the control version matters.

| Property | Rejected on | What to use |
|---|---|---|
| `AccessibleLabel` | `Classic/Button@2.2.0`, `Button@0.0.45` | the button's `Text`; icon button: `Tooltip` |
| `FocusedBorderThickness` | every control type tested in the reference app | only `FocusedBorderColor`, and only on `Classic/TextInput`, `Classic/ComboBox`, `Classic/DatePicker` |
| `Live` | `Label@2.5.1` | per-field error text; see [accessibility.md](accessibility.md) |
| `Size` | `Classic/ComboBox@2.4.0`, `Classic/DatePicker@2.6.0` | the control's font cannot be changed; height via `Height` |
| `RadiusTopLeft`, `RadiusTopRight`, `RadiusBottomLeft`, `RadiusBottomRight` | `Rectangle@2.3.0`, `Classic/ComboBox@2.4.0`, `Classic/DatePicker@2.6.0`, `NumberInput@2.9.12`, `ModernTextInput@1.1.1`, `TextInput@0.0.54` | decorative rounded corner: `Classic/Button@2.2.0` with `DisplayMode: =DisplayMode.Disabled` and `DisabledFill` |

Accepted (attested) on `Classic/TextInput@2.3.2`: `Radius*` and `FocusedBorderColor`.

**Not attested** (no screen of the reference app uses them on that type; **test in a small
block** before spreading): `Role` on `Label`, `ItemAccessibleLabel`, `Selectable`,
`ShowScrollbar`, `DelayItemLoading` and `LoadingSpinner` on `Gallery`, `AutoStart`, `AutoPause` and
`OnTimerStart` on `Timer`, `PaddingTop` and `PaddingRight` on `Label`.

Learn lists some of these properties (for example `FocusedBorderThickness` and `AutoPause`
appear on the Timer control's page). **The documentation says it exists; Studio, with that
`Control@version` in the YAML, rejects it.** In a conflict, Studio wins.

## 2. How to verify in Studio

1. **Look in the app itself**: does the property already appear on that control **type and version**
   in a screen file? If so, it is attested. If not, do not assume.

Destination: terminal (Bash), not Power Fx.

```bash
grep -rn "AccessibleLabel" Frontend/
```

2. **Paste a minimal block** (a single control, with the property) on a test screen. `PA2108` on
   paste = rejected.
3. **Code view of an existing control** (right-click > View code): the properties that
   show up there are the ones accepted by that `Control@version`.
4. Optional (preview): the official MCP server (`describe_control`) lists the control's
   properties ([pa-yaml-format.md](pa-yaml-format.md) §11).
5. Found a new rejection? Record type, version and date here and in `RECUSADAS` in
   `scripts/validar-telas.py`, with a test.

## 3. Alternatives

| You wanted | Do this |
|---|---|
| accessible name for an icon button | `Tooltip` plus a descriptive `Text` when there is room |
| focus thickness | trust the control's default and check in the Accessibility checker |
| a region the reader announces | without `Live`: dismissible message, long duration, error in a modal |
| rounded corner on a rectangle | disabled `Classic/Button` |
| font size on a combo or datepicker | there is none; adjust `Height` and the control |

## 4. How to extend

The validator's table is in `RECUSADAS` and `RECUSADA_EM_TODOS` in `scripts/validar-telas.py`.
An exact rejection (type and version) becomes an **ERROR** T008; the same property on another version of the type becomes a
**WARNING** T008 ("confirm in Studio"). Every new item gets a test in
`tests/powerapps-canvas/`.

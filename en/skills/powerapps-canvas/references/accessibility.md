# Accessibility (WCAG AA) in Canvas

Checklist and limits for a Canvas ManualLayout + Classic app. When the Learn documentation and the
Studio of the reference projects conflict, **what Studio accepts wins**: several accessibility
properties from Learn are rejected in the YAML of these controls (PA2108); see
[nonexistent-properties.md](nonexistent-properties.md).

## Contents

1. [What is attested and what is not](#1-what-is-attested-and-what-is-not)
2. [Checklist](#2-checklist)
3. [Limitations that cannot be worked around](#3-limitations-that-cannot-be-worked-around)
4. [Tool](#4-tool)
5. [Sources](#5-sources)

---

## 1. What is attested and what is not

In a real app, the accessibility pass was **reverted in full** (hundreds of properties) because
Studio rejected the block (PA2108). `[verified: reference project]`

| Property | Status |
|---|---|
| `AccessibleLabel` | **rejected** on `Classic/Button@2.2.0` and `Button@0.0.45` (the button's accessible name comes from `Text`); **not attested** on the others: test |
| `FocusedBorderThickness` | **rejected** on every control of the reference app |
| `Live` | **rejected** on `Label@2.5.1` |
| `Role` (`Label.Role.Heading1`) | **not attested**: test before spreading it |
| `FocusedBorderColor` | attested on `Classic/TextInput`, `Classic/ComboBox` and `Classic/DatePicker` |
| `Tooltip` | attested (icon buttons, like the toast's `✕`) |
| `TabIndex` | attested (`0` participates, `-1` does not) |
| `Underline` | attested on `Label` and on a badge button |

Consequence: what Learn asks for and Studio rejects becomes **mitigation by design**: text on the
control itself, `Tooltip`, contrast, text beyond color, a clean tab order. When your
Studio accepts one more property, record it in the table and in the validator.

## 2. Checklist

**Accessible name**
- [ ] Button: the `Text` describes the action. Icon button: `Tooltip`. No `Classic/Button` with
      `Text: =""` takes part in tabbing (row background and decorative shape: `TabIndex: =-1`
      or `DisplayMode.Disabled`).
- [ ] A row checkbox with `Text: =""` has no name: a recorded limitation; mitigate with the
      column label and the selection counter.

**Focus order and keyboard**
- [ ] Only `TabIndex: =0` or `-1`. A positive value is discouraged and can break screen readers
      ("Check the order of the screen items" in the checker).
- [ ] To reorder focus, use a container instead of `TabIndex`; enable *Simplified tab
      index*.
- [ ] Modern control: `AcceptsFocus` (there is no `TabIndex`).

**Visible focus**
- [ ] `FocusedBorderColor` with at least 3:1 against the background on the attested inputs.
- [ ] `FocusedBorderThickness` equal to 0 is an error in the checker ("Focus isn't showing"), but the
      property is rejected in the YAML: confirm in the checker that focus shows with the control's
      default `[unverified]`.

**Contrast** (see [design-tokens.md](design-tokens.md) §3 and §4)
- [ ] Normal text >= 4.5:1; large text >= 3:1; interactive border and icon >= 3:1.
- [ ] Also check `Hover*` and `Pressed*` (`PressedColor` and `PressedFill` swapped give invisible
      text).
- [ ] Disabled text has no requirement, but it must be distinguishable.

**Do not rely on color alone**
- [ ] A state shown by color also has text, an icon or an underline (a badge with `Underline`, a
      selected row with a text badge, an active tab with bold text and a stroke).

**Dynamic regions**
- [ ] `Live` is rejected on `Label@2.5.1`: with no live region, a message that appears without a user
      action (toast, counter) is not announced. Mitigation: the toast is dismissible, lasts 6 to 15 s and
      an error that requires action goes in a modal (not a toast); record the limit for the client.

**Form**
- [ ] Required not only by `*`; error **per field**, not just in the toast; label >= 12; interactive
      target >= 24 by 24 px (WCAG 2.2, 2.5.8).

**Structure**
- [ ] A descriptive screen name (the reader reads the screen name); related content in a
      `GroupContainer`.
- [ ] One `Heading1` per screen via `Role`, **if** `Role` is attested in your Studio.

**Time**
- [ ] A timer that triggers a change allows canceling, adjusting or warning 20 s in advance
      (auto-refresh with an on/off switch, [timers-async.md](timers-async.md) §2).

## 3. Limitations that cannot be worked around

Documented ([Accessibility limitations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessible-apps-limitations)):

| Limitation | Effect on the kit's pattern |
|---|---|
| dialog and overlay are not supported; use a separate screen or `Notify()` | every modal; mitigate with a `Back` button and focus order |
| a tab is accessible only via the modern Tab list | Button + Rectangle tabs; migration is the medium-term recommendation |
| a 2D table only with the classic Data Table | gallery with labels |
| a "homemade" combo (TextInput + Gallery) is not accessible | use `Classic/ComboBox` |
| no reaction to specific keys (Esc, arrows) | the modal does not close with Esc |
| `SetFocus` in limited scenarios | focus does not move to the modal when it opens |
| no equivalent to `aria-hidden` | content behind the overlay stays in the tree |
| expandable section: report the state in the label | the button's `Text` carries "Show details" or "Hide details" |

## 4. Tool

**App checker > Accessibility** (top right corner of Studio). Resolve in the order errors,
warnings, tips. Relevant rules: *Missing accessible label*, *Focus isn't showing*, *Check the
order of the screen items* (fires with `TabIndex > 0`), *Add State indication text*,
*Revise screen name*, *HTML won't be accessible* (`HtmlViewer`). Run it after changing the palette or
adding a new block.

## 5. Sources

- [Accessibility checker](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessibility-checker)
- [Accessibility properties](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/properties-accessibility)
- [Color contrast](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessible-apps-color)
- [Live regions](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessible-apps-live-regions)
- [Accessibility limitations](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/accessible-apps-limitations)

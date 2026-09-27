---
name: font-size-and-pixels
description: content.json font size is written in pixels (pt x 4/3), not points, even though the spec's size field is always points. Android renders from this value directly; Windows ignores it.
metadata:
  type: constraint
  status: proven
  related: [elements/text, constraints/width-factor-and-line-pitch]
---

# Font size is written in pixels in `content.json`

A DSL spec's `size:` field is always **points**, and stays points — do not
convert it yourself when writing a spec. But the engine writes the value into
`content.json` as `round(pt × 4/3)` — i.e. pixels — while the paired RTF field
keeps `\fs = pt × 2`. So `size: 48` in a spec produces JSON `64` and RTF `\fs96`.

**Why this matters if you ever touch `raw:` JSON directly:** Windows renders
text from the RTF field and ignores the plain JSON size number entirely. This
means a wrong JSON size number can look completely correct on Windows and still
be wrong. Android has no RTF fallback — it renders directly from the JSON
number — so a file with the JSON size left in points (not converted to pixels)
will render roughly 25% too small on Android while looking fine on Windows.

Rule: if hand-writing a text element in `raw:`, the JSON size field must be
`round(pt × 4/3)`, and the RTF `\fs` value must independently be `pt × 2`. Do
not assume these can be derived from each other casually — get both right.

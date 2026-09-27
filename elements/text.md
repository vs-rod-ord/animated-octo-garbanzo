---
name: text
description: The text element — role presets, sizing, alignment, and the RTF rule that actually drives rendering.
metadata:
  type: element
  status: proven
  dsl_support: full
  related: [spec/dsl-spec, constraints/font-size-and-pixels, constraints/width-factor-and-line-pitch]
---

# `text`

```yaml
- text:
    content: Photosynthesis           # required
    role: title | heading | body | caption | label   # default body
    size: 40          # pt, overrides role default
    font: Poppins     # any of 28 known families — see constraints/font-portability.md
    bold: true        # role may default this (title/heading → bold)
    color: "#1A1A2E"  # 6-digit RGB; engine converts to 8-digit ARGB for text fill
    align: left | center | right | justify   # default left
    at: top
    width: 1500       # wrap width; height is ALWAYS computed, never specified
```

## Role presets

| Role    | Size | Bold | Default width |
|---------|------|------|---------------|
| title   | 64   | yes  | 1760 (full content width) |
| heading | 48   | yes  | 1760 |
| body    | 34   | no   | 1500 |
| caption | 24   | no   | 1200 |
| label   | 28   | no   | fit-to-text |

## Rules

- **Never set `height`.** It is always computed from the wrapped line count and
  font metrics. Specifying it yourself is not supported and will be ignored or
  rejected.
- **Alignment is driven by RTF, not the JSON `text-align` field.** The engine
  generates `\qc`/`\qr`/`\qj` RTF codes for center/right/justify. If you ever
  emit a `text` element via `raw:` instead of the DSL, setting `text-align` in
  JSON alone will not actually center anything on Windows — see
  [`constraints/font-size-and-pixels.md`](../constraints/font-size-and-pixels.md)
  for the related Windows-renders-from-RTF fact.
- **No inline mixed formatting.** One bold word mid-sentence is not supported —
  myViewBoard textareas can't flow multiple styles inline. Use separate `text`
  elements, or accept uniform styling per block.
- `size:` in the spec is always **points**. Do not convert it yourself — the
  engine handles the points→pixels JSON conversion. See
  [`constraints/font-size-and-pixels.md`](../constraints/font-size-and-pixels.md).

## Worked `content.json` — a `textarea` element

This is what `text: {content: "Hello World!", size: 40, font: "Segoe UI"}`
becomes, taken directly from the reference engine's own construction logic
(not reverse-engineered from a doc — this is the literal shape it builds):

```json
{
  "textarea": {
    "id": "UUID",
    "x": 100.0,
    "y": 150.0,
    "width": 800.0,
    "height": 200.0,
    "custom-data": "{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0\\fnil\\fcharset0 Segoe UI;}}\\viewkind4\\uc1\\pard\\f0\\fs80\\cf0 Hello World!\\par}",
    "custom-data-tag": "RTFxamlStr_UWP",
    "matrix": "1,0,0,0,1,0,0,0,1",
    "text-blocks-container": [
      {
        "paragraph": {
          "id": "UUID",
          "font-size": 53.0,
          "text-align": "left",
          "text-list-container": [
            {
              "text": {
                "id": "UUID",
                "text": "Hello World!",
                "font-family": "Segoe UI",
                "font-size": 53.0,
                "fill": "#FF1A1A2E",
                "font-style": "normal",
                "font-stretch": "normal",
                "font-weight": "normal",
                "text-decoration": "normal",
                "baseline-align": "baseline",
                "fill-opacity": 1.0
              }
            }
          ]
        }
      }
    ]
  }
}
```

Field-by-field rules this example encodes — every one of these is a real,
previously-confirmed failure mode if gotten wrong, not a style preference:

- `font-size` in **both** `paragraph` and `text` is `round(pt × 4/3)` — here
  `40pt → 53.0` — never the raw point value. See
  [`constraints/font-size-and-pixels.md`](../constraints/font-size-and-pixels.md).
  The RTF `\fs` value is independently `pt × 2` (`\fs80` for 40pt) — the two
  numbers are related but each computed separately, not derived from each
  other in code.
- `fill` on the `text` object is **8-digit `#AARRGGBB`** (`#FF1A1A2E`), not
  6-digit — text fill and shape fill use different digit counts. See
  [`elements/shape.md`](shape.md) for the shape-side (6-digit) rule.
- `text-align` in JSON is `"left"`/`"center"`/`"right"`/`"justify"`, but this
  field is **cosmetic on Windows** — actual rendering is driven by the RTF
  alignment code (`\qc`/`\qr`/`\qj`) inside `custom-data`, which must be kept
  in sync with it. Omitting the RTF code while only setting JSON
  `text-align: "center"` will not center anything on Windows.
- `custom-data-tag` is always the literal string `"RTFxamlStr_UWP"`.
- No `additional` array entry is needed for a plain `textarea` — unlike shapes,
  text elements aren't referenced there.


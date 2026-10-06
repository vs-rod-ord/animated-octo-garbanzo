---
name: bullets
description: The bullets compound element — a list of items, each expanded to a shape plus a textarea by the engine.
metadata:
  type: element
  status: proven
  dsl_support: full
  related: [spec/dsl-spec, elements/text, elements/shape, constraints/text-wrapping-and-overlap]
---

# `bullets`

```yaml
- bullets:
    items: [Intro, Demo, Q&A]         # required; strings only in v1
    bullet: circle | square | dash | number   # default circle
    size: 34                          # item font size
    color: "#1A1A2E"                  # text color
    bullet_color: "#4F46E5"           # shape fill; default = accent color
    at: left
    width: 1200
```

Expands to one textarea per item plus one shape per item — this is a compound
element, not a single JSON element. Row pitch is computed from real font
metrics; items may wrap to multiple lines, and pitch adapts per item rather than
using a fixed value. `number` bullets are label textareas, not shape+number.
**Bullet items are narrow (often ~1200 canvas units or less) and wrap
readily** — when generating `content.json` directly, estimate each item's
wrapped height per
[`constraints/text-wrapping-and-overlap.md`](../constraints/text-wrapping-and-overlap.md)
before placing the next item's bullet + textarea pair, or consecutive items
will overlap as soon as any item's text wraps to two lines.

## Rules

- Items are plain strings only in this DSL version — no per-item rich formatting.
- Do not attach `animate:` or `link:` to a `bullets` element — it expands to
  multiple objects with no single thing to target. Use individual `text`/`shape`
  elements instead if you need a linkable or animatable list item.
- Bullet diameter and vertical centering are non-obvious and engine-computed —
  do not hand-calculate them even in a `raw:` fallback. Confirmed correct
  formula: diameter ≈ 0.70×font-size (matches cap-height), vertical offset
  quadratic-scaled from a value confirmed at fs=53. An earlier assumption
  (diameter ≈ 1×font-size) was disproven by isolated real-device testing — a
  1×fs circle visibly overshoots the text's cap-height regardless of where its
  center is placed.

## Worked `content.json` — one bullet item (circle style)

`bullets:` is not its own element type in `content.json` — each item expands
to one `ellipse` (or `polygon` for square/dash, or a `textarea` for number
style) plus one `textarea`, both ordinary page elements. This is item 1 of a
circle-bulleted list at `fs=34`, bullet diameter `0.70 × 34 ≈ 24`:

```json
{
  "ellipse": {
    "id": "UUID-bullet-1",
    "is-pie": false, "x": 0.0, "y": 0.0,
    "width": 24.0, "height": 24.0,
    "rx": 12.0, "ry": 12.0, "cx": 12.0, "cy": 12.0,
    "angle-start": 0.0, "angle-end": 359.9,
    "fill": "#4F46E5", "stroke": "#4F46E5", "stroke-width": 0.0,
    "fill-opacity": 1.0, "stroke-opacity": 0.0,
    "show-length-measurement": "false〈3x-separator〉true,False,〈3x-separator〉true,False,",
    "show-angle-measurement": "",
    "matrix": "1,0,120.0,0,1,258.0,0,0,1",
    "boundary": "108.0 246.0 132.0 270.0"
  }
}
```

with its own `additional` entry (see [`elements/shape.md`](shape.md) for the
ellipse `additional` shape), plus a sibling `textarea` for the item text (see
[`elements/text.md`](text.md) for that element's exact shape) positioned to
the right, with a 35-unit gap between the bullet's right edge and the text's
left edge. Both elements are independent, ordinary page elements — there is no
parent "bullets" object wrapping them in the output. (`〈3x-separator〉`
above is a placeholder for three literal `『` characters — see
[`constraints/raw-element-mechanical-checks.md`](../constraints/raw-element-mechanical-checks.md)
for the exact required string; markdown rendering can mangle repeated
multi-byte separator characters, so double-check the literal value against
that file rather than copying it from here.)

Do not hand-place the bullet's vertical offset by eyeballing it — see the
diameter/offset rule above.

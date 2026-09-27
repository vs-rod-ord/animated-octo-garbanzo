---
name: shape
description: The shape element and its full kind catalog — polygons, ellipses, 3D solids, rounded rectangles.
metadata:
  type: element
  status: proven
  dsl_support: full
  related: [spec/dsl-spec, elements/animate-and-link]
---

# `shape`

```yaml
- shape:
    kind: rect        # see catalog below — unknown kind is a build error
    at: [400, 300]
    width: 400
    height: 300
    fill: "#FFE600"   # 6-digit RGB (shapes are RGB, text is ARGB — do not mix these up)
    stroke: "#FF9077"
    stroke_width: 3
    label: "Step 1"   # optional; centered text, engine-computed
    label_size: 28
    label_color: "#1A1A2E"
```

## Shape kind catalog

Only these kinds are valid. An unknown kind is a build error — do not invent one.

| DSL kind | Notes |
|----------|-------|
| `rect`, `square` | |
| `triangle`, `right-triangle` | |
| `trapezoid`, `parallelogram` | |
| `circle` | rx=ry |
| `oval` | rx≠ry |
| `polygon-N` (N=3–12) | regular N-gon |
| `star` | 5-pointed |
| `quadrant` | fixed 2×2 grid — myViewBoard offers no other split |
| `points: [[x,y], …]` | freeform outline, straight segments only |
| `cube`, `sphere`, `hemisphere`, `cylinder`, `cone`, `truncated-cone`, `dihedral`, `rectangular-pyramid`, `triangular-pyramid` | flat fill only; stroke draws internal construction lines |
| `rounded-rect` | see below |

```yaml
- shape: {kind: rounded-rect, at: [400, 300], width: 400, height: 250,
          radius: 32, fill: "#4C6FFF"}
```

`rounded-rect` has no native corner-radius support in myViewBoard's polygon
element, so the engine builds it as a hand-drawn path rather than a simple
polygon. Optional `radius`/`corner_radius` (canvas units, default 15% of the
shorter side, clamped to `min(width,height)/2`).

## Rules

- Fill/stroke colors are always 6-digit `#RRGGBB` for shapes — never 8-digit.
  8-digit `#AARRGGBB` is a text-fill-only convention; mixing the two up is a
  common `raw:` mistake. See
  [`constraints/ai-pen-color-format.md`](../constraints/ai-pen-color-format.md)
  for a related, more severe version of this mistake.
- 3D solids (`cube`, `sphere`, etc.) render as flat fills only — there is no
  real 3D shading in this element type.

## Worked `content.json` — `polygon` (covers rect/triangle/trapezoid/star/polygon-N)

```json
{
  "polygon": {
    "id": "UUID",
    "x": 0.0,
    "y": 0.0,
    "width": 400.0,
    "height": 300.0,
    "points": "400,300 800,300 800,600 400,600",
    "fill": "#FFE600",
    "stroke": "#FF9077",
    "stroke-width": 3.0,
    "fill-opacity": 1.0,
    "stroke-opacity": 1.0,
    "is-show-incircle": false,
    "is-show-outcircle": false,
    "show-length-measurement": "false『『『true,False,『『『true,False,『『『true,False,『『『true,False,",
    "show-angle-measurement": "true,『『『true,『『『true,『『『true,",
    "matrix": "1,0,0,0,1,0,0,0,1"
  }
}
```

Every `polygon` needs a matching top-level `additional` array entry:

```json
{
  "element": {
    "id": "UUID",
    "ref": "<the polygon's own id, above>",
    "flip": "none",
    "is-locked": false,
    "is-moveable-locked": false,
    "is-replicate": false
  }
}
```

**`x`/`y` are always `0.0`** — absolute position lives in `points`, which
holds space-separated absolute `x,y` pairs, not local/relative coordinates.
`fill`/`stroke` are 6-digit `#RRGGBB` (never 8-digit — that's text-only, see
[`elements/text.md`](text.md)). The `show-length-measurement` /
`show-angle-measurement` strings above use the confirmed
`『『『` (triple-character, U+300E) separator — see
[`constraints/raw-element-mechanical-checks.md`](../constraints/raw-element-mechanical-checks.md)
for why a double separator here silently crashes the file on Android.

## Worked `content.json` — `ellipse` (covers `circle`/`oval`)

```json
{
  "ellipse": {
    "id": "UUID",
    "is-pie": false,
    "x": 0.0,
    "y": 0.0,
    "width": 303.0,
    "height": 303.0,
    "rx": 150.0,
    "ry": 150.0,
    "cx": 150.0,
    "cy": 150.0,
    "angle-start": 0.0,
    "angle-end": 359.9,
    "fill": "#FFCDD2",
    "stroke": "#D32F2F",
    "stroke-width": 3.0,
    "fill-opacity": 1.0,
    "stroke-opacity": 1.0,
    "show-length-measurement": "false『『『true,False,『『『true,False,",
    "show-angle-measurement": "",
    "matrix": "1,0,810.0,0,1,390.0,0,0,1",
    "boundary": "808.5 388.5 1111.5 691.5"
  }
}
```

Same `additional` entry shape as `polygon`, above. **`cx`/`cy` always equal
`rx`/`ry`** (this is a local center, not the absolute one) — absolute canvas
position is set entirely through the `matrix` translation:
`"1,0,{Cx−rx},0,1,{Cy−ry},0,0,1"`. `boundary` (`"x1 y1 x2 y2"`, space-separated)
is required — omitting it risks mis-placement.

## Worked `content.json` — `quadrant`

Its own top-level element type, not a `polygon` variant. Only one confirmed
shape exists — a 2×2 grid, built as one continuous `points` path tracing the
outer rectangle plus the two internal divider lines:

```json
{
  "quadrant": {
    "id": "UUID",
    "x": 0.0,
    "y": 0.0,
    "width": 266.26,
    "height": 241.61,
    "points": "1170.75,541.50 1431.00,541.60 1431.00,777.01 1170.75,777.11 1170.75,659.26 1431.00,659.26 1431.00,541.50 1300.88,541.50 1300.88,777.01 1170.75,777.01",
    "fill": "#FFFFFF",
    "fill-opacity": 0.0,
    "stroke": "#000000",
    "stroke-width": 6.0,
    "stroke-opacity": 1.0,
    "matrix": "1,0,0,0,1,0,0,0,1"
  }
}
```

Needs the same `additional` entry shape as `polygon`.

## Worked `content.json` — 3D solids (`pseudo3Dshape`)

A dedicated element type distinguished by a `3Dtype` field — **not** a
`polygon` with a 3D flag, despite how it looks in the shape palette. `points`
holds only **two** coordinates here (bounding-box corners), unlike `polygon`'s
full vertex list, and — like `ellipse` — it requires a `boundary` field:

```json
{
  "pseudo3Dshape": {
    "id": "UUID",
    "x": 245.98,
    "y": 281.25,
    "width": 216.77,
    "height": 203.25,
    "points": "0,0 216.77,203.25",
    "boundary": "242.98 278.25 465.75 487.50",
    "3Dtype": "cube",
    "fill": "#FFFFFF",
    "fill-opacity": 0.0,
    "stroke": "#000000",
    "stroke-opacity": 1.0,
    "stroke-width": 6.0,
    "matrix": "1,0,3,0,1,3,0,0,1"
  }
}
```

`3Dtype` values: `cube`, `sphere`, `hemisphere`, `dihedral`, `cylinder`, `cone`,
`truncated-cone`, `rectangular-pyramid`, `triangular-pyramid`. A filled 3D
solid (`fill-opacity: 1.0`) renders as a **single flat fill color** — there is
no shading, gradient, or lighting. The illusion of 3D structure comes entirely
from `stroke`-colored construction lines (e.g. a sphere's equator line) drawn
on top of the flat fill, using the same stroke color as the outer silhouette.
Needs the same `additional` entry shape as `polygon`.

## Worked `content.json` — `rounded-rect` (via `AI-pen`)

`polygon` has no corner-radius field, so a rounded rectangle is built as an
`AI-pen` path instead — this is the one shape kind that isn't a `polygon`
variant under the hood. Taken directly from the reference engine:

```json
{
  "AI-pen": {
    "id": "UUID",
    "matrix": "1,0,120,0,1,400,0,0,1",
    "foreground-objects-container": [
      {
        "path": {
          "id": "UUID",
          "x": 0.0,
          "y": 0.0,
          "width": 480.0,
          "height": 280.0,
          "fill-opacity": 1.0,
          "fill": "#4C6FFF",
          "stroke-width": 0.0,
          "stroke-opacity": 0.0,
          "stroke-miter-limit": 10.0,
          "lineshape-start": "round",
          "lineshape-end": "round",
          "lineshape-join": "round",
          "stroke": "#4C6FFF",
          "data": "M28,0 L452,0 A28,28 0 0 1 480,28 L480,252 A28,28 0 0 1 452,280 L28,280 A28,28 0 0 1 0,252 L0,28 A28,28 0 0 1 28,0 Z",
          "matrix": "1,0,120,0,1,400,0,0,1"
        }
      }
    ],
    "background-objects-container": [
      {
        "path": {
          "id": "UUID",
          "x": 0.0, "y": 0.0, "width": 480.0, "height": 280.0,
          "fill-opacity": 0.3,
          "fill": "#4C6FFF",
          "stroke-width": 0.5,
          "stroke-opacity": 0.0,
          "stroke-miter-limit": 10.0,
          "lineshape-start": "round", "lineshape-end": "round", "lineshape-join": "round",
          "stroke": "#4C6FFF",
          "data": "M28,0 L452,0 A28,28 0 0 1 480,28 L480,252 A28,28 0 0 1 452,280 L28,280 A28,28 0 0 1 0,252 L0,28 A28,28 0 0 1 28,0 Z",
          "matrix": "1,0,120,0,1,400,0,0,1"
        }
      }
    ]
  }
}
```

`AI-pen`'s `additional` entry has **no `flip` field**, unlike every other
shape type above — this is the one exception:

```json
{
  "element": {
    "id": "UUID",
    "ref": "<the AI-pen's own id, above>",
    "is-locked": false,
    "is-moveable-locked": false,
    "is-replicate": false
  }
}
```

Three confirmed rules, each a real failure mode:

1. **`matrix` must be a genuine scale/translate matrix** (`"1,0,{x},0,1,{y},0,0,1"`),
   never identity (`"1,0,0,0,1,0,0,0,1"`) — an identity matrix with an empty
   `background-objects-container` renders as a completely invisible shape.
2. **Path coordinates must equal the real on-canvas size** (scale=1.0) — do
   not shrink them into a small local space and scale up via the matrix.
   Fractional/tiny local arc coordinates render with flattened (unrounded)
   corners the first time the file opens, only fixing themselves after a
   manual re-save inside myViewBoard.
3. **Keep `stroke-width: 0.0` (fill-only, borderless).** A stroked rounded-rect
   path renders visibly *thicker* on the curved corners than the straight
   edges — a confirmed, unfixed `AI-pen` rendering limitation (it behaves like
   a pressure-sensitive hand-drawn pen stroke, not a uniform-width vector
   border). There is no known path-based fix; don't attempt a bordered
   rounded-rect with this technique. Also see
   [`constraints/ai-pen-color-format.md`](../constraints/ai-pen-color-format.md)
   for a separate, more severe `AI-pen` color-format trap.

---
name: ai-pen
description: AI-pen as a true-vector SVG path renderer — icons, custom shapes, rounded rectangles. Worked content.json, required container pattern, sourcing paths, and the starter helper that builds it safely.
metadata:
  type: element
  status: proven
  dsl_support: partial
  related: [elements/svg-image, constraints/ai-pen-path-rules, constraints/ai-pen-color-format, elements/shape, spec/starter-helpers]
---

# `AI-pen` — vector SVG paths on the canvas

There is no native "SVG element" in OLF. `AI-pen` (normally the ink tool) renders
**filled arbitrary SVG path data** as a crisp, resolution-independent vector that
stays sharp at any size. Use it for icons, simple illustrations, custom shapes and
rounded rectangles. For finished artwork that won't be scaled, or for SVG features
paths can't express (gradients), see [`svg-image.md`](svg-image.md) instead.

| Need | Use |
|---|---|
| Icon / silhouette that the user may resize | **`AI-pen`** (this file) |
| Rounded rectangle "card" | **`AI-pen`** via `ai_pen_rounded_rect` |
| Gradient / clipped / designer-exported art | `image` + `image/svg+xml` ([`svg-image.md`](svg-image.md)) |
| SVG text in a custom font | Not available from the starter; see "Not covered" below |

## Easiest, safest way: the starter helper

Paste `starter/olf_starter.py`, then `starter/olf_starter_svg.py`
(see [`spec/starter-helpers.md`](../spec/starter-helpers.md)):

```python
p = Doc("demo").page()                                       # (use doc = Doc(...) in real code)
p.add(ai_pen_icon(["M10 20v-6h4v6h5v-8h3L12 3L2 12h3v8z"],   # SVG path data, any commands
                  x=340, y=440, size=200, vb=24, fill="#1565C0"))
p.add(ai_pen_rounded_rect(80, 80, 600, 300, 40, "#E0F2FE"))  # card; add FIRST = behind text
paths, (vw, vh), warns = svg_to_paths(svg_text)              # from pasted <svg> text
p.add(ai_pen_icon(paths, x=100, y=100, size=200, vb=max(vw, vh)))
```

`ai_pen_icon` scrubs every path to **absolute `M L C A Z` only** (relative,
`H V Q S T` converted exactly), keeps local coordinates **non-negative** (folding any
offset into the matrix), forces plain `#RRGGBB` fills, and writes the required
container pattern below. Pass several `d` strings (or `(d, "#hex")` tuples) for
multi-path / multi-colour icons. Then run the validator.

## Required container pattern (load-bearing — do not simplify)

```json
{
  "AI-pen": {
    "id": "UUID",
    "matrix": "8.3333,0,340,0,8.3333,440,0,0,1",
    "foreground-objects-container": [
      {"path": {
        "id": "UUID", "x": 0.0, "y": 0.0, "width": 24.0, "height": 24.0,
        "fill-opacity": 1.0, "fill": "#1565C0",
        "stroke-width": 0.0, "stroke-opacity": 0.0, "stroke-miter-limit": 10.0,
        "lineshape-start": "round", "lineshape-end": "round", "lineshape-join": "round",
        "stroke": "#1565C0",
        "data": "M10 20L10 14L14 14L14 20L19 20L19 12L22 12L12 3L2 12L5 12L5 20Z",
        "matrix": "8.3333,0,340,0,8.3333,440,0,0,1"
      }}
    ],
    "background-objects-container": [
      {"path": {
        "id": "UUID", "x": 0.0, "y": 0.0, "width": 24.0, "height": 24.0,
        "fill-opacity": 0.3, "fill": "#1565C0",
        "stroke-width": 0.5, "stroke-opacity": 0.0, "stroke-miter-limit": 10.0,
        "lineshape-start": "round", "lineshape-end": "round", "lineshape-join": "round",
        "stroke": "#1565C0",
        "data": "M10 20L10 14L14 14L14 20L19 20L19 12L22 12L12 3L2 12L5 12L5 20Z",
        "matrix": "8.3333,0,340,0,8.3333,440,0,0,1"
      }}
    ]
  }
}
```

and in the single root `additional` array — **no `flip` field** for AI-pen:

```json
{"element": {"id": "UUID", "ref": "<the AI-pen's id>", "is-locked": false,
             "is-moveable-locked": false, "is-replicate": false}}
```

Rules this encodes (each from a real failure):

- **Matrix is a real scale/translate**: `"s,0,tx,0,s,ty,0,0,1"` with
  `s = display_px / icon_viewbox` and `tx,ty` the canvas top-left. The **same matrix
  string** goes on the `AI-pen` and on every path inside it. An identity matrix with
  an empty background container renders **invisible**.
- **`background-objects-container` must be populated**, mirroring each foreground
  path at `fill-opacity: 0.3`. Empty = risk of an invisible shape.
- `width`/`height` of each path = the icon's own viewBox size in local units.
- `data` is the path string; `fill`/`stroke` are plain `#RRGGBB`
  ([`constraints/ai-pen-color-format.md`](../constraints/ai-pen-color-format.md)).
- Filled look: `fill-opacity: 1.0`, `stroke-width: 0.0`, `stroke-opacity: 0.0`.
- Icons from a set with a different viewBox: Material/MDI 24, Heroicons 24,
  Tabler 24 (stroke-based — avoid), Bootstrap 16, Phosphor 256. Scale =
  `size / viewBox`.

## Where path data comes from (your sandbox has no internet)

1. **Write it yourself** from simple shapes — often the safest option (see the path
   rules file: independent solid subpaths render reliably).
2. **The user pastes an `<svg>`** — pass it to `svg_to_paths()`.
3. **A browsing/fetch tool** (if you have one outside the sandbox): Iconify,
   `https://api.iconify.design/{prefix}/{name}.svg` (e.g. `mdi/home`), no key; copy
   the `d` strings into your code. Prefer **filled** sets (`mdi`, `material-symbols`,
   `ph` fill, `bi` fill) over outline/stroke sets.
4. Never invent a "plausible-looking" path from memory for a complex icon you
   can't reproduce exactly — a wrong path still renders, just as the wrong picture.

## Always check the icon before using it

Read [`constraints/ai-pen-path-rules.md`](../constraints/ai-pen-path-rules.md): some
stock icons (rings, leaves, drops with cut-outs) render malformed in myViewBoard even
though they are valid SVG. `ai_pen_icon` can't fully detect this; use independent
solid subpaths whenever in doubt. The helper `hole_risk(parse_path(d))` flags the
common ring/donut case.

## Rounded rectangle (card)

`ai_pen_rounded_rect(x, y, w, h, r, fill)` is identical to the reference engine's
builder (field-for-field match verified). Keep `stroke_width=0` — strokes render
visibly thicker on the curved corners. Its path uses local coordinates equal to the
real size (scale 1.0); never shrink the local space and compensate with a matrix
scale (corners come out sharp on first open). For the older worked JSON of the same
element, see [`shape.md`](shape.md).

## Groups, rotation, per-element tools

Not covered by the starter or this corpus — say so rather than guessing a shape.

## Not covered: text as vector outlines

Converting font glyphs to `AI-pen` outlines (the only confirmed way to show a
**non-installed custom font** identically on Windows) needs `fontTools` and
HarfBuzz, which are not in the standard library. The confirmed requirements if you
have them: path pen must emit only `M L C Z` (convert quadratics to cubics), local
coordinates non-negative, one compound path per word, positions from HarfBuzz
advances. Otherwise use a normal `textarea` with a safe font
([`constraints/font-portability.md`](../constraints/font-portability.md)).

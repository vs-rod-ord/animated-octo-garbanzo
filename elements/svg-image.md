---
name: svg-image
description: Putting an SVG on the canvas as an image element (mime image/svg+xml) — what renders, what silently fails, the author-8x-oversize rule, and why animation and SVG text don't work.
metadata:
  type: element
  status: proven
  dsl_support: via-raw
  related: [elements/ai-pen, elements/image, constraints/ai-pen-path-rules, constraints/android-vs-windows-divergence, spec/starter-helpers]
---

# SVG as an `image` element

An `image` element can take an `.svg` file as its source (stored in the zip under
`images/`, like a PNG). It renders correctly at authored size but is
**rasterised once, not true vector** — it pixelates if the user enlarges it past
its intrinsic resolution. For icons and shapes that must stay sharp when resized,
use [`AI-pen`](ai-pen.md) instead.

```json
{"image": {"id": "UUID", "x": 560.0, "y": 253.0, "width": 800.0, "height": 533.0,
           "mime-type": "image/svg+xml", "source": "images/badge.svg",
           "matrix": "1,0,0,0,1,0,0,0,1"}}
```

No `additional` entry is needed. The `.svg` file must exist at exactly that path
inside the zip (the validator checks).

Starter helper (paste `olf_starter.py` then `olf_starter_svg.py`):

```python
add_svg_image(page, doc, "badge", svg_text, x=560, y=260, w=800, h=520)
```

It lints the SVG, rewrites the root `width`/`height` to **8× the display size**,
writes `images/badge.svg`, and adds the element. Keep the SVG's `viewBox` and the
display aspect ratio the same or the picture is distorted.

## The 8× rule

myViewBoard rasterises the SVG at (or near) its **own intrinsic size**, not its
on-canvas display size. An SVG authored at 200×133 shown in a 200×133 box already
looks blurry; the same art authored at 1600×1064 (8×) stays sharp even after being
dragged much larger. **Always set the SVG's root `width`/`height` ~8× the intended
display size.** No downside seen at 8×; don't go far beyond without testing.

## What renders inside an image-element SVG

The renderer is a static SVG→WPF converter (not a browser). Confirmed on Windows:

| SVG feature | Result |
|---|---|
| `<linearGradient>` fills | **Works** |
| `<clipPath>` | **Works** |
| Internal `<style>` with CSS class selectors | **Works** (Figma/Illustrator exports are fine) |
| `<pattern>` fill | **FAILS — renders solid BLACK** (worse than blank). Never use. |
| `<mask>` | **FAILS** — ignored, flat opaque shape |
| `<text>` (any font) | **FAILS — renders nothing** on Windows. Convert text to paths or use a normal `textarea` over the picture. |
| `<use>` / `<symbol>` | **FAILS** — blank. Inline the geometry first. |
| `<foreignObject>` | Dropped silently (rest of SVG still renders; cross-platform) |
| SMIL `<animate>`, `<animateTransform>`, `<set>` | **Static.** Parsed but never played; frozen at frame 0, Windows and Android |
| CSS `@keyframes`, JS | Static / not run |
| Embedded `@font-face` + `<text>` | Windows: nothing. **Android only:** renders the embedded font. Android-only trick; don't rely on it for cross-platform files |

Rule of thumb: **flatten before embedding** — inline `<use>`, convert text to
outlines, replace patterns/masks with plain shapes or pre-rendered raster, bake
transforms. Gradients, clipPaths and CSS classes need no pre-processing.

`svg_lint(svg_text)` and the validator warn on the failing features.

## Animation

There is no SVG-native animation route in OLF (the renderer has no animation
runtime). For tap-to-reveal use OLF's own `animate:` fade-in/fade-out on the
element ([`animate-and-link.md`](animate-and-link.md)). Real animation needs an HTML
activity layer — out of scope for this corpus.

## SVG features cheat-sheet: which route?

- Plain icon / silhouette, may be resized → `AI-pen`
- Gradient or clipped artwork, fixed size → `image` SVG (8× oversized)
- Anything needing text in the picture → draw the text as a normal `textarea` on
  top of the picture
- Photo-like or complex art → rasterise to PNG/JPEG and use `elements/image.md`
- RTF-embedded SVG (`\svgblip`) → **never**; renders blank. RTF pictures are raster only.

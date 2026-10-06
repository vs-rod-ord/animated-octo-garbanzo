---
name: ai-pen-path-rules
description: Which SVG paths render correctly as AI-pen — allowed commands, non-negative coordinates, the opposite-winding "donut hole" trap, rounded-rect stroke limit, and how to vet a stock icon.
metadata:
  type: constraint
  status: proven
  related: [elements/ai-pen, constraints/ai-pen-color-format, elements/svg-image]
---

# Rules for SVG path data inside `AI-pen`

All confirmed in real myViewBoard tests (2026-06 → 2026-09). `ai_pen_icon()` in
`starter/olf_starter_svg.py` applies rules 1–3 automatically; rule 4–6 need judgement.

## 1. Use absolute `M L C A Z` only

Every path ever confirmed working uses only `M`, `L`, `C`, `A`, `Z`. A font-library
glyph serialiser that emitted `H`/`V` shorthand and quadratic `Q` rendered
**completely invisible**. Convert before use: `H/V → L`, `Q/T/S → C` (a quadratic
`Q0→Q→P1` is exactly the cubic with `C1 = P0 + 2/3(Q−P0)`, `C2 = P1 + 2/3(Q−P1)`),
relative → absolute. Never trust a library's default SVG output for this renderer —
those optimise for file size, not for this parser. (The validator warns on anything
else.)

## 2. Local coordinates must be non-negative and at real scale

- All local path coordinates stay inside `[0,w]×[0,h]`. Glyph-style baseline paths
  with negative local Y rendered invisible even when otherwise correct. Shift the
  path so its minimum corner is at `(0,0)` and fold the offset into the matrix
  translate.
- Keep local coordinates at real magnitude and the matrix scale near what you need;
  don't divide coordinates by 10 and compensate with a 10× matrix scale (a
  rounded-rect built that way opened with sharp corners until re-saved).

## 3. Colours: plain `#RRGGBB` only

A non-hex `fill`/`stroke` (e.g. `url(#grad1)`, `currentColor`, `red`) is ignored on
Windows but **crashes the file open on Android**. See
[`ai-pen-color-format.md`](ai-pen-color-format.md). AI-pen has **no gradient
mechanism**: use a solid colour, or use an `image`-element SVG for gradients
([`elements/svg-image.md`](../elements/svg-image.md)).

## 4. The "donut hole" / opposite-winding trap

Paths that make a ring, hollow centre or internal cut-out by overlapping two contours
wound in **opposite directions** (or one self-overlapping subpath doing the same) can
render malformed or blank in myViewBoard **even though they are valid SVG** and look
perfect in other renderers. Seen failing: a sun icon with a ring core, a leaf with a
carved vein, a water-drop with arrows cut out. Seen working: icons made of
**independent, fully solid subpaths** (arrows, clouds, wave bars, `mdi:autorenew`),
and — notably — font letterforms with counters (a/e/o/B/8), so the trap is narrower
than "any hole". The exact trigger isn't isolated.

How to handle it:

1. Prefer icons/shapes built from independent solid subpaths.
2. If a ring/hole is needed, redraw it as a single filled annulus polygon or drop the
   hole.
3. When you hand-write a shape, draw each part as its own closed solid subpath.
4. `hole_risk(parse_path(d))` (starter) returns how many "contained opposite-winding"
   pairs it sees — a heuristic warning, not proof either way.
5. A standard SVG renderer rendering it correctly proves nothing about myViewBoard.

## 5. Stroke on rounded rectangles

Stroke width renders visibly thicker on curved corners than straight edges (it
tracks curvature — `AI-pen` is built for hand-drawn ink). Unfixable; use
`stroke_width=0` (fill only) for rounded-rect cards. A separate outline shape behind
the card is the workaround for a border.

## 6. Stroke-based icon sets

Outline sets (Tabler, Heroicons-outline, Feather) are drawn as strokes, not fills, so
a fill-based `AI-pen` renders them empty. Use a **filled** variant of the icon, or
convert strokes to filled shapes first.

## Capacity

48 AI-pen rounded rectangles (96 path entries) on one page showed no degradation.
Overlapping `fill-opacity` shapes composite correctly (real blended overlaps).
`AI-pen` re-serialises path data on every save (shorthand expanded, floats nudged) —
expect cosmetic diffs after a round trip; not data loss.

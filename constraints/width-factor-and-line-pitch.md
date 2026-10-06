---
name: width-factor-and-line-pitch
description: myViewBoard lays out text at 4/3 x nominal font size. This single scale factor drives wrap width, line pitch, and glyph size — never assume text metrics without it.
metadata:
  type: constraint
  status: proven
  related: [elements/text, constraints/font-size-and-pixels]
---

# The 4/3 scale factor governs all text layout

myViewBoard lays out text at **4/3 × the nominal font size** — font-size is in
points, the canvas is 96-DPI pixels, and that ratio is the conversion. This one
fact drives wrap width, line pitch, and glyph size together. Do not estimate
any of these independently; they are all derived from the same 4/3 relationship.

- **Line pitch** = `4/3 × natural_ratio` for the font family. This overturned an
  earlier, wrong assumption (e.g. "Segoe UI pitch is 0.88") — each old value was
  almost exactly half the correct one, because it was measured off a half-size
  export and never rescaled.
- **Wrap width factor** is exactly `72/96` — a points-to-pixels conversion on
  the horizontal axis only. It is **not** per-character tracking/kerning
  adjustment. Confirmed by testing strings with equal total advance width but
  very different character counts: a tracking-based hypothesis and a
  unit-scale hypothesis predict *opposite* line counts for such strings, and
  the unit-scale prediction won.
- A blank-line paragraph break costs roughly 2× the normal line pitch, not 1×.

## Measured pitch per family (pitch ÷ font size in POINTS)

Measured from real myViewBoard renders at 44pt (wrapped lines' vertical distance):

| Family | Measured | Derived `4/3 × hhea` | Starter uses (rounded up) |
|---|---|---|---|
| Segoe UI | 1.773 | 1.773 | 1.80 |
| Calibri | 1.614 | 1.628 | 1.65 |
| Georgia | 1.523 | 1.515 | 1.55 |
| Open Sans | 1.818 | 1.816 | 1.85 |
| Times New Roman | 1.477 | 1.533 | 1.55 |
| anything else | — | — | 1.85 |

So a wrapped block is `lines × pt × ratio` canvas units tall.

**Bold is not special.** An earlier note claimed bold text wraps at double the
regular pitch. That was an artefact of a wrong (2× too small) regular value; with the
correct ratio, bold and regular blocks measure the **same** pitch. Do **not** add a
bold pitch factor or an "extra line". Bold only matters for *wrapping*: its glyphs
are wider, so more lines can result — the starter's estimator uses a wider average
character (0.60 vs 0.55 of the pixel font size) when `bold=True`.

**If you ever need to reason about layout manually** (e.g. writing a `raw:`
element with custom positioning), always apply the 4/3 relationship rather than
guessing at pixel values from how the canvas looks — text box heights are
governed by this factor and under-reserving vertical space is the classic
"heading overlaps the content below it" bug.

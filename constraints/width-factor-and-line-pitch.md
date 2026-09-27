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

**If you ever need to reason about layout manually** (e.g. writing a `raw:`
element with custom positioning), always apply the 4/3 relationship rather than
guessing at pixel values from how the canvas looks — text box heights are
governed by this factor and under-reserving vertical space is the classic
"heading overlaps the content below it" bug.

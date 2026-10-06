---
name: text-wrapping-and-overlap
description: How to estimate wrapped line count and textarea height without real font metrics, so auto-flowed elements don't overlap when text wraps to multiple lines. Confirmed failure mode as of 2026-10-01.
metadata:
  type: constraint
  status: proven
  related: [elements/text, elements/bullets, spec/content-json-envelope]
---

# Text that wraps to 2+ lines will overlap the next element if you don't account for it

**Confirmed failure, 2026-10-01 (Google AI Studio test):** everything else in a
generated file was correct, but text blocks whose content wrapped to a second
line overlapped the element placed below them. Root cause: `height` (and
therefore the next element's `y` position) was computed as if every textarea
were exactly one line tall, regardless of how much text it actually held or
how wide the box was.

**Never assume a textarea is one line tall.** A `textarea`'s real height
depends on how many lines its text wraps to, which depends on the text length,
the box width, and the font size together — not on the text content alone.
This is true whether you're placing elements at fixed coordinates or
auto-flowing them top-to-bottom.

## You have no real font metrics — estimate conservatively, not precisely

The reference engine solves this with a real per-family font metrics table
(measured from actual font files) that this corpus does not give you, since
you're generating `content.json` yourself in a plain code sandbox with no
access to that table or to font files. Don't try to guess exact character
widths per font family. Instead, use a deliberately **conservative**
(slightly-too-generous) estimate — it's far better to leave a little extra
gap between elements than to underestimate and overlap them.

**Practical algorithm, using only the Python standard library:**

```python
import textwrap

def estimate_lines(text, font_size_pt, box_width_px):
    """Conservative line-count estimate — may overestimate, should not
    underestimate, for ordinary Latin proportional text."""
    json_px = round(font_size_pt * 4 / 3)          # see font-size-and-pixels.md
    avg_char_width_px = json_px * 0.55              # deliberately generous
    chars_per_line = max(1, int(box_width_px / avg_char_width_px))
    wrapped = textwrap.wrap(text, width=chars_per_line, break_long_words=True)
    return max(1, len(wrapped))

def estimate_textarea_height(text, font_size_pt, box_width_px):
    lines = estimate_lines(text, font_size_pt, box_width_px)
    line_pitch_px = font_size_pt * 1.8    # conservative; see note below
    return lines * line_pitch_px
```

- `0.55` for average character width and `1.8×pt` for line pitch are both
  **deliberately on the generous side**. `1.8×pt` is Segoe UI's measured pitch
  (`1.7727`) rounded up. **Other fonts differ — Open Sans is `1.818`, so `1.8` would
  slightly under-reserve it**; the starter helpers use a per-font table
  (`pitch_ratio(font)`, in
  [`width-factor-and-line-pitch.md`](width-factor-and-line-pitch.md)) and
  `1.85` for unknown fonts. **Bold does not change the pitch**; it only widens glyphs,
  so for bold text use `0.60` instead of `0.55` in the width estimate (the starter's
  `bold=True`). Err toward reserving more vertical space, not less, since a small
  gap is harmless but an overlap is a visible bug.
- Prefer the starter's `estimate_height(text, pt, width, bold=…, font=…)` over this
  snippet; the snippet above is the Segoe-UI-regular special case.
- `textwrap.wrap(..., break_long_words=True)` handles the case of a single
  very long word or URL that doesn't naturally break — without
  `break_long_words=True`, a long unbroken token can make the estimate wrong
  in the other (unsafe) direction.
- If the text is empty or whitespace-only, `estimate_lines` still returns `1`
  (a textarea reserves at least one line of height even when near-empty).

## The most common mistake: computing line pitch correctly, then forgetting to multiply by line count

**Confirmed 2026-10-01, in the very generation that motivated this file:** a
textarea with 122 characters of text at `width: 1580`, `font-size: 43` (JSON
pixels, ≈32pt) was given `height: 58.05` — which is exactly
`32.25pt × 1.8` (the single-line pitch value) and nothing more. The real text
wraps to **2 lines** in myViewBoard. The number 58.05 is the *line pitch*, not
the *textarea height* — the generator computed the pitch correctly and then
used it directly as the height, skipping the "how many lines does this
actually take" step entirely. The result: the next textarea's `y` only
accounted for one line's worth of space, and the two elements visibly
overlapped.

**Walk through this exact case to see the difference:**

```python
text = ("Evaporation: Thermal energy from the sun warms oceans, lakes, "
        "and rivers, turning liquid water into invisible water vapor.")
font_size_pt = 32.25     # from json_px 43 -> 43 / (4/3)
box_width_px = 1580

# WRONG — pitch alone, the mistake that actually happened:
wrong_height = font_size_pt * 1.8                       # = 58.05 — one line only

# RIGHT — must call estimate_lines() first and multiply:
lines = estimate_lines(text, font_size_pt, box_width_px) # = 2
right_height = lines * (font_size_pt * 1.8)              # = 116.1
```

`estimate_textarea_height()` as defined above already does this correctly —
**the bug is using `font_size_pt * 1.8` (or any line-pitch value) directly as
a textarea's height, instead of calling the full function and multiplying by
the actual estimated line count.** If you find yourself writing `height =
some_pitch_formula` anywhere without a `lines *` factor in the same
expression, that's this exact mistake. Always compute `estimate_lines()`
first, and always multiply.

## Apply this to every textarea, every time — not just long paragraphs

This includes short strings — "a lesson page title" rarely wraps, but a
`body`-role sentence at a typical content width (1500, per
[`elements/text.md`](../elements/text.md)'s role defaults) can easily run to
2–3 lines, and a `bullets:` item (narrower, per
[`elements/bullets.md`](../elements/bullets.md)) wraps even more readily. Do
not special-case "short text doesn't need this check" — compute it for every
textarea unconditionally.

## Auto-flow placement rule

When placing elements top-to-bottom without fixed coordinates (matching the
DSL's auto-flow behavior described in
[`spec/dsl-spec.md`](../spec/dsl-spec.md)):

1. Compute each text element's real height with `estimate_textarea_height`
   **before** deciding the next element's `y`.
2. The next element's `y` = this element's `y` + this element's **computed**
   height + a gutter (40 canvas units, matching the DSL's default — see
   `spec/dsl-spec.md`'s positioning section).
3. Never hardcode a fixed row height (e.g. "every row is 60px apart") across
   elements with different text lengths or font sizes — that's exactly the
   assumption that caused the confirmed overlap bug.

## Self-check addition

Add to the pre-delivery checklist in [`CORE.md`](../CORE.md): for every
textarea placed above another element (by auto-flow or by manual `y`
coordinates you chose yourself), confirm the gap between them accounts for the
*wrapped* height, not a single line — re-run `estimate_textarea_height` over
each one as a final check before delivering the file.

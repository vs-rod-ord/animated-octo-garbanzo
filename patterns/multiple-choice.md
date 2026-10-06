---
name: multiple-choice
description: The "multiple choice question" page template — what it is (a static canvas layout, not the poll or quiz mechanism), exact geometry, and a validator-clean 3-page build script.
metadata:
  type: pattern
  status: validator-clean
  related: [spec/starter-helpers, elements/text, constraints/text-wrapping-and-overlap, constraints/deferred-features-not-in-dsl]
---

# Multiple-choice question pages

When someone asks for "multiple choice" or "multiple question" pages for a lesson,
build **this static layout**. Do **not** reach for the poll mechanism
(`content-polls.json`, deferred and unverified — see
[`constraints/deferred-features-not-in-dsl.md`](../constraints/deferred-features-not-in-dsl.md))
or an HTML quiz. The established pattern is one plain page per question; the answer is
revealed verbally or live, **not** marked on the canvas.

## Geometry (reverse-engineered from a real, proven file)

| Element | Position / size |
|---|---|
| Title ("Multiple Choice") | textarea x=80, y=40, w=1400, h=96, 64pt bold, accent colour |
| Horizontal accent divider | thin rect, points `80,168 1840,168 1840,172 80,172` (1760×4) |
| Vertical accent divider | thin rect `968,220 972,220 972,1040 968,1040` (4×820) — splits question column from the picture panel |
| Question | bold textarea, left column x=80, **w=830**, starts at y=220, ~36pt |
| Options | separate plain textareas `"A.  …"`, `"B.  …"`, … stacked below the question, same x/w, ~30pt |
| Decorative picture | right panel (x≈1060–1840, y≈220–1040): shapes or an AI-pen icon |
| Background | one pale solid colour per page |

Only shapes (`polygon`/`ellipse`/`AI-pen`) need `additional` entries; textareas don't.

## Rules that matter

- **Questions and options wrap.** The left column is only 830 wide, so a bold 36pt
  question often runs to 3–4 lines. Use the flowing `p.text(...)` helper so each
  element's `y` advances by its *estimated wrapped height* — hand-placed rows overlap
  (a real bug in this exact template: bold questions collided with option "A").
- **Bold is not a different pitch**, just wider glyphs: pass `bold=True` so the line
  estimate uses the wider average character
  ([`width-factor-and-line-pitch.md`](../constraints/width-factor-and-line-pitch.md)).
- Pictures: prefer simple ellipse/polygon diagrams (proven) over unverified icon
  paths ([`elements/ai-pen.md`](../elements/ai-pen.md) says how to vet paths).
- Optional teacher answer key: a bold red textarea at **y=1200** (below the 1080
  canvas). Valid and harmless, but it makes validators print an expected
  "extends beyond the canvas" warning.
- Randomise or vary which letter is correct across pages; don't always make it B.

## Build script

[`starter/example_multiple_choice.py`](../starter/example_multiple_choice.py) — paste
`olf_starter.py` and `olf_validate.py` first. It defines `mc_page(doc, question,
options, accent, bg, graphic)` and builds three pages (a nucleus diagram, a volcano
diagram, a membrane ring). Reuse `mc_page` with your own content and `graphic`
functions.

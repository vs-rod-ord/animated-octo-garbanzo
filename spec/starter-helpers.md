---
name: starter-helpers
description: Ready-made stdlib-only Python helpers (builders + validator) to paste into your code sandbox, so you don't hand-write content.json and can't skip the mechanical rules.
metadata:
  type: spec
  status: proven
  related: [CORE, spec/content-json-envelope, constraints/text-wrapping-and-overlap, examples/water-cycle-full]
---

# Starter helpers and validator — use these instead of writing content.json by hand

Three raw Python files live in [`starter/`](../starter/). **Fetch each file's full
text, then paste it into your code sandbox verbatim and run it — do not retype or
"simplify" it.** Retyping is where mechanical bugs (px vs pt, missing
`stroke-opacity`, wrong separator, overlapping text) come back. They use only the
standard library, so they run in any chat sandbox with no network.

| File | Paste when | What it gives you |
|---|---|---|
| [`starter/olf_kit.py`](../starter/olf_kit.py) | **Easiest: ONE file with everything below** (generated concatenation of the four files). Attach or fetch just this. | all of the rows below |
| [`starter/olf_starter.py`](../starter/olf_starter.py) | **Always, first** | `Doc`, `Page`, text/shape/curve builders, wrapped-height flow, `doc.save()` |
| [`starter/olf_starter_extras.py`](../starter/olf_starter_extras.py) | Only if the request needs a table, image, animation or page/web link. Paste **after** the core file. | `add_table`, `add_image`, `animate`, `link_page`, `link_web` |
| [`starter/olf_starter_svg.py`](../starter/olf_starter_svg.py) | Only if the request needs SVG: vector icons/shapes (`AI-pen`) or an SVG image. Paste after the core file (independent of extras). | `ai_pen_icon`, `ai_pen_rounded_rect`, `svg_to_paths`, `add_svg_image`, `svg_lint`, `parse_path` |
| [`starter/olf_validate.py`](../starter/olf_validate.py) | **Always, before delivering** | `validate_olf(path)` + `print_report(...)` |

## Getting the helpers INTO your sandbox (this is the step that fails)

Your code sandbox almost certainly **cannot reach GitHub** (confirmed on ChatGPT: it
could read the pages with its browsing tool but could not download the `.py` files
inside the sandbox). Reading a file and having it in your sandbox are different
things. Try these, in order, and be honest about which you used:

1. **Direct fetch inside the sandbox** (`urllib`/`requests` to the raw URL) — try
   once; on any network error, stop trying.
2. **Ask the user to attach the file.** Say exactly: *"My sandbox can't download from
   GitHub. Please attach `starter/olf_kit.py` (one file with everything) to this chat —
   or download the repo as a ZIP (Code → Download ZIP) and attach that."* Then load it
   from the uploads folder (e.g. `/mnt/data/olf_kit.py`; for a ZIP, `zipfile` extract
   first) with `exec(open(path).read())`. **This is the reliable route.**
3. **Re-emit the file yourself:** if you have read the file with a browsing tool but the
   user cannot attach it, write its contents into a single code cell **verbatim** (the
   core file `olf_starter.py` plus `olf_validate.py` are enough for most pages). Do not
   "improve" or shorten it.

**Never claim the validator returned PASS unless you actually executed
`validate_olf` on the saved file.** If you could only check rules by hand, say so
plainly ("hand-checked against the rules; validator not run"). `starter/olf_kit.py`
is all four helper files concatenated into one, so a single attachment is enough.

## The workflow

1. Paste `olf_starter.py` (and `olf_starter_extras.py` if needed) into the sandbox and run it.
2. Build the document with the helpers (see the API below, or the full worked
   script [`starter/example_build.py`](../starter/example_build.py)).
3. `doc.save("name.olf")`.
4. Paste `olf_validate.py`, then `print_report(validate_olf("name.olf"))`.
5. **Fix every `ERROR` and re-run until the result is `PASS`.** Show the user the
   final report line. Only then hand over the file.

## API cheat sheet

```python
doc = Doc("description")
p = doc.page(bg="#FFFFFF")                    # a Page; p.y is the auto-flow cursor

p.title("Heading", size=44)                   # bold text, flows downward
p.text("Body ...", size=28)                   # y advances by lines*pitch + 40 (real wrapped height)
p.text("x", x=200, y=500, width=600)          # explicit y: does NOT move the cursor
p.bullets(["a", "b"])                         # one flowing textarea per item
p.rect(x, y, w, h, fill="#E2E8F0", stroke="#334155", stroke_width=3)
p.ellipse(cx, cy, rx, ry, fill="#BAE6FD")     # centre + radii (not top-left!)
p.polyline([(x1,y1),(x2,y2)], arrow_end=True) # straight arrow / line
p.curve(start, via, end, arrow_end=True)      # stroke-opacity 1.0 is built in
tid = p.text(...)                             # every p.* returns the element id

# centred label inside a shape: create the textarea yourself
h = estimate_height(label, 26, width, bold=True)              # bold=/font= change the estimate
p.add(textarea(cx - width/2, badge_y(cy - ry, 2*ry, 26), width, h, label, 26,
               bold=True, align="center"))                   # badge_y = calibrated centring

# extras (paste olf_starter_extras.py after the core file)
t = add_table(p, x=80, y=p.y, col_lengths=[420,1300], row_lengths=[80,110,110],
              cells=[["A","B"],["a1","b1"]], merges=[(row,col,row_span,col_span)])
p.y = t["bottom"] + GUTTER
animate(doc, element_id, "fade-in", "2")      # duration is a STRING "0".."3"
link_page(doc, element_id, 3)                 # 1-based page ordinal
link_web(doc, element_id, "https://example.com")
add_image(p, doc, "images/pic.png", png_bytes, "image/png", x, y, w, h)

# SVG (paste olf_starter_svg.py after the core file) -- see elements/ai-pen.md
p.add(ai_pen_icon(["<path d>", ("<path d>", "#F59E0B")], x, y, size=200, vb=24, fill="#1565C0"))
p.add(ai_pen_rounded_rect(x, y, w, h, r, "#E0F2FE"))        # add before text = behind it
paths, (vw, vh), warns = svg_to_paths(svg_text)             # path/circle/rect/polygon -> d
add_svg_image(p, doc, "name", svg_text, x, y, w, h)         # image/svg+xml, auto 8x oversize

doc.save("out.olf")
```

Worked SVG script: [`starter/example_svg_build.py`](../starter/example_svg_build.py).

Sizes (`size=`) are in **points**; the builders convert to JSON pixels and RTF
half-points for you. Coordinates are canvas units on a 1920×1080 canvas.

## What the helpers enforce for you (so you can't forget)

- JSON `font-size` = `round(pt × 4/3)` px; RTF `\fs` = `pt × 2`; RTF `\colortbl` kept in sync with the 8-digit `#AARRGGBB` text fill.
- 6-digit fill/stroke on shapes; every shape gets its `additional` entry (`flip: none`); no `flip` on AI-pen.
- The `『『『` triple separator, written raw (`ensure_ascii=False`).
- `stroke-opacity: 1.0` on every curve.
- Text height = `estimate_lines × pitch` (never pitch alone); flow `y` advances by that real height.
- Full envelope: `olf` root, wrapped pages, `backgrounds` array, one root `additional`, nine `meta` fields, space vs comma viewboxes.
- Table: even-index cell content, dense cell backgrounds, column-major containers, 18-unit cell-text inset.
- Links as 1-based ordinal strings in the root `links` array; animations in the `additional` entry.

## What the validator checks

Envelope shape and the nine `meta` fields; unique ids; every shape has exactly one
`additional` entry with the correct `flip` rule; 6- vs 8-digit colours; triple
separator; `stroke-opacity` present on curves/lines/shapes; matrix has nine
numbers; RTF font-size and colour agree with the JSON; 130pt cap; animation
duration is a string `"0"`–`"3"`; link `page-id` is an in-range ordinal string;
table container counts and even/dense index spaces; **layout collisions** (text drawn
*behind* a later shape = error; text partly covered, or an arrow/curve passing through
a text box = warning); **height too small** (error only when short even on an
optimistic line count, warning when only the generous count disagrees); **AI-pen** (real matrix, populated
background container, plain-hex colours, absolute path commands, non-negative
coordinates, no `flip`); **image** sources exist in the ZIP and SVG sources are
linted (`<text>`, `<pattern>`, `<use>`, animation, too-small intrinsic size); **textarea height ≥ the
wrapped-height estimate**; **true 2-D overlap** between text boxes (x *and* y, so
side-by-side text is not flagged); content beyond the canvas (warning).

It cannot see the real rendered font, so it errs on the safe side. It does not
replace opening the file in myViewBoard — it removes the mistakes that were
actually seen failing in live tests.

## If the helpers genuinely can't be fetched

Then fall back to hand-building per `spec/content-json-envelope.md` and the
`elements/*.md` worked JSON, say plainly that you could not run the validator, and
do the manual checklist in [`CORE.md`](../CORE.md).

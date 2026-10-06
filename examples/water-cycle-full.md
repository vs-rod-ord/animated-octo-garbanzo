---
name: water-cycle-full
description: A complete, validator-clean, multi-element worked example (3 pages — title + numbered list, cycle diagram with arrowed curves, summary table) with the exact script that built it.
metadata:
  type: example
  status: validator-clean
  related: [spec/starter-helpers, spec/content-json-envelope, constraints/text-wrapping-and-overlap]
---

# Full worked example: "The Water Cycle" (3 pages)

Status: **validator-clean** (`olf_validate.py` → PASS, 0 errors, 0 warnings;
output of the starter helpers matches the reference engine field-for-field on
every element type). **Not yet confirmed visually in myViewBoard** — update
this line to `myViewBoard-confirmed` after a real open.

Two files, use them together:

- [`starter/example_build.py`](../starter/example_build.py) — the build script.
  Read it as a demonstration of *how to call the helpers*: flowing text,
  tap-to-reveal animation, a page link, ellipse + centred label + arrowed curve,
  and a table with a bold header row. Run it after pasting the three starter files.
- [`examples/water_cycle_full.content.json`](water_cycle_full.content.json) — the
  exact `content.json` that script produces (pretty-printed here; the real file is
  written compact). Use it to see the whole file shape end to end: envelope,
  3 pages, root `additional` (shapes + animations), root `links`, table
  containers.

## What each page demonstrates

| Page | Demonstrates |
|---|---|
| 1 | Title + subtitle + four long numbered items that **wrap to 2 lines** and flow without overlapping; `animate` (fade-in on each step); `link_page` from the title to page 2 |
| 2 | Four ellipses with centred bold labels, four `curve` arrows with `arrow_end=True` and visible stroke; coloured background |
| 3 | `add_table` — 2 columns × 5 rows, header row bold, cell text sized to the wrapped height, row heights chosen so wrapped cells fit |

## Patterns worth copying

- Never position by guesswork: use `p.text(...)` so `y` advances by the real wrapped height.
- A label inside a shape: compute `h = estimate_height(...)`, then `y = cy - h/2`, `align="center"`.
- Table rows: choose `row_lengths` ≥ wrapped text height + 36 (2 × 18 inset). `add_table` prints a warning if a row is too short.
- End every build with `print_report(validate_olf(path))` and fix until `PASS`.

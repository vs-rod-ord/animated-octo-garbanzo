---
name: table
description: The table element — cells, merges, and sizing. The single most error-prone element; read constraints/table-index-spaces.md before writing merges.
metadata:
  type: element
  status: proven
  dsl_support: full
  related: [spec/dsl-spec, constraints/table-index-spaces]
---

# `table`

```yaml
- table:
    at: [585, 469]
    cells:                        # required; every row must be the same length
      - ['A1', 'A2', 'A3']
      - ['',   'B2', '']          # '' = no textarea for that cell
      - ['C1', 'C2', 'C3']
    merges:                       # [row, col, row_span, col_span] in CELL counts
      - [0, 0, 2, 1]              # A1+B1 merged downward
      - [1, 1, 1, 2]              # B2+B3 merged across
    columns: 160                  # one length for all, or a list of per-column
    rows: [95, 100, 95]           # widths/heights. Omitted → fit to content.
    size: 53
    align: center                 # default center, unlike text's left default
    stroke: "#000000"
    stroke_width: 3
    cell_fill: "#FFFFFF"
    cell_fill_opacity: 0.2        # the app's own default for an untouched cell
```

Write `merges` in plain cell counts (row, col, row_span, col_span) — the engine
converts these into myViewBoard's actual index encoding, which is not the same
thing. **Never write merge geometry directly in `raw:` without reading
[`constraints/table-index-spaces.md`](../constraints/table-index-spaces.md)
first** — myViewBoard neither validates nor repairs bad merge geometry, so a
mistake here silently produces a table with a half-erased border that still
opens and still saves.

Cell text lives in ordinary page textareas referenced by id from the table
element — it is not nested inside the table element itself.

## Rules

- A merged-over cell should have `''` for its text. If you give it text anyway,
  it gets re-pointed at the anchor cell's coordinates and will visually overlap
  the anchor's own text.
- `align: center` is the default for table cells, unlike `text`'s left default —
  don't assume table cells inherit the same defaults as standalone `text`.

## Worked `content.json` — a 3×3 table, no merges

This is the table *shell* — cell text is separate `textarea` elements
referenced by id, not nested here. Taken directly from the reference engine.

```json
{
  "table": {
    "id": "UUID",
    "x": 585.0,
    "y": 469.0,
    "width": 492.0,
    "height": 402.0,
    "rows": 3,
    "columns": 3,
    "matrix": "1,0,0,0,1,0,0,0,1",
    "stroke": "#000000",
    "stroke-width": 3.0,
    "stroke-opacity": 1.0,
    "column-lengths-array": "160 160 160",
    "row-lengths-array": "95 100 95",
    "column-min-lengths-array": "1 1 1",
    "row-min-lengths-array": "1 1 1",
    "cell-background-container": [
      {"cell-background": {"id": "UUID", "background": "#FFFFFF", "background-opacity": 0.2, "cell-column": 0, "cell-row": 0}},
      {"cell-background": {"id": "UUID", "background": "#FFFFFF", "background-opacity": 0.2, "cell-column": 0, "cell-row": 1}},
      {"cell-background": {"id": "UUID", "background": "#FFFFFF", "background-opacity": 0.2, "cell-column": 0, "cell-row": 2}},
      {"cell-background": {"id": "UUID", "background": "#FFFFFF", "background-opacity": 0.2, "cell-column": 1, "cell-row": 0}},
      {"cell-background": {"id": "UUID", "background": "#FFFFFF", "background-opacity": 0.2, "cell-column": 1, "cell-row": 1}},
      {"cell-background": {"id": "UUID", "background": "#FFFFFF", "background-opacity": 0.2, "cell-column": 1, "cell-row": 2}},
      {"cell-background": {"id": "UUID", "background": "#FFFFFF", "background-opacity": 0.2, "cell-column": 2, "cell-row": 0}},
      {"cell-background": {"id": "UUID", "background": "#FFFFFF", "background-opacity": 0.2, "cell-column": 2, "cell-row": 1}},
      {"cell-background": {"id": "UUID", "background": "#FFFFFF", "background-opacity": 0.2, "cell-column": 2, "cell-row": 2}}
    ],
    "merge-cell-container": [],
    "cell-content-container": [
      {"cell-content": {"id": "UUID", "cell-row": 0, "cell-column": 0, "ref": "<textarea id for A1>"}},
      {"cell-content": {"id": "UUID", "cell-row": 0, "cell-column": 2, "ref": "<textarea id for A2>"}}
    ]
  }
}
```

Rules encoded here, all previously-confirmed and non-obvious:

- `width` = `sum(column-lengths) + (columns + 1) × stroke-width`; `height` is
  the same formula on rows. Get this wrong and the table's own border strokes
  won't line up with its stated bounding box.
- **`cell-background-container` is written column-major** (all rows of column
  0, then column 1, ...) and uses **dense** indices (`cell-column`/`cell-row`
  are plain 0-based cell coordinates, no gaps).
- **`cell-content-container` uses EVEN indices** — cell *(r, c)* is referenced
  at `cell-row: 2r, cell-column: 2c`. The example above places text in cell
  (0,0) → `cell-row: 0, cell-column: 0`, and cell (0,1) → `cell-row: 0,
  cell-column: 2` (not `1`). A cell with no text simply has no
  `cell-content` entry — you don't need an empty placeholder.
- A table needs **no `additional` array entry** — unlike shapes, `table` isn't
  referenced there.
- **A table has no direct `table` element requirement for its own `x`/`y`** —
  these ARE absolute (unlike `polygon`'s always-`0.0` convention), so position
  the table directly via `x`/`y`, not via `matrix` translation.

## Worked `content.json` — merge container, once merges exist

If cell (0,0) spans 2 rows × 1 column (swallowing cell (1,0)), the
`merge-cell-container` (also column-major, EVEN indices, spans as an index
**extent** `2k−1` not a plain count `k`) looks like this — note every original
cell gets an entry, including swallowed ones, which point back at their
anchor's index:

```json
{
  "merge-cell-container": [
    {"merge-cell": {"id": "UUID", "start-from": "0,0", "merge-cell-rows": 3, "merge-cell-columns": 1}},
    {"merge-cell": {"id": "UUID", "start-from": "0,0", "merge-cell-rows": 1, "merge-cell-columns": 1}},
    {"merge-cell": {"id": "UUID", "start-from": "2,0", "merge-cell-rows": 1, "merge-cell-columns": 1}}
  ]
}
```

Here `"0,0"` is `"{2r},{2c}"` for the anchor cell (0,0), and its span
`merge-cell-rows: 3` is `2k−1` for a 2-row span (`k=2` → `2×2−1=3`), **not**
`2`. The swallowed cell (1,0) gets its own entry pointing back at `"0,0"` with
span `1,1` (unmerged span values). Getting any of this wrong — row-major
ordering, cell-count spans instead of extents, wrong index space — produces a
table with a half-erased border that **still opens and still saves without
any error**. See
[`constraints/table-index-spaces.md`](../constraints/table-index-spaces.md)
before writing merge geometry by hand.

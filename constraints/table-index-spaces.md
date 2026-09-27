---
name: table-index-spaces
description: A table element's cell-content, cell-background, and merge-cell containers each use a different index space. Getting this wrong produces a silently broken table myViewBoard never validates.
metadata:
  type: constraint
  status: proven
  related: [elements/table]
---

# Three index spaces coexist inside one table element

If writing table merge geometry directly (rather than via the DSL's plain
`merges: [row, col, row_span, col_span]` cell-count list, which the engine
converts for you), three different index spaces are in play simultaneously:

| container | index space |
|---|---|
| `cell-content` | **even** — cell *(r, c)* is stored at *(2r, 2c)*; odd indices are border positions |
| `cell-background` | **dense** — cell *(r, c)* is stored at *(r, c)*, no gaps |
| `merge-cell` | **even**, and a span is written as an index **extent** of `2k−1`, not a plain cell count `k` |

`merge-cell-container` and `cell-background-container` are both
**column-major** — confirmed against a hand-built table in myViewBoard itself; a
row-major merge container places the swallowed cells at the wrong indices.

## Why this matters

**myViewBoard neither validates nor repairs bad merge geometry.** An even span,
an off-edge merge, or an overlapping merge block silently produces a table with
a half-erased border that still opens and still saves without any error. There
is no runtime signal that anything is wrong — only visual inspection catches it.
The DSL's `merges:` field exists specifically so you never have to get this
right by hand; always prefer it over writing merge containers directly in
`raw:`.

A merged-over cell keeps whatever text it had, re-pointed at the anchor cell's
coordinates — prefer `''` for merged-over cells to avoid an overlap with the
anchor's own text.

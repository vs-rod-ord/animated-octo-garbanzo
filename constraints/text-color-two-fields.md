---
name: text-color-two-fields
description: A textarea's rendered color comes from the RTF colortbl, not the JSON fill field. Updating only the JSON field has no visible effect.
metadata:
  type: constraint
  status: proven
  related: [elements/text, constraints/android-vs-windows-divergence]
---

# Text color must be set in two places, and only one of them renders

A textarea's color is controlled by two separate fields, and they must both be
kept in sync:

| Field | Location | Actually renders? |
|-------|----------|-----|
| `fill` | `text-blocks-container` → `text` object (plain JSON) | No — internal model only |
| `\colortbl` | `custom-data` RTF string | **Yes — this is what myViewBoard actually renders** |

Updating only the JSON `fill` field has no visible effect on Windows — the text
stays whatever color the RTF `\colortbl` says. This is the text-color analogue
of the font-size fact in
[`constraints/font-size-and-pixels.md`](font-size-and-pixels.md): Windows
renders from RTF, and a JSON-only change is invisible there.

RTF color table format:

```
{\colortbl ;\red0\green0\blue0;}
```

To set color to e.g. `#002A4E` (R:0, G:42, B:78):

```
{\colortbl ;\red0\green42\blue78;}
```

If hand-writing a text element in `raw:`, always update both fields together —
never assume the JSON `fill` value alone is sufficient. The DSL's own `text:`
element handles this automatically; this constraint only matters for `raw:`
payloads.

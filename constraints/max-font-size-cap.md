---
name: max-font-size-cap
description: myViewBoard silently caps rendered text at 130pt — requesting anything larger grows the container but not the glyphs.
metadata:
  type: constraint
  status: proven
  related: [elements/text, constraints/font-size-and-pixels]
---

# Text is capped at 130pt, silently

myViewBoard caps rendered text size at **130pt**, regardless of what's requested.
Setting a larger size does not produce larger text — the text block container
grows to the requested size, but the rendered glyphs stay at 130pt, leaving
visibly empty space around undersized text.

| Format | Max value |
|--------|-----------|
| Points | 130pt |
| RTF `\fs` | `\fs260` |
| JSON `font-size` | `173.0` (pixels, per the pt×4/3 conversion) |

If a request implies very large display text (a title slide, a poster-style
callout), do not exceed 130pt — there is no way to render larger text through
this format, and doing so produces a visibly broken result (oversized container,
undersized glyphs) rather than an error.

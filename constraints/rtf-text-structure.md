---
name: rtf-text-structure
description: How to build the RTF string in a textarea's custom-data — exact template, size/colour/alignment/bold words, escaping (including non-ASCII and the literal word "Arial"), what RTF features work, and what is not clickable or does not survive a save.
metadata:
  type: constraint
  status: proven
  related: [elements/text, constraints/font-size-and-pixels, constraints/text-color-two-fields, constraints/font-portability, constraints/android-vs-windows-divergence]
---

# RTF in `custom-data`: what myViewBoard actually renders (Windows)

A `textarea` carries the same text twice: an RTF string in `custom-data` and a JSON
mirror in `text-blocks-container`. **Windows renders from the RTF**; the JSON is the
model. They must agree (size, colour, bold, alignment, text). The starter's
`make_rtf()` writes both correctly — use it. This file is for when you must reason
about or hand-write the RTF.

## The template (engine-proven)

```
{\rtf1\fbidis\ansi\ansicpg1252\deff0\nouicompat\deflang1033{\fonttbl{\f0\fnil\fcharset0 Segoe UI;}}
{\colortbl ;\red26\green26\blue46;}
{\*\generator Riched20 10.0.26100}\viewkind4\uc1
\pard\ql\tx720\cf1\b\f0\fs56 Text goes here\par
}
```

(real file: the pieces are joined with `\r\n` as shown; JSON-escape the backslashes.)

| Piece | Rule |
|---|---|
| `\fs` | **Half-points = points × 2.** 28pt text → `\fs56`. (Older notes said `\fs` = the JSON number; that is wrong.) |
| JSON `font-size` | **Pixels = round(points × 4/3)** — 28pt → `37.0`. See [`font-size-and-pixels.md`](font-size-and-pixels.md). |
| `{\colortbl ;\redR\greenG\blueB;}` + `\cf1` | **This is the colour that renders.** Set it from the same colour as the JSON `fill` (`#FFRRGGBB`). Updating only the JSON fill leaves the text black. |
| `\ql` `\qc` `\qr` `\qj` | **This is the alignment that renders.** The JSON `text-align` alone does nothing. |
| `\b` after `\cf1` | Bold on. JSON `font-weight` must be `"bold"` too. Omit for regular. |
| `\i`, `\ul`, `\strike` | Italic / underline / strikethrough (match `font-style`, `text-decoration`). |
| `\par}` | Ends the paragraph and closes the root group. |
| Max size | `\fs260` (130pt) is the cap; larger values render at 130pt but grow the box. |
| Line spacing | `\sl360\slmult1` = 1.5×, `\sl480\slmult1` = 2×; always pair `\sl` with `\slmult1`. Spacing changes line pitch — then your height estimate must scale too. |

## Escaping

- `\` → `\\`, `{` → `\{`, `}` → `\}`. An unescaped `\v` or `{` in body copy gets
  eaten as a control word (an unescaped `(\v)` once hid the rest of a line).
- **Non-ASCII** (accents, arrows, CJK, emoji): write as signed 16-bit `\uN?` — é is
  `\u233?`, → is `薔?`; code points above 0x7FFF are negative (`\u-10179?`);
  emoji are two surrogate `\u` escapes. The starter's `_rtf_escape` does all of this.
  The JSON mirror keeps the real characters.
- **The literal word "Arial" is silently rewritten to "Calibri"** by myViewBoard, in
  the *decoded text*, on open (any position, case-sensitive; `ArialX` → `CalibriX`).
  Raw-stream tricks (empty group, `\'41`, `\v0` break) all fail. Working fix: put an
  invisible **word joiner** inside the word — `Ari芈?al`. The starter does this
  automatically. Also: never use Arial as a *font* (see below).
- Never put `\falt`, family hints (`\fswiss`) or a font-fallback list in the RTF —
  ignored.

## Fonts

An unknown font name renders as **Segoe UI** (identical glyphs, no error), both in
RTF and JSON. There is no fallback chain. Reliable across machines: Segoe UI,
Calibri, Times New Roman, Georgia. See
[`font-portability.md`](font-portability.md). Several fonts in one paragraph work:
define `\f0`, `\f1` in the `fonttbl` and switch mid-line with `\f1`.

## Features that render (tested)

| Feature | Result |
|---|---|
| Inline picture `{\pict\pngblip…}` | **Renders inside the textarea** (raster only; **never `\svgblip`** — blank). An oversized picture overflows the box; size the textarea ≥ picture height. |
| Hidden text `\v … \v0` | Fully supported. |
| Hyperlink field `{\field{\*\fldinst{HYPERLINK "u"}}{\fldrslt text}}` | Shows the styled result text but is **NOT clickable**. For clickable links use the `link:` mechanism ([`elements/animate-and-link.md`](../elements/animate-and-link.md)). An empty `\fldrslt` leaks the URL into the visible text. |
| Other fields (`PAGE`…) | Static result text only, never evaluated. |
| `\object` groups | Their `\result` text renders; object data ignored. |
| Unknown control words | Silently dropped. |

## What does NOT survive a myViewBoard save

- Custom RTF destinations such as `{\*\mvbrole …}` and unknown JSON keys
  (`olf-customelement-key`) are **stripped** on save. Don't rely on them for
  semantic tagging after an edit.
- A saved file's **text height grows a fixed +4 px** per textarea regardless of font
  size, and a **Unicode arrow (→) may be dropped from the JSON mirror** (the RTF
  keeps it). Both are cosmetic for Windows but the second is an Android risk — on
  Android the JSON is what renders ([`android-vs-windows-divergence.md`](android-vs-windows-divergence.md)).

## Block geometry that follows from this

- Visible text starts ~8 canvas units inside the box: to align text to `x`, set the
  box at `x − 8`.
- Text is top-aligned; extra height only adds space at the bottom. A single line
  needs at least `1.25 × pt`; wrapped text needs `lines × pitch`
  ([`text-wrapping-and-overlap.md`](text-wrapping-and-overlap.md)).
- To centre one line of text inside a shape use the starter's `badge_y(y_shape,
  shape_h, pt)` (a calibrated offset) with a textarea as wide as the shape and
  `align="center"` — do not compute `shape_centre − height/2`.

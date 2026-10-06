---
name: android-vs-windows-divergence
description: Android and Windows myViewBoard share the same content.json schema but diverge in what they actually render from — Windows trusts RTF, Android does not store it at all.
metadata:
  type: constraint
  status: proven
  related: [constraints/font-size-and-pixels, constraints/raw-element-mechanical-checks]
---

# Android and Windows render from different fields of the same file

Both platforms read the same `content.json` schema, but they don't render from
the same fields:

- **Windows** renders text from the RTF (`custom-data`) field and largely
  ignores the plain JSON text/size fields when RTF is present. See
  [`constraints/font-size-and-pixels.md`](font-size-and-pixels.md) for the
  concrete consequence of this (a JSON-only size error is invisible on Windows).
- **Android** stores no RTF at all for its own saves (empty `custom-data`) and
  renders directly from the JSON text runs and JSON size field instead.

Because of this split, **a file can look completely correct when tested only on
Windows and still be broken on Android** — several confirmed bugs in this
project's history were exactly this shape (correct-looking on Windows, wrong or
crashing on Android). Treat Windows-only verification as insufficient for
anything intended to be portable.

## What differs in a platform's own saves (for reading files, not for writing them)

| | Android save | Windows save |
|---|---|---|
| `custom-data` / `custom-data-tag` | empty strings | full RTF / `RTFxamlStr_UWP` |
| run `font-family` | `open_sans` (built-in id) | `Segoe UI` |
| run `font-stretch` | absent | present |
| run `background`, `background-opacity` | present | absent |
| text runs | one clean run | split on RTF charset boundaries |
| matrix | floats `1.0,0.0,…` | ints `1,0,…` |
| page `viewbox` | space-separated | comma-separated |
| `meta` platform / versions / library | `Whiteboard for Android`, `3.9.7`, empty library fields | `myViewBoard for Windows`, `3.4.9.x`, library name |
| `create-time` | `2026/07/15/ 10:35:45` (24h, trailing `/`) | `7/14/2026 9:59:55 AM` |
| page `tools` | empty `"tools": []` present | omitted |
| canvas | per-file (e.g. 3840×2160 with a different viewbox) | per-file |

The **schema and ZIP layout are the same**; a file from either platform loads on the
other. All differences are serialisation style, the meta block, and how text is
stored.

## Rules for a file meant to open on BOTH

1. **Write a correct JSON text run for every textarea** — Android renders only from it:
   `font-size` in pixels (`round(pt × 4/3)`), `fill` as `#AARRGGBB`, `font-weight`,
   `text-align`, the full `text`. Never rely on RTF alone. The starter helpers write
   both.
2. **Write the RTF too** (Windows renders from it): everything in
   [`rtf-text-structure.md`](rtf-text-structure.md) is Windows-only; Android ignores it.
3. Use the triple-`『` separator in every measurement string (a double separator opens
   fine on Windows and **fails on Android**, error 9999).
4. Plain `#RRGGBB` in every AI-pen fill/stroke
   ([`ai-pen-color-format.md`](ai-pen-color-format.md)) — a bad value only crashes Android.
5. Use a font from the portable set; unknown fonts silently become the default. A
   Windows-flavoured `meta` block, integer matrices and RTF present in the file were
   all tested and ruled out as causes of an Android open failure — the real cause
   was the separator (rule 3).
6. Things that are **Windows-only**: RTF features (inline pictures, hidden text,
   hyperlink display), the Arial→Calibri rewrite and its escape, glyph-outline
   fonts being the only portable custom-font path. Things that are **Android-only**:
   an embedded `@font-face` inside an SVG image element renders its font on Android
   but not Windows ([`elements/svg-image.md`](../elements/svg-image.md)).
7. A Windows re-save may drop a Unicode arrow (→) from the JSON mirror while keeping
   it in the RTF — safe on Windows, a visible loss on Android. Prefer words or shape
   arrows over text arrows in files that will be re-saved and opened on Android.

Two other confirmed platform-specific facts, relevant if generating or
inspecting raw JSON:

- Android element matrices use floats and a space-separated page viewbox
  (where Windows/the generator convention elsewhere is comma-separated — see
  the polygon-separator rule in
  [`constraints/raw-element-mechanical-checks.md`](raw-element-mechanical-checks.md)
  for the related, higher-impact separator issue).
- Android's default/fallback font in its own native saves is Open Sans, not
  Segoe UI.

---
name: content-json-envelope
description: The full root content.json structure that every element and page sits inside. Read this before writing any content.json — a file missing this envelope will not open in myViewBoard even if every individual element is correct.
metadata:
  type: spec
  status: proven
  dsl_support: full
  related: [spec/dsl-spec, elements/text, elements/shape]
---

# The `content.json` envelope

**This is the single most important file to get right.** Every worked example
under `elements/*.md` shows one element object (a `textarea`, a `polygon`,
etc.) — none of them show how those objects are wrapped into a complete file.
A file with perfectly correct elements but a wrong envelope **will not open at
all** in myViewBoard. Confirmed empirically: a real test build got every
element-level constraint right (font-size pixel conversion, RTF/JSON color
sync, the triple separator, `additional` entry shapes) and still produced a
broken file, purely from envelope mistakes. Do not skip this file.

## Full skeleton, taken directly from the reference engine

```json
{
  "olf": {
    "width": 1920.0,
    "height": 1080.0,
    "viewbox": "0 0 1920 1080",
    "meta": {
      "id": "UUID",
      "create-platform": "myViewBoard for Windows",
      "create-by-library": "Viewsonic Open Learning Format library",
      "create-time": "9/28/2026 7:15:00 AM",
      "modify-time": "9/28/2026 7:15:00 AM",
      "create-library-version": "0.0.1.50",
      "create-version": "3.4.9.603 [64 bits]",
      "modify-version": "3.4.9.603 [64 bits]",
      "modify-platform": "myViewBoard for Windows",
      "description": "Generated OLF"
    },
    "pageset": [
      {
        "page": {
          "id": "UUID",
          "matrix": "1,0,0,0,1,0,0,0,1",
          "viewbox": "0,0,1920,1080",
          "is-hidden": false,
          "elements": [
            /* your text/shape/table/etc. element objects go here, e.g.
               {"textarea": {...}}, {"polygon": {...}} */
          ],
          "backgrounds": [
            {
              "background": {
                "id": "UUID",
                "type": "color",
                "fill": "#FFFFFF",
                "opacity": 1.0
              }
            }
          ]
        }
      }
    ],
    "additional": [
      /* one {"element": {...}} entry per shape/line/table element across the
         WHOLE file — see each elements/*.md file for that element's entry
         shape. This array lives here, at the root, not inside the page. */
    ],
    "links": [
      /* top-level link entries — see elements/animate-and-link.md */
    ],
    "groups": []
  }
}
```

## Rules that are easy to get wrong — each one confirmed to break the file

1. **Everything lives inside a top-level `"olf"` key.** The file's root object
   has exactly one key, `"olf"`. Do not write `meta` and `pageset` as
   top-level keys directly — this is the single most severe mistake, and a
   file with this mistake does not open at all.
2. **Each `pageset` entry is wrapped in `{"page": {...}}`.** Not a bare page
   object — every page needs that one extra layer of nesting.
3. **Two different viewbox conventions, easy to swap by accident:**
   `olf.viewbox` (root/canvas) is **space-separated** (`"0 0 1920 1080"`);
   `page.viewbox` is **comma-separated** (`"0,0,1920,1080"`). Using the wrong
   one in the wrong place is a real, confirmed mistake.
4. **`page` requires its own `matrix` (identity: `"1,0,0,0,1,0,0,0,1"`) and
   `is-hidden: false`.** Both are easy to omit since they don't seem to do
   anything when correct.
5. **Background is an array of objects, never a bare color string.** Write
   `page.backgrounds: [{"background": {"id", "type": "color", "fill",
   "opacity"}}]` — not `page.background: "#FFFFFF"`.
6. **`additional` is a single array on the root `olf` object, not per-page.**
   Every shape/line/table element across every page in the file goes into
   this one root-level array — don't create a separate `additional` array
   inside each page.
7. **`meta` needs all nine fields shown above**, not just `description`. The
   exact values of most of them (version strings, platform name) don't need
   to be authentic — myViewBoard doesn't appear to validate them strictly —
   but the fields need to be present with *some* string value. `id` should be
   a real UUID.
8. `links` and `groups` are both required arrays at the root, even when empty.

## Minimal complete example

Putting it together for the smallest possible valid file (one page, one
title text, matching `examples/minimal.yaml`):

```json
{
  "olf": {
    "width": 1920.0,
    "height": 1080.0,
    "viewbox": "0 0 1920 1080",
    "meta": {
      "id": "11111111-1111-1111-1111-111111111111",
      "create-platform": "myViewBoard for Windows",
      "create-by-library": "Viewsonic Open Learning Format library",
      "create-time": "9/28/2026 7:15:00 AM",
      "modify-time": "9/28/2026 7:15:00 AM",
      "create-library-version": "0.0.1.50",
      "create-version": "3.4.9.603 [64 bits]",
      "modify-version": "3.4.9.603 [64 bits]",
      "modify-platform": "myViewBoard for Windows",
      "description": "Hello myViewBoard"
    },
    "pageset": [
      {
        "page": {
          "id": "22222222-2222-2222-2222-222222222222",
          "matrix": "1,0,0,0,1,0,0,0,1",
          "viewbox": "0,0,1920,1080",
          "is-hidden": false,
          "elements": [
            {
              "textarea": {
                "id": "33333333-3333-3333-3333-333333333333",
                "x": 80.0, "y": 80.0, "width": 1760.0, "height": 115.2,
                "custom-data": "{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0\\fnil\\fcharset0 Segoe UI;}}{\\colortbl ;\\red26\\green26\\blue46;}\\viewkind4\\uc1\\pard\\f0\\fs128\\cf1\\b Hello myViewBoard\\par}",
                "custom-data-tag": "RTFxamlStr_UWP",
                "matrix": "1,0,0,0,1,0,0,0,1",
                "text-blocks-container": [
                  {
                    "paragraph": {
                      "id": "44444444-4444-4444-4444-444444444444",
                      "font-size": 85.0,
                      "text-align": "left",
                      "text-list-container": [
                        {
                          "text": {
                            "id": "55555555-5555-5555-5555-555555555555",
                            "text": "Hello myViewBoard",
                            "font-family": "Segoe UI",
                            "font-size": 85.0,
                            "fill": "#FF1A1A2E",
                            "font-style": "normal",
                            "font-stretch": "normal",
                            "font-weight": "bold",
                            "text-decoration": "normal",
                            "baseline-align": "baseline",
                            "fill-opacity": 1.0
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            }
          ],
          "backgrounds": [
            {
              "background": {
                "id": "66666666-6666-6666-6666-666666666666",
                "type": "color",
                "fill": "#FFFFFF",
                "opacity": 1.0
              }
            }
          ]
        }
      }
    ],
    "additional": [],
    "links": [],
    "groups": []
  }
}
```

Note `additional` is empty here — a plain `textarea` needs no `additional`
entry (only shapes/lines/tables do). Zip this as `content.json` at the root of
the archive, rename to `.olf`.

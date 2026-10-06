---
name: page-link-menu
description: Clickable table of contents / menu pages and "back to menu" links using page links — the confirmed-working recipe (ordinal page-id string, link on the shape), plus which link types are and are not verified.
metadata:
  type: pattern
  status: proven
  related: [elements/animate-and-link, spec/starter-helpers, elements/ai-pen]
---

# Menu / table-of-contents pages with page links

**Confirmed working in myViewBoard (2026-07-31):** a menu page with five buttons, each
navigating to the right page, built by a generator.

## The recipe

1. Build the pages in order. A target page's id is its **1-based position in the
   page list, as a string** — `"1"`, `"2"`, … **Never the page's UUID** (the UUID
   form was written first and the links were dead; myViewBoard also regenerates every
   id on save, so an ordinal is the only form that can survive).
2. For each button, add one entry to the root `links` array:

   ```json
   {"link": {"id": "UUID", "ref": "<element id>", "link-type": "page", "page-id": "3"}}
   ```

3. `ref` is the element that should be clickable. Put it on the **button shape**
   (rectangle, ellipse, AI-pen rounded rect). A bare textarea with nothing under it
   works too (a "BACK TO MENU" text link is confirmed).
4. **One link per stack.** If a shape and the label sitting on top of it both carry a
   link, the app deletes the label's. So: link the shape, leave its label an ordinary
   textarea.
5. Starter helpers: `link_page(doc, element_id, page_number)` (in
   `olf_starter_extras.py`); `page.add(...)` returns the element id to link.
6. Always add a "BACK TO MENU" link on each section page, otherwise there is no way
   back.

## Build script

[`starter/example_toc.py`](../starter/example_toc.py) — paste `olf_starter.py`,
`olf_starter_extras.py`, `olf_starter_svg.py` (for the rounded buttons) and
`olf_validate.py` first. Builds a menu page with three buttons and three section pages
with back-links, then validates (the validator checks every `page-id` is an in-range
ordinal string and every `ref` exists).

## Which link types are verified

| `link-type` | Payload | Status |
|---|---|---|
| `page` | `page-id` = ordinal string | **Confirmed working** (menu buttons and bare-text back links) |
| `web` | `url` | Written correctly but **unverified**: the one generator-written web link did not fire, and no later file has had one. Don't promise it works; tell the user to test it. |
| `text` | `text` | Unverified |
| `tool` | `tool-type` (e.g. `"Protractor"`) | Unverified; valid tool names beyond the example are not catalogued |
| `file`, `audio` | `file` | Unverified (needs a file packaged in the zip) |

**Hazard:** an *unknown element type* in the file (for example a `custom-element`)
may disable every link in the document. Keep link files free of unrecognised element
types — avoid `raw:` experiments on a page set that must navigate.

RTF `HYPERLINK` fields in a textarea are display-only, never clickable — use a link
object instead ([`constraints/rtf-text-structure.md`](../constraints/rtf-text-structure.md)).

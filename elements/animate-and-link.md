---
name: animate-and-link
description: The animate and link attributes — tap-to-reveal/hide visibility and page/URL/tool navigation, attachable to most elements.
metadata:
  type: element
  status: proven
  dsl_support: full
  related: [spec/dsl-spec, elements/shape, elements/table]
---

# `animate:` and `link:`

Both are **attributes**, not standalone elements — they attach to a single
element. Valid on every element type except `bullets` (which expands to a shape
plus a textarea per item, with no single object to target). On a compound
element like `table`, they attach to the primary object (the table itself, not
individual cells).

## `animate:`

```yaml
- shape: {kind: rect, …, animate: fade-in}                    # starts hidden, tap reveals
- shape: {kind: rect, …, animate: fade-out}                   # starts visible, tap hides
- shape: {kind: rect, …, animate: {toggle: true}}             # tap toggles visibility
- shape: {kind: rect, …, animate: [fade-in, fade-out]}        # same thing, explicit
- shape: {kind: rect, …, animate: {type: fade-in, duration: "2"}}
```

`duration` **must be a quoted string**: `"0"` instant, `"1"` slow, `"2"` medium,
`"3"` fast. Do not write a bare number — a bare YAML `1` parses as an int, and
while the official myViewBoard spec claims a float 0.1–60.0 is valid, in
practice myViewBoard silently rewrites any numeric duration to `"0"`. Always
quote it.

`"0"` is not "animation off": the element still starts hidden (fade-in) or
visible (fade-out) and still toggles on tap — only the transition itself is
removed.

## `link:`

```yaml
- shape: {kind: rect, …, link: {to_page: 2}}      # 1-based page number
- text:  {content: …,   link: {url: 'https://example.com'}}
- shape: {kind: rect, …, link: {text: 'a popup message'}}
- shape: {kind: rect, …, link: {tool: Protractor}}
```

Exactly one payload key per `link:` (`to_page`, `url`, `text`, or `tool` — never
more than one). `to_page` is the **ordinal page number as a string** (`"2"`),
never a page UUID — myViewBoard regenerates every element and page id on save,
so a UUID could not survive even if it briefly resolved.

## Rules

- **One link per visual target.** If a shape and a label sitting on top of it
  both carry a `link:`, myViewBoard keeps the shape's and silently deletes the
  label's. Don't put links on both.
- A `link:` on a bare `text` element with no shape underneath it works fine —
  the "put it on the shape" concern only applies when two linked elements
  overlap each other.

**Verification status:** only `page` links are confirmed working from generated
files (see [`patterns/page-link-menu.md`](../patterns/page-link-menu.md) for the
recipe and the link-pruning rule). `web`, `text`, `tool`, `file` and `audio` are
written in the correct shape but unverified.

## Worked `content.json` — where each attribute actually lives

Neither `animate:` nor `link:` is a field *inside* the element itself — both
attach elsewhere in the file, referencing the element by its `id`. This is
easy to get wrong if reasoning from the DSL's inline-looking YAML syntax.

**`animate:` lives inside that element's `additional` array entry**, as an
`animation-container` list:

```json
{
  "element": {
    "id": "UUID",
    "ref": "<the shape's own id>",
    "flip": "none",
    "is-locked": false,
    "is-moveable-locked": false,
    "is-replicate": false,
    "animation-container": [
      {"animation": {"id": "UUID", "type": "fade-in", "duration": "2"}},
      {"animation": {"id": "UUID", "type": "fade-out", "duration": "2"}}
    ]
  }
}
```

Both `fade-in` and `fade-out` attached together (as above) is what makes a tap
toggle visibility. `duration` is always a **quoted string** — `"0"`/`"1"`/`"2"`/`"3"` —
never a bare number; myViewBoard silently rewrites a numeric duration to `"0"`
on save.

**`link:` lives in the top-level `olf.links` array**, not inside the element
or its `additional` entry, referencing the element by `ref`:

```json
{
  "links": [
    {"link": {"id": "UUID", "ref": "<element id>", "link-type": "page", "page-id": "2"}},
    {"link": {"id": "UUID", "ref": "<element id>", "link-type": "web", "url": "https://example.com"}},
    {"link": {"id": "UUID", "ref": "<element id>", "link-type": "text", "text": "a popup message"}},
    {"link": {"id": "UUID", "ref": "<element id>", "link-type": "tool", "tool-type": "Protractor"}}
  ]
}
```

The payload field name depends on `link-type` — this mapping is exact and
each type uses only its own key:

| `link-type` | payload field |
|---|---|
| `page` | `page-id` (string, 1-based ordinal — `"2"`, never a UUID) |
| `web` | `url` |
| `text` | `text` |
| `tool` | `tool-type` |
| `file` | `file` |
| `audio` | `file` |

Never write a page UUID into `page-id` — myViewBoard regenerates every id in
the file on save, so even if it briefly resolved, it could not survive a
re-save. The ordinal string form is the only one that does.

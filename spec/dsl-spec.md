---
name: dsl-spec
description: The OLF DSL grammar — document structure, templates, positioning, layers, engine contract, and CLI/MCP interface. Read after CORE.md, before any elements/ file.
metadata:
  type: spec
  status: proven
  dsl_support: full
  related: [core, elements/text, elements/raw-passthrough]
---

# OLF DSL Specification (v1)

> **How to use this file in a chat sandbox (the default path).** This describes the
> reference engine's YAML language. You almost certainly **cannot run that engine**
> (no network, no packages). Treat this file as the **vocabulary and semantics** —
> what a `bullets` list, a `shape`, a role preset, a template *means* and what
> defaults it implies — and build the real file with the paste-in helpers in
> [`spec/starter-helpers.md`](starter-helpers.md), which implement the same rules.
> Where the text below says "call the engine", read it as "use the starter helpers
> and run the validator".

A compact YAML language for generating myViewBoard `.olf` files. Write a small
declarative spec; a deterministic engine expands it into a full, validated
`content.json` and zips it. All layout math — font metrics, RTF, element IDs,
boundary fields, color-format conversion — lives in the engine, never in the
spec. If you *do* have the engine (an MCP tool or a local checkout), call it
rather than computing these values yourself.

## Design principles

1. **Semantic, not geometric.** Say `bullets`, not "textarea + 7 ellipses with
   -8 offsets."
2. **Everything optional except content.** Every position, size, color, and font
   has a default; a valid spec can be 5 lines.
3. **Escape hatch at every level.** Any element may be `raw:` — a literal
   `content.json` fragment — so the DSL never blocks an unusual request. See
   [`elements/raw-passthrough.md`](../elements/raw-passthrough.md).
4. **Fail fast.** Unknown keys, unknown shape kinds, and out-of-range values are
   build errors with clear messages — myViewBoard itself drops unknown JSON
   silently, and the DSL layer must not repeat that mistake.

## Document structure

```yaml
dsl: 1                      # spec version, required
meta:
  title: Water Cycle Lesson # → olf.meta description; default "Generated OLF"
defaults:                   # optional, overrides built-in defaults for whole file
  font: Segoe UI
  color: "#1A1A2E"
pages:
  - template: title_slide   # Layer 1: a page from a template
    params: {title: The Water Cycle, subtitle: Grade 5 Science}
  - background: "#FFFFFF"   # Layer 2: a page from semantic elements
    elements:
      - text: {content: Evaporation, role: heading}
      - bullets: {items: [Heat from the sun, Water turns to vapor]}
```

`pages` is a list; each entry is either a **template page** (`template:` +
`params:`) or an **elements page** (`elements:` + optional `background:`).
Multi-page files are first-class — the engine emits one `pageset` entry per page.

Canvas is fixed at 1920×1080. The DSL does not expose canvas size — myViewBoard
requires these exact values.

## Layer 1 — Templates

```yaml
- template: bullet_list
  params:
    title: Days of the Week
    items: [Monday, Tuesday, Wednesday]
    theme: dark
```

Templates are parameterized Layer-2 specs, not parameterized OLF files: template
→ Layer-2 spec → engine.

| Template            | Params                                     |
|---------------------|---------------------------------------------|
| `title_slide`       | title, subtitle?, theme?                   |
| `bullet_list`       | title, items[], bullet?, theme?            |
| `two_column`        | title, left[], right[]                     |
| `section_marker`    | number, title                              |
| `blank`             | background?                                |

Unknown template name is a build error listing available templates. Do not
invent a template name that isn't in this table.

## Positioning (shared by every Layer-2 element)

```yaml
at: top-left | top | top-right | left | center | right |
    bottom-left | bottom | bottom-right    # named anchor
at: [120, 340]                             # absolute x,y
# omitted → auto-flow
```

- **Named anchors** place the element inside the content region (canvas minus
  margins; default margin 80).
- **Auto-flow** (no `at`): elements stack top-to-bottom from the content origin,
  separated by a gutter (default 40). Flow uses the element's *computed* height,
  never a guess — this is what prevents overlapping elements.
- `width:` is optional everywhere; each element type has a role- or kind-based
  default. See the specific `elements/*.md` file.

## Layer 2 — semantic elements

The list of what can appear under a page's `elements:` — full detail for each is
in its own file under `elements/`, not repeated here:

`text`, `bullets`, `shape`, `line`, `curve`, `image`, `table`, plus `animate:`
and `link:` as attributes attachable to most element types (not `bullets`).

**Deferred to a future DSL version** (use `raw:` meanwhile — see
[`constraints/deferred-features-not-in-dsl.md`](../constraints/deferred-features-not-in-dsl.md)):
`flashcard`, `poll`, AI-pen/SVG icon import, `group`, per-element rotation, and
`page.tools`.

## Layer 3 — raw passthrough

```yaml
- raw:
    element: { "AI-pen": { ... } }    # literal content.json element object
    additional: auto                  # auto (default) | none | literal object
```

Mixable with Layer-2 elements on the same page. Full detail, and the mechanical
safety checks that apply to every `raw:` payload, are in
[`elements/raw-passthrough.md`](../elements/raw-passthrough.md) and
[`constraints/raw-element-mechanical-checks.md`](../constraints/raw-element-mechanical-checks.md) —
read both before emitting a `raw:` element.

## Engine contract (what you never need to compute yourself)

The engine owns, invisibly to the spec: text measurement against real font
metrics for 28 families; RTF generation (alignment via `\qc`/`\qr`/`\qj`);
UUIDs and ID uniqueness for every element; `additional` entries; `boundary`
computation for ellipses/3D shapes; color-format enforcement (shapes are
6-digit `#RRGGBB`, text fill is 8-digit `#AARRGGBB`); shape-label centering and
bullet alignment; the required `meta` block, matrices, viewbox formats, and zip
packaging; and a validation pass (structure plus pairwise textarea bounding-box
overlap check) — a spec that builds is a spec that opens cleanly.

Never try to compute font metrics, RTF, IDs, or boundary values yourself in a
spec or in `raw:` content — that is exactly the category of mistake that builds
without error and fails silently in myViewBoard, sometimes only on Android.

## Errors and warnings the engine raises

**Build errors** (exit non-zero, no file written): unknown key/kind/template,
missing required param, malformed color, a `raw` element with a duplicate ID, a
numeric (non-string) animation `duration`, a link with no or several payload
keys, `to_page` outside the document, and any invalid table merge geometry.

**Build warnings** (file still written): a text block taller than remaining page
space, an element extending past canvas, missing glyphs for the chosen font, a
font that will fall back to Segoe UI, text in a merged-over table cell, and two
linked elements overlapping.

## CLI / MCP interface

```
python -m olf_dsl build  spec.yaml -o out.olf     # build + validate
python -m olf_dsl check  spec.yaml                # parse + validate spec only
python -m olf_dsl templates                       # list templates + params
```

As MCP tools: `dsl_reference()` (returns this spec), `list_templates()`,
`check_spec(spec_yaml)` (validate without writing), `generate_olf(spec_yaml,
filename)` (YAML in, `.olf` path out), `validate_olf(path)`, `measure_text(...)`.
See [`CORE.md`](../CORE.md) for what to do if no such tool is reachable from your
current platform.

## Minimal examples

**Smallest valid file:**

```yaml
dsl: 1
pages:
  - template: title_slide
    params: {title: Hello myViewBoard}
```

**Typical lesson page, no coordinates anywhere:**

```yaml
dsl: 1
meta: {title: Water Cycle}
pages:
  - elements:
      - text: {content: The Water Cycle, role: title, align: center}
      - bullets:
          items: [Evaporation, Condensation, Precipitation, Collection]
          bullet: number
      - text: {content: "Source: NOAA", role: caption, at: bottom-right}
```

See [`examples/`](../examples/) for complete worked files, including multi-page
and mixed-layer specs.

---
name: common-patterns
description: Worked composite page patterns combining several elements — a starting point for common requests before writing a spec from scratch.
metadata:
  type: pattern
  status: proven
  dsl_support: full
  related: [spec/dsl-spec, elements/text, elements/bullets]
---

# Common page patterns

These are worked shapes for frequent requests, meant to be adapted rather than
copied verbatim. For complete, runnable files, see [`examples/`](../examples/).

> **Reading the YAML below in a chat sandbox.** The snippets are written in the
> reference engine's YAML so they stay short. You will not run that engine; read them
> as *layout intent* (what goes on the page, in what order, with what emphasis) and
> build it with the helpers in [`spec/starter-helpers.md`](../spec/starter-helpers.md):
> `p.title(...)`, `p.text(...)`, `p.bullets([...])`, shapes and tables. The
> "coordinate-free" idea maps directly to the flowing `p.text()` cursor, which
> advances by the estimated wrapped height. Complete JSON-building scripts:
> [`water-cycle-full`](../examples/water-cycle-full.md),
> [`multiple-choice`](multiple-choice.md), [`page-link-menu`](page-link-menu.md).

## Coordinate-free lesson page

The default pattern for "make a page about X" — no `at:` anywhere, so the
engine's auto-flow handles vertical stacking and computed text height:

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

Prefer this pattern whenever the request doesn't call for a specific visual
layout — it's the least likely to produce overlapping elements, since the
engine computes every element's height rather than the model guessing at
coordinates.

## Mixed layers (semantic elements + a raw escape hatch together)

`raw:` elements can sit on the same page as ordinary Layer-2 elements. Use this
when most of a page is straightforward but one piece needs something the DSL
doesn't model yet (see
[`constraints/deferred-features-not-in-dsl.md`](../constraints/deferred-features-not-in-dsl.md)):

```yaml
dsl: 1
pages:
  - elements:
      - text: {content: Geometry, role: heading}
      - shape: {kind: sphere, at: [300, 400], width: 300, height: 300,
                fill: "#FFE600", stroke: "#FF9077", label: "3D"}
      - raw:
          element: {"AI-pen": {"...": "hand-drawn brace glyph"}}
```

Don't reach for `raw:` by default — use it only for the specific piece that
genuinely needs it, and read
[`constraints/raw-element-mechanical-checks.md`](../constraints/raw-element-mechanical-checks.md)
first.

## Title + supporting content + attribution

A common three-part structure: a title-role text, a body element (bullets,
table, or image), and a small caption anchored to a corner rather than flowed
in sequence:

```yaml
dsl: 1
pages:
  - elements:
      - text: {content: Photosynthesis, role: title, align: center}
      - table:
          cells:
            - ['Stage', 'Input', 'Output']
            - ['Light reaction', 'Sunlight, water', 'ATP, oxygen']
            - ['Calvin cycle', 'CO2, ATP', 'Glucose']
      - text: {content: "Grade 7 Biology", role: caption, at: bottom-left}
```

Anchoring the caption (`at: bottom-left`) rather than letting it auto-flow keeps
it out of the vertical stack the main content occupies.

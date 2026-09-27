---
name: raw-passthrough
description: The raw element — the Layer-3 escape hatch for content.json fragments the DSL doesn't have semantic support for yet. Read the mechanical-checks constraint file before using this.
metadata:
  type: element
  status: proven
  dsl_support: full
  related: [spec/dsl-spec, constraints/raw-element-mechanical-checks, constraints/deferred-features-not-in-dsl]
---

# `raw:`

```yaml
- raw:
    element: { "AI-pen": { ... } }    # literal content.json element object
    additional: auto                  # auto (default) | none | literal object
```

Mixable with Layer-2 elements on the same page. `additional: auto` generates the
standard `{element: {id, ref, flip, is-locked, …}}` entry automatically. Raw
elements are excluded from auto-flow height computation — they don't shift
other elements below them.

This is the deliberate escape hatch for anything the DSL doesn't model yet:
`flashcard`, `poll`, AI-pen/SVG icons, or any other element type not covered
under `elements/`. See
[`constraints/deferred-features-not-in-dsl.md`](../constraints/deferred-features-not-in-dsl.md)
for what's currently only reachable this way.

## Before writing any `raw:` payload

`raw:` bypasses every layout and schema decision the engine normally makes for
you. Read
[`constraints/raw-element-mechanical-checks.md`](../constraints/raw-element-mechanical-checks.md)
first — it lists the exact mechanical rules (id presence, matrix shape,
measurement-string separator, color digit-count) that a hand-written `raw:`
payload must satisfy, every one of which myViewBoard accepts *silently* when
violated and fails on later, sometimes only on Android.

An unrecognised element type inside `raw:` survives in the file (doesn't error)
but is silently dropped the next time the page is re-serialised by the app —
don't rely on `raw:` for durable custom metadata that needs to survive a human
re-save.

---
name: deferred-features-not-in-dsl
description: Flashcard, poll, groups, rotation, and page.tools are documented but not yet buildable through the DSL (AI-pen/SVG now has its own element docs and helper). Read this before claiming the DSL can generate one of these.
metadata:
  type: constraint
  status: documented-only
  dsl_support: documented-only
  related: [elements/raw-passthrough, spec/dsl-spec]
---

# Features documented but not in DSL v1

The DSL (v1) has no semantic element for these — do not claim it can generate
them directly. They are only reachable via `raw:`
(see [`elements/raw-passthrough.md`](../elements/raw-passthrough.md) and
[`constraints/raw-element-mechanical-checks.md`](raw-element-mechanical-checks.md)),
and even then, treat the shapes below as a starting reference, not a guarantee —
this information is documented from a real myViewBoard file, not engine-validated
the way every `elements/*.md` file is.

## Flashcard

```json
{
  "flashcard": {
    "id": "UUID",
    "category": "Tool_FLASH_CARD",
    "question-title": "Chinese",
    "question": "書",
    "answer": "English",
    "explanation": "Book",
    "question-image": "",
    "question-image-display-mode": "fit",
    "answer-image": "",
    "answer-image-display-mode": "fit",
    "width": 400,
    "height": 200,
    "matrix": "1,0,100,0,1,100,0,0,1"
  }
}
```

**Confirmed gotcha:** position is set via the `matrix` translation (`tx`, `ty`
in `"1,0,tx,0,1,ty,0,0,1"`) — the `x`/`y` fields on a flashcard element are
**ignored by myViewBoard**, unlike most other elements where `x`/`y` matter.
Don't assume flashcard positioning works like `shape` or `text`.

## Poll

Poll data lives in a **separate file**, `content-polls.json`, not inside
`content.json` — this is a packaging detail, not just a schema detail. The DSL
engine's zip-packaging step would need to know to include this second file;
don't assume writing correct poll JSON alone is sufficient without also
updating the packaging step.

```json
{
  "polls-pool": {
    "id": "UUID",
    "version": "1.0",
    "polls": [ /* one object per poll, keyed by type — see below */ ]
  }
}
```

Six poll types exist, each a differently-shaped object: `multiple-choice`,
`true-or-false`, `voting`, `rating`, `random-draw`, `free-response`. Each needs
its own unique `id`; `time-limit` fields use `"MM:SS"` string format, not
seconds as a number. `content.json` itself doesn't contain the poll logic —
only `content-polls.json` does; anything in `content.json` referencing a poll is
just a visual/layout cue, not the poll definition itself.

## AI-pen / SVG icon import — NOW COVERED (outside the DSL)

SVG icons and shapes via `AI-pen`, and SVG `image` elements, are documented in
[`elements/ai-pen.md`](../elements/ai-pen.md),
[`elements/svg-image.md`](../elements/svg-image.md) and
[`constraints/ai-pen-path-rules.md`](ai-pen-path-rules.md), with a tested helper
(`starter/olf_starter_svg.py`). The DSL itself still has no `svg:`/`icon:`
element; the helpers build the JSON directly.

## groups, per-element rotation, page.tools

Not detailed here — these exist in myViewBoard and are reachable via `raw:`,
but this corpus doesn't yet carry engine-validated reference material for them
the way it does for flashcard/poll above. If a request needs one of these,
say so explicitly rather than guessing at a plausible-looking JSON shape from
general knowledge of SVG or similar formats — several real bugs in this
project's history came from exactly that kind of plausible-but-wrong guess.

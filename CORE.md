---
name: core
description: Always read first. Reading order, scope, and the generation-path rule for the OLF DSL knowledge base.
metadata:
  type: core
  status: proven
---

# Start here

This repository teaches an AI how to turn a request ("make a lesson page about
the water cycle") into a real, working `.olf` file — **by default, generated
directly in your own code-execution sandbox**, not by calling an external tool.
Most people using this corpus are talking to plain Claude, ChatGPT, or Gemini
chat, with no MCP server or other tool access — so the default path has to work
there. See "The generation-path rule" below before writing anything.

## Reading order

1. This file.
2. [`spec/dsl-spec.md`](spec/dsl-spec.md) — the DSL's document structure, layers,
   and how positioning/defaults work. Read this fully; it's short.
3. **[`spec/content-json-envelope.md`](spec/content-json-envelope.md) — read this
   in full, every time, before writing any JSON.** It is not optional and not
   skippable even for a one-element file. This is the root `olf` → `pageset` →
   `page` structure every element sits inside. Confirmed by a real test: a
   generated file got every element-level constraint correct (font sizes,
   color sync, separators) and still failed to open, purely from getting this
   envelope wrong (no root `olf` key, pages not wrapped in `{"page": ...}`,
   wrong viewbox format, background as a bare string instead of an array).
   Getting the envelope right is more important than getting any individual
   element exactly right.
4. Only the specific files under [`elements/`](elements/) that the current request
   needs. Don't read all of them — each is self-contained.
5. Any [`constraints/`](constraints/) file whose topic touches an element you're
   using (e.g. writing a `table:`? read `constraints/table-index-spaces.md`).
6. [`spec/starter-helpers.md`](spec/starter-helpers.md) — **the default build
   method**: paste the helper `.py` files into your sandbox, build with them, and
   run the validator before delivering.
7. [`examples/water-cycle-full.md`](examples/water-cycle-full.md) — a complete
   multi-page worked example (script + resulting `content.json`) for few-shot grounding.

## What this DSL can build today (v1 scope)

Supported Layer-2 elements: `text`, `bullets`, `shape` (rect/triangle/oval/
polygon-N/star/quadrant/3D-solids/rounded-rect), `line`, `curve`, `image`, `table`
(with cell merges), plus `animate:` and `link:` attributes on most of the above.
Layer 1 templates: `title_slide`, `bullet_list`, `two_column`, `section_marker`,
`blank`. Layer 3 `raw:` is a literal `content.json` element passthrough, usable
for anything not in Layer 2.

**SVG** (vector icons/shapes via `AI-pen`, and SVG `image` elements) is covered
outside the DSL: read [`elements/ai-pen.md`](elements/ai-pen.md),
[`elements/svg-image.md`](elements/svg-image.md) and
[`constraints/ai-pen-path-rules.md`](constraints/ai-pen-path-rules.md), and build with
`starter/olf_starter_svg.py`.

**Not yet supported by the DSL** — `flashcard`, `poll`,
`group`, per-element rotation, and `page.tools` (Calculator etc.) are deferred to
a future version. See
[`constraints/deferred-features-not-in-dsl.md`](constraints/deferred-features-not-in-dsl.md)
before claiming the DSL can generate one of these — it currently cannot, though
`raw:` can sometimes stand in for a hand-built version of one.

## The generation-path rule

An OLF file is a **zip** containing `content.json`. Ordinary text generation
cannot produce zip bytes — only code execution can. Priority order:

**1. Default: write and run Python in your own sandbox, right now, in this
conversation.** ChatGPT's Advanced Data Analysis, Gemini's code execution tool,
and Claude's analysis/code-execution tool all give you a Python environment with
the standard library — `json`, `zipfile`, `uuid`, `datetime` are all you need to
build a valid `content.json` and zip it into a downloadable `.olf` file. Use the
DSL semantics in `spec/` and `elements/` to decide *what* to build, and every
file in `constraints/` as the literal rules for *how* to encode it correctly —
those constraint files exist specifically because getting the mechanics wrong
produces a file that opens looking fine and fails later, often only on Android,
with no error at build time. Treat this as the expected, normal path — not a
fallback.

**Do not assume you can reach an external engine.** Standard code-execution
sandboxes on all three major chat platforms have no general internet access as
of this writing — you cannot `pip install` an unlisted package, `git clone` this
project's real Python engine, or fetch anything by URL as a reliable default (a
narrow, tool-gated exception exists on some ChatGPT surfaces, but don't depend
on it being present). Build `content.json` yourself from what's documented in
this repository, using only the standard library.

**2. If an MCP tool wrapping the real engine happens to be available** (rare for
a plain chat user, more likely for a developer with a configured client), prefer
it — it reuses a tested, deterministic implementation instead of your own
freshly-written code, which is strictly more reliable. But do not assume this is
available; it is the exception, not the default.

**3. If you have no code execution at all** (a bare chat surface with no
sandbox), produce the `content.json` as text and say so explicitly — do not
claim to have generated a working `.olf` file. Tell the person exactly what to
do with it (save it as `content.json`, zip it at the root of the archive, rename
the `.zip` to `.olf`).

**Use the starter helpers and the validator — don't hand-write everything.**
[`spec/starter-helpers.md`](spec/starter-helpers.md) points to three raw Python
files (`starter/olf_starter.py`, `starter/olf_starter_extras.py`,
`starter/olf_validate.py`). Fetch them, paste them into your sandbox verbatim,
build with the helpers, save, then run `print_report(validate_olf("file.olf"))`
and **fix every ERROR until it prints PASS** before delivering. A complete worked
3-page example is in [`examples/water-cycle-full.md`](examples/water-cycle-full.md).
The helpers already enforce the mechanical rules below; the validator catches the
rest.

**If you could not fetch/run the validator** (or hand-built the JSON), then
self-check manually against every relevant file in `constraints/` — in that case
this review step is the only thing standing in for the validation pass. At
minimum, re-check:

- **Envelope first** (see
  [`spec/content-json-envelope.md`](spec/content-json-envelope.md)): root object
  has exactly one key, `"olf"`; each page is wrapped in `{"page": {...}}`;
  `olf.viewbox` is space-separated, `page.viewbox` is comma-separated; `page`
  has both `matrix` and `is-hidden`; background is a `backgrounds` array, not a
  bare string; `additional` is one array on the root `olf` object, not
  per-page; `meta` has all nine required fields.
- Font sizes converted to pixels (not left as points).
- The `『『『` triple separator on every measurement string.
- 6-digit shape colors vs. 8-digit text colors.
- Table merge index spaces if a table is present.
- Text color set via RTF `\colortbl`, not just the JSON `fill` field.
- **Every `curve` element has `stroke-opacity` set explicitly** (`1.0` for a
  fully visible stroke) — see
  [`constraints/curve-stroke-opacity.md`](constraints/curve-stroke-opacity.md).
  Confirmed failure: a `curve` with no `stroke-opacity` renders fully
  transparent, not opaque, even though every other field is correct.
- **Every textarea's real (wrapped) height was estimated and accounted for in
  the next element's position** — see
  [`constraints/text-wrapping-and-overlap.md`](constraints/text-wrapping-and-overlap.md).
  Confirmed failure: assuming every textarea is one line tall causes visible
  overlap the moment any text wraps to a second line. Check this for every
  textarea, not just ones that look long.

A file can pass every item below the envelope check and still fail to open —
confirmed by a real test where all five lower checks were correct and the file
still didn't work, purely from envelope mistakes. Check the envelope first,
every time.

## Worked JSON coverage in this corpus

Every `elements/*.md` file now includes a "Worked `content.json`" section with
a literal, engine-sourced example — `text`, `bullets`, every `shape` kind
(`polygon`/`ellipse`/`quadrant`/`pseudo3Dshape`/`rounded-rect`), `line`,
`curve`, `image`, `table` (including merges), `animate:`/`link:`, and `AI-pen`
(icons, rounded rectangles) plus SVG `image` elements. Prefer
copying the field structure from these examples over reconstructing it from
the DSL's semantic description alone — they're taken directly from the
reference engine's own construction code, not reverse-engineered from
behavior.

**Still gap-level, lower confidence:** `flashcard` and `poll` have literal JSON
too (see
[`constraints/deferred-features-not-in-dsl.md`](constraints/deferred-features-not-in-dsl.md)),
but `group`, per-element rotation, and `page.tools` have no
worked example anywhere in this repo. For those, say so explicitly rather than
inventing a plausible-looking JSON shape from general knowledge — several real
bugs in this project's history came from exactly that kind of guess.

## When something isn't covered

Several real bugs in this project's history came from the *official* myViewBoard
spec being wrong, or from a plausible-sounding guess being wrong in a way that
only failed at runtime (often Android-only, often silent). If a required field or
element behavior isn't covered in what you've read here, **ask rather than
guess** — do not fill the gap from general knowledge about JSON, SVG, or zip
formats. General knowledge about those formats does not reliably predict what
myViewBoard's specific, quirky parser accepts.

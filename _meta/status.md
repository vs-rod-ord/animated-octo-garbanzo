---
name: status
description: Sync-checkpoint log for this mirror — when it was last generated, from what source, and what's known-incomplete.
metadata:
  type: meta
  status: proven
---

# Sync status

This repository is a **documentation-only mirror**. It is not read by the local
`olf-dsl` engine and does not update automatically — it reflects a snapshot
taken deliberately, not the live state of the local project.

| | |
|---|---|
| Last generated | 2026-09-28 |
| Generated from | `olf-dsl/DSL_SPEC.md` (v1), `olf-dsl/olf_dsl/core.py` + `expand.py` (literal `content.json` construction, added 2026-09-28), `MD/OLF_required_parameters_summary.md`, `MD/OLF_Text_Block_Insertion_Guide.md`, `MD/OLF_Image_Insertion_Guide.md`, `MD/OLF_lines_and_3D_shapes_reference.md`, `MD/OLF_Rounded_Rectangle_Guide.md`, `MD/OLF_content_schema_annotated.md`, `MD/OLF_flashcard_template_doc.md`, `MD/OLF_poll_structure_doc.md`, and locally-confirmed findings (`MEMORY.md`-tracked) as of that date |
| Generation-path default | **Revised 2026-09-28**: the model builds `content.json` directly in its own chat-platform sandbox (stdlib only), not via an MCP tool — see `CORE.md`. MCP is now the secondary/opportunistic path. |
| Worked JSON coverage | `text`, `bullets`, all `shape` kinds, `line`, `curve`, `image`, `table` (+ merges), `animate:`/`link:` all have literal, engine-sourced `content.json` examples as of 2026-09-28. `flashcard`/`poll` have literal JSON from source docs (lower confidence — not engine-validated). `group`, rotation, `page.tools` still have none (AI-pen icons/SVG now covered, 2026-10-06). |
| `/lite/` tier | Not built — deliberately skipped. The intended audience (flagship ChatGPT/Gemini-class models) was assessed as a token-budget-constrained audience, not a model-capability-constrained one; Section 8/9 of the design brainstorm (`OKF_Knowledge_Hierarchy_Brainstorm.md`) covers the reasoning. Revisit if a genuinely small/weak-model audience becomes a real target. |
| MCP generation tool | Not yet built. This corpus assumes an MCP tool wrapping the `olf-dsl` engine will eventually be the primary generation path (see `CORE.md`'s generation-path rule) — until then, treat any platform without code execution as text-spec-only, per that same rule. |

## Live test findings

**2026-09-28, ChatGPT, first real test (prompt: title + 3-item bulleted list):**
The generated `.olf` correctly applied every *element-level* constraint
(font-size pixel conversion, RTF/JSON text-color sync, 6-digit shape colors,
the `『『『` triple separator, correct `additional` entry shapes for the bullet
ellipses) — but the file did not open, because the **root envelope was wrong**:
no top-level `"olf"` key (bare `{"meta":..., "pageset":...}` instead), pages
not wrapped in `{"page": {...}}`, `background` written as a bare color string
instead of a `backgrounds` array, `additional` nested per-page instead of once
at the root, page missing `matrix`/`is-hidden`, and `meta` missing 8 of its 9
required fields. Root cause: no file in this corpus ever showed the full
envelope — every `elements/*.md` worked example showed only the element
object, silently assuming the reader already knew how it gets wrapped.

**Fix applied same day:** added
[`spec/content-json-envelope.md`](../spec/content-json-envelope.md) with the
full root structure and a complete minimal worked file, and made it a
mandatory (not optional) step 3 in `CORE.md`'s reading order, ahead of any
`elements/*.md` file.

**2026-09-28/29, ChatGPT, re-test in the same conversation thread:** envelope
bug still present, byte-for-byte identical, despite the fix being live and
confirmed correct on GitHub at the time of the test. Everything *else* in the
file changed (new UUIDs, adjusted bullet spacing, a dropped `\b0` in RTF),
strongly suggesting ChatGPT patched its own earlier output rather than
re-fetching the corpus for that follow-up turn. Not conclusively diagnosed —
depends on whether the user's follow-up was in the same thread without an
explicit re-fetch instruction. Flagged as a possible platform-specific
caveat (same-thread follow-ups may not re-read updated source material) rather
than a corpus defect, pending a cleaner re-test.

**2026-10-01, Google AI Studio, fresh test ("The Water Cycle," 4 pages —
title, numbered list, cycle diagram with arrows, summary table):** envelope
fix confirmed working, file opened correctly, and the whole structure was
validated field-by-field (meta, additional/links arrays, table cell counts,
link payload) with no errors. Two new issues found, both confirmed and fixed
same day:

1. **Text overlap, same root cause as the first finding above, but a deeper
   instance of it.** Textarea elements whose content wrapped to 2 lines
   overlapped the element below. Root cause: no file in the corpus showed how
   to estimate wrapped line count without real font metrics. Fixed by adding
   [`constraints/text-wrapping-and-overlap.md`](../constraints/text-wrapping-and-overlap.md).
2. **Re-tested, still broken the same way** — a follow-up generation after
   fix #1 was live still overlapped, now diagnosed precisely: the generator
   computed the correct single-line pitch value (`32.25pt × 1.8 = 58.05`) and
   used it *directly* as the textarea height, never actually calling the
   line-count estimation step. The formula itself was correct (verified by
   hand: it predicts 2 lines and `height=116.1` for the exact failing text);
   the generator just skipped half of it. Fixed by adding an explicit
   worked-through "wrong vs. right" numeric example using this exact failure
   case directly in `constraints/text-wrapping-and-overlap.md`, naming the
   specific mistake pattern (`height = pitch_formula` with no `lines *`
   factor) so it's recognizable even without re-deriving the math.
3. **Curve elements (arrows) rendered fully invisible — confirmed by the user
   directly in myViewBoard, not just inferred from the JSON.** Root cause: the
   `curve` worked example in `elements/line-and-curve.md` never included
   `stroke-opacity`, unlike `polygon`/`ellipse`/`polyline`, which all had it
   from the start. That omission traced back to the original source reference
   this corpus was built from, which also omitted it — i.e., a "confirmed"
   example that had actually never been visually verified. Fixed by adding
   `stroke-opacity: 1.0` to the `curve` example and a new dedicated file,
   [`constraints/curve-stroke-opacity.md`](../constraints/curve-stroke-opacity.md).

Not yet re-tested. Next test should regenerate the same water-cycle request
and confirm both the text spacing and the arrow visibility.

**2026-10-06 — starter helpers, validator and full worked example added**
(gap items 2/3/4 from the 22-item review):

- `starter/olf_starter.py` (core, 279 lines) + `starter/olf_starter_extras.py`
  (table, image, animation, links), ported from `olf-dsl/olf_dsl/core.py`.
  Differential test vs the real engine: textarea, polygon, ellipse, polyline,
  curve, table+merge, animation, link and the full envelope all match
  field-for-field (ids normalised).
- `starter/olf_validate.py` — 14 live-failure classes tested by mutation (all
  caught): missing envelope, curve without `stroke-opacity`, height = pitch only,
  duplicate ids, UUID `page-id`, 2-char separator, text overlap, RTF/JSON colour
  mismatch, 8-digit shape fill, px-vs-pt font size, float animation duration,
  missing `flip`, odd table index, missing `meta` field.
- `examples/water-cycle-full.md` + `starter/example_build.py` +
  `examples/water_cycle_full.content.json`: 3 pages, validator-clean (0 errors,
  0 warnings). **Not yet confirmed in myViewBoard.**
- Not yet live-tested on any chat platform: whether each can fetch raw `.py`
  files from GitHub and paste them into its sandbox.

**2026-10-06 (later) — SVG support added to the corpus:**

- New: `elements/ai-pen.md`, `elements/svg-image.md`, `constraints/ai-pen-path-rules.md`
  (ported from `MD/OLF_SVG_Complete_Reference.md` + `OLF_SVG_Icon_Integration_Guide.md`),
  `starter/olf_starter_svg.py`, `starter/example_svg_build.py`.
- Tested: path parser/scrubber checked against an independent library (`svgelements`)
  on 9 path styles (relative, implicit lineto, S/Q/T, compact arc flags, exponents) —
  bbox error 0, round-trip stable; `ai_pen_rounded_rect` matches the engine's
  `make_rounded_rect` field-for-field; hole-risk heuristic flags a ring, not
  independent subpaths.
- Validator extended: AI-pen (identity matrix, empty background, non-hex colours,
  shorthand/relative/negative path data, `flip`), image source existence, SVG
  lint inside the zip. 10 new mutation tests, all caught.
- Not covered (needs non-stdlib): font-glyph → AI-pen outlines (fontTools/HarfBuzz);
  documented as a requirement list only.
- Not yet viewed in myViewBoard: `svg_example.olf` (icons + card + SVG image).

## Known gaps (documented-only, not DSL-buildable)

See [`constraints/deferred-features-not-in-dsl.md`](../constraints/deferred-features-not-in-dsl.md)
for the current list: flashcard, poll, AI-pen/SVG icon import, groups,
per-element rotation, `page.tools`.

## To re-sync this mirror

1. Re-check `olf-dsl/DSL_SPEC.md` for changes since the date above (new elements,
   changed defaults, new confirmed constraints).
2. Re-check `MEMORY.md` for new `feedback_*`/`project_*` entries logged since
   this date that represent confirmed, generation-relevant findings (not every
   memory entry belongs here — only ones that change what a prompting AI should
   do differently).
3. Update the table above with the new date and a one-line note on what changed.
4. Update `dsl_support` frontmatter on any file whose status changed (e.g. a
   deferred feature that's now in the DSL should move from
   `constraints/deferred-features-not-in-dsl.md` into its own `elements/*.md`
   file).

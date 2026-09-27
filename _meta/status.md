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
| Worked JSON coverage | `text`, `bullets`, all `shape` kinds, `line`, `curve`, `image`, `table` (+ merges), `animate:`/`link:` all have literal, engine-sourced `content.json` examples as of 2026-09-28. `flashcard`/`poll` have literal JSON from source docs (lower confidence — not engine-validated). AI-pen icon import (beyond `rounded-rect`), `group`, rotation, `page.tools` still have none. |
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
`elements/*.md` file. Not yet re-tested against a live platform — next test
should re-run the same ChatGPT prompt and confirm the envelope comes out
correct this time.

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

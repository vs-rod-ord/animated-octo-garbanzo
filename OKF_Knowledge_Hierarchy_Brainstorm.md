# OLF Knowledge Hierarchy for Cross-Platform AI Prompting — Research & Layout Comparison

Status: brainstorm / not yet implemented. No code or folder structure has been built from this yet — this is the working reference for deciding the design before building it.

Goal: publish the OLF format knowledge (currently `MEMORY.md`, `olf-dsl/DSL_SPEC.md`, `MD/*.md`) to a **new, separate repo** so that other AI platforms (ChatGPT, Gemini, etc.) can be pointed at it and prompted to generate OLF files — without requiring Roderick's local Cowork setup. The local `OLF_study` folder stays the "experiment" copy; the published repo is a documentation-only mirror, not a source of truth the local engine reads from.

---

## 1. Key research finding: this already has a name

**Open Knowledge Format (OKF)** — published by Google Cloud, June 2026 (v0.1), extended July 2026 (v0.2) — is almost exactly this idea already standardized: a directory of markdown files with YAML frontmatter, cross-linked into a graph, meant to be authored by people and read directly by any agent. No vector DB, no schema registry, no required tooling. The only hard requirement is a `type` field in every file's frontmatter; everything else (what types exist, what fields, what sections) is left to the producer.

Relevant properties for us:
- Each file = one concept (a metric, a table, a runbook — for us: one element type, one spec section, one gotcha).
- Frontmatter carries metadata (`type`, and optionally `status`/trust fields as of v0.2: provenance, trust, freshness, lifecycle, attestation).
- Designed to be **imported into multiple agents** — the stated use case is exactly "one bundle, many AI platforms."
- Deliberately minimal — the spec fits on one page. This matters because it's meant to stop agents from "burning token budget re-deriving structure on every task."

**llms.txt** is the complementary, more established convention (2024, adopted by Anthropic/Stripe/Cloudflare/Mintlify/etc.): a single root index file, short one-liners + links, meant to be the *first* thing an agent reads before deciding what else to fetch. No major AI vendor has committed to auto-crawling it as of Q1 2026, but that doesn't matter for our use case since we're pointing the AI at the link ourselves, not relying on discovery.

**Anthropic's own Skills progressive-disclosure pattern** (SKILL.md convention) is the closest first-party analogue to what we already do by hand: a thin always-loaded top file (name + one-line description, kept under ~500 lines) that points to deeper files only opened when the task needs them. This is a formalization of the existing "read MEMORY.md → then DSL_SPEC.md → then only the specific element MD file" reading order — it just isn't machine-declared anywhere today. A model landing on the GitHub repo cold has no way to know to follow that order unless we tell it explicitly.

---

## 2. Hosting: GitHub raw markdown vs. Azure SWA documentation site

**Can a static documentation site work for this, or does it need to be raw markdown?** Yes, a doc site can work — with caveats, and the better framing is "both, from one source" rather than choosing.

- ChatGPT's and Gemini's browsing/fetch tools do retrieve and parse rendered page content (stripping nav/boilerplate), not just raw HTML. Pointing a model at a doc-site URL is a supported pattern.
- **Failure mode:** if the SWA site is a JS-rendered SPA (content injected client-side after load), many AI fetch tools only see the initial HTML shell and miss the real content — the same failure mode as a client-rendered page defeating a basic web-fetch tool. Server-rendered/prerendered static HTML avoids this.
- HTML costs more tokens than markdown for the same structural content, and doc-site chrome (sidebar, nav, search box, footer) adds noise the model has to filter out.
- A doc site's information architecture (sidebar nav, click-to-discover) is built for human browsing, which is a different shape than what a model wants (the relevant subtree handed over in one read).

**The pattern doc-site tooling has converged on** (Mintlify does this automatically; Docusaurus/Astro Starlight need a plugin): serve the same content three ways from one source — the rendered HTML site for humans, every page also available as raw markdown via a `.md` URL suffix, and a root `llms.txt` (+ optionally `llms-full.txt`) auto-generated from the same source. One set of markdown files, three consumption paths.

**Recommendation:** if the SWA site gets built, build it *as a render of* the same markdown files that also live in the GitHub repo, rather than a hand-maintained separate site. Whether or not the SWA framework supports `.md`-suffix serving natively, the underlying source stays identical either way, so this isn't an either/or decision — GitHub raw markdown is the baseline that has to exist regardless; the SWA site is an optional human-friendly view on top of it.

**Custom GPT / Gemini Gem knowledge upload caveat:** even if the whole corpus is uploaded, retrieval per query is limited (~8,000–16,000 tokens pulled from a knowledge base that can be up to ~2M tokens), and content near the end of large files is more likely to be missed entirely ("semantic dilution" in dense concatenated docs). This argues for many well-scoped small files over one giant `llms-full.txt`, regardless of hosting choice.

---

## 3. Structural layout options

### Option A — OKF-flavored graph (typed nodes, cross-linked)

```
/olf-knowledge/
  llms.txt                        # one-line index, root entry point
  README.md                       # human-facing overview, links to llms.txt
  /spec/
    dsl-spec.md                   # type: spec — DSL_SPEC.md content
    schema.md                     # type: spec — raw content.json structure
  /elements/
    text.md                       # type: element
    ai-pen.md
    flashcard.md
    poll.md
    table.md
    image-svg.md
    activity-layer.md
    ...
  /platform-facts/                # the "ground truth beats docs" findings
    android-vs-windows.md         # type: constraint
    ai-pen-invalid-color-crash.md # type: gotcha
    polygon-separator-format.md   # type: gotcha
    font-portability.md           # type: constraint
    ...
  /patterns/
    multiple-choice-template.md   # type: pattern
    bullet-list-shape-text-align.md
    table-merge.md
  /examples/
    minimal-text-page.olf.json
```

Frontmatter carries `type`, `status` (proven/tentative/deprecated), and `related` cross-links by path. Maps closely onto the existing `MD/` folder — the change is adding frontmatter + explicit links + pulling the "gotcha/constraint" facts that currently only live in the private `MEMORY.md` out into public files.

- Best for: live-fetch/agentic use (agent follows links per-request); scales cleanly as elements are added.
- Cost: most restructuring work — splitting `OLF_required_parameters_summary.md` and similar into many typed files.

### Option B — llms.txt-flavored flat index (few files, deep sections)

```
/olf-knowledge/
  llms.txt              # curated TOC, one-line description + link per section
  llms-full.txt          # optional: everything concatenated, for static-upload use
  dsl-spec.md            # the engine spec, unchanged
  elements-reference.md  # ALL elements in one file, ## per element
  gotchas.md             # ALL platform facts/traps in one file
  patterns.md            # ALL composite patterns in one file
```

Closest to what exists today (`DSL_SPEC.md`, `OLF_required_parameters_summary.md`) — mostly relabeling/consolidation, not a rewrite.

- Best for: static upload (custom GPT knowledge, Gemini Gem, project instructions) where the platform can't crawl links and needs one or two complete files.
- Cost: big files get unwieldy; loses "load only what's needed" efficiency; every consumer eats the whole file even for a one-element question.

### Option C — Hybrid, Skills-style tiered disclosure

```
/olf-knowledge/
  llms.txt                     # index; doubles as the "always-loaded" tier
  CORE.md                      # <500 lines: DSL grammar essentials + reading order
  /deep/
    dsl-spec-full.md
    elements/*.md              # per-element, as in Option A
    gotchas/*.md                # per-finding, as in Option A
```

`CORE.md` is the thin always-loaded layer (mirrors the SKILL.md convention), spelling out the reading order explicitly so a stranger model discovers it without being told in-prompt every time. `/deep/` is fetched on demand.

- Best for: middle ground — works for both live-fetch and static-upload (CORE.md alone is small enough to paste whole; still links out for agents that can fetch).
- Cost: `CORE.md` must be kept in sync with the deep files — the same kind of drift risk `MEMORY.md`-vs-code divergence already warns about.

---

## 4. New axis: capability/context tier (the `/lite/` idea)

Separate from *which structural option*, there's a second, orthogonal decision: whether to maintain **one tier of content or two.**

```
/olf-knowledge/
  llms.txt
  /full/            # Option A's or C's layout — complete detail
    dsl-spec.md
    /elements/*.md
    /platform-facts/*.md
    /patterns/*.md
  /lite/             # "for haiku"-equivalent — same topic coverage, compressed
    dsl-spec.md      # grammar only, terse tables, no rationale/history
    /elements/*.md   # required params + one example each, no edge-case prose
    gotchas.md        # single consolidated file, flat bullet rules
```

`/lite/` mirrors `/full/`'s filenames 1:1 so nothing silently drops; each file is rewritten for minimum tokens and minimum ambiguity.

**Research findings that shape how `/lite/` should actually be authored (not just "make it shorter"):**

1. **OKF's atomic-entry convention** (title, brief definition, context, optional example — nothing else) is designed for exactly this: small, pre-structured, self-contained entries that avoid an agent "re-deriving structure" from scratch every time. This favors Option A/C's many-small-files shape over Option B's monoliths even before tiering is considered.

2. **The more important finding — small models don't just need less context, they often fail to use the context they're given at all.** One study found models at ≤7B parameters fail to extract the correct answer 85–100% of the time *even under oracle retrieval*, where the correct passage is guaranteed to be present. The dominant failure mode is disregarding the provided context entirely, not running out of room. Retrieval-utilization capability scales with model size and doesn't reliably emerge below roughly 7B parameters.

   **Implication:** shrinking file size solves a *token-budget* problem (a custom GPT's ~8–16k retrieval window, a doc-site page fetch) but not necessarily a *model-capability* problem. If the actual target for `/lite/` is a genuinely small/weak model (the way `for haiku/` targets Claude Haiku for teammates), brevity alone isn't the fix — the content needs to be restated as low-ambiguity, directive rules a weak model can't misread, which is a real second authoring pass, not a trim of the full version. This is presumably already the lesson learned building `for haiku/` — worth confirming that folder didn't just shorten the full docs but reworded them.

3. **Agentic browsing tools work in discrete steps, not one giant read.** Current agentic-search research frames it as three separate decisions: search → browse results → read one specific document. This is a strong argument for many small files (Option A/C) over few big ones (Option B) even for capable models: an agent doing iterative retrieval wants to land on `elements/flashcard.md` directly rather than page through `elements-reference.md` to find one section. It also means the **quality of `llms.txt` matters more than the prose quality of individual files**, since it's what the agent's first "search" step reads to decide where to go next.

4. **Compression technique specifics, if authoring `/lite/`:** the methods that preserve accuracy under compression are relevance filtering (cut anything not load-bearing), semantic deduplication (state each fact once), and extractive summarization (keep the exact governing sentence rather than paraphrase it) — reported around 50–80% token reduction with key facts retained. Loose paraphrasing is the failure mode to avoid. A `/lite/` file should read like the existing `MEMORY.md` gotcha entries already do — terse, rule-first, no narrative — rather than a shrunk version of prose.

**Open question worth resolving before building:** is `/lite/` meant to solve **model capability** (a genuinely small/weak model, à la Haiku) or **context budget** (a capable model with a tight retrieval window, à la a custom GPT)? These call for different fixes — capability wants simpler *language*; budget wants smaller *file size* — and don't always point the same direction. A capable-but-budget-constrained model may handle dense technical prose fine as long as it's short; a weak model needs both short *and* simple. Worth deciding which problem is actually being solved, or whether both are real and the tier needs to account for both.

Cross-referenced against the three structural options:
- **Option A + tiering:** `/full/` is the typed graph, `/lite/` a flat compressed shadow of it. Most power, most authoring cost (maintaining two versions of every file).
- **Option B + tiering:** `/lite/` is nearly trivial to add (Option B is already close to compressed). Cheapest to stand up, but `/full/` doesn't get graph/cross-link benefits.
- **Option C + tiering:** `CORE.md` *is already* a lite tier by design (the always-loaded thin layer), so adding a separate `/lite/` folder risks two different "compressed" concepts doing overlapping jobs for different reasons (progressive disclosure vs. weak-model support) — worth deciding if that's a real distinction here or accidental duplication.

---

## 5. Decisions made so far

- The published hierarchy is a **documentation-only mirror**, not something the local `olf-dsl/` Python engine reads from. The local `OLF_study` folder remains the "experiment"/testing copy.
- It will live in a **new, separate repo** (not folded into the existing `OLF_study` structure).
- Staleness (mirror drifting from what the DSL actually supports) is the main risk instead of drift breaking the engine. Two mitigation options surfaced, not yet chosen between:
  - Manual sync checkpoint — publish deliberately after a memory/consolidation pass, so the public copy is a known-good snapshot.
  - Per-file `dsl_support: full | partial | documented-only` status field — costs more to author but travels with the content, so a prompting AI can tell when something is documented but not yet DSL-generatable (e.g. some flashcard/poll/AI-pen edge cases currently only in `MD/OLF_required_parameters_summary.md`).
- Hosting: GitHub raw markdown is the baseline; an Azure SWA doc site, if built, should render from the same markdown source rather than being maintained separately.

## 6. Generation path: how another platform actually produces a `.olf` file

Two separate questions get conflated in "point an AI at a URL and have it generate an OLF": can the model produce *correct content*, and can it hand back an actual *installable file*. An OLF is a zip; ordinary chat-completion text generation cannot emit zip bytes, so "generate the file" only works if something on the platform can execute code or call a tool that packages it.

**What's available per platform (as of Sept 2026):**
- **Gemini** — natively generates and downloads files including ZIPs directly in chat (shipped April 2026). Would still need to know OLF's packaging rules (folder layout inside the zip beyond `content.json`), which is different knowledge than the element schema and would need its own doc.
- **ChatGPT** — no native one-click zip export found, but its sandboxed Python execution (Advanced Data Analysis, formerly Code Interpreter) can write files and produce a downloadable zip. Same end result, via code execution rather than a built-in command.
- **MCP is now supported by both**, and is the more portable option — OpenAI added MCP support (Developer Mode, read+write tools) September 2025; Google added remote MCP for Gemini Business/Enterprise July 2026. One MCP server reaches ChatGPT, Gemini, and Claude alike; a Custom GPT Action is locked to OpenAI's ecosystem and gated to paid workspace tiers.

**Superseded 2026-09-28 — see below.** This section originally recommended an MCP server as *the* generation path (spec of this section, struck through in spirit rather than deleted, for the reasoning trail): wrap the existing `olf-dsl` Python engine as an MCP tool (`build_olf(spec) → file`), and have the knowledge hierarchy teach a model to produce a DSL spec for that tool rather than raw `content.json`. That reasoning still holds *when an MCP tool is actually reachable* — deterministic code genuinely catches mechanical mistakes free text can't. But it assumed MCP access would be commonly available to the target audience, and Roderick corrected this: most real users of this corpus are plain Claude/ChatGPT/Gemini **chat** users with no MCP server, no custom client, and no Action configured. For them, defaulting to "produce a spec and wait for a tool" means the corpus never actually produces a file at all.

**Revised default: the model builds `content.json` and zips it directly, inside its own chat platform's code-execution sandbox** (ChatGPT's Advanced Data Analysis, Gemini's code execution tool, Claude's analysis/code-execution tool), using only the Python standard library. Research into each platform's sandbox as of Sept 2026 confirms why this has to be self-contained rather than fetching the real engine: ChatGPT's sandbox has no general outbound network access (a narrow `container.download`-by-known-URL feature exists on some surfaces, not to be relied on); Gemini's standard code-execution sandbox likewise has no network access; Claude's code-execution tool has no internet access either. None of the three can reliably `pip install` this project's real package or `git clone`/fetch it mid-conversation, so "have the model call the real engine" isn't actually reachable for the default case — only a locally-available MCP *connection* (not a fetch) would get there, and that's the exception, not the rule. This pushes correctness responsibility onto the documentation itself: `CORE.md`'s generation-path rule now also names a concrete self-check step (re-verify the constraint list before delivering) since there's no external validator in this path, and flags that `elements/*.md`'s DSL-YAML-shaped descriptions are semantic guidance for what to build, not literal `content.json` field references — a gap worth closing with more raw-JSON worked examples per element if this becomes the primary path long-term (currently only flashcard/poll have literal JSON shapes documented, carried over from `MD/OLF_required_parameters_summary.md`).

MCP (when actually available — a configured developer client, not a plain chat surface) remains the preferred path *if reachable*, since it reuses a tested implementation instead of freshly-written in-session code. The published corpus states priority as: (1) self-contained sandbox generation, default; (2) MCP tool, if reachable; (3) text-only spec output, if no code execution exists at all.

**Prompt patterns worth designing around** (not finalized): always point the model at `llms.txt` first rather than the whole repo, so it does the intended index → relevant-node walk instead of trying to ingest everything; ask it to self-check its generated `content.json` against every `constraints/*.md` file before presenting the result, since that self-check is now the only validation pass that exists; instruct the model explicitly to ask rather than guess when a field or behavior isn't covered in what it's read, since several of this project's own findings are "the docs were wrong, ground truth disagreed" — a model filling gaps from general JSON/zip knowledge will invent plausible-looking but wrong OLF structure; and if no code-execution path exists at all, the honest prompt pattern is "generate the spec as text for you to package yourself," not "generate the file."

---

## 7. LLM wiki vs. OKF — and what it means for context-constrained consumers

**Karpathy's "LLM wiki" pattern** (GitHub gist, April 2026) is a folder of markdown files an AI agent reads, writes, *and maintains*. Compiler analogy: `raw/` = immutable source material, the LLM = compiler, `wiki/` = generated output (one entity/concept page per file, Wikipedia-style, cross-linked), a schema file (`CLAUDE.md`/`AGENTS.md`-equivalent) = conventions. Three operations: **ingest** (new source → LLM integrates it into existing pages), **query** (agent reads the compiled wiki, not raw sources), **lint** (LLM checks its own wiki for internal contradictions/staleness). The advantage over RAG: knowledge *compounds* — each new source gets synthesized into existing pages rather than sitting as a chunk to rediscover every query. Structurally this is almost identical to what OKF formalizes as a distribution format (small typed, cross-linked markdown entities) — the LLM wiki is that shape with the LLM itself as author/maintainer, rather than a human hand-curating the corpus.

**Writing style takeaway for `/constraints/`-type nodes:** a specific, checkable rule — "the polygon separator must be `『『『` (three characters), not `『『`" — is easier for a model to apply correctly than a paragraph explaining *why* it's true. This lines up with the compression-technique guidance from Section 4: rule-first, falsifiable statements over narrative.

**Does the LLM-wiki pattern benefit smaller/context-constrained models? Yes, but it's a budget fix, not a capability fix — and the two don't fully overlap.**

- **Token-budget benefit (well-documented, substantial):** loading a compiled index plus the two or three relevant concept pages uses roughly 95% fewer tokens than loading equivalent raw source material, because the "figure out the structure" work happened once at authoring time instead of being re-derived by the model on every query. This is the real mechanism behind reported "70x faster than RAG" claims — not smarter retrieval, just less redundant re-parsing. Helps any token-budget-constrained consumer (a custom GPT's ~8–16k retrieval window, a doc-site page fetch) regardless of underlying model capability.
- **Model-capability benefit (partial, indirect):** the small-model research from Section 4 found ≤7B-parameter models disregard even *correctly retrieved* context 85–100% of the time. A pre-compiled page reduces how much irrelevant text such a model wades through (less noise, less chance its attention lands on the wrong span) but doesn't fix the underlying utilization deficit — a weak model handed one clean, correct entity page can still misread or ignore it.
- **Scale ceiling:** this pattern is reported to outperform RAG specifically under roughly 100–200 articles / 50,000–100,000 tokens total. Past that, flat "index + a few pages" breaks down and needs a real search layer (grep+reranker, or a `_meta/topic-map.md` once the index passes ~200 entries) — which reintroduces retrieval uncertainty, the exact thing this pattern avoids at smaller scale. Worth a rough token-count check on the eventual corpus size before assuming this holds indefinitely.
- **The reusable part isn't the autonomy.** The benefit comes from the *output shape* — small, pre-synthesized, one-concept-per-file, compiled index in front — not from the wiki being self-maintaining. That shape is identical to what OKF prescribes and what Option A/C already target, whether a human curates it by hand (the mirror/manual-checkpoint decision already made in Section 5) or an agent ingests-and-maintains it autonomously (Karpathy's full pattern). Given the "documentation-only mirror" decision, this project can take the context-efficiency benefit without adopting autonomous wiki maintenance — they're separable. The index file (`llms.txt`) is doing most of the actual work either way.

---

## 8. Recommended document organization (synthesis of all findings)

```
/olf-knowledge/                     # new repo root — documentation-only mirror
  llms.txt                          # compiled index — single most important file;
                                     #   the "search" step every agentic reader hits first
  README.md                         # human-facing overview, links to llms.txt
  CORE.md                           # <500 lines: DSL grammar essentials, explicit reading
                                     #   order, and the generation-path boundary (MCP vs.
                                     #   text-only — see Section 6)
  /spec/
    dsl-spec.md                     # type: spec — DSL_SPEC.md content
    schema.md                       # type: spec — raw content.json structure, reference only
  /elements/                        # one atomic file per element (OKF-style)
    text.md
    ai-pen.md
    flashcard.md
    poll.md
    table.md
    image-svg.md
    activity-layer.md
    ...
  /constraints/                     # platform facts, phrased as falsifiable Key-Result-style
    android-vs-windows.md           #   rules, not narrative (Section 7's writing-style takeaway)
    ai-pen-invalid-color-crash.md
    polygon-separator-format.md
    font-portability.md
    ...
  /patterns/
    multiple-choice-template.md
    bullet-list-shape-text-align.md
    table-merge.md
  /examples/                        # worked DSL specs — few-shot anchors for prompting
    minimal-text-page.yaml
    flashcard-deck.yaml
  /lite/                            # OPTIONAL — only if a genuinely weak-model target exists,
    ...                             #   separate from token-budget concerns (Section 4/7);
                                     #   mirrors /elements, /constraints, /patterns filenames
                                     #   1:1, rewritten flat/imperative, not just shortened
  /_meta/
    status.md                       # sync-checkpoint log + per-file dsl_support summary
    topic-map.md                    # NOT needed yet — reserve the slot for when the index
                                     #   passes ~200 entries (Section 7's scale ceiling)
```

Frontmatter per file (OKF-style): `type` (required), `status` (proven/tentative/deprecated), `dsl_support` (full/partial/documented-only — Section 5's staleness mitigation), `related` (cross-links by path).

**Reading order `CORE.md` should state explicitly**, so a model landing on this repo cold doesn't have to infer it: read `llms.txt` → read `CORE.md` → follow the link into `/spec/dsl-spec.md` → open only the specific `/elements/*.md` file(s) the task needs → check `/constraints/` for anything touching those elements → pull a matching `/examples/*.yaml` for few-shot grounding → emit a DSL spec (via MCP tool if available, else as text for the user to run locally).

---

## 9. How this structure helps smaller / context-constrained models generate valid OLFs

Pulling together Sections 4, 6, and 7 into the practical payoff:

1. **It fits in the window at all.** The compiled-index-plus-a-few-pages pattern (~95% fewer tokens than raw source dump) is often the difference between a constrained consumer (a custom GPT's ~8–16k retrieval pull, a small model's short window) being able to hold the relevant spec in context versus not. Without this, a budget-constrained consumer might simply never see the one `/constraints/` fact that matters for the element in question.
2. **Falsifiable, rule-first `/constraints/` entries reduce misreading risk.** The small-model research found the dominant failure mode is disregarding or misreading provided context, not running out of room. A flat, checkable rule ("separator must be `『『『`, three characters") gives a weak model less room to misinterpret than a paragraph it has to extract meaning from — this is the direct payoff of Section 7's falsifiability takeaway.
3. **`CORE.md`'s explicit reading order removes an agentic-search burden.** Research on agentic retrieval frames model behavior as discrete search → browse → read steps; a model that has to figure out *where to look* on its own is more likely to stop early, misjudge relevance, or land on the wrong file. Spelling out the order removes that decision entirely for both weak and capable models.
4. **`/examples/` gives few-shot grounding**, which tends to lift small-model output correctness more reliably than prose description alone — a worked spec to pattern-match against is a stronger signal than a schema to reason from abstractly.
5. **Revised (Section 6): for the actual target audience, there is no engine doing the packaging — the model does, in its own sandbox.** The original version of this point assumed an MCP path would carry the hardest correctness burden. Since most real users are on plain chat surfaces without MCP, that burden now sits with the model's self-written code and the `constraints/` self-check step instead. This makes points 1–4 and 6 above *more* load-bearing than originally framed, not less — the documentation quality genuinely is doing the reliability work now, for the default path, rather than being backstopped by a deterministic engine.
6. **A `/lite/` tier, if built, targets the residual capability gap directly** — per Section 4's compression-technique findings (relevance filtering, deduplication, extractive rule-first rewrites, not just shortened prose) — for whatever gap remains after 1–5 above have done what they can.
7. **Staying under the ~50–100k-token / ~100–200-file ceiling (Section 7) matters for weak models specifically**, since crossing it requires a real search/rerank layer — and small models are also weaker at multi-hop agentic search strategies, so the "flat index + a few pages is enough" property is worth protecting deliberately as the corpus grows, not just letting it happen.

---

## 10. Open questions / not yet decided

- ~~Which structural option (A/B/C) to commit to~~ — resolved: Section 8's layout is Option A (typed/graph) with Option C's `CORE.md` thin-layer folded in as the explicit reading-order file. Option B (few large files) was dropped — the token-efficiency (Section 7) and agentic-search (Section 6/9) research both argued against it.
- Whether `/lite/` ships at all, and if so, whether it targets model capability, context budget, or both (Section 7 suggests these need different fixes) — this is the one real structural fork still open.
- Sync/staleness mechanism (manual checkpoint vs. `dsl_support` status field vs. both — leaning both, per Section 5/8).
- Rough token-count check on the eventual full corpus size against the ~50–100k-token ceiling from Section 7.
- MCP tool interface design (`build_olf(spec) → file`) — now secondary/opportunistic per Section 6's revision, not the primary path; design it later if a developer-facing MCP client audience materializes.
- Whether to invest in literal `content.json` worked examples per element (beyond flashcard/poll) now that the model itself must author raw JSON by default — flagged in `CORE.md`'s "known corpus gap" note as of 2026-09-28.
- How to validate that a prompted model on another platform actually produced a *correct* OLF end-to-end — still open, next research topic.

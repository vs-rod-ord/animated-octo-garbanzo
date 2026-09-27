# OLF DSL Knowledge Base

A documentation-only mirror, published so any AI platform (ChatGPT, Gemini,
Claude, etc.) can be pointed at this repository and prompted to generate a
myViewBoard `.olf` file via the OLF DSL — a small YAML spec language, not the
raw `.olf` zip format directly.

If you're an AI reading this repo: start at [`llms.txt`](llms.txt), then
[`CORE.md`](CORE.md).

If you're a human: this is a snapshot, not the live source. The working engine
and test harness live in a separate local project; this repo exists to be read
by AI platforms that can't reach that local environment. See
[`_meta/status.md`](_meta/status.md) for when this was last synced.

## Layout

```
llms.txt          compiled index — read this first
CORE.md           reading order + generation-path rules
spec/             DSL grammar (document structure, layers, engine contract)
elements/         one file per supported DSL element
constraints/       ground-truth facts that override intuition or the official spec
patterns/          worked composite page patterns
examples/          worked DSL specs (YAML), for few-shot prompting
_meta/            sync status
```

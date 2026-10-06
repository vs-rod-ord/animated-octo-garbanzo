# OLF Knowledge Base

A documentation-and-helpers mirror, published so any AI platform (ChatGPT, Gemini,
Claude, …) can be pointed at this repository and prompted to generate a working
myViewBoard `.olf` file. An `.olf` is a ZIP containing `content.json`; the helpers
here let the AI build and validate one inside its own code sandbox using only the
Python standard library.

**If you're an AI reading this repo:** start at [`llms.txt`](llms.txt), then
[`CORE.md`](CORE.md). Fetch the files in [`starter/`](starter/) as raw text, paste
them into your sandbox, build, run the validator, and fix errors until it passes.

**If you're a human:** this is a snapshot of verified findings, not the live source.
The working engine and test harness live in a separate local project. See
[`_meta/status.md`](_meta/status.md) for what was last verified and what is still
untested.

## Layout

```
llms.txt        compiled index — read this first
CORE.md         reading order, generation-path rules, pre-delivery checklist
spec/           content.json envelope, starter-helper guide, DSL vocabulary
elements/       one file per element type (text, shapes, tables, SVG, links, …)
constraints/    ground-truth rules that override intuition or the official spec
patterns/       whole-page recipes (multiple choice, menus, composites)
examples/       worked examples and the JSON they produce
starter/        paste-in Python helpers + validator + example build scripts
_meta/          verification status and live test log
```

## Try it

Most chat sandboxes cannot download files from GitHub. So **attach
[`starter/olf_kit.py`](starter/olf_kit.py)** (one file) to the chat — or download this
repo as a ZIP (Code → Download ZIP) and attach that — then give the AI this prompt
(adjust the request):

> Read `https://raw.githubusercontent.com/vs-rod-ord/animated-octo-garbanzo/main/llms.txt`
> and follow it. I've attached `olf_kit.py`; load it in your code sandbox. Build a
> myViewBoard `.olf` file: *\<your request\>*. Run the validator on the saved file, fix
> every error, tell me the exact validator result, then give me the file to download.

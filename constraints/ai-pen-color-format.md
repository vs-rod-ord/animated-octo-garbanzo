---
name: ai-pen-color-format
description: An AI-pen fill or stroke value that isn't valid 6-digit hex is silently ignored on Windows but crashes the file open on Android.
metadata:
  type: constraint
  status: proven
  related: [elements/shape, elements/raw-passthrough, constraints/android-vs-windows-divergence]
---

# AI-pen fill/stroke must be valid hex, or Android will crash opening the file

An AI-pen element (used via `raw:` — the DSL has no native AI-pen element in
this version, see
[`constraints/deferred-features-not-in-dsl.md`](deferred-features-not-in-dsl.md))
must have `fill`/`stroke` values that are valid hex colors. A value that isn't —
for example an SVG paint-server reference like `url(#grad1)`, which is valid SVG
but not a plain hex color — behaves very differently by platform:

- **Windows:** the invalid value is silently ignored. The element still renders
  (typically with a default or missing fill), and the file opens with no error.
- **Android:** the same file **crashes on open**.

This was isolated by building twelve near-identical test files, each varying one
property, and opening all twelve on both platforms — only the file with the
non-hex fill value failed, and it failed only on Android. This is a strong
example of why Windows-only testing is not sufficient (see
[`constraints/android-vs-windows-divergence.md`](android-vs-windows-divergence.md)):
this bug produces zero symptoms on Windows.

**Rule:** never write a non-hex value (gradient references, `currentColor`,
named CSS colors, `url(...)` paint servers, etc.) into an AI-pen `fill` or
`stroke` field. Use a plain 6-digit `#RRGGBB` value, the same rule that applies
to ordinary shapes.

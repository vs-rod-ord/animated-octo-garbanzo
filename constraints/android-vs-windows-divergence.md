---
name: android-vs-windows-divergence
description: Android and Windows myViewBoard share the same content.json schema but diverge in what they actually render from — Windows trusts RTF, Android does not store it at all.
metadata:
  type: constraint
  status: proven
  related: [constraints/font-size-and-pixels, constraints/raw-element-mechanical-checks]
---

# Android and Windows render from different fields of the same file

Both platforms read the same `content.json` schema, but they don't render from
the same fields:

- **Windows** renders text from the RTF (`custom-data`) field and largely
  ignores the plain JSON text/size fields when RTF is present. See
  [`constraints/font-size-and-pixels.md`](font-size-and-pixels.md) for the
  concrete consequence of this (a JSON-only size error is invisible on Windows).
- **Android** stores no RTF at all for its own saves (empty `custom-data`) and
  renders directly from the JSON text runs and JSON size field instead.

Because of this split, **a file can look completely correct when tested only on
Windows and still be broken on Android** — several confirmed bugs in this
project's history were exactly this shape (correct-looking on Windows, wrong or
crashing on Android). Treat Windows-only verification as insufficient for
anything intended to be portable.

Two other confirmed platform-specific facts, relevant if generating or
inspecting raw JSON:

- Android element matrices use floats and a space-separated page viewbox
  (where Windows/the generator convention elsewhere is comma-separated — see
  the polygon-separator rule in
  [`constraints/raw-element-mechanical-checks.md`](raw-element-mechanical-checks.md)
  for the related, higher-impact separator issue).
- Android's default/fallback font in its own native saves is Open Sans, not
  Segoe UI.

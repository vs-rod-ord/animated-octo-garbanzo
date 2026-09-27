---
name: font-portability
description: Only 20 of the DSL's 28 known font families are bundled with myViewBoard and guaranteed to render identically everywhere. The other 8 depend on locally-installed system fonts.
metadata:
  type: constraint
  status: proven
  related: [elements/text]
---

# Prefer portable fonts for anything meant to be shared

The DSL/engine knows metrics for 28 font families, but they aren't equally
portable:

**Portable (20)** — bundled inside myViewBoard's own font assets, and the exact
set its own font picker offers. These render identically on any machine with
myViewBoard installed:

Arimo, Caladea, Carlito, Comic Relief, Cousine, Gelasio, Inter, Lato,
Merriweather, Montserrat, Noto Sans, Nunito, Open Sans, Oswald, PT Sans,
Playfair Display, Poppins, Raleway, Roboto, Tinos

**Windows-only (4 of the 28)** — Segoe UI (myViewBoard's own default), Calibri,
Times New Roman, Georgia. These resolve against locally-installed Windows system
fonts and will silently substitute to something else on a machine that lacks
them.

## Metric-compatible swaps

Some portable families are metric clones of the Windows-only ones, meaning the
swap changes nothing about where lines wrap:

| Windows font | Portable swap | Verified |
|---|---|---|
| Calibri | Carlito | yes — zero width delta |
| Times New Roman | Tinos | yes — zero width delta |
| Georgia | Gelasio | widths only — line heights shift slightly, ratios differ |
| Arial | Arimo | by design, no direct comparison available |
| Courier New | Cousine | by design, no direct comparison available |
| Cambria | Caladea | by design, no direct comparison available |

## Rule

When a font isn't specified by the user, or when portability matters (this
repo's whole purpose — generating files for platforms other than the local
author's machine), default to a portable family. If the user specifically asks
for a Windows-only font, honor it but flag that it depends on the target
machine having that font installed locally.

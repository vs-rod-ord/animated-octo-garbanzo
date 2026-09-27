---
name: raw-element-mechanical-checks
description: Mechanical rules every hand-written raw element payload must satisfy. myViewBoard accepts every violation silently, so these checks are the only thing standing between a raw element and a broken file.
metadata:
  type: constraint
  status: proven
  related: [elements/raw-passthrough]
---

# Mechanical checks on `raw:` payloads

`raw:` bypasses every layout and schema decision the engine normally makes.
Each rule below exists because myViewBoard accepted the violation **in
silence** — the file built with zero errors and zero warnings, and failed only
later, often only on one platform.

## Required (build errors if violated)

| check | why |
|---|---|
| `id` present and non-empty | an id-less element is invisible to the uniqueness check and produces an `additional` entry with `ref: null` |
| `matrix` has exactly 9 numeric components | |
| measurement strings use the **triple** `U+300E` (`『『『`) separator | a double separator (`『『`) opens fine on Windows and fails on **Android with error 9999** — this is the single highest-impact silent-failure bug found in this project |
| shape `fill`/`stroke` are 6-digit `#RRGGBB` | 8-digit `#AARRGGBB` is for text runs only, never shapes |
| `points` tokens parse as `x,y` | |

## Warnings (file still written, but suspect)

- An unrecognised element type — survives in the file and doesn't break links,
  but is silently dropped the next time the page is re-serialised.
- A `custom-element` — same behavior, so it's unusable for durable metadata.
- Extending past the canvas bounds.

## Why to take this seriously

A real scan across this project's own historical output found **3,432 elements
using the wrong (double) separator and 26 eight-digit shape colors across 58
files** — all pre-dating a 2026-07-15 fix. Every one of those files opened
without error and looked correct until tested specifically on the platform or
code path that exposed the defect. Assume the same is true of any new `raw:`
payload: passing "it opened" is not sufficient evidence of correctness.

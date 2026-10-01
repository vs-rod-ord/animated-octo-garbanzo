---
name: curve-stroke-opacity
description: A curve element with no explicit stroke-opacity renders fully transparent (invisible), not opaque. Confirmed 2026-10-01 from a real generated file where every arrow on a page was invisible despite being otherwise correctly formed.
metadata:
  type: constraint
  status: proven
  related: [elements/line-and-curve]
---

# `curve` needs explicit `stroke-opacity: 1.0`, or it's invisible

**Confirmed 2026-10-01:** a real generated `.olf` had four `curve` elements
(arrows connecting stages of a cycle diagram) that were in every other respect
correct — right field shape, right coordinates, right color, correctly listed
in the root `additional` array — and every one of them rendered completely
invisible in myViewBoard. The cause: none of them set `stroke-opacity`. Adding
`"stroke-opacity": 1.0` is the fix.

This is notable because `polygon`, `ellipse`, and `polyline` all have an
explicit `stroke-opacity` field in their own worked examples already (see
[`elements/shape.md`](../elements/shape.md) and
[`elements/line-and-curve.md`](../elements/line-and-curve.md)) — `curve` is
the one element type where an earlier version of this corpus omitted it,
because the original source reference this corpus was built from also omitted
it. Treat that as a reminder that a "confirmed" example in this corpus is only
as good as what it was actually tested against — this field's absence had
never been visually verified before.

**Rule:** always set `stroke-opacity` explicitly on a `curve` element — do not
assume it defaults to fully opaque the way it seems to for other shape types.

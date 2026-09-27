---
name: line-and-curve
description: The line and curve elements — straight/multi-segment lines and single-bend curves, with arrow and dash options.
metadata:
  type: element
  status: proven
  dsl_support: full
  related: [spec/dsl-spec]
---

# `line` and `curve`

```yaml
- line:  {from: [100, 500], to: [800, 500], arrow: none|end|both, dashed: true,
          color: "#CBD5E1", width: 4}
- line:  {points: [[100,100],[100,400],[500,400]], arrow: end}   # multi-segment
- curve: {from: [100,100], via: [400,50], to: [700,100], arrow: both}
```

`line` accepts either `from`/`to` (single segment) or `points` (a multi-segment
polyline). `curve` accepts exactly `from`/`via`/`to` — one control point, one
bend. There is no multi-bend curve in this DSL version.

`arrow: none | end | both` controls arrowheads. `dashed: true` on a `line`
produces a dashed stroke; `curve` has no dashed option in this DSL version.

## Worked `content.json` — `polyline` (`line:`)

```json
{
  "polyline": {
    "id": "UUID",
    "x": 0.0,
    "y": 0.0,
    "points": "485.99,735.03 785.25,815.28",
    "stroke": "#000000",
    "stroke-width": 6.0,
    "stroke-opacity": 1.0,
    "stroke-linecap": "round",
    "lineshape-start": "normal",
    "lineshape-end": "normal",
    "stroke-dasharray": "18,12",
    "matrix": "1,0,0,0,1,0,0,0,1"
  }
}
```

`points` is space-separated absolute `x,y` pairs — 2 or more, so a 3-point
polyline (`"x1,y1 x2,y2 x3,y3"`) renders as a right-angle bracket, useful for
axis-style diagrams. `lineshape-start`/`-end` are `"normal"` (no arrowhead) or
`"arrow"`, settable independently per end. Omit `stroke-dasharray` entirely for
a solid line — don't set it to an empty string. Needs the same `additional`
array entry as `polygon` (see [`elements/shape.md`](shape.md)).

## Worked `content.json` — `curve`

```json
{
  "curve": {
    "id": "UUID",
    "start-point": "200,300",
    "second-point": "400,100",
    "end-point": "600,300",
    "stroke": "#FF0000",
    "stroke-width": 2.0,
    "stroke-linecap-start": "none",
    "stroke-linecap-end": "arrow",
    "matrix": "1,0,0,0,1,0,0,0,1"
  }
}
```

Control points use `start-point`/`second-point`/`end-point` — **not** a
`points` field like `polyline`. Arrowheads: `stroke-linecap-start`/`-end` are
`"round"` (no arrowhead) or `"arrow"` (arrowhead); both ends can be `"arrow"`
for a double-headed curve. Needs the same `additional` array entry as
`polygon`.

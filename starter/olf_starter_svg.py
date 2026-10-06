"""olf_starter_svg.py -- SVG support: AI-pen vector icons/shapes and SVG image elements.

Paste AFTER olf_starter.py (uses uid, MATRIX, Page, Doc). Standard library only.
Does NOT need olf_starter_extras.py.

Two ways to put SVG on a canvas (see elements/svg-image.md and elements/ai-pen.md):

  A. TRUE VECTOR (scales cleanly): turn SVG path data into an AI-pen element.
        p.add(ai_pen_icon(["M10 20v-6h4v6h5v-8h3L12 3L2 12h3v8z"], x=340, y=440,
                          size=200, vb=24, fill="#1565C0"))
        # or straight from SVG text:
        paths, (vw, vh), warns = svg_to_paths(svg_text)
        p.add(ai_pen_icon(paths, x=100, y=100, size=200, vb=max(vw, vh)))
        p.add(ai_pen_rounded_rect(80, 80, 600, 300, 40, "#E0F2FE"))

  B. RASTERISED SVG IMAGE (any look, but pixelates if scaled up): an `image`
     element with mime image/svg+xml. Author it big; this helper does that:
        add_svg_image(p, doc, "diagram", svg_text, x=560, y=250, w=800, h=530)

Both are linted: unsupported SVG features are reported as warnings.
"""
import math
import re
import xml.etree.ElementTree as ET

_CMD = re.compile(r"\s*([MmLlHhVvCcSsQqTtAaZz])")
_NUM = re.compile(r"\s*,?\s*([-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?)")
_FLAG = re.compile(r"\s*,?\s*([01])")
_MORE = re.compile(r"\s*,?\s*[-+.\d]")
_ARITY = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7}


def _fmt(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ---------------------------------------------------------------------------
# 1. Path parsing -> absolute M / L / C / A / Z only
# ---------------------------------------------------------------------------
def parse_path(d):
    """SVG path data -> list of absolute segments:
    ('M',x,y) ('L',x,y) ('C',x1,y1,x2,y2,x,y) ('A',rx,ry,rot,large,sweep,x,y) ('Z',)
    H/V -> L, Q/T -> exact cubic C, S -> C, relative -> absolute."""
    segs, i, n = [], 0, len(d)
    cx = cy = sx = sy = 0.0
    lc = lq = None                      # last cubic / quad control point
    cmd = None
    while True:
        m = _CMD.match(d, i)
        if m:
            cmd, i = m.group(1), m.end()
            if cmd in "Zz":
                segs.append(("Z",))
                cx, cy, lc, lq = sx, sy, None, None
                continue
        else:
            if re.compile(r"\s*,?\s*").match(d, i).end() >= n:
                break
            if cmd is None or cmd in "Zz":
                raise ValueError("bad path data near %r" % d[i:i + 12])
        rel, up = cmd.islower(), cmd.upper()
        first_set = True
        while first_set or _MORE.match(d, i):
            first_set = False
            args = []
            for k in range(_ARITY[up]):
                if up == "A" and k in (3, 4):
                    mm = _FLAG.match(d, i)
                else:
                    mm = _NUM.match(d, i)
                if not mm:
                    raise ValueError("missing number in path near %r" % d[i:i + 12])
                args.append(float(mm.group(1)))
                i = mm.end()
            ox, oy = (cx, cy) if rel else (0.0, 0.0)
            if up == "M":
                cx, cy = args[0] + ox, args[1] + oy
                sx, sy = cx, cy
                segs.append(("M", cx, cy))
                lc = lq = None
                up, rel = "L", rel       # implicit repeats are lineto
            elif up == "L":
                cx, cy = args[0] + ox, args[1] + oy
                segs.append(("L", cx, cy)); lc = lq = None
            elif up == "H":
                cx = args[0] + (cx if rel else 0.0)
                segs.append(("L", cx, cy)); lc = lq = None
            elif up == "V":
                cy = args[0] + (cy if rel else 0.0)
                segs.append(("L", cx, cy)); lc = lq = None
            elif up == "C":
                x1, y1, x2, y2, x, y = (args[0] + ox, args[1] + oy, args[2] + ox,
                                        args[3] + oy, args[4] + ox, args[5] + oy)
                segs.append(("C", x1, y1, x2, y2, x, y))
                lc, lq, cx, cy = (x2, y2), None, x, y
            elif up == "S":
                x1, y1 = (2 * cx - lc[0], 2 * cy - lc[1]) if lc else (cx, cy)
                x2, y2, x, y = args[0] + ox, args[1] + oy, args[2] + ox, args[3] + oy
                segs.append(("C", x1, y1, x2, y2, x, y))
                lc, lq, cx, cy = (x2, y2), None, x, y
            elif up in "QT":
                if up == "Q":
                    qx, qy, x, y = args[0] + ox, args[1] + oy, args[2] + ox, args[3] + oy
                else:
                    qx, qy = (2 * cx - lq[0], 2 * cy - lq[1]) if lq else (cx, cy)
                    x, y = args[0] + ox, args[1] + oy
                segs.append(("C", cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy),
                             x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y), x, y))
                lq, lc, cx, cy = (qx, qy), None, x, y
            elif up == "A":
                x, y = args[5] + ox, args[6] + oy
                segs.append(("A", abs(args[0]), abs(args[1]), args[2],
                             int(args[3]), int(args[4]), x, y))
                cx, cy, lc, lq = x, y, None, None
    return segs


def segs_to_d(segs, dx=0.0, dy=0.0):
    out = []
    for s in segs:
        k = s[0]
        if k == "Z":
            out.append("Z")
        elif k in "ML":
            out.append("%s%s %s" % (k, _fmt(s[1] + dx), _fmt(s[2] + dy)))
        elif k == "C":
            out.append("C%s %s %s %s %s %s" % (
                _fmt(s[1] + dx), _fmt(s[2] + dy), _fmt(s[3] + dx), _fmt(s[4] + dy),
                _fmt(s[5] + dx), _fmt(s[6] + dy)))
        else:  # A
            out.append("A%s %s %s %d %d %s %s" % (
                _fmt(s[1]), _fmt(s[2]), _fmt(s[3]), s[4], s[5], _fmt(s[6] + dx), _fmt(s[7] + dy)))
    return "".join(out)


# ---------------------------------------------------------------------------
# 2. Geometry helpers: arc sampling, flattening, bbox, hole-risk heuristic
# ---------------------------------------------------------------------------
def _arc_points(x1, y1, rx, ry, phi_deg, fa, fs, x2, y2, n=16):
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2):
        return [(x2, y2)]
    phi = math.radians(phi_deg)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = (x1p ** 2) / (rx ** 2) + (y1p ** 2) / (ry ** 2)
    if lam > 1:
        s = math.sqrt(lam); rx, ry = rx * s, ry * s
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    co = math.sqrt(max(0.0, num / den)) * (-1 if fa == fs else 1)
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (x1 + x2) / 2
    cy = sp * cxp + cp * cyp + (y1 + y2) / 2
    ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    pts = []
    for k in range(1, n + 1):
        t = t1 + dt * k / n
        pts.append((cp * rx * math.cos(t) - sp * ry * math.sin(t) + cx,
                    sp * rx * math.cos(t) + cp * ry * math.sin(t) + cy))
    return pts


def flatten(segs):
    """-> list of subpaths, each a list of (x, y) points (curves/arcs sampled)."""
    subs, cur, cx, cy = [], [], 0.0, 0.0
    for s in segs:
        k = s[0]
        if k == "M":
            if len(cur) > 1:
                subs.append(cur)
            cx, cy = s[1], s[2]; cur = [(cx, cy)]
        elif k == "L":
            cx, cy = s[1], s[2]; cur.append((cx, cy))
        elif k == "C":
            for t in [i / 10 for i in range(1, 11)]:
                u = 1 - t
                cur.append((u**3 * cx + 3 * u * u * t * s[1] + 3 * u * t * t * s[3] + t**3 * s[5],
                            u**3 * cy + 3 * u * u * t * s[2] + 3 * u * t * t * s[4] + t**3 * s[6]))
            cx, cy = s[5], s[6]
        elif k == "A":
            cur += _arc_points(cx, cy, s[1], s[2], s[3], s[4], s[5], s[6], s[7])
            cx, cy = s[6], s[7]
        elif k == "Z" and cur:
            cx, cy = cur[0]
    if len(cur) > 1:
        subs.append(cur)
    return subs


def bbox_of(segs):
    pts = [p for sub in flatten(segs) for p in sub]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts))) / 2


def hole_risk(segs):
    """Heuristic WARNING for the 'opposite-winding donut hole' trap: a subpath whose
    bbox lies inside another subpath's bbox and winds the opposite way."""
    subs = [(p, _area(p)) for p in flatten(segs) if len(p) > 2]
    bb = [(min(q[0] for q in p), min(q[1] for q in p), max(q[0] for q in p), max(q[1] for q in p))
          for p, _ in subs]
    risks = 0
    for i in range(len(subs)):
        for j in range(len(subs)):
            if i != j and subs[i][1] * subs[j][1] < 0:
                a, b = bb[i], bb[j]
                if a[0] <= b[0] and a[1] <= b[1] and a[2] >= b[2] and a[3] >= b[3] \
                        and abs(subs[i][1]) > abs(subs[j][1]):
                    risks += 1
    return risks


# ---------------------------------------------------------------------------
# 3. AI-pen builders
# ---------------------------------------------------------------------------
_HEX6 = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _hex6(c, default):
    """Only plain #RRGGBB is allowed in AI-pen fill/stroke (Android CRASHES otherwise)."""
    if isinstance(c, str):
        c = c.strip()
        if _HEX6.match(c):
            return c.upper()
        if re.match(r"^#[0-9A-Fa-f]{3}$", c):
            return "#" + "".join(ch * 2 for ch in c[1:]).upper()
    return default


def _ai_pen(items, matrix, w, h, stroke_color, stroke_width):
    """items = [(d, fill6)]. Foreground + MIRRORED background container (required:
    an AI-pen with an empty background container or identity matrix can render invisible)."""
    fg, bg = [], []
    for d, fill in items:
        stroke = stroke_color or fill
        p = {"id": uid(), "x": 0.0, "y": 0.0, "width": float(w), "height": float(h),
             "fill-opacity": 1.0, "fill": fill, "stroke-width": float(stroke_width),
             "stroke-opacity": 1.0 if stroke_width > 0 else 0.0,
             "stroke-miter-limit": 10.0, "lineshape-start": "round",
             "lineshape-end": "round", "lineshape-join": "round",
             "stroke": stroke, "data": d, "matrix": matrix}
        q = dict(p); q["id"] = uid(); q["fill-opacity"] = 0.3
        q["stroke-width"] = 0.5; q["stroke-opacity"] = 0.3 if stroke_width > 0 else 0.0
        fg.append({"path": p}); bg.append({"path": q})
    pid = uid()
    elem = {"AI-pen": {"id": pid, "matrix": matrix,
                       "foreground-objects-container": fg,
                       "background-objects-container": bg}}
    # AI-pen `additional` entry has NO "flip" field.
    add = {"element": {"id": uid(), "ref": pid, "is-locked": False,
                       "is-moveable-locked": False, "is-replicate": False}}
    return elem, add


def ai_pen_icon(paths, x, y, size, vb=24.0, fill="#1565C0", stroke_color=None,
                stroke_width=0.0):
    """Place SVG path data on the canvas as a true-vector AI-pen shape.

    paths : list of `d` strings, or (d, "#RRGGBB") tuples for per-path colours
    x, y  : canvas top-left of the icon box;  size : displayed px (square box)
    vb    : the icon's own viewBox size (24 for Material/MDI, 256 Phosphor, 16 Bootstrap)
    Paths are scrubbed to absolute M/L/C/A/Z and kept non-negative (offset folded
    into the matrix). Solid fill only: gradients / currentColor / names are replaced
    with `fill`.  Returns (element, additional_entry) -- feed to page.add()."""
    items, all_segs = [], []
    for it in paths:
        d, f = (it, None) if isinstance(it, str) else it
        segs = parse_path(d)
        all_segs.append(segs)
        items.append((segs, _hex6(f, _hex6(fill, "#1565C0"))))
    mins_x = min(bbox_of(s)[0] for s in all_segs)
    mins_y = min(bbox_of(s)[1] for s in all_segs)
    sx_ = -mins_x if mins_x < 0 else 0.0
    sy_ = -mins_y if mins_y < 0 else 0.0
    maxx = max(bbox_of(s)[2] for s in all_segs) + sx_
    maxy = max(bbox_of(s)[3] for s in all_segs) + sy_
    scale = float(size) / float(vb)
    tx, ty = x - sx_ * scale, y - sy_ * scale
    matrix = "%s,0,%s,0,%s,%s,0,0,1" % (_fmt(scale), _fmt(tx), _fmt(scale), _fmt(ty))
    ready = [(segs_to_d(s, sx_, sy_), f) for s, f in items]
    return _ai_pen(ready, matrix, max(vb, maxx), max(vb, maxy),
                   _hex6(stroke_color, None), stroke_width)


def ai_pen_rounded_rect(x, y, w, h, r, fill, stroke=None, stroke_width=0.0):
    """Rounded-rectangle card. Identical to the reference engine's make_rounded_rect.
    Keep stroke_width=0 (strokes render thicker on the curved corners)."""
    r = float(max(0.0, min(r, min(w, h) / 2.0)))
    lw, lh = float(w), float(h)
    if r <= 0:
        d = "M0.0,0.0 L%s,0.0 L%s,%s L0.0,%s Z" % (lw, lw, lh, lh)
    else:
        d = ("M%s,0.0 L%s,0.0 A%s,%s 0 0 1 %s,%s L%s,%s A%s,%s 0 0 1 %s,%s "
             "L%s,%s A%s,%s 0 0 1 0.0,%s L0.0,%s A%s,%s 0 0 1 %s,0.0 Z" % (
                 r, lw - r, r, r, lw, r, lw, lh - r, r, r, lw - r, lh,
                 r, lh, r, r, lh - r, r, r, r, r))
    matrix = "1,0,%s,0,1,%s,0,0,1" % (x, y)
    return _ai_pen([(d, fill)], matrix, lw, lh, stroke, stroke_width)


# ---------------------------------------------------------------------------
# 4. SVG text -> paths  (+ lint)
# ---------------------------------------------------------------------------
def _local(tag):
    return tag.split("}")[-1]


def _ellipse_d(cx, cy, rx, ry):
    return "M%s %sA%s %s 0 1 0 %s %sA%s %s 0 1 0 %s %sZ" % (
        _fmt(cx - rx), _fmt(cy), _fmt(rx), _fmt(ry), _fmt(cx + rx), _fmt(cy),
        _fmt(rx), _fmt(ry), _fmt(cx - rx), _fmt(cy))


def _rect_d(x, y, w, h, rx, ry):
    rx, ry = min(rx or ry or 0, w / 2), min(ry or rx or 0, h / 2)
    if rx <= 0 or ry <= 0:
        return "M%s %sL%s %sL%s %sL%s %sZ" % (_fmt(x), _fmt(y), _fmt(x + w), _fmt(y),
                                               _fmt(x + w), _fmt(y + h), _fmt(x), _fmt(y + h))
    return ("M%s %sL%s %sA%s %s 0 0 1 %s %sL%s %sA%s %s 0 0 1 %s %sL%s %sA%s %s 0 0 1 %s %s"
            "L%s %sA%s %s 0 0 1 %s %sZ" % (
                _fmt(x + rx), _fmt(y), _fmt(x + w - rx), _fmt(y), _fmt(rx), _fmt(ry),
                _fmt(x + w), _fmt(y + ry), _fmt(x + w), _fmt(y + h - ry), _fmt(rx), _fmt(ry),
                _fmt(x + w - rx), _fmt(y + h), _fmt(x + rx), _fmt(y + h), _fmt(rx), _fmt(ry),
                _fmt(x), _fmt(y + h - ry), _fmt(x), _fmt(y + ry), _fmt(rx), _fmt(ry),
                _fmt(x + rx), _fmt(y)))


def svg_to_paths(svg_text):
    """Extract fillable shapes from SVG text -> ([(d, '#RRGGBB'|None)], (vw, vh), warnings).
    Handles path, circle, ellipse, rect (incl. rounded), polygon, polyline.
    Ignores (with a warning): transforms, strokes-only shapes, gradients, text, use."""
    warns = []
    root = ET.fromstring(svg_text)
    vb = root.get("viewBox")
    if vb:
        parts = [float(v) for v in re.split(r"[ ,]+", vb.strip())]
        vw, vh = parts[2], parts[3]
        if parts[0] or parts[1]:
            warns.append("viewBox origin is not 0,0 -- shapes may need shifting")
    else:
        num = lambda s: float(re.sub(r"[a-z%]+$", "", s or "24"))
        vw, vh = num(root.get("width")), num(root.get("height"))
    out = []
    num = lambda e, k, dflt=0.0: float(re.sub(r"[a-z%]+$", "", e.get(k) or str(dflt)))
    for el in root.iter():
        t = _local(el.tag)
        if t in ("text", "use", "symbol", "mask", "pattern", "foreignObject", "image"):
            warns.append("<%s> is not converted (unsupported)" % t)
        if t in ("linearGradient", "radialGradient"):
            warns.append("gradients are not supported in AI-pen -- solid fill used")
        if el.get("transform"):
            warns.append("transform=%r on <%s> ignored -- bake transforms into coordinates" % (el.get("transform"), t))
        d = None
        if t == "path":
            d = el.get("d")
        elif t == "circle":
            d = _ellipse_d(num(el, "cx"), num(el, "cy"), num(el, "r"), num(el, "r"))
        elif t == "ellipse":
            d = _ellipse_d(num(el, "cx"), num(el, "cy"), num(el, "rx"), num(el, "ry"))
        elif t == "rect":
            d = _rect_d(num(el, "x"), num(el, "y"), num(el, "width"), num(el, "height"),
                        num(el, "rx"), num(el, "ry"))
        elif t in ("polygon", "polyline"):
            nums = [float(v) for v in re.findall(r"[-+]?\d*\.?\d+", el.get("points", ""))]
            pts = list(zip(nums[0::2], nums[1::2]))
            if pts:
                d = "M" + "L".join("%s %s" % (_fmt(a), _fmt(b)) for a, b in pts) + "Z"
        elif t == "line":
            warns.append("<line> has no fill -- not converted (use a thin rect instead)")
        if not d:
            continue
        fillv = el.get("fill")
        if (fillv or "").strip().lower() == "none":
            warns.append("<%s> has fill=none (stroke-only) -- skipped; AI-pen icons are fill-based" % t)
            continue
        f = _hex6(fillv, None)
        if fillv and f is None and fillv != "currentColor":
            warns.append("fill %r is not plain hex -- default fill used" % fillv)
        out.append((d, f))
    return out, (vw, vh), warns


_BAD = [("pattern", "<pattern> fills render SOLID BLACK -- do not use"),
        ("mask", "<mask> is ignored (flat opaque) -- use clipPath or pre-render"),
        ("text", "<text> renders NOTHING -- convert text to paths (AI-pen glyph outlines)"),
        ("use", "<use> does not resolve -- inline the geometry"),
        ("symbol", "<symbol> does not resolve -- inline the geometry"),
        ("foreignObject", "<foreignObject> content is silently dropped"),
        ("animate", "SMIL animation never plays (static render)"),
        ("animateTransform", "SMIL animation never plays (static render)"),
        ("set", "SMIL animation never plays (static render)")]


def svg_lint(svg_text, display_w=None):
    """Warnings for features that fail inside an `image`-element SVG."""
    w = []
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as e:
        return ["SVG is not well-formed XML: %s" % e]
    seen = set()
    for el in root.iter():
        t = _local(el.tag)
        for tag, msg in _BAD:
            if t == tag and tag not in seen:
                seen.add(tag); w.append(msg)
        href = el.get("{http://www.w3.org/1999/xlink}href") or el.get("href")
        if href and href.startswith("http"):
            w.append("external resource %s will not load" % href[:40])
    if "@keyframes" in svg_text or "animation:" in svg_text:
        w.append("CSS animation never plays (static render)")
    if display_w:
        wid = root.get("width")
        if wid and re.match(r"^[\d.]+(px)?$", wid) and float(re.sub("px", "", wid)) < display_w * 4:
            w.append("intrinsic width %s < 4x display width %s -- will look blurry; author ~8x" % (wid, display_w))
    return w


def _set_svg_size(svg_text, w, h):
    m = re.search(r"<svg\b[^>]*>", svg_text)
    tag = m.group(0)
    new = tag
    if "viewBox" not in tag:
        ow = re.search(r'\bwidth="([\d.]+)', tag); oh = re.search(r'\bheight="([\d.]+)', tag)
        if ow and oh:
            new = new.replace("<svg", '<svg viewBox="0 0 %s %s"' % (ow.group(1), oh.group(1)), 1)
    for attr, val in (("width", w), ("height", h)):
        if re.search(r'\b%s="[^"]*"' % attr, new):
            new = re.sub(r'\b%s="[^"]*"' % attr, '%s="%d"' % (attr, val), new, 1)
        else:
            new = new.replace("<svg", '<svg %s="%d"' % (attr, val), 1)
    return svg_text.replace(tag, new, 1)


def add_svg_image(page, doc, name, svg_text, x, y, w, h, oversample=8):
    """`image` element with mime image/svg+xml. Rewrites the SVG root width/height to
    oversample x the display size (myViewBoard rasterises at intrinsic size, so
    authoring ~8x bigger stays sharp when the user enlarges it). Prints lint warnings."""
    for msg in svg_lint(svg_text):
        print("SVG WARNING:", msg)
    svg_text = _set_svg_size(svg_text, int(w * oversample), int(h * oversample))
    arc = "images/%s.svg" % re.sub(r"[^A-Za-z0-9_-]", "_", name)
    doc.extra_files[arc] = svg_text.encode("utf-8")
    return page.add({"image": {"id": uid(), "x": float(x), "y": float(y),
                               "width": float(w), "height": float(h),
                               "mime-type": "image/svg+xml", "source": arc,
                               "matrix": MATRIX}})

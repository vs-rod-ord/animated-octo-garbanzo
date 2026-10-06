"""olf_validate.py -- run this on your .olf BEFORE delivering it. Standard library only.

    report = validate_olf("out.olf")        # path to .olf, or a content dict
    print_report(report)                    # prints ERRORS / WARNINGS / summary

Rule: fix every ERROR, re-run until `errors == []`, and show the user the final
report. WARNINGS are judgement calls; fix them unless you have a reason.

Every check here exists because of a real failure (see constraints/*.md).
"""
import json
import re
import textwrap
import zipfile

SEP = "\u300e\u300e\u300e"
META_KEYS = ["id", "create-platform", "create-by-library", "create-time", "modify-time",
             "create-library-version", "create-version", "modify-version", "modify-platform"]
SHAPE_KINDS = {"polygon", "ellipse", "polyline", "curve", "quadrant", "pseudo3Dshape"}
FLIP_KINDS = SHAPE_KINDS
HEX6, HEX8 = re.compile(r"^#[0-9A-Fa-f]{6}$"), re.compile(r"^#[0-9A-Fa-f]{8}$")
MATRIX9 = re.compile(r"^(-?[\d.eE+-]+,){8}-?[\d.eE+-]+$")


_PITCH = {"Segoe UI": 1.80, "Calibri": 1.65, "Georgia": 1.55, "Open Sans": 1.85,
          "Times New Roman": 1.55}      # measured pitch/pt rounded up; bold is NOT different


def _est_lines(text, pt, width, bold=False, avg=None):
    px = round(pt * 4 / 3)
    avg = avg or (0.60 if bold else 0.55)          # fraction of the pixel font size per character
    per = max(1, int(width / (px * avg)))
    return sum(max(1, len(textwrap.wrap(p, per, break_long_words=True)))
               for p in str(text).split("\n"))


def validate_olf(src):
    errs, warns = [], []
    E, Wn = errs.append, warns.append

    # ---- load -------------------------------------------------------------
    zipnames, svgs = None, {}
    if isinstance(src, dict):
        data = src
    else:
        try:
            with zipfile.ZipFile(src) as zf:
                names = zf.namelist()
                zipnames = set(names)
                if "content.json" not in names:
                    E("ZIP has no content.json at the archive ROOT (found: %s)" % names[:5])
                    return {"errors": errs, "warnings": warns, "stats": {}}
                data = json.loads(zf.read("content.json").decode("utf-8"))
                for nm in names:
                    if nm.lower().endswith(".svg"):
                        svgs[nm] = zf.read(nm).decode("utf-8", "replace")
        except zipfile.BadZipFile:
            E("not a valid ZIP file")
            return {"errors": errs, "warnings": warns, "stats": {}}

    # ---- envelope ---------------------------------------------------------
    if not isinstance(data, dict) or list(data.keys()) != ["olf"]:
        E("root must be an object with exactly one key 'olf' (got %s)"
          % (list(data.keys()) if isinstance(data, dict) else type(data).__name__))
        return {"errors": errs, "warnings": warns, "stats": {}}
    olf = data["olf"]
    for k in ("width", "height", "viewbox", "meta", "pageset", "additional", "links", "groups"):
        if k not in olf:
            E("olf missing key '%s'" % k)
    if " " not in str(olf.get("viewbox", "")) or "," in str(olf.get("viewbox", "")):
        E("olf.viewbox must be SPACE-separated, e.g. '0 0 1920 1080' (got %r)" % olf.get("viewbox"))
    for k in META_KEYS:
        if k not in olf.get("meta", {}):
            E("meta missing '%s' (all 9 fields required)" % k)
    if not isinstance(olf.get("additional"), list):
        E("'additional' must be ONE array on the root olf object")

    ids, elems = {}, {}              # id -> where ; element id -> (kind, dict, page_no)
    def reg(i, where):
        if not i:
            E("%s has no id" % where)
        elif i in ids:
            E("duplicate id %s (%s and %s)" % (i, ids[i], where))
        else:
            ids[i] = where

    reg(olf.get("meta", {}).get("id"), "meta")
    pages = olf.get("pageset", [])
    if not pages:
        E("pageset is empty")
    for pn, wrap in enumerate(pages, 1):
        if not isinstance(wrap, dict) or list(wrap.keys()) != ["page"]:
            E("pageset[%d] must be {\"page\": {...}}" % (pn - 1))
            continue
        pg = wrap["page"]
        reg(pg.get("id"), "page %d" % pn)
        if "," not in str(pg.get("viewbox", "")) or " " in str(pg.get("viewbox", "")):
            E("page %d viewbox must be COMMA-separated '0,0,1920,1080' (got %r)"
              % (pn, pg.get("viewbox")))
        if "matrix" not in pg:
            E("page %d missing 'matrix'" % pn)
        if "is-hidden" not in pg:
            E("page %d missing 'is-hidden'" % pn)
        bgs = pg.get("backgrounds")
        if not isinstance(bgs, list) or not bgs or "background" not in bgs[0]:
            E("page %d 'backgrounds' must be an array of {\"background\": {id,type,fill,opacity}}" % pn)
        else:
            reg(bgs[0]["background"].get("id"), "page %d background" % pn)
        if "additional" in pg:
            E("page %d has its own 'additional' -- it belongs ONCE on the root olf object" % pn)
        for el in pg.get("elements", []):
            if not isinstance(el, dict) or len(el) != 1:
                E("page %d has a malformed element wrapper" % pn)
                continue
            kind, body = next(iter(el.items()))
            where = "page %d %s" % (pn, kind)
            reg(body.get("id"), where)
            elems[body.get("id")] = (kind, body, pn)
            _check_element(kind, body, where, E, Wn, reg)

    # ---- additional <-> elements -----------------------------------------
    refd = set()
    for i, a in enumerate(olf.get("additional", [])):
        e = a.get("element") if isinstance(a, dict) else None
        if not e:
            E("additional[%d] must be {\"element\": {...}}" % i)
            continue
        reg(e.get("id"), "additional[%d]" % i)
        ref = e.get("ref")
        if ref not in elems:
            E("additional[%d] ref %s matches no element" % (i, ref))
            continue
        if ref in refd:
            E("two additional entries for element %s" % ref)
        refd.add(ref)
        kind = elems[ref][0]
        if kind == "AI-pen" and "flip" in e:
            E("additional entry for AI-pen must NOT have 'flip'")
        if kind in FLIP_KINDS and e.get("flip") != "none":
            E("additional entry for %s needs \"flip\": \"none\"" % kind)
        for an in e.get("animation-container", []):
            d = an.get("animation", {})
            reg(d.get("id"), "animation")
            if not isinstance(d.get("duration"), str) or d.get("duration") not in "0123" or not d.get("duration"):
                E("animation duration must be the STRING '0'..'3' (got %r)" % d.get("duration"))
            if d.get("type") not in ("fade-in", "fade-out"):
                E("animation type must be fade-in|fade-out (got %r)" % d.get("type"))
    for rid, (kind, body, pn) in elems.items():
        if kind in SHAPE_KINDS and rid not in refd:
            E("page %d %s %s has no entry in root 'additional'" % (pn, kind, rid))

    # ---- links ------------------------------------------------------------
    n_pages = len(pages)
    for i, lk in enumerate(olf.get("links", [])):
        d = lk.get("link", {}) if isinstance(lk, dict) else {}
        reg(d.get("id"), "link %d" % i)
        if d.get("ref") not in elems:
            E("link %d ref matches no element" % i)
        lt = d.get("link-type")
        if lt == "page":
            pid = d.get("page-id")
            if not (isinstance(pid, str) and pid.isdigit() and 1 <= int(pid) <= n_pages):
                E("link %d page-id must be a 1-based ORDINAL STRING within 1..%d (got %r)"
                  % (i, n_pages, pid))
        elif lt == "web" and not d.get("url"):
            E("link %d web link needs 'url'" % i)
        elif lt not in ("page", "web", "text", "tool", "file", "audio"):
            E("link %d unknown link-type %r" % (i, lt))

    # ---- text: tables, overlap, height -----------------------------------
    cell_text = set()
    for rid, (kind, b, pn) in elems.items():
        if kind == "table":
            _check_table(b, pn, elems, cell_text, E, Wn)
    boxes = []
    for rid, (kind, b, pn) in elems.items():
        if kind != "textarea":
            continue
        txt, pt = _text_of(b)
        if pt:
            fam, bold = _font_of(b)
            # minimum honest height: (n-1) wrapped-line pitches + one line box (~1.25 x pt).
            # The starter reserves more (n x pitch); this is the floor, to avoid false alarms
            # on single-line boxes sized by hand.
            pitch = _PITCH.get(fam, 1.85)
            n_hi = _est_lines(txt, pt, b["width"], bold)                 # generous count
            n_lo = _est_lines(txt, pt, b["width"], bold, 0.48 if not bold else 0.52)  # tight count
            need_hi = ((n_hi - 1) * pitch + 1.25) * pt
            need_lo = ((n_lo - 1) * pitch + 1.25) * pt
            if b["height"] < need_lo * 0.95:           # too short even on the optimistic count
                E("page %d textarea %r: height %.1f < estimated wrapped height %.1f "
                  "(lines*pitch). Do NOT use pitch alone as height." % (pn, txt[:40], b["height"], need_lo))
            elif b["height"] < need_hi * 0.95:         # only the generous count disagrees
                Wn("page %d textarea %r: height %.1f may be too short if the text wraps to %d lines "
                   "(needs ~%.0f)" % (pn, txt[:40], b["height"], n_hi, need_hi))
            _check_rtf(b, txt, pt, pn, E, Wn)
        if rid not in cell_text:
            boxes.append((pn, rid, b["x"], b["y"], b["x"] + b["width"], b["y"] + b["height"], txt))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, c = boxes[i], boxes[j]
            if a[0] != c[0]:
                continue
            ox = min(a[4], c[4]) - max(a[2], c[2])
            oy = min(a[5], c[5]) - max(a[3], c[3])
            if ox > 1 and oy > 1:           # true 2-D overlap (x AND y)
                E("page %d text overlap: %r and %r overlap by %.0fx%.0f"
                  % (a[0], a[6][:30], c[6][:30], ox, oy))
    # images: source must exist in the zip; SVG sources get linted
    for rid, (kind, b, pn) in elems.items():
        if kind == "image" and zipnames is not None:
            s = b.get("source")
            if s not in zipnames:
                E("page %d image source %r is not in the ZIP (images must be stored at that path)" % (pn, s))
            elif s in svgs:
                _lint_svg(s, svgs[s], b.get("width"), pn, Wn)
            if b.get("mime-type") == "image/svg+xml" and s and not str(s).lower().endswith(".svg"):
                Wn("page %d image mime is svg+xml but source %r does not end in .svg" % (pn, s))
    # off-canvas
    for rid, (kind, b, pn) in elems.items():
        if kind in ("textarea", "image", "table") and \
                (b.get("x", 0) < -1 or b.get("y", 0) < -1 or
                 b.get("x", 0) + b.get("width", 0) > 1921 or b.get("y", 0) + b.get("height", 0) > 1081):
            Wn("page %d %s extends beyond the 1920x1080 canvas" % (pn, kind))

    # ---- layout collisions between text and shapes / arrows ---------------
    per_page = {}
    for rid, (kind, b, pn) in elems.items():              # insertion order = draw order
        per_page.setdefault(pn, []).append((kind, b, rid))
    for pn, items in per_page.items():
        for i, (kind, b, rid) in enumerate(items):
            if kind != "textarea" or rid in cell_text:
                continue
            tb = (b["x"], b["y"], b["x"] + b["width"], b["y"] + b["height"])
            area = max(1.0, (tb[2] - tb[0]) * (tb[3] - tb[1]))
            txt = _text_of(b)[0]
            for kind2, b2, rid2 in items[i + 1:]:          # shapes drawn AFTER the text cover it
                if kind2 not in ("polygon", "ellipse", "AI-pen", "quadrant"):
                    continue
                sb = _bbox(kind2, b2)
                if not sb or not _opaque(kind2, b2):
                    continue
                ox = min(tb[2], sb[2]) - max(tb[0], sb[0])
                oy = min(tb[3], sb[3]) - max(tb[1], sb[1])
                if ox <= 2 or oy <= 2:
                    continue
                if ox * oy >= 0.9 * area:
                    E("page %d text %r is hidden BEHIND a %s drawn after it -- add the shape first, "
                      "the text after (draw order = list order)" % (pn, txt[:30], kind2))
                elif ox * oy >= 0.3 * area:
                    Wn("page %d text %r is partly covered by a %s drawn after it (%.0f%% of the box)"
                       % (pn, txt[:30], kind2, 100.0 * ox * oy / area))
        for kind, b, rid in items:
            if kind not in ("curve", "polyline"):
                continue
            pts = _line_points(kind, b)
            for kind2, b2, rid2 in items:
                if kind2 != "textarea" or rid2 in cell_text:
                    continue
                x0, y0, x1, y1 = b2["x"] + 4, b2["y"] + 4, b2["x"] + b2["width"] - 4, b2["y"] + b2["height"] - 4
                inside = sum(1 for (px, py) in pts if x0 < px < x1 and y0 < py < y1)
                if inside >= 3:
                    Wn("page %d a %s passes through the text %r -- move the arrow or the text"
                       % (pn, kind, _text_of(b2)[0][:30]))

    stats = {"pages": n_pages, "elements": len(elems), "additional": len(olf.get("additional", [])),
             "links": len(olf.get("links", []))}
    return {"errors": errs, "warnings": warns, "stats": stats}


def _mat(b):
    try:
        m = [float(v) for v in str(b.get("matrix", "")).split(",")]
        return m[0], m[2], m[4], m[5]          # sx, tx, sy, ty
    except Exception:
        return 1.0, 0.0, 1.0, 0.0


def _bbox(kind, b):
    """Canvas-space bounding box (x0, y0, x1, y1) of a filled shape, or None."""
    try:
        if kind == "polygon":
            pts = [tuple(float(v) for v in p.split(",")) for p in b["points"].split()]
            return (min(p[0] for p in pts), min(p[1] for p in pts),
                    max(p[0] for p in pts), max(p[1] for p in pts))
        sx, tx, sy, ty = _mat(b)
        if kind == "ellipse":
            return (tx, ty, tx + b["rx"] * 2, ty + b["ry"] * 2)
        if kind == "AI-pen":
            p = b["foreground-objects-container"][0]["path"]
            return (tx, ty, tx + sx * p["width"], ty + sy * p["height"])
    except Exception:
        return None
    return None


def _opaque(kind, b):
    try:
        if kind == "AI-pen":
            return b["foreground-objects-container"][0]["path"].get("fill-opacity", 1.0) >= 0.5
        return float(b.get("fill-opacity", 1.0)) >= 0.5
    except Exception:
        return False


def _line_points(kind, b):
    """~12 canvas-space sample points along a curve (quadratic) or polyline."""
    try:
        if kind == "polyline":
            pts = [tuple(float(v) for v in p.split(",")) for p in b["points"].split()]
            out = []
            for (ax, ay), (cx, cy) in zip(pts, pts[1:]):
                out += [(ax + (cx - ax) * t / 8.0, ay + (cy - ay) * t / 8.0) for t in range(9)]
            return out
        s, v, e = [tuple(float(q) for q in b[k].split(",")) for k in ("start-point", "second-point", "end-point")]
        out = []
        for t in [i / 12.0 for i in range(13)]:
            u = 1 - t
            out.append((b["x"] + u * u * s[0] + 2 * u * t * v[0] + t * t * e[0],
                        b["y"] + u * u * s[1] + 2 * u * t * v[1] + t * t * e[1]))
        return out
    except Exception:
        return []


def _font_of(b):
    for p in b.get("text-blocks-container", []):
        for t in p.get("paragraph", {}).get("text-list-container", []):
            r = t.get("text", {})
            return r.get("font-family", "Segoe UI"), r.get("font-weight") == "bold"
    return "Segoe UI", False


def _text_of(b):
    runs, pt = [], None
    for p in b.get("text-blocks-container", []):
        for t in p.get("paragraph", {}).get("text-list-container", []):
            r = t.get("text", {})
            runs.append(r.get("text", ""))
            if pt is None and r.get("font-size"):
                pt = r["font-size"] * 3 / 4          # px -> pt
    return "".join(runs), pt


def _check_rtf(b, txt, pt, pn, E, Wn):
    rtf = b.get("custom-data", "")
    if not rtf:
        Wn("page %d textarea %r has empty custom-data (RTF); Windows renders from RTF" % (pn, txt[:30]))
        return
    m = re.search(r"\\fs(\d+)", rtf)
    if m and abs(int(m.group(1)) - pt * 2) > 2:
        E("page %d textarea %r: RTF \\fs%s disagrees with JSON font-size (%.0f px => \\fs%.0f). "
          "JSON is px = pt*4/3; RTF is pt*2." % (pn, txt[:30], m.group(1), pt * 4 / 3, pt * 2))
    if "Arial" in rtf:
        Wn("page %d textarea %r: the literal word 'Arial' is rewritten to 'Calibri' by "
           "myViewBoard (escape it as Ari\\u8288?al; never use Arial as a font)" % (pn, txt[:30]))
    cm = re.search(r"\\red(\d+)\\green(\d+)\\blue(\d+)", rtf)
    for p in b.get("text-blocks-container", []):
        for t in p.get("paragraph", {}).get("text-list-container", []):
            f = t.get("text", {}).get("fill", "")
            if not HEX8.match(f):
                E("page %d textarea %r: text fill %r must be 8-digit #AARRGGBB" % (pn, txt[:30], f))
            elif cm:
                want = "#%02X%02X%02X" % tuple(int(v) for v in cm.groups())
                if f[3:].upper() != want[1:]:
                    E("page %d textarea %r: JSON fill %s != RTF colortbl %s" % (pn, txt[:30], f, want))


def _check_element(kind, b, where, E, Wn, reg):
    if "matrix" in b and not MATRIX9.match(str(b["matrix"])):
        E("%s matrix must be 9 comma-separated numbers (got %r)" % (where, b["matrix"]))
    if kind in ("polygon", "ellipse", "polyline", "curve", "quadrant", "pseudo3Dshape"):
        for key in ("fill", "stroke"):
            if key in b and not HEX6.match(str(b[key])):
                E("%s %s %r must be 6-digit #RRGGBB (8-digit is for TEXT fill only)" % (where, key, b[key]))
        if kind in ("curve", "polyline", "polygon", "ellipse") and "stroke-opacity" not in b:
            E("%s needs explicit stroke-opacity (a curve without it is INVISIBLE)" % where)
        if kind == "curve" and b.get("stroke-opacity", 1) == 0:
            E("%s stroke-opacity is 0 -- invisible arrow" % where)
        for key in ("show-length-measurement", "show-angle-measurement"):
            v = b.get(key)
            if v and ("\u300e" in v) and ("\u300e" * 3 not in v or "\u300e" * 4 in v):
                E("%s %s must use the TRIPLE separator (3 x U+300E), never 2 or 4" % (where, key))
            if v and "\u300e" not in v and "true" in v and v.count("true") > 1:
                E("%s %s has several entries but no U+300E separator" % (where, key))
    if kind == "textarea":
        for k in ("custom-data-tag", "text-blocks-container"):
            if k not in b:
                E("%s missing %s" % (where, k))
        if b.get("custom-data-tag") and b["custom-data-tag"] != "RTFxamlStr_UWP":
            Wn("%s custom-data-tag is %r (expected RTFxamlStr_UWP)" % (where, b["custom-data-tag"]))
        for p in b.get("text-blocks-container", []):
            pp = p.get("paragraph", {})
            reg(pp.get("id"), where + " paragraph")
            for t in pp.get("text-list-container", []):
                r = t.get("text", {})
                reg(r.get("id"), where + " run")
                fs = r.get("font-size")
                if fs is not None and fs > 130 * 4 / 3 + 1:
                    E("%s font-size %s px exceeds the 130pt cap" % (where, fs))
                if fs is not None and fs != int(fs):
                    Wn("%s font-size %s is not a whole pixel number" % (where, fs))
    if kind == "image" and not b.get("source"):
        E("%s image missing 'source'" % where)
    if kind == "AI-pen":
        _check_ai_pen(b, where, E, Wn, reg)


_IDENT = "1,0,0,0,1,0,0,0,1"
_BAD_SVG = [("<pattern", "<pattern> fills render SOLID BLACK"), ("<mask", "<mask> is ignored"),
            ("<text", "<text> renders NOTHING (convert to paths)"),
            ("<use", "<use> does not resolve (inline it)"), ("<symbol", "<symbol> does not resolve"),
            ("<foreignObject", "<foreignObject> content is dropped"),
            ("<animate", "SMIL animation never plays"), ("<set ", "SMIL animation never plays"),
            ("@keyframes", "CSS animation never plays")]


def _lint_svg(name, text, display_w, pn, Wn):
    for tok, msg in _BAD_SVG:
        if tok in text:
            Wn("page %d SVG %s: %s" % (pn, name, msg))
    m = re.search(r"<svg\b[^>]*>", text)
    if m and display_w:
        wm = re.search(r'\bwidth="([\d.]+)', m.group(0))
        if not wm:
            Wn("page %d SVG %s has no width attribute -- intrinsic size unknown; author ~8x display" % (pn, name))
        elif float(wm.group(1)) < display_w * 4:
            Wn("page %d SVG %s intrinsic width %s < 4x display %.0f -- will look blurry" % (pn, name, wm.group(1), display_w))


def _check_ai_pen(b, where, E, Wn, reg):
    fgs = b.get("foreground-objects-container", [])
    bgs = b.get("background-objects-container", [])
    if not fgs:
        E("%s has no foreground-objects-container paths" % where)
    if not bgs:
        E("%s background-objects-container is EMPTY -- must mirror the foreground at fill-opacity 0.3 "
          "or the shape can render invisible" % where)
    elif len(bgs) != len(fgs):
        Wn("%s background has %d paths, foreground %d (should mirror)" % (where, len(bgs), len(fgs)))
    if b.get("matrix") == _IDENT:
        E("%s uses the IDENTITY matrix -- AI-pen needs a real scale/translate matrix or it can render invisible" % where)
    for grp, lst in (("foreground", fgs), ("background", bgs)):
        for item in lst:
            pth = item.get("path", {})
            reg(pth.get("id"), where + " " + grp + " path")
            for key in ("fill", "stroke"):
                if not HEX6.match(str(pth.get(key, ""))):
                    E("%s %s path %s %r must be plain #RRGGBB (non-hex CRASHES Android)"
                      % (where, grp, key, pth.get(key)))
            d = str(pth.get("data", ""))
            if not d:
                E("%s %s path has no 'data'" % (where, grp))
                continue
            if grp == "foreground":
                if re.search(r"[HhVvQqTtSsmlcaz]", d):
                    Wn("%s path data uses relative/shorthand commands (H V Q S T or lowercase) -- "
                       "prefer absolute M L C A Z only" % where)
                if re.search(r"(?<![0-9.eE])-\d", d):
                    Wn("%s path data has NEGATIVE coordinates -- keep local coords >= 0 and fold the "
                       "offset into the matrix" % where)
            if "url(" in d or "currentColor" in d:
                E("%s path data contains a paint reference" % where)


def _check_table(b, pn, elems, cell_text, E, Wn):
    rows, cols = b.get("rows", 0), b.get("columns", 0)
    nb = len(b.get("cell-background-container", []))
    if nb != rows * cols:
        E("page %d table: cell-background-container has %d entries, expected rows*cols=%d" % (pn, nb, rows * cols))
    mc = b.get("merge-cell-container", [])
    if mc and len(mc) != rows * cols:
        E("page %d table: merge-cell-container must have one entry per cell (%d), has %d" % (pn, rows * cols, len(mc)))
    for c in b.get("cell-content-container", []):
        d = c.get("cell-content", {})
        r, k = d.get("cell-row"), d.get("cell-column")
        if r is None or k is None or r % 2 or k % 2 or r > 2 * (rows - 1) or k > 2 * (cols - 1):
            E("page %d table cell-content (%s,%s) must use EVEN indices 2r,2c within the table" % (pn, r, k))
        if d.get("ref") not in elems:
            E("page %d table cell-content ref matches no element" % pn)
        else:
            cell_text.add(d["ref"])
    for lst in ("column-lengths-array", "row-lengths-array"):
        n = len(str(b.get(lst, "")).split())
        if n != (cols if lst.startswith("column") else rows):
            E("page %d table %s has %d values, expected %d" % (pn, lst, n, cols if lst.startswith("column") else rows))


def print_report(rep):
    print("STATS:", rep["stats"])
    for e in rep["errors"]:
        print("ERROR  :", e)
    for w in rep["warnings"]:
        print("WARNING:", w)
    print("RESULT : %s (%d errors, %d warnings)" % (
        "PASS" if not rep["errors"] else "FAIL", len(rep["errors"]), len(rep["warnings"])))
    return not rep["errors"]


if __name__ == "__main__":
    import sys
    # Only acts when run as a CLI with a path; harmless when pasted into a sandbox.
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".olf"):
        sys.exit(0 if print_report(validate_olf(sys.argv[1])) else 1)

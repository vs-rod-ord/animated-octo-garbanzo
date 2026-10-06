"""olf_starter.py -- CORE helpers for building a myViewBoard .olf in a plain sandbox.

Standard library only. Paste this whole file into your code sandbox unchanged
(do not retype it), then call it. Ported from the reference engine
(olf-dsl/olf_dsl/core.py); the mechanical rules are baked in so you cannot forget
them: px font sizes, RTF colour sync, 8-digit text fill / 6-digit shape fill,
the triple separator, `additional` entries, curve stroke-opacity, and
wrapped-height text flow.

Typical use:

    doc = Doc("Lesson on X")
    p = doc.page()
    p.title("The Water Cycle")                 # flows from the top
    p.text("Body sentence ...", size=28)       # y advances by REAL wrapped height
    a = p.ellipse(400, 700, 120, fill="#BAE6FD")
    p.curve((520, 700), (700, 600), (900, 700), arrow_end=True)
    doc.save("out.olf")

Tables / images / animation / links live in olf_starter_extras.py (paste it AFTER
this file). Then run olf_validate.py on the saved file before delivering.
"""
import json
import textwrap
import uuid
import zipfile
from datetime import datetime

W, H = 1920, 1080
MATRIX = "1,0,0,0,1,0,0,0,1"
MARGIN, GUTTER = 80, 40
_MSEP = "\u300e\u300e\u300e"          # THREE U+300E chars. Never change.


def uid():
    return str(uuid.uuid4())


# ---- measurement strings (triple separator) --------------------------------
def _show_angle(n):
    return _MSEP.join(["true,"] * n)


def _show_length(n):
    return _MSEP.join(["false"] + ["true,False,"] * n)


POLY_LEN, POLY_ANG = _show_length(4), _show_angle(4)
LINE_LEN, ELLIPSE_LEN = _show_length(1), _show_length(2)


# ---- colour / font helpers --------------------------------------------------
def argb(c6):
    """'#RRGGBB' -> '#FFRRGGBB'. Text `fill` ONLY. Shapes stay 6-digit."""
    return "#FF" + c6.lstrip("#").upper()


def _rgb(c6):
    c = c6.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def json_font_size(pt):
    """JSON font-size is PIXELS = round(pt * 4/3). RTF keeps points (fs = pt*2)."""
    return float(round(pt * 4.0 / 3.0))


def _rtf_escape(v):
    """Escape for the RTF stream. Backslash and braces; non-ASCII as signed-16-bit
    \\uN? (what myViewBoard itself writes); and the literal word 'Arial', which
    myViewBoard silently rewrites to 'Calibri' in the decoded text, is broken with an
    invisible word-joiner (U+2060) so it displays correctly."""
    out = []
    for ch in v.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}"):
        o = ord(ch)
        if o < 128:
            out.append(ch)
        elif o <= 0xFFFF:
            out.append("\\u%d?" % (o - 0x10000 if o > 0x7FFF else o))
        else:                                   # astral: UTF-16 surrogate pair
            o -= 0x10000
            for s in (0xD800 + (o >> 10), 0xDC00 + (o & 0x3FF)):
                out.append("\\u%d?" % (s - 0x10000))
    return "".join(out).replace("Arial", "Ari\\u8288?al")


def make_rtf(value, pt, font="Segoe UI", align="left", bold=False, color="#000000"):
    r, g, b = _rgb(color)
    a = {"left": "\\ql", "center": "\\qc", "right": "\\qr", "justify": "\\qj"}.get(align, "\\ql")
    return (
        "{\\rtf1\\fbidis\\ansi\\ansicpg1252\\deff0\\nouicompat\\deflang1033"
        "{\\fonttbl{\\f0\\fnil\\fcharset0 " + font + ";}}\r\n"
        "{\\colortbl ;\\red%d\\green%d\\blue%d;}\r\n" % (r, g, b) +
        "{\\*\\generator Riched20 10.0.26100}\\viewkind4\\uc1 \r\n"
        "\\pard" + a + "\\tx720\\cf1" + ("\\b" if bold else "") +
        "\\f0\\fs" + str(int(pt * 2)) + " " + _rtf_escape(value) + "\\par\r\n}\r\n"
    )


# ---- text height estimate (no font metrics available -> be conservative) ----
# Wrapped-line pitch = (pitch ratio) x font size in POINTS. Measured on real renders at
# fs=44: Segoe UI 1.773, Calibri 1.614, Georgia 1.523, Open Sans 1.818, Times New
# Roman 1.477 (derived 1.533). The values below are those rounded UP. Bold is NOT
# different (same pitch as regular); only its glyphs are wider, handled in the line count.
PITCH = {"Segoe UI": 1.80, "Calibri": 1.65, "Georgia": 1.55, "Open Sans": 1.85,
         "Times New Roman": 1.55}
PITCH_DEFAULT = 1.85            # unknown / other families: generous


def pitch_ratio(font="Segoe UI"):
    return PITCH.get(font, PITCH_DEFAULT)


def estimate_lines(text, pt, width_px, bold=False):
    json_px = round(pt * 4 / 3)
    avg = json_px * (0.60 if bold else 0.55)    # deliberately generous; bold is wider
    per_line = max(1, int(width_px / avg))
    total = 0
    for para in str(text).split("\n"):
        total += max(1, len(textwrap.wrap(para, width=per_line, break_long_words=True)))
    return total


def estimate_height(text, pt, width_px, bold=False, font="Segoe UI"):
    """lines * pitch. NEVER use the pitch alone as a height."""
    return estimate_lines(text, pt, width_px, bold) * pt * pitch_ratio(font)


def badge_y(y_shape, shape_h, pt):
    """Textarea y that makes a SINGLE line of text look vertically centred inside a
    shape (calibrated against real renders). The textarea box is not the visual text
    box, so y = shape_centre - h/2 sits visibly too low/high; use this instead.
    Give the textarea the shape's full width and align='center'."""
    fs_c = max(20, min(64, pt))
    c = 0.40 + (fs_c - 20) / 44.0 * 0.16
    return y_shape + round(shape_h / 2 - c * pt)


# ---- elements ---------------------------------------------------------------
def textarea(x, y, w, h, text, pt, font="Segoe UI", bold=False, color="#1A1A2E",
             align="left"):
    fs = json_font_size(pt)
    ja = align if align in ("center", "right", "justify") else "left"
    return {"textarea": {
        "id": uid(), "x": float(x), "y": float(y), "width": float(w), "height": float(h),
        "custom-data": make_rtf(text, pt, font, align, bold, color),
        "custom-data-tag": "RTFxamlStr_UWP", "matrix": MATRIX,
        "text-blocks-container": [{"paragraph": {
            "id": uid(), "font-size": fs, "text-align": ja,
            "text-list-container": [{"text": {
                "id": uid(), "text": text, "font-family": font, "font-size": fs,
                "fill": argb(color), "font-style": "normal", "font-stretch": "normal",
                "font-weight": "bold" if bold else "normal",
                "text-decoration": "normal", "baseline-align": "baseline",
                "fill-opacity": 1.0}}]}}],
    }}


def _add(ref):
    return {"element": {"id": uid(), "ref": ref, "flip": "none", "is-locked": False,
                        "is-moveable-locked": False, "is-replicate": False}}


def polygon(points, fill="#FFFFFF", stroke=None, stroke_width=0.0):
    pid = uid()
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return {"polygon": {
        "id": pid, "x": 0.0, "y": 0.0,
        "width": float(max(xs) - min(xs)), "height": float(max(ys) - min(ys)),
        "matrix": MATRIX, "fill": fill, "stroke": stroke or fill,
        "stroke-width": float(stroke_width), "fill-opacity": 1.0,
        "stroke-opacity": 1.0 if stroke_width else 0.0,
        "is-show-incircle": False, "is-show-outcircle": False,
        "show-length-measurement": POLY_LEN, "show-angle-measurement": POLY_ANG,
        "points": " ".join("%s,%s" % (round(x, 3), round(y, 3)) for x, y in points),
    }}, _add(pid)


def rect(x, y, w, h, **kw):
    return polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], **kw)


def ellipse(cx, cy, rx, ry=None, fill="#FFFFFF", stroke="#000000", stroke_width=3.0):
    ry = rx if ry is None else ry
    eid, tx, ty, half = uid(), cx - rx, cy - ry, stroke_width / 2
    return {"ellipse": {
        "id": eid, "is-pie": False, "x": 0.0, "y": 0.0,
        "width": float(rx * 2 + stroke_width), "height": float(ry * 2 + stroke_width),
        "rx": float(rx), "ry": float(ry), "cx": float(rx), "cy": float(ry),
        "angle-start": 0.0, "angle-end": 359.9, "fill": fill, "stroke": stroke,
        "stroke-width": float(stroke_width), "fill-opacity": 1.0, "stroke-opacity": 1.0,
        "show-length-measurement": ELLIPSE_LEN, "show-angle-measurement": "",
        "matrix": "1,0,%s,0,1,%s,0,0,1" % (tx, ty),
        "boundary": "%s %s %s %s" % (tx - half, ty - half, tx + 2 * rx + half, ty + 2 * ry + half),
    }}, _add(eid)


def polyline(points, color="#CBD5E1", width=4.0, arrow_start=False, arrow_end=False,
             dashed=False):
    pid = uid()
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    el = {"polyline": {
        "id": pid, "x": 0.0, "y": 0.0,
        "width": float(max(max(xs) - min(xs), 1)), "height": float(max(max(ys) - min(ys), 1)),
        "stroke-opacity": 1.0, "stroke-width": float(width), "stroke": color,
        "lineshape-start": "arrow" if arrow_start else "normal",
        "lineshape-end": "arrow" if arrow_end else "normal",
        "stroke-linecap": "round", "matrix": MATRIX, "show-length-measurement": LINE_LEN,
        "points": " ".join("%s,%s" % (round(x, 3), round(y, 3)) for x, y in points),
    }}
    if dashed:
        el["polyline"]["stroke-dasharray"] = "18,12"
    return el, _add(pid)


def curve(p_start, p_via, p_end, color="#000000", width=6.0, arrow_start=False,
          arrow_end=False):
    """Points absolute. Stored relative to bbox origin offset by stroke/2.
    stroke-opacity MUST be explicit 1.0 or the curve is invisible."""
    cid, half = uid(), width / 2
    pts = [p_start, p_via, p_end]
    x0, y0 = min(p[0] for p in pts) - half, min(p[1] for p in pts) - half
    rel = [(p[0] - x0, p[1] - y0) for p in pts]
    f = lambda q: "%s,%s" % (round(q[0], 4), round(q[1], 4))
    return {"curve": {
        "id": cid, "x": float(x0), "y": float(y0),
        "width": float(max(p[0] for p in pts) - min(p[0] for p in pts) + width),
        "height": float(max(p[1] for p in pts) - min(p[1] for p in pts) + width),
        "stroke-width": float(width), "stroke-opacity": 1.0,
        "stroke-linecap-start": "arrow" if arrow_start else "round",
        "stroke-linecap-end": "arrow" if arrow_end else "round",
        "start-point": f(rel[0]), "second-point": f(rel[1]), "end-point": f(rel[2]),
        "stroke": color, "matrix": MATRIX,
    }}, _add(cid)


# ---- page / document --------------------------------------------------------
class Page:
    """Collects elements; `y` is the auto-flow cursor for title()/text()."""

    def __init__(self, doc, bg="#FFFFFF"):
        self.doc, self.bg, self.elements, self.y = doc, bg, [], MARGIN

    def add(self, built):
        """Accepts an element, or (element, additional_entry). Returns element id."""
        el, add = built if isinstance(built, tuple) else (built, None)
        self.elements.append(el)
        if add is not None:
            self.doc.additional.append(add)
        return next(iter(el.values()))["id"]

    # flowing text: height = lines * pitch; next y = y + height + GUTTER
    def text(self, text, size=28, x=MARGIN, width=W - 2 * MARGIN, bold=False,
             color="#1A1A2E", align="left", y=None, gap=GUTTER, font="Segoe UI"):
        top = self.y if y is None else y
        h = estimate_height(text, size, width, bold=bold, font=font)
        tid = self.add(textarea(x, top, width, h, text, size, font=font, bold=bold,
                                color=color, align=align))
        if y is None:
            self.y = top + h + gap
        return tid

    def title(self, text, size=44, **kw):
        kw.setdefault("bold", True)
        return self.text(text, size=size, **kw)

    def bullets(self, items, size=28, x=MARGIN, width=W - 2 * MARGIN - 60, marker="\u2022"):
        """Simple flowing list: one textarea per item, text prefixed with a marker.
        (The engine's compound bullets element is richer; see elements/bullets.md.)"""
        return [self.text("%s  %s" % (marker, it), size=size, x=x, width=width, gap=20)
                for it in items]

    def rect(self, *a, **k): return self.add(rect(*a, **k))
    def ellipse(self, *a, **k): return self.add(ellipse(*a, **k))
    def polyline(self, *a, **k): return self.add(polyline(*a, **k))
    def curve(self, *a, **k): return self.add(curve(*a, **k))


class Doc:
    def __init__(self, description="Generated OLF"):
        self.description, self.pages, self.additional = description, [], []
        self.links, self.extra_files = [], {}

    def page(self, bg="#FFFFFF"):
        p = Page(self, bg)
        self.pages.append(p)
        return p

    def content(self):
        now = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p").lstrip("0").replace("/0", "/")
        pageset = [{"page": {
            "id": uid(), "matrix": MATRIX, "viewbox": "0,0,1920,1080",   # commas
            "is-hidden": False, "elements": p.elements,
            "backgrounds": [{"background": {"id": uid(), "type": "color",
                                            "fill": p.bg, "opacity": 1.0}}],
        }} for p in self.pages]
        return {"olf": {
            "width": 1920.0, "height": 1080.0, "viewbox": "0 0 1920 1080",   # spaces
            "meta": {
                "id": uid(), "create-platform": "myViewBoard for Windows",
                "create-by-library": "Viewsonic Open Learning Format library",
                "create-time": now, "modify-time": now,
                "create-library-version": "0.0.1.50",
                "create-version": "3.4.9.603 [64 bits]",
                "modify-version": "3.4.9.603 [64 bits]",
                "modify-platform": "myViewBoard for Windows",
                "description": self.description},
            "pageset": pageset, "additional": self.additional,
            "links": self.links, "groups": [],
        }}

    def save(self, path):
        """content.json must sit at the ZIP ROOT. ensure_ascii=False keeps U+300E raw."""
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("content.json", json.dumps(self.content(), ensure_ascii=False))
            for arc, data in self.extra_files.items():
                zf.writestr(arc, data)
        return path

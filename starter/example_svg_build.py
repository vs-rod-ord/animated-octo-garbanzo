"""example_svg_build.py -- worked SVG example (vector icons + rounded card + SVG image).

Prerequisite: olf_starter.py, olf_starter_svg.py and olf_validate.py already
executed in the same session (paste them first, in that order).
Page 1: three AI-pen icons from raw path data (true vector, resizable), a rounded
        card behind a caption, and a hand-written icon built from independent
        solid subpaths (safe).
Page 2: an SVG `image` element (gradient + clipPath -- both confirmed to render),
        authored 8x oversize automatically.
"""
doc = Doc("SVG demo")

# ---- page 1: AI-pen vector shapes ------------------------------------------
p1 = doc.page()
p1.title("Vector icons (AI-pen)", size=44)
y0 = 260
p1.add(ai_pen_rounded_rect(MARGIN, y0 - 40, 1760, 360, 40, "#E0F2FE"))       # card first = behind
HOME = "M10 20v-6h4v6h5v-8h3L12 3L2 12h3v8z"                                  # mdi:home, 24x24
STAR = "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2L9.19 8.63L2 9.24l5.46 4.73L5.82 21z"
ARROW = "M4 11v2h12l-5.5 5.5l1.42 1.42L19.84 12l-7.92-7.92L10.5 5.5L16 11z"   # independent solid
for i, (d, col, label) in enumerate([(HOME, "#1565C0", "Home"), (STAR, "#F59E0B", "Star"),
                                     (ARROW, "#16A34A", "Arrow")]):
    cx = 360 + i * 600
    p1.add(ai_pen_icon([d], x=cx - 100, y=y0, size=200, vb=24, fill=col))
    h = estimate_height(label, 26, 300)
    p1.add(textarea(cx - 150, y0 + 215, 300, h, label, 26, bold=True, align="center"))
p1.y = y0 + 380
p1.text("Icons are real vector paths: drag a corner in myViewBoard and they stay sharp.",
        size=28, color="#475569")

# ---- page 2: SVG image element (rasterised; authored 8x) --------------------
p2 = doc.page()
p2.title("SVG image element", size=44)
SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 260">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#38BDF8"/><stop offset="1" stop-color="#6366F1"/>
    </linearGradient>
    <clipPath id="c"><circle cx="200" cy="130" r="110"/></clipPath>
  </defs>
  <style>.ring{fill:none;stroke:#0F172A;stroke-width:6}</style>
  <rect width="400" height="260" rx="24" fill="#F8FAFC"/>
  <rect width="400" height="260" fill="url(#g)" clip-path="url(#c)"/>
  <circle class="ring" cx="200" cy="130" r="110"/>
</svg>"""
add_svg_image(p2, doc, "badge", SVG, x=560, y=260, w=800, h=520)

doc.save("svg_example.olf")
print_report(validate_olf("svg_example.olf"))

"""example_build.py -- complete worked example using the starter helpers.

Prerequisite: olf_starter.py, olf_starter_extras.py and olf_validate.py have
already been executed in the same Python session (paste them first, in that order).
Produces a 3-page file: (1) title + numbered list, (2) cycle diagram with
ellipses, labels and arrowed curves, (3) table. Then validates it.
"""
doc = Doc("The Water Cycle")

# ---- page 1: title + numbered list (wrapping text flows correctly) ----------
p1 = doc.page()
title_id = p1.title("The Water Cycle", size=54)
p1.text("Water moves continuously between the oceans, the air and the land.", size=30,
        color="#475569")
steps = [
    "Evaporation: heat from the sun warms oceans, lakes, and rivers, turning liquid water "
    "into invisible water vapor that rises into the air.",
    "Condensation: as vapor rises it cools and condenses into tiny droplets that gather to form clouds.",
    "Precipitation: when droplets grow heavy they fall as rain, snow, sleet or hail.",
    "Collection: water runs off or soaks into the ground and collects in oceans, lakes and rivers.",
]
step_ids = [p1.text("%d.  %s" % (i + 1, s), size=28, gap=24) for i, s in enumerate(steps)]
link_page(doc, title_id, 2)                    # click the title -> page 2
for sid in step_ids:                           # tap-to-reveal each step
    animate(doc, sid, "fade-in", "2")

# ---- page 2: cycle diagram ---------------------------------------------------
p2 = doc.page(bg="#F0F9FF")
p2.title("How the cycle flows", size=44)
RX, RY = 190, 80
nodes = [("Evaporation", 400, 580, "#FDE68A"), ("Condensation", 960, 260, "#E2E8F0"),
         ("Precipitation", 1520, 580, "#BAE6FD"), ("Collection", 960, 780, "#BBF7D0")]   # all above y=880
for label, cx, cy, fill in nodes:
    p2.ellipse(cx, cy, RX, RY, fill=fill, stroke="#334155", stroke_width=3.0)
    lh = estimate_height(label, 26, 2 * RX - 40, bold=True)
    p2.add(textarea(cx - RX + 20, badge_y(cy - RY, 2 * RY, 26), 2 * RX - 40, lh, label, 26,
                    bold=True, color="#0F172A", align="center"))
arrows = [((300, 505), (520, 360), (800, 280)),      # Evaporation -> Condensation
          ((1120, 280), (1400, 360), (1560, 500)),   # Condensation -> Precipitation
          ((1440, 650), (1300, 760), (1150, 780)),   # Precipitation -> Collection
          ((770, 780), (520, 760), (380, 665))]      # Collection -> Evaporation
for a, via, b in arrows:
    p2.curve(a, via, b, color="#0369A1", width=6.0, arrow_end=True)

# ---- page 3: summary table ---------------------------------------------------
p3 = doc.page()
p3.title("Summary", size=44)
t = add_table(p3, x=MARGIN, y=p3.y,
              col_lengths=[420, 1300], row_lengths=[80, 110, 110, 110, 110], size=24,
              cells=[["Stage", "What happens"],
                     ["Evaporation", "Sun-warmed liquid water becomes water vapor and rises."],
                     ["Condensation", "Cooling vapor turns into droplets that form clouds."],
                     ["Precipitation", "Heavy droplets fall as rain, snow, sleet or hail."],
                     ["Collection", "Water gathers in oceans, lakes, rivers and groundwater."]])

doc.save("water_cycle_example.olf")
rep = validate_olf("water_cycle_example.olf")
print_report(rep)

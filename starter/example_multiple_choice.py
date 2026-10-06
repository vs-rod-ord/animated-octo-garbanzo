"""example_multiple_choice.py -- the 'multiple choice' page template, 3 pages.

Prerequisite: olf_starter.py and olf_validate.py already executed (paste first).
Layout (reverse-engineered from a real proven file): title top-left, horizontal accent
divider, vertical divider splitting a question column (left) from a decorative panel
(right), bold question, lettered options stacked below, pale per-page background.
No correct answer is marked on the canvas -- reveal is spoken/live.
"""
TITLE_H = 96
LEFT_X, LEFT_W = 80, 830            # question column
DIV_Y = 168                         # horizontal divider top


def mc_page(doc, question, options, accent, bg, graphic, answer_key=None):
    p = doc.page(bg=bg)
    p.add(textarea(80, 40, 1400, TITLE_H, "Multiple Choice", 64, bold=True, color=accent))
    p.add(rect(80, DIV_Y, 1760, 4, fill=accent))                    # horizontal divider
    p.add(rect(968, 220, 4, 640, fill=accent))                      # vertical divider (ends above y=880)
    p.y = 220
    p.text(question, size=36, x=LEFT_X, width=LEFT_W, bold=True, color="#1E293B", gap=36)
    for i, opt in enumerate(options):
        p.text("%s.  %s" % ("ABCD"[i], opt), size=30, x=LEFT_X, width=LEFT_W,
               color="#334155", gap=24)
    graphic(p, accent)                                              # right panel 1060..1840
    if answer_key:                                                  # optional, OFF-canvas (y=1200)
        p.add(textarea(80, 1200, 1400, 60, "Answer: " + answer_key, 28, bold=True, color="#B91C1C"))
    return p


def nested_ellipses(p, accent):             # "nucleus"-style diagram
    p.ellipse(1450, 540, 330, 300, fill="#E0E7FF", stroke=accent, stroke_width=6)
    p.ellipse(1450, 540, 140, 130, fill="#A5B4FC", stroke=accent, stroke_width=6)


def triangle_stack(p, accent):              # "mountain/volcano"-style diagram
    p.add(polygon([(1100, 840), (1450, 260), (1800, 840)], fill="#FDBA74",
                  stroke=accent, stroke_width=6))
    p.add(polygon([(1330, 450), (1450, 260), (1570, 450)], fill="#FCA5A5",
                  stroke=accent, stroke_width=6))


def ring(p, accent):                        # "membrane"-style diagram (hollow ring)
    p.ellipse(1450, 540, 300, 300, fill="#DCFCE7", stroke=accent, stroke_width=24)


doc = Doc("Multiple choice demo")
mc_page(doc, "Which structure is known as the control centre of the cell?",
        ["Mitochondrion", "Nucleus", "Cell membrane", "Chloroplast"],
        accent="#4F46E5", bg="#EEF2FF", graphic=nested_ellipses)
mc_page(doc, "What is molten rock called while it is still beneath the Earth's surface?",
        ["Lava", "Magma", "Sediment", "Obsidian"],
        accent="#C2410C", bg="#FFF7ED", graphic=triangle_stack)
mc_page(doc, "Which part of the cell controls what enters and leaves it?",
        ["Cell wall", "Cytoplasm", "Cell membrane", "Vacuole"],
        accent="#15803D", bg="#F0FDF4", graphic=ring)

doc.save("multiple_choice_example.olf")
print_report(validate_olf("multiple_choice_example.olf"))

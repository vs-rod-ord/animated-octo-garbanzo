"""example_toc.py -- clickable table of contents / menu + back links (page links).

Prerequisite: olf_starter.py, olf_starter_extras.py, olf_starter_svg.py and
olf_validate.py already executed (paste in that order).
Page 1 is the menu: one rounded button per section. Each button is linked to its
section page. Every section page has a BACK TO MENU text link.
Rules baked in: page-id is the 1-BASED ORDINAL STRING of the target page (never its
UUID); put the link on the button SHAPE, not also on its label (the app prunes the
label's link when both overlap); labels sit on top as plain unlinked textareas.
"""
sections = [("Hadean", "4.6 - 4.0 billion years ago", "#FCA5A5"),
            ("Archean", "4.0 - 2.5 billion years ago", "#FDBA74"),
            ("Proterozoic", "2.5 billion - 538 million years ago", "#FDE68A")]

doc = Doc("Menu demo")
menu = doc.page(bg="#F8FAFC")
menu.title("Earth's Eons", size=54)
menu.text("Tap an eon to jump to its page.", size=28, color="#475569")

button_ids = []
y = menu.y + 20
for label, _, colour in sections:
    h = 130
    bid = menu.add(ai_pen_rounded_rect(MARGIN, y, 1000, h, 40, colour))     # the link target
    menu.add(textarea(MARGIN + 40, badge_y(y, h, 36), 920,
                      estimate_height(label, 36, 920, bold=True), label, 36, bold=True))
    button_ids.append(bid)
    y += h + 30

for i, (label, dates, colour) in enumerate(sections):
    pg = doc.page(bg="#FFFFFF")
    pg.title(label, size=54)
    pg.text(dates, size=32, color="#475569")
    back = pg.text("BACK TO MENU", size=28, bold=True, color="#1D4ED8", y=950)   # bare textarea link
    link_page(doc, back, 1)                      # page 1 = the menu
    link_page(doc, button_ids[i], i + 2)         # menu button i -> page i+2 (1-based ordinal)

doc.save("toc_example.olf")
print_report(validate_olf("toc_example.olf"))

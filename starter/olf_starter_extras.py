"""olf_starter_extras.py -- tables, images, animation, links.

Paste AFTER olf_starter.py (it uses uid, MATRIX, _add, textarea, estimate_height,
Page, Doc from there). Standard library only. Ported from olf-dsl core.py.

    t = add_table(p, x=80, y=p.y, col_lengths=[400, 800], row_lengths=[70, 70, 70],
                  cells=[["Stage", "What happens"], ["Evaporation", "Water -> vapor"],
                         ["Condensation", "Vapor -> clouds"]])
    p.y = t["bottom"] + GUTTER
    animate(doc, some_element_id, "fade-in", "2")
    link_page(doc, some_element_id, 3)         # jumps to page 3 (1-based)
"""

TABLE_PAD = 18.0                 # cell text inset from the cell interior, both axes
CELL_BG, CELL_BG_OPACITY = "#FFFFFF", 0.2


def _table_shell(x, y, col_lengths, row_lengths, stroke="#000000", sw=3.0):
    tid, cols, rows = uid(), len(col_lengths), len(row_lengths)
    bgs = [{"cell-background": {"id": uid(), "background": CELL_BG,
                                "background-opacity": CELL_BG_OPACITY,
                                "cell-column": c, "cell-row": r}}   # DENSE, column-major
           for c in range(cols) for r in range(rows)]
    return {"table": {
        "id": tid, "x": float(x), "y": float(y),
        "width": float(sum(col_lengths) + (cols + 1) * sw),
        "height": float(sum(row_lengths) + (rows + 1) * sw),
        "rows": rows, "columns": cols, "matrix": MATRIX,
        "stroke": stroke, "stroke-width": float(sw), "stroke-opacity": 1.0,
        "column-lengths-array": " ".join(str(v) for v in col_lengths),
        "row-lengths-array": " ".join(str(v) for v in row_lengths),
        "column-min-lengths-array": " ".join(["1"] * cols),
        "row-min-lengths-array": " ".join(["1"] * rows),
        "cell-background-container": bgs,
        "merge-cell-container": [], "cell-content-container": [],
    }}, _add(tid)


def _merge_entries(rows, cols, merges):
    """merges = [(row, col, row_span, col_span)] in plain 0-based CELL counts.
    One entry per cell, COLUMN-major; EVEN index space; extent = 2k-1."""
    anchors, swallowed = {}, {}
    for r, c, kr, kc in merges:
        anchors[(r, c)] = (2 * kr - 1, 2 * kc - 1)
        for dr in range(kr):
            for dc in range(kc):
                if (dr, dc) != (0, 0):
                    swallowed[(r + dr, c + dc)] = (r, c)
    out = []
    for c in range(cols):
        for r in range(rows):
            if (r, c) in anchors:
                out.append(("%d,%d" % (2 * r, 2 * c),) + anchors[(r, c)])
            elif (r, c) in swallowed:
                ar, ac = swallowed[(r, c)]
                out.append(("%d,%d" % (2 * ar, 2 * ac), 1, 1))
            else:
                out.append(("-1,-1", 1, 1))
    return out, swallowed


def add_table(page, x, y, col_lengths, row_lengths, cells, size=22, header=True,
              merges=(), sw=3.0):
    """cells[r][c] = text or None. Creates the table AND one textarea per cell,
    registers cell-content in the EVEN index space. Returns {'id','bottom'}.
    Cell width for wrap estimation = column length - 2*TABLE_PAD."""
    shell, add = _table_shell(x, y, col_lengths, row_lengths, sw=sw)
    t = shell["table"]
    rows, cols = len(row_lengths), len(col_lengths)
    if merges:
        entries, swallowed = _merge_entries(rows, cols, merges)
        t["merge-cell-container"] = [{"merge-cell": {
            "id": uid(), "start-from": sf, "merge-cell-rows": mr, "merge-cell-columns": mc}}
            for sf, mr, mc in entries]
    else:
        swallowed = {}
    page.add((shell, add))
    for r in range(rows):
        for c in range(cols):
            txt = cells[r][c] if r < len(cells) and c < len(cells[r]) else None
            if not txt:
                continue
            ix = x + sw + sum(v + sw for v in col_lengths[:c]) + TABLE_PAD
            iy = y + sw + sum(v + sw for v in row_lengths[:r]) + TABLE_PAD
            w = col_lengths[c] - 2 * TABLE_PAD
            h = estimate_height(txt, size, w)
            bold = header and r == 0
            ta = textarea(ix, iy, w, h, txt, size, bold=bold)
            page.elements.append(ta)
            rr, cc = swallowed.get((r, c), (r, c))
            t["cell-content-container"].append({"cell-content": {
                "id": uid(), "cell-row": 2 * rr, "cell-column": 2 * cc,
                "ref": ta["textarea"]["id"]}})
            # Row too short for wrapped text? Warn -- enlarge row_lengths instead.
            if h + 2 * TABLE_PAD > row_lengths[r] and (r, c) not in swallowed:
                print("WARNING: cell (%d,%d) needs ~%d tall, row is %s -- raise row_lengths"
                      % (r, c, h + 2 * TABLE_PAD, row_lengths[r]))
    return {"id": t["id"], "bottom": y + t["height"]}


def add_image(page, doc, arcname, data, mime, x, y, w, h):
    """arcname like 'images/pic.png'; data = bytes. Image elements need NO additional entry."""
    doc.extra_files[arcname] = data
    return page.add({"image": {"id": uid(), "x": float(x), "y": float(y),
                               "width": float(w), "height": float(h),
                               "mime-type": mime, "source": arcname, "matrix": MATRIX}})


def animate(doc, ref_id, anim_type="fade-in", duration="2"):
    """Attach to an element's `additional` entry. anim_type fade-in|fade-out;
    duration is a STRING '0'..'3'. Both types on one element = tap toggles it."""
    for a in doc.additional:
        if a["element"]["ref"] == ref_id:
            a["element"].setdefault("animation-container", []).append(
                {"animation": {"id": uid(), "type": anim_type, "duration": str(duration)}})
            return
    # image/textarea elements have no entry yet: create one WITHOUT flip is wrong for
    # shapes, but these types have none, so build the minimal entry.
    doc.additional.append({"element": {
        "id": uid(), "ref": ref_id, "is-locked": False, "is-moveable-locked": False,
        "is-replicate": False,
        "animation-container": [{"animation": {"id": uid(), "type": anim_type,
                                               "duration": str(duration)}}]}})


def _link(doc, ref_id, link_type, payload):
    entry = {"id": uid(), "ref": ref_id, "link-type": link_type}
    entry.update(payload)
    doc.links.append({"link": entry})


def link_page(doc, ref_id, page_number):
    """page-id is the 1-BASED ORDINAL as a STRING, never a page UUID."""
    _link(doc, ref_id, "page", {"page-id": str(int(page_number))})


def link_web(doc, ref_id, url):
    _link(doc, ref_id, "web", {"url": url})

# -*- coding: utf-8 -*-
"""Render one front page for Tuesday 24 November 2026.

Drawn at 2048x2048 and Lanczos-downsampled to 1024x1024, so every
measurement below is in final-page pixels and multiplied by SUPERSAMPLE
on the way to the canvas.

Two passes: the whole page is measured and packed first, then painted.
Each band is asserted to sit inside its own vertical slot, so no block
can print over its neighbour and the page cannot overrun.

Deterministic: no randomness, no clock, no set iteration.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import record as R  # noqa: E402

# ---------------------------------------------------------------- palette
PAPER = (245, 242, 234)
INK = (17, 15, 13)
BODY = (50, 45, 39)
GREY = (102, 95, 86)
LIGHT = (180, 172, 160)
RED = (150, 32, 26)
BLUE = (30, 60, 98)

FONTS = "/usr/share/fonts/truetype/liberation/"
PATHS = {
    "serif_b": FONTS + "LiberationSerif-Bold.ttf",
    "serif": FONTS + "LiberationSerif-Regular.ttf",
    "sans_b": FONTS + "LiberationSans-Bold.ttf",
    "sans": FONTS + "LiberationSans-Regular.ttf",
}

S = 2                      # supersample factor
PAGE = 1024
CANVAS = PAGE * S

M = 40                     # left/right margin
CW = PAGE - 2 * M          # 944
TOP = 20
BOTPAD = 12

# ------------------------------------------------------------ text engine
_canvas = Image.new("RGB", (CANVAS, CANVAS), PAPER)
draw = ImageDraw.Draw(_canvas)
_fcache = {}
BOXES = []


def fnt(kind, size):
    key = (kind, round(size, 2))
    if key not in _fcache:
        _fcache[key] = ImageFont.truetype(PATHS[kind], max(6, int(round(size * S))))
    return _fcache[key]


def tw(s, kind, size):
    return draw.textlength(s, font=fnt(kind, size)) / S


def text(x, y, s, kind, size, colour, track=0.0, tag="body"):
    if not s:
        return 0.0
    f = fnt(kind, size)
    if track:
        cx = x
        for ch in s:
            draw.text((cx * S, y * S), ch, font=f, fill=colour)
            cx += draw.textlength(ch, font=f) / S + track
        w = cx - x - track
    else:
        draw.text((x * S, y * S), s, font=f, fill=colour)
        w = draw.textlength(s, font=f) / S
    BOXES.append((x, y, x + w, y + size * 1.16, tag))
    return w


def tw_track(s, kind, size, track):
    return sum(tw(ch, kind, size) for ch in s) + track * (len(s) - 1)


def fitted(s, kind, size, maxw, floor=6.0, step=0.25):
    while size > floor and tw(s, kind, size) > maxw:
        size -= step
    return size


def wrap(s, kind, size, maxw, maxlines=None):
    """Greedy wrap with hyphen-splitting of overlong tokens."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if tw(trial, kind, size) <= maxw:
            cur = trial
            continue
        if cur:
            lines.append(cur)
            cur = w
        while tw(cur, kind, size) > maxw and len(cur) > 1:
            lo, hi = 1, len(cur)
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if tw(cur[:mid] + "-", kind, size) <= maxw:
                    lo = mid
                else:
                    hi = mid - 1
            lines.append(cur[:lo] + "-")
            cur = cur[lo:]
    if cur:
        lines.append(cur)
    if maxlines is None or len(lines) <= maxlines:
        return lines, False
    kept = lines[:maxlines]
    tail = kept[-1]
    while tail and tw(tail + "...", kind, size) > maxw:
        tail = tail.rsplit(" ", 1)[0] if " " in tail else tail[:-1]
    kept[-1] = (tail + "...") if tail else "..."
    return kept, True


def rule(y, colour=LIGHT, th=1.0, x0=None, x1=None):
    x0 = M if x0 is None else x0
    x1 = PAGE - M if x1 is None else x1
    draw.rectangle([x0 * S, y * S, x1 * S - 1, (y + max(th, 1.0 / S)) * S - 1],
                   fill=colour)
    BOXES.append((x0, y, x1, y + th, "rule"))


def vrule(x, y0, y1, colour=LIGHT):
    draw.rectangle([x * S, y0 * S, x * S + S - 1, y1 * S], fill=colour)


# --------------------------------------------------------------- masthead
MAST_NAME = "THE WORLD IN ONE DAY"
MAST_RED = "TUESDAY - ONE DAY OF WORLD NEWS, EVERY REGION"


def measure_masthead():
    nsize, ntrack = 12.5, 4.6
    nw = tw_track(MAST_NAME, "sans_b", nsize, ntrack)
    dsize = fitted(R.DAY_SHORT, "serif_b", 62.0, CW - 10, floor=20)
    dw = tw(R.DAY_SHORT, "serif_b", dsize)
    rsize, rtrack = 8.8, 1.7
    rw = tw_track(MAST_RED, "sans_b", rsize, rtrack)
    h = 1 + 6 + nsize * 1.2 + 1 + dsize * 1.02 + 3 + rsize * 1.3 + 5 + 3 + 1 + 9
    return dict(h=h, nsize=nsize, ntrack=ntrack, nw=nw, dsize=dsize, dw=dw,
                rsize=rsize, rtrack=rtrack, rw=rw)


def paint_masthead(m, top):
    y = top
    rule(y, INK, 1.2)
    y += 1 + 6
    text((PAGE - m["nw"]) / 2.0, y, MAST_NAME, "sans_b", m["nsize"], INK,
         track=m["ntrack"], tag="mast")
    y += m["nsize"] * 1.2 + 1
    text((PAGE - m["dw"]) / 2.0, y, R.DAY_SHORT, "serif_b", m["dsize"], INK,
         tag="mast")
    y += m["dsize"] * 1.02 + 3
    text((PAGE - m["rw"]) / 2.0, y, MAST_RED, "sans_b", m["rsize"], RED,
         track=m["rtrack"], tag="mast")
    y += m["rsize"] * 1.3 + 5
    rule(y, INK, 2.2)
    rule(y + 3.4, LIGHT, 1.0)
    return top + m["h"]


# ---------------------------------------------------------------- figures
def measure_figures():
    cellw = CW / 6.0
    cells = []
    for num, lab in R.FIGURES:
        nsz = fitted(num, "serif_b", 30.0, cellw - 16, floor=12)
        ll, _ = wrap(lab, "sans", 7.9, cellw - 14, maxlines=2)
        cells.append((num, nsz, ll))
    num_h = max(c[1] * 1.06 for c in cells)
    lab_h = max(len(c[2]) * 9.5 for c in cells)
    return dict(h=6 + num_h + 2 + lab_h + 8, cells=cells, cellw=cellw, num_h=num_h)


def paint_figures(fg, top):
    y = top + 6
    for i, (num, nsz, ll) in enumerate(fg["cells"]):
        cx = M + i * fg["cellw"]
        nw = tw(num, "serif_b", nsz)
        text(cx + (fg["cellw"] - nw) / 2.0, y, num, "serif_b", nsz, INK, tag="fig")
        ly = y + fg["num_h"] + 2
        for ln in ll:
            lw = tw(ln, "sans", 7.9)
            text(cx + (fg["cellw"] - lw) / 2.0, ly, ln, "sans", 7.9, GREY, tag="fig")
            ly += 9.5
        if i:
            vrule(cx - 1, top + 5, top + fg["h"] - 6)
    rule(top + fg["h"], LIGHT, 1.0)
    return top + fg["h"] + 1


# ------------------------------------------------------------- lead zone
LEAD_HEAD = 38.0
LEAD_LEAD = 40.5
LEAD_BODY = 12.8
LEAD_BODY_LEAD = 14.8
SUB_HEAD = 18.0
SUB_LEAD = 20.2
SUB_BODY = 10.4
SUB_BODY_LEAD = 12.2


def measure_lead(lead, subs):
    llines, _ = wrap(lead["head"], "serif_b", LEAD_HEAD, CW, maxlines=2)
    lb, _ = wrap(lead["body"], "serif", LEAD_BODY, CW, maxlines=2)
    lmeta = lead["area"] + "    " + lead["place"] + "    " + lead["topic"].upper()

    subw = (CW - 28) / 2.0
    spec = []
    for s in subs:
        hl, _ = wrap(s["head"], "serif_b", SUB_HEAD, subw, maxlines=2)
        bl, _ = wrap(s["body"], "serif", SUB_BODY, subw, maxlines=2)
        spec.append(dict(s=s, hl=hl, bl=bl, m=s["area"] + "   " + s["place"]))
    sh = max(len(x["hl"]) * SUB_LEAD + 2 + 10 + len(x["bl"]) * SUB_BODY_LEAD
             + 2 + 8 for x in spec)
    h = (len(llines) * LEAD_LEAD + 3 + 11 + len(lb) * LEAD_BODY_LEAD + 2 + 9
         + 7 + 1 + 7 + sh)
    return dict(h=h, llines=llines, lb=lb, lmeta=lmeta, spec=spec, subw=subw, sh=sh)


def paint_lead(L, top):
    lead = R.STORIES[0]
    y = top
    for ln in L["llines"]:
        text(M, y, ln, "serif_b", LEAD_HEAD, INK, tag="lead")
        y += LEAD_LEAD
    y += 3
    text(M, y, L["lmeta"], "sans_b", 9.4, RED, track=1.1, tag="lead")
    y += 11
    for ln in L["lb"]:
        text(M, y, ln, "serif", LEAD_BODY, BODY, tag="lead")
        y += LEAD_BODY_LEAD
    y += 2
    text(M, y, lead["src"], "sans", 8.2, GREY, tag="lead")
    y += 9
    rule(y, LIGHT, 1.0)
    y += 7
    sub_top = y
    for i, sp in enumerate(L["spec"]):
        x = M + i * (L["subw"] + 28)
        yy = sub_top
        for ln in sp["hl"]:
            text(x, yy, ln, "serif_b", SUB_HEAD, INK, tag="sub")
            yy += SUB_LEAD
        yy += 2
        text(x, yy, sp["m"], "sans_b", 8.2, RED, track=0.7, tag="sub")
        yy += 10
        for ln in sp["bl"]:
            text(x, yy, ln, "serif", SUB_BODY, BODY, tag="sub")
            yy += SUB_BODY_LEAD
        yy += 2
        text(x, yy, sp["s"]["src"], "sans", 7.6, GREY, tag="sub")
        if i == 0:
            vrule(M + L["subw"] + 13, sub_top, sub_top + L["sh"] - 4)
    return sub_top + L["sh"]


# ------------------------------------------------------------------ cards
CARD_SCALES = [
    (21.0, 23.0, 11.8, 14.4),
    (20.0, 22.0, 11.4, 13.9),
    (19.0, 21.0, 11.0, 13.5),
    (18.0, 20.0, 10.6, 13.0),
    (17.0, 18.9, 10.2, 12.5),
    (16.0, 17.8, 9.8, 12.0),
    (15.0, 16.7, 9.4, 11.6),
    (14.0, 15.6, 9.0, 11.1),
]

COLGUT = 23
COLW = (CW - 2 * COLGUT) / 3.0
GAP = 8.5

KICK_H = 9.5
HEAD_GAP = 1.5
BODY_GAP = 2.5
SRC_H = 9.0


def card_h(card, scale):
    return (KICK_H + len(card["hl"]) * scale[1] + HEAD_GAP
            + len(card["bl"]) * scale[3] + BODY_GAP + SRC_H)


def build_cards(stories, scale):
    hsz, hlead, bsz, blead = scale
    out = []
    for s in stories:
        hl, _ = wrap(s["head"], "serif_b", hsz, COLW, maxlines=3)
        bl, _ = wrap(s["body"], "serif", bsz, COLW, maxlines=2)
        c = dict(s=s, hl=hl, bl=bl)
        c["h"] = card_h(c, scale)
        out.append(c)
    return out


def pack(cards, top, bottom, gap=GAP, cols=3):
    """One card per area first; then greedy fill of the shortest column."""
    collist = [[] for _ in range(cols)]
    y = [top] * cols
    used = []

    def put(card):
        for i in sorted(range(cols), key=lambda k: (y[k], k)):
            need = card["h"] + (gap if collist[i] else 0)
            if y[i] + need <= bottom:
                collist[i].append(card)
                y[i] += need
                used.append(card)
                return True
        return False

    pool = list(cards)
    for area in R.AREAS:
        for c in pool:
            if c["s"]["area"] == area:
                put(c)
                pool.remove(c)
                break
    # Fill by proportional coverage: each area competes on
    # (cards placed / cards it has), so a region with only four stories in
    # the record is not crowded out by a region with ten. Ties fall back to
    # tier, then to record order, so the result is stable.
    avail = {}
    for c in cards:
        avail[c["s"]["area"]] = avail.get(c["s"]["area"], 0) + 1
    while pool:
        counts = {}
        for col in collist:
            for c in col:
                counts[c["s"]["area"]] = counts.get(c["s"]["area"], 0) + 1
        ahead = sorted(
            enumerate(pool),
            key=lambda p: (counts.get(p[1]["s"]["area"], 0)
                           / float(avail[p[1]["s"]["area"]]),
                           p[1]["s"]["tier"], p[0]),
        )
        placed_any = False
        for _, c in ahead:
            if put(c):
                pool.remove(c)
                placed_any = True
                break
        if not placed_any:
            break
    return collist, y, used, pool


# ------------------------------------------------------------------- main
BRIEF_ROW_H = 11.8
BRIEF_HEAD_H = 11.0
BRIEF_FS = 9.6
INDEX_H = 12.0


def main():
    stories = R.STORIES
    lead = stories[0]
    subs = stories[1:3]

    mast = measure_masthead()
    fig = measure_figures()
    L = measure_lead(lead, subs)

    fig_top = TOP + mast["h"] + 9
    fig_bot = fig_top + fig["h"] + 1
    lead_top = fig_bot + 10
    lead_bot = lead_top + L["h"]
    grid_top = lead_bot + 12

    footer_h = 24
    footer_top = PAGE - BOTPAD - footer_h

    grid_pool = stories[3:]
    order = ([s for s in grid_pool if s["tier"] == 2]
             + [s for s in grid_pool if s["tier"] == 3])

    # Joint search over brief rows x card scale. The grid is the readable,
    # detailed part of the page, so it is weighted well above the one-line
    # brief: prefer cards, then total stories, then a tighter brief.
    best = None
    for rows in range(5, 13):
        brief_h = BRIEF_HEAD_H + 2 + rows * BRIEF_ROW_H + 5
        brief_top = footer_top - 9 - brief_h
        grid_bottom = brief_top - INDEX_H - 4
        if grid_bottom - grid_top < 90:
            continue
        for scale in CARD_SCALES:
            cards = build_cards(order, scale)
            collist, coly, used, leftover = pack(cards, grid_top, grid_bottom)
            nbrief = min(rows * 2, len(leftover))
            key = (len(used) * 3 + nbrief, len(used), -rows)
            if best is None or key > best[0]:
                best = (key, rows, brief_h, brief_top, grid_bottom,
                        scale, cards, collist, coly, used, leftover)

    (_, rows, brief_h, brief_top, grid_bottom,
     scale, cards, collist, coly, used_cards, leftover) = best

    # brief entries: two columns of one-liners, ordered to even out the
    # regions the grid under-served rather than by record order
    bcolw = (CW - 24) / 2.0
    running = {a: 0 for a in R.AREAS}
    for c in used_cards:
        running[c["s"]["area"]] += 1
    for s in (lead,) + tuple(subs):
        running[s["area"]] += 1
    ranked = sorted(
        enumerate(leftover),
        key=lambda p: (running[p[1]["s"]["area"]], p[1]["s"]["tier"], p[0]),
    )
    brief_cols = [[], []]
    for i, (_, c) in enumerate(ranked[:rows * 2]):
        s = c["s"]
        aw = tw(s["area"], "sans_b", 7.0)
        line, _ = wrap(s["head"], "serif", BRIEF_FS, bcolw - aw - 5, maxlines=1)
        brief_cols[i % 2].append((s, aw, line[0] if line else ""))
        running[s["area"]] += 1

    drawn = [lead] + list(subs) + [c["s"] for c in used_cards]
    drawn += [e[0] for col in brief_cols for e in col]

    # ------------------------------------------------------------- paint
    BOXES.clear()
    paint_masthead(mast, TOP)
    paint_figures(fig, fig_top)
    lead_end = paint_lead(L, lead_top)
    assert lead_end <= grid_top, (lead_end, grid_top)

    rule(grid_top - 6, INK, 1.4)

    colx = [M + i * (COLW + COLGUT) for i in range(3)]
    for i, col in enumerate(collist):
        yy = grid_top
        for j, c in enumerate(col):
            s = c["s"]
            y0 = yy
            aw = text(colx[i], yy, s["area"], "sans_b", 7.4, RED, track=0.8,
                      tag="card")
            text(colx[i] + aw + 4, yy, s["slug"], "sans", 7.2, GREY, track=0.8,
                 tag="card")
            yy += KICK_H
            for ln in c["hl"]:
                text(colx[i], yy, ln, "serif_b", scale[0], INK, tag="card")
                yy += scale[1]
            yy += HEAD_GAP
            for ln in c["bl"]:
                text(colx[i], yy, ln, "serif", scale[2], BODY, tag="card")
                yy += scale[3]
            yy += BODY_GAP
            text(colx[i], yy, s["src"], "sans", 7.0, GREY, tag="card")
            yy += SRC_H
            assert abs((yy - y0) - c["h"]) < 0.01, (c["h"], yy - y0)
            if j < len(col) - 1:
                rule(yy - GAP / 2.0, LIGHT, 0.8, x0=colx[i], x1=colx[i] + COLW)
                yy += GAP
        assert yy <= grid_bottom + 0.5, (i, yy, grid_bottom)

    grid_used = max(coly)

    # ---- region index, counted from what was actually drawn ----------
    tally = {a: 0 for a in R.AREAS}
    for s in drawn:
        tally[s["area"]] += 1
    for a in R.AREAS:
        assert tally[a] > 0, "region missing from page: " + a
    assert sum(tally.values()) == len(drawn)
    idx_txt = "   ".join("%s %d" % (a, tally[a]) for a in R.AREAS)
    idx_y = grid_used + 3
    text(M, idx_y, idx_txt, "sans_b", 8.0, INK, track=0.7, tag="index")
    rule(idx_y + 10.0, INK, 1.0)
    assert idx_y + 10.5 <= brief_top - 2, (idx_y, brief_top)

    # ---- brief strip --------------------------------------------------
    rule(brief_top, INK, 1.2)
    text(M, brief_top + 4, "IN BRIEF", "sans_b", 7.4, RED, track=2.2, tag="brief")
    bstart = brief_top + BRIEF_HEAD_H + 2
    for ci in range(2):
        bx = M + ci * (bcolw + 24)
        yy = bstart
        for s, aw, line in brief_cols[ci]:
            text(bx, yy, s["area"], "sans_b", 7.0, RED, tag="brief")
            text(bx + aw + 5, yy - 0.8, line, "serif", BRIEF_FS, BODY, tag="brief")
            yy += BRIEF_ROW_H
    if brief_cols[0]:
        vrule(M + bcolw + 12, bstart - 1,
              bstart + max(len(brief_cols[0]), len(brief_cols[1])) * BRIEF_ROW_H - 3)

    # ---- footer -------------------------------------------------------
    rule(footer_top, INK, 1.0)
    srcs = sorted({s["src"] for s in drawn})
    line1 = "%s   -   %d stories, seven regions" % (R.DAY_LONG, len(drawn))
    text(M, footer_top + 5, line1, "sans_b", 7.8, INK, track=0.4, tag="foot")
    line2 = "Sources: " + ", ".join(srcs)
    fs = 7.0
    while tw(line2, "sans", fs) > CW and fs > 4.6:
        fs -= 0.1
    text(M, footer_top + 14, line2, "sans", fs, GREY, tag="foot")

    bottom = footer_top + footer_h

    # ---- audit --------------------------------------------------------
    over = [(t, round(a, 1), round(b, 1), round(d, 1)) for (a, bb, b, d, t) in BOXES
            if a < M - 0.6 or b > PAGE - M + 0.6 or d > PAGE - 2]
    if over:
        raise AssertionError("text outside margins: %r" % over[:6])

    out = _canvas.resize((PAGE, PAGE), Image.LANCZOS)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(HERE, "out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    out.save(path, format="PNG", optimize=True)

    print("record stories:", len(stories))
    print("stories drawn:", len(drawn))
    print("tally:", tally)
    print("sum(tally):", sum(tally.values()))
    print("grid cards:", len(used_cards), "brief rows:", rows,
          "brief entries:", sum(len(c) for c in brief_cols))
    print("card scale:", scale)
    print("grid band:", round(grid_top, 1), "->", round(grid_used, 1),
          "of", round(grid_bottom, 1))
    print("bottom y:", bottom)
    print("bytes:", os.path.getsize(path))


if __name__ == "__main__":
    main()

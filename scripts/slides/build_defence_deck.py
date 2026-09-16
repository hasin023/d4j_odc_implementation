"""Build the thesis defence slide deck.

Writes ONLY to the Defence copy:
  iut_submissions/presentation/Defence/SWE_..._presentation.pptx
The pre-defence files are never touched.

All content comes from the finalized defence book (latex/defence book/main.tex);
the reference list and its numbering follow the book's bibliography — 28 entries
are actually cited (the commented-out multi-fault citation is excluded).

Design: an academic, non-Beamer deck — white canvas, one deep navy primary,
grey neutrals, colour only inside figures. One sans family (Source Sans 3) for
all text, Source Code Pro for code and identifiers only.

Each slide carries a purpose-built figure rather than a repeated chart type: an
annotated Defects4J diff, the ODC taxonomy tree, a study-positioning spectrum,
the reasoning loop, nested agreement tiers, a Landis-Koch kappa ruler, waffle
grids, a label-transition flow, a vocabulary dot cloud, and dumbbell plots.
Every graphic is a native, editable shape (except the methodology diagram and
the logo), so the deck stays editable in Google Slides.

Size floors from the pre-defence deck: titles 30 pt, page numbers 18 pt,
body >= 15 pt (short labels >= 14 pt), references >= 15 pt.

Usage:  python scripts/slides/build_defence_deck.py
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
DEFENCE = ROOT / "iut_submissions/presentation/Defence"
DECK = DEFENCE / "SWE_Orthogonal Defect Classification on Defects4J Using an LLM-Driven Scientific Approach_presentation.pptx"
LOGO = DEFENCE / "iut_logo.png"  # 141 x 232 px
LOGO_RATIO = 141 / 232
CONTENT_TOTAL = 24
SW = 13.333

# ── Palette ────────────────────────────────────────────────────────────────
def rgb(h: str) -> RGBColor:
    return RGBColor.from_string(h)

WHITE = "FFFFFF"
NAVY = "12284C"
INK = "1C2128"
MUTED = "5A6270"
FAINT = "8A919C"
RULE = "D5D9DF"
PANEL = "F4F5F7"
PANEL2 = "E6EAF0"
PRE, PRE_BG = "A23B3B", "F7E6E6"
POST, POST_BG = "2F7D4F", "E3F1E8"
GOLD = "B7791F"
GREY_BAR = "B3B9C3"
# Muted ODC type colours, used only inside figures.
T = {"CHK": "C07A2C", "ALG": "2F5D9B", "ASN": "6D4C9A", "TIM": "8A9199",
     "FCO": "9B3D4E", "INT": "2B7F72", "REL": "8A6E52"}
TYPE_NAME = {"ALG": "Algorithm/Method", "ASN": "Assignment/Initialization", "CHK": "Checking",
             "TIM": "Timing/Serialization", "FCO": "Function/Class/Object",
             "INT": "Interface/O-O Messages", "REL": "Relationship"}

SANS = "Source Sans 3"
MONO = "Source Code Pro"
SECTIONS = [("Context", 3, 8), ("Methodology", 9, 16), ("Results", 17, 24)]


# ── Primitives ─────────────────────────────────────────────────────────────
def _drop_style(shape):
    """Remove the theme style reference, whose effect (a shadow) LibreOffice renders."""
    style = shape._element.find("{http://schemas.openxmlformats.org/presentationml/2006/main}style")
    if style is not None:
        shape._element.remove(style)


def box(s, x, y, w, h, fill=None, line=None, lw=0.75, shape=MSO_SHAPE.RECTANGLE):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill:
        sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = rgb(line); sh.line.width = Pt(lw)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    _drop_style(sh)
    return sh


def dot(s, x, y, d, fill):
    return box(s, x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL)


def text(s, x, y, w, h, runs, size=17, color=INK, font=SANS, bold=False, italic=False, align="l",
         anchor="t", spacing=1.0, after=0, inset=0.03):
    """runs: str | list of paragraphs; a paragraph is str or list of (text, style-dict)."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(inset))
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        p.line_spacing = spacing
        p.space_after = Pt(after)
        segs = [(para, {})] if isinstance(para, str) else para
        for seg, st in segs:
            r = p.add_run()
            r.text = seg
            f = r.font
            f.name = st.get("font", font)
            f.size = Pt(st.get("size", size))
            f.bold = st.get("bold", bold)
            f.italic = st.get("italic", italic)
            f.color.rgb = rgb(st.get("color", color))
            if st.get("sub"):
                r.font._rPr.set("baseline", "-25000")
    return tb


def line(s, x1, y1, x2, y2, color=RULE, width=0.75, arrow=False, dash=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    _drop_style(c)
    ln = c.line._get_or_add_ln()
    ns = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
    if dash:
        ln.append(parse_xml(f'<a:prstDash {ns} val="dash"/>'))
    if arrow:
        ln.append(parse_xml(f'<a:tailEnd {ns} type="triangle" w="med" len="med"/>'))
    return c


def bullets(s, x, y, w, h, items, size=17, after=10):
    paras = [[("▪  ", {"color": NAVY, "size": size - 4}), (it, {})] for it in items]
    return text(s, x, y, w, h, paras, size=size, after=after, spacing=1.05)


def label(s, x, y, w, txt, color=MUTED, align="l", size=14):
    return text(s, x, y, w, 0.36, txt.upper(), size=size, color=color, bold=True, align=align)


def stat(s, x, y, w, big, small, size=34, color=NAVY):
    text(s, x, y, w, size / 50, big, size=size, bold=True, color=color)
    text(s, x, y + size / 50 + 0.02, w, 0.42, small, size=16, color=MUTED)


def note(s, txt):
    text(s, 0.6, 6.55, 12.13, 0.4, txt, size=15, color=MUTED, italic=True)


def logo(s, x, y, h):
    s.shapes.add_picture(str(LOGO), Inches(x), Inches(y), Inches(h * LOGO_RATIO), Inches(h))


# ── Chrome ─────────────────────────────────────────────────────────────────
def new_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[0])
    box(s, 0, 0, SW, 7.5, fill=WHITE)
    return s


def title_bar(s, title):
    text(s, 0.6, 0.3, 11.3, 0.8, title, size=30, bold=True, color=NAVY, anchor="b")
    logo(s, 12.28, 0.32, 0.78)
    line(s, 0.6, 1.18, 12.73, 1.18, color=RULE, width=0.75)
    box(s, 0.6, 1.16, 1.0, 0.045, fill=NAVY)


def page_number(s, num, total=None):
    text(s, 10.9, 7.02, 1.83, 0.44, f"{num} / {total}" if total else str(num),
         size=18, bold=True, color=NAVY, align="r", anchor="m")


def chrome(prs, title, num):
    s = new_slide(prs)
    title_bar(s, title)
    line(s, 0.6, 7.0, 12.73, 7.0, color=RULE, width=0.75)
    text(s, 0.6, 7.04, 4.3, 0.4, "ODC on Defects4J  ·  Thesis Defence", size=14, color=FAINT, anchor="m")
    x = 5.0
    for name, lo, hi in SECTIONS:
        active = lo <= num <= hi
        w = 0.2 + 0.105 * len(name)
        text(s, x, 7.04, w, 0.4, name, size=14, bold=active, color=NAVY if active else FAINT, anchor="m", align="c")
        if active:
            box(s, x + 0.1, 7.39, w - 0.2, 0.035, fill=NAVY)
        x += w + 0.25
    page_number(s, num, CONTENT_TOTAL)
    return s


def keyline(s, y, msg, h=0.6):
    box(s, 0.6, y, 0.07, h, fill=NAVY)
    text(s, 0.85, y, 11.9, h, msg, size=18, anchor="m")


# ── Figure builders ────────────────────────────────────────────────────────
def waffle(s, x, y, cols, cell, gap, counts, order):
    """Square grid, one cell per unit, drawn in `order`."""
    i = 0
    for k in order:
        for _ in range(counts[k]):
            box(s, x + (i % cols) * (cell + gap), y + (i // cols) * (cell + gap), cell, cell, fill=T[k])
            i += 1
    return i


def dumbbell(s, x, y, w, rows, lo, hi, row_h=0.62, size=16, label_w=1.35,
             colors=(GREY_BAR, NAVY), fmt="{:.2f}"):
    """rows: (label, value_a, value_b) drawn as a connected pair of dots."""
    ax = x + label_w
    aw = w - label_w - 0.6
    for i, (lab, a, b) in enumerate(rows):
        yy = y + i * row_h + row_h / 2
        text(s, x, yy - 0.22, label_w, 0.44, lab, size=size, anchor="m")
        xa = ax + aw * (a - lo) / (hi - lo)
        xb = ax + aw * (b - lo) / (hi - lo)
        line(s, xa, yy, xb, yy, color=RULE, width=3.0)
        dot(s, xa - 0.09, yy - 0.09, 0.18, colors[0])
        dot(s, xb - 0.09, yy - 0.09, 0.18, colors[1])
        text(s, ax + aw + 0.1, yy - 0.22, 0.5, 0.44, fmt.format(b), size=size - 1, bold=True, anchor="m")
    return ax, aw


def dumbbell_key(s, x, y, items):
    cx = x
    for col, lab in items:
        dot(s, cx, y + 0.09, 0.2, col)
        w = 0.35 + 0.1 * len(lab)
        text(s, cx + 0.28, y, w, 0.38, lab, size=15, color=MUTED, anchor="m")
        cx += w + 0.35


def kappa_ruler(s, x, y, w, value, h=0.34, size=17):
    """Landis-Koch bands [27] with a marker at `value`."""
    bands = [(0.0, 0.20, "EDF0F4", "slight"), (0.20, 0.40, "D3DAE4", "fair"),
             (0.40, 0.60, "9FB0C6", "moderate"), (0.60, 0.80, "5E789F", "substantial"),
             (0.80, 1.0, "2E4A7D", "almost perfect")]
    for lo, hi, col, name in bands:
        bx, bw = x + w * lo, w * (hi - lo)
        box(s, bx, y, bw, h, fill=col)
        text(s, bx, y + h + 0.02, bw, 0.3, name, size=13, color=MUTED, align="c")
    mx = x + w * value
    box(s, mx - 0.015, y - 0.16, 0.03, h + 0.32, fill=INK)
    text(s, mx - 0.9, y - 0.56, 1.8, 0.4, f"κ = {value:.3f}", size=size, bold=True, align="c")


def table(s, x, y, cols, rows, size=16, row_h=0.46, bold_cols=()):
    """cols: (header, width, align); rows: tuples of str or run-lists."""
    xx = x
    for head, w, al in cols:
        text(s, xx, y, w, 0.42, head, size=15, bold=True, color=NAVY, align=al, anchor="b")
        xx += w
    total_w = sum(w for _, w, _ in cols)
    line(s, x, y + 0.47, x + total_w, y + 0.47, color=NAVY, width=1.25)
    for r_i, row in enumerate(rows):
        yy = y + 0.52 + r_i * row_h
        xx = x
        for c_i, ((head, w, al), v) in enumerate(zip(cols, row)):
            text(s, xx, yy, w, row_h, v, size=size, bold=c_i in bold_cols, align=al, anchor="m")
            xx += w
        line(s, x, yy + row_h, x + total_w, yy + row_h, color=RULE)


def diff_block(s, x, y, w, header, rows, size=15, row_h=0.4):
    """Code-review style diff. rows: (kind, code) with kind in ' ', '-', '+'."""
    box(s, x, y, w, 0.44, fill=PANEL2)
    text(s, x + 0.15, y, w - 0.3, 0.44, header, size=14, font=MONO, color=MUTED, anchor="m")
    body_h = len(rows) * row_h + 0.16
    box(s, x, y + 0.44, w, body_h, fill=PANEL)
    for i, (kind, code) in enumerate(rows):
        yy = y + 0.52 + i * row_h
        col, bg = {"-": (PRE, PRE_BG), "+": (POST, POST_BG)}.get(kind, (INK, None))
        if bg:
            box(s, x, yy, w, row_h, fill=bg)
            box(s, x, yy, 0.05, row_h, fill=col)
        text(s, x + 0.15, yy, w - 0.3, row_h, f"{kind} {code}", size=size, font=MONO, color=col, anchor="m")
    return y + 0.44 + body_h


CHART9 = [(" ", "    endIndex = endIndex - 1;"),
          ("-", "if (endIndex < 0) {"),
          ("+", "if ((endIndex < 0) || (endIndex < startIndex)) {"),
          (" ", "    emptyRange = true;"),
          (" ", "}")]


# ── Slides ─────────────────────────────────────────────────────────────────
def s01_title(prs):
    s = new_slide(prs)
    box(s, 0, 0, SW, 0.12, fill=NAVY)
    logo(s, 0.8, 0.55, 1.35)
    text(s, 1.8, 0.72, 7.0, 0.42, "Islamic University of Technology", size=20, bold=True, color=NAVY)
    text(s, 1.8, 1.12, 7.0, 0.4, "Department of Computer Science and Engineering", size=16, color=MUTED)
    text(s, 0.8, 2.25, 10.6, 1.7, ["Orthogonal Defect Classification", "on Defects4J"], size=44, bold=True, color=NAVY, spacing=0.95)
    text(s, 0.8, 3.95, 10.6, 0.6, "Using an LLM-Driven Scientific Approach", size=27)
    line(s, 0.8, 4.75, 3.4, 4.75, color=NAVY, width=1.5)
    text(s, 0.8, 4.87, 8.4, 0.42, "Thesis Defence  ·  B.Sc. in Computer Science and Engineering", size=17, color=MUTED)
    text(s, 0.8, 5.55, 4.6, 1.6, [
        [("Presented by", {"bold": True, "color": NAVY, "size": 15})],
        "Md. Sakib Hossain  (210042133)",
        "Mohammad Nahiyan Kabir  (210042168)",
        "Hasin Mahtab Alvee  (210042174)",
    ], size=16, after=2)
    text(s, 5.85, 5.55, 4.6, 1.6, [
        [("Supervisor", {"bold": True, "color": NAVY, "size": 15})],
        "Lutfun Nahar Lota, Assistant Professor",
        [("Co-supervisor", {"bold": True, "color": NAVY, "size": 15})],
        "Ishmam Tashdeed, Lecturer",
    ], size=16, after=2)
    box(s, 0, 7.38, SW, 0.12, fill=NAVY)


def s02_outline(prs, num):
    s = chrome(prs, "Outline", num)
    groups = [("Context", "slides 3–8", ["Motivation and Defects4J", "ODC and related work", "Pre-fix vs post-fix", "Research questions"]),
              ("Methodology", "slides 9–16", ["Pipeline and evidence", "Conditions and prompts", "The reasoning loop", "Evaluation and setup"]),
              ("Results", "slides 17–24", ["RQ1–RQ2: types, coverage", "RQ3: agreement and drift", "RQ4: taxonomy and loop", "Threats and conclusion"])]
    for i, (sec, rng, items) in enumerate(groups):
        x = 0.6 + i * 4.15
        box(s, x, 1.75, 3.85, 0.07, fill=NAVY)
        text(s, x, 2.05, 0.8, 0.75, f"{i + 1}", size=44, bold=True, color=PANEL2, anchor="m")
        text(s, x + 0.85, 2.05, 3.0, 0.45, sec, size=23, bold=True, anchor="m")
        text(s, x + 0.85, 2.55, 3.0, 0.36, rng, size=15, color=MUTED)
        bullets(s, x, 3.2, 3.85, 3.0, items, size=18, after=18)


def s03_motivation(prs, num):
    s = chrome(prs, "Motivation: Classifying Defects in Defects4J", num)
    stat(s, 0.6, 1.45, 2.7, "836", "reproducible real bugs", size=46)
    stat(s, 3.5, 1.45, 2.7, "17", "Java projects [5]", size=46)
    line(s, 0.6, 2.75, 6.3, 2.75, color=RULE)
    bullets(s, 0.6, 2.95, 5.9, 2.4, ["Defect types need different debugging strategies",
                                     "Aggregated labels expose recurring mistakes",
                                     "Manual triage is accurate, but does not scale"], size=18, after=18)
    x, w = 6.9, 5.83
    label(s, x, 1.45, w, "What every Defects4J bug ships with")
    rows = [("Bug report", MUTED), ("Failing tests + stack traces", MUTED),
            ("Buggy source", PRE), ("Fixed source", POST), ("Fix diff", POST)]
    for i, (a, c) in enumerate(rows):
        y = 1.88 + i * 0.78
        box(s, x, y, w, 0.66, fill=PANEL if c == MUTED else (PRE_BG if c == PRE else POST_BG))
        box(s, x, y, 0.07, 0.66, fill=c)
        text(s, x + 0.3, y, w - 0.5, 0.66, a, size=18, bold=True, color=INK if c == MUTED else c, anchor="m")
    keyline(s, 5.95, [[("Every bug ships with its fix, so one bug can be classified ", {}),
                       ("before", {"bold": True, "color": PRE}), (" and ", {}), ("after", {"bold": True, "color": POST}), (" it.", {})]], h=0.7)


def s04_odc(prs, num):
    s = chrome(prs, "Orthogonal Defect Classification (ODC)", num)
    text(s, 0.6, 1.32, 12.13, 0.45, [[("ODC [4, 15] describes a defect when it is found (", {}), ("opener", {"italic": True}),
        (") and when it is fixed (", {}), ("closer", {"italic": True}), ("). We classify one closer attribute:", {})]], size=18)
    rx, ry, rw = 4.5, 1.95, 2.6
    box(s, rx, ry, rw, 0.6, fill=NAVY)
    text(s, rx, ry, rw, 0.6, "Defect Type", size=19, bold=True, color=WHITE, align="c", anchor="m")
    text(s, rx + rw + 0.2, ry, 4.0, 0.6, "the nature of the correction", size=17, color=MUTED, anchor="m")
    fams = [("Control and Data Flow", 0.6, 6.25, ["CHK", "ALG", "ASN", "TIM"]),
            ("Structural", 7.1, 5.63, ["FCO", "INT", "REL"])]
    line(s, rx + rw / 2, ry + 0.6, rx + rw / 2, 2.85, color=FAINT, width=1.25)
    line(s, 0.6 + 6.25 / 2, 2.85, 7.1 + 5.63 / 2, 2.85, color=FAINT, width=1.25)
    defs = {"CHK": "missing or wrong condition", "ALG": "wrong computation", "ASN": "wrong value or initialization",
            "TIM": "wrong ordering or concurrency", "FCO": "missing capability", "INT": "wrong interaction across a boundary",
            "REL": "broken association"}
    for fam, fx, fw, types in fams:
        cx = fx + fw / 2
        line(s, cx, 2.85, cx, 3.05, color=FAINT, width=1.25)
        box(s, fx, 3.05, fw, 0.5, fill=PANEL2)
        text(s, fx, 3.05, fw, 0.5, fam, size=17, bold=True, color=NAVY, align="c", anchor="m")
        gap = 0.12
        cw = (fw - gap * (len(types) - 1)) / len(types)
        for j, k in enumerate(types):
            x = fx + j * (cw + gap)
            line(s, x + cw / 2, 3.55, x + cw / 2, 3.73, color=FAINT, width=1.0)
            box(s, x, 3.73, cw, 2.05, fill=WHITE, line=RULE)
            box(s, x, 3.73, cw, 0.07, fill=T[k])
            text(s, x + 0.06, 3.87, cw - 0.12, 0.9, TYPE_NAME[k].replace("/", "/\n").split("\n"),
                 size=16, bold=True, align="c", anchor="m", spacing=0.95)
            text(s, x + 0.08, 4.8, cw - 0.16, 0.9, defs[k], size=15, color=MUTED, align="c", spacing=0.98)
    text(s, 0.6, 6.05, 12.13, 0.45, [[("+ Other", {"bold": True}),
        ("  —  escape category added in this study, allowed only with a written justification", {"color": MUTED})]], size=17)


def s05_related(prs, num):
    s = chrome(prs, "Related Work and the Research Gap", num)
    label(s, 0.6, 1.4, 12.13, "What prior work on Defects4J actually labels")
    ax, aw, ay = 1.0, 11.0, 3.15
    line(s, ax, ay, ax + aw, ay, color=FAINT, width=1.25, arrow=True)
    marks = [(0.07, "how a bug\nmanifests", "Van der Spuy &\nFischer 2025 [8]", "488 faults"),
             (0.36, "what the patch\nchanged", "Sobreira et al.\n2018 [9]", "395 patches"),
             (0.62, "one-off manual\ninspection", "Jiang et al.\n2019 [10]", "50 bugs")]
    for px, what, who, count in marks:
        x = ax + aw * px
        dot(s, x - 0.09, ay - 0.09, 0.18, NAVY)
        text(s, x - 1.15, ay - 1.35, 2.3, 0.9, what.split("\n"), size=17, bold=True, align="c", anchor="b", spacing=0.95)
        text(s, x - 1.15, ay + 0.18, 2.3, 0.75, who.split("\n"), size=15, color=MUTED, align="c", spacing=0.95)
        text(s, x - 1.15, ay + 0.95, 2.3, 0.36, count, size=15, bold=True, color=NAVY, align="c")
    gx = ax + aw * 0.80
    box(s, gx, ay - 1.45, ax + aw - gx, 2.7, fill=PANEL2)
    text(s, gx, ay - 1.35, ax + aw - gx, 0.9, ["semantic", "defect type"], size=19, bold=True, color=NAVY, align="c", spacing=0.95)
    text(s, gx, ay + 0.25, ax + aw - gx, 0.8, ["not labelled", "at scale"], size=16, color=PRE, align="c", spacing=1.0)
    text(s, 0.6, 4.65, 5.9, 1.2, [[("LLM classifiers [11, 12, 14, 16]", {"bold": True})],
                                  [("read bug-report text only; without a fixed taxonomy their labels are inconsistent.", {"color": MUTED})]],
         size=17, spacing=1.05, after=4)
    text(s, 6.9, 4.65, 5.83, 1.2, [[("ODC studies [19, 20, 21]", {"bold": True})],
                                   [("classify other corpora — never Defects4J at benchmark scale.", {"color": MUTED})]],
         size=17, spacing=1.05, after=4)
    keyline(s, 5.95, "Gap: no semantic defect-type labels for Defects4J, and no way to evaluate them without ground truth.", h=0.6)


def s06_problem(prs, num):
    s = chrome(prs, "Problem Statement", num)
    box(s, 0.6, 1.5, 0.07, 1.6, fill=NAVY)
    text(s, 0.95, 1.45, 11.7, 1.7, [[("Classify Defects4J bugs into ODC defect types ", {}),
        ("from pre-fix evidence alone", {"bold": True, "color": NAVY}), (" — and evaluate that classification ", {}),
        ("without ground-truth labels.", {"bold": True, "color": NAVY})]], size=27, anchor="m", spacing=1.08)
    label(s, 0.6, 3.5, 12.13, "A solution therefore has to be")
    reqs = [("Context-aware", "code, tests, traces and reports together"), ("Semantic", "the defect mechanism, not the syntax"),
            ("Taxonomy-constrained", "a fixed, comparable label space"), ("Evaluable", "carries its own reference, without ground truth")]
    for i, (a, b) in enumerate(reqs):
        x = 0.6 + (i % 2) * 6.2
        y = 4.1 + (i // 2) * 1.5
        line(s, x, y, x + 5.93, y, color=NAVY, width=1.25)
        text(s, x, y + 0.14, 5.93, 0.48, a, size=21, bold=True)
        text(s, x, y + 0.66, 5.93, 0.5, b, size=17, color=MUTED)


def s07_idea(prs, num):
    s = chrome(prs, "Core Idea: One Bug, Two Classifications", num)
    x, w = 0.6, 6.45
    label(s, x, 1.4, w, "Defects4J Chart_9")
    end = diff_block(s, x, 1.8, w, "org.jfree.data.time.TimeSeries", CHART9, size=14, row_h=0.38)
    text(s, x, end + 0.1, w, 0.42, "The fix widens a guard to catch an empty range.", size=16, color=MUTED)
    vx, vw = 7.4, 5.33
    for i, (t_, c, ev, why) in enumerate([("Pre-fix", PRE, "report · tests · trace · code", "Triage: no fix exists yet."),
                                          ("Post-fix", POST, "the same evidence + the fix diff", "Informed by the correction.")]):
        yy = 1.4 + i * 1.7
        box(s, vx, yy, vw, 1.5, fill=WHITE, line=RULE)
        box(s, vx, yy, 0.07, 1.5, fill=c)
        text(s, vx + 0.25, yy + 0.08, vw - 0.4, 0.45, t_, size=19, bold=True, color=c)
        text(s, vx + 0.25, yy + 0.53, vw - 0.4, 0.42, ev, size=16, font=MONO)
        text(s, vx + 0.25, yy + 0.98, vw - 0.4, 0.45, why, size=16, color=MUTED)
    label(s, 0.6, 4.95, 12.13, "Defects4J has no ODC labels, so we define")
    for i, (a, b) in enumerate([("Post-fix label", "the fix-informed reference"), ("Pre-fix vs post-fix", "does the triage label hold?"), ("Labels differ", "drift")]):
        x = 0.6 + i * 4.15
        line(s, x, 5.35, x + 3.85, 5.35, color=NAVY, width=1.25)
        text(s, x, 5.42, 3.85, 0.42, a, size=19, bold=True, color=NAVY)
        text(s, x, 5.85, 3.85, 0.42, [[("= ", {"color": FAINT}), (b, {})]], size=17)
    note(s, "Agreement is not correctness: we measure how closely a pre-fix label reproduces a better-informed reference.")


def s08_rqs(prs, num):
    s = chrome(prs, "Research Questions", num)
    rqs = [("RQ1", "Distribution", "Which ODC types dominate, and does the mix differ by project?"),
           ("RQ2", "Coverage", "Do the seven types cover every bug, or is “Other” needed?"),
           ("RQ3", "Accuracy", "How often does the pre-fix label match the post-fix reference?"),
           ("RQ4", "Components", "What do (a) the taxonomy and (b) the enforced loop contribute?")]
    for i, (k, n, q) in enumerate(rqs):
        y = 1.5 + i * 1.2
        box(s, 0.6, y + 0.08, 1.25, 0.82, fill=NAVY)
        text(s, 0.6, y + 0.08, 1.25, 0.82, k, size=22, bold=True, color=WHITE, align="c", anchor="m")
        text(s, 2.1, y + 0.08, 10.6, 0.45, n, size=21, bold=True)
        text(s, 2.1, y + 0.52, 10.6, 0.5, q, size=17, color=MUTED)
        if i < 3:
            line(s, 0.6, y + 1.12, 12.73, y + 1.12, color=RULE)
    note(s, "410 bugs  ·  six Defects4J projects  ·  1,640 classifications.")


def s09_pipeline(prs, num):
    s = chrome(prs, "Pipeline Overview", num)
    img = ROOT / "scripts/slides/assets/methodology_diagram.png"  # cropped copy of latex/defence book/Methodology Diagram.png
    h = 5.45
    w = h * 1920 / 1000
    s.shapes.add_picture(str(img), Inches((SW - w) / 2), Inches(1.4), Inches(w), Inches(h))


def s10_evidence(prs, num):
    s = chrome(prs, "Evidence Collection: the Case File", num)
    x, w = 0.6, 6.1
    label(s, x, 1.42, w, "context.json  ·  one per bug and evidence mode")
    box(s, x, 1.82, w, 4.4, fill=PANEL)
    rows = [("{", INK), ('  "bug_report":        sanitized,', INK), ('  "failing_tests":     name, message,', INK),
            ('                       stack trace,', INK), ('  "suspicious_frames": project frames,', INK),
            ('  "code_snippets":     ±12 / ±18 lines,', INK), ('  "coverage":          line, branch,', INK),
            ('  "hidden_oracles":    modified classes,', GOLD), ('  "fix_diff":          post-fix only', POST), ("}", INK)]
    for i, (t_, c) in enumerate(rows):
        text(s, x + 0.25, 1.98 + i * 0.42, w - 0.4, 0.42, t_, size=15, font=MONO, color=c)
    items = [("Suspicious frames", "Only frames in the project's own source; JUnit, JDK and build-tool frames are dropped.", NAVY),
             ("Sanitized pre-fix evidence", "Classes touched by the fix and “fixed in” discussion are removed.", NAVY),
             ("Hidden oracle", "Modified classes are kept for evaluation, never put in the prompt.", GOLD)]
    for i, (a, b, col) in enumerate(items):
        yy = 1.85 + i * 1.5
        box(s, 7.1, yy + 0.06, 0.06, 1.1, fill=col)
        text(s, 7.35, yy, 5.38, 0.45, a, size=19, bold=True, color=NAVY)
        text(s, 7.35, yy + 0.45, 5.38, 0.95, b, size=16, color=MUTED, spacing=1.05)
    note(s, "Pre-fix and post-fix runs share one evidence store; only the fix diff differs.")


def s11_conditions(prs, num):
    s = chrome(prs, "Classification Conditions", num)
    text(s, 0.6, 1.32, 12.13, 0.45, "A condition = taxonomy (label space) × strategy (reasoning).", size=18, color=MUTED)
    gx, gy, cw, ch = 2.3, 2.4, 1.85, 0.92
    label(s, gx, 1.95, cw * 3, "Taxonomy", align="c")
    text(s, 0.6, gy, 1.7, 0.45, "STRATEGY", size=14, bold=True, color=MUTED, anchor="m")
    valid = {("zero", "free"), ("few", "closed"), ("few", "open"), ("scientific", "closed"), ("scientific", "open")}
    for ci, c in enumerate(["free", "closed", "open"]):
        text(s, gx + ci * cw, gy, cw, 0.45, c, size=17, bold=True, align="c", anchor="m")
    line(s, 0.6, gy + 0.5, gx + 3 * cw, gy + 0.5, color=NAVY, width=1.25)
    for ri, r in enumerate(["zero", "few", "scientific"]):
        y = gy + 0.55 + ri * ch
        text(s, 0.6, y, 1.7, ch, r, size=17, bold=True, anchor="m")
        for ci, c in enumerate(["free", "closed", "open"]):
            x = gx + ci * cw
            if (r, c) == ("scientific", "open"):
                box(s, x + 0.08, y + 0.08, cw - 0.16, ch - 0.16, fill=NAVY)
                text(s, x + 0.08, y + 0.08, cw - 0.16, ch - 0.16,
                     ["scientific-open", [("default", {"size": 14, "bold": False})]],
                     size=15, bold=True, color=WHITE, align="c", anchor="m", spacing=0.95)
            elif (r, c) in valid:
                box(s, x + 0.08, y + 0.08, cw - 0.16, ch - 0.16, fill=PANEL2)
                text(s, x + 0.08, y + 0.08, cw - 0.16, ch - 0.16, f"{r}-{c}", size=15, bold=True, color=NAVY, align="c", anchor="m")
            else:
                text(s, x, y, cw, ch, "—", size=16, color=FAINT, align="c", anchor="m")
        line(s, 0.6, y + ch, gx + 3 * cw, y + ch, color=RULE)
    text(s, 0.6, 5.7, 7.2, 0.8, "Five of nine combinations are valid: zero uses no taxonomy, and free defines none.", size=16, color=MUTED)
    dx = 8.05
    yy = 1.95
    for head, items in [("Taxonomy", [("free", "the model's own words"), ("closed", "one of the 7 ODC types"), ("open", "7 types + a justified “Other”")]),
                        ("Strategy", [("zero", "one plain prompt"), ("few", "definitions, tree, 5 examples"), ("scientific", "enforced hypothesis–probe loop")])]:
        label(s, dx, yy, 4.68, head)
        yy += 0.42
        for k, d in items:
            text(s, dx, yy, 1.25, 0.56, k, size=17, bold=True, color=NAVY, anchor="m")
            text(s, dx + 1.25, yy, 3.43, 0.56, d, size=16, anchor="m", spacing=0.98)
            line(s, dx, yy + 0.58, 12.73, yy + 0.58, color=RULE)
            yy += 0.6
        yy += 0.25


def s12_prompts(prs, num):
    s = chrome(prs, "Prompt Design", num)
    text(s, 0.6, 1.3, 12.13, 0.42, "Capitalised names are prompt components: defined once, or filled in per bug.", size=17, color=MUTED)

    def msg(x, y, w, h, role, lines, accent, fill=PANEL, size=15):
        box(s, x, y, w, h, fill=fill)
        box(s, x, y, 0.06, h, fill=accent)
        text(s, x + 0.22, y + 0.06, 1.15, 0.32, role, size=13, font=MONO, bold=True, color=accent)
        text(s, x + 1.45, y + 0.04, w - 1.65, h - 0.1, lines, size=size, font=MONO, spacing=1.12, after=2, anchor="m")

    def arrow(x, y1, y2):
        line(s, x, y1, x, y2, color=FAINT, width=1.25, arrow=True)

    # left: single call
    lx, lw = 0.6, 5.95
    box(s, lx, 1.88, lw, 0.46, fill=NAVY)
    text(s, lx + 0.22, 1.88, lw - 0.4, 0.46, [[("few-open", {"bold": True}), ("     one call, one answer", {"size": 15})]],
         size=16, font=MONO, color=WHITE, anchor="m")
    msg(lx, 2.55, lw, 1.5, "system", ["ODC_TAXONOMY  ANTI_BIAS_RULES", "DECISION_TREE      (7 questions)",
                                      "FEW_SHOT_EXAMPLES  (5 bugs)", "OUTPUT_SCHEMA"], NAVY)
    arrow(lx + lw / 2, 4.05, 4.32)
    msg(lx, 4.32, lw, 0.62, "user", ["BUG_CONTEXT"], MUTED)
    arrow(lx + lw / 2, 4.94, 5.21)
    msg(lx, 5.21, lw, 0.62, "model", ["one JSON classification"], POST, fill=POST_BG)
    # right: loop
    rx, rw = 6.78, 5.95
    box(s, rx, 1.88, rw, 0.46, fill=NAVY)
    text(s, rx + 0.22, 1.88, rw - 0.4, 0.46, [[("scientific-open", {"bold": True}), ("     up to 6 turns", {"size": 15})]],
         size=16, font=MONO, color=WHITE, anchor="m")
    msg(rx, 2.55, rw, 1.0, "system", ["ODC_TAXONOMY  ANTI_BIAS_RULES", "PROBE_CATALOGUE  TURN_SCHEMA"], NAVY)
    arrow(rx + rw / 2, 3.55, 3.78)
    msg(rx, 3.78, rw, 0.54, "user", ["BUG_CONTEXT (summary)"], MUTED)
    box(s, rx - 0.12, 4.5, rw + 0.24, 1.42, fill=WHITE, line=NAVY, lw=1.0)
    text(s, rx + 0.02, 4.53, 2.6, 0.3, "EACH TURN", size=13, bold=True, color=NAVY)
    msg(rx, 4.86, rw, 0.48, "model", ["hypothesis · prediction · probe"], NAVY, fill=PANEL, size=14)
    msg(rx, 5.38, rw, 0.48, "user", ["PROBE_RESULT"], GOLD, fill="FBF2E3", size=14)
    text(s, rx + rw + 0.02, 4.5, 0.55, 1.42, "×6", size=16, bold=True, color=NAVY, align="c", anchor="m")
    arrow(rx + rw / 2, 5.92, 6.15)
    msg(rx, 6.15, rw, 0.55, "model", ["conclude → ODC defect type"], POST, fill=POST_BG)
    text(s, lx, 6.15, lw, 0.55, "The taxonomy and the evidence are identical in both.", size=16, italic=True, color=MUTED, anchor="m")


def s13_loop(prs, num):
    s = chrome(prs, "The Enforced Scientific Reasoning Loop", num)
    steps = [("Hypothesis", "commit to a type"), ("Prediction", "evidence that must exist"),
             ("Probe", "request that evidence"), ("Observation", "read what came back")]
    x0, y0, bw, gap = 0.6, 1.6, 2.55, 0.64
    for i, (a, b) in enumerate(steps):
        x = x0 + i * (bw + gap)
        box(s, x, y0, bw, 1.1, fill=WHITE, line=NAVY, lw=1.25)
        box(s, x, y0, bw, 0.06, fill=NAVY)
        text(s, x, y0 + 0.12, bw, 0.45, a, size=19, bold=True, color=NAVY, align="c")
        text(s, x, y0 + 0.58, bw, 0.42, b, size=16, color=MUTED, align="c")
        if i < 3:
            line(s, x + bw + 0.06, y0 + 0.55, x + bw + gap - 0.06, y0 + 0.55, color=NAVY, width=1.75, arrow=True)
    lx = x0 + 3 * (bw + gap) + bw / 2
    fx = x0 + bw / 2
    yb = y0 + 1.55
    line(s, lx, y0 + 1.1, lx, yb, color=NAVY, width=1.5)
    line(s, lx, yb, fx, yb, color=NAVY, width=1.5, dash=True)
    line(s, fx, yb, fx, y0 + 1.14, color=NAVY, width=1.5, dash=True, arrow=True)
    text(s, 3.2, yb + 0.02, 6.9, 0.42, "next turn while the evidence is insufficient  ·  at most 6 turns", size=15, color=MUTED, italic=True, align="c")
    box(s, 10.18, yb + 0.52, 2.55, 0.55, fill=POST_BG)
    text(s, 10.18, yb + 0.52, 2.55, 0.55, "Conclude: ODC label", size=16, bold=True, color=POST, align="c", anchor="m")
    text(s, 0.6, yb + 0.52, 9.3, 0.55, "Adapted from AutoSD [17, 18]: from locating a fault to naming its type.", size=16, color=MUTED, anchor="m")
    label(s, 0.6, 4.3, 12.13, "Five probes, executed against the evidence store")
    probes = [("list_evidence()", "what evidence exists"), ("full_stack_trace(test)", "trace and message"),
              ("snippet(class)", "source snippets"), ("coverage(class)", "line and branch"), ("bug_report()", "the full report")]
    for i, (p, d) in enumerate(probes):
        x = 0.6 + (i % 2) * 4.3
        y = 4.72 + (i // 2) * 0.68
        box(s, x, y, 4.1, 0.56, fill=PANEL)
        text(s, x + 0.2, y, 2.65, 0.56, p, size=14, font=MONO, bold=True, color=NAVY, anchor="m")
        text(s, x + 2.85, y, 1.05, 0.56, d, size=14, color=MUTED, anchor="m", align="r")
    text(s, 9.3, 4.9, 3.43, 1.2, "The prediction is fixed before the evidence arrives, so a first guess cannot be rationalised.", size=17, italic=True, anchor="m", spacing=1.05)


def s14_eval(prs, num):
    s = chrome(prs, "Evaluation Framework: Four Tiers of Agreement", num)
    label(s, 0.6, 1.4, 6.9, "Tiers 1–3 are nested: strict inside forgiving")
    tiers = [(0.0, 6.9, "EDF0F4", "Tier 3   Family match", "both types in the same family", MUTED),
             (0.8, 5.3, "C9D3E1", "Tier 2   Top-2 match", "either label is the other's alternative", NAVY),
             (1.6, 3.7, "2E4A7D", "Tier 1   Strict match", "the same ODC type", WHITE)]
    for i, (dx, w, col, name, desc, tc) in enumerate(tiers):
        y = 1.85 + i * 0.95
        box(s, 0.6 + dx, y, w, 0.85, fill=col)
        text(s, 0.78 + dx, y, w - 0.3, 0.45, name, size=17, bold=True, color=tc)
        text(s, 0.78 + dx, y + 0.42, w - 0.3, 0.4, desc, size=15, color=tc)
    text(s, 0.6, 4.75, 6.9, 1.0, "Three types cover 97.8% of labels, so shuffled labels still reach >92% on Tiers 2–3: we use them to grade disagreements, not as scores.",
         size=16, color=MUTED, spacing=1.05)
    x, w = 7.85, 4.88
    label(s, x, 1.4, w, "Tier 4  ·  Cohen's kappa")
    text(s, x, 1.75, w, 0.7, [[("κ", {"italic": True}), ("  =  (", {}), ("p", {"italic": True}), ("o", {"sub": True}), (" − ", {}),
                               ("p", {"italic": True}), ("e", {"sub": True}), (")  /  (1 − ", {}), ("p", {"italic": True}),
                               ("e", {"sub": True}), (")", {})]], size=27, anchor="m")
    text(s, x, 2.5, w, 0.9, [[("p", {"italic": True}), ("o", {"sub": True}), (" is observed agreement, ", {"color": MUTED}),
                              ("p", {"italic": True}), ("e", {"sub": True}), (" the agreement expected by chance.", {"color": MUTED})]],
         size=17, spacing=1.06)
    kappa_ruler(s, x, 4.5, w, 0.505)
    text(s, x, 5.2, w, 0.4, "Landis–Koch bands [27]", size=15, color=MUTED, align="c")


def s15_reference(prs, num):
    s = chrome(prs, "Why the Post-Fix Label Is a Valid Reference", num)
    label(s, 0.6, 1.4, 7.3, "Human agreement on ODC-style classification rises with evidence")
    ax, ay, aw, ah = 1.15, 2.4, 5.3, 2.5
    line(s, ax, ay, ax, ay + ah, color=FAINT, width=1.0)
    for v in (0.0, 0.5, 1.0):
        yy = ay + ah * (1 - v)
        line(s, ax, yy, ax + aw, yy, color=RULE)
        text(s, 0.6, yy - 0.18, 0.48, 0.36, f"{v:.1f}", size=14, color=FAINT, align="r")
    text(s, 0.6, ay - 0.42, 1.4, 0.36, "κ", size=15, bold=True, color=FAINT, italic=True)
    pts = [(0.10, 0.16, "fault descriptions only [22]", PRE),
           (0.52, 0.70, "full repository context [25]", GOLD),
           (0.93, 0.93, "full code and change [26]", POST)]
    prev = None
    for px, v, lab, col in pts:
        x, y = ax + aw * px, ay + ah * (1 - v)
        if prev:
            line(s, prev[0], prev[1], x, y, color=NAVY, width=2.0)
        prev = (x, y)
    for i, (px, v, lab, col) in enumerate(pts):
        x, y = ax + aw * px, ay + ah * (1 - v)
        dot(s, x - 0.11, y - 0.11, 0.22, col)
        text(s, x - 0.9, y - 0.58, 1.8, 0.4, f"{v:.2f}", size=18, bold=True, color=col, align="c")
        ly = 5.02 + i * 0.38
        dot(s, ax, ly + 0.09, 0.18, col)
        text(s, ax + 0.3, ly, 5.4, 0.38, lab, size=15, anchor="m")
    x = 7.6
    label(s, x, 1.4, 5.13, "Our data behave the same way")
    for i, (a, b) in enumerate([("68.0% → 76.3%", "strategy agreement, without → with the fix"),
                                ("6 of 6", "projects agree more once the fix is visible")]):
        y = 2.1 + i * 1.5
        text(s, x, y, 5.13, 0.55, a, size=27, bold=True, color=NAVY)
        text(s, x, y + 0.55, 5.13, 0.45, b, size=16, color=MUTED)
        line(s, x, y + 1.05, 12.73, y + 1.05, color=RULE)
    keyline(s, 6.2, "The run that sees the fix is better informed — but two labels can agree and both be wrong.", h=0.6)


def s16_setup(prs, num):
    s = chrome(prs, "Experimental Setup", num)
    label(s, 0.6, 1.4, 7.5, "410 bugs  ·  one square per bug")
    projects = [("Closure", 153), ("Math", 106), ("Lang", 61), ("Mockito", 38), ("Chart", 26), ("Time", 26)]
    shades = ["12284C", "24406E", "3A5A8C", "5E789F", "8A9EB8", "B3C0D2"]
    cell, gap, cols = 0.155, 0.045, 30
    i = 0
    for (p_, n), col in zip(projects, shades):
        for _ in range(n):
            box(s, 0.6 + (i % cols) * (cell + gap), 1.85 + (i // cols) * (cell + gap), cell, cell, fill=col)
            i += 1
    for j, ((p_, n), col) in enumerate(zip(projects, shades)):
        x = 0.6 + (j % 3) * 2.3
        y = 4.85 + (j // 3) * 0.45
        box(s, x, y + 0.08, 0.22, 0.22, fill=col)
        text(s, x + 0.32, y, 1.9, 0.38, f"{p_}  {n}", size=16, anchor="m")
    x, w = 7.9, 4.83
    label(s, x, 1.4, w, "Models")
    for i2, (m, d) in enumerate([("gemini-3.1-flash-lite-preview", "410 bugs"), ("gpt-5-mini", "13 bugs")]):
        y = 1.8 + i2 * 0.52
        text(s, x, y, 3.6, 0.48, m, size=15, font=MONO, color=NAVY, anchor="m")
        text(s, x + 3.6, y, 1.23, 0.48, d, size=15, color=MUTED, anchor="m", align="r")
        line(s, x, y + 0.5, 12.73, y + 0.5, color=RULE)
    label(s, x, 3.15, w, "Every bug, four times")
    for i2, (a, b) in enumerate([("2 conditions", "scientific-open and few-open"),
                                 ("2 evidence modes", "pre-fix and post-fix"),
                                 ("1,640", "classifications, plus a zero-free baseline")]):
        y = 3.6 + i2 * 0.92
        text(s, x, y, w, 0.42, a, size=21, bold=True, color=NAVY)
        text(s, x, y + 0.42, w, 0.42, b, size=16, color=MUTED)
    keyline(s, 6.15, "Reporting follows the guidelines for empirical studies with LLMs [28].", h=0.5)


def s17_rq12(prs, num):
    s = chrome(prs, "RQ1–RQ2: Distribution and Coverage", num)
    label(s, 0.6, 1.4, 7.5, "RQ1  ·  410 pre-fix labels, one square per bug")
    counts = {"CHK": 198, "ALG": 175, "ASN": 28, "REL": 5, "FCO": 3, "INT": 1}
    waffle(s, 0.6, 1.82, 30, 0.155, 0.045, counts, ["CHK", "ALG", "ASN", "REL", "FCO", "INT"])
    legend = [("CHK", "Checking  48.3%"), ("ALG", "Algorithm/Method  42.7%"), ("ASN", "Assignment  6.8%"),
              ("REL", "Relationship  1.2%"), ("FCO", "Function/Class  0.7%"), ("INT", "Interface  0.2%")]
    for j, (k, lab) in enumerate(legend):
        x = 0.6 + (j % 2) * 3.8
        y = 4.8 + (j // 2) * 0.44
        box(s, x, y + 0.08, 0.22, 0.22, fill=T[k])
        text(s, x + 0.32, y, 3.4, 0.38, lab, size=16, anchor="m")
    text(s, 0.6, 6.2, 7.3, 0.85, [[("97.8%", {"bold": True, "color": NAVY}),
        (" in three Control and Data Flow types; Timing never occurs. Mix by project: scientific ", {}),
        ("p = 0.096", {"bold": True}), (", few-shot ", {}), ("p = 0.010", {"bold": True}), (".", {})]],
        size=16, spacing=1.06)
    x, w = 8.35, 4.38
    box(s, x, 1.4, w, 5.05, fill=PANEL)
    label(s, x + 0.3, 1.55, w - 0.5, "RQ2  ·  the “Other” category")
    text(s, x + 0.3, 1.9, w - 0.5, 1.15, [[("0", {}), ("  of 1,640", {"size": 24, "color": MUTED, "bold": False})]],
         size=58, bold=True, color=NAVY, anchor="m")
    text(s, x + 0.3, 3.05, w - 0.5, 0.8, "classifications chose “Other”, although it was offered every time.", size=16, spacing=1.05)
    line(s, x + 0.3, 3.9, x + w - 0.3, 3.9, color=RULE)
    for i, (a, b) in enumerate([("≤ 0.2%", "95% upper bound on the escape rate"), ("6 of 7", "ODC types actually used")]):
        y = 4.25 + i * 0.95
        text(s, x + 0.3, y, 1.3, 0.7, a, size=20, bold=True, color=NAVY, anchor="m")
        text(s, x + 1.65, y, w - 1.95, 0.7, b, size=15, color=MUTED, anchor="m", spacing=0.98)


def s18_rq3(prs, num):
    s = chrome(prs, "RQ3: Agreement with the Fix-Informed Reference", num)
    text(s, 0.6, 1.35, 3.0, 1.0, "70.2%", size=54, bold=True, color=NAVY, anchor="m")
    text(s, 3.7, 1.4, 4.4, 0.9, "of pre-fix labels match the post-fix reference exactly", size=19, anchor="m", spacing=1.05)
    text(s, 8.2, 1.35, 4.53, 0.55, "95% CI [65.6, 74.9]", size=16, color=MUTED, anchor="m", align="r")
    label(s, 0.6, 2.45, 12.13, "All 410 bugs (scientific-open)")
    cx = 0.6
    for share, col, lab in [(0.702, POST, "exact match  70.2%"), (0.273, GOLD, "near miss  27.3%"), (0.024, PRE, "")]:
        w = 12.13 * share
        box(s, cx, 2.82, w, 0.72, fill=col)
        if lab:
            text(s, cx, 2.82, w, 0.72, lab, size=18, bold=True, color=WHITE, align="c", anchor="m")
        cx += w
    text(s, 0.6, 3.58, 9.6, 0.42, "near miss: one label is the other's alternative, or both share a family", size=15, color=MUTED, italic=True)
    text(s, 10.2, 3.58, 2.53, 0.42, "unrelated  2.4%", size=15, bold=True, color=PRE, align="r")
    label(s, 0.6, 4.3, 6.2, "Chance-corrected agreement")
    kappa_ruler(s, 0.6, 5.15, 6.2, 0.505)
    text(s, 0.6, 5.8, 6.2, 0.4, "few-shot reaches κ = 0.389 (fair)", size=15, color=MUTED, align="c")
    x, w = 7.4, 5.33
    label(s, x, 4.3, w, "Where the disagreement comes from")
    text(s, x, 4.68, w, 1.25, [[("Two fix-aware classifications agree only ", {}), ("76.3%", {"bold": True}),
        (" of the time. Pre-fix sits about 6 points below that ceiling; the rest is ODC boundary ambiguity.", {})]],
        size=17, spacing=1.08)
    box(s, x, 5.95, w, 0.72, fill=PANEL)
    text(s, x + 0.2, 5.95, 1.15, 0.72, "93.2%", size=22, bold=True, color=NAVY, anchor="m")
    text(s, x + 1.45, 5.95, w - 1.65, 0.72, "name the reference type as the label or as a recorded alternative",
         size=15, color=MUTED, anchor="m", spacing=1.03)


def s19_changes(prs, num):
    s = chrome(prs, "RQ3: How Labels Change When the Fix Is Visible", num)
    label(s, 0.6, 1.38, 7.6, "Pre-fix label (row)  →  post-fix label (column)")
    names = ["Checking", "Algorithm", "Assignment", "other types"]
    M = [[148, 37, 8, 5], [38, 119, 10, 8], [3, 2, 18, 5], [3, 2, 1, 3]]
    x0, y0, cw, ch, hw = 2.4, 2.35, 1.3, 0.78, 1.8
    for j, n in enumerate(names):
        text(s, x0 + j * cw, y0 - 0.44, cw, 0.4, n, size=15, bold=True, color=NAVY, align="c", anchor="m")
    for i, n in enumerate(names):
        y = y0 + i * ch
        text(s, x0 - hw - 0.12, y, hw, ch, n, size=15, bold=True, color=NAVY, align="r", anchor="m")
        for j, v in enumerate(M[i]):
            x = x0 + j * cw
            if i == j:
                fill, col, bold = PANEL2, INK, True
            elif v >= 30:
                fill, col, bold = NAVY, WHITE, True
            elif v >= 8:
                fill, col, bold = "9FB0C6", INK, True
            elif v > 0:
                fill, col, bold = "DEE4EC", MUTED, False
            else:
                fill, col, bold = WHITE, FAINT, False
            box(s, x + 0.03, y + 0.03, cw - 0.06, ch - 0.06, fill=fill, line=RULE if fill == WHITE else None)
            text(s, x, y, cw, ch, str(v) if v else "·", size=18 if v >= 8 else 16, bold=bold, color=col, align="c", anchor="m")
    for i in range(4):
        box(s, x0 + i * cw + 0.03, y0 + i * ch + 0.03, cw - 0.06, ch - 0.06, fill=None, line=POST, lw=1.75)
    text(s, 0.6, y0 + 4 * ch + 0.15, 7.6, 0.42, [[("outlined", {"bold": True, "color": POST}), ("  the label did not change        ", {"color": MUTED}),
        ("darker", {"bold": True, "color": NAVY}), ("  more bugs", {"color": MUTED})]], size=15)
    text(s, 0.6, y0 + 4 * ch + 0.6, 8.0, 0.45, "The two dark cells cancel out: 38 bugs move one way, 37 the other.", size=17)
    for i, (a, b) in enumerate([("29.8%", "of bugs change label (122 of 410)"), ("80.3%", "of changes stay in these three types"),
                                ("0.051", "total variation distance: the mix barely moves")]):
        y = 1.65 + i * 1.5
        text(s, 8.6, y, 4.13, 0.62, a, size=30, bold=True, color=NAVY)
        text(s, 8.6, y + 0.62, 4.13, 0.6, b, size=16, color=MUTED, spacing=1.03)
        if i < 2:
            line(s, 8.6, y + 1.3, 12.73, y + 1.3, color=RULE)
    note(s, "Algorithm/Method vs Checking is also the boundary that human raters confuse [22].")


def s20_rq4a(prs, num):
    s = chrome(prs, "RQ4a: Contribution of the ODC Taxonomy", num)
    # left: the free-form long tail
    text(s, 0.6, 1.35, 6.3, 0.55, [[("366", {"size": 30, "bold": True, "color": PRE}), ("  different labels", {"size": 19})]], size=19, anchor="m")
    text(s, 0.6, 1.9, 6.3, 0.4, "when the model writes its own (zero-free, 410 bugs)", size=15, color=MUTED)
    bx, by, bh = 0.95, 5.15, 2.3   # baseline y, max bar height
    line(s, bx - 0.25, by, 7.0, by, color=FAINT, width=1.0)
    for v in (5, 10, 15):
        yy = by - bh * v / 15
        line(s, bx - 0.25, yy, 7.0, yy, color=RULE)
        text(s, 0.6, yy - 0.16, 0.3, 0.32, str(v), size=13, color=FAINT, align="r")
    heads = [15, 4, 3, 3, 3, 3, 3] + [2] * 17
    bw, gap = 0.115, 0.045
    for i, v in enumerate(heads):
        h = bh * v / 15
        box(s, bx + i * (bw + gap), by - h, bw, h, fill=PRE if i == 0 else "C88585")
    tail_x = bx + len(heads) * (bw + gap) + 0.12
    tail_w = 7.0 - tail_x - 0.05
    box(s, tail_x, by - bh / 15, tail_w, bh / 15, fill="E3BEBE")
    line(s, tail_x, by + 0.18, tail_x + tail_w, by + 0.18, color=FAINT, width=1.0)
    text(s, tail_x - 0.6, by + 0.24, tail_w + 1.2, 0.4, "342 labels used exactly once", size=15, bold=True, color=PRE, align="c")
    text(s, bx - 0.35, by - bh - 0.42, 3.2, 0.4, "“Null Pointer Dereference”  15 bugs", size=15, color=MUTED)
    text(s, 0.6, 5.72, 6.5, 0.95, [[("The same bug (Chart_9), written twice:", {"color": MUTED, "size": 15})],
                                   [("“Improper input validation logic”", {"color": PRE})],
                                   [("“Incorrect boundary condition logic”", {"color": POST})]], size=16, after=1, spacing=1.05)
    # right: the taxonomy collapses them into six comparable buckets
    x, w = 7.6, 5.13
    text(s, x, 1.35, w, 0.55, [[("6", {"size": 30, "bold": True, "color": NAVY}), ("  comparable labels", {"size": 19})]], size=19, anchor="m")
    text(s, x, 1.9, w, 0.4, "with the ODC taxonomy (scientific-open)", size=15, color=MUTED)
    counts = [("CHK", 198), ("ALG", 175), ("ASN", 28), ("REL", 5), ("FCO", 3), ("INT", 1)]
    cx = x
    for k, n in counts:
        seg = w * n / 410
        box(s, cx, 2.4, max(seg, 0.03), 0.8, fill=T[k])
        if seg > 0.9:
            text(s, cx, 2.4, seg, 0.8, str(n), size=17, bold=True, color=WHITE, align="c", anchor="m")
        cx += seg
    text(s, x, 3.3, w, 0.4, "every bug lands in one of six buckets that can be counted", size=15, color=MUTED)
    table(s, x, 3.95, [("Condition", 2.6, "l"), ("Same label, both modes", 2.53, "r")],
          [("zero-free", [[("15.1%", {"color": PRE})]]), ("few-open", "66.6%"), ("scientific-open", "70.2%")],
          size=17, row_h=0.54, bold_cols=(0, 1))
    box(s, x, 6.3, 0.07, 0.55, fill=NAVY)
    text(s, x + 0.25, 6.3, w - 0.3, 0.55, "A fixed taxonomy lets us count anything at all.", size=17, anchor="m")


def s21_rq4b(prs, num):
    s = chrome(prs, "RQ4b: Contribution of the Scientific Loop", num)
    text(s, 0.6, 1.35, 5.0, 0.8, "Δκ = +0.115", size=38, bold=True, color=NAVY, anchor="m")
    text(s, 0.6, 2.15, 5.0, 0.5, [[("κ 0.389", {"color": MUTED}), ("  →  ", {}), ("0.505", {"bold": True, "color": NAVY})]], size=20)
    box(s, 0.6, 2.8, 5.3, 0.95, fill=POST_BG)
    text(s, 0.8, 2.8, 4.9, 0.95, [[("Statistically significant: ", {"bold": True, "color": POST})],
                                  [("95% CI [0.026, 0.208],  p ≈ 0.012  (paired bootstrap)", {})]], size=16, anchor="m", after=2)
    for i, (a, b) in enumerate([("6 of 6", "projects improve; sign test p = 0.016"),
                                ("p = 0.221", "McNemar on raw agreement: few-shot's 265 Algorithm labels inflate chance agreement"),
                                ("Closure", "smallest gain (+0.065); its interval still includes 0")]):
        y = 4.1 + i * 0.95
        line(s, 0.6, y - 0.05, 5.9, y - 0.05, color=RULE)
        text(s, 0.6, y, 1.45, 0.88, a, size=18, bold=True, anchor="m")
        text(s, 2.1, y, 3.8, 0.88, b, size=15, color=MUTED, anchor="m", spacing=1.0)
    cx, cw = 6.4, 6.33
    label(s, cx, 1.35, cw, "Per-project κ  ·  every project improves")
    base, top = 5.75, 2.25
    for v in (0.0, 0.25, 0.5, 0.75):
        yy = base - (base - top) * v / 0.75
        line(s, cx + 0.55, yy, cx + cw, yy, color=FAINT if v == 0 else RULE, width=0.75)
        text(s, cx, yy - 0.18, 0.48, 0.36, f"{v:.2f}", size=13, color=FAINT, align="r")
    data = [("Chart", 0.349, 0.672), ("Math", 0.537, 0.603), ("Lang", 0.497, 0.546),
            ("Mockito", 0.272, 0.499), ("Time", 0.212, 0.480), ("Closure", 0.294, 0.359)]
    gw = (cw - 0.7) / len(data)
    for i, (p_, few, sci) in enumerate(data):
        gx = cx + 0.7 + i * gw
        bwid = gw * 0.33
        hs = []
        for j, (v, col) in enumerate([(few, GREY_BAR), (sci, NAVY)]):
            h = (base - top) * v / 0.75
            box(s, gx + 0.12 + j * (bwid + 0.05), base - h, bwid, h, fill=col)
            hs.append(h)
        text(s, gx, base - max(hs) - 0.42, gw, 0.38, f"+{sci - few:.2f}", size=14, bold=True, color=POST, align="c")
        text(s, gx - 0.05, base + 0.06, gw, 0.38, p_, size=15, align="c")
    dumbbell_key(s, cx + 1.5, 6.25, [(GREY_BAR, "few-shot"), (NAVY, "scientific")])


def s22_mechanisms(prs, num):
    s = chrome(prs, "Qualitative Analysis of Thirteen Bugs", num)
    # left: how the pipeline goes wrong
    label(s, 0.6, 1.4, 5.9, "Failure modes we found")
    modes = [("Symptom-site bias", "Chart_17", "the label follows where the exception surfaced"),
             ("Bug-report anchoring", "Math_90", "a fix suggested in the report becomes the label"),
             ("Surface syntax", "Math_23", "the post-fix label follows the patch shape"),
             ("Underdetermined", "Lang_20", "two valid fixes imply two ODC types")]
    for i, (m, b, d) in enumerate(modes):
        y = 1.88 + i * 1.12
        box(s, 0.6, y, 0.06, 0.92, fill=PRE)
        text(s, 0.85, y, 3.6, 0.42, m, size=18, bold=True)
        text(s, 4.4, y, 1.75, 0.42, b, size=15, font=MONO, color=NAVY, align="r", anchor="m")
        text(s, 0.85, y + 0.42, 5.3, 0.45, d, size=16, color=MUTED)
    # right: the developer's repair choice
    x, w = 6.95, 5.78
    label(s, x, 1.4, w, "Where the developer had a choice")
    cards = [("Math_90", "a Comparable check (CHK)", "a typed overload (INT)"),
             ("Math_17", "a range check (CHK)", "both: check + fallback"),
             ("Time_3", "better arithmetic (ALG)", "amount != 0 guards (CHK)"),
             ("Lang_20", "a null check (CHK)", "a new capacity (ASN)")]
    for i, (bug, avail, chose) in enumerate(cards):
        y = 1.88 + i * 1.12
        box(s, x, y, w, 0.92, fill=PANEL)
        text(s, x + 0.2, y + 0.04, 1.5, 0.4, bug, size=15, font=MONO, bold=True, color=NAVY, anchor="m")
        text(s, x + 1.75, y + 0.02, w - 1.95, 0.42, [[("could have been  ", {"color": FAINT, "size": 14}), (avail, {"color": MUTED})]], size=15, anchor="m")
        text(s, x + 1.75, y + 0.46, w - 1.95, 0.42, [[("developer chose  ", {"color": FAINT, "size": 14}), (chose, {"bold": True})]], size=15, anchor="m")
    keyline(s, 6.4, [[("It records the repair chosen — for ", {}), ("77%", {"bold": True, "color": NAVY}),
                      (" of changed labels that type is already a recorded alternative.", {})]], h=0.5)


def s23_threats(prs, num):
    s = chrome(prs, "Threats to Validity", num)
    rows = [("Internal", "non-deterministic output; evidence sanitized against fix leakage"),
            ("Construct", "agreement is a proxy; the modified class is absent for 285 of 410 bugs"),
            ("External", "6 of 17 projects; corpus results from one model; Java only"),
            ("Conclusion", "one run per condition; resampled values are estimates; a single rater for 13 bugs"),
            ("Other", "possible pre-training exposure; confidence fields are not a usable signal")]
    for i, (a, b) in enumerate(rows):
        y = 1.45 + i * 1.04
        box(s, 0.6, y + 0.1, 2.45, 0.76, fill=PANEL)
        text(s, 0.6, y + 0.1, 2.45, 0.76, a, size=20, bold=True, color=NAVY, align="c", anchor="m")
        text(s, 3.3, y, 9.43, 0.95, b, size=18, anchor="m", spacing=1.05)
        line(s, 0.6, y + 0.99, 12.73, y + 0.99, color=RULE)
    note(s, "Each threat is stated in the book together with the mitigation applied.")


def s24_conclusion(prs, num):
    s = chrome(prs, "Conclusion and Future Work", num)
    for i, (a, b) in enumerate([("97.8%", "three types (RQ1)"), ("0 of 1,640", "“Other” (RQ2)"),
                                ("70.2%", "pre-fix match (RQ3)"), ("+0.115", "Δκ from the loop (RQ4)")]):
        x = 0.6 + i * 3.1
        box(s, x, 1.4, 2.9, 0.07, fill=NAVY)
        text(s, x, 1.58, 2.9, 0.8, a, size=36, bold=True, color=NAVY, anchor="m")
        text(s, x, 2.38, 2.9, 0.42, b, size=16, color=MUTED)
    label(s, 0.6, 3.02, 5.9, "Contributions", color=NAVY, size=20)
    bullets(s, 0.6, 3.5, 5.9, 3.0, ["A taxonomy × strategy condition space", "An enforced loop with auditable transcripts",
                                    "Evaluation without ground truth", "410 bugs, analysed with two LLMs"], size=19, after=20)
    label(s, 6.95, 3.02, 5.78, "Future work", color=NAVY, size=20)
    bullets(s, 6.95, 3.5, 5.78, 3.0, ["Human reference labels for a sample", "Grade the reasoning, not only the label",
                                      "Full corpus, more models, consensus", "Impact, Trigger and Age attributes"], size=19, after=20)


REFS = [
    "[1] G. Catolino et al., “Not All Bugs Are the Same: Understanding, Characterizing, and Classifying Bug Types,” Journal of Systems and Software, vol. 152, 2019.",
    "[2] T. Hirsch and B. Hofer, “Using Textual Bug Reports to Predict the Fault Category of Software Bugs,” Array, vol. 15, 2022.",
    "[3] R. Andrade et al., “An Empirical Study on the Classification of Bug Reports with Machine Learning,” arXiv preprint, 2025.",
    "[4] R. Chillarege et al., “Orthogonal Defect Classification – A Concept for In-Process Measurements,” IEEE Transactions on Software Engineering, vol. 18, no. 11, 1992.",
    "[5] R. Just, D. Jalali, and M. D. Ernst, “Defects4J: A Database of Existing Faults to Enable Controlled Testing Studies for Java Programs,” Proc. International Symposium on Software Testing and Analysis (ISSTA), 2014.",
    "[6] M. N. Rafi et al., “Revisiting Defects4J for Fault Localization in Diverse Development Scenarios,” IEEE/ACM 22nd International Conference on Mining Software Repositories (MSR), 2025.",
    "[7] M. Martinez et al., “Automatic Repair of Real Bugs in Java: A Large-Scale Experiment on the Defects4J Dataset,” Empirical Software Engineering, vol. 22, no. 4, 2017.",
    "[8] A. Van der Spuy and B. Fischer, “An Anatomy of 488 Faults from Defects4J Based on the Control- and Data-Flow Graph Representations of Programs,” Proc. 29th International Conference on Evaluation and Assessment in Software Engineering (EASE), 2025.",
    "[9] V. Sobreira et al., “Dissection of a Bug Dataset: Anatomy of 395 Patches from Defects4J,” IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER), 2018.",
    "[10] J. Jiang, Y. Xiong, and X. Xia, “A Manual Inspection of Defects4J Bugs and Its Implications for Automatic Program Repair,” Science China Information Sciences, vol. 62, no. 10, 2019.",
    "[11] G. Colavito et al., “Large Language Models for Issue Report Classification,” Ital-IA 2024 Thematic Workshops, CEUR Workshop Proceedings, vol. 3762, 2024.",
    "[12] A. Koyuncu, “Exploring Fine-Grained Bug Report Categorization with Large Language Models and Prompt Engineering: An Empirical Study,” ACM Transactions on Software Engineering and Methodology, vol. 35, no. 3, 2026.",
    "[13] Y. Nong et al., “Chain-of-Thought Prompting of Large Language Models for Discovering and Fixing Software Vulnerabilities,” arXiv preprint, 2024.",
    "[14] C. Li et al., “KnowBug: Enhancing Large Language Models with Bug Report Knowledge for Deep Learning Framework Bug Prediction,” Knowledge-Based Systems, vol. 305, 2024.",
    "[15] IBM, “Orthogonal Defect Classification v5.2 for Software Design and Code,” IBM Research, 2013.",
    "[16] X. Du et al., “LLM-BRC: A Large Language Model-Based Bug Report Classification Framework,” Software Quality Journal, vol. 32, no. 3, 2024.",
    "[17] S. Kang et al., “Explainable Automated Debugging via Large Language Model-driven Scientific Debugging,” Empirical Software Engineering, vol. 30, no. 2, 2025.",
    "[18] S. Kang, G. An, and S. Yoo, “A Quantitative and Qualitative Evaluation of LLM-Based Explainable Fault Localization,” Proc. ACM on Software Engineering, vol. 1, no. FSE, 2024.",
    "[19] L. Huang et al., “AutoODC: Automated Generation of Orthogonal Defect Classifications,” Automated Software Engineering, vol. 22, no. 1, 2015.",
    "[20] F. Thung, D. Lo, and L. Jiang, “Automatic Defect Categorization,” Proc. 19th Working Conference on Reverse Engineering (WCRE), 2012.",
    "[21] A. M. Esfahani, N. Kahani, and S. A. Ajila, “Understanding Defects in Generated Codes by Language Models,” 34th International Conference on Collaborative Advances in Software and Computing (CASCON), 2024.",
    "[22] K. Henningsson and C. Wohlin, “Assuring Fault Classification Agreement – An Empirical Evaluation,” Proc. 2004 International Symposium on Empirical Software Engineering (ISESE), 2004.",
    "[23] J. Hernández-González et al., “Learning to Classify Software Defects from Crowds: A Novel Approach,” Applied Soft Computing, vol. 62, 2018.",
    "[24] K. El Emam and I. Wieczorek, “The Repeatability of Code Defect Classifications,” Proc. Ninth International Symposium on Software Reliability Engineering (ISSRE), 1998.",
    "[25] A. Rahman and E. Farhana, “An Exploratory Characterization of Bugs in COVID-19 Software Projects,” arXiv preprint, 2020.",
    "[26] J. Agnelo, N. Laranjeiro, and J. Bernardino, “Using Orthogonal Defect Classification to Characterize NoSQL Database Defects,” Journal of Systems and Software, vol. 159, 2020.",
    "[27] J. R. Landis and G. G. Koch, “The Measurement of Observer Agreement for Categorical Data,” Biometrics, vol. 33, no. 1, 1977.",
    "[28] S. Baltes et al., “Guidelines for Empirical Studies in Software Engineering involving Large Language Models,” Empirical Software Engineering, 2026.",
]


def refs_slide(prs, num, part, total_parts, items):
    s = new_slide(prs)
    title_bar(s, f"References ({part}/{total_parts})")
    text(s, 0.6, 1.42, 12.13, 5.45, items, size=14, after=9, spacing=1.04)
    line(s, 0.6, 7.0, 12.73, 7.0, color=RULE, width=0.75)
    page_number(s, num)


def closing_slide(prs, num):
    s = new_slide(prs)
    box(s, 0, 0, SW, 0.12, fill=NAVY)
    logo(s, 0.8, 1.9, 2.3)
    line(s, 2.6, 2.0, 2.6, 4.1, color=RULE, width=1.0)
    text(s, 2.95, 1.95, 9.5, 1.0, "Thank you", size=48, bold=True, color=NAVY)
    text(s, 2.95, 2.95, 9.5, 0.6, "Questions and discussion", size=26)
    text(s, 2.95, 3.65, 9.5, 0.5, "Orthogonal Defect Classification on Defects4J Using an LLM-Driven Scientific Approach", size=17, color=MUTED)
    text(s, 2.95, 4.7, 9.5, 0.5, "Md. Sakib Hossain  ·  Mohammad Nahiyan Kabir  ·  Hasin Mahtab Alvee", size=17)
    box(s, 0, 7.38, SW, 0.12, fill=NAVY)
    page_number(s, num)


def build():
    prs = Presentation(str(DECK))
    ids = prs.slides._sldIdLst
    for sid in list(ids):
        prs.part.drop_rel(sid.rId)
        ids.remove(sid)
    s01_title(prs)
    order = [s02_outline, s03_motivation, s04_odc, s05_related, s06_problem, s07_idea, s08_rqs,
             s09_pipeline, s10_evidence, s11_conditions, s12_prompts, s13_loop, s14_eval, s15_reference, s16_setup,
             s17_rq12, s18_rq3, s19_changes, s20_rq4a, s21_rq4b, s22_mechanisms, s23_threats, s24_conclusion]
    for i, fn in enumerate(order, start=2):
        fn(prs, i)
    chunks = [REFS[:10], REFS[10:19], REFS[19:]]
    for i, chunk in enumerate(chunks):
        refs_slide(prs, 25 + i, i + 1, len(chunks), chunk)
    closing_slide(prs, 28)
    prs.save(str(DECK))
    print(f"wrote {DECK.name}: {len(prs.slides)} slides")


if __name__ == "__main__":
    build()

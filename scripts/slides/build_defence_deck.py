"""Build the thesis defence slide deck.

Writes ONLY to the Defence copy:
  iut_submissions/presentation/Defence/SWE_..._presentation.pptx
The pre-defence files are never touched.

All content comes from the finalized defence book (latex/defence book/main.tex);
the reference list and its numbering follow the book's bibliography — 29 entries
are cited, in order of first citation.

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
GOLD_BG = "FBF1DF"
BLUE, BLUE_BG = "2F5D9B", "E4ECF7"
PURPLE, PURPLE_BG = "5B4B9A", "ECE8F6"
TEAL, TEAL_BG = "2B7F72", "E0F0ED"
GREY_BAR = "B3B9C3"
# Muted ODC type colours, used only inside figures.
T = {"CHK": "C07A2C", "ALG": "2F5D9B", "ASN": "6D4C9A", "TIM": "8A9199",
     "FCO": "9B3D4E", "INT": "2B7F72", "REL": "8A6E52"}
TYPE_NAME = {"ALG": "Algorithm/Method", "ASN": "Assignment/Initialization", "CHK": "Checking",
             "TIM": "Timing/Serialization", "FCO": "Function/Class/Object",
             "INT": "Interface/O-O Messages", "REL": "Relationship"}

SANS = "Source Sans 3"
MONO = "Source Code Pro"
SECTIONS = [("Context", 2, 7), ("Methodology", 8, 15), ("Results", 16, 24)]


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
    paras = [[("▪  ", {"color": NAVY, "size": size - 4})] + (it if isinstance(it, list) else [(it, {})]) for it in items]
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
    if value is None:
        return
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
    bullets(s, 0.6, 2.9, 6.0, 2.9, ["A standard benchmark for debugging research [6, 7]",
                                    "Defect types need different debugging strategies [1]",
                                    "Manual triage is accurate, but does not scale [3]",
                                    [("LLMs can read all this evidence — ", {}), ("but should they answer at once, or investigate?", {"bold": True, "color": NAVY})]],
            size=17, after=12)
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
    for k, (a, b, col) in enumerate([("LLM classifiers [11–14, 16]", "read report text only; without a fixed taxonomy, labels drift", BLUE),
                                     ("ODC studies [19–21]", "classify other corpora, never Defects4J at scale", TEAL),
                                     ("Scientific debugging [17, 18]", "hypothesis → experiment loops, used to find faults, not to type them", PURPLE)]):
        x = 0.6 + k * 4.1
        box(s, x, 4.6, 3.9, 0.06, fill=col)
        text(s, x, 4.72, 3.9, 1.15, [[(a, {"bold": True, "color": col})], [(b, {"color": MUTED, "size": 15})]], size=17, spacing=1.03, after=3)
    keyline(s, 5.98, "Gap: no semantic defect types for Defects4J, no way to evaluate them, and no test of whether investigating helps.", h=0.6)


def s06_problem(prs, num):
    s = chrome(prs, "Problem Statement", num)
    box(s, 0.6, 1.45, 0.07, 1.2, fill=NAVY)
    text(s, 0.95, 1.4, 11.7, 1.3, [[("Classify Defects4J bugs into ODC defect types ", {}),
        ("from pre-fix evidence alone", {"bold": True, "color": NAVY}), (" — and evaluate that classification ", {}),
        ("without ground-truth labels.", {"bold": True, "color": NAVY})]], size=24, anchor="m", spacing=1.08)
    label(s, 0.6, 2.9, 12.13, "A solution has to be …   →   how we meet it")
    reqs = [("Context-aware", "code, tests, traces, report", "one case file per bug", BLUE),
            ("Semantic", "mechanism, not syntax", "ODC defect type", BLUE),
            ("Taxonomy-constrained", "a fixed, comparable label space", "7 ODC types", PURPLE),
            ("Open to its own limits", "can say a bug does not fit", "“Other” + justification", PURPLE),
            ("Scalable", "no manual labelling", "LLM strategies", PURPLE),
            ("Evaluable", "brings its own reference", "post-fix reference", TEAL)]
    for i, (a, b, ans, col) in enumerate(reqs):
        x = 0.6 + (i % 2) * 6.2
        y = 3.3 + (i // 2) * 1.15
        box(s, x, y, 5.93, 1.0, fill=PANEL)
        text(s, x + 0.2, y + 0.06, 3.3, 0.45, a, size=19, bold=True, color=NAVY, anchor="m")
        text(s, x + 0.2, y + 0.5, 3.3, 0.42, b, size=15, color=MUTED, anchor="m")
        text(s, x + 3.35, y, 0.35, 1.0, "→", size=20, color=FAINT, align="c", anchor="m")
        box(s, x + 3.72, y + 0.24, 2.05, 0.52, fill=col)
        text(s, x + 3.72, y + 0.24, 2.05, 0.52, ans, size=14, bold=True, color=WHITE, align="c", anchor="m")


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
    for i, (a, b) in enumerate([("Post-fix label", "the reference answer"), ("Pre-fix vs post-fix", "does the triage label hold?"), ("Labels differ", "drift")]):
        x = 0.6 + i * 4.15
        line(s, x, 5.35, x + 3.85, 5.35, color=NAVY, width=1.25)
        text(s, x, 5.42, 3.85, 0.42, a, size=19, bold=True, color=NAVY)
        text(s, x, 5.85, 3.85, 0.42, [[("= ", {"color": FAINT}), (b, {})]], size=17)
    note(s, "Agreement is not correctness: we measure how closely a pre-fix label reproduces a better-informed reference.")


def s08_rqs(prs, num):
    s = chrome(prs, "Research Questions", num)
    rqs = [("RQ1", "Distribution", "Which ODC types dominate, and does the mix differ by project?", "p. 16", BLUE),
           ("RQ2", "Coverage", "Do the seven types cover every bug, or is “Other” needed?", "p. 16", TEAL),
           ("RQ3", "Accuracy", "How often does the pre-fix label match the post-fix reference?", "pp. 17–18", GOLD),
           ("RQ4a", "Taxonomy", "What does the ODC taxonomy add over the model’s own words?", "p. 19", PURPLE),
           ("RQ4b", "Scientific strategy", "What does the scientific strategy add over a strong few-shot prompt?", "pp. 20–22", POST)]
    for i, (k, n, q, pg, col) in enumerate(rqs):
        y = 1.42 + i * 1.08
        box(s, 0.6, y + 0.1, 1.25, 0.8, fill=col)
        text(s, 0.6, y + 0.1, 1.25, 0.8, k, size=21, bold=True, color=WHITE, align="c", anchor="m")
        text(s, 2.1, y + 0.08, 9.0, 0.44, n, size=21, bold=True, color=NAVY)
        text(s, 2.1, y + 0.52, 9.0, 0.44, q, size=17, color=MUTED)
        text(s, 11.2, y + 0.1, 1.53, 0.8, pg, size=15, color=col, bold=True, align="r", anchor="m")
        if i < 4:
            line(s, 0.6, y + 1.03, 12.73, y + 1.03, color=RULE)


def rbox(s, x, y, w, h, fill=WHITE, line_col=NAVY, lw=1.25):
    b = box(s, x, y, w, h, fill=fill, line=line_col, lw=lw, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    b.adjustments[0] = min(0.12, 0.08 / max(min(w, h), 0.1))
    return b


def node(s, x, y, w, h, runs, fill=WHITE, line_col=NAVY, size=14, color=INK, bold=False, lw=1.0):
    rbox(s, x, y, w, h, fill=fill, line_col=line_col, lw=lw)
    text(s, x + 0.05, y, w - 0.1, h, runs, size=size, color=color, bold=bold, align="c", anchor="m", spacing=0.95)


def s09_pipeline(prs, num):
    s = chrome(prs, "Pipeline Overview", num)
    cols = [(0.6, 3.45, "1  Preprocessing", BLUE), (4.4, 5.05, "2  Classification", PURPLE), (9.8, 2.93, "3  Evaluation", TEAL)]
    for x, w, t_, col in cols:
        rbox(s, x, 1.35, w, 0.42, fill=col, line_col=col)
        text(s, x, 1.35, w, 0.42, t_, size=17, bold=True, color=WHITE, align="c", anchor="m")
    # ── Preprocessing
    x, w = 0.6, 3.45
    node(s, x, 1.95, w, 0.72, [[("Defects4J v3.0.1", {"bold": True, "color": BLUE, "size": 16})],
                               [("17 Java projects  ·  836 bugs", {"color": MUTED})]], line_col=BLUE, fill=BLUE_BG)
    line(s, x + w / 2, 2.67, x + w / 2, 2.87, color=BLUE, width=1.5, arrow=True)
    rbox(s, x, 2.9, w, 1.92, line_col=BLUE)
    text(s, x, 2.95, w, 0.36, "Collect, per bug", size=15, bold=True, color=BLUE, align="c", anchor="m")
    for i, (t_, col) in enumerate([("Bug report", BLUE), ("Failing tests + stack traces", PRE), ("Suspicious frames + code snippets", GOLD),
                                   ("Coverage (optional)", TEAL), ("Fix diff: buggy → fixed", POST)]):
        yy = 3.33 + i * 0.29
        box(s, x + 0.2, yy + 0.07, 0.15, 0.15, fill=col)
        text(s, x + 0.45, yy, w - 0.5, 0.29, t_, size=14, anchor="m")
    line(s, x + w / 2, 4.82, x + w / 2, 5.02, color=BLUE, width=1.5, arrow=True)
    rbox(s, x, 5.05, w, 1.75, fill=PANEL, line_col=BLUE)
    text(s, x, 5.1, w, 0.36, [[("context.json", {"font": MONO, "bold": True, "color": BLUE}), ("  one case file", {"color": MUTED, "size": 14})]],
         size=15, align="c", anchor="m")
    node(s, x + 0.15, 5.5, w - 0.3, 0.38, [[("Pre-fix  ", {"bold": True, "color": PRE}), ("symptoms, sanitised", {})]], line_col=PRE, fill=PRE_BG)
    node(s, x + 0.15, 5.95, w - 0.3, 0.38, [[("Post-fix  ", {"bold": True, "color": POST}), ("symptoms + fix diff", {})]], line_col=POST, fill=POST_BG)
    text(s, x, 6.37, w, 0.36, "modified classes = hidden oracle", size=14, color=GOLD, bold=True, align="c", anchor="m")
    line(s, 4.05, 5.9, 4.38, 5.9, color=NAVY, width=1.75, arrow=True)
    # ── Classification
    x, w = 4.4, 5.05
    node(s, x, 1.95, 2.45, 0.5, [[("LLM  ", {"bold": True, "color": PURPLE}), ("Gemini · gpt-5-mini", {})]], line_col=PURPLE, fill=PURPLE_BG)
    node(s, x + 2.6, 1.95, 2.45, 0.5, [[("ODC  ", {"bold": True, "color": PURPLE}), ("7 types + “Other”", {})]], line_col=PURPLE, fill=PURPLE_BG)
    # single-call lane
    fx, fw = x, 1.55
    rbox(s, fx, 2.6, fw, 3.35, line_col=RULE, fill=WHITE)
    text(s, fx, 2.64, fw, 0.34, "single call", size=15, bold=True, color=BLUE, align="c", anchor="m")
    node(s, fx + 0.1, 3.0, fw - 0.2, 0.45, "Evidence summary", size=13)
    line(s, fx + fw / 2, 3.45, fx + fw / 2, 3.57, color=NAVY, width=1.25, arrow=True)
    node(s, fx + 0.1, 3.6, fw - 0.2, 0.55, [[("zero-shot", {"bold": True, "color": FAINT})], "own words"], size=13, line_col=FAINT)
    text(s, fx, 4.15, fw, 0.22, "or", size=12, color=MUTED, italic=True, align="c", anchor="m")
    node(s, fx + 0.1, 4.37, fw - 0.2, 0.55, [[("few-shot", {"bold": True, "color": BLUE})], "+ 5 examples"], size=13, line_col=BLUE, fill=BLUE_BG)
    line(s, fx + fw / 2, 4.92, fx + fw / 2, 5.32, color=NAVY, width=1.25, arrow=True)
    text(s, fx + fw / 2 + 0.05, 4.98, 0.7, 0.3, "1 call", size=12, color=MUTED, italic=True, anchor="m")
    node(s, fx + 0.1, 5.35, fw - 0.2, 0.45, "Label", size=14, bold=True, color=POST, fill=POST_BG, line_col=POST)
    # scientific lane
    sx, sw = x + 1.65, 3.4
    rbox(s, sx, 2.6, sw, 3.35, line_col=PURPLE, fill=WHITE, lw=1.5)
    text(s, sx, 2.64, sw, 0.34, "scientific: enforced loop", size=15, bold=True, color=PURPLE, align="c", anchor="m")
    mx, mw = sx + 0.12, 1.85
    node(s, mx, 3.0, mw, 0.42, "Evidence summary", size=14)
    line(s, mx + mw / 2, 3.42, mx + mw / 2, 3.55, color=NAVY, width=1.25, arrow=True)
    node(s, mx, 3.58, mw, 0.55, ["Hypothesis", "+ prediction"], size=14, bold=True, color=PURPLE, fill=PURPLE_BG, line_col=PURPLE)
    line(s, mx + mw / 2, 4.13, mx + mw / 2, 4.3, color=NAVY, width=1.25, arrow=True)
    node(s, mx, 4.33, mw, 0.45, "Enough evidence?", size=14, fill=GOLD_BG, line_col=GOLD, bold=True, color=GOLD)
    line(s, mx + mw / 2, 4.78, mx + mw / 2, 5.32, color=POST, width=1.25, arrow=True)
    text(s, mx + mw / 2 + 0.05, 4.86, 0.6, 0.3, "yes", size=14, color=POST, bold=True, anchor="m")
    node(s, mx, 5.35, mw, 0.45, "Conclude", size=14, bold=True, color=POST, fill=POST_BG, line_col=POST)
    px, pw = mx + mw + 0.32, sw - mw - 0.56
    node(s, px, 4.33, pw, 0.45, "Probe", size=14, bold=True, color=BLUE, fill=BLUE_BG, line_col=BLUE)
    line(s, mx + mw, 4.555, px, 4.555, color=NAVY, width=1.25, arrow=True)
    text(s, mx + mw - 0.02, 4.3, 0.36, 0.22, "no", size=13, color=MUTED, bold=True, align="c", anchor="m")
    line(s, px + pw / 2, 4.33, px + pw / 2, 4.16, color=NAVY, width=1.25, arrow=True)
    node(s, px, 3.58, pw, 0.55, "Observe", size=14, color=BLUE, fill=BLUE_BG, line_col=BLUE)
    line(s, px, 3.855, mx + mw, 3.855, color=NAVY, width=1.25, arrow=True)
    text(s, px - 0.05, 4.92, pw + 0.1, 0.8, ["max 6 turns,", "then forced", "conclusion"], size=13, color=MUTED, italic=True, align="c", spacing=0.95)
    # output
    line(s, fx + fw / 2, 5.8, fx + fw / 2, 6.1, color=NAVY, width=1.25, arrow=True)
    line(s, mx + mw / 2, 5.8, mx + mw / 2, 6.1, color=NAVY, width=1.25, arrow=True)
    node(s, x, 6.12, w, 0.68, [[("classification.json", {"font": MONO, "bold": True, "color": PURPLE})],
                               [("ODC label  ·  alternative types  ·  reasoning transcript", {"color": MUTED})]], size=14, fill=PANEL, line_col=PURPLE)
    line(s, 9.45, 6.46, 9.62, 6.46, color=NAVY, width=1.75)
    line(s, 9.62, 6.46, 9.62, 2.45, color=NAVY, width=1.75)
    line(s, 9.62, 2.45, 9.78, 2.45, color=NAVY, width=1.75, arrow=True)
    # ── Evaluation
    x, w = 9.8, 2.93
    rbox(s, x, 1.95, w, 1.12, line_col=TEAL, fill=TEAL_BG)
    text(s, x, 1.97, w, 0.34, "Compare labels", size=15, bold=True, color=TEAL, align="c", anchor="m")
    for i, t_ in enumerate(["pre-fix vs post-fix: 4 tiers", "scientific vs few-shot", "manual reading: 13 bugs"]):
        text(s, x + 0.1, 2.3 + i * 0.25, w - 0.2, 0.25, t_, size=14, color=INK, align="c", anchor="m")
    line(s, x + w / 2, 3.07, x + w / 2, 3.2, color=TEAL, width=1.5, arrow=True)
    rbox(s, x, 3.22, w, 2.03, line_col=TEAL)
    text(s, x, 3.25, w, 0.34, "Research questions", size=15, bold=True, color=TEAL, align="c", anchor="m")
    for i, (a, b, col) in enumerate([("RQ1", "type distribution", BLUE), ("RQ2", "taxonomy coverage", TEAL), ("RQ3", "pre-fix accuracy", GOLD),
                                     ("RQ4a", "taxonomy's value", PURPLE), ("RQ4b", "scientific vs few-shot", POST)]):
        yy = 3.6 + i * 0.32
        box(s, x + 0.15, yy + 0.03, 0.62, 0.26, fill=col)
        text(s, x + 0.15, yy + 0.03, 0.62, 0.26, a, size=12, bold=True, color=WHITE, align="c", anchor="m")
        text(s, x + 0.85, yy, w - 0.9, 0.32, b, size=14, anchor="m")
    line(s, x + w / 2, 5.25, x + w / 2, 5.4, color=TEAL, width=1.5, arrow=True)
    rbox(s, x, 5.42, w, 1.38, fill=PANEL, line_col=TEAL)
    text(s, x, 5.45, w, 0.34, "Outputs", size=15, bold=True, color=TEAL, align="c", anchor="m")
    for i, t_ in enumerate(["ODC labels with transcripts", "Statistics and result tables", "Code, prompts and data"]):
        yy = 5.8 + i * 0.32
        dot(s, x + 0.2, yy + 0.11, 0.1, TEAL)
        text(s, x + 0.38, yy, w - 0.45, 0.32, t_, size=14, anchor="m")


def s10_evidence(prs, num):
    s = chrome(prs, "Evidence Collection: One Case File per Bug", num)
    # 0. the bug
    box(s, 0.6, 1.8, 1.65, 2.45, fill=NAVY)
    text(s, 0.6, 1.8, 1.65, 2.45, [[("Defects4J", {"size": 15, "bold": False})], "bug",
                                   [("", {"size": 8})], [("buggy version", {"size": 14, "bold": False})],
                                   [("fixed version", {"size": 14, "bold": False})], [("issue link", {"size": 14, "bold": False})]],
         size=21, bold=True, color=WHITE, align="c", anchor="m", spacing=1.0)
    line(s, 2.3, 3.02, 2.7, 3.02, color=NAVY, width=1.75, arrow=True)
    # 1. collect
    label(s, 2.75, 1.4, 5.05, "1 · Collect")
    rows = [("Bug report", "fetched from the issue tracker"),
            ("Failing tests", "buggy version run: error + trace"),
            ("Suspicious frames", "trace lines in the project’s own code"),
            ("Code snippets", "±12 lines of code, ±18 of tests"),
            ("Coverage", "line and branch data (optional)")]
    for r, (a, b) in enumerate(rows):
        y = 1.8 + r * 0.5
        box(s, 2.75, y, 5.05, 0.43, fill=PANEL)
        text(s, 2.9, y, 1.8, 0.43, a, size=15, bold=True, color=NAVY, anchor="m")
        text(s, 4.7, y, 3.08, 0.43, b, size=14, color=MUTED, anchor="m", spacing=0.95)
    line(s, 7.85, 3.02, 8.2, 3.02, color=NAVY, width=1.75, arrow=True)
    # 2. store
    x, w = 8.25, 4.48
    label(s, x, 1.4, w, "2 · Store: context.json")
    bands = [(PANEL2, NAVY, "Evidence", "cleaned and deduplicated; shown to the model"),
             (GOLD_BG, GOLD, "Hidden oracle", "modified classes; for evaluation only"),
             (POST_BG, POST, "Fix diff", "buggy → fixed code; post-fix only")]
    for r, (bg, col, a, b) in enumerate(bands):
        y = 1.8 + r * 0.83
        box(s, x, y, w, 0.76, fill=bg)
        box(s, x, y, 0.07, 0.76, fill=col)
        text(s, x + 0.25, y + 0.02, w - 0.35, 0.36, a, size=16, bold=True, color=col, anchor="m")
        text(s, x + 0.25, y + 0.37, w - 0.35, 0.36, b, size=14, color=INK, anchor="m")
    # 3. two case files
    label(s, 0.6, 4.5, 12.13, "3 · Build two case files  ·  the only difference is the fix diff")
    for c, (col, bg, a, b, c2) in enumerate([
            (PRE, PRE_BG, "Pre-fix case file", "evidence only; fix hints removed from the report and metadata", "→ the label we evaluate"),
            (POST, POST_BG, "Post-fix case file", "the same evidence + the fix diff", "→ the reference label")]):
        x = 0.6 + c * 6.2
        box(s, x, 4.88, 5.93, 1.02, fill=bg)
        box(s, x, 4.88, 0.07, 1.02, fill=col)
        text(s, x + 0.25, 4.92, 3.2, 0.42, a, size=18, bold=True, color=col, anchor="m")
        text(s, x + 3.2, 4.92, 2.6, 0.42, c2, size=16, bold=True, color=col, anchor="m", align="r")
        text(s, x + 0.25, 5.36, 5.55, 0.48, b, size=15, color=INK, anchor="m")
    # who reads it
    box(s, 0.6, 6.08, 12.13, 0.74, fill=PANEL)
    text(s, 0.8, 6.08, 11.8, 0.74,
         [[("Every strategy and both LLMs read the same file.  ", {"bold": True, "color": NAVY}),
           ("few-shot", {"bold": True}), (" reads the evidence summary once;  ", {"color": MUTED}),
           ("scientific", {"bold": True}), (" reads the same summary, then probes for the held-back rest.", {"color": MUTED})]],
         size=15, anchor="m")


def s11_conditions(prs, num):
    s = chrome(prs, "Classification Conditions and Models", num)
    text(s, 0.6, 1.3, 12.13, 0.42, [[("A condition = ", {"color": MUTED}), ("taxonomy", {"bold": True}), (" (which labels)  ×  ", {"color": MUTED}),
                                     ("strategy", {"bold": True}), (" (how it reasons),  run by an ", {"color": MUTED}),
                                     ("LLM", {"bold": True}), (".", {"color": MUTED})]], size=17, anchor="m")
    gx, gy, cw, ch = 2.35, 1.95, 1.62, 0.95
    label(s, gx, gy, cw * 3, "Taxonomy", align="c")
    cols = [("free", "own words"), ("closed", "7 ODC types"), ("open", "7 types + “Other”")]
    for ci, (c, d) in enumerate(cols):
        text(s, gx + ci * cw, gy + 0.35, cw, 0.62, [c, [(d, {"size": 14, "bold": False, "color": MUTED})]],
             size=17, bold=True, align="c", anchor="m", spacing=0.95)
    text(s, 0.6, gy + 0.35, 1.7, 0.62, "STRATEGY", size=14, bold=True, color=MUTED, anchor="m")
    line(s, 0.6, gy + 1.02, gx + 3 * cw, gy + 1.02, color=NAVY, width=1.25)
    rows = [("zero", "plain prompt"), ("few", "worked examples"), ("scientific", "hypothesis → probe")]
    used = {("zero", "free"): PANEL2, ("few", "open"): PANEL2, ("scientific", "open"): NAVY,
            ("few", "closed"): PANEL2, ("scientific", "closed"): PANEL2}
    defined = set()
    for ri, (r, d) in enumerate(rows):
        y = gy + 1.07 + ri * ch
        text(s, 0.6, y, 1.75, ch, [r, [(d, {"size": 14, "bold": False, "color": MUTED})]], size=17, bold=True, anchor="m", spacing=0.95)
        for ci, (c, _) in enumerate(cols):
            x = gx + ci * cw
            if (r, c) in used:
                fill = used[(r, c)]
                box(s, x + 0.07, y + 0.08, cw - 0.14, ch - 0.16, fill=fill)
                runs = [f"{r}-{c}"] + ([[("default", {"size": 13, "bold": False})]] if fill == NAVY else [])
                text(s, x + 0.07, y + 0.08, cw - 0.14, ch - 0.16, runs, size=15, bold=True,
                     color=WHITE if fill == NAVY else NAVY, align="c", anchor="m", spacing=0.95)
            elif (r, c) in defined:
                b = box(s, x + 0.07, y + 0.08, cw - 0.14, ch - 0.16, fill=WHITE, line=RULE, lw=1.0)
                text(s, x + 0.07, y + 0.08, cw - 0.14, ch - 0.16, f"{r}-{c}", size=14, color=FAINT, align="c", anchor="m")
            else:
                text(s, x, y, cw, ch, "—", size=16, color=FAINT, align="c", anchor="m")
        line(s, 0.6, y + ch, gx + 3 * cw, y + ch, color=RULE)
    text(s, 0.6, 5.95, 7.2, 0.5, "Five of nine combinations are valid: zero-shot uses no taxonomy, so it pairs only with free.",
         size=15, color=MUTED, italic=True, spacing=1.0)
    # right: the LLM as a third, swappable axis
    x, w = 8.0, 4.73
    label(s, x, gy, w, "Third axis: the LLM")
    models = [("Gemini 3.1 Flash-Lite", "Google  ·  main model", "structured output enforced by the API"),
              ("gpt-5-mini", "OpenAI  ·  second model", "a reasoning model, used to cross-check")]
    for k, (a, b, c) in enumerate(models):
        y = gy + 0.42 + k * 1.45
        box(s, x, y, w, 1.28, fill=PANEL)
        box(s, x, y, 0.07, 1.28, fill=NAVY)
        text(s, x + 0.25, y + 0.08, w - 0.35, 0.42, a, size=18, bold=True, color=NAVY, anchor="m")
        text(s, x + 0.25, y + 0.48, w - 0.35, 0.36, b, size=15, color=INK, anchor="m")
        text(s, x + 0.25, y + 0.84, w - 0.35, 0.36, c, size=14, color=MUTED, anchor="m")
    box(s, x, gy + 3.35, w, 0.95, fill=PANEL2)
    text(s, x + 0.2, gy + 3.35, w - 0.4, 0.95, [[("Only the model changes: ", {"bold": True, "color": NAVY}),
                                                ("same case files, prompts, taxonomy and validation.", {})]], size=16, anchor="m", spacing=1.02)


def s12_prompts(prs, num):
    s = chrome(prs, "Prompt Design: What Each Strategy Sends", num)
    box(s, 0.6, 1.35, 12.13, 0.55, fill=PANEL2)
    text(s, 0.8, 1.35, 11.8, 0.55, [[("Same in both:  ", {"bold": True, "color": NAVY}),
                                     ("ODC taxonomy  ·  anti-bias rules  ·  the bug’s evidence summary  ·  JSON answer format", {})]],
         size=17, anchor="m")

    def bubble(x, y, w, h, tag, body, col, bg):
        box(s, x, y, w, h, fill=bg)
        box(s, x, y, 0.07, h, fill=col)
        text(s, x + 0.25, y + 0.04, 1.4, 0.34, tag, size=14, bold=True, color=col, anchor="m")
        text(s, x + 0.25, y + 0.36, w - 0.4, h - 0.4, body, size=16, color=INK, spacing=1.02)

    for c, (title, sub, col, bg) in enumerate([("few-shot", "one call, one answer", BLUE, BLUE_BG),
                                               ("scientific", "up to 6 turns", PURPLE, PURPLE_BG)]):
        x = 0.6 + c * 6.25
        w = 5.88
        box(s, x, 2.1, w, 0.48, fill=col)
        text(s, x + 0.2, 2.1, w - 0.3, 0.48, [[(title, {"bold": True}), (f"   ·   {sub}", {"size": 15})]], size=18, color=WHITE, anchor="m")
    # few-shot column
    x, w = 0.6, 5.88
    bubble(x, 2.75, w, 0.95, "① Instructions", "ODC definitions, a 7-question decision tree, 5 worked examples", BLUE, BLUE_BG)
    bubble(x, 3.85, w, 0.8, "② The bug", "the evidence summary", MUTED, PANEL)
    line(s, x + w / 2, 4.7, x + w / 2, 5.95, color=FAINT, width=1.5, arrow=True)
    text(s, x + w / 2 + 0.15, 4.95, 2.6, 0.8, ["one call,", "no extra evidence"], size=16, color=MUTED, italic=True, anchor="m")
    bubble(x, 6.0, w, 0.8, "③ Answer", "one JSON: type, alternatives, reasoning", POST, POST_BG)
    # scientific column
    x = 6.85
    bubble(x, 2.75, w, 0.95, "① Instructions", "ODC definitions, the list of 5 probes, turn rules", PURPLE, PURPLE_BG)
    bubble(x, 3.85, w, 0.8, "② The bug", "the same summary; the rest is held back", MUTED, PANEL)
    box(s, x, 4.8, w, 1.05, fill=WHITE, line=PURPLE, lw=1.0)
    text(s, x + 0.2, 4.82, 2.0, 0.3, "EACH TURN", size=13, bold=True, color=PURPLE, anchor="m")
    text(s, x + 0.2, 5.12, w - 0.4, 0.34, [[("model  ", {"bold": True, "color": PURPLE}), ("hypothesis → prediction → probe request", {})]], size=15, anchor="m")
    text(s, x + 0.2, 5.46, w - 0.4, 0.34, [[("pipeline  ", {"bold": True, "color": GOLD}), ("returns what the probe found", {})]], size=15, anchor="m")
    bubble(x, 6.0, w, 0.8, "③ Answer", "the same JSON + the full turn transcript", POST, POST_BG)


def s13_loop(prs, num):
    s = chrome(prs, "How the Scientific Strategy Reasons", num)
    label(s, 0.6, 1.35, 12.13, "The summary is read once  ·  every turn then starts at Hypothesis")

    def step(x, y, w, h, title, sub, col, bg, lw=1.25):
        rbox(s, x, y, w, h, fill=bg, line_col=col, lw=lw)
        text(s, x, y + 0.08, w, 0.42, title, size=18, bold=True, color=col, align="c", anchor="m")
        text(s, x + 0.08, y + 0.48, w - 0.16, h - 0.52, sub, size=14, color=INK, align="c", spacing=0.98)

    y1, h1 = 1.78, 1.05
    step(0.6, y1, 1.85, h1, "Start", "evidence summary", MUTED, PANEL)
    step(2.8, y1, 2.2, h1, "Hypothesis", "a specific cause", PURPLE, PURPLE_BG)
    step(5.35, y1, 2.2, h1, "Prediction", "what must be there", PURPLE, PURPLE_BG)
    step(7.9, y1, 2.2, h1, "Enough evidence?", "the model decides", GOLD, GOLD_BG)
    step(10.53, y1, 2.2, h1, "Conclude", "ODC label + alternatives", POST, POST_BG, lw=1.75)
    for x_from, x_to in [(2.45, 2.8), (5.0, 5.35), (7.55, 7.9)]:
        line(s, x_from + 0.03, y1 + h1 / 2, x_to - 0.03, y1 + h1 / 2, color=NAVY, width=1.75, arrow=True)
    line(s, 10.13, y1 + h1 / 2, 10.5, y1 + h1 / 2, color=POST, width=2.0, arrow=True)
    text(s, 10.02, y1 + 0.1, 0.6, 0.28, "yes", size=15, bold=True, color=POST, align="c", anchor="m")
    # second row: the experiment
    y2, h2 = 3.25, 1.0
    line(s, 9.0, y1 + h1, 9.0, y2 - 0.03, color=NAVY, width=1.75, arrow=True)
    text(s, 9.08, y1 + h1 + 0.05, 0.5, 0.3, "no", size=15, bold=True, color=MUTED, anchor="m")
    step(7.9, y2, 2.2, h2, "Probe", "ask for hidden evidence", BLUE, BLUE_BG)
    line(s, 7.87, y2 + h2 / 2, 7.58, y2 + h2 / 2, color=NAVY, width=1.75, arrow=True)
    step(5.35, y2, 2.2, h2, "Observation", "read what came back", BLUE, BLUE_BG)
    line(s, 5.32, y2 + h2 / 2, 3.9, y2 + h2 / 2, color=NAVY, width=1.75, dash=True)
    line(s, 3.9, y2 + h2 / 2, 3.9, y1 + h1 + 0.03, color=NAVY, width=1.75, dash=True, arrow=True)
    text(s, 3.98, y2 + 0.12, 1.3, 0.34, "next turn", size=15, italic=True, color=NAVY, anchor="m")
    text(s, 10.53, y2 + 0.05, 2.2, 0.95, ["at most 6 turns;", "on the last one it", "must conclude"],
         size=14, italic=True, color=MUTED, align="c", spacing=0.98)
    text(s, 0.6, y2 + 0.1, 3.1, 0.9, [[("Adapted from AutoSD [17, 18]", {"bold": True, "color": NAVY})],
                                      [("from locating a fault to naming its type", {"color": MUTED})]], size=15, spacing=1.02)
    # probes
    label(s, 0.6, 4.55, 12.13, "Five probes: the only way to see evidence held back from the prompt")
    probes = [(["list_evidence()"], "what evidence exists"), (["full_stack_trace", "(test)"], "full trace and message"),
              (["snippet(class)"], "source of a class"), (["coverage(class)"], "line and branch data"), (["bug_report()"], "the full report")]
    tw = (12.13 - 4 * 0.15) / 5
    for k, (p_, d) in enumerate(probes):
        x = 0.6 + k * (tw + 0.15)
        box(s, x, 4.93, tw, 1.05, fill=BLUE_BG)
        box(s, x, 4.93, tw, 0.06, fill=BLUE)
        text(s, x + 0.12, 5.02, tw - 0.2, 0.58, p_, size=14, font=MONO, bold=True, color=BLUE, anchor="m", spacing=0.95)
        text(s, x + 0.12, 5.58, tw - 0.2, 0.36, d, size=14, color=INK, anchor="m")
    keyline(s, 6.2, "The prediction is written before the evidence arrives, so a first guess cannot be rationalised afterwards.", h=0.55)


def s14_eval(prs, num):
    s = chrome(prs, "Evaluation: How We Compare Two Labels", num)
    text(s, 0.6, 1.3, 12.13, 0.45, [[("For each bug we compare its ", {}), ("pre-fix", {"bold": True, "color": PRE}), (" label with its ", {}),
                                     ("post-fix", {"bold": True, "color": POST}), (" label, from strict to forgiving.", {})]], size=17, anchor="m")
    cw, gap = (12.13 - 3 * 0.25) / 4, 0.25
    cards = [("Tier 1", "Strict match", "Same ODC type?", BLUE),
             ("Tier 2", "Top-2 match", "Is one label the other’s alternative?", PURPLE),
             ("Tier 3", "Family match", "Same ODC family?", TEAL),
             ("Tier 4", "Cohen’s κ", "Agreement beyond chance, over all bugs?", GOLD)]
    y = 1.95
    for k, (tier, name, q, col) in enumerate(cards):
        x = 0.6 + k * (cw + gap)
        box(s, x, y, cw, 3.25, fill=PANEL)
        box(s, x, y, cw, 0.07, fill=col)
        text(s, x + 0.2, y + 0.15, cw - 0.3, 0.34, tier.upper(), size=13, bold=True, color=col, anchor="m")
        text(s, x + 0.2, y + 0.48, cw - 0.3, 0.42, name, size=20, bold=True, color=NAVY, anchor="m")
        text(s, x + 0.2, y + 0.92, cw - 0.3, 0.7, q, size=16, color=INK, spacing=1.0)
        ey = y + 1.7
        if k < 3:
            ex = [(("Checking", "Checking"), "same type"),
                  (("Checking", "Algorithm"), "Algorithm was listed as an alternative"),
                  (("Checking", "Assignment"), "both in Control and Data Flow")][k]
            (a, b), note_ = ex
            for r, (lab, v, c2) in enumerate([("pre", a, PRE), ("post", b, POST)]):
                yy = ey + r * 0.42
                text(s, x + 0.2, yy, 0.55, 0.36, lab, size=13, bold=True, color=c2, anchor="m")
                box(s, x + 0.78, yy + 0.02, cw - 1.0, 0.33, fill=WHITE, line=RULE, lw=0.75)
                text(s, x + 0.78, yy + 0.02, cw - 1.0, 0.33, v, size=14, color=INK, align="c", anchor="m")
            text(s, x + 0.2, ey + 0.9, cw - 0.3, 0.6, note_, size=14, color=MUTED, italic=True, spacing=1.0)
        else:
            bw = cw - 0.4
            for q_ in range(10):
                shade = ["EDF0F4", "E3E8EF", "D3DAE4", "BCC8D8", "9FB0C6", "8196B5", "5E789F", "46628E", "2E4A7D", "1D3563"][q_]
                box(s, x + 0.2 + q_ * bw / 10, ey + 0.2, bw / 10, 0.34, fill=shade)
            text(s, x + 0.15, ey + 0.58, 1.2, 0.3, "0 = chance", size=13, color=MUTED, anchor="m")
            text(s, x + cw - 1.35, ey + 0.58, 1.2, 0.3, "1 = perfect", size=13, color=MUTED, anchor="m", align="r")
            text(s, x + 0.2, ey + 0.9, cw - 0.3, 0.6, "read on the Landis–Koch scale [27]", size=14, color=MUTED, italic=True, spacing=1.0)
        if k < 2:
            text(s, x + cw - 0.02, y + 1.0, gap + 0.04, 0.4, "›", size=24, bold=True, color=FAINT, align="c", anchor="m")
    text(s, 0.6, 5.25, 9.0, 0.36, "Tier 1 and κ are the scores; Tiers 2–3 tell a near miss from an unrelated label.", size=15, color=MUTED, italic=True, anchor="m")
    label(s, 0.6, 5.72, 12.13, "Comparing scientific with few-shot: every bug falls into one of four outcomes")
    outs = [("both right", PANEL2, NAVY), ("only scientific right", POST, WHITE), ("only few-shot right", GREY_BAR, WHITE), ("both wrong", PANEL, FAINT)]
    ow = (12.13 - 3 * 0.15) / 4
    for k, (t_, fill, fc) in enumerate(outs):
        ox = 0.6 + k * (ow + 0.15)
        box(s, ox, 6.1, ow, 0.62, fill=fill)
        text(s, ox, 6.1, ow, 0.62, t_, size=16, bold=True, color=fc, align="c", anchor="m")


def s15_reference(prs, num):
    s = chrome(prs, "Why the Post-Fix Label Is a Reliable Reference", num)
    text(s, 0.6, 1.32, 12.13, 0.5, [[("The post-fix run is the same classifier given ", {}), ("one extra piece of evidence: the developer’s fix.", {"bold": True, "color": NAVY}),
                                     (" Four reasons make it the better-informed rater.", {})]], size=17, anchor="m")
    reasons = [("It sees what defines the answer.",
                "In ODC, the Defect Type is the nature of the correction [4, 15]. Pre-fix has to guess the correction from symptoms; post-fix can read it."),
               ("More evidence makes raters agree.",
                "Human raters agree far more when they see the code and the change than when they read only a fault description [22–26]."),
               ("It points at one specific fault.",
                "A buggy version holds about 9.2 faults [29]. The fix diff shows exactly the one the benchmark bug is about."),
               ("Nothing else changes.",
                "Same model, same prompt, same taxonomy, same evidence. Any difference between the two labels comes from the fix alone.")]
    for i, (a, b) in enumerate(reasons):
        y = 1.98 + i * 1.22
        box(s, 0.6, y + 0.05, 0.5, 0.5, fill=NAVY, shape=MSO_SHAPE.OVAL)
        text(s, 0.6, y + 0.05, 0.5, 0.5, str(i + 1), size=18, bold=True, color=WHITE, align="c", anchor="m")
        text(s, 1.3, y, 8.6, 0.45, a, size=20, bold=True, color=NAVY, anchor="m")
        text(s, 1.3, y + 0.46, 8.6, 0.7, b, size=16, color=INK, spacing=1.03)
        if i < 3:
            line(s, 0.6, y + 1.15, 12.73, y + 1.15, color=RULE)
        vx, vy, vw = 10.3, y + 0.08, 2.43
        if i == 0:
            box(s, vx, vy, vw, 0.42, fill=PRE_BG)
            text(s, vx, vy, vw, 0.42, "− buggy line", size=14, font=MONO, color=PRE, align="c", anchor="m")
            box(s, vx, vy + 0.5, vw, 0.42, fill=POST_BG)
            text(s, vx, vy + 0.5, vw, 0.42, "+ fixed line", size=14, font=MONO, color=POST, align="c", anchor="m")
        elif i == 1:
            for k, (v, col) in enumerate([(0.16, PRE), (0.70, GOLD), (0.93, POST)]):
                bx = vx + 0.15 + k * 0.8
                hh = 0.62 * v
                box(s, bx, vy + 0.95 - hh, 0.55, hh, fill=col)
                text(s, bx - 0.15, vy + 0.95 - hh - 0.3, 0.85, 0.28, f"κ {v:.2f}", size=13, bold=True, color=col, align="c", anchor="m")
            line(s, vx, vy + 0.95, vx + vw, vy + 0.95, color=FAINT, width=0.75)
        elif i == 2:
            for k in range(9):
                dot(s, vx + 0.25 + k * 0.23, vy + 0.33, 0.19, POST if k == 4 else GREY_BAR)
            text(s, vx, vy + 0.58, vw, 0.34, "the fix repairs one", size=14, color=POST, bold=True, align="c", anchor="m")
        else:
            for r, (lab, col, extra) in enumerate([("pre-fix", PRE, False), ("post-fix", POST, True)]):
                yy = vy + r * 0.5
                text(s, vx, yy, 0.85, 0.42, lab, size=14, bold=True, color=col, anchor="m")
                for k in range(3):
                    box(s, vx + 0.9 + k * 0.33, yy + 0.08, 0.26, 0.26, fill=GREY_BAR)
                if extra:
                    box(s, vx + 1.89, yy + 0.08, 0.52, 0.26, fill=POST)
                    text(s, vx + 1.89, yy + 0.08, 0.52, 0.26, "+fix", size=12, bold=True, color=WHITE, align="c", anchor="m")


def s16_setup(prs, num):
    s = chrome(prs, "Experimental Setup", num)
    label(s, 0.6, 1.4, 5.2, "410 bugs from 6 projects  ·  one square per bug")
    projects = [("Closure", 153), ("Math", 106), ("Lang", 61), ("Mockito", 38), ("Chart", 26), ("Time", 26)]
    shades = ["12284C", "24406E", "3A5A8C", "5E789F", "8A9EB8", "B3C0D2"]
    cell, gap, cols = 0.14, 0.04, 28
    i = 0
    for (p_, n), col in zip(projects, shades):
        for _ in range(n):
            box(s, 0.6 + (i % cols) * (cell + gap), 1.85 + (i // cols) * (cell + gap), cell, cell, fill=col)
            i += 1
    for j, ((p_, n), col) in enumerate(zip(projects, shades)):
        x = 0.6 + (j % 3) * 1.72
        y = 4.75 + (j // 3) * 0.45
        box(s, x, y + 0.11, 0.22, 0.22, fill=col)
        text(s, x + 0.32, y, 1.4, 0.44, f"{p_} {n}", size=15, anchor="m")
    x = 6.1
    label(s, x, 1.4, 6.63, "What we ran")
    eqs = [("Main study  ·  Gemini 3.1 Flash-Lite", ["410 bugs", "scientific + few-shot", "pre + post"], "1,640", NAVY),
           ("Baseline for RQ4a  ·  Gemini 3.1 Flash-Lite", ["410 bugs", "zero-free", "pre + post"], "820", PANEL2),
           ("Cross-model check  ·  gpt-5-mini", ["13 bugs", "scientific + few-shot", "pre + post"], "52", PANEL2)]
    widths = [1.1, 2.0, 1.15]
    for r, (m, toks, res, fill) in enumerate(eqs):
        y = 1.85 + r * 1.4
        text(s, x, y, 6.63, 0.36, m, size=15, color=NAVY, bold=True, anchor="m")
        cx = x
        for t_, w in zip(toks, widths):
            box(s, cx, y + 0.45, w, 0.58, fill=PANEL)
            text(s, cx, y + 0.45, w, 0.58, t_, size=15, bold=True, color=INK, align="c", anchor="m")
            cx += w
            text(s, cx, y + 0.45, 0.32, 0.58, "×" if t_ != toks[-1] else "=", size=18, color=FAINT, align="c", anchor="m")
            cx += 0.32
        box(s, cx, y + 0.45, 12.73 - cx, 0.58, fill=fill)
        text(s, cx, y + 0.45, 12.73 - cx, 0.58, [[(res, {"bold": True}), (" runs", {"size": 14})]], size=19,
             color=WHITE if fill == NAVY else NAVY, align="c", anchor="m")
    keyline(s, 6.2, "The 13 cross-model bugs are the ones we also read by hand.  Reporting follows the LLM study guidelines [28].", h=0.55)


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
    s = chrome(prs, "RQ3: Agreement with the Post-Fix Reference", num)
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
    note(s, "Algorithm/Method vs Checking is also the boundary human raters confuse [22]; the fix shows one fault of several [29].")


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


def pair_bars(s, x, y, rows, unit, name_w=1.95, row_h=0.46, size=15):
    """One row per group: a green bar (only the loop right) above a grey bar (only few-shot right),
    both starting from the same baseline, with the count at the end of each bar."""
    for r, (name, loop_n, few_n) in enumerate(rows):
        yy = y + r * row_h
        text(s, x, yy, name_w, row_h * 0.9, name, size=size, anchor="m")
        bx = x + name_w + 0.1
        box(s, bx, yy + 0.04, max(loop_n * unit, 0.03), 0.17, fill=POST)
        text(s, bx + loop_n * unit + 0.06, yy - 0.04, 0.6, 0.26, str(loop_n), size=14, bold=True, color=POST, anchor="m")
        box(s, bx, yy + 0.23, max(few_n * unit, 0.03), 0.17, fill=GREY_BAR)
        text(s, bx + few_n * unit + 0.06, yy + 0.16, 0.6, 0.26, str(few_n), size=14, color=FAINT, anchor="m")
    line(s, x + name_w + 0.1, y - 0.02, x + name_w + 0.1, y + len(rows) * row_h - 0.06, color=FAINT, width=1.0)


def s21_rq4b_bugs(prs, num):
    s = chrome(prs, "RQ4b: Scientific Beats Few-Shot, Bug by Bug", num)
    # headline: three numbers, each with a plain-language caption
    text(s, 0.6, 1.3, 1.45, 1.0, "73", size=54, bold=True, color=POST, anchor="m")
    text(s, 2.0, 1.36, 2.4, 0.9, [[("bugs ", {}), ("only scientific", {"bold": True})], "gets right"],
         size=18, color=POST, anchor="m", spacing=0.95)
    text(s, 4.4, 1.3, 1.1, 1.0, "58", size=40, bold=True, color=FAINT, anchor="m")
    text(s, 5.4, 1.36, 2.2, 0.9, [[("bugs ", {}), ("only few-shot", {"bold": True})], "gets right"],
         size=18, color=FAINT, anchor="m", spacing=0.95)
    box(s, 7.6, 1.45, 0.05, 0.75, fill=RULE)
    text(s, 7.8, 1.3, 1.5, 1.0, "+15", size=40, bold=True, color=NAVY, anchor="m")
    text(s, 9.25, 1.36, 3.48, 0.9, [[("more bugs right with scientific", {"bold": True, "color": NAVY})],
                                    [("than with few-shot (73 − 58)", {"color": MUTED, "size": 15})]],
         size=17, anchor="m", spacing=1.0)
    # 410-bug strip
    label(s, 0.6, 2.42, 7.6, "All 410 bugs  ·  does the pre-fix label match the post-fix label?")
    text(s, 8.2, 2.38, 4.53, 0.4, [[("κ 0.389 → 0.505", {"bold": True, "color": NAVY}), ("  ·  significant, p ≈ 0.012", {"color": MUTED})]],
         size=15, align="r", anchor="m")
    segs = [(215, PANEL2, NAVY, "both right  215"), (73, POST, WHITE, "only scientific  73"),
            (58, GREY_BAR, WHITE, "only few-shot  58"), (64, PANEL, FAINT, "both wrong  64")]
    cx, bw = 0.6, 12.13
    for n, fill, fc, lab in segs:
        w = bw * n / 410
        box(s, cx, 2.8, w, 0.62, fill=fill)
        text(s, cx, 2.8, w, 0.62, lab, size=15, bold=True, color=fc, align="c", anchor="m")
        cx += w
    # shared legend for both charts below
    box(s, 0.6, 3.7, 0.34, 0.2, fill=POST)
    text(s, 1.02, 3.62, 2.6, 0.36, "only scientific right", size=15, bold=True, color=POST, anchor="m")
    box(s, 3.55, 3.7, 0.34, 0.2, fill=GREY_BAR)
    text(s, 3.97, 3.62, 2.8, 0.36, "only few-shot right", size=15, color=FAINT, anchor="m")
    line(s, 0.6, 4.08, 12.73, 4.08, color=RULE)
    # left: by evidence requested
    label(s, 0.6, 4.22, 6.6, "More hidden evidence asked for  →  more scientific wins")
    pair_bars(s, 0.6, 4.72, [("never asked", 6, 4), ("asked 1–2 times", 42, 41),
                             ("asked 3+ times", 25, 13), ("got the fixed code", 12, 6)], unit=3.2 / 42)
    # right: by project
    x = 7.55
    label(s, x, 4.22, 5.18, "Scientific wins as often or more, in every project")
    pair_bars(s, x, 4.72, [("Chart", 8, 2), ("Mockito", 7, 2), ("Time", 7, 4)], unit=1.4 / 27, name_w=1.05)
    pair_bars(s, x + 2.65, 4.72, [("Math", 15, 14), ("Lang", 9, 9), ("Closure", 27, 27)], unit=1.4 / 27, name_w=0.95)


def chip(s, x, y, w, h, runs, fill=PANEL, line_col=None, size=15, color=INK, dash=False, bold=False):
    b = box(s, x, y, w, h, fill=fill, line=line_col, lw=1.0)
    if dash:
        from pptx.enum.dml import MSO_LINE
        b.line.dash_style = MSO_LINE.DASH
    text(s, x + 0.1, y, w - 0.2, h, runs, size=size, color=color, anchor="m", bold=bold)


def s21b_rq4b_models(prs, num):
    s = chrome(prs, "RQ4b: Why Scientific Wins — Evidence from the 13 Bugs", num)
    # headline score
    text(s, 0.6, 1.28, 2.9, 0.78, [[("5", {"color": POST}), (" : ", {"color": FAINT}), ("1", {"color": FAINT})]],
         size=46, bold=True, anchor="m")
    text(s, 0.6, 2.02, 3.1, 0.42, "5 bugs vs 1 bug, all pre-fix", size=14, color=MUTED, anchor="m")
    # which bugs only one strategy gets right, named
    tx = 3.75
    text(s, tx + 1.45, 1.3, 5.0, 0.34, [[("■ ", {"color": POST}), ("only scientific right", {"bold": True, "color": POST})]], size=15, anchor="m")
    text(s, tx + 6.55, 1.3, 2.43, 0.34, [[("■ ", {"color": GREY_BAR}), ("only few-shot right", {"bold": True, "color": FAINT})]], size=15, anchor="m")
    rows = [("Gemini", ["Math_17", "Mockito_26", "Chart_7"], ["Math_104"]),
            ("gpt-5-mini", ["Time_3", "Chart_11"], [])]
    for r, (m, sci, few) in enumerate(rows):
        y = 1.72 + r * 0.4
        text(s, tx, y, 1.4, 0.34, m, size=15, font=MONO, color=NAVY, anchor="m")
        cx = tx + 1.45
        for b in sci:
            w = 0.2 + 0.105 * len(b)
            box(s, cx, y + 0.02, w, 0.3, fill=POST)
            text(s, cx, y + 0.02, w, 0.3, b, size=14, font=MONO, bold=True, color=WHITE, align="c", anchor="m")
            cx += w + 0.1
        cx = tx + 6.55
        for b in few:
            w = 0.2 + 0.105 * len(b)
            box(s, cx, y + 0.02, w, 0.3, fill=GREY_BAR)
            text(s, cx, y + 0.02, w, 0.3, b, size=14, font=MONO, bold=True, color=WHITE, align="c", anchor="m")
        if not few:
            text(s, cx, y, 1.0, 0.34, "none", size=15, color=FAINT, italic=True, anchor="m")
    text(s, tx, 1.3, 1.4, 0.34, "model", size=14, color=MUTED, anchor="m")
    line(s, 0.6, 2.5, 12.73, 2.5, color=RULE)
    # example cards
    label(s, 0.6, 2.65, 12.13, "What the transcripts show")
    cards = [("Time_3", "gpt-5-mini", "Checking", "Algorithm", "kept testing “a zero guard is missing” for six turns", True),
             ("Chart_11", "gpt-5-mini", "Assignment", "Algorithm", "narrowed its prediction to one wrong assignment", True),
             ("Math_17", "Gemini", "Checking", "Function", "had to name a concrete cause: a range check", True),
             ("Math_104", "Gemini", "Algorithm", "Assignment", "named the wrong constant, but chose Algorithm", False)]
    cw, gap = (12.13 - 3 * 0.25) / 4, 0.25
    for c, (bug, m, sci, few, why, win) in enumerate(cards):
        x = 0.6 + c * (cw + gap)
        y = 3.05
        col = POST if win else GOLD
        box(s, x, y, cw, 2.05, fill=POST_BG if win else PANEL)
        box(s, x, y, cw, 0.07, fill=col)
        text(s, x + 0.18, y + 0.14, cw - 0.3, 0.4, [[(bug, {"bold": True, "font": MONO, "color": NAVY}), (f"  {m}", {"color": MUTED, "size": 14})]],
             size=16, anchor="m")
        text(s, x + 0.18, y + 0.56, cw - 0.3, 0.36, [[("scientific  ", {"color": MUTED, "size": 14}),
                                                      (sci, {"bold": True, "color": POST if win else FAINT})]], size=17, anchor="m")
        text(s, x + 0.18, y + 0.9, cw - 0.3, 0.36, [[("few-shot  ", {"color": MUTED, "size": 14}),
                                                     (few, {"bold": True, "color": FAINT if win else POST})]], size=17, anchor="m")
        text(s, x + 0.18, y + 1.3, cw - 0.3, 0.7, why, size=15, color=INK, spacing=1.0)
    text(s, 0.6, 5.13, 12.13, 0.32, [[("green", {"bold": True, "color": POST}), (" = the label that matches our manual reading", {"color": MUTED})]],
         size=14)
    # findings: pipeline vs model
    y0 = 5.62
    box(s, 0.6, y0, 0.07, 1.2, fill=POST)
    text(s, 0.85, y0, 5.6, 0.4, "Same with both models  →  the pipeline", size=15, bold=True, color=NAVY, anchor="m")
    text(s, 0.85, y0 + 0.42, 5.6, 0.78, ["Scientific beats few-shot pre-fix: 6 vs 4 of 13",
                                         "Misleading clues can stop it too early (Chart_17)"], size=16, spacing=1.05)
    box(s, 6.85, y0, 0.07, 1.2, fill=NAVY)
    text(s, 7.1, y0, 5.63, 0.4, "Differs between models  →  the model", size=15, bold=True, color=NAVY, anchor="m")
    text(s, 7.1, y0 + 0.42, 5.63, 0.78,
         [[("Evidence requests per bug: Gemini ", {}), ("1.7", {"bold": True}), (", gpt-5-mini ", {}), ("3.0", {"bold": True})],
          [("Gemini trusts its first summary and stops early", {"color": MUTED})]], size=16, spacing=1.05)


def s22_mechanisms(prs, num):
    s = chrome(prs, "Qualitative Analysis of Thirteen Bugs", num)
    text(s, 0.6, 1.3, 12.13, 0.45, [[("We read every artifact by hand: ", {"bold": True, "color": NAVY}),
                                     ("evidence, full reasoning transcript and developer’s fix, for both strategies and both models", {"color": MUTED})]],
         size=16, anchor="m")
    # left: failure modes as cue -> wrong label chains
    x, w = 0.6, 5.95
    box(s, x, 1.9, w, 0.5, fill=PRE_BG)
    text(s, x + 0.2, 1.9, w - 0.3, 0.5, [[("1  ", {"bold": True, "color": PRE}), ("How the classification goes wrong", {"bold": True, "color": PRE})]],
         size=17, anchor="m")
    modes = [("Symptom-site bias", "Chart_17", "the exception site", "CHK", "ALG"),
             ("Bug-report anchoring", "Math_90", "a fix suggested in the report", "CHK", "INT"),
             ("Surface syntax", "Math_23", "the shape of the patch", "ASN", "ALG"),
             ("Underdetermined", "Lang_20", "two equally valid fixes", "CHK", "ASN")]
    for r, (m, bug, cue, said, right) in enumerate(modes):
        y = 2.55 + r * 0.95
        text(s, x, y, 3.6, 0.38, [[(m, {"bold": True}), (f"   {bug}", {"font": MONO, "color": NAVY, "size": 14})]], size=16, anchor="m")
        chip(s, x, y + 0.42, 2.95, 0.4, [[("cue: ", {"color": FAINT, "size": 14}), (cue, {})]], fill=PANEL, size=14)
        line(s, x + 3.0, y + 0.62, x + 3.4, y + 0.62, color=FAINT, width=1.25, arrow=True)
        chip(s, x + 3.45, y + 0.42, 1.2, 0.4, [[("said ", {"color": PRE, "size": 13}), (said, {"bold": True, "color": PRE})]],
             fill=WHITE, line_col=PRE, size=15)
        chip(s, x + 4.75, y + 0.42, 1.2, 0.4, [[("fix ", {"color": POST, "size": 13}), (right, {"bold": True, "color": POST})]],
             fill=WHITE, line_col=POST, size=15)
    # right: developer choices as forks
    x, w = 6.95, 5.78
    box(s, x, 1.9, w, 0.5, fill=PANEL2)
    text(s, x + 0.2, 1.9, w - 0.3, 0.5, [[("2  ", {"bold": True, "color": NAVY}), ("Where the developer had a choice", {"bold": True, "color": NAVY})]],
         size=17, anchor="m")
    forks = [("Math_90", "a Comparable check", "CHK", "a typed overload", "INT"),
             ("Math_17", "a range check only", "CHK", "check + fallback", "CHK+ALG"),
             ("Time_3", "better arithmetic", "ALG", "amount != 0 guards", "CHK"),
             ("Lang_20", "a null check", "CHK", "a new capacity", "ASN")]
    for r, (bug, could, ct, chose, cht) in enumerate(forks):
        y = 2.55 + r * 0.95
        bx = x
        box(s, bx, y + 0.22, 1.25, 0.46, fill=NAVY)
        text(s, bx, y + 0.22, 1.25, 0.46, bug, size=15, bold=True, font=MONO, color=WHITE, align="c", anchor="m")
        jx = bx + 1.25
        line(s, jx, y + 0.45, jx + 0.2, y + 0.45, color=FAINT, width=1.25)
        line(s, jx + 0.2, y + 0.2, jx + 0.2, y + 0.7, color=FAINT, width=1.25)
        line(s, jx + 0.2, y + 0.2, jx + 0.45, y + 0.2, color=FAINT, width=1.25, dash=True)
        line(s, jx + 0.2, y + 0.7, jx + 0.45, y + 0.7, color=NAVY, width=1.75)
        cx = jx + 0.5
        chip(s, cx, y + 0.02, w - (cx - x), 0.36, [[("could  ", {"color": FAINT, "size": 13}), (could, {"color": MUTED}),
                                                   (f"  {ct}", {"color": FAINT, "bold": True})]], fill=WHITE, line_col=RULE, size=14, dash=True)
        chip(s, cx, y + 0.52, w - (cx - x), 0.36, [[("chose  ", {"color": NAVY, "size": 13}), (chose, {"bold": True}),
                                                   (f"  {cht}", {"color": NAVY, "bold": True})]], fill=PANEL2, size=14)
    keyline(s, 6.42, [[("A fix repairs one of several faults [29] — for ", {}), ("77%", {"bold": True, "color": NAVY}),
                       (" of changed labels, the other type is already a recorded alternative.", {})]], h=0.48)


def s23_threats(prs, num):
    s = chrome(prs, "Threats to Validity", num)
    rows = [("Internal", ["The model can give a different answer each time it runs.",
                          "We removed fix hints from the pre-fix evidence, so it cannot see the answer."]),
            ("Construct", ["Matching the post-fix label is not the same as being right.",
                           "The class that was fixed is missing from the evidence for 285 of 410 bugs."]),
            ("External", ["We studied 6 of the 17 projects, all in Java, with one model on all 410 bugs.",
                          "Other projects or models may give different numbers; a second model ran on 13 bugs."]),
            ("Conclusion", ["Each setup ran once, so our intervals are estimates, not repeated measurements.",
                            "One person did the manual reading of the 13 bugs."]),
            ("Other", ["These bugs are public, so the model may have seen them during training.",
                       "The confidence score the model reports does not warn us when it is wrong."])]
    for i, (a, b) in enumerate(rows):
        y = 1.42 + i * 1.1
        box(s, 0.6, y + 0.12, 2.3, 0.8, fill=PANEL)
        text(s, 0.6, y + 0.12, 2.3, 0.8, a, size=20, bold=True, color=NAVY, align="c", anchor="m")
        text(s, 3.15, y, 9.58, 1.04, [b[0], [(b[1], {"color": MUTED})]], size=17, anchor="m", spacing=1.02, after=3)
        if i < len(rows) - 1:
            line(s, 0.6, y + 1.05, 12.73, y + 1.05, color=RULE)


def s24_conclusion(prs, num):
    s = chrome(prs, "Conclusion and Future Work", num)
    for i, (a, b) in enumerate([("97.8%", "three types (RQ1)"), ("0 of 1,640", "“Other” (RQ2)"),
                                ("70.2%", "pre-fix match (RQ3)"), ("73 vs 58", "scientific vs few-shot wins (RQ4)")]):
        x = 0.6 + i * 3.1
        box(s, x, 1.4, 2.9, 0.07, fill=NAVY)
        text(s, x, 1.58, 2.9, 0.8, a, size=36, bold=True, color=NAVY, anchor="m")
        text(s, x, 2.38, 2.9, 0.42, b, size=16, color=MUTED)
    label(s, 0.6, 3.02, 5.9, "Contributions", color=NAVY, size=20)
    bullets(s, 0.6, 3.5, 5.9, 3.0, ["A taxonomy × strategy condition space", "Enforced scientific reasoning + transcripts",
                                    "Where scientific beats few-shot, bug by bug", "Evaluation without ground truth"], size=19, after=20)
    label(s, 6.95, 3.02, 5.78, "Future work", color=NAVY, size=20)
    bullets(s, 6.95, 3.5, 5.78, 3.0, ["Strengthen scientific's weak spots", "Pick scientific or few-shot per bug",
                                      "Human reference labels for a sample", "More models, Impact, Trigger, Age"], size=19, after=20)


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
    "[29] D. Callaghan and B. Fischer, “Mining Bug Repositories for Multi-Fault Programs,” IEEE/ACM 22nd International Conference on Mining Software Repositories (MSR), Data and Tool Showcase Track, 2025.",
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
    order = [s03_motivation, s04_odc, s05_related, s06_problem, s07_idea, s08_rqs,
             s09_pipeline, s10_evidence, s11_conditions, s12_prompts, s13_loop, s14_eval, s15_reference, s16_setup,
             s17_rq12, s18_rq3, s19_changes, s20_rq4a, s21_rq4b_bugs, s22_mechanisms, s21b_rq4b_models, s23_threats, s24_conclusion]
    for i, fn in enumerate(order, start=2):
        fn(prs, i)
    chunks = [REFS[:10], REFS[10:20], REFS[20:]]
    for i, chunk in enumerate(chunks):
        refs_slide(prs, 25 + i, i + 1, len(chunks), chunk)
    closing_slide(prs, 28)
    prs.save(str(DECK))
    print(f"wrote {DECK.name}: {len(prs.slides)} slides")


if __name__ == "__main__":
    build()

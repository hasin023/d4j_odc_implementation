"""Build the thesis defence slide deck.

Writes ONLY to the Defence copy:
  iut_submissions/presentation/Defence/SWE_..._Defence_Presentation.pptx
The pre-defence files are never touched.

All content comes from the finalized defence book (latex/defence book/main.tex).
Design: a light "debugging / code-review" canvas — git-diff colours for pre-fix
(red) and post-fix (green), IBM Plex Mono for code-like labels, and one fixed
colour per ODC defect type reused in every chart. Every graphic is a native,
editable shape (no images), so the deck stays editable in Google Slides.

Size floors taken from the pre-defence deck: titles 30 pt, page numbers 18 pt,
body text >= 15 pt, references >= 12 pt.

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
DECK = ROOT / "iut_submissions/presentation/Defence/SWE_Orthogonal Defect Classification on Defects4JUsing an LLM-Driven Scientific Approach_Defence_Presentation.pptx"

CONTENT_TOTAL = 24

# ── Palette ────────────────────────────────────────────────────────────────
def rgb(h: str) -> RGBColor:
    return RGBColor.from_string(h)

PAPER = "F7F6F2"
PANEL = "FFFFFF"
PANEL2 = "EFEDE6"
INK = "1E2230"
MUTED = "5B6272"
RULE = "D8D4CA"
PRE, PRE_BG = "C62F3A", "FBE8E8"
POST, POST_BG = "23813F", "E4F3E8"
SEC = {"P1": "2F4B9A", "P2": "1D7F6E", "P3": "C4661F"}
SEC_NAME = {"P1": "CONTEXT", "P2": "METHODOLOGY", "P3": "RESULTS & ANALYSIS"}
# One colour per ODC type, used everywhere.
T = {
    "CHK": "D9822B", "ALG": "3867B0", "ASN": "8A5BB0", "TIM": "8C959F",
    "FCO": "B23A48", "INT": "1F8A70", "REL": "A0785A", "OTH": "9AA0A6",
}
TYPE_NAME = {
    "ALG": "Algorithm/Method", "ASN": "Assignment/Initialization", "CHK": "Checking",
    "TIM": "Timing/Serialization", "FCO": "Function/Class/Object",
    "INT": "Interface/O-O Messages", "REL": "Relationship",
}

SANS = "IBM Plex Sans"
MONO = "IBM Plex Mono"

# ── Low-level helpers ──────────────────────────────────────────────────────
def box(slide, x, y, w, h, fill=None, line=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE, radius=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line); s.line.width = Pt(lw)
    else:
        s.line.fill.background()
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    s.text_frame.text = ""
    return s


def rbox(slide, x, y, w, h, fill=None, line=None, lw=1.0, radius=0.06):
    return box(slide, x, y, w, h, fill, line, lw, MSO_SHAPE.ROUNDED_RECTANGLE, radius)


def text(slide, x, y, w, h, runs, size=17, color=INK, font=SANS, bold=False, align="l",
         anchor="t", spacing=1.0, space_after=0, inset=0.04):
    """runs: str | list of paragraphs; a paragraph is str or list of (text, style-dict)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
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
        p.space_after = Pt(space_after)
        segs = [(para, {})] if isinstance(para, str) else para
        for seg, st in segs:
            r = p.add_run()
            r.text = seg
            f = r.font
            f.name = st.get("font", font)
            f.size = Pt(st.get("size", size))
            f.bold = st.get("bold", bold)
            f.italic = st.get("italic", False)
            f.color.rgb = rgb(st.get("color", color))
    return tb


def line(slide, x1, y1, x2, y2, color=RULE, width=1.25, arrow=False, dash=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    if dash:
        ln.append(parse_xml('<a:prstDash xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="dash"/>'))
    if arrow:
        ln.append(parse_xml('<a:tailEnd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" type="triangle" w="med" len="med"/>'))
    return c


def chip(slide, x, y, w, h, label, fill, color=PANEL, size=15, font=MONO, bold=True):
    rbox(slide, x, y, w, h, fill=fill, radius=0.3)
    text(slide, x, y, w, h, label, size=size, color=color, font=font, bold=bold, align="c", anchor="m", inset=0.02)


def dot(slide, x, y, d, fill):
    return box(slide, x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL)


# ── Slide scaffolding ──────────────────────────────────────────────────────
def new_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[0])
    box(s, 0, 0, 13.333, 7.5, fill=PAPER)
    return s


def header(s, part, eyebrow, title, num):
    col = SEC[part]
    box(s, 0.55, 0.42, 0.09, 0.95, fill=col)
    text(s, 0.78, 0.30, 11.5, 0.42, [[("// ", {"color": col}), (f"{num:02d}  {eyebrow}", {"color": col})]],
         size=15, font=MONO, bold=True)
    text(s, 0.78, 0.66, 12.0, 0.75, title, size=30, bold=True, color=INK)


def footer(s, part, num, total=CONTENT_TOTAL):
    col = SEC[part]
    line(s, 0.55, 6.95, 12.78, 6.95, color=RULE, width=1.0)
    chip(s, 0.55, 7.04, 0.55, 0.36, part, col, size=14)
    text(s, 1.2, 7.02, 7.0, 0.4, SEC_NAME[part], size=14, font=MONO, color=MUTED, bold=True, anchor="m")
    label = f"{num:02d} / {total}" if total else f"{num:02d}"
    text(s, 10.6, 6.98, 2.2, 0.48, label, size=18, font=MONO, bold=True, color=INK, align="r", anchor="m")


def content_slide(prs, part, eyebrow, title, num):
    s = new_slide(prs)
    header(s, part, eyebrow, title, num)
    footer(s, part, num)
    return s


def takeaway(s, y, msg, part, h=0.62):
    col = SEC[part]
    rbox(s, 0.55, y, 12.23, h, fill=PANEL, line=col, lw=1.5, radius=0.12)
    box(s, 0.55, y, 0.12, h, fill=col)
    text(s, 0.85, y, 11.8, h, msg, size=17, color=INK, anchor="m", bold=False)


def card(s, x, y, w, h, title_txt, body, accent, title_size=18, body_size=16, fill=PANEL):
    rbox(s, x, y, w, h, fill=fill, line=RULE, lw=1.0, radius=0.05)
    box(s, x, y, w, 0.08, fill=accent)
    text(s, x + 0.18, y + 0.18, w - 0.36, 0.5, title_txt, size=title_size, bold=True, color=INK)
    text(s, x + 0.18, y + 0.66, w - 0.36, h - 0.8, body, size=body_size, color=MUTED, spacing=1.05, space_after=4)


def hbar(s, x, y, w_total, h, segments, labels=True, size=15):
    """segments: list of (share 0..1, colour, label)."""
    cx = x
    for share, col, lab in segments:
        w = w_total * share
        if w <= 0:
            continue
        box(s, cx, y, w, h, fill=col)
        if labels and lab and w > 0.9:
            text(s, cx, y, w, h, lab, size=size, color=PANEL, bold=True, align="c", anchor="m", inset=0.02)
        cx += w


def legend(s, x, y, items, size=15):
    """items: list of (colour, label); draws small squares (Plex has no ■ glyph)."""
    cx = x
    for col, lab in items:
        box(s, cx, y + 0.13, 0.2, 0.2, fill=col)
        w = 0.32 + 0.105 * len(lab)
        text(s, cx + 0.26, y, w, 0.46, lab, size=size, color=MUTED, anchor="m")
        cx += w + 0.25


# ── Slides ─────────────────────────────────────────────────────────────────
def s01_title(prs):
    s = new_slide(prs)
    box(s, 0, 0, 13.333, 0.14, fill=INK)
    text(s, 0.8, 0.55, 11.8, 0.45, "ISLAMIC UNIVERSITY OF TECHNOLOGY  ·  DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING",
         size=15, font=MONO, bold=True, color=MUTED)
    text(s, 0.8, 1.35, 7.4, 1.9, [
        [("Orthogonal Defect Classification on ", {}), ("Defects4J", {"color": SEC["P1"]})],
    ], size=40, bold=True, spacing=0.95)
    text(s, 0.8, 3.2, 7.4, 0.6, "Using an LLM-Driven Scientific Approach", size=24, color=MUTED)
    chip(s, 0.8, 4.0, 2.7, 0.46, "THESIS DEFENCE", INK, size=15)

    text(s, 0.8, 4.85, 4.3, 1.7, [
        [("Presented by", {"font": MONO, "size": 15, "bold": True, "color": MUTED})],
        "Md. Sakib Hossain  ·  210042133",
        "Mohammad Nahiyan Kabir  ·  210042168",
        "Hasin Mahtab Alvee  ·  210042174",
    ], size=16, space_after=2)
    text(s, 5.2, 4.85, 3.0, 2.3, [
        [("Supervised by", {"font": MONO, "size": 15, "bold": True, "color": MUTED})],
        "Lutfun Nahar Lota",
        [("Assistant Professor", {"color": MUTED, "size": 15})],
        [("Co-supervisor", {"color": MUTED, "size": 15})],
        [("Ishmam Tashdeed", {}), ("  Lecturer", {"color": MUTED, "size": 15})],
    ], size=16, space_after=1)

    # Right: a diff card that states the core idea.
    x, y, w = 8.3, 1.35, 4.45
    rbox(s, x, y, w, 4.75, fill=INK, radius=0.04)
    text(s, x + 0.25, y + 0.2, w - 0.5, 0.4, "bug.diff", size=15, font=MONO, color="9AA3B5", bold=True)
    rows = [
        ("  ", "one bug, two views", "C9CFDB"),
        ("- ", "pre-fix:  symptoms", "F1959B"),
        ("+ ", "post-fix: + the fix", "8FD3A2"),
        ("  ", "", "C9CFDB"),
        ("  ", "7 ODC defect types", "C9CFDB"),
    ]
    for i, (pfx, t_, c) in enumerate(rows):
        text(s, x + 0.25, y + 0.75 + i * 0.5, w - 0.5, 0.45, [[(pfx, {"color": c}), (t_, {"color": c})]],
             size=16, font=MONO, bold=True)
    for i, k in enumerate(["ALG", "ASN", "CHK", "TIM", "FCO", "INT", "REL"]):
        chip(s, x + 0.25 + (i % 4) * 0.86, y + 3.35 + (i // 4) * 0.55, 0.78, 0.42, k, T[k], size=14)
    box(s, 0, 7.36, 13.333, 0.14, fill=INK)


def s02_roadmap(prs, num):
    s = new_slide(prs)
    text(s, 0.78, 0.30, 11.5, 0.42, [[("// ", {"color": INK}), (f"{num:02d}  ROADMAP", {"color": INK})]], size=15, font=MONO, bold=True)
    box(s, 0.55, 0.42, 0.09, 0.95, fill=INK)
    text(s, 0.78, 0.66, 12.0, 0.75, "Presentation Roadmap", size=30, bold=True)
    cols = [
        ("P1", "Context", "03–08", ["Why classify defects", "Defects4J & ODC", "Related work & gap", "Pre-fix / post-fix idea", "Research questions"]),
        ("P2", "Methodology", "09–16", ["Pipeline & evidence", "Classification conditions", "Prompts & scientific loop", "Evaluation framework", "Experimental setup"]),
        ("P3", "Results & Analysis", "17–24", ["RQ1–RQ2: distribution & coverage", "RQ3: agreement & label changes", "RQ4: taxonomy & loop", "Failure modes & two models", "Threats & conclusion"]),
    ]
    for i, (part, name, rng, items) in enumerate(cols):
        x = 0.55 + i * 4.16
        col = SEC[part]
        rbox(s, x, 1.75, 3.95, 4.85, fill=PANEL, line=RULE, radius=0.04)
        box(s, x, 1.75, 3.95, 0.1, fill=col)
        chip(s, x + 0.25, 2.1, 0.62, 0.42, part, col, size=15)
        text(s, x + 1.0, 2.05, 2.8, 0.5, name, size=21, bold=True, anchor="m")
        text(s, x + 0.25, 2.65, 3.5, 0.4, f"slides {rng}", size=15, font=MONO, color=MUTED, bold=True)
        paras = [[("› ", {"color": col, "bold": True}), (it, {})] for it in items]
        text(s, x + 0.25, 3.2, 3.5, 3.2, paras, size=17, space_after=9)
    footer_simple(s, num)


def footer_simple(s, num):
    line(s, 0.55, 6.95, 12.78, 6.95, color=RULE, width=1.0)
    text(s, 0.55, 7.02, 7.0, 0.4, "ODC × DEFECTS4J  ·  THESIS DEFENCE", size=14, font=MONO, color=MUTED, bold=True, anchor="m")
    text(s, 10.6, 6.98, 2.2, 0.48, f"{num:02d} / {CONTENT_TOTAL}", size=18, font=MONO, bold=True, color=INK, align="r", anchor="m")


def s03_why(prs, num):
    s = content_slide(prs, "P1", "CONTEXT", "Why Classify Defects — and Why Defects4J?", num)
    # Left: the problem
    card(s, 0.55, 1.65, 5.6, 3.75, "Why classify defects?", [
        [("› ", {"color": SEC["P1"]}), ("Turns bug reports into process signals", {})],
        [("› ", {"color": SEC["P1"]}), ("Different defect types need different debugging and repair strategies", {})],
        [("› ", {"color": SEC["P1"]}), ("Aggregated labels show which mistakes a process keeps producing", {})],
        [("› ", {"color": SEC["P1"]}), ("Manual triage gives good labels but does not scale", {})],
    ], SEC["P1"], title_size=19, body_size=17)
    # Right: Defects4J
    x = 6.45
    rbox(s, x, 1.65, 6.33, 3.75, fill=PANEL, line=RULE, radius=0.05)
    box(s, x, 1.65, 6.33, 0.08, fill=SEC["P1"])
    text(s, x + 0.2, 1.83, 3.6, 0.5, [[("Defects4J benchmark ", {}), ("[1]", {"color": MUTED, "bold": False})]], size=19, bold=True)
    for i, (big, small) in enumerate([("836", "active bugs"), ("17", "Java projects")]):
        text(s, x + 0.2 + i * 1.9, 2.3, 1.8, 0.7, big, size=36, bold=True, color=SEC["P1"], font=MONO)
        text(s, x + 0.2 + i * 1.9, 2.98, 1.8, 0.4, small, size=15, color=MUTED)
    text(s, x + 3.95, 1.83, 2.3, 0.4, "per bug", size=15, font=MONO, bold=True, color=MUTED)
    arts = [("bug report", MUTED), ("failing tests", MUTED), ("buggy source", PRE), ("fixed source", POST), ("fix diff", POST)]
    for i, (a, c) in enumerate(arts):
        yy = 2.25 + i * 0.52
        dot(s, x + 3.95, yy + 0.13, 0.18, c)
        text(s, x + 4.25, yy, 2.0, 0.45, a, size=16, font=MONO, anchor="m")
    text(s, x + 0.2, 3.7, 3.6, 1.5, "Reproducible real-world bugs with developer patches and tests — the standard benchmark for Java fault studies.",
         size=16, color=MUTED, spacing=1.05)
    takeaway(s, 5.65, [[("Key property: ", {"bold": True}), ("every bug ships with its fix, so the same bug can be examined ", {}),
                        ("before", {"bold": True, "color": PRE}), (" and ", {}), ("after", {"bold": True, "color": POST}), (" the fix.", {})]], "P1", h=0.9)


def s04_odc(prs, num):
    s = content_slide(prs, "P1", "BACKGROUND", "Orthogonal Defect Classification (ODC)", num)
    # opener / closer strip
    rbox(s, 0.55, 1.6, 12.23, 1.05, fill=PANEL, line=RULE, radius=0.08)
    text(s, 0.8, 1.66, 2.2, 0.45, "OPENER", size=15, font=MONO, bold=True, color=PRE)
    text(s, 0.8, 2.05, 5.0, 0.5, "found:  Activity · Trigger · Impact", size=17, color=MUTED)
    line(s, 6.66, 1.75, 6.66, 2.5, color=RULE, width=1.0)
    text(s, 6.9, 1.66, 2.2, 0.45, "CLOSER", size=15, font=MONO, bold=True, color=POST)
    text(s, 6.9, 2.05, 5.8, 0.5, [[("fixed:  ", {}), ("Defect Type", {"bold": True, "color": INK}), (" · Target · Qualifier · Age · Source", {})]],
         size=17, color=MUTED)
    text(s, 0.55, 2.85, 12.2, 0.5, [[("This thesis classifies the ", {}), ("Defect Type", {"bold": True}),
        (": the nature of the correction, one of seven types in two families [2, 3]", {})]], size=18)
    fams = [
        ("Control and Data Flow", [("CHK", "missing or wrong guard / condition"), ("ALG", "wrong computation or procedure"),
                                   ("ASN", "wrong value or initialization"), ("TIM", "wrong concurrency / ordering")]),
        ("Structural", [("FCO", "missing design-level capability"), ("INT", "wrong interaction across a boundary"),
                        ("REL", "broken association between entities")]),
    ]
    for f_i, (fam, types) in enumerate(fams):
        x = 0.55 if f_i == 0 else 6.86
        w = 6.1 if f_i == 0 else 5.92
        text(s, x, 3.42, w, 0.45, fam, size=15, font=MONO, bold=True, color=MUTED)
        for i, (k, d) in enumerate(types):
            yy = 3.85 + i * 0.72
            rbox(s, x, yy, w, 0.62, fill=PANEL, line=RULE, radius=0.12)
            box(s, x, yy, 0.12, 0.62, fill=T[k])
            text(s, x + 0.28, yy, 2.9 if f_i == 0 else 2.85, 0.62, TYPE_NAME[k], size=16, bold=True, anchor="m")
            text(s, x + 3.15, yy, w - 3.25, 0.62, d, size=15, color=MUTED, anchor="m")
    text(s, 6.86, 6.0, 5.92, 0.8, [[("+ Other", {"font": MONO, "bold": True, "color": T["OTH"]}),
        ("  escape category, added in this study", {"color": MUTED})]], size=16, anchor="m")


def s05_related(prs, num):
    s = content_slide(prs, "P1", "RELATED WORK", "What Existing Work Does — and Misses", num)
    cards = [
        ("488", "faults", "Van der Spuy 2025 [4]", "Control/data-flow classes", "how a bug manifests, not its type"),
        ("395", "patches", "Sobreira et al. 2018 [5]", "Repair-action patterns", "what changed, not why"),
        ("50", "bugs", "Jiang et al. 2019 [6]", "Manual inspection", "detailed, but does not scale"),
    ]
    for i, (big, unit, who, what, lim) in enumerate(cards):
        x = 0.55 + i * 4.16
        rbox(s, x, 1.6, 3.95, 2.75, fill=PANEL, line=RULE, radius=0.05)
        text(s, x + 0.25, 1.72, 3.5, 0.8, [[(big, {"size": 36, "bold": True, "font": MONO, "color": SEC["P1"]}), (f"  {unit}", {"size": 16, "color": MUTED})]], size=16)
        text(s, x + 0.25, 2.5, 3.5, 0.45, who, size=15, font=MONO, color=MUTED, bold=True)
        text(s, x + 0.25, 2.92, 3.5, 0.5, what, size=17, bold=True)
        text(s, x + 0.25, 3.45, 3.5, 0.8, [[("− ", {"color": PRE, "bold": True, "font": MONO}), (lim, {})]], size=16, color=MUTED)
    rbox(s, 0.55, 4.55, 12.23, 1.25, fill=PANEL, line=RULE, radius=0.06)
    text(s, 0.8, 4.62, 3.3, 0.45, "LLM-based classification", size=15, font=MONO, bold=True, color=SEC["P1"])
    text(s, 0.8, 5.02, 11.8, 0.75, [
        [("Promising with good prompts [7–9], but ", {}), ("relies on bug-report text only", {"bold": True}),
         (", and without a fixed taxonomy different runs give ", {}), ("inconsistent labels", {"bold": True}), (".", {})]], size=17)
    takeaway(s, 6.0, [[("Gap: ", {"bold": True}), ("no semantic defect-type labelling of Defects4J at benchmark scale, and no way to evaluate one without ground truth.", {})]], "P1", h=0.78)


def s06_problem(prs, num):
    s = content_slide(prs, "P1", "PROBLEM STATEMENT", "The Problem We Address", num)
    rbox(s, 0.55, 1.65, 12.23, 1.55, fill=INK, radius=0.06)
    text(s, 0.9, 1.65, 11.5, 1.55, [[("How can we classify Defects4J bugs into ODC defect types ", {}),
        ("from pre-fix evidence alone", {"color": "F1959B"}), (", and evaluate that classification ", {}),
        ("without ground-truth labels", {"color": "8FD3A2"}), ("?", {})]], size=24, color=PANEL, bold=True, anchor="m", spacing=1.05)
    text(s, 0.55, 3.45, 12.0, 0.45, "A solution therefore has to be:", size=15, font=MONO, bold=True, color=MUTED)
    reqs = [
        ("Context-aware", "code, tests, stack traces and bug reports together"),
        ("Semantic", "classifies the defect mechanism, not syntax"),
        ("Taxonomy-constrained", "a fixed ODC label space, comparable across studies"),
        ("Open to its own limits", "can record a bug that fits no type"),
        ("Scalable", "LLM-based, no manual labelling"),
        ("Evaluable", "carries its own reference, since Defects4J has none"),
    ]
    for i, (t_, d) in enumerate(reqs):
        x = 0.55 + (i % 3) * 4.16
        y = 3.95 + (i // 3) * 1.45
        rbox(s, x, y, 3.95, 1.28, fill=PANEL, line=RULE, radius=0.08)
        text(s, x + 0.22, y + 0.12, 3.5, 0.45, [[("✓ ", {"color": POST}), (t_, {})]], size=18, bold=True)
        text(s, x + 0.22, y + 0.56, 3.55, 0.7, d, size=16, color=MUTED)


def s07_idea(prs, num):
    s = content_slide(prs, "P1", "CORE IDEA", "One Bug, Two Classifications", num)
    for i, (sign, name, col, bg, what, why) in enumerate([
        ("−", "PRE-FIX", PRE, PRE_BG, "bug report · failing tests · stack trace · source code", "The triage situation: no fix exists yet. This is the label the pipeline produces."),
        ("+", "POST-FIX", POST, POST_BG, "the same evidence + the developer's buggy-to-fixed diff", "Better informed: an ODC type describes the correction, and this run sees it."),
    ]):
        x = 0.55 + i * 6.2
        rbox(s, x, 1.65, 6.03, 2.75, fill=bg, line=col, lw=1.5, radius=0.05)
        text(s, x + 0.25, 1.78, 5.6, 0.55, [[(f"{sign} ", {"color": col}), (name, {"color": col})]], size=22, font=MONO, bold=True)
        text(s, x + 0.25, 2.4, 5.6, 0.8, what, size=18, color=INK, bold=True)
        text(s, x + 0.25, 3.25, 5.6, 1.1, why, size=17, color=MUTED, spacing=1.05)
    text(s, 0.55, 4.6, 12.2, 0.45, "Defects4J has no ODC labels, so:", size=15, font=MONO, bold=True, color=MUTED)
    steps = [("post-fix label", "= the fix-informed reference"), ("pre-fix vs post-fix", "= does the triage label hold?"), ("labels differ", "= drift")]
    for i, (a, b) in enumerate(steps):
        x = 0.55 + i * 4.16
        rbox(s, x, 5.05, 3.95, 1.2, fill=PANEL, line=RULE, radius=0.08)
        text(s, x + 0.2, 5.12, 3.6, 0.5, a, size=18, font=MONO, bold=True, color=INK)
        text(s, x + 0.2, 5.58, 3.6, 0.6, b, size=17, color=MUTED)
    text(s, 0.55, 6.35, 12.2, 0.5, [[("Agreement is not correctness: ", {"bold": True, "color": INK}),
        ("we measure how closely a pre-fix label reproduces a better-informed reference.", {})]], size=16, color=MUTED)

def s08_rqs(prs, num):
    s = content_slide(prs, "P1", "RESEARCH QUESTIONS", "Four Research Questions", num)
    rqs = [
        ("RQ1", "Defect-type distribution", "Which ODC types dominate Defects4J, and does the mix differ across projects?", "slide 17"),
        ("RQ2", "Taxonomy coverage", "Do the seven ODC types cover every bug, or is the “Other” escape needed?", "slide 17"),
        ("RQ3", "Classification accuracy", "How often does the pre-fix label match the post-fix reference, and how do labels change?", "18–19"),
        ("RQ4", "Contribution of each part", "a) What does the ODC taxonomy add?  b) What does the enforced loop add over few-shot?", "20–21"),
    ]
    for i, (k, name, q, where) in enumerate(rqs):
        y = 1.6 + i * 1.2
        rbox(s, 0.55, y, 12.23, 1.06, fill=PANEL, line=RULE, radius=0.08)
        chip(s, 0.8, y + 0.26, 1.05, 0.54, k, SEC["P1"], size=18)
        text(s, 2.1, y, 3.3, 1.06, name, size=19, bold=True, anchor="m")
        text(s, 5.4, y, 6.0, 1.06, q, size=16, color=MUTED, anchor="m", spacing=1.02)
        text(s, 11.35, y, 1.3, 1.06, where, size=15, font=MONO, color=SEC["P1"], bold=True, anchor="m", align="r")
    text(s, 0.55, 6.45, 12.2, 0.42, "Evaluated on 410 bugs from 6 projects · 1,640 classifications", size=16, font=MONO, color=MUTED, bold=True)

def s09_pipeline(prs, num):
    s = content_slide(prs, "P2", "PIPELINE", "Pipeline Architecture", num)
    img = ROOT / "scripts/slides/assets/methodology_diagram.png"  # cropped copy of latex/defence book/Methodology Diagram.png
    h = 5.3
    w = h * 1920 / 1000
    s.shapes.add_picture(str(img), Inches((13.333 - w) / 2), Inches(1.55), Inches(w), Inches(h))
def s10_evidence(prs, num):
    s = content_slide(prs, "P2", "EVIDENCE COLLECTION", "Building the Case File: context.json", num)
    x, y, w, h = 0.55, 1.6, 5.7, 5.15
    rbox(s, x, y, w, h, fill=INK, radius=0.03)
    lines_ = [
        ("{", "C9CFDB"),
        ('  "bug_report":  sanitized text,', "C9CFDB"),
        ('  "failing_tests": [name, message,', "C9CFDB"),
        ('                    stack trace],', "C9CFDB"),
        ('  "suspicious_frames": [...],', "C9CFDB"),
        ('  "code_snippets": [±12 / ±18 lines],', "C9CFDB"),
        ('  "coverage": [line, branch rates],', "C9CFDB"),
        ('  "hidden_oracles": {modified classes},', "E7C56B"),
        ('  "fix_diff": "..."   // post-fix only', "8FD3A2"),
        ("}", "C9CFDB"),
    ]
    for i, (t_, c) in enumerate(lines_):
        text(s, x + 0.25, y + 0.25 + i * 0.47, w - 0.4, 0.45, t_, size=15, font=MONO, color=c, bold=True)
    pts = [
        ("Suspicious frames", "Keep only stack frames in the project's own source; drop JUnit, JDK and build-tool frames. They decide which code the model reads."),
        ("Sanitized pre-fix evidence", "Remove the classes the fix touched and any “fixed in” discussion from bug reports, so the pre-fix run cannot see the fix."),
        ("Hidden oracle", "Modified classes are stored for evaluation only — never in the prompt."),
    ]
    for i, (a, b) in enumerate(pts):
        yy = 1.6 + i * 1.72
        rbox(s, 6.5, yy, 6.28, 1.55, fill=PANEL, line=RULE, radius=0.06)
        box(s, 6.5, yy, 0.1, 1.55, fill=SEC["P2"])
        text(s, 6.78, yy + 0.1, 5.85, 0.45, a, size=18, bold=True)
        text(s, 6.78, yy + 0.52, 5.85, 1.0, b, size=16, color=MUTED, spacing=1.03)


def s11_conditions(prs, num):
    s = content_slide(prs, "P2", "CLASSIFICATION CONDITIONS", "Two Choices Define Every Condition", num)
    gx, gy, cw, ch = 2.1, 2.1, 1.75, 1.05
    cols = ["free", "closed", "open"]
    rows = ["zero", "few", "scientific"]
    text(s, gx, 1.55, cw * 3, 0.45, "TAXONOMY  (label space)", size=15, font=MONO, bold=True, color=MUTED, align="c")
    text(s, 0.55, gy - 0.02, 1.5, 0.4, "STRATEGY", size=15, font=MONO, bold=True, color=MUTED)
    valid = {("zero", "free"), ("few", "closed"), ("few", "open"), ("scientific", "closed"), ("scientific", "open")}
    for c_i, c in enumerate(cols):
        text(s, gx + c_i * cw, gy - 0.02, cw, 0.4, c, size=16, font=MONO, bold=True, align="c")
    for r_i, r in enumerate(rows):
        text(s, 0.55, gy + 0.42 + r_i * ch, 1.5, ch, r, size=16, font=MONO, bold=True, anchor="m")
        for c_i, c in enumerate(cols):
            x = gx + c_i * cw + 0.06
            y = gy + 0.42 + r_i * ch + 0.06
            ok = (r, c) in valid
            default = (r, c) == ("scientific", "open")
            if default:
                rbox(s, x, y, cw - 0.12, ch - 0.12, fill=SEC["P2"], radius=0.1)
                text(s, x, y, cw - 0.12, ch - 0.12, [f"{r}-", f"{c}", [("default", {"size": 14})]], size=15, font=MONO, bold=True, color=PANEL, align="c", anchor="m", spacing=0.9)
            elif ok:
                rbox(s, x, y, cw - 0.12, ch - 0.12, fill=PANEL, line=SEC["P2"], lw=1.5, radius=0.1)
                text(s, x, y, cw - 0.12, ch - 0.12, [f"{r}-", f"{c}"], size=15, font=MONO, bold=True, color=INK, align="c", anchor="m", spacing=0.9)
            else:
                rbox(s, x, y, cw - 0.12, ch - 0.12, fill=PANEL2, radius=0.1)
                text(s, x, y, cw - 0.12, ch - 0.12, "—", size=16, color="A7A9AE", align="c", anchor="m")
    text(s, 0.55, 5.75, 7.0, 1.0, "5 of 9 combinations are valid: zero has no taxonomy, and free defines none.", size=16, color=MUTED)
    rx = 7.85
    items = [
        ("free", "model's own words", MUTED),
        ("closed", "one of the 7 ODC types", MUTED),
        ("open", "7 types + “Other”, which needs a written justification", MUTED),
        ("zero", "one plain prompt, no taxonomy", MUTED),
        ("few", "one prompt: definitions, checklist, 5 worked examples", MUTED),
        ("scientific", "enforced hypothesis → probe → observation loop", MUTED),
    ]
    for i, (k, d, c) in enumerate(items):
        yy = 1.62 + i * 0.84 + (0.25 if i >= 3 else 0)
        text(s, rx, yy, 1.75, 0.75, k, size=16, font=MONO, bold=True, color=SEC["P2"], anchor="m")
        text(s, rx + 1.75, yy, 3.2, 0.75, d, size=16, color=INK, anchor="m", spacing=1.0)
    line(s, rx, 4.13, 12.78, 4.13, color=RULE, width=1.0)


def s12_prompts(prs, num):
    s = content_slide(prs, "P2", "PROMPT DESIGN", "Prompt Templates, Not Raw Prompts", num)
    def template(x, name, sub, lines_):
        rbox(s, x, 1.6, 6.03, 4.55, fill=INK, radius=0.03)
        text(s, x + 0.25, 1.7, 5.6, 0.45, [[(name, {"color": PANEL}), (f"   {sub}", {"color": "9AA3B5"})]], size=17, font=MONO, bold=True)
        for i, (t_, c) in enumerate(lines_):
            text(s, x + 0.25, 2.25 + i * 0.46, 5.65, 0.45, t_, size=15, font=MONO, color=c, bold=c != "C9CFDB")
    hl, pl, cm = "7FB6F0", "C9CFDB", "8A93A6"
    template(0.55, "few", "single call", [
        ("[SYSTEM]", cm), ("  ODC_TAXONOMY  ANTI_BIAS_RULES", hl), ("  DECISION_TREE   (7 questions)", hl),
        ("  FEW_SHOT_EXAMPLES  (5)", hl), ("  OUTPUT_SCHEMA", hl), ("[USER]", cm), ("  Classify this bug:  BUG_CONTEXT", pl),
        ("[MODEL]  one JSON classification", pl),
    ])
    template(6.75, "scientific", "multi-turn loop", [
        ("[SYSTEM]", cm), ("  ODC_TAXONOMY  ANTI_BIAS_RULES", hl), ("  PROBE_CATALOGUE  TURN_SCHEMA", hl),
        ("[USER]  BUG_CONTEXT (summary)", pl), ("loop t = 1 … 6:", cm), ("  [MODEL] hypothesis, prediction, probe", pl),
        ("  [USER]  PROBE_RESULT", "8FD3A2"), ("until conclude → OUTPUT_SCHEMA", pl),
    ])
    takeaway(s, 6.3, [[("Same taxonomy and evidence; ", {}), ("scientific", {"bold": True, "font": MONO}),
                        (" replaces the decision tree and examples with a turn protocol.", {})]], "P2", h=0.55)


def s13_loop(prs, num):
    s = content_slide(prs, "P2", "SCIENTIFIC DEBUGGING PROTOCOL", "The Enforced Reasoning Loop", num)
    col = SEC["P2"]
    # cycle (adapted from AutoSD [10])
    nodes = [
        ("Hypothesis", "commit to a defect type", 0.75, 1.85),
        ("Prediction", "evidence that must exist", 3.65, 1.85),
        ("Probe", "request that evidence", 3.65, 4.05),
        ("Observation", "read what came back", 0.75, 4.05),
    ]
    for name, sub, x, y in nodes:
        rbox(s, x, y, 2.55, 1.35, fill=PANEL, line=col, lw=1.75, radius=0.12)
        text(s, x, y + 0.15, 2.55, 0.5, name, size=19, bold=True, align="c", color=INK)
        text(s, x + 0.1, y + 0.66, 2.35, 0.6, sub, size=15, align="c", color=MUTED)
    line(s, 3.3, 2.52, 3.65, 2.52, color=col, width=2.25, arrow=True)
    line(s, 4.92, 3.2, 4.92, 4.05, color=col, width=2.25, arrow=True)
    line(s, 3.65, 4.72, 3.3, 4.72, color=col, width=2.25, arrow=True)
    line(s, 2.02, 4.05, 2.02, 3.2, color=col, width=2.25, arrow=True)
    text(s, 0.75, 5.55, 5.45, 1.25, [
        [("Conclude ", {"bold": True, "color": POST}), ("when the evidence supports one type,", {})],
        [("else next turn — ", {}), ("max 6 turns", {"bold": True, "font": MONO})],
        [("Adapted from AutoSD [10]: find a fault → name its type", {"color": MUTED, "size": 15})],
    ], size=16, space_after=2)
    # probes
    text(s, 6.75, 1.6, 6.0, 0.45, "5 probes · executed on the evidence store", size=15, font=MONO, bold=True, color=MUTED)
    probes = [
        ("list_evidence()", "inventory of what exists"),
        ("full_stack_trace(test)", "complete trace + message"),
        ("snippet(class)", "all source snippets of a class"),
        ("coverage(class)", "full line / branch coverage"),
        ("bug_report()", "full report (sanitized pre-fix)"),
    ]
    for i, (p, d) in enumerate(probes):
        y = 2.05 + i * 0.8
        rbox(s, 6.75, y, 6.03, 0.68, fill=PANEL, line=RULE, radius=0.14)
        text(s, 6.95, y, 3.1, 0.68, p, size=15, font=MONO, bold=True, color=col, anchor="m")
        text(s, 10.0, y, 2.72, 0.68, d, size=15, color=MUTED, anchor="m")
    text(s, 6.75, 6.12, 6.03, 0.75, [[("The prediction is fixed ", {}), ("before", {"bold": True}),
        (" the evidence arrives, so the model cannot rationalise its first guess.", {})]], size=16, color=INK)


def s14_eval(prs, num):
    s = content_slide(prs, "P2", "EVALUATION FRAMEWORK", "Four Tiers of Agreement", num)
    col = SEC["P2"]
    tiers = [
        ("T1", "Strict match", "same ODC type", 5.6),
        ("T2", "Top-2 match", "either label among the other's alternatives", 6.35),
        ("T3", "Family match", "both types in the same family", 7.1),
    ]
    text(s, 0.55, 1.5, 6.0, 0.4, "strictest → most forgiving", size=15, font=MONO, bold=True, color=MUTED)
    for i, (k, name, d, w) in enumerate(tiers):
        y = 1.95 + i * 0.92
        rbox(s, 0.55, y, w, 0.78, fill=PANEL, line=col, lw=1.5, radius=0.18)
        chip(s, 0.72, y + 0.16, 0.62, 0.46, k, col, size=15)
        text(s, 1.5, y, 2.1, 0.78, name, size=18, bold=True, anchor="m")
        text(s, 3.55, y, w - 3.1, 0.78, d, size=16, color=MUTED, anchor="m")
    y = 4.85
    rbox(s, 0.55, y, 7.1, 1.35, fill=PANEL, line=col, lw=1.5, radius=0.12)
    chip(s, 0.72, y + 0.45, 0.62, 0.46, "T4", col, size=15)
    text(s, 1.5, y + 0.1, 6.0, 0.5, [[("Cohen's κ", {"font": SANS}), (" — strict match corrected for chance", {})]], size=18, bold=True)
    text(s, 1.5, y + 0.62, 6.0, 0.62, [[("κ", {"font": SANS}), (" = (p_o − p_e) / (1 − p_e)", {})]], size=20, font=MONO, bold=True, color=col)
    x = 8.0
    rbox(s, x, 1.5, 4.78, 4.7, fill=PANEL2, radius=0.05)
    text(s, x + 0.22, 1.62, 4.35, 0.5, "Reading the tiers", size=18, bold=True)
    text(s, x + 0.22, 2.15, 4.35, 1.6, [[("3 types cover 97.8% of labels and share one family, so ", {}),
        ("shuffled labels still reach >92%", {"bold": True, "color": PRE}), (" on T2–T3. We use them to grade disagreements: near miss vs unrelated.", {})]],
        size=16, color=MUTED, spacing=1.05)
    text(s, x + 0.22, 3.85, 4.35, 0.4, "κ, worked out (scientific)", size=15, font=MONO, bold=True, color=col)
    for i, (a, b) in enumerate([("p_o = 0.702", "labels agree"), ("p_e = 0.399", "agree by chance"), ("κ   = 0.505", "moderate")]):
        text(s, x + 0.22, 4.3 + i * 0.58, 2.2, 0.5, a, size=17, font=MONO, bold=True, color=INK, anchor="m")
        text(s, x + 2.45, 4.3 + i * 0.58, 2.2, 0.5, b, size=16, color=MUTED, anchor="m")
    text(s, 0.55, 6.35, 12.2, 0.5, [[("Landis–Koch [13]: ", {"bold": True}), ("0.21–0.40 fair  ·  0.41–0.60 moderate  ·  ≥ 0.61 substantial", {})]], size=16, color=MUTED)

def s15_reference(prs, num):
    s = content_slide(prs, "P2", "WHY POST-FIX IS A VALID REFERENCE", "Agreement Depends on Evidence", num)
    text(s, 0.55, 1.55, 6.2, 0.45, "Human agreement on ODC-style labels", size=15, font=MONO, bold=True, color=MUTED)
    studies = [
        ("fault descriptions only", 0.16, "Henningsson & Wohlin [11]", PRE),
        ("full code and change", 0.93, "Agnelo et al. [12]", POST),
    ]
    for i, (lab, k, who, c) in enumerate(studies):
        y = 2.1 + i * 1.45
        text(s, 0.55, y, 6.0, 0.45, lab, size=17, bold=True)
        box(s, 0.55, y + 0.5, 5.2, 0.5, fill=PANEL2)
        box(s, 0.55, y + 0.5, 5.2 * k, 0.5, fill=c)
        text(s, 0.55 + 5.2 * k + 0.1 if k < 0.6 else 0.65, y + 0.5, 1.6, 0.5, f"κ = {k:.2f}", size=17, font=MONO, bold=True,
             color=INK if k < 0.6 else PANEL, anchor="m")
        text(s, 0.55, y + 1.02, 6.0, 0.4, who, size=15, color=MUTED)
    text(s, 0.55, 5.0, 5.9, 1.2, "More evidence → higher agreement, so the run that sees the fix is the better-informed rater.",
         size=17, color=INK, spacing=1.05)
    text(s, 7.1, 1.55, 5.6, 0.45, "Our data agree", size=15, font=MONO, bold=True, color=MUTED)
    stats = [
        ("16 → 0", "human-review flags: pre-fix → post-fix"),
        ("68.0% → 76.3%", "scientific vs few-shot agreement, without → with the fix"),
        ("6 / 6", "projects where the strategies agree more once the fix is visible"),
    ]
    for i, (big, d) in enumerate(stats):
        y = 2.05 + i * 1.3
        rbox(s, 7.1, y, 5.68, 1.15, fill=PANEL, line=RULE, radius=0.08)
        text(s, 7.3, y + 0.05, 2.9, 1.05, big, size=22, font=MONO, bold=True, color=SEC["P2"], anchor="m")
        text(s, 10.05, y + 0.05, 2.65, 1.05, d, size=15, color=MUTED, anchor="m", spacing=1.0)
    takeaway(s, 6.12, "Caveat: two labels can agree and both be wrong — we claim reproduction of a reference, not correctness.", "P2", h=0.66)


def s16_setup(prs, num):
    s = content_slide(prs, "P2", "EXPERIMENTAL SETUP", "Corpus, Models, and Statistics", num)
    projects = [("Closure", 153, "compiler"), ("Math", 106, "numerics"), ("Lang", 61, "utilities"),
                ("Mockito", 38, "mocking"), ("Chart", 26, "plotting"), ("Time", 26, "date/time")]
    text(s, 0.55, 1.55, 6.3, 0.45, "410 bugs · 6 Defects4J projects", size=15, font=MONO, bold=True, color=MUTED)
    for i, (p_, n, d) in enumerate(projects):
        y = 2.05 + i * 0.62
        text(s, 0.55, y, 1.35, 0.5, p_, size=16, bold=True, anchor="m")
        bw = 2.9 * n / 153
        box(s, 1.95, y + 0.08, bw, 0.36, fill=SEC["P2"])
        text(s, 1.95 + bw + 0.08, y, 0.7, 0.5, str(n), size=16, font=MONO, bold=True, anchor="m")
        text(s, 5.65, y, 1.3, 0.5, d, size=15, color=MUTED, anchor="m")
    rbox(s, 0.55, 5.9, 6.2, 0.92, fill=PANEL, line=RULE, radius=0.1)
    text(s, 0.75, 5.9, 5.9, 0.92, [[("410 × 2 conditions × 2 modes = ", {}), ("1,640", {"bold": True, "font": MONO, "color": SEC["P2"]}),
                                     (" classifications, + zero-free baseline", {})]], size=16, anchor="m")
    text(s, 7.15, 1.55, 5.6, 0.45, "Models", size=15, font=MONO, bold=True, color=MUTED)
    for i, (m, d) in enumerate([("gemini-3.1-flash-lite", "all 410-bug results"), ("gpt-5-mini", "cross-model analysis")]):
        y = 2.0 + i * 0.72
        rbox(s, 7.15, y, 5.63, 0.62, fill=PANEL, line=RULE, radius=0.16)
        text(s, 7.35, y, 3.3, 0.62, m, size=15, font=MONO, bold=True, anchor="m")
        text(s, 10.5, y, 2.2, 0.62, d, size=15, color=MUTED, anchor="m", align="r")
    text(s, 7.15, 3.6, 5.6, 0.45, "Statistics", size=15, font=MONO, bold=True, color=MUTED)
    tests = [("permutation χ²", "RQ1"), ("rule of three", "RQ2"), ("bootstrap CI", "RQ3"),
             ("paired bootstrap Δκ", "RQ4b"), ("McNemar exact", "RQ4"), ("sign test", "RQ4b")]
    for i, (t_, rq) in enumerate(tests):
        x = 7.15 + (i % 2) * 2.86
        y = 4.05 + (i // 2) * 0.92
        rbox(s, x, y, 2.77, 0.8, fill=PANEL, line=RULE, radius=0.14)
        text(s, x + 0.12, y + 0.02, 2.55, 0.45, t_, size=15, bold=True, anchor="m")
        text(s, x + 0.12, y + 0.4, 2.55, 0.36, rq, size=15, font=MONO, color=SEC["P2"], bold=True, anchor="m")

def s17_rq12(prs, num):
    s = content_slide(prs, "P3", "RQ1 · RQ2", "Three Types Dominate — and Nothing Escapes", num)
    col = SEC["P3"]
    text(s, 0.55, 1.55, 7.0, 0.45, "RQ1 · type mix (scientific, pre-fix)", size=15, font=MONO, bold=True, color=MUTED)
    segs = [(198 / 410, T["CHK"], "Checking 48.3%"), (175 / 410, T["ALG"], "Algorithm 42.7%"), (28 / 410, T["ASN"], ""), (9 / 410, T["REL"], "")]
    hbar(s, 0.55, 2.05, 7.0, 0.85, segs, size=15)
    legend(s, 0.55, 2.95, [(T["ASN"], "Assignment 6.8%"), (T["REL"], "other types 2.2%")])
    text(s, 0.55, 3.45, 3.2, 1.0, "97.8%", size=44, font=MONO, bold=True, color=col)
    text(s, 3.1, 3.55, 4.4, 0.9, "of bugs fall in three Control and Data Flow types", size=17, color=INK, anchor="m")
    rbox(s, 0.55, 4.6, 7.0, 1.55, fill=PANEL, line=RULE, radius=0.06)
    text(s, 0.75, 4.66, 6.6, 0.45, "Does the mix differ by project? (permutation χ²)", size=17, bold=True)
    for i, (a, b) in enumerate([("scientific", "p = 0.096   no, at the 5% level"), ("few-shot", "p = 0.010   yes")]):
        text(s, 0.75, 5.1 + i * 0.47, 1.9, 0.45, a, size=15, font=MONO, bold=True, color=col)
        text(s, 2.65, 5.1 + i * 0.47, 4.8, 0.45, b, size=15, font=MONO, color=INK)
    text(s, 0.55, 6.25, 7.0, 0.6, "Timing/Serialization: 0 of 1,640 — expected for single-threaded unit-test failures.", size=15, color=MUTED)
    x = 7.95
    rbox(s, x, 1.55, 4.83, 5.25, fill=INK, radius=0.04)
    text(s, x + 0.3, 1.7, 4.3, 0.45, "RQ2 · “Other” escape", size=15, font=MONO, bold=True, color="9AA3B5")
    text(s, x + 0.3, 2.2, 4.3, 1.2, [[("0", {"size": 64}), (" / 1,640", {"size": 26, "color": "C9CFDB"})]], size=64, font=MONO, bold=True, color=PANEL)
    text(s, x + 0.3, 3.4, 4.3, 0.8, "classifications chose “Other”, although it was offered every time", size=16, color="C9CFDB")
    for i, (a, b) in enumerate([("≤ 0.2%", "95% upper bound on the escape rate"), ("28·17·13", "rare types were still used"),
                                ("366", "labels written without a taxonomy")]):
        y = 4.35 + i * 0.78
        text(s, x + 0.3, y, 1.75, 0.7, a, size=17, font=MONO, bold=True, color="8FD3A2", anchor="m")
        text(s, x + 2.1, y, 2.6, 0.7, b, size=15, color="C9CFDB", anchor="m", spacing=0.98)

def s18_rq3(prs, num):
    s = content_slide(prs, "P3", "RQ3 · AGREEMENT", "Pre-Fix Labels Mostly Hold Up", num)
    col = SEC["P3"]
    text(s, 0.55, 1.5, 3.0, 1.1, "70.2%", size=50, font=MONO, bold=True, color=col)
    text(s, 3.55, 1.62, 4.0, 0.9, "of pre-fix labels match the post-fix reference exactly", size=18, anchor="m")
    text(s, 8.0, 1.45, 4.8, 0.75, [[("κ", {"font": SANS}), (" = 0.505", {}), ("  moderate", {"color": MUTED, "size": 16, "font": SANS, "bold": False})]],
         size=30, font=MONO, bold=True, color=INK, anchor="m")
    text(s, 8.0, 2.2, 4.8, 0.45, "95% CI [0.433, 0.574]", size=15, font=MONO, color=MUTED, bold=True)
    text(s, 0.55, 2.85, 12.0, 0.45, "What happens to all 410 bugs (scientific):", size=15, font=MONO, bold=True, color=MUTED)
    hbar(s, 0.55, 3.3, 12.23, 0.95, [(0.702, POST, "exact match 70.2%"), (0.273, "E0A43A", "near miss 27.3%"), (0.024, PRE, "")], size=17)
    legend(s, 10.1, 4.3, [(PRE, "unrelated 2.4%")])
    text(s, 0.55, 4.3, 9.3, 0.5, "near miss = one label is the other's runner-up, or both share a family", size=15, color=MUTED)
    rbox(s, 0.55, 4.95, 6.0, 1.85, fill=PANEL, line=RULE, radius=0.06)
    text(s, 0.75, 5.02, 3.0, 0.45, "Four tiers", size=17, bold=True)
    text(s, 3.2, 5.05, 3.2, 0.42, "scientific   few-shot", size=15, font=MONO, color=MUTED, align="r")
    for i, (a, b, c) in enumerate([("T1 strict", "70.2%", "66.6%"), ("T2 top-2", "97.1%", "98.5%"), ("T4 kappa", "0.505", "0.389")]):
        text(s, 0.75, 5.5 + i * 0.42, 2.4, 0.42, a, size=16, font=MONO, bold=True)
        text(s, 3.15, 5.5 + i * 0.42, 3.25, 0.42, f"{b:>7}   {c:>7}", size=16, font=MONO, align="r", color=INK)
    rbox(s, 6.78, 4.95, 6.0, 1.85, fill=PANEL2, radius=0.06)
    text(s, 7.0, 5.02, 5.6, 0.45, "Reference level", size=17, bold=True)
    text(s, 7.0, 5.45, 5.6, 1.3, [[("Two fix-aware runs still agree only ", {}), ("76.3%", {"bold": True, "font": MONO}),
        (" of the time; pre-fix is ", {}), ("~6 points", {"bold": True}), (" below. Much of the rest is ODC boundary ambiguity.", {})]],
        size=16, color=INK, spacing=1.05)

def s19_changes(prs, num):
    s = content_slide(prs, "P3", "RQ3 · LABEL CHANGES", "When the Fix Is Visible, Labels Move — but Nearby", num)
    col = SEC["P3"]
    pos = {"ALG": (0.75, 4.55), "CHK": (5.1, 4.55), "ASN": (2.93, 1.75)}
    W, H = 2.0, 0.9
    def centre(k):
        x, y = pos[k]; return x + W / 2, y + H / 2
    edges = [("ALG", "CHK", "75", 7.0), ("ALG", "ASN", "12", 2.25), ("CHK", "ASN", "11", 2.25)]
    for a, b, n, w in edges:
        (x1, y1), (x2, y2) = centre(a), centre(b)
        line(s, x1, y1, x2, y2, color=col, width=w)
    for a, b, n, w in edges:
        (x1, y1), (x2, y2) = centre(a), centre(b)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        rbox(s, mx - 0.45, my - 0.26, 0.9, 0.52, fill=PAPER, line=col, lw=1.5, radius=0.3)
        text(s, mx - 0.45, my - 0.26, 0.9, 0.52, n, size=18, font=MONO, bold=True, align="c", anchor="m")
    for k, (x, y) in pos.items():
        rbox(s, x, y, W, H, fill=T[k], radius=0.2)
        text(s, x, y, W, H, TYPE_NAME[k].split("/")[0], size=16, bold=True, color=PANEL, align="c", anchor="m")
    text(s, 0.55, 5.65, 7.1, 0.45, "edge = bugs whose label moved between the two types", size=15, color=MUTED)
    text(s, 0.55, 6.08, 7.1, 0.8, [[("80.3%", {"bold": True, "font": MONO, "color": col}),
        (" of changes stay inside these three types — the boundary human raters also confuse.", {})]], size=16, spacing=1.05)
    stats = [
        ("29.8%", "of bugs change label (122 of 410)"),
        ("0.051", "total variation distance: the overall mix barely moves"),
        ("38 / 37", "Algorithm → Checking vs Checking → Algorithm"),
        ("43 / 54", "Closure changes on the Algorithm–Checking boundary"),
    ]
    for i, (big, d) in enumerate(stats):
        y = 1.6 + i * 1.3
        rbox(s, 7.95, y, 4.83, 1.15, fill=PANEL, line=RULE, radius=0.08)
        text(s, 8.12, y, 1.85, 1.15, big, size=22, font=MONO, bold=True, color=col, anchor="m")
        text(s, 10.0, y, 2.7, 1.15, d, size=15, color=MUTED, anchor="m", spacing=1.0)

def s20_rq4a(prs, num):
    s = content_slide(prs, "P3", "RQ4a · TAXONOMY", "Without a Taxonomy, Labels Cannot Be Counted", num)
    col = SEC["P3"]
    rows = [("zero-free", "no taxonomy", 366, "15.1%", "8.38", PRE), ("few-open", "ODC + examples", 6, "66.6%", "1.29", MUTED),
            ("scientific-open", "ODC + loop", 6, "70.2%", "1.45", POST)]
    text(s, 0.55, 1.55, 7.2, 0.45, "distinct labels for 410 bugs", size=15, font=MONO, bold=True, color=MUTED)
    for i, (c, d, n, rep, ent, cc) in enumerate(rows):
        y = 2.05 + i * 1.0
        text(s, 0.55, y, 2.4, 0.45, c, size=16, font=MONO, bold=True)
        text(s, 0.55, y + 0.42, 2.4, 0.4, d, size=15, color=MUTED)
        box(s, 2.95, y + 0.12, max(0.12, 4.3 * n / 366), 0.6, fill=cc)
        text(s, 2.95 + max(0.12, 4.3 * n / 366) + 0.12 if n < 300 else 3.05, y + 0.12, 1.2, 0.6, str(n), size=20, font=MONO, bold=True,
             color=INK if n < 300 else PANEL, anchor="m")
    rbox(s, 0.55, 5.15, 7.2, 1.65, fill=PANEL2, radius=0.06)
    text(s, 0.75, 5.22, 6.8, 0.45, "Chart_9, zero-free, same bug:", size=15, font=MONO, bold=True, color=MUTED)
    text(s, 0.75, 5.62, 6.8, 1.1, [[("− ", {"color": PRE, "font": MONO, "bold": True}), ("“Improper input validation logic”", {})],
                                   [("+ ", {"color": POST, "font": MONO, "bold": True}), ("“Incorrect boundary condition logic”", {})]],
         size=17, space_after=4)
    text(s, 8.15, 1.55, 4.6, 0.45, "label identical in both modes", size=15, font=MONO, bold=True, color=MUTED)
    for i, (c, d, n, rep, ent, cc) in enumerate(rows):
        y = 2.05 + i * 1.0
        text(s, 8.15, y, 2.3, 0.85, rep, size=26, font=MONO, bold=True, color=cc if cc != MUTED else INK, anchor="m")
        text(s, 10.3, y, 2.45, 0.85, [[(f"entropy {ent} bits", {})]], size=15, font=MONO, color=MUTED, anchor="m")
    rbox(s, 8.15, 5.15, 4.63, 1.65, fill=PANEL, line=col, lw=1.5, radius=0.08)
    box(s, 8.15, 5.15, 0.1, 1.65, fill=col)
    text(s, 8.4, 5.2, 4.25, 1.55, [[("342 of 366", {"bold": True, "font": MONO}), (" free-form labels occur only once. A taxonomy is a precondition for aggregate analysis.", {})]],
         size=16, anchor="m", spacing=1.05)


def s21_rq4b(prs, num):
    s = content_slide(prs, "P3", "RQ4b · SCIENTIFIC LOOP", "The Loop Beats a Strong Few-Shot Prompt", num)
    col = SEC["P3"]
    text(s, 0.55, 1.5, 4.7, 0.95, [[("Δκ", {"font": SANS}), (" = +0.115", {})]], size=36, font=MONO, bold=True, color=col, anchor="m")
    text(s, 0.55, 2.42, 4.7, 0.8, "95% CI [0.026, 0.208]\np ≈ 0.012, paired bootstrap", size=15, font=MONO, color=MUTED, bold=True)
    text(s, 0.55, 3.2, 4.7, 0.6, [[("κ ", {}), ("0.389", {"bold": True}), (" few-shot → ", {}), ("0.505", {"bold": True, "color": col}), (" scientific", {})]], size=18)
    facts = [("6 / 6", "projects with higher κ (sign test p = 0.016)"),
             ("p = 0.221", "raw McNemar: few-shot's 265 Algorithm labels inflate chance agreement"),
             ("Closure", "gain +0.065, CI includes 0")]
    for i, (a, b) in enumerate(facts):
        y = 3.95 + i * 0.96
        rbox(s, 0.55, y, 4.7, 0.84, fill=PANEL, line=RULE, radius=0.1)
        text(s, 0.7, y, 1.55, 0.84, a, size=16, font=MONO, bold=True, color=INK, anchor="m")
        text(s, 2.25, y, 2.95, 0.84, b, size=15, color=MUTED, anchor="m", spacing=1.0)
    cx, cy, cw, chh = 5.55, 1.55, 7.23, 5.3
    rbox(s, cx, cy, cw, chh, fill=PANEL, line=RULE, radius=0.03)
    text(s, cx + 0.25, cy + 0.1, 6.7, 0.45, "per-project kappa, pre-fix vs post-fix", size=15, font=MONO, bold=True, color=MUTED)
    data = [("Chart", 0.672, 0.349), ("Math", 0.603, 0.537), ("Lang", 0.546, 0.497), ("Mockito", 0.499, 0.272),
            ("Time", 0.480, 0.212), ("Closure", 0.359, 0.294)]
    bw = 5.0
    for i, (p_, sci, few) in enumerate(data):
        y = cy + 0.62 + i * 0.7
        text(s, cx + 0.2, y, 1.3, 0.62, p_, size=15, bold=True, anchor="m")
        box(s, cx + 1.5, y + 0.03, bw * few / 0.75, 0.26, fill="B9BEC7")
        box(s, cx + 1.5, y + 0.33, bw * sci / 0.75, 0.26, fill=col)
        text(s, cx + 1.5 + bw * sci / 0.75 + 0.08, y + 0.18, 0.9, 0.45, f"{sci:.2f}", size=15, font=MONO, bold=True, anchor="m")
    legend(s, cx + 0.25, cy + 4.85, [("B9BEC7", "few-shot"), (col, "scientific")])

def s22_mechanisms(prs, num):
    s = content_slide(prs, "P3", "QUALITATIVE · CROSS-MODEL", "Failure Modes, and What Depends on the Model", num)
    col = SEC["P3"]
    text(s, 0.55, 1.55, 6.0, 0.45, "13 manually analysed scenario bugs", size=15, font=MONO, bold=True, color=MUTED)
    modes = [
        ("Symptom-site bias", "Chart_17", "label follows where the exception surfaced, not what was changed"),
        ("Bug-report anchoring", "Math_90", "a fix suggested in the report becomes the label"),
        ("Surface syntax", "Math_23", "post-fix run labels the patch shape, not the ODC definition"),
        ("Underdetermined", "Lang_20", "two valid fixes imply two different ODC types"),
    ]
    for i, (m, bug, d) in enumerate(modes):
        y = 2.0 + i * 1.18
        rbox(s, 0.55, y, 6.0, 1.05, fill=PANEL, line=RULE, radius=0.08)
        box(s, 0.55, y, 0.1, 1.05, fill=PRE)
        text(s, 0.8, y + 0.05, 3.3, 0.45, m, size=17, bold=True)
        text(s, 4.4, y + 0.05, 2.0, 0.45, bug, size=15, font=MONO, bold=True, color=MUTED, align="r")
        text(s, 0.8, y + 0.48, 5.6, 0.55, d, size=15, color=MUTED)
    x = 6.85
    text(s, x, 1.55, 5.9, 0.45, "Gemini vs gpt-5-mini, same bugs & prompts", size=15, font=MONO, bold=True, color=MUTED)
    rbox(s, x, 2.0, 5.93, 1.85, fill=POST_BG, line=POST, lw=1.25, radius=0.05)
    text(s, x + 0.2, 2.05, 5.5, 0.45, "Comes from the pipeline (both models)", size=17, bold=True, color=POST)
    text(s, x + 0.2, 2.5, 5.55, 1.55, [
        [("› loop beats few-shot pre-fix: ", {}), ("6 vs 4", {"bold": True, "font": MONO})],
        [("› fix resolves ambiguity: few post-fix ", {}), ("11 · 12", {"bold": True, "font": MONO})],
        [("› same failures on Chart_17, Math_90, Lang_20", {})],
    ], size=16, space_after=3)
    rbox(s, x, 4.05, 5.93, 2.75, fill=PANEL, line=col, lw=1.25, radius=0.05)
    text(s, x + 0.2, 4.1, 5.5, 0.45, "Comes from the model", size=17, bold=True, color=col)
    text(s, x + 0.2, 4.58, 5.55, 2.15, [
        [("› loop uses the fix diff: ", {}), ("6 vs 11", {"bold": True, "font": MONO}), (" of 13", {})],
        [("› probes per run: ", {}), ("1.7 vs 3.0", {"bold": True, "font": MONO})],
        [("› only 3 of 6 correct bugs shared", {})],
        [("› loop output depends more on the model", {})],
    ], size=16, space_after=3)


def s23_threats(prs, num):
    s = content_slide(prs, "P3", "THREATS TO VALIDITY", "What Could Undermine These Results", num)
    quads = [
        ("Internal", ["LLM output is non-deterministic", "pre-fix evidence sanitized against fix leakage", "prompt names no expected distribution"]),
        ("Construct", ["agreement ≠ correctness", "modified class missing from evidence for 285 / 410 bugs", "zero-free used the earlier evidence corpus"]),
        ("External", ["6 of 17 projects; Closure 153 of 174", "corpus results from one model", "Java and Defects4J only"]),
        ("Conclusion", ["one run per bug per condition", "bootstrap / permutation values are estimates", "13-bug analysis: purposive, single rater"]),
    ]
    for i, (name, items) in enumerate(quads):
        x = 0.55 + (i % 2) * 6.2
        y = 1.6 + (i // 2) * 2.4
        rbox(s, x, y, 6.03, 2.25, fill=PANEL, line=RULE, radius=0.05)
        box(s, x, y, 6.03, 0.08, fill=SEC["P3"])
        text(s, x + 0.25, y + 0.18, 5.5, 0.5, name, size=20, bold=True)
        text(s, x + 0.25, y + 0.66, 5.6, 1.55, [[("› ", {"color": SEC["P3"], "bold": True}), (it, {})] for it in items], size=16, color=MUTED, space_after=3)
    text(s, 0.55, 6.47, 12.2, 0.42, "Also: possible pre-training exposure to Defects4J; model confidence fields are not a usable signal.", size=15, color=MUTED)


def s24_conclusion(prs, num):
    s = content_slide(prs, "P3", "CONCLUSION", "Conclusion and Future Work", num)
    col = SEC["P3"]
    text(s, 0.55, 1.55, 6.5, 0.45, "Contributions", size=15, font=MONO, bold=True, color=MUTED)
    contribs = ["Taxonomy × strategy condition space", "Open ODC with a justified “Other” escape",
                "Enforced hypothesis–probe loop with auditable transcripts", "Pre-fix / post-fix evaluation without ground truth",
                "Results on 410 bugs, analysed with two LLMs"]
    text(s, 0.55, 2.0, 6.4, 2.9, [[("✓ ", {"color": POST, "bold": True}), (c, {})] for c in contribs], size=17, space_after=7)
    text(s, 7.2, 1.55, 5.6, 0.45, "Future work", size=15, font=MONO, bold=True, color=MUTED)
    fw = ["Human reference labels for a random sample", "Grade the reasoning, not only the label",
          "Full corpus with more LLMs and consensus", "Impact, Trigger and Age attributes", "All Defects4J projects, other benchmarks"]
    text(s, 7.2, 2.0, 5.6, 2.9, [[("→ ", {"color": col, "bold": True}), (f_, {})] for f_ in fw], size=17, space_after=7)
    rbox(s, 0.55, 4.95, 12.23, 1.85, fill=INK, radius=0.05)
    nums = [("97.8%", "three types"), ("0 / 1,640", "escapes"), ("70.2%", "pre-fix match"), ("+0.115", "Δκ from the loop")]
    for i, (big, lab) in enumerate(nums):
        x = 0.8 + i * 3.02
        text(s, x, 5.1, 2.9, 0.85, big, size=30, font=MONO, bold=True, color="8FD3A2" if i != 1 else "F2C57C")
        text(s, x, 5.92, 2.9, 0.6, lab, size=16, color="C9CFDB")


REFS = [
    "[1] R. Just, D. Jalali, and M. D. Ernst, “Defects4J: A Database of Existing Faults to Enable Controlled Testing Studies for Java Programs,” ISSTA, 2014.",
    "[2] R. Chillarege et al., “Orthogonal Defect Classification — A Concept for In-Process Measurements,” IEEE TSE, vol. 18, no. 11, 1992.",
    "[3] IBM, “Orthogonal Defect Classification v5.2 for Software Design and Code,” IBM Research, 2013.",
    "[4] A. Van der Spuy and B. Fischer, “An Anatomy of 488 Faults from Defects4J Based on the Control- and Data-Flow Graph Representations of Programs,” EASE, 2025.",
    "[5] V. Sobreira et al., “Dissection of a Bug Dataset: Anatomy of 395 Patches from Defects4J,” SANER, 2018.",
    "[6] J. Jiang, Y. Xiong, and X. Xia, “A Manual Inspection of Defects4J Bugs and Its Implications for Automatic Program Repair,” Science China Information Sciences, 2019.",
    "[7] G. Colavito et al., “Large Language Models for Issue Report Classification,” Ital-IA Workshops, 2024.",
    "[8] A. Koyuncu, “Exploring Fine-Grained Bug Report Categorization with Large Language Models and Prompt Engineering,” ACM TOSEM, 2026.",
    "[9] C. Li et al., “KnowBug: Enhancing Large Language Models with Bug Report Knowledge for Deep Learning Framework Bug Prediction,” Knowledge-Based Systems, 2024.",
    "[10] S. Kang, B. Chen, S. Yoo, and J.-G. Lou, “Explainable Automated Debugging via Large Language Model-driven Scientific Debugging,” Empirical Software Engineering, 2025.",
    "[11] K. Henningsson and C. Wohlin, “Assuring Fault Classification Agreement — An Empirical Evaluation,” ISESE, 2004.",
    "[12] J. Agnelo, N. Laranjeiro, and J. Bernardino, “Using Orthogonal Defect Classification to Characterize NoSQL Database Defects,” Journal of Systems and Software, 2020.",
    "[13] J. R. Landis and G. G. Koch, “The Measurement of Observer Agreement for Categorical Data,” Biometrics, vol. 33, no. 1, 1977.",
]


def refs_slide(prs, num, part_no, items):
    s = new_slide(prs)
    box(s, 0.55, 0.42, 0.09, 0.95, fill=INK)
    text(s, 0.78, 0.30, 11.5, 0.42, [[("// ", {}), (f"{num:02d}  REFERENCES", {})]], size=15, font=MONO, bold=True, color=INK)
    text(s, 0.78, 0.66, 12.0, 0.75, f"References ({part_no}/2)", size=30, bold=True)
    text(s, 0.78, 1.65, 11.95, 5.1, items, size=15, color=INK, space_after=10, spacing=1.05)
    line(s, 0.55, 6.95, 12.78, 6.95, color=RULE, width=1.0)
    text(s, 10.6, 6.98, 2.2, 0.48, f"{num:02d}", size=18, font=MONO, bold=True, color=INK, align="r", anchor="m")


def thanks_slide(prs, num):
    s = new_slide(prs)
    box(s, 0, 0, 13.333, 7.5, fill=INK)
    text(s, 0.8, 2.3, 11.7, 1.2, [[("- ", {"color": "F1959B"}), ("questions?", {"color": "F1959B"})]], size=48, font=MONO, bold=True, align="c")
    text(s, 0.8, 3.45, 11.7, 1.2, [[("+ ", {"color": "8FD3A2"}), ("thank you", {"color": "8FD3A2"})]], size=48, font=MONO, bold=True, align="c")
    text(s, 0.8, 5.1, 11.7, 0.5, "Orthogonal Defect Classification on Defects4J Using an LLM-Driven Scientific Approach", size=18, color="C9CFDB", align="c")
    text(s, 10.6, 6.98, 2.2, 0.48, f"{num:02d}", size=18, font=MONO, bold=True, color="C9CFDB", align="r", anchor="m")


def build():
    prs = Presentation(str(DECK))
    sld_ids = prs.slides._sldIdLst
    for sld_id in list(sld_ids):
        prs.part.drop_rel(sld_id.rId)
        sld_ids.remove(sld_id)

    s01_title(prs)
    builders = [s02_roadmap, s03_why, s04_odc, s05_related, s06_problem, s07_idea, s08_rqs,
                s09_pipeline, s10_evidence, s11_conditions, s12_prompts, s13_loop, s14_eval, s15_reference, s16_setup,
                s17_rq12, s18_rq3, s19_changes, s20_rq4a, s21_rq4b, s22_mechanisms, s23_threats, s24_conclusion]
    for i, b in enumerate(builders, start=2):
        b(prs, i)
    refs_slide(prs, 25, 1, REFS[:7])
    refs_slide(prs, 26, 2, REFS[7:])
    thanks_slide(prs, 27)
    prs.save(str(DECK))
    print(f"wrote {DECK.name}: {len(prs.slides)} slides")


if __name__ == "__main__":
    build()

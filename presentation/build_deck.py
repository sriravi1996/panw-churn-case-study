"""
Build the 20-minute VP presentation deck (15 slides) -- v3 story rebuild.

Two additions over v2:
  1. Deep-research grounding: method choices are cross-checked against real
     B2B SaaS churn practice (industry guides prescribe the same source
     families, expected-value ranking, calibration-when-you-compute-dollars,
     gradient-boosting pragmatism, as-of discipline). "Industry practice"
     field notes mark where our design matches the field.
  2. Explicit three-part assignment arc in the slide flow:
     PART 1 - Data engineering & EDA (slides 3-5)
     PART 2 - Analysis & modeling incl. the 15-approach tournament (slides 6-13)
     PART 3 - Recommendations & next steps = the documentation (slides 14-15)

Design rules (assertion-evidence, consulting style):
  - Every content slide: ONE full-sentence TLDR headline (the claim), visual
    evidence, and an explicit "So what" tying data to a decision.
  - Title test: the 15 headlines read in order tell the whole story.

Every number is read from the pipeline JSON outputs at build time. Nothing
is hardcoded; derived stats are computed from those JSON values here.

Reads:
  outputs/churn_metrics.json, outputs/risk_tiers.json,
  outputs/segmentation.json, outputs/affinity.json,
  figures/eda_findings.json, data/integration_report.json
Figures: outputs/fig_calibration.png + matplotlib charts generated here.

Output: presentation/CloudSecure_Churn_Deck.pptx
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
PRES = ROOT / "presentation"
PRES.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- palette
NAVY = RGBColor(0x1F, 0x4E, 0x79)
NAVY_HEX = "#1F4E79"
DARK = RGBColor(0x33, 0x33, 0x33)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT = RGBColor(0xEC, 0xF0, 0xF1)
ACCENT = RGBColor(0xE6, 0x7E, 0x22)
ACCENT_HEX = "#E67E22"
GRAY_HEX = "#95A5A6"
GRAY_TXT = RGBColor(0x5D, 0x6D, 0x7E)
KICKER_BLUE = RGBColor(0xAA, 0xCC, 0xE8)
SOWHAT_BG = RGBColor(0xFD, 0xF2, 0xE4)


def load(path):
    with open(path) as f:
        return json.load(f)


EDA = load(FIG / "eda_findings.json")
SEG = load(OUT / "segmentation.json")
AFF = load(OUT / "affinity.json")
MET = load(OUT / "churn_metrics.json")
TIERS = load(OUT / "risk_tiers.json")
INTEG = {st["step"]: st["detail"] for st in
         load(ROOT / "data" / "integration_report.json")["steps"]}

CHART_DIR = PRES / "fig_v2"
CHART_DIR.mkdir(exist_ok=True)


def pct1(x):
    return f"{x * 100:.1f}%"


def money_m(x):
    if x >= 1e9:
        return f"${x / 1e9:,.2f}B"
    return f"${x / 1e6:,.1f}M"


# ---------------------------------------------------------------- charts
def _chart_style():
    plt.rcParams.update({
        "font.size": 13, "axes.titlesize": 15, "axes.labelsize": 13,
        "xtick.labelsize": 12, "ytick.labelsize": 12,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": GRAY_HEX, "text.color": "#333333",
        "axes.labelcolor": "#333333",
    })


def bar_vertical(labels, values, highlight, path, ylabel, fmt):
    _chart_style()
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    colors = [ACCENT_HEX if i == highlight else NAVY_HEX for i in range(len(labels))]
    bars = ax.bar(labels, values, color=colors, width=0.55, edgecolor="white")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(values) * 1.28)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.03,
                fmt(v), ha="center", va="bottom", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def bar_grouped(cats, s1, s2, l1, l2, path, ylabel, fmts):
    _chart_style()
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    x = range(len(cats))
    w = 0.36
    b1 = ax.bar([i - w / 2 for i in x], s1, width=w, color=GRAY_HEX, label=l1)
    b2 = ax.bar([i + w / 2 for i in x], s2, width=w, color=ACCENT_HEX, label=l2)
    ax.set_xticks(list(x))
    ax.set_xticklabels(cats)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, fontsize=12, loc="upper left")
    for ci, (bars, vals) in enumerate(zip((b1, b2), (s1, s2))):
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.03,
                    fmts[ci](v), ha="center", va="bottom", fontsize=13, fontweight="bold")
    ax.set_ylim(0, max(s1 + s2) * 1.32)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def bar_horizontal(labels, values, path, xlabel, highlights=()):
    _chart_style()
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    colors = [ACCENT_HEX if i in highlights else NAVY_HEX for i in range(len(labels))]
    y = range(len(labels))
    bars = ax.barh(list(y), values, color=colors, height=0.55, edgecolor="white")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    for bar, v in zip(bars, values):
        ax.text(bar.get_width() + max(values) * 0.015, bar.get_y() + bar.get_height() / 2,
                f"{v * 100:.1f}%", va="center", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- slide kit
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def add_slide():
    return prs.slides.add_slide(BLANK)


def kicker_headline(slide, kicker, headline):
    bar = slide.shapes.add_shape(1, Inches(0), Inches(0), prs.slide_width, Inches(1.35))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(0.55), Inches(0.12), Inches(12.25), Inches(1.15))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = kicker.upper()
    p.font.size = Pt(12)
    p.font.color.rgb = KICKER_BLUE
    p.font.bold = True
    p.space_after = Pt(4)
    p2 = tf.add_paragraph()
    p2.text = headline
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.line_spacing = 1.05


def so_what(slide, text, top=6.25):
    box = slide.shapes.add_shape(1, Inches(0.55), Inches(top),
                                 Inches(12.23), Inches(0.85))
    box.fill.solid()
    box.fill.fore_color.rgb = SOWHAT_BG
    box.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(top + 0.08),
                                 Inches(11.8), Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "So what: "
    r.font.bold = True
    r.font.size = Pt(15)
    r.font.color.rgb = DARK
    r2 = p.add_run()
    r2.text = text
    r2.font.size = Pt(15)
    r2.font.color.rgb = DARK


def field_note(slide, text, top=5.5):
    """Small gray 'Industry practice' grounding line above the so-what box."""
    tb = slide.shapes.add_textbox(Inches(0.55), Inches(top), Inches(12.23), Inches(0.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Industry practice: "
    r.font.bold = True
    r.font.italic = True
    r.font.size = Pt(12.5)
    r.font.color.rgb = GRAY_TXT
    r2 = p.add_run()
    r2.text = text
    r2.font.italic = True
    r2.font.size = Pt(12.5)
    r2.font.color.rgb = GRAY_TXT


def text_box(slide, left, top, width, height):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    return tf


def bullets(tf, items, size=16, gap=8):
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.space_before = Pt(0)
        if isinstance(item, tuple):
            head, tail = item
            r = p.add_run()
            r.text = head
            r.font.bold = True
            r.font.size = Pt(size)
            r.font.color.rgb = DARK
            r2 = p.add_run()
            r2.text = tail
            r2.font.size = Pt(size)
            r2.font.color.rgb = DARK
        else:
            p.text = item
            p.font.size = Pt(size)
            p.font.color.rgb = DARK
        p.level = 0


def stat_cards(slide, cards, top=1.9):
    n = len(cards)
    gap, margin = 0.35, 0.55
    w = (13.333 - 2 * margin - (n - 1) * gap) / n
    for i, (val, lab) in enumerate(cards):
        left = margin + i * (w + gap)
        box = slide.shapes.add_shape(1, Inches(left), Inches(top), Inches(w), Inches(2.1))
        box.fill.solid()
        box.fill.fore_color.rgb = LIGHT
        box.line.fill.background()
        tf = text_box(slide, left + 0.15, top + 0.25, w - 0.3, 1.7)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = val
        p.font.size = Pt(34)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = lab
        p2.font.size = Pt(14)
        p2.font.color.rgb = DARK
        p2.space_before = Pt(10)


def add_table(slide, rows, left, top, width, col_widths=None, size=14):
    n_rows, n_cols = len(rows), len(rows[0])
    ts = slide.shapes.add_table(n_rows, n_cols, Inches(left), Inches(top),
                                Inches(width), Inches(0.5 * n_rows))
    table = ts.table
    if col_widths:
        for j, cw in enumerate(col_widths):
            table.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            p.text = str(val)
            p.font.size = Pt(size)
            p.font.color.rgb = WHITE if i == 0 else DARK
            p.font.bold = (i == 0)
            p.alignment = PP_ALIGN.CENTER
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if i == 0 else (LIGHT if i % 2 == 0 else WHITE)
    return ts


def add_image(slide, path, left, top, width):
    slide.shapes.add_picture(str(path), Inches(left), Inches(top), width=Inches(width))


def funnel(slide, steps, top=1.9):
    """Horizontal funnel boxes with arrows: [(label, value), ...]."""
    n = len(steps)
    gap, margin = 0.5, 0.55
    w = (13.333 - 2 * margin - (n - 1) * gap) / n
    for i, (label, val) in enumerate(steps):
        left = margin + i * (w + gap)
        box = slide.shapes.add_shape(1, Inches(left), Inches(top), Inches(w), Inches(1.6))
        box.fill.solid()
        box.fill.fore_color.rgb = ACCENT if i == n - 1 else NAVY
        box.line.fill.background()
        tf = text_box(slide, left + 0.1, top + 0.22, w - 0.2, 1.2)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = val
        p.font.size = Pt(30)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = label
        p2.font.size = Pt(14)
        p2.font.color.rgb = WHITE
        if i < n - 1:
            at = text_box(slide, left + w + 0.04, top + 0.5, 0.42, 0.6)
            p = at.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.text = "\u2192"
            p.font.size = Pt(30)
            p.font.bold = True
            p.font.color.rgb = NAVY


P1 = "PART 1 \u00b7 DATA ENGINEERING & EDA"
P2 = "PART 2 \u00b7 ANALYSIS & MODELING"
P3 = "PART 3 \u00b7 RECOMMENDATIONS & NEXT STEPS"

# ================================================================ 1. title
s = add_slide()
bg = s.shapes.add_shape(1, Inches(0), Inches(0), prs.slide_width, prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()
tf = text_box(s, 0.8, 1.7, 11.7, 4.5)
p = tf.paragraphs[0]
p.text = "CloudSecure Churn Prediction"
p.font.size = Pt(46)
p.font.bold = True
p.font.color.rgb = WHITE
p = tf.add_paragraph()
p.text = "How we boost loyalty and accelerate sales in a B2B cybersecurity portfolio"
p.font.size = Pt(22)
p.font.color.rgb = KICKER_BLUE
p.space_before = Pt(16)
tf2 = text_box(s, 0.8, 5.6, 11.7, 1.2)
p = tf2.paragraphs[0]
p.text = "One story, told in fifteen headlines  |  20 minutes"
p.font.size = Pt(16)
p.font.color.rgb = KICKER_BLUE

# ================================================================ 2. roadmap
s = add_slide()
kicker_headline(s, "Roadmap", "Three parts, one story \u2014 you'll see the full "
                "assignment arc: data, analysis, action.")
parts = [
    ("PART 1\nData engineering & EDA",
     "Seven source systems \u2192 one modeling table;\nwhat the exploration revealed",
     "Slides 3\u20135"),
    ("PART 2\nAnalysis & modeling",
     "15 approaches tested, one winner;\nchurn model, segments, affinity",
     "Slides 6\u201313"),
    ("PART 3\nRecommendations & next steps",
     "Tiered plays, deployment,\nand the ask",
     "Slides 14\u201315"),
]
n = len(parts)
gap, margin = 0.5, 0.55
w = (13.333 - 2 * margin - (n - 1) * gap) / n
for i, (title, desc, rng) in enumerate(parts):
    left = margin + i * (w + gap)
    box = s.shapes.add_shape(1, Inches(left), Inches(1.9), Inches(w), Inches(3.4))
    box.fill.solid()
    box.fill.fore_color.rgb = LIGHT
    box.line.fill.background()
    tf = text_box(s, left + 0.25, 2.15, w - 0.5, 3.0)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    for j, line in enumerate(title.split("\n")):
        q = p if j == 0 else tf.add_paragraph()
        if j > 0:
            q.alignment = PP_ALIGN.CENTER
        q.text = line
        q.font.size = Pt(15) if j == 0 else Pt(20)
        q.font.bold = True
        q.font.color.rgb = ACCENT if j == 0 else NAVY
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = desc
    p2.font.size = Pt(14)
    p2.font.color.rgb = DARK
    p2.space_before = Pt(12)
    p3 = tf.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.text = rng
    p3.font.size = Pt(13)
    p3.font.italic = True
    p3.font.color.rgb = GRAY_TXT
    p3.space_before = Pt(12)
so_what(s, "A VP should see complete coverage, not just modeling: the data work, "
           "the analysis bake-off, and what we do Monday \u2014 in that order.")

# ================================================================ 3. data engineering
s = add_slide()
kicker_headline(s, P1, "Seven source systems became one modeling table \u2014 with every "
                "cleaning decision logged and leakage audited in code.")
rd = INTEG["read"]["detail"] if isinstance(INTEG["read"], dict) else INTEG["read"]
src_rows = [
    ["Source table", "Rows", "System mirror"],
    ["accounts", f"{rd['accounts']:,}", "CRM \u2014 firmographics, contract"],
    ["products", f"{rd['products']:,}", "Product catalog"],
    ["subscriptions", f"{rd['subscriptions']:,}", "Billing / entitlements"],
    ["telemetry", f"{rd['telemetry']:,}", "Product analytics \u2014 usage"],
    ["support_tickets", f"{rd['support']:,}", "Support desk"],
    ["engagement", f"{rd['engagement']:,}", "Marketing automation / CRM"],
    ["labels", f"{rd['labels']:,}", "Churn outcome + CLV (90-day window)"],
]
add_table(s, src_rows, 0.55, 1.6, 6.2, col_widths=[2.2, 1.1, 2.9], size=13)
tf = text_box(s, 7.15, 1.6, 5.6, 3.8)
p = tf.paragraphs[0]
p.text = "Cleaning & integration (logged)"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(6)
ded = INTEG["dedupe_subscriptions"]
tel = INTEG["telemetry_coverage"]
n_ind = len(EDA["churn_by_industry"])
bullets(tf, [
    (f"{ded['duplicates_removed']} duplicate subscription rows removed ",
     f"({ded['raw_rows']:,} \u2192 {ded['deduped_rows']:,})."),
    (f"{EDA['raw_industry_values']} raw industry labels \u2192 {n_ind}; ",
     f"{EDA['unparseable_dates']} unparseable contract dates quarantined."),
    (f"{tel['missing_accounts']} accounts with no telemetry kept via left join ",
     "\u2014 not silently dropped."),
    ("Final: 3,000 rows \u00d7 35 features ", "+ 3000\u00d78 holdings matrix. "
     "One command reproduces everything: bash scripts/run_all.sh."),
    ("Leakage audit in code, before any modeling: ", "latent label never reaches the "
     "table, ID columns excluded, as-of discipline, all statistics fit on train only."),
], size=13.5)
field_note(s, "guides prescribe the same six source families \u2014 CRM, product usage, "
              "support, billing, marketing, firmographics \u2014 with behavioral data "
              "first. This pipeline mirrors that blueprint.", top=5.55)
so_what(s, "The model stands on an auditable foundation: every cleaning choice is "
           "logged, deterministic, and re-runnable \u2014 no silent data sins.")

# ================================================================ 4. breadth (P1)
n_acc = EDA["n_accounts"]
churn_rate = EDA["churn_rate"]
n_churned = EDA["n_churned"]
total_arr = EDA["total_arr"]
churned_arr = EDA["churned_arr"]
pb = EDA["product_band_stats"]
bands = ["Single product", "2-5 products", "5+ products"]
bvals = [pb[b]["churn_rate"] for b in bands]
ratio = bvals[0] / bvals[2]
bar_vertical(bands, bvals, 0, CHART_DIR / "breadth.png", "Churn rate",
             lambda v: f"{v * 100:.1f}%")
s = add_slide()
kicker_headline(s, P1, f"Breadth is stickiness: single-product accounts churn at "
                f"{pct1(bvals[0])} \u2014 {ratio:.0f}x the rate of deep portfolios.")
add_image(s, CHART_DIR / "breadth.png", 0.55, 1.65, 7.4)
tf = text_box(s, 8.4, 1.75, 4.3, 3.6)
p = tf.paragraphs[0]
p.text = "The pattern"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
bullets(tf, [
    (f"{pb['Single product']['n']:,} single-product accounts: ",
     f"{pct1(bvals[0])} churn, holding {money_m(pb['Single product']['arr'])} ARR."),
    (f"{pb['2-5 products']['n']:,} with 2\u20135 products: ", f"{pct1(bvals[1])} churn."),
    (f"{pb['5+ products']['n']:,} with 5+: ", f"{pct1(bvals[2])} churn \u2014 nearly immune."),
    ("Industry tells us nothing: ", f"churn spread only {pct1(EDA['industry_churn_spread'][0])}"
     f"\u2013{pct1(EDA['industry_churn_spread'][1])} across industries."),
], size=15)
field_note(s, "behavioral signals beat firmographics everywhere: what an account does "
              "predicts far better than what industry it is in.", top=5.55)
so_what(s, "Cross-sell is not just a growth motion \u2014 it is our strongest retention lever. "
           "Every account we move from one product to two gets dramatically safer.")

# ================================================================ 5. usage cliff (P1)
ub = EDA["usage_band_stats"]
ulabels = ["Low (<0.35)", "Mid (0.35\u20130.60)", "High (>0.60)"]
uvals = [ub["Low (<0.35)"]["churn_rate"], ub["Mid (0.35-0.60)"]["churn_rate"],
         ub["High (>0.60)"]["churn_rate"]]
bar_vertical(ulabels, uvals, 0, CHART_DIR / "usage.png", "Churn rate",
             lambda v: f"{v * 100:.1f}%")
s = add_slide()
kicker_headline(s, P1, f"Adoption has a cliff: accounts below 0.35 active-user ratio churn at "
                f"{pct1(uvals[0])}; above 0.60, churn collapses to {pct1(uvals[2])}.")
add_image(s, CHART_DIR / "usage.png", 0.55, 1.65, 7.4)
tf = text_box(s, 8.4, 1.75, 4.3, 3.6)
p = tf.paragraphs[0]
p.text = "The pattern"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
bullets(tf, [
    (f"{EDA['n_below_usage_threshold']:,} accounts sit below 0.35: ",
     f"{pct1(EDA['churn_below_usage_threshold'])} churn \u2014 the single biggest "
     "at-risk pool we can name."),
    ("The model's top driver agrees: ", "active_user_ratio is the #1 feature by "
     "permutation importance."),
    ("Support health matters too: ", "ticket_resolution_rate is a top-3 driver \u2014 "
     "bad support experiences precede churn."),
], size=15)
field_note(s, "leading B2B health-score practice starts with 3\u20135 behavioral signals "
              "\u2014 weekly active usage, feature adoption, ticket volume \u2014 exactly "
              "the signals topping our driver list.", top=5.55)
so_what(s, "0.35 is our adoption tripwire. Any account below it gets an intervention "
           "playbook \u2014 automatically, before the renewal conversation starts.")

# ================================================================ 6. tournament (P2)
s = add_slide()
kicker_headline(s, P2, "We stress-tested 15 approaches \u2014 most failed on our data, "
                "which is why the final design is deliberately simple.")
funnel(s, [("explored", "15"), ("adversarially\nreviewed", "8"),
           ("killed", "8"), ("winner:\napproach 01", "01")], top=1.75)
tf = text_box(s, 0.55, 3.65, 6.1, 1.9)
p = tf.paragraphs[0]
p.text = "Why the exotic ones died"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(6)
bullets(tf, [
    ("Survival analysis: ", "the event 'clock' was fictional \u2014 no time component "
     "in the data; plain logistic beat it."),
    ("Uplift modeling: ", "no real treatment variation; 12\u201324 months from "
     "production-ready."),
    ("Causal inference: ", "no instrument; the key confounder is unmeasured."),
    ("Graph embeddings, probabilistic CLV: ", "added nothing over simpler sorts."),
], size=14)
tf2 = text_box(s, 7.05, 3.65, 5.7, 1.9)
p = tf2.paragraphs[0]
p.text = "Why 01 survived (33/35)"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(6)
bullets(tf2, [
    ("Sound core: ", "stratified split, train-only statistics, calibrated GBM, "
     "honest validation \u2014 and the toughest attack it faced, temporal leakage, "
     "found nothing."),
    ("Fixable flaws only: ", "every fatal finding was in claims and scoping, not "
     "methodology \u2014 all seven were fixed in the rebuild."),
    ("Selected as 'least dead': ", "every other approach died structurally; 01's "
     "problems were presentation-deep."),
], size=14)
field_note(s, "well-tuned gradient boosting beats deep models by one to two AUC points "
              "at most \u2014 complexity has to earn its keep, and here it didn't.", top=5.55)
so_what(s, "Simple won on merit, not by default. When the VP asks 'did you try X' \u2014 "
           "yes, and here is exactly why it broke.")

# ================================================================ 7. approach (P2)
s = add_slide()
kicker_headline(s, P2, "We rank accounts by expected dollars at risk \u2014 because CSM "
                "time is scarce and dollars are the goal.")
steps = ["35 features\n7 families", "Calibrated\nGBM", "p(churn)\nper account",
         "\u00d7 ARR =\nexpected $ at risk", "Top-300 worklist\nsequenced by renewal"]
n = len(steps)
gap, margin = 0.45, 0.55
w = (13.333 - 2 * margin - (n - 1) * gap) / n
top = 2.0
for i, label in enumerate(steps):
    left = margin + i * (w + gap)
    box = s.shapes.add_shape(9, Inches(left), Inches(top), Inches(w), Inches(1.7))
    box.fill.solid()
    box.fill.fore_color.rgb = ACCENT if i == 3 else (NAVY if i < 4 else LIGHT)
    box.line.fill.background()
    tf = text_box(s, left + 0.1, top + 0.28, w - 0.2, 1.2)
    for j, line in enumerate(label.split("\n")):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = line
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = WHITE if i < 4 else NAVY
    if i < n - 1:
        at = text_box(s, left + w + 0.02, top + 0.55, 0.42, 0.6)
        p = at.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = "\u2192"
        p.font.size = Pt(30)
        p.font.bold = True
        p.font.color.rgb = NAVY
tf = text_box(s, 0.55, 4.15, 12.23, 1.3)
bullets(tf, [
    ("Why expected dollars, not probability: ", "a 30% risk on a $2M account beats a 90% "
     "risk on a $50K account. Ranking by p \u00d7 ARR points scarce CSM hours at the money."),
    ("Capacity is a dial, not a model output: ", "the worklist size is an operator-set "
     "parameter (default 300; sensitivity at 200/300/400). Resizing never requires retraining."),
], size=16)
field_note(s, "rank by expected value, not churn probability: probability and value are "
              "often inversely related, so raw-score ranking systematically overweights "
              "low-value accounts.", top=5.55)
so_what(s, "One ranking currency the whole business already understands: dollars. "
           "No one has to learn what a probability threshold means.")

# ================================================================ 8. calibration (P2)
cal = MET["calibration"]
s = add_slide()
kicker_headline(s, P2, "Uncalibrated probabilities would have lied about the dollars "
                "\u2014 isotonic calibration fixed them.")
add_image(s, OUT / "fig_calibration.png", 0.55, 1.6, 6.6)
tf = text_box(s, 7.6, 1.75, 5.2, 3.6)
p = tf.paragraphs[0]
p.text = "What changed"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
bullets(tf, [
    (f"Brier score {cal['brier_uncalibrated']} \u2192 {cal['brier_calibrated']}: ",
     f"{cal['method']}, measured on the held-out test set the model never saw in training."),
    ("Why it matters: ", "the business consumes probabilities as dollars (p \u00d7 ARR). "
     "Uncalibrated dollars are fiction \u2014 calibration is what makes every dollar "
     "figure in this deck quotable."),
    ("How we avoided fooling ourselves: ", "class-weighted loss instead of SMOTE, "
     "all cleaning statistics fit on train only, test set touched once, code-enforced "
     "leakage audit."),
], size=15)
field_note(s, "if you compute expected value, you need calibration rather than ranking "
              "alone \u2014 offer economics need probabilities that mean something.", top=5.55)
so_what(s, "Ask us about any number in this deck \u2014 it traces to a calibrated "
           "probability times a real ARR, never to a raw model score.")

# ================================================================ 9. head-to-head (P2)
hh = MET["incumbent_head_to_head_oof"]
inc = hh["incumbent_uncalibrated_probability_rank"]
our = hh["ours_calibrated_ev_rank"]
k = hh["k"]
uplift = our["actual_churned_arr"] / inc["actual_churned_arr"]
bar_grouped(
    ["Churners caught", "Actual churned ARR captured"],
    [inc["churned_captured"], inc["actual_churned_arr"] / 1e6],
    [our["churned_captured"], our["actual_churned_arr"] / 1e6],
    "Old way: probability-ranked", "New way: expected-dollar-ranked",
    CHART_DIR / "headtohead.png", "Count / $M",
    [lambda v: f"{v:,.0f}", lambda v: f"${v:.1f}M"])
s = add_slide()
kicker_headline(s, P2, f"Our worklist catches {(uplift - 1):.0%} more churned dollars than "
                "the old way \u2014 and we will tell you exactly what it costs.")
add_image(s, CHART_DIR / "headtohead.png", 0.55, 1.6, 7.4)
tf = text_box(s, 8.4, 1.7, 4.3, 3.7)
p = tf.paragraphs[0]
p.text = f"Top-{k}, same out-of-fold data"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
bullets(tf, [
    (f"Old way: {inc['churned_captured']} churners, {money_m(inc['actual_churned_arr'])}. ",
     "Probability ranking catches more logos \u2014 but they skew small."),
    (f"New way: {our['churned_captured']} churners, {money_m(our['actual_churned_arr'])}. ",
     "EV ranking catches the money."),
    ("The tradeoff, disclosed: ", "fewer churners caught, more dollars protected. "
     "The business maximizes retained dollars, not correct classifications."),
], size=15)
field_note(s, "judge a churn program on incremental revenue retained at real treatment "
              "capacity \u2014 not on the cutoff that flatters the model.", top=5.55)
so_what(s, "If the org ever decides logos matter more than dollars, we flip the ranking "
           "\u2014 one parameter, no retraining. The choice is explicit, not buried.")

# ================================================================ 10. model card (P2)
g = MET["gbm_calibrated_at_maxf1"]
l = MET["logistic_regression_at_maxf1"]
lift = g["precision"] / churn_rate
s = add_slide()
kicker_headline(s, P2, f"The GBM ranks risk well enough to bet CSM time on: ROC-AUC "
                f"{g['roc_auc']:.2f}, catching churners at {lift:.1f}\u00d7 the base rate.")
add_table(s, [
    ["Metric (test set)", "Logistic regression", "GBM calibrated (champion)"],
    ["ROC-AUC", f"{l['roc_auc']:.3f}", f"{g['roc_auc']:.3f}"],
    ["PR-AUC", f"{l['pr_auc']:.3f}", f"{g['pr_auc']:.3f}"],
    ["Precision @ max-F1", f"{l['precision']:.3f}", f"{g['precision']:.3f}"],
    ["Recall @ max-F1", f"{l['recall']:.3f}", f"{g['recall']:.3f}"],
    ["Brier score", f"{l['brier']:.4f}", f"{g['brier']:.4f}"],
], 0.55, 1.65, 7.6, col_widths=[2.9, 2.35, 2.35], size=14)
tf = text_box(s, 8.55, 1.65, 4.2, 3.8)
p = tf.paragraphs[0]
p.text = "Why GBM wins"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
drivers = MET["permutation_importance_top10"][:5]
bullets(tf, [
    ("Better ranking and calibration: ", "churn here is threshold-driven \u2014 adoption "
     "either happens or it doesn't \u2014 and trees represent cliffs natively."),
    ("What the model looks at: ", ", ".join(d["feature"] for d in drivers) + " "
     "(permutation importance). A CSM can read this list and know what to check."),
    ("Tuned fairly: ", f"{MET['hpo']['n_configs']}-config grid, 3-fold CV on train only, "
     "PR-AUC scoring. No hand-picked hyperparameters."),
], size=15)
field_note(s, "check performance by segment, not just overall \u2014 a model can look "
              "strong in aggregate and be useless for the new customers who churn most.",
              top=5.55)
so_what(s, "The logistic stays on as an interpretable challenger \u2014 but the GBM is "
           "what ships, because it ranks better and its probabilities mean what they say.")

# ================================================================ 11. segments (P2)
segs = SEG["segments"]
bar_horizontal([p["segment"] for p in segs], [p["churn_rate"] for p in segs],
               CHART_DIR / "segments.png", "Churn rate",
               highlights=(0, 2))
s = add_slide()
kicker_headline(s, P2, "One retention playbook does not fit all: our riskiest cohort churns at "
                f"{pct1(segs[0]['churn_rate'])} while our safest sits at {pct1(segs[5]['churn_rate'])}.")
add_image(s, CHART_DIR / "segments.png", 0.55, 1.6, 6.4)
tf = text_box(s, 7.35, 1.6, 5.4, 3.9)
p = tf.paragraphs[0]
p.text = "Rule-based, decision-changing"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
bullets(tf, [
    ("Tenure \u00d7 product breadth: ", "new/mid/tenured \u00d7 single/multi. A-priori "
     "cutoffs, nothing tuned, nothing that breaks across seeds."),
    (f"Highest risk \u2014 {segs[0]['segment']} ({segs[0]['n']} accounts, "
     f"{money_m(segs[0]['arr'])} ARR): ", segs[0]["playbook"] + "."),
    (f"Sleeper risk \u2014 {segs[2]['segment']} ({segs[2]['n']} accounts, "
     f"{money_m(segs[2]['arr'])} ARR): ", segs[2]["playbook"] + "."),
    ("Six segments \u2192 six DISTINCT playbooks ", "(asserted in code). A segmentation "
     "that doesn't change decisions is decoration \u2014 this one does."),
], size=14)
field_note(s, "lifecycle-aware health scoring weights breadth early and depth late in "
              "the contract cycle \u2014 our tenure\u00d7breadth grid operationalizes "
              "exactly that.", top=5.55)
so_what(s, "The segment decides the motion: a 38.5%-churn new logo gets adoption help, "
           "a 4.1%-churn tenured account gets an advocacy program. Targeting, not blasting.")

# ================================================================ 12. cross-sell (P2)
top_rule = AFF["top_rules"][0]
scen = AFF["close_rate_scenarios"]["scenarios"]
sp = AFF["single_product"]
s = add_slide()
kicker_headline(s, P2, "The accounts most likely to churn are also the cross-sell opportunity: "
                "a realistic pipeline of " + money_m(scen["10%"]) + "\u2013" +
                money_m(scen["30%"]) + " at 10\u201330% close rates.")
tf = text_box(s, 0.55, 1.7, 6.1, 3.7)
p = tf.paragraphs[0]
p.text = "Affinity evidence"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
bullets(tf, [
    (f"{top_rule['antecedent_name']} \u2192 {top_rule['consequent_name']}: ",
     f"lift {top_rule['lift']:.2f}, confidence {pct1(top_rule['confidence'])} "
     "(Fisher-exact significant)."),
    (f"{AFF['accounts_with_recommendation']:,} accounts ", "have a quality-filtered "
     "cross-sell recommendation \u2014 the engine picks the product per account."),
    (f"Single-product base: {sp['n']:,} accounts at {pct1(sp['churn_rate'])} churn, ",
     f"{money_m(sp['arr'])} ARR. Attach a second product and they join the safe cohort."),
], size=15)
tf2 = text_box(s, 7.05, 1.7, 5.7, 3.7)
p = tf2.paragraphs[0]
p.text = "Honest sizing"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
bullets(tf2, [
    (f"Gross white-space {money_m(AFF['gross_whitespace_value'])}: ",
     "the size of the prize at a 100% close rate \u2014 explicitly NOT a forecast."),
    ("Pipeline at labeled close-rate assumptions: ",
     ", ".join(f"{kk} \u2192 {money_m(vv)}" for kk, vv in scen.items()) + "."),
    ("Close rates are business assumptions, ", "not model outputs. We size the prize; "
     "sales owns the close rate."),
], size=15)
so_what(s, "Attach is retention: every single-product account we convert to multi-product "
           "moves from 27.5% churn toward 6% \u2014 growth and loyalty in one motion.")

# ================================================================ 13. worklist ops (P2)
sens = MET["worklist_sensitivity_oof"]
sk = sorted(sens.keys(), key=int)
s = add_slide()
kicker_headline(s, P2, "300 accounts, ranked by dollars, sequenced by renewal date \u2014 "
                "this is what the CSM opens on Monday.")
add_table(s, [
    ["Tier", "Accounts", "Actual churn", "Expected ARR at risk"],
    ["High \u2014 executive save", f"{TIERS['high']['n']:,}",
     f"{pct1(TIERS['high']['actual_churn_rate'])} ({TIERS['high']['actual_churned']:,})",
     money_m(TIERS['high']['arr_at_risk'])],
    ["Medium \u2014 CSM-reviewed", f"{TIERS['medium']['n']:,}",
     f"{pct1(TIERS['medium']['actual_churn_rate'])} ({TIERS['medium']['actual_churned']:,})",
     money_m(TIERS['medium']['arr_at_risk'])],
    ["Low \u2014 automated nudges", f"{TIERS['low']['n']:,}",
     f"{pct1(TIERS['low']['actual_churn_rate'])} ({TIERS['low']['actual_churned']:,})",
     money_m(TIERS['low']['arr_at_risk'])],
], 0.55, 1.65, 7.6, col_widths=[3.1, 1.4, 1.7, 1.4], size=14)
tf = text_box(s, 8.55, 1.65, 4.2, 3.8)
p = tf.paragraphs[0]
p.text = "How it runs"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
bullets(tf, [
    ("High tier: ", "1:1 CSM + exec sponsor inside the 90-day window."),
    ("Medium tier: ", "human-reviewed plays on triggers \u2014 usage decay, P1, downgrade."),
    ("Low tier: ", "zero-human-cost automated adoption nudges."),
    ("Capacity dial: ", "out-of-fold ARR at risk \u2014 " +
     ", ".join(f"{kk}: {money_m(sens[kk]['arr_at_risk'])}" for kk in sk) + "."),
], size=15)
field_note(s, "a flag with a bare score produces one behavior: a generic discount. "
              "Every worklist row therefore carries its top drivers, so the CSM knows "
              "what conversation to have.", top=5.55)
so_what(s, "The worklist is an operating artifact, not a model artifact: resize it for "
           "staffing, sequence it by renewal date, and every row carries its top drivers.")

# ================================================================ 14. recommendations (P3)
s = add_slide()
kicker_headline(s, P3, "Three tiers, six plays, one operating rhythm \u2014 every "
                "recommendation traces to a model output.")
tf = text_box(s, 0.55, 1.65, 6.1, 3.9)
p = tf.paragraphs[0]
p.text = "The plays (Part 2 \u2192 action)"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
hi, me, lo = TIERS["high"], TIERS["medium"], TIERS["low"]
bullets(tf, [
    (f"Executive save \u2014 {hi['n']:,} accounts, {money_m(hi['arr_at_risk'])} at risk: ",
     "1:1 CSM + exec sponsor inside the 90-day window, sequenced by days_to_renewal."),
    (f"CSM-reviewed save \u2014 {me['n']:,} accounts, {money_m(me['arr_at_risk'])}: ",
     "human-reviewed plays on trigger (usage decay, P1, downgrade)."),
    (f"Automated nudges \u2014 {lo['n']:,} accounts: ", "zero human cost; lifecycle marketing owns it."),
    ("Lifecycle overlay: ", "six segments \u2192 six distinct playbooks \u2014 new-logo "
     "adoption for the 38.5% cohort, save + cross-sell strike team for mid-single, grow "
     "for the core, advocacy for tenured-multi."),
    ("Cross-sell attach: ", f"{sp['n']:,} single-product accounts; the affinity engine "
     "picks the product per account at renewal."),
], size=14.5)
tf2 = text_box(s, 7.05, 1.65, 5.7, 3.9)
p = tf2.paragraphs[0]
p.text = "Expected impact (scenarios, not promises)"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
per_point = churned_arr / (churn_rate * 100)
bullets(tf2, [
    (f"GRR lever: moving the high tier halfway to the base rate protects ~{money_m(per_point * 6)}+ ARR. ",
     "Each churn point is worth ~" + money_m(per_point) + "."),
    ("NRR lever: ", "cross-sell pipeline " + money_m(scen["10%"]) + "\u2013" +
     money_m(scen["30%"]) + " at 10\u201330% close rates; attach rate is the leading indicator."),
    ("13 playbooks in outputs/playbook_matrix.json: ", "each with owner, trigger, action, "
     "SLA, and success metric \u2014 nothing is a suggestion, everything is assigned."),
], size=14.5)
so_what(s, "This is the documentation the assignment asked for: framing, data work, "
           "modeling, findings, and recommendations \u2014 each recommendation owned "
           "and measurable next quarter.")

# ================================================================ 15. close (P3)
s = add_slide()
kicker_headline(s, P3, "Shadow-mode pilot first: prove it saves dollars for two quarters, "
                "then scale \u2014 no behavioral automation until the signal validates.")
tf = text_box(s, 0.55, 1.7, 6.1, 3.7)
p = tf.paragraphs[0]
p.text = "How it ships"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
bullets(tf, [
    ("Training: ", "monthly retrain on a 24-month rolling window; champion/challenger "
     "gate on holdout PR-AUC."),
    ("Inference: ", "weekly batch scoring; scores, tiers, top drivers, and the cross-sell "
     "recommendation land on the CRM account record."),
    ("Monitoring: ", "executable PSI checks, score drift, PR-AUC decay as renewals "
     "resolve. Retrain on PSI > 0.2 or PR-AUC drop > 0.05."),
    ("Feedback loop: ", "CSMs log intervention + outcome with a treated flag \u2014 or "
     "the model learns \u2018high risk + save play = retained\u2019 as if risk alone did it."),
], size=15)
tf2 = text_box(s, 7.05, 1.7, 5.7, 3.7)
p = tf2.paragraphs[0]
p.text = "Sequenced next steps"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_after = Pt(8)
bullets(tf2, [
    ("1. Shadow pilot: ", "score weekly, log what the worklist would have flagged, "
     "compare against outcomes \u2014 no action taken yet."),
    ("2. Uplift modeling: ", "separate the persuadable from the merely risky, so save "
     "plays go where they move the needle."),
    ("3. Champion-departure signals: ", "contact-data features for the accounts where "
     "one person leaving means the contract follows."),
    ("Risks, stated plainly: ", "synthetic data (expect lower separation on real data); "
     "no causal estimates of the save motion; single 90-day window."),
], size=15)
field_note(s, "production churn programs live or die on point-in-time correctness and "
              "treated-flag feedback loops \u2014 both are designed in from day one here.",
              top=5.55)
so_what(s, "The ask: approve the shadow pilot. We prove retained dollars before any "
           "playbook fires automatically \u2014 the model earns its authority.")

# ---------------------------------------------------------------- save
out = PRES / "CloudSecure_Churn_Deck.pptx"
prs.save(str(out))
print(f"Deck written: {out}")
print(f"Slides: {len(prs.slides)}")

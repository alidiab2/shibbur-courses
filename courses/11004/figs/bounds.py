#!/usr/bin/env python3
"""11004 · bounds (§1.1) — builds the figures, assembles lessons/bounds.json AND narration/bounds.json.
Run from the repo root:  python3 courses/11004/figs/bounds.py   (FK_KEEP_GOING=1 shows every figure's problems)"""
import hashlib, json, os, re, sys
sys.path.insert(0, os.path.expanduser("~/Developer/ali-skills/ali-skills-shibbur-course/scripts"))
from fk import Fig, num

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
W = 480
HOT = "ltr"


# ---------------------------------------------------------------- vertical number line (bigger = higher)
class VA:
    """a vertical axis: the set lives ON it, a ceiling is a hatched slab above a line, a floor a slab below"""
    def __init__(s, f, xa, ytop, ybot, lo, hi, ticks=(), both=False, labels=False, step=None, only=None, until=None):
        s.f, s.xa, s.ytop, s.ybot, s.lo, s.hi = f, xa, ytop, ybot, lo, hi
        with f.group(step=step, only=only, until=until):
            f.line(xa, ybot, xa, ytop, "mut", 4, arrow="both" if both else True)
            for t in ticks:
                f.line(xa - 8, s.py(t), xa + 8, s.py(t), "mut", 3)
                if labels: f.text(xa - 24, s.py(t) + 1, num(t), "ink", 20, 600, "right", True, "mid")

    def py(s, v):
        return s.ybot - (v - s.lo) / (s.hi - s.lo) * (s.ybot - s.ytop)

    def seg(s, a, b, c="1", open_a=False, open_b=False, step=None, only=None, until=None):
        f = s.f
        ya = s.ybot - 6 if a is None else s.py(a)
        yb = s.ytop + 18 if b is None else s.py(b)
        with f.group(step=step, only=only, until=until):
            f.line(s.xa, ya, s.xa, yb, c, 12)
            if a is not None: f.dot(s.xa, ya, c, 11, hollow=open_a)
            if b is not None: f.dot(s.xa, yb, c, 11, hollow=open_b)

    def pts(s, vals, c="1", r=7, step=None, only=None, until=None):
        with s.f.group(step=step, only=only, until=until):
            for v in vals: s.f.dot(s.xa, s.py(v), c, r)

    def _hatch(s, y, x0, x1, up, c):
        d, x = "", x0 + 8
        while x + 14 <= x1 - 2:
            d += "M%s %s L%s %s " % (x, y, x + 14, y + (-18 if up else 18))
            x += 18
        s.f.path(d.strip(), c, "none", 2)

    def wall(s, v, up=True, c="2", hl=40, hr=40, label=None, lw=84, lc=None, step=None, only=None, until=None):
        """ceiling (up=True) or floor at height v; optional chip label to the right"""
        f, y, xa = s.f, s.py(v), s.xa
        with f.group(step=step, only=only, until=until):
            f.rect(xa - hl, y - 18 if up else y, hl + hr, 18, c, "soft")
            s._hatch(y, xa - hl, xa + hr, up, c)
            f.line(xa - hl, y, xa + hr, y, c, 5)
            if label is not None:
                f.chip(xa + hr + 8, y + (-17 if up else -17) + (-9 if up else 9), lw, 34, label, lc or c, ltr=True)

    def mark(s, v, label, c="good", hl=26, hr=26, tx=None, step=None, only=None, until=None):
        """the sup/inf marker: a short bar across the axis + label text to the right"""
        f, y, xa = s.f, s.py(v), s.xa
        with f.group(step=step, only=only, until=until):
            f.line(xa - hl, y, xa + hr, y, c, 5)
            f.text(xa + hr + 8 if tx is None else tx, y, label, c, 20, 700, "left", True, "mid")


def fig(h, alt):
    return Fig(W, h, alt=alt)


# ---------------------------------------------------------------- figures
def hook_fig(closing=False):
    f = fig(300, "المجموعة (2,4) على محور عمودي وسقف بينزل فوقها" if not closing else "السقف بيلزق عند 4 وأي سقف أوطى بيقطعو عدد من المجموعة")
    ax = VA(f, 150, 22, 284, 0, 11, ticks=(0, 2, 4, 6, 8), labels=True)
    ax.seg(2, 4, "1", True, True)
    f.text(190, ax.py(2.0), "A", "1", 24, 700, "left", True, "mid")
    if not closing:
        ax.wall(9, True, "2", 18, 120, "9", 56, only=2)
        ax.wall(4.5, True, "2", 18, 120, "4.5", 56, only=3)
        return f.block(kind="steps", frames=[
            "المجموعة: كل الأعداد بين \\(2\\) و\\(4\\) بدون الطرفين",
            "سقف عند \\(9\\): ولا عدد من المجموعة فوقو",
            "نزّلناه كتير، لـ \\(4.5\\) — لسا سقف. لوين بيوقف؟"], title="سقف بينزل فوق المجموعة")
    ax.wall(4, True, "good", 18, 120, "sup 4", 84, only=1)
    ax.wall(3, True, "bad", 18, 120, "3", 56, only=2)
    f.dot(150, ax.py(3.5), "bad", 9, only=2)
    f.text(168, ax.py(3.5) - 11, "3.5", "bad", 20, 700, "left", True, "mid", halo=True, only=2)
    return f.block(kind="steps", frames=[
        "نزّلنا السقف لحد ما لمس \\(4\\) — وما لمس ولا عدد من المجموعة",
        "أوطى منو، مثلاً \\(3\\): في عدد من المجموعة (\\(3.5\\)) طلع فوقو"], title="الجواب على السؤال")


def def_fig():
    f = fig(300, "مجموعة من ثلاث أعداد 1 و2 و3 مع سقف 4 وسقف مرفوض 2.5 وأرضية 0")
    ax = VA(f, 150, 22, 284, -1, 5, ticks=(0, 1, 2, 3, 4), labels=True)
    ax.pts((1, 2, 3), "1", 9)
    ax.wall(4, True, "2", 18, 100, "M=4", 84, only=2)
    ax.wall(2.5, True, "bad", 18, 100, "2.5", 56, only=3)
    f.text(190, ax.py(3), "3 ✗", "bad", 22, 700, "left", True, "mid", halo=True, only=3)
    ax.wall(0, False, "2", 18, 100, "m=0", 84, step=4)
    return f.block(kind="steps", frames=[
        "ثلاث أعداد على المحور (الأكبر فوق)",
        "سقف \\(M=4\\): كل عدد من \\(A\\) تحتو أو عليه",
        "سقف \\(2.5\\)؟ لأ — العدد \\(3\\) طلع من فوقو",
        "أرضية \\(m=0\\): كل عدد من \\(A\\) فوقها أو عليها"], title="سقف وأرضية لمجموعة صغيرة")


def panel_base(f, x0, step=None, ytop=30, ybot=270):
    return VA(f, x0 + 36, ytop, ybot, -4, 8, ticks=(-4, -2, 0, 2, 4, 6, 8), both=True, step=step)


def ex117_fig():
    f = fig(320, "ثلاث مجموعات: (1,5) و(-2,∞) والأعداد الطبيعية مع حدودها")
    # panel 1
    a1 = panel_base(f, 0, 1)
    a1.seg(1, 5, "1", True, True, step=1)
    a1.wall(5.17, True, "2", 28, 28, None, step=1)
    f.text(36 + 38, a1.py(5.17) - 8, "5.17", "2", 20, 700, "left", True, "mid", step=1)
    a1.wall(-3.4, False, "2", 28, 28, None, step=1)
    f.text(36 + 38, a1.py(-3.4) + 2, "−3.4", "2", 20, 700, "left", True, "mid", step=1)
    f.text(70, 306, "(1,5)", "ink", 20, 700, "middle", True, step=1)
    # panel 2
    a2 = panel_base(f, 160, 2)
    a2.seg(-2, None, "1", True, False, step=2)
    a2.wall(-4, False, "2", 28, 28, None, step=2)
    f.text(196 + 38, a2.py(-4) + 2, "−4", "2", 20, 700, "left", True, "mid", step=2)
    f.chip(196 + 20, 48, 100, 34, "لا سقف", "bad", step=2)
    f.text(230, 306, "(−2,∞)", "ink", 20, 700, "middle", True, step=2)
    # panel 3
    a3 = panel_base(f, 320, 3)
    a3.pts((1, 2, 3, 4, 5, 6, 7), "1", 7, step=3)
    a3.wall(0, False, "2", 28, 28, None, step=3)
    f.text(356 + 38, a3.py(0) + 2, "0", "2", 20, 700, "left", True, "mid", step=3)
    f.chip(356 + 20, 48, 100, 34, "لا سقف", "bad", step=3)
    f.text(390, 306, "ℕ", "ink", 22, 700, "middle", True, step=3)
    return f.block(kind="steps", title="مثال 1.17", frames=[
        "\\((1,5)\\): سقف \\(5.17\\) وأرضية \\(-3.4\\) — من الجهتين",
        "\\((-2,\\infty)\\): أرضية \\(-4\\) (أو \\(-\\pi\\)) بس لا سقف",
        "\\(\\mathbb N\\): أرضية \\(0\\) بس لا سقف — هاد اللي لسا ما أثبتناه"])


def arch_fig():
    f = fig(300, "الأعداد الطبيعية على المحور وسقف مجرّب وعدد طبيعي فوقو")
    ax = VA(f, 150, 22, 284, 0, 12, ticks=(0, 2, 4, 6, 8, 10))
    ax.pts(range(1, 12), "1", 6)
    for st, v in ((1, 2.5), (2, 2.5), (3, 5.2), (4, 9.4)):
        ax.wall(v, True, "2", 18, 90, "M=%g" % v, 100, only=st)
    for st, n in ((2, 3), (3, 6), (4, 10)):
        with f.group(only=st):
            f.dot(150, ax.py(n), "good", 11)
            f.text(150 - 30, ax.py(n) + 1, "n=%d" % n, "good", 22, 700, "right", True, "mid")
    return f.block(kind="steps", title="لأي سقف في عدد طبيعي فوقو", frames=[
        "نجرّب سقف للأعداد الطبيعية: \\(M=2.5\\)",
        "في \\(n=3\\) طلع فوق السقف",
        "سقف تاني \\(M=5.2\\)؟ \\(n=6\\) فوقو",
        "وكمان \\(M=9.4\\)؟ \\(n=10\\) فوقو — دايماً بنلاقي"])


def lower_fig():
    f = fig(300, "المجموعة (-∞,3) وسقف بينزل لحد 3 ثم سقف 2.8 بيقطعو عدد من المجموعة")
    ax = VA(f, 150, 22, 284, -2, 8, ticks=(0, 2, 4, 6), labels=True, both=True)
    ax.seg(None, 3, "1", False, True)
    ax.wall(6, True, "2", 18, 120, "6", 56, only=2)
    ax.wall(4, True, "2", 18, 120, "4", 56, only=2)
    ax.wall(3, True, "good", 18, 120, "sup 3", 84, only=3)
    ax.wall(2, True, "bad", 18, 120, "2", 56, only=4)
    f.dot(150, ax.py(2.5), "bad", 9, only=4)
    f.text(168, ax.py(2.5) - 11, "2.5", "bad", 20, 700, "left", True, "mid", halo=True, only=4)
    return f.block(kind="steps", title="\\(A=(-\\infty,3)\\) وسقف بينزل", frames=[
        "كل الأعداد تحت \\(3\\)، والـ \\(3\\) نفسو مش منها",
        "سقف عند \\(6\\) وسقف عند \\(4\\): الاتنين شغّالين",
        "نزّلناه لـ \\(3\\) ولزق: ما عاد ينزل",
        "أوطى منو، \\(2\\)؟ بينو وبين \\(3\\) في عدد من المجموعة (\\(2.5\\)) — فوق السقف"])


def three_panels(mode):
    """mode 'sup': example 1.21 (a panel per frame) · 'max': example 1.23 (same panels, verdicts)"""
    sup = mode == "sup"
    f = fig(320, "ثلاث مجموعات (-2,5] و(-∞,3) و[4,∞) مع السوبريموم والإنفيموم" if sup else "نفس المجموعات: هل السوبريموم والإنفيموم جوّا المجموعة")
    S = (lambda i: dict(step=i)) if sup else (lambda i: {})
    U = (lambda i: dict(step=i)) if sup else (lambda i: dict(until=i))   # sup/inf labels live until the verdict
    # panel 1 : (-2,5]
    a = panel_base(f, 0, 1 if sup else None)
    a.seg(-2, 5, "1", True, False, **S(1))
    a.mark(5, "sup 5", **U(1)); a.mark(-2, "inf −2", **U(1))
    f.text(70, 306, "(−2,5]", "ink", 20, 700, "middle", True, **S(1))
    if not sup:
        a.mark(5, "max 5", step=2)
        f.chip(58, a.py(-2) - 17, 100, 34, "min ✗", "bad", ltr=True, step=2)
    # panel 2 : (-inf,3)
    b = panel_base(f, 160, 2 if sup else None)
    b.seg(None, 3, "1", False, True, **S(2))
    b.mark(3, "sup 3", **U(2))
    f.text(230, 306, "(−∞,3)", "ink", 20, 700, "middle", True, **S(2))
    if sup:
        f.chip(218, b.py(-3) - 17, 112, 34, "لا أرضية", "bad", step=2)
    else:
        f.chip(218, b.py(-3) - 17, 112, 34, "لا أرضية", "bad", until=2)
        f.chip(218, b.py(3) - 17, 100, 34, "max ✗", "bad", ltr=True, step=3)
        f.chip(218, b.py(-3) - 17, 100, 34, "min ✗", "bad", ltr=True, step=3)
    # panel 3 : [4,inf)
    c = panel_base(f, 320, 3 if sup else None)
    c.seg(4, None, "1", False, False, **S(3))
    c.mark(4, "inf 4", **U(3))
    f.text(390, 306, "[4,∞)", "ink", 20, 700, "middle", True, **S(3))
    if sup:
        f.chip(378, c.py(7) - 17, 100, 34, "لا سقف", "bad", step=3)
    else:
        f.chip(378, c.py(7) - 17, 100, 34, "لا سقف", "bad", until=3)
        c.mark(4, "min 4", step=4)
        f.chip(378, c.py(7) - 17, 100, 34, "max ✗", "bad", ltr=True, step=4)
    if sup:
        return f.block(kind="steps", title="مثال 1.21", frames=[
            "\\((-2,5]\\): السقف الأوطى \\(5\\) والأرضية الأعلى \\(-2\\)",
            "\\((-\\infty,3)\\): \\(\\sup=3\\) — وما في أرضية أصلاً",
            "\\([4,\\infty)\\): \\(\\inf=4\\) — وما في سقف أصلاً"])
    return f.block(kind="steps", title="مثال 1.23", frames=[
        "نفس المجموعات: السوبريموم والإنفيموم من المثال اللي قبل",
        "\\((-2,5]\\): الـ \\(5\\) جوّا المجموعة فهو أكبر قيمة، والـ \\(-2\\) برّا فما في أصغر قيمة",
        "\\((-\\infty,3)\\): الـ \\(3\\) برّا المجموعة، فما في أكبر قيمة ولا أصغر",
        "\\([4,\\infty)\\): الـ \\(4\\) جوّا فهو أصغر قيمة، وما في أكبر قيمة"])


def bounded_fig():
    f = fig(300, "المجموعة (-3,1) بين أرضية -3 وسقف 1 ثم سقف وأرضية متماثلين عند 3 و-3")
    ax = VA(f, 150, 22, 284, -4, 4, ticks=(-3, -2, -1, 0, 1, 2, 3), labels=True, both=True)
    ax.seg(-3, 1, "1", True, True)
    ax.wall(1, True, "2", 18, 100, "M=1", 84, only=2)
    ax.wall(-3, False, "2", 18, 100, "m=−3", 96, only=2)
    ax.wall(3, True, "good", 18, 100, "c=3", 84, step=3)
    ax.wall(-3, False, "good", 18, 100, "−c", 84, step=3)
    return f.block(kind="steps", title="مثال 1.25: \\((-3,1)\\)", frames=[
        "المجموعة \\((-3,1)\\) بين \\(-3\\) و\\(1\\)",
        "في سقف \\(M\\) وأرضية \\(m\\): بالتالي محدودة",
        "نرفع السقف لـ \\(3\\): صار السقف والأرضية بنفس البعد عن الصفر"])


def axiom_fig():
    f = fig(300, "الأعداد النسبية اللي مربعها أقل من 2 وثقب عند جذر 2 وسقوف نسبية تنزل لحد الثقب")
    ax = VA(f, 150, 22, 284, 1.3, 1.62, ticks=(1.4, 1.5, 1.6), labels=True)
    ax.seg(None, 1.4142, "1", False, True)
    f.dot(150, ax.py(1.4142), "mut", 11, hollow=True, until=3)
    f.dot(150, ax.py(1.4142), "good", 12, step=4)
    for v in (1.6, 1.5, 1.45, 1.42):
        ax.wall(v, True, "2", 18, 70, None, step=2)
    f.text(270, ax.py(1.4142) + 24, "√2", "bad", 24, 700, "left", True, "mid", step=3, until=3)
    f.text(270, ax.py(1.4142) + 24, "√2 = sup", "good", 24, 700, "left", True, "mid", step=4)
    return f.block(kind="steps", title="لماذا المسلّمة", frames=[
        "فقط الأعداد النسبية: \\(A=\\{x\\in\\mathbb Q:\\ x^2<2\\}\\) بتوصل لحد ثقب عند \\(\\sqrt2\\)",
        "سقوف نسبية بتنزل: \\(1.6\\)، \\(1.5\\)، \\(1.45\\)، \\(1.42\\)…",
        "أوطى سقف لازم يكون \\(\\sqrt2\\)، وهاد مش نسبي — فما في أوطى سقف بـ \\(\\mathbb Q\\)",
        "بـ \\(\\mathbb R\\) الثقب مسدود: \\(\\sqrt2\\) موجود وهو السوبريموم"])


# ---------------------------------------------------------------- lesson text
B = []          # (name, block)
IX = {}


def add(name, block):
    IX[name] = len(B)
    B.append(block)
    return block


def box(name, kind, title, html):
    return add(name, {"t": "box", "kind": kind, "title": title, "html": html})


def p(name, html): return add(name, {"t": "p", "html": "<p>%s</p>" % html})
def h(name, text): return add(name, {"t": "h", "text": text})


def quiz_mc(name, prompt, opts, ans, hint, sol):
    return add(name, {"t": "quiz", "q": {"kind": "mc", "prompt": "<p>%s</p>" % prompt,
        "options": [{"v": str(i + 1), "html": o} for i, o in enumerate(opts)], "answer": [str(ans)],
        "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}})


def quiz_text(name, prompt, answers, hint, sol):
    return add(name, {"t": "quiz", "q": {"kind": "text", "prompt": "<p>%s</p>" % prompt, "answer": answers,
        "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}})


# 0 · why
add("why", {"t": "why", "html": r"<p>عندنا كل الأعداد بين \(2\) و\(4\). حطّينا فوقها <b>سقف</b>: خط ما في ولا عدد منها بيطلع فوقو. وبدنا ننزّلو أوطى وأوطى.</p><p><b>لوين بيوقف؟</b> وهل بيلمس عدد من المجموعة ولا لأ؟ هاد أساس كل النهايات اللي جاية.</p>"})
add("hook", hook_fig())

# 1 · ceiling and floor
h("h1", "1 · سقف وأرضية (חסם מלעיל וחסם מלרע)")
p("p1", "شو معنى إنه عدد «سقف» لمجموعة؟ شوف على مجموعة صغيرة.")
add("fig_def", def_fig())
box("def116", "def", "تعريف · <bdi>הגדרה 1.16</bdi>",
    r"<p>لتكن \(A\) مجموعة جزئية من \(\mathbb R\) (<bdi>תת קבוצה של הממשיים</bdi>).</p>"
    r"<ol><li><b>حدّ أعلى</b> (<bdi>חסם מלעיל</bdi>): عدد \(M\in\mathbb R\) بحيث لكل \(a\in A\) يتحقق \(a\le M\) دايماً. بنقول «\(M\) حدّ أعلى لـ \(A\)»، وإذا في واحد فـ \(A\) <b>محدودة من الأعلى</b> (<bdi>חסומה מלעיל</bdi>).</li>"
    r"<li><b>حدّ أدنى</b> (<bdi>חסם מלרע</bdi>): عدد \(m\in\mathbb R\) بحيث لكل \(a\in A\) يتحقق \(m\le a\) دايماً. وإذا في واحد فـ \(A\) <b>محدودة من الأسفل</b> (<bdi>חסומה מלרע</bdi>).</li></ol>")
add("ex117", ex117_fig())

# 2 · Archimedes
h("h2", "2 · ما في سقف للأعداد الطبيعية (משפט ארכימדס)")
p("p2", "حاسين إنه ما في سقف للأعداد الطبيعية، بس هاد لسا بالحدس. المبرهنة هاي هي اللي بتضبطو.")
add("fig_arch", arch_fig())
box("thm118", "thm", "مبرهنة أرخميدس · <bdi>משפט ארכימדס 1.18</bdi>",
    r"<p>لكل عدد حقيقي \(M\) يوجد عدد طبيعي \(n\) بحيث:</p><p>\[M\lt n\]</p><p><small>بتُقبل هون بدون برهان — الرسمة بتبيّن الفكرة.</small></p>")
quiz_text("q_arch", r"عند السقف \(M=7.3\): اكتب أصغر عدد طبيعي \(n\) بيحقق \(M\lt n\).", ["8"],
          "\\(n\\) لازم يكون أكبر من \\(7.3\\) تماماً.",
          r"الأعداد \(7\) و\(7.3\) مش أكبر من \(7.3\) بالنسبة لـ \(7\)، فأصغر واحد هو \(8\). وهيك السقف \(7.3\) مش سقف لـ \(\mathbb N\).")

# 3 · sup / inf
h("h3", "3 · أوطى سقف (סופרימום ואינפימום)")
p("p3", "إذا في سقف واحد، في سقوف كتير. شوف شو بيصير لما بننزّل السقف على هاي المجموعة.")
add("fig_lower", lower_fig())
box("cor119", "thm", "نتيجة · <bdi>מסקנה 1.19</bdi>",
    r"<p>لتكن \(A\) مجموعة جزئية من \(\mathbb R\).</p><ol><li>إذا \(M\) حدّ أعلى لـ \(A\) وكان \(M\le\tilde M\) فـ \(\tilde M\) حدّ أعلى كمان.</li>"
    r"<li>إذا \(m\) حدّ أدنى لـ \(A\) وكان \(\tilde m\le m\) فـ \(\tilde m\) حدّ أدنى كمان.</li></ol>")
p("p3b", "فمنطقي نختار <b>أوطى سقف</b> و<b>أعلى أرضية</b>.")
box("def120", "def", "تعريف · <bdi>הגדרה 1.20</bdi>",
    r"<p>لتكن \(A\) مجموعة جزئية من \(\mathbb R\).</p><ol><li>إذا \(A\) محدودة من الأعلى، أوطى حدّ أعلى لها اسمو <b>السوبريموم</b> (<bdi>סופרימום</bdi>) أو الحدّ الأعلى الأصغر (<bdi>חסם עליון</bdi>)، ورمزو \(\sup A\)</li>"
    r"<li>إذا \(A\) محدودة من الأسفل، أعلى حدّ أدنى لها اسمو <b>الإنفيموم</b> (<bdi>אינפימום</bdi>) أو الحدّ الأدنى الأكبر (<bdi>חסם תחתון</bdi>)، ورمزو \(\inf A\)</li></ol>")
box("rule_sup", "rule", "لتثبت أنّ \\(\\sup A=M\\)",
    r"<ol><li>\(M\) حدّ أعلى: كل \(a\in A\) بيحقق \(a\le M\) بدون استثناء</li><li>أي \(\tilde M\lt M\) مش حدّ أعلى: في \(a\in A\) بيحقق \(\tilde M\lt a\)</li></ol>")
quiz_mc("q_sup_why", r"لماذا \(2.8\) مش \(\sup\) للمجموعة \((-\infty,3)\)؟",
        ["لأنه جوّا المجموعة والـ \\(\\sup\\) لازم يكون برّا",
         "لأنه مش حدّ أعلى أصلاً: العدد \\(2.9\\) من المجموعة فوقو",
         "لأنه أصغر من \\(3\\) بس"], 2,
        "ما بتفرق إذا \\(2.8\\) جوّا المجموعة أو لأ — اسأل: هل هو سقف؟",
        r"\(2.8\) لازم أولاً يكون حدّ أعلى (الشرط ١). بس \(2.9\in A\) وفوقو، فالشرط ٢ مش لازم أصلاً نوصلو. وفي الخيار الأول: الـ \(\sup\) ممكن يكون جوّا المجموعة.")
add("ex121", three_panels("sup"))
quiz_text("q_sup", r"احسب \(\sup A\) للمجموعة \(A=(-7,-2]\) (اكتب عدد).", ["-2", "−2"],
          "السقف الأوطى بيلمس نهاية المجموعة من فوق.",
          r"كل عدد من \(A\) \(\le -2\)، وأي عدد أصغر من \(-2\) بيقطعو \(-2\) نفسو (وهو من \(A\)). \(-7\) هو الإنفيموم مش السوبريموم.")

# 4 · max / min
h("h4", "4 · لما السوبريموم جوّا المجموعة (מקסימום ומינימום)")
p("p4", "بأمثلة 1.21 السوبريموم مرات من المجموعة ومرات لأ. شو بيتغير إذا كان منها؟")
box("def122", "def", "تعريف · <bdi>הגדרה 1.22</bdi>",
    r"<p>لتكن \(A\) مجموعة جزئية من \(\mathbb R\) بحيث:</p><p>\[\sup A=M,\qquad \inf A=m\]</p>"
    r"<ol><li>إذا \(M\in A\) بنقول \(M\) <b>القيمة العظمى</b> (<bdi>מקסימום</bdi>) لـ \(A\)، ورمزها \(M=\max A\)</li>"
    r"<li>إذا \(m\in A\) بنقول \(m\) <b>القيمة الصغرى</b> (<bdi>מינימום</bdi>) لـ \(A\)، ورمزها \(m=\min A\)</li></ol>")
add("ex123", three_panels("max"))
quiz_mc("q_max", r"المجموعة \(A=[-1,6)\). أي جملة صحيحة؟",
        ["\\(\\min A=-1\\) و\\(\\max A=6\\)",
         "\\(\\inf A=\\min A=-1\\)، و\\(\\sup A=6\\) بس ما في \\(\\max A\\)",
         "\\(\\inf A=-1\\) بس ما في \\(\\min A\\)"], 2,
        "اسأل لكل طرف: هل هو جوّا المجموعة (نقطة ممتلئة)؟",
        r"الطرف \(-1\) مغلق فهو من \(A\) فـ \(\min A=-1\). الطرف \(6\) مفتوح فهو برّا \(A\) فـ \(\sup A=6\) بس ما في \(\max A\).")

# 5 · bounded
h("h5", "5 · محدودة من الجهتين (קבוצה חסומה)")
p("p5", "ليش ما نجمع السقف والأرضية بجملة وحدة؟")
add("fig_bdd", bounded_fig())
box("def124", "def", "تعريف · <bdi>הגדרה 1.24</bdi>",
    r"<p>مجموعة \(A\subseteq\mathbb R\) اسمها <b>محدودة</b> (<bdi>חסומה</bdi>) إذا كانت محدودة من الأعلى ومن الأسفل، يعني يوجد \(m,M\in\mathbb R\) يحققوا الآتي لكل عضو من \(A\):</p><p>\[m\le a\le M\]</p><p>أي \(A\subseteq[m,M]\)</p>")
box("key_c", "key", "بصيغة مكافئة · <bdi>הערה 1.26</bdi>",
    r"<p>\(A\) محدودة إذا وفقط إذا يوجد \(c\in\mathbb R\) موجب يحقق التالي لكل عضو في المجموعة:</p><p>\[-c\le a\le c\]</p>"
    r"<p>وإذا \(m\) و\(M\) حدّين بنختار:</p><p>\[c=\max\{|m|,|M|\}\]</p>")
quiz_text("q_c", r"للمجموعة \(A=[-5,2]\): اكتب أصغر \(c\) بيحقق \(-c\le a\le c\) لكل \(a\in A\).", ["5"],
          "قارن \\(|m|\\) و\\(|M|\\).",
          r"\(c=\max\{|-5|,|2|\}=\max\{5,2\}=5\). الـ \(2\) بس مش كافي لأنه \(-5\) بيضل برّا.")
quiz_mc("q_bdd", "أي مجموعة من هدول <b>محدودة</b>؟",
        ["\\(\\mathbb N\\)", "\\((-\\infty,0]\\)", "\\(\\{\\frac1n:\\ n\\in\\mathbb N\\}\\)", "\\(\\mathbb Z\\)"], 3,
        "لازم سقف <b>وأرضية</b> معاً.",
        r"\(\mathbb N\) أرضيتها \(0\) بس ما إلها سقف، \((-\infty,0]\) العكس، و\(\mathbb Z\) من الجهتين مفتوحة. أما \(\frac1n\) فكلها محصورة بين \(0\) و\(1\) تماماً.")

# 6 · completeness
h("h6", "6 · مسلّمة التمام (אקסיומת השלמות)")
p("p6", "كل مجموعة محدودة شفناها كان إلها أوطى سقف. هل هاد مضمون؟")
add("fig_axiom", axiom_fig())
box("ax127", "key", "مسلّمة · <bdi>אקסיומת השלמות 1.27</bdi>",
    r"<p>لتكن \(A\) مجموعة غير فارغة (<bdi>לא ריקה</bdi>) من \(\mathbb R\).</p><ol><li>إذا \(A\) محدودة من الأعلى فلها سوبريموم.</li><li>إذا \(A\) محدودة من الأسفل فلها إنفيموم.</li></ol>")
p("p6b", "وليش «غير فارغة»؟ لأنه بالفارغة كل عدد سقف، فما في أوطى سقف.")
box("cor128", "thm", "نتيجة · <bdi>מסקנה 1.28</bdi>",
    r"<p>إذا \(A\) محدودة وغير فارغة فلها سوبريموم وإنفيموم.</p>")
quiz_mc("q_ax", "أي مجموعة من هدول <b>ما إلها</b> سوبريموم؟",
        ["\\(\\mathbb N\\)", "\\([0,1)\\)", "\\(\\{\\frac1n:\\ n\\in\\mathbb N\\}\\)"], 1,
        "المسلّمة بتطلب مجموعة محدودة من الأعلى.",
        r"\(\mathbb N\) ما إلها سقف (أرخميدس) فالمسلّمة ما بتنطبق. الباقي محدودة وغير فارغة، فإلهم سوبريموم.")

# closing
h("h7", "تمرين وخلاصة")
add("mistakes", {"t": "mistakes", "title": "أخطاء الامتحان", "rows": [
    {"no": "\\(\\sup A\\) دايماً من المجموعة", "yes": "مرات بس: لو من \\(A\\) اسمو \\(\\max A\\). مثلاً \\((2,4)\\): \\(\\sup=4\\) وما في \\(\\max\\)"},
    {"no": "أي سقف هو السوبريموم", "yes": "السوبريموم هو أوطى سقف — لازم تتأكد إنه ما في أوطى منو"},
    {"no": "\\(\\mathbb N\\) محدودة لأنها فوق الصفر", "yes": "محدودة بس لو في سقف وأرضية. \\(\\mathbb N\\) أرضية بس"},
    {"no": "\\(\\sup(-\\infty,3)=\\infty\\)", "yes": "\\(\\sup=3\\)، واللانهاية مش عدد — المجموعة غير محدودة من الأسفل"}]})
add("xq", {"t": "xq", "q": r"<p>أثبت أنّ \(\sup A=1\) للمجموعة \(A=\{1-\frac1n:\ n\in\mathbb N\}\).</p>",
    "steps": [
        {"label": "١ · حدّ أعلى", "body": r"<p>\(1-\frac1n\lt1\) لكل \(n\). فكل عدد من \(A\) أصغر من \(1\)، يعني \(1\) سقف.</p>"},
        {"label": "٢ · ما في أوطى", "body": r"<p>خد أي \(\tilde M\lt1\). حسب أرخميدس في \(n\) بحيث \(n\gt\frac{1}{1-\tilde M}\)، فـ \(\frac1n\lt1-\tilde M\).</p>"},
        {"label": "٣ · النتيجة", "body": r"<p>عندها \(1-\frac1n\gt\tilde M\): عدد من \(A\) فوق \(\tilde M\)، فـ \(\tilde M\) مش سقف. إذًا \(\sup A=1\).</p>"}],
    "a": r"<p>\(\sup A=1\)، و\(1\notin A\) فما في قيمة عظمى.</p>"})
quiz_mc("q_final", r"المجموعة \(A=\{\frac1n:\ n\in\mathbb N\}\). أي جملة صحيحة؟",
        ["\\(\\inf A=\\min A=0\\)",
         "\\(\\max A=1\\)، و\\(\\inf A=0\\) بس ما في \\(\\min A\\)",
         "\\(\\inf A=1\\)"], 2,
        "اسأل: هل \\(0\\) عضو من المجموعة؟ وهل \\(1\\) عضو؟",
        r"\(1\in A\) وهو الأكبر فـ \(\max A=1\). الأعداد \(\frac1n\) بتقرّب لـ \(0\) ولا بتوصلو (أرخميدس)، فـ \(\inf A=0\) بس \(0\notin A\) فما في قيمة صغرى.")
add("close", hook_fig(True))
cards = [
    ("حدّ أعلى / أدنى (<bdi>חסם מלעיל / מלרע</bdi>)", r"\(a\le M\) لكل \(a\in A\) · \(m\le a\) لكل \(a\in A\)<br>مرفوع أو منزّل: كل حدّ أعلى منو حدّ أعلى."),
    ("السوبريموم (<bdi>סופרימום</bdi>)", r"أوطى حدّ أعلى: \(\sup A\)<br>بدّو شرطين: سقف + ما في أوطى. مرات برّا المجموعة."),
    ("الإنفيموم (<bdi>אינפימום</bdi>)", r"أعلى حدّ أدنى: \(\inf A\)<br>نفس الشرطين من التحت."),
    ("القيمة العظمى / الصغرى (<bdi>מקסימום / מינימום</bdi>)", r"\(\max A=\sup A\) فقط إذا \(\sup A\in A\)<br>\((2,4)\): \(\sup=4\) بس ما في قيمة عظمى."),
    ("محدودة (<bdi>חסומה</bdi>)", r"\(m\le a\le M\) أو \(-c\le a\le c\)<br>لازم سقف وأرضية معاً."),
    ("مبرهنة أرخميدس (<bdi>משפט ארכימדס</bdi>)", r"لكل \(M\) يوجد \(n\in\mathbb N\) بحيث \(M\lt n\)<br>يعني \(\mathbb N\) ما إلها سقف."),
    ("مسلّمة التمام (<bdi>אקסיומת השלמות</bdi>)", r"مجموعة غير فارغة ومحدودة من الأعلى ← لها \(\sup\)<br>بـ \(\mathbb Q\) غير صحيحة (\(\sqrt2\))."),
]
for i, (fr, bk) in enumerate(cards):
    add("card%d" % i, {"t": "card", "front": fr, "back": bk})

LESSON = {"slug": "bounds", "title": "السقف والأرضية: حدود مجموعات الأعداد", "he": "חסימות של תתי קבוצות של הממשיים",
          "ref": "חוברת §1.1 · עמ׳ 5–7", "minutes": 12,
          "desc": "الحدّ الأعلى والأدنى، السوبريموم والإنفيموم، القيمة العظمى والصغرى، المحدودية ومسلّمة التمام.",
          "blocks": B}


# ---------------------------------------------------------------- narration
def formulas(b):
    """TeX of every \\( \\) / \\[ \\] of a block, in the order the build counts them"""
    s = []
    if b["t"] == "steps":
        s += [b.get("title", "")] + [x["caption"] for x in b["frames"]]
    elif b["t"] == "box":
        s += [b["title"], b["html"]]
    else:
        s += [b.get("text", ""), b.get("html", "")]
    return [m.group(0) for t in s for m in re.finditer(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", t, re.S)]


def MK(name, needle):
    fs = formulas(B[IX[name]])
    for k, t in enumerate(fs):
        if needle in t: return {"math": k}
    raise SystemExit("no formula %r in %s: %s" % (needle, name, fs))


def S(name, emo, say, pause=0.4, pace="normal", frame=None, style=None):
    d = {"block": IX[name]}
    if frame: d["frame"] = frame
    d.update({"emotion": emo, "pace": pace, "pause": pause, "say": say})
    if style: d["style"] = style
    return d


def sh(t): return {"show": t}


SEG = [
    S("why", "curious", ["تخيّل السقف بينزل ببطء، سنتي سنتي. مرة بتحس إنه لمس شي… ومرة ما في شي بيلمسو ومع هيك ما بينزل أكتر. وين بيوقف بالضبط؟"], 1.0),
    S("why", "warm", ["بآخر الدرس بتجاوب بثانية. وهاد الأساس لكل النهايات اللي جاية بالمادة. يلا."], 0.4),
    S("hook", "curious", ["الدواير الفاضية على الطرفين يعني الاتنين والأربعة مش منها. خلّي بالك منها."], 0.5, frame=1),
    S("hook", "playful", ["جرّب سقف عالي، تسعة. أكيد شغّال، بس رخيص."], 0.3, frame=2),
    S("hook", "curious", ["نزّلناه كتير. لسا ما لمس شي. فكّر: لوين رح يوقف؟"], 1.0, frame=3),

    S("h1", "calm", ["أول شي: معنى كلمة سقف."], 0.4),
    S("fig_def", "calm", ["ثلاث أعداد بس، عشان نشوف المعنى بالعين."], 0.3, frame=1),
    S("fig_def", "calm", ["السقف أربعة: كل واحد منهم تحتو. هاد هو الشرط، مش أكتر."], 0.4, frame=2),
    S("fig_def", "surprised", ["والسقف اتنين ونص؟ لأ! التلاتة طالعة من فوقو. عدد واحد بيخرّب السقف كلو."], 0.6, frame=3),
    S("fig_def", "calm", ["والأرضية هي نفس الحكي مقلوب، من تحت."], 0.4, frame=4),
    S("def116", "serious", ["بالعبري بيحكوله", sh("חסם מלעיל"), "وللأرضية", sh("חסם מלרע"), ". اسم رسمي لشي شفناه بالعين."], 0.5, pace="slow"),
    S("ex117", "calm", ["المجال المفتوح من واحد لخمسة: سقف خمسة وسبعتاشر من مية، وأرضية سالب تلاتة وأربعة من عشرة. مش الوحيدين."], 0.3, frame=1),
    S("ex117", "calm", ["هون في أرضية بس. ولو اجيت تحط سقف، في عدد دايماً بيطلع فوقو."], 0.4, frame=2),
    S("ex117", "curious", ["والطبيعية؟ أرضية أكيد. بس سقف؟ حاسين إنه لأ، بس لسا ما أثبتنا."], 0.8, frame=3),

    S("h2", "curious", ["وهون بدنا إثبات."], 0.3),
    S("fig_arch", "calm", ["نجرّب سقف للطبيعية. اتنين ونص."], 0.3, frame=1),
    S("fig_arch", "playful", ["بالبساطة، التلاتة فوقو. فاتنين ونص مش سقف."], 0.3, frame=2),
    S("fig_arch", "calm", ["سقف تاني، أكبر؟ دايماً في طبيعي أكبر منو."], 0.3, frame=3),
    S("fig_arch", "excited", ["مهما كبّرت السقف، بنلاقي عدد فوقو. هاي هي المبرهنة!"], 0.5, frame=4),
    S("thm118", "serious", ["هاي اللي بنستعملها كل ما بدنا نثبت إنه شي بيصغر لحد الصفر، زي واحد على إن."], 0.4),

    S("h3", "curious", ["السقوف كتير. أي سقف بيهمنا؟"], 0.9),
    S("fig_lower", "calm", ["مجموعة كل الأعداد تحت تلاتة. التلاتة نفسها مش منها."], 0.4, frame=1),
    S("fig_lower", "calm", ["ستة سقف، وأربعة كمان. شايف؟ كل سقف بيطلّع اللي فوقو سقف."], 0.4, frame=2),
    S("fig_lower", "excited", ["وصلنا تلاتة، ولزق! هاد أوطى سقف. اسمو السوبريموم."], 0.6, frame=3, style="بصوت فيه اكتشاف"),
    S("fig_lower", "curious", ["وإذا نزّلنا شوي كمان، اتنين؟ بينو وبين تلاتة في عدد من المجموعة، فالسقف انكسر."], 0.8, frame=4),
    S("cor119", "calm", ["هاي نتيجة بسيطة، بس هي اللي بتخلّينا نحكي عن الأوطى."], 0.3),
    S("def120", "serious", ["بالعبري", sh("סופרימום"), "وللتحت", sh("אינפימום"), ". السوبريموم هو اللي لزق، والماكس هو اللي جوّا."], 0.5, pace="slow"),
    S("rule_sup", "emphatic", ["شرطين دايماً. أول شي: هو سقف. تاني شي: أي رقم أوطى منو مش سقف. هاد اللي رح يجي بالامتحان."], 0.5),
    S("ex121", "calm", ["نفس الفكرة على تلات مجموعات. هون السوبريموم خمسة والإنفيموم سالب اتنين."], 0.3, frame=1),
    S("ex121", "calm", ["وهون السوبريموم تلاتة، والأرضية؟ ما في أصلاً."], 0.3, frame=2),
    S("ex121", "calm", ["والعكس هون: الإنفيموم أربعة وما في سقف."], 0.3, frame=3),

    S("h4", "curious", ["بس هل السوبريموم دايماً جوّا المجموعة؟"], 0.9),
    S("def122", "serious", ["لما بيكون جوّا بنسمّيه", sh("מקסימום"), "وللتحت", sh("מינימום"), ". يعني السوبريموم عام، والماكس بس لما يلزق جوّا."], 0.5, pace="slow"),
    S("ex123", "calm", ["نفس المجموعات."], 0.2, frame=1),
    S("ex123", "calm", ["خمسة نقطة ممتلئة، يعني منها: ماكس. وسالب اتنين دايرة فاضية: ما في مين."], 0.5, frame=2),
    S("ex123", "surprised", ["هون التلاتة برّا. يعني ما في ماكس أصلاً، مع إنه في سوبريموم!"], 0.6, frame=3),
    S("ex123", "calm", ["والأربعة جوّا: مين. ولا ماكس لأنه ما في سقف."], 0.4, frame=4),

    S("h5", "calm", ["نجمع السقف والأرضية."], 0.3),
    S("fig_bdd", "calm", ["المجال المفتوح من سالب تلاتة لواحد."], 0.3, frame=1),
    S("fig_bdd", "calm", ["بين أرضية وسقف: هاد معنى محدودة. الاتنين لازم."], 0.4, frame=2),
    S("fig_bdd", "emphatic", ["وهاد بيعطينا صيغة أسهل: خلّي السقف والأرضية بنفس البعد عن الصفر. الأكبر بين البعدين."], 0.4, frame=3),
    S("def124", "serious", ["محدودة بالعبري", sh("חסומה"), ". لازم الجهتين مع بعض."], 0.4, pace="slow"),

    S("h6", "curious", ["بس هل لازم يكون في أوطى سقف؟"], 0.9),
    S("fig_axiom", "calm", ["نجرّب بالنسبية بس. الأعداد اللي مربعها أقل من اتنين."], 0.4, frame=1),
    S("fig_axiom", "calm", ["سقوف نسبية بتنزل وبتنزل."], 0.3, frame=2),
    S("fig_axiom", "surprised", ["بس الأوطى لازم يكون جذر اتنين، وهو مش نسبي! يعني بالنسبية: ما في أوطى سقف."], 0.8, frame=3),
    S("fig_axiom", "excited", ["بالحقيقية الثقب مسدود. هاي بالضبط المسلّمة."], 0.5, frame=4),
    S("ax127", "serious", ["بالعبري", sh("אקסיומת השלמות"), ". بنقبلها بدون برهان، وكل النهايات بتبني عليها."], 0.4, pace="slow"),

    S("h7", "warm", ["خلّينا نطبّق."], 0.3),
    S("mistakes", "emphatic", ["أخطر غلطة: تقول إنه السوبريموم دايماً من المجموعة. لأ! هو اللي لزق، والماكس هو اللي جوّا."], 0.5),
    S("xq", "calm", ["نفس الشرطين على سؤال امتحان. الأول سقف، والتاني بنستعمل أرخميدس."], 0.4),
    S("close", "warm", ["رجعنا لسؤال البداية. السقف وقف عند الأربعة، ولزق بدون ما يلمس عدد من المجموعة."], 0.5, frame=1),
    S("close", "excited", ["وأي واحد أوطى؟ بيقطعو عدد منها. سوبريموم بدون ماكس. شو قولك؟"], 1.0, frame=2),
]


def narration():
    blocks = json.dumps(B, ensure_ascii=False, separators=(",", ":"))
    segs = []
    for s in SEG:
        s = dict(s)
        s["say"] = [x for x in s["say"]]
        segs.append(s)
    return {"v": 1, "lessonHash": hashlib.sha1(blocks.encode()).hexdigest()[:8],
            "voice": {"persona": "مدرّس شاب، صاحب، بيحكي فلسطيني/شامي", "gender": "male"}, "segments": segs}


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "courses/11004/lessons"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "courses/11004/narration"), exist_ok=True)
    with open(os.path.join(ROOT, "courses/11004/lessons/bounds.json"), "w", encoding="utf-8") as fh:
        json.dump(LESSON, fh, ensure_ascii=False, indent=2); fh.write("\n")
    if "--no-narration" not in sys.argv:
        with open(os.path.join(ROOT, "courses/11004/narration/bounds.json"), "w", encoding="utf-8") as fh:
            json.dump(narration(), fh, ensure_ascii=False, indent=2); fh.write("\n")
    print("blocks:", len(B))

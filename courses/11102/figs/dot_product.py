#!/usr/bin/env python3
"""Generator for lesson 11102/dot-product: builds figures, assembles lessons/dot-product.json
and narration/dot-product.json. Run from anywhere: python3 courses/11102/figs/dot_product.py"""
import hashlib, json, math, os, re, sys
sys.path.insert(0, os.path.expanduser("~/Developer/ali-skills/ali-skills-shibbur-course/scripts"))
from fk import Fig

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # courses/11102
pol = Fig._pol


# ---------------------------------------------------------------- figures
def hook_draw(f, H_extra=False):
    """(2,3) and (-3,2) from the origin; shared by the hook and the closing."""
    O = (240, 190); s = 48
    P = lambda x, y: (O[0] + s * x, O[1] - s * y)
    f.line(40, O[1], 440, O[1], "mut", 2.5)
    f.line(O[0], 214 if not H_extra else 214, O[0], 14, "mut", 2.5)
    a, b = P(2, 3), P(-3, 2)
    f.arrow(*O, *a, c="1", w=4)
    f.arrow(*O, *b, c="2", w=4)
    f.text(a[0] + 50, a[1] + 4, "(2,3)", "1", 22, 700, ltr=True, valign="mid")
    f.text(b[0] - 6, b[1] - 20, "(-3,2)", "2", 22, 700, ltr=True)
    return O, P


def fig_hook():
    f = Fig(480, 240, alt="المتجه (2,3) والمتجه (-3,2) خارجين من نقطة الأصل وعلامة سؤال بين زاويتهم")
    O, P = hook_draw(f)
    a0, a1 = math.degrees(math.atan2(3, 2)), math.degrees(math.atan2(2, -3))
    f.curve([pol(*O, a0 + (a1 - a0) * i / 12, 46) for i in range(13)], "bad", 3.5, smooth=False)
    mid = (a0 + a1) / 2
    x, y = pol(*O, mid, 72)
    f.text(x, y, "?", "bad", 26, 800, ltr=True, valign="mid")
    return f.block("")


def fig_hook_close():
    f = Fig(480, 322, alt="نفس المتجهين: ضرب الإحداثيات بيطلع صفر فالزاوية قائمة")
    O, P = hook_draw(f, True)
    a0, a1 = math.degrees(math.atan2(3, 2)), math.degrees(math.atan2(2, -3))
    with f.group(until=2):
        f.curve([pol(*O, a0 + (a1 - a0) * i / 12, 46) for i in range(13)], "bad", 3.5, smooth=False)
        x, y = pol(*O, (a0 + a1) / 2, 72)
        f.text(x, y, "?", "bad", 26, 800, ltr=True, valign="mid")
    f.right_angle(*O, a0, a1, s=34, c="good", w=4, step=3)
    f.chip(40, 222, 190, 40, "2·(-3) = -6", c="1", size=22, ltr=True, step=2)
    f.chip(250, 222, 190, 40, "3·2 = 6", c="2", size=22, ltr=True, step=2)
    f.chip(100, 270, 280, 40, "-6 + 6 = 0", c="good", solid=True, size=24, ltr=True, step=3)
    return f.block("", "steps", [
        "نفس المتجهين من أول الدرس، وعلامة السؤال بينهم.",
        "الأولى بالأولى بتعطي \\(-6\\)، والتانية بالتانية بتعطي \\(6\\) فقط.",
        "المجموع صفر، فالزاوية قايمة. متعامدين!"], title="الجواب: الضرب السلمي بيطلع صفر")


def fig_shadow():
    s = 44; O = (190, 215)
    P = lambda x, y: (O[0] + s * x, O[1] - s * y)
    f = Fig(480, 322, alt="المتجه v الأزرق على المحور والمتجه u، ظل u على v، وحاصل ضرب الظل بطول v")
    f.line(30, O[1], 460, O[1], "mut", 2.5)
    tv = P(4, 0)
    f.arrow(*O, *tv, c="1", w=4.5)
    f.text(tv[0] + 22, tv[1] - 4, "v", "1", 24, 800, ltr=True)
    # case 1: u=(3,4)
    t1 = P(3, 4)
    with f.group(until=4):
        f.arrow(*O, *t1, c="2", w=4.5)
        f.text(t1[0] + 20, t1[1] + 2, "u", "2", 24, 800, ltr=True)
        f.angle(*O, 46, 0, math.degrees(math.atan2(4, 3)), "α", c="mut", w=3)
    with f.group(step=2, until=4):
        for k in (1, 2, 3):
            f.arrow(O[0] + s * k, O[1] - s * k * 4 / 3, O[0] + s * k, O[1] - 3, c="mut", w=2.5, dash=True)
        f.line(O[0], O[1] + 15, O[0] + 3 * s, O[1] + 15, "good", 8)
    f.text(O[0] + 1.5 * s, O[1] + 48, "3", "good", 26, 800, ltr=True, step=3, until=4)
    f.text(O[0] + 3.6 * s, O[1] - 18, "4", "1", 24, 800, ltr=True, step=4, until=4)
    f.chip(110, 272, 260, 42, "v · u = 4 · 3 = 12", c="good", solid=True, size=24, ltr=True, step=4, until=4)
    # case 2: u=(0,4)
    t2 = P(0, 4)
    with f.group(only=5):
        f.arrow(*O, *t2, c="2", w=4.5)
        f.text(t2[0] + 20, t2[1] + 4, "u", "2", 24, 800, ltr=True)
        f.right_angle(*O, 0, 90, s=22, c="mut", w=3)
        f.dot(O[0], O[1] + 15, "good", 8)
        f.text(O[0], O[1] + 48, "0", "good", 26, 800, ltr=True)
        f.chip(110, 272, 260, 42, "v · u = 4 · 0 = 0", c="good", solid=True, size=24, ltr=True)
    # case 3: u=(-3,4)
    t3 = P(-3, 4)
    with f.group(only=6):
        f.arrow(*O, *t3, c="2", w=4.5)
        f.text(t3[0] - 4, t3[1] - 18, "u", "2", 24, 800, ltr=True)
        f.angle(*O, 46, 0, 180 - math.degrees(math.atan2(4, 3)), "α", c="mut", w=3)
        f.arrow(t3[0], t3[1] + 4 + 30, t3[0], O[1] - 3, c="mut", w=2.5, dash=True)
        f.line(O[0], O[1] + 15, O[0] - 3 * s, O[1] + 15, "good", 8)
        f.text(O[0] - 1.5 * s, O[1] + 48, "-3", "good", 26, 800, ltr=True)
        f.chip(80, 272, 330, 42, "v · u = 4 · (-3) = -12", c="good", solid=True, size=24, ltr=True)
    return f.block("", "steps", [
        "متجهين طالعين من نفس النقطة، والزاوية بينهم اسمها \\(\\alpha\\) بالرسمة.",
        "ضوء نازل من فوق بزاوية قايمة على \\(v\\). الظل اللي بيوقع على \\(v\\) هو الخط الأخضر.",
        "طول الظل بيطلع \\(3\\)، وهو \\(|u|\\cos\\alpha\\) بالضبط.",
        "منضرب طول الظل \\(3\\) بطول \\(v\\) وهو \\(4\\)، فبيطلع \\(12\\). هاد هو الضرب السلمي.",
        "زاوية قايمة: الظل نقطة، صفر. شو بيصير لما الزاوية تكبر أكتر؟",
        "زاوية منفرجة: الظل انقلب للجهة التانية، فالنتيجة سالبة."],
        title="الضرب السلمي = الظل × الطول")


def fig_examples():
    f = Fig(480, 290, alt="مثالين: متجهين متعامدين ضربهم صفر ومتجهين بزاوية 45 درجة ضربهم 1، ثم مقارنة بالإحداثيات")
    O = (110, 180); s = 100
    with f.group(only=1):
        f.arrow(*O, O[0] + s, O[1], c="1", w=4.5)
        f.arrow(*O, O[0], O[1] - s, c="2", w=4.5)
        f.right_angle(*O, 0, 90, s=24, c="mut", w=3)
        f.text(O[0] + s + 14, O[1] + 8, "(1,0,0)", "1", 22, 700, "left", ltr=True)
        f.text(O[0], O[1] - s - 14, "(0,1,0)", "2", 22, 700, ltr=True)
        f.chip(60, 232, 330, 44, "1 · 1 · cos(π/2) = 0", c="good", solid=True, size=24, ltr=True)
    with f.group(only=2):
        f.arrow(*O, O[0] + s, O[1], c="1", w=4.5)
        f.arrow(*O, O[0] + s, O[1] - s, c="2", w=4.5)
        f.angle(*O, 44, 0, 45, "π/4", c="mut", w=3)
        f.text(O[0] + s + 14, O[1] + 8, "(1,0)", "1", 22, 700, "left", ltr=True)
        f.text(O[0] + s + 14, O[1] - s, "(1,1)", "2", 22, 700, "left", ltr=True)
        f.chip(60, 232, 330, 44, "1 · √2 · cos(π/4) = 1", c="good", solid=True, size=24, ltr=True)
    with f.group(only=3):
        f.text(120, 40, "بالزاوية", "mut", 22, 700)
        f.text(360, 40, "بالإحداثيات", "mut", 22, 700)
        f.chip(16, 62, 210, 52, "1·1·cos(π/2) = 0", c="1", size=20, ltr=True)
        f.chip(250, 62, 214, 52, "1·0+0·1+0·0 = 0", c="good", size=20, ltr=True)
        f.chip(16, 140, 210, 52, "1·√2·cos(π/4) = 1", c="1", size=20, ltr=True)
        f.chip(250, 140, 214, 52, "1·1+0·1 = 1", c="good", size=20, ltr=True)
    return f.block("", "steps", [
        "مثال 1.9: متجهين متعامدين. الزاوية قايمة، فالنتيجة صفر.",
        "المتجه \\((1,0)\\) و\\((1,1)\\): الزاوية \\(45^\\circ\\)، والأطوال \\(1\\) و\\(\\sqrt2\\) على الترتيب.",
        "نفس الأرقام طلعت من ضرب الخانات بدون زاوية. صدفة؟"],
        title="مثال 1.9: بالزاوية وبالأرقام")


def fig_proof():
    # v=(3,4), u=(4,3): angles beta, gamma from the x axis; alpha = beta - gamma
    s = 40; O = (50, 230)
    P = lambda x, y: (O[0] + s * x, O[1] - s * y)
    b = math.degrees(math.atan2(4, 3)); g = math.degrees(math.atan2(3, 4))
    f = Fig(480, 270, alt="المتجه v=(3,4) والمتجه u=(4,3) والزاويتين عن المحور الأفقي، وحساب جيب تمام الزاوية بينهم")
    f.line(24, O[1], 250, O[1], "mut", 2.5)
    f.arrow(*O, *P(3, 4), c="1", w=4.5)
    f.arrow(*O, *P(4, 3), c="2", w=4.5)
    f.text(P(3, 4)[0] - 4, P(3, 4)[1] - 14, "v", "1", 24, 800, ltr=True)
    f.text(P(4, 3)[0] + 18, P(4, 3)[1] + 10, "u", "2", 24, 800, ltr=True)
    with f.group(until=1):
        f.angle(*O, 140, g, b, "α", c="good", w=3.5)
    with f.group(step=2):
        f.angle(*O, 100, 0, b, "β", c="1", w=3)
        f.angle(*O, 60, 0, g, "γ", c="2", w=3)
    with f.group(only=2):
        f.text(270, 80, "cos β = 3/5", "1", 22, 700, "left", ltr=True)
        f.text(270, 112, "sin β = 4/5", "1", 22, 700, "left", ltr=True)
        f.text(270, 156, "cos γ = 4/5", "2", 22, 700, "left", ltr=True)
        f.text(270, 188, "sin γ = 3/5", "2", 22, 700, "left", ltr=True)
    with f.group(only=3):
        f.text(262, 80, "α = β − γ", "good", 22, 700, "left", ltr=True)
        f.text(262, 120, "cos α = cos(β−γ)", "ink", 22, 700, "left", ltr=True)
        f.text(262, 160, "= 12/25 + 12/25", "ink", 22, 700, "left", ltr=True)
        f.text(262, 200, "= 24/25", "good", 24, 800, "left", ltr=True)
    with f.group(only=4):
        f.text(262, 90, "|v||u|cos α", "ink", 22, 700, "left", ltr=True)
        f.text(262, 126, "= 25 · 24/25", "ink", 22, 700, "left", ltr=True)
        f.text(262, 162, "= 24", "good", 24, 800, "left", ltr=True)
        f.chip(252, 184, 218, 48, "3·4 + 4·3 = 24", c="good", solid=True, size=22, ltr=True)
    # frame 1: setting only
    return f.block("", "steps", [
        "المتجه \\(v=(3,4)\\) والمتجه \\(u=(4,3)\\) والزاوية بينهم \\(\\alpha\\) هي المطلوبة.",
        "كل متجه بيعرف زاويته عن المحور: الخانة الأولى على الطول هي \\(\\cos\\) والتانية على الطول هي \\(\\sin\\) تبعها.",
        "الزاوية \\(\\alpha\\) هي الفرق بين الزاويتين. تذكير: \\(\\cos(\\beta-\\gamma)=\\cos\\beta\\cos\\gamma+\\sin\\beta\\sin\\gamma\\) وهيك بنحسب جيب التمام.",
        "منضرب بالطولين \\(5\\) و\\(5\\) فبيطلع نفس جواب ضرب الخانات."],
        title="ليش الصيغة بالإحداثيات صحيحة؟ (في \\(\\mathbb R^2\\))")


def fig_angle():
    f = Fig(480, 262, alt="متجهين بينهم زاوية مجهولة، حساب الضرب والأطوال ثم جيب التمام يساوي نص والزاوية pi على 3")
    O = (60, 222); L = 160
    a, b = pol(*O, 20, L), pol(*O, 80, L)
    f.arrow(*O, *a, c="1", w=4.5)
    f.arrow(*O, *b, c="2", w=4.5)
    f.text(a[0] + 4, a[1] + 26, "v", "1", 24, 800, ltr=True)
    f.text(b[0] + 18, b[1] + 4, "u", "2", 24, 800, ltr=True)
    f.angle(*O, 60, 20, 80, "?", c="bad", w=3.5, until=3)
    f.angle(*O, 60, 20, 80, "π/3", c="good", w=3.5, label_c="good", step=4)
    f.chip(262, 20, 200, 40, "v = (1,1,0)", c="1", size=22, ltr=True)
    f.chip(262, 66, 200, 40, "u = (0,1,1)", c="2", size=22, ltr=True)
    f.text(272, 148, "v · u = 1", "ink", 22, 700, "left", ltr=True, step=2)
    f.text(272, 180, "|v| = |u| = √2", "ink", 22, 700, "left", ltr=True, step=2)
    f.text(272, 220, "cos α = 1/2", "ink", 24, 800, "left", ltr=True, step=3)
    f.text(272, 252, "α = π/3", "good", 26, 800, "left", ltr=True, step=4)
    return f.block("", "steps", [
        "مثال 1.12: عنا متجهين بالإحداثيات، والزاوية بينهم مجهولة.",
        "ضرب الخانات بيعطي \\(1\\)، وطول كل واحد فيهم \\(\\sqrt2\\) تماماً.",
        "منقسم على حاصل ضرب الطولين، بيطلع \\(\\cos\\alpha\\) نص. أي زاوية جيب تمامها نص؟",
        "إذن الزاوية \\(\\alpha=\\frac{\\pi}{3}\\)، يعني ستين درجة."],
        title="مثال 1.12: الزاوية من الأرقام")


def fig_orth():
    f = Fig(480, 262, alt="متجهين متعامدين: الظل صفر وحاصل الضرب السلمي صفر")
    O = (110, 200); s = 44
    f.line(24, O[1], 300, O[1], "mut", 2.5)
    f.arrow(*O, O[0] + 4 * s, O[1], c="1", w=4.5)
    f.arrow(*O, O[0], O[1] - 4 * s, c="2", w=4.5)
    f.right_angle(*O, 0, 90, s=26, c="good", w=4)
    f.dot(O[0], O[1] + 15, "good", 8)
    f.text(O[0] + 4 * s + 22, O[1] - 4, "v", "1", 24, 800, ltr=True)
    f.text(O[0] + 22, O[1] - 4 * s + 6, "u", "2", 24, 800, ltr=True)
    f.text(O[0], O[1] + 46, "0", "good", 26, 800, ltr=True)
    f.chip(310, 70, 160, 56, "v · u = 0", c="good", solid=True, size=26, ltr=True)
    return f.block("")


def fig_perp():
    s = 30; O = (140, 160)
    P = lambda x, y: (O[0] + s * x, O[1] - s * y)
    f = Fig(480, 320, alt="المتجه (3,-4) والخط المتقطع للمتجهات المتعامدة عليه وهو اتجاه (4,3)")
    f.line(20, O[1], 300, O[1], "mut", 2.5)
    f.line(O[0], 310, O[0], 20, "mut", 2.5)
    f.arrow(*O, *P(3, -4), c="1", w=4.5)
    f.text(P(3, -4)[0] + 8, P(3, -4)[1] + 28, "(3,-4)", "1", 22, 700, ltr=True)
    with f.group(step=2):
        f.line(*P(-4, -3), *P(4, 3), c="good", w=3, dash=True)
        f.arrow(*O, *P(2, 1.5), c="2", w=4.5)
        f.text(P(2, 1.5)[0] + 18, P(2, 1.5)[1] + 22, "u", "2", 24, 800, ltr=True)
        f.right_angle(*O, math.degrees(math.atan2(-4, 3)), math.degrees(math.atan2(3, 4)), s=20, c="mut", w=3)
    with f.group(step=4):
        f.dot(*P(4, 3), "good", 9)
        f.text(P(4, 3)[0] - 12, P(4, 3)[1] - 16, "(4,3)", "good", 22, 700, "right", ltr=True)
    f.text(330, 70, "u = (x, y)", "2", 22, 700, "left", ltr=True, step=2)
    f.text(330, 114, "3x − 4y = 0", "ink", 22, 700, "left", ltr=True, step=3)
    f.chip(318, 140, 150, 44, "u = t(4,3)", c="good", solid=True, size=24, ltr=True, step=4)
    f.text(322, 226, "12 − 12 = 0 ✓", "good", 22, 700, "left", ltr=True, step=5)
    return f.block("", "steps", [
        "مثال 1.14: بدنا كل المتجهات المتعامدة على \\(v=(3,-4)\\)، كلها بدون استثناء.",
        "نختار \\(u=(x,y)\\) أي متجه. المتعامدين كلهم بيجوا على خط واحد.",
        "التعامد يعني الضرب صفر، يعني \\(3x-4y=0\\) بالزبط.",
        "المعادلة \\(3x=4y\\) بتتحقق لـ \\(x=4\\) و\\(y=3\\) وأي مضاعف إلها، وهيك الجواب \\(t(4,3)\\) بالضبط.",
        "فحص: ضرب \\((3,-4)\\) في \\((4,3)\\) بيعطي \\(12-12=0\\)، تمام."],
        title="مثال 1.14: كل المتجهات المتعامدة على \\((3,-4)\\)")


def fig_vv():
    f = Fig(480, 150, alt="المتجه v وظله على نفسه هو المتجه كله، فالضرب v·v يساوي مربع الطول")
    O = (50, 60); L = 190
    f.arrow(*O, O[0] + L, O[1], c="1", w=4.5)
    f.line(O[0], O[1] + 18, O[0] + L, O[1] + 18, "good", 8)
    f.text(O[0] + L + 22, O[1] + 4, "v", "1", 24, 800, ltr=True)
    f.text(O[0] + L / 2, O[1] + 58, "|v|", "good", 24, 800, ltr=True)
    f.chip(280, 32, 186, 52, "v·v = |v|²", c="good", solid=True, size=26, ltr=True)
    return f.block("")


# ---------------------------------------------------------------- lesson text
B = []      # blocks
N = {}      # name -> index


def add(name, blk):
    if name: N[name] = len(B)
    B.append(blk)


def p(html): return {"t": "p", "html": "<p>%s</p>" % html}
def h(text): return {"t": "h", "text": text}
def box(kind, title, html): return {"t": "box", "kind": kind, "title": title, "html": html}
def mc(prompt, opts, ans, hint, sol):
    return {"t": "quiz", "q": {"kind": "mc", "prompt": "<p>%s</p>" % prompt,
            "options": [{"v": str(i + 1), "html": o} for i, o in enumerate(opts)], "answer": [str(ans)],
            "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}}
def tx(prompt, ans, hint, sol):
    return {"t": "quiz", "q": {"kind": "text", "prompt": "<p>%s</p>" % prompt, "answer": ans,
            "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}}

add("why", {"t": "why", "html":
    "<p>عندك سهمين على ورقة: \\((2,3)\\) والتاني \\((-3,2)\\) بالإحداثيات. وما معك منقلة. متعامدين ولا لا؟ خمّن قبل ما نكمّل.</p>"
    "<p>العين بتقول \"تقريباً\"، والامتحان بدو جواب أكيد. بآخر الدرس بتجاوب بضرب كم رقم.</p>"})
add("hook", fig_hook())

# 1
add("h1", h("1 · الضرب السلمي (<bdi>מכפלה סקלרית</bdi>)"))
add("p1", p("أول عملية بتاخد <b>متجهين</b> وبتطلّع <b>عدد</b> واحد. شوف كيف: بنعمل ظل."))
add("shadow", fig_shadow())
add("def18", box("def", "تعريف · <bdi>הגדרה 1.8</bdi>",
    "<p>ليكن \\(\\vec v,\\vec u\\in\\mathbb R^2,\\mathbb R^3\\) متجهين غير صفريين. الضرب السلمي بينهم:</p>"
    "<p>\\[\\vec v\\cdot\\vec u=|\\vec v|\\cdot|\\vec u|\\cos(\\alpha)\\]</p>"
    "<p>\\(0\\le\\alpha\\le\\pi\\) هي الزاوية بين المتجهين. (مش صفر: وإلا ما في زاوية.)</p>"))
add("cos", box("note", "تذكير · جدول \\(\\cos\\)",
    "<table><tr><th>\\(\\alpha\\)</th><td>\\(0\\)</td><td>\\(\\frac{\\pi}{6}\\)</td><td>\\(\\frac{\\pi}{4}\\)</td><td>\\(\\frac{\\pi}{3}\\)</td></tr>"
    "<tr><th>\\(\\cos\\)</th><td>\\(1\\)</td><td>\\(\\frac{\\sqrt3}{2}\\)</td><td>\\(\\frac{\\sqrt2}{2}\\)</td><td>\\(\\frac12\\)</td></tr>"
    "<tr><th>\\(\\alpha\\)</th><td>\\(\\frac{\\pi}{2}\\)</td><td>\\(\\frac{2\\pi}{3}\\)</td><td>\\(\\frac{3\\pi}{4}\\)</td><td>\\(\\pi\\)</td></tr>"
    "<tr><th>\\(\\cos\\)</th><td>\\(0\\)</td><td>\\(-\\frac12\\)</td><td>\\(-\\frac{\\sqrt2}{2}\\)</td><td>\\(-1\\)</td></tr></table>"))
add("q1", mc("\\(|v|=4\\) و\\(|u|=3\\) والزاوية بينهم \\(\\frac{2\\pi}{3}\\). شو الضرب السلمي؟",
    ["\\(6\\)", "\\(12\\)", "\\(-6\\)"], 3,
    "جيب التمام لزاوية منفرجة بيطلع سالب. شوفه بالجدول.",
    "حسب التعريف 1.8: \\(4\\cdot3\\cdot\\cos\\frac{2\\pi}{3}=12\\cdot(-\\frac12)=-6\\). الخيار \\(6\\) نسي الإشارة، و\\(12\\) حسب جيب التمام \\(1\\)."))

# 2
add("h2", h("2 · أمثلة: بالزاوية وبالأرقام"))
add("p2", p("جرّب التعريف على متجهين بسيطين. وبعدين خمّن: في طريقة أسهل من الزاوية؟"))
add("examples", fig_examples())

# 3
add("h3", h("3 · الضرب السلمي من الإحداثيات"))
add("p3", p("مش صدفة. المحاضر بيعطيها كادّعاء، وإحنا بنشوف ليش بالمستوى."))
add("proof", fig_proof())
add("thm110", box("thm", "ادّعاء · <bdi>טענה 1.10</bdi>",
    "<p>ليكن \\(\\vec v_1=(a_1,b_1,c_1)\\) و\\(\\vec v_2=(a_2,b_2,c_2)\\) في \\(\\mathbb R^3\\). عندها:</p>"
    "<p>\\[\\vec v_1\\cdot\\vec v_2=a_1a_2+b_1b_2+c_1c_2\\]</p>"
    "<p>وبنفس الشكل في \\(\\mathbb R^2\\):</p><p>\\[\\vec v_1\\cdot\\vec v_2=a_1a_2+b_1b_2\\]</p>"
    "<p><small>الكتيّب بيعطيها بدون برهان. الرسمة فوق بتبرهنها بالمستوى فقط.</small></p>"))
add("q3", tx("احسب \\((1,-2,2)\\cdot(3,1,-2)\\) بالإحداثيات. اكتب العدد.", ["-3", "−3"],
    "ضرب خانة بخانة، وبعدين جمع. انتبه للإشارات.",
    "حسب الادّعاء 1.10: \\(3+(-2)+(-4)=-3\\). السالب يعني زاوية منفرجة."))

# 4
add("h4", h("4 · الزاوية من الأرقام"))
add("p4", p("هلّق بنعرف الضرب وبدنا الزاوية: قسمنا الطرفين على الأطوال وبقي جيب التمام لحاله."))
add("def111", box("def", "تعريف · <bdi>הגדרה 1.11</bdi>",
    "<p>لمتجهين غير صفريين \\(\\vec v,\\vec u\\in\\mathbb R^2,\\mathbb R^3\\)، الزاوية \\(\\alpha\\) بينهم هي العدد الوحيد في \\([0,\\pi]\\) اللي بيحقق:</p>"
    "<p>\\[\\cos(\\alpha)=\\frac{\\vec v\\cdot\\vec u}{|\\vec v|\\cdot|\\vec u|}\\]</p>"))
add("angle", fig_angle())
add("q4", mc("\\(v=(1,0)\\) و\\(u=(-1,1)\\). شو الزاوية بينهم؟",
    ["\\(\\frac{\\pi}{4}\\)", "\\(\\frac{3\\pi}{4}\\)", "\\(\\frac{\\pi}{2}\\)"], 2,
    "الضرب السلمي هون سالب. هل الزاوية حادة؟",
    "الضرب \\(-1\\)، الأطوال \\(1\\) و\\(\\sqrt2\\). \\(\\cos\\alpha=-\\frac{1}{\\sqrt2}=-\\frac{\\sqrt2}{2}\\) فـ \\(\\alpha=\\frac{3\\pi}{4}\\). الخيار \\(\\frac{\\pi}{4}\\) نسي الإشارة."))

# 5
add("h5", h("5 · التعامد (<bdi>מאונכים</bdi>)"))
add("p5", p("رجعنا للظل: زاوية قايمة، ظل صفر، ضرب صفر. هاد التعريف."))
add("orth", fig_orth())
add("def113", box("def", "تعريف · <bdi>הגדרה 1.13</bdi>",
    "<p>متجهين \\(\\vec v,\\vec u\\) <b>متعامدان</b> (<bdi>מאונכים</bdi> أو <bdi>ניצבים</bdi> أو <bdi>אורתוגונלים</bdi>) إذا:</p>"
    "<p>\\[\\vec v\\cdot\\vec u=0\\]</p>"
    "<p><small>الصيغة هي التعريف، فالمتجه الصفري متعامد مع كل متجه.</small></p>"))
add("q5", mc("حسبنا \\((1,2)\\cdot(4,-2)=0\\). شو بنستنتج؟",
    ["متعامدين", "واحد منهم صفر", "متوازيين"], 1,
    "الأعداد: \\(ab=0\\) يعني واحد صفر. هل نفس الشي هون؟",
    "حسب التعريف 1.13 صفر يعني متعامدين. ولا واحد منهم صفر. الصفر هون للضرب السلمي مش للمتجهين."))
add("perp", fig_perp())

# 6
add("h6", h("6 · خصائص الضرب السلمي"))
add("p6", p("أهم خاصية: ضرب متجه بنفسه. الزاوية صفر فالظل هو كله."))
add("vv", fig_vv())
add("thm115", box("thm", "ادّعاء · <bdi>טענה 1.15</bdi>",
    "<p>ليكن \\(\\vec v,\\vec u,\\vec w\\in\\mathbb R^2,\\mathbb R^3\\) و\\(\\alpha\\in\\mathbb R\\). عندها:</p>"
    "<ul><li>\\(\\vec v\\cdot\\vec u=|\\vec v|\\cdot|\\vec u|\\cos(\\alpha)\\)</li>"
    "<li>\\(\\vec v\\cdot\\vec u=\\vec u\\cdot\\vec v\\)</li>"
    "<li>\\((\\alpha\\vec v)\\cdot\\vec u=\\alpha(\\vec v\\cdot\\vec u)\\)</li>"
    "<li>\\((\\vec v+\\vec u)\\cdot\\vec w=\\vec v\\cdot\\vec w+\\vec u\\cdot\\vec w\\)</li>"
    "<li>\\(\\vec v\\cdot\\vec v=|\\vec v|^2\\ge0\\)، والمساواة بـ \\(0\\) إذا وفقط إذا \\(\\vec v=\\vec 0\\)</li></ul>"))
add("whys", {"t": "html", "html":
    "<ul><li>التبديل: \\(|v||u|\\cos\\alpha\\) ما بتفرق مين الأول.</li>"
    "<li>الإخراج: تكبير \\(v\\) مرتين بيكبّر الظل مرتين.</li>"
    "<li>التوزيع: بنفتح الخانات بالادّعاء 1.10.</li></ul>"})
add("sumsq", box("idea", "وين بتستعملها بالامتحان",
    "<p>بنفتح \\(|v+u|^2\\) بالخصائص:</p>"
    "<p>\\[\\begin{aligned}|v+u|^2&=(v+u)\\cdot(v+u)\\\\&=|v|^2+2\\,v\\cdot u+|u|^2\\end{aligned}\\]</p>"
    "<p>ولما \\(v\\cdot u=0\\) بيضل \\(|v|^2+|u|^2\\): فيثاغورس.</p>"))
add("q6", mc("\\(|v|=2\\) و\\(|u|=3\\) و\\(v\\cdot u=1\\). احسب مربع طول المجموع \\(|v+u|^2\\) رقمياً.",
    ["\\(13\\)", "\\(25\\)", "\\(14\\)", "\\(15\\)"], 4,
    "افتح \\((v+u)\\cdot(v+u)\\). كم مرة بيطلع \\(v\\cdot u\\)؟",
    "\\(4+2\\cdot1+9=15\\). الخيار \\(13\\) نسي الحد الأوسط، و\\(14\\) كتبه مرة وحدة، و\\(25\\) جمع الأطوال ثم ربّع."))

# closing
add("hc", h("تمرين وخلاصة"))
add("mist", {"t": "mistakes", "title": "غلط شائع", "rows": [
    {"no": "الضرب السلمي بيطلع متجه.", "yes": "بيطلع <b>عدد</b> واحد."},
    {"no": "الضرب السلمي صفر يعني إنه واحد من المتجهين صفر.", "yes": "صح بس لما واحد منهم صفر. المتعامدين كمان ضربهم صفر، مثلاً \\((1,2)\\cdot(2,-1)=0\\)."},
    {"no": "الضرب سالب؟ أكيد غلطت بالحساب.", "yes": "سالب يعني زاوية منفرجة. صفر يعني قايمة."},
    {"no": "جيب تمام الزاوية هو الضرب السلمي مباشرة.", "yes": "صح بس لما \\(|v||u|=1\\). غير هيك لازم تقسم على الأطوال."}]})
add("qc1", tx("المتجهين \\((a,4)\\) و\\((2,-1)\\) متعامدين. جد العدد \\(a\\) اللي بيحقق هاد.", ["2"],
    "اكتب الضرب السلمي كمعادلة بـ \\(a\\) وساوي بصفر.",
    "التعامد يعني الضرب صفر: \\(2a-4=0\\) فـ \\(a=2\\)."))
add("qc2", mc("كل المتجهات المتعامدة على \\((2,1)\\) هي (حيث \\(t\\in\\mathbb R\\)):",
    ["\\(t(1,2)\\)", "\\(t(1,-2)\\)", "\\(t(2,1)\\)", "\\((1,-2)\\) فقط"], 2,
    "ابدأ بـ \\(2x+y=0\\) ثم اختار واحد من الحلول وكبّره بـ \\(t\\).",
    "\\(2x+y=0\\) يعني \\(y=-2x\\) فـ \\(t(1,-2)\\). \\(t(1,2)\\) غلطة إشارة، و\\(t(2,1)\\) هو نفس المتجه (مش متعامد)، و\\((1,-2)\\) نسي الضرب بـ \\(t\\) هنا."))
add("close", fig_hook_close())
add("close_p", p("ظل × طول، وصفر معناه متعامدين. هيك جاوبنا بدون منقلة."))
add("c1", {"t": "card", "front": "الضرب السلمي (<bdi>מכפלה סקלרית</bdi>) بالزاوية", "back": "<p>\\(\\vec v\\cdot\\vec u=|\\vec v||\\vec u|\\cos\\alpha\\)</p><p>الناتج عدد، وسالب لزاوية منفرجة.</p>"})
add("c2", {"t": "card", "front": "الضرب السلمي بالإحداثيات", "back": "<p>\\(a_1a_2+b_1b_2+c_1c_2\\)</p><p>ضرب خانة بخانة وجمع.</p>"})
add("c3", {"t": "card", "front": "الزاوية بين متجهين", "back": "<p>\\(\\cos\\alpha=\\frac{\\vec v\\cdot\\vec u}{|\\vec v||\\vec u|}\\)</p><p>لا تنسى القسمة على الأطوال.</p>"})
add("c4", {"t": "card", "front": "متعامدين (<bdi>מאונכים</bdi>)", "back": "<p>\\(\\vec v\\cdot\\vec u=0\\)</p><p>مش لازم واحد منهم صفر.</p>"})
add("c5", {"t": "card", "front": "\\(\\vec v\\cdot\\vec v\\)", "back": "<p>\\(|\\vec v|^2\\)</p><p>و\\(|v+u|^2=|v|^2+2v\\cdot u+|u|^2\\)</p>"})


# lecturer's notation: every vector letter in TeX carries an arrow (\overrightarrow); figures keep plain letters
def _vec(tex):
    tex = re.sub(r"\\vec\s*(?:\{([vuw])\}|([vuw]))(_\d)?", lambda m: "\\overrightarrow{%s%s}" % (m.group(1) or m.group(2), m.group(3) or ""), tex)
    parts = re.split(r"(\\[A-Za-z]+)", tex)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            part = re.sub(r"(?<![A-Za-z{])([vuw])(_\d)?(?![A-Za-z}])", lambda m: "\\overrightarrow{%s%s}" % (m.group(1), m.group(2) or ""), part)
        out.append(part)
    return "".join(out)


def _arrows(x, key=None):
    if isinstance(x, str):
        if key == "svg": return x
        return re.sub(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", lambda m: ("\\(%s\\)" % _vec(m.group(1))) if m.group(1) is not None else ("\\[%s\\]" % _vec(m.group(2))), x, flags=re.S)
    if isinstance(x, list): return [_arrows(i) for i in x]
    if isinstance(x, dict): return {k: _arrows(v, k) for k, v in x.items()}
    return x


B[:] = _arrows(B)

LESSON = {"slug": "dot-product", "title": "الضرب السلمي (מכפלה סקלרית)", "he": "מכפלה סקלרית",
          "ref": "חוברת §1.1 · עמ׳ 4–6", "minutes": 11,
          "desc": "الضرب السلمي: ظل × طول، بالإحداثيات، الزاوية والتعامد.", "blocks": B}


# ---------------------------------------------------------------- narration
def seg(name, emotion, pause, say, frame=None, pace="normal"):
    d = {"block": N[name]}
    if frame: d["frame"] = frame
    d.update({"emotion": emotion, "pace": pace, "pause": pause, "say": say})
    return d


S = lambda t: {"show": t}
SEGMENTS = [
    seg("why", "curious", 1.0, ["سؤال قبل ما نبلّش: عندك سهمين على ورقة، ", S("وما معك منقلة"), ". كيف بتعرف إذا هم متعامدين؟ فكّر شوي."]),
    seg("why", "warm", 0.4, ["بآخر الدرس بتجاوب بثانية، بضرب كم رقم. الأداة اسمها الضرب السلمي، وبالعبري بيحكوله מכפלה סקלרית. يلا."]),
    seg("shadow", "curious", 0.5, ["شوف الرسمة. سهمين طالعين من نفس النقطة. فكّر بالأزرق كأنه أرض، وبالبرتقالي كأنه عمود مايل."], 1),
    seg("shadow", "curious", 0.5, ["تخيّل شمس فوقنا، وضوءها نازل مستقيم. العمود المايل بيرمي ظل على الأرض… وهاد الخط الأخضر."], 2),
    seg("shadow", "calm", 0.4, ["طول الظل تلاتة. يعني هاد الجزء من البرتقالي اللي ماشي مع الأزرق."], 3),
    seg("shadow", "excited", 0.6, ["وهلّق بسيطة: ظل ضرب طول. تلاتة ضرب أربعة، اتناشر. هاد هو الضرب السلمي. ظل ضرب طول."], 4),
    seg("shadow", "curious", 1.0, ["عند التسعين الضوء بينزل عالنقطة تماماً. هلّق ارفع السهم أكتر… وين رح يروح الظل برأيك؟"], 5),
    seg("shadow", "surprised", 0.5, ["الظل انقلب للجهة التانية! فالنتيجة سالبة، ناقص اتناشر. زاوية منفرجة، ضرب سالب. هاي أول إشي الناس بتنساه."], 6),
    seg("def18", "serious", 0.5, ["هاي نفس الفكرة بالرموز: بدل الظل، طول يو ضرب جيب تمام الزاوية. وانتبه، الناتج عدد، مش سهم."]),
    seg("cos", "calm", 0.3, ["هاد الجدول رح نحتاجه بعد شوي. الزوايا المنفرجة جيب تمامها سالب."], pace="fast"),
    seg("q1", "encouraging", 0.3, ["شوف الإشارة قبل الرقم."]),
    seg("examples", "calm", 0.4, ["نبدأ بالأسهل: سهمين على المحورين. بالعين شايف إنهم قايمين، فلازم النتيجة تكون صفر."], 1),
    seg("examples", "calm", 0.4, ["وهلّق متجهين بزاوية خمسة وأربعين. الأطوال واحد وجذر اتنين، وطلعت النتيجة واحد."], 2),
    seg("examples", "curious", 1.0, ["شوف الأرقام جنب بعض. الطريقتين نفس الجواب، وبدون زاوية بالثانية. صدفة؟"], 3),
    seg("p3", "playful", 0.4, ["لا، مش صدفة. وهلّق منشوف ليش."]),
    seg("proof", "calm", 0.4, ["نبرهنها بالمستوى. عنا سهمين، والزاوية بينهم هي المطلوبة."], 1),
    seg("proof", "calm", 0.4, ["ليش بنحتاج زاويتين عن الأرض؟ لأنه خانات كل سهم هي جيب التمام والساين، وهيك بيدخل الجبر على الصورة."], 2),
    seg("proof", "curious", 0.6, ["هاي الخدعة: الزاوية بينهم هي الفرق بين الزاويتين. وصيغة جيب تمام الفرق بتعطينا ضرب خانات. أربعة وعشرين على خمسة وعشرين."], 3),
    seg("proof", "excited", 0.5, ["منضرب بالطولين خمسة وخمسة، بيطلع أربعة وعشرين. وهاد بالزبط تلاتة ضرب أربعة زائد أربعة ضرب تلاتة. ضرب خانات!"], 4),
    seg("thm110", "emphatic", 0.5, ["هاي صيغة الامتحان: كل خانة بتنضرب باللي قبالها، وبعدين منجمع. بدون زاوية، بدون منقلة."]),
    seg("q3", "encouraging", 0.3, ["انتبه لإشارة الناقص."]),
    seg("def111", "serious", 0.5, ["هون قلبنا اللعبة: بنعرف الضرب، وبدنا الزاوية. المتجهين لازم يكونوا غير صفريين، وإلا ما في زاوية."]),
    seg("angle", "curious", 0.9, ["قبل ما نحسب: بالنظر، الزاوية بين هدول حادة ولا منفرجة؟"], 1),
    seg("angle", "calm", 0.4, ["الحساب كله أرقام، بدون ما نرسم أي زاوية. الضرب واحد، وكل طول جذر اتنين."], 2),
    seg("angle", "curious", 1.0, ["منقسم: واحد على جذر اتنين ضرب جذر اتنين، يعني نص. أي زاوية جيب تمامها نص؟ شوف الجدول."], 3),
    seg("angle", "excited", 0.5, ["باي على تلاتة! ستين درجة. وما احتجنا منقلة."], 4),
    seg("q4", "encouraging", 0.3, ["الإشارة بتحكي إذا الزاوية أكبر من تسعين."]),
    seg("p5", "warm", 0.5, ["رجعنا للسؤال اللي ضل معلّق: متعامدين؟ الظل صفر يعني الضرب صفر، وهاد بالضبط معنى التعامد."]),
    seg("def113", "serious", 0.5, ["بالعبري بيحكولهم מאונכים أو ניצבים. والصيغة هي التعريف، حتى للمتجه الصفري."]),
    seg("q5", "curious", 0.5, ["بالأعداد، إذا حاصل الضرب صفر، واحد منهم صفر. هل نفس الشي هون؟ جاوب."]),
    seg("perp", "calm", 0.4, ["بدنا كل المتجهات المتعامدة على تلاتة وسالب أربعة."], 1),
    seg("perp", "curious", 0.4, ["ناخد متجه مجهول، إكس وواي. المتعامدين كلهم بيجوا على خط واحد، الخط المتقطع."], 2),
    seg("perp", "calm", 0.4, ["وهيك بنترجم التعامد لمعادلة عادية."], 3),
    seg("perp", "surprised", 0.5, ["هون الخدعة: تلاتة إكس بتساوي أربعة واي. جرّب إكس أربعة وواي تلاتة… زبطت! وأي مضاعف إلها كمان."], 4),
    seg("perp", "emphatic", 0.5, ["وبنفحص: اتناشر ناقص اتناشر، صفر. وهاد اللي بتحفظه: الجواب بشكل تي ضرب أربعة وتلاتة."], 5),
    seg("p6", "emphatic", 0.5, ["هاي أهم خاصية، لأنها بتربط الضرب السلمي بالطول اللي بنعرفه من الدرس الأول."]),
    seg("thm115", "calm", 0.4, ["الباقي بديهي. وآخر وحدة بتقول: ضرب متجه بنفسه ما بيكون سالب، وبيطلع صفر بس للمتجه الصفري."]),
    seg("sumsq", "surprised", 0.5, ["وهاد اللي بيجي بالامتحان: طول المجموع بالتربيع. بنفتحه زي قانون المربع، بس الحد الأوسط ضرب سلمي. ولما يصير صفر… فيثاغورس طلع لحاله!"]),
    seg("q6", "encouraging", 0.3, ["الحد الأوسط بيجي مرتين."]),
    seg("mist", "emphatic", 0.5, ["هاد أخطر فخ: عقلنا متعوّد على الأعداد، بس المتجهات بتتصرف بشكل تاني."]),
    seg("qc2", "encouraging", 0.3, ["بعد ما تحل المعادلة، انتبه لشكل الجواب."]),
    seg("close", "curious", 0.6, ["نرجع للسؤال اللي بالأول. نفس السهمين، وعلامة السؤال بينهم."], 1),
    seg("close", "calm", 0.4, ["اتنين ضرب سالب تلاتة، سالب ستة. تلاتة ضرب اتنين، ستة."], 2),
    seg("close", "excited", 0.5, ["المجموع صفر! متعامدين. بثانية، وبدون منقلة."], 3),
    seg("close_p", "warm", 0.5, ["ظل ضرب طول، وصفر يعني متعامدين. بالتوفيق بالامتحان."]),
]


def lesson_hash(blocks):
    return hashlib.sha1(json.dumps(blocks, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()[:8]


if __name__ == "__main__":
    with open(os.path.join(ROOT, "lessons", "dot-product.json"), "w", encoding="utf-8") as fh:
        json.dump(LESSON, fh, ensure_ascii=False, indent=2); fh.write("\n")
    NARR = {"v": 1, "lessonHash": lesson_hash(B), "voice": {"persona": "مدرّس شاب، صاحب، بيحكي فلسطيني/شامي", "gender": "male"}, "segments": SEGMENTS}
    with open(os.path.join(ROOT, "narration", "dot-product.json"), "w", encoding="utf-8") as fh:
        json.dump(NARR, fh, ensure_ascii=False, indent=2); fh.write("\n")
    print("lesson blocks:", len(B), "segments:", len(SEGMENTS))

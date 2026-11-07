#!/usr/bin/env python3
"""Builds courses/11004/lessons/bounds.json (figures + lesson text).  Run: python3 bounds.py"""
import json, os, sys
sys.path.insert(0, os.path.expanduser("~/Developer/ali-skills/ali-skills-shibbur-course/scripts"))
from fk import Fig

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "lessons", "bounds.json")


def P(h): return {"t": "p", "html": "<p>%s</p>" % h}
def H(t): return {"t": "h", "text": t}
def BOX(kind, title, html): return {"t": "box", "kind": kind, "title": title, "html": html}
def MC(prompt, opts, ans, hint, sol):
    return {"t": "quiz", "q": {"kind": "mc", "prompt": "<p>%s</p>" % prompt,
            "options": [{"v": str(i + 1), "html": o} for i, o in enumerate(opts)],
            "answer": [str(ans)], "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}}
def TX(prompt, ans, hint, sol):
    return {"t": "quiz", "q": {"kind": "text", "prompt": "<p>%s</p>" % prompt, "answer": ans,
            "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}}


LO, HI, X0, X1 = -4, 8, 30, 440
def px(v): return X0 + (v - LO) / (HI - LO) * (X1 - X0)


def axis(f, y, ticks=True):
    f.number_line(X0, X1, y, LO, HI, 1) if ticks else f.line(X0 - 8, y, X1 + 8, y, "mut", 4, arrow=True)
    return px


def label(f, v, y, t, c="ink", **kw):
    f.text(px(v), y, t, c, 22, 700, ltr=True, **kw)


# ---------------------------------------------------------------- figures
def fig_bounds():
    f = Fig(480, 190, alt="المجموعة A=(1,5) وحاجز علوي 5.17 وحاجز سفلي 1")
    y = 100
    axis(f, y)
    f.interval(1, 5, False, False, "1", step=1)
    label(f, 3, y - 24, "A", step=1)
    f.dot(px(5.17), y, "2", 11, step=2); f.arrow(px(5.17), y - 40, px(5.17) - 52, y - 40, "2", 3.5, step=2)
    label(f, 5.9, y - 56, "M = 5.17", step=2)
    f.dot(px(-3.4), y, "3", 11, step=3); f.arrow(px(-3.4), y - 40, px(-3.4) + 52, y - 40, "3", 3.5, step=3)
    label(f, -3, y - 56, "m = −3.4", step=3)
    return f.block(kind="steps", title="حاجز علوي وحاجز سفلي لـ \\(A=(1,5)\\)", frames=[
        "المجموعة A: كل الأعداد بين 1 و 5 (الأزرق)",
        "M=5.17 برتقالي: كل عنصر بـ A أصغر منه، فهو حاجز علوي",
        "m=−3.4 بنفسجي: كل عنصر بـ A أكبر منه، فهو حاجز سفلي"])


def fig_ex117():
    f = Fig(480, 330, alt="ثلاث مجموعات: قطع مفتوح، شعاع، والطبيعية")
    ys = [64, 160, 256]
    for i, y in enumerate(ys):
        f.line(X0 - 8, y, X1 + 8, y, "grid", 4, arrow=True, step=i + 1)
    y = ys[0]
    f.line(px(1), y, px(5), y, "1", 10, step=1); f.dot(px(1), y, "1", 11, hollow=True, step=1); f.dot(px(5), y, "1", 11, hollow=True, step=1)
    f.dot(px(5.17), y, "2", 9, step=1); f.dot(px(-3.4), y, "3", 9, step=1)
    f.text(24, y - 26, "(1,5)", "ink", 22, 700, "left", ltr=True, step=1); f.text(240, y + 50, "حاجز من الاتجاهين", "ink", 21, 700, step=1)
    y = ys[1]
    f.line(px(-2), y, X1 + 8, y, "1", 10, step=2); f.dot(px(-2), y, "1", 11, hollow=True, step=2)
    f.dot(px(-4), y, "3", 9, step=2)
    f.text(24, y - 26, "(−2,∞)", "ink", 22, 700, "left", ltr=True, step=2); f.text(240, y + 50, "حاجز سفلي بس", "ink", 21, 700, step=2)
    y = ys[2]
    for v in range(1, 9):
        f.dot(px(v), y, "1", 8, step=3)
    f.dot(px(-3.14), y, "3", 9, step=3)
    f.text(24, y - 26, "ℕ", "ink", 22, 700, "left", ltr=True, step=3); f.text(240, y + 50, "حاجز سفلي بس", "ink", 21, 700, step=3)
    return f.block(kind="steps", title="أمثلة 1.17: مين حاجز من فوق، مين من تحت", frames=[
        "(1,5): فيه حاجز علوي (5.17) وحاجز سفلي (−3.4)",
        "(−2,∞): بيستمر لليمين، فما في حاجز علوي. حاجز سفلي مثلاً −4",
        "ℕ: بيكبر دايماً، فما في حاجز علوي. حاجز سفلي مثلاً \\(-\\pi\\)"])


def fig_archimedes():
    f = Fig(480, 190, alt="الأعداد الطبيعية على المحور وواحد منها أكبر من M")
    y = 110
    axis(f, y)
    f.dot(px(5.17), y, "2", 11, step=1); label(f, 5.17, y - 28, "M", step=1)
    for v in range(1, 9):
        f.dot(px(v), y, "1", 7, step=2)
    f.dot(px(6), y, "good", 13, step=3); label(f, 6, y - 28, "n", "ink", step=3)
    f.arrow(px(5.17) + 2, y - 54, px(6) - 2, y - 54, "good", 3, step=3)
    return f.block(kind="steps", title="مبرهنة أرخميدس", frames=[
        "عدد حقيقي M (برتقالي)، مهما كان كبير",
        "الأعداد الطبيعية 1, 2, 3 … (أزرق) بتكبر وبتكبر",
        "أكيد في n طبيعي بيتخطّى M: \\(M\\lt n\\)"])


def fig_bound_rays():
    f = Fig(480, 200, alt="الحواجز العلوية للمجموعة (1,5) شعاع يبدأ من 5 والسفلية شعاع ينتهي عند 1")
    y = 110
    axis(f, y)
    f.interval(1, 5, False, False, "1")
    label(f, 3, y - 24, "A")
    f.line(px(5), y - 40, X1 + 8, y - 40, "2", 8, arrow=True, step=1)
    f.dot(px(5), y - 40, "2", 10, step=1)
    f.text(330, y - 62, "كل حاجز علوي", "ink", 21, 700, step=1)
    f.line(px(1), y - 40, X0 - 8, y - 40, "3", 8, arrow=True, step=2)
    f.dot(px(1), y - 40, "3", 10, step=2)
    f.text(120, y - 62, "كل حاجز سفلي", "ink", 21, 700, step=2)
    return f.block(kind="steps", title="لو في حاجز، في ما لا نهاية منها", frames=[
        "الحواجز العلوية (برتقالي): من 5 ولليمين كلها",
        "الحواجز السفلية (بنفسجي): من 1 ولليسار كلها"])


def fig_sup_inf():
    f = Fig(480, 220, alt="sup هو أصغر حاجز علوي وinf هو أكبر حاجز سفلي للمجموعة (-2,5]")
    y = 120
    axis(f, y)
    f.interval(-2, 5, False, True, "1")
    label(f, 1.5, y - 24, "A")
    f.line(px(5), y - 44, X1 + 8, y - 44, "2", 8, arrow=True, step=1)
    f.dot(px(5), y - 44, "good", 12, step=2)
    f.text(px(5), y - 70, "sup A = 5", "ink", 22, 700, ltr=True, step=2)
    f.line(px(-2), y - 44, X0 - 8, y - 44, "3", 8, arrow=True, step=3)
    f.dot(px(-2), y - 44, "good", 12, step=4)
    f.text(px(-2), y - 70, "inf A = −2", "ink", 22, 700, ltr=True, step=4)
    return f.block(kind="steps", title="\\(A=(-2,5]\\): الأصغر من فوق والأكبر من تحت", frames=[
        "الحواجز العلوية: من 5 لليمين (برتقالي)",
        "أصغرهم 5: هاد \\(\\sup A\\) (أخضر)",
        "الحواجز السفلية: من −2 لليسار (بنفسجي)",
        "أكبرهم −2: هاد \\(\\inf A\\) (أخضر)"])


def fig_ex121():
    f = Fig(480, 244, alt="sup وinf لمجموعتين: شعاع مفتوح من الأعلى وشعاع مغلق من الأسفل")
    for y, a, b, cl, cr, t in ((70, None, 3, True, False, ("(−∞,3)", "sup = 3")), (170, 4, None, True, True, ("[4,∞)", "inf = 4"))):
        f.line(X0 - 8, y, X1 + 8, y, "grid", 4, arrow=True)
        pa = X0 - 8 if a is None else px(a)
        pb = X1 + 8 if b is None else px(b)
        f.line(pa, y, pb, y, "1", 10)
        if a is not None: f.dot(pa, y, "good", 12, hollow=not cl)
        if b is not None: f.dot(pb, y, "good", 12, hollow=not cr)
        f.text(24, y - 26, t[0], "ink", 22, 700, "left", ltr=True)
        f.text(240, y + 50, t[1], "ink", 22, 700, ltr=True)
    return f.block("لاحظ: النقطة الفاضية معناها sup أو inf مش من المجموعة، والممتلئة معناها من المجموعة.")


def fig_maxmin():
    f = Fig(480, 330, alt="ثلاث مجموعات: أين ينتمي sup وinf للمجموعة")
    rows = [(60, -2, 5, False, True, ("(−2,5]", "max = 5  ·  ما في min")),
            (160, None, 3, True, False, ("(−∞,3)", "ما في max  ·  ما في min")),
            (260, 4, None, True, True, ("[4,∞)", "min = 4  ·  ما في max"))]
    for i, (y, a, b, cl, cr, t) in enumerate(rows):
        s = i + 1
        f.line(X0 - 8, y, X1 + 8, y, "grid", 4, arrow=True, step=s)
        pa = X0 - 8 if a is None else px(a)
        pb = X1 + 8 if b is None else px(b)
        f.line(pa, y, pb, y, "1", 10, step=s)
        if a is not None: f.dot(pa, y, "good" if cl else "bad", 12, hollow=not cl, step=s)
        if b is not None: f.dot(pb, y, "good" if cr else "bad", 12, hollow=not cr, step=s)
        f.text(24, y - 26, t[0], "ink", 22, 700, "left", ltr=True, step=s)
        f.text(240, y + 50, t[1], "ink", 21, 700, step=s)
    return f.block(kind="steps", title="أمثلة 1.23: هل sup و inf بينتموا لـ A؟", frames=[
        "(−2,5]: 5 جوا A (أخضر) فهو max. −2 برا A (أحمر) فما في min",
        "(−∞,3): 3 برا A، يعني sup بس مش max. وما في حاجز سفلي أصلاً",
        "[4,∞): 4 جوا A فهو min. وما في حاجز علوي"])


def fig_bounded():
    f = Fig(480, 200, alt="المجموعة (-3,1) داخل القطع [m,M] وداخل [-c,c]")
    y = 110
    axis(f, y)
    f.interval(-3, 1, False, False, "1")
    label(f, -1, y - 24, "A")
    f.line(px(-3), y - 50, px(1), y - 50, "2", 5, step=1)
    f.dot(px(-3), y - 50, "2", 9, step=1); f.dot(px(1), y - 50, "2", 9, step=1)
    f.text(px(-3), y - 68, "m", "ink", 22, 700, ltr=True, step=1); f.text(px(1), y - 68, "M", "ink", 22, 700, ltr=True, step=1)
    f.line(px(-3), y - 50, px(3), y - 50, "good", 5, step=2)
    f.dot(px(-3), y - 50, "good", 9, step=2); f.dot(px(3), y - 50, "good", 9, step=2)
    f.text(px(3), y - 68, "c = 3", "ink", 22, 700, ltr=True, step=3)
    return f.block(kind="steps", title="المجموعة المحدودة: \\(A\\subseteq[m,M]\\)", frames=[
        "المجموعة A بين m (أصغر) و M (أكبر)",
        "نضمن كل A داخل القطع [−c, c] المتناظر",
        "مثال: \\(A=(-3,1)\\) ناخد \\(c=3\\)"])


def fig_complete():
    f = Fig(480, 250, alt="شروط وجود sup وinf حسب أكسيوما التمام")
    f.chip(24, 24, 100, 50, "A ≠ ∅", "1", step=1)
    f.chip(132, 24, 170, 50, "חסומה מלעיל", "2", step=1)
    f.arrow(310, 49, 340, 49, "mut", 3, step=1)
    f.chip(346, 24, 110, 50, "sup A  ✓", "good", step=1)
    f.chip(24, 100, 100, 50, "A ≠ ∅", "1", step=2)
    f.chip(132, 100, 170, 50, "חסומה מלרע", "3", step=2)
    f.arrow(310, 125, 340, 125, "mut", 3, step=2)
    f.chip(346, 100, 110, 50, "inf A  ✓", "good", step=2)
    f.chip(24, 176, 100, 50, "A ≠ ∅", "1", step=3)
    f.chip(132, 176, 170, 50, "חסומה", "6", step=3)
    f.arrow(310, 201, 340, 201, "mut", 3, step=3)
    f.chip(346, 176, 110, 50, "sup+inf", "good", step=3)
    return f.block(kind="steps", title="אקסיומת השלמות: متى بنضمن وجود sup و inf", frames=[
        "مجموعة مش فاضية وحاجز علوي: بالتأكيد بيوجد sup",
        "مجموعة مش فاضية وحاجز سفلي: بالتأكيد بيوجد inf",
        "مجموعة مش فاضية ومحدودة: بيوجد الاثنين (نتيجة 1.28)"])


def build():
    B = []
    B.append({"t": "why", "html":
        "<p>الدرس هاد بيعلّمك تحدّ مجموعة من فوق ومن تحت. بنستعمله بالنهايات والمتتاليات وبكل مكان بنحكي فيه \"أكبر قيمة\" أو \"أصغر قيمة\".</p>"
        "<p><b>بهالدرس:</b></p><ol>"
        "<li>الحاجز العلوي والسفلي (<bdi>חסם מלעיל ומלרע</bdi>)</li>"
        "<li>مبرهنة أرخميدس ولا نهاية الحواجز</li>"
        "<li>الأصغر من فوق والأكبر من تحت: \\(\\sup\\) و\\(\\inf\\)</li>"
        "<li>الأكبر والأصغر: \\(\\max\\) و\\(\\min\\)</li>"
        "<li>المجموعة المحدودة (<bdi>חסומה</bdi>)</li>"
        "<li>أكسيوما التمام (<bdi>אקסיומת השלמות</bdi>)</li></ol>"})

    # 1
    B += [H("1 · حاجز علوي وحاجز سفلي"),
          P("بدنا نحكي إنه مجموعة A (جزء من \\(\\mathbb{R}\\)) \"ما بتتخطى\" عدد معيّن. هاد العدد اسمه حاجز."),
          fig_bounds(),
          BOX("def", "تعريف · <bdi>הגדרה 1.16</bdi>", "<p>ليكن \\(A\\) جزء من \\(\\mathbb{R}\\). نقول إنه A <b>محدودة من فوق</b> (<bdi>חסומה מלעיל</bdi>) إذا يوجد \\(M\\in\\mathbb{R}\\) بحيث لكل \\(a\\in A\\):</p><p>\\[a\\le M\\]</p><p>وبنقول إنه M هو <b>حاجز علوي</b> (<bdi>חסם מלעיל</bdi>) لـ A.</p>"),
          P("نفس الشي من تحت: عدد m أصغر أو يساوي كل عناصر A."),
          BOX("def", "تعريف · <bdi>הגדרה 1.16 (המשך)</bdi>", "<p>A <b>محدودة من تحت</b> (<bdi>חסומה מלרע</bdi>) إذا يوجد \\(m\\in\\mathbb{R}\\) بحيث لكل \\(a\\in A\\):</p><p>\\[m\\le a\\]</p><p>وهو <b>حاجز سفلي</b> (<bdi>חסם מלרע</bdi>) لـ A.</p>"),
          BOX("ex", "مثال · <bdi>דוגמה 1.17</bdi>", "<ol><li>القطع المفتوح \\((1,5)\\): حاجز علوي مثلاً \\(M=5.17\\) وحاجز سفلي مثلاً \\(m=1,\\,-3.4\\).</li>"
              "<li>الشعاع \\((-2,\\infty)\\): محدود من تحت مثلاً \\(m=-4,\\,-\\pi\\) لكن مش محدود من فوق.</li>"
              "<li>الطبيعية \\(\\mathbb{N}\\): محدودة من تحت لكن مش من فوق.</li></ol>"),
          fig_ex117(),
          P("المثال التالت بنفهمه بالحدس: \\(\\mathbb{N}\\) بتكبر وبتكبر ومش ممكن عدد يتخطاها كلها. بس هاد بدو برهان، وهاد اللي عندنا بالنقطة الجاية.")]

    # 2
    B += [H("2 · مبرهنة أرخميدس ولا نهاية الحواجز"),
          P("حدس \\(\\mathbb{N}\\) إنها مش محدودة من فوق هو بالضبط مبرهنة أرخميدس: مهما كان M كبير، في طبيعي أكبر منه."),
          fig_archimedes(),
          BOX("thm", "مبرهنة أرخميدس · <bdi>משפט ארכימדס 1.18</bdi>", "<p>لكل عدد حقيقي \\(M\\in\\mathbb{R}\\) يوجد عدد طبيعي \\(n\\in\\mathbb{N}\\) بحيث</p><p>\\[M\\lt n\\]</p>"),
          P("من التعريف بنستنتج نتيجة مهمة: إذا في حاجز، في حواجز كتير. أي عدد أكبر من حاجز علوي هو كمان حاجز علوي."),
          BOX("key", "نتيجة · <bdi>מסקנה 1.19</bdi>", "<p>ليكن A جزء من \\(\\mathbb{R}\\).</p><ol>"
              "<li>إذا M حاجز علوي لـ A، فكل \\(\\tilde M\\) بحيث \\(M\\le\\tilde M\\) هو كمان حاجز علوي لـ A.</li>"
              "<li>إذا m حاجز سفلي لـ A، فكل \\(\\tilde m\\) بحيث \\(\\tilde m\\le m\\) هو كمان حاجز سفلي لـ A.</li></ol>"),
          fig_bound_rays(),
          P("يعني مجموعة الحواجز العلوية هي شعاع للأعلى، والسفلية شعاع للأسفل. أسئلة طبيعية: مين أصغر حاجز علوي؟ ومين أكبر حاجز سفلي؟")]
    B.append(MC("المجموعة \\(\\mathbb{N}\\) محدودة من تحت بـ:", ["0", "−100", "كل ما سبق", "ما بتنحد"], 3,
                "الحاجز السفلي: أي عدد أصغر أو يساوي كل عناصرها. وبعد حاجز واحد في حواجز تانية (نتيجة 1.19).",
                "كل عنصر في \\(\\mathbb{N}\\) أكبر أو يساوي 1، فأي عدد \\(\\le1\\) حاجز سفلي: 0 و −100 كلهم حواجز."))
    B.append(MC("أي مجموعة من هدول محدودة من فوق؟", ["\\(\\mathbb{N}\\)", "\\((-2,\\infty)\\)", "\\((1,5)\\)"], 3,
                "هل في عدد أكبر من كل عناصرها؟",
                "\\(\\mathbb{N}\\) و\\((-2,\\infty)\\) بيكبروا بدون حدود (أرخميدس). \\((1,5)\\) كل عناصره أقل من 5."))

    # 3
    B += [H("3 · الأصغر من فوق والأكبر من تحت: sup و inf"),
          P("بين كل الحواجز العلوية نختار الأصغر، لأنه هو الأقرب للمجموعة. وبين كل الحواجز السفلية نختار الأكبر."),
          fig_sup_inf(),
          BOX("def", "تعريف · <bdi>הגדרה 1.20</bdi>", "<p>ليكن A جزء من \\(\\mathbb{R}\\).</p><ol>"
              "<li>إذا A محدودة من فوق: الحاجز العلوي <b>الأصغر</b> هو الـ<b>سوبريمم</b> (<bdi>הסופרמום</bdi>) ونكتب \\(\\sup A\\).</li>"
              "<li>إذا A محدودة من تحت: الحاجز السفلي <b>الأكبر</b> هو الـ<b>إنفيمم</b> (<bdi>האינפימום</bdi>) ونكتب \\(\\inf A\\).</li></ol>"),
          BOX("ex", "مثال · <bdi>דוגמה 1.21</bdi>", "<ol><li>\\(A=(-2,5]\\): \\(\\inf A=-2\\) و\\(\\sup A=5\\).</li>"
              "<li>\\(A=(-\\infty,3)\\): \\(\\sup A=3\\) و A مش محدودة من تحت.</li>"
              "<li>\\(A=[4,\\infty)\\): \\(\\inf A=4\\) و A مش محدودة من فوق.</li></ol>"),
          fig_ex121(),
          P("لاحظ إنه أحياناً sup و inf بيكونوا من المجموعة وأحياناً لأ. مثلاً \\(\\sup(-\\infty,3)=3\\) لكن 3 مش جوا المجموعة.")]

    # 4
    B += [H("4 · الأكبر والأصغر: max و min"),
          P("لما الـ sup أو الـ inf بيكون من المجموعة نفسها، نعطيه اسم جديد."),
          BOX("def", "تعريف · <bdi>הגדרה 1.22</bdi>", "<p>ليكن A جزء من \\(\\mathbb{R}\\) بحيث \\(\\sup A=M\\) و\\(\\inf A=m\\).</p><ol>"
              "<li>إذا \\(M\\in A\\): M هو <b>المكسيمم</b> (<bdi>המקסימום</bdi>) ونكتب \\(M=\\max A\\).</li>"
              "<li>إذا \\(m\\in A\\): m هو <b>المينيمم</b> (<bdi>המינימום</bdi>) ونكتب \\(m=\\min A\\).</li></ol>"),
          P("نرجع للأمثلة السابقة ونسأل: هل الـ sup والـ inf جوا المجموعة؟"),
          fig_maxmin(),
          BOX("ex", "مثال · <bdi>דוגמה 1.23</bdi>", "<ol><li>\\(A=(-2,5]\\): \\(\\max A=5\\) لكن ما في min لأنه \\(\\inf A=-2\\notin A\\).</li>"
              "<li>\\(A=(-\\infty,3)\\): ما في max لأنه \\(\\sup A=3\\notin A\\)، وما في min لأنه A مش محدودة من تحت.</li>"
              "<li>\\(A=[4,\\infty)\\): \\(\\min A=4\\) و A مش محدودة من فوق (فما في max).</li></ol>"),
          BOX("trap", "فخ", "<p>\\(\\sup\\) موجود بدون ما يكون \\(\\max\\): مثلاً \\(\\sup(0,1)=1\\) لكن 1 مش جوا المجموعة، يعني ما في max.</p>")]
    B.append(MC("لـ \\(A=[2,7)\\) ماذا يصح؟",
                ["\\(\\min A=2\\) و\\(\\max A=7\\)", "\\(\\min A=2\\) و\\(\\sup A=7\\) وما في max", "\\(\\inf A=2\\) وما في min", "ما في sup"], 2,
                "اسأل: هل 2 جوا A؟ هل 7 جوا A؟",
                "2 جوا (قطع مغلق من اليسار) فهو min. 7 برا (مفتوح من اليمين) فهو sup بس، وما في max."))
    B.append(TX("احسب \\(\\sup A\\) لـ \\(A=(-2,5]\\).", ["5"],
                "أصغر حاجز علوي: الطرف الأيمن.", "كل عناصر A \\(\\le5\\)، و5 نفسه جوا A. فأصغر حاجز علوي هو 5."))

    # 5
    B += [H("5 · المجموعة المحدودة (חסומה)"),
          P("مجموعة محدودة من الاتجاهين كمان بتسمّى مجموعة محدودة، وهي كلها بين m و M."),
          BOX("def", "تعريف · <bdi>הגדרה 1.24</bdi>", "<p>مجموعة \\(A\\subseteq\\mathbb{R}\\) تسمى <b>محدودة</b> (<bdi>חסומה</bdi>) إذا هي محدودة من تحت ومن فوق. يعني يوجد \\(m,M\\in\\mathbb{R}\\) بحيث لكل \\(a\\in A\\):</p><p>\\[m\\le a\\le M,\\qquad\\text{أي}\\quad A\\subseteq[m,M]\\]</p>"),
          P("تعريف بنفس المعنى: A محدودة إذا يوجد \\(c\\in\\mathbb{R}\\) موجب بحيث \\(-c\\le a\\le c\\) لكل \\(a\\in A\\). وبهالحالة c حاجز للمجموعة."),
          fig_bounded(),
          BOX("ex", "مثال · <bdi>דוגמה 1.25</bdi>", "<p>لـ \\(A=(-3,1)\\) بنقدر نختار \\(c=3\\) وفعلاً \\(A\\subseteq[-3,3]\\).</p>"),
          BOX("note", "ملاحظة · <bdi>הערה 1.26</bdi>", "<p>إذا A محدودة من فوق بـ M ومن تحت بـ m، بنقدر نختار \\[c=\\max\\{|m|,|M|\\}\\]</p>")]

    # 6
    B += [H("6 · أكسيوما التمام (אקסיומת השלמות)"),
          P("السؤال: هل sup و inf بيوجدوا دايماً؟ الجواب: إذا في حاجز، بيوجد. هاد مش بيتبرهن، بنقبله كأكسيوما."),
          fig_complete(),
          BOX("key", "أكسيوما · <bdi>אקסיומת השלמות 1.27</bdi>", "<p>ليكن A جزء غير فاضي من \\(\\mathbb{R}\\).</p><ol>"
              "<li>إذا A محدودة من فوق فإنه يوجد لها \\(\\sup\\).</li>"
              "<li>إذا A محدودة من تحت فإنه يوجد لها \\(\\inf\\).</li></ol>"),
          BOX("key", "نتيجة · <bdi>מסקנה 1.28</bdi>", "<p>ليكن A جزء غير فاضي ومحدود من \\(\\mathbb{R}\\). عندها يوجد لـ A \\(\\sup\\) و\\(\\inf\\).</p>"),
          BOX("idea", "فكرة", "<p>هاي الخاصية هي اللي بتفرق \\(\\mathbb{R}\\) عن \\(\\mathbb{Q}\\): ما في فجوات بالمحور الحقيقي.</p>")]

    # closing
    B += [{"t": "method", "title": "كيف تلاقي sup و inf لمجموعة قطع", "steps": [
              "ارسم المجموعة على المحور (انتبه للنقاط الفاضية والممتلئة).",
              "الطرف الأيمن هو \\(\\sup A\\) (إذا في طرف أيمن، وإلا المجموعة مش محدودة من فوق).",
              "الطرف الأيسر هو \\(\\inf A\\) (وإلا مش محدودة من تحت).",
              "إذا الطرف جوا المجموعة (نقطة ممتلئة) فهو max أو min، وإذا برا فما في."]},
          {"t": "mistakes", "title": "أخطاء شائعة", "rows": [
              {"no": "\\(\\sup A\\) دايماً جوا A", "yes": "\\(\\sup(0,1)=1\\notin(0,1)\\)"},
              {"no": "إذا في sup فيه max", "yes": "max بس لما sup ∈ A"},
              {"no": "حاجز علوي واحد بس", "yes": "إذا M حاجز فكل \\(\\tilde M\\ge M\\) حاجز"},
              {"no": "\\(\\mathbb{N}\\) محدودة", "yes": "محدودة من تحت بس (أرخميدس)"}]},
          {"t": "checklist", "title": "شو لازم تعرف من هالدرس", "items": [
              "الحاجز العلوي والسفلي (<bdi>חסם מלעיל / מלרע</bdi>)",
              "مبرهنة أرخميدس: لكل M يوجد n طبيعي أكبر (<bdi>משפט ארכימדס</bdi>)",
              "\\(\\sup A\\) أصغر حاجز علوي و\\(\\inf A\\) أكبر حاجز سفلي (<bdi>סופרמום, אינפימום</bdi>)",
              "\\(\\max A\\) و\\(\\min A\\): لما sup أو inf جوا المجموعة",
              "المجموعة المحدودة (<bdi>חסומה</bdi>): \\(A\\subseteq[m,M]\\)",
              "أكسيوما التمام: غير فاضية + محدودة من فوق فيها sup"]},
          {"t": "card", "front": "\\(\\sup A\\) (<bdi>סופרמום</bdi>)", "back": "الحاجز العلوي الأصغر لـ A"},
          {"t": "card", "front": "\\(\\inf A\\) (<bdi>אינפימום</bdi>)", "back": "الحاجز السفلي الأكبر لـ A"},
          {"t": "card", "front": "أكسيوما التمام (<bdi>אקסיומת השלמות</bdi>)", "back": "\\(A\\ne\\emptyset\\) ومحدودة من فوق ⇒ يوجد \\(\\sup A\\). ومحدودة من تحت ⇒ يوجد \\(\\inf A\\)."},
          {"t": "card", "front": "مجموعة محدودة (<bdi>חסומה</bdi>)", "back": "\\(m\\le a\\le M\\) لكل \\(a\\in A\\)، أي \\(A\\subseteq[m,M]\\)"},
          MC("لـ \\(A=(-\\infty,3)\\) أي جملة صحيحة؟",
             ["\\(\\max A=3\\)", "\\(\\sup A=3\\) وما في max", "\\(\\inf A=3\\)", "A محدودة"], 2,
             "3 جوا A؟ وهل A محدودة من تحت؟",
             "3 برا A فما في max، لكن 3 أصغر حاجز علوي فهو sup. A مش محدودة من تحت، فما في inf."),
          MC("أي مجموعة فيها min لكن مافيها max؟",
             ["\\((0,1)\\)", "\\([0,1]\\)", "\\([0,1)\\)", "\\((0,1]\\)"], 3,
             "min يعني 0 جوا. max ما بدو 1 جوا.", "\\([0,1)\\): 0 جوا فهو min، و1 برا فما في max."),
          TX("إذا \\(A\\subseteq[m,M]\\) مع \\(m=-5,\\ M=2\\)، ما قيمة \\(c=\\max\\{|m|,|M|\\}\\)؟", ["5"],
             "احسب \\(|m|\\) و\\(|M|\\) وخد الأكبر.", "\\(|{-5}|=5\\) و\\(|2|=2\\) فالأكبر 5، وبكون \\(A\\subseteq[-5,5]\\).")]
    return B


lesson = {"slug": "bounds", "title": "حدود المجموعات الجزئية للأعداد الحقيقية", "he": "חסימות של תתי קבוצות של הממשיים",
          "ref": "חוברת §1.1 · עמ׳ 5–7", "minutes": 26,
          "desc": "حاجز علوي وسفلي، أرخميدس، \\(\\sup\\) و\\(\\inf\\)، \\(\\max\\) و\\(\\min\\)، وأكسيوما التمام.",
          "blocks": build()}

if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(lesson, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    bl = lesson["blocks"]
    print("figures", sum(b["t"] == "figure" for b in bl), "steps", sum(b["t"] == "steps" for b in bl),
          "quizzes", sum(b["t"] == "quiz" for b in bl))

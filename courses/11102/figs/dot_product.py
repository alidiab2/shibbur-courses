#!/usr/bin/env python3
"""Lesson `dot-product` (section 1.1, booklet p4-6). Run: python3 dot_product.py -> ../lessons/dot-product.json"""
import math
from _ch1lib import *


def arc(f, O, r, a0, a1, c="2", step=None, w=3.5):
    pts = [(O[0] + r * math.cos(math.radians(a)), O[1] - r * math.sin(math.radians(a))) for a in [a0 + (a1 - a0) * i / 10 for i in range(11)]]
    f.curve(pts, c=c, w=w, smooth=False, step=step)


def fig_geo():
    f = Fig(480, 290, alt="متجهان من نفس النقطة بينهما زاوية ألفا، وظل u على v طوله |u| cos ألفا، والمجموع هو الضرب السلمي")
    O = (60, 215); V = (400, 215)
    a = 45; L = 230
    U = (O[0] + L * math.cos(math.radians(a)), O[1] - L * math.sin(math.radians(a)))
    F = (U[0], O[1])
    f.arrow(*O, *V, c="1", w=5, step=1); f.text(V[0] - 6, V[1] + 34 - 4, "v", c="1", size=24, step=1)
    f.arrow(*O, *U, c="2", w=5, step=1); f.text(U[0] - 28, U[1] - 4, "u", c="2", size=24, step=1)
    arc(f, O, 70, 0, 45, c="ink", step=2)
    f.text(O[0] + 90, O[1] - 20, "α", c="ink", size=26, step=2)
    f.line(*U, *F, c="mut", w=3, dash=True, step=3)
    f.line(O[0], O[1] + 14, F[0], F[1] + 14, c="good", w=7, step=3)
    f.text((O[0] + F[0]) / 2, O[1] + 46, "|u|·cos α", c="good", size=22, step=3)
    f.text(250, 110, "v·u=|v||u|cos α", c="ink", size=21, anchor="left", step=4)
    return f.block("", kind="steps", title="الضرب السلمي هندسيا",
                   frames=["متجهين \\(\\vec v,\\vec u\\) من نفس النقطة", "الزاوية بينهم \\(\\alpha\\) (بين \\(0\\) و \\(\\pi\\))", "ظل \\(\\vec u\\) على \\(\\vec v\\) طوله \\(|\\vec u|\\cos\\alpha\\)", "منضربه بطول \\(\\vec v\\): هاد هو الضرب السلمي"])


def fig_signs():
    f = Fig(480, 240, alt="ثلاث حالات: زاوية حادة الضرب موجب، زاوية قائمة الضرب صفر، زاوية منفرجة الضرب سالب")
    cfg = [(90, 30, "α < π/2", "موجب", "good"), (240, 90, "α = π/2", "صفر", "mut"), (390, 150, "α > π/2", "سالب", "bad")]
    for cx, ang, lab, sign, col in cfg:
        O = (cx, 150)
        f.arrow(*O, O[0] + 80, O[1], c="1", w=5)
        f.arrow(*O, O[0] + 80 * math.cos(math.radians(ang)), O[1] - 80 * math.sin(math.radians(ang)), c="2", w=5)
        f.text(cx, 40, lab, c="ink", size=22)
        f.chip(cx - 45, 185, 90, 40, sign, c=col, size=21)
    return f.block("لاحظ: إشارة الضرب السلمي هي إشارة \\(\\cos\\alpha\\).")


def fig_ex19():
    f = Fig(480, 250, alt="مثالان: متجهان متعامدان ضربهما صفر، ومتجه مع قطر الربع زاويته 45 درجة ضربهما 1")
    for cx, (u, lab, res) in ((120, ((0, 1), "(1,0)·(0,1)=0", "good")), (350, ((1, 1), "(1,0)·(1,1)=1", "good"))):
        O = (cx - 70, 175)
        s = 100
        f.arrow(*O, O[0] + s, O[1], c="1", w=5)
        f.arrow(*O, O[0] + s * u[0], O[1] - s * u[1], c="2", w=5)
        if u == (0, 1):
            f.line(O[0] + 22, O[1], O[0] + 22, O[1] - 22, c="ink", w=3)
            f.line(O[0], O[1] - 22, O[0] + 22, O[1] - 22, c="ink", w=3)
            f.text(cx, 40, "α = π/2", c="ink", size=22)
        else:
            arc(f, O, 50, 0, 45, c="ink")
            f.text(cx, 40, "α = π/4", c="ink", size=22)
        f.text(cx, 225, lab, c=res, size=21)
    return f.block("لاحظ: الزاوية القائمة بتعطي صفر، والزاوية \\(45^\\circ\\) بتعطي 1.")


def fig_coord():
    f = Fig(480, 300, alt="ضرب متجهين بالإحداثيات: نضرب كل إحداثي بالمقابل ثم نجمع النتائج")
    rows = [(1, 4, 4), (2, -5, -10), (3, 6, 18)]
    f.text(70, 38, "v", c="1", size=24); f.text(200, 38, "u", c="2", size=24)
    for i, (a, b, p) in enumerate(rows):
        y = 55 + i * 62
        f.chip(30, y, 80, 46, str(a), c="1", size=24)
        f.text(135, y + 31, "·", c="ink", size=30, ltr=True)
        f.chip(160, y, 80, 46, str(b).replace("-", "−"), c="2", size=24)
        f.text(270, y + 31, "=", c="ink", size=26, ltr=True, step=i + 2)
        f.chip(300, y, 110, 46, str(p).replace("-", "−"), c="good", size=24, step=i + 2)
    f.line(30, 248, 440, 248, c="mut", w=3, step=5)
    f.text(240, 285, "4 − 10 + 18 = 12", c="good", size=26, step=5)
    return f.block("", kind="steps", title="\\((1,2,3)\\cdot(4,-5,6)\\)",
                   frames=["نكتب المتجهين جنب بعض", "الإحداثي الأول مع الأول: \\(1\\cdot4=4\\)", "الثاني مع الثاني: \\(2\\cdot(-5)=-10\\)", "الثالث مع الثالث: \\(3\\cdot6=18\\)", "نجمع: \\(4-10+18=12\\)"])


def fig_angle():
    f = Fig(480, 270, alt="خطوات حساب الزاوية بين (1,1,0) و (0,1,1): الضرب السلمي 1، الطولين جذر 2، جيب التمام نصف، الزاوية 60 درجة")
    items = [("v·u = 0 + 1 + 0 = 1", "1"), ("|v| = |u| = √2", "2"), ("cos α = 1 / (√2·√2) = 1/2", "1"), ("α = π/3  (60°)", "good")]
    for i, (t, c) in enumerate(items):
        f.chip(30, 20 + i * 62, 420, 50, t, c=c, solid=(i == 3), size=22, step=i + 1)
    return f.block("", kind="steps", title="الزاوية بين \\((1,1,0)\\) و \\((0,1,1)\\)",
                   frames=["الضرب السلمي بالإحداثيات", "الطولين", "جيب التمام من הגדרה 1.11", "الزاوية: \\(\\cos\\alpha=\\frac12\\) يعني \\(\\alpha=\\frac{\\pi}{3}\\)"])


def fig_perp():
    f = Fig(480, 330, alt="المتجه (3,-4) والخط المتقطع الذي يحوي كل المتجهات المتعامدة معه، والمتجه (4,3) عليه")
    p = f.axes((60, 15, 360, 288), xr=(-5, 5), yr=(-4, 4), grid=True, ticks=(1, 1), labels=False, xlabel="", ylabel="")
    O = p.pt(0, 0)
    f.arrow(*O, *p.pt(3, -4), c="1", w=5, step=1)
    f.text(p.pt(3, -4)[0] + 10, p.pt(3, -4)[1] - 4, "v=(3,−4)", c="1", size=20, anchor="left", step=1)
    a, b = p.pt(-3.2, -2.4), p.pt(3.2, 2.4)
    f.line(*a, *b, c="2", w=4, dash=True, step=2)
    # right angle mark
    d1 = (3 / 5, -4 / 5); d2 = (4 / 5, 3 / 5); k = 0.6
    pts = [p.pt(k * d1[0], k * d1[1]), p.pt(k * (d1[0] + d2[0]), k * (d1[1] + d2[1])), p.pt(k * d2[0], k * d2[1])]
    f.curve(pts, c="ink", w=3, smooth=False, step=3)
    f.arrow(*O, *p.pt(4, 3), c="good", w=6, step=3)
    f.text(p.pt(4, 3)[0] - 14, p.pt(4, 3)[1] - 16, "(4,3)", c="good", size=22, anchor="right", step=3)
    return f.block("", kind="steps", title="كل المتجهات المتعامدة مع \\((3,-4)\\)",
                   frames=["المتجه \\(\\vec v=(3,-4)\\)", "المتعامدين معه كلهم على هالخط", "مثلا \\((4,3)\\): الزاوية قائمة والضرب 0"])


def build():
    b = []
    b.append(WHY("الضرب السلمي هو أول عملية بتعطينا <b>عدد</b> من متجهين، وبيعطينا الزوايا والتعامد. بنستعمله بالمستويات والخطوط بعد شوي.",
                 ["التعريف الهندسي (<bdi>מכפלה סקלרית</bdi>)", "الحساب بالإحداثيات (<bdi>טענה 1.10</bdi>)", "الزاوية بين متجهين", "التعامد (<bdi>אורתוגונליים</bdi>)", "الخصائص (<bdi>טענה 1.15</bdi>)"]))

    b += [H("1 · التعريف الهندسي"),
          P("الضرب السلمي (<bdi>מכפלה סקלרית</bdi>) بياخد متجهين وبيعطي <b>عدد</b> واحد. شوف الرسمة: منضرب طول الأول بطول الثاني بجيب تمام الزاوية بينهم."),
          fig_geo(),
          BOX("def", "تعريف · <bdi>הגדרה 1.8</bdi>", "<p>ليكن \\(\\vec v,\\vec u\\in\\mathbb R^2,\\mathbb R^3\\) غير صفريين. نعرّف الضرب السلمي بينهم:</p><p>\\[\\vec v\\cdot\\vec u=|\\vec v|\\cdot|\\vec u|\\cos(\\alpha)\\]</p><p>حيث \\(0\\le\\alpha\\le\\pi\\) هي الزاوية بين المتجهين.</p>"),
          P("بما إنه \\(\\cos\\alpha\\) هو اللي بيحدد الإشارة، الضرب ممكن يطلع موجب أو صفر أو سالب."),
          fig_signs(),
          fig_ex19(),
          BOX("ex", "مثال · <bdi>דוגמה 1.9</bdi>", "<p>\\[\\begin{pmatrix}1\\\\0\\\\0\\end{pmatrix}\\cdot\\begin{pmatrix}0\\\\1\\\\0\\end{pmatrix}=1\\cdot1\\cdot\\cos\\tfrac{\\pi}{2}=0\\]</p><p>\\[\\begin{pmatrix}1\\\\0\\end{pmatrix}\\cdot\\begin{pmatrix}1\\\\1\\end{pmatrix}=1\\cdot\\sqrt{2}\\cos\\tfrac{\\pi}{4}=\\tfrac{\\sqrt{2}}{\\sqrt{2}}=1\\]</p>"),
          MC("متجهان طولهما 2 و 3 والزاوية بينهم \\(\\pi\\) (عكس بعض). كم الضرب السلمي؟",
             ["\\(6\\)", "\\(-6\\)", "\\(0\\)"], 2,
             "\\(\\cos\\pi\\) كم؟", "\\(2\\cdot3\\cdot\\cos\\pi=6\\cdot(-1)=-6\\). الخيار 1 نسي إنه \\(\\cos\\pi=-1\\)؛ الخيار 3 هو حالة الزاوية القائمة.")]

    b += [H("2 · الحساب بالإحداثيات"),
          P("بدون ما نعرف الزاوية، في طريقة أسهل: نضرب الإحداثيات المتقابلة ونجمع. لاحظ بالمثال اللي فات إنه نفس النتيجة طلعت."),
          fig_coord(),
          BOX("thm", "טענה 1.10", "<p>ليكن \\(\\vec v_1=\\begin{pmatrix}a_1\\\\b_1\\\\c_1\\end{pmatrix},\\ \\vec v_2=\\begin{pmatrix}a_2\\\\b_2\\\\c_2\\end{pmatrix}\\in\\mathbb R^3\\). عندها:</p><p>\\[\\vec v_1\\cdot\\vec v_2=a_1a_2+b_1b_2+c_1c_2\\]</p><p>وبنفس الطريقة بـ \\(\\mathbb R^2\\) (إحداثيين بس).</p>"),
          BOX("note", "ملاحظة", "<p>شوف مثال 1.9 الأول \\(\\begin{pmatrix}1\\\\0\\\\0\\end{pmatrix}\\cdot\\begin{pmatrix}0\\\\1\\\\0\\end{pmatrix}=1\\cdot0+0\\cdot1+0\\cdot0=0\\) هاد مش صدفة: الصيغة بتعطينا طريقة جبرية للحساب.</p>"),
          TQ("احسب \\(\\begin{pmatrix}2\\\\-1\\\\3\\end{pmatrix}\\cdot\\begin{pmatrix}4\\\\0\\\\-5\\end{pmatrix}\\).", ["-7"],
             "اضرب كل زوج وبعدين اجمع الثلاث نتائج.", "\\(8+0-15=-7\\).")]

    b += [H("3 · الزاوية بين متجهين"),
          P("من الطريقتين مع بعض بنقدر نحسب الزاوية: منحسب الضرب بالإحداثيات، والأطوال، ومنعوّض بالتعريف الهندسي."),
          BOX("def", "تعريف · <bdi>הגדרה 1.11</bdi>", "<p>لكل متجهين \\(\\vec v,\\vec u\\in\\mathbb R^2,\\mathbb R^3\\) غير صفريين، الزاوية \\(\\alpha\\) بينهم هي العدد في \\([0,\\pi]\\) الذي يحقق:</p><p>\\[\\cos(\\alpha)=\\frac{\\vec v\\cdot\\vec u}{|\\vec v|\\cdot|\\vec u|}\\]</p>"),
          fig_angle(),
          BOX("ex", "مثال · <bdi>דוגמה 1.12</bdi>", "<p>الزاوية بين \\(\\vec v=\\begin{pmatrix}1\\\\1\\\\0\\end{pmatrix}\\) و \\(\\vec u=\\begin{pmatrix}0\\\\1\\\\1\\end{pmatrix}\\): الضرب \\(=1\\)، \\(|\\vec v|=|\\vec u|=\\sqrt{2}\\)، فـ \\(\\cos\\alpha=\\frac12\\) و \\(\\alpha=\\frac\\pi3\\).</p>"),
          MC("شو الزاوية بين \\((1,1)\\) و \\((-1,1)\\)؟",
             ["\\(\\frac\\pi4\\)", "\\(\\frac\\pi2\\)", "\\(\\pi\\)"], 2,
             "احسب الضرب أول شي.", "\\(1\\cdot(-1)+1\\cdot1=0\\) فـ \\(\\cos\\alpha=0\\) و \\(\\alpha=\\frac\\pi2\\).")]

    b += [H("4 · التعامد"),
          P("لما الضرب السلمي بيطلع صفر، الزاوية قائمة. هاي الحالة الخاصة مهمة كثير، إلها اسم."),
          BOX("def", "تعريف · <bdi>הגדרה 1.13</bdi>", "<p>بنقول إنّ \\(\\vec v,\\vec u\\) <b>متعامدين</b> (<bdi>מאונכים</bdi> أو <bdi>ניצבים</bdi> أو <bdi>אורתוגונלים</bdi>) إذا</p><p>\\[\\vec v\\cdot\\vec u=0\\]</p>"),
          fig_perp(),
          P("المثال بالرسمة: بدنا كل المتجهات المتعامدة مع \\(\\vec v=(3,-4)\\). نفرض متجه عام \\(\\vec u=(x,y)\\) ونكتب الضرب = 0."),
          BOX("ex", "مثال · <bdi>דוגמה 1.14</bdi>", "<p>\\[\\vec v\\cdot\\vec u=3x-4y=0\\ \\Rightarrow\\ 3x=4y\\]</p><p>يعني \\(\\vec u\\) هو متعامد مع \\(\\vec v\\) إذا وفقط إذا هو من الشكل</p><p>\\[t\\begin{pmatrix}4\\\\3\\end{pmatrix},\\quad t\\in\\mathbb R\\]</p>"),
          TQ("المتجه \\((k,2)\\) متعامد مع \\((3,-6)\\). كم \\(k\\)؟", ["4"],
             "الضرب السلمي لازم يكون 0.", "\\(3k+2\\cdot(-6)=3k-12=0\\) فـ \\(k=4\\).")]

    b += [H("5 · خصائص الضرب السلمي"),
          P("هاي الخصائص بنستعملها بكل حساب. أكثر وحدة بتفيدنا: \\(\\vec v\\cdot\\vec v\\) بيعطي مربع الطول."),
          BOX("thm", "טענה 1.15", "<p>ليكن \\(\\vec v,\\vec u,\\vec w\\in\\mathbb R^2,\\mathbb R^3\\) و \\(\\alpha\\in\\mathbb R\\). عندها:</p><ul>"
              "<li>\\(\\vec v\\cdot\\vec u=|\\vec v|\\cdot|\\vec u|\\cos(\\alpha)\\)</li>"
              "<li>تبديل: \\(\\vec v\\cdot\\vec u=\\vec u\\cdot\\vec v\\)</li>"
              "<li>\\((\\alpha\\vec v)\\cdot\\vec u=\\alpha(\\vec v\\cdot\\vec u)\\)</li>"
              "<li>توزيع: \\((\\vec v+\\vec u)\\cdot\\vec w=\\vec v\\cdot\\vec w+\\vec u\\cdot\\vec w\\)</li>"
              "<li>\\(\\vec v\\cdot\\vec v=|\\vec v|^2\\ge0\\)، والمساواة بالصفر إذا وفقط إذا \\(\\vec v=\\vec 0\\)</li></ul>"),
          BOX("ex", "مثال", "<p>مثلا \\(\\vec v=(3,4)\\): \\(\\vec v\\cdot\\vec v=9+16=25=|\\vec v|^2\\) (الطول 5).</p>"),
          MISTAKES("أخطاء شائعة", [
              ("الضرب السلمي متجه", "الضرب السلمي <b>عدد</b>"),
              ("\\(\\vec v\\cdot\\vec u=0\\) يعني أحدهم صفري", "ممكن متعامدين وكلهم غير صفريين"),
              ("\\(\\vec v\\cdot\\vec v=|\\vec v|\\)", "\\(\\vec v\\cdot\\vec v=|\\vec v|^2\\)")]),
          CHECK(["الضرب السلمي (<bdi>מכפלה סקלרית</bdi>) = عدد: \\(|\\vec v||\\vec u|\\cos\\alpha\\).",
                 "بالإحداثيات: نضرب المتقابل ونجمع (<bdi>טענה 1.10</bdi>).",
                 "الزاوية: \\(\\cos\\alpha=\\frac{\\vec v\\cdot\\vec u}{|\\vec v||\\vec u|}\\).",
                 "متعامدين (<bdi>אורתוגונליים</bdi>) \\(\\Leftrightarrow\\) الضرب 0.",
                 "\\(\\vec v\\cdot\\vec v=|\\vec v|^2\\) وباقي الخصائص."]),
          CARD("الضرب السلمي بالإحداثيات", "\\(a_1a_2+b_1b_2+c_1c_2\\)"),
          CARD("الزاوية بين متجهين", "\\(\\cos\\alpha=\\dfrac{\\vec v\\cdot\\vec u}{|\\vec v||\\vec u|}\\)"),
          CARD("متعامدين (<bdi>מאונכים</bdi>)", "\\(\\vec v\\cdot\\vec u=0\\)"),
          MC("\\(\\vec v=(1,2,2)\\). كم \\(\\vec v\\cdot\\vec v\\)؟",
             ["\\(3\\)", "\\(9\\)", "\\(5\\)"], 2,
             "\\(\\vec v\\cdot\\vec v=|\\vec v|^2\\).", "\\(1+4+4=9\\). الطول 3 والمربع 9؛ الخيار 1 هو الطول بس."),
          TQ("شو جيب تمام الزاوية بين \\((1,0)\\) و \\((1,1)\\)؟ (اكتبها \\(0.71\\) أو \\(\\sqrt{2}/2\\) )", ["0.71", "0.707", "sqrt(2)/2", "1/sqrt(2)"],
             "الضرب 1، والأطوال 1 و \\(\\sqrt{2}\\).", "\\(\\cos\\alpha=\\frac1{1\\cdot\\sqrt{2}}=\\frac{\\sqrt{2}}2\\approx0.71\\) والزاوية \\(\\frac\\pi4\\)."),
          MC("لأي \\(t\\) المتجه \\(t(4,3)\\) متعامد مع \\((3,-4)\\)؟",
             ["لكل \\(t\\) حقيقي", "فقط \\(t=1\\)", "فقط \\(t>0\\)"], 1,
             "احسب الضرب بدلالة \\(t\\).", "\\(3\\cdot4t-4\\cdot3t=0\\) لكل \\(t\\) (حتى \\(t<0\\) و \\(t=0\\)).")]
    write_lesson("dot-product", "الضرب السلمي (מכפלה סקלרית)", "מכפלה סקלרית", "חוברת §1.1 · עמ׳ 4–6",
                 "تعريف الضرب السلمي، حسابه بالإحداثيات، الزاوية، والتعامد.", b)


if __name__ == "__main__":
    build()

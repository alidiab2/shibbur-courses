#!/usr/bin/env python3
"""cross_product.py - the ONE generator for lesson `cross-product` (11102, section 1.2).
Builds the figures, assembles lessons/cross-product.json AND narration/cross-product.json.
Run from the repo root:  FK_KEEP_GOING=1 python3 courses/11102/figs/cross_product.py
"""
import hashlib, json, os, sys
sys.path.insert(0, os.path.expanduser("~/Developer/ali-skills/ali-skills-shibbur-course/scripts"))
from fk import Fig

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_L = os.path.join(ROOT, "courses/11102/lessons/cross-product.json")
OUT_N = os.path.join(ROOT, "courses/11102/narration/cross-product.json")

# ---------------------------------------------------------------- 3D floor schematic (x toward viewer, y right, z up)
OX, OY = 170, 112
def P(x, y, z):
    return (OX - 28 * x + 50 * y, OY + 18 * x - 9 * z)

A_, B_, C_ = P(2, 0, 0), P(2, 3, 0), P(0, 3, 0)
FLOOR = [P(0, 0, 0), A_, B_, C_]

def floor(f, labels=True, shade=None, ushade=None):
    f.polygon(FLOOR, "1", step=None)
    if labels:
        f.text(66, OY + 25, "v=(2,0,0)", "1", 20, ltr=True)
        f.text(290, OY - 17, "u=(0,3,0)", "2", 20, ltr=True)
    f.arrow(*P(0, 0, 0), *A_, c="1", w=4)
    f.arrow(*P(0, 0, 0), *C_, c="2", w=4)

def hook_fig():
    f = Fig(480, 210, alt="متجهان على الأرض وسهم ثالث عمودي عليهما، لفوق أو لتحت؟")
    floor(f)
    f.arrow(OX, OY - 6, OX, P(0, 0, 6)[1], c="3", w=4, dash=True)
    f.arrow(OX, OY + 6, OX, P(0, 0, -6)[1], c="3", w=4, dash=True)
    f.text(OX + 28, P(0, 0, 6)[1] + 8, "؟", "3", 30)
    f.text(OX + 28, P(0, 0, -6)[1] - 4, "؟", "3", 30)
    return f.block("لاحظ: المتجهان على الأرض، والسهم الثالث بيطلع لفوق أو لتحت.")

def curl(f, rev=False, **kw):
    """curved arrow around O from v towards u (or back)"""
    pts = [(148, OY + 15), (160, OY + 26), (186, OY + 25), (206, OY + 15)]
    if rev: pts = pts[::-1]
    f.curve(pts, c="mut", w=3.5, **kw)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    f.arrow(x1, y1, x2, y2, c="mut", w=3.5, **kw)

def idea_steps():
    f = Fig(480, 210, alt="متجهان يفردان مستوى، وكل المتجهات العمودية عليه على خط واحد، نختار واحداً بالطول والاتجاه")
    floor(f, labels=False)
    f.text(262, OY + 21, "المستوى", "ink", 20, until=2)
    f.text(70, OY + 30, "v", "1", 24, ltr=True)
    f.text(330, OY - 12, "u", "2", 24, ltr=True)
    # frame 2: the line of candidates
    f.line(OX, 172, OX, 30, c="3", w=3, dash=True, step=2, until=2)
    for z, lab in ((3, "w"), (6, "2w"), (-3, "−w")):
        x, y = P(0, 0, z)
        f.dot(x, y, c="3", r=7, step=2, until=2)
        f.text(x + 30, y + 7, lab, "3", 20, ltr=True, step=2, until=2)
    # frame 3: length = area
    f.polygon(FLOOR, "good", step=3)
    f.text(262, OY + 21, "المساحة", "good", 20, step=3, until=3)
    f.arrow(OX, OY - 6, OX, P(0, 0, 6)[1], c="good", w=5, step=3)
    f.text(OX + 34, P(0, 0, 6)[1] + 8, "|w|", "good", 22, ltr=True, step=3)
    # frame 4: direction
    curl(f, step=4)
    f.arrow(OX, OY + 6, OX, P(0, 0, -4)[1], c="bad", w=4, dash=True, step=4)
    f.text(OX + 30, P(0, 0, -4)[1] + 4, "✗", "bad", 24, step=4)
    return f.block(kind="steps", title="كيف منختار المتجه الثالث w", frames=[
        "المتجهان \\(v\\) و\\(u\\) بيفردوا مستوى",
        "كل متجه عمودي على المستوى بيقع على خط واحد",
        "المساحة بتحدد الطول",
        "اليد اليمين بتحدد الاتجاه"])

def sin_steps():
    f = Fig(480, 250, alt="متوازي أضلاع طول ضلعيه 4 و3 والزاوية 30 درجة، ارتفاعه 1.5 ومساحته 6")
    ox, oy, s = 60, 205, 45
    import math
    vt = (ox + 4 * s, oy)
    ut = (ox + 3 * s * math.cos(math.radians(30)), oy - 3 * s * math.sin(math.radians(30)))
    ft = (vt[0] + ut[0] - ox, ut[1])
    f.polygon([(ox, oy), vt, ft, ut], "good", step=2)
    f.arrow(ox, oy, *vt, c="1", w=4)
    f.arrow(ox, oy, *ut, c="2", w=4)
    f.angle(ox, oy, 46, 0, 30, "α", c="mut")
    f.text((ox + vt[0]) / 2 + 30, 236, "|v|=4", "1", 20, ltr=True)
    f.text(88, 150, "|u|=3", "2", 20, ltr=True)
    f.line(ut[0], ut[1], ut[0], oy, c="bad", w=3, dash=True, step=2)
    f.right_angle(ut[0], oy, 90, 180, 14, step=2)
    f.text(ut[0] + 80, 176, "h=|u|sinα", "bad", 20, ltr=True, step=2)
    f.chip(200, 28, 262, 40, "|w| = 4·3·sin30° = 6", c="good", size=20, ltr=True, step=3)
    return f.block(kind="steps", title="المساحة = القاعدة × الارتفاع", frames=[
        "\\(|v|=4\\)، \\(|u|=3\\)، والزاوية \\(\\alpha=30^\\circ\\)",
        "الارتفاع هو \\(|u|\\sin\\alpha\\)",
        "المساحة بتطلع طول \\(w\\)"])

# ---- matrices
BR = lambda x, y, H: None

def vec_col(f, x0, x1, y0, y1, **kw):
    f.path("M%s,%s L%s,%s L%s,%s L%s,%s" % (x0 + 12, y0, x0, y0, x0, y1, x0 + 12, y1), "mut", "none", 4, **kw)
    f.path("M%s,%s L%s,%s L%s,%s L%s,%s" % (x1 - 12, y0, x1, y0, x1, y1, x1 - 12, y1), "mut", "none", 4, **kw)

ROWS_Y = [66, 118, 170]
def formula_steps():
    f = Fig(480, 240, alt="مصفوفة i j k فوق v وu، وبتغطية كل عمود بنطلع مركّب من النتيجة")
    rows = [["i", "j", "k"], ["a", "b", "c"], ["d", "e", "f"]]
    hls = {2: {(0, 0): "1", (1, 1): "2", (1, 2): "2", (2, 1): "2", (2, 2): "2"},
           3: {(0, 1): "1", (1, 0): "2", (1, 2): "2", (2, 0): "2", (2, 2): "2"},
           4: {(0, 2): "1", (1, 0): "2", (1, 1): "2", (2, 0): "2", (2, 1): "2"}}
    with f.group(only=1): f.matrix(20, 40, rows, 56, 52)
    for k, hl in hls.items():
        with f.group(only=k): f.matrix(20, 40, rows, 56, 52, hl=hl)
    f.text(262, 124, "=", "ink", 32, step=2)
    vec_col(f, 300, 450, 40, 196, step=2)
    for k, t in zip((2, 3, 4), ("bf − ce", "cd − af", "ae − bd")):
        f.text(375, ROWS_Y[k - 2] + 7, t, "good", 22, ltr=True, step=k)
    return f.block(kind="steps", title="الصيغة: غطّي عمود وتصالب", frames=[
        "الصف الأول \\(i,j,k\\)، وتحته \\(v\\) و\\(u\\)",
        "غطّينا عمود \\(i\\)، بقي \\(b,c,e,f\\)",
        "غطّينا عمود \\(j\\)، بقي \\(a,c,d,f\\)",
        "غطّينا عمود \\(k\\)، بقي \\(a,b,d,e\\)"])

def example_steps():
    f = Fig(480, 252, alt="حساب (1,-1,0) ضرب متجهي (0,1,2) والتأكد من النتيجة")
    rows = [["i", "j", "k"], ["1", "−1", "0"], ["0", "1", "2"]]
    f.matrix(14, 24, rows, 56, 52)
    L = 236
    for y, t in zip(ROWS_Y, ("(−1)·2 − 0·1 = −2", "0·0 − 1·2 = −2", "1·1 − (−1)·0 = 1")):
        f.text(L, y - 16, t, "ink", 20, anchor="left", ltr=True, only=2)
    f.chip(14, 196, 200, 40, "w = (−2, −2, 1)", c="good", size=22, ltr=True, step=3)
    f.text(L, ROWS_Y[0] - 16, "w·v = −2 + 2 + 0 = 0", "good", 20, anchor="left", ltr=True, only=3)
    f.text(L, ROWS_Y[1] - 16, "w·u = 0 − 2 + 2 = 0", "good", 20, anchor="left", ltr=True, only=3)
    f.text(L, ROWS_Y[0] - 16, "|w|² = 4 + 4 + 1 = 9", "good", 20, anchor="left", ltr=True, only=4)
    f.text(L, ROWS_Y[1] - 16, "|v|²|u|² − (v·u)²", "2", 20, anchor="left", ltr=True, only=4)
    f.text(L, ROWS_Y[2] - 16, "= 2·5 − (−1)² = 9", "2", 20, anchor="left", ltr=True, only=4)
    return f.block(kind="steps", title="مثال 1.18: \\((1,-1,0)\\times(0,1,2)\\)", frames=[
        "\\(v\\) بالصف التاني و\\(u\\) بالتالت",
        "حسبنا المركّبات الثلاثة",
        "الناتج \\(w\\)، وضربه السلمي بالاتنين صفر",
        "\\(\\sin^2\\alpha=1-\\cos^2\\alpha\\) بتعطي نفس التسعة"])

def swap_steps():
    f = Fig(480, 210, alt="v ضرب u بيطلع لفوق، وبتبديل الترتيب u ضرب v بيطلع لتحت بنفس الطول")
    floor(f, labels=False)
    f.text(70, OY + 30, "v", "1", 24, ltr=True)
    f.text(330, OY - 12, "u", "2", 24, ltr=True)
    curl(f, only=1)
    f.arrow(OX, OY - 6, OX, P(0, 0, 6)[1], c="good", w=5, only=1)
    f.text(OX + 56, P(0, 0, 6)[1] + 10, "v×u", "good", 22, ltr=True, only=1)
    curl(f, rev=True, only=2)
    f.arrow(OX, OY + 6, OX, P(0, 0, -6)[1], c="bad", w=5, only=2)
    f.text(OX + 56, P(0, 0, -6)[1] - 4, "u×v", "bad", 22, ltr=True, only=2)
    return f.block(kind="steps", title="بدّلنا الترتيب", frames=[
        "\\(v\\times u\\): الإبهام لفوق",
        "\\(u\\times v\\): نفس الطول، الإبهام لتحت"])

def answer_steps():
    f = Fig(480, 210, alt="الجواب: السهم لفوق وطوله 6 يساوي مساحة المتوازي")
    floor(f)
    f.arrow(OX, OY - 6, OX, P(0, 0, 6)[1], c="good", w=5)
    f.chip(OX - 140, P(0, 0, 6)[1] - 4, 116, 36, "(0,0,6)", c="good", size=22, ltr=True, step=1, until=1)
    f.polygon(FLOOR, "good", step=2)
    f.text(262, OY + 21, "2·3 = 6", "good", 20, ltr=True, step=2)
    f.text(OX - 70, P(0, 0, 6)[1] + 8, "|w|=6", "good", 22, ltr=True, step=2)
    curl(f, step=2)
    return f.block(kind="steps", title="جواب السؤال الأول", frames=[
        "الصيغة بتعطي \\((0,0,6)\\)",
        "طول السهم يساوي المساحة، واتجاهه لفوق"])

# ================================================================= LESSON
blocks, N = [], {}
def add(name, b):
    N[name] = len(blocks); blocks.append(b)
def H(t): return {"t": "h", "text": t}
def Pp(h): return {"t": "p", "html": "<p>%s</p>" % h}
def Box(kind, title, html): return {"t": "box", "kind": kind, "title": title, "html": html}
def Mc(prompt, opts, ans, hint, sol):
    return {"t": "quiz", "q": {"kind": "mc", "prompt": "<p>%s</p>" % prompt,
            "options": [{"v": str(i + 1), "html": o} for i, o in enumerate(opts)], "answer": [str(ans)],
            "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}}
def Tx(prompt, ans, hint, sol):
    return {"t": "quiz", "q": {"kind": "text", "prompt": "<p>%s</p>" % prompt, "answer": ans,
            "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}}

add("why", {"t": "why", "html":
  "<p>عندك متجهين على الأرض: \\(v=(2,0,0)\\) و\\(u=(0,3,0)\\). بدنا سهم ثالث <b>واقف</b> بزاوية قائمة على الاثنين، وطوله بيساوي مساحة المتوازي اللي بينهم.</p>"
  "<p>خمّن: لفوق ولا لتحت؟ وقديش طوله؟ الأداة اسمها <b>الضرب المتجهي</b> (<bdi>מכפלה וקטורית</bdi>)، وهي اللي بتعطيك الاتجاه العمودي على أي مستوى بالفراغ.</p>"})
add("hook", hook_fig())

add("h1", H("1 · ليش بدنا متجه ثالث؟"))
add("p1", Pp("متجهين غير متناسبين (واحد مش مضاعف للتاني) بيفردوا <b>مستوى</b> (<bdi>מישור</bdi>). كل المتجهات العمودية عليه بتقع على خط واحد، فأي واحد منهم بدنا؟"))
add("s1", idea_steps())
add("b1", Box("idea", "فكرة · شيئين بيحددوا \\(w\\)",
  "<p><b>الطول:</b> مساحة المتوازي (<bdi>שטח המקבילית</bdi>).</p><p><b>الاتجاه:</b> قاعدة اليد اليمين (<bdi>כלל יד ימין</bdi>)، أو قاعدة البرغي (<bdi>כלל הבורג</bdi>).</p>"))

add("h2", H("2 · التعريف"))
add("n2", Box("note", "تذكير", "<p>\\(v\\perp w\\) يعني \\(v\\cdot w=0\\): الضرب السلمي صفر = متعامدين.</p>"))
add("p2", Pp("كيف منحسب المساحة من الطولين والزاوية؟ قاعدة × ارتفاع."))
add("s2", sin_steps())
add("b2", Box("def", "تعريف · <bdi>הגדרה 1.16</bdi>",
  "<p>ليكن \\(v,u\\in\\mathbb R^3\\). الضرب المتجهي (<bdi>מכפלה וקטורית</bdi>) \\(w=v\\times u\\) هو المتجه الذي يحقق:</p>"
  "<ol><li>\\(v\\perp w\\) و\\(u\\perp w\\)</li>"
  "<li>\\(|w|=|u|\\cdot|v|\\sin(\\alpha)\\)، حيث \\(\\alpha\\) الزاوية بين \\(v\\) و\\(u\\)</li>"
  "<li>\\(\\langle v,u,w\\rangle\\) جملة يد يمنى (<bdi>מערכת יד ימין</bdi>)</li></ol>"
  "<p><small>لو \\(v,u\\) متناسبين فالزاوية صفر، والـ\\(\\sin\\) صفر، فالطول صفر والناتج المتجه الصفر.</small></p>"))
add("q1", Mc("\\(|v|=2\\)، \\(|u|=5\\)، والزاوية بينهم \\(30^\\circ\\). احسب طول \\(v\\times u\\) وانتبه للدالة.",
  ["\\(5\\sqrt3\\)", "\\(10\\)", "\\(5\\)", "\\(0\\)"], 3,
  "الطول بيستعمل \\(\\sin\\) مش \\(\\cos\\)، و\\(\\sin30^\\circ\\) معروفة.",
  "\\(|v\\times u|=2\\cdot5\\cdot\\sin30^\\circ=5\\). الخيار \\(5\\sqrt3\\) جاي من \\(\\cos30^\\circ\\) (غلطة الضرب السلمي)، و\\(10\\) نسيت فيه \\(\\sin\\)، و\\(0\\) بيصح بس لما المتجهين متناسبين."))

add("h3", H("3 · الصيغة بالإحداثيات"))
add("p3", Pp("التعريف ما بيفيد بالحساب: كيف بدنا نلاقي \\(w\\) من الأرقام بس؟ بدنا صيغة بالإحداثيات."))
add("n3", Box("note", "ترميز · متجهات الأساس",
  "<p>\\(i=\\begin{pmatrix}1\\\\0\\\\0\\end{pmatrix}\\)، \\(j=\\begin{pmatrix}0\\\\1\\\\0\\end{pmatrix}\\)، \\(k=\\begin{pmatrix}0\\\\0\\\\1\\end{pmatrix}\\)</p>"))
add("s3", formula_steps())
add("b3", Box("thm", "ادّعاء · <bdi>טענה 1.17</bdi>",
  "<p>ليكن \\(v=\\begin{pmatrix}a\\\\b\\\\c\\end{pmatrix}\\) و\\(u=\\begin{pmatrix}d\\\\e\\\\f\\end{pmatrix}\\) في \\(\\mathbb R^3\\). الضرب المتجهي بيُحسب هيك:</p>"
  "<p>\\[\\begin{aligned}v\\times u&=\\begin{vmatrix}i&j&k\\\\a&b&c\\\\d&e&f\\end{vmatrix}\\\\&=\\begin{pmatrix}bf-ce\\\\cd-af\\\\ae-bd\\end{pmatrix}\\end{aligned}\\]</p>"
  "<p><small>بدون برهان هون. منتأكد منها بمثال بعد شوي.</small></p>"))
add("i3", Box("idea", "فكرة · ليش الأوسط معكوس؟",
  "<p>الدور دائري: المركّب الأول من \\((y,z)\\)، التاني من \\((z,x)\\)، التالت من \\((x,y)\\). عشان هيك التاني \\(cd-af\\) مش \\(af-cd\\) — وهاي غلطة شائعة."
  "</p>"))
add("s4", example_steps())
add("q3", Mc("احسب \\(v\\times u\\) للمتجهين \\(v=(1,2,3)\\) و\\(u=(4,5,6)\\)، وانتبه للإشارات.",
  ["\\((-3,-6,-3)\\)", "\\((-3,6,-3)\\)", "\\((3,-6,3)\\)", "\\((4,10,18)\\)"], 2,
  "المركّب الأوسط هو \\(cd-af\\).",
  "الصيغة بتعطي \\((12-15,\\ 12-6,\\ 5-8)=(-3,6,-3)\\). الخيار الأول كتب الأوسط \\(af-cd=-6\\) (معكوس)، والتالت هو \\(u\\times v\\) (الترتيب معكوس)، والرابع ضرب الأرقام المتقابلة وهاد مش ضرب متجهي."))
add("q4", Tx("المتجه \\(v=(1,2,0)\\) و\\(u=(0,0,k)\\)، و\\(v\\times u=(6,-3,0)\\). جد \\(k\\) واكتب عدد.", ["3"],
  "حط \\(a=1,b=2,c=0\\) و\\(d=0,e=0,f=k\\) بالصيغة، وساوِ أول مركّب بـ 6.",
  "المركّب الأول: \\(bf-ce=2k=6\\) فـ\\(k=3\\). والتاني: \\(cd-af=-k=-3\\) بيأكد نفس القيمة."))

add("h4", H("4 · الخصائص"))
add("p4", Pp("شو بيصير لو بدّلنا ترتيب المتجهين؟ خمّن قبل ما تكبس."))
add("s5", swap_steps())
add("b4", Box("thm", "ادّعاء · <bdi>טענה 1.19</bdi>",
  "<p>ليكن \\(v_1,v_2,v_3\\in\\mathbb R^3\\) و\\(\\alpha\\in\\mathbb R\\). عندها:</p>"
  "<p>\\[\\begin{aligned}v_1\\times v_2&=-v_2\\times v_1\\\\(\\alpha v_1)\\times v_2&=\\alpha(v_1\\times v_2)\\\\(v_1+v_2)\\times v_3&=v_1\\times v_3\\\\&\\quad+v_2\\times v_3\\end{aligned}\\]</p>"
  "<p><small>بتنبرهن من التعريف أو من الصيغة.</small></p>"))
add("p5", Pp("وإذا ضربنا متجه بنفسه، الناتج بيساوي سالب نفسه، يعني المتجه الصفر."))
add("q5", Mc("معطى \\(v\\times u=(2,-1,4)\\). احسب \\((2u)\\times v\\) من غير ما تعرف \\(v\\) و\\(u\\).",
  ["\\((4,-2,8)\\)", "\\((-2,1,-4)\\)", "\\((2,-1,4)\\)", "\\((-4,2,-8)\\)"], 4,
  "خطوتين: بدّل الترتيب، وطلّع العدد 2 برا.",
  "\\((2u)\\times v=2(u\\times v)=-2(v\\times u)=(-4,2,-8)\\). الأول نسي إشارة التبديل، والتاني نسي الـ2، والتالت نسي الاتنين."))

add("hc", H("تمرين وخلاصة"))
add("mis", {"t": "mistakes", "title": "أخطاء الامتحان", "rows": [
  {"no": "\\(v\\times u\\) عدد", "yes": "متجه! العدد هو الضرب السلمي \\(v\\cdot u\\)"},
  {"no": "\\(v\\times u=u\\times v\\)", "yes": "\\(v\\times u=-u\\times v\\) — بيتساووا بس لما الناتج صفر"},
  {"no": "\\(|v\\times u|=|v||u|\\cos\\alpha\\)", "yes": "\\(\\sin\\alpha\\) — الـ\\(\\cos\\) للضرب السلمي، وبتصح بس لما \\(\\alpha=45^\\circ\\)"},
  {"no": "المركّب الأوسط \\(af-cd\\)", "yes": "\\(cd-af\\) — الدور دائري"}]})
add("q6", Tx("احسب \\((1,2,3)\\times(2,4,6)\\) واكتب الجواب على شكل \\((x,y,z)\\).", ["(0,0,0)", "0"],
  "المتجه التاني مضاعف للأول. قديش \\(\\sin\\) الزاوية بينهم؟",
  "\\(bf-ce=12-12=0\\)، و\\(cd-af=6-6=0\\)، و\\(ae-bd=4-4=0\\). الصفر لأنه المتجهين متناسبين: الزاوية صفر، والمساحة صفر."))
add("s6", answer_steps())
add("c1", {"t": "card", "front": "الضرب المتجهي <bdi>מכפלה וקטורית</bdi> — تعريف",
  "back": "\\(w=v\\times u\\): عمودي على \\(v\\) و\\(u\\)، طوله \\(|v||u|\\sin\\alpha\\) (المساحة)، واتجاهه يد يمنى. الناتج متجه مش عدد."})
add("c2", {"t": "card", "front": "الصيغة بالإحداثيات <bdi>טענה 1.17</bdi>",
  "back": "\\(v\\times u=\\begin{pmatrix}bf-ce\\\\cd-af\\\\ae-bd\\end{pmatrix}\\) — الأوسط معكوس."})
add("c3", {"t": "card", "front": "ترتيب الضرب المتجهي <bdi>טענה 1.19</bdi>",
  "back": "\\(v_1\\times v_2=-v_2\\times v_1\\)، وبيساوي صفر لما المتجهين متناسبين."})

import re
_MATH = re.compile(r"(\\\(.*?\\\)|\\\[.*?\\\])", re.S)
def _arrow_math(m, letters):
    return re.sub(r"(?<![\\A-Za-z{])([%s])(_\d)?(?![A-Za-z])" % letters,
                  lambda g: "\\overrightarrow{%s%s}" % (g.group(1), g.group(2) or ""), m)
def arrowize(o, letters, key=None):
    if isinstance(o, str):
        return o if key in ("svg", "alt") else _MATH.sub(lambda m: _arrow_math(m.group(0), letters), o)
    if isinstance(o, list): return [arrowize(x, letters) for x in o]
    if isinstance(o, dict): return {k: arrowize(v, letters, k) for k, v in o.items()}
    return o
_IJK = {N["n3"], N["b3"], N["s3"]}
blocks[:] = [arrowize(b, "vuwijk" if i in _IJK else "vuw") for i, b in enumerate(blocks)]

LESSON = {"slug": "cross-product", "title": "الضرب المتجهي", "he": "מכפלה וקטורית",
          "ref": "חוברת §1.2 · עמ׳ 6–8", "minutes": 8,
          "desc": "سهم عمودي على متجهين، طوله مساحة المتوازي، وصيغة حسابه من الإحداثيات.",
          "blocks": blocks}

# ================================================================= NARRATION
def S(block, say, emotion="calm", pace="normal", pause=0.4, frame=None, style=None):
    d = {"block": N[block]}
    if frame: d["frame"] = frame
    d.update({"emotion": emotion, "pace": pace})
    if style: d["style"] = style
    d.update({"pause": pause, "say": say})
    return d
sh = lambda t, s=None: ({"show": t} if s is None else {"show": t, "say": s})

SEGS = [
 S("why", ["سؤال قبل ما نبلّش: عندك سهمين مرسومين على الأرض، واحد طوله اتنين وواحد طوله تلاتة. بدك سهم تالت واقف عليهم بزاوية قائمة… لفوق ولا لتحت؟ وقديش طوله؟"], "curious", pause=1.0),
 S("why", ["بآخر الدرس بتجاوب بثانية. الأداة اسمها", sh("الضرب المتجهي"), "، وبالعبري بيحكوله", sh("מכפלה וקטורית"), ". يلا."], "warm", pause=0.4),
 S("s1", ["متجهين مش مضاعفات بعض بيفردوا مستوى، متل لوح خشب مسطّح."], "calm", pause=0.3, frame=1),
 S("s1", ["هلّق، المسامير اللي بتنغرز بزاوية قائمة بهاللوح… كلها على نفس الخط، بس بأطوال مختلفة. أي مسمار بدنا؟"], "curious", pause=0.9, frame=2),
 S("s1", ["الطول بيجي من المساحة. اللوح مساحته ستة؟ المسمار طوله ستة."], "calm", pause=0.3, frame=3),
 S("s1", ["وبقي الاتجاه، لفوق ولا لتحت؟ لفّ أصابع إيدك اليمين من الأول للتاني، والإبهام بيشاور على المسمار."], "emphatic", pause=0.5, frame=4),
 S("s1", ["عمودي، مساحة، إيد يمين. هي التلات كلمات اللي بتحدد المتجه الثالث."], "warm", pause=0.4, frame=4),
 S("b1", ["وبالامتحان بيسموها", sh("כלל יד ימין"), "، فاحفظ الاسم."], "calm", pause=0.3),
 S("s2", ["نطّلع على اللوح من فوق. الطولين أربعة وتلاتة، والزاوية تلاتين درجة."], "calm", pause=0.3, frame=1),
 S("s2", ["مساحة المتوازي قاعدة ضرب ارتفاع. شو الارتفاع؟ …طول ألفا من فوق، ضرب ساين الزاوية."], "curious", pause=0.8, frame=2),
 S("s2", ["أربعة ضرب تلاتة ضرب نص… ستة! وهاي المساحة هي بالضبط طول المسمار."], "excited", pause=0.4, frame=3),
 S("b2", ["التعريف بيجمع التلات: عمودي على الاتنين، طوله بالساين، واتجاهه", sh("جملة يد يمنى"), ". واللي لازم تتذكره: ساين، مش كوس."], "serious", pace="slow", pause=0.5),
 S("q1", ["قبل ما تحسب… اسأل حالك: كوس ولا ساين؟"], "encouraging", pause=0.9),
 S("p3", ["التعريف حلو بالفكرة، بس مين بدو يقيس زاوية بالامتحان؟ بدنا صيغة من الأرقام بس."], "curious", pause=0.6),
 S("s3", ["هاي هي الصيغة. صف فيه الأساس، وتحته متجهينا. اللي لازم تعرفه: كيف بيطلع كل مركّب."], "calm", pause=0.3, frame=1),
 S("s3", ["الأول: غطّي عمود آي، وخد اللي بقي. بي ضرب إف، ناقص سي ضرب إي."], "calm", pause=0.3, frame=2),
 S("s3", ["التاني: غطّي عمود جاي… وانتبه! بنبدأ من سي ضرب دي، وبعدين ناقص إيه ضرب إف."], "serious", pause=0.4, frame=3),
 S("s3", ["والتالت: إيه ضرب إي، ناقص بي ضرب دي."], "calm", pause=0.3, frame=4),
 S("b3", ["هاي هي الصيغة اللي بتحسب فيها بالامتحان. وبعد شوي بنتأكد منها بمثال."], "serious", pace="slow", pause=0.4),
 S("i3", ["الأوسط بيجي معكوس. السبب إنه الدور دائري: واي زِد، وبعدين زِد إكس، وبعدين إكس واي. هيك ما بتنسى."], "emphatic", pause=0.5),
 S("s4", ["حط الأول بالصف التاني والتاني بالتالت. قبل ما تضغط، توقّع: شو بيطلع؟"], "curious", pause=0.9, frame=1),
 S("s4", ["الأول: ناقص اتنين. التاني: ناقص اتنين كمان. والتالت: واحد."], "calm", pause=0.4, frame=2),
 S("s4", ["شوف! الضرب السلمي مع كل واحد منهم صفر. يعني فعلاً عمودي على الاتنين."], "excited", pause=0.4, frame=3),
 S("s4", ["والطول: تسعة من الجهتين. يعني الطول تلاتة، زي ما التعريف بده. هيك تأكدنا من الصيغة بإيدينا."], "reassuring", pause=0.5, frame=4),
 S("q3", ["رتّب الأحرف الأول، وبعدين المركّب الأوسط."], "encouraging", pause=0.3),
 S("p4", ["شو بيصير لو بدّلنا الترتيب؟ خمّن."], "curious", pause=0.9),
 S("s5", ["عنا الأول ضرب التاني، والإبهام لفوق."], "calm", pause=0.3, frame=1),
 S("s5", ["هلّق بدّلنا… نفس الطول، بس الإبهام نزل لتحت! الإشارة انقلبت."], "surprised", pause=0.5, frame=2),
 S("b4", ["الأولى هي المهمة: بدّل الترتيب بتقلب الإشارة. والباقي زي الأرقام العادية، بتطلّع العدد برا وبتوزّع الجمع."], "calm", pause=0.4),
 S("mis", ["أخطر غلطة: تنسى إشارة التبديل، أو تحط كوس مكان ساين."], "emphatic", pause=0.4),
 S("s6", ["نرجع لسؤالنا. بالصيغة: الأول صفر، التاني صفر، والتالت ستة."], "curious", pause=0.5, frame=1),
 S("s6", ["لفوق وطوله ستة، بالضبط مساحة المتوازي اتنين ضرب تلاتة!"], "excited", pause=0.5, frame=2),
 S("s6", ["عمودي، مساحة، إيد يمين. بالتوفيق!"], "warm", pause=0.3, frame=2),
]

def lesson_hash():
    return hashlib.sha1(json.dumps(blocks, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()[:8]

NARR = {"v": 1, "lessonHash": lesson_hash(),
        "voice": {"persona": "مدرّس شاب، صاحب، بيحكي فلسطيني/شامي", "gender": "male"},
        "segments": SEGS}

for path, obj in ((OUT_L, LESSON), (OUT_N, NARR)):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2); fh.write("\n")
print("blocks", len(blocks), "segments", len(SEGS))

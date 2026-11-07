#!/usr/bin/env python3
"""11102 ch.2 lesson 2 'polar-form' (PDF section 2.1, p17-20): builds figures AND writes lessons/polar-form.json.
Run:  python3 courses/11102/figs/polar-form.py"""
import json, math, os, sys
sys.path.insert(0, os.path.expanduser("~/Developer/ali-skills/ali-skills-shibbur-course/scripts"))
from fk import Fig, lint

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lessons", "polar-form.json")
B = []
def h(t): B.append({"t": "h", "text": t})
def p(x): B.append({"t": "p", "html": "<p>%s</p>" % x})
def box(kind, title, html): B.append({"t": "box", "kind": kind, "title": title, "html": html})
def mc(prompt, opts, ans, hint, sol):
    B.append({"t": "quiz", "q": {"kind": "mc", "prompt": "<p>%s</p>" % prompt,
              "options": [{"v": str(i + 1), "html": o} for i, o in enumerate(opts)], "answer": [str(ans)],
              "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}})
def txt(prompt, ans, hint, sol):
    B.append({"t": "quiz", "q": {"kind": "text", "prompt": "<p>%s</p>" % prompt, "answer": ans,
              "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}})

# ---- drawing helpers: origin (ox,oy), pixel radius, angle in degrees (counter-clockwise, y up)
def P(o, R, deg): return (o[0] + R * math.cos(math.radians(deg)), o[1] - R * math.sin(math.radians(deg)))
def arc(f, o, R, a0, a1, c="1", w=4, step=None, only=None, until=None, grow=0.0):
    n = max(6, int(abs(a1 - a0) / 8))
    pts = [P(o, R + grow * (a0 + (a1 - a0) * i / n - a0), a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    f.curve(pts, c, w, smooth=True, step=step, only=only, until=until)
def axes(f, o, left, right, down, up, step=None):
    with f.group(step=step):
        f.arrow(o[0] - left, o[1], o[0] + right, o[1], "mut", 3.5)
        f.arrow(o[0], o[1] + down, o[0], o[1] - up, "mut", 3.5)
        f.dot(o[0], o[1], "mut", 6)

# ------------------------------------------------------------------ why
B.append({"t": "why", "html": (
    "<p>الشكل <b>a+ib</b> ممتاز للجمع، بس الضرب والقوى بتصير مرهقة فيه. الشكل القطبي بيخلّي الضرب والرفع للقوة والجذور سهلين جداً.</p>"
    "<p><b>بهالدرس:</b></p><ol>"
    "<li>مسافة وزاوية بدل \\((a,b)\\)</li>"
    "<li>الشكل القطبي \\(r\\,\\mathrm{cis}(\\theta)\\) (<bdi>הצגה קוטבית</bdi>)</li>"
    "<li>الزاوية والأرغومنت (<bdi>ארגומנט</bdi>)</li>"
    "<li>التحويل بين الشكلين</li>"
    "<li>ضرب الأعداد القطبية، دي مواڤر والمعكوس</li>"
    "<li>الجذور من الرتبة \\(n\\) (<bdi>שורש מסדר n</bdi>)</li></ol>")})

# ------------------------------------------------------------------ 1
h("1 · مسافة وزاوية بدل (a, b)")
p("لحد هسا كتبنا \\(z=a+ib\\). هاي اسمها <b>الصيغة الكرتيزية</b> أو الجبرية (<bdi>הצגה קרטזית / אלגברית</bdi>). هي سهلة للجمع والطرح، بس صعبة للضرب ولرفع العدد لقوة عالية.")
p("في طريقة تانية نحدد فيها النقطة \\(z\\) على المستوى: بنقول <b>كم بعيدة عن الأصل</b> و <b>بأي اتجاه</b>.")
O = (80, 240)
f = Fig(480, 290, alt="النقطة z محددة بطريقتين: بالضلعين a و b، أو بالبعد r عن الأصل والزاوية θ")
axes(f, O, 40, 390, 30, 220)
z = P(O, 220, 40)
f.dot(*z, "1", 10)
f.text(z[0] + 12, z[1] - 12, "z", "1", 26, 700, "left")
f.line(O[0], O[1], z[0], O[1], "2", 4, dash=True, until=1)
f.line(z[0], O[1], z[0], z[1], "2", 4, dash=True, until=1)
f.text((O[0] + z[0]) / 2, O[1] + 28, "a", "2", 24, 700, until=1)
f.text(z[0] + 14, (O[1] + z[1]) / 2 + 8, "b", "2", 24, 700, "left", until=1)
f.line(O[0], O[1], z[0], z[1], "good", 5, step=2)
m = P(O, 120, 40)
f.text(m[0] - 14, m[1] - 8, "r", "good", 26, 700, "right", step=2)
arc(f, O, 62, 0, 40, "1", 5, step=3)
q = P(O, 92, 20)
f.text(q[0], q[1] + 8, "θ", "1", 26, 700, "left", step=3)
B.append(f.block(kind="steps", title="طريقتين لتحديد \\(z\\)", frames=[
    "الطريقة القديمة: نمشي \\(a\\) أفقياً و \\(b\\) عمودياً.",
    "الطريقة الجديدة: أول شي <b>المسافة</b> \\(r\\) عن الأصل.",
    "وبعدين <b>الزاوية</b> \\(\\theta\\) من المحور الحقيقي الموجب."]))
p("بالتفصيل: \\(r\\) اللي عرفناه قبل \\(r=|z|\\) ونسميه <b>الراديوس</b> (<bdi>רדיוס</bdi>). و \\(\\theta\\) هي الزاوية بين المحور الأفقي (<bdi>ציר Re</bdi>) وبين المتجه من الأصل لـ \\(z\\)، بعكس عقارب الساعة.")
p("بما إنو كل عدد مركّب إله نقطة واحدة وكل نقطة إلها عدد واحد، فبنقدر نحدد \\(z\\) بالزوج \\((r,\\theta)\\) بدل \\((a,b)\\).")
box("def", "تعريف · <bdi>הצגה קוטבית</bdi>", "<ul><li>\\(r=|z|\\): بعد \\(z\\) عن الأصل (<bdi>רדיוס</bdi>)</li><li>\\(\\theta\\): الزاوية بين الاتجاه الموجب لمحور \\(\\mathrm{Re}\\) والمتجه اللي بيوصل الأصل بـ \\(z\\)</li></ul>")

# ------------------------------------------------------------------ 2
h("2 · الشكل القطبي r cis(θ)")
p("نرسم مثلث قائم الزاوية: الوتر \\(r\\) والضلعين \\(a\\) و \\(b\\). من علم المثلثات (الجيب وجيب التمام) منقدر نحسب \\(a\\) و \\(b\\) من \\(r\\) و \\(\\theta\\).")
O = (50, 220)
tip = P(O, 280, 33)
f = Fig(480, 290, alt="مثلث قائم الوتر r والزاوية θ؛ الضلع الأفقي a = r cos θ والعمودي b = r sin θ")
f.line(O[0], O[1], tip[0], O[1], "2", 5, step=2)
f.line(tip[0], O[1], tip[0], tip[1], "2", 5, step=3)
f.line(O[0], O[1], tip[0], tip[1], "1", 5.5)
f.dot(*tip, "1", 9); f.text(tip[0] + 10, tip[1] - 10, "z", "1", 26, 700, "left")
mm = P(O, 140, 33)
f.text(mm[0] - 14, mm[1] - 6, "r", "1", 26, 700, "right")
arc(f, O, 66, 0, 33, "1", 5)
q = P(O, 96, 16)
f.text(q[0], q[1] + 8, "θ", "1", 26, 700, "left")
f.text((O[0] + tip[0]) / 2, O[1] + 34, "a = r cos(θ)", "2", 24, 700, step=2)
f.text(tip[0] + 14, (O[1] + tip[1]) / 2 + 8, "b = r sin(θ)", "2", 24, 700, "left", step=3)
B.append(f.block(kind="steps", title="\\(a\\) و \\(b\\) من \\(r\\) و \\(\\theta\\)", frames=[
    "الوتر \\(r\\) والزاوية \\(\\theta\\).", "الضلع المجاور للزاوية: \\(a=r\\cos(\\theta)\\).", "الضلع المقابل للزاوية: \\(b=r\\sin(\\theta)\\)."]))
p("والعكس: من \\(a\\) و \\(b\\) منحسب \\(r\\) بفيثاغورس و \\(\\theta\\) بالـ \\(\\arctan\\).")
box("key", "التحويل · <bdi>המעבר</bdi>",
    "<p>\\[\\begin{cases}a=r\\cos(\\theta)\\\\ b=r\\sin(\\theta)\\end{cases}\\]</p><p>\\[\\begin{cases}r=\\sqrt{a^2+b^2}\\\\ \\theta=\\arctan\\!\\left(\\tfrac ba\\right)\\end{cases}\\]</p>")
p("هسا منعوّض \\(a\\) و \\(b\\) بالصيغة \\(z=a+ib\\) ومنخرج \\(r\\) عامل مشترك:")
box("def", "تعريف · <bdi>cis</bdi>", "<p>\\[z=a+ib=r\\cos(\\theta)+ir\\sin(\\theta)=r\\big(\\cos(\\theta)+i\\sin(\\theta)\\big):=r\\,\\mathrm{cis}(\\theta)\\]</p>")
p("\\(\\mathrm{cis}(\\theta)\\) هو اختصار لـ \\(\\cos\\theta+i\\sin\\theta\\). مثال سريع: \\(2\\,\\mathrm{cis}(0^\\circ)=2\\) و \\(2\\,\\mathrm{cis}(90^\\circ)=2i\\).")
mc("ما هو الشكل القطبي لـ \\(z=1+i\\)؟", ["\\(\\sqrt2\\,\\mathrm{cis}(45^\\circ)\\)", "\\(2\\,\\mathrm{cis}(45^\\circ)\\)", "\\(\\sqrt2\\,\\mathrm{cis}(135^\\circ)\\)", "\\(\\mathrm{cis}(45^\\circ)\\)"], 1,
   "احسب \\(r=\\sqrt{a^2+b^2}\\) أولاً، وبعدين \\(\\arctan(b/a)\\).",
   "\\(r=\\sqrt{1+1}=\\sqrt2\\) و \\(\\theta=\\arctan(1)=45^\\circ\\). الخيار \\(2\\,\\mathrm{cis}\\) نسي الجذر (حسب \\(a+b\\) أو \\(a^2+b^2\\)). الخيار \\(\\mathrm{cis}(45^\\circ)\\) نسي الراديوس.")

# ------------------------------------------------------------------ 3
h("3 · الزاوية والأرغומنت (ארגומנט)")
p("الزاوية مش وحيدة. إذا لفّيت دورة كاملة (\\(360^\\circ\\)) بترجع لنفس النقطة، فهاي زاويا مختلفة لنفس العدد.")
O = (150, 150)
f = Fig(480, 300, alt="الزاوية 20 درجة والزاوية 380 درجة تعطيان نفس الاتجاه، فهما نفس العدد المركب")
axes(f, O, 40, 300, 130, 130)
t = P(O, 190, 20)
f.line(O[0], O[1], t[0], t[1], "1", 5)
f.dot(*t, "1", 9)
arc(f, O, 60, 0, 20, "1", 5)
f.text(O[0] + 108, O[1] - 10, "20°", "1", 22, 700, "left")
arc(f, O, 70, 0, 380, "2", 4, step=2, grow=0.1)
f.text(O[0] + 100, O[1] + 118, "380°", "2", 22, 700, "left", step=2)
B.append(f.block(kind="steps", title="زاويتين لنفس النقطة", frames=[
    "\\(r\\,\\mathrm{cis}(20^\\circ)\\): الاتجاه \\(20^\\circ\\).", "نلف دورة كاملة وزيادة \\(20^\\circ\\): \\(380^\\circ\\). نفس الاتجاه بالضبط."]))
box("note", "ملاحظة · <bdi>הערה 2.16 (1)</bdi>", "<p>\\(r\\,\\mathrm{cis}(20^\\circ)=r\\,\\mathrm{cis}(380^\\circ)\\) لأنو \\(380=20+360\\). لهيك الزاوية معرّفة بالضبط حتى إضافة وطرح مضاعفات \\(360^\\circ\\). منرمز لكل الزوايا المناسبة لـ \\(z\\) بـ</p>"
    "<p>\\[\\arg(z)=\\{\\theta+2\\pi k:\\ k\\in\\mathbb{Z}\\}\\]</p><p>وهاد هو <b>الأرغومنت</b> (<bdi>ארגומנט</bdi>) لـ \\(z\\).</p>")
p("المشكلة التانية: \\(\\arctan\\) بيعطي دايماً زاوية بين \\(-90^\\circ\\) و \\(90^\\circ\\)، يعني ما بيفرّق بين ربعين. لازم تتأكد بنفسك بأي ربع النقطة.")
O = (240, 162)
u = 70
zp = (O[0] - u, O[1] - u * math.sqrt(3)); wp = (O[0] + u, O[1] + u * math.sqrt(3))
f = Fig(480, 330, alt="العددان −1+i√3 و 1−i√3 لهما نفس النسبة b/a لكنهما في ربعين مختلفين: زاويتاهما 120 و 300 درجة")
axes(f, O, 150, 150, 150, 150)
f.dot(*zp, "1", 10); f.text(zp[0] - 12, zp[1] - 8, "z", "1", 26, 700, "right")
f.dot(*wp, "2", 10); f.text(wp[0] + 12, wp[1] + 24, "w", "2", 26, 700, "left")
f.line(*zp, *wp, "mut", 3, dash=True, step=2)
f.line(O[0], O[1], zp[0], zp[1], "1", 4, step=3); arc(f, O, 36, 0, 120, "1", 5, step=3)
q = P(O, 58, 78); f.text(q[0], q[1], "120°", "1", 20, 700, "middle", step=3)
f.line(O[0], O[1], wp[0], wp[1], "2", 4, step=4); arc(f, O, 88, 0, 300, "2", 5, step=4)
q = P(O, 98, 322); f.text(q[0] + 4, q[1] + 20, "300°", "2", 22, 700, "left", step=4)
B.append(f.block(kind="steps", title="\\(z=-1+i\\sqrt3\\) و \\(w=1-i\\sqrt3\\)", frames=[
    "\\(z\\) بالربع الثاني و \\(w\\) بالربع الرابع.", "النسبة \\(\\tfrac ba=-\\sqrt3\\) نفسها للاثنين: الـ \\(\\arctan\\) لحاله ما بيفرق.",
    "من الرسمة: \\(z\\) بالربع الثاني فزاويتها \\(120^\\circ\\).", "و \\(w\\) بالربع الرابع فزاويتها \\(300^\\circ\\)."]))
box("note", "ملاحظة · <bdi>הערה 2.16 (2)</bdi>",
    "<p>عند \\(a\\neq0\\) في زاويتين \\(0\\le\\theta<2\\pi\\) بيحققوا \\(\\theta=\\arctan(\\tfrac ba)\\). لتحدد أي وحدة بتناسب \\(z\\) لازم تشوف بأي ربع هي. مثلاً \\(\\tfrac ba=-\\sqrt3\\) لـ \\(z=-1+i\\sqrt3\\) و \\(w=1-i\\sqrt3\\): \\(z\\) بالربع الثاني فزاويتها \\(120^\\circ\\)، و \\(w\\) بالرابع فزاويتها \\(300^\\circ\\).</p>")
box("note", "تذكير (مش من الكتيب)", "<p>لو \\(a=0\\) ما منقدر نقسم \\(b/a\\). بهالحالة \\(z\\) على المحور التخيلي: زاويتها \\(90^\\circ\\) إذا \\(b>0\\) و \\(270^\\circ\\) إذا \\(b<0\\).</p>")
p("ملاحظة التالتة: المرافق بيعكس الزاوية.")
O = (110, 150)
f = Fig(480, 300, alt="z = r cis θ في الأعلى ومرافقه r cis(−θ) في الأسفل بنفس الطول وزاوية معاكسة")
axes(f, O, 40, 330, 130, 130)
z1 = P(O, 190, 35); z2 = P(O, 190, -35)
f.arrow(O[0], O[1], z1[0], z1[1], "1", 4.5); f.text(z1[0] + 10, z1[1] - 8, "z", "1", 26, 700, "left")
arc(f, O, 60, 0, 35, "1", 4.5)
f.arrow(O[0], O[1], z2[0], z2[1], "2", 4.5, step=2); f.text(z2[0] + 10, z2[1] + 26, "z̄", "2", 26, 700, "left", step=2)
arc(f, O, 82, 0, -35, "2", 4.5, step=2)
f.text(O[0] + 110, O[1] - 20, "θ", "1", 24, 700, "left"); f.text(O[0] + 120, O[1] + 36, "−θ", "2", 24, 700, "left", step=2)
B.append(f.block(kind="steps", title="المرافق بزاوية معاكسة", frames=["\\(z=r\\,\\mathrm{cis}(\\theta)\\).", "\\(\\overline z\\): نفس \\(r\\) وزاوية \\(-\\theta\\)."]))
box("note", "ملاحظة · <bdi>הערה 2.16 (3)</bdi>", "<p>إذا \\(z=r\\,\\mathrm{cis}(\\theta)\\) فإن \\(\\overline z=r\\,\\mathrm{cis}(-\\theta)\\).</p>")
mc("لـ \\(z=-1-i\\)، ما زاويتها \\(\\theta\\) بين \\(0\\) و \\(360^\\circ\\)؟", ["\\(45^\\circ\\)", "\\(135^\\circ\\)", "\\(225^\\circ\\)", "\\(315^\\circ\\)"], 3,
   "\\(\\arctan(1)=45^\\circ\\) بس بأي ربع النقطة \\((-1,-1)\\)؟",
   "النقطة بالربع الثالث (سالب سالب)، فالزاوية \\(45^\\circ+180^\\circ=225^\\circ\\). الخيار \\(45^\\circ\\) هو خطأ الـ \\(\\arctan\\) من غير فحص الربع.")

# ------------------------------------------------------------------ 4
h("4 · التحويل بين الشكلين")
p("نمرّن على الاتجاهين. أول شي من القطبي للعادي: نحسب \\(a=r\\cos\\theta\\) و \\(b=r\\sin\\theta\\).")
O = (240, 130); u = 40
f = Fig(480, 290, alt="النقطة 3cis(270°) هي 3 وحدات تحت الأصل على المحور التخيلي: العدد −3i")
axes(f, O, 150, 150, 135, 120)
zt = P(O, 3 * u, 270)
f.arrow(O[0], O[1], zt[0], zt[1], "1", 5, step=1)
arc(f, O, 45, 0, 270, "2", 5, step=2)
f.text(O[0] + 54, O[1] + 40, "270°", "2", 22, 700, "left", step=2)
f.dot(*zt, "good", 11, step=3); f.text(zt[0] + 14, zt[1] + 2, "z = −3i", "good", 24, 700, "left", step=3)
f.text(O[0] + 12, O[1] + 70, "3", "1", 22, 700, "left", step=1)
B.append(f.block(kind="steps", title="\\(3\\,\\mathrm{cis}(270^\\circ)\\)", frames=[
    "الراديوس \\(3\\).", "نلف \\(270^\\circ\\) بعكس عقارب الساعة (ثلاث أرباع دورة).", "منوصل للمحور التخيلي السالب: \\(z=-3i\\)."]))
box("ex", "مثال · <bdi>דוגמה 2.17</bdi>", "<p>جد الصيغة الكرتيزية لـ \\(z=3\\,\\mathrm{cis}(270^\\circ)\\).</p>"
    "<p>\\[\\begin{cases}a=3\\cos(270^\\circ)=0\\\\ b=3\\sin(270^\\circ)=-3\\end{cases}\\quad\\Rightarrow\\quad z=-3i\\]</p>")
p("هسا الاتجاه التاني: من العادي للقطبي. أول \\(r\\) وبعدين \\(\\theta\\).")
O = (70, 240)
u = 80
zt = (O[0] + u * 1, O[1] - u * math.sqrt(3))
f = Fig(480, 300, alt="العدد 1+i√3: ضلعاه 1 و √3 والوتر 2 والزاوية 60 درجة")
axes(f, O, 30, 380, 30, 230)
f.line(O[0], O[1], zt[0], O[1], "2", 5); f.line(zt[0], O[1], zt[0], zt[1], "2", 5)
f.dot(*zt, "1", 10); f.text(zt[0] + 12, zt[1] - 8, "z = 1 + i√3", "1", 24, 700, "left")
f.text((O[0] + zt[0]) / 2, O[1] + 30, "a = 1", "2", 22, 700, step=1)
f.text(zt[0] + 14, (O[1] + zt[1]) / 2 + 8, "b = √3", "2", 22, 700, "left", step=1)
f.line(O[0], O[1], zt[0], zt[1], "good", 5.5, step=2); mm = P(O, 80, 60)
f.text(mm[0] - 14, mm[1] - 4, "r = 2", "good", 24, 700, "right", step=2)
arc(f, O, 26, 0, 60, "1", 5, step=3)
f.text(O[0] + 56, O[1] - 8, "60°", "1", 20, 700, "middle", step=3)
B.append(f.block(kind="steps", title="\\(1+i\\sqrt3\\) للشكل القطبي", frames=[
    "الضلعان \\(a=1\\) و \\(b=\\sqrt3\\).", "\\(r=\\sqrt{1+3}=2\\).", "\\(\\theta=\\arctan(\\sqrt3)=60^\\circ\\)."]))
box("ex", "مثال · <bdi>דוגמה 2.18</bdi>", "<p>جد الصيغة القطبية لـ \\(z=1+i\\sqrt3\\).</p>"
    "<p>\\[\\begin{cases}r=\\sqrt{a^2+b^2}=\\sqrt4=2\\\\ \\theta=\\arctan(\\tfrac ba)=\\arctan(\\sqrt3)=60^\\circ\\end{cases}\\quad\\Rightarrow\\quad z=2\\,\\mathrm{cis}(60^\\circ)\\]</p>")
B.append({"t": "method", "title": "من a+ib للشكل القطبي", "steps": [
    "احسب \\(r=\\sqrt{a^2+b^2}\\).",
    "احسب \\(\\arctan(b/a)\\) (إذا \\(a\\ne0\\)).",
    "شوف بأي ربع النقطة \\((a,b)\\) وصحّح الزاوية (زيد \\(180^\\circ\\) إذا \\(a<0\\)).",
    "اكتب \\(z=r\\,\\mathrm{cis}(\\theta)\\) وتأكد بالرجوع: \\(r\\cos\\theta=a\\)."]})
txt("حوّل \\(z=2\\,\\mathrm{cis}(180^\\circ)\\) للشكل \\(a+ib\\). اكتب قيمة \\(a\\).", ["-2"],
    "\\(a=r\\cos\\theta\\) و \\(\\cos180^\\circ=-1\\).", "\\(a=2\\cos180^\\circ=-2\\) و \\(b=2\\sin180^\\circ=0\\). يعني \\(z=-2\\).")

# ------------------------------------------------------------------ 5
h("5 · الضرب بالشكل القطبي")
p("هون بتظهر قوة الشكل القطبي: الضرب صار <b>ضرب أطوال وجمع زوايا</b>.")
O = (70, 260); u = 70
zt = P(O, 2 * u, 20); wt = P(O, 1.5 * u, 70); pt = P(O, 3 * u, 90)
f = Fig(480, 300, alt="ضرب z = 2cis(20°) في w = 1.5cis(70°): الطول 3 والزاوية 90 درجة")
axes(f, O, 30, 380, 20, 240)
f.arrow(O[0], O[1], zt[0], zt[1], "1", 4.5, step=1); f.text(zt[0] + 8, zt[1] - 10, "z", "1", 26, 700, "left", step=1)
f.arrow(O[0], O[1], wt[0], wt[1], "2", 4.5, step=2); f.text(wt[0] - 10, wt[1] - 6, "w", "2", 26, 700, "right", step=2)
f.arrow(O[0], O[1], pt[0], pt[1], "good", 5, step=3); f.text(pt[0] + 12, pt[1] + 6, "zw", "good", 26, 700, "left", step=3)
arc(f, O, 100, 0, 20, "1", 4, step=3)
arc(f, O, 125, 20, 90, "2", 4, step=3)
f.text(O[0] + 112, O[1] - 6, "20°", "1", 20, 700, "left", step=3)
f.text(O[0] + 100, O[1] - 135, "+70°", "2", 20, 700, "left", step=3)
f.text(O[0] + 210, O[1] - 180, "90° = 20° + 70°", "good", 20, 700, "left", step=4)
B.append(f.block(kind="steps", title="\\(2\\,\\mathrm{cis}(20^\\circ)\\cdot1.5\\,\\mathrm{cis}(70^\\circ)\\)", frames=[
    "\\(z\\): الطول \\(2\\) والزاوية \\(20^\\circ\\).", "\\(w\\): الطول \\(1.5\\) والزاوية \\(70^\\circ\\).",
    "الجداء \\(zw\\): الطول \\(2\\cdot1.5=3\\)، وبنكمّل الدوران من \\(z\\).", "الزاوية جمع الزاويتين: \\(90^\\circ\\). يعني \\(zw=3i\\)."]))
box("thm", "משפט 2.19 · <bdi>משפט</bdi>", "<p>لكل \\(z,w\\in\\mathbb{C}\\) غير صفر، إذا \\(z=r_1\\mathrm{cis}(\\theta_1)\\) و \\(w=r_2\\mathrm{cis}(\\theta_2)\\) فإن</p>"
    "<p>\\[zw=r_1r_2\\,\\mathrm{cis}(\\theta_1+\\theta_2)\\]</p>")
p("البرهان بيعتمد على جيب وجيب تمام مجموع زاويتين. منفتح الأقواس ونعرف الشكل:")
B.append({"t": "xq", "q": "<p>أثبت أن \\(zw=r_1r_2\\,\\mathrm{cis}(\\theta_1+\\theta_2)\\).</p>", "steps": [
    {"label": "نكتب الجداء", "body": "<p>\\[zw=r_1(\\cos\\theta_1+i\\sin\\theta_1)\\,r_2(\\cos\\theta_2+i\\sin\\theta_2)\\]</p>"},
    {"label": "نفتح الأقواس", "body": "<p>\\[=r_1r_2\\big((\\cos\\theta_1\\cos\\theta_2-\\sin\\theta_1\\sin\\theta_2)+i(\\sin\\theta_1\\cos\\theta_2+\\cos\\theta_1\\sin\\theta_2)\\big)\\]</p><p>(استعملنا \\(i^2=-1\\) بالحد \\(i^2\\sin\\theta_1\\sin\\theta_2\\)).</p>"},
    {"label": "قوانين مجموع زاويتين", "body": "<p>الأولى هي \\(\\cos(\\theta_1+\\theta_2)\\) والتانية \\(\\sin(\\theta_1+\\theta_2)\\).</p>"}],
    "a": "<p>\\[zw=r_1r_2\\big(\\cos(\\theta_1+\\theta_2)+i\\sin(\\theta_1+\\theta_2)\\big)=r_1r_2\\,\\mathrm{cis}(\\theta_1+\\theta_2)\\ \\blacksquare\\]</p>"})
p("من المبرهنة بتطلع عدة نتائج حلوة. أول وحدة: الضرب <b>هندسياً</b>.")
box("key", "الضرب هندسياً", "<p>بالضرب \\(z\\cdot w\\): منضرب الأطوال ومنجمع الزوايا.</p>")
mc("جد \\(2\\,\\mathrm{cis}(20^\\circ)\\cdot3\\,\\mathrm{cis}(40^\\circ)\\).", ["\\(6\\,\\mathrm{cis}(60^\\circ)\\)", "\\(5\\,\\mathrm{cis}(60^\\circ)\\)", "\\(6\\,\\mathrm{cis}(800^\\circ)\\)", "\\(6\\,\\mathrm{cis}(20^\\circ)\\)"], 1,
   "الأطوال بتنضرب والزوايا بتنجمع.",
   "الطول \\(2\\cdot3=6\\) والزاوية \\(20^\\circ+40^\\circ=60^\\circ\\). الخيار \\(5\\,\\mathrm{cis}\\) جمع الأطوال. الخيار \\(\\mathrm{cis}(800^\\circ)\\) ضرب الزوايا.")
p("ثاني نتيجة: رفع العدد لقوة. لو ضربنا \\(z\\) بنفسه \\(n\\) مرات، الطول بيصير \\(r^n\\) والزاوية \\(n\\theta\\).")
O = (60, 270); u = 80
pts = [P(O, 1.2 * u, 25), P(O, 1.44 * u, 50), P(O, 1.728 * u, 75)]
f = Fig(480, 300, alt="z و z² و z³ بالزوايا θ و 2θ و 3θ وبأطوال r و r² و r³ تكبر")
axes(f, O, 30, 380, 20, 250)
for i, (c, lab) in enumerate([("1", "z"), ("2", "z²"), ("good", "z³")]):
    f.arrow(O[0], O[1], pts[i][0], pts[i][1], c, 4.5, step=i + 1)
    f.text(pts[i][0] + 10, pts[i][1] - 4, lab, c, 26, 700, "left", step=i + 1)
f.text(460, 40, "كل ضربة: الطول × r والزاوية + θ", "mut", 20, 600, "right", step=3)
B.append(f.block(kind="steps", title="القوى: الطول يكبر والزاوية تتضاعف", frames=[
    "\\(z=r\\,\\mathrm{cis}(\\theta)\\).", "\\(z^2=r^2\\,\\mathrm{cis}(2\\theta)\\).", "\\(z^3=r^3\\,\\mathrm{cis}(3\\theta)\\)."]))
box("thm", "משפט דה־מואבר · <bdi>De Moivre</bdi>", "<p>لكل \\(n\\in\\mathbb{Z}\\) و \\(\\theta\\in\\mathbb{R}\\):</p><p>\\[\\big(r\\,\\mathrm{cis}(\\theta)\\big)^n=r^n\\,\\mathrm{cis}(n\\theta)\\]</p>")
txt("احسب \\((\\mathrm{cis}(30^\\circ))^6\\) واكتبه كعدد حقيقي.", ["-1"],
    "طبّق دي مواڤر: الزاوية بتضرب بـ \\(6\\).", "\\(\\mathrm{cis}(180^\\circ)=\\cos180^\\circ+i\\sin180^\\circ=-1\\).")
p("ثالث نتيجة: المعكوس الضربي. من الصيغة اللي شفناها \\(z^{-1}=\\frac{\\overline z}{|z|^2}\\) منعوّض \\(z=r\\,\\mathrm{cis}(\\theta)\\):")
O = (60, 150); u = 100
zt = P(O, 1.25 * u, 40); it = P(O, 0.8 * u, -40)
f = Fig(480, 300, alt="z بطول r وزاوية θ، ومعكوسه بطول 1/r وزاوية −θ تحت المحور")
axes(f, O, 30, 380, 120, 130)
f.arrow(O[0], O[1], zt[0], zt[1], "1", 4.5); f.text(zt[0] + 10, zt[1] - 4, "z", "1", 26, 700, "left")
f.arrow(O[0], O[1], it[0], it[1], "good", 4.5, step=2); f.text(it[0] + 10, it[1] + 22, "z⁻¹", "good", 26, 700, "left", step=2)
arc(f, O, 34, 0, 40, "1", 4)
arc(f, O, 50, 0, -40, "good", 4, step=2)
B.append(f.block(kind="steps", title="المعكوس الضربي", frames=[
    "\\(z=r\\,\\mathrm{cis}(\\theta)\\) كبير الطول.", "\\(z^{-1}\\): الطول بينقلب لـ \\(\\tfrac1r\\) (قصير) والزاوية بتعكس إشارتها."]))
B.append({"t": "xq", "q": "<p>احسب \\(z^{-1}\\) لـ \\(z=r\\,\\mathrm{cis}(\\theta)\\).</p>", "steps": [
    {"label": "الصيغة", "body": "<p>\\[z^{-1}=\\frac{\\overline z}{|z|^2}=\\frac1{r^2}\\overline{(r\\cos\\theta+ir\\sin\\theta)}\\]</p>"},
    {"label": "المرافق", "body": "<p>\\[=\\frac1{r^2}\\,(r\\cos\\theta-ir\\sin\\theta)\\]</p>"},
    {"label": "نخرج r", "body": "<p>\\[=\\frac1r\\big(\\cos(-\\theta)+i\\sin(-\\theta)\\big)\\]</p>"}],
    "a": "<p>يعني \\(z^{-1}\\) إله القيمة المطلقة \\(\\tfrac1r=\\tfrac1{|z|}\\) وزاويته \\(-\\theta\\).</p>"})

# ------------------------------------------------------------------ 6
h("6 · الجذور من الرتبة n (שורש מסדר n)")
p("من دي مواڤر منعرف نفتش عن عدد \\(w\\) بحيث \\(w^n=z\\). خد \\(z=r\\,\\mathrm{cis}(\\theta)\\) و \\(n\\in\\mathbb{N}\\) وعرّف:")
box("key", "الجذر الأول", "<p>\\[w_0=\\sqrt[n]{r}\\,\\mathrm{cis}\\!\\left(\\tfrac{\\theta}{n}\\right)\\ \\Rightarrow\\ w_0^n=z\\]</p>")
p("بس في كمان! لأنو \\(\\theta\\) بتتحدد بإضافة \\(2\\pi k\\)، فكل \\(k\\) بيعطي جذر:")
box("key", "الجذر رقم k", "<p>\\[w_k=\\sqrt[n]{r}\\,\\mathrm{cis}\\!\\left(\\tfrac{\\theta+2\\pi k}{n}\\right)\\ \\Rightarrow\\ w_k^n=z\\]</p>")
box("note", "ملاحظة · <bdi>הערה 2.20</bdi>", "<p>\\(w_n=w_0\\)، وبشكل أعم \\(w_k=w_{k+n}\\) لكل \\(k\\). يعني بعد \\(n\\) جذور بتبدأ القيم تتكرر.</p>")
box("def", "تعريف · <bdi>הגדרה 2.21</bdi>", "<p>لـ \\(z\\in\\mathbb{C}\\) و \\(n\\in\\mathbb{N}\\): العدد \\(w\\in\\mathbb{C}\\) هو <b>جذر من الرتبة \\(n\\)</b> (<bdi>שורש מסדר n</bdi>) لـ \\(z\\) إذا \\(w^n=z\\).</p>")
f = Fig(480, 310, alt="ثلاثة جذور تكعيبية موزعة على دائرة نصف قطرها 2 بزوايا 40 و 160 و 280 درجة، بينهما 120 درجة")
O = (240, 155); R = 108
f.circle(O[0], O[1], R, "mut", fill="none", w=3)
axes(f, O, 138, 138, 140, 140)
ang = [40, 160, 280]; col = ["1", "2", "3"]
pp = [P(O, R, a) for a in ang]
with f.group(step=5):
    f.polygon(pp, "good", fill="soft", w=3)
for i in range(3):
    f.arrow(O[0], O[1], pp[i][0], pp[i][1], col[i], 3.5, step=i + 2 if i == 0 else i + 2)
    f.dot(*pp[i], col[i], 10, step=i + 2)
    lp = P(O, R + 24, ang[i])
    f.text(lp[0], lp[1] + 8, "w₀ w₁ w₂".split()[i], col[i], 26, 700, step=i + 2)
arc(f, O, 30, 0, 40, "1", 4, step=2)
arc(f, O, 46, 40, 160, "2", 4, step=3)
arc(f, O, 46, 160, 280, "3", 4, step=4)
f.text(O[0] + 40, O[1] - 8, "40°", "1", 20, 700, "left", step=2)
q = P(O, 74, 100); f.text(q[0], q[1], "+120°", "2", 20, 700, "middle", step=3)
q = P(O, 74, 220); f.text(q[0], q[1] + 8, "+120°", "3", 20, 700, "middle", step=4)
B.append(f.block(kind="steps", title="الجذور بتتوزع بالتساوي على دائرة", frames=[
    "الدائرة: نصف قطرها \\(\\sqrt[3]{r}=2\\).", "الجذر الأول \\(w_0\\) بزاوية \\(\\tfrac\\theta3=40^\\circ\\).",
    "كل \\(k\\) بيضيف \\(\\tfrac{360^\\circ}{3}=120^\\circ\\): \\(w_1\\).", "\\(w_2\\) بعد \\(120^\\circ\\) كمان.",
    "بنوصل المثلث: جذور المعادلة \\(w^3=z\\) رؤوس مثلث متساوي الأضلاع."]))
box("thm", "משפט 2.22 · <bdi>משפט</bdi>", "<p>لـ \\(z=r\\,\\mathrm{cis}(\\theta)\\) و \\(n\\in\\mathbb{N}\\): إلـ \\(z\\) بالضبط \\(n\\) جذور مختلفة من الرتبة \\(n\\)، وهي</p>"
    "<p>\\[\\left\\{w_k=\\sqrt[n]{r}\\,\\mathrm{cis}\\!\\left(\\tfrac{\\theta+2\\pi k}{n}\\right)\\right\\}_{k=0}^{n-1}\\]</p>")
p("هسا المثال \\(2.23\\): نحل \\(z^3=-4+4\\sqrt3\\,i\\).")
f = Fig(480, 270, alt="ثلاث خطوات: r = 8 فجذره التكعيبي 2، الزاوية 120 درجة، فالجذور 40 و 160 و 280")
f.chip(16, 14, 448, 52, "r = √(16 + 48) = 8 ⇒ ∛r = 2", "1", size=22, step=1)
f.chip(16, 80, 448, 52, "arctan(−√3), Q2 ⇒ θ = 120°", "2", size=22, step=2)
f.chip(16, 146, 448, 52, "w_k = 2cis((120° + 360°k) / 3)", "3", size=22, step=3)
f.chip(16, 212, 448, 48, "40°  ,  160°  ,  280°", "good", solid=True, size=24, step=4)
B.append(f.block(kind="steps", title="حل \\(z^3=-4+4\\sqrt3\\,i\\)", frames=[
    "الطول: \\(r=8\\) فجذره التكعيبي \\(2\\).", "الزاوية: \\(\\arctan(-\\sqrt3)\\) والنقطة بالربع الثاني: \\(120^\\circ\\).",
    "منعوّض بالصيغة \\(w_k\\).", "\\(k=0,1,2\\) بيعطوا ثلاث زوايا."]))
box("ex", "مثال · <bdi>דוגמה 2.23</bdi>", "<p>جد كل حلول \\(z^3=-4+i4\\sqrt3\\).</p>"
    "<p>الراديوس: \\(r=\\sqrt{(-4)^2+(4\\sqrt3)^2}=8\\)، فـ \\(\\sqrt[3]r=2\\).</p>"
    "<p>الزاوية: \\(\\theta=\\arctan\\!\\Big(\\tfrac{4\\sqrt3}{-4}\\Big)=\\arctan(-\\sqrt3)\\). العدد بالربع الثاني فالزاوية \\(120^\\circ\\).</p>"
    "<p>من الصيغة:</p><p>\\[w_0=2\\,\\mathrm{cis}(40^\\circ),\\quad w_1=2\\,\\mathrm{cis}(160^\\circ),\\quad w_2=2\\,\\mathrm{cis}(280^\\circ)\\]</p>")
mc("كم جذر مختلف من الرتبة \\(5\\) لعدد مركّب \\(z\\neq0\\)؟", ["\\(5\\)", "\\(1\\)", "\\(2\\)", "\\(10\\)"], 1,
   "حسب المبرهنة 2.22: عدد الجذور = الرتبة.", "بالضبط \\(n=5\\) جذور (\\(k=0,\\dots,4\\)). بعد ذلك بتتكرر القيم (\\(w_5=w_0\\)).")
txt("جذور \\(z^3=8\\) هي \\(2\\,\\mathrm{cis}(120^\\circ k)\\). كم زاوية الجذر \\(w_1\\) بالدرجات؟", ["120"],
    "\\(8=8\\,\\mathrm{cis}(0^\\circ)\\) فـ \\(\\theta=0\\). عوّض في \\(\\tfrac{\\theta+360^\\circ k}{3}\\) مع \\(k=1\\).", "\\(\\tfrac{0+360}{3}=120^\\circ\\).")

# ------------------------------------------------------------------ closing
B.append({"t": "mistakes", "title": "أخطاء شائعة", "rows": [
    {"no": "\\(\\theta=\\arctan(b/a)\\) دايماً بلا فحص الربع", "yes": "شوف الربع: إذا \\(a<0\\) زيد \\(180^\\circ\\)"},
    {"no": "ضرب: نجمع الأطوال", "yes": "نضرب الأطوال ونجمع الزوايا"},
    {"no": "\\((r\\,\\mathrm{cis}\\,\\theta)^n=r\\,\\mathrm{cis}(n\\theta)\\)", "yes": "\\(r^n\\,\\mathrm{cis}(n\\theta)\\) (الطول كمان بيترفع للقوة)"},
    {"no": "جذر \\(n\\) واحد بس", "yes": "في \\(n\\) جذور، \\(k=0,\\dots,n-1\\)"}]})
B.append({"t": "checklist", "title": "شو لازم تعرف من هالدرس", "items": [
    "الشكل القطبي \\(z=r\\,\\mathrm{cis}(\\theta)\\) (<bdi>הצגה קוטבית</bdi>) مقابل الكرتيزي (<bdi>הצגה קרטזית</bdi>)",
    "\\(r=\\sqrt{a^2+b^2}\\)، \\(a=r\\cos\\theta\\)، \\(b=r\\sin\\theta\\)",
    "الأرغومنت \\(\\arg(z)\\) (<bdi>ארגומנט</bdi>) محدد حتى \\(2\\pi k\\)، وفحص الربع",
    "\\(\\overline z=r\\,\\mathrm{cis}(-\\theta)\\)",
    "\\(zw=r_1r_2\\,\\mathrm{cis}(\\theta_1+\\theta_2)\\) و (<bdi>משפט דה־מואבר</bdi>) \\((r\\,\\mathrm{cis}\\theta)^n=r^n\\mathrm{cis}(n\\theta)\\)",
    "\\(z^{-1}=\\tfrac1r\\,\\mathrm{cis}(-\\theta)\\)",
    "\\(n\\) جذور (<bdi>שורש מסדר n</bdi>): \\(w_k=\\sqrt[n]r\\,\\mathrm{cis}\\big(\\tfrac{\\theta+2\\pi k}{n}\\big)\\)"]})
for fr, bk in [("\\(r\\,\\mathrm{cis}(\\theta)\\) تعني؟", "\\(r(\\cos\\theta+i\\sin\\theta)\\)"),
               ("\\(zw\\) بالقطبي؟", "\\(r_1r_2\\,\\mathrm{cis}(\\theta_1+\\theta_2)\\)"),
               ("دي مواڤر؟", "\\((r\\,\\mathrm{cis}\\theta)^n=r^n\\,\\mathrm{cis}(n\\theta)\\)"),
               ("جذور \\(z=r\\,\\mathrm{cis}\\theta\\) من الرتبة \\(n\\)؟", "\\(\\sqrt[n]r\\,\\mathrm{cis}\\big(\\tfrac{\\theta+2\\pi k}{n}\\big),\\ k=0..n-1\\)"),
               ("\\(\\overline{r\\,\\mathrm{cis}\\theta}\\)؟", "\\(r\\,\\mathrm{cis}(-\\theta)\\)")]:
    B.append({"t": "card", "front": fr, "back": bk})
mc("ما قيمة \\((1+i)^8\\)؟ (تلميح: \\(1+i=\\sqrt2\\,\\mathrm{cis}(45^\\circ)\\))", ["\\(16\\)", "\\(8\\)", "\\(16i\\)", "\\(-16\\)"], 1,
   "طبّق دي مواڤر: الطول \\((\\sqrt2)^8\\) والزاوية \\(8\\cdot45^\\circ\\).",
   "\\((\\sqrt2)^8=16\\) والزاوية \\(360^\\circ\\) فـ \\(\\mathrm{cis}(360^\\circ)=1\\). النتيجة \\(16\\). الخيار \\(8\\) رفع الجذر غلط.")
mc("حلول \\(z^2=-4\\) هي:", ["\\(2i\\) و \\(-2i\\)", "\\(2\\) و \\(-2\\)", "\\(4i\\) و \\(-4i\\)", "\\(2i\\) فقط"], 1,
   "\\(-4=4\\,\\mathrm{cis}(180^\\circ)\\). في جذرين (\\(n=2\\)).",
   "\\(w_k=2\\,\\mathrm{cis}\\big(\\tfrac{180^\\circ+360^\\circ k}{2}\\big)\\): \\(k=0\\) يعطي \\(2\\,\\mathrm{cis}(90^\\circ)=2i\\) و \\(k=1\\) يعطي \\(2\\,\\mathrm{cis}(270^\\circ)=-2i\\).")
B.append({"t": "xq", "q": "<p>جد كل حلول \\(z^2=-1+i\\sqrt3\\) بالشكل القطبي.</p>", "steps": [
    {"label": "الشكل القطبي للطرف الأيمن", "body": "<p>\\(r=\\sqrt{1+3}=2\\). \\(\\arctan(-\\sqrt3)\\) والنقطة بالربع الثاني فـ \\(\\theta=120^\\circ\\).</p>"},
    {"label": "الصيغة", "body": "<p>\\(w_k=\\sqrt2\\,\\mathrm{cis}\\big(\\tfrac{120^\\circ+360^\\circ k}{2}\\big)\\)، \\(k=0,1\\).</p>"}],
    "a": "<p>\\(w_0=\\sqrt2\\,\\mathrm{cis}(60^\\circ)\\) و \\(w_1=\\sqrt2\\,\\mathrm{cis}(240^\\circ)\\).</p>"})

lesson = {"slug": "polar-form", "title": "التمثيل القطبي", "he": "הצגה קוטבית של מספר מרוכב",
          "ref": "חוברת §2.1 · עמ׳ 17–20", "minutes": 26,
          "desc": "الراديوس والزاوية، الضرب ودي مواڤر والمعكوس، والجذور من الرتبة n.", "blocks": B}
probs = lint(lesson)
if probs: raise SystemExit("lint: %s" % probs)
with open(OUT, "w", encoding="utf-8") as fh: json.dump(lesson, fh, ensure_ascii=False, indent=2)
n = lambda t: sum(1 for b in B if b["t"] == t)
print("wrote", OUT, "figures", n("figure"), "steps", n("steps"), "quizzes", n("quiz"))

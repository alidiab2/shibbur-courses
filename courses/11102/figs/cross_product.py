#!/usr/bin/env python3
"""Lesson `cross-product` (section 1.2 + 1.2.1, booklet p6-8). Run: python3 cross_product.py -> ../lessons/cross-product.json"""
import math
from _ch1lib import *


def fig_idea():
    f = Fig(480, 300, alt="مستوى بشكل متوازي أضلاع يمر ببداية المحاور ومتجه w عمودي عليه نحو الأعلى")
    O, A, B, C = (90, 240), (300, 240), (200, 170), (410, 170)
    f.arrow(*O, *A, c="1", w=5, step=1); f.text(A[0] + 4, A[1] + 32, "v", c="1", size=24, step=1)
    f.arrow(*O, *B, c="2", w=5, step=1); f.text(B[0] - 30, B[1] - 6, "u", c="2", size=24, step=1)
    f.polygon([O, A, C, B], c="mut", fill="soft", step=2)
    f.text(250, 212, "مساحة", c="ink", size=20, step=2)
    f.arrow(*O, O[0], 50, c="good", w=6, step=3)
    f.text(O[0] + 16, 60, "w", c="good", size=26, step=3, anchor="left")
    f.line(O[0], O[1] - 22, O[0] + 22, O[1] - 22, c="ink", w=3, step=3)
    f.line(O[0] + 22, O[1] - 22, O[0] + 22, O[1], c="ink", w=3, step=3)
    return f.block("", kind="steps", title="شو بدنا من المتجه الثالث",
                   frames=["متجهين \\(\\vec v,\\vec u\\) مش متناسبين", "هم بيفتحوا مستوى (متوازي أضلاع بينهم)", "بدنا \\(\\vec w\\) عمودي على المستوى كله"])


def fig_area():
    f = Fig(480, 270, alt="متوازي أضلاع ضلعاه v و u وزاوية ألفا بينهما والارتفاع |u| sin ألفا، فالمساحة |v||u| sin ألفا")
    O, A = (70, 215), (300, 215)
    ang = 55; L = 150
    B = (O[0] + L * math.cos(math.radians(ang)), O[1] - L * math.sin(math.radians(ang)))
    C = (A[0] + B[0] - O[0], B[1])
    f.polygon([O, A, C, B], c="mut", fill="soft", step=1)
    f.arrow(*O, *A, c="1", w=5, step=1); f.text(185, 248, "|v|", c="1", size=22, step=1)
    f.arrow(*O, *B, c="2", w=5, step=1); f.text(B[0] - 70, (B[1] + O[1]) / 2, "|u|", c="2", size=22, step=1)
    pts = [(O[0] + 40 * math.cos(math.radians(a)), O[1] - 40 * math.sin(math.radians(a))) for a in range(0, ang + 1, 5)]
    f.curve(pts, c="ink", w=3, smooth=False, step=2)
    f.text(O[0] + 62, O[1] - 16, "α", c="ink", size=22, step=2)
    f.line(B[0], B[1], B[0], O[1], c="good", w=4, dash=True, step=3)
    f.text(B[0] + 10, (B[1] + O[1]) / 2, "h = |u|sin α", c="good", size=20, anchor="left", step=3)
    f.text(240, 36, "|w| = |v|·|u|·sin α", c="good", size=22, step=4)
    return f.block("", kind="steps", title="الطول = مساحة متوازي الأضلاع",
                   frames=["متوازي الأضلاع الذي يفتحه \\(\\vec v,\\vec u\\)", "الزاوية بينهم \\(\\alpha\\)", "الارتفاع \\(h=|\\vec u|\\sin\\alpha\\)", "المساحة = القاعدة × الارتفاع = \\(|\\vec w|\\)"])


def fig_hand():
    f = Fig(480, 290, alt="قاعدة اليد اليمنى: نلف الأصابع من v نحو u فيشير الإبهام نحو w")
    O = (130, 235)
    A = (O[0] + 220, O[1])
    B = (O[0] + 130 * math.cos(math.radians(50)), O[1] - 130 * math.sin(math.radians(50)))
    f.arrow(*O, *A, c="1", w=5, step=1); f.text(A[0] + 6, A[1] + 28, "v", c="1", size=24, step=1)
    f.arrow(*O, *B, c="2", w=5, step=1); f.text(B[0] + 12, B[1] - 8, "u", c="2", size=24, step=1, anchor="left")
    pts = [(O[0] + 75 * math.cos(math.radians(a)), O[1] - 75 * math.sin(math.radians(a))) for a in range(0, 41, 5)]
    f.curve(pts, c="ink", w=4, smooth=False, step=2)
    f.arrow(pts[-2][0], pts[-2][1], *( (O[0] + 75 * math.cos(math.radians(50)), O[1] - 75 * math.sin(math.radians(50))) ), c="ink", w=4, step=2)
    f.text(O[0] + 110, O[1] - 52, "ندور", c="ink", size=20, step=2, anchor="left")
    f.arrow(*O, O[0], 40, c="good", w=6, step=3)
    f.text(O[0] + 16, 52, "w = v × u", c="good", size=22, step=3, anchor="left")
    return f.block("", kind="steps", title="قاعدة اليد اليمنى",
                   frames=["نحط \\(\\vec v\\) ثم \\(\\vec u\\) بنفس المستوى", "نلف أصابع اليد اليمنى من \\(\\vec v\\) نحو \\(\\vec u\\)", "الإبهام بيشير لاتجاه \\(\\vec w=\\vec v\\times\\vec u\\)"])


def mat(f, x, y, rows, cs=70, rh=50):
    f.matrix(x, y, rows, cell_w=cs, cell_h=rh, size=24)
    f.line(x - 12, y - 4, x - 12, y + rh * 3 + 4, c="ink", w=3)
    f.line(x + cs * 3 + 12, y - 4, x + cs * 3 + 12, y + rh * 3 + 4, c="ink", w=3)


def det_fig(rows, comps, title, alt, frames, x=30, y=40):
    f = Fig(480, 260, alt=alt)
    cs, rh = 56, 52
    mat(f, x, y, rows, cs, rh)
    cover = [[(1, 1), (1, 2), (2, 1), (2, 2)], [(1, 0), (1, 2), (2, 0), (2, 2)], [(1, 0), (1, 1), (2, 0), (2, 1)]]
    for k in range(3):
        for r, c in cover[k]:
            f.rect(x + c * cs + 4, y + r * rh + 4, cs - 8, rh - 8, c="2", fill="soft", r=8, only=k + 2)
        f.rect(x + k * cs + 4, y + 4, cs - 8, rh - 8, c="1", fill="soft", r=8, only=k + 2)
        f.chip(x + cs * 3 + 30, y + 6 + k * 56, 230, 46, comps[k], c="good", size=20, step=k + 2)
    return f.block("", kind="steps", title=title, frames=frames)


def fig_props():
    f = Fig(480, 280, alt="v×u يشير للأعلى و u×v يشير للأسفل بنفس الطول فهما متعاكسان")
    O = (200, 140)
    f.arrow(*O, O[0], 30, c="good", w=6, step=1); f.text(O[0] + 16, 50, "v × u", c="good", size=22, step=1, anchor="left")
    f.arrow(*O, O[0], 250, c="bad", w=6, step=2); f.text(O[0] + 16, 245, "u × v", c="bad", size=22, step=2, anchor="left")
    f.arrow(*O, O[0] + 130, O[1] + 20, c="1", w=5); f.text(O[0] + 136, O[1] + 46, "v", c="1", size=22)
    f.arrow(*O, O[0] + 70, O[1] - 14, c="2", w=5); f.text(O[0] + 66, O[1] - 26, "u", c="2", size=22)
    return f.block("", kind="steps", title="تبديل المتجهين بيعكس الاتجاه",
                   frames=["\\(\\vec v\\times\\vec u\\) للأعلى", "\\(\\vec u\\times\\vec v=-\\vec v\\times\\vec u\\): نفس الطول واتجاه معاكس"])


def build():
    b = []
    b.append(WHY("الضرب المتجهي بياخد متجهين من \\(\\mathbb R^3\\) وبيعطي <b>متجه</b> عمودي عليهم. هو اللي بيعطينا معادلة المستوى بالدرس الجاي.",
                 ["الفكرة: متجه عمودي على المستوى", "التعريف (<bdi>הגדרה 1.16</bdi>) بثلاث شروط", "قاعدة اليد اليمنى", "الصيغة التحليلية بـ \\(\\vec i,\\vec j,\\vec k\\)", "مثال وتحقق", "الخصائص (<bdi>טענה 1.19</bdi>)"]))

    b += [H("1 · الفكرة: متجه عمودي"),
          P("بالفراغ، كل متجهين مش متناسبين بيفتحوا <b>مستوى</b> بيمر ببداية المحاور. المستوى هاد إله اتجاه عمودي عليه."),
          P("بدنا نحدد متجه ثالث \\(\\vec w\\) بشكل وحيد. بنحتاج نعرف <b>طوله</b> و<b>اتجاهه</b> بالضبط (من ضمن الاتنين اللي بيعاكسوا بعض)."),
          fig_idea(),
          P("الطول: بنختاره يساوي مساحة متوازي الأضلاع اللي بيفتحه \\(\\vec v,\\vec u\\). الاتجاه: بقاعدة اليد اليمنى.")]

    b += [H("2 · التعريف"),
          fig_area(),
          BOX("def", "تعريف · <bdi>הגדרה 1.16</bdi>", "<p>ليكن \\(\\vec v,\\vec u\\in\\mathbb R^3\\). الضرب المتجهي (<bdi>מכפלה וקטורית</bdi>) \\(\\vec w=\\vec v\\times\\vec u\\) هو المتجه الذي يحقق:</p><ol>"
              "<li>\\(\\vec v\\perp\\vec w,\\quad \\vec u\\perp\\vec w\\)</li>"
              "<li>\\(|\\vec w|=|\\vec u|\\cdot|\\vec v|\\,|\\sin(\\alpha)|\\) حيث \\(\\alpha\\) الزاوية بين \\(\\vec v\\) و \\(\\vec u\\)</li>"
              "<li>\\(\\langle\\vec v,\\vec u,\\vec w\\rangle\\) منظومة يد يمين (<bdi>מערכת יד ימין</bdi>)</li></ol>"),
          P("طبعا هالتعريف مش مريح للحساب. بعد شوي منعطي صيغة جاهزة بالإحداثيات."),
          MC("\\(|\\vec v|=2\\)، \\(|\\vec u|=3\\) والزاوية بينهم \\(30^\\circ\\). كم \\(|\\vec v\\times\\vec u|\\)؟",
             ["\\(6\\)", "\\(3\\)", "\\(3\\sqrt{3}\\)"], 2,
             "استعمل \\(\\sin\\) مش \\(\\cos\\).", "\\(2\\cdot3\\cdot\\sin30^\\circ=6\\cdot\\frac12=3\\). الخيار 1 نسي الجيب؛ الخيار 3 استعمل \\(\\cos30^\\circ\\).")]

    b += [H("3 · قاعدة اليد اليمنى"),
          P("الشرط الثالث بيقول أي واحد من الاتجاهين العموديين نختار. إذا لفينا أصابع اليد اليمنى من \\(\\vec v\\) نحو \\(\\vec u\\)، الإبهام بيشير لـ \\(\\vec w\\)."),
          fig_hand(),
          P("هيك الترتيب مهم: \\(\\vec v\\times\\vec u\\) غير \\(\\vec u\\times\\vec v\\). بنرجع له بالخصائص.")]

    b += [H("4 · الصيغة التحليلية"),
          P("للحساب بنستعمل ثلاث متجهات خاصة (الترميز المقبول):"),
          P("\\[\\vec i=\\begin{pmatrix}1\\\\0\\\\0\\end{pmatrix},\\quad \\vec j=\\begin{pmatrix}0\\\\1\\\\0\\end{pmatrix},\\quad \\vec k=\\begin{pmatrix}0\\\\0\\\\1\\end{pmatrix}\\]"),
          det_fig([["i", "j", "k"], ["a", "b", "c"], ["d", "e", "f"]],
                  ["bf − ce", "cd − af", "ae − bd"], "الصيغة خطوة خطوة", "مصفوفة 3 في 3 صفها الأول i j k ونحذف عمود كل مرة لنحسب مركبة من النتيجة",
                  ["نكتب المتجهات بصفين تحت \\(\\vec i,\\vec j,\\vec k\\)", "المركبة الأولى: نحذف عمود \\(\\vec i\\): \\(bf-ce\\)", "الثانية: نحذف عمود \\(\\vec j\\) (بإشارة معكوسة): \\(cd-af\\)", "الثالثة: نحذف عمود \\(\\vec k\\): \\(ae-bd\\)"]),
          BOX("thm", "טענה 1.17", "<p>ليكن \\(\\vec v=\\begin{pmatrix}a\\\\b\\\\c\\end{pmatrix},\\ \\vec u=\\begin{pmatrix}d\\\\e\\\\f\\end{pmatrix}\\in\\mathbb R^3\\). عندها:</p><p>\\[\\vec v\\times\\vec u=\\begin{vmatrix}\\vec i&\\vec j&\\vec k\\\\ a&b&c\\\\ d&e&f\\end{vmatrix}=\\begin{pmatrix}bf-ce\\\\ cd-af\\\\ ae-bd\\end{pmatrix}\\]</p>"),
          BOX("note", "ملاحظة", "<p>الصيغة بتتعلق بمفهوم المحدد (<bdi>דטרמיננטה</bdi>) اللي منشوفه لاحقا بالكورس، والمحاضر هون بيعطي الصيغة بدون برهان.</p>"),
          BOX("idea", "واجب بيتي من المحاضر", "<p>تحقق إنّ المتجه اللي بيطلع بالصيغة بيحقق الشرطين الأولين من التعريف: عمودي على \\(\\vec v\\) وعلى \\(\\vec u\\). منعمله بالمثال تحت.</p>")]

    b += [H("5 · مثال وتحقق"),
          det_fig([["i", "j", "k"], ["1", "−1", "0"], ["0", "1", "2"]],
                  ["(−1)·2 − 0·1 = −2", "0·0 − 1·2 = −2", "1·1 − (−1)·0 = 1"], "الضرب المتجهي للمثال 1.18", "حساب الضرب المتجهي للمتجهين (1,-1,0) و (0,1,2) فتطلع النتيجة (-2,-2,1)",
                  ["\\(\\vec v=(1,-1,0)\\) و \\(\\vec u=(0,1,2)\\)", "المركبة الأولى: \\(-2\\)", "المركبة الثانية: \\(-2\\)", "الثالثة: \\(1\\)"]),
          BOX("ex", "مثال · <bdi>דוגמה 1.18</bdi>", "<p>ليكن \\(\\vec v=(1,-1,0)\\) و \\(\\vec u=(0,1,2)\\) في \\(\\mathbb R^3\\). عندها:</p><p>\\[\\vec v\\times\\vec u=\\begin{vmatrix}\\vec i&\\vec j&\\vec k\\\\1&-1&0\\\\0&1&2\\end{vmatrix}=\\begin{pmatrix}-2\\\\-2\\\\1\\end{pmatrix}\\]</p>"),
          BOX("ex", "تحقق (الواجب)", "<p>نضرب سلميا بكل متجه أصلي:</p><p>\\[\\vec w\\cdot\\vec v=-2+2+0=0\\]</p><p>\\[\\vec w\\cdot\\vec u=0-2+2=0\\]</p><p>الاتنين صفر يعني \\(\\vec w\\) عمودي عليهم. (قاعدة جيدة تتحقق فيها من حسابك.)</p>"),
          MC("\\(\\vec i\\times\\vec j\\) بيطلع:",
             ["\\(\\vec k\\)", "\\(-\\vec k\\)", "\\(\\vec 0\\)"], 1,
             "\\(\\vec i=(1,0,0),\\ \\vec j=(0,1,0)\\). طبّق الصيغة.", "\\(a=1,b=0,c=0,d=0,e=1,f=0\\): \\((0,\\,0,\\,1\\cdot1-0)=(0,0,1)=\\vec k\\). يد يمنى: من \\(x\\) لـ \\(y\\) والإبهام لـ \\(z\\).")]

    b += [H("6 · الخصائص"),
          fig_props(),
          BOX("thm", "טענה 1.19", "<p>ليكن \\(\\vec v_1,\\vec v_2,\\vec v_3\\in\\mathbb R^3\\). عندها:</p><ul>"
              "<li>\\(\\vec v_1\\times\\vec v_2=-\\vec v_2\\times\\vec v_1\\)</li>"
              "<li>\\((\\alpha\\vec v_1)\\times\\vec v_2=\\alpha(\\vec v_1\\times\\vec v_2)\\)</li>"
              "<li>\\((\\vec v_1+\\vec v_2)\\times\\vec v_3=\\vec v_1\\times\\vec v_3+\\vec v_2\\times\\vec v_3\\)</li></ul>"),
          P("هاي الخصائص بتتبرهن من التعريف أو من الصيغة. أهم شي: الضرب المتجهي <b>مش تبديلي</b>."),
          BOX("ex", "مثال", "<p>مثلا \\(\\vec j\\times\\vec i=-\\vec k\\) بينما \\(\\vec i\\times\\vec j=\\vec k\\).</p>"),
          MC("\\(\\vec v\\times\\vec u=(1,2,3)\\). كم \\(\\vec u\\times\\vec v\\)؟",
             ["\\((1,2,3)\\)", "\\((-1,-2,-3)\\)", "\\((3,2,1)\\)"], 2,
             "تبديل الترتيب بيعمل شو؟", "\\(\\vec u\\times\\vec v=-\\vec v\\times\\vec u=(-1,-2,-3)\\).")]

    b += [METHOD("حساب \\(\\vec v\\times\\vec u\\) بالإحداثيات", [
              "اكتب \\(\\vec v=(a,b,c)\\) و \\(\\vec u=(d,e,f)\\) بحسب الترتيب المطلوب.",
              "الأولى: \\(bf-ce\\)، الثانية: \\(cd-af\\)، الثالثة: \\(ae-bd\\).",
              "تحقق: النتيجة ضرب سلمي بكل متجه أصلي = 0."]),
          MISTAKES("أخطاء شائعة", [
              ("\\(\\vec v\\times\\vec u=\\vec u\\times\\vec v\\)", "\\(\\vec v\\times\\vec u=-\\vec u\\times\\vec v\\)"),
              ("الضرب المتجهي عدد", "الضرب المتجهي <b>متجه</b> (والسلمي هو العدد)"),
              ("المركبة الثانية \\(af-cd\\)", "المركبة الثانية \\(cd-af\\) (إشارة معكوسة)")]),
          CHECK(["الضرب المتجهي (<bdi>מכפלה וקטורית</bdi>) متجه عمودي على المتجهين.",
                 "طوله \\(|\\vec v||\\vec u||\\sin\\alpha|\\) = مساحة متوازي الأضلاع.",
                 "اتجاهه بقاعدة اليد اليمنى (<bdi>מערכת יד ימין</bdi>).",
                 "الصيغة \\((bf-ce,\\ cd-af,\\ ae-bd)\\) (<bdi>טענה 1.17</bdi>).",
                 "تقلب الإشارة عند تبديل الترتيب (<bdi>טענה 1.19</bdi>)."]),
          CARD("\\(\\vec v\\times\\vec u\\)", "\\((bf-ce,\\ cd-af,\\ ae-bd)\\)"),
          CARD("طول الضرب المتجهي", "\\(|\\vec v|\\,|\\vec u|\\,|\\sin\\alpha|\\) = مساحة متوازي الأضلاع"),
          CARD("\\(\\vec u\\times\\vec v\\)", "\\(-\\vec v\\times\\vec u\\)"),
          TQ("احسب \\(\\begin{pmatrix}2\\\\0\\\\1\\end{pmatrix}\\times\\begin{pmatrix}1\\\\1\\\\0\\end{pmatrix}\\) واكتب المركبة الأخيرة.", ["2"],
             "المركبة الثالثة هي \\(ae-bd\\).", "\\(a=2,b=0,d=1,e=1\\): \\(2\\cdot1-0\\cdot1=2\\). النتيجة كاملة \\((-1,1,2)\\)."),
          MC("كم مساحة متوازي الأضلاع الذي يفتحه \\((3,0,0)\\) و \\((0,4,0)\\)؟",
             ["\\(7\\)", "\\(12\\)", "\\(0\\)"], 2,
             "المساحة = طول الضرب المتجهي.", "\\((3,0,0)\\times(0,4,0)=(0,0,12)\\) وطوله 12. (الزاوية قائمة: \\(3\\cdot4\\cdot1\\).)"),
          MC("كم \\(\\vec v\\times\\vec v\\)؟",
             ["\\(|\\vec v|^2\\)", "\\(\\vec 0\\)", "\\(\\vec v\\)"], 2,
             "الزاوية بين متجه ونفسه كم؟", "\\(\\sin0=0\\) فالطول 0 والنتيجة \\(\\vec 0\\). (الخيار 1 هو \\(\\vec v\\cdot\\vec v\\) السلمي.)")]
    write_lesson("cross-product", "الضرب المتجهي (מכפלה וקטורית)", "מכפלה וקטורית", "חוברת §1.2 · עמ׳ 6–8",
                 "تعريف الضرب المتجهي، قاعدة اليد اليمنى، الصيغة بالإحداثيات والخصائص.", b)


if __name__ == "__main__":
    build()

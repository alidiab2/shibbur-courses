"""Shared helpers for the chapter-1 figure/lesson scripts of course 11102 (algebra 1)."""
import sys, os, json, re
sys.path.insert(0, os.path.expanduser("~/Developer/ali-skills/ali-skills-shibbur-course/scripts"))
from fk import Fig  # noqa

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lessons")


def H(t): return {"t": "h", "text": t}
def P(s): return {"t": "p", "html": "<p>%s</p>" % s}
def BOX(kind, title, html): return {"t": "box", "kind": kind, "title": title, "html": html}
def MATH(tex): return {"t": "math", "tex": tex}
def HTML(h): return {"t": "html", "html": h}
def CARD(f, b): return {"t": "card", "front": f, "back": b}
def CHECK(items, title="شو لازم تعرف من هالدرس"): return {"t": "checklist", "title": title, "items": items}
def METHOD(title, steps): return {"t": "method", "title": title, "steps": steps}
def MISTAKES(title, rows): return {"t": "mistakes", "title": title, "rows": [{"no": a, "yes": b} for a, b in rows]}
def WHY(intro, points, when=None):
    h = "<p>%s</p><p><b>بهالدرس:</b></p><ol>%s</ol>" % (intro, "".join("<li>%s</li>" % p for p in points))
    if when: h += "<p>%s</p>" % when
    return {"t": "why", "html": h}


def MC(prompt, options, ans, hint, sol):
    return {"t": "quiz", "q": {"kind": "mc", "prompt": "<p>%s</p>" % prompt,
            "options": [{"v": str(i + 1), "html": o} for i, o in enumerate(options)],
            "answer": [str(ans)], "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}}


def TQ(prompt, answers, hint, sol):
    return {"t": "quiz", "q": {"kind": "text", "prompt": "<p>%s</p>" % prompt, "answer": answers,
            "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}}


def proj3(ox, oy, s):
    """oblique projection: x toward viewer (down-left), y right, z up"""
    def f(x, y, z):
        return (ox + s * (y - 0.5 * x), oy - s * (z - 0.38 * x))
    return f


def write_lesson(slug, title, he, ref, desc, blocks):
    words = 0
    for b in blocks:
        for k in ("html", "text", "tex"):
            if k in b: words += len(re.sub(r"<[^>]+>", " ", b[k]).split())
    figs = sum(1 for b in blocks if b["t"] == "figure")
    steps = sum(1 for b in blocks if b["t"] == "steps")
    quiz = sum(1 for b in blocks if b["t"] == "quiz")
    minutes = max(5, round(words / 120 + figs + steps + 1.5 * quiz))
    d = {"slug": slug, "title": title, "he": he, "ref": ref, "minutes": minutes, "desc": desc, "blocks": blocks}
    path = os.path.join(OUT, slug + ".json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("%s: %d blocks, figures %d, steps %d, quizzes %d, ~%d min" % (slug, len(blocks), figs, steps, quiz, minutes))

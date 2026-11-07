"""Shared helpers for the chapter-2 lesson scripts (11004). Each <slug>.py builds figures + the lesson JSON."""
import sys, os, json, re, math
sys.path.insert(0, os.path.expanduser("~/Developer/ali-skills/ali-skills-shibbur-course/scripts"))
from fk import Fig

LESSONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lessons")


def P(html): return {"t": "p", "html": "<p>%s</p>" % html}
def H(text): return {"t": "h", "text": text}
def BOX(kind, title, html): return {"t": "box", "kind": kind, "title": title, "html": html}
def CARD(front, back): return {"t": "card", "front": front, "back": back}
def CHECK(items, title="شو لازم تعرف من هالدرس"): return {"t": "checklist", "title": title, "items": items}
def WHY(html): return {"t": "why", "html": html}
def METHOD(title, steps): return {"t": "method", "title": title, "steps": steps}
def MISTAKES(title, rows): return {"t": "mistakes", "title": title, "rows": [{"no": a, "yes": b} for a, b in rows]}
def XQ(q, steps, a): return {"t": "xq", "q": q, "steps": [{"label": l, "body": b} for l, b in steps], "a": a}
def MATH(tex): return {"t": "math", "tex": tex}


def MC(prompt, options, ans, hint, sol):
    return {"t": "quiz", "q": {"kind": "mc", "prompt": "<p>%s</p>" % prompt,
            "options": [{"v": str(i + 1), "html": o} for i, o in enumerate(options)],
            "answer": [str(ans)], "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}}


def TX(prompt, answers, hint, sol):
    return {"t": "quiz", "q": {"kind": "text", "prompt": "<p>%s</p>" % prompt, "answer": answers,
            "hint": "<p>%s</p>" % hint, "solution": "<p>%s</p>" % sol}}


_TAGS = r"(p|b|strong|i|em|code|bdi|span|br|ul|ol|li|sub|sup|small|table|tr|td|th|pre|div|details|summary)"


def _fix(o, key=None):
    if isinstance(o, str):
        if key == "svg": return o
        o = re.sub(r"<(/?)u>", r"<\1em>", o)
        return re.sub(r"<(?!/?" + _TAGS + r"\b)", "&lt;", o)
    if isinstance(o, list): return [_fix(x) for x in o]
    if isinstance(o, dict): return {k: _fix(v, k) for k, v in o.items()}
    return o


def write_lesson(slug, title, he, ref, desc, blocks):
    blocks = _fix(blocks)
    words = 0
    figs = quizzes = 0
    for b in blocks:
        txt = json.dumps({k: v for k, v in b.items() if k != "svg"}, ensure_ascii=False)
        words += len(re.sub(r"<[^>]+>|\\[a-z]+", " ", txt).split())
        figs += b["t"] in ("figure", "steps")
        quizzes += b["t"] == "quiz"
    minutes = max(5, round(words / 120 + figs + 1.5 * quizzes))
    kinds = {}
    for b in blocks: kinds[b["t"]] = kinds.get(b["t"], 0) + 1
    L = {"slug": slug, "title": title, "he": he, "ref": ref, "minutes": minutes, "desc": desc, "blocks": blocks}
    os.makedirs(LESSONS, exist_ok=True)
    with open(os.path.join(LESSONS, slug + ".json"), "w", encoding="utf-8") as fh:
        json.dump(L, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("%s: %d blocks, figure=%d steps=%d quiz=%d, ~%d min" % (
        slug, len(blocks), kinds.get("figure", 0), kinds.get("steps", 0), kinds.get("quiz", 0), minutes))


# ---------- arrow diagrams between two sets ----------
def sets(f, xa, xb, A, B, yc=130, gap=52, tA="A", tB="B", cA="1", cB="2", colA=None, colB=None,
         step=None, only=None, until=None, r=20, wid=44):
    """draw two sets as ovals with element circles; returns (posA, posB) dicts label -> (x, y)."""
    colA, colB = colA or {}, colB or {}
    posA, posB = {}, {}
    with f.group(step=step, only=only, until=until):
        for xs, S, t, c, col, pos in ((xa, A, tA, cA, colA, posA), (xb, B, tB, cB, colB, posB)):
            h = len(S) * gap + 14
            top = yc - h / 2
            f.rect(xs - wid, top, 2 * wid, h, "mut", "soft", 44)
            if t: f.text(xs, top - 12, t, "ink", 22, 700)
            for i, e in enumerate(S):
                y = top + 7 + gap * (i + 0.5)
                pos[e] = (xs, y)
                f.chip(xs - r, y - r, 2 * r, 2 * r, str(e), col.get(e, c), r=r, size=22 if r >= 19 else 20)
    return posA, posB


def arr(f, posA, posB, a, b, c="1", w=3.5, dash=False, step=None, only=None, until=None, r=20):
    (x1, y1), (x2, y2) = posA[a], posB[b]
    d = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    return f.arrow(x1 + ux * (r + 3), y1 + uy * (r + 3), x2 - ux * (r + 4), y2 - uy * (r + 4), c, w, dash, step=step, only=only, until=until)


def tick_axes(f, box, xr, yr, ticks=(1, 1), labels=True, grid=False, step=None, xlabel="x", ylabel="y"):
    return f.axes(box, xr, yr, grid=grid, ticks=ticks, labels=labels, xlabel=xlabel, ylabel=ylabel, step=step)

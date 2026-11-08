#!/usr/bin/env python3
"""Shibbur narration -> local Arabic TTS (Chatterbox Multilingual via the arabic-video-studio toolkit).

  scripts/tts/run.sh <course> [slug ...] [--voice teacher] [--out DIR] [--force]
                     [--pilot 0,1,2,3] [--dry]
  scripts/tts/run.sh compare --dirs DIR1 DIR2 ... --out index.html     (pilot comparison page)

Pipeline per lesson
  node scripts/narration.mjs export --provider generic   (official spoken text, math readings included)
  -> tokens of the ORIGINAL spoken text (UTF-16 offsets kept)
  -> Arabic TTS words (Hebrew -> voice transliteration, digits -> words, Latin -> letter names, symbols dropped),
     every produced word remembers its source token(s)
  -> sentences (2-28 words, textgate clean) with the punctuation kind that follows each
  -> studio.tts.synth_many  (gate -> ONE worker/model load -> ASR QA -> cache)
  -> per segment: join with gaps + fades, trim, loudnorm -16 LUFS, mp3 44.1k mono 96k  -> <out>/<code>/<slug>/NNN.mp3
  -> NNN.json  ElevenLabs-style character alignment against the original spoken text (accepted by `narration.mjs import`)
  -> NNN.meta.json sidecar (source hash, QA, sentences)  -> resumable.

Run with the toolkit's interpreter: use scripts/tts/run.sh (it sets PYTHONPATH and picks the venv python).
Only invented character voices / the user's own voice (see `avs voice list`). Never real-person voices.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CACHE_FILE = HERE / "lexicon-cache.json"
CLEAN_VERSION = "c4"          # bump when the cleaning/assembly logic changes -> hashes change -> segments regenerate

# --------------------------------------------------------------------------------------------------------------------
# Emotion / pace -> Chatterbox controls.  Exaggeration is quantised to 5 levels so the voice-conditionals cache works
# (one conditional per (voice, exaggeration, cfg)).  `style` text is ignored by this engine (counted and logged).
# raw spec -> level:  calm .40 -> .45 · warm .50 -> .55 · curious .55 · encouraging .55 · reassuring .45 · serious .35
#                      emphatic .65 · playful .65 · excited .75 · surprised .70 -> .75
# --------------------------------------------------------------------------------------------------------------------
LEVELS = [0.35, 0.45, 0.55, 0.65, 0.75]
CFG_OF_LEVEL = {0.35: 0.55, 0.45: 0.50, 0.55: 0.45, 0.65: 0.40, 0.75: 0.35}    # more expressive = lower cfg weight
EMOTION_EX = {
    "calm": 0.45, "warm": 0.55, "curious": 0.55, "encouraging": 0.55, "reassuring": 0.45,
    "serious": 0.35, "emphatic": 0.65, "playful": 0.65, "excited": 0.75, "surprised": 0.75,
}
PACE_SPEED = {"slow": 0.92, "normal": 1.0, "fast": 1.07}
GAP = {"comma": 0.18, "sentence": 0.32, "question": 0.35, "soft": 0.10}      # seconds of silence after a sentence
FADE = 0.008                                                                # seconds, cosine fade at every join
LUFS = -16.0

# --------------------------------------------------------------------------------------------------------------------
# Spoken names (same as docs/SPEAKMATH.md)
# --------------------------------------------------------------------------------------------------------------------
LATIN = {"a": "إيه", "b": "بي", "c": "سي", "d": "دي", "e": "إي", "f": "إف", "g": "جي", "h": "إتش", "i": "آي", "j": "جاي",
         "k": "كيه", "l": "إل", "m": "إم", "n": "إن", "o": "أو", "p": "بي", "q": "كيو", "r": "آر", "s": "إس", "t": "تي",
         "u": "يو", "v": "في", "w": "دبليو", "x": "إكس", "y": "واي", "z": "زِد"}      # p/v: no Persian letters (gate R5)
LATIN_WORDS = {"sin": "سينوس", "cos": "كوسينوس", "tan": "تانجنس", "cot": "كوتانجنس", "log": "لوغ", "ln": "لن", "exp": "إكسب",
               "max": "ماكس", "min": "مين", "sup": "سوبريموم", "inf": "إنفيموم", "lim": "ليميت", "next": "نكست",
               "pdf": "بي دي إف", "pi": "باي"}
GREEK = {"α": "ألفا", "β": "بيتا", "γ": "غاما", "δ": "دلتا", "ε": "إبسيلون", "ϵ": "إبسيلون", "θ": "ثيتا", "λ": "لامدا",
         "μ": "ميو", "π": "باي", "ρ": "رو", "σ": "سيغما", "τ": "تاو", "φ": "فاي", "ω": "أوميغا", "Δ": "دلتا كبيرة",
         "Σ": "سيغما كبيرة", "Ω": "أوميغا كبيرة", "ϕ": "فاي"}
SYMBOL_WORDS = {"=": "يساوي", "+": "زائد", "×": "ضرب", "·": "ضرب", "÷": "على", "%": "بالمئة", "°": "درجة", "²": "تربيع",
                "³": "تكعيب", "≤": "أصغر أو يساوي", "≥": "أكبر أو يساوي", "≠": "لا يساوي", "<": "أصغر من", ">": "أكبر من",
                "∞": "ما لا نهاية", "√": "جذر", "≈": "تقريباً يساوي", "→": "بتروح ل", "⇒": "يعني"}
PERSIAN = {"پ": "ب", "چ": "تش", "ژ": "ج", "گ": "ج", "ڤ": "ف", "ک": "ك", "ی": "ي", "ە": "ه", "ۆ": "و"}
# number words: nominative -> the oblique/colloquial spelling the voice says more naturally
OBLIQUE = {"عشرون": "عشرين", "ثلاثون": "ثلاثين", "أربعون": "أربعين", "خمسون": "خمسين", "ستون": "ستين", "سبعون": "سبعين",
           "ثمانون": "ثمانين", "تسعون": "تسعين", "ألفان": "ألفين", "اثنان": "اثنين", "مئتان": "ميتين", "مئتا": "ميتين",
           "مئة": "مية", "مئات": "ميات", "مليونان": "مليونين", "ثلاثمئة": "ثلاثمية", "أربعمئة": "أربعمية",
           "خمسمئة": "خمسمية", "ستمئة": "ستمية", "سبعمئة": "سبعمية", "ثمانمئة": "ثمانمية", "تسعمئة": "تسعمية"}
DIGITS_RE = re.compile(r"[0-9٠-٩۰-۹]")
HEBREW_RE = re.compile(r"[֑-ׇא-ת׳״]")


def char_class(ch: str) -> str:
    if DIGITS_RE.match(ch):
        return "digit"
    if ch.isascii() and ch.isalpha():
        return "latin"
    if HEBREW_RE.match(ch):
        return "hebrew"
    if ch in GREEK:
        return "greek"
    if "؀" <= ch <= "ۿ" or "ݐ" <= ch <= "ݿ" or ch == "ـ":
        return "arabic"
    return "other"


# --------------------------------------------------------------------------------------------------------------------
# toolkit imports (lazy: --help works anywhere)
# --------------------------------------------------------------------------------------------------------------------
A = TG = TR = VB = TTS = None


def toolkit():
    global A, TG, TR, VB, TTS
    from studio import arabic as A_, textgate as TG_, translit as TR_, voicebook as VB_, tts as TTS_  # noqa: N812
    A, TG, TR, VB, TTS = A_, TG_, TR_, VB_, TTS_


def utf16_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


# --------------------------------------------------------------------------------------------------------------------
# lexicon cache (Hebrew / English words -> Arabic-letter voice form).  Editable: a hand-fixed value stays.
# --------------------------------------------------------------------------------------------------------------------
class Lex:
    def __init__(self):
        try:
            self.d = json.loads(CACHE_FILE.read_text("utf-8"))
        except Exception:
            self.d = {}
        self.dirty = False

    def get(self, lang: str, word: str) -> str:
        key = f"{lang}|{word}"
        if key in self.d:
            return self.d[key]
        speak = ""
        try:
            r = TR.translit(word, lang)
            speak = (r.get("speak") or "").strip()
        except Exception as e:  # noqa: BLE001
            print(f"  ! translit {lang} {word}: {e}", file=sys.stderr)
        self.d[key] = speak
        self.dirty = True
        return speak

    def save(self):
        if self.dirty:
            CACHE_FILE.write_text(json.dumps(self.d, ensure_ascii=False, indent=1, sort_keys=True) + "\n", "utf-8")
            self.dirty = False


# --------------------------------------------------------------------------------------------------------------------
# 1. tokens of the original spoken text
# --------------------------------------------------------------------------------------------------------------------
class Tok:
    __slots__ = ("c", "n", "t", "kind")        # c/n: offsets in code points of the text

    def __init__(self, c, n, t, kind):
        self.c, self.n, self.t, self.kind = c, n, t, kind


def tokenize(text: str) -> list[Tok]:
    toks, i, n = [], 0, len(text)

    def isw(ch):
        return ch.isalnum() or unicodedata.category(ch).startswith("M") or ch == "ـ"

    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
        elif isw(ch):
            j = i + 1
            while j < n:
                c = text[j]
                if isw(c):
                    j += 1
                elif c in ".,٫" and j + 1 < n and text[j - 1].isdigit() and text[j + 1].isdigit():
                    j += 1                                           # decimal point / thousands comma inside a number
                elif c in "'’׳״" and j + 1 < n and text[j - 1].isalpha() and text[j + 1].isalpha():
                    j += 1
                else:
                    break
            toks.append(Tok(i, j - i, text[i:j], "w"))
            i = j
        else:
            toks.append(Tok(i, 1, ch, "p"))
            i += 1
    return toks


BREAK_OF = {".": "sentence", "!": "sentence", "؟": "question", "?": "question", "،": "comma", ",": "comma", "؛": "comma",
            ";": "comma", ":": "comma", "…": "sentence"}
BREAK_RANK = {None: 0, "soft": 1, "comma": 2, "sentence": 3, "question": 4}


def levant_number(raw: str) -> str:
    """digits -> Arabic words, colloquial-friendly spelling. 1.19 -> «واحد نقطة تسعة عشر», 3.14159 -> digits one by one."""
    raw = raw.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")).replace(",", "").replace("٫", ".")
    whole, _, frac = raw.partition(".")
    out = A.int_to_words(int(whole or "0"))
    if frac:
        if len(frac) <= 2 and not frac.startswith("0"):
            tail = A.int_to_words(int(frac))
        else:
            tail = " ".join(A.int_to_words(int(d)) for d in frac)
        out += " نقطة " + tail
    words = []
    for w in out.split():
        pre = "و" if w.startswith("و") and w[1:] in OBLIQUE else ""
        bare = w[1:] if pre else w
        words.append(pre + OBLIQUE.get(bare, bare))
    return " ".join(words)


def clean_arabic(run: str) -> str:
    run = "".join(PERSIAN.get(c, c) for c in run)
    return "".join(c for c in run if c in TG.LETTERS or c in TG.HARAKAT)


def script_runs(s: str):
    """[(class, text)]; a decimal point / comma between digits stays inside the digit run."""
    runs = []
    for i, ch in enumerate(s):
        k = char_class(ch)
        if k == "other" and ch in ".,٫" and 0 < i < len(s) - 1 and DIGITS_RE.match(s[i - 1]) and DIGITS_RE.match(s[i + 1]):
            k = "digit"
        elif k == "other" and ch in "'’\"":
            continue
        if runs and runs[-1][0] == k:
            runs[-1][1] += ch
        else:
            runs.append([k, ch])
    return runs


def transform_word(tok: Tok, lex: Lex, notes: list) -> list[dict]:
    """One word token -> list of {t: arabic word, glue: bool}."""
    out: list[dict] = []
    for k, r in script_runs(tok.t):
        if k == "digit":
            out += [{"t": w, "glue": False} for w in levant_number(r).split()]
        elif k == "hebrew":
            sp = lex.get("he", re.sub(r"[׳״]", "", r))
            ws = [w for w in (clean_arabic(w) for w in sp.split()) if w]
            if not ws:
                notes.append(f"no pronunciation for Hebrew «{r}»")
            out += [{"t": w, "glue": False} for w in ws]
        elif k == "latin":
            low = r.lower()
            if low in LATIN_WORDS:
                ws = LATIN_WORDS[low].split()
            elif len(r) <= 3 or r.isupper():
                ws = [LATIN[c] for c in low]
            else:
                ws = [w for w in (clean_arabic(w) for w in lex.get("en", low).split()) if w] or [LATIN[c] for c in low]
            out += [{"t": w, "glue": False} for w in ws]
        elif k == "greek":
            out += [{"t": w, "glue": False} for r_ in r for w in GREEK[r_].split()]
        elif k == "arabic":
            glue = r.endswith("ـ")
            w = clean_arabic(r)
            if w:
                out.append({"t": w, "glue": glue or w.strip("ًٌٍَُِّْ") in ("و", "ل", "ب", "ف", "ك")})   # detached prefix
            elif r.strip("ـ"):
                notes.append(f"dropped «{r}»")
        else:
            notes.append(f"dropped «{r}»")
    return out


def build_items(text: str, lex: Lex):
    """-> toks, items, notes.  item: {'k':'w','t':word,'src':[tok idx],'glue':bool} | {'k':'p','brk':kind}"""
    toks = tokenize(text)
    items, notes = [], []
    for ti, tok in enumerate(toks):
        if tok.kind == "p":
            ch = tok.t
            if ch in BREAK_OF:
                items.append({"k": "p", "brk": BREAK_OF[ch]})
            elif ch in SYMBOL_WORDS:
                for w in SYMBOL_WORDS[ch].split():
                    items.append({"k": "w", "t": w, "src": [ti], "glue": False})
            elif ch in "-−–":
                prev = text[tok.c - 1] if tok.c > 0 else " "
                nxt = text[tok.c + 1] if tok.c + 1 < len(text) else " "
                if nxt.isdigit() and not prev.isalnum():
                    items.append({"k": "w", "t": "سالب", "src": [ti], "glue": False})
                elif prev.isspace() and nxt.isspace():
                    items.append({"k": "w", "t": "ناقص", "src": [ti], "glue": False})
            elif ch in "()[]{}\"'«»“”‘’*_/\\|`~":
                pass
            else:
                notes.append(f"dropped symbol «{ch}»")
            continue
        for w in transform_word(tok, lex, notes):
            items.append({"k": "w", "t": w["t"], "src": [ti], "glue": w["glue"]})
    # glue: a detached «و» or a prefix with tatweel («لـ يو») joins the next word
    out = []
    i = 0
    while i < len(items):
        it = items[i]
        if it["k"] == "w" and it["glue"] and i + 1 < len(items) and items[i + 1]["k"] == "w":
            nxt = items[i + 1]
            items[i + 1] = {"k": "w", "t": it["t"] + nxt["t"], "src": it["src"] + nxt["src"], "glue": False}
        else:
            out.append({**it, "glue": False} if it["k"] == "w" else it)
        i += 1
    return toks, out, notes


# --------------------------------------------------------------------------------------------------------------------
# 2. sentences
# --------------------------------------------------------------------------------------------------------------------
MIN_TARGET, MAX_WORDS, MAX_CHARS = 3, 24, 165      # a bit tighter than the gate (2..28 words, 190 chars incl. harakat)


def nchars(words):
    return len(" ".join(w["t"] for w in words))


def make_pieces(items):
    pieces, cur = [], []
    for it in items:
        if it["k"] == "w":
            cur.append(it)
        else:
            brk = it["brk"]
            if cur:
                pieces.append({"words": cur, "brk": brk})
                cur = []
            elif pieces and BREAK_RANK[brk] > BREAK_RANK[pieces[-1]["brk"]]:
                pieces[-1]["brk"] = brk
    if cur:
        pieces.append({"words": cur, "brk": "sentence"})
    return pieces


_HARAKAT_RE = re.compile(r"[\u064B-\u0652\u0670\u0640]")


def norm_word(w: str) -> str:
    """spoken word without harakat/tatweel, alef variants folded -> for list lookups"""
    return _HARAKAT_RE.sub("", w).replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")


INTERJ = {"اهلين", "اهلا", "طيب", "هيك", "يلا", "لا", "لاا", "اه", "ايوه", "تمام", "ماشي", "منيح", "خلص", "شوف", "هلق", "يعني"}
INTERJ_N = {norm_word(x) for x in INTERJ} | {"لأ", "لا"}
DANGLING = {norm_word(x) for x in "زائد ناقص ضرب على بيساوي يساوي من ل القوس جذر أس فوقه وتحته اللي".split()}
NO_SPLIT_AFTER = {norm_word(x) for x in "أصغر أكبر أو مش سكر أس بإندكس الصف العمود نقطة".split()} | {"اصغر", "اكبر"}
LONG_WORDS, LONG_CHARS = 18, MAX_CHARS            # a piece longer than this is split at a natural joint (gap = comma)
LABEL_NOUNS = {"الصف", "العمود"}
EQ_WORDS = {"بيساوي", "يساوي"}
JOINT_WORDS = {"يعني", "اذا", "لكل", "بحيث"}
NOT_CONJ = {"واحد", "واحده", "وحده", "واحدة", "وحدة", "وحدات", "وسط", "وين", "وقت", "وجه"}   # start with «و» but are not «و + word»


def _pw(ws, k):
    return norm_word(ws[k]["t"])


def split_allowed(ws, k):
    """may a piece boundary go right before ws[k]?  (never inside a 2-word unit, never after a dangling word)"""
    p, c = _pw(ws, k - 1), _pw(ws, k)
    if p in DANGLING and not (p == "القوس" and k >= 2 and _pw(ws, k - 2) == "سكر"):
        return False
    if p in NO_SPLIT_AFTER or p.startswith("بإندكس") or p.startswith("باندكس"):
        return False
    if c == "نقطة" and k + 1 < len(ws) and _pw(ws, k + 1) not in ("تالتة", "ثالثة", "اولي", "اولى", "ثانية", "تانية"):
        return False                                   # decimal «صفر نقطة تسعة»
    if c.startswith("درجة") or c.startswith("درجه") or c == "الدرجة":
        return False                                   # number word + «درجة»
    if c in ("من", "او") and p in ("اصغر", "اكبر"):
        return False
    if c in EQ_WORDS and p in ("مش", "او"):
        return False                                   # «مش بيساوي», «أكبر أو بيساوي»
    if k >= 2 and _pw(ws, k - 2) in LABEL_NOUNS:
        return False                                   # «الصف الأول» | first item
    return True


def joint_tier(ws, k, eq_seen):
    c = _pw(ws, k)
    if c in EQ_WORDS and eq_seen:
        return 1
    if c in JOINT_WORDS or (c == "اللي" and k + 1 < len(ws) and _pw(ws, k + 1).startswith("بتحقق")) \
            or (c.startswith("و") and len(c) > 2 and c not in NOT_CONJ):
        return 2
    return 3


def split_long(p, _eq_before=0):
    """Split a piece longer than LONG_WORDS (or LONG_CHARS) at natural joints; every cut is a «comma» gap."""
    ws = p["words"]
    if len(ws) <= LONG_WORDS and nchars(ws) <= LONG_CHARS:
        return [p]
    n, mid = len(ws), len(ws) / 2
    eq_seen, eqs = _eq_before > 0, []
    for k in range(1, n):
        if _pw(ws, k - 1) in EQ_WORDS:
            eq_seen = True
        eqs.append(eq_seen)
    # eqs[k-1]: an equality word occurs before position k  (so the 1st one is never a cut, the 2nd+ are)
    ok = [k for k in range(2, n - 1) if split_allowed(ws, k)]
    pick = None
    for tiers, mh in (((1, 2), 3), ((1, 2), 2), ((3,), 3), ((3,), 2)):
        cands = [k for k in ok if k >= mh and n - k >= mh and joint_tier(ws, k, eqs[k - 1]) in tiers]
        for tier in tiers:
            c2 = [k for k in cands if joint_tier(ws, k, eqs[k - 1]) == tier]
            if c2:
                pick = min(c2, key=lambda x: abs(x - mid))
                break
        if pick:
            break
    if pick is None:
        pick = max(2, min(n - 2, int(mid))) if n >= 4 else max(1, n // 2)
    left = {"words": ws[:pick], "brk": "comma"}
    right = {"words": ws[pick:], "brk": p["brk"]}
    nxt_eq = _eq_before + sum(1 for w in ws[:pick] if norm_word(w["t"]) in EQ_WORDS)
    return split_long(left, _eq_before) + split_long(right, nxt_eq)


def _fix_short(pieces):
    """The textgate needs >= 2 words per call: only 1-word pieces are merged (forward into the next piece when it is an
    opener/interjection or was followed by a comma, else backward); the gap of the boundary that remains is kept."""
    i = 0
    while len(pieces) > 1 and i < len(pieces):
        p = pieces[i]
        if len(p["words"]) >= 2:
            i += 1
            continue
        w = norm_word(p["words"][0]["t"])
        fwd = w in INTERJ_N or p["brk"] in ("comma", "soft")
        if p["brk"] == "question":
            fwd = False
        if i == 0:
            fwd = True
        elif i == len(pieces) - 1:
            fwd = False
        if fwd:
            pieces[i + 1] = {"words": p["words"] + pieces[i + 1]["words"], "brk": pieces[i + 1]["brk"]}
            del pieces[i]
        else:
            pieces[i - 1] = {"words": pieces[i - 1]["words"] + p["words"], "brk": p["brk"]}
            del pieces[i]
            i -= 1
        if i < 0:
            i = 0
    return pieces


def _merge_comma_short(pieces, min_words=4):
    """Chatterbox hallucinates on 2-3 word inputs: a piece under `min_words` joins its neighbour when the boundary
    between them is a COMMA (forward preferred; backward if forward is impossible or would exceed LONG_WORDS).
    Sentence / question boundaries are never crossed."""
    changed = True
    while changed:
        changed = False
        for i, p in enumerate(pieces):
            n = len(p["words"])
            if n >= min_words:
                continue
            if p["brk"] in ("comma", "soft") and i + 1 < len(pieces) and n + len(pieces[i + 1]["words"]) <= LONG_WORDS:
                pieces[i + 1] = {"words": p["words"] + pieces[i + 1]["words"], "brk": pieces[i + 1]["brk"]}
                del pieces[i]
            elif i > 0 and pieces[i - 1]["brk"] in ("comma", "soft") and n + len(pieces[i - 1]["words"]) <= LONG_WORDS:
                pieces[i - 1] = {"words": pieces[i - 1]["words"] + p["words"], "brk": p["brk"]}
                del pieces[i]
            else:
                continue
            changed = True
            break
    return pieces


def _fix_dangling(pieces):
    """A clause/long-split cut never lands after a structural word (زائد، بيساوي، من، القوس …): move it one word later.
    (A real sentence end . ؟ ! is never moved: sentences are never merged.)"""
    i = 0
    while i < len(pieces) - 1:
        p, q = pieces[i], pieces[i + 1]
        ws = p["words"]
        last = norm_word(ws[-1]["t"])
        if p["brk"] not in ("sentence", "question") and last in DANGLING and not (last == "القوس" and len(ws) >= 2 and norm_word(ws[-2]["t"]) == "سكر"):
            if len(q["words"]) <= 2:
                pieces[i:i + 2] = [{"words": ws + q["words"], "brk": q["brk"]}]
            else:
                pieces[i] = {"words": ws + q["words"][:1], "brk": "comma"}
                pieces[i + 1] = {"words": q["words"][1:], "brk": q["brk"]}
            continue
        i += 1
    return pieces


def make_sentences(items):
    pieces = _merge_comma_short(_fix_short(make_pieces(items)))
    pieces = _fix_dangling(pieces)
    out = []
    for p in pieces:
        out += split_long(p)
    return [{"words": [w["t"] for w in p["words"]], "src": [w["src"] for w in p["words"]], "brk": p["brk"],
             "text": " ".join(w["t"] for w in p["words"])} for p in out]


def gate_fix(text: str):
    """textgate must be clean; else try suggest_fix; -> (clean text | None, reason)"""
    errs = TG.errors(TG.check(text))
    if not errs:
        return text, ""
    fixed = TG.suggest_fix(text)
    errs2 = TG.errors(TG.check(fixed)) if fixed else errs
    if fixed and not errs2:
        return fixed, "fixed"
    return None, "; ".join(e.short() for e in (errs2 or errs)[:2])


# --------------------------------------------------------------------------------------------------------------------
# 3. emotion / voice
# --------------------------------------------------------------------------------------------------------------------
def quantise(x: float) -> float:
    return min(sorted(LEVELS, reverse=True), key=lambda lv: abs(lv - x))        # ties -> the higher level


def seg_cfg(base: dict, vid: str, emotion: str, pace: str) -> dict:
    prof = VB.profile(vid)
    if not prof:
        raise SystemExit(f"unknown voice «{vid}» (avs voice list)")
    if VB.is_parody(vid) or VB.guard(vid, prof.get("name", "")):
        raise SystemExit(f"voice «{vid}» is a real-person voice - not allowed (invented characters / own voice only)")
    base_ex = float(base.get("exaggeration", 0.45))
    vex = prof.get("exaggeration")
    vex = base_ex if vex is None else float(vex)
    level = quantise(EMOTION_EX.get(emotion, 0.45) + (vex - base_ex))        # the voice's own energy shifts every emotion
    prof_speed = float(prof.get("speed") or 1.0)
    over = {"exaggeration": level, "cfg_weight": CFG_OF_LEVEL[level], "speed": round(prof_speed * PACE_SPEED.get(pace, 1.0), 3),
            "max_tries": 3}
    return VB.tts_cfg(base, vid, over)


# --------------------------------------------------------------------------------------------------------------------
# 4. export / plan
# --------------------------------------------------------------------------------------------------------------------
def export_segments(code: str, slugs: list[str]):
    tmp = Path(tempfile.mkdtemp(prefix="narr-export-"))
    cmd = ["node", "scripts/narration.mjs", "export", code] + (slugs if len(slugs) == 1 else [])
    cmd += ["--provider", "generic", "--out", str(tmp)]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"export failed: {r.stderr.strip() or r.stdout.strip()}")
    lessons = {}
    for f in sorted((tmp / code).glob("*.jsonl")):
        if slugs and f.stem not in slugs:
            continue
        lessons[f.stem] = [json.loads(l) for l in f.read_text("utf-8").splitlines() if l.strip()]
    shutil.rmtree(tmp, ignore_errors=True)
    return lessons


def plan_segment(req: dict, lex: Lex):
    toks, items, notes = build_items(req["text"], lex)
    sents = make_sentences(items)
    bad = []
    for s in sents:
        clean, why = gate_fix(s["text"])
        if clean is None:
            bad.append(why)
        elif clean != s["text"]:
            if len(clean.split()) != len(s["words"]):
                bad.append("fix changed word count")
            else:
                s["text"], s["words"] = clean, clean.split()
    if not sents:
        bad.append("no speakable words")
    return {"toks": toks, "sents": sents, "notes": notes, "errors": bad}


def seg_hash(req: dict, vid: str, cfg: dict) -> str:
    sig = json.dumps([CLEAN_VERSION, req["text"], vid, cfg.get("exaggeration"), cfg.get("cfg_weight"), cfg.get("speed"),
                      GAP, LUFS], ensure_ascii=False)
    return hashlib.sha1(sig.encode()).hexdigest()[:12]


# --------------------------------------------------------------------------------------------------------------------
# 5. assembly
# --------------------------------------------------------------------------------------------------------------------
def fade(a, sr, secs=FADE):
    import numpy as np
    n = min(int(sr * secs), len(a) // 2)
    if n > 1:
        ramp = (1 - np.cos(np.linspace(0, math.pi, n))) / 2
        a = a.copy()
        a[:n] *= ramp
        a[-n:] *= ramp[::-1]
    return a


def trim_silence(a, sr, thr_db=-46.0, keep_head=0.02, keep_tail=0.05):
    import numpy as np
    win = max(1, int(sr * 0.01))
    k = len(a) // win
    if k == 0:
        return a, 0.0
    env = np.abs(a[: k * win]).reshape(k, win).max(1)
    loud = np.where(env > 10 ** (thr_db / 20))[0]
    if not len(loud):
        return a, 0.0
    s = max(0, loud[0] * win - int(keep_head * sr))
    e = min(len(a), (loud[-1] + 1) * win + int(keep_tail * sr))
    return a[s:e], s / sr


def ffmpeg_loudnorm_mp3(wav: Path, mp3: Path):
    base = ["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", str(wav)]
    p1 = subprocess.run(base + ["-af", f"loudnorm=I={LUFS}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p1.stderr, re.S)
    af = f"loudnorm=I={LUFS}:TP=-1.5:LRA=11"
    if m:
        try:
            d = json.loads(m.group(0))
            if float(d["input_i"]) > -70:
                af += (f":measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
                       f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")
        except Exception:
            pass
    r = subprocess.run(base + ["-af", af, "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "96k", str(mp3)],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("ffmpeg: " + r.stderr[-300:])


def assemble(sents, results, mp3: Path):
    """-> (duration, [(start, dur)] per sentence in the final file)"""
    import numpy as np
    import soundfile as sf
    parts, starts, t, sr0 = [], [], 0.0, None
    for k, (s, r) in enumerate(zip(sents, results)):
        a, sr = sf.read(r["wav"], dtype="float32")
        if a.ndim > 1:
            a = a.mean(1)
        sr0 = sr0 or sr
        a = fade(a, sr)
        starts.append((t, len(a) / sr))
        parts.append(a)
        t += len(a) / sr
        if k < len(sents) - 1:
            g = np.zeros(int(GAP[s["brk"]] * sr), dtype="float32")
            parts.append(g)
            t += len(g) / sr
    full = np.concatenate(parts)
    full, lead = trim_silence(full, sr0)
    with tempfile.TemporaryDirectory() as d:
        w = Path(d) / "seg.wav"
        sf.write(w, full, sr0)
        ffmpeg_loudnorm_mp3(w, mp3)
    return len(full) / sr0, [(s - lead, d) for s, d in starts]


# --------------------------------------------------------------------------------------------------------------------
# 6. timings -> ElevenLabs alignment on the ORIGINAL text
# --------------------------------------------------------------------------------------------------------------------
def token_times(plan, preds, starts):
    """{token index: [s, e]} from the predictor's word times of every sentence."""
    tt: dict[int, list[float]] = {}
    for s, pr, (st, dur) in zip(plan["sents"], preds, starts):
        words, _ = pr.word_times(s["text"], dur)
        for w, srcs in zip(words, s["src"]):
            lens = [max(1, plan["toks"][i].n) for i in srcs]
            tot, acc = sum(lens), 0
            for i, ln in zip(srcs, lens):
                a = st + w["t0"] + (w["t1"] - w["t0"]) * acc / tot
                b = st + w["t0"] + (w["t1"] - w["t0"]) * (acc + ln) / tot
                acc += ln
                cur = tt.setdefault(i, [a, b])
                cur[0], cur[1] = min(cur[0], a), max(cur[1], b)
    return tt


def alignment(text: str, toks, tt, dur):
    """ElevenLabs-style character alignment, one entry per UTF-16 unit of `text`."""
    chars, u16 = [], []
    for ch in text:
        u16.append(len(chars))
        chars.append(ch)
        if ord(ch) > 0xFFFF:
            chars.append("")                                   # second UTF-16 unit
    n = len(chars)
    s_arr, e_arr = [None] * n, [None] * n
    for i, tok in enumerate(toks):
        if i not in tt:
            continue
        a, b = tt[i]
        for j in range(tok.n):
            u = u16[tok.c + j]
            s_arr[u] = a + (b - a) * j / tok.n
            e_arr[u] = a + (b - a) * (j + 1) / tok.n
    for u in range(n):                                          # untimed chars (spaces, punctuation, dropped symbols)
        if s_arr[u] is None and u > 0 and e_arr[u - 1] is not None:
            s_arr[u] = e_arr[u] = e_arr[u - 1]
    nxt = None
    for u in range(n - 1, -1, -1):                              # leading untimed chars take the next start
        if s_arr[u] is None:
            s_arr[u] = e_arr[u] = nxt if nxt is not None else 0.0
        else:
            nxt = s_arr[u]
    last = 0.0
    for u in range(n):                                          # monotonic, clamped to the audio
        s_arr[u] = round(min(max(s_arr[u], last), dur), 3)
        e_arr[u] = round(min(max(e_arr[u], s_arr[u]), dur), 3)
        last = s_arr[u]
    return {"characters": chars, "character_start_times_seconds": s_arr, "character_end_times_seconds": e_arr}


def words_of(text: str, al):
    """[(c, n, s, e, word)] for the page highlight, same logic as the importer (UTF-16 offsets)."""
    out = []
    for m in re.finditer(r"\S+", text):
        c = utf16_len(text[: m.start()])
        n = utf16_len(m.group(0))
        out.append((c, n, al["character_start_times_seconds"][c], al["character_end_times_seconds"][c + n - 1], m.group(0)))
    return out


# --------------------------------------------------------------------------------------------------------------------
# 7. main driver
# --------------------------------------------------------------------------------------------------------------------
def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def fmt_dur(s):
    s = int(s)
    return f"{s // 3600}h{(s % 3600) // 60:02d}m" if s >= 3600 else f"{s // 60}m{s % 60:02d}s"


def monitor(keys, stop, t0, total):
    from studio.paths import TTS_CACHE
    while not stop.wait(20):
        done = sum(1 for k in keys if (TTS_CACHE / f"{k}.json").exists())
        el = time.time() - t0
        eta = el / done * (total - done) if done else 0
        log(f"  tts {done}/{total} sentences · elapsed {fmt_dur(el)}" + (f" · ETA {fmt_dur(eta)}" if done else " · (model loading / first sentence)"))


def run_lesson(code, slug, reqs, args, lex, base_cfg, outdir: Path):
    from studio.project import tts_key
    lesson_dir = outdir / code / slug
    lesson_dir.mkdir(parents=True, exist_ok=True)
    idxs = args.pilot_idx if args.pilot_idx is not None else list(range(len(reqs)))
    idxs = [i for i in idxs if 0 <= i < len(reqs)]
    todo, report = [], {"ok": 0, "warn": 0, "bad": 0, "failed": 0, "skipped": 0, "audio": 0.0, "style": 0, "details": {}}
    for i in idxs:
        req = reqs[i]
        nnn = f"{i:03d}"
        cfg = seg_cfg(base_cfg, args.voice, req["emotion"], req["pace"])
        h = seg_hash(req, args.voice, cfg)
        meta_p = lesson_dir / f"{nnn}.meta.json"
        if req.get("style"):
            report["style"] += 1
        if not args.force and meta_p.exists() and (lesson_dir / f"{nnn}.mp3").exists() and (lesson_dir / f"{nnn}.json").exists():
            try:
                m = json.loads(meta_p.read_text("utf-8"))
                if m.get("hash") == h:
                    report["skipped"] += 1
                    report[m["qa"]] += 1
                    report["audio"] += m["dur"]
                    report["details"][i] = m
                    continue
            except Exception:
                pass
        plan = plan_segment(req, lex)
        if plan["errors"]:
            log(f"  {slug} segment {nnn} FAILED cleaning: {plan['errors'][0]}")
            report["failed"] += 1
            report["details"][i] = {"qa": "failed", "why": plan["errors"], "text": req["text"], "emotion": req["emotion"], "pace": req["pace"],
                                    "sentences": [s["text"] for s in plan["sents"]], "notes": plan["notes"]}
            continue
        for n_ in plan["notes"]:
            log(f"  segment {nnn} note: {n_}")
        todo.append({"i": i, "nnn": nnn, "req": req, "cfg": cfg, "hash": h, "plan": plan})
    lex.save()
    if args.dry:
        for t in todo:
            print(f"--- {t['nnn']} [{t['req']['emotion']}/{t['req']['pace']} ex={t['cfg']['exaggeration']} cfg={t['cfg']['cfg_weight']} sp={t['cfg']['speed']}]")
            print("  ORIG:", t["req"]["text"])
            for s in t["plan"]["sents"]:
                print(f"  - ({s['brk']}) {s['text']}")
        return report
    if not todo:
        return report
    # ---- synthesis: every sentence of the lesson in ONE call (model loads once)
    items, owner = [], []
    for t in todo:
        for k, s in enumerate(t["plan"]["sents"]):
            items.append((s["text"], t["cfg"]))
            owner.append(t)
    keys = [tts_key(tx, c) for tx, c in items]
    log(f"{code}/{slug}: {len(todo)} segments, {len(items)} sentences · free RAM {TTS.free_gb():.1f} GB · other tts: {TTS.other_tts_running() or 'none'}")
    stop = threading.Event()
    t0 = time.time()
    threading.Thread(target=monitor, args=(keys, stop, t0, len(items)), daemon=True).start()
    try:
        results = TTS.synth_many(items, wait_minutes=args.wait)
    finally:
        stop.set()
    report["gen_wall"] = time.time() - t0
    report["gen_compute"] = sum((r or {}).get("gen") or 0 for r in results)
    report["sent_audio"] = sum((r or {}).get("dur") or 0 for r in results if r and not r.get("cached"))
    report["sent_cached"] = sum(1 for r in results if r and r.get("cached"))
    for t in todo:
        t["res"] = []
    for t, r in zip(owner, results):
        t["res"].append(r)
    # ---- assemble per segment
    for t in todo:
        i, nnn, req, plan = t["i"], t["nnn"], t["req"], t["plan"]
        bad = [r for r in t["res"] if r is None or r.get("error")]
        if bad:
            err = (bad[0] or {}).get("error") or "no result"
            log(f"  segment {nnn} FAILED synthesis: {err}")
            report["failed"] += 1
            report["details"][i] = {"qa": "failed", "why": [str(err)], "text": req["text"], "emotion": req["emotion"], "pace": req["pace"],
                                    "sentences": [s["text"] for s in plan["sents"]]}
            continue
        preds = [VB.predictor(t["cfg"]) for _ in plan["sents"]]
        mp3 = lesson_dir / f"{nnn}.mp3"
        dur, starts = assemble(plan["sents"], t["res"], mp3)
        tt = token_times(plan, preds, starts)
        al = alignment(req["text"], plan["toks"], tt, dur)
        (lesson_dir / f"{nnn}.json").write_text(json.dumps(al, ensure_ascii=False) + "\n", "utf-8")
        rank = {"ok": 0, "warn": 1, "bad": 2}
        qa = max((r.get("qa") or "warn" for r in t["res"]), key=lambda q: rank.get(q, 1))
        why = sorted({w for r in t["res"] for w in (r.get("why") or [])})
        meta = {"hash": t["hash"], "qa": qa, "why": why, "dur": round(dur, 3), "text": req["text"], "emotion": req["emotion"],
                "pace": req["pace"], "voice": args.voice, "exaggeration": t["cfg"]["exaggeration"], "cfg_weight": t["cfg"]["cfg_weight"],
                "speed": t["cfg"]["speed"], "style_ignored": req.get("style") or "",
                "sentences": [{"text": s["text"], "brk": s["brk"], "qa": r.get("qa"), "why": r.get("why"), "dur": r.get("dur"),
                               "heard": ((r.get("asr") or {}).get("heard") or "")[:160]}
                              for s, r in zip(plan["sents"], t["res"])],
                "notes": plan["notes"], "words": [list(w) for w in words_of(req["text"], al)]}
        (lesson_dir / f"{nnn}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", "utf-8")
        report[qa] += 1
        report["audio"] += dur
        report["details"][i] = meta
        log(f"  {nnn} {qa:4s} {dur:5.1f}s  [{req['emotion']}/{req['pace']}]  {req['text'][:60]}")
    return report


def print_report(code, slug, rep):
    n = rep["ok"] + rep["warn"] + rep["bad"] + rep["failed"]
    print(f"\n== {code}/{slug}: {n} segments  ok {rep['ok']} · warn {rep['warn']} · bad {rep['bad']} · failed(cleaning/synth) {rep['failed']}"
          f"  (resumed {rep['skipped']})")
    line = f"   audio {rep['audio'] / 60:.2f} min"
    if rep.get("gen_wall"):
        line += (f" · generation {fmt_dur(rep['gen_wall'])} wall, {rep['gen_compute']:.0f}s model compute"
                 f" · {rep['sent_audio'] / max(1, rep['gen_wall']):.2f} s audio per s wall / {rep['sent_audio'] / max(1, rep['gen_compute']):.2f} per s compute"
                 f" ({rep['sent_cached']} sentences from cache)")
    print(line)
    if rep["style"]:
        print(f"   `style` text ignored by this engine in {rep['style']} segments")
    for i, d in sorted(rep["details"].items()):
        if d["qa"] != "ok":
            print(f"   {i:03d} {d['qa']}: {'; '.join(d.get('why') or [])[:140]}")


# --------------------------------------------------------------------------------------------------------------------
# 8. verification via the real importer, pilot page
# --------------------------------------------------------------------------------------------------------------------
def verify_import(code, slug, lesson_dir: Path, idxs):
    """Run `narration.mjs import` on a temp copy (only the generated segments) and check words[] against the text."""
    src_n = REPO / "courses" / code / "narration" / f"{slug}.json"
    tmp = Path(tempfile.mkdtemp(prefix="narr-verify-"))
    try:
        (tmp / "scripts").mkdir()
        for f in (REPO / "scripts").glob("*.mjs"):
            shutil.copy(f, tmp / "scripts" / f.name)
        if (REPO / "package.json").exists():
            shutil.copy(REPO / "package.json", tmp / "package.json")
        n = json.loads(src_n.read_text("utf-8"))
        n["segments"] = [n["segments"][i] for i in idxs]
        (tmp / "courses" / code / "narration").mkdir(parents=True)
        (tmp / "courses" / code / "narration" / f"{slug}.json").write_text(json.dumps(n, ensure_ascii=False))
        d = tmp / "in"
        d.mkdir()
        for k, i in enumerate(idxs):
            shutil.copy(lesson_dir / f"{i:03d}.mp3", d / f"{k:03d}.mp3")
            shutil.copy(lesson_dir / f"{i:03d}.json", d / f"{k:03d}.json")
        r = subprocess.run(["node", "scripts/narration.mjs", "import", code, slug, "--dir", str(d), "--provider", "chatterbox"],
                           cwd=tmp, capture_output=True, text=True)
        if r.returncode:
            return {"ok": False, "error": (r.stderr or r.stdout)[-400:]}
        out = json.loads((tmp / "courses" / code / "narration" / f"{slug}.json").read_text("utf-8"))
        problems = []
        for k, i in enumerate(idxs):
            text = json.loads((lesson_dir / f"{i:03d}.meta.json").read_text("utf-8"))["text"]
            ws = out["audio"]["segments"][k]["words"]
            dur = out["audio"]["segments"][k]["dur"]
            exp = [(utf16_len(text[: m.start()]), utf16_len(m.group(0))) for m in re.finditer(r"\S+", text)]
            if [(w["c"], w["n"]) for w in ws] != exp:
                problems.append(f"{i:03d}: word offsets differ ({len(ws)} vs {len(exp)} words)")
            if any(b["s"] + 1e-6 < a["s"] for a, b in zip(ws, ws[1:])):
                problems.append(f"{i:03d}: timings not monotonic")
            if any(w["e"] < w["s"] or w["e"] > dur + 1e-3 for w in ws):
                problems.append(f"{i:03d}: bad interval")
            zero = sum(1 for w, (c, n) in zip(ws, exp) if w["e"] - w["s"] < 0.01 and re.search(r"\w", text.encode("utf-16-le")[2 * c:2 * (c + n)].decode("utf-16-le")))
            if zero > max(2, len(ws) // 6):
                problems.append(f"{i:03d}: {zero} near-zero-length words")
        return {"ok": not problems, "problems": problems, "checked": len(idxs)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


CSS = """body{font:15px/1.5 -apple-system,Segoe UI,sans-serif;margin:24px;background:#fafafa;color:#222}h1{margin:0 0 4px}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px;vertical-align:top;background:#fff}th{background:#f0f0f0}
.t{direction:rtl;text-align:right;font-size:17px}.w.on{background:#ffe38a;border-radius:3px}.q-ok{color:#0a7d2c}.q-warn{color:#b07000}.q-bad,.q-failed{color:#c00}
.meta{font-size:12px;color:#666}audio{width:100%;min-width:220px}details{margin-top:4px;font-size:12px;color:#444;direction:rtl;text-align:right}"""
JS = """document.querySelectorAll('audio').forEach(a=>{const box=a.closest('td');const ws=box.querySelectorAll('.w');
a.addEventListener('timeupdate',()=>{const t=a.currentTime;ws.forEach(w=>w.classList.toggle('on',t>=+w.dataset.s&&t<+w.dataset.e));});
a.addEventListener('play',()=>document.querySelectorAll('audio').forEach(o=>{if(o!==a)o.pause()}));});"""


def sample_cell(d: dict, mp3_rel: str, show_text=True):
    e = html.escape
    if d["qa"] == "failed":
        return f"<td><span class='q-failed'>FAILED</span> {e('; '.join(d.get('why') or []))}</td>"
    spans = " ".join(f"<span class='w' data-s='{w[2]}' data-e='{w[3]}'>{e(w[4])}</span>" for w in d["words"])
    sent = "<br>".join(f"{e(s['text'])} <span class='meta'>({s['brk']}, {s['qa']})</span>" for s in d["sentences"])
    heard = "<br>".join(e(s.get("heard") or "") for s in d["sentences"] if s.get("qa") != "ok")
    return (f"<td><audio controls preload='none' src='{e(mp3_rel)}'></audio>"
            f"<div class='meta'><b class='q-{d['qa']}'>{d['qa'].upper()}</b> · {d['dur']:.1f}s · {d['emotion']}/{d['pace']} · ex {d['exaggeration']} cfg {d['cfg_weight']} · speed {d['speed']}"
            + (f" · {e('; '.join(d['why']))}" if d.get("why") else "") + "</div>"
            + (f"<div class='t'>{spans}</div>" if show_text else "")
            + f"<details><summary>TTS sentences</summary>{sent}" + (f"<br><i>heard:</i> {heard}" if heard else "") + "</details></td>")


def write_pilot_page(outdir: Path, code, slug, voice, report):
    rows = [f"<tr><th>{i:03d}</th>{sample_cell(d, f'{code}/{slug}/{i:03d}.mp3')}</tr>" for i, d in sorted(report["details"].items())]
    page = (f"<!doctype html><meta charset='utf-8'><title>pilot {voice}</title><style>{CSS}</style><h1>Pilot — {html.escape(voice)}</h1>"
            f"<div class='meta'>{code}/{slug}</div><table>{''.join(rows)}</table><script>{JS}</script>")
    (outdir / "pilot.html").write_text(page, "utf-8")
    (outdir / "pilot.json").write_text(json.dumps({"voice": voice, "code": code, "slug": slug,
                                                    "details": {str(k): v for k, v in report["details"].items()}}, ensure_ascii=False), "utf-8")


def compare(dirs: list[Path], out: Path):
    data = [(d, json.loads((d / "pilot.json").read_text("utf-8"))) for d in dirs]
    idxs = sorted({int(i) for _, p in data for i in p["details"]})
    head = "".join(f"<th>{html.escape(p['voice'])}</th>" for _, p in data)
    rows = []
    for i in idxs:
        first = next((p["details"][str(i)] for _, p in data if str(i) in p["details"]), None)
        cells = []
        for d, p in data:
            det = p["details"].get(str(i))
            if not det:
                cells.append("<td class='meta'>—</td>")
                continue
            rel = os.path.relpath(d / p["code"] / p["slug"] / f"{i:03d}.mp3", out.parent)
            cells.append(sample_cell(det, rel, show_text=False))
        rows.append(f"<tr><th>{i:03d}</th><td class='t'>{html.escape(first['text']) if first else ''}</td>{''.join(cells)}</tr>")
    page = (f"<!doctype html><meta charset='utf-8'><title>Shibbur TTS pilot</title><style>{CSS}</style>"
            f"<h1>Shibbur narration pilot — voices compared</h1><div class='meta'>{data[0][1]['code']}/{data[0][1]['slug']} · Chatterbox Multilingual (local)</div>"
            f"<table><tr><th>#</th><th>spoken text</th>{head}</tr>{''.join(rows)}</table><script>{JS}</script>")
    out.write_text(page, "utf-8")
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("course", nargs="?")
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--voice", default="teacher")
    ap.add_argument("--out", default=str(Path.home() / "Developer" / "shibbur-tts" / "audio"))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--pilot", help="comma list of segment indices: generate only these and write pilot.html")
    ap.add_argument("--dry", action="store_true", help="show the cleaning (original -> TTS sentences), synthesize nothing")
    ap.add_argument("--wait", type=float, default=60.0, help="minutes to wait for the model lock / free RAM")
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--dirs", nargs="*", help="compare: pilot output dirs")
    args = ap.parse_args()
    toolkit()
    if args.course == "compare":
        compare([Path(d) for d in args.dirs], Path(args.out))
        return
    if not args.course:
        ap.error("course code required")
    args.pilot_idx = [int(x) for x in args.pilot.split(",")] if args.pilot else None
    from studio.paths import load_config
    base = dict(load_config()["tts"])
    lessons = export_segments(args.course, args.slugs)
    if not lessons:
        raise SystemExit("no narration found")
    lex = Lex()
    outdir = Path(args.out).expanduser()
    for slug, reqs in lessons.items():
        t0 = time.time()
        rep = run_lesson(args.course, slug, reqs, args, lex, base, outdir)
        if args.dry:
            continue
        print_report(args.course, slug, rep)
        done = sorted(i for i, d in rep["details"].items() if d["qa"] != "failed")
        if done and not args.no_verify:
            v = verify_import(args.course, slug, outdir / args.course / slug, done)
            print("   import check:", "OK" if v["ok"] else "PROBLEMS", f"({v.get('checked', 0)} segments)", v.get("problems") or v.get("error") or "")
        if args.pilot_idx is not None:
            write_pilot_page(outdir, args.course, slug, args.voice, rep)
            print("   pilot page:", outdir / "pilot.html")
        print(f"   total wall {fmt_dur(time.time() - t0)}")
    lex.save()


if __name__ == "__main__":
    main()

"""Unit tests for the sentence splitting of narrate_tts (prosody rules).

Run (no toolkit / audio needed, make_sentences works on plain word/punctuation items):
    ~/.local/share/arabic-video-studio/venv/bin/python scripts/tts/test_cleaning.py      (or: pytest)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import narrate_tts as N

PUNCT = {".": "sentence", "!": "sentence", "؟": "question", "?": "question", "…": "sentence", "،": "comma", ",": "comma"}


def sents(text):
    """text of spoken words + punctuation -> make_sentences() output."""
    items, n = [], 0
    for tok in re.findall(r"[\wً-ْـ]+|[.!؟?…،,]", text):
        if tok in PUNCT:
            items.append({"k": "p", "brk": PUNCT[tok]})
        else:
            items.append({"k": "w", "t": tok, "src": [n], "glue": False})
            n += 1
    return N.make_sentences(items)


def texts(text):
    return [s["text"] for s in sents(text)]


def brks(text):
    return [s["brk"] for s in sents(text)]


def test_version_bumped():
    assert N.CLEAN_VERSION != "c3"


def test_no_merge_across_sentence_end():
    # dry 11102/001: «وبنخلّص بالقسمة. طويل شوي، بس…» used to become one piece
    t = "وبنخلّص بالقسمة. طويل شوي، بس مفيد كتير."
    assert texts(t)[0] == "وبنخلّص بالقسمة" and brks(t)[0] == "sentence"
    assert texts(t)[1].startswith("طويل شوي")
    # 2-word sentences stay alone (dry 11102/004)
    assert texts("منكبّر المجموعة. شوف الأربع معادلات.") == ["منكبّر المجموعة", "شوف الأربع معادلات"]


def test_ellipsis_is_a_sentence_end():
    assert brks("هاي الفكرة كلها… بس مش بسيطة أبداً.") == ["sentence", "sentence"]


def test_question_keeps_kind_even_when_short():
    # dry 11102/005: «فشو منعمل؟ منضيف …» lost the question
    t = "فشو منعمل؟ منضيف الأعداد السالبة."
    assert texts(t)[0] == "فشو منعمل" and brks(t) == ["question", "sentence"]


def test_one_word_forward_for_interjection():
    assert texts("أهلين. اليوم رح نتعرّف على الأعداد المركّبة.") == ["أهلين اليوم رح نتعرّف على الأعداد المركّبة"]
    assert texts("طيب. منبلّش من الأساس.") == ["طيب منبلّش من الأساس"]


def test_one_word_forward_when_comma():
    assert [x["text"] for x in sents("منبلّش بالأساس. وبعدين، هلّق نكمّل بالجمع.")] == \
        ["منبلّش بالأساس", "وبعدين هلّق نكمّل بالجمع"]


def test_one_word_backward_otherwise():
    s = sents("هاي الأعداد المركّبة كلها. جرّب. بعدين منكمّل الدرس.")
    assert [x["text"] for x in s] == ["هاي الأعداد المركّبة كلها جرّب", "بعدين منكمّل الدرس"]
    assert s[0]["brk"] == "sentence"                       # the boundary that remains keeps its kind


def test_one_word_question_stays_question():
    s = sents("منكتبها هيك بالأول. ليش؟ لأنها أبسط.")
    assert s[0]["text"] == "منكتبها هيك بالأول ليش" and s[0]["brk"] == "question"


def test_src_mapping_preserved():
    s = sents("أهلين. اليوم رح نتعلّم الجمع.")
    assert s[0]["src"] == [[0], [1], [2], [3], [4]] and len(s[0]["words"]) == len(s[0]["src"])


EQ = "زِد بيساوي إيه زائد آي بي بيساوي آر كوسينوس ثيتا زائد آي آر سينوس ثيتا بيساوي آر القوس كوسينوس ثيتا زائد آي سينوس ثيتا"


def test_long_split_before_second_equality():
    # dry 11102/019: 25 words, no split
    out = sents(EQ)
    assert len(out) >= 2 and all(len(s["words"]) <= 18 for s in out)
    assert out[0]["words"][:2] == ["زِد", "بيساوي"]           # the first «بيساوي» is never a cut
    assert out[1]["text"].startswith("بيساوي")
    assert [s["brk"] for s in out[:-1]] == ["comma"] * (len(out) - 1) and out[-1]["brk"] == "sentence"


def test_long_split_at_joints():
    # dry 11004/038
    t = ("التعريف إف بتكون خَاسُومَا إذا يوجد عدد إم بينتمي للأعداد الحقيقية بحيث لكل إكس بينتمي لإيه "
         "بيتحقق القيمة المطلقة لإف من إكس")
    out = texts(t)
    assert len(out) >= 2 and all(len(x.split()) <= 18 for x in out)
    assert any(x.split()[0] in ("إذا", "لكل", "بحيث", "يعني") for x in out[1:]), out


def test_split_before_yaani():
    # dry 11004/009
    t = "بتكون خَاد خَاد عِرْكِيت إذا إكس واحد مش بيساوي إكس اثنين يعني إف من إكس واحد مش بيساوي إف من إكس اثنين."
    out = texts(t)
    assert len(out) == 2 and out[1].startswith("يعني") or any(x.startswith("إذا") for x in out[1:])
    assert all(len(x.split()) <= 18 for x in out)


def test_split_before_alli_bethaqeq_and_waw():
    # dry 11004/075
    t = ("هو المجال المفتوح من إيه لبي بيساوي مجموعة كل إكس من الأعداد الحقيقية اللي بتحقق إيه أصغر من إكس "
         "وبعدين نكمّل الشرح تبعنا لهون")
    out = texts(t)
    assert all(len(x.split()) <= 18 for x in out)
    assert any(x.startswith("اللي بتحقق") or x.startswith("وبعدين") for x in out[1:]), out


def test_two_word_units_not_split():
    t = ("لما إيه واحد أصغر أو بيساوي إيه اثنين بيصير إف من إيه واحد أصغر أو بيساوي إف من إيه اثنين هاي عُولَا "
         "ولصفر أصغر من إيه مش بيساوي واحد ولإكس أكبر من صفر")
    out = texts(t)
    assert len(out) >= 2
    pairs = [("أصغر", "من"), ("أكبر", "من"), ("أكبر", "أو"), ("أو", "بيساوي"), ("مش", "بيساوي"), ("أصغر", "أو")]
    for a, b in zip(out, out[1:]):
        for p, q in pairs:
            assert not (a.split()[-1] == p and b.split()[0] == q), (a, b)


def test_split_allowed_units():
    def W(s):
        return [{"t": w} for w in s.split()]
    assert not N.split_allowed(W("ا ب ج د أصغر من ه و ز"), 5)          # أصغر | من
    assert not N.split_allowed(W("ا ب ج مش بيساوي ه"), 4)              # مش | بيساوي
    assert not N.split_allowed(W("ا ب ج أكبر أو بيساوي ه"), 4)         # أكبر | أو
    assert not N.split_allowed(W("ا ب ج أكبر أو بيساوي ه"), 5)         # أو | بيساوي
    w = W("ا ب ج سكّر القوس ه")
    assert not N.split_allowed(w, 4) and N.split_allowed(w, 5)        # «سكّر القوس» stays, may end after it
    assert not N.split_allowed(W("ا ب ج بإندكس إكس ه"), 4)             # بإندكس X
    assert not N.split_allowed(W("ا ب ج أُس إكس ه"), 4)                # أُس X
    assert not N.split_allowed(W("ا ب ج ثلاثين درجة ه"), 4)            # number + درجة
    w = W("ا الصف الأول إيه واحد ه")
    assert not N.split_allowed(w, 2) and not N.split_allowed(w, 3)    # label | first item


def test_never_end_on_dangling_word():
    dangling = {N.norm_word(x) for x in "زائد ناقص ضرب على بيساوي من لـ القوس جذر أُس فوقه وتحته اللي".split()}
    t = ("منعرّف إف أربعة من إكس بيساوي لوغ بالأساس إيه إكس زائد واحد ناقص اثنين ضرب ثلاثة على أربعة زائد خمسة "
         "ناقص ستة ضرب سبعة على ثمانية زائد تسعة ناقص عشرة")
    out = sents(t)
    assert len(out) >= 2
    for s in out[:-1]:
        assert N.norm_word(s["words"][-1]) not in dangling, s["text"]
    # a clause comma right after «زائد» moves one word later
    out = sents("واحد زائد اثنين زائد، ثلاثة ناقص أربعة بيساوي خمسة.")
    assert N.norm_word(out[0]["words"][-1]) != "زائد"


def test_sentence_end_after_unit_is_kept():
    # a real sentence end is never moved, even after «بيساوي» (dry 11004/046)
    out = texts("والنازلة نفس الشي بس مع أكبر أو بيساوي. وإذا كانت واحدة منهم منحكي مونوتونية.")
    assert out[0].endswith("أكبر أو بيساوي") and out[1].startswith("وإذا")


def test_waw_of_number_word_is_not_a_joint_and_decimal_not_cut():
    # dry 11004/094: «… صفر نقطة | واحد نجمة …» was cut inside a decimal / at the number «واحد»
    t = "يو صفر نقطة واحد نجمة من واحد بيساوي المجال المفتوح من صفر نقطة تسعة لواحد اتحاد المجال المفتوح من واحد لواحد نقطة واحد"
    out = sents(t)
    assert all(len(s["words"]) <= 18 for s in out)
    for a, b in zip(out, out[1:]):
        assert a["words"][-1] != "نقطة" and b["words"][0] != "واحد", (a["text"], b["text"])


def test_short_comma_pieces_merge_forward():
    # dry 11102/001: «وبعدين العدد آي، بعدين الجمع والضرب، وبنخلّص بالقسمة. …»
    out = sents("منبدأ من الأساس، شوف هاي، بعدين الجمع والضرب كلها بسرعة.")
    assert [s["text"] for s in out] == ["منبدأ من الأساس", "شوف هاي بعدين الجمع والضرب كلها بسرعة"] or len(out) == 2
    assert all(len(s["words"]) >= 4 for s in out)


def test_short_comma_piece_backward_when_last():
    out = sents("هلّق منحسب الناتج النهائي بالتفصيل، بس هيك.")
    assert len(out) == 1 and out[0]["text"].endswith("بس هيك") and out[0]["brk"] == "sentence"


def test_short_pieces_not_merged_across_sentence_or_question():
    assert texts("الدرس أول. منكبّر المجموعة. شوف الأربع معادلات.") == ["الدرس أول", "منكبّر المجموعة", "شوف الأربع معادلات"]
    assert brks("فشو منعمل؟ منضيف الأعداد السالبة هلّق.") == ["question", "sentence"]


def test_comma_merge_never_exceeds_limit():
    long17 = " ".join(["كلمة"] * 17)
    out = sents(f"{long17}، بس هيك، ومنكمّل هلّق بالدرس.")
    assert all(len(s["words"]) <= 18 for s in out)


def test_two_word_segments_ok():
    for t in ("نيجي للتعريف.", "فشو منعمل؟", "هلّق العكس."):
        s = sents(t)
        assert len(s) == 1 and len(s[0]["words"]) == 2


def test_char_limit_still_splits():
    t = " ".join(["كلمةطويلةجدا"] * 14) + "."
    assert all(len(s["words"]) <= 18 and len(s["text"]) <= N.LONG_CHARS for s in sents(t))


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", name)
            except Exception as e:      # noqa: BLE001
                fails += 1
                print("FAIL", name, repr(e)[:300])
    sys.exit(1 if fails else 0)

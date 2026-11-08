# speakmath — TeX → spoken Arabic (exact)

Every formula in a narration is read by code, not by hand, so the reading is exact and the same
everywhere. Input: the KaTeX subset used in the lessons. Output: one Arabic string a TTS voice reads
naturally (Levantine tutor, standard spelling so TTS pronounces it), with commas where a speaker
must pause to keep the structure unambiguous.

Principles
1. **Exact first, natural second.** Two different formulas must never produce the same reading.
   Where natural speech is ambiguous (a_{n+1} vs a_n+1, compound fractions, powers of sums) add the
   minimal structure words (بإندكس، القوس، كلّه على، الأُس) and a comma.
2. **Same symbol, same words** across the whole course.
3. **Fail loudly.** Unknown command/environment → error with the formula; never guess or drop.
4. Context matters only through explicit, documented rules (vector operands, interval vs pair,
   function application vs product, upper/lower case clash).

## Atoms
Latin letters (italic variables), as students say them:
a إيه · b بي · c سي · d دي · e إي · f إف · g جي · h إتش · i آي · j جاي · k كيه · l إل · m إم ·
n إن · o أو · p پي · q كيو · r آر · s إس · t تي · u يو · v ڤي · w دبليو · x إكس · y واي · z زِد.
Uppercase: same name; if the same letter appears in both cases in one formula, uppercase gets
"كبيرة" (A → "إيه كبيرة").
Greek: α ألفا · β بيتا · γ غاما · δ دلتا · ε/ϵ إبسيلون · θ ثيتا · λ لامدا · μ ميو · π باي ·
ρ رو · σ سيغما · τ تاو · φ فاي · ω أوميغا · Δ دلتا كبيرة · Σ سيغما كبيرة.
Numbers in words, standard spelling: 0 صفر … 10 عشرة, 11 أحد عشر, 12 اثنا عشر, 13–19 ثلاثة عشر…,
20 عشرين, 21 واحد وعشرين, 100 مية, 1000 ألف, up to 10⁹; decimals "نقطة" + the digits one by one, always
("صفر نقطة خمسة", "ثلاثة نقطة واحد أربعة", "صفر نقطة سبعة خمسة"); unary minus "سالب"; binary minus "ناقص".
Special constants: e (Euler, when used as e^…) إي · π باي · i (imaginary unit in complex context or
written as a number coefficient like 2i, 3-4i) آي · \infty ما لا نهاية.

## Operators and relations
| TeX | reading |
|---|---|
| `+` · `-` · `\pm` | زائد · ناقص (unary: سالب) · زائد ناقص |
| `\cdot` | ضرب; between two vector operands: نقطة (dot product) |
| `\times` | ضرب; between two vector operands: ضرب متجهي |
| juxtaposition `2x`, `ab`, `2\pi` | read side by side ("اثنين إكس") |
| `=` `\ne`/`\neq` | بيساوي · مش بيساوي |
| `<` `>` `\le` `\ge` `\lt` `\gt` | أصغر من · أكبر من · أصغر أو بيساوي · أكبر أو بيساوي |
| `\approx` | تقريباً بيساوي |
| `\in` `\notin` | بينتمي لـ · ما بينتمي لـ |
| `\subseteq` `\subset` | مجموعة جزئية من |
| `\cup` `\cap` `\setminus` | اتحاد · تقاطع · ناقص |
| `\emptyset` | المجموعة الفاضية |
| `\Rightarrow` `\implies` · `\iff` `\Leftrightarrow` | يعني · إذا وفقط إذا |
| `\forall` · `\exists` · `\mid` (in sets) · `:` (in sets) | لكل · في · اللي بتحقق · اللي بتحقق |
| `\perp` · `\parallel` | متعامد مع · موازي لـ |
| `\circ` composition `g\circ f` | جي تركيب إف ; degree `30^\circ` → ثلاثين درجة |
| `\to` | بتروح لـ |
| `\dots` `\ldots` `\cdots` | وهيك (in a list: "، وهيك") |

## Structures
| TeX | reading |
|---|---|
| `\frac{a}{b}` atoms | إيه على بي |
| numeric unit fractions | ½ نص · ⅓ ثلث · ¼ ربع · 1/5…1/10 خمس سدس سبع ثمن تسع عشر · 2/3 ثلثين · 3/4 ثلاث أرباع (only when both are plain integers ≤ 10) |
| compound numerator | "N، كلّه على D" |
| compound denominator | "N على المقدار D،" |
| both compound | "الكسر اللي فوقه N، وتحته D" |
| `x^2` · `x^3` | إكس تربيع · إكس تكعيب |
| `x^n`, `x^{-1}`, `x^{10}` | إكس أُس إن · إكس أُس سالب واحد · إكس أُس عشرة |
| compound exponent `x^{n+1}` | "إكس أُس، إن زائد واحد،" (comma after the exponent if more follows) |
| compound base `(a+b)^2` | "القوس إيه زائد بي، تربيع" |
| `f^{-1}` (function letter) | إف العكسية |
| `\sin^2 x` | سينوس تربيع إكس |
| `a_n` · `x_1` | إيه إن · إكس واحد |
| compound subscript `a_{n+1}` | "إيه بإندكس إن زائد واحد،"|
| `\sqrt{x}` · compound | جذر إكس · "جذر، X،" |
| `\sqrt[3]{x}` · `\sqrt[n]{x}` | الجذر التكعيبي لإكس · الجذر رقم إن لإكس |
| `\vec v` `\overrightarrow{v}` | ڤي (the letter; the arrow is implied by the context) — `\vec 0` المتجه الصفري |
| `\overrightarrow{AB}` (two points) | المتجه إيه بي |
| `\overline z` · `\hat i` · `\tilde x` | زِد بار · آي هات · إكس تيلدا |
| `|x|` · `|z|` | القيمة المطلقة لـ X |
| `|\vec v|` · `\|v\|` | طول ڤي |
| `f(x)`, `g(f(x))` (letter before parens that is a function in the formula: f g h, or \sin etc.) | إف من إكس · جي من إف من إكس |
| grouping parens around a compound | "القوس … ،" |
| pair/tuple `(1,2)`, `(a_1,…,a_n)` | "الزوج واحد واثنين" (2 items) · "النقطة/المتجه بإحداثيات …" (3+) — "المتجه" if the formula says it's a vector (\vec on the other side of =), else "الإحداثيات" |
| intervals: mixed brackets `[a,b)`, `(a,b]`; `[a,b]`; `(a,b)` after `\in`/`\subseteq`/`=`-a-set or with ∞ | المجال المغلق من إيه لبي · المفتوح · "المجال من إيه، مفتوح، لبي، مغلق" for half-open |
| `\{1,2,3\}` | المجموعة اللي فيها واحد، اثنين، ثلاثة |
| `\{x\in A : P\}` / `\mid` | مجموعة كل إكس من A اللي بتحقق P |
| `\mathbb R` `\mathbb Q` `\mathbb Z` `\mathbb N` `\mathbb C` | الأعداد الحقيقية · النسبية · الصحيحة · الطبيعية · المركّبة ; with exponent `\mathbb R^3` → آر ثلاثة |
| `\sin \cos \tan \cot` | سينوس · كوسينوس · تانجنس · كوتانجنس |
| `\arcsin \arccos \arctan \operatorname{arccot}` | أركسينوس · أركوسينوس · أركتانجنس · أركوتانجنس |
| `\ln` · `\log` · `\log_b` | لن · لوغ · لوغ بالأساس بي |
| `\mathrm{cis}` · `\mathrm{Re}` · `\mathrm{Im}` `\operatorname{Im}` · `\arg` | سيس · الجزء الحقيقي من · الجزء التخيلي من · الأرغومنت تبع |
| `\sup A` `\inf A` `\max` `\min` | السوبريموم تبع A · الإنفيموم تبع · الماكسيموم تبع · المينيموم تبع |
| `\lim_{x\to a} f` | النهاية لما إكس بتروح لإيه، لـ … |
| `\sum_{k=1}^{n} a_k` | المجموع من كيه بيساوي واحد لإن، لـ … |
| `\int_a^b f(x)\,dx` | التكامل من إيه لبي، لإف من إكس، دي إكس |
| `pmatrix` one column | المتجه بإحداثيات … (column) ; general: "المصفوفة: الصف الأول …، الصف الثاني …" |
| `vmatrix` | المحدِّد تبع المصفوفة: الصف الأول … |
| `cases` | "حسب الحالة: … لما …، و… لما …" (`\text{if}`/`,` separators) |
| `\text{…}` | the text as is (Arabic) |
| spacing `\ \, \; \quad \qquad \!` , `\left \right \big \Big \middle` | ignored for words; `\quad`/`\qquad` between two statements → "، و" |
| `\blacksquare` `\square` (end of proof) | "وهيك خلصنا البرهان" |
| `\mathrm{X}` other | the letters/words inside |
| `\langle u,v\rangle` | الضرب الداخلي تبع يو وڤي |
| `\tfrac` `\dfrac` | as `\frac` |

## API and tools
- `scripts/speakmath.mjs`: `speak(tex, {pairs, vector}) → string` (`pairs: 'interval'` reads every `(a,b)` as an interval except ordered
  pairs in a set, points `(x,f(x))` and bare-arrow pairs; `vector: true` forces the vector reading of 3+ tuples); throws `SpeakMathError` on anything
  unknown. CLI: `node scripts/speakmath.mjs '\frac{a+b}{2}'`.
- `node scripts/speakmath.mjs --corpus` — reads every formula in every lesson, writes
  `dist-review/speakmath.html` (formula rendered with KaTeX next to its reading, grouped by
  construct, searchable) and fails on any error.
- Tests: `scripts/speakmath.test.mjs` (gold pairs; `node --test`).
- Narration: a `math` part with no `say` gets `say = speak(tex)` at build time (and in export);
  a `say` written by hand stays only when the part has `"keep": true`.

## Additions (decided while covering every formula of the corpus)
Numbers: 200 ميتين · 300 ثلاثمية … 900 تسعمية · 2000 ألفين · 3000–10000 "ثلاثة آلاف" · 11000+ "أحد عشر ألف" ·
10⁶ مليون · 10⁹ مليار; compound numbers join with "و" (مية وخمسة وعشرين); a number above 10⁹ is an error.
An integer with a leading zero ("007") is read digit by digit.

| TeX | reading |
|---|---|
| `\{x\}`, `\{2.7\}`, `\{-0.5\}` (one item that is not a non-negative integer) | الجزء الكسري لـ … |
| `[x]`, `[-1.3]` (square brackets with one item) | الجزء الصحيح لـ … |
| `\{3\}`, `\{0\}` (one non-negative integer) | المجموعة اللي فيها ثلاثة |
| `\{a_n\}_{n=1}^{\infty}` (braces with limits) | "المتتالية إيه إن، من إن بيساوي واحد لما لا نهاية" |
| `\mathbb R^+` · `\mathbb R^{++}` | الأعداد الحقيقية الموجبة · الأعداد الحقيقية الموجبة تماماً |
| `\mathbb I` | الأعداد غير النسبية |
| `\operatorname{Im}(f)` (image of a function; `\mathrm{Im}(z)` stays the imaginary part) | الصورة تبع إف |
| `Id` · `Id_A` | آي دي · آي دي إيه (a function: `Id(x)` → آي دي من إكس) |
| `A_g^*` · `^*` | إيه جي نجمة · نجمة |
| `U_\epsilon(x_0)` | يو إبسيلون من إكس صفر (function letters before parentheses: f g h F G H U) |
| `a/b`, `\sqrt2/2` | إيه على بي · جذر اثنين على اثنين |
| `k=0..n-1` (`..`) | كيه بيساوي صفر لحد إن ناقص واحد |
| `3^?` | ثلاثة أُس قديش |
| `:=` | بيساوي بالتعريف |
| `:` before a domain with a later `\to` (`f:A\to B`) | من — "إف من إيه بتروح لبي" |
| `:` as a plain separator (`\vec v=(a,b):\ \vec v\cdot\vec v=1`) | ؛ (Arabic semicolon, a stronger pause) |
| `\text{if}` · `\text{otherwise}` in cases | لما · غير هيك (other Latin text is an error) |
| `cases` whose rows have no `&` (a system) | "المعادلتين مع بعض: A، وB" (3+: "المعادلات مع بعض: …") |
| `\langle a,b,c\rangle` (3 items) | الضرب الثلاثي تبع إيه وبي وسي |
| `\forall x` · `\exists x` | لكل إكس · في إكس |
| `\hat{v}` compound / `\overline{a+b}` | "القوس إيه زائد بي، بار" (same pattern for hat/tilde) |
| `\overrightarrow{P_0P}` (several items) | المتجه بي صفر بي |
| `\mathrm{xyz}` (unknown letters) | the letters one by one |

Rules that were left open:
- **Compound** (needs the comma/"القوس" form): in a fraction numerator = contains `+ - ±`, a relation, a list or a fraction;
  in a denominator = anything but one atom (a product, sum or fraction); in an exponent, subscript, root, `|…|`, `\overline`,
  interval end, function argument = anything but one atom (`n+1`, `2x`, `x^2`, `f(x)`). A leading unary minus on one atom
  is still one atom (`x^{-1}` → "أُس سالب واحد"). A power or root of one atom: `x^n`, `\sqrt{x}`.
- A prefix construct that is not closed by a word (`\sqrt`, a non-numeric fraction) followed by a juxtaposed factor gets a comma:
  `\sqrt3\,i` → "جذر ثلاثة، آي". An absolute value/length next to any other factor gets "ضرب" instead (`|\vec v||\vec u|`).
- A power of something that is not an atom (`|z|^2`, `f(x)^2`, `\sqrt2^3`) puts a comma before the power word:
  "القيمة المطلقة لزِد، تربيع"; `|z^2|` has none ("القيمة المطلقة لزِد تربيع").
- A function name followed directly by a non-numeric fraction wraps it: `\cos\frac\pi4` → "كوسينوس القوس باي على أربعة".
  `\cos(\theta)` drops the parentheses, `\cos(\theta_1+\theta_2)` keeps "القوس …،". Letter functions always use "من":
  `f(x+1)` → "إف من القوس إكس زائد واحد"; several arguments `f(a,b)` → "إف من إيه، بي".
- `(a,b)` is an interval (not a pair) when an end is ∞, after `\in \subseteq \cup \cap \setminus \sup \inf \max \min`, in a `:` … `\to` domain
  position, or in an `=` chain with a set (a set literal, `\mathbb`, an interval, `U(…)`, or a lone capital letter other than
  P Q R O M N). `[a,b]`, `[a,b)`, `(a,b]` are always intervals; compound ends get a comma.
- A tuple of 3+ items: "المتجه بإحداثيات …" when the formula has a vector (`\vec`, `\overrightarrow`, `\hat`, a column matrix) or the tuple
  is multiplied/added to something; "النقطة بإحداثيات …" when a capital letter names it (`P=(1,2,3)`); otherwise "الإحداثيات …".
- Quad: `\quad` next to `\Rightarrow`/`\iff`/`\text`: "،"; after a comma: "و"; otherwise "، و". A run of quads counts once.
- A `|` inside `\{…\}` after an operand is the "such that" bar (like `\mid`).
- **Nested groups.** A parenthesised group (or a compound function argument) that sits inside another group is closed out loud:
  "القوس … ، سكّر القوس،". Depth-1 groups keep the plain "القوس …،" (so `(a+b)-(c+d)` → "القوس إيه زائد بي، ناقص القوس سي زائد دي").
  Example: `((a+b)-(c+d))e` → "القوس القوس إيه زائد بي، سكّر القوس، ناقص القوس سي زائد دي، سكّر القوس، إي".
- Interior soft commas: a "،" that closes a construct is kept when more follows and dropped at the end of the reading.

## Per-lesson hints and the build
`speak(tex)` has no idea which lesson it is in, so `(1,5)` is a pair unless told otherwise. A course can say, in `course.json`:
`"speakmath": {"lessons": {"bounds": {"pairs": "interval"}}}`. The build, `narration.mjs` (export/import/stats), the migration and
`speakmath.mjs --corpus` all pass that hint. A pair with π in it (`(0,\pi)`) is an interval everywhere.
`node scripts/narration-mathsay.mjs [--dry]` is the one-off migration from hand-written math `say` to generated readings.

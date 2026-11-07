# شيبور — كورسات براوده

محتوى كورسات تطبيق **Shibbur** (آيفون). كل شي JSON عادي، وبينبني لـ API ثابت وبيننشر على GitHub Pages:
https://alidiab2.github.io/shibbur-courses/

## البنية
```
site.json                          الاسم، الشعار، المواضيع وترتيب الكورسات
courses/<code>/course.json         بيانات الكورس + الفصول (كل فصل فيه قائمة slugs)
courses/<code>/lessons/<slug>.json الدرس: بيانات + blocks
scripts/build.mjs                  بيتحقق وبيبني dist/
```

## تشغيل محلي
```
node scripts/build.mjs --check                 # تحقق بس
node scripts/build.mjs                         # بيبني dist/
python3 -m http.server 8790 -d dist            # معاينة
```
بعدين بالتطبيق: قائمة المطوّر ← السيرفر ← `http://<mac-ip>:8790/`

## كيف أضيف…
**كورس:** سوّي مجلد `courses/<code>/` فيه `course.json` و`lessons/`، وضيف `{ "code", "tag", "paid": false }` تحت الموضوع المناسب بـ `site.json` (الترتيب = ترتيب العرض).

**فصل:** ضيف عنصر بـ `chapters` بـ `course.json`: `{ "n", "slug", "title", "lead", "isExam", "lessons": ["slug1", ...] }`.

**درس:** ملف `courses/<code>/lessons/<slug>.json` (اسم الملف = `slug`):
```json
{ "slug": "x", "title": "...", "he": "عبري؟", "ref": "مرجع؟", "minutes": 15, "desc": "...", "blocks": [ ... ] }
```
وبعدها ضيف الـ slug لقائمة `lessons` بالفصل. درس بلا فصل أو فصل بلا ملف = خطأ بالبناء.

**سؤال:** block من نوع `quiz` جوّا الدرس. لا تكتب `id` ولا `lesson` ولا `chapter`، البناء بيعبّيهم (`<code>/<slug>/<i>`):
```json
{ "t": "quiz", "q": { "kind": "mc", "prompt": "<p>...</p>",
  "options": [{"v":"1","html":"..."},{"v":"2","html":"..."}],
  "answer": ["2"], "hint": "اختياري", "solution": "<p>...</p>" } }
{ "t": "quiz", "q": { "kind": "text", "prompt": "...", "answer": ["0.5","1/2"], "solution": "..." } }
```
بـ `mc`: القيم `v` لازم تكون "1".."n" بالترتيب و`answer` وحدة منهم. بـ `text`: `answer` بدائل مقبولة.

## أنواع الـ blocks (ملخص)
| t | حقول |
|---|---|
| `why` `p` `html` | `html` |
| `h` | `text` |
| `box` | `kind` (key/ex/note…), `title`, `html` |
| `figure` | `svg`, `alt`, `caption?` |
| `math` | `tex` (بدون delimiters) |
| `code` | `lang`, `code`, `out?`, `stdin?` |
| `mistakes` | `title`, `rows:[{no, yes}]` |
| `method` | `title`, `steps:[html]` |
| `xq` | `q`, `steps:[{label, body}]`, `a` |
| `faq` | `title`, `items:[{q, a}]` |
| `card` | `front`, `back` |
| `checklist` | `title?`, `items:[html]`, `rest?` |
| `quiz` | `q` (فوق) |

الـ HTML مسموح فيه بس: p b strong i em code bdi span br ul ol li sub sup small table tr td th pre div details summary. الرياضيات TeX داخل `\( … \)` و`\[ … \]`. التفاصيل الكاملة بعقد الـ API (`docs/API.md` بمشروع التطبيق shibbur-ios).

## صوت الدرس
كل درس ممكن يكون إله شرح صوتي ("استمع للدرس"): مدرّس بيحكي مع الطالب، والتطبيق بيظلّل البلوك والعبارة والمعادلة وقت ما بتنقال. العقد الكامل: `docs/NARRATION.md` بمشروع التطبيق.

**الملفات**
```
courses/<code>/narration/<slug>.json   النص المحكي (بيكتبه الـ skill)
courses/<code>/audio/<slug>/NNN.mp3    ملف صوت لكل مقطع (000، 001، …)
```
البناء بيتحقق منهم (`show` لازم يكون موجود بنص البلوك، `math` ضمن عدد المعادلات، الملفات الصوتية كلها موجودة) وبينشر `narration/<code>/<slug>.json` و`audio/<code>/<slug>/`. بالـ `LessonMeta` بيطلع `narrated: true` وإذا الصوت كامل `audio: true`. إذا تغيّر الدرس بعد كتابة الشرح بيطلع تحذير "narration may be stale".

**تصدير لخدمة صوت**
```
node scripts/narration.mjs export <code> [slug] --provider elevenlabs|gemini|openai|generic --out tts/
```
بيكتب `tts/<code>/<slug>.jsonl` (طلب لكل مقطع) و`README.txt`. حوّل كل سطر لملف `000.mp3`، `001.mp3`… (وإذا بتقدر خُد timings: ElevenLabs alignment أو Whisper words بملف `000.json`).

**استيراد**
```
node scripts/narration.mjs import <code> <slug> --dir <مجلد الصوت> --provider elevenlabs
```
بينسخ الصوت لـ `courses/<code>/audio/<slug>/` وبيكتب قسم `audio` (المدة وتوقيت كل كلمة؛ بدون timings بيتقدّر من طول النص) جوّا ملف الشرح.

`node scripts/narration.mjs stats [code]` بيعرض عدد المقاطع والحروف والدقائق المقدّرة وإذا الصوت موجود.

**شو بيعمل التطبيق:** إذا في صوت بيشغّله، وإلا بيقرأ النص بصوت الآيفون العربي؛ بيظلّل البلوك والعبارة والكلمة الحالية، وبيحرّك رسمات الخطوات مع الصوت.

## النشر
Push على `main` → GitHub Actions بيعمل `--check` وبيبني وبينشر `dist/` على Pages. الـ PR بيعمل تحقق بس.

## لون وأيقونة الكورس

بـ `site.json` كل كورس إله `color` و`icon`، وكل موضوع إله `icon`:

- `color`: واحد من `indigo` `coral` `teal` `amber` `violet` `green` `rose` `sky`
- `icon`: اسم أيقونة من SF Symbols (مثلاً `function`، `cpu`، `chart.xyaxis.line`، `memorychip.fill`). بتلاقي الأسماء بتطبيق SF Symbols عالماك.

إذا ما حطّيتهم، التطبيق بيختار لون وأيقونة ثابتين للكورس لحاله.

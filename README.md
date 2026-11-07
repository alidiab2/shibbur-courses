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

## النشر
Push على `main` → GitHub Actions بيعمل `--check` وبيبني وبينشر `dist/` على Pages. الـ PR بيعمل تحقق بس.

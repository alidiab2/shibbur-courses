// Build the static JSON API from the source layout.
// usage: node scripts/build.mjs [--out dist] [--check]
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const check = args.includes('--check');
const oi = args.indexOf('--out');
const outDir = path.resolve(root, oi >= 0 ? args[oi + 1] : 'dist');

const BLOCKS = {
  why: ['html'], p: ['html'], h: ['text'], box: ['kind', 'title', 'html'],
  figure: ['svg', 'alt'], math: ['tex'], code: ['lang', 'code'],
  mistakes: ['title', 'rows'], method: ['title', 'steps'], xq: ['q', 'steps', 'a'],
  faq: ['title', 'items'], card: ['front', 'back'], checklist: ['items'],
  html: ['html'], quiz: ['q'],
};

const errors = [];
const err = (m) => errors.push(m);
const readJSON = (p) => {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); }
  catch (e) { err(`${path.relative(root, p)}: ${e.message}`); return null; }
};
const isStr = (x) => typeof x === 'string';
const sha1 = (s) => crypto.createHash('sha1').update(s).digest('hex');
const pick = (o, keys) => Object.fromEntries(keys.filter((k) => o[k] !== undefined && o[k] !== null).map((k) => [k, o[k]]));

function validateQuestion(q, where) {
  if (!q || typeof q !== 'object') return err(`${where}: quiz.q missing`);
  if (q.kind !== 'mc' && q.kind !== 'text') err(`${where}: kind must be "mc" or "text"`);
  if (!isStr(q.prompt)) err(`${where}: missing prompt`);
  if (!isStr(q.solution)) err(`${where}: missing solution`);
  if (!Array.isArray(q.answer) || !q.answer.length || !q.answer.every(isStr)) err(`${where}: answer must be a non-empty array of strings`);
  if (q.kind === 'mc') {
    if (!Array.isArray(q.options) || !q.options.length) return err(`${where}: mc needs options`);
    q.options.forEach((o, i) => {
      if (!o || o.v !== String(i + 1)) err(`${where}: option ${i} must have v="${i + 1}"`);
      if (!o || !isStr(o.html)) err(`${where}: option ${i} missing html`);
    });
    if (Array.isArray(q.answer)) {
      if (q.answer.length !== 1) err(`${where}: mc answer must have exactly one value`);
      for (const a of q.answer) if (!q.options.some((o) => o && o.v === a)) err(`${where}: mc answer "${a}" is not one of options[].v`);
    }
  }
}

function validateBlock(b, where) {
  if (!b || typeof b !== 'object' || !isStr(b.t)) return err(`${where}: block without "t"`);
  if (!(b.t in BLOCKS)) return err(`${where}: unknown block type "${b.t}"`);
  for (const k of BLOCKS[b.t]) if (b[k] === undefined || b[k] === null) err(`${where}: block "${b.t}" missing "${k}"`);
  if (b.t === 'quiz') validateQuestion(b.q, where);
}

// ---------- load + validate ----------
const site = readJSON(path.join(root, 'site.json'));
if (!site) fail();
for (const k of ['name', 'tagline']) if (!isStr(site[k])) err(`site.json: missing ${k}`);
if (!Array.isArray(site.subjects)) { err('site.json: subjects must be an array'); fail(); }

const coursesDir = path.join(root, 'courses');
const folders = fs.existsSync(coursesDir)
  ? fs.readdirSync(coursesDir, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name) : [];
const listed = new Set();
const courses = new Map(); // code -> {course, lessons:[Lesson], questions:[Question]}

const HUES = ['indigo', 'coral', 'teal', 'amber', 'violet', 'green', 'rose', 'sky'];
for (const s of site.subjects) {
  if (s.icon !== undefined && !isStr(s.icon)) err(`site.json: subject ${s.id} icon must be an SF Symbol name`);
  for (const k of ['id', 'title', 'desc']) if (!isStr(s[k])) err(`site.json: subject missing ${k}`);
  for (const c of s.courses || []) {
    if (!isStr(c.code) || !isStr(c.tag)) err(`site.json: course entry needs code and tag`);
    if (c.color !== undefined && !HUES.includes(c.color)) err(`site.json: course ${c.code} color "${c.color}" must be one of ${HUES.join(', ')}`);
    if (c.icon !== undefined && !isStr(c.icon)) err(`site.json: course ${c.code} icon must be an SF Symbol name`);
    if (listed.has(c.code)) err(`site.json: course ${c.code} listed twice`);
    listed.add(c.code);
    if (!folders.includes(c.code)) err(`site.json: course ${c.code} has no folder courses/${c.code}`);
  }
}
for (const f of folders) if (!listed.has(f)) err(`courses/${f}: folder not listed in site.json`);

for (const code of folders.filter((f) => listed.has(f))) {
  const dir = path.join(coursesDir, code);
  const c = readJSON(path.join(dir, 'course.json'));
  if (!c) continue;
  const W = `courses/${code}`;
  if (c.code !== code) err(`${W}/course.json: code "${c.code}" does not match folder`);
  for (const k of ['title', 'desc', 'subject']) if (!isStr(c[k])) err(`${W}/course.json: missing ${k}`);
  if (!site.subjects.some((s) => s.id === c.subject && (s.courses || []).some((x) => x.code === code))) err(`${W}/course.json: subject "${c.subject}" does not list this course in site.json`);
  if (!Array.isArray(c.chapters)) { err(`${W}/course.json: chapters must be an array`); continue; }

  const lessonsDir = path.join(dir, 'lessons');
  const files = fs.existsSync(lessonsDir) ? fs.readdirSync(lessonsDir).filter((f) => f.endsWith('.json')).map((f) => f.slice(0, -5)) : [];
  const used = new Set();
  const chapters = [], lessons = [], questions = [];
  const ns = new Set();

  for (const ch of c.chapters) {
    for (const k of ['slug', 'title', 'lead']) if (!isStr(ch[k])) err(`${W}: chapter ${ch.n} missing ${k}`);
    if (!Number.isInteger(ch.n)) err(`${W}: chapter "${ch.slug}" needs integer n`);
    if (ns.has(ch.n)) err(`${W}: duplicate chapter n ${ch.n}`);
    ns.add(ch.n);
    if (typeof ch.isExam !== 'boolean') err(`${W}: chapter ${ch.n} needs boolean isExam`);
    if (!Array.isArray(ch.lessons)) { err(`${W}: chapter ${ch.n} lessons must be an array`); continue; }
    const metas = [];
    for (const slug of ch.lessons) {
      if (used.has(slug)) { err(`${W}: duplicate lesson slug "${slug}"`); continue; }
      used.add(slug);
      if (!files.includes(slug)) { err(`${W}: lesson "${slug}" listed in chapter ${ch.n} but ${W}/lessons/${slug}.json is missing`); continue; }
      const L = readJSON(path.join(lessonsDir, `${slug}.json`));
      if (!L) continue;
      const LW = `${W}/lessons/${slug}.json`;
      if (L.slug !== slug) err(`${LW}: slug "${L.slug}" does not match filename`);
      for (const k of ['title', 'desc']) if (!isStr(L[k])) err(`${LW}: missing ${k}`);
      if (!Number.isInteger(L.minutes)) err(`${LW}: minutes must be an integer`);
      if (!Array.isArray(L.blocks)) { err(`${LW}: blocks must be an array`); continue; }
      let i = 0;
      const blocks = L.blocks.map((b, bi) => {
        validateBlock(b, `${LW} block ${bi}`);
        if (b && b.t === 'quiz' && b.q) {
          const q = {
            id: `${code}/${slug}/${i++}`, lesson: slug, chapter: ch.n,
            ...pick(b.q, ['kind', 'prompt', 'options', 'answer', 'hint', 'solution']),
          };
          questions.push(q);
          return { ...b, q };
        }
        return b;
      });
      const nq = i;
      const meta = { ...pick(L, ['slug', 'title', 'he', 'ref', 'minutes', 'desc']), questions: nq };
      metas.push(meta);
      lessons.push({ v: 1, code, chapter: ch.n, ...pick(L, ['slug', 'title', 'he', 'ref', 'minutes', 'desc']), blocks });
    }
    chapters.push({ n: ch.n, slug: ch.slug, title: ch.title, lead: ch.lead, isExam: ch.isExam, lessons: metas });
  }
  for (const f of files) if (!used.has(f)) err(`${W}/lessons/${f}.json: not listed in any chapter`);
  const look = site.subjects.flatMap((s) => s.courses || []).find((x) => x.code === code) || {};
  courses.set(code, {
    course: { v: 1, code, title: c.title, desc: c.desc, subject: c.subject, hash: '', ...pick(look, ['color', 'icon']), chapters },
    lessons, questions,
  });
}

function fail() {
  console.error(`\n${errors.length} error(s):\n` + errors.map((e) => `  - ${e}`).join('\n'));
  process.exit(1);
}
if (errors.length) fail();

// ---------- hashes + summaries ----------
const summaries = new Map();
const manifestCourses = [];
const bundleText = new Map();
for (const [code, d] of courses) {
  const hash = sha1(JSON.stringify({ v: 1, course: d.course, lessons: d.lessons })).slice(0, 10);
  d.course.hash = hash;
  const bundle = JSON.stringify({ v: 1, course: d.course, lessons: d.lessons });
  bundleText.set(code, bundle);
  const minutes = d.lessons.reduce((a, l) => a + l.minutes, 0);
  const entry = site.subjects.flatMap((s) => s.courses).find((x) => x.code === code);
  summaries.set(code, {
    code, title: d.course.title, desc: d.course.desc, tag: entry.tag, subject: d.course.subject,
    chapters: d.course.chapters.length, lessons: d.lessons.length, questions: d.questions.length,
    minutes, paid: entry.paid === true, hash, ...pick(entry, ['color', 'icon']),
  });
  manifestCourses.push({ code, hash, lessons: d.lessons.length, questions: d.questions.length, bytes: Buffer.byteLength(bundle) });
}

if (check) {
  console.log(`OK: ${courses.size} courses valid`);
  for (const [code, s] of summaries) console.log(`  ${code}: ${s.chapters} chapters, ${s.lessons} lessons, ${s.questions} questions, ${s.minutes} min`);
  process.exit(0);
}

// ---------- write ----------
fs.rmSync(outDir, { recursive: true, force: true });
const put = (rel, data) => {
  const p = path.join(outDir, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, typeof data === 'string' ? data : JSON.stringify(data));
};
put('.nojekyll', '');
put('manifest.json', { v: 1, generated: new Date().toISOString(), courses: manifestCourses });
put('catalog.json', {
  v: 1, site: { name: site.name, tagline: site.tagline },
  subjects: site.subjects.map((s) => ({ id: s.id, title: s.title, desc: s.desc, ...pick(s, ['icon']), courses: (s.courses || []).map((c) => summaries.get(c.code)) })),
});
for (const [code, d] of courses) {
  put(`course/${code}.json`, d.course);
  for (const l of d.lessons) put(`lesson/${code}/${l.slug}.json`, l);
  put(`questions/${code}.json`, { v: 1, code, questions: d.questions });
  put(`bundle/${code}.json`, bundleText.get(code));
}
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
put('index.html', `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(site.name)}</title>
<body dir="rtl" style="font-family:system-ui;max-width:640px;margin:2rem auto;padding:0 1rem">
<h1>${esc(site.name)}</h1><p>${esc(site.tagline)}</p>
<ul>${[...summaries.values()].map((s) => `<li><a href="bundle/${s.code}.json">${esc(s.title)}</a> — ${s.lessons} دروس، ${s.questions} سؤال <code>${s.hash}</code></li>`).join('')}</ul>
<p><a href="manifest.json">manifest.json</a> · <a href="catalog.json">catalog.json</a></p></body>`);
console.log(`Built ${courses.size} courses -> ${path.relative(process.cwd(), outDir) || '.'}`);
for (const [code, s] of summaries) console.log(`  ${code}: ${s.chapters} chapters, ${s.lessons} lessons, ${s.questions} questions, ${s.minutes} min, hash ${s.hash}`);

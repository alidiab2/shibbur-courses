// Build the static JSON API from the source layout.
// usage: node scripts/build.mjs [--out dist] [--check]
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { validateNarration, resolveNarration, speakOptsFor } from './narration-lib.mjs';

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
  steps: ['svg', 'frames', 'alt'],   // a figure that builds frame by frame (data-step / data-only / data-until on svg elements)
};

// Drawings must be self-contained, themeable and safe: one root <svg> with a viewBox, no scripts/handlers/external refs.
function validateSVG(svg, where) {
  if (!isStr(svg)) return err(`${where}: svg must be a string`);
  const t = svg.trim();
  if (!t.startsWith('<svg') || !t.endsWith('</svg>')) err(`${where}: svg must be one <svg>…</svg> element`);
  if (!/viewBox="[^"]+"/.test(t)) err(`${where}: svg needs a viewBox (it scales to the screen width)`);
  if (/<script|\son[a-z]+=|javascript:|(?:href|src)="https?:/i.test(t)) err(`${where}: svg has scripts, event handlers or external links`);
  if (/<svg[^>]*\swidth="\d/.test(t)) err(`${where}: drop width/height on the root svg; size comes from viewBox`);
  return t;
}

const errors = [];
const warnings = [];
const narrations = new Map(); // `${code}/${slug}` -> {data, audioDir|null}
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

// RTL text whose sentence/paragraph ENDS with inline math (or digits) renders its punctuation on the wrong
// side and can scramble the line — catch it before rendering.
function bidiLint(b, where) {
  const texts = [];
  const walk = (v, k) => {
    if (typeof v === 'string') { if (k !== 'svg' && /[\u0600-\u06FF]/.test(v)) texts.push([k, v]); }
    else if (Array.isArray(v)) v.forEach((x) => walk(x, k));
    else if (v && typeof v === 'object') for (const [kk, x] of Object.entries(v)) walk(x, kk);
  };
  walk(b, '');
  for (const [k, v] of texts) {
    for (const part of v.split(/<\/(?:p|li|td|th|summary)>|<br\s*\/?>/)) {
      const t = part.replace(/<[^>]+>/g, '').trim();
      if (!/[\u0600-\u06FF]/.test(t)) continue;
      if (/\\\)\s*[.،؟?!:؛]$/.test(t) && !/^[^A-Za-z0-9\\]*[\u0600-\u06FF]/.test(t)) warnings.push(`${where}: BIDI (look at it in the render) — "${k}" starts with math/Latin and ends with math + punctuation (the line takes LTR direction and scrambles): "…${t.slice(-40)}" — end the sentence with an Arabic word or put the formula on its own \\[ \\] line`);
    }
  }
}

function validateBlock(b, where) {
  if (!b || typeof b !== 'object' || !isStr(b.t)) return err(`${where}: block without "t"`);
  if (!(b.t in BLOCKS)) return err(`${where}: unknown block type "${b.t}"`);
  for (const k of BLOCKS[b.t]) if (b[k] === undefined || b[k] === null) err(`${where}: block "${b.t}" missing "${k}"`);
  if (b.t === 'quiz') validateQuestion(b.q, where);
  bidiLint(b, where);
  if (b.t === 'figure') validateSVG(b.svg, where);
  if (b.t === 'steps') {
    const svg = validateSVG(b.svg, where);
    if (!Array.isArray(b.frames) || b.frames.length < 2) return err(`${where}: steps needs at least 2 frames`);
    b.frames.forEach((f, i) => { if (!f || !isStr(f.caption)) err(`${where}: steps frame ${i + 1} needs a caption`); });
    if (svg) {
      const used = [...svg.matchAll(/data-(?:step|only|until)="(\d+)"/g)].map((m) => +m[1]);
      if (!used.length) err(`${where}: steps svg has no data-step / data-only / data-until elements`);
      for (const n of used) if (n < 1 || n > b.frames.length) err(`${where}: steps svg refers to frame ${n} but there are ${b.frames.length} frames`);
    }
  }
}

// Optional narration: courses/<code>/narration/<slug>.json (+ audio/<slug>/ files).
function loadNarration(code, slug, L, W, sopts) {
  const np = path.join(root, 'courses', code, 'narration', `${slug}.json`);
  const audioDir = path.join(root, 'courses', code, 'audio', slug);
  if (!fs.existsSync(np)) {
    if (fs.existsSync(audioDir)) warnings.push(`${W}/audio/${slug}: audio folder without a narration file (ignored)`);
    return null;
  }
  const NW = `${W}/narration/${slug}.json`;
  const data = readJSON(np);
  if (!data) return null;
  const r = validateNarration(data, L, NW, sopts);
  r.errors.forEach(err); warnings.push(...r.warnings);
  const resolved = r.errors.length ? data : resolveNarration(data, L, sopts); // math parts get their reading from speakmath
  let audioOk = false;
  if (data.audio !== undefined) {
    const a = data.audio, segs = Array.isArray(data.segments) ? data.segments : [];
    if (!a || typeof a !== 'object' || !isStr(a.provider) || !Array.isArray(a.segments)) err(`${NW}: audio must be {provider, segments:[]}`);
    else if (a.segments.length !== segs.length) err(`${NW}: audio has ${a.segments.length} segments but narration has ${segs.length}`);
    else {
      let ok = true;
      a.segments.forEach((x, i) => {
        if (!x || !isStr(x.src) || !(typeof x.dur === 'number' && x.dur > 0)) { ok = false; return err(`${NW}: audio.segments[${i}] needs src and dur`); }
        if (x.src !== path.basename(x.src) || !fs.existsSync(path.join(audioDir, x.src))) { ok = false; err(`${NW}: audio file ${W}/audio/${slug}/${x.src} is missing`); }
        if (x.words !== undefined && !Array.isArray(x.words)) { ok = false; err(`${NW}: audio.segments[${i}].words must be an array`); }
      });
      audioOk = ok;
    }
  } else if (fs.existsSync(audioDir)) warnings.push(`${NW}: audio folder exists but the narration has no "audio" section (run narration.mjs import)`);
  narrations.set(`${code}/${slug}`, { data: resolved, audioDir: audioOk ? audioDir : null });
  return { audioOk };
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
      const nar = loadNarration(code, slug, L, W, speakOptsFor(c, slug));
      if (nar) { meta.narrated = true; if (nar.audioOk) meta.audio = true; }
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
  for (const w of warnings) console.warn(`warning: ${w}`);
  console.error(`\n${errors.length} error(s):\n` + errors.map((e) => `  - ${e}`).join('\n'));
  process.exit(1);
}
if (errors.length) fail();
for (const w of warnings) console.warn(`warning: ${w}`);

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
  console.log(`OK: ${courses.size} courses valid, ${narrations.size} narrations`);
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
for (const [key, n] of narrations) {
  put(`narration/${key}.json`, n.data);
  if (n.audioDir) fs.cpSync(n.audioDir, path.join(outDir, 'audio', key), { recursive: true });
}
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
put('index.html', `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(site.name)}</title>
<body dir="rtl" style="font-family:system-ui;max-width:640px;margin:2rem auto;padding:0 1rem">
<h1>${esc(site.name)}</h1><p>${esc(site.tagline)}</p>
<ul>${[...summaries.values()].map((s) => `<li><a href="bundle/${s.code}.json">${esc(s.title)}</a> — ${s.lessons} دروس، ${s.questions} سؤال <code>${s.hash}</code></li>`).join('')}</ul>
<p><a href="manifest.json">manifest.json</a> · <a href="catalog.json">catalog.json</a></p></body>`);
console.log(`Built ${courses.size} courses -> ${path.relative(process.cwd(), outDir) || '.'}`);
for (const [code, s] of summaries) console.log(`  ${code}: ${s.chapters} chapters, ${s.lessons} lessons, ${s.questions} questions, ${s.minutes} min, hash ${s.hash}`);

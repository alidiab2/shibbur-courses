// One-off: convert live API dumps (catalog.json + bundle-<code>.json) into the source layout.
// usage: node scripts/import.mjs <dir-with-dumps>
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const src = process.argv[2];
if (!src) { console.error('usage: node scripts/import.mjs <dir>'); process.exit(1); }

const readJSON = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const writeJSON = (p, o) => {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(o, null, 2) + '\n');
};
const pick = (o, keys) => Object.fromEntries(keys.filter((k) => o[k] !== undefined && o[k] !== null).map((k) => [k, o[k]]));

const catalog = readJSON(path.join(src, 'catalog.json'));
writeJSON(path.join(root, 'site.json'), {
  name: catalog.site.name,
  tagline: catalog.site.tagline,
  subjects: catalog.subjects.map((s) => ({
    id: s.id, title: s.title, desc: s.desc,
    courses: s.courses.map((c) => ({ code: c.code, tag: c.tag, paid: c.paid })),
  })),
});

for (const s of catalog.subjects) for (const c of s.courses) {
  const { course, lessons } = readJSON(path.join(src, `bundle-${c.code}.json`));
  const bySlug = new Map();
  for (const l of lessons) {
    if (bySlug.has(l.slug)) throw new Error(`dup slug ${c.code}/${l.slug}`);
    bySlug.set(l.slug, l);
  }
  const dir = path.join(root, 'courses', c.code);
  fs.rmSync(dir, { recursive: true, force: true });
  writeJSON(path.join(dir, 'course.json'), {
    code: course.code, title: course.title, desc: course.desc, subject: course.subject,
    chapters: course.chapters.map((ch) => ({
      n: ch.n, slug: ch.slug, title: ch.title, lead: ch.lead, isExam: ch.isExam,
      lessons: ch.lessons.map((m) => m.slug),
    })),
  });
  for (const l of lessons) {
    let i = 0;
    const blocks = l.blocks.map((b) => {
      if (b.t !== 'quiz') return b;
      const expected = `${c.code}/${l.slug}/${i++}`;
      if (b.q.id !== expected) console.warn(`odd question id ${b.q.id} (expected ${expected})`);
      const { id, lesson, chapter, ...q } = b.q;
      return { ...b, q: pick(q, ['kind', 'prompt', 'options', 'answer', 'hint', 'solution']) };
    });
    writeJSON(path.join(dir, 'lessons', `${l.slug}.json`), {
      ...pick(l, ['slug', 'title', 'he', 'ref', 'minutes', 'desc']), blocks,
    });
  }
  console.log(`${c.code}: ${course.chapters.length} chapters, ${lessons.length} lessons`);
}

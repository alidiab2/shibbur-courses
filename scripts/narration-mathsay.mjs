// One-off migration: math parts of the narrations get their reading from speakmath instead of a hand-written `say`.
//   node scripts/narration-mathsay.mjs [--dry] [--report FILE]
// For every math part: compare the hand-written say with speak(<k-th TeX of the block>), write a report
// (formula | old | new), then remove `say` from the part (unless it has "keep": true). --dry changes no file.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { blockTex, isKept, speakOptsFor } from './narration-lib.mjs';
import { speak } from './speakmath.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const dry = args.includes('--dry');
const ri = args.indexOf('--report');
const reportPath = ri >= 0 ? path.resolve(args[ri + 1]) : '/private/tmp/claude-504/mathsay-diff.txt';

// compare ignoring punctuation, spacing, diacritics and spelling variants of alef/ya/ta marbuta
const norm = (s) => s.normalize('NFKD').replace(/[ً-ٰٟـ]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
  .replace(/[^\p{L}\p{N}]/gu, '').toLowerCase();

// words-overlap similarity (0..1) of two readings, used only to spot `math: k` indices that point at the wrong formula
const words = (s) => new Set(s.normalize('NFKD').replace(/[ً-ٰٟـ]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
  .replace(/[^\p{L}\p{N}\s]/gu, '').toLowerCase().split(/\s+/).filter(Boolean));
const sim = (a, b) => {
  const A = words(a), B = words(b);
  let i = 0;
  for (const w of A) if (B.has(w)) i++;
  return i / Math.max(1, (A.size + B.size) / 2);
};

const rows = [];
const suspects = [];
let files = 0, parts = 0, removed = 0, kept = 0, already = 0;
const codes = fs.readdirSync(path.join(root, 'courses'), { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name).sort();
for (const code of codes) {
  const nd = path.join(root, 'courses', code, 'narration');
  if (!fs.existsSync(nd)) continue;
  for (const f of fs.readdirSync(nd).filter((x) => x.endsWith('.json')).sort()) {
    const slug = f.slice(0, -5);
    const np = path.join(nd, f);
    const n = JSON.parse(fs.readFileSync(np, 'utf8'));
    const lesson = JSON.parse(fs.readFileSync(path.join(root, 'courses', code, 'lessons', `${slug}.json`), 'utf8'));
    const sopts = speakOptsFor(JSON.parse(fs.readFileSync(path.join(root, 'courses', code, 'course.json'), 'utf8')), slug);
    let changed = false;
    n.segments.forEach((seg, si) => {
      seg.say.forEach((p) => {
        if (!p || typeof p !== 'object' || p.math === undefined) return;
        parts++;
        const tex = blockTex(lesson.blocks[seg.block])[p.math];
        const gen = speak(tex, sopts);
        // does the hand reading describe ANOTHER formula of the same block? (a wrong `math` index in the narration)
        let suspect = null;
        if (typeof p.say === 'string' && norm(p.say) !== norm(gen)) {
          const texs = blockTex(lesson.blocks[seg.block]);
          const s0 = sim(p.say, gen);
          texs.forEach((t2, j) => {
            if (j === p.math || suspect) return;
            let g2; try { g2 = speak(t2, sopts); } catch { return; }
            if (norm(g2) === norm(p.say) || (sim(p.say, g2) >= 0.5 && s0 < 0.2)) suspect = { index: j, tex: t2 };
          });
        }
        if (typeof p.say === 'string') rows.push({ where: `${code}/${slug} seg ${si} block ${seg.block} math ${p.math}`, tex, old: p.say, gen, kept: isKept(p) });
        else already++;
        if (suspect) {
          suspects.push({ where: `${code}/${slug} seg ${si} block ${seg.block} math ${p.math}`, tex, old: p.say, alt: suspect });
          p.keep = true; changed = true; kept++; // leave the hand reading alone: the narration's index is probably wrong
          return;
        }
        if (isKept(p)) { kept++; return; }
        if ('say' in p) { delete p.say; removed++; changed = true; }
      });
    });
    files++;
    if (changed && !dry) fs.writeFileSync(np, JSON.stringify(n, null, 2) + '\n');
  }
}

const exact = rows.filter((r) => r.old === r.gen).length;
const same = rows.filter((r) => norm(r.old) === norm(r.gen)).length;
const diff = rows.filter((r) => norm(r.old) !== norm(r.gen));
// "partial": the hand reading is only a piece of the full reading (the narration text around it probably says the rest)
const isPartial = (r) => norm(r.gen).includes(norm(r.old)) && norm(r.old).length < norm(r.gen).length;
const partial = diff.filter(isPartial);
const lines = [];
lines.push(`narration math say: old hand-written reading vs speakmath`);
lines.push(`files ${files}, math parts ${parts}, with a hand-written say ${rows.length}, already generated ${already}`);
lines.push(`identical ${exact}, same after ignoring punctuation/spelling ${same - exact}, different ${diff.length}`);
lines.push(`of the different ones, ${partial.length} are partial readings (old is contained in new: the narration probably says the rest around it, tagged [partial])`);
lines.push(`say removed ${removed}${dry ? ' (dry run: nothing written)' : ''}, kept (keep:true) ${kept} of which suspect-index ${suspects.length}`);
lines.push('');
lines.push('formula | old (hand-written) | new (speakmath) | where');
lines.push('--------------------------------------------------------');
for (const r of diff) lines.push(`${r.tex} | ${r.old} | ${r.gen} | ${r.where}${isPartial(r) ? ' [partial]' : ''}`);
lines.push('');
lines.push(`SUSPECT INDEX (${suspects.length}): the hand reading matches another formula of the block better than the one \`math\` points at.`);
lines.push('These parts were given "keep": true (hand reading unchanged); fix the index in the narration, then drop keep.');
for (const x of suspects) lines.push(`${x.where}: points at ${x.tex} | old: ${x.old} | looks like ${x.alt.tex} (math ${x.alt.index})`);
lines.push('');
lines.push(`(${same} readings equal to the old one are not listed)`);
fs.mkdirSync(path.dirname(reportPath), { recursive: true });
fs.writeFileSync(reportPath, lines.join('\n') + '\n');
console.log(lines.slice(0, 4).join('\n'));
console.log(`report: ${reportPath}`);

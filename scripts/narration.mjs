// Narration tooling: export TTS requests, import audio + timings, stats.
//   node scripts/narration.mjs export <code> [slug] --provider elevenlabs|gemini|openai|generic --out DIR
//   node scripts/narration.mjs import <code> <slug> --dir FOLDER [--provider NAME]
//   node scripts/narration.mjs stats [code]
// Contract: shibbur-ios/docs/NARRATION.md. No dependencies.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spokenText, AUDIO_EXTS, resolveNarration, speakOptsFor } from './narration-lib.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const flags = {}, pos = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) flags[argv[i].slice(2)] = argv[++i]; else pos.push(argv[i]);
}
const [cmd, ...rest] = pos;
const die = (m) => { console.error(`error: ${m}`); process.exit(1); };
const readJSON = (p) => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (e) { die(`${path.relative(root, p)}: ${e.message}`); } };
// narration with every generated math reading filled in (needs the lesson for the TeX)
const resolved = (code, slug, n) => {
  const lp = path.join(root, 'courses', code, 'lessons', `${slug}.json`);
  if (!fs.existsSync(lp)) die(`missing ${path.relative(root, lp)} (needed to read the math parts)`);
  const cp = path.join(root, 'courses', code, 'course.json');
  try { return resolveNarration(n, readJSON(lp), speakOptsFor(fs.existsSync(cp) ? readJSON(cp) : null, slug)); } catch (e) { die(`${code}/${slug}: ${e.message}`); }
};
const nnn = (i) => String(i).padStart(3, '0');
const narrationPath = (code, slug) => path.join(root, 'courses', code, 'narration', `${slug}.json`);
const listNarrated = (code) => {
  const d = path.join(root, 'courses', code, 'narration');
  return fs.existsSync(d) ? fs.readdirSync(d).filter((f) => f.endsWith('.json')).map((f) => f.slice(0, -5)).sort() : [];
};
const allCodes = () => fs.readdirSync(path.join(root, 'courses'), { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name).sort();

// ---------- style mapping ----------
const EMO_AR = {
  calm: 'هادئ ومطمئن', warm: 'دافئ وودّي', curious: 'فضولي ومتسائل', excited: 'متحمّس', encouraging: 'مشجّع',
  serious: 'جدّي ومركّز', playful: 'مرح وخفيف', emphatic: 'يشدّد على الفكرة', reassuring: 'يطمّن الطالب', surprised: 'متفاجئ',
};
const EMO_EN = {
  calm: 'calm', warm: 'warm and friendly', curious: 'curious', excited: 'excited', encouraging: 'encouraging',
  serious: 'serious and focused', playful: 'playful', emphatic: 'emphatic', reassuring: 'reassuring', surprised: 'surprised',
};
const PACE_AR = { slow: 'ببطء ووضوح', normal: 'بسرعة عادية', fast: 'بسرعة أكبر شوي' };
const PACE_EN = { slow: 'slowly and clearly', normal: 'at a natural pace', fast: 'a little faster' };
const PACE_SPEED = { slow: 0.85, normal: 1.0, fast: 1.12 };
const defaults = (s) => ({ emotion: s.emotion || 'calm', pace: s.pace || 'normal', pause: s.pause ?? 0 });

// ElevenLabs v3: emotion as a bracket audio tag at the start; pauses as "..." at the end.
// If v3 tags change, adjust only elTag() / elPause().
const elTag = (emotion) => `[${emotion}]`;
const elPause = (pause) => (pause >= 1.5 ? ' ... ... ...' : pause >= 0.75 ? ' ... ...' : pause >= 0.3 ? ' ...' : '');

function buildRequest(provider, code, slug, i, seg, voice) {
  const text = spokenText(seg);
  const { emotion, pace, pause } = defaults(seg);
  const persona = (voice && voice.persona) || '';
  const style = seg.style || '';
  const base = { code, slug, index: i, file: nnn(i) };
  switch (provider) {
    case 'generic':
      return { ...base, text, emotion, pace, style, pause, voice: voice || {} };
    case 'elevenlabs':
      return { ...base, model: 'eleven_v3', text: `${elTag(emotion)} ${text}${elPause(pause)}`,
        voice_settings: { speed: PACE_SPEED[pace], stability: emotion === 'calm' || emotion === 'serious' ? 0.7 : 0.4 } };
    case 'gemini':
      return { ...base, text,
        prompt: ['تكلّم بلهجة شامية/فلسطينية طبيعية.', persona && `الشخصية: ${persona}.`, `النبرة: ${EMO_AR[emotion]}.`, `السرعة: ${PACE_AR[pace]}.`, style && `توجيه إضافي: ${style}.`].filter(Boolean).join(' ') };
    case 'openai':
      return { ...base, input: text,
        instructions: [`Speak Levantine/Palestinian Arabic like a friendly tutor. Tone: ${EMO_EN[emotion]}. Speak ${PACE_EN[pace]}.`,
          persona && `Persona: ${persona}.`, style && `Direction: ${style}.`,
          `تكلّم بلهجة شامية/فلسطينية، بنبرة ${EMO_AR[emotion]}، ${PACE_AR[pace]}.`].filter(Boolean).join(' ') };
    default: die(`unknown provider "${provider}"`);
  }
}

const README_TXT = (provider) => `Narration TTS requests (provider: ${provider})
==========================================
Layout:  <code>/<slug>.jsonl   one JSON request per line, one line per audio segment.
Each line has "index" and "file" (000, 001, ...). Turn each line into one audio clip and name it <file>.mp3
(e.g. 000.mp3, 001.mp3, ...). The text to speak is in "text" (or "input" for openai).
${provider === 'elevenlabs' ? 'ElevenLabs: use model eleven_v3 and the "with timestamps" endpoint if you can; keep the character alignment JSON as <file>.json.\n' : ''}${provider === 'gemini' ? 'Gemini: "prompt" is the style direction, "text" is what to speak.\n' : ''}${provider === 'openai' ? 'OpenAI: "instructions" is the voice direction, "input" is what to speak.\n' : ''}
Expected return folder (per lesson):
  000.mp3 001.mp3 ...        required, one per segment, same numbering
  000.json 001.json ...      optional word timings, either
        ElevenLabs alignment: {"characters":[...],"character_start_times_seconds":[...],"character_end_times_seconds":[...]}
        (may be nested under "alignment" or "normalized_alignment")
     or Whisper words:        {"words":[{"word":"..","start":0.0,"end":0.4}, ...]}
  Without timings the app estimates word timing from text length.
Then run:
  node scripts/narration.mjs import <code> <slug> --dir <folder> --provider ${provider}
which copies the audio to courses/<code>/audio/<slug>/ and writes the "audio" section into
courses/<code>/narration/<slug>.json. The "pause" value is silence after the segment (the app adds it; ElevenLabs gets "..." too).
`;

function doExport() {
  const [code, slug] = rest;
  if (!code) die('usage: export <code> [slug] --provider P --out DIR');
  const provider = flags.provider || 'generic';
  if (!flags.out) die('--out DIR is required');
  const out = path.resolve(flags.out);
  const slugs = slug ? [slug] : listNarrated(code);
  if (!slugs.length) die(`no narration files in courses/${code}/narration`);
  fs.mkdirSync(path.join(out, code), { recursive: true });
  let total = 0;
  for (const s of slugs) {
    const p = narrationPath(code, s);
    if (!fs.existsSync(p)) die(`missing ${path.relative(root, p)}`);
    const n = resolved(code, s, readJSON(p));
    const lines = n.segments.map((seg, i) => JSON.stringify(buildRequest(provider, code, s, i, seg, n.voice)));
    fs.writeFileSync(path.join(out, code, `${s}.jsonl`), lines.join('\n') + '\n');
    total += lines.length;
    console.log(`  ${code}/${s}: ${lines.length} requests`);
  }
  fs.writeFileSync(path.join(out, 'README.txt'), README_TXT(provider));
  console.log(`Exported ${total} requests (${provider}) -> ${out}`);
}

// ---------- mp3 duration (MPEG audio frame walk) ----------
const BR = {
  '1-1': [0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448], '1-2': [0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384],
  '1-3': [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320], '2-1': [0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256],
  '2-2': [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160], '2-3': [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
};
const SR = { 3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000] };
export function mp3Duration(buf) {
  let pos = 0;
  if (buf.length > 10 && buf.toString('latin1', 0, 3) === 'ID3') pos = 10 + (((buf[6] & 0x7f) << 21) | ((buf[7] & 0x7f) << 14) | ((buf[8] & 0x7f) << 7) | (buf[9] & 0x7f));
  let secs = 0, frames = 0;
  while (pos + 4 <= buf.length) {
    if (buf[pos] !== 0xff || (buf[pos + 1] & 0xe0) !== 0xe0) { pos++; continue; }
    const ver = (buf[pos + 1] >> 3) & 3, layer = (buf[pos + 1] >> 1) & 3, bri = buf[pos + 2] >> 4, sri = (buf[pos + 2] >> 2) & 3, pad = (buf[pos + 2] >> 1) & 1;
    if (ver === 1 || layer === 0 || bri === 0 || bri === 15 || sri === 3) { pos++; continue; }
    const L = 4 - layer, v = ver === 3 ? 1 : 2;
    const kbps = BR[`${v}-${L}`][bri], sr = SR[ver][sri];
    const spf = L === 1 ? 384 : (L === 3 && v === 2 ? 576 : 1152);
    const len = L === 1 ? (Math.floor(12 * kbps * 1000 / sr) + pad) * 4 : Math.floor((spf / 8) * kbps * 1000 / sr) + pad;
    if (len < 4) { pos++; continue; }
    secs += spf / sr; frames++; pos += len;
  }
  return frames ? secs : null;
}

// ---------- timings -> words ----------
const r3 = (x) => Math.round(x * 1000) / 1000;
function splitWords(text) {
  const out = []; const re = /\S+/g; let m;
  while ((m = re.exec(text))) out.push({ c: m.index, n: m[0].length, t: m[0] });
  return out;
}
const norm = (w) => w.normalize('NFKD').replace(/[ً-ٰٟـ]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
  .replace(/[^\p{L}\p{N}]/gu, '').toLowerCase();

// fill null starts/ends by linear interpolation between known neighbours
function fillGaps(ws, dur) {
  let i = 0;
  while (i < ws.length) {
    if (ws[i].s != null) { i++; continue; }
    let j = i; while (j < ws.length && ws[j].s == null) j++;
    const a = i > 0 ? ws[i - 1].e : 0, b = j < ws.length ? ws[j].s : dur;
    const cnt = j - i, step = (b - a) / cnt;
    for (let k = 0; k < cnt; k++) { ws[i + k].s = a + step * k; ws[i + k].e = a + step * (k + 1); }
    i = j;
  }
}

function fromElevenLabs(al, text, dur) {
  const A = al.alignment || al.normalized_alignment || al;
  const chars = A.characters, st = A.character_start_times_seconds, en = A.character_end_times_seconds;
  // drop audio tags like [warm] and <break .../> from the timing characters
  const tc = []; let depth = 0, tag = 0;
  chars.forEach((ch, k) => {
    if (ch === '[') { depth++; return; }
    if (ch === ']' && depth) { depth--; return; }
    if (ch === '<') { tag++; return; }
    if (ch === '>' && tag) { tag--; return; }
    if (depth || tag) return;
    tc.push({ ch, s: st[k], e: en[k] });
  });
  const cs = new Array(text.length).fill(null);
  let j = 0;
  for (let i = 0; i < text.length; i++) {
    if (/\s/.test(text[i])) continue;
    let f = -1;
    for (let k = j; k < Math.min(tc.length, j + 8); k++) if (tc[k].ch === text[i]) { f = k; break; }
    if (f >= 0) { cs[i] = tc[f]; j = f + 1; }
  }
  const ws = splitWords(text).map((w) => {
    const hit = cs.slice(w.c, w.c + w.n).filter(Boolean);
    return { c: w.c, n: w.n, s: hit.length ? hit[0].s : null, e: hit.length ? hit[hit.length - 1].e : null };
  });
  return ws;
}

function fromWhisper(list, text) {
  const tw = splitWords(text);
  const sw = list.map((w) => ({ n: norm(w.word || w.text || ''), s: w.start, e: w.end }));
  let j = 0;
  return tw.map((w) => {
    const key = norm(w.t);
    let f = -1;
    if (key) for (let k = j; k < Math.min(sw.length, j + 6); k++) if (sw[k].n === key) { f = k; break; }
    if (f < 0) return { c: w.c, n: w.n, s: null, e: null };
    j = f + 1;
    return { c: w.c, n: w.n, s: sw[f].s, e: sw[f].e };
  });
}

function estimate(text, dur) {
  const tw = splitWords(text); const total = tw.reduce((a, w) => a + w.n + 1, 0); let t = 0;
  return tw.map((w) => { const s = t; t += (w.n + 1) / total * dur; return { c: w.c, n: w.n, s, e: t }; });
}

function doImport() {
  const [code, slug] = rest;
  if (!code || !slug || !flags.dir) die('usage: import <code> <slug> --dir FOLDER [--provider NAME]');
  const np = narrationPath(code, slug);
  if (!fs.existsSync(np)) die(`missing ${path.relative(root, np)}`);
  const n = readJSON(np);
  const rn = resolved(code, slug, n); // same text the export sent to the TTS
  const dir = path.resolve(flags.dir);
  const dest = path.join(root, 'courses', code, 'audio', slug);
  const segs = [];
  rn.segments.forEach((seg, i) => {
    const ext = AUDIO_EXTS.find((x) => fs.existsSync(path.join(dir, nnn(i) + x)));
    if (!ext) die(`segment ${i}: ${nnn(i)}.mp3 not found in ${dir}`);
    const file = nnn(i) + ext, buf = fs.readFileSync(path.join(dir, file));
    const text = spokenText(seg);
    let tim = null;
    const jp = path.join(dir, nnn(i) + '.json');
    if (fs.existsSync(jp)) tim = readJSON(jp);
    let dur = ext === '.mp3' ? mp3Duration(buf) : null;
    let ws = null, kind = 'none';
    if (tim) {
      const A = tim.alignment || tim.normalized_alignment || tim;
      if (Array.isArray(A.characters) && Array.isArray(A.character_start_times_seconds)) {
        kind = 'elevenlabs';
        if (dur == null) dur = Math.max(...A.character_end_times_seconds);
        ws = fromElevenLabs(tim, text, dur);
      } else if (Array.isArray(tim.words) || Array.isArray(tim.segments)) {
        kind = 'whisper';
        const list = tim.words || tim.segments.flatMap((s) => s.words || []);
        if (dur == null) dur = Math.max(...list.map((w) => w.end));
        ws = fromWhisper(list, text);
      } else die(`${jp}: unknown timing format`);
    }
    if (dur == null || !isFinite(dur)) die(`segment ${i}: cannot determine duration of ${file} (provide timings json for non-mp3)`);
    if (ws) { fillGaps(ws, dur); ws = ws.map((w) => ({ s: r3(Math.min(w.s, dur)), e: r3(Math.min(Math.max(w.e, w.s), dur)), c: w.c, n: w.n })); }
    else ws = estimate(text, dur).map((w) => ({ s: r3(w.s), e: r3(w.e), c: w.c, n: w.n }));
    segs.push({ file, entry: { src: file, dur: r3(dur), words: ws } });
    console.log(`  ${file}: ${r3(dur)}s, ${ws.length} words, timings: ${kind}`);
  });
  fs.rmSync(dest, { recursive: true, force: true });
  fs.mkdirSync(dest, { recursive: true });
  for (const s of segs) fs.copyFileSync(path.join(dir, s.file), path.join(dest, s.file));
  n.audio = { provider: flags.provider || (n.audio && n.audio.provider) || 'unknown', segments: segs.map((s) => s.entry) };
  fs.writeFileSync(np, JSON.stringify(n, null, 2) + '\n');
  console.log(`Imported ${segs.length} segments -> ${path.relative(root, dest)}; updated ${path.relative(root, np)}`);
}

function doStats() {
  const codes = rest[0] ? [rest[0]] : allCodes();
  let tc = 0, ts = 0;
  for (const code of codes) {
    for (const slug of listNarrated(code)) {
      const n = resolved(code, slug, readJSON(narrationPath(code, slug)));
      const chars = n.segments.reduce((a, s) => a + [...spokenText(s)].length, 0);
      const audio = !!(n.audio && n.audio.segments && n.audio.segments.length === n.segments.length);
      const real = audio ? n.audio.segments.reduce((a, s) => a + s.dur, 0) : null;
      console.log(`${code}/${slug}: ${n.segments.length} segments, ${chars} chars, ~${(chars / 13 / 60).toFixed(1)} min` + (audio ? ` (audio ${(real / 60).toFixed(1)} min)` : '') + `, audio: ${audio ? 'y' : 'n'}`);
      tc += chars; ts += n.segments.length;
    }
  }
  console.log(`Total: ${ts} segments, ${tc} chars, ~${(tc / 13 / 60).toFixed(1)} min`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  if (cmd === 'export') doExport(); else if (cmd === 'import') doImport(); else if (cmd === 'stats') doStats();
  else die('usage: narration.mjs export|import|stats ...');
}

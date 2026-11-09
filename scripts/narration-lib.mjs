// Shared narration helpers (contract: shibbur-ios/docs/NARRATION.md). No dependencies.
import crypto from 'node:crypto';
import { speak } from './speakmath.mjs';

export const EMOTIONS = ['calm', 'warm', 'curious', 'excited', 'encouraging', 'serious', 'playful', 'emphatic', 'reassuring', 'surprised'];
export const PACES = ['slow', 'normal', 'fast'];
export const AUDIO_EXTS = ['.mp3', '.m4a'];

const isStr = (x) => typeof x === 'string';
const TEX_RE = /\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]/g;

export const lessonHash = (blocks) => crypto.createHash('sha1').update(JSON.stringify(blocks)).digest('hex').slice(0, 8);

// Strings of a block that the student can see, in document order (TeX still inside).
export function blockFields(b) {
  if (!b || typeof b !== 'object') return [];
  const out = [];
  const add = (...xs) => xs.forEach((x) => { if (isStr(x)) out.push(x); });
  switch (b.t) {
    case 'why': case 'p': case 'html': add(b.html); break;
    case 'h': add(b.text); break;
    case 'box': add(b.title, b.html); break;
    case 'figure': add(b.caption); break;
    case 'steps': add(b.caption); (b.frames || []).forEach((f) => f && add(f.caption)); break;
    case 'mistakes': add(b.title); (b.rows || []).forEach((r) => r && add(r.no, r.yes)); break;
    case 'method': add(b.title); (b.steps || []).forEach((s) => add(s)); break;
    case 'xq': add(b.q); (b.steps || []).forEach((s) => s && add(s.label, s.body)); add(b.a); break;
    case 'faq': add(b.title); (b.items || []).forEach((i) => i && add(i.q, i.a)); break;
    case 'card': add(b.front, b.back); break;
    case 'checklist': add(b.title); (b.items || []).forEach((s) => add(s)); add(b.rest); break;
    case 'quiz': if (b.q) { add(b.q.prompt); (b.q.options || []).forEach((o) => o && add(o.html)); add(b.q.hint, b.q.solution); } break;
    default: break;
  }
  return out;
}

export function decodeEntities(s) {
  const named = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
    if (e[0] === '#') {
      const cp = e[1].toLowerCase() === 'x' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      try { return String.fromCodePoint(cp); } catch { return m; }
    }
    return named[e.toLowerCase()] ?? m;
  });
}

const BLOCK_TAG = /<\/?(?:p|br|li|ul|ol|div|tr|td|th|table|pre|details|summary)\b[^>]*>/gi;
export const collapse = (s) => s.replace(/\s+/g, ' ').trim();

// Visible text of a block with TeX removed (replaced by a space), tags stripped, entities decoded.
export function visibleText(b) {
  return collapse(blockFields(b).map((f) => {
    const noTex = f.replace(TEX_RE, ' ');
    return decodeEntities(noTex.replace(BLOCK_TAG, ' ').replace(/<[^>]*>/g, ''));
  }).join(' '));
}

export function texCount(b) {
  let n = b && b.t === 'math' ? 1 : 0;
  for (const f of blockFields(b)) n += (f.match(TEX_RE) || []).length;
  return n;
}

// The TeX strings of a block in the order `math: k` and texCount() number them: a math block's own `tex` first,
// then every \( ... \) / \[ ... \] of its visible fields in document order.
export function blockTex(b) {
  const out = [];
  if (b && b.t === 'math') out.push(isStr(b.tex) ? b.tex : '');
  for (const f of blockFields(b)) for (const m of f.matchAll(TEX_RE)) out.push(m[1] ?? m[2]);
  return out;
}

// A math part reads its formula by code (speakmath) unless it is hand-written AND marked "keep": true.
export const isKept = (p) => p.keep === true && isStr(p.say) && !!p.say.trim();
// Per-lesson reading hints live in course.json: "speakmath": {"lessons": {"<slug>": {"pairs": "interval"}}}
export const speakOptsFor = (course, slug) => ((course && course.speakmath && course.speakmath.lessons && course.speakmath.lessons[slug]) || {});
export function mathReading(p, block, opts) {
  return speak(blockTex(block)[p.math], opts); // throws SpeakMathError
}
export function resolvePart(p, block, opts) {
  if (!p || typeof p !== 'object' || p.math === undefined || isKept(p)) return p;
  return { ...p, say: mathReading(p, block, opts) };
}
// Copy of a narration with every generated math `say` filled in (throws SpeakMathError on a formula it cannot read).
export function resolveNarration(n, lesson, opts) {
  const blocks = lesson.blocks;
  return { ...n, segments: n.segments.map((s) => ({ ...s, say: s.say.map((p) => resolvePart(p, blocks[s.block], opts)) })) };
}

export const partSpoken = (p) => (isStr(p) ? p : p && (isStr(p.say) ? p.say : isStr(p.show) ? p.show : ''));
export const spokenText = (seg) => (seg.say || []).map(partSpoken).join(' ');

// Returns { errors:[], warnings:[] }.
export function validateNarration(n, lesson, where, opts) {
  const errors = [], warnings = [];
  const err = (m) => errors.push(`${where}: ${m}`);
  const warn = (m) => warnings.push(`${where}: ${m}`);
  if (!n || typeof n !== 'object') { err('not an object'); return { errors, warnings }; }
  if (n.v !== 1) err('v must be 1');
  const blocks = lesson.blocks;
  if (n.lessonHash !== undefined && n.lessonHash !== lessonHash(blocks)) warn('WARNING lessonHash differs from the lesson: narration may be stale');
  if (n.voice !== undefined && (typeof n.voice !== 'object' || n.voice === null)) err('voice must be an object');
  if (!Array.isArray(n.segments) || !n.segments.length) { err('segments must be a non-empty array'); return { errors, warnings }; }
  const cache = new Map();
  const info = (bi) => {
    if (!cache.has(bi)) cache.set(bi, { text: visibleText(blocks[bi]), tex: texCount(blocks[bi]) });
    return cache.get(bi);
  };
  n.segments.forEach((s, si) => {
    const W = `segment ${si}`;
    if (!s || typeof s !== 'object') return err(`${W}: not an object`);
    const bi = s.block;
    const blockOk = Number.isInteger(bi) && bi >= 0 && bi < blocks.length;
    if (!blockOk) err(`${W}: block ${JSON.stringify(bi)} out of range (lesson has ${blocks.length} blocks)`);
    if (s.frame !== undefined) {
      if (!blockOk || blocks[bi].t !== 'steps') err(`${W}: frame only allowed on a steps block`);
      else if (!Number.isInteger(s.frame) || s.frame < 1 || s.frame > blocks[bi].frames.length) err(`${W}: frame ${s.frame} must be 1..${blocks[bi].frames.length}`);
    }
    if (s.emotion !== undefined && !EMOTIONS.includes(s.emotion)) err(`${W}: emotion "${s.emotion}" not in ${EMOTIONS.join('|')}`);
    if (s.pace !== undefined && !PACES.includes(s.pace)) err(`${W}: pace "${s.pace}" must be slow|normal|fast`);
    if (s.pause !== undefined && !(typeof s.pause === 'number' && s.pause >= 0 && s.pause <= 3)) err(`${W}: pause must be a number 0..3`);
    if (s.style !== undefined && !isStr(s.style)) err(`${W}: style must be a string`);
    if (!Array.isArray(s.say) || !s.say.length) return err(`${W}: say must be a non-empty array`);
    const generated = new Map();
    s.say.forEach((p, pi) => {
      const P = `${W} part ${pi}`;
      if (isStr(p)) { if (!p.trim()) err(`${P}: empty string`); return; }
      if (!p || typeof p !== 'object') return err(`${P}: must be a string, {show[,say]} or {math,say}`);
      if (p.show !== undefined) {
        if (!isStr(p.show) || !p.show.trim()) err(`${P}: show must be a non-empty string`);
        else if (p.say !== undefined && (!isStr(p.say) || !p.say.trim())) err(`${P}: say must be a non-empty string`);
        else if (blockOk && !info(bi).text.includes(collapse(p.show))) err(`${P}: show "${p.show}" not found in the visible text of block ${bi}`);
      } else if (p.math !== undefined) {
        if (!Number.isInteger(p.math) || p.math < 0) err(`${P}: math must be a non-negative integer`);
        else if (blockOk && p.math >= info(bi).tex) err(`${P}: math ${p.math} but block ${bi} has only ${info(bi).tex} formula(s)`);
        if (p.say !== undefined && (!isStr(p.say) || !p.say.trim())) err(`${P}: say must be a non-empty string`);
        if (p.keep !== undefined && typeof p.keep !== 'boolean') err(`${P}: keep must be true or false`);
        if (p.keep === true && p.say === undefined) warn(`${P}: keep without a hand-written say (the reading is generated)`);
        if (blockOk && Number.isInteger(p.math) && p.math >= 0 && p.math < info(bi).tex && !isKept(p)) {
          try { generated.set(p, mathReading(p, blocks[bi], opts)); } catch (e) { err(`${P}: ${e.message}`); }
        }
      } else err(`${P}: must have show or math`);
    });
    const spokenOf = (p) => (generated.has(p) ? generated.get(p) : partSpoken(p));
    const len = [...s.say.map(spokenOf).join(' ')].length;
    if (len > 600) err(`${W}: spoken text is ${len} chars (max 600)`);
    else if (len > 400) warn(`${W}: spoken text is ${len} chars (over 400, consider splitting)`);
    // a word mixing Arabic and Hebrew letters (الטענה) is unreadable for the TTS
    for (const p of s.say) {
      const txt = isStr(p) ? p : (p && typeof p === 'object' ? [p.show, p.say].filter(isStr).join(' ') : '');
      for (const w of txt.split(/[\s.,،؛:!?؟()«»"'\-–—…]+/)) {
        if (/[֐-׿]/.test(w) && /[؀-ۿ]/.test(w)) err(`${W}: word "${w}" mixes Arabic and Hebrew letters — write the Arabic word and the Hebrew term separately`);
      }
    }
    // a question to the student needs time to think before the answer
    {
      const last = String(s.say.map(spokenOf).join(' ')).trim();
      if (/[؟?]$/.test(last) && !(typeof s.pause === 'number' && s.pause >= 0.8)) warn(`${W}: STYLE ends on a question but pause is ${s.pause ?? 'default'} — give the student ≥ 0.8 s to think before the answer`);
    }
    // listening quality: a segment that mostly re-reads the block's own text adds nothing
    if (blockOk) {
      const norm = (t) => String(t).replace(/[\u064B-\u0652\u0640]/g, '').split(/[^\p{L}\p{N}]+/u).filter((w) => [...w].length >= 3);
      const screen = new Set(norm(info(bi).text));
      const words = norm(s.say.map(spokenOf).join(' '));
      if (words.length >= 5) {
        const on = words.filter((w) => screen.has(w)).length / words.length;
        if (on >= 0.6) warn(`${W}: STYLE ${Math.round(on * 100)}% of its words are already on screen — the voice re-reads the block; say the why, a link, or a warning instead (or cut it)`);
      }
    }
    // listening quality: a formula read symbol by symbol longer than an ear can hold
    for (const p of s.say) {
      if (p && typeof p === 'object' && p.math !== undefined) {
        const words = String(spokenOf(p) || '').trim().split(/\s+/).filter(Boolean).length;
        if (words > 10) warn(`${W}: STYLE formula ${p.math} is read as ${words} words — too long to follow by ear; say what it means in words and read at most its key part`);
      }
    }
  });
  // listening quality: every steps figure is talked through frame by frame
  const narrated = new Map();
  n.segments.forEach((s) => { if (s && Number.isInteger(s.block)) { const f = narrated.get(s.block) || new Set(); f.add(s.frame !== undefined ? s.frame : 1); /* no frame = plays over frame 1 */ narrated.set(s.block, f); } });
  blocks.forEach((b, bi) => {
    if (b.t !== 'steps') return;
    if (!narrated.has(bi)) return warn(`STYLE steps block ${bi} is silent — give each frame its own segment (what changed, why it matters)`);
    const f = narrated.get(bi);
    const missing = b.frames.map((_, i) => i + 1).filter((k) => !f.has(k));
    if (missing.length) warn(`STYLE steps block ${bi}: no segment for frame(s) ${missing.join(', ')}`);
  });
  // rhythm: a long run of the same emotion sounds flat
  { let run = 1, start = 0;
    for (let i = 1; i <= n.segments.length; i++) {
      const a = n.segments[i - 1] && n.segments[i - 1].emotion, b = n.segments[i] && n.segments[i].emotion;
      if (i < n.segments.length && a && a === b) { run++; continue; }
      if (run > 4) warn(`STYLE segments ${start}–${i - 1}: ${run} in a row are "${a}" — vary the emotion (a question, a surprise, a challenge)`);
      run = 1; start = i;
    } }
  const emos = new Set(n.segments.map((s) => s && s.emotion).filter(Boolean));
  if (n.segments.length >= 20 && emos.size < 4) warn(`STYLE only ${emos.size} emotion(s) used — a real tutor varies (curious, surprised, playful, emphatic…)`);
  return { errors, warnings };
}

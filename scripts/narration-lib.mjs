// Shared narration helpers (contract: shibbur-ios/docs/NARRATION.md). No dependencies.
import crypto from 'node:crypto';

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

export const partSpoken = (p) => (isStr(p) ? p : p && (isStr(p.say) ? p.say : isStr(p.show) ? p.show : ''));
export const spokenText = (seg) => (seg.say || []).map(partSpoken).join(' ');

// Returns { errors:[], warnings:[] }.
export function validateNarration(n, lesson, where) {
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
        if (!isStr(p.say) || !p.say.trim()) err(`${P}: math part needs a non-empty say`);
      } else err(`${P}: must have show or math`);
    });
    const len = [...spokenText(s)].length;
    if (len > 600) err(`${W}: spoken text is ${len} chars (max 600)`);
    else if (len > 400) warn(`${W}: spoken text is ${len} chars (over 400, consider splitting)`);
  });
  return { errors, warnings };
}

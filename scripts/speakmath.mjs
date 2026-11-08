// speakmath: exact TeX (KaTeX subset) -> spoken Arabic. No dependencies.
// Contract: docs/SPEAKMATH.md. API: speak(tex, opts) -> string; throws SpeakMathError.
//   node scripts/speakmath.mjs '<tex>'      print the reading
//   node scripts/speakmath.mjs --corpus     read all lessons, write dist-review/speakmath.html, exit 1 on errors
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export class SpeakMathError extends Error {
  constructor(message, tex, token) {
    super(`${message}${token !== undefined ? ` [token: ${token}]` : ''} in formula: ${tex}`);
    this.name = 'SpeakMathError';
    this.tex = tex;
    this.token = token;
  }
}

// ---------------------------------------------------------------- numbers
const ONES = ['صفر', 'واحد', 'اثنين', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة', 'عشرة', 'أحد عشر', 'اثنا عشر',
  'ثلاثة عشر', 'أربعة عشر', 'خمسة عشر', 'ستة عشر', 'سبعة عشر', 'ثمانية عشر', 'تسعة عشر'];
const TENS = { 2: 'عشرين', 3: 'ثلاثين', 4: 'أربعين', 5: 'خمسين', 6: 'ستين', 7: 'سبعين', 8: 'ثمانين', 9: 'تسعين' };
const HUNDREDS = { 1: 'مية', 2: 'ميتين', 3: 'ثلاثمية', 4: 'أربعمية', 5: 'خمسمية', 6: 'ستمية', 7: 'سبعمية', 8: 'ثمانمية', 9: 'تسعمية' };

function below100(n) {
  if (n < 20) return ONES[n];
  const u = n % 10, t = Math.floor(n / 10);
  return u ? `${ONES[u]} و${TENS[t]}` : TENS[t];
}
function below1000(n) {
  const h = Math.floor(n / 100), r = n % 100;
  if (!h) return below100(r);
  return r ? `${HUNDREDS[h]} و${below100(r)}` : HUNDREDS[h];
}
function scaled(n, one, two, few, many) { // n in 1..999 of a scale unit
  if (n === 1) return one;
  if (n === 2) return two;
  if (n <= 10) return `${ONES[n]} ${few}`;
  return `${below1000(n)} ${many}`;
}
export function numberToArabic(n) {
  if (!Number.isInteger(n)) throw new RangeError(`numberToArabic: not an integer: ${n}`);
  if (n < 0) return `سالب ${numberToArabic(-n)}`;
  if (n > 1e9) throw new RangeError(`numberToArabic: out of range: ${n}`);
  if (n < 1000) return below1000(n);
  const parts = [];
  let rest = n;
  const bil = Math.floor(rest / 1e9); rest %= 1e9;
  const mil = Math.floor(rest / 1e6); rest %= 1e6;
  const th = Math.floor(rest / 1000); rest %= 1000;
  if (bil) parts.push(scaled(bil, 'مليار', 'مليارين', 'مليارات', 'مليار'));
  if (mil) parts.push(scaled(mil, 'مليون', 'مليونين', 'ملايين', 'مليون'));
  if (th) parts.push(scaled(th, 'ألف', 'ألفين', 'آلاف', 'ألف'));
  if (rest) parts.push(below1000(rest));
  return parts.map((p, i) => (i ? `و${p}` : p)).join(' ');
}
// "12" -> words; "3.14" -> "ثلاثة نقطة واحد أربعة" (digits one by one after the point)
export function numberStringToArabic(s) {
  const [ip, fp] = s.split('.');
  const iw = ip.length > 1 && ip[0] === '0' ? [...ip].map((d) => ONES[Number(d)]).join(' ') : numberToArabic(Number(ip));
  if (fp === undefined) return iw;
  return `${iw} نقطة ${[...fp].map((d) => ONES[Number(d)]).join(' ')}`;
}

// ---------------------------------------------------------------- vocabulary
const LETTERS = {
  a: 'إيه', b: 'بي', c: 'سي', d: 'دي', e: 'إي', f: 'إف', g: 'جي', h: 'إتش', i: 'آي', j: 'جاي', k: 'كيه', l: 'إل', m: 'إم',
  n: 'إن', o: 'أو', p: 'پي', q: 'كيو', r: 'آر', s: 'إس', t: 'تي', u: 'يو', v: 'ڤي', w: 'دبليو', x: 'إكس', y: 'واي', z: 'زِد',
};
const GREEK = {
  alpha: 'ألفا', beta: 'بيتا', gamma: 'غاما', delta: 'دلتا', epsilon: 'إبسيلون', varepsilon: 'إبسيلون', theta: 'ثيتا', vartheta: 'ثيتا',
  lambda: 'لامدا', mu: 'ميو', pi: 'باي', rho: 'رو', sigma: 'سيغما', tau: 'تاو', phi: 'فاي', varphi: 'فاي', omega: 'أوميغا',
  Delta: 'دلتا كبيرة', Sigma: 'سيغما كبيرة',
};
const MATHBB = { R: ['الأعداد الحقيقية', 'آر'], Q: ['الأعداد النسبية', 'كيو'], Z: ['الأعداد الصحيحة', 'زِد'], N: ['الأعداد الطبيعية', 'إن'],
  C: ['الأعداد المركّبة', 'سي'], I: ['الأعداد غير النسبية', 'آي'] };
// function words: [word, link]; link is said between the name and its argument (when there is one)
const FNS = {
  sin: ['سينوس', ''], cos: ['كوسينوس', ''], tan: ['تانجنس', ''], cot: ['كوتانجنس', ''],
  arcsin: ['أركسينوس', ''], arccos: ['أركوسينوس', ''], arctan: ['أركتانجنس', ''], arccot: ['أركوتانجنس', ''],
  ln: ['لن', ''], log: ['لوغ', ''], cis: ['سيس', ''],
  Re: ['الجزء الحقيقي', 'من'], Im: ['الجزء التخيلي', 'من'], ImImage: ['الصورة', 'تبع'], arg: ['الأرغومنت', 'تبع'],
  sup: ['السوبريموم', 'تبع'], inf: ['الإنفيموم', 'تبع'], max: ['الماكسيموم', 'تبع'], min: ['المينيموم', 'تبع'],
  lim: ['النهاية', ''], sum: ['المجموع', ''], int: ['التكامل', ''], Id: ['آي دي', ''],
};
const LETTER_FN = new Set(['f', 'g', 'h', 'F', 'G', 'H', 'U']);
const NOT_APP = new Set(['lim', 'sum', 'int', 'sup', 'inf', 'max', 'min']);
const ORD = ['', 'الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس', 'السادس', 'السابع', 'الثامن', 'التاسع', 'العاشر'];
const UNIT_FRAC = { '1/2': 'نص', '1/3': 'ثلث', '1/4': 'ربع', '1/5': 'خمس', '1/6': 'سدس', '1/7': 'سبع', '1/8': 'ثمن', '1/9': 'تسع', '1/10': 'عشر',
  '2/3': 'ثلثين', '3/4': 'ثلاث أرباع' };
const G = ''; // glue: attach to the next word without a space
const lam = (s) => (s ? `ل${G}${s}` : s);
const wa = (s) => (s ? `و${G}${s}` : s);

const REL = {
  '=': 'بيساوي', ne: 'مش بيساوي', '<': 'أصغر من', '>': 'أكبر من', le: 'أصغر أو بيساوي', ge: 'أكبر أو بيساوي', approx: 'تقريباً بيساوي',
  in: `بينتمي ل${G}`, notin: `ما بينتمي ل${G}`, subseteq: 'مجموعة جزئية من', Rightarrow: 'يعني', iff: 'إذا وفقط إذا',
  perp: 'متعامد مع', parallel: `موازي ل${G}`, to: `بتروح ل${G}`, ':=': 'بيساوي بالتعريف',
};
const REL_CMD = { ne: 'ne', neq: 'ne', le: 'le', leq: 'le', ge: 'ge', geq: 'ge', lt: '<', gt: '>', approx: 'approx', in: 'in', notin: 'notin',
  subseteq: 'subseteq', subset: 'subseteq', Rightarrow: 'Rightarrow', implies: 'Rightarrow', iff: 'iff', Leftrightarrow: 'iff',
  perp: 'perp', parallel: 'parallel', to: 'to' };
const OP_CMD = { cdot: 'cdot', times: 'times', pm: '±', cup: 'cup', cap: 'cap', setminus: 'setminus', circ: 'circ' };
const GREEK_SET = new Set(Object.keys(GREEK));
const SPACE_CMD = new Set([' ', ',', ';', '!', ':', '>']);
const SIZE_CMD = new Set(['left', 'right', 'big', 'Big', 'bigg', 'Bigg', 'bigl', 'bigr', 'Bigl', 'Bigr', 'biggl', 'biggr', 'Biggl', 'Biggr']);
const DELIM_CMD = { '{': '{', '}': '}', '|': '||', langle: 'langle', rangle: 'rangle', lbrace: '{', rbrace: '}', vert: '|', Vert: '||',
  lvert: '|', rvert: '|', lVert: '||', rVert: '||' };
const DELIM_CHAR = { '(': '(', ')': ')', '[': '[', ']': ']', '|': '|' };
const ENVS = new Set(['pmatrix', 'vmatrix', 'cases']);
const OPERAND = new Set(['num', 'var', 'greek', 'sym', 'accent', 'frac', 'sqrt', 'delim', 'script', 'brace', 'mathbb', 'letters', 'app', 'matrix', 'text', 'fn']);

// ---------------------------------------------------------------- tokenizer
function decodeEntities(s) {
  return s.replace(/&(lt|gt|amp|quot|nbsp);/g, (m, e) => ({ lt: '<', gt: '>', amp: '&', quot: '"', nbsp: ' ' }[e]));
}

function tokenize(src, tex) {
  const toks = [];
  let i = 0;
  const fail = (m, t) => { throw new SpeakMathError(m, tex, t); };
  const readCmd = () => { // at src[i] === '\\'
    const m = /^\\([A-Za-z]+|[\s\S])/.exec(src.slice(i));
    if (!m) fail('dangling backslash', '\\');
    return { name: m[1], len: m[0].length };
  };
  const delimOf = (c) => {
    if (c.k === 'char' && DELIM_CHAR[c.v]) return DELIM_CHAR[c.v];
    if (c.k === 'cmd' && DELIM_CMD[c.v]) return DELIM_CMD[c.v];
    return null;
  };
  const rawTok = () => { // read one raw token at i (no size handling)
    const c = src[i];
    if (c === '\\') {
      const { name, len } = readCmd();
      const t = { k: 'cmd', v: name, pos: i, end: i + len };
      i += len; return t;
    }
    const t = { k: 'char', v: c, pos: i, end: i + 1 };
    i++; return t;
  };
  while (i < src.length) {
    const c = src[i];
    if (/\s/.test(c)) { i++; continue; }
    const t = rawTok();
    if (t.k === 'cmd' && ['text', 'mbox', 'mathrm', 'operatorname'].includes(t.v)) {
      let j = i;
      while (j < src.length && /\s/.test(src[j])) j++;
      if (src[j] === '{') {
        let depth = 0, e = j;
        for (; e < src.length; e++) { if (src[e] === '{') depth++; else if (src[e] === '}' && --depth === 0) break; }
        if (depth) fail('unbalanced braces', '{');
        toks.push(t, { k: 'lbrace', v: '{', pos: j, end: j + 1 }, { k: 'raw', v: src.slice(j + 1, e), pos: j + 1, end: e }, { k: 'rbrace', v: '}', pos: e, end: e + 1 });
        i = e + 1; continue;
      }
    }
    if (t.k === 'cmd' && SIZE_CMD.has(t.v) || t.k === 'cmd' && t.v === 'middle') {
      while (i < src.length && /\s/.test(src[i])) i++;
      if (i >= src.length) fail('missing delimiter after \\' + t.v, '\\' + t.v);
      const d = rawTok();
      if (t.v === 'middle') {
        if (d.v === '|' && d.k === 'char') { toks.push({ k: 'mid', v: '|', pos: t.pos, end: d.end }); continue; }
        fail('unsupported \\middle delimiter', `\\middle${d.k === 'cmd' ? '\\' : ''}${d.v}`);
      }
      const dv = delimOf(d);
      if (!dv) fail(`unsupported delimiter after \\${t.v}`, `${d.k === 'cmd' ? '\\' : ''}${d.v}`);
      toks.push({ k: 'delim', v: dv, pos: t.pos, end: d.end, sized: true }); continue;
    }
    if (t.k === 'char' && t.v === '{') { toks.push({ ...t, k: 'lbrace' }); continue; }
    if (t.k === 'char' && t.v === '}') { toks.push({ ...t, k: 'rbrace' }); continue; }
    const dv = delimOf(t);
    if (dv) { toks.push({ k: 'delim', v: dv, pos: t.pos, end: t.end }); continue; }
    if (t.k === 'char' && /[0-9]/.test(t.v)) { toks.push({ ...t, k: 'digit' }); continue; }
    if (t.k === 'char' && /[A-Za-z]/.test(t.v)) { toks.push({ ...t, k: 'letter' }); continue; }
    if (t.k === 'char' && /[^\x00-\x7f]/.test(t.v)) fail('non-ASCII character outside \\text', t.v);
    toks.push(t);
  }
  return toks;
}

// ---------------------------------------------------------------- parser
class Parser {
  constructor(src, tex) { this.src = src; this.tex = tex; this.toks = tokenize(src, tex); this.p = 0; }
  fail(m, t) { throw new SpeakMathError(m, this.tex, t); }
  peek(o = 0) { return this.toks[this.p + o]; }
  next() { return this.toks[this.p++]; }
  show(t) { return t ? `${t.k === 'cmd' ? '\\' : ''}${t.v}` : 'end of input'; }
  expect(pred, what) {
    const t = this.next();
    if (!t || !pred(t)) this.fail(`expected ${what}`, this.show(t));
    return t;
  }
  parseAll() {
    const items = this.parseRow(() => false);
    if (this.p < this.toks.length) this.fail('unexpected token', this.show(this.peek()));
    return items;
  }
  // parse items until stop(tok, items) is true (token is not consumed) or the input ends
  parseRow(stop, kind) {
    const items = [];
    for (;;) {
      const t = this.peek();
      if (!t || stop(t, items)) break;
      const it = this.parseItem(false, items, kind);
      if (it === null) continue;
      items.push(this.finishOperand(it));
    }
    return items;
  }
  // scripts + function application after an operand
  finishOperand(it) {
    if (!OPERAND.has(it.t)) return it;
    let cur = this.scripts(it);
    const t = this.peek();
    if (t && t.k === 'delim' && t.v === '(' && this.isFunctionish(cur)) {
      this.next();
      const body = this.parseDelimBody('(');
      cur = this.scripts({ t: 'app', fn: cur, arg: body });
    }
    return cur;
  }
  scripts(it) {
    let cur = it;
    for (;;) {
      const t = this.peek();
      if (!(t && t.k === 'char' && (t.v === '^' || t.v === '_'))) return cur;
      this.next();
      const arg = this.parseArg();
      const key = t.v === '^' ? 'sup' : 'sub';
      if (cur.t === 'script') {
        if (cur[key]) this.fail(`double ${key === 'sup' ? 'superscript' : 'subscript'}`, t.v);
        cur[key] = arg;
      } else cur = { t: 'script', base: cur, sub: null, sup: null, [key]: arg };
    }
  }
  isFunctionish(a) {
    const base = a.t === 'script' ? a.base : a;
    if (base.t === 'fn') return !NOT_APP.has(base.name);
    if (base.t === 'var') return LETTER_FN.has(base.v);
    if (a.t === 'delim' && a.open === '(') return hasFnLetter(a.items) && !a.items.some((x) => x.t === 'comma' || x.t === 'rel');
    return false;
  }
  parseArg() {
    const t = this.peek();
    if (!t) this.fail('missing argument', 'end of input');
    if (t.k === 'lbrace') {
      this.next();
      const items = this.parseRow((x) => x.k === 'rbrace');
      this.expect((x) => x.k === 'rbrace', '}');
      return items;
    }
    const it = this.parseItem(true, []);
    if (it === null) this.fail('missing argument', this.show(this.peek()));
    return [it];
  }
  rawBraceText() { // after a command: { raw text }
    const open = this.expect((x) => x.k === 'lbrace', '{');
    let depth = 1, j = this.p;
    for (; j < this.toks.length; j++) {
      if (this.toks[j].k === 'lbrace') depth++;
      else if (this.toks[j].k === 'rbrace' && --depth === 0) break;
    }
    if (depth) this.fail('unbalanced braces', '{');
    const text = this.src.slice(open.end, this.toks[j].pos);
    this.p = j + 1;
    return text;
  }
  parseDelimBody(open) {
    const closers = open === '(' || open === '[' ? [')', ']'] : [{ '{': '}', langle: 'rangle', '||': '||', '|': '|' }[open]];
    const stop = (t, items) => {
      if (t.k !== 'delim' || !closers.includes(t.v)) return false;
      if (open === '|') return canClose(items);
      return true;
    };
    const items = this.parseRow(stop, open === '{' ? 'set' : '');
    const c = this.next();
    if (!c || c.k !== 'delim' || !closers.includes(c.v)) this.fail(`unclosed ${open}`, this.show(c));
    return { t: 'delim', open, close: c.v, items };
  }
  parseItem(single, soFar, kind) {
    const t = this.next();
    switch (t.k) {
      case 'digit': {
        let s = t.v;
        if (!single) {
          while (this.peek() && this.peek().k === 'digit') s += this.next().v;
          const a = this.peek(), b = this.peek(1);
          if (a && a.k === 'char' && a.v === '.' && b && b.k === 'digit') {
            this.next(); s += '.';
            while (this.peek() && this.peek().k === 'digit') s += this.next().v;
          }
        }
        return { t: 'num', v: s };
      }
      case 'letter': {
        const n = this.peek();
        if (t.v === 'I' && n && n.k === 'letter' && n.v === 'd' && !(this.peek(1) && this.peek(1).k === 'letter')) {
          this.next(); return { t: 'fn', name: 'Id' };
        }
        return { t: 'var', v: t.v };
      }
      case 'lbrace': {
        const items = this.parseRow((x) => x.k === 'rbrace');
        this.expect((x) => x.k === 'rbrace', '}');
        return { t: 'brace', items };
      }
      case 'rbrace': this.fail('unmatched }', '}'); break;
      case 'delim': {
        if (t.v === ')' || t.v === ']' || t.v === '}' || t.v === 'rangle') this.fail('unmatched closing delimiter', t.v);
        if (t.v === '|' && kind === 'set' && canClose(soFar)) return { t: 'mid' };
        return this.parseDelimBody(t.v);
      }
      case 'mid': return { t: 'mid' };
      case 'char': return this.parseChar(t, single, soFar);
      case 'cmd': return this.parseCmd(t, single);
      default: this.fail('unexpected token', this.show(t));
    }
    return null;
  }
  parseChar(t, single) {
    const v = t.v;
    if (v === '+' || v === '-' || v === '*' || v === '/') return { t: 'op', v };
    if (v === '=') return { t: 'rel', v: '=' };
    if (v === '<' || v === '>') return { t: 'rel', v };
    if (v === ',') return { t: 'comma' };
    if (v === ';') return { t: 'semi' };
    if (v === ':') {
      const n = this.peek();
      if (!single && n && n.k === 'char' && n.v === '=') { this.next(); return { t: 'rel', v: ':=' }; }
      return { t: 'colon' };
    }
    if (v === '.') {
      const n = this.peek();
      if (!single && n && n.k === 'char' && n.v === '.') { this.next(); return { t: 'dots2' }; }
      return { t: 'punct' };
    }
    if (v === '?') return { t: 'sym', v: 'unknown' };
    if (v === '&') this.fail('& outside a matrix environment', '&');
    return this.fail('unknown character', v);
  }
  parseCmd(t, single) {
    const n = t.v;
    if (SPACE_CMD.has(n)) return { t: 'space' };
    if (n === 'quad' || n === 'qquad') return { t: 'quad' };
    if (n === '\\') this.fail('\\\\ outside an environment', '\\\\');
    if (GREEK_SET.has(n)) return { t: 'greek', v: n };
    if (REL_CMD[n]) return { t: 'rel', v: REL_CMD[n] };
    if (OP_CMD[n]) return { t: 'op', v: OP_CMD[n] };
    if (n === 'mid') return { t: 'mid' };
    if (n === 'dots' || n === 'ldots' || n === 'cdots') return { t: 'dots' };
    if (n === 'infty' || n === 'emptyset') return { t: 'sym', v: n };
    if (n === 'blacksquare' || n === 'square') return { t: 'qed' };
    if (n === 'forall' || n === 'exists') return { t: 'quant', v: n };
    if (['sin', 'cos', 'tan', 'cot', 'arcsin', 'arccos', 'arctan', 'ln', 'log', 'lim', 'sum', 'int', 'sup', 'inf', 'max', 'min', 'arg'].includes(n)) return { t: 'fn', name: n };
    if (n === 'text' || n === 'mbox') return { t: 'text', s: this.rawBraceText() };
    if (n === 'mathrm' || n === 'operatorname') {
      const s = this.rawBraceText().trim();
      if (n === 'operatorname' && s === 'Im') return { t: 'fn', name: 'ImImage' };
      if (n === 'mathrm' && (s === 'Re' || s === 'Im' || s === 'cis')) return { t: 'fn', name: s };
      if (s === 'arccot') return { t: 'fn', name: 'arccot' };
      if (!/^[A-Za-z]+$/.test(s)) this.fail('unsupported \\' + n + ' content', s);
      return { t: 'letters', v: s };
    }
    if (n === 'mathbb') {
      const arg = this.parseArg();
      const v = arg.length === 1 && (arg[0].t === 'var') ? arg[0].v : null;
      if (!v || !MATHBB[v]) this.fail('unsupported \\mathbb letter', v || '?');
      return { t: 'mathbb', v };
    }
    if (n === 'vec' || n === 'overrightarrow' || n === 'overline' || n === 'hat' || n === 'tilde') {
      return { t: 'accent', kind: n, body: this.parseArg() };
    }
    if (n === 'frac' || n === 'tfrac' || n === 'dfrac') {
      const num = this.parseArg(), den = this.parseArg();
      return { t: 'frac', num, den };
    }
    if (n === 'sqrt') {
      let index = null;
      const a = this.peek();
      if (a && a.k === 'delim' && a.v === '[') {
        this.next();
        index = this.parseRow((x) => x.k === 'delim' && x.v === ']');
        this.expect((x) => x.k === 'delim' && x.v === ']', ']');
      }
      return { t: 'sqrt', index, body: this.parseArg() };
    }
    if (n === 'begin') return this.parseEnv();
    if (n === 'end') this.fail('\\end without \\begin', '\\end');
    return this.fail('unknown command', '\\' + n);
  }
  envName() {
    this.expect((x) => x.k === 'lbrace', '{');
    let s = '';
    while (this.peek() && this.peek().k === 'letter') s += this.next().v;
    this.expect((x) => x.k === 'rbrace', '}');
    return s;
  }
  parseEnv() {
    const name = this.envName();
    if (!ENVS.has(name)) this.fail('unsupported environment', name);
    const rows = [[]];
    let cell = [];
    const stop = (t) => (t.k === 'char' && t.v === '&') || (t.k === 'cmd' && (t.v === '\\' || t.v === 'end'));
    for (;;) {
      const items = this.parseRow(stop);
      const t = this.next();
      if (!t) this.fail(`unterminated environment ${name}`, name);
      cell = items;
      rows[rows.length - 1].push(cell);
      if (t.k === 'char') continue; // &
      if (t.v === '\\') { rows.push([]); continue; }
      const en = this.envName();
      if (en !== name) this.fail(`\\end{${en}} does not match \\begin{${name}}`, en);
      break;
    }
    const last = rows[rows.length - 1];
    if (last.length === 1 && last[0].filter((x) => x.t !== 'space').length === 0) rows.pop();
    return { t: 'matrix', env: name, rows };
  }
}

function canClose(items) {
  for (let i = items.length - 1; i >= 0; i--) {
    if (items[i].t === 'space') continue;
    return OPERAND.has(items[i].t) && items[i].t !== 'fn';
  }
  return false;
}
function walk(items, f) { // visit every item (deep)
  for (const x of items) {
    if (!x) continue;
    f(x);
    switch (x.t) {
      case 'script': walk([x.base], f); if (x.sub) walk(x.sub, f); if (x.sup) walk(x.sup, f); break;
      case 'frac': walk(x.num, f); walk(x.den, f); break;
      case 'sqrt': if (x.index) walk(x.index, f); walk(x.body, f); break;
      case 'delim': case 'brace': walk(x.items, f); break;
      case 'accent': walk(x.body, f); break;
      case 'app': walk([x.fn], f); walk([x.arg], f); break;
      case 'matrix': x.rows.forEach((r) => r.forEach((c) => walk(c, f))); break;
      default: break;
    }
  }
}
function hasFnLetter(items) {
  let found = false;
  walk(items, (x) => { if (x.t === 'var' && LETTER_FN.has(x.v)) found = true; });
  return found;
}

// ---------------------------------------------------------------- analysis helpers
const clean = (items) => items.filter((x) => x.t !== 'space');
const isNum = (it, v) => it && it.t === 'num' && (v === undefined || it.v === v);
const baseOf = (x) => (x && x.t === 'script' ? baseOf(x.base) : x);
const isAbs = (x) => { const b = baseOf(x); return b && b.t === 'delim' && (b.open === '|' || b.open === '||'); };
const splitTop = (items, pred) => {
  const parts = [[]];
  for (const x of items) { if (pred(x)) parts.push([]); else parts[parts.length - 1].push(x); }
  return parts;
};
const isInfty = (items) => { const c = clean(items); return c.some((x) => x.t === 'sym' && x.v === 'infty'); };

// classification of a row: atom | scripted | unit | frac | product | sum
function cls(items) {
  const c = clean(items);
  if (!c.length) return 'atom';
  if (c.some((x) => ['rel', 'comma', 'semi', 'colon', 'mid', 'quad', 'dots', 'dots2', 'qed', 'quant'].includes(x.t))) return 'sum';
  let operands = 0, prodOp = false;
  let first = null;
  for (let i = 0; i < c.length; i++) {
    const x = c[i];
    if (x.t === 'op') {
      const unaryLead = i === 0 && (x.v === '-' || x.v === '+');
      if (unaryLead) continue;
      if (['+', '-', '±', 'cup', 'cap', 'setminus'].includes(x.v)) return 'sum';
      prodOp = true;
      continue;
    }
    operands++;
    if (!first) first = x;
  }
  if (prodOp || operands > 1) return 'product';
  return clsNode(first);
}
function clsNode(x) {
  switch (x.t) {
    case 'num': case 'var': case 'greek': case 'sym': case 'mathbb': case 'letters': case 'text': case 'fn': return 'atom';
    case 'accent': return cls(x.body) === 'atom' ? 'atom' : 'unit';
    case 'script': return clsNode(x.base) === 'atom' ? 'scripted' : 'unit';
    case 'frac': return 'frac';
    case 'brace': return cls(x.items);
    default: return 'unit';
  }
}
const isSimple = (c) => c === 'atom' || c === 'scripted';

function containsVec(items) {
  let r = false;
  const rec = (arr) => {
    for (const x of arr) {
      if (!x) continue;
      if (x.t === 'accent' && ['vec', 'overrightarrow', 'hat'].includes(x.kind)) r = true;
      else if (x.t === 'matrix' && x.env === 'pmatrix' && x.rows.every((row) => row.length === 1)) r = true;
      else if (x.t === 'delim' && (x.open === '|' || x.open === '||')) continue;
      else if (x.t === 'script') { rec([x.base]); }
      else if (x.t === 'frac') { rec(x.num); rec(x.den); }
      else if (x.t === 'delim' || x.t === 'brace') rec(x.items);
      else if (x.t === 'accent') rec(x.body);
    }
  };
  rec(items);
  return r;
}

// a "vector operand" (for \cdot and \times)
function isVecOperand(x) {
  if (!x) return false;
  switch (x.t) {
    case 'accent': return ['vec', 'overrightarrow', 'hat'].includes(x.kind);
    case 'script': return isVecOperand(x.base);
    case 'matrix': return x.env === 'pmatrix' && x.rows.every((row) => row.length === 1) && x.rows.length >= 1;
    case 'delim': {
      if (x.open !== '(' && x.open !== '[') return false;
      const parts = splitTop(clean(x.items), (y) => y.t === 'comma');
      if (parts.length >= 2) return !x.interval;
      return clean(x.items).some((y) => isVecOperand(y));
    }
    case 'brace': return clean(x.items).some((y) => isVecOperand(y));
    default: return false;
  }
}

function annotate(it, ctx) { // mark intervals / tuple modes on delim nodes of one row
  const c = it;
  const roundPair = (x) => x.t === 'delim' && x.open === '(' && x.close === ')' && splitTop(clean(x.items), (y) => y.t === 'comma').length === 2;
  const isSetish = (seg) => seg.some((x) => {
    if (x.t === 'mathbb') return true;
    if (x.t === 'delim' && (x.open === '{' || x.open === '[')) return true;
    if (x.t === 'delim' && x.interval) return true;
    if (x.t === 'script' && x.base.t === 'delim' && x.base.open === '{') return true;
    if (x.t === 'op' && ['cup', 'cap', 'setminus'].includes(x.v)) return true;
    if (x.t === 'app' && baseOf(x.fn).t === 'var' && baseOf(x.fn).v === 'U') return true;
    return false;
  }) || (seg.length === 1 && seg[0].t === 'var' && /[A-Z]/.test(seg[0].v) && !'PQROMN'.includes(seg[0].v))
    || (seg.length === 1 && seg[0].t === 'script' && baseOf(seg[0]).t === 'var' && /[A-Z]/.test(baseOf(seg[0]).v) && !'PQROMN'.includes(baseOf(seg[0]).v) && seg[0].base.t === 'var' && seg[0].sub && !seg[0].sub.some((y) => y.t === 'num'));
  c.forEach((x, i) => {
    if (x.t !== 'delim' || (x.open !== '(' && x.open !== '[')) return;
    const parts = splitTop(clean(x.items), (y) => y.t === 'comma');
    if (parts.length === 2 && (x.open !== x.close || x.open === '[' || x.close === ']' ) && !((x.open === '(') && (x.close === ')'))) x.interval = true;
    if (parts.length === 2 && x.open === '(' && x.close === ')') {
      const p = c[i - 1], n = c[i + 1];
      if (parts.some((q) => isInfty(q))) x.interval = true;
      if (p && ((p.t === 'rel' && ['in', 'notin', 'subseteq'].includes(p.v)) || (p.t === 'op' && ['cup', 'cap', 'setminus'].includes(p.v)) || (p.t === 'fn' && ['sup', 'inf', 'max', 'min'].includes(p.name)))) x.interval = true;
      if (n && n.t === 'op' && ['cup', 'cap', 'setminus'].includes(n.v)) x.interval = true;
    }
  });
  // pairs of numbers/symbols with a π end are intervals; with {pairs:'interval'} every pair is, except ordered pairs
  // inside a set, points of a function (x,f(x)) and the two sides of a bare arrow (0,1)->(1,0)
  const arrowNoColon = c.findIndex((x) => x.t === 'rel' && x.v === 'to') >= 0 && !c.some((x) => x.t === 'colon');
  c.forEach((x, i) => {
    if (!roundPair(x) || x.noInterval) return;
    const parts = splitTop(clean(x.items), (y) => y.t === 'comma');
    let pi = false, app = false;
    walk(x.items, (y) => { if (y.t === 'greek' && y.v === 'pi') pi = true; if (y.t === 'app') app = true; });
    const nearArrow = (c[i - 1] && c[i - 1].t === 'rel' && c[i - 1].v === 'to') || (c[i + 1] && c[i + 1].t === 'rel' && c[i + 1].v === 'to');
    if (pi) x.interval = true;
    else if (ctx.pairs === 'interval' && !app && !(arrowNoColon && nearArrow)) x.interval = true;
    void parts;
  });
  // function domain context: ... : D \to C
  const colon = c.findIndex((x) => x.t === 'colon');
  const arrow = c.findIndex((x) => x.t === 'rel' && x.v === 'to');
  if (colon >= 0 && arrow > colon) {
    c.forEach((x, i) => {
      if (roundPair(x) && (c[i - 1] && (c[i - 1].t === 'colon' || (c[i - 1].t === 'rel' && c[i - 1].v === 'to')))) x.interval = true;
    });
  }
  // '=' chains
  for (let pass = 0; pass < 2; pass++) {
    const segs = splitTop(c, (x) => x.t === 'rel' && x.v === '=');
    if (segs.length > 1) {
      segs.forEach((seg, si) => {
        const others = segs.filter((_, j) => j !== si);
        if (others.some((o) => isSetish(o))) seg.forEach((x) => { if (roundPair(x)) x.interval = true; });
      });
    }
  }
}
function tupleMode(x, i, it, ctx) {
  const p = it[i - 1], n = it[i + 1];
  const opAdj = (y) => y && y.t === 'op' && ['+', '-', 'cdot', 'times'].includes(y.v);
  if (ctx.hasVec) return 'vec';
  if (p && OPERAND.has(p.t) && p.t !== 'fn') return 'vec';
  if (opAdj(p) || opAdj(n)) return 'vec';
  if (it.some((y) => y.t === 'delim' && y !== x && y.open === '(' && !y.interval && splitTop(clean(y.items), (z) => z.t === 'comma').length >= 2 && y !== x)
    && it.some((y) => y.t === 'op' && y.v === '+')) return 'vec';
  if (it.some((y) => (y.t === 'var' && /[A-Z]/.test(y.v)) || (y.t === 'script' && y.base.t === 'var' && /[A-Z]/.test(y.base.v)))) return 'point';
  return 'plain';
}

// ---------------------------------------------------------------- verbalizer
function sayNum(s) { return numberStringToArabic(s); }

function Ctx(tex, ast, opts) {
  const lower = new Set(), upper = new Set();
  let hasVec = false;
  walk(ast, (x) => {
    if (x.t === 'var') (x.v === x.v.toLowerCase() ? lower : upper).add(x.v.toLowerCase());
    if (x.t === 'accent' && ['vec', 'overrightarrow', 'hat'].includes(x.kind)) hasVec = true;
    if (x.t === 'matrix' && x.env === 'pmatrix' && x.rows.every((row) => row.length === 1)) hasVec = true;
  });
  const clash = new Set([...lower].filter((l) => upper.has(l)));
  return { tex, clash, hasVec: hasVec || !!(opts && opts.vector), pairs: opts && opts.pairs, depth: 0 };
}

function fail(ctx, m, t) { throw new SpeakMathError(m, ctx.tex, t); }

function sayVar(x, ctx) {
  const lower = x.v.toLowerCase();
  const name = LETTERS[lower];
  return x.v !== lower && ctx.clash.has(lower) ? `${name} كبيرة` : name;
}

function sayItems(items, ctx) { return sayRow(items, ctx); }

// reading of a row that is an argument of a construct ("compound" handling is done by the caller)
function sayRow(items, ctx) {
  const it = clean(items).filter((y, k, a) => !(y.t === 'quad' && a[k + 1] && a[k + 1].t === 'quad'));
  annotate(it, ctx);
  const out = [];
  const push = (s) => { if (s) out.push(s); };
  for (let i = 0; i < it.length; i++) {
    const x = it[i];
    const prev = it[i - 1], nx = it[i + 1];
    const unary = !prev || ['op', 'rel', 'comma', 'semi', 'colon', 'mid', 'quad', 'quant'].includes(prev.t);
    switch (x.t) {
      case 'op': {
        if (x.v === '+') push('زائد');
        else if (x.v === '-') push(unary ? 'سالب' : 'ناقص');
        else if (x.v === '±') push('زائد ناقص');
        else if (x.v === 'cdot' || x.v === 'times') {
          let r = it[i + 1], ri = i + 1;
          if (r && r.t === 'op' && r.v === '-') { r = it[i + 2]; ri = i + 2; }
          const vec = isVecOperand(prev) && isVecOperand(r);
          push(x.v === 'cdot' ? (vec ? 'نقطة' : 'ضرب') : (vec ? 'ضرب متجهي' : 'ضرب'));
        } else if (x.v === 'circ') push('تركيب');
        else if (x.v === '/') push('على');
        else if (x.v === 'cup') push('اتحاد');
        else if (x.v === 'cap') push('تقاطع');
        else if (x.v === 'setminus') push('ناقص');
        else if (x.v === '*') push('نجمة');
        else fail(ctx, 'unsupported operator', x.v);
        break;
      }
      case 'rel': push(REL[x.v]); break;
      case 'comma': case 'semi': push('،'); break;
      case 'colon': {
        const later = it.slice(i + 1).some((y) => y.t === 'rel' && y.v === 'to');
        push(later ? 'من' : '؛');
        break;
      }
      case 'mid': fail(ctx, '\\mid outside a set', '\\mid'); break;
      case 'punct': if (i !== it.length - 1 && !(nx && nx.t === 'quad')) fail(ctx, 'stray period', '.'); break;
      case 'dots': push('وهيك'); break;
      case 'dots2': push('لحد'); break;
      case 'qed': push('، وهيك خلصنا البرهان'); break;
      case 'quad': {
        if (!prev || !nx) break;
        const arrowish = (y) => y && ((y.t === 'rel' && ['Rightarrow', 'iff', 'to'].includes(y.v)) || y.t === 'text' || y.t === 'qed');
        if (prev.t === 'comma') push(nx.t === 'text' ? '' : 'و');
        else if (arrowish(prev) || arrowish(nx)) push('،');
        else push('، و');
        break;
      }
      case 'quant': push(x.v === 'forall' ? 'لكل' : 'في'); break;
      default: {
        // operand
        const bx = baseOf(x);
        // big operators capture a body
        if (bx.t === 'fn' && ['lim', 'sum', 'int'].includes(bx.name)) {
          const stopAdd = bx.name !== 'int';
          let j = i + 1;
          const body = [];
          for (; j < it.length; j++) {
            const y = it[j];
            if (['rel', 'comma', 'semi', 'colon', 'mid', 'quad', 'qed'].includes(y.t)) break;
            if (stopAdd && y.t === 'op' && ['+', '-', '±'].includes(y.v) && body.length) break;
            body.push(y);
          }
          if (prev && OPERAND.has(prev.t) && prev.t !== 'fn') push(isAbs(prev) ? 'ضرب' : '');
          push(sayBigOp(x, body, ctx));
          i = j - 1;
          break;
        }
        if (prev && OPERAND.has(prev.t) && prev.t !== 'fn') {
          if (isAbs(prev) || isAbs(x)) push('ضرب');
          else if (needsClose(prev)) push('،');
        }
        let piece = sayOperand(x, ctx, nx, it, i);
        const pb = baseOf(prev);
        if (x.t === 'frac' && pb && pb.t === 'fn' && !FNS[pb.name][1] && !unitFrac(x)) piece = `القوس ${piece}،`; // sin pi/4 -> sin (pi over 4)
        push(piece);
        if (needsAfter(x, nx)) push('،');
      }
    }
  }
  return out.join(' ');
}

function needsClose(prev) {
  const b = prev;
  if (b.t === 'sqrt') return true;
  if (b.t === 'frac') return !unitFrac(b);
  if (b.t === 'script' && b.base.t === 'sqrt') return true;
  return false;
}
function needsAfter(x, nx) { // vector-like literals end with a comma when more follows
  if (!nx) return false;
  if (x.t === 'matrix') return true;
  return false;
}

function unitFrac(x) {
  const n = clean(x.num), d = clean(x.den);
  if (n.length === 1 && d.length === 1 && isNum(n[0]) && isNum(d[0]) && /^\d+$/.test(n[0].v) && /^\d+$/.test(d[0].v)) {
    return UNIT_FRAC[`${n[0].v}/${d[0].v}`] || null;
  }
  return null;
}

function sayBigOp(x, body, ctx) {
  const fn = baseOf(x);
  const sub = x.t === 'script' ? x.sub : null, sup = x.t === 'script' ? x.sup : null;
  const SUB = sub ? sayRow(sub, ctx) : '', SUP = sup ? sayRow(sup, ctx) : '';
  if (fn.name === 'lim') {
    if (!sub) fail(ctx, '\\lim needs a limit under it', '\\lim');
    return `النهاية لما ${SUB}، ${lam(sayRow(body, ctx))}،`;
  }
  if (fn.name === 'sum') {
    return `المجموع${sub ? ` من ${SUB}` : ''}${sup ? ` ${lam(SUP)}` : ''}، ${lam(sayRow(body, ctx))}،`;
  }
  // integral: the trailing "d x" is the differential
  let b = clean(body);
  let diff = '';
  const n = b.length;
  if (n >= 2 && b[n - 2].t === 'var' && b[n - 2].v === 'd' && b[n - 1].t === 'var') {
    diff = `، دي ${sayVar(b[n - 1], ctx)}`;
    b = b.slice(0, n - 2);
  }
  return `التكامل${sub ? ` من ${SUB}` : ''}${sup ? ` ${lam(SUP)}` : ''}، ${lam(sayRow(b, ctx))}${diff}`;
}

function sayOperand(x, ctx, nx, row, idx) {
  switch (x.t) {
    case 'num': return sayNum(x.v);
    case 'var': return sayVar(x, ctx);
    case 'greek': return GREEK[x.v];
    case 'sym': {
      if (x.v === 'infty') return 'ما لا نهاية';
      if (x.v === 'emptyset') return 'المجموعة الفاضية';
      return 'قديش'; // '?' as an unknown
    }
    case 'letters': return [...x.v].map((ch) => LETTERS[ch.toLowerCase()]).join(' ');
    case 'text': return sayText(x.s, ctx);
    case 'mathbb': return MATHBB[x.v][0];
    case 'fn': {
      const [w, link] = FNS[x.name];
      const hasArg = nx && OPERAND.has(nx.t) && !(nx.t === 'fn' && !link);
      return link && hasArg ? `${w} ${link}` : w;
    }
    case 'brace': return sayRow(x.items, ctx);
    case 'accent': return sayAccent(x, ctx);
    case 'frac': return sayFrac(x, ctx);
    case 'sqrt': return saySqrt(x, ctx);
    case 'app': return sayApp(x, ctx);
    case 'matrix': return sayMatrix(x, ctx);
    case 'delim': return sayDelim(x, ctx, row, idx);
    case 'script': return sayScript(x, ctx, nx, row, idx);
    default: return fail(ctx, 'cannot read item', x.t);
  }
}

function sayText(s, ctx) {
  const t = s.replace(/\s+/g, ' ').trim();
  if (/[A-Za-z]/.test(t)) {
    const map = { if: 'لما', otherwise: 'غير هيك', and: 'و', or: 'أو' };
    if (map[t.toLowerCase()]) return map[t.toLowerCase()];
    fail(ctx, 'Latin text cannot be read', t);
  }
  return t;
}

function sayAccent(x, ctx) {
  const body = clean(x.body);
  const one = body.length === 1 ? body[0] : null;
  switch (x.kind) {
    case 'vec': case 'overrightarrow': {
      if (one && isNum(one, '0')) return 'المتجه الصفري';
      if (one && ['var', 'greek', 'script'].includes(one.t) && cls(body) !== 'unit') return sayRow(body, ctx);
      if (one && one.t === 'script') return sayRow(body, ctx);
      if (body.length > 1) return `المتجه ${sayRow(body, ctx)}`;
      return sayRow(body, ctx);
    }
    case 'overline': {
      const c = cls(body);
      return c === 'atom' ? `${sayRow(body, ctx)} بار` : `القوس ${sayRow(body, ctx)}، بار`;
    }
    case 'hat': case 'tilde': {
      const word = x.kind === 'hat' ? 'هات' : 'تيلدا';
      const c = cls(body);
      return c === 'atom' ? `${sayRow(body, ctx)} ${word}` : `القوس ${sayRow(body, ctx)}، ${word}`;
    }
    default: return fail(ctx, 'unsupported accent', x.kind);
  }
}

function sayFrac(x, ctx) {
  const u = unitFrac(x);
  if (u) return u;
  const cn = clean(x.num), cd = clean(x.den);
  const kn = cls(cn), kd = cls(cd);
  const compN = kn === 'sum' || kn === 'frac', compD = kd === 'product' || kd === 'sum' || kd === 'frac';
  const N = sayRow(cn, ctx), D = sayRow(cd, ctx);
  if (compN && compD) return `الكسر اللي فوقه ${N}، وتحته ${D}`;
  if (compN) return `${N}، كلّه على ${D}`;
  if (compD) return `${N} على المقدار ${D}،`;
  return `${N} على ${D}`;
}

function saySqrt(x, ctx) {
  const body = clean(x.body), k = cls(body);
  const B = sayRow(body, ctx);
  if (!x.index) return k === 'atom' ? `جذر ${B}` : `جذر، ${B}،`;
  const idx = clean(x.index);
  if (idx.length === 1 && isNum(idx[0], '2')) return k === 'atom' ? `جذر ${B}` : `جذر، ${B}،`;
  const tail = k === 'atom' ? lam(B) : `${lam(B)}،`;
  if (idx.length === 1 && isNum(idx[0], '3')) return `الجذر التكعيبي ${tail}`;
  const ik = cls(idx), I = sayRow(idx, ctx);
  return `الجذر رقم ${ik === 'atom' ? I : `، ${I}،`} ${tail}`;
}

function sayArgs(arg, ctx, trigLike) {
  const parts = splitTop(clean(arg.items), (y) => y.t === 'comma');
  if (parts.length === 1) {
    if (!parts[0].length) fail(ctx, 'empty argument list', '()');
    const k = cls(parts[0]);
    const simple = trigLike ? (isSimple(k) || k === 'unit') : !['product', 'sum', 'frac'].includes(k);
    if (simple) return sayRow(parts[0], ctx);
    ctx.depth++;
    const R = sayRow(parts[0], ctx);
    ctx.depth--;
    return ctx.depth >= 1 ? `القوس ${R}، سكّر القوس،` : `القوس ${R}،`;
  }
  return parts.map((p) => sayRow(p, ctx)).join('، ');
}

function sayApp(x, ctx) {
  const fnb = baseOf(x.fn);
  if (fnb.t === 'fn') {
    const [w, link] = FNS[fnb.name];
    const name = x.fn.t === 'script' ? sayScript(x.fn, ctx, null, [], 0) : w;
    const trig = link === '' && fnb.name !== 'Id';
    const args = sayArgs(x.arg, ctx, trig);
    return `${name} ${link || (trig ? '' : 'من')} ${args}`;
  }
  const name = x.fn.t === 'delim' ? sayDelim(x.fn, ctx, [], 0) : sayOperand(x.fn, ctx, null, [], 0);
  return `${name} من ${sayArgs(x.arg, ctx, false)}`;
}

function powerWords(sup, ctx) {
  const c = clean(sup);
  if (c.length === 1 && c[0].t === 'num' && c[0].v === '2') return 'تربيع';
  if (c.length === 1 && c[0].t === 'num' && c[0].v === '3') return 'تكعيب';
  if (c.length === 1 && c[0].t === 'op' && c[0].v === '*') return 'نجمة';
  if (c.length === 1 && c[0].t === 'op' && c[0].v === '+') return 'موجب';
  const k = cls(c);
  const R = sayRow(c, ctx);
  return k === 'atom' ? `أُس ${R}` : `أُس، ${R}،`;
}

function sayScript(x, ctx, nx, row, idx) {
  const base = x.base, sub = x.sub && clean(x.sub), sup = x.sup && clean(x.sup);
  const isCirc = sup && sup.length === 1 && sup[0].t === 'op' && sup[0].v === 'circ';
  // sequences {a_n}_{n=1}^∞
  if (base.t === 'delim' && base.open === '{') {
    const inner = clean(base.items);
    if (inner.some((y) => y.t === 'mid' || y.t === 'colon')) {
      // set-builder with limits: unusual
    }
    let s = `المتتالية ${sayRow(inner, ctx)}،`;
    if (sub) s += ` من ${sayRow(sub, ctx)}`;
    if (sup) s += ` ${lam(sayRow(sup, ctx))}`;
    return s;
  }
  // mathbb
  if (base.t === 'mathbb' && sup && !sub) {
    if (sup.length === 1 && sup[0].t === 'op' && sup[0].v === '+') return `${MATHBB[base.v][0]} الموجبة`;
    if (sup.length === 2 && sup.every((y) => y.t === 'op' && y.v === '+')) return `${MATHBB[base.v][0]} الموجبة تماماً`;
    const k = cls(sup);
    if (k === 'atom') return `${MATHBB[base.v][1]} ${sayRow(sup, ctx)}`;
    return `${MATHBB[base.v][1]} أُس، ${sayRow(sup, ctx)}،`;
  }
  let s;
  const bb = base;
  // inverse function
  if (bb.t === 'var' && LETTER_FN.has(bb.v) && sup && !sub && sup.length === 2 && sup[0].t === 'op' && sup[0].v === '-' && isNum(sup[1], '1')) {
    return `${sayVar(bb, ctx)} العكسية`;
  }
  s = sayOperand(bb, ctx, null, row, idx);
  // fn with link handled by the row (fn followed by an argument); here add sub/sup words
  if (bb.t === 'fn' && FNS[bb.name][1]) {
    const hasArg = row && row[idx + 1] && OPERAND.has(row[idx + 1].t);
    s = hasArg ? `${FNS[bb.name][0]} ${FNS[bb.name][1]}` : FNS[bb.name][0];
  }
  const openEnded = ['sqrt', 'app', 'matrix', 'accent'].includes(bb.t) || isAbs(bb) || bb.t === 'frac';
  if (sub) {
    const k = cls(sub), R = sayRow(sub, ctx);
    if (bb.t === 'fn' && bb.name === 'log') s += k === 'atom' ? ` بالأساس ${R}` : ` بالأساس، ${R}،`;
    else s += k === 'atom' ? ` ${R}` : ` بإندكس ${R}،`;
  }
  if (sup) {
    if (isCirc) {
      if (openEnded) s += '،';
      return `${s} درجة`;
    }
    if (openEnded && !sub) s += '،';
    s += ` ${powerWords(sup, ctx)}`;
  }
  return s;
}

function sayDelim(x, ctx, row, idx) {
  const items = clean(x.items);
  const o = x.open;
  if (o === '|' || o === '||') {
    if (!items.length) fail(ctx, 'empty absolute value', '|');
    const vec = o === '||' || containsVec(items);
    const k = cls(items), R = sayRow(items, ctx);
    if (vec) return k === 'atom' ? `طول ${R}` : `طول، ${R}،`;
    return k === 'atom' ? `القيمة المطلقة ${lam(R)}` : `القيمة المطلقة ${lam(R)}،`;
  }
  if (o === 'langle') {
    const parts = splitTop(items, (y) => y.t === 'comma').map((p) => sayRow(p, ctx));
    if (parts.length === 2) return `الضرب الداخلي تبع ${parts[0]} ${wa(parts[1])}`;
    if (parts.length === 3) return `الضرب الثلاثي تبع ${parts[0]} ${wa(parts[1])} ${wa(parts[2])}`;
    return fail(ctx, 'unsupported \\langle…\\rangle content', '\\langle');
  }
  if (o === '{') return saySet(items, ctx);
  const parts = splitTop(items, (y) => y.t === 'comma');
  const mixed = x.close !== (o === '(' ? ')' : ']');
  if (o === '[' && parts.length === 1 && !mixed) {
    if (!items.length) fail(ctx, 'empty brackets', '[]');
    return `الجزء الصحيح ${lam(sayRow(items, ctx))}`;
  }
  if (parts.length === 1) { // plain grouping
    if (!items.length) fail(ctx, 'empty parentheses', '()');
    if (o === '[' || mixed) fail(ctx, 'unsupported bracket group', '[');
    ctx.depth++;
    const inner = sayRow(items, ctx);
    ctx.depth--;
    // a group nested in another group says where it closes, so the enclosing group's own closing stays unambiguous
    const more = ctx.depth >= 1;
    return more ? `القوس ${inner}، سكّر القوس،` : `القوس ${inner}،`;
  }
  if (parts.length === 2 && (x.interval || o === '[' || mixed)) {
    return sayInterval(x, parts, ctx);
  }
  if (o === '[') fail(ctx, 'unsupported bracket list', '[');
  // tuples
  if (parts.length === 2) {
    const [a, b] = parts;
    const compound = [a, b].some((p) => ['product', 'sum', 'frac'].includes(cls(p)));
    const A = sayRow(a, ctx), B = sayRow(b, ctx);
    return compound ? `الزوج ${A}، ${wa(B)}،` : `الزوج ${A} ${wa(B)}`;
  }
  const mode = tupleMode(x, row ? row.indexOf(x) : 0, row || [], ctx);
  const list = parts.map((p) => sayRow(p, ctx)).join('، ');
  const head = mode === 'vec' ? 'المتجه بإحداثيات' : mode === 'point' ? 'النقطة بإحداثيات' : 'الإحداثيات';
  return `${head} ${list}،`;
}

function sayInterval(x, parts, ctx) {
  const [a, b] = parts;
  const comp = (p) => ['product', 'sum', 'frac'].includes(cls(p));
  const A = sayRow(a, ctx) + (comp(a) ? '،' : ''), B = sayRow(b, ctx) + (comp(b) ? '،' : '');
  const lo = x.open === '[' ? 'مغلق' : 'مفتوح', hi = x.close === ']' ? 'مغلق' : 'مفتوح';
  if (lo === hi) return `المجال ${lo === 'مغلق' ? 'المغلق' : 'المفتوح'} من ${A} ${lam(B)}`;
  return `المجال من ${A.replace(/،$/, '')}، ${lo}، ${lam(B.replace(/،$/, ''))}، ${hi}،`;
}

function saySet(items, ctx) {
  if (!items.length) return 'المجموعة الفاضية';
  items.forEach((y) => { if (y.t === 'delim') y.noInterval = true; }); // ordered pairs inside a set stay pairs
  const sepIdx = items.findIndex((y) => y.t === 'mid' || y.t === 'colon');
  if (sepIdx >= 0) {
    const left = items.slice(0, sepIdx), right = items.slice(sepIdx + 1);
    let L;
    const inIdx = left.findIndex((y) => y.t === 'rel' && y.v === 'in');
    if (inIdx === 1 && left[0].t === 'var') L = `مجموعة كل ${sayRow([left[0]], ctx)} من ${sayRow(left.slice(2), ctx)}`;
    else L = `مجموعة كل ${sayRow(left, ctx)}`;
    return `${L} اللي بتحقق ${sayRow(right, ctx)}`;
  }
  const parts = splitTop(items, (y) => y.t === 'comma');
  if (parts.length === 1) {
    const only = parts[0];
    const isPlainInt = only.length === 1 && only[0].t === 'num' && /^\d+$/.test(only[0].v);
    if (!isPlainInt && !only.some((y) => y.t === 'dots')) {
      const sig = cls(only);
      if (sig === 'atom' || sig === 'scripted' || (only[0] && only[0].t === 'op' && only[0].v === '-')) {
        if (only.length === 1 && (only[0].t === 'var' || only[0].t === 'num') || (only.length === 2 && only[0].t === 'op')) {
          return `الجزء الكسري ${lam(sayRow(only, ctx))}`;
        }
      }
    }
  }
  return `المجموعة اللي فيها ${parts.map((p) => sayRow(p, ctx)).join('، ')}`;
}

function sayMatrix(x, ctx) {
  const rows = x.rows;
  if (!rows.length) fail(ctx, 'empty matrix', x.env);
  const cellTxt = (c) => sayRow(c, ctx);
  if (x.env === 'cases') {
    const sys = rows.every((r) => r.length === 1);
    const lines = rows.map((r) => {
      if (r.length === 1) return cellTxt(r[0]);
      if (r.length !== 2) fail(ctx, 'cases row with more than two cells', '&');
      let cond = clean(r[1]);
      while (cond.length && (cond[0].t === 'semi' || cond[0].t === 'comma')) cond = cond.slice(1);
      const head = cellTxt(r[0]);
      if (cond.length && cond[0].t === 'text') return `${head}، ${cellTxt(cond)}`;
      return `${head} لما ${cellTxt(cond)}`;
    });
    if (sys) return `${rows.length === 2 ? 'المعادلتين' : 'المعادلات'} مع بعض: ${lines.map((l, i) => (i ? wa(l) : l)).join('، ')}`;
    return `حسب الحالة: ${lines.map((l, i) => (i ? wa(l) : l)).join('، ')}`;
  }
  const width = Math.max(...rows.map((r) => r.length));
  if (x.env === 'pmatrix' && width === 1) {
    return `المتجه بإحداثيات ${rows.map((r) => cellTxt(r[0])).join('، ')}`;
  }
  if (rows.length > 10) fail(ctx, 'matrix with more than 10 rows', x.env);
  const body = rows.map((r, i) => `الصف ${ORD[i + 1]} ${r.map(cellTxt).join('، ')}`).join('، ');
  return x.env === 'vmatrix' ? `المحدِّد تبع المصفوفة: ${body}` : `المصفوفة: ${body}`;
}

// ---------------------------------------------------------------- output
function finish(s) {
  return s
    .replace(/\s+/g, ' ')
    .replace(/\s*([،؛])/g, '$1')
    .replace(/([،؛]\s*)+/g, (m) => (m.includes('؛') ? '؛ ' : '، '))
    .replace(/\s+/g, '')
    .replace(/لال/g, 'لل')
    .replace(//g, '')
    .replace(/^[،؛\s]+|[،؛\s]+$/g, '')
    .trim();
}

export function speak(tex, opts = {}) {
  if (typeof tex !== 'string') throw new SpeakMathError('formula must be a string', String(tex));
  try {
    const src = decodeEntities(tex);
    const parser = new Parser(src, tex);
    const ast = parser.parseAll();
    if (!clean(ast).length) throw new SpeakMathError('empty formula', tex);
    const ctx = Ctx(tex, ast, opts);
    const out = finish(sayRow(ast, ctx));
    if (!out) throw new SpeakMathError('empty reading', tex);
    return out;
  } catch (e) {
    if (e instanceof SpeakMathError) throw e;
    throw new SpeakMathError(`internal error: ${e.message}`, tex);
  }
}

// ---------------------------------------------------------------- CLI
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');

export function collectFormulas() { // unique TeX strings of every lesson, with first location
  const found = new Map();
  const TEX_RE = /\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]/g;
  const add = (tex, where) => { const t = tex.trim(); if (t && !found.has(t)) found.set(t, where); };
  const scan = (v, where, key) => {
    if (typeof v === 'string') {
      if (key === 'svg') return;
      if (key === 'tex') { add(v, where); return; }
      for (const m of v.matchAll(TEX_RE)) add(m[1] ?? m[2], where);
    } else if (Array.isArray(v)) v.forEach((x) => scan(x, where, key));
    else if (v && typeof v === 'object') for (const [k, x] of Object.entries(v)) scan(x, where, k);
  };
  const coursesDir = path.join(root, 'courses');
  for (const code of fs.readdirSync(coursesDir).sort()) {
    const ld = path.join(coursesDir, code, 'lessons');
    if (!fs.existsSync(ld)) continue;
    for (const f of fs.readdirSync(ld).sort()) {
      if (f.endsWith('.json')) scan(JSON.parse(fs.readFileSync(path.join(ld, f), 'utf8')), `${code}/${f.slice(0, -5)}`, '');
    }
  }
  return found;
}

function topConstruct(tex) { // coarse bucket for the review page
  const has = (re) => re.test(tex);
  if (has(/\\begin\{vmatrix\}/)) return 'determinant';
  if (has(/\\begin\{cases\}/)) return 'cases';
  if (has(/\\begin\{pmatrix\}/)) return 'matrix / column vector';
  if (has(/\\mathrm\{cis\}/)) return 'polar form (cis)';
  if (has(/\\\{[^}]*(\\mid|\\middle\||:)/)) return 'set builder';
  if (has(/\\(overrightarrow|vec|hat)/)) return 'vectors';
  if (has(/\\(overline|mathrm\{(Re|Im)\}|operatorname\{Im\})|\d\s*i\b|\bi\b/)) return 'complex numbers';
  if (has(/\\(sum|int|lim)\b/)) return 'sum / integral / limit';
  if (has(/\\(sin|cos|tan|cot|arc\w+|ln|log)\b/)) return 'trig / log';
  if (has(/\\(sup|inf|max|min)\b/)) return 'bounds';
  if (has(/\\(circ|to|iff|Rightarrow|Leftrightarrow)\b|f\^\{-1\}/)) return 'functions / logic';
  if (has(/\\\{|\\in\b|\\notin|\\subseteq|\\mathbb|\\cup|\\cap|\\setminus|\\emptyset/)) return 'sets';
  if (has(/\\(tfrac|frac|dfrac)/)) return 'fractions';
  if (has(/\\sqrt/)) return 'roots';
  if (has(/\|/)) return 'absolute value / length';
  if (has(/[\[(][^\])]*,[^\])]*[\])]/)) return 'tuples / intervals';
  if (has(/_/)) return 'subscripts / sequences';
  if (has(/\^/)) return 'powers';
  if (has(/[=<>]|\\le|\\ge|\\ne/)) return 'equations / inequalities';
  return 'other';
}
const CONSTRUCT_RULES = [
  ['frac', /\\(tfrac|frac|dfrac)/], ['sqrt', /\\sqrt/], ['script', /[\^_]/], ['abs / length', /\|/], ['vec / accent', /\\(vec|overrightarrow|overline|hat|tilde)/],
  ['matrix env', /\\begin\{(pmatrix|vmatrix)\}/], ['cases', /\\begin\{cases\}/], ['set braces', /\\\{/], ['interval / tuple', /[\[(][^\])]*,[^\])]*[\])]/],
  ['mathbb', /\\mathbb/], ['functions (trig/log)', /\\(sin|cos|tan|cot|arc\w+|ln|log)\b/], ['sup/inf/max/min', /\\(sup|inf|max|min)\b/],
  ['relation / arrow', /\\(in|notin|subseteq|ne|neq|le|ge|lt|gt|approx|to|iff|Rightarrow|Leftrightarrow|perp)\b|[=<>]/],
  ['cdot / times', /\\(cdot|times)/], ['circ (degree / compose)', /\\circ/], ['text', /\\text/], ['dots', /\\(dots|ldots|cdots)/],
];

function esc(s) { return s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

function copyKatex(outDir) {
  const src = '/Users/focus/Developer/shibbur-ios/Sources/RichText/Resources/web/katex';
  const dst = path.join(outDir, 'katex');
  if (!fs.existsSync(src)) return false;
  fs.mkdirSync(dst, { recursive: true });
  for (const f of ['katex.min.css', 'katex.min.js']) fs.copyFileSync(path.join(src, f), path.join(dst, f));
  fs.cpSync(path.join(src, 'fonts'), path.join(dst, 'fonts'), { recursive: true });
  return true;
}

function runCorpus() {
  const found = collectFormulas();
  const rows = [], errors = [];
  const counts = new Map();
  const hints = new Map();
  const optsFor = (where) => {
    const [code, slug] = where.split('/');
    if (!hints.has(code)) {
      const cp = path.join(root, 'courses', code, 'course.json');
      hints.set(code, fs.existsSync(cp) ? JSON.parse(fs.readFileSync(cp, 'utf8')) : null);
    }
    const c = hints.get(code);
    return (c && c.speakmath && c.speakmath.lessons && c.speakmath.lessons[slug]) || {};
  };
  for (const [tex, where] of found) {
    try {
      const say = speak(tex, optsFor(where));
      rows.push({ tex, say, where, group: topConstruct(tex) });
      for (const [name, re] of CONSTRUCT_RULES) if (re.test(tex)) counts.set(name, (counts.get(name) || 0) + 1);
    } catch (e) {
      if (!(e instanceof SpeakMathError)) throw e;
      errors.push({ tex, where, message: e.message });
    }
  }
  console.log(`speakmath corpus: ${found.size} unique formulas, ${rows.length} read, ${errors.length} errors`);
  console.log('formulas per construct (a formula can count in several):');
  for (const [k, v] of [...counts].sort((a, b) => b[1] - a[1])) console.log(`  ${String(v).padStart(5)}  ${k}`);
  for (const e of errors) console.error(`ERROR ${e.where}: ${e.message}`);
  const outDir = path.join(root, 'dist-review');
  fs.mkdirSync(outDir, { recursive: true });
  const hasKatex = copyKatex(outDir);
  const groups = new Map();
  for (const r of rows) { if (!groups.has(r.group)) groups.set(r.group, []); groups.get(r.group).push(r); }
  const html = `<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>speakmath review</title>${hasKatex ? '<link rel="stylesheet" href="katex/katex.min.css"><script src="katex/katex.min.js"></script>' : ''}
<style>body{font-family:system-ui,-apple-system,sans-serif;margin:0 auto;max-width:980px;padding:16px;line-height:1.6}
h2{margin-top:2em;border-bottom:1px solid #8884;padding-bottom:4px}input{width:100%;font-size:18px;padding:8px;box-sizing:border-box;position:sticky;top:0}
.row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.3fr);gap:12px;padding:8px 0;border-bottom:1px solid #8882}
.tex{direction:ltr;overflow-x:auto}.say{font-size:17px}.src{direction:ltr;color:#888;font-size:12px;font-family:monospace;grid-column:1/-1}
@media(max-width:640px){.row{grid-template-columns:1fr}}</style>
<h1>speakmath: ${rows.length} formulas</h1><input id="q" placeholder="search TeX / reading / lesson" autofocus>
${[...groups].sort((a, b) => b[1].length - a[1].length).map(([g, rs]) => `<section class="grp"><h2>${esc(g)} (${rs.length})</h2>${rs.map((r) =>
    `<div class="row" data-s="${esc((r.tex + ' ' + r.say + ' ' + r.where).toLowerCase())}"><div class="tex" data-tex="${esc(r.tex)}"></div><div class="say">${esc(r.say)}</div><div class="src">${esc(r.tex)} — ${esc(r.where)}</div></div>`).join('')}</section>`).join('\n')}
<script>
document.querySelectorAll('.tex').forEach(function(e){try{katex.render(e.dataset.tex.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&'),e,{throwOnError:false})}catch(x){e.textContent=e.dataset.tex}});
var q=document.getElementById('q');q.addEventListener('input',function(){var v=q.value.toLowerCase();document.querySelectorAll('.row').forEach(function(r){r.style.display=r.dataset.s.indexOf(v)>=0?'':'none'});document.querySelectorAll('.grp').forEach(function(g){g.style.display=[].some.call(g.querySelectorAll('.row'),function(r){return r.style.display!=='none'})?'':'none'})});
</script></html>`;
  fs.writeFileSync(path.join(outDir, 'speakmath.html'), html);
  fs.writeFileSync(path.join(outDir, 'speakmath.json'), JSON.stringify(rows, null, 1));
  console.log(`wrote ${path.relative(process.cwd(), path.join(outDir, 'speakmath.html'))}`);
  process.exit(errors.length ? 1 : 0);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  if (args[0] === '--corpus') runCorpus();
  else if (args.length) {
    try { console.log(speak(args.join(' '))); } catch (e) { console.error(e.message); process.exit(1); }
  } else { console.error("usage: speakmath.mjs '<tex>' | --corpus"); process.exit(2); }
}

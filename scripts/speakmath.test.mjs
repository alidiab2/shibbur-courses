import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { blockTex, resolveNarration, speakOptsFor, validateNarration, texCount, blockFields } from './narration-lib.mjs';
import { speak, SpeakMathError, numberToArabic, numberStringToArabic, collectFormulas } from './speakmath.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const gold = JSON.parse(fs.readFileSync(path.join(here, 'speakmath.gold.json'), 'utf8'));

test('gold pairs are exact', () => {
  assert.ok(gold.length >= 45);
  for (const [tex, want] of gold) assert.equal(speak(tex), want, tex);
});

test('gold has no duplicate formulas', () => {
  const seen = new Set();
  for (const [tex] of gold) { assert.ok(!seen.has(tex), `duplicate gold formula: ${tex}`); seen.add(tex); }
});

test('numbers 0..20 and tens', () => {
  const w = ['صفر', 'واحد', 'اثنين', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة', 'عشرة', 'أحد عشر', 'اثنا عشر', 'ثلاثة عشر',
    'أربعة عشر', 'خمسة عشر', 'ستة عشر', 'سبعة عشر', 'ثمانية عشر', 'تسعة عشر', 'عشرين'];
  w.forEach((x, i) => assert.equal(numberToArabic(i), x));
  assert.equal(numberToArabic(30), 'ثلاثين');
  assert.equal(numberToArabic(90), 'تسعين');
});

test('numbers 21..999', () => {
  assert.equal(numberToArabic(21), 'واحد وعشرين');
  assert.equal(numberToArabic(45), 'خمسة وأربعين');
  assert.equal(numberToArabic(100), 'مية');
  assert.equal(numberToArabic(101), 'مية وواحد');
  assert.equal(numberToArabic(112), 'مية واثنا عشر');
  assert.equal(numberToArabic(200), 'ميتين');
  assert.equal(numberToArabic(300), 'ثلاثمية');
  assert.equal(numberToArabic(380), 'ثلاثمية وثمانين');
  assert.equal(numberToArabic(999), 'تسعمية وتسعة وتسعين');
});

test('numbers 1000..1,000,000', () => {
  assert.equal(numberToArabic(1000), 'ألف');
  assert.equal(numberToArabic(1001), 'ألف وواحد');
  assert.equal(numberToArabic(2000), 'ألفين');
  assert.equal(numberToArabic(3000), 'ثلاثة آلاف');
  assert.equal(numberToArabic(5050), 'خمسة آلاف وخمسين');
  assert.equal(numberToArabic(11000), 'أحد عشر ألف');
  assert.equal(numberToArabic(100000), 'مية ألف');
  assert.equal(numberToArabic(1000000), 'مليون');
  assert.equal(numberToArabic(2000000), 'مليونين');
  assert.equal(numberToArabic(1e9), 'مليار');
  assert.throws(() => numberToArabic(1e9 + 1), RangeError);
});

test('every integer 0..1,000,000 has a non-empty, unique reading', () => {
  const seen = new Set();
  for (let n = 0; n <= 1000000; n += 1) {
    const s = numberToArabic(n);
    assert.ok(s && !/undefined/.test(s), `n=${n}`);
    if (n < 5000) { assert.ok(!seen.has(s), `duplicate for ${n}: ${s}`); seen.add(s); }
  }
});

test('decimals and negatives', () => {
  assert.equal(numberStringToArabic('0.5'), 'صفر نقطة خمسة');
  assert.equal(numberStringToArabic('3.14'), 'ثلاثة نقطة واحد أربعة');
  assert.equal(numberStringToArabic('12.05'), 'اثنا عشر نقطة صفر خمسة');
  assert.equal(speak('0.75'), 'صفر نقطة سبعة خمسة');
  assert.equal(speak('-0.5'), 'سالب صفر نقطة خمسة');
  assert.equal(speak('-12'), 'سالب اثنا عشر');
  assert.equal(speak('a-3'), 'إيه ناقص ثلاثة');
  assert.equal(speak('a=-3'), 'إيه بيساوي سالب ثلاثة');
  assert.equal(speak('(-1)^5=-1'), 'القوس سالب واحد، أُس خمسة بيساوي سالب واحد');
  assert.equal(speak('\\pm2'), 'زائد ناقص اثنين');
  assert.equal(speak('007'), 'صفر صفر سبعة');
});

test('upper/lower case clash', () => {
  assert.equal(speak('A'), 'إيه');
  assert.equal(speak('a'), 'إيه');
  assert.equal(speak('Aa'), 'إيه كبيرة إيه');
  assert.equal(speak('m\\le a\\le M'), 'إم أصغر أو بيساوي إيه أصغر أو بيساوي إم كبيرة');
  assert.equal(speak('x\\in X'), 'إكس بينتمي لإكس كبيرة');
  assert.equal(speak('\\sup A=M'), 'السوبريموم تبع إيه بيساوي إم');
  assert.equal(speak('\\mathbb R\\subseteq A'), 'الأعداد الحقيقية مجموعة جزئية من إيه');
});

test('atoms, operators, relations', () => {
  assert.equal(speak('\\alpha+\\beta\\pm\\gamma'), 'ألفا زائد بيتا زائد ناقص غاما');
  assert.equal(speak('2\\pi k'), 'اثنين باي كيه');
  assert.equal(speak('\\Delta x\\ne0'), 'دلتا كبيرة إكس مش بيساوي صفر');
  assert.equal(speak('a\\lt b\\gt c'), 'إيه أصغر من بي أكبر من سي');
  assert.equal(speak('a\\ge b'), 'إيه أكبر أو بيساوي بي');
  assert.equal(speak('x\\approx0.7'), 'إكس تقريباً بيساوي صفر نقطة سبعة');
  assert.equal(speak('A\\cup B\\cap C\\setminus D'), 'إيه اتحاد بي تقاطع سي ناقص دي');
  assert.equal(speak('\\vec v\\perp\\vec w'), 'ڤي متعامد مع دبليو');
  assert.equal(speak('\\vec v\\parallel\\vec w'), 'ڤي موازي لدبليو');
  assert.equal(speak('A\\iff B'), 'إيه إذا وفقط إذا بي');
  assert.equal(speak('x\\to\\infty'), 'إكس بتروح لما لا نهاية');
  assert.equal(speak('\\emptyset'), 'المجموعة الفاضية');
  assert.equal(speak('x&lt;1'), 'إكس أصغر من واحد');
});

test('fractions: atoms, unit words, compound numerator/denominator', () => {
  assert.equal(speak('\\frac{a}{b}'), 'إيه على بي');
  assert.equal(speak('\\frac12'), 'نص');
  assert.equal(speak('\\frac{1}{3}'), 'ثلث');
  assert.equal(speak('\\frac{2}{3}'), 'ثلثين');
  assert.equal(speak('\\frac{1}{10}'), 'عشر');
  assert.equal(speak('\\frac{3}{5}'), 'ثلاثة على خمسة');
  assert.equal(speak('\\dfrac{a+b}{c}'), 'إيه زائد بي، كلّه على سي');
  assert.equal(speak('\\frac{1}{2x}'), 'واحد على المقدار اثنين إكس');
  assert.equal(speak('\\frac{1}{x^2}'), 'واحد على إكس تربيع');
  assert.equal(speak('\\frac{\\frac12}{3}'), 'نص، كلّه على ثلاثة');
  assert.equal(speak('\\frac{a}{b}c'), 'إيه على بي، سي');
  assert.equal(speak('\\cos\\frac\\pi4'), 'كوسينوس القوس باي على أربعة');
});

test('powers, subscripts', () => {
  assert.equal(speak('x^3'), 'إكس تكعيب');
  assert.equal(speak('x^n'), 'إكس أُس إن');
  assert.equal(speak('x^{10}'), 'إكس أُس عشرة');
  assert.equal(speak('x^{n+1}=y'), 'إكس أُس، إن زائد واحد، بيساوي واي');
  assert.equal(speak('e^{i\\theta}'), 'إي أُس، آي ثيتا');
  assert.equal(speak('x_1+x_{10}'), 'إكس واحد زائد إكس عشرة');
  assert.equal(speak('a_{n+1}-a_n=d'), 'إيه بإندكس إن زائد واحد، ناقص إيه إن بيساوي دي');
  assert.equal(speak('(a+b)^n'), 'القوس إيه زائد بي، أُس إن');
  assert.equal(speak('|z|^2'), 'القيمة المطلقة لزِد، تربيع');
  assert.equal(speak('|z^2|'), 'القيمة المطلقة لزِد تربيع');
  assert.equal(speak('f(x)^2'), 'إف من إكس، تربيع');
  assert.equal(speak('A_g^*'), 'إيه جي نجمة');
  assert.equal(speak('\\mathbb R^+'), 'الأعداد الحقيقية الموجبة');
  assert.equal(speak('\\mathbb R^{++}'), 'الأعداد الحقيقية الموجبة تماماً');
});

test('roots, abs, length, accents', () => {
  assert.equal(speak('\\sqrt{x}'), 'جذر إكس');
  assert.equal(speak('\\sqrt{x+1}=2'), 'جذر، إكس زائد واحد، بيساوي اثنين');
  assert.equal(speak('\\sqrt[n]{x}'), 'الجذر رقم إن لإكس');
  assert.equal(speak('\\sqrt[2]{x}'), 'جذر إكس');
  assert.equal(speak('|x|'), 'القيمة المطلقة لإكس');
  assert.equal(speak('|\\vec v+\\vec u|\\le|\\vec v|+|\\vec u|'), 'طول، ڤي زائد يو، أصغر أو بيساوي طول ڤي زائد طول يو');
  assert.equal(speak('\\|v\\|'), 'طول ڤي');
  assert.equal(speak('\\vec 0'), 'المتجه الصفري');
  assert.equal(speak('\\overrightarrow{PQ}'), 'المتجه پي كيو');
  assert.equal(speak('\\overrightarrow{v}'), 'ڤي');
  assert.equal(speak('\\hat i+\\tilde x'), 'آي هات زائد إكس تيلدا');
  assert.equal(speak('\\overline{z+w}'), 'القوس زِد زائد دبليو، بار');
  assert.equal(speak('\\sqrt3\\,i'), 'جذر ثلاثة، آي');
});

test('vector operands: dot, cross, juxtaposed lengths', () => {
  assert.equal(speak('\\vec a\\cdot\\vec b'), 'إيه نقطة بي');
  assert.equal(speak('\\vec a\\times\\vec b'), 'إيه ضرب متجهي بي');
  assert.equal(speak('2\\cdot\\vec b'), 'اثنين ضرب بي');
  assert.equal(speak('|\\vec a|\\cdot|\\vec b|'), 'طول إيه ضرب طول بي');
  assert.equal(speak('(\\vec a+\\vec b)\\cdot\\vec c'), 'القوس إيه زائد بي، نقطة سي');
  assert.equal(speak('(1,2,3)\\times(0,1,0)'), 'المتجه بإحداثيات واحد، اثنين، ثلاثة، ضرب متجهي المتجه بإحداثيات صفر، واحد، صفر');
  assert.equal(speak('\\mathbb R\\times\\mathbb R'), 'الأعداد الحقيقية ضرب الأعداد الحقيقية');
  assert.equal(speak('|a||b|'), 'القيمة المطلقة لإيه ضرب القيمة المطلقة لبي');
});

test('function application vs product', () => {
  assert.equal(speak('f(x)'), 'إف من إكس');
  assert.equal(speak('g(f(x))'), 'جي من إف من إكس');
  assert.equal(speak('f(x+1)'), 'إف من القوس إكس زائد واحد');
  assert.equal(speak('f(a,b)'), 'إف من إيه، بي');
  assert.equal(speak('a(b+c)'), 'إيه القوس بي زائد سي');
  assert.equal(speak('i(b+d)'), 'آي القوس بي زائد دي');
  assert.equal(speak('f^{-1}(x)'), 'إف العكسية من إكس');
  assert.equal(speak('(f+g)(x)'), 'القوس إف زائد جي، من إكس');
  assert.equal(speak('(a+b)(c+d)'), 'القوس إيه زائد بي، القوس سي زائد دي');
  assert.equal(speak('\\sin^2x'), 'سينوس تربيع إكس');
  assert.equal(speak('\\cos(\\theta)'), 'كوسينوس ثيتا');
  assert.equal(speak('\\cos(\\theta_1+\\theta_2)'), 'كوسينوس القوس ثيتا واحد زائد ثيتا اثنين');
  assert.equal(speak('\\mathrm{Re}(z)'), 'الجزء الحقيقي من زِد');
  assert.equal(speak('\\log_a x'), 'لوغ بالأساس إيه إكس');
  assert.equal(speak('\\ln x'), 'لن إكس');
  assert.equal(speak('\\arg(z)'), 'الأرغومنت تبع زِد');
  assert.equal(speak('\\operatorname{arccot}x'), 'أركوتانجنس إكس');
});

test('interval vs pair, tuples', () => {
  assert.equal(speak('(1,2)'), 'الزوج واحد واثنين');
  assert.equal(speak('(a,b)'), 'الزوج إيه وبي');
  assert.equal(speak('x\\in(a,b)'), 'إكس بينتمي للمجال المفتوح من إيه لبي');
  assert.equal(speak('(0,\\infty)'), 'المجال المفتوح من صفر لما لا نهاية');
  assert.equal(speak('[0,1)'), 'المجال من صفر، مغلق، لواحد، مفتوح');
  assert.equal(speak('(0,1]'), 'المجال من صفر، مفتوح، لواحد، مغلق');
  assert.equal(speak('(a,b)=\\{x\\mid a<x<b\\}'), 'المجال المفتوح من إيه لبي بيساوي مجموعة كل إكس اللي بتحقق إيه أصغر من إكس أصغر من بي');
  assert.equal(speak('f:(0,1)\\to\\mathbb R'), 'إف من المجال المفتوح من صفر لواحد بتروح للأعداد الحقيقية');
  assert.equal(speak('(0,1)\\to(1,0)'), 'الزوج صفر وواحد بتروح للزوج واحد وصفر');
  assert.equal(speak('(1,2,3)'), 'الإحداثيات واحد، اثنين، ثلاثة');
  assert.equal(speak('P=(1,2,3)'), 'پي بيساوي النقطة بإحداثيات واحد، اثنين، ثلاثة');
  assert.equal(speak('\\vec v=(1,2,3)'), 'ڤي بيساوي المتجه بإحداثيات واحد، اثنين، ثلاثة');
  assert.equal(speak('(x,y)'), 'الزوج إكس وواي');
});

test('sets', () => {
  assert.equal(speak('\\{a,b\\}'), 'المجموعة اللي فيها إيه، بي');
  assert.equal(speak('\\{\\}'), 'المجموعة الفاضية');
  assert.equal(speak('\\{x\\in A:\\ x>0\\}'), 'مجموعة كل إكس من إيه كبيرة اللي بتحقق إكس أكبر من صفر'.replace('إيه كبيرة', 'إيه'));
  assert.equal(speak('\\{x\\}'), 'الجزء الكسري لإكس');
  assert.equal(speak('[x]'), 'الجزء الصحيح لإكس');
  assert.equal(speak('\\{3\\}'), 'المجموعة اللي فيها ثلاثة');
  assert.equal(speak('\\{a_n\\}_{n=1}^{\\infty}'), 'المتتالية إيه إن، من إن بيساوي واحد لما لا نهاية');
  assert.equal(speak('\\mathbb{N}\\subseteq\\mathbb{Z}'), 'الأعداد الطبيعية مجموعة جزئية من الأعداد الصحيحة');
  assert.equal(speak('\\mathbb C'), 'الأعداد المركّبة');
  assert.equal(speak('\\mathbb I'), 'الأعداد غير النسبية');
  assert.equal(speak('\\left\\{x\\ \\middle|\\ x>0\\right\\}'), 'مجموعة كل إكس اللي بتحقق إكس أكبر من صفر');
});

test('big operators', () => {
  assert.equal(speak('\\sum_{k=1}^{n}k'), 'المجموع من كيه بيساوي واحد لإن، لكيه');
  assert.equal(speak('\\sum_{k=1}^{n}k^2+1'), 'المجموع من كيه بيساوي واحد لإن، لكيه تربيع، زائد واحد');
  assert.equal(speak('\\int_a^b f(x)\\,dx'), 'التكامل من إيه لبي، لإف من إكس، دي إكس');
  assert.equal(speak('\\lim_{x\\to a}f(x)=L'), 'النهاية لما إكس بتروح لإيه، لإف من إكس، بيساوي إل');
});

test('matrices, cases, determinants', () => {
  assert.equal(speak('\\begin{pmatrix}1\\\\ 2\\end{pmatrix}'), 'المتجه بإحداثيات واحد، اثنين');
  assert.equal(speak('\\begin{pmatrix}a&b\\\\c&d\\end{pmatrix}'), 'المصفوفة: الصف الأول إيه، بي، الصف الثاني سي، دي');
  assert.equal(speak('\\begin{vmatrix}a&b\\\\c&d\\end{vmatrix}'), 'المحدِّد تبع المصفوفة: الصف الأول إيه، بي، الصف الثاني سي، دي');
  assert.equal(speak('f(x)=\\begin{cases}x&;\\ x\\ge0\\\\-x&;\\ x<0\\end{cases}'),
    'إف من إكس بيساوي حسب الحالة: إكس لما إكس أكبر أو بيساوي صفر، وسالب إكس لما إكس أصغر من صفر');
  assert.equal(speak('\\begin{cases}a=1\\\\b=2\\end{cases}'), 'المعادلتين مع بعض: إيه بيساوي واحد، وبي بيساوي اثنين');
  assert.equal(speak('\\begin{pmatrix}1\\\\0\\end{pmatrix}\\cdot\\begin{pmatrix}0\\\\1\\end{pmatrix}'),
    'المتجه بإحداثيات واحد، صفر، نقطة المتجه بإحداثيات صفر، واحد');
});

test('text, spacing, quad, lists, qed', () => {
  assert.equal(speak('x\\in A\\ \\text{ و }\\ y\\in B'), 'إكس بينتمي لإيه و واي بينتمي لبي');
  assert.equal(speak('a\\,b\\;c\\!d\\ e'), 'إيه بي سي دي إي');
  assert.equal(speak('a=1,\\quad b=2'), 'إيه بيساوي واحد، و بي بيساوي اثنين');
  assert.equal(speak('a=1\\qquad b=2'), 'إيه بيساوي واحد، و بي بيساوي اثنين');
  assert.equal(speak('a\\quad\\Rightarrow\\quad b'), 'إيه، يعني، بي');
  assert.equal(speak('1,2,\\dots,n'), 'واحد، اثنين، وهيك، إن');
  assert.equal(speak('k=0..n'), 'كيه بيساوي صفر لحد إن');
  assert.equal(speak('x=y\\ \\blacksquare'), 'إكس بيساوي واي، وهيك خلصنا البرهان');
  assert.equal(speak('\\langle\\vec u,\\vec v\\rangle'), 'الضرب الداخلي تبع يو وڤي');
  assert.equal(speak('30^\\circ+45^\\circ'), 'ثلاثين درجة زائد خمسة وأربعين درجة');
  assert.equal(speak('g\\circ f'), 'جي تركيب إف');
});

test('output is normalised', () => {
  for (const [tex] of gold) {
    const s = speak(tex);
    assert.ok(!/\s{2,}/.test(s) && !/\s،/.test(s) && !/،،/.test(s) && !/^[،\s]|[،\s]$/.test(s) && !/\uE000/.test(s), `${tex} -> ${s}`);
  }
});

test('errors: unknown command, environment, characters, structure', () => {
  const bad = ['\\foo', '\\begin{align}x\\end{align}', 'é', '\\text{hello}', '(1,2', '\\frac{1}', 'x^', '|x', '\\mathbb{X}', '', '\\sqrt[3',
    '1000000000000', '\\left. x \\right)', '\\begin{pmatrix}1\\end{cases}', 'x)', '&', 'x\\\\y', '\\mid', '\\textbf{x}', '\\middle\\|'];
  for (const tex of bad) assert.throws(() => speak(tex), SpeakMathError, tex);
  try { speak('a+\\foo'); assert.fail('no throw'); } catch (e) {
    assert.ok(e instanceof SpeakMathError);
    assert.match(e.message, /\\foo/);
    assert.match(e.message, /a\+\\foo/);
    assert.equal(e.tex, 'a+\\foo');
    assert.equal(e.token, '\\foo');
  }
  assert.throws(() => speak(42), SpeakMathError);
});

test('the whole course corpus reads without errors', () => {
  const found = collectFormulas();
  assert.ok(found.size > 1000);
  let n = 0;
  for (const tex of found.keys()) { assert.ok(speak(tex).length > 0, tex); n++; }
  assert.equal(n, found.size);
});

test('speak option pairs:interval', () => {
  assert.equal(speak('(1,5)'), 'الزوج واحد وخمسة');
  assert.equal(speak('(1,5)', { pairs: 'interval' }), 'المجال المفتوح من واحد لخمسة');
  assert.equal(speak('(x,f(x))', { pairs: 'interval' }), 'الزوج إكس وإف من إكس');
  assert.equal(speak('\\{(x,y)\\mid x>0\\}', { pairs: 'interval' }), 'مجموعة كل الزوج إكس وواي اللي بتحقق إكس أكبر من صفر');
  assert.equal(speak('(0,\\pi)'), 'المجال المفتوح من صفر لباي');
});

test('narration: k-th TeX of a block follows the validator order', () => {
  const root = path.resolve(here, '..');
  let blocks = 0;
  for (const code of fs.readdirSync(path.join(root, 'courses'))) {
    const ld = path.join(root, 'courses', code, 'lessons');
    if (!fs.existsSync(ld)) continue;
    for (const f of fs.readdirSync(ld)) {
      for (const b of JSON.parse(fs.readFileSync(path.join(ld, f), 'utf8')).blocks) {
        assert.equal(blockTex(b).length, texCount(b), `${code}/${f} block ${b.t}`);
        blocks++;
      }
    }
  }
  assert.ok(blocks > 100);
  const b = { t: 'p', html: 'a \\(x^2\\) b \\[y\\] c \\(z\\)' };
  assert.deepEqual(blockTex(b), ['x^2', 'y', 'z']);
  assert.deepEqual(blockTex({ t: 'math', tex: 'a+b' }), ['a+b']);
  assert.deepEqual(blockFields({ t: 'math', tex: 'a' }), []);
});

test('narration: math say is generated unless keep:true', () => {
  const lesson = { blocks: [{ t: 'p', html: 'نقطة \\(\\frac12\\) و \\(x^2\\)' }] };
  const n = { v: 1, segments: [{ block: 0, say: ['أول', { math: 0 }, { math: 1, say: 'يدوي' }, { math: 1, say: 'يدوي', keep: true }, { show: 'نقطة' }] }] };
  const r = resolveNarration(n, lesson);
  assert.deepEqual(r.segments[0].say.slice(1, 4), [{ math: 0, say: 'نص' }, { math: 1, say: 'إكس تربيع' }, { math: 1, say: 'يدوي', keep: true }]);
  assert.equal(n.segments[0].say[1].say, undefined, 'input is not mutated');
  const v = validateNarration(n, lesson, 'x');
  assert.deepEqual(v.errors, []);
  const bad = { v: 1, segments: [{ block: 0, say: [{ math: 5 }] }] };
  assert.ok(validateNarration(bad, lesson, 'x').errors.some((e) => /math 5/.test(e)));
  const lesson2 = { blocks: [{ t: 'math', tex: '\\foo' }] };
  assert.ok(validateNarration({ v: 1, segments: [{ block: 0, say: [{ math: 0 }] }] }, lesson2, 'x').errors.some((e) => /unknown command/.test(e)));
  assert.throws(() => resolveNarration({ v: 1, segments: [{ block: 0, say: [{ math: 0 }] }] }, lesson2), SpeakMathError);
  assert.deepEqual(speakOptsFor({ speakmath: { lessons: { a: { pairs: 'interval' } } } }, 'a'), { pairs: 'interval' });
  assert.deepEqual(speakOptsFor({}, 'a'), {});
});

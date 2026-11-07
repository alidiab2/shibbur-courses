# 11004 — חדו"א 1 (Jacobson–Shnabel) — Chapter 2 · פונקציות (p7–21)

## 2-intro · functions (p7–11) → lesson `functions`
- [x] p7  idea  שלוש התאמות f1,f2,f3 בין A={1,2,3} ל-B={a,b,c,d}; f1(1)=a,f1(1)=b,f1(2)=c   → steps: arrow diagrams, problems marked
- [x] p8  idea  f1 לא פונקציה (איבר ב-A ללא חץ + איבר עם שני חיצים); f2 גם לא; f3 כן  → steps (same figure)
- [x] p8  def   הגדרה 2.1 פונקציה (לכל x קיים y יחיד)                                   → box def + checklist figure
- [x] p8  def   הגדרה 2.2 תחום / טווח                                                   → figure: A (domain) and B (codomain) ovals
- [x] p8  notation סימון f:A→B, f(x)=y                                                   → box key
- [x] p8  remark הערה 2.3 שוויון פונקציות (אותו תחום, טווח, f(x)=g(x))                   → figure: two arrow diagrams, same / different codomain
- [x] p8  def   הגדרה 2.4 מקור ותמונה                                                    → figure: x→y labelled
- [x] p9  remark הערה 2.5 (מקור אחד לכל y? לא — רק תמונה אחת לכל x; ייתכן יותר ממקור אחד; ייתכן y ללא מקור) → figure: arrows, y with 2 sources, w with none
- [x] p9  def   הגדרה 2.6 Im(f) קבוצת התמונה                                             → figure: highlighted subset of B
- [x] p9  ex    דוגמה 2.7  f(1)=a,f(2)=a,f(3)=c, Im={a,c}                               → box ex + figure
- [x] p9  def   הגדרה 2.8 משתנה בלתי תלוי / תלוי                                         → box def
- [x] p9  def   הגדרה 2.9 מכפלה קרטזית A×A, ℝ²                                           → figure: grid of pairs
- [x] p10 def   הגדרה 2.10 מערכת צירים קרטזית                                            → figure: axes with point (x,y)
- [x] p10 def   הגדרה 2.11 גרף G(f)={(x,f(x))|x∈A}                                       → steps: points build the graph
- [x] p10 ex    דוגמה 2.12: f=3, f=x, f=x², f=sin x (גרף + תמונה)                        → figure: 4 mini graphs w/ images
- [x] p10 def   הגדרה 2.13 ערך מוחלט |x|                                                 → figure graph
- [x] p10 ex    דוגמה 2.14 גרף ותמונה של |x|                                             → box ex
- [x] p10 notation [x]=m, m≤x<m+1 (חלק שלם)                                              → number line
- [x] p11 def   הגדרה 2.15 פונקציית הערך השלם [x]                                        → figure: staircase
- [x] p11 ex    דוגמה 2.16 גרף ותמונה של [x]                                             → box ex
- [x] p11 def   הגדרה 2.17 {x}=x-[x] פונקציית הערך השברי                                 → figure: sawtooth
- [x] p11 ex    דוגמה 2.18 גרף ותמונה של {x}                                             → box ex

## 2.1 · סדרות (p11–13) → lesson `sequences`
- [x] p11 def   הגדרה 2.19 סדרה f:ℕ→A, {f(n)}, a_n=f(n), {a_n}_{n=1}^∞                   → steps: dots on axes
- [x] p11 ex    דוגמה 2.20 הסדרה ההרמונית a_n=1/n, גרף ותמונה                            → figure
- [x] p11 remark שתי דוגמאות מבית הספר (חשבונית, הנדסית)                                  → intro to next points
- [x] p12 def   הגדרה 2.21 סדרה חשבונית, הפרש d, a_{i+1}-a_i=d, איברים a1+(n-1)d          → steps: +d jumps
- [x] p12 formula סכום n איברים S_n = (a1+an)/2·n = (2a1+d(n-1))/2·n                    → steps: Gauss pairing
- [x] p12 ex    דוגמה 2.22 {-3,5,13,21,…} S10=330                                        → box ex
- [x] p12 def   הגדרה 2.23 סדרה הנדסית, מנה q, a_n=a1 q^{n-1}                            → steps: ×q jumps
- [x] p12 formula S_n = a1 (1-q^n)/(1-q), q≠1                                            → box key
- [x] p13 ex    דוגמה 2.24 a1=3,q=2, S10=3(2^10-1)                                       → box ex
- [x] p13 def   סדרה מוגדרת ברקורסיה a_{n+1}=f(a1..an)                                   → flow figure
- [x] p13 ex    דוגמה 2.25 פיבונאצ'י a_{n+2}=a_n+a_{n+1}, a1=1,a2=2: 1,2,3,5,8,13 + מדרגות → steps

## 2.2 · פונקציות אלמנטריות (p13–14) → lesson `elementary-functions`
- [x] p13 list  1 קבועה f1=c                                                              → graph
- [x] p13 list  2 ליניארית f2=x                                                          → graph
- [x] p13 list  3 מעריכית f3=a^x, 0<a≠1                                                  → graph (a>1, a<1)
- [x] p13 list  4 לוגריתמית f4=log_a x, x>0                                              → graph
- [x] p13 list  5 טריגונומטרית f5=sin x                                                  → graph
- [x] p13 list  6 טריגונומטרית הפוכה f6=arcsin x                                         → graph

## 2.3 · תכונות של פונקציות (p14–21) → lesson `function-properties`
- [x] p14 intro שני סוגים מיוחדים (מקרים של הערה 2.5)                                    → why card
- [x] p14 def   הגדרה 2.26.1 חד-חד ערכית: x1≠x2 ⇒ f(x1)≠f(x2)                            → steps/figure arrows
- [x] p14 def   הגדרה 2.26.2 על: Im(f)=B                                                 → figure arrows
- [x] p14 remark הערה 2.27 הוכחת חח"ע דרך f(x1)=f(x2) ⇒ x1=x2                            → method box
- [x] p14-15 ex דוגמה 2.28 (ארבעה מקרים)                                                  → steps: 4 diagrams
- [x] p15 ex    דוגמה 2.29 (ax+b, e^x, sin x, x³, x³+x²)                                  → table + horizontal-line figure
- [x] p15 remark "על" = התמונה מתפרשת על כל הטווח                                         → caption
- [x] p15 ex    דוגמה 2.30 x² בארבעה תחומים/טווחים                                       → steps: 4 graphs
- [x] p16 def   הגדרה 2.31 פונקציה חסומה |f(x)|≤M ; e^x לא, sin x כן                      → figure band
- [x] p16 ex    דוגמה 2.32 (n/(n+1), [x], {x})                                            → box ex + figure
- [x] p16 def   הגדרה 2.33 מונוטונית עולה / יורדת / מונוטונית                             → steps
- [x] p16 ex    דוגמה 2.34 (ax+b, e^x, |x|)                                               → figure
- [x] p17 def   הגדרה 2.35 מחזורית, מחזור יסודי                                           → figure sin
- [x] p17 ex    דוגמה 2.36 (sin,cos 2π ; tan π ; ליניארית לא)                            → figure
- [x] p17 def   הגדרה 2.37 זוגית / אי זוגית                                               → figure
- [x] p17 thm   מסקנה 2.38 אי זוגית ⇒ f(0)=0                                              → box thm
- [x] p17 ex    דוגמה 2.39 (sin אי זוגית, cos זוגית, x^n)                                 → box ex
- [x] p18 def   הגדרה 2.40 חיבור, כפל בסקלר, כפל, מנה (A_g^*)                              → figure
- [x] p18 remark חיבור וכפל של חסומות חסומה; מנה לא בהכרח                                  → trap box
- [x] p18 def   הגדרה 2.41 הרכבה g∘f=g(f(x))                                              → flow figure
- [x] p18 ex    דוגמה 2.42 sin(e^x), e^{sin x}                                           → box ex
- [x] p18 remark תנאי: התמונה של f בתחום של g                                             → note
- [x] p18 def   הגדרה 2.43 פונקציית הזהות Id_A                                            → box
- [x] p19 def   הגדרה 2.44 Id על ℝ                                                       → box
- [x] p19 remark הערה 2.45 f∘Id_A=f=Id_B∘f                                               → box
- [x] p19 def   הגדרה 2.46 הפיכה, g∘f=Id_A, f∘g=Id_B, הופכית                              → steps
- [x] p19 claim טענה 2.47 יחידות ההופכית, סימון f^{-1}                                    → box thm
- [x] p19 remark הערה 2.48 (f^{-1})^{-1}=f                                                → box
- [x] p19 remark חזרה ל-2.30 סעיף 4 (x² ו-√x)                                             → figure
- [x] p19 thm   משפט 2.49 הפיכה ⇔ חח"ע ועל                                                → figure chips
- [x] p19 thm   מסקנה 2.50 f^{-1}(b)=a ⇔ f(a)=b                                           → box thm
- [x] p20 ex    דוגמה 2.51 f=2x, f^{-1}=x/2                                               → box ex
- [x] p20 ex    דוגמה 2.52 x² על ℝ⁺, √x                                                   → box ex
- [x] p20 ex    דוגמה 2.53 e^x: ℝ→ℝ⁺⁺, ln x                                              → box ex
- [x] p20 remark הגרפים של f ו-f^{-1} שיקוף ביחס ל-y=x                                    → steps
- [x] p20 def   הגדרה 2.54 arcsin (sin על [-π/2,π/2]→[-1,1])                              → graph
- [x] p20 list  arccos [0,π]; p21 arctan (-π/2,π/2); arccot (0,π)                         → graphs
- [x] p21 remark לצייר גרפים תוך שימוש בסימטריה ביחס ל-y=x                                → covered by reflection steps

(stop: p21 "3 גבולות של סדרות" belongs to chapter 3)

## Render status
- `functions`: visuals: 8 figures, 5 steps · quizzes: 7 · rendered: light ✓ dark ✓
- `sequences`: visuals: 0 figures, 5 steps · quizzes: 6 · rendered: light ✓ dark ✓
- `elementary-functions`: visuals: 1 figures, 4 steps · quizzes: 4 · rendered: light ✓ dark ✓
- `function-properties`: visuals: 2 figures, 15 steps · quizzes: 17 · rendered: light ✓ dark ✓
- note: the renderer's page snapshot caps at 24000px, so lessons were split into chunks only in the check copy to render all step frames; flashcards show mirrored in static snapshots (3D flip artifact of the renderer, not content).

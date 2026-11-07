# 11102 — אלגברה 1מח (Ofir Shnabel booklet) — Chapter 1 map

## Ch 1 · ווקטורים וגיאומטריה אנליטית

### 1-intro · vectors (p2–4)  → lesson `vectors`
- [x] p2  idea  ווקטור = גודל + כיוון, המיקום לא חשוב                         → figure: same arrow in two places + different arrow (point 1)
- [x] p2  notation  P1P2 (נקודת התחלה/סוף)                                      → steps: P₁→P₂, move to origin, coordinates (point 2)
- [x] p2  notation  וקטור ב-R² (a,b) וב-R³ (a,b,c) כעמודה                       → figure R², figure R³ oblique (point 2)
- [x] p2  remark  מה ההבדל בין נקודות לווקטורים (פעולות)                         → p block
- [x] p2  def 1.1  R², R³                                                       → box def
- [x] p2  def 1.2  −v, αv (α חיובי), v+u, v−u                                   → steps scalar (v,2v,−v,½v), steps sum, steps difference; box def; ex; quiz
- [x] p3  remark 1.3  אורך |v| בפיתגורס ב-R² וב-R³                              → steps R², steps R³; box note; ex; quiz
- [x] p3  def  וקטור האפס                                                      → box def; steps v+(−v)=0
- [x] p3  def  וקטור יחידה                                                     → p block (+ unit circle in point 7)
- [x] p3  def  קו-ליניאריים                                                    → figure line through origin with u, αu, −αu, bad w
- [x] p3  cor 1.4  קו-ליניאריים ⇔ פרופורציונאליים                               → box thm; ex; quiz
- [x] p3–4 claim 1.5  8 תכונות החיבור והכפל בסקלר                               → two tables (html) + box thm; commutativity shown in the sum steps; ex
- [x] p4  def 1.6  וקטור מנורמל v̂ = v/|v|                                       → steps unit circle; box def; ex
- [x] p4  claim 1.7  תכונות האורך (אי שוויון המשולש, נירמול)                     → figure triangle inequality; box thm; quizzes
visuals: 5 figures, 8 steps · quizzes: 9

### 1.1 · מכפלה סקלרית (p4–6)  → lesson `dot-product`
- [x] p4  def 1.8  v·u = |v||u|cos α                                           → steps geometric (projection); figure sign cases; box def
- [x] p4–5 ex 1.9  e1·e2 = 0, (1,0)·(1,1) = 1                                  → figure two panels; box ex
- [x] p5  claim 1.10  v1·v2 = a1a2+b1b2+c1c2                                   → steps (1,2,3)·(4,−5,6); box thm; quiz
- [x] p5  def 1.11  cos α = v·u/(|v||u|)                                       → box def; steps angle
- [x] p5  ex 1.12  זווית בין (1,1,0) ל-(0,1,1) = π/3                            → steps; box ex; quiz
- [x] p6  def 1.13  מאונכים ⇔ v·u = 0                                          → box def
- [x] p6  ex 1.14  כל הווקטורים המאונכים ל-(3,−4): t(4,3)                       → steps; box ex; quiz
- [x] p6  claim 1.15  תכונות המכפלה הסקלרית                                     → box thm; ex; mistakes
visuals: 2 figures, 4 steps · quizzes: 7

### 1.2 · מכפלה וקטורית (p6–8)  → lesson `cross-product`
- [x] p6  motivation  וקטור w מאונך למישור, גודל = שטח מקבילית, כלל יד ימין     → steps idea; point 3 hand rule
- [x] p7  def 1.16  v×u: ⊥, |w|=|u||v|sin α, מערכת יד ימין                      → steps area; steps hand; box def; quiz
- [x] p7  notation  i, j, k                                                    → p block
- [x] p7  claim 1.17  נוסחת הדטרמיננטה                                         → steps formula; box thm; box note (determinant later)
- [x] p7  homework  v×u מקיים את שתי התכונות הראשונות                           → box idea + verification in example
- [x] p7  ex 1.18  (1,−1,0)×(0,1,2) = (−2,−2,1)                                → steps; box ex; verification box; quiz
- [x] p8  claim 1.19  אנטי-סימטריה, סקלר, פילוג                                 → steps v×u vs u×v; box thm; ex; quiz
visuals: 0 figures, 6 steps · quizzes: 6

### 1.3 · משוואת מישור (p8–10)  → lesson `plane-equation`
- [x] p8  idea  שתי דרכים: וקטורית (פרמטרית) ואלגברית                            → steps parametric plane; box def
- [x] p8  derivation  P0P·v = 0 ⇒ ax+by+cz−ax0−by0−cz0 = 0                     → steps normal; box key
- [x] p9  cor 1.20  ax+by+cz+d=0                                               → box thm; quiz
- [x] p9  def 1.21  נורמל, לא יחיד                                             → figure not unique; box def; quiz
- [x] p9  ex 1.22  נקודה (1,0,1), נורמל (2,−1,0): 2x−y−2=0                       → steps; box ex; quiz
- [x] p9  ex 1.23  מהצגה וקטורית לאלגברית: 2x+7y+6z−34=0                        → steps; box ex; quizzes
- [x] p10 remark  מעבר מאלגברית לוקטורית (בהמשך הקורס)                           → box note
visuals: 1 figure, 4 steps · quizzes: 8

### 1.4 · ישרים במישור ובמרחב (p10)  → lesson `lines`
- [x] p10 def 1.24  L = {u1 + t v}                                             → steps line; box def; ex; quiz
- [x] p10 remark 1.25  נקודה/כיוון לא יחידים, הצגה וקטורית/פרמטרית               → figure; box note; quiz
- [x] p10 ex 1.26  ישר דרך P=(2,−1,6), Q=(3,1,−2)                              → steps PQ; steps chips; box ex; quiz
visuals: 1 figure, 3 steps · quizzes: 6

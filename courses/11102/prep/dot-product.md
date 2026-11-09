# prep — dot-product (§1.1 מכפלה סקלרית, p4–6)

1. One idea: الضرب السلمي = ظل × طول — كم سهم u ماشي بنفس اتجاه v، مضروب بطول v. النتيجة عدد، مش سهم.
2. Why it exists: need a number that tells angle/perpendicularity from coordinates, no protractor. Hook: (2,3) & (-3,2) perpendicular? Answer by 2·(-3)+3·2 = 0.
3. Chain: def 1.8 (|v||u|cos α) ← shadow picture ← three cases: acute +, right 0, obtuse − ← examples 1.9 (two) give same numbers as coordinate products ← claim 1.10 (not luck; R² proof via cos(β−γ), R³ stated) ← so cos α = v·u/(|v||u|) (1.11, angle from numbers; α in [0,π] because cos is 1-1 there) ← ex 1.12 ← 0 ⇒ perpendicular (1.13) ← ex 1.14 (all u ⊥ (3,−4): 3x=4y ⇒ t(4,3)) ← properties 1.15 (v·v=|v|² closes the loop with |v| from lesson 1).
   Missing links written out: the shadow is signed; the formula is the definition of ⊥ (also for 0 vector); 3x=4y → pick x=4,y=3 then scale by t.
4. Hard places:
   - "dot product is a vector" → say a number (a chip with 12), the picture ends on a number.
   - sign: students forget negative = obtuse → case frame 3 + quiz with 2π/3.
   - v·u=0 ⇒ v=0 or u=0 (numbers habit) → trap mc in point 5 + mistakes.
   - cos table gaps (2π/3, 3π/4) → reminder table box before first use.
   - from 3x=4y to t(4,3) feels like magic → unfold: choose (4,3), scale.
   - forgetting to divide by |v||u| when getting the angle → mistakes row (true only if |v||u|=1).
5. Exam: compute v·u in R³; find angle (cos⁻¹ with table); find all/which vectors ⊥ a given one (answer t(·,·)); parameter making two vectors ⊥; expand |v+u|².
6. Central image: shadow of u on v × |v|. Exact (signed shadow = |u|cos α). Breaks nowhere for α in [0,π]. Clean numbers v=(4,0), u=(3,4): shadow 3, dot 12.
7. Emphasis: workhorse = coordinate formula (1.10) and ⊥ ⟺ 0. One line: commutative, scalar, distributive. Picture: v·v=|v|². Cut: Hebrew synonyms beyond box, proof of distributivity (one line why: expand coordinates), 1.9 as separate box (folded into figure), |v+u|² only as short idea box (+Pythagoras payoff).
8. Hard case: obtuse (shadow on the other side, negative) and v·u=0 with both non-zero (not "one is zero").
9. Intuition for 1.10 in R²: each vector = length×(cos,sin) from the x-axis; α=β−γ; cos(β−γ) expands to products of coordinates. Conditions: nonzero vectors in 1.8/1.11 (no angle with 0-vector); α∈[0,π] so arccos single-valued.

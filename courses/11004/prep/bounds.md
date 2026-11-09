# prep · bounds (1.1, p5–7)

1. **One idea**: a set on the number line; a *ceiling* is a number no member pokes above; the *lowest* ceiling (sup) is the one that sticks to the set — it may or may not be a member.
2. **Why it exists**: "the largest element" fails for (2,4) — there is none. sup/inf are the honest replacement and the axiom guarantees they exist; limits/continuity/integrals later all lean on it. Hook = lower a ceiling over (2,4): where does it stop, is it a member?
3. **Chain**: upper bound (a≤M ∀a) → raising a ceiling keeps it a ceiling (cor 1.19) → so ceilings are infinitely many → natural to ask for the lowest → sup (two checks: it is a ceiling; nothing lower is) → if sup∈A call it max → bounded = ceiling AND floor ⇔ |a|≤c → in ℚ the lowest ceiling can be missing (√2) → axiom: in ℝ it never is (non-empty, bounded above) → cor: bounded non-empty ⇒ sup, inf.
   Missing link in PDF: Archimedes is only *used* for "ℕ has no ceiling"; the PDF says "intuitive, not proved" — one line + steps with 3 different M.
4. **Hard**: (a) sup not in the set — students think sup must be a member → hollow dot + (−∞,3) lowering; (b) "sup" vs "a ceiling" (any ceiling) → colour: ceilings = t-2, sup = t-good; (c) max vs sup; (d) bounded needs BOTH sides (ℕ is bounded below only); (e) the second check of sup ("nothing lower") — general argument: any M̃<3 → between M̃ and 3 there is a member of A.
5. **Exam**: compute sup/inf/max/min of an interval-ish set; decide whether max/min exist; prove sup A = M via two checks (often with Archimedes for 1−1/n or 1/n); show bounded via c=max{|m|,|M|}. Lost points: forgetting check 2, claiming sup∈A.
6. **Central image**: vertical number line (bigger = higher), set = thick segment on the axis, ceiling = hatched slab above a line, floor = slab below. Breaks nowhere for ℝ (just don't use for ℚ gaps without the hole drawn).
7. **Emphasis / cut**: most time on sup (point 3: lowering + two checks) and max-vs-sup; Archimedes one line + 4 frames; bounded one figure; axiom one figure (ℚ hole). Not said: other characterisations (sup via ε), uniqueness of sup, proof of Archimedes.
8. **Hard case**: A=(−∞,3): any M̃<3: (M̃+3)/2 ∈A and above M̃ ⇒ M̃ not a ceiling.
9. **Simplify**: axiom — without it ℚ fails (set of rationals with x²<2). Each definition condition: "non-empty" else every number is a ceiling and there's no lowest.

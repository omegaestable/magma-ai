# Assignment: law 33020 — `x = (y * (((x * y) * z) * x)) * y`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec33020.lean` (rules: `gen/rules33020.txt`, checker: `python gen/chk33020.py 3000`).
This law is R-FORM (x = A ◇ y). The skeleton's `op` is the free model of its DUAL L-form law and `inst` is `fun a b => op b a`; `theorem law` is stated for the L-form pattern, and `lhs` unfolds EquationLHS to exactly it. Prove `law` as stated.

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0012`: eq1 33020 = `x = (y * (((x * y) * z) * x)) * y` ⇒ eq2 28770 = `x = (((y * y) * y) * x) * (y * z)`   → judge with `python judge1.py <file> 33020:28770`, dev dir `python devrow.py 33020 28770`
- `research_order5_hard_0054`: eq1 33020 = `x = (y * (((x * y) * z) * x)) * y` ⇒ eq2 20034 = `x = (y * y) * ((z * (x * x)) * z)`   → judge with `python judge1.py <file> 33020:20034`, dev dir `python devrow.py 33020 20034`

Dual rows (law 12883, the dual of 33020) — build each with `dualcert.py` from your ACCEPTED certificate once it is accepted:
- `research_order5_hard_0031`: eq1 12883 = `x = y * ((x * (z * (y * x))) * y)` ⇒ eq2 30591 = `x = (y * (y * ((z * z) * x))) * y`   → `python dualcert.py <accepted.lean> 12883 12883 30591 gen/dual_12883_30591.lean` then `python judge1.py gen/dual_12883_30591.lean 12883:30591`
  (your `op` is the model of law 12883, so pass 12883 as the L_eq_id argument of dualcert.py)

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

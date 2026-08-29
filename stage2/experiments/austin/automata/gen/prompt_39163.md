# Assignment: law 39163 — `x = (((y * x) * (y * z)) * y) * y`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec39163.lean` (rules: `gen/rules39163.txt`, checker: `python gen/chk39163.py 3000`).
This law is R-FORM (x = A ◇ y). The skeleton's `op` is the free model of its DUAL L-form law and `inst` is `fun a b => op b a`; `theorem law` is stated for the L-form pattern, and `lhs` unfolds EquationLHS to exactly it. Prove `law` as stated.

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0002`: eq1 39163 = `x = (((y * x) * (y * z)) * y) * y` ⇒ eq2 22818 = `x = (y * (z * y)) * ((x * x) * y)`   → judge with `python judge1.py <file> 39163:22818`, dev dir `python devrow.py 39163 22818`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

# Assignment: law 38249 — `x = ((y * ((x * x) * z)) * y) * y`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec38249.lean` (rules: `gen/rules38249.txt`, checker: `python gen/chk38249.py 3000`).
This law is R-FORM (x = A ◇ y). The skeleton's `op` is the free model of its DUAL L-form law and `inst` is `fun a b => op b a`; `theorem law` is stated for the L-form pattern, and `lhs` unfolds EquationLHS to exactly it. Prove `law` as stated.

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0072`: eq1 38249 = `x = ((y * ((x * x) * z)) * y) * y` ⇒ eq2 22818 = `x = (y * (z * y)) * ((x * x) * y)`   → judge with `python judge1.py <file> 38249:22818`, dev dir `python devrow.py 38249 22818`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

# Assignment: law 40914 — `x = ((((y * x) * y) * z) * x) * z`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec40914.lean` (rules: `gen/rules40914.txt`, checker: `python gen/chk40914.py 3000`).
This law is R-FORM (x = A ◇ y). The skeleton's `op` is the free model of its DUAL L-form law and `inst` is `fun a b => op b a`; `theorem law` is stated for the L-form pattern, and `lhs` unfolds EquationLHS to exactly it. Prove `law` as stated.

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0016`: eq1 40914 = `x = ((((y * x) * y) * z) * x) * z` ⇒ eq2 4916 = `x = y * (x * (x * (y * (z * z))))`   → judge with `python judge1.py <file> 40914:4916`, dev dir `python devrow.py 40914 4916`
- `research_order5_hard_0023`: eq1 40914 = `x = ((((y * x) * y) * z) * x) * z` ⇒ eq2 28770 = `x = (((y * y) * y) * x) * (y * z)`   → judge with `python judge1.py <file> 40914:28770`, dev dir `python devrow.py 40914 28770`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

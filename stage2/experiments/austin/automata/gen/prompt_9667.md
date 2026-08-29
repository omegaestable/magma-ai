# Assignment: law 9667 — `x = y * ((z * y) * (x * (y * y)))`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec9667.lean` (rules: `gen/rules9667.txt`, checker: `python gen/chk9667.py 3000`).

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0071`: eq1 9667 = `x = y * ((z * y) * (x * (y * y)))` ⇒ eq2 25964 = `x = (y * ((x * x) * y)) * (z * z)`   → judge with `python judge1.py <file> 9667:25964`, dev dir `python devrow.py 9667 25964`

Dual rows (law 36638, the dual of 9667) — build each with `dualcert.py` from your ACCEPTED certificate once it is accepted:
- `research_order5_hard_0060`: eq1 36638 = `x = (((y * y) * x) * (y * z)) * y` ⇒ eq2 28770 = `x = (((y * y) * y) * x) * (y * z)`   → `python dualcert.py <accepted.lean> 9667 36638 28770 gen/dual_36638_28770.lean` then `python judge1.py gen/dual_36638_28770.lean 36638:28770`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

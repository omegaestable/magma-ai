# Assignment: law 23357 — `x = ((y * x) * y) * (x * (y * z))`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec23357.lean` (rules: `gen/rules23357.txt`, checker: `python gen/chk23357.py 3000`).

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0048`: eq1 23357 = `x = ((y * x) * y) * (x * (y * z))` ⇒ eq2 22455 = `x = (y * (x * x)) * ((y * z) * y)`   → judge with `python judge1.py <file> 23357:22455`, dev dir `python devrow.py 23357 22455`

Dual rows (law 23653, the dual of 23357) — build each with `dualcert.py` from your ACCEPTED certificate once it is accepted:
- `research_order5_hard_0080`: eq1 23653 = `x = ((y * z) * x) * (z * (x * z))` ⇒ eq2 22818 = `x = (y * (z * y)) * ((x * x) * y)`   → `python dualcert.py <accepted.lean> 23357 23653 22818 gen/dual_23653_22818.lean` then `python judge1.py gen/dual_23653_22818.lean 23653:22818`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

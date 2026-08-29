# Assignment: law 18137 — `x = (y * x) * (z * ((x * z) * z))`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec18137.lean` (rules: `gen/rules18137.txt`, checker: `python gen/chk18137.py 3000`).

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0042`: eq1 18137 = `x = (y * x) * (z * ((x * z) * z))` ⇒ eq2 25964 = `x = (y * ((x * x) * y)) * (z * z)`   → judge with `python judge1.py <file> 18137:25964`, dev dir `python devrow.py 18137 25964`

Dual rows (law 27863, the dual of 18137) — build each with `dualcert.py` from your ACCEPTED certificate once it is accepted:
- `research_order5_hard_0053`: eq1 27863 = `x = ((y * (y * x)) * y) * (x * z)` ⇒ eq2 30591 = `x = (y * (y * ((z * z) * x))) * y`   → `python dualcert.py <accepted.lean> 18137 27863 30591 gen/dual_27863_30591.lean` then `python judge1.py gen/dual_27863_30591.lean 27863:30591`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

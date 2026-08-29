# Assignment: law 6878 — `x = y * (y * ((z * x) * (x * y)))`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec6878.lean` (rules: `gen/rules6878.txt`, checker: `python gen/chk6878.py 3000`).

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0034`: eq1 6878 = `x = y * (y * ((z * x) * (x * y)))` ⇒ eq2 28770 = `x = (((y * y) * y) * x) * (y * z)`   → judge with `python judge1.py <file> 6878:28770`, dev dir `python devrow.py 6878 28770`

Dual rows (law 39126, the dual of 6878) — build each with `dualcert.py` from your ACCEPTED certificate once it is accepted:
- `research_order5_hard_0044`: eq1 39126 = `x = (((y * x) * (x * z)) * y) * y` ⇒ eq2 22455 = `x = (y * (x * x)) * ((y * z) * y)`   → `python dualcert.py <accepted.lean> 6878 39126 22455 gen/dual_39126_22455.lean` then `python judge1.py gen/dual_39126_22455.lean 39126:22455`
- `research_order5_hard_0075`: eq1 39126 = `x = (((y * x) * (x * z)) * y) * y` ⇒ eq2 30591 = `x = (y * (y * ((z * z) * x))) * y`   → `python dualcert.py <accepted.lean> 6878 39126 30591 gen/dual_39126_30591.lean` then `python judge1.py gen/dual_39126_30591.lean 39126:30591`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

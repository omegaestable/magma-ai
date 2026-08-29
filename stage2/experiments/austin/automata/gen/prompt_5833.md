# Assignment: law 5833 — `x = y * (x * (y * ((z * x) * y)))`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec5833.lean` (rules: `gen/rules5833.txt`, checker: `python gen/chk5833.py 3000`).

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0058`: eq1 5833 = `x = y * (x * (y * ((z * x) * y)))` ⇒ eq2 22818 = `x = (y * (z * y)) * ((x * x) * y)`   → judge with `python judge1.py <file> 5833:22818`, dev dir `python devrow.py 5833 22818`

Dual rows (law 40070, the dual of 5833) — build each with `dualcert.py` from your ACCEPTED certificate once it is accepted:
- `research_order5_hard_0084`: eq1 40070 = `x = (((y * (x * z)) * y) * x) * y` ⇒ eq2 17522 = `x = (y * z) * (x * (z * (z * z)))`   → `python dualcert.py <accepted.lean> 5833 40070 17522 gen/dual_40070_17522.lean` then `python judge1.py gen/dual_40070_17522.lean 40070:17522`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

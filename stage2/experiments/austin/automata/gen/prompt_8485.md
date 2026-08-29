# Assignment: law 8485 — `x = y * (x * (((z * x) * y) * y))`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec8485.lean` (rules: `gen/rules8485.txt`, checker: `python gen/chk8485.py 3000`).

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0096`: eq1 8485 = `x = y * (x * (((z * x) * y) * y))` ⇒ eq2 4916 = `x = y * (x * (x * (y * (z * z))))`   → judge with `python judge1.py <file> 8485:4916`, dev dir `python devrow.py 8485 4916`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

# Assignment: law 7701 — `x = y * (y * ((x * (z * x)) * y))`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec7701.lean` (rules: `gen/rules7701.txt`, checker: `python gen/chk7701.py 3000`).

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0094`: eq1 7701 = `x = y * (y * ((x * (z * x)) * y))` ⇒ eq2 15535 = `x = y * (((x * (z * z)) * y) * y)`   → judge with `python judge1.py <file> 7701:15535`, dev dir `python devrow.py 7701 15535`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

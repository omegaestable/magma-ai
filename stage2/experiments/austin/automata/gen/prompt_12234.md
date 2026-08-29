# Assignment: law 12234 — `x = y * (((z * x) * y) * (x * y))`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec12234.lean` (rules: `gen/rules12234.txt`, checker: `python gen/chk12234.py 3000`).

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0061`: eq1 12234 = `x = y * (((z * x) * y) * (x * y))` ⇒ eq2 22818 = `x = (y * (z * y)) * ((x * x) * y)`   → judge with `python judge1.py <file> 12234:22818`, dev dir `python devrow.py 12234 22818`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

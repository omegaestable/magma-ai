# Assignment: law 11280 — `x = y * ((y * (z * y)) * (x * y))`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec11280.lean` (rules: `gen/rules11280.txt`, checker: `python gen/chk11280.py 3000`).

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0092`: eq1 11280 = `x = y * ((y * (z * y)) * (x * y))` ⇒ eq2 25964 = `x = (y * ((x * x) * y)) * (z * z)`   → judge with `python judge1.py <file> 11280:25964`, dev dir `python devrow.py 11280 25964`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

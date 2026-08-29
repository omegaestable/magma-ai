# Assignment: law 5837 — `x = y * (x * (y * ((z * y) * y)))`

Skeleton: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rec5837.lean` (rules: `gen/rules5837.txt`, checker: `python gen/chk5837.py 3000`).

Rows of this law (all must be judged; the skeleton's `rhs` handles the first goal, copy the file and replace `rhs` for the others):
- `research_order5_hard_0021`: eq1 5837 = `x = y * (x * (y * ((z * y) * y)))` ⇒ eq2 22818 = `x = (y * (z * y)) * ((x * x) * y)`   → judge with `python judge1.py <file> 5837:22818`, dev dir `python devrow.py 5837 22818`
- `research_order5_hard_0045`: eq1 5837 = `x = y * (x * (y * ((z * y) * y)))` ⇒ eq2 25964 = `x = (y * ((x * x) * y)) * (z * z)`   → judge with `python judge1.py <file> 5837:25964`, dev dir `python devrow.py 5837 25964`

Copy every ACCEPTED certificate to `certs/<row id>.lean` (exact file the judge accepted).

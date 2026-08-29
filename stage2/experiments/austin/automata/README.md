# Tag-automaton models for the Austin research set (2026-08-28)

Infinite models of `x = T(x,y,z)` laws as *tag automata*: an inductive carrier
(generators + tag constructors, `J` = free product, `S` = square, …) with `op`
given by an ordered list of pattern rules with equality guards. Results and
the construction theory: `stage2/results/2026-08-28-austin-tag-automata.md`.

| File | Role |
| --- | --- |
| `laws.py` | parsing, catalog ids, duality (`ROOT` is hard-coded; edit for another checkout) |
| `symb.py` | **complete symbolic verifier** — `Model(tags, rules).verify(law)` returns the failing branches (0 = proof for every element of the carrier). Patterns: `'$v'` vars (repeats = equality checks), `(tag, …)`, `('AS','$v',sub)` whole-subterm binding, `('OP',p1,p2)` / `('OPB',name,p1,p2)` / `('A1',p)` recursive self-consistency checks (bounded unfolding, `max_op_depth`; sound over-approximation, currently blows up at depth 2) |
| `synth.py` | seeds + CEGIS repairs (projection / keep / *directed*), global best-first, `minimize`, `dual_model`, `good_orientation`, `synthesize_any` |
| `render2.py` | Lean certificate (binary case tree, `simp (disch := …) [op, eqf, *]` leaves) |
| `concrete.py` | ground evaluator + biased random tests |
| `batch.py` | `SYN_TIME=900 SYN_PROCS=8 SYN_SKIP=… python batch.py out.jsonl [eq1_id …]` |
| `pipeline.py` | `python pipeline.py batch.jsonl certs/ [eq1_id …]` — render every row of every model (best of 4 evaluation orders, duals included), bulk-judge, append `certs/ledger.jsonl` |
| `ship.py` | fixture lines + `DISTILLED_CERTS` entries from the ledger |
| `judge1.py` | `python judge1.py cert.lean <eq1_id>:<eq2_id>` — judge one certificate |
| `ledger.py` | accepted-row summary |
| `complete.py` | exact critical-pair completion (diverges on the hard family — kept as the measurement) |
| `semantic5107.py` | the semantic fixed-point model of 5107 (too slow as written; the concrete 4-rule recursive model that passes 3,000 biased tests is in the results doc) |
| `killbatch.py` | kill a batch driver *and* its spawned pool workers (rail 15) |

Run everything from this directory with the venv interpreter and
`PYTHONIOENCODING=utf-8`.

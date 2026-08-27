# Order-5 miss classification — 60-row sample, 2026-08-27

Measurement only; `solver.py` untouched. Data: `order5-classification-2026-08-27.jsonl`
(one line per row: z3 per-n results, verdict guess, verified table if any, prover results).
Script: `stage2/experiments/order5_classify.py` (6-process pool). Timing caveat: the user's
real Marathon run was on the machine throughout, so wall clocks are upper bounds.

Sample: 40 `collapse_candidate` + 20 `no_small_countermodel`, spread evenly through
`order5-sweep-20k-2026-08-25-ALL-failures.jsonl` (353 rows).

## z3 (uninterpreted `f` over 0..n-1, eq1 ground-enumerated, ¬eq2 as a disjunction; 60 s per call)

| bucket | n | result |
| --- | --- | --- |
| 40 collapse candidates | eq1 alone at n=2..7 | **40/40 unsat at every n it finished** — 29 unsat through n=7 (n=7 proof 0.3–49 s), 11 unsat through n=5/6 then z3 timeout. Not one has a finite non-trivial model ≤ 7. |
| 20 no_small_countermodel | eq1 alone | sat (non-trivial) at essentially every n; countermodel **unsat at n=2..6 on all 20** |
| 20 no_small_countermodel | countermodel n=7 | **3 sat** (`order5_33443_27657`, `order5_13566_47051`, `order5_32201_9330`), verified `witness_check` + `table_is_counterexample` |
| 16 unresolved | countermodel n=8 (180 s) | 8 unsat, 8 timeout, 0 found |

FP library (1048 teorth FinitePoly tables): 1 hit, `order5_39561_8027`, an order-8 table.

## Verdict tally

- **FALSE, verified: 4 / 60** (3 order-7 z3 tables + 1 order-8 FP table). Four *distinct*
  tables; nothing clusters, so nothing is shippable as a named witness. All are above the
  cheap constraint tier's orders (8,9,6,4,10 — note 7 is not in the list) and the wide
  tier at 45 s/order finds none of them.
- **TRUE by collapse, likely: 40 / 60** — every collapse candidate. The triage tag is
  vindicated: eq1 has no finite model of size 2..7 (proved for 29, ≤5/6 for 11).
- **16 / 60 open on the FALSE side**: eq1 has models at every order, no countermodel ≤ 7
  (≤ 8 for half of them). These need order ≥ 8/9 witnesses or are TRUE without collapse.

## Provers on the 40 collapse rows (target `x = y`, 120 s each)

| prover | collapse found |
| --- | --- |
| `solver.completion_prove(eq1, x=y)` (shipped caps 44/400) | **0/40**; 26 saturate in < 4 s |
| `solver.egg_saturate_prove(eq1, x=y)` | **0/40**; all burn the 120 s |
| kb2 dev tool, `max_size=60, max_active=2000` | **3/40** in 0.0 s / 0.5 s / 42.6 s; 15 saturate without a collapse, 22 hit the 120 s budget |
| `solver.completion_prove(eq1, **real eq2**, escalate=True)` (working-tree flag: 60/2000 after a cheap-cap saturation) | **3/40**, all kernel-verified: `order5_18399_29663` collapse 0.0 s 1,230 B; `order5_19979_28620` collapse 0.18 s 1,346 B; `order5_9327_53436` **join** 60.7 s 4,471 B |

The shipped route's instant "saturation" is a false floor: on `order5_18399_29663` kb2's 4th
processed equation is `((z◇z)◇z)◇((z◇z)◇z) = y` (a collapse) and it comes from critical pairs
of weight > 44, which `COMPLETION_MAX_SIZE = 44` drops on `push`. Escalated, the same
route closes it in 0.0 s. On the other 37, escalation costs 120 s each (22 budget-bound,
15 saturate at (60, 2000) too) — so this is a real but small lever (3/40 ≈ 7.5% of the
collapse bucket ≈ 19 of the 253 tagged rows, extrapolated) and its cost must be placed
after everything cheap.

## Recommendation (one engine change)

Ship `escalate=True` for `completion_route` (the tier-scaled slot, not the 2 s probe),
gated on "cheap-cap saturation with clock left" exactly as the working-tree code already
does, and cap the escalated pass at ~60–120 s. Evidence: 3/40 sampled collapse rows
closed and kernel-verified, 0 lost (escalation only runs after the cheap pass has
already failed), and the rows it wins are the ones z3 proves have no finite model — i.e.
rows that *no* FALSE search at any budget can ever claim. The sibling FALSE-side lever
(3 of 20 witnesses sit at order 7, which the cheap constraint tier never visits) is the
second candidate: add 7 to the cheap tier's order list, cheaper than any escalation.
What will **not** move the bucket: more egg budget (0/40 at 120 s), the LLM lane
(0/353), FP library (1/20 on the FALSE side only).

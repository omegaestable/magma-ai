# 2026-07-23 — spotcheck batches + the e-graph answer to the lemma-derivability wall

Two workstreams: the standing accuracy loop (four unseen mixed batches, all
clean), and the ranked-#1 frontier question — *why* small true lemmas are not
derivable — answered with evidence and a validated mechanism. No solver.py
changes (per the "only edit when sure" rail); the prototype and port plan are
staged for next session.

## 1. Standing accuracy loop — 4 batches, 358 rows, 0 mistakes

| Batch | Mix | Rows | Accuracy | Coverage |
| --- | --- | ---: | ---: | ---: |
| 1 | 8T+8F × 9 sources, `fast` | 144 | 100% | 92.4% |
| 2 | ETP-only 30T+30F (fresh pool) | 60 | 100% | 98.3% |
| 3 | hard2/hard3/eval_extra_hard/eval_order5 @ `standard` | 64 | 100% | 90.6% |
| 4 | default 5T+5F × 9 sources, `fast` | 90 | 100% | 95.6% |

Nothing pinned; `spotcheck_failures.jsonl` still empty. All skips safe.
Cumulative across sessions: ~1,500+ distinct rows, still zero wrong verdicts.

## 2. Where the TRUE frontier actually is (ETP explicit-path survey)

Labelled the 119 remaining `fast`-tier audit skips (67 TRUE / 52 FALSE;
`stage2/results/skips-2026-07-23.json`) and computed, for every TRUE miss, the
shortest path from eq1 to the goal through the ETP's **explicit-proof graph**
(`etp_paths.py` scratch; output `stage2/results/etp-paths-2026-07-23.json`):

- **Only 5 of 67 are one intermediate law away** (hops=2). The distribution
  runs 2→45 hops with the mass at 4–24. The frontier rows *provably* need long
  chains of individually-ATP-proved implications — that is the mathematical
  reason brute-force budget scaling has failed in four separate sessions.
- **Every hop-2 intermediate has a 4-op RHS** — just past the enumerated
  lemma library's 3-op cap. (But see §3: extending the library would NOT help.)
- Several paths pass through `Eq2: x = y` — those rows are singleton-collapse
  rows where `lemma_bootstrap:trivial` already aims at the right target and
  the closure simply cannot derive `a = b` (e.g. hard2_0073 needs 3 chained
  ATP edges *before* the collapse becomes derivable).
- Recurring-eq1 clusters worth knowing: Eq1057 (hard3_0134/0135,
  evaluation_hard_0178 — and ETP says **Eq1057 ⇒ Eq4, the left projection
  law**, so one derivation would pay 3 rows via `projection_bootstrap`'s
  existing goal check), Eq3577, Eq2307, Eq691, Eq853, Eq2521, Eq1367 (2 rows
  each).

## 3. The oracle-pivot experiment — closure power, not candidate generation

`oracle_pivot_test.py` (scratch) injected the ETP-known intermediates as
lemma-chain helpers, exactly mirroring `lemma_chain_bootstrap_route`'s
`extra_rules` path, with 8 s per closure call:

- **The closure failed every genuine explicit edge it was handed** — the only
  two first-hops it derived were trivial substitution instances of eq1
  (Eq1506[z:=y]=Eq1491, Eq3067[y:=x]=Eq3051), and even then the follow-on
  step failed.
- Conclusion, sharper than session 2's "0 of 7 at 22x budget": **even with a
  perfect oracle for *which* lemma to aim at, the closure cannot traverse one
  ATP edge.** Widening the lemma library to 4 ops is measured-dead before
  building it; the binding constraint is closure power.

## 4. Why: the actual ETP proofs are equality saturation

`full_entries.json` names the theorem for Eq1057 ⇒ Eq4:
`Generated/MagmaEgg/small/_004.lean` — **egg**, the e-graph equality-saturation
tool. Fetched and decoded the proof (scratch `magmaegg_004.lean`): it
instantiates eq1 at composite ground terms built from the goal's own two
variables — `v3 = x◇y`, `v4 = x◇v3`, `v9 = y◇v4` (note: *every auxiliary is a
product of two earlier terms*) — with 7-op intermediate terms shared in an
e-graph. Two structural reasons our engines cannot find this:

1. `derived_cp_closure` is a **bidirectional whole-term path search** with
   `term_slack` size caps; the proof's intermediates are far larger than
   goal+slack, and without sharing, the frontier explodes exactly as the caps
   predict.
2. Critical-pair rules only unify rule subterms — they never *enumerate ground
   instantiations* like `h v4 x v9`, which is the move every MagmaEgg proof
   makes.

## 5. Mini-egg prototype — mechanism validated

`mini_egg2.py` (scratch): ground e-graph (union-find + hashcons + batched
rebuild congruence closure), eq1 applied by e-matching; bare-var expansions
restricted to a pool grown as the *product-closure of goal subterms* (the
MagmaEgg auxiliary-term pattern), cheapest instantiations first.

Against the 9 single edges the CP closure failed in §3 (≤20 s each, pure
Python):

| Edge | mini-egg | CP closure |
| --- | --- | --- |
| Eq1491⇒Eq359 | **YES** (0.0 s) | no |
| Eq3561⇒Eq3577 | **YES** (1.7 s) | no |
| Eq2666⇒Eq2860 | **YES** (2.1 s) | no |
| Eq1703⇒Eq2113 | **YES** (11 s; genuine singleton collapse — `a=b` holds in every small Eq1703-model) | no |
| Eq1057⇒Eq4, Eq2398⇒Eq2567 | no — Python e-match speed bound (2–5 rounds/20 s) | no |
| Eq1695⇒Eq1932, Eq2042⇒Eq2893, Eq3051⇒Eq3082 | no — pool-policy bound (search stalls) | no |

**Negative control: 25 random ETP explicit-FALSE pairs, 0 false positives** —
the congruence machinery does not unsoundly merge.

Saturation-only so far (no proof extraction). Proof extraction is mechanical
(egg-style proof forest → the same T/S/C/h-instance grammar the kernel already
checks) and is the port's main work item.

## 6. What this buys: 29 of the 67 remaining TRUE misses (measured)

Aimed the saturation directly at each actual missed goal (20 s/row, 6
workers, `egg_real_rows.py`): **29/67 proved** — 22 official (hard2 ×6,
hard3 ×10, normal ×6) + 7 HF. Wins include rows whose ETP explicit path is
9–11 hops (`hard2_0137`, `hard2_0153`) — saturation does not follow the
path, it just merges ground terms. The 29 ids:
hard2 0008/0021/0028/0070/0137/0153;
hard3 0134/0135/0168/0176/0187/0193/0202/0208/0232/0353;
normal 0144/0161/0256/0492/0917/0927; evaluation_hard_0140;
evaluation_normal 0036/0094/0108; evaluation_order5 0022/0080/0142.

These are saturation claims, not certificates yet — the port's proof
extraction + kernel check is the gate before any is counted. All 29 are
TRUE-labelled (cross-checked), consistent with the 0/25 FALSE control.

- Port cost estimate: EGraph core (~150 lines, exists) + proof-forest
  extraction (~200 lines) + route wiring/certs/oracle dispatch. The
  certificate shape can be plain `exact_expr` (a single big T/S/C
  composition) — already kernel-checkable, no new oracle surface.
- Prototype promoted to `stage2/experiments/egg_saturation.py` (+
  `egg_real_rows.py`, `egg_false_controls.py`) so next session starts from
  working code, not scratch.

## 6b. Shipped the same session: `true:egg_closure`

Built proof extraction and shipped the engine into `solver.py`
(`egg_saturate_prove`, `egg_closure_route`, placed last among TRUE engines).

**How the proof is produced and why it is trustworthy.** The e-graph keeps a
proof forest — one edge per class merge — where a *rule* edge records the
`h`-instance that justified it and a *congr* edge records a shared top op with
pairwise-merged children. When the goal sides land in one class, a BFS between
them yields an explanation; congruence edges expand recursively into
single-position rewrites. That raw explanation is long (it walks the whole
merge history — 2,376 steps for one row), so two sound passes shrink it: a
**cycle cut** (drop everything between two visits of the same term state) and
a **greedy bridge** (jump to the farthest later state reachable in one eq1
rewrite), iterated to a fixpoint — 2,376 → 222 steps on that row. Finally the
renderer **replays every step syntactically** against the concrete term before
emitting a single character; any mismatch discards the whole proof. So a bug
anywhere upstream fails closed. The certificate is a balanced `.trans` tree of
`congrArg`-wrapped `h`-instances — plain `exact_expr`, checked by the existing
`ProofKernel` with **no new oracle surface**.

**Two engineering facts worth keeping.** (1) A registered term's class is
authoritative; re-deriving it bottom-up between rebuilds reads a stale
hashcons key and spawns a duplicate class — this silently broke saturation
parity with the prototype until the `term_class` fast path was added. (2) The
real judge's code cap is **50,000 bytes** (`vendor .../judge/verify.py`), not
the solver's 100,000 `MAX_LEAN_CODE_BYTES`; a 59,820-byte cert was rejected
`malformed` while a 48,526-byte one passed. The route caps proofs at 46 KB and
certs at 49.5 KB.

**Validation.**
- Offline kernel: **21–23 of the 67 frontier TRUE rows** extract and verify
  (run-to-run drift from the same wall-clock races the other closure engines
  have; the golden gate collapses closure families for exactly this reason).
- Real local Lean judge: a 9-cert size ladder from 700 B to 48 KB —
  **8/9 accepted**, the one failure being the 59.8 KB cert now excluded by the
  byte cap. Certs of every size in-cap passed.
- Negative control: **0/25** ETP-FALSE pairs produce a proof, through the full
  extract+render path.
- `pytest stage2/tests/test_primitives.py`: 59 passed. Full audit / golden
  regen / spotcheck / package: see the addendum once complete.

### Addendum — full official audit with the shipped route

Official corpus at `fast` tier (`audit-2026-07-23-egg.json`) vs the session-4
baseline. Compare TRUE, not solved (FALSE carries the ±7 timing band):

| Set | Solved | TRUE | was TRUE |
| --- | ---: | ---: | ---: |
| `hard1` | 64/69 | 24 | 24 |
| `hard2` | 177/200 | 92 | 87 |
| `hard3` | 387/400 | 183 | 177 |
| `normal` | 989/1000 | 490 | 485 |
| **Total** | **1617/1669** | **789** | **773** |

**+16 official TRUE, zero oracle failures.** Attribution: **`true:egg_closure`
fired on 13 rows — 12 of them previously `skip` (genuine new coverage), all
oracle-clean**; the remaining 4 of the +16 are `lemma_chain`/`derived_cp`
rows flipping skip→solved on the run-to-run timing band, not egg. This is the
`fast`-tier (10 s/row) figure under 16-worker contention; Solo runs the egg
route at `standard`/`deep` (75–220 s), where the prototype reached 21–23 of
these rows, so the deployed Solo ceiling is higher than this audit shows.

HF evaluation sets (`audit-hf-2026-07-23-egg.json`, 8 workers):

| Set | Solved | TRUE | was TRUE |
| --- | ---: | ---: | ---: |
| `hf_evaluation_extra_hard` | 170/200 | 100 | 100 |
| `hf_evaluation_hard` | 198/200 | 98 | 96 |
| `hf_evaluation_normal` | 198/200 | 98 | 95 |
| `hf_evaluation_order5` | 188/200 | 88 | 88 |
| **Total** | **754/800** | **384** | **379** |

**+5 HF TRUE, egg fired 4 times (3 new coverage), zero oracle failures.**
Combined: **+21 TRUE across official+HF, 15 direct egg wins, 0 oracle
failures on all 2,689 problems.**

### Golden fixture: a selection fix the port surfaced

The first gate run after the port failed on exactly one row — `hard2_0082`,
a `true:lemma_chain:enum319` win that solved at its 10.0 s budget ceiling
(9.0–10.2 s standalone) and tipped over under the loaded gate. Not an egg or
solver defect: `make_golden` grouped candidates by the *full* route label, and
`lemma_chain:enum319` is a unique per-library-index label, so that one
budget-marginal row got force-pinned with no faster alternative. Fixed
`make_golden` to group by route *family* (as `test_golden.route_family`
already does) and pin the fastest representatives per family — so every engine
stays covered but marginal singletons are replaced by rows with budget
headroom. New fixture: 136 entries / 70 labels / 52 families; all 136 re-solve
with 0 skips / 0 drift under an 8-worker parallel stress (a harsher load than
the gate). `egg_closure` stays excluded (wall-clock nondeterministic, last).

## 6c. Real rounds — end-to-end through the actual Lean judge

Offline-kernel and spotcheck evidence is necessary but the playground scores a
real Lean `accepted`. `stage2/experiments/real_rounds.py` runs the full
playground path — `solve_problem` → strip to `{verdict, code}` →
`judge.verify.verify_answer` with the production proof policy — and reports
acceptance. Two rounds:

| Round | Rows | Submitted to Lean | **Accepted** | Rejected | Wrong verdict |
| --- | ---: | ---: | ---: | ---: | ---: |
| Broad mixed (fresh, 9 sources, `fast`) | 54 | 50 (27 TRUE / 23 FALSE) | **50** | 0 | 0 |
| Egg frontier (67 TRUE misses, `fast`) | 67 | 19 | **19** | 0 | 0 |
| **Total** | 121 | 69 | **69** | 0 | 0 |

**Every certificate the solver emitted was accepted by the real Lean judge;
none were rejected; no wrong verdict was ever submitted.**

The egg round is the one that matters for this session: **18 of the 18
`true:egg_closure` certificates it produced were accepted by the real Lean
judge** — rows the pre-egg solver could not touch at all — with certificates
spanning **480 bytes to 34.9 KB** and Lean compile times of 2.6–4.8 s. This is
the end-to-end confirmation that the extraction produces genuine Lean proofs,
not just offline-kernel-valid ones. (Only 19/67 solved at `fast` tier; the 48
skips are budget, not soundness — Solo runs egg at `standard`/`deep`.)

One transient failure worth noting: running both rounds concurrently at
`standard` effort oversubscribed the machine and the judge's `lake env`
LEAN_PATH probe timed out (30 s). Not a cert defect — the harness now isolates
per-row judge-infra errors, and the egg round rerun alone was clean.

## 7. Rails for the port (carried out this session)

1. Build proof extraction **first**, offline, and validate every extracted
   proof through `oracles.ProofKernel` on the known-YES edges before any
   solver wiring.
2. Route placement: last, after `lemma_chain` (pure addition, no drift), armed
   only when the deterministic pass has budget left; it must respect
   `local_deadline`/`memory_exceeded` like the other deep engines.
3. Re-run the FALSE-pair negative control at production budgets; add a
   spotcheck-style battery to the gate.
4. Do not delete or demote any existing route on the strength of this — the
   e-graph is additive coverage (2026-07-21 rail).

## Artifacts

- `stage2/results/skips-2026-07-23.json` — labelled current misses (gitignored
  like other results JSON; regenerate from the session-4 audits).
- `stage2/results/etp-paths-2026-07-23.json` — explicit-path chains.
- Scratchpad (session-local): `etp_paths.py`, `oracle_pivot_test.py`,
  `mini_egg.py`, `mini_egg2.py`, `mini_egg_controls.py`,
  `mini_egg_real_rows.py`, `magmaegg_004.lean`.

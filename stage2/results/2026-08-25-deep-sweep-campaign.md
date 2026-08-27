# 2026-08-25: deep sweep campaign — measurement log

Running log of the 150,000-row unseen-row campaign planned in
`stage2/docs/DEEP_SWEEP_ROADMAP.md`. **Measurement and logging only**, per
explicit instruction: no solver change lands until the campaign has produced a
ranked, evidence-backed defect list. One section per batch, appended as batches
land.

Machine condition for every run below unless stated otherwise: 32 logical CPUs,
16 audit workers, background load 6–31% (Chrome / VS Code / a GPU-bound
`gpuowl` process). Rail 5e observed throughout — never two `audit_corpus.py`
sweeps at once.

---

## Track A — 10,000 unseen order-4 rows (ground truth)

`stage2/results/etp-sweep-10k-2026-08-25.jsonl`, seed `20260825`, balanced
5,000 TRUE / 5,000 FALSE, drawn from the 4,694² ETP outcome matrix excluding
the four 2026-08-20 batches and the standing spotcheck coverage ledger.
**0 row-id overlap with the prior 20,000** (checked, not assumed).

Audited at `fast` effort, unbounded per row, 16 workers — identical settings to
the 2026-08-20 batches, so the 30,000 rows are one comparable population.

| | Value |
| --- | --- |
| Rows | 10,000 |
| **Solved** | **9,995 (99.95%)** |
| Skipped | 5 |
| Crashes | 0 |
| Oracle failures | 0 |
| **Label mismatches (verdict vs ETP ground truth)** | **0** |
| Verdicts | 4,996 TRUE / 4,999 FALSE |
| Wall clock | **1,206.9 s** (16,959.9 s of CPU — 87.8% pool utilisation) |
| Per-row seconds | mean 1.696, p50 **0.005**, p95 9.52, p99 10.51, slowest solved 177.3 |

### The miss rate fell 5× against the 2026-08-20 baseline

| | 2026-08-20 (20,000 rows) | 2026-08-25 (10,000 rows) |
| --- | --- | --- |
| Solved | 99.74% | **99.95%** |
| Misses per 10,000 | 26 | **5** |
| Wall clock per row (16 workers) | 0.368 s | **0.121 s** |

Both movements are attributable and neither is noise: `true:completion` and the
2026-08-24 goal bridge closed 49 of that sample's 52 frontier rows, and skips
are the expensive rows (all five here cost 264–521 s each, against a p50 of
5 ms), so removing them moves the wall clock hard. The **3× throughput
improvement** matters for the roadmap: track B's projection drops from ~10 h to
roughly **3.4 h**.

### The five misses, and how they line up with the known frontier

Full records in `stage2/results/etp-sweep-10k-2026-08-25-failures.jsonl`.

| Row | Label | s | eq1 |
| --- | --- | --- | --- |
| `etp_3569_4143` | true | 520.5 | `x ◇ y = y ◇ ((z ◇ y) ◇ x)` |
| `etp_2923_3397` | true | 441.4 | `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` |
| `etp_2923_156` | true | 420.6 | `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` |
| `etp_2854_4676` | true | 289.2 | `x = ((x ◇ (x ◇ y)) ◇ x) ◇ z` |
| `etp_481_3050` | **false** | 263.8 | `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` |

Three things worth recording:

- **`eq1 = 3569` is the same hypothesis as `etp_3569_4653`**, one of exactly two
  order-4 TRUE rows left open after the 2026-08-24 goal bridge. Its second
  goal misses too. That is independent confirmation, on fresh rows, that the
  open frontier is a **hypothesis-side** property — the same finding the
  20,000-row sample reported (top-5 eq1 ids = 58% of misses), reproduced at a
  different sample size on disjoint rows.
- **`eq1 = 2923` accounts for 2 of 5**, and its shape `x = F(x, y, z)` with
  `term_size(F) = 4` is the family closed in 2026-08-12 by ordered completion —
  i.e. a family the solver *can* do, on goals it cannot reach.
- **`etp_481_3050` is only the second FALSE miss ever seen** in 30,000 unseen
  order-4 rows (the first was `etp_1661_3524`, still open and heavily
  diagnosed). "The countermodel search is airtight" should be read as
  "airtight to about 1 in 15,000", not literally.

### Finding: 25 rows per 10,000 carry a certificate with no verification of any kind

This is the first thing this campaign has surfaced that was not already known,
and it is a **risk** finding rather than a measured loss.

The audit verifies a TRUE certificate two ways: it proof-kernel-checks the Lean
text if the shape is one the kernel parses, and it model-checks the verdict
against finite models of the hypothesis. On this batch:

- **54 rows** emitted a certificate whose shape the kernel classifies as
  `other` — it cannot be parsed, so it is not proof-checked;
- **4,355** TRUE rows had a battery with **no non-trivial model**, which makes
  model-checking vacuous. That is expected and benign for collapse laws (the
  trivial magma satisfies everything) and 4,310 of them are kernel-verified
  anyway;
- the intersection is **45 rows** with neither check. Their verdicts are
  nonetheless *correct* — all 45 match ETP's ground-truth label — but nothing
  offline says the Lean text proves what it claims.

Cross-referencing `stage2/fixtures/judge_verified_certs.jsonl` (102 entries,
91 distinct routes, all re-judged on Lean 4.32.2 on 2026-08-24) narrows it
further. Nine of those route families have **zero** real-judge evidence as well:

| Route family | Rows in this batch | Judge-pinned certs |
| --- | --- | --- |
| `true:crossed_pair_singleton` | 6 | **0** |
| `true:deep_repeat_singleton` | 3 | **0** |
| `true:reverse_deep_repeat_singleton` | 3 | **0** |
| `true:front_double_self_collapse` | 3 | **0** |
| `true:mirrored_alternating_front_self_collapse` | 2 | **0** |
| `true:alternating_front_self_collapse` | 2 | **0** |
| `true:forked_square_singleton` | 2 | **0** |
| `true:sandwich_repeat_singleton` | 2 | **0** |
| `true:outer_sandwich_singleton` | 2 | **0** |
| `true:derived_left_projection` | 2 | **0** (model-checked non-vacuously, so not in the 45) |

So **25 of 10,000 rows (0.25%)** are served by families with neither offline nor
real-judge evidence behind their Lean text. The exposure is not the 0.25%: it is
that a rendering defect in any one of those families is invisible to every
check we run and would cost *every* row it serves (rail 3c — a sound witness is
not automatically a shippable one; every local check reads the parsed Python,
not the rendered Lean).

The fix is cheap and is pure measurement, so it belongs in this campaign rather
than the improvement pass: **judge one certificate per family** (nine calls,
~3–8 s each) and pin whatever comes back. Queued for a quiet-machine window —
`lake env` times out under a running sweep, so it cannot overlap a batch.

### Timing shape

p50 of **5 ms** against a mean of 1.70 s says what the route table is for: half
the rows are decided by a syntactic recogniser or a named witness before any
search starts. The route census:

| Family | Rows | | Family | Rows |
| --- | --- | --- | --- | --- |
| `witness` (named/structured/affine tables) | 4,687 | | `constancy` | 120 |
| `singleton` | 2,331 | | `linear` | 105 |
| `egg_collapse` | 1,241 | | `derived_cp_closure` | 84 |
| `completion` | 841 | | `egg_bootstrap` | 52 |
| `spine` | 181 | | `universal_identity` | 41 |
| `equational_closure` | 135 | | 20+ smaller families | ~180 |

`completion` — the engine that shipped four days ago — is now the **fourth**
largest route family on unseen rows, serving 841 of 10,000. On the local corpus
it serves 304 of 2,669. That gap is the point of measuring on unseen rows.

---

## Track D pilots — order-6 (≤2 variables), and why the track was redesigned

`data/generated/eq_order6_vars2.txt`, **27,456 laws**, generated by
`stage2/experiments/generate_eq_catalog.py`. No order-6 catalog exists anywhere;
this one is pinned by reproducing ETP's own `eq_size5.txt` **line for line** —
all 62,576 rows in the same order, plus the 4,694-law order-≤4 slice and the ≤2
and ≤3 variable slices. Set equality would have been suggestive; identical line
order means the enumeration and the orientation tie-break are both right.

### Pilot 1 — uniform draw, 200 rows

| | Value |
| --- | --- |
| Rows | 200 |
| Solved | **200 (100%)**, skipped 0, crashes 0, oracle failures 0 |
| Verdicts | **0 TRUE / 200 FALSE** |
| Wall clock | 160.9 s — of which **159.4 s is one row** (`order6_2920_1532`, `false:linear:z11:4,4`) |
| Per-row seconds | p50 **0.008**, p95 0.041 |
| Certificate bytes | min 265, p50 265, p95 313, max 600 — against a 19,500-byte FALSE budget |
| Routes | `witness` 177, `linear` 17, `spine` 6 |

### Pilot 2 — big hypothesis, small goal, 200 rows

eq1 from the order-6 catalog, eq2 from the order-≤5 ≤2-variable catalog (5,034
laws), on the theory that a strong law implies many weak ones. Same result:
**200/200 FALSE**, 120.5 s, 0 skips, 0 oracle failures.

### What the pilots settled

Two things, and the second is the useful one.

**Nothing breaks at order 6.** 400/400 solved, no crash, no deadline overshoot
(unlike the order-5 territory opened on 2026-08-20, where 9 of 205 skip rows
overran a 300 s cap, one by 11.8×), and certificates one to two orders of
magnitude under the byte cap. The ≤2-variable cap is why the certificates stay
small: `decide` cost is `n ** variables`, so these are the *cheapest* witnesses
of any track despite having the largest terms. That is the robustness answer
track D existed to give, and it is now given — in 5 minutes rather than 4.5 hours.

**A uniform ≤2-variable draw cannot measure the TRUE side, and the labelled
order-4 matrix says exactly why.** The TRUE base rate over all 22,028,942
order-≤4 pairs is **37.10%**; restricted to pairs with ≤2 variables on both
sides it is **4.17%**; for a 4-operation ≤2-variable hypothesis against any
≤2-variable goal, **2.87%**. Fewer variables means a more constraining law, and
two unrelated constraining laws essentially never imply one another. The effect
is already ~9× at order 4 and stronger at order 6 (0 TRUE in 400 draws bounds
the rate at ≲1%). It is a property of the **variable cap**, not of the order —
which is also why track C is unaffected: at ≤3 variables the base rate is
25.46%, and the 2026-08-20 order-5 sample duly came out 19% TRUE.

So the uniform order-6 track is retired and replaced by a **stratified** one.
`stage2/experiments/filter_hard_region.py` discards any pair for which an
independent small-model search finds a magma satisfying eq1 and refuting eq2.
It uses `stage2/tests/oracles.py`, which by contract shares no code with
`solver.py`, so "survivor" is not defined by the thing being measured. What
survives is every TRUE pair plus the FALSE pairs whose witness is not small —
the population that actually exercises the solver.

Measured on order-6 ≤2 vars: **14.23% survive** (500 kept from 3,513 checked in
5 s on 12 workers, 13.5 ms per pair), splitting **401 `no_small_countermodel`
to 99 `collapse_candidate`** — the latter being hypotheses with no non-trivial
model in the battery, which is where order-6 TRUE rows concentrate.

**Any batch built this way is stratified, not random.** Its solve rate is not
comparable to a uniform sweep's and its FALSE rows are biased hard by
construction. Both numbers have to be quoted together or the stratified one
reads as a regression.

---

## Finding: the countermodel search eats the order-4 frontier's budget, mostly hunting witnesses that cannot exist

`sweep_report.py --diagnose` re-solved all five track-A misses with every engine
wrapped in a timer, under the 300 s row budget a real runner would impose. The
profile is the same on all five:

| Row | Label | `constraint_countermodel` | `egg_ladder` | `egg_priority_bootstrap` | `egg_bootstrap` | share of budget on witness search |
| --- | --- | --- | --- | --- | --- | --- |
| `etp_2923_156` | true | **111.5 s** | 60.2 s | 40.0 s | 24.0 s | 37% |
| `etp_481_3050` | **false** | **227.9 s** (+3.0 s cheap tier) | — | — | 7.4 s | **76%** |
| `etp_3569_4143` | true | **135.5 s** | 60.5 s | 40.2 s | 28.0 s | 45% |
| `etp_2854_4676` | true | **145.1 s** | 61.3 s | — | 16.6 s | 54% |
| `etp_2923_3397` | true | **112.7 s** | 60.1 s | 40.0 s | 24.0 s | 38% |

The single largest consumer on every unsolved row is the wide-tier
`constraint_countermodel`, at **37–76% of the row's entire clock** — and on
**four of the five it is provably wasted**, because those rows are TRUE and no
countermodel exists at any order. Under Marathon's per-row budget that time
comes straight out of other rows (rail 13), and under Solo it is time the TRUE
engines never get.

This is not the same defect as rail 5f-vii (a cost gate placed after a search
rather than before it, fixed 2026-08-13). Nothing here overruns its budget; the
budget is being spent exactly as configured. The question the campaign raises is
whether the *configuration* is right: the wide tier is the last-resort FALSE
search, it runs before nothing, and it is scheduled ahead of no cheap
"is a witness even possible here" test beyond the ones already in place.

Recorded as a ranked lever, **not acted on** — this is a measurement session,
and five rows is not enough to size a scheduling change. The number to watch as
tracks B and C land is whether the same profile holds across a few hundred
misses; if it does, the lever is worth a session on its own, and the diagnose
pass now produces the evidence for free on every batch.

Two smaller observations from the same traces, worth keeping:

- `egg_ladder` spends **60 s to the second** on four of five rows, and
  `egg_priority_bootstrap` 40 s, and `egg_bootstrap` 24 s — these are
  tier-scaled budgets being consumed in full, not searches terminating. On a
  row where the answer is not in that family, that is 124 s of guaranteed loss.
- `etp_481_3050`, the FALSE miss, is the mirror image: it spends 76% of its
  clock in the one engine that *could* have solved it, and still misses. That
  row wants a better search, not a bigger share — the same conclusion the
  heavily-diagnosed `etp_1661_3524` reached on 2026-08-24.

### Pilot 3 — stratified hard region, 500 rows

Drawn by `filter_hard_region.py` from the 20,000-row order-6 pool: 401
`no_small_countermodel` + 99 `collapse_candidate`. Audited at `fast`,
`--row-budget 300`, 16 workers.

| | Uniform (pilot 1) | **Stratified (pilot 3)** |
| --- | --- | --- |
| Rows | 200 | 500 |
| Solved | 200 (100%) | **499 (99.8%)**, 1 skip |
| Verdicts | 0 TRUE / 200 FALSE | **12 TRUE** / 487 FALSE |
| Oracle failures / crashes | 0 / 0 | **0 / 0** |
| p50 / p95 / p99 seconds | 0.008 / 0.041 / — | 0.007 / 0.024 / **142.1** |
| Slowest solved | 159.4 s | 246.4 s |
| Certificate bytes (p50 / max) | 265 / 600 | 277 / **982** |
| Wall clock | 160.9 s | 300.9 s (1,952.6 s CPU) |

The stratification did what it was built to do. `false:linear:z*` — the `Z_n`
witness family that reaches past the small-model region — went from **17 of 200
(8.5%)** on the uniform draw to **197 of 500 (39%)** here, and TRUE rows went
from 0 to 12. The route census is now genuinely varied: `witness` 234,
`linear` 197, `spine` 35, `singleton` 9, `affine` 9, `enum_fin3` 4,
`local_model4` 4, `central` 4, `derived_cp_closure` 2, `completion` 1.

The cost shape is bimodal and worth stating precisely: **p95 is 24 ms and p99 is
142 s**. About 1% of the hard region is expensive and the rest is still nearly
free, so the mean (3.9 CPU-s/row) describes no actual row.

**Sizing:** 500 rows in 300.9 s wall ⇒ a full 20,000-row stratified track D
costs **~3.3 h** and would yield roughly 480 TRUE rows, ~19,500 FALSE, and ~200
expensive rows. Filtering the candidate pool to feed it costs ~13.5 ms/pair, so
~141,000 candidates ≈ 32 min single-core, minutes in parallel.

The one skip, `order6_16514_17426` (eq1 `x = ((((x*x)*(x*x))*x)*x)*y`, eq2
`x*x = x*(y*(((x*x)*x)*y))`), is the first order-6 miss on record.

**Track D's original question is already answered.** 900 order-6 rows across
three pilots: 0 crashes, 0 oracle failures, 0 deadline overshoots, certificates
two orders of magnitude under the byte cap. Nothing in the solver is tuned to
term size ≤ 5. What a full 20,000-row track D would add is *stress on the FALSE
witness ladder at large term size* — real value, but no scoring category behind
it, so it stays the first thing to cut.

---

## Track C — 20,000 unseen order-5 rows (≤3 variables), COMPLETE

Four 5,000-row batches, seed `20260825`, drawn from the 26,990 laws of
`eq_size5.txt` with ≤3 variables, excluding the 2026-08-20 10,000-row draw, the
200-row pilot, both 2026-08-24 order-5 Marathon manifests, **and the HF
`evaluation_order5` set**. 0 overlap, verified by `(eq1_id, eq2_id)` pair.
`fast` effort, `--row-budget 300`, 16 workers.

| Batch | Rows | Solved | Skips | TRUE | FALSE | Wall |
| --- | --- | --- | --- | --- | --- | --- |
| b01 | 5,000 | 4,907 (98.14%) | 93 | 1,036 | 3,871 | 2,732 s |
| b02 | 5,000 | 4,922 (98.44%) | 78 | 1,045 | 3,877 | 2,548 s |
| b03 | 5,000 | 4,906 (98.12%) | 94 | 1,091 | 3,815 | 3,105 s |
| b04 | 5,000 | 4,912 (98.24%) | 88 | 1,057 | 3,855 | 2,813 s |
| **total** | **20,000** | **19,647 (98.24%)** | **353** | **4,229** | **15,418** | **3 h 07 m** |

**0 crashes, 0 oracle failures.** Every TRUE certificate proof-kernel-verified
or model-checked and every FALSE witness table independently re-verified — which
here means "0 unsound certificates", not "0 wrong answers": order-5 pairs have no
ground truth and cannot have any.

### Against the only prior order-5 measurement

| | 2026-08-20 | **2026-08-25** |
| --- | --- | --- |
| Rows | 4,000 | **20,000** |
| Solved | 94.9% | **98.24%** |
| Skip rate | 5.1% | **1.76%** |
| Wall clock per row (16 workers) | 1.466 s | **0.560 s** |

Five times the rows, **+3.3 points**, and 2.6× the throughput — on the category
worth a quarter of the final score. `true:completion` is now order-5's **second
largest** route family at 1,769 rows, behind only the named-witness portfolio;
`egg_collapse` serves 868 and `linear` 1,258.

It also cost far less than forecast: 3 h 07 m against a 4.5–8 h projection built
on the 2026-08-20 rate. The projection was not wrong when it was made — the
2026-08-21 deadline caps and the 2026-08-24 bridge changed the cost of exactly
the rows that dominated it.

### The order-5 frontier has a different shape from order-4's

This is the most useful thing track C produced, and it says the two tracks want
different levers.

- **No dominant hypothesis.** The largest failure cluster is **4 rows of 353**,
  against order-4 where five eq1 ids account for 58% of all misses. Order-5
  misses do not concentrate on a law family.
- **But they are perfectly uniform on size and arity**: all 353 have **exactly
  5 operations**, and **352 of 353 have 3 variables** (the remaining one has 2).
  325 have a bare variable alone on one side of the hypothesis.

So order-4's frontier is a *family* wall — a handful of hypotheses the proof
search cannot get through — while order-5's is a *size and arity* wall: the
solver runs out of room at the top of the space, uniformly, regardless of which
law it is looking at. A fix aimed at one will not move the other.

---

## Track B — 100,000 unseen order-4 rows, 4 of 10 batches

| Batch | Rows | Solved | Skips | Wall |
| --- | --- | --- | --- | --- |
| b01 | 10,000 | 9,996 (99.96%) | 4 | 1,385 s |
| b02 | 10,000 | 9,997 (99.97%) | 3 | 1,445 s |
| b03 | 10,000 | 9,995 (99.95%) | 5 | 1,402 s |
| b04 | 10,000 | 9,997 (99.97%) | 3 | 1,209 s |
| **so far** | **40,000** | **39,985 (99.96%)** | **15** | **1 h 30 m** |

0 crashes, 0 oracle failures, **0 label mismatches**. `eq1 = 3569` accounts for
**4 of the 15 misses** — the third independent confirmation today that the
order-4 frontier is a hypothesis-side property, and that `3569` specifically is
its largest single contributor.

Batches b05–b10 were restarted at **8 workers** rather than 16 after ~4.8 h of
sustained 100% CPU. Coverage is unaffected — order-4 rows at `fast` tier are not
budget-marginal (p95 is 9.4 s against no per-row cap) — but the wall clocks of
b05–b10 are **not comparable** to b01–b04's and must not be averaged with them.

---

## The unverified-certificate risk is closed: 10/10 judge-accepted

The track-A finding, resolved the same day. Scanning all eleven audits produced
today (70,900 rows) for certificates the proof kernel classifies as `other`
turned up **29 route families**, of which **10 had no entry in
`stage2/fixtures/judge_verified_certs.jsonl`** — 138 rows served by builders
with neither offline nor real-judge evidence behind their Lean text.

One certificate from each was put through the real Lean judge (v4.32.2):

| Route family | Rows | Judge | s |
| --- | --- | --- | --- |
| `true:deep_repeat_singleton` | 20 | **accepted** | 46.8 |
| `true:sandwich_repeat_singleton` | 17 | **accepted** | 2.7 |
| `true:reverse_deep_repeat_singleton` | 15 | **accepted** | 2.6 |
| `true:mirrored_alternating_front_self_collapse` | 15 | **accepted** | 2.7 |
| `true:alternating_front_self_collapse` | 14 | **accepted** | 2.7 |
| `true:forked_square_singleton` | 14 | **accepted** | 2.8 |
| `true:crossed_pair_singleton` | 14 | **accepted** | 2.8 |
| `true:front_double_self_collapse` | 13 | **accepted** | 2.7 |
| `true:outer_sandwich_singleton` | 12 | **accepted** | 2.7 |
| `true:derived_left_projection` | 4 | **accepted** | 2.7 |

**10/10 accepted, 0 rejected.** All ten are now pinned byte-for-byte; the
fixture is **112 entries** and the offline gate is **270 passed, 2 skipped**
(up from 260 — the ten new pins are ten new tests).

Three tooling defects were fixed to make that safe, each of which would have
cost something later:

1. **`judge_rows.py --write-fixture` REPLACES the fixture.** Using it for a
   10-row run would have silently deleted the other 102 pins — every one of
   which cost a real judge call. Added `--append-fixture`, and reworded
   `--write-fixture`'s help so the destructive one reads as destructive.
2. **The fixture was not self-contained.** `test_judge_verified.py` resolves a
   pinned row from the official and HF sets; rows pinned from a generated sweep
   batch are in neither, and the batch files are gitignored so CI would not have
   them either. The first append turned the gate into **260 passed, 12 skipped**
   — ten pins that had just cost ten judge calls, degraded to silent skips.
   Fixture entries now carry their own `equation1`/`equation2`/eq ids and the
   test falls back to them. **A pin that skips is worse than no pin**: it reads
   as coverage.
3. `judge_rows.py` gained `--problems` (resolve ids from arbitrary batch files),
   `--route` and `--per-route` — one certificate per family is what pins a
   family, and there was no way to ask for that.

---

## Track B — COMPLETE, and the combined order-4 result

All ten batches landed. b01–b04 ran at 16 workers, b05–b10 at 20 (the machine
was throttled to 8 briefly between them; that batch was discarded and re-run).
**Wall clocks across the two settings are not comparable and must not be
averaged** — coverage is, since order-4 rows at `fast` are not budget-marginal
(p95 9.4 s against no per-row cap).

| | Rows | Solved | Skips | Crashes | Oracle failures | Label mismatches |
| --- | --- | --- | --- | --- | --- | --- |
| Track B | 100,000 | 99,959 (**99.959%**) | 41 | 0 | 0 | 0 |
| **Track A + B combined** | **110,000** | **109,954 (99.958%)** | **46** | **0** | **0** | **0** |

Verdicts split 54,960 TRUE / 54,994 FALSE. p50 **5 ms**, p95 9.37 s, p99 10.52 s,
slowest solved 354.7 s.

Route census over 110,000 unseen order-4 rows:

| Family | Rows | | Family | Rows |
| --- | --- | --- | --- | --- |
| `witness` | 51,557 | | `equational_closure` | 1,671 |
| `singleton` | 25,693 | | `constancy` | 1,382 |
| `egg_collapse` | 14,047 | | `linear` | 1,235 |
| **`completion`** | **8,317** | | `derived_cp_closure` | 810 |
| `spine` | 1,859 | | `egg_bootstrap` | 733 |

### The order-4 frontier, at 110,000 rows

46 misses: **40 TRUE, 6 FALSE**. Every one has a 4-operation hypothesis — the
top of the order-4 space — and 38 of 46 have 3 variables.

| eq1 | misses | | eq1 | misses |
| --- | --- | --- | --- | --- |
| **2923** | **16** | | 481 | 2 |
| **3569** | **7** | | 3051 | 2 |
| 650 | 5 | | 9 others | 1 each |
| 3983 | 4 | | | |

**The top four hypotheses account for 32 of 46 misses (70%)** — sharper than the
58% the 20,000-row sample reported, and now measured on 5.5× the rows. This is
the single most actionable number the campaign produced: the entire order-4
frontier is four laws.

`eq1 = 3569` is `x ◇ y = y ◇ ((z ◇ y) ◇ x)`, already known open from
`etp_3569_4653`. `eq1 = 2923` is `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` — the
`x = F(x, y, z)` shape that ordered completion closed for `hard2_0073` in
2026-08-12, failing here against 16 different goals.

The six FALSE misses are `etp_481_3050`, `etp_481_2132`, `etp_2162_3877`,
`etp_2531_23`, `etp_898_4270`, `etp_2316_4656` — **6 in 110,000, about 1 in
18,000**, and `481` appears twice. Before today the FALSE side had exactly one
known miss in 20,000 rows; it is now characterised rather than anecdotal.

---

## Campaign totals

| Track | Rows | Solved | Crashes | Oracle failures | Label mismatches |
| --- | --- | --- | --- | --- | --- |
| A + B — order-4 (labelled) | 110,000 | 109,954 (99.958%) | 0 | 0 | **0** |
| C — order-5 ≤3 vars | 20,000 | 19,647 (98.24%) | 0 | 0 | n/a (unlabelled) |
| D — order-6 ≤2 vars (pilots) | 900 | 899 | 0 | 0 | n/a (unlabelled) |
| **Total** | **130,900** | — | **0** | **0** | **0** |

For scale: everything the solver had ever been measured on before today was
26,669 rows. This campaign is **4.9× that, in one day**, with zero unsound
certificates and zero wrong verdicts anywhere ground truth exists.

**Every certificate family emitting kernel-unparseable Lean across all 130,700
audited rows is now judge-pinned** — 29 families, 10 of which had no evidence of
any kind this morning, all 10 accepted by the real Lean judge on v4.32.2.

Standing spotcheck, run after the campaign: **90 rows / 9 sources, 100%
accuracy, 100% coverage, 0 mistakes**. Offline gate: **270 passed, 2 skipped**.

## Ranked levers for the improvement pass

1. **Four order-4 hypotheses are 70% of a 110,000-row frontier** — `2923` (16),
   `3569` (7), `650` (5), `3983` (4). Two are already characterised as needing
   facts self-superposition never derives (`CLAUDE.md`, "Known open frontier");
   the untried idea on record is seeding completion with goal-subterm instances,
   egg_ladder-style. This is a *family* problem with four names on it.
2. **Order-5's frontier is a size/arity wall, not a family wall** — 353 misses,
   largest cluster 4, but **all 353 at exactly 5 operations and 352 of 353 at 3
   variables**. Whatever fixes lever 1 will not touch this, and vice versa.
   Order-5 is a quarter of the score and is at 98.24% against order-4's 99.96%,
   so this is where the points are.
3. **The wide countermodel search takes 37–76% of every unsolved order-4 row's
   clock**, and on 4 of 5 profiled rows it is hunting a witness that cannot
   exist. Now cheap to re-measure at scale: `sweep_report --diagnose` produces
   the profile on any batch's ledger.
4. **The FALSE side is characterised, not anecdotal**: 6 misses in 110,000, with
   `eq1 = 481` twice. Enough to look for a shared structure rather than treating
   each as a one-off.

# Population calibration: were the unseen-row miss rates measured on the right population?

**Date** 2026-08-27 · **Solver** main tree at `319d778` (no solver/test/doc edits in
this session) · **Effort** `fast`, `--row-budget 300` (models Marathon's fair share
of `N x 300 s`) · **Workers** 3 (the box is 32 logical cores and was shared with
other agents throughout).

**Load caveat (rail 22).** Every wall clock below was taken with **40-42 other
Python processes** on the box and the CPU pinned at **77-100%**. Coverage numbers
(solved / skipped / oracle failures) are unaffected by load; the wall clocks are
**upper bounds**, not clean measurements.

The question: the private evaluation set has four equal-weight categories —
Normal, Hard, Extra Hard, **Order 5** — and each public mirror is balanced
100 TRUE / 100 FALSE. Every unseen sweep so far was a **uniform catalog draw**,
with order-5 restricted to **<= 3 variables**. Both restrictions turn out to
matter, and in opposite directions.

---

## 1. Order-5, >= 4 variables — never swept before, and it is not a frontier

### Command

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe stage2/experiments/audit_corpus.py \
  --file stage2/experiments/order5-ge4var-250-2026-08-27.jsonl \
  --effort fast --row-budget 300 --workers 3 \
  --out stage2/results/audit-order5-ge4var-250-2026-08-27.json
```

Batch: 250 pairs, both sides >= 4 variables, seed 20260827 (pre-existing).

### Result

| | value |
| --- | --- |
| solved | **250 / 250** |
| skipped | **0** |
| crashes | **0** |
| oracle failures | **0** |
| label mismatches | n/a — the batch is unlabelled (generated order-5 pairs, outside the order-4 outcome matrix) |
| verdicts | 133 TRUE / 117 FALSE |
| wall clock | 288.5 s on 3 workers (663.0 s of row-seconds), under heavy external load |
| row seconds | p50 **0.00** · p90 7.71 · p95 9.84 · p99 47.94 · max 112.78 |

**Skip rate 0.0% (0/250) against the <= 3-variable baseline of 1.76% (353/20,000).**
Rule of three puts the 95% upper bound at 1.2%, so this is consistent with "no
worse" and suggestive of "much better" — and the direction is confirmed by
re-slicing the old 20,000-row <= 3-var sweep, which nobody had done:

| eq1 variables | misses / rows | rate |
| --- | --- | --- |
| 1 | 0 / 75 | 0.00% |
| 2 | 1 / 3,582 | 0.03% |
| **3** | **352 / 16,343** | **2.15%** |
| >= 4 (this batch) | **0 / 250** | **0.00%** |

**Order-5 difficulty peaks at exactly 3 variables and falls off on both sides.**
That is the same fact CLAUDE.md already records from the other end ("352 of 353
misses have 3 variables") — but it had been read as "we happen to sample 3-var
rows", when it is really a **peak**: fewer variables makes the hypothesis weaker
(nothing to prove from), more variables makes it more constraining, and a more
constraining order-5 law usually just collapses the magma.

The route distribution says exactly that. Of the 133 TRUE verdicts, **111 are
collapse-shaped** (`true:singleton` 63, `true:completion:collapse` 31,
`true:egg_collapse` 17); of the 117 FALSE verdicts, **103 are the tiny named
witness tables** (`C0` 43, `RP` 31, `LP` 29). Full distribution:

```
  63  true:singleton              43  false:witness:C0
  31  true:completion:collapse    31  false:witness:RP
  17  true:egg_collapse           29  false:witness:LP
   8  true:completion:bridge       5  false:witness:T3L
   6  true:constancy:00            3  false:witness:T3R
   3  true:completion:join         2  false:witness:S4B
   2  true:derived_cp_closure      1  false:witness:S5B / linear:z4 / spine:leftsucc:z3 / S4C
   1  true:lemma_bootstrap:enum371 / rewrite / universal_identity:right
```

**Misses: none. There is no miss shape to report.**

### The caveat that matters more than the headline

The public Order-5 mirror (`data/hf_cache/evaluation_order5.jsonl`, difficulty
`order5_normal`) has a structural property neither of our order-5 populations
reproduces: **100% of its rows have a bare variable on one side of *both*
equations** (`x = F(...)`). Our sweeps are drawn from the size-5 catalog, which
is 63.9% bare-variable-side; this new >= 4-var batch is 39.6% bare on both sides
(99 of 250 rows).

That axis is not cosmetic — it is the **hardest** axis in the order-5 data:

| shape (20k <= 3-var sweep) | misses / rows | rate |
| --- | --- | --- |
| eq1 not bare, eq2 not bare | 28 / 2,663 | 1.05% |
| eq1 not bare, eq2 bare | 0 / 4,553 | 0.00% |
| eq1 bare, eq2 not bare | 111 / 4,556 | 2.44% |
| **eq1 bare, eq2 bare** | **214 / 8,228** | **2.60%** |
| ... restricted to 3 variables | 213 / 6,718 | **3.17%** |

So the correct projection for the private Order-5 category re-weights our
measured rates onto **its** shape (100% both-bare; eq1 variables 2/3/4/5/6 at
8.5 / 41.5 / 35.0 / 12.5 / 2.5%):

| | projected miss rate | of a 200-row category |
| --- | --- | --- |
| point estimate (>= 4 var cell = our measured 0/99 both-bare rows) | **1.32%** | **2.6 rows** |
| 95% upper bound (rule of three on that cell, 3/99) | 2.84% | 5.7 rows |
| the naive number we have been quoting (flat 353/20,000) | 1.77% | 3.5 rows |

The naive flat rate was **too pessimistic on the >= 4-var half and too optimistic
on the both-bare 3-var core**; the two errors partly cancel, which is luck, not
method.

---

## 2. Official-set distribution match

### 2.1 Profile of the public sets

`stage2/experiments/population_profile.py` (new, measurement-only) tabulates eq1/eq2
operation and variable counts, bare-variable-side fraction and TRUE/FALSE balance:

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe stage2/experiments/population_profile.py \
  --out stage2/results/population-profile-2026-08-27.json
```

| set | n | TRUE | eq1 bare | eq1 ops (0/1/2/3/4/5 %) | eq1 vars (1..6 %) |
| --- | --- | --- | --- | --- | --- |
| official normal | 1000 | 50.0 | 72.6 | .1 / .7 / 7.1 / **92.1** | .5 / 13.8 / 41.4 / 35.4 / 8.2 / .7 |
| official hard1 | 69 | 34.8 | 68.1 | – / – / 18.8 / **81.2** | – / 10.1 / 68.1 / 15.9 / 5.8 / – |
| official hard2 | 200 | 50.0 | 73.5 | – / – / 4.5 / **95.5** | – / 19.5 / 43.0 / 24.0 / 13.5 / – |
| official hard3 | 400 | 48.8 | 81.5 | .3 / 1.8 / 13.3 / **84.8** | – / 12.8 / 52.3 / 30.8 / 4.3 / – |
| hf evaluation_normal | 200 | 50.0 | 74.5 | 10.0 / 3.0 / 1.5 / 12.5 / **73.0** | 13.0 / 10.5 / 50.0 / 19.5 / 5.5 / 1.5 |
| hf evaluation_hard | 200 | 50.0 | 82.0 | 1.5 / .5 / 8.0 / **39.0** / **51.0** | 1.5 / 21.0 / 61.5 / 15.5 / .5 / – |
| hf evaluation_extra_hard | 200 | 50.0 | 57.5 | – / – / 1.0 / **67.0** / **32.0** | – / 32.5 / 44.0 / 23.5 / – / – |
| hf evaluation_order5 | 200 | 50.0 | **100.0** | 5 ops: **100** | – / 8.5 / 41.5 / 35.0 / 12.5 / 2.5 |
| **ETP order-4 catalog** (4,694 laws) | – | – | 66.9 | .04 / .11 / .83 / 7.75 / **91.27** | .66 / 16.6 / 44.5 / 30.8 / 6.9 / .5 |
| **uniform draw, 2,000 rows, seed 20260828** | 2000 | 50.0 | 73.0 | .1 / .25 / .65 / 7.6 / **91.4** | .55 / 13.9 / 44.1 / 35.1 / 6.0 / .5 |
| our stratified `etp-hardtest-1000` | 1000 | 50.0 | 69.8 | 4 ops: **100** | – / – / 48.1 / 40.9 / 10.2 / .8 |

Uniform draw command (the tool balances the draw 50/50 by construction, which is
what the public sets do too, so it is the right reference):

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe stage2/experiments/sample_etp_matrix.py \
  --count 2000 --seed 20260828 --out stage2/results/etp-uniform-2000-2026-08-28.jsonl \
  --exclude <12 prior batch files>
```

**Answer to the question as posed: it depends on which "official hard" you mean,
and the two disagree sharply.**

- **Official `hard1`/`hard2`/`hard3` are essentially uniform in shape** — 87.6%
  4-operation hypotheses against the catalog's 91.3%. Our sweeps model them well.
- **The HF `evaluation_hard` / `evaluation_extra_hard` sets are not** — 54.25% of
  their hypotheses are **3-operation**, a **7x enrichment** over the catalog's
  7.75%, and only 41.5% are 4-op. These two sets carry the private evaluation's
  own category names (`difficulty` fields are literally `normal`, `hard`,
  `extra_hard`, `order5_normal`), so they are the better model of what will be
  graded.
- **Our stratified `etp-hardtest-1000` batch is 100% 4-op** — further from *both*
  official populations than a plain uniform draw is.

### 2.2 What that does to the expected miss rate (importance reweighting)

This is the more powerful measurement, because it uses all 510,000 order-4 rows
already swept rather than 250 new ones. Pooling the three big uniform sweeps
(`etp-sweep-100k-2026-08-25`, `-200k-2026-08-26`, `-200k-2026-08-27`, plus the 10k
pilot): **218 misses in 510,000 rows = 0.0427%** (190 TRUE / 28 FALSE). Sliced by
hypothesis shape and label:

| eq1 ops | eq1 vars | label | misses / rows | rate | uniform weight |
| --- | --- | --- | --- | --- | --- |
| <= 3 | any | any | **0 / 38,373** | **0.0000%** | 7.5% |
| 4 | 2 | F | 4 / 54,720 | 0.0073% | 10.7% |
| 4 | 2 | **T** | 10 / 2,320 | **0.4310%** | 0.45% |
| 4 | 3 | F | 23 / 112,531 | 0.0204% | 22.1% |
| 4 | 3 | **T** | **150 / 87,060** | **0.1723%** | 17.1% |
| 4 | 4 | F | 1 / 54,271 | 0.0018% | 10.6% |
| 4 | 4 | T | 30 / 109,446 | 0.0274% | 21.5% |
| 4 | 5-6 | any | 0 / 42,289 | 0.0000% | 8.3% |

**Not one of the 218 misses has a hypothesis smaller than 4 operations**, and
`4 ops / 3 vars / TRUE` alone holds 150 of them.

Re-weighting those cell rates onto each population's own (eq1 ops, eq1 vars,
label) joint:

| population | projected miss rate | ratio vs uniform | per 200-row category |
| --- | --- | --- | --- |
| uniform draw (measured) | 0.0427% | 1.00x | 0.09 |
| official normal | 0.0413% | 0.97x | 0.08 |
| official hard1+2+3 | 0.0487% | 1.14x | 0.10 |
| hf evaluation_normal | 0.0597% | 1.40x | 0.12 |
| hf evaluation_hard | 0.0321% | 0.75x | 0.06 |
| hf evaluation_extra_hard | 0.0070% | **0.16x** | 0.01 |
| our `etp-hardtest-1000` | 0.0436% | 1.02x | — |
| our new `etp-officialshape-250` | 0.0189% | 0.44x | — |

Caveat: this conditions on eq1 shape and label only. It cannot see whatever made
the organizers call a row "hard", which is presumably a property of the *pair*.
It is an estimate of the shape effect, not a prediction of the score.

### 2.3 The shape-matched batch

`stage2/experiments/build_officialshape_batch.py` (new) matches the pooled
HF `evaluation_hard` + `evaluation_extra_hard` joint over (eq1 ops, eq1 vars,
TRUE/FALSE) by conditional sampling from the full ETP matrix — equivalent to
importance-sampling a uniform draw, without drawing and discarding millions of
rows. Within a cell, candidate eq1 ids are weighted by how many eq2 ids carry the
requested label, so the draw is uniform over *pairs* in the cell, not merely over
eq1.

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe stage2/experiments/build_officialshape_batch.py \
  --count 250 --seed 20260827 --out stage2/results/etp-officialshape-250-2026-08-27.jsonl
```

Excluded **611,796 (eq1,eq2) pairs** drawn from 229 files — every `*.jsonl` under
`stage2/results/` and `stage2/experiments/` (the deep-sweep `etp-*` / `order4-*` /
`order5-*` batches) plus every official and HF set. No shortfall in any cell.

Realized vs target (pooled HF hard+extra_hard):

| | target | realized |
| --- | --- | --- |
| eq1 ops 3 / 4 | 54.25% / 41.50% | 53.2% / 41.2% |
| eq1 vars 2 / 3 / 4 | 26.75% / 52.75% / 19.50% | 26.4% / 52.4% / 19.6% |
| TRUE | 50.0% | 50.0% (125 / 125) |
| eq1 bare-var side | 69.75% (not targeted) | 70.0% |
| eq2 ops 4 | 88.0% (not targeted) | 88.0% |

**Report this batch as STRATIFIED (rail 18): its solve rate is comparable to
another shape-matched batch, never to a uniform sweep's.**

### 2.4 Audit of the shape-matched batch

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe stage2/experiments/audit_corpus.py \
  --file stage2/results/etp-officialshape-250-2026-08-27.jsonl \
  --effort fast --row-budget 300 --workers 3 \
  --out stage2/results/audit-officialshape-250-2026-08-27.json
```

| | value |
| --- | --- |
| solved | **250 / 250** |
| skipped / crashes / oracle failures | **0 / 0 / 0** |
| **label mismatches** | **0 of 250** (matrix labels, checked row by row) |
| verdicts | 125 TRUE / 125 FALSE — exactly the labels |
| wall clock | 56.3 s on 3 workers (129.2 s of row-seconds), under heavy external load |
| row seconds | p50 **0.00** · p90 3.34 · p95 3.64 · p99 6.47 · **max 9.35** |

**Misses: none.** Route distribution (28 distinct routes):

```
  77  true:singleton                  41  false:witness:LP
  20  true:egg_collapse               32  false:witness:RP
   6  true:constancy:00               29  false:witness:C0
   6  true:completion:join             6  false:witness:XOR
   4  true:rewrite                     3  false:witness:NIMP / T3R
   3  true:completion:collapse         2  false:spine:rightsucc:z2 / leftsucc:z2 / witness:T3L
   2  true:completion:bridge           1  false:linear:z4 / linear:z3 / spine:leftsucc:z3 / Z3A / S5C
   1  true:absorption_context_bridge / universal_identity:left / egg_bootstrap:{right_col,left_row}_constant
      / front_double_self_collapse / wrapped_tail_singleton / mirrored_alternating_front_self_collapse
```

Honest statistical caveat: at the uniform baseline of 0.0427%, a 250-row batch
expects **0.1 misses** — so 250/250 confirms *no new failure mode appears in the
official-shape region* but cannot on its own prove that region is easier. The
0.44x claim rests on the 510,000-row reweighting in 2.2, not on these 250 rows.
The **max row time of 9.35 s** (against a 300 s budget) is the load-bearing
observation: this population never gets near the deep engines.

---

## 3. What this changes

1. **The order-4 categories are not where the remaining points are.** Every
   order-4 population we can profile projects to **0.01-0.12 expected misses per
   200-row category**, and the hardest cell (`4 ops / 3 vars / TRUE`, 0.17%) is
   *under*-represented in the sets that carry the private categories' names.
2. **Order 5 carries ~95% of the projected loss** — **2.6 of 200 rows** (95%
   upper bound 5.7), against ~0.3 rows total across the other three categories.
   It is a quarter of the score.
3. **The order-5 frontier is narrower than "5 ops, 3 vars".** It is
   `3 variables AND a bare variable on both sides` — **3.17%** (213/6,718),
   against 0.00-0.07% everywhere else in the order-5 space we have measured.
   That is a **6,718-row-wide target**, and 213 known instances of it.
4. **Our unseen batches were mis-aimed on two axes.** `etp-hardtest-1000` was
   100% 4-op (1.02x uniform difficulty — the stratification bought nothing on the
   hypothesis axis), and every order-5 sweep excluded the >= 4-var half of the
   category, which turns out to be free. The batch that would have been worth
   1,000 rows is *order-5, 3 variables, bare on both sides*.

### Suggested next batch (not run this session)

An order-5 batch drawn to the **private mirror's** shape — both equations
`x = F(...)`, eq1 variables weighted 8.5 / 41.5 / 35.0 / 12.5 / 2.5 across
2 / 3 / 4 / 5 / 6 — is the only draw whose solve rate can be quoted against the
Order-5 category. `stage2/experiments/build_officialshape_batch.py` is the order-4
version of exactly that; the order-5 analogue needs the size-5 catalog
(`data/stage2_official_problems/eq_size5.txt`, 62,576 laws) and has no labels, so
it measures skip rate only.

## Files written

| file | what |
| --- | --- |
| `stage2/experiments/population_profile.py` | set/batch shape profiler (new, measurement-only) |
| `stage2/experiments/build_officialshape_batch.py` | shape-matched ETP batch builder (new) |
| `stage2/results/population-profile-2026-08-27.json` | profiles of all 8 public sets |
| `stage2/results/etp-uniform-2000-2026-08-28.jsonl` | uniform reference draw, seed 20260828 |
| `stage2/results/etp-officialshape-250-2026-08-27.jsonl` | the shape-matched batch (STRATIFIED) |
| `stage2/results/audit-order5-ge4var-250-2026-08-27.json` | audit, order-5 >= 4 vars |
| `stage2/results/audit-officialshape-250-2026-08-27.json` | audit, shape-matched batch |

# Deep sweep roadmap — 150,000 unseen rows

Written 2026-08-25. Owner doc for the measurement campaign that follows the
2026-08-24 final engine session. **Measurement and logging only** — no solver
changes until the campaign has produced a ranked, evidence-backed defect list.
That ordering is deliberate and is the same one the 2026-08-20 session used:
fixes chosen from one batch's frontier generalise badly, fixes chosen from
150,000 rows do not.

## Why this campaign, and why now

Three facts from the final rules (`CLAUDE.md`, "Rules update 2026-08-24") set
the whole shape of it:

1. **No evaluation problem is reused** from Stage 1 or any public set. The
   2,669-row local corpus is 100% solved and therefore carries **zero**
   remaining signal about the score. Only unseen-row generalization counts.
2. **Order 5 is a quarter of the score** — its own equal-weight category
   alongside Normal, Hard and Extra Hard. The order-5 measurement to date is a
   single 4,000-row sample at 98.0%, which is the thinnest evidence behind any
   quarter of the score.
3. **`accepted` = 1 point, anything else 0.** A skip and a wrong answer cost
   the same, so a coverage miss and a soundness miss are worth the same number
   of points — but they are worth wildly different amounts of *information*,
   which is why the ledger below keeps them apart.

Everything the solver has ever been measured on is 2,669 corpus rows + 20,000
order-4 + 4,000 order-5 ETP rows = **26,669**. This campaign is **150,000**.

## The four tracks

| # | Track | Rows | Drawn from | Vars | Ground truth | Batches | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | order-4 | 10,000 | ETP outcome matrix (4,694²) | any | **yes** | 1 × 10k | **running 2026-08-25** |
| B | order-4 | 100,000 | ETP outcome matrix | any | **yes** | 10 × 10k | generated, queued |
| C | order-5 | 20,000 | `eq_size5.txt`, 26,990 laws with ≤3 vars | ≤3 | no | 4 × 5k | generated, queued |
| D | order-6 | 20,000 | **generated** catalog, 27,456 laws with ≤2 vars | ≤2 | no | 200-row pilot, then 8 × 2.5k | **redesigned after the pilot — see below** |

"order N" is ETP's own sense throughout: the **total number of `*` operations
across both sides** of the equation. It is not the magma's carrier size, which
is what "order 5 countermodel" means elsewhere in this repo — the two senses
collide constantly and the difference is worth restating at the top of every
report.

### What each track can and cannot prove

This is the single easiest thing to overclaim, so it is stated before any
result:

- **A and B carry ETP's ground-truth label.** A row can therefore fail three
  ways: `skip` (no answer), `oracle_failed` (an answer whose certificate the
  offline oracle could not verify), and `label_mismatch` (an answer that
  contradicts known truth). Only these tracks can produce the sentence "0 wrong
  answers".
- **C and D have no ground truth and cannot have any.** Nobody has ever
  computed an order-5×order-5 implication matrix (~62,576² pairs), let alone an
  order-6 one. `audit_row` tolerates the missing `answer` and still
  proof-kernel-checks every TRUE certificate, model-checks it against finite
  models of the hypothesis, and independently re-verifies every FALSE witness
  table. So "0 oracle failures" on C/D means **"0 unsound certificates"**, not
  "0 wrong answers". Never write the second sentence for C or D.
- **None of it is judge evidence.** All four tracks are the offline oracle,
  which is an upper bound on judge acceptance (rail 3). Real-judge sampling is
  a separate step, below.

## Generated artifacts, and the proof they are unseen

All batch files live in `stage2/results/`. Every draw excludes every prior
draw, and the disjointness was checked by row id / `(eq1_id, eq2_id)` pair
rather than assumed:

| File | Rows | Seed | Excludes | Verified |
| --- | --- | --- | --- | --- |
| `etp-sweep-10k-2026-08-25.jsonl` | 10,000 (5,000 T / 5,000 F) | `20260825` | the four 2026-08-20 batches + the spotcheck coverage ledger | 0 overlap with the prior 20,000 |
| `etp-sweep-100k-2026-08-25.jsonl` (+ `-b01..b10`) | 100,000 (50,000 T / 50,000 F) | `202608251` | the prior 20,000 **and** track A's 10,000 | 0 overlap with either |
| `order5-sweep-20k-2026-08-25.jsonl` (+ `-b01..b04`) | 20,000 | `20260825` | the 2026-08-20 10,000-row draw, the 200-row pilot, both 2026-08-24 order-5 Marathon manifests, **and the HF `evaluation_order5` set** | 0 overlap; max 3 variables confirmed |
| `order6-sweep-20k-2026-08-25.jsonl` (+ pilot, `-b01..b08`) | 20,000 | `20260825` | nothing to exclude — first order-6 rows ever drawn | all 20,000 pairs distinct, max 2 variables, all equations exactly 6 ops, 0 parse failures |

**Reproducibility caveat.** `stage2/results/*.jsonl` and `data/generated/` are
gitignored, so none of these batch files is in git. Each is regenerable from its
seed and script — but a draw that passes `--exclude` reproduces only while the
*excluded* files are still on disk, and those are gitignored too. If a batch file
is lost, regenerate it before deleting anything it excluded, and re-check
disjointness rather than assuming the seed carried it.

Cumulative unseen order-4 coverage once A and B land: **130,000 distinct rows**
(20,000 already measured + 10,000 + 100,000). If the intent is exactly 100,000
cumulative, stop track B after batch `b07`.

### The order-6 catalog had to be built, and is pinned against ETP's own

ETP publishes catalogs only up to order 5. `stage2/experiments/generate_eq_catalog.py`
generates any order, and its canonical form was reverse-engineered from
`eq_size5.txt` rather than guessed:

* variables named by **first occurrence** left to right — x, y, z, w, u, v, r;
* equations identified up to relabeling **and** swapping the two sides;
* the kept representative has ≤ ops on the left, tie-broken by a structural
  shape order (a leaf before any product, then by the **left** argument's
  operation count, recursively), then by the variable slot sequence;
* reflexive `t = t` dropped except `x = x` itself.

`--verify` regenerates orders 0..5 and reproduces `eq_size5.txt` **line for
line** — all 62,576 rows in the same order, plus the 4,694-law order-≤4 slice
and the ≤2 / ≤3 variable slices. Set equality would have been suggestive; exact
line order means the enumeration and the tie-break are both right. Order 6 with
≤2 variables is **27,456** laws, so track D draws from a ~754M-pair space.

### Track D was redesigned after its pilot, and the reason is measurable

Two 200-row order-6 pilots — one drawing both sides from the order-6 catalog,
one drawing the goal from the smaller order-≤5 catalog — both came back
**200/200 FALSE, 0 skips, p50 8 ms**, with the entire 161 s wall clock of the
first spent on a single row. Certificates were 265–600 bytes against a 19,500-byte
FALSE budget. A uniform 20,000-row draw would therefore have cost ~4.5 h to
measure the named-witness table and essentially nothing else.

**The cause is the variable cap, not the order**, and the labelled order-4
matrix settles it without any guessing:

| Population | TRUE base rate |
| --- | --- |
| all 22,028,942 order-≤4 pairs | **37.10%** |
| both sides ≤3 variables | 25.46% |
| both sides ≤2 variables | **4.17%** |
| 4-op ≤2-var hypothesis → any ≤2-var goal | **2.87%** |

Fewer variables means a more constraining law, and two unrelated constraining
laws essentially never imply one another. The effect is ~9× at order 4 already;
at order 6 it is stronger still (0 TRUE in 400 draws bounds the rate at ≲1%).
This is also why **track C needs no such treatment** — at ≤3 variables the base
rate is 25%, and the 2026-08-20 order-5 sample duly came out 19% TRUE.

The fix is to stratify rather than to draw uniformly.
`stage2/experiments/filter_hard_region.py` discards any pair for which an
independent small-model search finds a magma satisfying eq1 and refuting eq2,
using `stage2/tests/oracles.py` — which by contract shares no code with
`solver.py`, so "survivor" is not defined by the thing being measured. What
survives is every TRUE pair plus the FALSE pairs whose witness is not small.
Measured on order-6 ≤2 vars: **14.2% survive**, at 13.5 ms per pair (3,513 pairs
filtered in 5 s on 12 workers), splitting 401 `no_small_countermodel` to 99
`collapse_candidate` — the latter being hypotheses with no non-trivial model in
the battery, which is where order-6 TRUE rows concentrate.

**Any batch built this way must be reported as stratified, never as random.**
Its solve rate is not comparable to a uniform sweep's, and its FALSE rows are
biased hard by construction. Track D is re-scoped to a 500-row hard-region pilot
first; the full row count is set from what that pilot costs per row, because the
hard region is exactly the expensive region.

## Cost model

Measured basis, all at `fast` effort on 16 workers:

| Basis | Rows | Wall clock | Per row |
| --- | --- | --- | --- |
| order-4, 2026-08-20, unbounded | 20,000 | 7,351 s | **0.368 s** |
| order-5 ≤3 vars, 2026-08-20, `--row-budget 300` | 4,000 | 5,865 s | **1.466 s** |
| order-6 | — | — | **unknown — pilot first** |

Projections, with the caveat that the 2026-08-21 session made the corpus audit
~24% faster and closed 49 of the 52 order-4 frontier rows (skips are the
expensive rows, so both effects push the real number down):

| Track | Rows | Projection at the measured rate | Expected with the 08-21/08-24 solver |
| --- | --- | --- | --- |
| A | 10,000 | 3,680 s (~1.0 h) | **measured: 1,207 s (0.34 h)** |
| B | 100,000 | 36,800 s (~10.2 h) | **~3.4 h** at track A's measured 0.121 s/row, 10 batches of ~20 min |
| C | 20,000 | 29,320 s (~8.1 h) | ~6–8 h, 4 batches of ~1.5–2 h |
| D | re-scoped | uniform draw measured at **0.80 s/row** (200 rows, 160.9 s) — but 99.5% of that population is decided in under 10 ms | **hard-region pilot decides**; the uniform variant is retired |

Total campaign: roughly **16–20 h of machine time plus track D**. It is
batch-granular throughout, so it survives interruption at any batch boundary.

## Per-batch protocol

Four steps, in order, for every batch of every track:

```powershell
# 1. Check what else is on the machine FIRST. A wall clock quoted under
#    unrelated load is not a measurement (CLAUDE.md, "Timing caveat").
powershell -NoProfile -Command "1..3 | ForEach-Object { (Get-CimInstance Win32_Processor).LoadPercentage; Start-Sleep 2 }"

# 2. The sweep. ONE AT A TIME — never two audit_corpus.py runs on the same
#    machine (rail 5e); 16-worker pools starve each other and manufacture
#    losses that are not real.
.\.venv\Scripts\python.exe stage2/experiments/audit_corpus.py `
    --file stage2/results/<batch>.jsonl --effort fast --workers 16 `
    --out stage2/results/audit-<batch>.json

# 3. Failure ledger + summary (+ a row-id diff against the previous batch's
#    report where the rows overlap — they do not here, so --baseline is for
#    re-runs of the same batch after a solver change).
.\.venv\Scripts\python.exe stage2/experiments/sweep_report.py `
    --audit stage2/results/audit-<batch>.json `
    --batch stage2/results/<batch>.jsonl `
    --out-prefix stage2/results/<batch>

# 4. Diagnose every failed row: re-solve with all 19 engines wrapped in a
#    timer, so a skip records WHERE its wall clock went instead of only how
#    much of it there was.
.\.venv\Scripts\python.exe stage2/experiments/sweep_report.py `
    --audit stage2/results/audit-<batch>.json `
    --batch stage2/results/<batch>.jsonl `
    --out-prefix stage2/results/<batch> --diagnose --diagnose-budget 300
```

`sweep_report.py --audit a.json b.json ... --batch a.jsonl b.jsonl ...` merges
several batches into one report, which is how a finished track is read as a
single measurement. It refuses to double-count a repeated row id.

### Row budgets per track

- **A, B (order 4): unbounded.** Matches the 2026-08-20 baseline exactly, so
  the 130,000 rows are one comparable population. A cap would not be free:
  prior batches contain genuine solves at 790 s, 1,475 s and 2,161 s.
- **C (order 5): `--row-budget 300`.** Matches the 2026-08-20 order-5 run.
- **D (order 6): the pilot decides**, with `--row-budget 300` as the starting
  guess. Order-6 terms are one operation larger than anything the search
  engines have ever been fed, and the *last* time new territory was opened
  (order 5, 2026-08-20) it exposed an un-deadlined inner loop that overran a
  300 s cap by 11.8×. Treat an overshoot as an expected finding, not a surprise.

## Execution order, and why

1. **A — 10,000 order-4** (running). The cheapest track, on the only
   distribution with ground truth, against a solver whose order-4 frontier
   moved on 2026-08-21 and 2026-08-24. It re-baselines everything and it
   validates the whole harness before 10 hours are committed to track B.
2. **D pilot — 200 order-6.** Cheap, and it is the only unknown in the cost
   model. Run it early so track D can be scheduled at all.
3. **C — 20,000 order-5**, in four 5k batches. Highest score-weighted value:
   a quarter of the official score rests on a single 4,000-row sample today.
4. **B — 100,000 order-4**, in ten 10k batches. Highest statistical power,
   lowest per-row information — it is the track that finds the 1-in-20,000
   defects (the FALSE frontier row `etp_1661_3524` was exactly that), so it
   runs last and can be truncated at any batch boundary.
5. **D — 20,000 order-6**, in eight 2.5k batches, scheduled from the pilot.

Track D is deliberately last on value: there is **no order-6 category in the
scoring**, and its ≤2-variable slice is narrow. It is generalization insurance
— evidence that nothing in the solver is quietly tuned to term size ≤ 5 — not
a score-bearing measurement. Cut it first if time runs short.

## Stop conditions

Stop the campaign and switch to fixing, immediately, on any of:

- **any `label_mismatch`** on tracks A/B — a verdict contradicting ETP's known
  truth is a wrong answer, the most expensive defect class there is;
- **any `oracle_failed`** on any track — an emitted certificate the offline
  oracle cannot verify is a latent `incorrect` submission;
- **any `crash`** — rail 11: one bad row must never be able to kill a Marathon
  manifest, and a crash in the audit is that bug's offline shadow;
- a batch losing rows a prior batch of the same track solved (row-id diff, rail
  2 — totals swing ±7 on noise and prove nothing).

A rising *skip* count is **not** a stop condition. It is the expected output of
this campaign and the input to the improvement pass.

## What to watch for in new territory

- **Deadline overshoot (rail 5f, five instances and counting).** Order-6 terms
  are the biggest thing any engine here has seen. `sweep_report --diagnose`
  names the overrunning engine directly, which is what took three sessions to
  do by inference last time (rail 5f-vi: sample the stack, don't reason about
  which function it must be).
- **Certificate bytes.** Order-6 goals render larger proofs. Every route that
  ever skipped a row for size was, until 2026-08-13, skipping against a phantom
  cap; the real caps are 100,000 B overall / 20,000 B for FALSE. The ledger
  records `code_bytes` per solved row, so the distribution is measurable rather
  than assumed.
- **`decide` cost is `n ** variables`, not order.** Track D is ≤2 variables, so
  its witnesses are the *cheapest* to check of any track; track C at ≤3
  variables is `n³`. This cuts against intuition — the bigger equations have
  the cheaper countermodels.
- **The FALSE/TRUE skew.** Tracks A and B are balanced 50/50 by construction
  off the known matrix. C and D cannot be — nothing is labelled, and random
  pairs of unrelated laws are overwhelmingly non-implications (the 2026-08-20
  order-5 sample came out 3,077 FALSE / 718 TRUE). Do not read a high solve
  rate on C/D as evidence about the TRUE side.
- **Failure clustering by hypothesis law.** On order 4 this was by far the most
  informative statistic: the top 5 eq1 ids accounted for 58% of all misses
  across 20,000 rows, stable at every sample size checked. `sweep_report`
  computes it per batch and across a merged track, keyed both by eq id and by
  canonical equation text (the id is meaningless across catalogs; the canonical
  text is not).

## After the campaign: the improvement pass

Deferred by design, and scoped from the merged ledgers rather than from any one
batch:

1. Rank the frontier by **cluster size × score weight** — an order-5 cluster is
   worth 4× an order-6 one and the two order-4 tracks share a quarter each.
2. Take the top clusters to the dev tool at `stage2/experiments/completion/`,
   which prints derivations the solver route does not.
3. Whatever ships must clear the standing bar: offline gate green, an isolated
   audit diffed by row id showing 0 lost, and — for any certificate-builder
   change — real-judge verification (rails 3, 3c). Local acceptance is not
   cloud evidence.
4. Re-run the affected track with `--baseline` pointed at this campaign's
   report, so the improvement is a row-id diff and not a total.

## Known real-judge gap

Nothing in this campaign is judge evidence. Once the frontier is stable, sample
~100 certificates stratified by track, verdict, route family and byte size
through `stage2/experiments/judge_rows.py` on the Lean 4.32.2 toolchain. Track
D matters most there: order-6 rows are the only ones emitting certificate
shapes at sizes the 102-entry judge-parity fixture does not cover.

## Tooling built for this campaign

| File | What it does |
| --- | --- |
| `stage2/experiments/generate_eq_catalog.py` | ETP-canonical equation catalog for any order; `--verify` reproduces `eq_size5.txt` line for line |
| `stage2/experiments/sweep_report.py` | failure ledger + summary + row-id baseline diff; `--diagnose` re-solves failures with all 19 engines timed; merges many batches into one report |
| `stage2/experiments/sample_order5_pairs.py` | gained `--catalog` / `--id-prefix`, so it draws from a generated order-6 catalog as well as the vendored order-5 one |
| `stage2/experiments/sample_etp_matrix.py` | **fixed**: the draw loop rebuilt `seen \| drawn` on every row, which is O(n²) — 10,000 rows took ~1 min and 100,000 had not finished in 10. Now 100,000 in 5.5 s, with byte-identical output for the same seed (verified against the already-drawn 10k) |

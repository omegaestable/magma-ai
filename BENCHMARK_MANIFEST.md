# Benchmark Manifest

**What this file is.** The inventory of every problem set in the repo: what each
one is, where it came from, how big it is, and how the sets overlap each other.
Everything below is a property of the *files on disk* — it does not move when the
solver changes. Counts, splits, disjointness and hashes in this document were
measured directly on **2026-08-13**.

**What this file is not.** A scoreboard. Solved counts, coverage, audit wall
clocks and judge evidence belong to **`CLAUDE.md` → "Current measured state"**,
which is the single authority for them; per-session detail lives in
`stage2/results/`. This file carried `1201/1669 solved` from a 2026-05-18 run
long after it stopped being true — the exact stale-headline failure CLAUDE.md
warns about. The fix is structural: coverage numbers are not restated here at
all, and this file should never need editing because a run went better.

Stage 1's prompt-evaluation files are a separate, finished archive — see the last
section.

## The three distinct corpora

Everything the solver is measured against locally reduces to three
**pairwise-disjoint** corpora. Every other benchmark file in the repo is a copy,
a notational mirror, or a subset of one of them.

| Corpus | Rows | TRUE / FALSE | Equation catalog | Notation |
| --- | --- | --- | --- | --- |
| Official public sets — `normal`, `hard1`, `hard2`, `hard3` | 1,669 | 819 / 850 | ETP order-4 | `◇` |
| HF `evaluation_*` sets — 4 files, 200 rows each | 800 | 400 / 400 | order-4, except `evaluation_order5` | `*` |
| `sample_200` — an ETP sample, not an official set | 200 | 100 / 100 | ETP order-4 | `◇` |
| **Distinct total** | **2,669** | **1,319 / 1,350** | | |

Disjointness was checked two independent ways, and both give **0 overlap** for
all three pairs: no shared `(eq1_id, eq2_id)` pair, and no shared implication
after normalising `*`/`◇` to one symbol and renaming variables in
first-appearance order. So the HF `evaluation_*` sets really are the only local
proxy for a distribution the solver was never tuned against — that is why
`spotcheck.py` samples them alongside the official four and calls the union "the
8 distinct benchmark sets".

Per-file detail:

| File | Rows | TRUE / FALSE | `difficulty` | Notes |
| --- | --- | --- | --- | --- |
| `normal.jsonl` | 1,000 | 500 / 500 | `normal` | |
| `hard1.jsonl` | 69 | 24 / 45 | `hard` | the only set that is not label-balanced |
| `hard2.jsonl` | 200 | 100 / 100 | `hard` | |
| `hard3.jsonl` | 400 | 195 / 205 | `hard` | |
| `evaluation_normal.jsonl` | 200 | 100 / 100 | `normal` | |
| `evaluation_hard.jsonl` | 200 | 100 / 100 | `hard` | |
| `evaluation_extra_hard.jsonl` | 200 | 100 / 100 | `extra_hard` | |
| `evaluation_order5.jsonl` | 200 | 100 / 100 | `order5_normal` | **order-5 laws** — see catalogs below |
| `sample_200.json` | 200 | 100 / 100 | — | ETP rows; ids leak the label, see "Problem shape" |

## Copies, mirrors and subsets

None of these adds a distinct implication. Knowing that is what keeps totals
honest.

| File | Rows | Relationship to a corpus above |
| --- | --- | --- |
| `data/stage2_official_problems/*` | — | **Byte-identical** copy of the vendored official files — sha256-checked on all seven shared top-level files, `eq_size5.txt` included. This is the copy `audit_corpus.py` actually reads: `PROBLEMS_DIR` points here, not at `vendor/`. |
| `data/hf_cache/` `normal`, `hard1`, `hard2`, `hard3` `.jsonl` | 1,669 | Exact notational mirrors of the official four: identical id lists in identical order, **0 answer mismatches over all 1,669 rows**, `*` in place of `◇`. Useful only as an alpha-invariance test of the solver's parsing and of `DISTILLED_CERTS` content-keying. |
| `data/hf_cache/hard.jsonl` | 200 | 200 rows carrying just **69 distinct implications — exactly `hard1`'s** — resampled with multiplicity up to 4 (0 conflicting answers). Row-level split 74 / 126 TRUE / FALSE is that multiplicity, not new content. |
| `sample_20.json` | 20 | 20 rows **of `normal`**, ids and all (`normal_0646`, `normal_0103`, …). The audit's default smoke set. |
| `marathon/normal_100.jsonl` | 100 | The first 100 rows of `normal` (`normal_0001`…`normal_0100`). Marathon smoke slice. |

## Row accounting: the naive total double-counts by 20

```
official normal + hard1 + hard2 + hard3     1,669   distinct
HF evaluation_* x4                        +   800   distinct, disjoint from official
sample_200                                +   200   distinct, disjoint from both
                                            -----
distinct rows                               2,669
```

A **2,689** total has appeared in session notes. It is the sum of the two audit
invocations rather than of the corpora: `--all` audits `SETS`, which is
1,000 + 69 + 200 + 400 + `sample_20` (20) + `sample_200` (200) = **1,889**, and
`--hf` audits **800**. 1,889 + 800 = 2,689 — but all 20 `sample_20` rows are
already inside `normal`, so 20 rows are counted twice.

Both numbers describe the same work; the audit re-solves `sample_20` on purpose,
because it is the cheap smoke set. Only the *sum* is wrong. **Quote the three
corpora separately** — "official 1,669, HF `evaluation_*` 800, `sample_200` 200"
— or quote **2,669** if one number is unavoidable.

## Problem shape

Every row is a flat JSON object. Fields, and which files carry them:

| Field | Where | Meaning |
| --- | --- | --- |
| `id` | all | set-local row id |
| `eq1_id`, `eq2_id` | all | **1-based line index** into an equation catalog (below) |
| `equation1`, `equation2` | all | the hypothesis and goal laws, as text |
| `answer` | all except `sample_20.json` | ground-truth label. Absent from the private evaluation set. |
| `index`, `difficulty` | official `.jsonl` + HF `.jsonl` only | not present in `sample_20` / `sample_200` |

Two consequences worth carrying:

- **`sample_20` has no `answer` field**, so an audit of it measures *coverage
  only* — `audit_corpus.py` label-checks a row only when `problem["answer"]` is a
  bool. Never quote a `sample_20` number as accuracy evidence.
- **`sample_200`'s ids encode the label**: they are `true_<eq1>_<eq2>` /
  `false_<eq1>_<eq2>` (e.g. `true_2739_2736`, `false_1876_1895`). That is fine for
  a fixture and radioactive for solver policy — it is CLAUDE.md rail 9 with a
  loaded gun. No route may read `id`.

More generally: **the field set is not uniform across these files**, so any
solver gate written as `problem.get(a) == problem.get(b)` has to require both
keys present. Rail 5g records what happened when it did not — two absent ids
compared equal and the row got `exact h`.

## Equation catalogs

`eq1_id` / `eq2_id` index a catalog file by line number. **There are two
catalogs, and they do not share a numbering** — which is why an id-pair
comparison across sets is only meaningful within one of them:

| Catalog | Laws | Notation | Used by | Path |
| --- | --- | --- | --- | --- |
| ETP order-4 | 4,694 | `◇` | official sets, `sample_20`, `sample_200`, `evaluation_normal`/`_hard`/`_extra_hard` | `data/exports/equations.txt` |
| Order-5 | 62,576 | `*` | `evaluation_order5` only | `vendor/stage2-official/examples/problems/eq_size5.txt` (and its byte-identical copy in `data/stage2_official_problems/`) |

Spot-verified 2026-08-13: `equations.txt` line 2918 is `x = ((y ◇ (x ◇ y)) ◇ z) ◇ w`,
matching `normal_0001`'s `eq1_id`; `eq_size5.txt` line 19883 is
`x = (y * x) * ((z * (x * x)) * z)`, matching `evaluation_order5_0001`'s.

Observed id ranges: the order-4 sets all sit in [1, 4693]; `evaluation_order5`
sits in [4863, 41402]. That gap is the reason `evaluation_order5` cannot collide
with anything else by id — and the content check above confirms it does not
collide by law either.

## The ETP outcome matrix — the fifth source

`data/exports/` holds the Equational Theories Project export, not a benchmark
set: a 4,694 x 4,694 outcome matrix (~22M labelled implication pairs) plus the
raw implication CSV and closure. It is a second ground truth the solver has never
been tuned against, and `spotcheck.py` samples it as source `etp` alongside the 8
distinct benchmark sets. `sample_200` is drawn from this same space, which is why
it is disjoint from the official sets.

`data/teorth_cache/` is the mined teorth material (equation catalog, duals,
implication graph, packed outcome matrix, cached proof pages) — theory input, not
a benchmark. See `theory/TEORTH_WORKFLOW.md`.

## Which tool reads which set

| Tool | Default | `--all` | `--hf` |
| --- | --- | --- | --- |
| `stage2/experiments/audit_corpus.py` | `sample_20` (20 rows) | `SETS` — 1,889 rows | the 4 `evaluation_*` sets — 800 rows |
| `stage2/experiments/spotcheck.py` | balanced random batches over the 8 distinct sets + `etp` | | |

Note `--hf` covers only the four `evaluation_*` sets, **not** the HF mirrors of
the official sets — those are excluded on purpose (no new content). Real-judge
campaigns have sometimes also run `data/hf_cache/hard.jsonl`; that is 200 rows of
`hard1` content, so treat it as extra judge samples of known implications, not as
200 more problems.

Two standing rules from CLAUDE.md apply whenever these files are audited:
**never run two `audit_corpus.py` sweeps concurrently** (rail 5e), and when
measuring a deployed tier, pass `--row-budget` — Solo and Marathon always bound a
row and the audit does not unless told to (rail 12).

## How the sets are consumed by the official harness

**Solo** runs one problem per solver subprocess over stdin/stdout JSON. Use it
for fast certificate debugging. Canonical docs:

```text
vendor/stage2-official/docs/solo_mode.md
vendor/stage2-official/examples/solo/TUTORIAL.md
```

**Marathon** runs many problems per solver subprocess from a manifest JSONL,
appending answers to an output JSONL under one global budget. Use it for
competition strategy, triage and cache reuse. Canonical docs:

```text
vendor/stage2-official/docs/marathon_mode.md
vendor/stage2-official/examples/marathon/TUTORIAL.md
```

Any benchmark file above can be a Marathon manifest; `marathon/normal_100.jsonl`
is the shipped smoke slice. Budgets, sandbox limits and judge caps are **not**
restated here — they are configuration, they have drifted before, and
`CLAUDE.md` plus `vendor/stage2-official/pipeline/config.json` are the
authorities.

## Provenance and refresh

`theory/tools/fetch_problem_sets.py` maintains both local caches: it downloads
the Hugging Face subsets of
`SAIRfoundation/equational-theories-selected-problems` into `data/hf_cache/`
(9 subsets, recorded with URLs and byte counts in `data/hf_cache/manifest.json`,
fetched 2026-05-12) and copies the vendored official files into
`data/stage2_official_problems/`. Both caches are git-tracked.

If upstream renames or adds a file, the vendored official repo and the current
directory contents are canonical — update this manifest rather than trusting the
names above.

## Local result storage

`stage2/results/` holds Stage 2 run summaries, failure ledgers and promotion
evidence, date-stamped. Do not mix Stage 2 results into the archived Stage 1
result directories. Superseded summaries stay — they are the evidence trail — so
read the date on a file before quoting it; the most recent sessions are
`2026-08-12-tier-inversion-and-latency.md` and
`2026-08-12-final-nine-completion.md`. `CLAUDE.md` names the current ones.

## Stage 1 archive

```text
stage1/data/benchmark/
stage1/data/hf_cache/
```

Historical analysis only. Stage 1 is finished; no work starts there.

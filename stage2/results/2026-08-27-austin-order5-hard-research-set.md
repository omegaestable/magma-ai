# 2026-08-27 — `research_order5_hard`: the organizers' Austin-law research set

Not a leaderboard artifact. The organizers posted a 100-row "experimental"
dataset (HF config `research_order5_hard`, dataset
`SAIRfoundation/equational-theories-selected-problems`) built entirely from
teorth's own **unresolved** order-5 Austin-law classification, explicitly
excluded from evaluation and with "ground truth unknown for some" rows. This
doc records what the dataset actually is and what the current solver toolkit
can and cannot do with it. Every number below is measured; nothing here
changed `stage2/submissions/solver.py`'s behavior or the official-corpus
numbers in `CLAUDE.md`.

## What the dataset is

An **Austin law** admits infinite models but no nontrivial finite ones
(`paper/blueprint_source/chapter/order_5.tex`, confirmed unchanged against
the live blueprint page today). Teorth's classification of the 106 order-5
laws with only-trivial finite models splits into three groups:

- **Table 1 — 10 confirmed Austin laws** (4916, 15535, 17522, 20034, 22455,
  22818, 25964, 28770, 30591, 41082).
- **Table 2 — 96 equations**, trivial finite models confirmed, but Vampire's
  decision procedure could not establish whether they admit infinite models
  (i.e. Austin-status is open).
- **Table 3 — 24 equations**, where even nontrivial-finite-model *existence*
  is unknown.

Every one of the 100 dataset rows pairs `eq2` = one of the 10 confirmed
Austin laws with `eq1` drawn **exclusively** from Table 2 or Table 3 (verified
by id cross-reference, zero rows fall outside both tables). 69 distinct `eq1`
values appear: 55 from Table 2, 14 from Table 3 (21 of the 100 rows touch a
Table-3 `eq1`). This is teorth's actual open research frontier, handed to us
as a "problem set."

## The reduction that matters

Because every `eq2` is a *confirmed* Austin law (no nontrivial finite model,
period), the FALSE side of every row collapses to a question about `eq1`
alone: **any nontrivial finite model of `eq1` is automatically a countermodel**,
regardless of which Austin law it's paired against — a nontrivial finite
model can never satisfy an Austin law by definition. Symmetrically, the
cheapest possible TRUE route is **`eq1` collapsing to `x = y`** under pure
equational logic (sound in every model, finite or infinite): that would prove
`eq1 ⇒ anything`, settling every row sharing that `eq1` at once, and would
also mean `eq1` is not actually Austin-compatible at all.

So the 100 rows reduce to 69 independent per-`eq1` questions, each answerable
by solving the synthetic pair `eq1 ⇒ (x = y)` — a strictly smaller/cheaper
goal than the real Austin-law targets (rail 5d), and it exercises exactly the
two mechanisms capable of resolving *any* row here. It does not cover a
theoretical third case (a direct, non-collapse equational consequence of
`eq1` that happens to imply one specific Austin law without full collapse);
that case is the reason the real-goal audit (below) was also run in full.

## What was run

| # | What | Command shape | Result |
| - | --- | --- | --- |
| 1 | Full 100 rows, real Austin goals, `fast` tier, **unbounded** row clock | `audit_corpus.py --file research_order5_hard.jsonl --effort fast` | **0/100 solved**, 0 crashes, 3903 s wall (16 workers) — every row ran its entire fast-tier engine chain to exhaustion (~460 s/row average; contrast the official corpus's 1889 rows/145 s, where most rows short-circuit early) |
| 2 | 69 unique `eq1` vs `x=y`, `fast` tier, single-pass, 60 s/row cap | same, `--single-pass --row-budget 60` | **0/69**, 482 s wall |
| 3 | Same 69, `standard` tier (7.5×), 90 s/row cap | `--effort standard --single-pass --row-budget 90` | **0/69**, 723 s wall |
| 4 | The 14 Table-3-only `eq1`, `deep` tier (22×), 180 s/row cap | `--effort deep --single-pass --row-budget 180` | **0/14**, 722 s wall |
| 5 | All 69, `completion_prove` called directly (bypasses the other ~13 engines) | one-off script, `time_budget=90, escalate=True` | **0/69** — every row hit `COMPLETION_ESCALATION_SECONDS = 25.0`, a deliberately fixed, non-tier-scaled absolute cap on the escalated (unfailing-superposition) mode; most finished in ~25 s |
| 6 | The 14 Table-3 `eq1`, `_completion_prove_once` called directly with the 25 s design cap **removed** (240 s budget, `max_active` 400→4000, pair-weight ladder to 960) | one-off script | **0/14**, and **none even saturated** — `saturated: False` with 584–54,053 pairs dropped for size/capacity in every row |

`--single-pass` is a new `audit_corpus.py` flag (kept in the tree): it skips
`solve_problem`'s cheaper-tiers-first ladder and runs exactly one pass at
`--effort`. The ladder's assumption that a failing cheap pass is near-free
(~0.15 s median, per its own docstring) is false on this family — run #1
alone cost ~460 s/row — so laddering into `standard`/`deep` would have taxed
every row for that cost before ever trying the deeper tier.

Every run's offline oracle checks (proof kernel for TRUE, independent
witness re-verification for FALSE) reported **0 oracle failures** throughout,
because there was nothing to check — every row is `skip`/`no_collapse`. No
certificate was ever emitted, so none needed real-judge verification.

## Reading the result

Zero solved across six escalating attempts, including one that gave the
single strongest general-purpose TRUE mechanism in the solver
(`completion`, unfailing superposition + normalize-at-push + variable-merge
seeding) roughly **10× its deployed time budget** — and it still didn't
saturate, let alone collapse, on any of the 14 rows where the answer is most
plausibly still open in the literature. That is not evidence of a solver
defect. It is the expected outcome of handing a curve-fit, engineered
heuristic portfolio a set of equations selected *because* a complete,
dedicated first-order superposition prover (Vampire) already ran on
essentially this same question — "does `eq1` admit an implication to another
law in this set, in particular to `x=y`" — and came back empty for all 96
Table-2 equations (`paper/blueprint_source/chapter/order_5.tex`, §"Equations
with trivial finite models"). Table 2's FALSE side is additionally not just
hard but **provably closed**: "no nontrivial finite model" is an established
fact for those 55 `eq1`'s, so no amount of finite countermodel search will
ever find one there.

What would actually move this: a bespoke infinite-model construction per
`eq1` along the lines of `paper/blueprint_source/chapter/
infinite_magma_constructions.tex` (translation-invariant/affine magmas,
Asterix-equation-style reduction to a univariate functional equation), which
is genuine per-equation mathematical work, not a search the current engines
are shaped to do — or a complete ATP integration (Vampire/E/Prover9), which
is out of scope for a sandboxed, no-network submission environment anyway.
Both are real research, not a solver bug fix.

## Side findings (operational, not corpus-affecting)

- **`pool.map(..., chunksize=4)` hides completion until a whole chunk
  finishes.** Watching a run sit at "0 done" for several minutes on a
  16-worker pool is expected when each worker's first chunk (4 rows × up to
  the row budget) hasn't finished yet — not a hang. Confirmed by reading the
  main process's own `rows`/`i` locals live with `py-spy dump --pid <main>
  --locals` while it ran; this is a good general technique for reading
  `audit_corpus.py` progress without waiting for its own coarse print
  cadence.
- **`COMPLETION_ESCALATION_SECONDS = 25.0` is deliberately absolute** (the
  comment at `solver.py:8648` explains why: a tier multiplier there would
  hand a last-resort TRUE search the budget the wide countermodel tiers
  need). Confirmed by direct measurement (run #5's uniform ~25 s
  timings) rather than by reading the comment alone.
- Per-row cost on this specific equation family (order-5, 4–5 operations,
  drawn from a set two independent tools — ours and Vampire's — both find
  hard) is **not** representative of order-5 in general; do not fold the
  ~460 s/row `fast`-tier figure into any deployed-tier cost model without a
  random (not adversarially curated) order-5 sample to compare against.

## Artifacts

- `data/hf_cache/research_order5_hard.jsonl` — canonical mirror (added
  `research_order5_hard` to `theory/tools/fetch_problem_sets.py`'s
  `HF_SUBSETS`, same convention as `evaluation_order5`).
- `stage2/experiments/audit_corpus.py` — new `--single-pass` flag.
- Raw JSON from every run above is under `stage2/results/2026-08-27-austin-*.json`
  (gitignored, regenerate with the commands in the table).

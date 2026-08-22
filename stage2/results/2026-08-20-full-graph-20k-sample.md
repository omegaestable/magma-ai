# 2026-08-20: 20,000-row random sample of the full order-4 ETP graph

Goal: push testing beyond the 2,669-row official+HF+sample_200 corpus (100%
solved) into the full ~22M-pair order-4 ETP outcome matrix
(`data/exports/general_outcomes.json.gz`, 4,694x4,694 laws), which the solver
has never been systematically measured against at this scale. Four balanced
5,000-row batches (batches 1-2 got a real-LLM lemma-lane pass over their
unsolved rows; batches 3-4 were added later the same session and are
offline-only so far), offline audit throughout (no cloud judge). This is a
**measurement + logging** session per explicit instruction — no solver
changes, fixes deferred to a later "improvement pass" session.

## Method

- `stage2/experiments/sample_etp_matrix.py` (new): draws a random sample from
  the full matrix, reusing `spotcheck.ETPMatrix` (same rejection-sampling
  logic already used for the standing spotcheck loop), balanced 50/50
  true/false, preferring pairs outside the spotcheck coverage ledger.
  `--exclude` accepts prior batches so a second draw cannot repeat pairs.
- `stage2/experiments/audit_corpus.py` (extended): new `--file` flag runs the
  existing solve -> offline-oracle -> ground-truth-label pipeline
  (`audit_row`) against an arbitrary jsonl, not just the named official/HF
  sets. No change to audit semantics otherwise.
- `stage2/experiments/llm_balanced_eval.py` (extended): new `--file` /
  `--all-in-file` flags let it run the real two-phase (network-threads /
  verify-processes, rail 6) LLM lemma lane directly against a pre-built
  frontier file instead of only the three hardcoded official sets.
- Batch 1: seed `20260820`, `stage2/results/etp-sample-5000-2026-08-20.jsonl`.
- Batch 2: seed `20260820002`, excluding batch 1,
  `stage2/results/etp-sample-5000-batch2-2026-08-20.jsonl`. Verified 0
  row-id overlap with batch 1.
- Batch 3: seed `20260821003`, excluding batches 1-2,
  `stage2/results/etp-sample-5000-batch3-2026-08-20.jsonl`. Verified 0
  row-id overlap with batches 1-2.
- Batch 4: seed `20260821004`, excluding batches 1-3,
  `stage2/results/etp-sample-5000-batch4-2026-08-20.jsonl`. Verified 0
  row-id overlap with batches 1-3.
- All four audited at `fast` effort, unbounded per-row (the audit's
  historical "ceiling" mode, matching how the official 1,669-row corpus is
  measured — rail 12 says add `--row-budget` only when modeling a deployed
  tier, which this is not). Order-4's cost profile never needed a cap, unlike
  the order-5 sampling run the same session (see
  `2026-08-20-order5-sample-4000.md`).

## Results

| | Batch 1 | Batch 2 | Batch 3 | Batch 4 | Combined |
| --- | --- | --- | --- | --- | --- |
| Rows | 5,000 | 5,000 | 5,000 | 5,000 | **20,000** |
| Solved | 4,989 | 4,988 | 4,988 | 4,983 | **19,948 (99.74%)** |
| Skipped | 11 | 12 | 12 | 17 | 52 |
| Crashes | 0 | 0 | 0 | 0 | 0 |
| Oracle failures | 0 | 0 | 0 | 0 | 0 |
| Wall clock (16 workers) | 1,478 s | 2,340 s | 1,342 s | 2,191 s | — |

0 oracle failures and 0 crashes across every row means every TRUE verdict
proof-kernel-verified or model-checked, and every FALSE verdict's witness
table independently re-verified — no unsound answer anywhere in 20,000 fresh
rows the solver was never tuned against.

## The failure frontier is overwhelmingly one law family - but not entirely

All 52 unsolved rows are logged in
`stage2/results/etp-sample-failures-2026-08-20.jsonl` (id, eq1/eq2 text,
ground-truth label, deterministic seconds, LLM-lane outcome where attempted).

- **51/52 are TRUE-labeled**, consistent with the established pattern that
  the FALSE/countermodel search is the solid side and TRUE proof search is
  where misses concentrate (rail 5d family) - but batch 3 added the first
  **FALSE** miss of the sample, `etp_1661_3524` (eq1
  `x = (x ◇ y) ◇ ((y ◇ z) ◇ y)`), so "the countermodel search is airtight"
  should be read as "airtight to 1-in-20,000", not literally 0, and batch 4
  added none more (still exactly 1). Worth a dedicated look in the
  improvement pass: is this a genuinely hard countermodel (needs an
  order/shape the cheap+wide tiers don't try), or a gap in the search's
  coverage.
- Of the 51 TRUE misses, essentially all have an **eq1 of the shape
  `x = F(x, y, z)`, `term_size(F) = 4`** — e.g. `etp_2920_*`'s eq1
  `((y ◇ (x ◇ z)) ◇ x) ◇ y = x` is the same shape (up to renaming) as
  `hard2_0073`'s eq1, the family closed in the 2026-08-12 session by ordered
  completion (Knuth-Bendix), not by equality saturation (see "Two claims
  that stood in this file were wrong" in `CLAUDE.md`).
- Clusters on a small set of eq1 ids across multiple eq2 targets, now even
  sharper at 20,000 rows: `1350` (9 hits), `2920` (6), `944` (6), `1923` (5),
  `2307` (4, new at batch 4) - the top 5 hypothesis laws now account for 30 of
  52 failures (58%), each failing against several different unrelated goals.
  This is a hypothesis-side property, not a goal-side one, and the ratio has
  held steady across every batch size checked so far (13/23 = 57% at 10,000;
  20/35 = 57% at 15,000; 30/52 = 58% at 20,000).

## Real LLM lemma lane: 0/23 closed, 0 unsafe (batches 1-2 only)

Batches 3-4's 29-row combined frontier have **not** had an LLM pass yet -
only batches 1-2 (23 rows total) were run through it this session. Ran every
one of those 23 rows through the real `openai/gpt-oss-120b` (via
OpenRouter/DeepInfra) lemma lane, production-matching parameters
(`reasoning_effort=medium`, `max_output_tokens=16384`, matching
`LLM_CONFIG`/`LLM_MAX_OUTPUT_TOKENS` in `solver.py` — the dev script's own
stale defaults of `6144`/no explicit reasoning tier reproduced the exact
"18% of calls losing their answer to token exhaustion" failure mode from the
2026-07-23 session at 100% rate on the first attempt; rerun with corrected
params fixed that).

- Batch 1 (11 rows): 0 closed. 8 `lemma_not_derivable_from_hypothesis`, 2
  `guided_chain_unproved_or_bad_endpoints`, 1 `lemma_does_not_imply_goal`.
- Batch 2 (12 rows): 0 closed. 9 `lemma_not_derivable_from_hypothesis`, 3
  `guided_chain_unproved_or_bad_endpoints`.
- **0 `FATAL`/wrong-verdict outcomes in 23 attempts** — every rejection was
  safe (no candidate submitted), matching the standing soundness bar.

This is consistent with the 2026-08-11 finding that this specific family is
unreachable by equality saturation "at any budget" and needed ordered
completion instead — a single LLM lemma proposal plus one-shot closure search
is structurally the wrong tool for it too, same as the engine that failed on
it before.

## For the improvement pass (not done this session)

The highest-leverage next lever is already identified and already validated,
just not shipped: **port the completion pipeline
(`stage2/experiments/completion/`, `solve_row.py`) into `solver.py` as a
general route**, not per-row distillation. `CLAUDE.md`'s "Known open
frontier" section already carries a GO verdict on this from the 2026-08-12
session, plus one documented defect to fix while porting (a derived collapse
`x = y` is discarded unoriented). This sample makes the case with fresh,
never-tuned-against evidence: 51 of 52 (98%) of the local failure frontier at
20,000 rows is this one family, recurring across unrelated goals. Per rail 9,
any port must generalize the law shape (`x = F(x,y,z)`, `term_size(F) = 4`),
never hardcode the specific eq1 ids surfaced here.

Secondary, lower-confidence observation worth a follow-up sample: whether
`term_size(F) = 4` collapse-shaped eq1 laws are unsolved *in general* by the
deployed engines, or whether these are unlucky specific instances within a
mostly-solved shape — the official/HF corpus already contains solved rows of
adjacent shapes, so this needs a shape-targeted sample, not eq1-id grep, to
answer. Also worth a look: the one FALSE miss, `etp_1661_3524` - is it a
one-off or the first sighting of a second, smaller failure mode.

## Artifacts

- `stage2/experiments/sample_etp_matrix.py` — new sampler
- `stage2/experiments/audit_corpus.py` — `--file` flag added
- `stage2/experiments/llm_balanced_eval.py` — `--file`/`--all-in-file` flags added
- `stage2/results/etp-sample-5000-2026-08-20.jsonl` — batch 1 (5,000 rows)
- `stage2/results/etp-sample-5000-batch2-2026-08-20.jsonl` — batch 2 (5,000 rows)
- `stage2/results/etp-sample-5000-batch3-2026-08-20.jsonl` — batch 3 (5,000 rows)
- `stage2/results/etp-sample-5000-batch4-2026-08-20.jsonl` — batch 4 (5,000 rows)
- `stage2/results/audit-etp-sample-5000-2026-08-20.json` — batch 1 audit
- `stage2/results/audit-etp-sample-5000-batch2-2026-08-20.json` — batch 2 audit
- `stage2/results/audit-etp-sample-5000-batch3-2026-08-20.json` — batch 3 audit
- `stage2/results/audit-etp-sample-5000-batch4-2026-08-20.json` — batch 4 audit
- `stage2/results/etp-sample-5000-unsolved.jsonl` /
  `-batch2-unsolved.jsonl` / `-batch3-unsolved.jsonl` / `-batch4-unsolved.jsonl`
  — the 11 + 12 + 12 + 17 row frontiers
- `stage2/results/llm-etp-sample-5000-batch1-frontier.json` /
  `-batch2-frontier.json` — real LLM lemma-lane attempts (batches 3-4 not yet run)
- `stage2/results/etp-sample-failures-2026-08-20.jsonl` — **the consolidated
  52-row failure log for the improvement pass**, one JSON object per row:
  `batch, id, eq1_id, eq2_id, equation1, equation2, answer,
  deterministic_status, deterministic_seconds, llm_attempted, llm_status,
  llm_detail`

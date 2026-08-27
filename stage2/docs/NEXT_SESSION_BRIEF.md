# Next session brief — resume the 2026-08-26 improvement pass

Written 2026-08-26 late evening, mid-session, at a deliberate stop. Read
`CLAUDE.md` first; this file is the exact resume point. **Nothing is running**
(`Get-Process python*,lean*,lake*` was empty at handover). All work below is
in the **uncommitted working tree** — commit it first thing (`git status`
shows `solver.py`, `test_primitives.py`, the fixture, three new experiment
scripts, and the whole vendored harness sync).

## State of the solver (all gate-green: 285 passed, 2–3 skipped, see below)

Shipped in `stage2/solver/solver.py` this session, each aimed at a *family*:

1. **Multi-fill goal bridge** (`_goal_neighbors(..., fills)`; node cap
   6000 → 200000). Closes eq1 `3569` (34/34), `2854`, `1366`, and both
   formerly "structurally unreachable" rows `etp_1366_3436` / `etp_3569_4653`
   in ≤ 0.1 s. Real judge on Lean 4.33.1: 4/4 bridge certs accepted.
2. **Bridge ON in the probe slot** (`completion_probe_route`, bounded by its
   own 2 s). Without it the same rows landed 120–160 s later after every other
   engine burned its budget (measured inside the gate).
3. **`COMPLETION_BUDGET` 8 → 90, clamped by `COMPLETION_ROUTE_MAX_SECONDS =
   300`.** The eq1 `2923`/`650` families (96 of the 218 order-4 misses) close
   by plain `completion:join`; the join takes 19 s in a fresh process but
   42 s on the (thermally loaded) box an hour later and 60–72 s after the
   closure/egg engines have run — **that drift is unexplained and worth a
   profile** (`_kb_resolve` was memoized; not GC — tested).
4. **`FP_WITNESS_TABLES`**: 113 teorth FinitePoly tables (orders 3–11, ~11 KB),
   greedy set-cover over 480 hard FALSE rows disjoint from the test batch
   (covers 421/436). Tested LAST in `_false_witness_portfolio` so every golden
   pin holds. Judge: 5/5 accepted (orders 5, 6, 8, 11). Closes 13/28 ledger
   FALSE misses at 0.00 s.
5. **5 distilled infinite/large countermodels** (`false:distilled:inf_e*`,
   4.8 KB): 𝔽₂⁵ twisted weak central groupoid as a Nat bit formula (×3),
   teorth tables of order 21 and 24. Judge-accepted on 4.33.1, pinned.
6. **LLM lane egg fallback** in `llm_lemma_candidate` (`LLM_LEMMA_EGG_TIME_BUDGET`).

Packaged size before items 5–6: **484,408 B** (15.6 KB headroom). Re-measure
with `minify_submission.py` before adding anything.

## The harness is now Lean/Mathlib v4.33.1 (upstream `13648682`)

Synced per rail 14; `vendor/stage2-official/UPSTREAM.md` records the merge
(local patches preserved; `proxy.py` conflict resolved by keeping both the
provider normalizer and upstream's per-model `_resolve_model`). Judge caps in
`config.json` unchanged. Parity smoke 4/4 accepted. **Gotcha:** `lake build`
says "Nothing to build" (empty default target) — after wiping `.lake/build`,
build `JudgeMagma JudgeDecide JudgeFinOp JudgeSupport` explicitly and delete
`.artifacts`. Fixture is 127 entries.

## Measured this session (all in `stage2/results/`)

- Completion alone on the 190 TRUE order-4 misses at 45 s: **151/190**
  (`shipped-order4-full.log` in the session scratchpad; families: 650 47/47,
  2923 49/49, 3569 34/34, 3983 6/23, 3051 0/6, 463 0/4).
- Full-solver audit of the 218 ledger: **60/218 — NOT TRUSTWORTHY**, it ran
  under massive self-inflicted contention (rail 5e) and before items 2–5.
  `audit-merged-order4-misses-2026-08-26.json`. **Re-run isolated** — this is
  the first thing to do.
- Order-5 (353 misses): completion 25, library 2 → 27/353. 133 budget-bound,
  195 structural. 0 refutable by the independent battery. **Different wall;
  nothing tried moved it** (180 s completion 0/8, collapse-directed egg 0/7).
- LLM lane, real calls: gpt-oss low 353 rows/238k tok, gpt-oss medium 40/173k,
  gemma-4-31b 40/407k (10 truncated) → **0 settled rows**; the model claims
  TRUE on essentially every row. `llm-settle-order5-*.jsonl`. Harness:
  `stage2/experiments/llm_settle_rows.py` (strip the stale process-env
  `OPENROUTER_API_KEY` first; gemma needs `--no-provider-pin`).
- FALSE misses: search found 0/28 (mace to order 9, z3 to order 10 — proved
  orders ≤ 6 empty —, 973k polynomials); teorth tables 13/28; theory pass
  10/15 of the rest (`infinite-countermodels-2026-08-26.jsonl`, all
  judge-accepted). Still open: eq1 `481` ×3, `2531` ×2 (teorth: confluence /
  greedy models only). Not shipped for bytes: the four ℕ parity certs (2.6 KB
  each) and the order-36 table (3.9 KB, 123 s).
- Hard unseen test batch ready: `etp-hardtest-1000-2026-08-26.jsonl` (500/500,
  **stratified** — 4-op ≥3-var hypotheses, FALSE side hard-region filtered;
  0 overlap with any prior draw). Not yet run.

## 2026-08-27 progress (append)

- Isolated 218 audit (before the bridge-poll fix): **167/218**, 0 oracle
  failures, 0 label mismatches. Official corpus **1869/1869, 0 lost / 0
  gained / 0 flips** vs 2026-08-24; spotcheck 90/90.
- Found and fixed rail 5f-iv #6: the probe-slot bridge enumerated
  `product(fills, repeat=len(unbound))` with no poll between rejected images
  — `hard3_0283` spent 1,445 s in a 2 s slot; now 3.8 s. Added
  `COMPLETION_BRIDGE_MAX_UNBOUND = 3` + a size lower-bound prune + a poll.
- Re-running official + HF + 218 audits after that fix (sequential,
  isolated). Then: swap the flapping `etp_3983_4296` pin for stable 3983
  rows (`etp_3983_4577`, `etp_3983_4483`), package, Marathon on the hard
  1000, docs.

## State at the end of 2026-08-27

Shipped and verified (gate 297/2, official 1869/1869 + HF 800/800 with 0
lost, spotcheck 90/90, 41/41 new certs judge-accepted on 4.33.1, artifact
426,613 B): multi-fill bridge (+ in probe), completion budget 90/cap 300,
escalated caps on false saturation, `FP_WITNESS_TABLES`, `false:formula:WCG5`,
10 infinite/large distilled certs, 16 large live-solvable distilled entries
deleted (rows re-judged 16/16). Marathon on the hard 1000: see
`stage2/results/2026-08-26-improvement-pass.md`. Still uncommitted.

Organizer stress test (final-leaderboard config): 200/200 offline, 200/200
real-judge. Hard-1000 Marathon: 999/1000 accepted, 0 rejected; the one miss is
`etp_1486_3862` (FALSE, eq1 `x = (y ◇ x) ◇ (x ◇ (z ◇ z))`, eq2
`x ◇ x = (x ◇ (x ◇ x)) ◇ x`) — first thing to try: the teorth library scan +
z3 at n=7..9, same as the 28-miss hunt.

## Next levers, ranked (from the measurements, not guesses)

1. **Order-5 collapse bucket (≈250 of 353, all TRUE-by-collapse, z3-proved).**
   The collapse lives in critical pairs of weight > 44. Escalation to (60,
   2000) gets ~7.5%; 22/40 were still budget-bound at 120 s. A completion that
   keeps large pairs cheaply (term indexing, or capping the number of *derived
   rules* instead of pair weight) is the engine to build. Positive control:
   `order5_18399_29663` (collapse at the 4th derived equation).
2. **eq1 `3983` (17 rows)**: bridge needs ~175 s / 316k nodes at slack ≥ 6 —
   lands at standard/deep tiers only. Smarter frontier ordering would bring it
   to `fast`.
3. **eq1 `481` ×3 and `2531` ×2**: only confluence/greedy refutations exist
   in teorth — needs the free-magma-mod-rewrite construction as a Lean cert.
4. **eq1 `3051`/`463`/`1740`/`4465`/`4457`** (structural saturation even at
   60/2000): need derived helper facts (egg_ladder-style rungs from a small
   law library) rather than bridge moves.

## Old resume queue (done)

1. Commit. Gate (`-n auto` on a quiet box; sequential if skip count ≠ 2 — the
   third skip seen today is the `etp_3983_4296` pin drifting between
   `egg_ladder:goal:h1` and `completion:bridge` on timing; re-pin it with
   `judge_rows.py --ids etp_3983_4296 --append-fixture` after removing its
   old line, or accept the drift skip).
2. **Isolated** audit of the 218 ledger: `audit_corpus.py --file
   stage2/results/merged-order4-misses-218-audit.jsonl --row-budget 420` —
   nothing else running. Expect ~170/218; diff residual vs
   `order4-residual-after-fix-ids.json`.
3. Isolated official audit (`--all`), diff by row id vs
   `audit-2026-08-24*.json`: **0 lost required**. Then `spotcheck.py`.
4. `package_solver.ps1`; confirm < 500,000.
5. Real Marathon on the 1000-row hard batch (`tmp_stage2_smoke/real-run-tools/
   run_marathon_batch.py`, real key via `.env`, 4.33.1 judge). Report as
   stratified.
6. Results doc `stage2/results/2026-08-26-improvement-pass.md` + CLAUDE.md
   table refresh + `LATEST_HANDOFF.md`.

## Levers not taken (ranked)

- Order-5 wall: no deterministic idea moved it; the LLM lane didn't either.
  The one untried angle is FALSE-side: 253/353 have no small model of eq1 —
  z3 unsat proofs on a sample would tell whether they are TRUE-by-collapse
  (then a stronger collapse prover) or FALSE with large/infinite witnesses.
- A **bit-formula witness renderer** (Nat.land/lor/shiftLeft): the 𝔽₂⁵
  magma judged in 15 s as a formula vs 262 s as a 32×32 `List.getD` table —
  unlocks order > 25 witnesses generally.
- An **infinite parity-model witness family** (the `Equation1661` dual) as a
  certificate builder instead of per-row distillation.
- eq1 `3051` (6 rows) needs derived helper facts, not bridge moves (leaf
  inflation measured 0/7).

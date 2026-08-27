# 2026-08-26/27 — the improvement pass: learn the merged frontier, test the LLM lane for real, sync to Lean 4.33.1

Fix session after three pure-measurement campaigns (110k + 200k + 200k unseen
order-4 rows, 20k order-5). Input: `merged-order4-misses-218.jsonl` (190 TRUE /
28 FALSE) and `order5-sweep-20k-2026-08-25-ALL-failures.jsonl` (353, unlabeled).
Rule kept throughout: fix the *family*, never the row (rail 9); every
certificate-builder change judge-verified (rail 3c); diff by row id (rail 2).

## Headline

| Measurement | Before | After |
| --- | --- | --- |
| Order-4 ledger (218 rows, all previously missed), full solver, **isolated**, 420 s/row | 0/218 by construction | **167/218** (149 TRUE / 18 FALSE), 0 oracle failures, 0 label mismatches, 0 crashes |
| eq1 `2923` / `650` / `3569` / `2854` (the four-law frontier, 70% of all misses) | 0 | **46/49, 46/47, 34/34, 2/2** |
| The two "structurally unreachable" survivors `etp_1366_3436`, `etp_3569_4653` | open since 08-24 | closed in 0.1 s, judge-accepted |
| FALSE misses (28) | 0 | **18/28** (13 library + 5 distilled infinite/large) |
| Order-5 ledger (353) | 0 | 27/353 — a different wall (see below) |
| Real judge on new certificate families (Lean 4.33.1) | — | **15/15 accepted** |
| Offline gate | 270 passed / 2 skipped | 285 passed / 2 skipped |
| Official corpus + HF, isolated, row-id diff vs 2026-08-24 | 2669/2669 | **1869/1869 + 800/800, 0 lost / 0 gained / 0 flips**, 0 oracle failures; spotcheck 90/90 |

## What shipped, and the measurement behind each

1. **Multi-fill goal bridge** (`_goal_neighbors(..., fills)`). The bridge filled
   an unbound target-side variable with one constant (the smallest in the
   matched subterm). Adding the goal's own skolem constants as candidates
   closes eq1 `3569` (34/34, 0.1 s each), `2854`, `1366`, and both survivors —
   none of which closes without it. Node cap 6000 → 200000 (eq1 `3983` needs
   ~71k expansions; the deadline is the real stop, rail 5f).
2. **Bridge ON in the probe slot.** Off since 08-24 because a single-fill
   bridge turned ~0 s saturation losses into full-budget losses; multi-fill
   closes the families above in ≤ 0.1 s and polls the probe's own 2 s
   deadline. Measured inside the gate: without it the same rows landed
   120–160 s later after every other engine burned its budget.
3. **`COMPLETION_BUDGET` 8 → 90 s, clamped by `COMPLETION_ROUTE_MAX_SECONDS =
   300`.** eq1 `2923`/`650` (96 of 218) close by plain `completion:join`,
   which needs 19 s in a fresh process — but 42 s on the same thermally
   loaded box an hour later and 60–72 s after the closure/egg engines have run
   (not GC: tested). The unclamped ×22 deep scaling would have handed
   completion the whole Solo row ahead of the wide countermodel tiers.
4. **`FP_WITNESS_TABLES`** — 113 teorth FinitePoly tables (orders 3–11, ~11 KB).
   Provenance chain, end to end: `teorth_finitepoly_library.py` extracts the
   1,048-table FinitePoly library to
   `stage2/results/teorth-finitepoly-library.jsonl`, and
   `select_witness_library.py` runs greedy set-cover over it against 480 hard
   FALSE rows the old named tables miss (disjoint from the held-out test
   batch): covers 421/436 at ~1.5 ms per row. Tested last in the portfolio so
   every golden route pin holds (first: 5 pins broke; after families: 1).
   The witness hunt behind it: constraint search to order 9, z3 to order 10
   (which *proved* orders ≤ 6 empty for the survivors), 973k quadratic
   polynomials — **0 witnesses by search, 13 by looking in teorth's tables**.
5. **Five distilled infinite/large countermodels** (`false:distilled:inf_e*`,
   4.8 KB): a twisted weak central groupoid on 𝔽₂⁵ written as a Nat bit
   formula (3 rows; 496 B, 15 s — the same magma as a 32×32 `List.getD`
   table took 262 s), and teorth refutation tables of order 21 and 24.
   Five more accepted certs (ℕ parity model dual to teorth `Equation1661`,
   ×4; an order-36 table) are in `infinite-countermodels-2026-08-26.jsonl`
   but not shipped — 14 KB against ~10 KB of headroom.
6. **LLM lane egg fallback** in `llm_lemma_candidate`; `_kb_resolve` memoized.
7. **`false:formula:WCG5`** — the 𝔽₂⁵ twisted weak central groupoid as a live
   closed-form witness family (bit-formula certificate, byte-identical to the
   accepted `etp_1485_1483` code). Refutes 31,779 ETP pairs, 44 of them by no
   named table; live route serves 35. Judge 6/6 accepted. +1.7 KB.
8. **Escalated completion caps on false saturation**: `completion_route`
   re-runs at (`max_size` 60, `max_active` 2000) only when the cheap caps
   saturate short of the goal with clock left. On the order-5 frontier the
   shipped caps discard the 5-op critical pairs and report a false
   saturation in 0–12 s where the dev tool at (60, 2000) derives the collapse;
   on order-4 it closes 3 of the 14 small-family stragglers instantly.
9. **Bytes**: 56 distilled entries are now live-solvable and offline-verified
   (`distilled-deletion-candidates-2026-08-27.json`); the 16 largest (81 KB,
   each solved live in ≤ 14 s) were deleted and their rows re-judged
   **16/16 accepted** on the live routes; the four ℕ-parity certs and the
   order-36 table then shipped as `inf_e*` distilled entries.

Byte cost: packaged artifact 472,522 → 492,853 (peak) → **426,613 B** after the byte work (73 KB headroom).

## The LLM lane, answered with real calls

Three configurations on the order-5 frontier through the shipped pipeline
(`llm_settle_rows.py`: prompt → model → `candidate_from_llm_text_with_reason`
→ offline oracles; any kernel-verified TRUE or exhaustively-checked FALSE table
counts as settled, no label needed):

| Config | Rows | Completion tokens | Settled |
| --- | --- | --- | --- |
| gpt-oss-120b, `reasoning_effort=low` (deployed) | 353 | 238,498 | **0** |
| gpt-oss-120b, medium | 40 | 172,937 | **0** |
| gemma-4-31b-it (unpinned; DeepInfra 404s it) | 40 | 407,403 (10 truncated at 16k) | **0** |

The model claimed TRUE on every row it answered and never proposed a table;
106/353 proposed lemmas were underivable even with the egg fallback, 84
did not imply the goal. Reasoning effort is not the binding constraint. On
the evidence of 433 calls / ~820k tokens the lane earns nothing on the
frontier; it stays in for the free-lunch cases it was built for.

## Order-5: what the wall actually is (z3 classification, 60-row sample)

`order5-classification-2026-08-27.{jsonl,md}`. **40/40 sampled "collapse
candidates" are TRUE-by-collapse** — eq1 alone has no finite model of size
2–7 (proved through n=7 for 29, through 5–6 for the rest). On them the shipped
completion "saturates" in < 4 s because `COMPLETION_MAX_SIZE = 44` discards
the critical pairs of weight > 44 that carry the collapse (on
`order5_18399_29663` the 4th derived equation at (60, 2000) *is* the
collapse). Escalated caps (shipped, see item 8) close 3/40 kernel-verified;
egg 0/40; LLM 0/353. The FALSE side: 4/60 settled (three order-7 z3 tables,
one order-8 library table — four distinct tables, nothing to name); the
solver's own constraint search at order 7 finds 1/100, so the schedule is not
the lever. So order-5 is a *proof-size* wall on a bucket that is almost
entirely TRUE: the next engine is a completion that keeps big critical pairs
without paying for them (indexing, or a cap on *derived* rules rather than on
pair weight).

## Order-5 before that classification — measured, not moved

353 misses: completion at 45 s closes 25 (20 via bridge); at 180 s, 0/8 more.
133 rows are still productive at 45 s, 195 saturate. The independent
small-model battery refutes **0** (no cheap FALSE gap), and 253 have no
nontrivial small model of eq1 — yet collapse-directed egg/completion closes
0/7 of those at 30–90 s. The library adds 2. Total 27/353. Nothing tried this
session (budget, collapse targeting, three LLM configs, the library) moved it;
the untried angle is z3 unsat proofs on a sample to learn whether the 253 are
TRUE-by-collapse or FALSE with large witnesses.

## Dead ends, so nobody re-runs them

- Leaf-inflation moves in the bridge: 0/7 on eq1 `3051` (its reachable graph
  within the size cap is tiny; it needs derived helper facts).
- Normalizing bridge neighbours to normal form: kills the search outright —
  the bridge exists to go *up* the order.
- Smaller slack for `3983`: the meeting term needs slack ≥ 6 and 316k
  expansions regardless.
- `_kb_resolve` memoization halves the recursion but tuple hashing eats the
  wall-clock gain.
- Adding order 7 to the cheap constraint schedule (the z3 classification found
  order-7 witnesses on order-5 rows): the solver's propagation search finds
  **1/100** of the `no_small_countermodel` order-5 rows at 45 s — z3 is the
  stronger search, not the schedule.
- Escalated completion caps on order-5 collapse candidates: 1/30 on one sample,
  3/11 on the agent's — a real but modest lever; most rows genuinely saturate
  even at (60, 2000).

## Harness: Lean/Mathlib v4.33.1

Upstream moved 4 commits (rail 14): the kernel-soundness toolchain bump, judge
fallbacks now equal to the deployed caps, a `CODE_NOT_UTF8` status,
`llm.reasoning_effort` low + per-model allowlist, Marathon snapshotting the
judge config pre-launch. `config.json` judge limits unchanged. Synced with all
local patches (`UPSTREAM.md`); parity smoke 4/4 accepted. Gotcha: `lake build`
builds nothing with an empty default target — build each `lean_lib` explicitly.

## Verification trail

- Isolated 218 audit: `audit-merged-order4-misses-2026-08-27-isolated.json`
  (the earlier `…-2026-08-26.json` at 60/218 ran under self-inflicted
  contention and predates items 2–5 — do not quote it).
- Judge: `judge-2026-08-26-new-families(-b).jsonl`, `judge-2026-08-27-repin.jsonl`,
  `infinite-countermodels-2026-08-26.jsonl`; fixture 112 → 127 entries.
- Official corpus, spotcheck, packaging, hard-batch Marathon: below.

## Official corpus / spotcheck / packaging / unseen hard batch

- Official (`audit-2026-08-27-official-b.json`) 1869/1869, HF
  (`audit-2026-08-27-hf.json`) 800/800; row-id diff vs the 2026-08-24
  baselines: 0 lost / 0 gained / 0 verdict flips. ~78 rows now route through
  `completion` earlier (bridge in the probe slot) — same verdicts, same
  kernel checks. Slowest row 22 s.
- A first official pass (`…-official.json`, same totals) exposed rail 5f-iv's
  sixth instance: `hard3_0283` spent **1,445 s** inside the probe's 2 s slot
  because the multi-fill bridge enumerated `product(fills, repeat=len(unbound))`
  with no deadline poll between rejected images. Stack-sampled, not inferred.
  Fixed with a poll inside the enumeration, a size lower-bound prune before
  it, and `COMPLETION_BRIDGE_MAX_UNBOUND = 3`; the row now takes 3.8 s and
  `hard3` as a set went 1,470 s → 43 s.
- Spotcheck: 90 rows / 9 sources, 100% accuracy, 100% coverage.
- **Organizer stress test (2026-08-27 drop, mirrors the final leaderboard:
  `order4_normal`/`hard`/`extra_hard`/`order5_normal`, 25 TRUE + 25 FALSE
  each)**: offline **200/200** (22.7 s on 12 workers, 0 verdict mismatches,
  0 oracle failures); real judge on Lean 4.33.1 **200/200 accepted, 0
  rejected** (`judge-stress-test-2026-08-27.jsonl`).
- Packaging: `stage2/submissions/solver.py` 426,613 B, gate 297/2.
- **Real Marathon, 1000-row stratified hard unseen batch**
  (`etp-hardtest-1000-2026-08-26.jsonl`: 4-op ≥3-var hypotheses, FALSE side
  hard-region filtered at 7.3% survival, 0 overlap with any prior draw;
  deployed budgets, LLM lane live, Lean 4.33.1 judge): **999/1000 accepted,
  0 rejected, 1 not attempted** (`etp_1486_3862 False x = (y ◇ x) ◇ (x ◇ (z ◇ z)) => x ◇ x = (x ◇ (x ◇ x)) ◇ x`). Solver wall 5,048 s of 300,000
  (~5 s/row); LLM lane 10,772 tokens, 0 accepts. Report as stratified — not
  comparable to a uniform sweep.

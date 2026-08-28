# 2026-08-27 — improvement pass 2: the final repo session

Eight-pillar diagnosis, then eight parallel implementation branches, merged and
verified the same day. Every solver change below is judge-verified (rail 3c),
row-id diffed (rail 2), and tested with positive *and* negative controls (rail
5c). Numbers carry their load caveat (rail 22): the diagnosis and
implementation agents shared the 32-core box (20–46 concurrent Python
processes), so every wall clock they report is an upper bound; coverage counts
are load-independent. Final verification numbers (isolated audits, packaged
size, real Marathon/Solo) are in §6.

Inputs: `CLAUDE.md` at commit `319d778` (improvement pass 1), the vendored
harness at upstream `817a4653` (docs-only sync: the 300 s Lean timeout is per
Lean *phase*; code cap is UTF-8 bytes), the diagnosis findings (scratchpad
`diag/*.md`, summarised in §2), and the calibration measurement in
`2026-08-27-population-calibration.md`.

## 1. Headline

| Item | Before | After |
| --- | --- | --- |
| Offline gate | 297 passed / 2 skipped | see §6 |
| Order-5 FALSE side, held-out 353 sweep misses covered by the witness portfolio | 2 / 353 | **134 / 353 (38.0%)** — 18 z3-harvested tables, 4.1 KB |
| Fresh disjoint 2,000-row order-5 sample (`--row-budget 60`), row-id diff | 1953 | **1966**, 0 lost, 13 gained, 0 flips |
| Order-4 residual (51 rows the solver missed at 420 s/row) | 0 | **18 via `egg_ladder` with the mined laws** (all 17 residual eq1-`3983` rows + `etp_4453_4652`); 31/51 solved overall at 420 s |
| Order-5 collapse sample (40 z3-proved TRUE-by-collapse rows) | 3 / 40 (escalated caps) | **6 / 40** with unfailing superposition; 0/40 known-FALSE rows claimed; escalation bounded at 25 s absolute |
| LLM lane, real calls on the 37-row hard sample | 0 / 37 (0 / 433 historically) | **3 / 37**, all `llm:true:ladder:goal`, 3/3 judge-accepted — the first judge-accepted TRUE proofs from the lane ever; a 20-row real Marathon added 2 more LLM accepts |
| FALSE certificates | `List.getD` tables up to order 25; order-30 3-var tables passed the gate but are judge-REJECTED (heartbeats) | closed-form arithmetic/bitwise rendering (381–383 B at any order, 7× cheaper), shape-aware decide-cost gate; `order5_18263_27751` (n=43) judge-accepted in 36 s |
| Marathon clock use | 1.7% of the budget, `deep` unreachable | second `deep` pass over unresolved rows + speculative fallback; LLM lane budget-derived (up to ~4N calls, 3 protocol rounds) |
| Solo | 0.55 deterministic share, insurance judge call, 6 decorative LLM rounds | 0.85 share, overtime escalated completion slot (closes `etp_2923_156` in 27.8 s), rejected-cert retry, no insurance call |
| Cheap constraint tier | shared 3 s deadline: orders 6/4/10 never reached; 44.7–49.9% of ALL wall-clock on TRUE rows | per-order 0.8 s slices over (8,9,6,5,4,7,10); the two TRUE probes now run before it (−48.7% wall on uniform order-4, 0 route changes) |
| `local_model_counterexample` | one deadline before the size loop: sizes 5+ dead code for months | per-size slices, sizes (4,5,6,7), escalation +8; a 1.5 s unscaled probe before the TRUE engines |
| Real-judge certificates this session | — | **63 / 63 accepted** across all agents (2+3+21+2+2+5 on branches, 4 parity smoke, 7 re-pins, 2 O5W18, 1+7 re-judged pins; see §4) |

## 2. Diagnosis (what was measured before anything changed)

Eight agents, one per pillar, read-only on the solver; a critic re-ranked the
findings by risk-adjusted gain and the perf agent's findings arrived last.

- **Compliance.** Banned-token mirror byte-exact (36/36); PROMPT extraction and
  payload shapes conformant; both official harnesses green (Marathon 27/27,
  Solo harness 0 failures across every bucket incl. 96 challenger attacks);
  artifact runs under Python 3.11 in a sandbox-like env. Real deviations: a
  stray `stage2/submissions/__pycache__` (created mid-session by an agent
  importing the artifact) makes the organizer's `_validate_submission_layout`
  reject the whole submission; `SUBMISSION_NOTE.md` under-disclosed the
  embedded data; a variable literally named `h` would shadow the hypothesis
  binder (judge-measured: `intro h g` rejected, renamed accepted). Digit or
  uppercase variables are unjudgeable for everyone (the judge's own binder scan
  is `\b([a-z])\b`), so that risk is ~0.
- **Performance.** Per-engine profiler over three samples: the cheap constraint
  tier is 44.7/48.5/49.9% of all wall-clock and wins 212 rows in 510,000;
  `egg_probe` 38–44%; `completion_probe` 0.0–0.3%. Marathon's single pass used
  5,048 s of 300,000 s and `effort_for_seconds(150)` = `standard`, so `deep`
  was unreachable; a controlled 19-row deep pass gained +2/19, 0 lost.
  Promoting `completion_route` above the egg family is a measured LOSS (15/20
  vs 19/20) — recorded as a dead end.
- **Order-5 collapse wall.** Eleven completion strategies converge on the same
  6/40; 60 s buys nothing over 20 s. The one real lever: equations whose sides
  have incomparable variable sets had `ori == []` and were inert for both
  rewriting and superposition; superposing with both orientations (the
  unfailing-completion side condition is already in `crit_pairs`) takes 3/40 →
  6/40. `COMPLETION_MAX_ACTIVE` set the *global* expiry flag and skipped the
  goal bridge (latent at fast, reachable at standard/deep); the passive queue
  silently truncated at its cap; `subsumed()` never polled the deadline.
- **LLM lane.** 322 real calls / 831k tokens / $0.22 across 7 protocols. The
  verdict is set by prompt framing (148/148 TRUE under TRUE-framed prompts incl.
  4 provably FALSE rows; 24/24 FALSE under a FALSE-framed one, 0 valid tables).
  A justified-derivation protocol (A2) whose laws are replayed rung-by-rung
  through `egg_saturate_prove_multi` settles 2/37; neither half alone settles
  any. By-product: 31 model-proposed laws the solver could PROVE close 19/51 of
  the order-4 residual deterministically. Each unresolved row got exactly one
  call per run under a flat 64-call cap (1.3% / 0.03% budget utilisation).
- **Lean.** The 300 s timeout is per phase and the decide is not re-run in
  phase 2 (measured phase-2 1.6–19.7 s, uncorrelated with phase-1 cost). The
  declaration allowlist is non-transitive (helpers under `submission.*` may use
  any tactic; `omega` does not normalise `Nat.add` spelling). The FALSE
  decide-cost axis is `applications × n²` for tables — an order-30 3-var table
  passed both old gates and is judge-REJECTED on heartbeats — while a formula
  rendering costs `applications` only and is accepted to n=60 / 262,144
  applications. The 12.6–95 KB TRUE band had no judge evidence; 4/4 accepted.
- **FALSE side, order 5.** z3 over 47 fresh misses: ≥23% are FALSE with a
  witness at order ≤ 9; greedy set-cover of 13 z3 tables covers 30.7% of 398
  misses, cross-validated 57/351 on a disjoint sample. teorth's remaining 935
  FinitePoly tables are worth 2 rows; 800 random Latin squares satisfy 0 of 280
  hypotheses. `local_model_counterexample` had one deadline before its size loop
  (sizes 5+ never searched); the cheap constraint tier's shared 3 s deadline
  never reached orders 6/4/10 (0/47 vs 3/47 per-order). Two of the six "open"
  order-4 FALSE rows were already closed by `FP6`. Infinite-carrier confluence
  certificates for eq1 481/2531/1661/1486: NO-GO offline (no Lean source in the
  cache).
- **Solo/tests.** The deep deterministic pass is clock-bound (7/8 misses burn
  100% of a 900 s deadline); 0.55 share withheld 1,310 s for a 0/433 lane; the
  insurance reflexive judge call cannot score and pollutes `{history.attempts}`;
  the duplicate-LLM branch set no feedback (temperature 0 + seed 0 ⇒ guaranteed
  repeats). `run_solo`, the memory-guard reset (rail 10) and the banned-token
  mirror had no executing tests; every test read the source, not the artifact.
- **Calibration** (`2026-08-27-population-calibration.md`). The ≥4-variable
  half of order 5, never swept, is **250/250** — order-5 difficulty peaks at
  exactly 3 variables. Reweighting the 510k swept order-4 rows onto the official
  sets' shapes projects 0.01–0.12 misses per 200-row category; Order 5 projects
  ~2.6/200, concentrated in rows with 3 variables and a bare variable on both
  sides (3.17% miss rate there). That is the population the deep sweeps should
  draw next.

## 3. What shipped (branch → merge commit), each with its own verification

| Branch | Shipped | Verification on the branch |
| --- | --- | --- |
| `impl/compliance-tests` | parser accepts the judge grammar and renames reserved binder names (`h`, `G`, …) to `q0..qn`; lone-surrogate guard in `judge_answer_payload`/`sanitize_lean_code`; Solo insurance call deleted; duplicate-LLM feedback; packager runs the organizer's layout validator; CI pins the banned-token set (36) and `DEFAULT_PROOF_POLICY` (59 prefixes); `SUBMISSION_NOTE.md` rewritten against the measured inventory; new tests `test_compliance.py` (15), `test_solo.py` (9), `test_marathon_guard.py` (3), `test_artifact.py` (6) | gate 331/1; `rc02_h_renamed` judge-accepted 4.6 s |
| `impl/false-side` | per-size deadlines + sizes (4,5,6,7) + `LOCAL_MODEL_MAX_INSTANCES`; cheap constraint tier per-order 0.8 s over (8,9,6,5,4,7,10) with the timed-out-order-is-not-exhausted fix; 1.5 s unscaled local-model probe; `O5_WITNESS_TABLES` (17 tables) | 2,000-row order-5 sample 1953→1966, 0 lost; hard2 0 lost/0 flips; oracle 17/17 + 18/18; judge 2/2 |
| `impl/completion` | `sup_ori` unfailing superposition, escalation ladder (60,120,240,480) under an absolute 25 s cap with `norm_push` + variable-merge seeding, passive eviction, `active_full` flag, `subsumed()` deadline poll, `completion:saturated_nontrivial_model` signal | 40-row collapse sample 6/40; 40 negative controls 0 served; hard3 0 lost/0 flips; judge 3/3 (incl. the new `exact (h a a b)` merge-seeded lemma shape) |
| `impl/lean-formula` | `formula_op_expr` recogniser (affine/quadratic/xor-land-lor) + `false_certificate_formula`; three-way `false_certificate`; `maxHeartbeats 1000000` in both table renderers; shape-aware `witness_decide_is_affordable` (`FORMULA_MAX_DECIDE_APPLICATIONS` 150k, `TABLE_MAX_DECIDE_WORK` 8M); `FORMULA_LINEAR_SIZES` (27..47) with the 5f-vii pre-check; `egg:proof_too_large` counter; oracle can now read formula certs; 9 new + 7 updated pins | gate 332/2; hard1 + hard2 0 lost/0 flips; judge **21/21** (n=43 row accepted 36.1 s) |
| `impl/pacing` | Marathon second `deep` pass + `_MARATHON_ROW_EVIDENCE` + speculative `fallback:marathon_grind`; Solo share 0.85, overtime escalated completion slot, rejected-certificate retry (`_REJECTED_WITNESS_TABLES`, `_EXCLUDED_ROUTES`), `solver_analysis(rejected_verdict=)`; `LLM_HTTP_TIMEOUT_SECONDS` 600; `test_pacing.py` (20) | real local Marathon 30 rows: 24/30, `not_attempted` 6→0, 0 rejected real answers; overtime closes `etp_2923_156` in 27.8 s where a 3,060 s deep pass returns None at 610 s; judge 2/2 |
| `impl/mined-laws` | `MINED_LEMMA_LIBRARY_TEXT` (19 laws, library 601→620), 0.5 s per-law budget, gated off order-5 collapse shapes (≥5 ops AND no small nontrivial model) | 51-row residual: 31/51, 18 via `egg_ladder`; order-5 cost median +0.01 s/row; hard3 0 lost/0 flips; judge 2/2 |
| `impl/llm-lane` | PROMPT = A2 shell ending in `{solver.protocol}`; `PROTOCOL_BODIES` (3) + FALSE-first body; `llm_ladder_candidate` (rung replay); `marathon_llm_call_allowance` (8k tokens/call estimate, 32k reserve, cap 4000); multi-round Marathon lane with evidence-based direction/priority; `LLM_MAX_OUTPUT_TOKENS` 32768; Solo rounds send the protocol; `test_llm_lane.py` (17); `llm_lane_e2e.py` | real calls: 3/37 settled (1/37 single-round control); judge 3/3 + 2 inside a real 20-row Marathon (12/20 at a truncated 1,200 s budget, 11.4% token utilisation) |
| `impl/docs` | CLAUDE.md consolidated (history table, rails 23–33), README/CURRENT_STATE/tests README refreshed, `DEEP_SWEEP_RUNBOOK.md`, tracked `run_marathon_batch.py`/`run_solo_batch.py`, `sample_order5_pairs.py --min-variables`, UPSTREAM.md | all documented commands `--help`-verified |
| post-merge (lead) | duplicate `_MARATHON_ROW_EVIDENCE` and `_term_op_count` definitions reconciled; TRUE probes moved before the cheap constraint tier (perf SP-2 variant A); large-linear scan moved before the TRUE engines (SP-3); `O5W18` (3 rows, 178 B) from the completed z3 harvest — the harvest at orders 7/8/9 is now spent (154 candidate tables cover only 14 more open rows, 13 of them single-row) | gate + isolated audits in §6; judge 2/2 (O5W18) + 7/7 (re-pins) + 4/4 parity |

Dead ends measured this session, so nobody re-runs them: `completion_route`
promotion (15/20 vs 19/20); eleven completion selection/cap strategies (same
6/40); more z3 hours at orders 7–9 (spent); teorth FinitePoly remainder (2 rows);
random Latin squares (0/800); a FALSE-table LLM protocol (0/24); `reasoning_effort`
medium (2.8× tokens for the same rows); infinite-carrier confluence certs offline
(NO-GO); `local_model` with `max_flips = 800` at sizes ≥ 6 (misses a witness it
finds at 4,000).

## 4. Real-judge evidence (Lean/Mathlib v4.33.1, deployed caps 100,000 / 20,000 / 300 s)

All through `stage2/experiments/judge_cert_text.py` (raw certificate text from
the branch solver) or `judge_rows.py`, one judge process at a time.

- compliance: `rc02_h_renamed` 1/1.
- false-side: `order5_13928_7727` (O5W5, order 9) and `order5_11497_52058`
  (O5W9) 2/2; re-judged after the heartbeat line 2/2.
- completion: `order5_18399_29663`, `order5_32102_22671`, `order5_28585_58647`
  3/3 (lemma_chain, up to 15 helper lemmas).
- lean-formula: 21/21 — formula z11 / z17 / z25 / z43 / quadratic, the order-9
  fallback `evaluation_order5_0059`, 7 re-judged table pins, the four 45–88 KB
  TRUE certs, the four previously unpinned route families.
- pacing: `etp_2923_156` (overtime join) and `order5_46513_41697` 2/2; the
  30-row Marathon scored 24 accepted / 0 rejected real answers.
- mined-laws: `etp_3983_3800` (54,917 B) and `etp_4453_4652` 2/2.
- llm-lane: `etp_4453_4652`, `etp_3983_3963`, `etp_3983_3997` 3/3, plus
  `etp_3983_3800` and `etp_3983_3997` accepted by the runner's own judge inside
  the 20-row Marathon.
- lead: parity smoke `normal_0001`, `hard2_0027`, `hard2_0051`, `hard2_0092`
  4/4; 7 FALSE re-pins 7/7; O5W18 2/2.

Fixture: 138 → 159 entries, every new row carrying its own equations and ids
(rail 16); no duplicate ids.

## 5. Integration issues found at merge (and why they matter for next time)

- Two branches defined `_term_op_count` with different signatures (Term vs
  equation); the later definition silently replaced the earlier at import and
  broke every `egg_ladder` call. Two branches defined `_MARATHON_ROW_EVIDENCE`.
  Lesson: when parallel agents share one module, grep the merged file for
  duplicate top-level `def`/assignment names before running anything.
- Fixture lines updated *in place* by one branch lost a union-style conflict
  resolution to the untouched copies on other branches; re-judging the seven
  rows fixed it. Lesson: resolve fixture conflicts by re-judging, not by text.
- A test that monkeypatched `solver_analysis` with a positional-only lambda broke
  when another branch added a keyword argument; a pacing test still counted the
  insurance judge call another branch deleted.
- The Agent tool's worktree isolation bases worktrees on `origin/main`, not on
  local HEAD — an unpushed commit is invisible to them. Worktrees were re-made by
  hand from HEAD.

## 6. Final verification (filled after the merged solver was measured)

<<FINAL-NUMBERS: gate, isolated official + HF audits with row-id diffs, spotcheck, packaged size, sandbox-shaped real Marathon, real Solo>>

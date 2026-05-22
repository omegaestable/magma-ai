# 2026-05-21 Prune Refactor And Fallback Reproduction

This note records the May 21 solver cleanup and selected-row reproduction pass. Raw scratch artifacts remain under `tmp_stage2_smoke/`; this file is the durable handoff summary.

## Solver Cleanup

- Refactored the duplicated bidirectional closure search into `_closure_route_impl` in `stage2/solver/solver.py`.
- Rebuilt `absorption_closure_route`, `deep_absorption_closure_route`, and `equational_closure_route` as thin wrappers around the shared helper.
- Preserved route order and timing constants, especially `ABSORPTION_TIME_BUDGET = 0.05`.
- Changed `fallback_true_certificate()` to return `reflexive_true_certificate()` instead of carrying a duplicate Lean body.
- Packaged output: `stage2/submissions/solver.py`, `85173` bytes.

## Validation Evidence

- Python syntax checks passed for source and packaged solver.
- Packaging succeeded; source and packaged hashes matched after repackaging.
- Submission directory contained only `solver.py`.
- Route profile on `normal_100`: `74` deterministic candidates, `26` skips, `49.925s`.
- Official Solo harness on `sample_20`: exit `0`, no failing categories.
- Official zero-token Marathon `normal_100`: `74/100`, `74` accepted, `26` not attempted, `0` tokens, `50.5s`.
- Analyzer agreed on `normal_100`: `score=74`, gaps `{'true_template_gap': 26}`.

## Selected-Row Reproduction

User-provided labels were normalized by removing the true/false label segment, for example `hard1_true_0065` -> `hard1_0065`. Public rows came from `vendor/stage2-official/examples/problems/`; evaluation rows came from `data/hf_cache/`.

Direct runner-equivalent probing used official judge normalization via `_to_judge_problem(problem)`, not raw `verify_answer(problem, ...)`.

Broad 27-row direct probe:

- `evaluation_extra_hard_0045`, `evaluation_extra_hard_0043`, and `evaluation_extra_hard_0041` are now solved as `FALSE ACCEPTED` by `false:witness:S4C` in about 4-6 seconds.
- The other 24 listed rows reproduce the Solo-style fallback shape: submitted `TRUE`, judge `incorrect`, error code `LEAN_REJECTED`.
- Direct local timings for fallback rows were about 1.3-3.2 seconds because the probe bypassed live proxy waiting and checked the final fallback directly.

Official zero-token Marathon on the same 27-row manifest:

- Score: `3/27`.
- Attempted: `3`.
- Not attempted: `24`.
- Status split: `{'accepted': 3, 'not_attempted': 24}`.
- Wall time: `49.1s`.
- Tokens: `0`.
- Accepted routes: `false:witness:S4C` for the three `evaluation_extra_hard_false_*` rows.

Scratch artifacts:

- `tmp_stage2_smoke/2026-05-21-fallback-batch-27.jsonl`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-direct-probe.py`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-direct-probe.jsonl`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-zero/summary.json`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-zero/run.log`

## Handoff Lessons

1. Generalize proof and witness families; do not add solver policy keyed to public or evaluation row ids.
2. Selected-row reproduction is useful for diagnosis, but promotion claims need full lanes or focused route fixtures with judge-accepted certificates.
3. Solo fallback `TRUE INCORRECT` rows and Marathon zero-token `not_attempted` rows are the same unresolved deterministic gap viewed through different runner policies.
4. The three `evaluation_extra_hard_false_*` rows appear fixed in the current package. If they failed elsewhere, that evidence likely came from an older package or a different upload.
5. The remaining listed fallback rows are unresolved TRUE/template gaps or finite-countermodel gaps; fix them by adding reusable certificate/witness families or improving judged LLM output, not by special-casing ids.

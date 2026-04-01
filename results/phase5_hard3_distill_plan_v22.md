# Phase 5.1 Distill Plan for v22 Hard3 Lift

## Objective
- Reach at least 60% hard3 accuracy on unseen 30/30 seeds.
- Preserve 100% normal accuracy gate before any promotion.

## Evidence Baseline
- Current paid campaign:
  - normal seed20260401: 60/60
  - normal seed20260402: 56/60
  - hard3 seed20260401: 31/60
  - hard3 seed20260402: 30/60
- Failure mode: overwhelmingly FALSE misses from default TRUE lane (`SOURCE: N`, `REASONING: NONE`).
- Teorth implication data source confirmed live at https://teorth.github.io/equational_theories/implications/ (last updated Jan 1, 2026, commit 5e46624).

## Distillation Principles
- No denser-E2 heuristic re-enable unless zero normal false positives on unseen normal gates.
- No benchmark pair hardcoding.
- Add only compact, signature-based or witness-backed FALSE lanes.
- Every FALSE output must carry explicit source lane (`S`, `W`, `G`, `O`, etc.).
- Stay below 10KB template size.

## Workstream A: Teorth-Proven False Family Mining (Primary Lift)
Goal: mine compact family rules from Teorth graph/full_entries that are repeated on hard3 FALSE and collision-safe on normal TRUE.

1. Build mined feature table per pair using Teorth IDs:
- eq1_id, eq2_id
- graph status (2/6 explicit or implicit proof false)
- class IDs from equivalence classes
- per-side shape features: stars, depth, length, variable multiset/parity, leaf boundary

2. Mine candidate family signatures (not exact pair ids):
- class-pair families `(class(eq1), class(eq2))`
- mixed shape signatures `(e1_side_stars, e2_side_stars, e1_depth, e2_depth, len deltas)`
- parity/leaf pattern signatures

3. Safety filter:
- Drop any candidate with normal TRUE collisions on full normal cache.
- Keep only candidates with repeated hard3 FALSE support (>=3) and zero normal TRUE collisions.

4. Output artifacts:
- `results/phase5_teorth_signature_candidates.json`
- `results/phase5_teorth_signature_candidates.md` with support/collision stats and provenance notes.

Expected contribution: +4 to +8 hard3 correct if safe signatures are found.

## Workstream B: Witness Gap Recovery (Low Risk Lift)
Goal: recover FALSE pairs already separable by deterministic finite witnesses but currently escaping.

1. Recompute separability on current hard3 failures against expanded witness library.
2. Separate failures into:
- witness-separable but template-missed
- not witness-separable (needs oracle family)

3. Strengthen deterministic witness lane only where mathematically checked:
- enforce witness-first routing for candidate hard signatures
- ensure emitted `SOURCE: W` and witness label

Expected contribution: +2 to +4 hard3 correct with near-zero normal risk.

## Workstream C: Compact Oracle Patch Trial (Only if A+B yield safe rules)
Goal: add minimal hard oracle expansion to `hard_oracle` dict in the template.

Patch constraints:
- max 10-20 signatures per patch wave
- each signature must pass zero-collision normal TRUE screen
- signatures must be family-level features, not benchmark pair IDs

Patch verification sequence:
1. hard3 seeds 20260401 and 20260402
2. normal seeds 20260401 and 20260402
3. if any normal FP increase, revert patch

Expected contribution: +1 to +3 hard3 correct without normal regression.

## Evaluation Gate Protocol
For each patch wave:
1. Run paid normal gates first (must be 100% to proceed).
2. Run paid hard3 gates.
3. Rebuild fail ledger and Teorth certificates.
4. Decide keep/revert.

Commands:
- `sim_lab.py` on unseen normal/hard3 seed files with `cheatsheets/v22_witness.txt`
- `analyze_seed_failures.py` for full ledger
- `teorth_true_proof_agent.py certify-benchmark` for source metadata

## Stop/Go Criteria
- GO: hard3 >= 60% and normal = 100% across required unseen seeds.
- HOLD: hard3 improves but normal drops below 100%; keep mining, do not promote.
- REVERT: any patch adds normal false positives with no hard3 lift.

## Immediate Next Iteration (Execution Order)
1. Implement mining script for Teorth signature families and collision screening.
2. Produce candidate table and select top safe signatures.
3. Patch template with smallest safe oracle update.
4. Re-run full paid gates and regenerate ledger.
5. Promote only if stop/go criteria pass.

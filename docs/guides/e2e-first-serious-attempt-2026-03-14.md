# First Serious Naive E2E Attempt (2026-03-14)

## Scope

Goal: run the repository naively, workflow-by-workflow, from the documented path; log what breaks, what is nonsense, and what is genuinely useful for Stage 1 submission readiness.

## Workflow Pass Log

| Step | Command Family | Outcome | Critical Notes |
|---|---|---|---|
| 1 | `evaluate.py --mode heuristic` on local/no-leak | PASS | Heuristic looked strong (0.80 local, 0.875 no-leak) but this is research-only and not submission-valid. |
| 2 | `run_eval.py --dry-run` | PASS | Pipeline setup checks are clean and useful. |
| 3 | `run_eval.py` live on baseline cheatsheet | PASS with poor quality | Submission-valid but weak: local 0.51, no-leak 0.70, hardest20 0.45. Hard bucket collapsed. |
| 4 | `download_data.py` local/no-leak/hardest500 | PASS | Hardest500 generation now exists; no errors. |
| 5 | `evaluate.py` on hardest500 | PASS but suspicious | Heuristic scored 1.00 on hardest500 (likely not representing LLM-facing hardness). |
| 6 | `train.py --dataset default` | FAIL (first attempt) | Hard failure: missing `features/default.pkl`; naive onboarding breaks here. |
| 7 | `features.py` + rerun `train.py` | PASS | CV OOF 0.9861; model training healthy after manual bootstrap. |
| 8 | `workstream_analysis.py` proof/counterexample modes | PASS | Useful mining artifacts generated quickly. |
| 9 | `distill.py` candidate generation | PASS with warning | Completed; one transient connection retry occurred; candidate produced. |
| 10 | `run_eval.py` on distilled candidate | PASS with regression | no-leak fell to 0.50; hardest20 stayed 0.45; TRUE recall collapsed further. |

## Raw Results (Key Numbers)

### Baseline cheatsheet (`cheatsheet.txt`, 2568 bytes)

- Local sample (n=100): accuracy 0.51
- No-leak benchmark (n=40): accuracy 0.70
- Hardest20 (n=20): accuracy 0.45
- Pattern: high FALSE accuracy, weak TRUE accuracy, especially in hard bucket.

### Distilled candidate (`cheatsheets/cheatsheet_e2e_candidate_default.txt`, 3229 bytes)

- No-leak sample (n=100): accuracy 0.50
- Hardest20 (n=20): accuracy 0.45
- Severe issue: on no-leak sample, TRUE accuracy reached 0.00 while FALSE stayed very high.

### ML/Research branch

- XGBoost CV OOF: accuracy 0.9861, log-loss 0.0443
- Dominant features are solver-like (`counterexample_size`, `has_counterexample`, `rewriting_proved`), which is useful for research but risky to over-interpret for cheatsheet-only behavior.

## Challenges and Nonsense Logged

1. A documented naive path can hard-fail:
   - `train.py --dataset default` assumes a precomputed feature cache that may not exist.
2. Hardest500 appears misaligned with the user-facing goal:
   - Heuristic hitting 1.00 while LLM cheatsheet runs fail on hard slices is a red flag for benchmark construct validity.
3. Distillation can optimize style while regressing behavior:
   - Candidate grew in bytes but became more FALSE-biased on sampled no-leak eval.
4. True/false asymmetry is currently under-governed:
   - Accuracy alone hides collapse in TRUE recall.

## Critical Reflection by Workstream

- A (alignment): strong, no major new compliance issues found.
- B (benchmark hygiene): improved by generating hardest500, but adversarial validity still questionable.
- C (math extraction): method coverage is broad, but exact singleton class representation is still missing in cheatsheet path.
- D (cheatsheet optimization): still the bottleneck; byte budget underused and hard TRUE handling weak.
- E (ML support): useful for mining; not directly translating to robust prompt behavior yet.
- F (adversarial eval): now practical, and it reveals major failures that aggregate metrics hide.

## What Changed From This E2E

1. Roadmap updated with this attempt and reprioritized blockers.
2. Cheatsheet updated with anti-collapse guidance and stronger singleton candidate cues.
3. Enhancement prompt prepared for the next E2E cycle.

## Recommendation Before Next E2E

Do not run another broad E2E until four blockers are addressed:

1. Add exact singleton-membership representation to cheatsheet path.
2. Add hard TRUE guardrails (avoid reflex FALSE when rewrite/specialization cues exist).
3. Fix `train.py` bootstrap behavior for missing feature datasets.
4. Rebuild hardest benchmark objective to align with cheatsheet-only LLM failure modes.

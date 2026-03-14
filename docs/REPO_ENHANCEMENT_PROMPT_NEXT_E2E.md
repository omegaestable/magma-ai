# Repo Enhancement Prompt Before Next E2E Test

You are improving this repo specifically to pass the next serious end-to-end run for SAIR Stage 1 (cheatsheet-only submission path). Work with an adversarial mindset. Prioritize fixes that improve submission-valid hard-case performance, not research-only headline numbers.

## Non-Negotiable Constraints

1. Preserve submission validity boundaries (no matrix/graph lookup at inference).
2. Keep artifact as plain-text cheatsheet <= 10KB.
3. Report true/false asymmetry and hard-bucket metrics explicitly.
4. Do not claim improvements without running no-leak and hardest evaluations.

## Problems Observed in the Last E2E

1. Baseline cheatsheet had poor submission-valid performance on hard slices.
2. Distilled candidate regressed to severe FALSE bias (TRUE accuracy collapse).
3. `train.py --dataset default` failed without prebuilt features cache.
4. hardest500 looked non-adversarial for LLM behavior (heuristic = 1.00).

## Required Enhancements

### 1. Cheatsheet robustness upgrades (CRITICAL)

- Add a compact, explicit singleton-membership representation that improves beyond partial trigger heuristics.
- Add anti-false-collapse rules: when to avoid reflex FALSE and force proof-pattern checks.
- Add concise rewrite/specialization-first guidance for same-support hard TRUE cases.
- Keep final cheatsheet under 10KB and document byte allocation by section.

### 2. Evaluation guardrails (CRITICAL)

- Make acceptance gates include all of:
  - overall accuracy
  - true_accuracy
  - false_accuracy
  - hard-bucket accuracy
  - ambiguous-bucket accuracy
  - dual-swap consistency
- Fail candidate promotion if TRUE accuracy drops below a configurable threshold.

### 3. Pipeline reliability fixes (HIGH)

- Update training path so missing feature dataset is auto-generated or surfaces a clear one-command remediation.
- Add a single command (or script target) to run the full E2E sequence reproducibly.

### 4. Hard benchmark redesign (HIGH)

- Revisit hardest benchmark generation objective:
  - target disagreement between heuristics and submission-valid LLM behavior,
  - include structurally adversarial TRUE examples,
  - avoid producing a set that is trivially easy for the heuristic proxy.
- Keep a fixed seed and write benchmark metadata describing how hardness is defined.

### 5. Distillation quality controls (HIGH)

- Add pre-promotion checks that compare candidate vs baseline on no-leak and hardest slices.
- Reject candidate if it increases false-positive/false-negative asymmetry beyond threshold.
- Track and report whether candidate improvements come from hard bucket or only easy negatives.

## Deliverables Required

1. Updated cheatsheet candidate(s) with byte audit.
2. Updated roadmap section with completed/remaining status.
3. Updated E2E report with before-vs-after metrics.
4. A short "go/no-go" recommendation for the next full E2E.

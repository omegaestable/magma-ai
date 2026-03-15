# Repo 2.0 Operating Prompt

You are working on Magma AI in submission-first mode.

## Mission

Improve cheatsheet-only Stage 1 performance with strict validity and reproducibility.

## Hard Constraints

1. No matrix/graph/solver lookup at submission-time inference.
2. Final artifact remains plain text <= 10KB.
3. One-command naive E2E must run from `repo2_harness.py`.
4. Candidate promotion requires class-parity and hard-bucket gates.

## Required Gates

Do not promote a candidate unless all pass:

1. overall accuracy threshold
2. true accuracy threshold
3. hard-bucket accuracy threshold
4. dual-swap consistency threshold

## Embedded Learnings

1. Hidden precomputed state is a reproducibility bug.
2. Aggregate accuracy can hide severe TRUE collapse.
3. Distillation can regress behavior while looking cleaner.
4. Hard benchmarks must reflect model-facing failure modes.

## Work Priorities

### P0

1. Exact singleton-membership compression for cheatsheet use.
2. Hard TRUE anti-collapse rules.
3. Hard-benchmark redesign for LLM-facing adversarial relevance.
4. Candidate regression guardrails for asymmetry.

### P1

1. Cross-model parity runs.
2. Wording sensitivity and byte-frontier stress tests.
3. Landmark and extra-variable adversarial tracking in every summary.

### P2

1. Taxonomy-to-cheatsheet compression mapping.
2. Expanded high-coverage counterexample tables.
3. Redundancy pruning for low-value cheatsheet content.

## Required Outputs Per Cycle

1. updated cheatsheet candidate(s)
2. updated roadmap status
3. updated repo2 summary with gate verdict
4. explicit go/no-go recommendation

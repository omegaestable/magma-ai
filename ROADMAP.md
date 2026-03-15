# Roadmap 2.0: Submission-First System

This roadmap replaces the previous backlog with an execution-focused plan built from the 2026-03-14 serious E2E findings.

## Mission

Build the strongest Stage 1 cheatsheet-only submission path with:
1. strict submission validity,
2. reliable one-command reproducibility,
3. robust hard-case performance.

## What Changed in 2.0

1. Training now auto-bootstraps missing feature datasets.
2. One-command harness added in `repo2_harness.py`.
3. Acceptance gating now includes class parity and hard-bucket quality, not only aggregate accuracy.
4. Legacy exploratory flow is superseded by a deterministic run path.

## Hard Lessons Embedded

1. A pipeline that requires hidden precomputed state is not reproducible.
2. Aggregate accuracy can hide TRUE-collapse and hard-bucket failure.
3. Distillation can regress behavior while appearing cleaner.
4. Hard benchmarks must align with model-facing failure modes, not solver comfort.

## Repo 2.0 Architecture

### Submission path (valid)

- Artifact: `cheatsheet.txt`
- Evaluator: `run_eval.py`
- Benchmark slices: `data/no_leak_benchmark.jsonl`, `data/hardest_500.jsonl`

### Research support path (invalid for submission-time inference)

- Feature mining and training: `features.py`, `train.py`
- Proof/counterexample mining: `workstream_analysis.py`, `solver.py`, `magma_search.py`, `proof_search.py`

### Orchestration path

- End-to-end runner: `repo2_harness.py`
- Single command target for naive reproducibility.

## Acceptance Gates (Required)

A candidate is not promoted unless all pass:

1. `overall_accuracy >= 0.60`
2. `true_accuracy >= 0.45`
3. `hard_bucket_accuracy >= 0.35`
4. `dual_swap_consistency >= 0.90`

These defaults are configured in `repo2_harness.py` and can be tightened.

## Priority Queue

### P0: Immediate (this cycle)

1. Add exact singleton-membership compressed representation in cheatsheet flow.
2. Add hard TRUE guardrails and rewrite-first escalation in cheatsheet.
3. Add hardest benchmark redesign objective to target LLM-facing difficulty.
4. Add candidate promotion checks for asymmetry regressions.

### P1: Next

1. Cross-model parity runs (Qwen 3B, Qwen 7B, Gemma 2B).
2. Wording sensitivity and byte-frontier stress tests (5KB, 8KB, 9.5KB, 10KB).
3. Extra-variable adversarial slice and per-landmark tracking in every E2E summary.

### P2: Structural enrichment

1. Equation taxonomy completion and cheatsheet compression mapping.
2. Top-coverage magma curation expansion.
3. Redundancy pruning of low-marginal-value cheatsheet rules.

## Repo 2.0 Definition of Done

1. `repo2_harness.py` runs without manual prep on a fresh clone with dependencies installed.
2. Training no longer fails when feature cache is absent.
3. Baseline and candidate reports include full parity metrics and gate verdicts.
4. Documentation matches actual executable path.
5. Historical failed artifacts are cleaned from tracked repo state.

## Commands

### One-command naive E2E

```bash
python repo2_harness.py --name repo2_run --eval-model ollama-qwen2.5-3b
```

### One-command with distillation candidate

```bash
python repo2_harness.py --name repo2_run --eval-model ollama-qwen2.5-3b --run-distill
```

### Strict gating example

```bash
python repo2_harness.py --name repo2_strict --min-overall-acc 0.65 --min-true-acc 0.50 --min-hard-acc 0.40 --min-dual-consistency 0.95
```

# Magma AI (Repo 2.0)

Submission-first repository for SAIR Stage 1 equational implication over magmas.

## Primary Goal

Produce the best possible plain-text cheatsheet (`cheatsheet.txt`, <= 10KB) for TRUE/FALSE implication decisions.

## Repo 2.0 Principles

1. Mathematical structure first.
2. Submission-valid behavior separated from research tooling.
3. One-command reproducibility for naive E2E execution.
4. Hard-case and class-parity metrics treated as first-class gates.

## Quick Start

### 1. Environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. One-command naive E2E

```bash
python repo2_harness.py --name repo2_run --eval-model ollama-qwen2.5-3b
```

This does all of the following in order:

1. Generates local/no-leak/hardest benchmark slices.
2. Trains research model with automatic dataset bootstrapping if features are missing.
3. Evaluates baseline cheatsheet on no-leak with dual-swap checks.
4. Emits a consolidated summary in `results/repo2_summary_<name>.json`.

Optional distillation ablation pass:

```bash
python repo2_harness.py --name repo2_run --eval-model ollama-qwen2.5-3b --run-distill
```

## Immediate Fix Included

`train.py` now auto-bootstraps feature datasets when `--dataset` is missing. Example:

```bash
python train.py --dataset default --model-type xgboost --cv 5 --hardest-k 500 --name xgb_default
```

If `features/default.pkl` is absent, it is generated automatically from matrix sampling.

## Submission Boundary

Submission-valid inference:

1. Prompting only with cheatsheet text.
2. No matrix/graph/solver/model lookup at inference time.

Research-only tooling:

1. `solver.py`, `proof_search.py`, `magma_search.py`
2. `features.py`, `train.py`, `workstream_analysis.py`

## Core Files

1. `cheatsheet.txt`: current live submission artifact candidate.
2. `cheatsheets/cheatsheet_2026-03-14_full_budget_v2.txt`: archived promoted full-budget baseline.
3. `repo2_harness.py`: one-command orchestrator.
4. `run_eval.py`: submission-valid LLM benchmark harness.
5. `train.py`: research model training with auto-bootstrap.
6. `ROADMAP.md`: Repo 2.0 prioritized plan.
7. `docs/guides/tutorial.md`: operational walkthrough.
8. `docs/guides/cheatsheet-revamp-2026-03-14.md`: rigorous rating of the old cheatsheets and rationale for the new baseline.

## Acceptance Gates

Configured in `repo2_harness.py` (override via CLI):

1. overall accuracy >= 0.60
2. true accuracy >= 0.45
3. hard-bucket accuracy >= 0.35
4. dual-swap consistency >= 0.90

## Notes

1. Local model aliases are configured in `config.py`.
2. Default local endpoint is `http://localhost:11434/v1`.
3. Set `OLLAMA_BASE_URL` to target a non-default endpoint.

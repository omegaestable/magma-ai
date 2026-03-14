# Repository Architecture

This repository is organized around a strict separation between the public Stage 1 artifact and the broader research stack that helps construct it.

## Design Principle

The cheatsheet is the artifact. Everything else exists to generate, stress-test, or interpret that artifact.

That separation matters because the dense implication matrix and solver stack contain answer-like information that is useful offline but invalid if treated as hidden inference-time assistance.

## Top-Level Structure

| Path | Role |
|---|---|
| `cheatsheet.txt` | Current submission candidate |
| `equations.txt` | Canonical equation list |
| `config.py` | Shared repo paths and experiment configuration |
| `data/` | Local benchmarks and research exports |
| `docs/` | Paper assets, memos, architecture, and guides |
| `evaluate.py` | Local heuristic benchmark or prompt export |
| `run_eval.py` | LLM evaluation for cheatsheet-only inference |
| `distill.py` | Offline cheatsheet distillation |
| `solver.py` | Research-only decision engine |

## Submission-Support Components

These scripts support Stage 1 without redefining the artifact boundary.

| File | Responsibility |
|---|---|
| `config.py` | Shared configuration and paths used by both submission-support and research workflows |
| `analyze_equations.py` | Shared parsing and structural utilities |
| `llm_client.py` | LLM transport for distillation and cheatsheet-only evaluation |
| `run_eval.py` | Evaluate a cheatsheet using an LLM and record benchmark-validity metadata |
| `distill.py` | Build or compress candidate cheatsheets from labeled examples |
| `benchmark_utils.py` | Shared bucket labeling, matrix sampling, metric metadata, and validity annotations |
| `download_data.py` | Generate a local JSONL benchmark or attempt remote dataset download |
| `evaluate.py` | Local prompt export for cheatsheet workflows and heuristic research benchmarking |

`evaluate.py` is intentionally mixed-use: `prompt` mode is support tooling, while `heuristic` mode is a research proxy and not a submission-valid evaluator.

## Research-Only Components

These are valuable for mathematical discovery and benchmarking, but they are not valid submission-time inference tools.

| File | Responsibility |
|---|---|
| `solver.py` | Combine trivial rules, graph access, proof search, and counterexample search |
| `proof_search.py` | Proof-oriented implication search |
| `magma_search.py` | Counterexample search over small magmas |
| `features.py` | Feature extraction for ML experiments |
| `train.py` | ML training pipeline |
| `run_experiments.py` | Ablation runner and experiment orchestration |
| `research.py` | Notebook-style exploratory analysis |

## Data Layout

| Path | Contents |
|---|---|
| `data/local_benchmark.jsonl` | Balanced local benchmark for smoke tests |
| `data/exports/export_raw_implications_14_3_2026.csv` | Dense implication matrix |
| `data/exports/export_explorer_14_3_2026.csv` | Explorer summary export |

The exports directory is intentionally separated from the lightweight JSONL benchmark so reviewers can distinguish research assets from evaluation inputs.

## Documentation Layout

| Path | Purpose |
|---|---|
| `docs/guides/tutorial.md` | Operational walkthrough |
| `docs/guides/math-background.md` | Mathematical background from the paper |
| `docs/competition_alignment_memo.md` | Rule-alignment audit |
| `docs/benchmark_integrity_memo.md` | Evaluation-rigor notes |
| `docs/paper/` | PDFs and LaTeX source for the project paper |

## Data Flow

### Submission-Support Flow

1. Start from `equations.txt` and labeled training/eval data.
2. Use `distill.py` to produce a candidate cheatsheet.
3. Use `run_eval.py` to evaluate the cheatsheet on JSONL benchmark data.
4. Store results under `results/` with benchmark-validity metadata.

### Research Flow

1. Use `data/exports/export_raw_implications_14_3_2026.csv` as a dense source of implication labels.
2. Use `solver.py`, `proof_search.py`, `magma_search.py`, and `features.py` to discover patterns, counterexamples, and heuristic signals.
3. Distill only the robust mathematical content back into `cheatsheet.txt`.

## Guardrails

- The matrix is allowed for offline analysis, local benchmark generation, and research experiments.
- The matrix is not allowed as an inference-time lookup oracle for a submission-valid path.
- Format examples in `run_eval.py` should come from a separate labeled source, not from the evaluation file itself.
- Accuracy is the primary Stage 1 metric in this repo; log-loss is tracked only as a local calibration diagnostic.
- Accuracy reports should be read alongside bucket breakdowns and trivial/nontrivial counts.
# Competition Alignment Memo

Source basis for this memo:

- [MASTER_SUBMISSION_AGENT_PROMPT.md](MASTER_SUBMISSION_AGENT_PROMPT.md)
- Repository code and data available locally on 2026-03-14

External organizer rules page is not archived in this repo, so any claim not present in the prompt above is marked unverified.

## Workstream A Status

This memo closes Workstream A as follows:

- A1: the final artifact is documented as a single plain-text cheatsheet under 10 KB, and nothing else counts as the submission artifact.
- A2: every top-level code path is labeled below as submission-support, shared support, or research-only.
- A3: the repo now treats accuracy as the primary Stage 1 metric and log-loss as a secondary local diagnostic only.
- A4: prompt export is explicitly separated from matrix sampling; matrix-backed sampling remains allowed for offline benchmarking but not for any submission-valid inference path.

## Claims Audit

| Repo claim | Status | Notes |
|---|---|---|
| Final artifact is a plain-text cheatsheet under 10 KB | Verified | Explicit in [MASTER_SUBMISSION_AGENT_PROMPT.md](MASTER_SUBMISSION_AGENT_PROMPT.md). |
| Stage 1 should be optimized for binary TRUE/FALSE correctness | Verified | Explicit in [MASTER_SUBMISSION_AGENT_PROMPT.md](MASTER_SUBMISSION_AGENT_PROMPT.md). |
| Solver, graph, proof search, and ML may be used offline | Verified | Explicit in [MASTER_SUBMISSION_AGENT_PROMPT.md](MASTER_SUBMISSION_AGENT_PROMPT.md). |
| Matrix-backed solver behavior is the Stage 1 submission path | Rejected | Conflicts with the prompt’s submission-artifact boundary. |
| README accuracy numbers 99.8% and 100.0% are established | Unsupported | No reproducible artifact in the repo currently backs these figures. |
| README statement that Stage 1 scoring is on a balanced 50/50 set | Unverified | Present in old README, not backed by an archived primary rules source in the repo. |
| README deadline and budget statements are authoritative | Unverified | Not backed by an archived primary rules source in the repo. |

## Invalid Assumptions Removed Or Flagged

1. Treating `solver.py` plus matrix or graph lookup as if it were the submission artifact.
2. Using evaluation-set labeled examples as prompt-format demonstrations in `run_eval.py`.
3. Presenting single global accuracy without trivial/nontrivial split or bucket breakdown.
4. Stating unsupported base-rate and accuracy numbers in top-level docs or cheatsheet text.

## Clean Statement Of The Submitted Artifact

The intended Stage 1 artifact for this repo is a single plain-text cheatsheet, represented by [cheatsheet.txt](../cheatsheet.txt). Any solver, matrix lookup, proof search, counterexample search, or ML system is offline support only and must not be treated as hidden inference-time behavior.

## Metric Alignment

The repo should be read with one scoring rule hierarchy:

- Primary metric: accuracy on binary TRUE/FALSE decisions.
- Secondary local diagnostics: log-loss, bucket accuracy, and trivial versus nontrivial splits.

Implications for repo behavior:

- [run_eval.py](../run_eval.py) is the submission-support evaluator because it measures cheatsheet-only prompting and reports benchmark-validity metadata.
- [evaluate.py](../evaluate.py) is a local support script. In heuristic mode it is explicitly research-only. In prompt mode it is only a prompt exporter and now requires JSONL input instead of silently sampling from the dense matrix.
- Any number reported from solver-, graph-, or matrix-backed inference is not a submission score.

## Code Path Audit

The table below labels the repository's top-level Python modules by competition relevance.

| Path | Classification | Reason |
|---|---|---|
| [cheatsheet.txt](../cheatsheet.txt) | Submission artifact | This is the only intended Stage 1 artifact. |
| [config.py](../config.py) | Shared support | Holds shared paths and config for both submission-support and research tools. |
| [analyze_equations.py](../analyze_equations.py) | Shared support | Structural parsing utilities used across both evaluation support and research code. |
| [benchmark_utils.py](../benchmark_utils.py) | Shared support | Shared benchmark loading, labeling, bucketing, and validity metadata. |
| [llm_client.py](../llm_client.py) | Submission-support | Provides the local Ollama transport used by cheatsheet distillation and cheatsheet-only evaluation. |
| [run_eval.py](../run_eval.py) | Submission-support | Cheatsheet-only LLM evaluation with explicit validity metadata. |
| [evaluate.py](../evaluate.py) | Mixed: submission-support plus research mode | Prompt export supports cheatsheet workflows; heuristic mode is a research proxy only. |
| [distill.py](../distill.py) | Submission-support | Offline authoring tool for producing the cheatsheet artifact. |
| [download_data.py](../download_data.py) | Submission-support | Generates local offline benchmarks from the dense matrix. |
| [solver.py](../solver.py) | Research-only | Uses proof search, counterexample search, and optional graph access. |
| [proof_search.py](../proof_search.py) | Research-only | Proof search and graph-assisted reasoning are invalid as hidden submission-time inference. |
| [magma_search.py](../magma_search.py) | Research-only | Counterexample construction is offline research support. |
| [features.py](../features.py) | Research-only | Builds ML features, including matrix-backed datasets. |
| [train.py](../train.py) | Research-only | Trains predictive models, not the submission artifact. |
| [run_experiments.py](../run_experiments.py) | Research-only | Orchestrates ablations over distillation and evaluation pipelines. |
| [research.py](../research.py) | Research-only | Notebook-style exploratory analysis. |

## Leakage Boundary

The repository boundary is now stated operationally:

- Allowed offline: generate JSONL benchmarks from the dense matrix, analyze the matrix, train models, mine proof patterns, and stress-test cheatsheets.
- Allowed submission-support: evaluate a cheatsheet with [run_eval.py](../run_eval.py) using JSONL labels that stay outside the model prompt, with optional format examples only from a separate labeled file.
- Not allowed for a submission-valid path: querying the dense matrix, implication graph, solver, proof search, or counterexample engine while deciding a benchmark problem.

The remaining ambiguity is benchmark provenance, not inference leakage: a JSONL file may still have been generated offline from the dense matrix, but the submission-valid question is whether the inference path itself has answer-like access. This repo now records that distinction in benchmark metadata.
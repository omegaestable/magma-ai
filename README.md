# Magma AI

This repository is now organized around a strict Stage 1 submission boundary.

- The intended final artifact is a plain-text cheatsheet under 10 KB.
- Solver, proof search, counterexample search, and ML remain offline research tools.
- Every benchmark path should say whether it is submission-valid or research-only.

## Current Ground Truth

The strongest repository-local source of truth is [MASTER_SUBMISSION_AGENT_PROMPT.md](MASTER_SUBMISSION_AGENT_PROMPT.md). External organizer rules are not archived in this repo yet, so any rule claim not present in that file should be treated as unverified until a primary source is added.

Verified local facts:

- `equations.txt` contains 4694 equations.
- `export_raw_implications_14_3_2026.csv` is a dense 4694 x 4694 implication matrix.
- The dense matrix contains 8,178,279 positive entries and 13,855,357 negative entries, so the positive rate is about 37.12% over ordered pairs.
- Matrix-backed graph lookup is useful for research, but it is not the submission artifact.

## Paths

Submission-support path:

- `cheatsheet.txt`: current champion submission candidate.
- `distill.py`: offline cheatsheet authoring and compression support.
- `run_eval.py`: LLM cheatsheet evaluation with bucketed reporting and explicit validity metadata.
- `evaluate.py`: local heuristic benchmark or prompt export with explicit validity metadata.
- `benchmark_utils.py`: shared bucket logic and benchmark metadata helpers.

Research-only path:

- `solver.py`: proof/counterexample/graph decision engine.
- `proof_search.py`, `magma_search.py`: offline theorem and counterexample tooling.
- `features.py`, `train.py`: ML feature extraction and classifier training.
- `run_experiments.py`: ablation orchestrator.

## What Changed

- Removed the default leakage path in `run_eval.py` where format examples were drawn from the evaluation set itself.
- Changed prompt evaluation defaults to zero format examples unless a separate labeled file is provided.
- Added per-bucket reporting, trivial/nontrivial counts, byte counts, and benchmark-validity metadata.
- Rewrote the top-level docs and cheatsheet to avoid unsupported accuracy and base-rate claims.

## Quick Start

Prompt-only local benchmark from explicit JSONL data:

```bash
python run_eval.py --cheatsheet cheatsheet.txt --data path/to/eval.jsonl --format-data path/to/train.jsonl --name local_eval
```

Supported no-network local benchmark path:

```bash
python download_data.py --generate-local --n 200 --seed 42
python evaluate.py --mode heuristic --data data/local_benchmark.jsonl
```

Attempting to fetch official JSONL files from the old Hugging Face slug:

```bash
set HF_TOKEN=hf_your_read_token_here
python download_data.py
```

As of 2026-03-14, the hardcoded Hugging Face dataset slug in this repo appears stale and returns 404. Treat this path as best-effort only until the organizer provides a current official dataset location.

Research-only heuristic benchmark from the dense matrix:

```bash
python evaluate.py --mode heuristic --matrix export_raw_implications_14_3_2026.csv --n 100
```

Prompt export for manual testing:

```bash
python evaluate.py --mode prompt --matrix export_raw_implications_14_3_2026.csv --n 10
```

## Notes

- Hugging Face is not required for repo-local benchmarking; the supported fallback is `data/local_benchmark.jsonl`, generated from the checked-in implication matrix.
- `download_data.py` still supports `HF_TOKEN`, `HUGGINGFACE_HUB_TOKEN`, or `--token` in case a current official dataset URL is restored later.
- A benchmark is only submission-valid when the inference path uses the cheatsheet alone, with no matrix or graph lookup and no evaluation-label examples embedded into the prompt.
- The memos in `docs/` record the current audit, benchmark risks, mathematical notes, and open uncertainties.

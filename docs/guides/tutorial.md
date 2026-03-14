# Tutorial

This tutorial walks through the repository from a cold start to a reproducible local evaluation run.

## 1. Understand The Objective

The Stage 1 task is to answer questions of the form:

> Does Equation 1 imply Equation 2 over all magmas?

The intended artifact is a plain-text cheatsheet under 10 KB. The repo includes more tooling than that because the cheatsheet is built from mathematical and empirical work, but the extra tooling is support code, not the artifact itself.

If you are new to the mathematics, read [math-background.md](math-background.md) first.

## 2. Set Up The Environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional environment variables for live LLM evaluation:

```powershell
$env:OPENAI_API_KEY="sk-..."
$env:ANTHROPIC_API_KEY="..."
```

## 3. Inspect The Main Assets

- `equations.txt` is the canonical numbered law list.
- `cheatsheet.txt` is the current submission candidate.
- `data/local_benchmark.jsonl` is the smallest useful offline benchmark.
- `data/no_leak_benchmark.jsonl` is the held-out-equation benchmark for leakage-sensitive checks.
- `data/hardest_500.jsonl` is the structurally misleading hardest-case slice.
- `data/exports/export_raw_implications_14_3_2026.csv` is the dense research matrix.

## 4. Run The Offline Heuristic Benchmark

This requires no API keys and gives a fast smoke test that the local tooling works.

```bash
python evaluate.py --mode heuristic --data data/local_benchmark.jsonl
```

What this does:

- loads `equations.txt`;
- loads `cheatsheet.txt` so the byte budget is checked;
- loads labeled JSONL pairs from `data/local_benchmark.jsonl`;
- scores them with the built-in heuristic pipeline;
- reports accuracy, log-loss, bucket counts, bucket shares, and trivial/nontrivial breakdown.

This is a research benchmark, not a competition-faithful LLM evaluation.

## 5. Generate A Fresh Local Benchmark

If you want a newly sampled benchmark from the dense matrix:

```bash
python download_data.py --generate-local --n 200 --seed 42
```

That command creates or refreshes `data/local_benchmark.jsonl` using balanced sampling from the dense matrix.

For the Workstream B no-leak benchmark:

```bash
python download_data.py --generate-no-leak --n 200 --holdout-count 100 --seed 42
```

That command creates `data/no_leak_benchmark.jsonl` and `data/no_leak_holdout.json`.

For the Workstream B hardest-case slice:

```bash
python download_data.py --generate-hardest --hardest-n 500 --seed 42
```

That command creates `data/hardest_500.jsonl`.

## 6. Validate The LLM Evaluation Pipeline Safely

Before making live model calls, run a dry-run check:

```bash
python run_eval.py --data data/local_benchmark.jsonl --dry-run
```

This verifies:

- cheatsheet byte size;
- evaluation data loading;
- environment readiness;
- prompt construction.

## 7. Run A Live Cheatsheet Evaluation

```bash
python run_eval.py --cheatsheet cheatsheet.txt --data data/local_benchmark.jsonl --eval-model gpt-4o-mini --name smoke_eval
```

Important safety rule:

- The default is `--n-format 0`.
- If you choose to use format examples, pass a separate file with `--format-data`.
- Do not reuse the evaluation file as prompt examples.

Example with separate format data:

```bash
python run_eval.py --cheatsheet cheatsheet.txt --data data/hard.jsonl --format-data data/normal.jsonl --n-format 2 --name heldout_eval
```

If you are training research-time feature models and want to respect the no-leak split, pass the holdout file into feature extraction:

```bash
python features.py --data data/normal.jsonl --exclude-eq-file data/no_leak_holdout.json --name no_leak_features
```

## 8. Distill A New Cheatsheet Candidate

If you have labeled training data available, create a new candidate:

```bash
python distill.py --data data/normal.jsonl --name candidate_a --n-shots 150
```

Typical loop:

1. Distill a candidate cheatsheet.
2. Compare its size against the 10 KB limit.
3. Evaluate it with `run_eval.py`.
4. Manually inspect failure buckets.
5. Refine the cheatsheet or distillation prompt.

## 9. Use The Research Stack Carefully

These scripts are useful, but not submission-valid at inference time:

- `solver.py`
- `proof_search.py`
- `magma_search.py`
- `train.py`
- `run_experiments.py`

Use them to discover proof patterns, counterexamples, and structural invariants. Then compress the robust lessons into the cheatsheet.

## 10. Read The Outputs

The most important outputs are:

- `results/eval_*.json`: evaluation results, including benchmark-validity metadata.
- `results/train_*.json` and `results/cv_*.json`: ML experiment summaries.
- `cheatsheets/*.txt`: generated candidate cheatsheets.

When comparing runs, prioritize:

1. validity of the evaluation path;
2. nontrivial-bucket accuracy;
3. stability across runs or models;
4. cheatsheet size and clarity.
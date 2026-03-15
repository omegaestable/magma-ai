# Tutorial (Repo 2.0)

This tutorial is the canonical operational path for the repository.

## 1. Install and activate

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Run the one-command E2E harness

```bash
python repo2_harness.py --name repo2_run --eval-model ollama-qwen2.5-3b
```

Expected behavior:

1. Generates benchmark slices (`local`, `no_leak`, `hardest`).
2. Runs training with feature auto-bootstrap if needed.
3. Runs submission-valid baseline eval on no-leak.
4. Writes summary JSON in `results/repo2_summary_repo2_run.json`.

## 3. Optional candidate distillation and evaluation

```bash
python repo2_harness.py --name repo2_run --eval-model ollama-qwen2.5-3b --run-distill
```

This adds:

1. candidate cheatsheet generation,
2. candidate no-leak eval,
3. gate verdicts for baseline and candidate.

## 4. Read gate verdicts

Open `results/repo2_summary_<name>.json` and inspect:

1. `overall_accuracy`
2. `true_accuracy`
3. `hard_bucket_accuracy`
4. `dual_swap_consistency`
5. `pass`

A candidate should not be promoted if any required gate fails.

## 5. Manual training still supported

```bash
python train.py --dataset default --model-type xgboost --cv 5 --hardest-k 500 --name xgb_manual
```

If the dataset cache is missing, `train.py` auto-creates it.

## 6. Guardrails

1. Keep submission inference cheatsheet-only.
2. Keep matrix/solver/ML use strictly research-time.
3. Treat class asymmetry regressions as failures even if aggregate accuracy looks acceptable.

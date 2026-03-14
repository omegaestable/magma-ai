# Benchmark Integrity Memo

## Design Decisions

1. `run_eval.py` defaults to zero format examples to prevent label leakage from the evaluation set.
2. `run_eval.py` accepts `--format-data` so format examples come from a separate labeled file.
3. `run_eval.py` and `evaluate.py` emit explicit benchmark metadata, including whether a run is submission-valid.
4. Bucket summaries report counts, shares, and accuracies for: trivial, specialization, counterexample_easy, ambiguous, landmark, hard.
5. `download_data.py` generates `data/no_leak_benchmark.jsonl` with held-out equation metadata and `data/hardest_20.jsonl` for structurally misleading cases.
6. `features.py` can exclude held-out equations so feature extraction respects the no-leak split.

## Interpretation Rules

1. A run is submission-valid only when the inference artifact is the cheatsheet and the model has no matrix or graph access at inference time.
2. Using separate labeled format examples is acceptable for local study; reusing evaluation labels is not.
3. Matrix-sampled labels are acceptable as offline supervision, but only if the inference path does not query the matrix.
4. `heuristic` mode in `evaluate.py` is research-only because it measures a handcrafted proxy, not the submitted artifact.

## Known Limitations

1. HF dataset URLs are stale; remote download is best-effort. Set `SAIR_STAGE1_*_URL` env vars when organizer URLs change.
2. Local benchmarks (`local_benchmark.jsonl`, `no_leak_benchmark.jsonl`, `hardest_20.jsonl`) are matrix-derived — useful for internal validation, not as external held-out benchmarks.
3. External competition-rule pages are not archived locally.
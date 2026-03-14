# Benchmark Integrity Memo

## Main Findings

1. The old `run_eval.py` path leaked labels by selecting format examples from the evaluation set and then appending their correct answers into the prompt.
2. The old repo presentation encouraged reading matrix-backed solver results as Stage 1 performance, even though that is a research path, not the submission artifact.
3. The old local reporting emphasized headline accuracy without bucket breakdowns, trivial share, or validity metadata.

## Repairs Made

1. `run_eval.py` now defaults to zero format examples.
2. `run_eval.py` accepts `--format-data` so format examples can come from a separate labeled file.
3. `run_eval.py` and `evaluate.py` now emit explicit benchmark metadata, including whether a run is submission-valid.
4. Bucket summaries now report counts, shares, and accuracies for:
   - trivial
   - specialization
   - counterexample_easy
   - ambiguous
   - landmark
   - hard
5. `download_data.py` can now generate `data/no_leak_benchmark.jsonl` with held-out equation metadata and `data/hardest_500.jsonl` for structurally misleading cases.
6. `features.py` can exclude the held-out equation list so feature extraction respects the no-leak split.

## Interpretation Rules

1. A run is submission-valid only when the inference artifact is the cheatsheet and the model has no matrix or graph access at inference time.
2. Using separate labeled format examples is acceptable for local study; reusing evaluation labels is not.
3. Matrix-sampled labels are acceptable as offline supervision, but only if the inference path does not query the matrix.
4. `heuristic` mode in [evaluate.py](evaluate.py) is research-only because it measures a handcrafted proxy, not the submitted artifact.

## Remaining Gaps

1. The hardcoded Hugging Face dataset slug in the repo appears stale and returns HTTP 404 as of 2026-03-14, so official JSONL download remains best-effort unless alternate URLs are provided.
2. The supported repo-local fallbacks are `data/local_benchmark.jsonl`, `data/no_leak_benchmark.jsonl`, and `data/hardest_500.jsonl`; all are matrix-derived and therefore useful for internal validation, not as organizer-held-out external benchmarks.
3. External competition-rule pages are not archived locally, so some old README claims remain unverified historically even after cleanup.
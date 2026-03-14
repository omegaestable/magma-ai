# Data Directory

This folder contains lightweight benchmark files and the heavier research exports used to derive them.

## Files

| Path | Purpose |
|---|---|
| `local_benchmark.jsonl` | Small offline benchmark generated from the dense implication matrix |
| `no_leak_benchmark.jsonl` | Held-out-equation benchmark for no-leak evaluation |
| `no_leak_holdout.json` | Metadata and held-out equation indices for the no-leak benchmark |
| `hardest_20.jsonl` | Structurally misleading hardest-case benchmark |
| `normal.jsonl` | Organizer-provided split, if later restored or downloaded |
| `hard.jsonl` | Organizer-provided hard split, if later restored or downloaded |
| `exports/export_raw_implications_14_3_2026.csv` | Dense 4694 x 4694 implication matrix |
| `exports/export_explorer_14_3_2026.csv` | Explorer-oriented summary export |

## JSONL Format

Benchmark files use records of the form:

```json
{"equation1_index": 4, "equation2_index": 3, "implies": true}
```

The equation indices are 1-based and refer directly to lines in `equations.txt`.

## Dense Matrix Encoding

The dense implication matrix stores more than a bare boolean label.

- `3`: TRUE, already established from known project data.
- `4`: TRUE, but originally marked as needing a direct proof artifact.
- `-3`: FALSE, already established from known project data.
- `-4`: FALSE, but originally marked as needing an explicit counterexample artifact.
- `0`: unknown or unused entry.

For local benchmark generation, this repo treats any positive value as TRUE and any negative value as FALSE.

## Generating Local Data

```bash
python download_data.py --generate-local --n 200 --seed 42
```

This creates a balanced `data/local_benchmark.jsonl` file sampled from the dense matrix and is the recommended no-network smoke test for the evaluation pipeline.

```bash
python download_data.py --generate-no-leak --n 200 --holdout-count 100 --seed 42
```

This creates `data/no_leak_benchmark.jsonl` plus `data/no_leak_holdout.json` so the same held-out equations can be excluded from feature extraction.

```bash
python download_data.py --generate-hardest --hardest-n 500 --seed 42
```

This creates `data/hardest_500.jsonl`, a benchmark concentrated on pairs where lightweight structural heuristics are actively misleading.

## Reproducibility Notes

- `local_benchmark.jsonl` is the preferred offline benchmark for local development.
- `no_leak_benchmark.jsonl` is the preferred offline benchmark for leakage-sensitive evaluation.
- `hardest_20.jsonl` is the preferred offline benchmark for adversarial debugging of misleading structural signals.
- The dense exports are research assets, not submission artifacts.
- Remote HF download is best-effort; set `SAIR_STAGE1_NORMAL_URL` / `SAIR_STAGE1_HARD_URL` env vars if organizer URLs change.

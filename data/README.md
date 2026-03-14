# Local benchmark data

This folder stores benchmark JSONL files used by the evaluation pipeline.

## Files

| File | Source | Purpose |
|---|---|---|
| `local_benchmark.jsonl` | Generated from CSV matrix via `download_data.py --generate-local` | Supported offline eval without any external dataset host |
| `normal.jsonl` | Organizer-provided official split, if available | Official training split |
| `hard.jsonl` | Organizer-provided official split, if available | Official hard split |

## Generating local data

The supported fallback is to generate a local benchmark from the implication
matrix CSV:

```
python download_data.py --generate-local
```

This creates `data/local_benchmark.jsonl` with 200 balanced pairs sampled from
the CSV matrix—enough to validate the full LLM evaluation pipeline.

Note: the old hardcoded Hugging Face dataset slug referenced elsewhere in this
repo appears stale and returns 404 as of 2026-03-14.

# Benchmark Manifest

Stage 2 benchmarks are proof-certificate problem sets consumed by the official harness. The old Stage 1 normal/hard/hard3 prompt-evaluation files are archived under `stage1/data/`.

## Official Development Problems

The vendored official repository includes public development problem files under:

```text
vendor/stage2-official/examples/problems/
```

Expected files include sample sets and public mirrored subsets such as `sample_20.json`, `sample_200.json`, `normal.jsonl`, and hard-family JSONL files. Treat the official repo docs and current directory contents as canonical if upstream changes names.

Current public development file sizes used in this repo:

- `normal.jsonl`: `1000`
- `hard1.jsonl`: `69`
- `hard2.jsonl`: `200`
- `hard3.jsonl`: `400`
- `sample_20.json`: `20`
- `sample_200.json`: `200`

## Problem Shape

Each problem contains at least:

1. problem id
2. `eq1_id`
3. `eq2_id`
4. `equation1`
5. `equation2`

Some public files may also include an answer field for development. The private evaluation set is separate and TBD upstream.

The root cache also contains imported Hugging Face `evaluation_*` subsets, but
those are analysis-only for now and are not part of the official runner-facing
benchmark workflow unless explicitly promoted later.

## Solo Mode

Solo runs one problem per solver subprocess through stdin/stdout JSON. Use it for fast certificate debugging.

Canonical docs:

```text
vendor/stage2-official/docs/solo_mode.md
vendor/stage2-official/examples/solo/TUTORIAL.md
```

## Marathon Mode

Marathon runs many problems per solver subprocess with a shared budget. Use it for competition strategy, triage, and cache reuse.

Canonical docs:

```text
vendor/stage2-official/docs/marathon_mode.md
vendor/stage2-official/examples/marathon/TUTORIAL.md
```

## Local Result Storage

Use `stage2/results/` for Stage 2 summaries, failure ledgers, and promotion evidence. Do not mix new Stage 2 results into archived Stage 1 result directories.

Key generated artifacts after the 2026-05-12 readiness pass:

- `2026-05-12-public-finite-countermodels-summary.md`
- `2026-05-12-public-failure-ledger.jsonl`
- `2026-05-12-competition-preflight.md`

The current best public benchmark total is `998/1669` solved with `0` LLM
calls, but the ledger still shows the next frontier clearly:

- `571` public `true_template_gap`
- `100` public `finite_countermodel_gap`

## Stage 1 Archive

Archived Stage 1 benchmark data lives at:

```text
stage1/data/benchmark/
stage1/data/hf_cache/
```

Use those only for historical analysis.

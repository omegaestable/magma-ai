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

Treat `normal/hard1/hard2/hard3` as the full public benchmark refresh set. Treat `sample_20`, `sample_200`, targeted one-off JSON fixtures, and Marathon slices as smoke/debug evidence unless a document explicitly promotes a date-stamped run under `stage2/results/`.

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

Current analysis-only root-cache files include `evaluation_normal.jsonl`, `evaluation_hard.jsonl`, `evaluation_extra_hard.jsonl`, and `evaluation_order5.jsonl`.

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

Current local smoke slice: `examples/problems/marathon/normal_100.jsonl`. The latest packaged smoke accepted `74/100` with zero token budget in `60.6s` on 2026-05-25. Do not fold this into the full public total.

## Local Result Storage

Use `stage2/results/` for Stage 2 summaries, failure ledgers, and promotion evidence. Do not mix new Stage 2 results into archived Stage 1 result directories.

Key generated artifacts:

- `2026-05-18-zero-token-public-refresh-after-witness.md`
- `2026-05-12-public-finite-countermodels-summary.md`
- `2026-05-12-public-failure-ledger.jsonl`
- `2026-05-12-competition-preflight.md`

The current completed public benchmark total is `1201/1669` solved with `0` LLM
calls, from `2026-05-18-zero-token-public-refresh-after-witness.md`. Full
public no-loss validation of the final optimized package is still pending.
The ledger now shows the next frontier clearly:

- `429` public TRUE misses
- `39` public FALSE misses

Latest smoke-only housekeeping evidence, separate from those public totals:

- `sample_20`: `15/20` in the 2026-05-25 no-key Solo smoke
- `sample_200`: `169/200` in the 2026-05-25 no-key Solo smoke
- Marathon `normal_100`: `74/100`, zero tokens in the 2026-05-25 packaged smoke
- accepted-grind fixture with heartbeat cap: `34/34`
- compact witness fixture: `8/8`
- fresh May 17 hard mixes with zero-token Marathon: `91/150`, `83/150`, and `72/150` on seeds `20260516`, `20260517`, and `20260518`

## Stage 1 Archive

Archived Stage 1 benchmark data lives at:

```text
stage1/data/benchmark/
stage1/data/hf_cache/
```

Use those only for historical analysis.

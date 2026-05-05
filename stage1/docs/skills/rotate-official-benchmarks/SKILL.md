---
name: rotate-official-benchmarks
description: 'Refresh rotating unseen SAIR benchmark bundles from the official Hugging Face subsets. Use when local evaluation looks memorized, when results drift from the official lab, or when you need fresh normal 30/30, hard 20/20, and hard3 10/10 slices.'
argument-hint: 'Optional: say whether to purge legacy unseen files or refresh the Hugging Face cache.'
user-invocable: true
disable-model-invocation: false
---

# Rotate Official Benchmarks

Use this skill when the local benchmark suite has gone stale, when repeated runs look suspiciously high, or when you want a closer match to the official SAIR lab pools.

## Procedure

1. Regenerate the rotating benchmark bundle:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe make_unseen_30_30_sets.py --purge-legacy-unseen
```

2. If you need to refetch the upstream subsets first, add `--refresh-cache`.

3. Read `data/benchmark/rotating_official_latest.json` and use the listed JSONL files for unseen evaluation.

4. Run evaluation against those files instead of any historical `*_unseen_*.jsonl` artifact.

5. If the new bundle exposes regressions, distill before editing the cheatsheet.

## Outputs

- `data/benchmark/*_rotation*.jsonl`
- `data/benchmark/rotating_official_latest.json`
- `data/benchmark/rotating_official_state.json`

## Guardrails

- Source only from the official Hugging Face subsets `normal`, `hard`, and `hard3`.
- Default class balance is `30/30` for normal, `20/20` for hard, and `10/10` for hard3.
- Treat frozen `*_unseen_*.jsonl` files as legacy artifacts, not canonical evaluation inputs.
- Do not promote a cheatsheet from one rotating bundle alone; pair the bundle with normal gate evidence.
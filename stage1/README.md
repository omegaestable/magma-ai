# Stage 1 Archive

This directory preserves the SAIR Equational Theories Stage 1 prompt-cheatsheet work.

Stage 1 is no longer the active workflow. The top-level repo now targets Stage 2 Lean-certificate solver development.

## Final State

- Final active candidate: `cheatsheets/v28d.txt`.
- Previous champion: `cheatsheets/v28c.txt`.
- Historical champion: `cheatsheets/v24j.txt`.
- Reported leaderboard position at transition: 22 general, 10 GPT-only.
- Old evaluator and wrappers: `eval/`.
- Old analysis and distillation scripts: `analysis/`.
- Old verification helpers: `verify/`.
- Old benchmark data: `data/`.
- Old results and scoreboards: `results/`.
- Old prompt docs and champion notes: `docs/`.

## Layout

- `cheatsheets/`: submitted and candidate prompt files.
- `eval/`: Stage 1 paid-model evaluator, wrappers, and scoreboard tooling.
- `analysis/`: failure distillation, hard-set analysis, and mining scripts.
- `verify/`: Stage 1 safety checks and witness audits.
- `research/`: optional orchestration and experimental helpers.
- `docs/`: Stage 1 playbooks, rules, prompt plans, and champion history.
- `data/`: Stage 1 benchmark pools and Hugging Face cache.
- `results/`: Stage 1 run payloads, scoreboards, and proof-lab outputs.
- `_archive/`: older exploratory scripts.
- `paper/`: Stage 1 manuscript artifacts.

## Repro Notes

Most Stage 1 scripts were written to run from the old repository root. If historical reproduction is needed, expect to adjust paths or run from a compatibility copy. Do not use this archive as the active Stage 2 starting point.

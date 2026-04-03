# Current State

This file is the operational truth for the current phase. Keep it short and update it when the champion, candidate, or gate results change.

Last updated: 2026-04-03

## Current Artifacts

- Baseline champion: `cheatsheets/v21f_structural.txt`
- Active candidate: `cheatsheets/v23.txt`
- Canonical evaluator: `sim_lab.py`
- Canonical wrapper: `run_paid_eval.ps1`

## Current Strategy

- Submission style: pure natural-language cheatsheet
- Allowed template variables: `{{equation1}}`, `{{equation2}}`
- Banned: Jinja2 logic, dynamic lookup tables, benchmark-pair hardcoding
- Current working direction: 4 structural tests with strong decision-table framing and strict output discipline

## Known Benchmarks Status

Baseline v21f:

- Warmup seed0: 90%
- Warmup seed1: 90%
- Full normal seed0: 90%
- Full normal seed1: 90%
- Full normal seed2: 90%

Current v23 status:

- Warmup seed0: 90%
- Warmup seed1: 90%
- Full normal seed0: 95%
- Full normal seed1: 85%
- Full normal seed2: 90% (10/10 TRUE, 8/10 FALSE, parse 100%)
- Unseen and hard stress: still blocked because the full normal gate set contains a regression

## Current Read

- v23 has completed the full normal seed set but is not promoted.
- v21f remains the safe champion because v23 regressed on full normal seed1 and only tied the champion on seed2.
- The main live risks are false-positive coverage gaps on normal FALSE pairs, execution variance, and restart drift.
- Promotion is blocked; the next move is the distill-patch loop rather than stress runs.

## Operational Promotion Rule

For v23 to replace v21f:

1. all three full normal seeds must meet or beat the current champion
2. no full normal seed may regress below the champion
3. if any full normal seed regresses, return to the distill-patch loop instead of promoting

## Open Risks

1. v23 still has run-to-run variance.
2. Full normal seed1 is still below the champion and blocks promotion.
3. Full normal seed2 missed `normal_0628` and `normal_0907`, both false positives with clean parsing.
4. Old planning and historical docs can still distract fresh agents if they ignore this file.
5. Research-only scripts remain visible at the repo root and can pull work off the canonical path.

## Next Decision Point

Distill the full normal regressions, patch v23 conservatively, and re-run the failing normal seeds before any unseen or hard stress work.
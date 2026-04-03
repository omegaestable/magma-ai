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
- Full normal seed2: not yet run
- Unseen and hard stress: blocked until full normal seed set is complete

## Current Read

- v23 is promising but not promoted.
- v21f remains the safe champion until v23 clears the full normal gate set without regression.
- The main live risks are execution variance and restart drift, not missing infrastructure.
- Promotion is blocked until v23 completes full normal seed2 and the full normal set is stable.

## Open Risks

1. v23 still has run-to-run variance.
2. Full normal seed2 still needs confirmation.
3. Old planning and historical docs can still distract fresh agents if they ignore this file.
4. Research-only scripts remain visible at the repo root and can pull work off the canonical path.

## Next Decision Point

Decide whether v23 becomes the new champion after the full normal seed set and stress runs are complete.
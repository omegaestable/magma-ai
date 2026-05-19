# Latest Handoff

Updated: 2026-05-18

This is the compressed team-memory note for the current Stage 2 solver and homelab state.

## What Changed

- Added broad zero-token `true:grind` fallback as a discovery route for short absorption/congruence-shaped TRUE rows.
- Added three more compact named FALSE witness tables to `stage2/solver/solver.py`: `S4D`, `S4E`, and `S5D`.
- Packaged `stage2/submissions/solver.py` is `69553` bytes, and `stage2/submissions/` contains only `solver.py`.
- Added reusable zero-token sweep tooling:
  - `stage2/experiments/run_zero_token_sweeps.py`
  - `stage2/experiments/analyze_zero_token_run.py`
- The vendored Solo harness still has local OpenRouter provider-normalization drift; this does not affect zero-token Marathon scoring.

## Best Public Evidence

Latest official public evidence is the completed zero-token Marathon refresh after the `S4D`/`S4E`/`S5D` witness patch:

- `normal`: `803/1000` solved, `305 TRUE + 498 FALSE`, `0` solver tokens (`normal` score was salvaged with `--score-only`).
- `hard1`: `42/69` solved, `6 TRUE + 36 FALSE`, `0` tokens.
- `hard2`: `92/200` solved, `16 TRUE + 76 FALSE`, `0` tokens.
- `hard3`: `264/400` solved, `63 TRUE + 201 FALSE`, `0` tokens.

Public total is now `1201/1669`, split `390 TRUE + 811 FALSE`, with `35` not attempted and `433` incorrect attempted certificates.

Durable summary:

- `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`

## Latest Local Evidence

- Pre-final-witness public zero-token Marathon sweep: `1189/1669`.
- Post-witness public zero-token Marathon refresh: `1201/1669`, a `+12` delta.
- Net public FALSE lift from `S4D`/`S4E`/`S5D`: `+10` (`hard1 +3`, `hard2 +3`, `hard3 +4`, `normal +0`).
- Focused residual FALSE fixture: `8/8` accepted, `0` tokens, route counts `S4D=5`, `S4E=1`, `S5D=2`.
- `true:grind` public behavior after refresh: `34` accepted, `433` incorrect.
- Answer-kind accepted totals: `811 false:finite`, `356 true:certificate`, `34 true:grind`.
- Remaining public misses by answer labels: `429` TRUE and `39` FALSE.

Other durable notes:

- `stage2/results/2026-05-17-hard-mix-witness-summary.md`
- `stage2/results/2026-05-17-homelab-openrouter-proxy-smoke.md`
- `stage2/docs/playground-preflight.md`

## Highest-Value Learnings

1. Compact finite witnesses are still low-risk deterministic FALSE gains, but the public frontier is now overwhelmingly TRUE-heavy.
2. Broad `grind` is useful as a temporary discovery route, not as the next clean solver strategy: it scored `34` public TRUE wins but caused `433` official incorrect proof attempts and slow hard-lane scoring.
3. Accepted `grind` wins are mostly absorption/congruence-shaped (`31/34` absorption-shaped, `25/34` same-LHS). Widening existing closure bounds recovered only `4/34`, so the next TRUE route should be proof-producing local congruence/e-graph extraction.
4. The normal refresh initially hit a judge infrastructure artifact error compiling `JudgeProblem`; preserving `answers.jsonl` and rerunning `--score-only` with an isolated `JUDGE_ARTIFACT_DIR` cleanly recovered the score.
5. HF/evaluation mirror sweeps remain discovery evidence and should stay separate from public Marathon evidence.

## Risks And Cautions

1. Treat the `1201/1669` result as official zero-token Marathon evidence, not the older Solo/pipeline summary format.
2. Do not promote broad `true:grind` as final-clean without addressing its `433` incorrect public attempts.
3. Do not call vendored Solo harness behavior official-clean without noting the local provider-normalization drift.
4. `tmp_stage2_smoke/` remains scratch space. Promote only date-stamped summaries under `stage2/results/` into team memory.
5. The judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr and summaries.
6. Runner-equivalent certificate debugging should use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)`.

## Recommended Next Steps

1. Implement a bounded local congruence/e-graph TRUE extractor before broad `true:grind`. Reuse existing term parsing, substitution, absorption pool, and proof-chain helpers; emit explicit `h`, `.symm`, `.trans`, and `congrArg` Lean terms.
2. Validate it on `tmp_stage2_smoke/2026-05-17-zero-token-sweep/local_congruence_grind_focus.jsonl`, then rerun the focused witness and TRUE closure regression fixtures.
3. Tighten or remove broad `true:grind` once explicit TRUE certificates cover most of its accepted wins.
4. Run the HF mirror sweep as a separate discovery lane:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\run_zero_token_sweeps.py --scope hf --include-hf-core-duplicates --run-root tmp_stage2_smoke\2026-05-17-zero-token-hf-after-witness --force
```

5. Before any upload/promotion, rerun the adversarial review checklist and re-check `stage2/docs/playground-preflight.md`.
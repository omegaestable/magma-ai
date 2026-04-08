# Current State

This file is the operational truth for the current phase. Keep it short and update it when the champion, candidate, or gate results change.

Last updated: 2026-04-07 (v24j promoted)

## Current Artifacts

- **Champion: `cheatsheets/v24j.txt`** (8,955 bytes, 87.4% of 10,240 cap)
- Previous champion: `cheatsheets/v21f_structural.txt` (historical)
- Canonical evaluator: `sim_lab.py`
- Canonical wrapper: `run_paid_eval.ps1`
- Final report: `results/v24j_final_report.md`
- Next design doc: `V25A_MASTER_PROMPT.md`

## Current Strategy

- Submission style: pure natural-language cheatsheet
- Allowed template variables: `{{equation1}}`, `{{equation2}}`
- Banned: Jinja2 logic, dynamic lookup tables, benchmark-pair hardcoding
- Architecture: 4 structural tests (LP, RP, C0, VARS) + decision table + T3R algebraic rescue (a*b=next(b) on Z3)
- Key innovations over v21f/v23c: T3R rescue for algebraic separation, explicit rewrite-with-numbers-first protocol, E1 abort guard, verbose worked examples

## v24j Benchmark Results

All runs use `normal_balanced60` and `hard3_balanced40` rotation0002 benchmarks.

Current v24j (9,043 bytes):

- Normal run 1: **91.7%** (4 FP, 1 FN, 100% parse, F1=92.1%)
- Normal run 2: **90.0%** (6 FP, 0 FN, 100% parse, F1=90.9%)
- Normal mean: **90.85%**

- Hard3 run 1: **72.5%** (11 FP, 0 FN, 100% parse, F1=78.4%)
- Hard3 run 2: **65.0%** (13 FP, 1 FN, 100% parse, F1=73.1%)
- Hard3 mean: **68.75%**

Pre-final v24j (8,887 bytes, before Example F addition):

- Normal: **93.3%** (4 FP, 0 FN, 100% parse)
- Hard3: **52.5%** (17 FP, 2 FN, 100% parse)

Invalid run (catastrophically golfed 6,690-byte version, discarded):

- Normal: 66.7% — excluded from all averages

## Current Read

- v24j is the culmination of the v24 line: v24a through v24j, adding T3R algebraic rescue to the 4-test structural backbone.
- v24j achieves **100% parse rate** and near-zero FN on all valid runs.
- Normal performance (90-93%) matches or exceeds the v21f/v23c structural ceiling (~88-92%).
- Hard3 performance (65-72.5%) is a major step up from v23c's 50% (which had 0% FALSE accuracy).
- The T3R rescue (a*b=next(b) on Z3) provides genuine algebraic separation power that structural tests alone cannot.
- Prompt verbosity is critical: compressing examples or the decision table causes catastrophic collapse (see the 66.7% golfed run).
- At 8,955 bytes (87.4% of cap), budget for further expansion is limited.

## Open Risks

1. Hard3 FALSE accuracy (35-45%) is still the main gap — many algebraic separations need witnesses beyond T3R's Z3 next-map.
2. Temperature stochasticity creates ~5% noise floor per run.
3. Byte budget is 87.4% consumed — only ~1,285 bytes remain for v25 additions.
4. Prompt is near the verbosity/performance sweet spot — further additions risk execution degradation.

## Next Decision Point

v24 line is complete. Next agent should:

1. Read `V25A_MASTER_PROMPT.md` for the next design document.
2. Focus on hard3 FALSE coverage improvement while protecting normal safety.
3. Any v25 candidate must gate on normal ≥90% mean before hard3 testing.
4. Do not compress or golf v24j content — verbosity is load-bearing.
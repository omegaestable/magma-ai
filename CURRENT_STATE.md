# Current State

This file is the operational truth for the current phase. Keep it short and update it when the champion, candidate, or gate results change.

Last updated: 2026-04-14 (v27a created — v26b base + XOR/T4A/T5B magma tests)

## Critical Pipeline Changes (2026-04-11)

1. **Prompt mode switched to RAW**: cheatsheet IS the complete prompt. No eval template wrapping.
2. **3 official evaluation models**: GPT-OSS-120B, Llama 3.3 70B, Gemma 4 31B IT (equal weight).
3. **Verdict parser upgraded**: 3-tier extraction matching official `judge.py` (boxed > labeled > line).
4. **Spine Isolation Theorem** integrated as `spine_classify.py` — new separation test with zero false positives.

## Current Artifacts

- **Active candidate: `cheatsheets/v27a.txt`** (10,161 bytes — v26b + XOR/T4A/T5B)
- Previous champion: v24j (8,955 bytes)
- Cancelled line: v26a–v26f (kept as historical artifacts)
- Canonical evaluator: `sim_lab.py` (aligned with official judge 2026-04-11)
- Canonical wrapper: `run_paid_eval.ps1`
- Smoke/gate runner: `run_smoke_gate.ps1`
- Spine classifier: `spine_classify.py`

## Current Strategy

- Submission style: pure natural-language cheatsheet (IS the complete prompt)
- Prompt mode: **raw** (cheatsheet sent directly to model, no wrapping)
- Allowed template variables: `{{equation1}}`, `{{equation2}}`
- Banned: Jinja2 logic, dynamic lookup tables, benchmark-pair hardcoding
- Architecture: 4 structural tests (LP, RP, C0, VARS) + decision table + Spine Depth Check + T3R rescue + T3L rescue
- v26b adds: expanded T3L section with explicit guard (LP E1=HOLD), step-by-step instructions, next(a) rule
- Evaluation: 3 models × balanced benchmarks, official verdict parser (GPT-OSS primary for speed)

## v26b Benchmark Results (GPT-OSS-120B, raw mode, 2026-04-12)

**v26a → v26b delta**: Expanded T3L from 4 lines to full section with guard + instructions. Trimmed 5 redundant RULES lines.

### v26b (9,729 bytes):
- Normal (20, rotation0011): **95.0%** (1 FP, 0 FN, F1=95.2%) — matches v26a
- Hard3 (20, rotation0011): **75.0%** (5 FP, 0 FN, F1=80.0%) — **+10pp vs v26a**
- Hard2 (20, random): **40.0%** (12 FP, 0 FN) — same as v26a (10/12 need 4+ element magmas)

### v26a (10,146 bytes, previous):
- Normal (20, rotation0010): **95.0%** (1 FP)
- Hard3 (20, rotation0010): **65.0%** (7 FP)
- Hard2 (20, random): **40.0%** (12 FP)

### Historical v24j (8,955 bytes, wrapped mode):
- Normal mean: **90.85%**
- Hard3 mean: **68.75%**

## Current Read

- v26b is the current best candidate: 4 structural tests + Spine Depth + T3R + expanded T3L.
- v26b achieves **100% parse rate** and **zero FN** on all runs.
- Normal 95% is stable across v26a and v26b (structural tests carry normal).
- Hard3 75% is a +10pp gain from v26a's 65% — the T3L expansion fixed at least one execution error class.
- Hard2 remains at 40% because 10/12 FALSE pairs need 4+ element magma witnesses, beyond our 3-element techniques.
- All errors are FP (model says TRUE when answer is FALSE) — coverage gaps, not execution errors.
- 511 bytes remaining in v26b for further expansion.

## Error Classification (v26b, 2026-04-12)

- **Normal FP** (1): coverage gap needing 3-element magma [[0,1,2],[0,0,0],[0,0,0]]
- **Hard3 FP** (5): all 5 are 3-element separable but need non-T3R/T3L magmas
- **Hard2 FP** (12): 2 are 3-element separable, 10 need 4+ element magmas
- **Theoretical ceiling** with only 3-element techniques: ~17/18 errors are fixable with unlimited byte budget
- **Practical ceiling**: hard2 is structurally bottlenecked by 4+ element requirements

## Open Risks

1. **Single-model testing**: All v26b scores are GPT-OSS-120B only. Llama 3.3 70B had rate-limiting (429). Gemma 4 31B IT was too slow.
2. Hard2 FALSE accuracy is 0% — these pairs systematically evade all current tests.
3. Temperature stochasticity creates ~5% noise floor per run.
4. 511 bytes remaining — tight budget for any further expansion.
5. **DEADLINE: April 20, 2026 (8 days)**

## Next Steps

1. Test v26b on Llama 3.3 70B and Gemma 4 31B IT when rate limits clear.
2. Consider adding a third algebraic magma (e.g., all-zero [[0,0,0],[0,0,0],[0,0,0]]) to catch more hard3 FALSE.
3. Run full gate (50/50 normal + 50/50 hard3) for promotion evidence.
4. If cross-model safety holds → v26b is submission candidate.
5. Submit by April 20.
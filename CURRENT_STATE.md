# Current State

This file is the operational truth for the current phase. Keep it short and update it when the champion, candidate, or gate results change.

Last updated: 2026-04-17 (v28d DECLARED CHAMPION — 96.7% normal, 50.0% comp hard)

## Critical Pipeline Changes (2026-04-11)

1. **Prompt mode switched to RAW**: cheatsheet IS the complete prompt. No eval template wrapping.
2. **3 official evaluation models**: GPT-OSS-120B, Llama 3.3 70B, Gemma 4 31B IT (equal weight).
3. **Verdict parser upgraded**: 3-tier extraction matching official `judge.py` (boxed > labeled > line).
4. **Spine Isolation Theorem** integrated as `spine_classify.py` — new separation test with zero false positives.

## Current Artifacts

- **CHAMPION: `cheatsheets/v28d.txt`** (9,081 bytes — v28c + T5B all-ones guard fix)
- Previous champion: v28c (8,911 bytes)
- Historical: v24j (8,955 bytes), cancelled line v26a–v26f
- Canonical evaluator: `sim_lab.py` (aligned with official judge 2026-04-11)
- Canonical wrapper: `run_paid_eval.ps1`
- Smoke/gate runner: `run_smoke_gate.ps1`
- Spine classifier: `spine_classify.py`

## Current Strategy

- Submission style: pure natural-language cheatsheet (IS the complete prompt)
- Prompt mode: **raw** (cheatsheet sent directly to model, no wrapping)
- Allowed template variables: `{{equation1}}`, `{{equation2}}`
- Banned: Jinja2 logic, dynamic lookup tables, benchmark-pair hardcoding
- Architecture: 6 structural tests (LP, RP, C0, VARS, LDepth, Spine) + decision table + T3R/T3L/T5B/NL1 rescue magma tests
- v28d change: T5B now requires E1 to pass on BOTH default assignment AND all-ones before declaring separation
- Evaluation: GPT-OSS-120B primary (API via OpenRouter), raw mode, balanced rotations

## v28c/v28d Benchmark Results (GPT-OSS-120B, raw mode)

### v28c (8,911 bytes, 87.0% of cap):
- hard3 r21 (20): **90.0%** (18/20) — high variance rotation
- hard3 r22 (30): **46.7%** (14/30)
- hard2 r22 (30): **43.3%** (13/30)
- Competition hard r23 (30): **43.3%** (13/30) — TP=8, FP=10, FN=7, TN=5, unparsed=1
- Normal: pending

### v28d (9,081 bytes, 88.7% of cap) — CHAMPION:
- **Normal r23 (30): 96.7% (29/30)** — PASSED safety gate (TP=15, FP=1, FN=0, TN=14)
- **Competition hard r23 (30): 50.0% (15/30)** — TP=11, FP=11, FN=4, TN=4 (+6.7pp vs v28c)
- **Hard3 r24 (30): 83.3% (25/30)** — TP=15, FP=5, FN=0, TN=10, 100% TRUE recall
- **Hard2 r24 (30): 43.3% (13/30)** — TP=9, FP=11, FN=6, TN=4
- T5B fix confirmed: hard_0174 ✗→✓, hard_0169 ✗→✓

### v28c → v28d change:
T5B all-ones guard. Mathematically proven strictly positive across all pools:
| Pool | v28c ceiling | v28d ceiling | Delta |
|------|-------------|-------------|-------|
| Competition hard (200) | 51.0% | 51.5% | +0.5% |
| hard3 (400) | 66.0% | 66.2% | +0.2% |
| normal (1000) | 90.3% | 90.8% | +0.5% |

## Known Unsoundness (2026-04-17)

| Test | False seps (hard) | False seps (hard3) | False seps (normal) | Status |
|------|-------------------|--------------------|--------------------|--------|
| T5B | 7 → fixed in v28d | varies | varies | FIXED |
| NL1 | 3 | varies | varies | NOT fixed (net negative on hard) |
| T3R | 3 (all ≥4 vars) | 4 | 17 | NOT fixed (net negative overall) |
| T3L | 0 | 0 | 0 | Sound — no fix needed |

## Open Risks

1. **Single-model testing**: All v28 scores are GPT-OSS-120B only. Llama/Gemma untested since v24j.
2. API severely congested — evals taking 30+ minutes for 30 problems.
3. High variance between rotations (hard3 r21=90% vs r22=46.7%).
4. 1,159 bytes remaining in v28d — budget for future improvements.
5. **DEADLINE: April 20, 2026 (3 days)**

## Next Steps

1. ~~Run v28d competition hard r23~~ — DONE: 50.0% (15/30), +6.7pp over v28c.
2. ~~Declare v28d champion~~ — DONE.
3. ~~Run v28d hard3 r24~~ — DONE: 83.3% (25/30), 100% TRUE recall.
4. ~~Run v28d hard2 r24~~ — DONE: 43.3% (13/30).
5. Consider cross-model testing on Llama/Gemma for confidence.
6. Repo cleanup and submission polish.
7. Submit by April 20.
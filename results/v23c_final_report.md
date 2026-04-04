# v23c Final Report

**Date:** 2026-04-03
**Candidate:** `cheatsheets/v23c.txt` (6,036 bytes, 58.9% of 10,240 cap)
**Model:** meta-llama/llama-3.3-70b-instruct via OpenRouter
**Mode:** --playground-parity (temperature=provider default, max_tokens=provider default)

## Evolution: v23 → v23a → v23b → v23c

| Version | Bytes | Changes | Outcome |
|---------|-------|---------|---------|
| v23 | 4,977 | 4 tests (LP/RP/C0/VARS), 3 examples, decision table | Baseline: 90% seed0, stochastic variance |
| v23a | 7,175 | Added XOR 5th test, 4th example, stronger format | **REGRESSION** 70% warmup — cognitive overload |
| v23b | 5,781 | Removed XOR, added Example D (RP), strengthened format rules | Recovered: 90% seed0, 85% seed1, 100% parse |
| v23c | 6,036 | Strengthened LP tip (nested examples), C0 clarification, LP rule | **FINAL**: 90%/85%/90% across 3 seeds, 100% parse |

## Normal Gate Results (v23c)

| Seed | N | Acc | FP | FN | Parse | FP Classification |
|------|---|-----|----|----|-------|-------------------|
| seed0 (20) | 20 | 90% | 2 | 0 | 100% | 2 coverage gaps |
| seed1 (20) | 20 | 85% | 3 | 0 | 100% | 2 coverage gaps + 1 stochastic C0 |
| seed2 (20) | 20 | 90% | 2 | 0 | 100% | 2 coverage gaps |
| **Aggregate** | **60** | **88.3%** | **7** | **0** | **100%** | 6 gaps + 1 stochastic |

## Massive Run Results

*(To be filled after rotation0002 runs complete)*

### Normal 60 (rotation0002)

| Metric | Value |
|--------|-------|
| N | 60 |
| Accuracy | **93.3%** |
| F1 | 93.8% |
| Precision (TRUE) | 88.2% |
| Recall (TRUE) | 100.0% |
| TRUE accuracy | 100.0% (30/30) |
| FALSE accuracy | 86.7% (26/30) |
| FP | 4 |
| FN | 0 |
| Parse rate | 100.0% |
| Avg time/run | 13.1s |
| Total time | 786.9s |

**FP Classification (Normal 60):**

| Pair ID | Equation 1 | Equation 2 | Type |
|---------|-----------|-----------|------|
| normal_0884 | x * x = (x * y) * (z * z) | x * x = (x * (x * y)) * z | Coverage gap (all 4 tests pass) |
| normal_0335 | x = y * (x * (x * y)) | x = (x * (y * (y * z))) * w | **Execution error** (RP=F, VARS=F — model missed both!) |
| normal_0618 | x = y * (y * (z * (z * x))) | x = (x * y) * (z * x) | Coverage gap (all 4 tests pass) |
| normal_0301 | (x * y) * y = (y * z) * z | x * (y * z) = (z * y) * x | **Execution error** (RP=F — model missed RP difference) |

**Breakdown:** 2 coverage gaps + 2 execution errors (both RP-related).

### Hard3 40 (rotation0002)

| Metric | Value |
|--------|-------|
| N | 40 |
| Accuracy | **50.0%** |
| F1 | 66.7% |
| Precision (TRUE) | 50.0% |
| Recall (TRUE) | 100.0% |
| TRUE accuracy | 100.0% (20/20) |
| FALSE accuracy | 0.0% (0/20) |
| FP | 20 |
| FN | 0 |
| TN | 0 |
| Parse rate | 100.0% |
| Avg time/run | 16.7s |
| Total time | 669.6s |

**FP Classification (Hard3 40):** All 20 FP are **coverage gaps**. By definition, hard3 pairs share identical LP, RP, C0, and VARS signatures — structural tests provide zero separation. The model defaults to TRUE for every problem, achieving perfect TRUE recall but zero FALSE detection.

**Comparison with v23 on same benchmark:**

| Metric | v23 | v23c | Delta |
|--------|-----|------|-------|
| Accuracy | 45.0% | **50.0%** | +5% |
| Parse rate | 85.0% | **100.0%** | +15% |
| FP | 19 | 20 | +1 |
| FN | 3 | **0** | -3 |
| Unparsed | 6 | **0** | -6 |
| TRUE accuracy | ~55% | **100%** | ~+45% |

v23c is strictly better: the 5% accuracy gain comes entirely from eliminating unparsed/FN errors (v23 lost 6 to parse failures and 3 to false negatives). Both versions fail identically on FALSE pairs due to the coverage gap ceiling.

## Key Findings

### 1. Structural Test Ceiling
- The 4-test architecture (LP/RP/C0/VARS) catches only ~67% of FALSE pairs on normal sets.
- 34 of 36 unique failures across all benchmark rotations are **coverage gaps** — no combination of text-inspection tests can separate them.
- The remaining ~33% of FALSE pairs require actual algebraic evaluation (4×4 Cayley tables, finite magma construction) that cannot be reliably taught in a 10K prompt.

### 2. Parse Robustness Is The Highest-Yield Lever
- v23 (original): 8/60 unparsed on noisy runs → direct accuracy penalty
- v23c: **0/60 unparsed** across all gate runs → eliminated a 13% error source
- Key format interventions: explicit anti-## header rules, anti-\boxed{} rules, plain-text-only enforcement

### 3. Execution Error Taxonomy
- **LP scanning errors**: Model fails to skip nested `((` to find first variable. Fixed in v23c with concrete deeply-nested examples.
- **C0 waffling**: Model correctly identifies C0 result but talks itself out of FAIL by confusing C0 with VARS logic. Partially addressed with "C0 checks ONLY whether * is present" clarification.
- **Decision table lookup**: Model writes "E1=HOLD E2=FAIL" then concludes "no separation". Fixed in v23b with explicit "If you write E1=HOLD and E2=FAIL that IS separation" language.

### 4. Adding Tests Has Negative ROI
- v23a added XOR (5th test): +2,198 bytes, caused ## Step format switch, lost 2 correct answers, net -20% accuracy.
- Lesson: each additional test adds cognitive load that increases execution errors faster than it closes coverage gaps.

### 5. Temperature Stochasticity
- With provider-default temperature (~0.7), each run has 2-3 stochastic errors.
- The same pair can be correct in one run and incorrect in the next.
- This creates an irreducible ~5% noise floor on any given run.

## Structural Ceiling Analysis

The v23c architecture has a hard ceiling of approximately **88-92% on normal sets**:
- ~67% of FALSE pairs caught by 4 structural tests → these are almost always correct
- ~33% of FALSE pairs are coverage gaps → model defaults TRUE (wrong)
- TRUE pairs are 100% accurate (no false negatives)
- Stochastic execution errors add ~0-5% noise per run

**Breaking this ceiling requires fundamentally different capabilities:**
1. Teaching finite magma construction in the prompt (risky: adds >2K bytes, high execution error rate)
2. Adding a precomputed lookup table (banned: no Jinja2 logic, no benchmark memorization)
3. Using a more capable model (not in scope for this prompt architecture)
4. Hybrid approach: structural tests catch what they can, then a second-pass algebraic hint for specific failure patterns (v24 direction)

## Comparison to Champion (v21f)

| Metric | v21f | v23c | Delta |
|--------|------|------|-------|
| Bytes | 4,736 | 6,036 | +1,300 |
| Tests | 4 | 4 | same |
| Parse rate | ~87% (noisy) | 100% | **+13%** |
| Normal seed0 | 90% | 90% | tied |
| Normal seed1 | 90% | 85% | -5% |
| Normal seed2 | 90% | 90% | tied |
| FN rate | >0% | **0%** | improved |
| Execution errors | common | rare | improved |

v23c is strictly better on parse robustness and FN elimination but has not clearly beaten v21f on aggregate accuracy due to stochastic variance.

## Recommendation

v23c should replace v23 as the active candidate. It is the best-tested iteration with the strongest evidence base. However, **promotion over v21f as champion is borderline** — it ties on 2/3 seeds and loses on 1/3.

For competition submission: v23c is the safer choice due to 100% parse rate and 0% FN rate.

# V24I Master Prompt — Algebraic Rescue Design

**Date:** 2026-04-03
**Status:** DESIGN COMPLETE — evidence base fully established
**Base:** v23c (6,036 bytes, 93.3% normal, 50% hard3)
**Goal:** Break the 50% hard3 ceiling WITHOUT regressing normal
**Approach:** Radically different — algebraic magma evaluation, not more text-inspection

## 1. WHY v24a–h ALL FAILED ON HARD3

Eight iterations (v24a through v24h) tried adding structural text-inspection tests
(LSUCC, RSUCC, D3, L3) to the v23c base. All produced the same result:

- **Normal: 88–93%** (some regression from cognitive overload)
- **Hard3 FALSE: 0/20** (zero catches in every version)

### Root Cause: Structural Tests Cannot Separate Hard3 FALSE

Automated analysis proves:
- **0/20** hard3 FALSE pairs are separable by LP, RP, C0, VARS, or L3
- All 20 pairs have matching structural profiles: both E1 and E2 produce
  HOLD-HOLD or FAIL-FAIL on every text-inspection test
- The 4 FP errors on normal and 20 FN on hard3 are COVERAGE GAPS,
  not execution errors

### Root Cause: No 2-Element Magma Separates Either

Exhaustive check of all 16 binary operations on {0,1}:
- **0/20** hard3 FALSE pairs are separable by ANY 2-element magma
- XOR, AND, OR, XNOR — none of them help
- The V24 master prompt's Direction A (XOR/XNOR rescue) is a dead end for hard3

## 2. THE BREAKTHROUGH: 3-ELEMENT MAGMA SEPARATION

Exhaustive check of all 19,683 operations on {0,1,2}:
- **15/20** hard3 FALSE pairs are separable by SOME 3-element magma
- **265** magmas have at least 1 catch — **all 265 have 0 FP** on TRUE pairs
- **5/20** pairs require 4+ element magmas (hard3_0073, 0074, 0163, 0166, 0328)

### Greedy Set Cover (0-FP, 3-element magmas)

| Step | Magma Table               | New Catches | Total |
|------|---------------------------|-------------|-------|
| 1    | [[1,2,0],[1,2,0],[1,2,0]] | 0017,0096,0113,0116,0180 | 5/20 |
| 2    | [[0,0,0],[1,1,0],[2,0,2]] | 0128,0151,0153 | 8/20 |
| 3    | [[0,0,0],[2,1,1],[1,2,2]] | 0253,0280 | 10/20 |
| 4    | [[0,1,1],[0,1,2],[0,1,2]] | 0254,0383 | 12/20 |
| 5    | [[1,1,1],[2,2,2],[0,0,0]] | 0218,0301 | 14/20 |
| 6    | [[0,0,0],[0,0,0],[0,1,0]] | 0359 | 15/20 |

### Key Insight: Steps 1 and 5 Are Named Magmas

- **Step 1 = T3R**: a*b = (b+1) mod 3 (right-translation). Catches 5 pairs.
- **Step 5 = T3L**: a*b = (a+1) mod 3 (left-translation). Catches 2 pairs.

These are the ONLY two magmas with clean 1-line evaluation rules.
The other 4 magmas have complex tables that can't be taught to a 70B model.

## 3. THE GUARDED SPOT-CHECK THEOREM

### Problem
Evaluating an equation against a magma requires checking ALL variable assignments
(3^k for k variables). Too expensive for the model.

### Solution
Under T3R (a*b = next(b)):
- If E1 has **RP=HOLD** (last letter matches on both sides), then the equation
  either holds for ALL assignments or fails for ALL assignments.
- Therefore a single spot-check at one assignment is equivalent to the universal check.

**Proof sketch:** Under T3R, eval(expr) = (rightmost_leaf_value + right_spine_depth) mod 3.
When RP=HOLD, both sides share the same rightmost variable, so the equation reduces to
comparing constants. It either always matches or never matches.

### Corollary
**Guarded T3R**: Run T3R spot-check ONLY when E1 RP=HOLD. Then:
- If E1 passes → E1 holds universally → safe to compare with E2
- If E2 fails → valid separation → sound FALSE conclusion
- If E1 fails → E1 fails universally → no separation possible

**Guarded T3L**: Same argument with LP=HOLD instead of RP=HOLD.

### Verified Results (guarded approach)

| Benchmark | Structural Only | + Guarded T3R+T3L | FP |
|-----------|----------------|--------------------|----|
| Normal    | 56/60 = 93.3%  | 56/60 = 93.3%     | 0  |
| Hard3     | 20/40 = 50.0%  | 27/40 = 67.5%     | 0  |

Hard3 FALSE breakdown:
- T3R catches: 0017, 0096, 0113, 0116, 0180 (5 pairs, all E1 RP=HOLD)
- T3L catches: 0218, 0301 (2 pairs, all E1 LP=HOLD)
- Still missed: 13/20 (need complex magmas or 4-element)

## 4. V24I CHEATSHEET DESIGN

### Architecture
1. **Phase 1 — Structural Tests**: LP, RP, C0, VARS (unchanged from v23c)
2. **Phase 2 — Algebraic Rescue**:
   - T3R: guarded by E1 RP=HOLD
   - T3L: guarded by E1 LP=HOLD
3. **Default**: TRUE

### Execution Model for T3R
The model does NOT count depth. Instead it evaluates step by step:
1. Assign variables: first=0, second=1, third=2, fourth=0
2. Find innermost * in expression
3. Compute: result = next(right argument value). Ignore left argument.
4. Replace the innermost * expression with the result number.
5. Repeat until expression reduces to a single number.
6. Compare LHS and RHS.

The "next" function: next(0)=1, next(1)=2, next(2)=0.

For T3L: same but result = next(LEFT argument value). Ignore right argument.

### Byte Budget
- v23c structural core: ~5,200 bytes (tests + examples A-D)
- T3R rescue section: ~650 bytes
- T3L rescue section: ~300 bytes
- Example E (T3R worked): ~550 bytes
- Total estimate: ~6,700 bytes (65% of 10,240 cap)

### Examples
- Examples A–D: unchanged from v23c (LP, RP, C0 separation + TRUE)
- Example E: NEW — FALSE via T3R rescue (hard3_0017 pattern)

## 5. RISK ANALYSIS

### Known Risks
1. **Evaluation errors**: Model incorrectly applies next() or misparses expressions
   - Mitigation: T3R ignores left args → simpler parsing (only trace right branch)
   - Mitigation: next() is a 3-entry lookup → minimal arithmetic
2. **Cognitive bleed**: T3R instructions interfere with structural test execution
   - Mitigation: Rescue section is clearly separated ("run ONLY if...")
   - Mitigation: Rescue fires less often than structural tests
3. **Guard bypass**: Model runs T3R when E1 RP=FAIL → potential false positives
   - Mitigation: Guard is explicitly stated in bold
   - Mitigation: Even if bypassed, FP rate on TRUE pairs is low

### Comparison to v24a–h
| Risk | v24a–h (structural) | v24i (algebraic) |
|------|---------------------|-------------------|
| Cognitive overload | HIGH (5th test collapses) | MODERATE (rescue is separate phase) |
| False positives | 0 (structural tests are sound) | 0 (guarded check is sound) |
| Hard3 improvement | 0/20 across 8 versions | 7/20 (proven) |
| Normal regression | 0–5 pp (v24a: -5pp) | 0 pp (expected) |

## 6. WHAT v24i CANNOT CATCH

The 13 remaining hard3 FALSE pairs fall into:
- **5 pairs needing 4+ element magmas** (0073, 0074, 0163, 0166, 0328):
  Require specific Cayley tables on {0,1,2,3} or larger. Cannot be taught.
- **8 pairs with complex 3-element separators** (0128, 0151, 0153, 0253, 0254, 0280, 0359, 0383):
  Separable by 3-element magmas but the magma rules are too complex to describe simply.

Future directions (v25+):
- Teach additional named 3-element magmas (diminishing returns)
- Add a "complexity heuristic" (e.g., if expression trees differ in shape → FALSE)
- Use few-shot hard3 examples to prime model intuition

## 7. ANTI-PATTERNS CONFIRMED

1. **Do NOT add more text-inspection tests.** 8 iterations (v24a–h) proved structural
   tests CANNOT separate hard3 FALSE. Ever.
2. **Do NOT try 2-element magmas.** All 16 checked, 0/20 catches.
3. **Do NOT use unguarded spot-checks.** 15/30 FP on normal TRUE without RP/LP guard.
4. **Do NOT teach unnamed complex magmas.** Only T3R and T3L have simple rules.
5. **Do NOT ask model to check all assignments.** Use guarded single-point instead.

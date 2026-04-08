# v24j Final Report

Date: 2026-04-07
Champion: `cheatsheets/v24j.txt` (8,955 bytes, 87.4% of 10,240 cap)
Previous champion: `cheatsheets/v21f_structural.txt`
Design lineage: v24a → v24b → v24c → v24d → v24e → v24f → v24g → v24h → v24i → v24j

## Performance Summary

### Current v24j (8,955 bytes)

Normal 60-problem balanced set (rotation0002):

| Run | Accuracy | FP | FN | Parse | F1 | TRUE acc | FALSE acc |
|-----|----------|----|----|-------|-----|----------|-----------|
| 1   | 91.7%    | 4  | 1  | 100%  | 92.1% | 96.7%  | 86.7%     |
| 2   | 90.0%    | 6  | 0  | 100%  | 90.9% | 100.0% | 80.0%     |
| **Mean** | **90.85%** | **5** | **0.5** | **100%** | **91.5%** | **98.35%** | **83.35%** |

Hard3 40-problem balanced set (rotation0002):

| Run | Accuracy | FP | FN | Parse | F1 | TRUE acc | FALSE acc |
|-----|----------|----|----|-------|-----|----------|-----------|
| 1   | 72.5%    | 11 | 0  | 100%  | 78.4% | 100.0% | 45.0%     |
| 2   | 65.0%    | 13 | 1  | 100%  | 73.1% | 95.0%  | 35.0%     |
| **Mean** | **68.75%** | **12** | **0.5** | **100%** | **75.75%** | **97.5%** | **40.0%** |

### Pre-final v24j (8,887 bytes, before Example F addition)

| Benchmark | Accuracy | FP | FN | Parse | F1 | TRUE acc | FALSE acc |
|-----------|----------|----|----|-------|-----|----------|-----------|
| Normal 60 | 93.3%    | 4  | 0  | 100%  | 93.8% | 100.0% | 86.7%     |
| Hard3 40  | 52.5%    | 17 | 2  | 100%  | 65.4% | 90.0%  | 15.0%     |

### Invalidated run (catastrophically golfed 6,690-byte version)

| Benchmark | Accuracy | FP | FN | Parse | Notes |
|-----------|----------|----|----|-------|-------|
| Normal 60 | 66.7%    | 17 | 3  | 96.7% | Golfed version deleted and replaced; excluded from all averages |

## Architecture

v24j uses a two-stage approach:

**Stage 1: Structural tests (LP, RP, C0, VARS)**
Each test extracts a syntactic property from both sides of both equations and checks using the decision table:
- E1=HOLD + E2=FAIL → separation → FALSE
- All other combinations → continue to next test

**Stage 2: T3R algebraic rescue**
Guarded by RP showing E1=HOLD (no separation from all structural tests). Uses the Z3 next-map magma (a*b = next(b)) to algebraically evaluate both equations. If E1 holds but E2 doesn't under this magma → separation → FALSE.

## Math Review

### Structural ceiling theorem
The 4 structural tests (LP, RP, C0, VARS) are sound syntactic invariants. They catch most FALSE cases where E1 preserves a property that E2 violates. However, they cannot distinguish algebraically different equations that share all syntactic properties. The ceiling is ~88-92% on normal sets.

### T3R number-first fix
A critical v24 discovery: LLMs make systematic errors when asked to substitute and evaluate simultaneously. The "rewrite with numbers FIRST, then evaluate" protocol eliminates the #1 T3R execution error class. This is reinforced with worked examples.

### E1 abort guard
T3R must check E1 first. If E1 LHS ≠ E1 RHS under the magma, the magma cannot separate (you need E1 to hold for any counterexample). Early abort prevents false separations.

### Guarded rescue entry
T3R runs only when RP showed E1=HOLD. If RP showed E1=FAIL, the structural backbone already determined no separation is possible from RP, and T3R cannot help — skip to TRUE. This guard prevents unnecessary computation and reduces error surface.

## Skill Review: What Worked

1. **Verbose worked examples**: 6 worked examples (A through F) covering every outcome path. Compression causes catastrophic performance loss.
2. **Explicit decision table**: The 4-row HOLD/FAIL table after every test. Models execute this reliably when it's visually prominent.
3. **Rewrite-with-numbers-first**: Separate substitution from evaluation. Eliminates the dominant T3R error mode.
4. **E1 abort**: Check E1 before E2 in T3R. Prevents false separations.
5. **Plain text format**: No headers, no bullet lists, no LaTeX. Models follow imperative instructions better than structured documents.
6. **Default TRUE bias**: Correct because most implications are true. Reduces FN (the more costly error in competition scoring).

## Learnings: What Doesn't Help

1. **More structural tests**: Additional syntactic tests (variable count, nesting depth, etc.) didn't improve accuracy — the 4-test set covers the syntactic separation space well.
2. **2-element magmas**: Z2 witnesses are too weak. Z3 (T3R) is the minimum useful algebraic size.
3. **Aggressive golfing**: Compressing the cheatsheet from 9,043 to 6,690 bytes caused a 25pp accuracy collapse (66.7% vs 91.7%). Verbosity is load-bearing.
4. **T3L without number-first**: The left-argument analog (a*b=next(a)) was explored but didn't add enough separation power to justify the byte cost.
5. **Additional rescue magmas**: Adding more Z3 magmas (e.g., a*b=next(a), constant maps) increased byte count without proportional hard3 uplift.

## Collapse Avoidance

These are known prompt-engineering constraints for this cheatsheet:

- Never compress worked examples (Examples A–F are all load-bearing)
- Never golf the decision table (the 4-row table must be visually distinct)
- Never remove the "rewrite with numbers FIRST" instruction
- Never remove the E1 abort guard
- Never use markdown headers, numbered lists, or LaTeX notation in the cheatsheet

## Version History

| Version | Bytes | Key change | Normal | Hard3 |
|---------|-------|-----------|--------|-------|
| v24a | ~7,000 | Initial T3R rescue added | ~88% | ~55% |
| v24i | ~8,500 | Refined structural tests + T3R | ~90% | ~60% |
| v24j (pre-F) | 8,887 | T3R number-first fix, E1 abort | 93.3% | 52.5% |
| v24j (final) | 8,955 | Added Example F (harder nested T3R) | 90.85% mean | 68.75% mean |

## v25 Direction

See `V25A_MASTER_PROMPT.md` for the full design document.

Key priorities:
1. Improve hard3 FALSE accuracy (currently 35-45%) without regressing normal safety
2. Remaining byte budget: ~1,285 bytes
3. Candidate approaches: additional witness magmas, pattern-based FALSE heuristics
4. Gate: any v25 candidate must achieve ≥90% normal mean before hard3 testing

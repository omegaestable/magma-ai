# v24 Master Prompt — Design Document

**Date:** 2026-04-03
**Status:** DRAFT — pending v23c massive run results
**Goal:** Break the 90% normal ceiling established by v21f/v23c
**Constraint:** Only `{{equation1}}` and `{{equation2}}` substitution. NO Jinja2 logic. Max 10,240 bytes.

## 1. WHY v23 CAPS AT ~90%

The v23 family uses 4 text-inspection tests (LP, RP, C0, VARS) to detect structural separation between equations. These tests cover ~67% of FALSE pairs on normal benchmark sets. The remaining ~33% are **coverage gaps** — FALSE pairs where no text-inspection test produces E1=HOLD + E2=FAIL.

Coverage gaps require algebraic reasoning:
- Constructing a finite magma (e.g., 2- or 3-element Cayley table) satisfying E1 but not E2
- Evaluating whether a substitution breaks E2 under E1's structure
- Recognizing identity/idempotent/commutative patterns that create separation

The model (llama-3.3-70b-instruct) cannot reliably perform these computations when:
- The prompt already contains 6K+ bytes of structural test instructions
- Temperature > 0 introduces stochastic reasoning errors
- The output contract requires strict formatting

## 2. WHAT v24 SHOULD TRY

### Direction A: Lightweight Algebraic Hints (RECOMMENDED)

After the 4 structural tests complete with no separation, add a **focused second pass** that teaches the model to check 2-3 specific algebraic patterns known to catch the most common coverage gaps.

**Pattern 1 — Idempotent Test (x◇x = x):**
Many coverage gaps involve idempotent magmas. If E1 is consistent with all idempotent magmas but E2 is not, that's separation.
- Check: substitute x◇x → x everywhere in both equations. Does E1 reduce to a tautology? Does E2 become a contradiction?
- This catches ~15% of remaining coverage gaps based on packed pair analysis.

**Pattern 2 — Constant Magma (x◇y = c for all x,y):**
If E1 holds in all constant magmas but E2 does not, that's separation.
- Check: replace every `a * b` with a fixed constant `c`. Does E1 become `c = c`? Does E2?
- This catches ~8% of remaining coverage gaps.

**Pattern 3 — Left/Right Projection (x◇y = x or x◇y = y):**
- Check: replace every `a * b` with `a` (left projection). Does E1 hold? Does E2?
- Then replace every `a * b` with `b` (right projection). Same check.
- This catches ~12% of remaining coverage gaps.

**Risk:** Each algebraic hint adds ~500-800 bytes and requires the model to do symbolic substitution, which has ~70% accuracy on llama-3.3-70b. Net benefit depends on whether the extra coverage outweighs new execution errors.

**Mitigation:** Teach ONE algebraic hint at a time, measure impact, then decide whether to add more.

### Direction B: Example-Heavy Approach (ALTERNATIVE)

Instead of teaching algebraic reasoning, provide 8-10 worked examples covering different failure modes:
- 4 structural separation examples (current: LP, RP, C0, VARS)
- 4 coverage-gap examples showing TRUE verdicts where tests miss

**Risk:** More examples = more bytes = less room for instructions. Model may pattern-match examples instead of reasoning.

### Direction C: Two-Phase Prompt (EXPERIMENTAL)

Split the prompt into two phases:
1. Phase 1: Structural tests (current approach) → if separation found, answer FALSE
2. Phase 2: If no separation, perform a "sanity check" by trying one specific algebra

**Risk:** The model may not reliably transition between phases. The output contract may be harder to enforce across phases.

## 3. EVIDENCE BASE FOR v24

### Packed Pair Cache Analysis

The 250 cached proof pages provide ground truth for which algebraic constructions prove separation:
- **156 rewrite_metatheorem** pairs: separation via rewriting rules (currently uncatchable by text inspection)
- **88 subgraph_seed** pairs: separation via finite magma construction
- **5 exceptional_hard** pairs: require specialized constructions
- **1 automated_reasoner** pair: found by automated search

### Most Common Coverage Gap Patterns

From manual analysis of 34 unique coverage-gap failures across benchmark rotations:

1. **Both equations have same LP, RP, C0, VARS profile** but differ in nesting depth or term structure
2. **E1 is a "wider" equation** (more variables, deeper nesting) that E2's structure cannot replicate
3. **E2 introduces fresh variables** not in E1 — but VARS test only catches this when one side is bare

### Key Measurements Needed for v24

1. Accuracy of llama-3.3-70b on idempotent substitution (can it reliably substitute x*x→x?)
2. Accuracy on constant-magma check (can it reliably replace all `a*b` with `c`?)
3. Byte cost of each algebraic hint (must stay under ~4,200 bytes total to fit cap)
4. Net accuracy impact: does new coverage > new execution errors?

## 4. RECOMMENDED v24 DEVELOPMENT PLAN

### Phase 1: Idempotent Hint Pilot
1. Add a single algebraic hint (idempotent test) to v23c
2. Test on warmup seeds
3. Measure: new correct answers vs new execution errors
4. If net positive → keep, else → revert

### Phase 2: Coverage Expansion
1. If Phase 1 succeeds, add constant-magma hint
2. Same test loop
3. Byte budget discipline: each addition must fit under 10,240

### Phase 3: Gate Loop
1. Full 3-seed normal gate (must beat 90%)
2. If gate passes → hard3 stress test
3. If gate fails → trim last addition, try alternative

### Exit Criteria
- v24 consistently scores ≥92% on normal sets (2+ percentage points above v23c ceiling)
- No normal seed below 88%
- Parse rate remains at 100%
- FN rate remains at 0%

## 5. FILES AND ARTIFACTS

### Starting Point
- `cheatsheets/v23c.txt` — the best v23 iteration (6,036 bytes)
- `data/teorth_cache/pair_cache_packed.jsonl` — 250 cached proof constructions
- `results/v23c_final_report.md` — complete evaluation evidence

### Analysis Tools
- `v21_verify_structural_rules.py` — structural test implementations (rule_LP, rule_RP, rule_C0, rule_AND)
- `analyze_seed_failures.py` — failure categorization
- `distill.py` — failure → cheatsheet-edit suggestions

### Evaluation
- `sim_lab.py --playground-parity` — canonical evaluator
- `run_paid_eval.ps1` — quick wrapper

## 6. ANTI-PATTERNS TO AVOID

1. **Do NOT add more text-inspection tests.** XOR, XNOR, Z3A all have negative ROI due to execution errors.
2. **Do NOT add >2 algebraic hints at once.** Cognitive overload causes format collapse.
3. **Do NOT add long worked examples for algebraic hints.** Keep examples to ≤3 lines each.
4. **Do NOT decrease structural test coverage.** The 4-test backbone is the foundation.
5. **Do NOT change the output contract.** VERDICT/REASONING/PROOF/COUNTEREXAMPLE format is battle-tested.
6. **Do NOT use ## headers, numbered steps, or \boxed{} in examples.** These trigger format collapse.

# Failures

Every cheatsheet version that failed to match champion performance (95% normal + 75% hard3), organized by failure mode.

---

## FAILURE MODE 1: TOO SIMPLE — Insufficient Tests

### magma_eval_test (3,953 bytes) — Pure Magma, No Structure
- Normal: 87.5% (N=8, Llama)
- **Failure**: Only one test (single 3-element magma). No structural pre-screening. Many FALSE pairs that structural tests catch trivially (LP, RP, C0) required full magma evaluation — wasting model effort and missing cases where the magma doesn't separate.
- **Lesson**: Structural tests are not optional. They're the backbone.

### v21f_structural (4,736 bytes) — Structure Only, No Algebra
- No paid eval results recorded.
- **Failure**: 4 structural tests (LP, RP, C0, VARS) but no algebraic rescue. Hard FALSE pairs that pass all structural tests have no fallback.
- **Lesson**: Structure alone caps at ~90% normal. Need algebraic rescue for the remaining 10%.

---

## FAILURE MODE 2: WRONG TESTS — Added Tests That Hurt

### v23a (7,175 bytes) — XOR Parity Test Added
- Normal: 70.0% (N=10, Llama) ← massive regression from v23's 93%
- **Failure**: Added a variable occurrence parity (XOR) test. The model miscomputed parity counts, generating false separations on TRUE pairs. Also added FORMAT RULES banning model improvisation — over-constraining.
- **Lesson**: Parity/counting tests are high-risk for model execution errors. If the model can't reliably compute the test, it's worse than not having it.

### v24a (8,548 bytes) — LSUCC + RSUCC Depth Tests
- Normal: 88.3% (N=60, Llama) — below champion's 93%
- **Failure**: Added LSUCC (left-depth mod 3) and RSUCC (right-depth mod 3). Two new depth tests confused the model — too many tests to track, and depth mod 3 is harder than depth mod 2.
- **Lesson**: More tests ≠ better accuracy. Each test must justify its cost in model attention and error risk.

### v24b (6,604 bytes) — RSUCC Only
- Normal: 91.7% (N=60, Llama) — close but no cigar
- Hard3: 42.5% (N=40) — terrible
- **Failure**: Kept RSUCC, dropped LSUCC. RSUCC alone didn't help hard3 at all. Still no algebraic rescue.
- **Lesson**: Depth-mod-3 structural tests are marginal. The real bottleneck is algebraic rescue coverage.

### v24c–v24f (7,271–7,551 bytes) — D3/L3 Depth Experiments
- Normal: 88–92% range — unstable
- No hard3 data for most
- **Failure**: Swapped between D3 (trailing-paren depth mod 3), L3 (leading-paren depth mod 3), and back. Musical chairs with marginal tests. Never found the sweet spot.
- **Lesson**: Iterating on marginal structural tests has diminishing returns. Should have pivoted to algebraic rescue sooner.

---

## FAILURE MODE 3: OVERFIT SIMPLIFICATION — Good Core But Missing Pieces

### v23 (4,977 bytes) — Solid Structural Foundation
- Normal: 93.3% (N=60, Llama) — good
- Hard3: 50.0% (N=20–40) — FAcc=0%
- **Failure**: 4 structural tests work great for normal, but hard3 FALSE pairs pass all structural tests. Zero FALSE accuracy on hard3 = coinflip.
- **Lesson**: This IS the structural ceiling. ~93% normal, ~50% hard3. Algebraic rescue is mandatory to break through.

### v23b (5,781 bytes) — Tightened v23
- Normal: 90.0% (N=20, Llama)
- **Failure**: Simplified wording of v23 but didn't add any new capability. Trading wording clarity for no new power.
- **Lesson**: Wording refinement alone doesn't move the needle. Need new tests.

### v23c (6,036 bytes) — Multi-Model v23
- Normal: 93.3% (N=60, all 3 models) — strong
- Hard3: 50.0% (N=40–60) — same ceiling as v23
- **Failure**: Proved the structural ceiling is model-independent. All 3 models hit the same 93%/50% wall.
- **Lesson**: The ceiling is mathematical, not model-dependent. Must add algebraic capability.

### v24g (7,271 bytes) — Reverted to VARS
- Normal: 91.7% (N=60, Llama)
- **Failure**: Dropped depth tests, went back to LP/RP/C0/VARS. Marginally worse than v23c's 93.3% despite more bytes. No algebraic rescue.
- **Lesson**: Going backward doesn't help. Need to go forward with algebra.

### v24h (6,182 bytes) — L3 Gated on LP
- Normal: 91.7% (N=60, Llama)
- Hard3: 50.0% (N=40) — same structural ceiling
- **Failure**: Gated L3 on LP=HOLD — a good idea in theory, but L3 itself is too marginal to matter.
- **Lesson**: Gating is good practice, but gating a weak test is still weak.

---

## FAILURE MODE 4: NEAR-MISS — Almost Champion

### v24i (8,984 bytes) — First Structural+Algebraic Hybrid
- Normal: 91.7% (N=60, Llama)
- Hard3: 62.5% (N=40, Llama) — breakthrough!
- **Failure**: Had T3R + T3L rescue but T3R instructions weren't clear enough. Models made execution errors on the magma evaluation. 91.7% normal is below champion threshold.
- **Lesson**: T3R/T3L is the right idea. Execution clarity is the bottleneck. v24j fixed this.

### v26a (10,146 bytes) — Spine Depth Added
- Normal: 95.0% (N=20, GPT-OSS) — champion level!
- Hard3: 70.0% (N=30, GPT-OSS) — close but 5pp short
- **Failure**: Spine Depth Check was the right addition but T3L was too terse (4 lines). Models couldn't execute T3L reliably. Only 511 bytes from cap — barely any room to fix T3L.
- **Lesson**: Being too big is a liability. v26b fixed T3L within the remaining space.

---

## FAILURE MODE 5: KITCHEN SINK — Too Many Tests Cause Collapse

### v25a (10,078 bytes) — Right-Spine Shortcut
- Normal: 75.0% (N=20, Llama) ← catastrophic regression
- **Failure**: Added a right-spine shortcut optimization for T3R. The shortcut was mathematically correct but the model couldn't follow the multi-step spine-walking procedure. Also >10KB, fighting the byte cap.
- **Lesson**: Mathematical correctness ≠ model executability. Simpler step-by-step beats clever shortcuts.

### v25b (9,654 bytes) — Removed Shortcut
- Normal: 85.0% (N=20, Llama) — still below champion
- Hard3: 40.0% (N=20) — terrible, and TRUE pairs flagged too (TAcc=20%!)
- **Failure**: Removed spine shortcut but the whole T3R/T3L section was still confusing. TRUE accuracy collapsed to 20% on hard3 — the model was running T3L on TRUE pairs and getting wrong answers.
- **Lesson**: T3L without a clear gate (LP=HOLD requirement) is dangerous. Ungated rescue tests destroy TRUE accuracy.

### v26c (9,375 bytes) — COUNT2 + LDEPTH + MA1 + MA2
- Normal: 92.0% (N=50, GPT-OSS)
- Hard3: 46.0% (N=50) — worse than v26b despite more tests!
- **Failure**: Added COUNT2, LDEPTH structural tests and MA1, MA2 magma rescues (4 new tests total). Too many tests → model loses track of the decision flow → execution errors multiply.
- **Lesson**: 6+ tests is too many. The model's attention budget is finite. Each additional test steals attention from the core tests that work.

### v26d (10,042 bytes) — M3A + M3B Different Magmas
- Normal: 92.0% (N=50, GPT-OSS) — but 76.7% on N=60 set!
- Hard3: 68.0% (N=50) — decent but unstable
- **Failure**: Tried different 3-element magma tables (M3A, M3B) instead of T3R/T3L. These magmas are lookup-table based — the model has to memorize a 3×3 table and do multi-step lookups. Error-prone. Normal instability (76–92%) is a red flag.
- **Lesson**: Named algebraic rules (next(b), next(a)) are easier for models than arbitrary lookup tables.

### v26e (9,902 bytes) — Lean Rollback
- Normal: 90.0% (N=60, GPT-OSS) — below champion
- Hard2: 56.7% (N=60)
- **Failure**: Stripped back to v26b-era tests. Slightly worse than v26b due to wording differences. Not a regression exactly — just didn't improve.
- **Lesson**: Rollback to a known-good point is valid strategy, but you need to match the exact wording that works.

### v26f (9,686 bytes) — XOR + T4A + T5B Checkpoint
- Normal: 80.0% (N=40, GPT-OSS) ← major regression
- Hard3: 70.0% (N=20) — decent
- Hard2: 23–40% (N=20–30) — terrible
- **Failure**: Added 3 ungated magma checkpoint tests (XOR 2-element, T4A 4-element, T5B 5-element) as a "safety net before saying TRUE." The model runs these on TRUE pairs and computes them incorrectly → false separations → TRUE accuracy collapses.
- **Lesson**: Ungated algebraic tests on 4–5 element magmas are too hard for models to execute. Even mathematically sound tests cause regression if the model can't compute them reliably.

---

## FAILURE MODE 6: CATASTROPHIC REGRESSION — v27 Line

### v27a (10,161 bytes) — v26b + XOR/T4A/T5B
- Normal: **67.5%** (N=40, GPT-OSS) ← worst champion-era version
- TAcc: **45.0%** ← model says FALSE on more than half of TRUE pairs!
- FAcc: 90.0%
- Hard3: running, already showing regression
- **Also**: 10,399 bytes when equations substituted → **EXCEEDS 10KB CAP** on hard3!
- **Failure**: Combined v26b's solid core with v26f's failed XOR/T4A/T5B tests. Same failure mode as v26f but worse because the base is larger. The "No gate. Always run" instruction means XOR/T4A/T5B execute on every TRUE pair → model botches multi-element arithmetic → FALSE on TRUE pairs.
- **Lesson**: This is the ultimate proof that ungated multi-element magma tests destroy performance. They're mathematically sound (0 false flags in our Python evaluator) but the model can't compute them. The gap between mathematical soundness and model executability is the central failure mode of this project.

### v27b (10,126 bytes) — v27a minus T5B
- No eval results yet.
- **Failure**: Dropped T5B but kept XOR + T4A. Likely the same problems as v27a/v26f, just slightly less severe.
- **Lesson**: Removing the worst test isn't enough. The architecture (ungated multi-element magmas) is the problem, not any single test.

---

## Summary Scoreboard

| Version | Bytes | Normal% | Hard3% | Verdict | Failure Mode |
|---------|------:|--------:|-------:|---------|-------------|
| magma_eval_test | 3,953 | 87.5 | — | FAIL | Too simple |
| v21f | 4,736 | — | — | FAIL | No algebra |
| v23 | 4,977 | 93.3 | 50.0 | FAIL | Structural ceiling |
| v23a | 7,175 | 70.0 | — | FAIL | XOR hurt |
| v23b | 5,781 | 90.0 | — | FAIL | No new capability |
| v23c | 6,036 | 93.3 | 50.0 | FAIL | Structural ceiling |
| v24a | 8,548 | 88.3 | — | FAIL | Too many depth tests |
| v24b | 6,604 | 91.7 | 42.5 | FAIL | RSUCC marginal |
| v24c | 7,536 | 91.7 | — | FAIL | D3 marginal |
| v24d | 7,536 | 88.3 | — | FAIL | D3 marginal |
| v24e | 7,551 | 90.0 | — | FAIL | L3 marginal |
| v24f | 7,420 | 90.0 | — | FAIL | L3 marginal |
| v24g | 7,271 | 91.7 | — | FAIL | Backward step |
| v24h | 6,182 | 91.7 | 50.0 | FAIL | Structural ceiling |
| v24i | 8,984 | 91.7 | 62.5 | FAIL | Near-miss, T3R unclear |
| v25a | 10,078 | 75.0 | — | FAIL | Spine shortcut collapse |
| v25b | 9,654 | 85.0 | 40.0 | FAIL | Ungated T3L danger |
| v26a | 10,146 | 95.0 | 70.0 | FAIL | T3L too terse |
| v26c | 9,375 | 92.0 | 46.0 | FAIL | Kitchen sink |
| v26d | 10,042 | 92.0 | 68.0 | FAIL | Lookup table confusion |
| v26e | 9,902 | 90.0 | — | FAIL | Rollback imprecise |
| v26f | 9,686 | 80.0 | 70.0 | FAIL | Ungated multi-elem magmas |
| v27a | 10,161 | 67.5 | — | FAIL | Catastrophic ungated magmas |
| v27b | 10,126 | — | — | FAIL | Same architecture as v27a |

---

## Synthesized Learnings

### What Works

1. **4 structural tests (LP, RP, C0, VARS)**: The unbreakable core. Models compute these nearly perfectly. They catch ~65% of FALSE pairs and never flag TRUE pairs. Never remove or weaken these.

2. **Default TRUE bias**: The cheatsheet says "answer TRUE unless a test proves FALSE." This protects TRUE accuracy. Every version that maintained this had ≥90% TAcc on normal.

3. **Gated rescues on RP/LP HOLD**: "Run T3R only if RP showed E1=HOLD" prevents the model from wasting effort and making errors on inapplicable cases.

4. **Simple named operations over lookup tables**: `next(b)` (cyclic shift) is trivially executable. A 3×3 lookup table like `[[1,0,0],[2,1,2],[1,2,0]]` causes errors. Named rules win.

5. **Step-by-step rewrite before evaluation**: "Replace every variable with its number. Work ONLY with numbers from here on." This explicit rewrite step in T3R/T3L eliminates variable-tracking errors during nested evaluation.

6. **Decision table repetition**: Drilling the 4-row HOLD/FAIL table into the prompt prevents the #1 model error: confusing "E1=FAIL,E2=HOLD" (no separation) with "E1=HOLD,E2=FAIL" (separation).

7. **Worked examples**: Each example demonstrates one specific test catching a FALSE pair, or all tests passing for a TRUE pair. Models learn the decision flow from examples.

8. **Spine Depth Check**: A zero-execution-risk test (just count opening parens) that catches left-spine idempotent power FALSE pairs. Free accuracy at zero model-error cost.

### What Doesn't Work

1. **Ungated algebraic tests**: Running XOR/T4A/T5B on ALL pairs regardless of structural results causes the model to incorrectly "find" separation on TRUE pairs. This is the #1 killer. v23a, v25b, v26f, v27a all died from this.

2. **Multi-element magmas (4+ elements)**: The model cannot reliably compute modular arithmetic on 4 or 5 elements. `(2a - b) mod 5` sounds simple but models make off-by-one, sign, and mod errors routinely. Even XOR (`(a+b) mod 2`) fails when the variable-to-number assignment wraps (`var2→0, var3→1`).

3. **More than 6 structural tests**: v26c tried 6 structural + 4 algebraic = 10 tests. The model lost track of the flow. Attention is finite — each test steals from the others.

4. **Clever shortcuts**: v25a's right-spine shortcut was mathematically equivalent to step-by-step evaluation but the model couldn't follow it. Verbose but simple > terse but clever.

5. **Lookup tables**: Arbitrary 3×3 tables (M3A, M3B, MA1, MA2) are harder to execute than `next(b)` even though they're the same size magma. The named rule is mnemonic; the table is memory.

6. **Approaching the byte cap**: Every version >10KB had trouble. v27a at 10,161 bytes exceeded the cap when equations were substituted. The effective byte budget is ~9,800 bytes after accounting for equation substitution overhead.

7. **Wording-only iterations**: v23→v23b→v23c, v24c→v24d→v24e all shuffled wording without adding capability. The returns are 0–2pp. Real gains come from new mathematically-grounded tests.

8. **Depth mod 3 tests (LSUCC, RSUCC, D3, L3)**: Four versions tried various depth tests. None reliably improved over the basic 4 structural tests. The signal is too weak and the execution too error-prone.

### The Central Tradeoff

**Mathematical soundness vs. model executability.** Our XOR/T4A/T5B tests have 0 false flags on 999 TRUE pairs when computed by Python. But the model computes them wrong ~30% of the time, generating false separations that tank TRUE accuracy.

The champion architecture (v24j/v26b) stays in the zone where model executability is high:
- Structural tests: near-0% error rate
- T3R/T3L (3-element, named rule): ~5% error rate
- Spine Depth (pure counting): ~0% error rate

The failed architectures push into:
- XOR (2-element, wrap assignment): ~15% error rate
- T4A (4-element): ~25% error rate
- T5B (5-element): ~35% error rate

**The accuracy ceiling of the champion architecture is ~95% normal, ~75% hard3.** Breaking through requires either better model execution or finding tests that are both powerful AND simple enough for the model.

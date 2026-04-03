# v23 Plan — Historical Planning Document

This file preserves the original v23 planning document.

It is not the operational source of truth anymore.

Use `CURRENT_STATE.md` for the live baseline, candidate, latest gate results, and next decision point.

## How To Read This File

1. Read this file as planning history, not live status.
2. Treat the sections below as the original design intent for v23.
3. When this file and `CURRENT_STATE.md` disagree, `CURRENT_STATE.md` wins.

## Status Snapshot (As Of 2026-04-03)

- Baseline champion remains `cheatsheets/v21f_structural.txt`
- Active candidate remains `cheatsheets/v23.txt`
- v23 has not been promoted
- Current working v23 direction is a 4-structural-test natural-language variant with stronger output discipline
- Full normal seed2 still needs confirmation before promotion can even be considered

## Outcome Versus Original Plan

The original v23 plan below aimed for a richer natural-language cheatsheet with XOR/Z3A counting tests and optional soft heuristics.

What actually happened:

1. The counting-heavy direction proved execution-risky on the target model.
2. XOR/Z3A style additions created miscounting regressions and prompt brittleness.
3. The safer live direction returned to the proven 4-test structural lane with clearer decision-table and output-contract wording.
4. The repo now treats v23 as an iterative candidate built on the simpler structural core, not as a commitment to the original 6-test plan.

What remains useful from this document:

1. The diagnosis of why v21f caps near 90%
2. The byte-budget reasoning
3. The discussion of deep coverage gaps and structural ceilings
4. The risk register for overly clever prompt additions

**Created:** 2026-04-02  
**Deadline:** 2026-04-20 (18 days)  
**Constraint:** Only `{{equation1}}` and `{{equation2}}` substitution. NO Jinja2 logic.  
**Baseline:** v21f_structural.txt — 4,736 bytes, 4 tests, ~90% normal, ~85% random seeds  
**Budget:** 10,240 bytes total → 5,504 bytes headroom over v21f

---

## 1. DIAGNOSIS — Why v21f Caps at ~90%

| Error type | Count (per 20) | Root cause | Fix path |
|---|---|---|---|
| **FP (predicts TRUE, answer FALSE)** | 2–3 | No structural separator exists → default TRUE fires | More tests, better default heuristics |
| **FN (predicts FALSE, answer TRUE)** | 0 | Rules are sound, never false-separate | N/A — no regression risk |

The ~10% error floor is 100% false positives: FALSE pairs where LP/RP/C0/VARS all find no separation, so the LLM defaults TRUE. Zero false negatives — the existing tests never fire incorrectly.

### Coverage gaps by layer

| Layer | FALSE pairs covered | Cumulative % | Headroom used |
|---|---|---|---|
| LP + RP + C0 + VARS (v21f) | 132/173 | 76.3% | 0 bytes (baseline) |
| + XOR (mod 2 parity) | +8 | 80.9% | ~400 bytes |
| + Z3A (mod 3 parity) | +4 | 83.2% | ~400 bytes |
| + STAR_PARITY (star count mod 2) | +0 (XNOR subsumes) | 83.2% | — |
| 8 structural total | 144/173 | 83.2% | ~800 bytes total |
| + 11 witness brute-force | +6 | 86.7% | impractical for NL |
| **Deep gap (no method)** | 23 pairs | — | unsolvable structurally |

---

## 2. STRATEGY — Three Lanes

### Lane 1: More structural tests (NL-teachable, sound, deterministic)

Add **XOR** and **Z3A** to the existing 4 tests. Both are provably sound (verified against full 4694×4694 matrix). 

**XOR rule (mod 2 parity):** For each variable, count how many times it appears on LHS and RHS separately. If count_LHS ≡ count_RHS (mod 2) for all variables → HOLD. If any variable has mismatched parity → FAIL.

**Z3A rule (mod 3 parity):** Same but mod 3.

**Risk:** LLMs miscount variables at ~30% rate in complex expressions. The v22 passdown explicitly notes "XOR test extensively tried and rejected: LLM miscounts variables at 1024 tokens." Mitigation: 
- Extremely explicit step-by-step counting instructions
- Tell LLM to list each variable occurrence, then count
- Worked examples showing the counting

**Expected gain:** +12 FALSE pairs covered (132→144), or about +7% on normal.

**Byte cost:** ~800 bytes for both rules + instructions + examples.

### Lane 2: Lightweight heuristic cues (non-deterministic, probabilistic)

Paper-backed soft signals that the LLM can use for "tiebreaker" when structural tests don't separate:

1. **Fresh variable in E2 not in E1**: If E2 contains a variable that never appears in E1, the implication E1→E2 is harder but NOT automatically FALSE (universally quantified vars). Do NOT use as a hard FALSE rule (v19 showed 62% misfire rate).

2. **Star count / depth asymmetry**: Large asymmetry in operator count or nesting depth between E1 and E2 correlates with FALSE (~70% precision). Can serve as a soft "lean FALSE" cue when no structural test fires.

3. **Shape symmetry**: If both equations have identical parse tree shape (ignoring variable names), lean TRUE strongly.

**Risk:** These are probabilistic. They can cause false negatives (wrongly saying FALSE on TRUE pairs). Must be framed as soft hints, not hard rules.

**Expected gain:** Hard to quantify. Maybe +2–5% on the deep gap pairs.

**Byte cost:** ~500–800 bytes.

### Lane 3: Improved TRUE defense (reduce FN from new tests)

v21f has zero false negatives because its default is TRUE and its tests are sound. Adding XOR/Z3A preserves soundness (verified). But adding soft heuristics (Lane 2) could introduce FNs. Need:

- Strong framing: "Only the structural tests (LP/RP/C0/VARS/XOR/Z3A) can prove FALSE. If none fires, default TRUE."
- Soft signals can override default only with explicit reasoning.
- Keep the "HARD RULE: verdict must match analysis" instruction.

---

## 3. BYTE BUDGET

```
SECTION                              BYTES    NOTES
─────────────────────────────────────────────────────────
Header + task definition              150     E1/E2 placeholders, task statement
Quick TRUE shortcut                    80     "x = T where x not in T → TRUE"
Step 0: split on =                    200     Extract 4 pieces
6 structural tests (LP,RP,C0,VARS,   1,200   Each ~200 bytes with instructions
  XOR,Z3A)
Decision table                        300     Same as v21f
Soft heuristic cues                   500     Star count, depth, fresh vars
Output format                         300     VERDICT/REASONING/PROOF/COUNTEREXAMPLE
Hard rules / reminders                300     "verdict must match analysis"
Worked Example A (FALSE via C0)       400     Kept from v21f
Worked Example B (FALSE via LP)       300     Kept from v21f
Worked Example C (TRUE, no sep)       400     Kept from v21f
Worked Example D (FALSE via XOR)      400     NEW — demonstrate counting
Worked Example E (FALSE via Z3A)      400     NEW — demonstrate mod 3
═════════════════════════════════════════════════════════
ESTIMATED TOTAL                     ~5,030    49% of 10,240 limit
REMAINING HEADROOM                  ~5,210    For iteration, more examples, tuning
```

This is conservative. We have massive headroom for:
- More worked examples targeting common LLM mistakes
- Additional anti-hallucination guardrails
- A "common traps" section

---

## 4. IMPLEMENTATION PLAN

### Phase 1: Build v23 cheatsheet with 6 tests (Day 1–2)

1. **Start from v21f_structural.txt** as literal base
2. **Add TEST 5 — XOR** with explicit counting instructions:
   - "List every letter (variable) in LHS. Count each."
   - "List every letter in RHS. Count each."
   - "For each variable: if LHS_count is even and RHS_count is odd (or vice versa) → FAIL."
   - "All matching → HOLD."
3. **Add TEST 6 — Z3A** with mod 3 counting instructions:
   - Same structure but "divide count by 3 and check remainder"
4. **Add worked examples D (XOR) and E (Z3A)** using real benchmark pairs
5. **Add soft heuristic section** (star count asymmetry, depth mismatch)
6. **Measure bytes** — target ≤8,000 to leave iteration room

### Phase 2: Local eval gate (Day 2–3)

**Gate sequence (from v22 passdown):**

```powershell
# Warmup (must pass both ≥90%):
python sim_lab.py --data data/benchmark/normal_balanced10_true5_false5_seed0.jsonl --cheatsheet cheatsheets/v23.txt --openrouter --model meta-llama/llama-3.3-70b-instruct --playground-parity --errors
python sim_lab.py --data data/benchmark/normal_balanced10_true5_false5_seed1.jsonl --cheatsheet cheatsheets/v23.txt --openrouter --model meta-llama/llama-3.3-70b-instruct --playground-parity --errors

# Full eval (need 2/3 ≥90%, all ≥70%):
python sim_lab.py --data data/benchmark/normal_balanced20_true10_false10_seed0.jsonl --cheatsheet cheatsheets/v23.txt --openrouter --model meta-llama/llama-3.3-70b-instruct --playground-parity --errors
python sim_lab.py --data data/benchmark/normal_balanced20_true10_false10_seed1.jsonl --cheatsheet cheatsheets/v23.txt --openrouter --model meta-llama/llama-3.3-70b-instruct --playground-parity --errors
python sim_lab.py --data data/benchmark/normal_balanced20_true10_false10_seed2.jsonl --cheatsheet cheatsheets/v23.txt --openrouter --model meta-llama/llama-3.3-70b-instruct --playground-parity --errors
```

**Success criteria:**
- No regression on TRUE pairs (zero false negatives)
- Improvement on FALSE pairs (fewer false positives)
- Target: ≥95% on normal balanced seeds

### Phase 3: Error distillation loop (Day 3–5)

For each failure from Phase 2:
1. Classify as execution error (LLM miscounted) vs coverage gap (no test covers it)
2. For execution errors → refine counting instructions, add worked examples
3. For coverage gaps → check if a new heuristic could help
4. Re-run eval. Iterate until stable.

### Phase 4: Cross-model testing (Day 5–7)

Test on at least 2 models:
- `meta-llama/llama-3.3-70b-instruct` (primary)
- `google/gemini-2.0-flash-001` (if available via OpenRouter)
- `qwen/qwen-2.5-72b-instruct` (if available)

Cheatsheet must be robust across models. Key concern: smaller models may struggle more with counting. If counting rules cause regressions on other models, consider dropping XOR/Z3A for those models and submitting the simpler 4-test version.

### Phase 5: Stress test + submission (Day 7–10)

- Unseen normal 60 (30T/30F from `make_unseen_30_30_sets.py`)
- Hard3 stress (26 hard pairs)
- Random seed sweep (3 random seeds)
- Competition playground test on SAIR website

---

## 5. RISKS AND MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM miscounts variables for XOR/Z3A | HIGH (30%) | Regression from new FNs | Explicit step-by-step, worked examples, fallback to 4-test if worse |
| Soft heuristics cause FNs | MEDIUM | Lose TRUE accuracy | Frame as soft cues only, never override structural separation |
| Cross-model instability | MEDIUM | Works on Llama, fails on Gemini | Test early, keep simpler fallback version |
| Deep gap pairs (~13% of FALSE) unfixable | HIGH | Cannot reach 100% on normal | Accept ceiling, optimize safe-side accuracy |
| Competition eval has different equation distribution | LOW | Wasted optimization | All tests are globally sound — they generalize to any 4694-pool pair |

---

## 6. THEORETICAL ACCURACY CEILING

| Scenario | Expected accuracy |
|---|---|
| **v21f baseline (4 tests)** | ~90% normal seeded, ~85% random |
| **v23 with 6 tests, perfect LLM execution** | ~95% (144/173 FALSE covered + all TRUE correct) |
| **v23 with 6 tests + soft heuristics** | ~93–97% (some soft heuristic wins, some FN losses) |
| **v23 with XOR/Z3A counting errors** | ~88–93% (FN risk from miscounts offsets FALSE coverage gain) |
| **Absolute ceiling (all 11 witnesses)** | ~93% (150/173 FALSE + all TRUE) |

The **23 deep gap pairs (13.3% of FALSE)** are unsolvable by any known structural/witness method in our toolkit. They require algebraic proof or larger magma search (>4 elements). At 50/50 TRUE/FALSE balance, these represent ~6.7% of total problems — setting a hard floor of ~93% maximum accuracy.

---

## 7. ALTERNATIVE APPROACHES CONSIDERED AND REJECTED

### A: Equation ID lookup table
- Embed a mapping from equation text → 0-based ID, then a sparse lookup table
- **Rejected:** Fragile (depends on exact text matching across models), and the v23 Jinja2 gap table failure proved that precomputed answers are dangerous — one wrong entry = one wrong answer with no LLM reasoning to catch it.

### B: Teach the LLM to evaluate small magma tables
- Give the LLM a 2×2 magma table and teach it to check if equations hold
- **Rejected:** Requires arithmetic (0*1=?, table lookup). v22 passdown showed LLMs make ~30% arithmetic errors. Worse than counting.

### C: Equivalence class encoding
- Encode which equations are equivalent and use that to infer TRUE
- **Rejected:** 1,415 classes × text identifiers = too many bytes, and the LLM can't reliably match equation text to class membership.

### D: CNN feature extraction in language
- Describe the CNN's character-level features and teach the LLM to extract them
- **Rejected:** The CNN's power comes from learned convolution filters, not human-describable rules. The structural tests already capture the extractable features.

### E: Full default-FALSE strategy
- Flip default to FALSE (since 62.88% of all pairs are FALSE)
- **Rejected:** Competition eval is 50/50 balanced. Default FALSE would give 50% on TRUE → ~75% total at best. Default TRUE with sound FALSE tests is strictly better.

---

## 8. KEY FILES REFERENCE

| File | Role |
|---|---|
| `cheatsheets/v21f_structural.txt` | v23 starting point (4,736 bytes, 4 tests) |
| `sim_lab.py` | Eval harness — `--playground-parity --openrouter --errors` |
| `v21_verify_structural_rules.py` | Rule soundness verification (8 rules all verified) |
| `v22_coverage_analysis.py` | Coverage gap analysis |
| `v22_mine_sound_rules.py` | Sound rule mining (13 rules tested) |
| `distill.py` | Error taxonomy from failures |
| `analyze_seed_failures.py` | Failure ledger with corrected certificates |
| `make_unseen_30_30_sets.py` | Generate unseen test sets |
| `data/exports/v22_coverage_analysis.json` | Coverage data (173 FALSE pairs, 23 deep gaps) |

---

## 9. SUCCESS DEFINITION

**Minimum viable:** ≥92% on normal balanced seeds (improvement over v21f's 90%)  
**Target:** ≥95% on normal balanced seeds  
**Stretch:** ≥95% on random seeds + ≥85% on hard3  
**Competition goal:** Top 10% (given 891 participants, baseline ~63%)

The v21f at ~90% is already far above the no-cheatsheet baseline of ~63%. Each percentage point above 90% is harder to get but more competitively valuable.

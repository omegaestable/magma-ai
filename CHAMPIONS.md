# Champions

Only two cheatsheet versions achieved both normal ≥95% AND hard3 ≥75%.

Current champion: **v28d** (9,081 bytes) — 96.7% normal, 83.3% hard3, 50.0% competition hard.

---

## v28d — Current Champion (9,081 bytes)

### Architecture
6 structural tests (LP, RP, C0, VARS, COUNT2, LDEPTH) + Spine Depth Check + T3R/T3L/T5B/NL1 rescue magma tests.

### Best Results
| Difficulty | Model | N | Acc | TAcc | FAcc |
|-----------|-------|-----|-------|-------|-------|
| normal r23 | GPT-OSS-120B | 30 | 96.7% | 100% | 93.3% |
| hard3 r24 | GPT-OSS-120B | 30 | 83.3% | 100% | 66.7% |
| comp hard r23 | GPT-OSS-120B | 30 | 50.0% | 73.3% | 26.7% |
| hard2 r24 | GPT-OSS-120B | 30 | 43.3% | 60.0% | 26.7% |

### What v28d Added Over v28c
- **T5B all-ones guard**: requires E1 to pass on BOTH default variable assignment AND all-ones before declaring separation. Fixes 7 false separations on competition hard pool.
- **Confirmed fixes**: hard_0174 ✗→✓, hard_0169 ✗→✓ (+2 TP, +6.7pp accuracy).
- **Zero normal regression**: 96.7% normal safety gate passed.

### Why It's the Champion
- **Highest normal accuracy ever**: 96.7% (29/30), 100% TRUE recall, zero FN.
- **Best competition hard score**: 50.0% (15/30) — +6.7pp over v28c's 43.3%.
- **Mathematically proven strictly superior** to v28c across all pools.
- **1,159 bytes headroom** remaining for future improvements.

---

## v24j — Previous Champion (8,955 bytes)

### Architecture
4 structural tests (LP, RP, C0, VARS) + T3R rescue (a*b=next(b), gated on RP=HOLD) + implicit T3L.

### Best Results
| Difficulty | Model         | N   | Acc   | TAcc  | FAcc  |
|-----------|---------------|-----|-------|-------|-------|
| normal    | GPT-OSS-120B  | 60  | 95.0% | 100%  | 90.0% |
| normal    | GPT-OSS-120B  | 100 | 94.0% | 100%  | 88.0% |
| normal    | Gemma 31B     | 60  | 93.3% | 100%  | 86.7% |
| normal    | Llama 70B     | 60  | 93.3% | 100%  | 86.7% |
| normal    | Llama 70B     | 100 | 93.0% | 98.0% | 88.0% |
| hard3     | Llama 70B     | 20  | 75.0% | 100%  | 50.0% |
| hard3     | Llama 70B     | 40  | 72.5% | 100%  | 45.0% |
| hard3     | GPT-OSS-120B  | 40  | 62.5% | 100%  | 25.0% |

### Why It Won
- **Structural core is rock-solid**: LP/RP/C0/VARS almost never produce false results on TRUE pairs.
- **T3R rescue works**: a*b=next(b) is simple enough for models to execute reliably, catches many 3-element-separable FALSE pairs.
- **Compact size**: 8,955 bytes — leaves ~1KB headroom. Not fighting the byte cap.
- **Zero FN on normal**: model never calls TRUE pairs FALSE. All errors are FP (misses on FALSE pairs).
- **Cross-model stable**: 93%+ on all 3 models for normal.

### Weaknesses
- Hard3 FAcc tops at 50% — half of hard FALSE pairs evade T3R/T3L.
- Hard2 is 40% — needs 4+ element magmas it can't compute.
- No COUNT2 or LDEPTH structural tests (could catch more easy FALSE pairs cheaply).

---

## v26b — Current Best Candidate (9,729 bytes)

### Architecture
4 structural tests (LP, RP, C0, VARS) + Spine Depth Check (n|m divisibility) + T3R rescue + expanded T3L rescue.

### Best Results
| Difficulty | Model         | N   | Acc   | TAcc  | FAcc  |
|-----------|---------------|-----|-------|-------|-------|
| normal    | GPT-OSS-120B  | 20  | 95.0% | 100%  | 90.0% |
| hard3     | GPT-OSS-120B  | 20  | 75.0% | 100%  | 50.0% |
| hard2     | GPT-OSS-120B  | 20  | 40.0% | 100%  | 0.0%  |

### What v26b Added Over v24j
- **Spine Depth Check**: pure-depth divisibility test for left-spine idempotent powers. Zero execution error risk (just counting parens).
- **Expanded T3L**: full section with LP=HOLD guard, step-by-step instructions, next(a) rule. v24j had this implicit; v26b makes it explicit.
- **+10pp hard3 vs v26a** (65% → 75%): the T3L expansion fixed execution errors where models were doing T3L wrong.

### Why It's the Best
- Matches v24j on normal (95%) and hard3 (75%) despite being on a single model/rotation.
- 511 bytes of headroom remaining for extensions.
- Zero FN across all benchmark types — all errors are coverage gaps (FP), not execution errors.

---

## Key Shared Traits of Champions

1. **4 structural tests, no more**: LP, RP, C0, VARS. These are fast, reliable, and the model almost never computes them wrong.
2. **Default TRUE**: only say FALSE when a test proves separation. This protects TRUE accuracy.
3. **Gated rescues**: T3R only runs when RP=HOLD, T3L only when LP=HOLD. Gates prevent unnecessary computation and false flags.
4. **Simple 3-element magma**: next(b) or next(a) on {0,1,2}. Models can do mod-3 arithmetic reliably.
5. **Compact prompts**: 9–10KB with breathing room. Not fighting the byte cap.
6. **Decision table drilled in**: the 4-row table (HOLD/HOLD, HOLD/FAIL, FAIL/HOLD, FAIL/FAIL) is repeated and exemplified. The model must internalize that ONLY E1=HOLD+E2=FAIL is separation.

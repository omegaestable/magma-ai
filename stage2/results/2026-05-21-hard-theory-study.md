# 2026-05-21 Hard Theory Study

This study uses `evaluation_hard` and `evaluation_extra_hard` as analysis-only rows. Only `hard1`/`hard2`/`hard3` rows have official public-sample Marathon evidence.

## Summary

- rows: 50
- public official rows: 30
- study-only rows: 20
- already_solved_false: 20
- already_solved_true: 11
- easy_false_log: 4
- true_template_candidate: 15

## Implementation Result

- Added deterministic TRUE route `true:self_square_absorption` for hypotheses of shape `r = (p ◇ r) ◇ (p ◇ r)` and goals of shape `r = A ◇ (B ◇ r)`.
- Direct official verifier check for `hard1_0052` accepted the explicit Lean proof with no axioms.
- Study50 profile changed from `31` candidates / `19` skips / `36.666s` to `32` candidates / `18` skips / `36.346s`.
- Public30 official zero-token Marathon improved from `15/30` to `16/30`; accepted TRUE rows increased from `2` to `3`; remaining TRUE template gaps dropped from `11` to `10`.
- Corpus scan over official `hard1`/`hard2`/`hard3` plus `evaluation_hard`/`evaluation_extra_hard` found one matching row: `hard1_0052`.

## Official Run Comparison

| Run | Score | TRUE accepted | FALSE accepted | TRUE gaps | FALSE gaps | Wall seconds | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline public30 | 15/30 | 2 | 13 | 11 | 4 | 26.0 | 0 |
| after `true:self_square_absorption` | 16/30 | 3 | 13 | 10 | 4 | 25.5 | 0 |

## By Source

| Source | already_solved_true | true_template_candidate | already_solved_false | easy_false_log | unknown_hard |
|---|---:|---:|---:|---:|---:|
| evaluation_extra_hard | 7 | 0 | 3 | 0 | 0 |
| evaluation_hard | 2 | 4 | 4 | 0 | 0 |
| hard1 | 0 | 4 | 4 | 2 | 0 |
| hard2 | 0 | 5 | 3 | 2 | 0 |
| hard3 | 2 | 2 | 6 | 0 | 0 |

## TRUE Template Candidates

| ID | Lane | Pair | Teorth | Profile seconds | Equation 1 | Equation 2 |
|---|---|---|---|---:|---|---|
| hard1_0013 | official_public_sample | 4208,3356 | implicit_proof_true | 0.397 | x ◇ y = ((z ◇ y) ◇ x) ◇ x | x ◇ y = y ◇ (y ◇ (y ◇ y)) |
| hard1_0052 | official_public_sample | 169,2056 | implicit_proof_true | 0.747 | x = (y ◇ x) ◇ (y ◇ x) | x = ((x ◇ y) ◇ x) ◇ (z ◇ x) |
| hard1_0061 | official_public_sample | 447,1247 | implicit_proof_true | 2.076 | x = x ◇ (y ◇ (z ◇ (x ◇ y))) | x = x ◇ (((y ◇ x) ◇ z) ◇ w) |
| hard1_0069 | official_public_sample | 286,532 | implicit_proof_true | 0.597 | x = ((y ◇ y) ◇ z) ◇ x | x = y ◇ (y ◇ (z ◇ (w ◇ x))) |
| hard2_0005 | official_public_sample | 1181,2449 | implicit_proof_true | 2.104 | x = y ◇ ((z ◇ (z ◇ x)) ◇ y) | x = (x ◇ ((x ◇ y) ◇ y)) ◇ x |
| hard2_0097 | official_public_sample | 2248,4079 | implicit_proof_true | 2.190 | x = (x ◇ (x ◇ (y ◇ y))) ◇ z | x ◇ x = ((x ◇ y) ◇ z) ◇ w |
| hard2_0141 | official_public_sample | 2983,2791 | implicit_proof_true | 1.229 | x = ((y ◇ (z ◇ x)) ◇ z) ◇ z | x = ((y ◇ z) ◇ (y ◇ y)) ◇ x |
| hard2_0178 | official_public_sample | 853,849 | implicit_proof_true | 2.027 | x = x ◇ ((y ◇ z) ◇ (x ◇ y)) | x = x ◇ ((y ◇ y) ◇ (z ◇ y)) |
| hard2_0199 | official_public_sample | 2668,2848 | implicit_proof_true | 2.182 | x = ((x ◇ y) ◇ (x ◇ z)) ◇ w | x = ((x ◇ (x ◇ x)) ◇ x) ◇ y |
| hard3_0260 | official_public_sample | 2478,2287 | implicit_proof_true | 2.295 | x = (x ◇ ((y ◇ z) ◇ x)) ◇ z | x = (x ◇ (y ◇ (z ◇ w))) ◇ z |
| hard3_0329 | official_public_sample | 3074,4288 | implicit_proof_true | 0.641 | x = (((x ◇ y) ◇ x) ◇ z) ◇ w | x ◇ (x ◇ y) = x ◇ (z ◇ z) |
| evaluation_hard_0070 | study_only | 59,830 | implicit_proof_true | 2.009 | x = x * (y * (z * y)) | x = x * ((x * y) * (z * z)) |
| evaluation_hard_0072 | study_only | 86,1009 | implicit_proof_true | 1.789 | x = y * (z * (y * x)) | x = y * ((z * w) * (w * x)) |
| evaluation_hard_0096 | study_only | 447,4077 | implicit_proof_true | 1.960 | x = x * (y * (z * (x * y))) | x * x = ((x * y) * z) * y |
| evaluation_hard_0148 | study_only | 552,1563 | implicit_proof_true | 2.147 | x = y * (z * (x * (w * w))) | x = (y * z) * (x * (z * w)) |

## Easy FALSE Log

| ID | Lane | Pair | Teorth | Profile seconds | Equation 1 | Equation 2 |
|---|---|---|---|---:|---|---|
| hard1_0009 | official_public_sample | 2656,2863 | explicit_proof_false | 2.084 | x = ((x ◇ x) ◇ (y ◇ z)) ◇ y | x = ((x ◇ (y ◇ x)) ◇ x) ◇ y |
| hard1_0033 | official_public_sample | 2994,2623 | implicit_proof_false | 1.983 | x = ((y ◇ (z ◇ y)) ◇ y) ◇ x | x = (y ◇ ((z ◇ w) ◇ y)) ◇ x |
| hard2_0009 | official_public_sample | 898,2673 | implicit_proof_false | 1.926 | x = y ◇ ((x ◇ z) ◇ (z ◇ y)) | x = ((x ◇ y) ◇ (y ◇ y)) ◇ y |
| hard2_0016 | official_public_sample | 646,4127 | implicit_proof_false | 1.977 | x = x ◇ (y ◇ ((y ◇ z) ◇ y)) | x ◇ y = ((x ◇ y) ◇ x) ◇ x |

## Artifacts

- Ledger JSONL: `stage2/results/2026-05-21-hard-theory-study-ledger.jsonl`
- Easy FALSE JSONL: `stage2/results/2026-05-21-hard-theory-easy-false-log.jsonl`
- TRUE miss pairs: `stage2/results/proof_lab/2026-05-21-hard-theory-true-miss-pairs.txt`
- Baseline public30 run: `stage2/results/2026-05-21-hard-theory-public30-baseline-marathon/analysis.json`
- After public30 run: `stage2/results/2026-05-21-hard-theory-public30-after-self-square-marathon/analysis.json`
- After profile: `stage2/results/2026-05-21-hard-theory-study50-profile-after-self-square.json`
- Motif corpus scan: `stage2/results/2026-05-21-self-square-route-corpus-scan.jsonl`

# 2026-05-21 Hard Pass 2 Study

Fresh non-overlapping pass after `true:self_square_absorption`. `evaluation_hard` and `evaluation_extra_hard` are study-only; only `hard1`/`hard2`/`hard3` public rows are official evidence.

## Summary

- seed: `202605211`
- public rows: 90 (38 TRUE / 52 FALSE)
- study rows: 150 (65 TRUE / 85 FALSE)
- public90 baseline: 48/90, 4 TRUE, 44 FALSE, 34 TRUE gaps, 8 FALSE gaps, 84.1s, 0 tokens
- implemented `true:repeat_tail_absorption` for `hard3_0020` after a shadow closure hit produced a 220-byte accepted certificate
- profile study150 after route: 94 candidates / 56 skips, `true:repeat_tail_absorption` count 1, elapsed 116.4s
- public90 after route: 49/90, 5 TRUE, 44 FALSE, 33 TRUE gaps, 8 FALSE gaps, 81.1s, 0 tokens
- public30 regression after route: 16/30, including `true:self_square_absorption` count 1, 0 tokens
- baseline profile study150: 93 candidates / 57 skips
- true template candidates: 43
- easy FALSE log: 14

## Implemented Route

`true:repeat_tail_absorption` handles hypotheses of shape `r = p ◇ (q ◇ (q ◇ r))` and goals of shape `r = (r ◇ r) ◇ (r ◇ (A ◇ r))`. For `hard3_0020`, the emitted certificate is:

```lean
import JudgeProblem

def submission : Goal := by
	intro G _ h
	intro x y
	exact ((h x y y).trans (h (y ◇ (y ◇ (y ◇ x))) (x ◇ x) x)).trans (congrArg (fun t => ((x ◇ x) ◇ (x ◇ t))) (h (y ◇ x) x y)).symm
```

Runner-equivalent direct verification accepted the certificate. A corpus scan over official `hard1`/`hard2`/`hard3` plus `evaluation_hard` and `evaluation_extra_hard` found one match: `hard3_0020`.

## By Source

| Source | already_solved_true | true_template_candidate | already_solved_false | easy_false_log | unknown_hard |
|---|---:|---:|---:|---:|---:|
| evaluation_extra_hard | 12 | 1 | 12 | 5 | 0 |
| evaluation_hard | 6 | 8 | 15 | 1 | 0 |
| hard1 | 0 | 11 | 15 | 4 | 0 |
| hard2 | 0 | 12 | 14 | 4 | 0 |
| hard3 | 4 | 11 | 15 | 0 | 0 |

## Top Public TRUE Candidates

| ID | Pair | Teorth | Profile seconds | Equation 1 | Equation 2 |
|---|---|---|---:|---|---|
| hard2_0193 | 2190,4320 | implicit_proof_true | 2.460 | x = ((y ◇ z) ◇ y) ◇ (w ◇ x) | x ◇ (y ◇ x) = y ◇ (x ◇ x) |
| hard1_0056 | 1953,608 | implicit_proof_true | 2.431 | x = (y ◇ (y ◇ z)) ◇ (w ◇ x) | x = y ◇ (z ◇ (w ◇ (u ◇ x))) |
| hard3_0244 | 2190,3388 | implicit_proof_true | 2.320 | x = ((y ◇ z) ◇ y) ◇ (w ◇ x) | x ◇ y = z ◇ (x ◇ (z ◇ y)) |
| hard1_0023 | 164,3470 | implicit_proof_true | 2.285 | x = (x ◇ y) ◇ (z ◇ z) | x ◇ x = x ◇ ((y ◇ z) ◇ w) |
| hard2_0083 | 2178,3431 | implicit_proof_true | 2.283 | x = ((y ◇ z) ◇ y) ◇ (x ◇ x) | x ◇ y = z ◇ (w ◇ (x ◇ y)) |
| hard3_0284 | 2678,3462 | implicit_proof_true | 2.256 | x = ((x ◇ y) ◇ (y ◇ z)) ◇ w | x ◇ x = x ◇ ((y ◇ x) ◇ y) |
| hard3_0214 | 2042,2692 | implicit_proof_true | 2.244 | x = ((x ◇ x) ◇ y) ◇ (x ◇ z) | x = ((x ◇ y) ◇ (z ◇ w)) ◇ y |
| hard1_0027 | 54,2695 | implicit_proof_true | 2.242 | x = x ◇ (y ◇ (x ◇ z)) | x = ((x ◇ y) ◇ (z ◇ w)) ◇ u |
| hard3_0020 | 90,1428 | implicit_proof_true | 2.219 | x = y ◇ (z ◇ (z ◇ x)) | x = (x ◇ x) ◇ (x ◇ (y ◇ x)) |
| hard2_0037 | 3242,1251 | implicit_proof_true | 2.201 | x = (((y ◇ z) ◇ w) ◇ w) ◇ x | x = x ◇ (((y ◇ y) ◇ y) ◇ x) |
| hard1_0065 | 59,2240 | implicit_proof_true | 2.191 | x = x ◇ (y ◇ (z ◇ y)) | x = (x ◇ (x ◇ (x ◇ y))) ◇ x |
| hard2_0066 | 1716,2469 | implicit_proof_true | 2.188 | x = (y ◇ x) ◇ ((z ◇ w) ◇ w) | x = (x ◇ ((y ◇ y) ◇ y)) ◇ x |
| hard1_0018 | 2105,1229 | implicit_proof_true | 2.172 | x = ((y ◇ x) ◇ y) ◇ (z ◇ z) | x = x ◇ (((x ◇ y) ◇ x) ◇ y) |
| hard2_0069 | 1317,1021 | implicit_proof_true | 2.170 | x = y ◇ (((y ◇ x) ◇ y) ◇ z) | x = x ◇ ((x ◇ (x ◇ x)) ◇ y) |
| hard2_0174 | 2907,2968 | implicit_proof_true | 2.166 | x = ((y ◇ (x ◇ x)) ◇ z) ◇ z | x = ((y ◇ (y ◇ z)) ◇ w) ◇ x |
| hard1_0059 | 298,1045 | implicit_proof_true | 2.164 | x = ((y ◇ z) ◇ z) ◇ x | x = x ◇ ((y ◇ (y ◇ x)) ◇ x) |
| hard2_0060 | 636,1070 | implicit_proof_true | 2.140 | x = x ◇ (y ◇ ((x ◇ z) ◇ y)) | x = x ◇ ((y ◇ (z ◇ w)) ◇ w) |
| hard3_0266 | 2521,1879 | implicit_proof_true | 2.135 | x = (y ◇ ((x ◇ z) ◇ z)) ◇ x | x = (x ◇ (y ◇ z)) ◇ (w ◇ x) |
| hard1_0007 | 2343,3446 | implicit_proof_true | 2.133 | x = (y ◇ (y ◇ (y ◇ z))) ◇ x | x ◇ y = z ◇ (w ◇ (w ◇ y)) |
| hard2_0072 | 2908,1198 | implicit_proof_true | 2.115 | x = ((y ◇ (x ◇ x)) ◇ z) ◇ w | x = y ◇ ((z ◇ (w ◇ x)) ◇ y) |

## Easy FALSE Log

| ID | Lane | Pair | Teorth | Profile seconds | Equation 1 | Equation 2 |
|---|---|---|---|---:|---|---|
| hard1_0008 | official_public_sample | 646,1020 | explicit_proof_false | 1.430 | x = x ◇ (y ◇ ((y ◇ z) ◇ y)) | x = x ◇ ((x ◇ (x ◇ x)) ◇ x) |
| hard1_0025 | official_public_sample | 3008,1131 | implicit_proof_false | 2.151 | x = ((y ◇ (z ◇ z)) ◇ x) ◇ y | x = y ◇ ((y ◇ (z ◇ x)) ◇ z) |
| hard1_0037 | official_public_sample | 1336,419 | implicit_proof_false | 2.213 | x = y ◇ (((y ◇ z) ◇ y) ◇ x) | x = x ◇ (x ◇ (y ◇ (y ◇ x))) |
| hard1_0062 | official_public_sample | 2116,2327 | implicit_proof_false | 2.019 | x = ((y ◇ x) ◇ z) ◇ (z ◇ y) | x = (y ◇ (y ◇ (x ◇ x))) ◇ x |
| hard2_0012 | official_public_sample | 1368,4612 | implicit_proof_false | 2.051 | x = y ◇ (((z ◇ y) ◇ x) ◇ z) | (x ◇ x) ◇ y = (y ◇ z) ◇ z |
| hard2_0027 | official_public_sample | 1167,1763 | implicit_proof_false | 2.169 | x = y ◇ ((z ◇ (y ◇ y)) ◇ x) | x = (y ◇ z) ◇ ((x ◇ z) ◇ x) |
| hard2_0125 | official_public_sample | 2890,2652 | explicit_proof_false | 2.282 | x = ((x ◇ (y ◇ z)) ◇ z) ◇ x | x = ((x ◇ x) ◇ (y ◇ y)) ◇ x |
| hard2_0133 | official_public_sample | 898,949 | implicit_proof_false | 2.091 | x = y ◇ ((x ◇ z) ◇ (z ◇ y)) | x = y ◇ ((z ◇ x) ◇ (y ◇ z)) |
| evaluation_extra_hard_0172 | study_only | 168,3463 | explicit_proof_false | 1.989 | x = (y * x) * (x * z) | x * x = x * ((y * x) * z) |
| evaluation_extra_hard_0180 | study_only | 168,3864 | explicit_proof_false | 2.248 | x = (y * x) * (x * z) | x * x = (x * (x * y)) * x |
| evaluation_extra_hard_0184 | study_only | 168,3952 | explicit_proof_false | 1.984 | x = (y * x) * (x * z) | x * y = (y * (x * x)) * y |
| evaluation_extra_hard_0186 | study_only | 168,3989 | explicit_proof_false | 1.984 | x = (y * x) * (x * z) | x * y = (z * (x * x)) * y |
| evaluation_extra_hard_0194 | study_only | 168,4357 | explicit_proof_false | 1.824 | x = (y * x) * (x * z) | x * (y * z) = x * (y * w) |
| evaluation_hard_0145 | study_only | 695,3342 | implicit_proof_false | 1.990 | x = y * (x * ((z * z) * y)) | x * y = y * (x * (x * x)) |

## Artifacts

- Public manifest: `tmp_stage2_smoke/2026-05-21-hard-pass2-public90.jsonl`
- Study manifest: `tmp_stage2_smoke/2026-05-21-hard-pass2-study150.jsonl`
- Profile: `stage2/results/2026-05-21-hard-pass2-study150-profile.json`
- After-route profile: `stage2/results/2026-05-21-hard-pass2-study150-profile-after-repeat-tail.json`
- Teorth certification: `stage2/results/2026-05-21-hard-pass2-teorth.jsonl`
- Ledger JSONL: `stage2/results/2026-05-21-hard-pass2-study-ledger.jsonl`
- Easy FALSE JSONL: `stage2/results/2026-05-21-hard-pass2-easy-false-log.jsonl`
- Shadow probe: `stage2/results/2026-05-21-hard-pass2-true-gap-shadow-probe.jsonl`
- Route corpus scan: `stage2/results/2026-05-21-repeat-tail-route-corpus-scan.jsonl`
- Public90 baseline: `stage2/results/2026-05-21-hard-pass2-public90-baseline-marathon/analysis.json`
- Public90 after route: `stage2/results/2026-05-21-hard-pass2-public90-after-repeat-tail-marathon/analysis.json`
- Public30 regression after route: `stage2/results/2026-05-21-hard-theory-public30-after-repeat-tail-marathon/analysis.json`

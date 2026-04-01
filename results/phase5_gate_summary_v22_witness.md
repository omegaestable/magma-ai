# Phase 5 Gate Summary (Paid Campaign) - v22_witness

## Seed-by-Seed Scores

| Suite | Seed file | Accuracy | F1(strict) | TRUE acc | FALSE acc | TP/FP/FN/TN | Fails |
|---|---|---:|---:|---:|---:|---|---:|
| normal unseen 30/30 | normal_balanced60_true30_false30_seed20260401_unseen_20260401 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 30/0/0/30 | 0 |
| normal unseen 30/30 | normal_balanced60_true30_false30_seed20260402_unseen_20260401 | 0.9333 | 0.9375 | 1.0000 | 0.8667 | 30/4/0/26 | 4 |
| hard3 unseen 30/30 | hard3_balanced60_true30_false30_seed20260401_unseen_20260401 | 0.5167 | 0.6742 | 1.0000 | 0.0333 | 30/29/0/1 | 29 |
| hard3 unseen 30/30 | hard3_balanced60_true30_false30_seed20260402_unseen_20260401 | 0.5000 | 0.6667 | 1.0000 | 0.0000 | 30/30/0/0 | 30 |

Aggregate over 240 runs:
- Correct: 177
- Incorrect: 62
- Unparsed: 1
- Accuracy: 0.7375
- Dominant failure mode: FALSE misses from default-TRUE lane (`SOURCE: N`, `REASONING: NONE`) = 62/63 failures.

## Forensics Artifacts
- Full fail ledger: `results/phase5_fail_ledger_v22_witness.md`
- Teorth source metadata:
  - `results/teorth_cert_normal_seed20260401.jsonl`
  - `results/teorth_cert_normal_seed20260402.jsonl`
  - `results/teorth_cert_hard3_seed20260401.jsonl`
  - `results/teorth_cert_hard3_seed20260402.jsonl`
- Oracle mining/proposal: `results/phase5_oracle_update_proposal_v22_witness.md`

## Gate Decision
- Normal safety gate is **not closed** on this pass due to non-zero normal false misses in seed20260402.
- Hard3 FALSE coverage remains insufficient.
- Promotion status: **blocked pending more hard3 mining and re-gated normal safety**.

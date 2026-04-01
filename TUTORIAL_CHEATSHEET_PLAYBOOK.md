# Cheatsheet Playbook

This playbook is the end-to-end path from raw data to a promoted cheatsheet.

## 1. Goal and Promotion Standard

Target artifact: one prompt template in `cheatsheets/`.

Promotion standard:
1. Normal safety gate passes (no regressions on required unseen suites).
2. Hard performance improves measurably.
3. Every reported FALSE has source-backed certificate metadata.
4. Template remains under 10KB (`10,240` bytes on disk).

## 2. Environment Setup

1. Activate venv.
2. Set OpenRouter key:

```powershell
$env:OPENROUTER_API_KEY = "<your_key>"
```

3. Optional refresh of Teorth assets:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe fetch_teorth_data.py --check
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe fetch_teorth_data.py --force
```

## 3. Baseline Evaluation

Run paid baseline for current candidate:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/normal_balanced60_true30_false30_seed20260401_unseen_20260401.jsonl --cheatsheet cheatsheets/v22_witness.txt --openrouter --output results/sim_paid_normal_seed20260401_v22_witness.json

C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/hard3_balanced60_true30_false30_seed20260401_unseen_20260401.jsonl --cheatsheet cheatsheets/v22_witness.txt --openrouter --output results/sim_paid_hard3_seed20260401_v22_witness.json
```

## 4. Failure Forensics

Generate fail ledger:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe analyze_seed_failures.py --cheatsheet cheatsheets/v22_witness.txt --result-files results/sim_paid_normal_seed20260401_v22_witness.json,results/sim_paid_hard3_seed20260401_v22_witness.json --out results/seed_failure_report.md
```

Generate broader pattern distillation:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe distill.py --result-file results/sim_paid_hard3_seed20260401_v22_witness.json --out-dir results/manual_distill --cycle 1
```

Attach Teorth provenance:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe teorth_true_proof_agent.py certify-benchmark --input data/benchmark/hard3_balanced60_true30_false30_seed20260401_unseen_20260401.jsonl --output results/teorth_cert_hard3_seed20260401.jsonl
```

## 5. Bulk Proof Mining (Optional but Recommended)

Scrape many proof pages by pair:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe proof_scraping_lab.py --from-results results/sim_paid_hard3_seed20260401_v22_witness.json --failed-only --limit 200 --out-prefix results/proof_lab/hard3_failures_seed20260401
```

Use output artifacts:
- JSONL for machine processing.
- Markdown for fast human review.

## 6. Candidate Update Strategy

Preferred order for safe uplift:
1. Fix deterministic witness lane gaps.
2. Add compact oracle signatures only after normal TRUE collision checks.
3. Keep heuristic FALSE lane disabled unless proven normal-safe.

Hard constraints:
1. No benchmark pair hardcoding as policy.
2. Preserve source labels for FALSE decisions.
3. Keep template concise and deterministic.

## 7. Candidate Validation

Run template correctness and budget checks:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe v22_test_jinja2.py
```

Then rerun paid gates (normal first, then hard):

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/normal_balanced60_true30_false30_seed20260401_unseen_20260401.jsonl --cheatsheet cheatsheets/v22_witness.txt --openrouter --output results/sim_paid_normal_seed20260401_v22_witness.json

C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/normal_balanced60_true30_false30_seed20260402_unseen_20260401.jsonl --cheatsheet cheatsheets/v22_witness.txt --openrouter --output results/sim_paid_normal_seed20260402_v22_witness.json

C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/hard3_balanced60_true30_false30_seed20260401_unseen_20260401.jsonl --cheatsheet cheatsheets/v22_witness.txt --openrouter --output results/sim_paid_hard3_seed20260401_v22_witness.json

C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/hard3_balanced60_true30_false30_seed20260402_unseen_20260401.jsonl --cheatsheet cheatsheets/v22_witness.txt --openrouter --output results/sim_paid_hard3_seed20260402_v22_witness.json
```

## 8. Promotion Checklist

1. Normal suites: no new regressions.
2. Hard suites: measurable lift versus previous champion.
3. Ledger produced and reviewed.
4. Teorth provenance attached for contentious cases.
5. Final verdict recorded (`promoted`, `unchanged`, or `blocked`).

# Cheatsheet Playbook

This is the end-to-end operator tutorial for the current natural-language-only cheatsheet workflow.

## 1. Goal

Produce one text cheatsheet in `cheatsheets/` that stays under 10,240 bytes, remains mathematically defensible, and improves performance without normal-set regression.

Current operating artifacts:

- Baseline champion: `cheatsheets/v21f_structural.txt`
- Active candidate: `cheatsheets/v23.txt`

## 2. Hard Rules

1. Cheatsheets are plain text only.
2. Only `{{equation1}}` and `{{equation2}}` substitution is allowed.
3. No Jinja2 logic of any kind.
4. No benchmark-pair hardcoding as policy.
5. Normal safety comes before hard-set uplift.

## 3. Environment Setup

1. Activate the repo venv.
2. Set your OpenRouter key.
3. Optionally refresh Teorth data if you are doing provenance work.

```powershell
$env:OPENROUTER_API_KEY = "<your_key>"
python fetch_teorth_data.py --check
```

## 4. Evaluate The Baseline Or Candidate

Fast wrapper form:

```powershell
.\run_paid_eval.ps1 -Benchmark normal_balanced10_true5_false5_seed0 -Cheatsheet v21f_structural
```

Direct evaluator form:

```powershell
python sim_lab.py --data data/benchmark/normal_balanced10_true5_false5_seed0.jsonl --cheatsheet cheatsheets/v23.txt --openrouter --model meta-llama/llama-3.3-70b-instruct --playground-parity --errors
```

For current promotion work, use this order:

1. warmup normal seeds 0 and 1
2. full normal seeds 0, 1, and 2
3. unseen and hard benchmarks only after normal is stable

## 5. Inspect The Outputs

Primary outputs:

- `results/sim_*.json`
- `results/scoreboard.md`
- `results/scoreboard.csv`

Look at:

1. overall accuracy
2. true accuracy
3. false accuracy
4. parse rate
5. quality score
6. specific failures

## 6. Distill Failures

Build the fail ledger:

```powershell
python analyze_seed_failures.py
```

Build a broader pattern summary from a result file:

```powershell
python distill.py --result-file results/<your_run>.json --out-dir results/manual_distill --cycle 1
```

Use this stage to decide whether misses are:

1. execution bugs
2. formatting collapse
3. coverage gaps
4. provenance issues

## 7. Add Proof Or Source Grounding When Needed

Attach Teorth provenance:

```powershell
python teorth_true_proof_agent.py certify-benchmark --input data/benchmark/normal_balanced20_true10_false10_seed0.jsonl --output results/teorth_cert_seed0.jsonl
```

Bulk proof scraping is optional and should be used only when provenance mining is the real bottleneck:

```powershell
python proof_scraping_lab.py --from-results results/<your_run>.json --failed-only --limit 100 --out-prefix results/proof_lab/failures
```

For archival construction mining, seed a cached recursive crawl from the Teorth metadata:

```powershell
python proof_scraping_lab.py --from-full-entries --recursive --limit 500 --out-prefix results/proof_lab/archive_seed
```

Then convert that crawl into a construction-family atlas for downstream hard-false distillation:

```powershell
python proof_construction_atlas.py --crawl-jsonl results/proof_lab/archive_seed.jsonl --out-prefix results/proof_lab/archive_seed_atlas
```

## 8. Patch The Cheatsheet

Patch only after you understand the error type.

Preferred order for safe improvement:

1. fix execution and formatting failures
2. tighten sound structural instructions
3. add compact clarifying examples only when they reduce error without increasing brittleness

Avoid:

1. making the prompt longer just to feel safer
2. adding counting-heavy logic unless you have strong evidence it helps this model
3. optimizing around one benchmark file

## 9. Validate Before Promotion

Always check size:

```powershell
(Get-Item "cheatsheets\v23.txt").Length
```

Then re-run normal gates before any hard campaign.

## 10. Promotion Checklist

1. Normal gates do not regress against the champion.
2. Hard or unseen performance is not worse.
3. Parse and quality behavior remain acceptable.
4. The change is mathematically explainable.
5. Results and ledger agree with the promotion decision.

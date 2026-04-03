# Eval Workflow

This is the canonical benchmark and promotion workflow for cheatsheet development.

## Goal

Promote a candidate only when it is normal-safe and backed by reproducible evidence.

## Canonical Loop

1. Run warmup normal benchmarks.
2. Run full normal gates.
3. If any full normal seed regresses, stop and distill that failing seed first.
4. Patch the cheatsheet only after the failure type is clear.
5. Re-run the failing normal seed, then return to the full normal gate set.
5. Safety holds only when all full normal seeds meet or beat the champion with no regression.
6. Run unseen and hard stress only after safety holds.

## Standard Benchmark Tiers

### Warmup

Purpose: catch obvious regressions quickly.

- `data/benchmark/normal_balanced10_true5_false5_seed0.jsonl`
- `data/benchmark/normal_balanced10_true5_false5_seed1.jsonl`

### Full Normal Gate

Purpose: promotion-quality normal safety check.

- `data/benchmark/normal_balanced20_true10_false10_seed0.jsonl`
- `data/benchmark/normal_balanced20_true10_false10_seed1.jsonl`
- `data/benchmark/normal_balanced20_true10_false10_seed2.jsonl`

Operational rule: the candidate should meet or beat the current champion across all three of these files before hard-set uplift matters.

### Stress And Unseen

Use after normal is stable:

- regenerate the rotating official-like bundle with `make_unseen_30_30_sets.py`
- evaluate the `normal`, `hard`, and `hard3` files listed in `data/benchmark/rotating_official_latest.json`

Recommended refresh command:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe make_unseen_30_30_sets.py --purge-legacy-unseen
```

## Canonical Commands

Quick wrapper:

```powershell
.\run_paid_eval.ps1 -Benchmark normal_balanced10_true5_false5_seed0 -Cheatsheet v21f_structural
```

Direct evaluator:

```powershell
python sim_lab.py --data data/benchmark/normal_balanced20_true10_false10_seed0.jsonl --cheatsheet cheatsheets/v23.txt --openrouter --model meta-llama/llama-3.3-70b-instruct --playground-parity --errors
```

## What To Inspect

Primary outputs:

- `results/sim_*.json`
- `results/scoreboard.md`
- `results/scoreboard.csv`

Retention guidance:

1. `results/sim_*.json` are working payloads for immediate analysis and are ignored by git.
2. After you have distilled or summarized a run, prefer keeping the scoreboard outputs instead of a pile of raw payloads.
3. If you need durable evidence for a decision, capture it in the scoreboard, current-state notes, or a reviewed ledger rather than relying on many local raw files.

From each run, inspect:

1. accuracy
2. true accuracy
3. false accuracy
4. parse rate
5. quality score
6. error list

## Failure Triage

After a failed run:

1. Use `analyze_seed_failures.py` to build the fail ledger.
2. Use `distill.py` to classify patterns.
3. Decide whether misses are:
   - execution errors
   - coverage gaps
   - formatting collapse
   - provenance mismatches

### Failure Categories

- execution error: the model reasons incorrectly about a rule that should have worked, or produces malformed analysis
- coverage gap: the current structural lane has no sound separator for the pair, so default behavior stays wrong
- formatting collapse: the model abandons the required output contract or drifts into prose that the parser cannot trust
- provenance mismatch: benchmark truth and source-backed evidence disagree and the pair needs audit before policy changes

If the failure type is unclear, do not patch the cheatsheet first. Build the ledger and classify before editing.

### Distillation Scope

Default practice:

1. Distill every failure on warmup and full normal gates.
2. For larger hard or unseen runs, start with all failures if count is manageable; otherwise begin with the highest-frequency or repeated patterns.
3. Do not generalize from one isolated miss when the ledger suggests a broader coverage pattern.

## Promotion Rule

Promote only if all of the following hold:

1. No normal regression against the current champion.
2. Hard or unseen performance is not worse.
3. Quality and parse behavior remain acceptable.
4. The change is explainable in mathematical terms.

Operational definition of "safety holds": all three full normal seeds meet or beat the current champion with no regression.

If those conditions do not hold, keep the old champion.

## Banned Shortcuts

1. No benchmark-pair hardcoding.
2. No Jinja2 logic in cheatsheets.
3. No promotion from one lucky run.
4. No ignoring quality/parse failures just because raw accuracy looks better.
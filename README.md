# magma-ai

Focused local harness for SAIR Stage 1 magma implication evaluation.

## Fast Start

Prerequisite for paid-model runs:

```powershell
$env:OPENROUTER_API_KEY = "<your_key>"
```

Common paid-model run on the exact 5 TRUE / 5 FALSE normal benchmark:

```powershell
.\run_paid_eval.ps1 -Benchmark normal_balanced10_true5_false5_seed0 -Cheatsheet v10_proof_required
.\run_paid_eval.ps1 -Benchmark normal_balanced10_true5_false5_seed0 -Cheatsheet v13_proof_required
```

These commands run:

- Model: `meta-llama/llama-3.3-70b-instruct`
- Backend: OpenRouter
- Benchmark: `data/benchmark/normal_balanced10_true5_false5_seed0.jsonl`
- Cheatsheets: `cheatsheets/v10_proof_required.txt` or `cheatsheets/v13_proof_required.txt`

## Canonical Benchmarks

- `normal_balanced10_true5_false5_seed0`
- `normal_balanced12_true6_false6_seed0`
- `normal_balanced20_true10_false10_seed0`
- `normal_balanced20_true10_false10_seed1`
- `normal_balanced20_true10_false10_seed2`
- `hard1_balanced6_true3_false3_seed0`
- `hard1_balanced14_true7_false7_seed0`
- `hard2_balanced14_true7_false7_seed0`
- `control_hard20_seed17`
- `control_balanced_normal100_hard20_seed17`
- `control_balanced100_25x4_seed17`

All benchmark files live under `data/benchmark/`.

## Direct Python Commands

If you want the raw simulator command instead of the wrapper:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/normal_balanced10_true5_false5_seed0.jsonl --cheatsheet cheatsheets/v10_proof_required.txt --openrouter --model meta-llama/llama-3.3-70b-instruct

C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/normal_balanced10_true5_false5_seed0.jsonl --cheatsheet cheatsheets/v13_proof_required.txt --openrouter --model meta-llama/llama-3.3-70b-instruct
```

## Results

Result JSONs are written to `results/` with filenames like:

```text
sim_meta-llama_llama-3.3-70b-instruct_normal_balanced10_true5_false5_seed0_v13_proof_required_YYYYMMDD_HHMMSS.json
```

The scoreboard summary is in `results/scoreboard.md`.

## Background VNext Search

This repo now includes an iterative search controller that only promotes `v_next`
when a candidate beats the current champion consistently on the fixed balanced20
normal gate suite using `meta-llama/llama-3.3-70b-instruct` in playground-parity
mode.

Build the fixed balanced20 gates:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe vnext_search.py build-gates
```

Baseline the current champion across the 3-seed gate suite:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe vnext_search.py baseline
```

Run one candidate cycle:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe vnext_search.py cycle
```

Run a bounded unattended search loop:

```powershell
.\run_vnext_search.ps1 -Action loop -Cycles 3 -BudgetUsd 1.0 -Background
```

Check status:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe vnext_search.py status
```

Workflow artifacts are written under `results/vnext_search/` and staged
candidates are written under `cheatsheets/generated/`.
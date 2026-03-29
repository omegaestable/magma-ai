# magma-ai

Focused local harness for SAIR Stage 1 magma implication evaluation.

Paid OpenRouter evaluation is the only supported inference path in this repo.
Local model inference has been retired because it was not trustworthy for submission decisions.

## Fast Start

Prerequisite for paid-model runs:

```powershell
$env:OPENROUTER_API_KEY = "<your_key>"
```

Common paid-model run on the exact 5 TRUE / 5 FALSE normal benchmark:

```powershell
.\run_paid_eval.ps1 -Benchmark normal_balanced10_true5_false5_seed0 -Cheatsheet v19_noncollapse
.\run_paid_eval.ps1 -Benchmark normal_balanced10_true5_false5_seed0 -Cheatsheet v13_proof_required
```

These commands run:

- Model: `meta-llama/llama-3.3-70b-instruct`
- Backend: OpenRouter
- Benchmark: `data/benchmark/normal_balanced10_true5_false5_seed0.jsonl`
- Cheatsheets: `cheatsheets/v19_noncollapse.txt` or `cheatsheets/v13_proof_required.txt`

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
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/normal_balanced10_true5_false5_seed0.jsonl --cheatsheet cheatsheets/v19_noncollapse.txt --openrouter --model meta-llama/llama-3.3-70b-instruct

C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/normal_balanced10_true5_false5_seed0.jsonl --cheatsheet cheatsheets/v13_proof_required.txt --openrouter --model meta-llama/llama-3.3-70b-instruct
```

Official HF subsets supported directly by `sim_lab.py` are `normal`, `hard`, `hard1`, `hard2`, and `hard3`.

Example:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --subset hard3 --cheatsheet cheatsheets/v19_noncollapse.txt --openrouter --model meta-llama/llama-3.3-70b-instruct
```

`sim_lab.py` now requires OpenRouter credentials and always uses the paid backend.

## Results

Result JSONs are written to `results/` with filenames like:

```text
sim_meta-llama_llama-3.3-70b-instruct_normal_balanced10_true5_false5_seed0_v19_noncollapse_YYYYMMDD_HHMMSS.json
```

The scoreboard summary is in `results/scoreboard.md`.

## Legacy Note

V1 search pipeline files and artifacts were retired during production cleanup.
Only the V2 rebooted pipeline is supported.

## VNext Search V2 (Reboot)

The rebooted pipeline is implemented in `vnext_search_v2.py` with strict
anti-collapse gating and a single authoritative baseline (`v13_proof_required`).

Current prompt state:

- `v13_proof_required` is still the persisted V2 search baseline/champion.
- `v19_noncollapse` is the current manually patched non-collapsing prompt used for direct evaluation work.

Policy locks in V2:

- Fixed evaluation model: `meta-llama/llama-3.3-70b-instruct`
- Fixed gate suite: `normal_balanced20_true10_false10_seed0/1/2`
- Promotion gate: `2/3` seed wins + per-seed class floors
- Default mode is `shadow` (evaluate candidates without auto-promotion)

Bootstrap the reboot flow:

```powershell
.\run_vnext_search_v2.ps1 -Action build-gates
.\run_vnext_search_v2.ps1 -Action freeze-legacy
.\run_vnext_search_v2.ps1 -Action init
.\run_vnext_search_v2.ps1 -Action status
```

Run one strict cycle:

```powershell
.\run_vnext_search_v2.ps1 -Action cycle
```

Run strict historical replay checks (defaults to v14/v16/v17 vs v13 baseline):

```powershell
.\run_vnext_search_v2.ps1 -Action replay-check
```

Override replay labels:

```powershell
.\run_vnext_search_v2.ps1 -Action replay-check -Cheatsheets "v14_proof_required,v16_early_false_signal,v17_corrected"
```

Warmup-first anti-collapse behavior:

- Every new candidate is screened on `normal_balanced10_true5_false5_seed0` before any 20/20 evaluation.
- Full 3-seed `balanced20` evaluation is blocked until the search records the configured non-collapse streak on the 5/5 warmup gate.
- Warmup currently requires non-zero TRUE recall and non-zero F1 in practice via the configured floors in `vnext_search_v2_config.json`.

Run bounded loop in background:

```powershell
.\run_vnext_search_v2.ps1 -Action loop -Cycles 3 -BudgetUsd 0.5 -Background
```

V2 decision artifacts are written to:

- `results/vnext_search_v2/decisions/` (one decision JSON per cycle)
- `results/vnext_search_v2/replay/` (replay-check outputs)

V2 distillation now emits both structural and verified-witness sidecars under `results/vnext_search_v2/distilled_signals/`:

- `*_distillation_brief.md` for ranked failure patterns
- `*_witness_brief.md` for compact verified small-magma separations on recent false positives

You can also distill a raw paid result JSON directly:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe distill.py --result-file results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced10_true5_false5_seed0_v18_evidence_hierarchy_YYYYMMDD_HHMMSS.json --out-dir results/manual_distill --cycle 18
```

## Proof Atlas

Build the research-first proof atlas and render the first competition cheatsheet candidate:

```powershell
python proof_atlas.py
```

Artifacts are written to:

- `results/proof_atlas/proof_atlas.jsonl`
- `results/proof_atlas/proof_atlas.md`
- `results/proof_atlas/validation_report.json`
- `cheatsheets/generated_v2/cheatsheet_competition_v1.txt`

Build the atlas-guided public-corpus development artifacts and generated prompt variants:

```powershell
python atlas_public_dev.py
```

This uses:

- full `data/hf_cache/normal.jsonl`
- full `data/hf_cache/hard1.jsonl`
- held-out `data/hf_cache/hard2.jsonl`
- held-out `data/hf_cache/hard3.jsonl`

Artifacts are written to:

- `results/proof_atlas_public/dataset_split.json`
- `results/proof_atlas_public/public_corpus_alignment.jsonl`
- `results/proof_atlas_public/public_corpus_family_report.json`
- `results/proof_atlas_public/variant_decisions.json`
- `cheatsheets/generated_v2/atlas_public/`

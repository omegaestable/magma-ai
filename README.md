# magma-ai

Cheatsheet-first tooling for SAIR Equational Theories Stage 1.

Main objective: produce a compact (<10KB), source-grounded cheatsheet that maximizes hard-set performance while preserving normal-set safety.

Paid OpenRouter evaluation is the only supported inference path in this repo.

## Main Goal

Build and promote a single cheatsheet in `cheatsheets/` that passes your gate policy:

1. Strong hard performance (for current phase target, hard3 uplift).
2. Zero normal-safety regressions before promotion.
3. Reproducible evidence: score summaries, failure ledger, and certificate provenance.

## Quick Start

Set OpenRouter key in your shell:

```powershell
$env:OPENROUTER_API_KEY = "<your_key>"
```

Run one paid eval quickly:

```powershell
.\run_paid_eval.ps1 -Benchmark normal_balanced10_true5_false5_seed0 -Cheatsheet v22_witness
```

Raw simulator form:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe sim_lab.py --data data/benchmark/normal_balanced10_true5_false5_seed0.jsonl --cheatsheet cheatsheets/v22_witness.txt --openrouter --model meta-llama/llama-3.3-70b-instruct
```

## Tutorials

- Full cheatsheet playbook: `TUTORIAL_CHEATSHEET_PLAYBOOK.md`
- Script and skill index: `TUTORIAL_SCRIPT_SKILLS.md`
- Competition constraints and scoring: `RULESET.md`

## Script and Skill Map

This repo has three practical skill groups that drive cheatsheet work.

### 1) Evaluate and Gate (truth source for promotion)

- `sim_lab.py`: paid-model evaluator (OpenRouter), strict parsing/scoring, JSON result payloads.
- `run_paid_eval.ps1`: convenience wrapper for common paid benchmark runs.
- `scoreboard.py`: aggregates run outputs to leaderboard-style summaries.

Use when: you need pass/fail evidence for a candidate cheatsheet.

### 2) Distill and Forensics (convert failures into actionable rules)

- `distill.py`: failure taxonomy and pattern library from run artifacts.
- `analyze_seed_failures.py`: per-case fail ledger with corrected certificates.
- `v22_coverage_analysis.py`: coverage audits for structural/witness/oracle lanes.
- `v22_mine_sound_rules.py`: globally sound invariant mining against matrix truth.

Use when: hard misses or regressions must be explained and translated into candidate rule changes.

### 3) Teorth/Proof Data Skills (source-backed certificates)

- `fetch_teorth_data.py`: fetches and caches Teorth data (`graph.json`, `full_entries.json`, equations).
- `teorth_true_proof_agent.py`: attaches Teorth graph/full_entries provenance to benchmark pairs.
- `proof_scraping_lab.py`: bulk scrape lab for many `show_proof.html?pair=a,b` pages.
- `v21_data_infrastructure.py`: equation mapping, witness masks, matrix-grounded implication lookup.

Use when: you need auditable theorem/counterexample source trails and proof-page mining at scale.

## Complete Script Index

### Core Pipeline

- `sim_lab.py`: canonical evaluator.
- `run_paid_eval.ps1`: fast paid runs.
- `run_vnext_search_v2.ps1`: orchestration wrapper for V2 search actions.
- `vnext_search_v2.py`: candidate search, gate checks, decision artifacts.
- `vnext_search_v2_config.json`: search and gate configuration.

### Cheatsheet Construction and Validation

- `v22_build_cheatsheet.py`: build/assemble v22 cheatsheet variants.
- `v22_test_jinja2.py`: template rendering + benchmark correctness checks + size checks.
- `_test_v22_render.py`: ad-hoc rendering tests.

### Distillation and Rule Mining

- `distill.py`: pattern extraction from failures.
- `v22_coverage_analysis.py`: lane-level coverage accounting.
- `v22_mine_sound_rules.py`: sound rule mining from full matrix.
- `analyze_seed_failures.py`: fail-ledger generation.

### Data and Proof Utilities

- `fetch_teorth_data.py`: fetch/cache Teorth assets.
- `teorth_true_proof_agent.py`: add graph/full_entries source metadata.
- `proof_scraping_lab.py`: bulk scrape proof pages by pair IDs.
- `make_unseen_30_30_sets.py`: generate unseen balanced seed sets.
- `v21_data_infrastructure.py`: matrix/equation/witness infrastructure.
- `v21_verify_structural_rules.py`: structural rule verification utilities.

### Atlas / Research Helpers

- `proof_atlas.py`: build proof atlas artifacts.
- `atlas_public_dev.py`: build public-corpus atlas and candidate variants.
- `test_proof_atlas.py`, `test_atlas_public_dev.py`: tests.

### Misc

- `invoke_copilot_candidate.py`: candidate invocation helper.

## Canonical Workflows (Cheatsheet-Centric)

### Workflow A: Evaluate Current Cheatsheet

1. Run paid eval on normal/hard seeds with `sim_lab.py`.
2. Inspect `results/sim_*.json` and `results/scoreboard.md`.
3. Gate decision: keep, patch, or revert.

### Workflow B: Distill Failures into Safe Changes

1. Build ledger: `analyze_seed_failures.py`.
2. Build pattern summary: `distill.py`.
3. Add proof provenance: `teorth_true_proof_agent.py`.
4. Propose compact deterministic changes (witness/oracle/structural), not benchmark memorization.

### Workflow C: Mine Proof Chains in Bulk

1. Choose pair source (`--pairs`, `--pairs-file`, `--from-jsonl`, `--from-results`).
2. Scrape: `proof_scraping_lab.py`.
3. Use JSONL/MD outputs to identify reusable theorem/fact families.

### Workflow D: Build and Validate a New Candidate

1. Edit candidate in `cheatsheets/`.
2. Validate template and budget with `v22_test_jinja2.py`.
3. Re-run paid normal safety gates first.
4. Run hard campaigns and ledger.
5. Promote only when safety and uplift criteria pass.

## Benchmark and Data Notes

- Benchmarks: `data/benchmark/`.
- HF caches: `data/hf_cache/`.
- Teorth caches: `data/teorth_cache/`.
- Dense implications matrix: `data/exports/export_raw_implications_14_3_2026.csv`.
- Equation catalog: `data/exports/equations.txt`.

## Results and Artifacts

- Run payloads: `results/sim_*.json`.
- Scoreboard: `results/scoreboard.md`, `results/scoreboard.csv`.
- Gate summaries/ledgers/plans: `results/phase5_*.md`.
- Proof scrape outputs: `results/proof_lab/*.jsonl`, `results/proof_lab/*.md`.

## Practical Guardrails

1. Keep cheatsheets under 10,240 bytes on disk.
2. Prefer deterministic witnesses and graph-backed certificates.
3. Do not hardcode exact benchmark pairs as oracle policy.
4. Do not promote with normal regression.
5. Treat paid seeds and fail ledgers as source-of-truth for decisions.

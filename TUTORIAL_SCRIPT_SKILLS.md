# Script and Skills Tutorial

This document explains what each script does and which practical skill it supports for cheatsheet development.

## Skill Families

1. Evaluation skill: run reliable paid-model benchmarks and compare candidates.
2. Distillation skill: convert failures into compact, reusable decision rules.
3. Proof skill: attach theorem/facts provenance and finite certificates.
4. Promotion skill: enforce safety gates and decide champion status.

## Script-by-Script Guide

## Evaluation Skill

- `sim_lab.py`
  - Purpose: canonical paid evaluator and report writer.
  - Input: benchmark JSONL or HF subset, cheatsheet template.
  - Output: `results/sim_*.json`.

- `run_paid_eval.ps1`
  - Purpose: convenience wrapper around simulator calls.
  - Input: benchmark stem and cheatsheet label.
  - Output: standard run payloads under `results/`.

- `scoreboard.py`
  - Purpose: summarize run payloads and costs.
  - Output: `results/scoreboard.md`, `results/scoreboard.csv`.

## Distillation Skill

- `distill.py`
  - Purpose: classify errors and build pattern library for prompt iteration.
  - Output: taxonomy, pattern library, and markdown brief.

- `analyze_seed_failures.py`
  - Purpose: build a fail ledger with corrected certificates.
  - Output: markdown ledger for postmortem and promotion review.

- `v22_coverage_analysis.py`
  - Purpose: quantify which lanes (structural/witness/oracle) catch false cases.
  - Output: coverage report for deciding what to patch.

- `v22_mine_sound_rules.py`
  - Purpose: mine globally sound invariant separators from matrix truth.
  - Output: candidate rule stats and dataset coverage diagnostics.

## Proof Skill

- `fetch_teorth_data.py`
  - Purpose: fetch/cache Teorth assets (`graph.json`, `full_entries.json`, equations, duals).

- `teorth_true_proof_agent.py`
  - Purpose: attach graph/full_entries source metadata to benchmark rows.
  - Typical use: certify-benchmark mode for provenance artifacts.

- `proof_scraping_lab.py`
  - Purpose: bulk scrape many proof pages (`show_proof.html?pair=a,b`).
  - Pair sources: inline pairs, pair file, benchmark jsonl, sim results.
  - Output: JSONL + markdown report.

- `v21_data_infrastructure.py`
  - Purpose: equation-ID mapping, witness masks, matrix lookups.
  - Often used by distillation and forensic scripts.

- `v21_verify_structural_rules.py`
  - Purpose: authoritative checks for LP/RP/C0/VARS/XOR/Z3A/XNOR soundness.

## Candidate Build Skill

Cheatsheets use only `{{equation1}}` and `{{equation2}}` substitution. No Jinja2 logic allowed.

## Search and Promotion Skill

- `vnext_search_v2.py`
  - Purpose: evaluate candidate mutations under strict anti-collapse policy.

- `run_vnext_search_v2.ps1`
  - Purpose: run workflow actions (`init`, `cycle`, `loop`, `replay-check`).

- `vnext_search_v2_config.json`
  - Purpose: policy and gate configuration.

## Atlas/Research Skill

- `proof_atlas.py`
  - Purpose: research atlas artifacts and candidate generation.

- `atlas_public_dev.py`
  - Purpose: public-corpus development datasets/reports/variants.

- `test_proof_atlas.py`, `test_atlas_public_dev.py`
  - Purpose: regression checks for atlas tooling.

## Recommended Usage Pattern

1. Evaluate baseline (`sim_lab.py`).
2. Distill failures (`analyze_seed_failures.py`, `distill.py`).
3. Attach proof sources (`teorth_true_proof_agent.py`, optional `proof_scraping_lab.py`).
4. Patch candidate (`cheatsheets/*.txt`).
5. Validate template and rerun normal safety gates before hard gates.
6. Promote only with explicit no-regression evidence.

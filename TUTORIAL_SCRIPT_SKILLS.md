# Script and Skills Tutorial

This document maps the repo by role so humans and agents can find the right path quickly.

## Read This After

1. `README.md`
2. `EVAL_WORKFLOW.md`
3. `RESTART_CHECKLIST.md`

## Canonical Roles

### 1. Evaluate And Gate

Use this role when you need benchmark evidence or a promotion decision.

- `sim_lab.py`
  - Canonical paid evaluator
  - Inputs: benchmark JSONL, cheatsheet template
  - Outputs: `results/sim_*.json`

- `run_paid_eval.ps1`
  - Quick wrapper for standard benchmark runs
  - Best starting command for routine evaluation

- `scoreboard.py`
  - Summarizes run payloads and costs
  - Outputs: `results/scoreboard.md`, `results/scoreboard.csv`

Artifact note:

- `results/sim_*.json` are local working payloads and should be treated as disposable once distilled or summarized.
- `results/scoreboard.md` and `results/scoreboard.csv` are the preferred retained summaries.

Start here if your question is: "How is the current cheatsheet performing?"

### 2. Distill And Forensics

Use this role when a run failed and you need a mathematically grounded explanation.

- `analyze_seed_failures.py`
  - Builds a fail ledger with corrected certificates

- `distill.py`
  - Groups failures into reusable patterns

- `v22_coverage_analysis.py`
  - Measures which rule lanes cover false cases

- `v22_mine_sound_rules.py`
  - Mines globally sound separators from matrix truth

Start here if your question is: "Why did this benchmark fail, and what safe edit follows from it?"

### 3. Proof And Source Grounding

Use this role when you need provenance, theorem backing, or proof-page mining.

- `fetch_teorth_data.py`
  - Refreshes Teorth assets and caches

- `teorth_true_proof_agent.py`
  - Attaches graph/full_entries source metadata to benchmark rows

- `proof_scraping_lab.py`
  - Bulk proof-page scraping for deeper provenance work

- `v21_data_infrastructure.py`
  - Equation IDs, matrix lookups, witness masks

- `v21_verify_structural_rules.py`
  - Soundness verification helper for structural rules

Start here if your question is: "Can we justify this TRUE or FALSE with source-backed evidence?"

### 4. Patch The Candidate

This repo patches cheatsheets directly.

Rules:

1. Cheatsheets live in `cheatsheets/`
2. Only `{{equation1}}` and `{{equation2}}` substitution is allowed
3. No Jinja2 logic is allowed
4. Simpler, sounder prompts beat larger brittle prompts

Main files:

- `cheatsheets/v21f_structural.txt`
- `cheatsheets/v23.txt`

### 5. Optional And Research Paths

These are not the canonical starting points for most tasks:

- `vnext_search_v2.py`
- `run_vnext_search_v2.ps1`
- `vnext_search_v2_config.json`
- `proof_atlas.py`
- `atlas_public_dev.py`
- `invoke_copilot_candidate.py`

Use them only when the task explicitly calls for search orchestration, atlas work, or broader research tooling.

## Recommended Usage Pattern

1. Evaluate current baseline or candidate.
2. Distill failures.
3. Add proof grounding if needed.
4. Patch the cheatsheet.
5. Re-run normal safety gates.
6. Only then run hard or unseen stress.
7. Promote only with explicit no-regression evidence.

# magma-ai

Cheatsheet-first tooling for SAIR Equational Theories Stage 1.

This repo exists to produce one competition-ready text cheatsheet under 10,240 bytes that answers:

"Does equation1 imply equation2 over all magmas?"

The operating priority is:

1. Math and rule soundness first.
2. Normal-set safety before any hard-set uplift.
3. Reproducible paid-model evidence before promotion.

Paid OpenRouter evaluation is the supported inference path in this repo.

## Current State

- **Champion: `cheatsheets/v24j.txt`** (8,955 bytes, 87.4% of cap)
- Previous champion: `cheatsheets/v21f_structural.txt` (historical)
- Canonical evaluator: `sim_lab.py`
- Canonical quick-run wrapper: `run_paid_eval.ps1`
- Current strategy: pure natural-language cheatsheet with 4 structural tests + T3R algebraic rescue

## Hard Constraints

1. Submission artifact is one file in `cheatsheets/`.
2. Cheatsheet must stay at or below 10,240 bytes on disk.
3. Only `{{equation1}}` and `{{equation2}}` substitution is allowed.
4. Jinja2 logic is banned. No `set`, `if`, `for`, macros, gap tables, or computed lookup logic in the cheatsheet.
5. Do not hardcode benchmark pairs as policy.
6. Do not promote a candidate with normal-set regression.

## Start Here

## Canonical Cold-Start Read Order

Follow this order exactly:

1. `README.md`
2. `CURRENT_STATE.md`
3. `AGENTS.md`
4. `.github/copilot-instructions.md`
5. `RESTART_CHECKLIST.md`
6. `EVAL_WORKFLOW.md`
7. `BENCHMARK_MANIFEST.md`
8. `TUTORIAL_CHEATSHEET_PLAYBOOK.md`
9. `TUTORIAL_SCRIPT_SKILLS.md`

For humans:

1. Read this file.
2. Read `CURRENT_STATE.md`.
3. Read `RULESET.md`.
4. Read `EVAL_WORKFLOW.md`.
5. Read `TUTORIAL_CHEATSHEET_PLAYBOOK.md`.

For agents:

1. Follow the canonical cold-start read order above.
2. Use `AGENTS.md` and `.github/copilot-instructions.md` as the repo-specific operating contract.

## Quick Start

Activate the repo venv and set your OpenRouter key:

```powershell
$env:OPENROUTER_API_KEY = "<your_key>"
```

Run a quick baseline check:

```powershell
.\run_paid_eval.ps1 -Benchmark normal_balanced10_true5_false5_seed0 -Cheatsheet v24j
```

Run the active candidate directly:

```powershell
python sim_lab.py --data data/benchmark/normal_balanced10_true5_false5_seed0.jsonl --cheatsheet cheatsheets/v24j.txt --openrouter --model meta-llama/llama-3.3-70b-instruct --playground-parity --errors
```

Check cheatsheet size on disk:

```powershell
(Get-Item "cheatsheets\v24j.txt").Length
```

Refresh the rotating official-like evaluation bundle:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe make_unseen_30_30_sets.py --purge-legacy-unseen
```

That command regenerates fresh balanced slices from the official Hugging Face `normal`, `hard`, and `hard3` subsets and records the latest file paths in `data/benchmark/rotating_official_latest.json`.

## Canonical Workflow

The repo should be approached through one loop only:

1. Evaluate candidate on normal safety gates.
2. Distill failures into a ledger and pattern summary.
3. Patch cheatsheet conservatively.
4. Re-run normal gates.
5. Run full and stress benchmarks only after normal safety holds.
6. Promote only with explicit evidence.

If you are not inside that loop, you are probably in a research or historical path.

## Core Files

### Evaluate and Gate

- `sim_lab.py`: canonical paid evaluator, strict parsing, result JSON output
- `run_paid_eval.ps1`: convenience wrapper for standard paid runs
- `scoreboard.py`: summarizes run payloads into leaderboard-style outputs

### Distill and Forensics

- `distill.py`: converts failures into patterns and candidate edits
- `analyze_seed_failures.py`: builds fail ledgers with corrected certificates
- `v22_coverage_analysis.py`: measures which lanes cover false cases
- `v22_mine_sound_rules.py`: mines globally sound structural rules

### Data and Proof Grounding

- `fetch_teorth_data.py`: fetches and refreshes Teorth assets
- `teorth_true_proof_agent.py`: attaches source-backed proof metadata
- `proof_scraping_lab.py`: bulk proof-page scraper and cached archival crawler
- `proof_construction_atlas.py`: second-pass family extractor for cached proof crawls
- `v21_data_infrastructure.py`: matrix, equation, and witness utilities
- `v21_verify_structural_rules.py`: authoritative rule verification helpers

### Research and Optional Paths

- `vnext_search_v2.py`: search/orchestration path, not the canonical starting point
- `proof_atlas.py`, `atlas_public_dev.py`: research helpers, not required for the standard cheatsheet loop
- `invoke_copilot_candidate.py`: helper script, not a primary entrypoint

## Documentation Map

- `CURRENT_STATE.md`: short-lived operational truth for the current phase
- `EVAL_WORKFLOW.md`: canonical benchmark and promotion flow
- `RESTART_CHECKLIST.md`: cold-start checklist for humans and agents
- `BENCHMARK_MANIFEST.md`: benchmark naming legend and dataset roles
- `TUTORIAL_CHEATSHEET_PLAYBOOK.md`: end-to-end operator tutorial
- `TUTORIAL_SCRIPT_SKILLS.md`: role-based script map
- `RULESET.md`: competition constraints and scoring
- `V23_PLAN.md`: historical planning context
- `V24_MASTER_PROMPT.md`: historical v24 design document
- `V25A_MASTER_PROMPT.md`: next-generation design document

## Benchmarks and Data

- Benchmarks: `data/benchmark/`
- Rotating benchmark manifest: `data/benchmark/rotating_official_latest.json`
- Teorth cache: `data/teorth_cache/`
- Dense implications matrix: `data/exports/export_raw_implications_14_3_2026.csv`
- Equation catalog: `data/exports/equations.txt`
- Results: `results/sim_*.json`
- Scoreboards: `results/scoreboard.md`, `results/scoreboard.csv`

## Local Artifact Hygiene

Treat these as local, disposable artifacts unless a task explicitly needs them:

1. `results/sim_*.json` raw simulator payloads
2. `tmp*/` transient root temp directories
3. intermediate distill temp folders under `results/manual_distill/`

Retention rule:

1. Keep `results/scoreboard.md` and `results/scoreboard.csv` as the human-readable summary layer.
2. Keep raw `results/sim_*.json` only while you are actively diagnosing a run.
3. Delete raw ignored artifacts after summarizing or distilling them.
4. Treat frozen `*_unseen_*.jsonl` benchmark files as deprecated local artifacts; regenerate rotating bundles from the official Hugging Face subsets instead.

## Promotion Rules

1. Normal safety gates must pass before hard-set runs matter.
2. Every FALSE decision path should remain mathematically defensible.
3. Results, ledgers, and provenance must agree before promotion.
4. If a candidate is better on hard but weaker on normal, keep the old champion.

## Anti-Regression Guardrails

1. Do not reintroduce Jinja2 logic into cheatsheets.
2. Do not optimize against one benchmark file at the expense of general rules.
3. Prefer compact, sound structural reasoning over brittle heuristics.
4. Treat run artifacts and failure ledgers as the source of truth.
5. When in doubt, revert to the simpler, safer cheatsheet.

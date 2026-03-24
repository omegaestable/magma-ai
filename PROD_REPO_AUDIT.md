# Production Repository Audit and Slimming

Date: 2026-03-22

## Scope

This audit focused on making the repository production-ready by removing stale generated artifacts, legacy v1 pipeline files, caches, and duplicated data while preserving core source code, benchmarks, and canonical cheatsheets.

## Key Findings

- The largest tracked duplication was `paper/exports_from_magma_ai/export_raw_implications_14_3_2026.csv`, which duplicated `data/exports/export_raw_implications_14_3_2026.csv`.
- Legacy v1 search artifacts and raw run outputs were tracked and caused repository bloat and maintenance noise.
- Python cache files and log files were tracked and should never have been versioned.

## Cleanup Actions Applied

### Removed tracked cache and logs

- `__pycache__/*.pyc`
- `*.log` files committed at repo root

### Removed tracked generated candidate artifacts

- `cheatsheets/generated/*`

### Removed tracked raw simulator outputs

- `results/sim_*.json`
- legacy `results/vnext_search/*` artifacts

### Removed deprecated v1 pipeline files

- `vnext_search.py`
- `vnext_search_config.json`
- `run_vnext_search.ps1`
- `monitor_vnext_search.ps1`
- `invoke_copilot_candidate.ps1`

### Removed duplicated export payload

- `paper/exports_from_magma_ai/*` (duplicate of `data/exports/*`)

## Ignore Policy Added

A new `.gitignore` was added to prevent reintroducing junk:

- Python env/cache: `.venv/`, `__pycache__/`, `*.py[cod]`
- Logs: `*.log`
- Generated cheatsheets: `cheatsheets/generated/`, `cheatsheets/generated_v2/`
- Raw run outputs: `results/sim_*.json`
- Local/legacy search artifacts under `results/vnext_search*`

## Documentation Alignment

- `README.md` was updated to retire v1 workflow references.
- V2 pipeline is the only supported workflow path.
- `distill.py` usage text/default out-dir now points to v2 paths.

## Measured Impact

- File count dropped from 1464 to 1358 files.
- Workspace footprint dropped from 145.99 MB to 80.21 MB.
- Staged deletion summary: 107 files removed.

## Production Hygiene Rules Going Forward

1. Never commit raw run JSON artifacts from `results/sim_*.json`.
2. Never commit candidate scratch outputs from `cheatsheets/generated*`.
3. Keep only summarized, curated result artifacts (for example `results/scoreboard.md`, `results/scoreboard.csv`) when needed.
4. Use v2 pipeline only; do not reintroduce v1 scripts.
5. Treat `data/exports/*` as the canonical export location; avoid mirrored copies.

## 2026-03-24 Trim Pass

This follow-up trim removed transient artifacts created during prompt-iteration and diagnosis work while preserving canonical prompts, curated distillation outputs, benchmarks, and scoreboard summaries.

### Removed

- Root-level exploratory helpers: `_leaf_check.py`, `_magma_check.py`, `_magma_search.py`
- Temporary diagnosis distill outputs under `results/manual_distill/_tmp_v19_diag/`
- Temporary post-patch distill outputs under `results/manual_distill/_tmp_v19_postpatch/`
- Scratch candidate prompts under `cheatsheets/generated_v2/`
- Raw simulator result payloads under `results/sim_*.json`

### Policy Update

- Ignore `results/manual_distill/_tmp_*/` so temporary diagnosis artifacts stay local by default.

### Notes

- Curated manual distill directories and canonical prompt files were intentionally retained.
- Python cache files remain covered by ignore rules; if any tracked `.pyc` files are still present locally they should be removed outside the text patch path because the patch tool does not handle those binary deletions reliably.

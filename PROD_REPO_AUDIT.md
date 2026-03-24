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

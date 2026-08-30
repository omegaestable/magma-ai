# Theory Tool Index

The scripts in this directory support Stage 2 math extraction, Teorth provenance checks, witness mining, and problem-set hygiene. They are research and development tools; submitted solver code must remain a single self-contained `solver.py`.

Run commands from the repo root in PowerShell unless a command uses `Push-Location theory\tools`.

## Cache And Problem-Set Hygiene

- `fetch_teorth_data.py`: downloads or checks Teorth assets in `data/teorth_cache/`, including `graph.json`, `full_entries.json`, `duals.json`, `smallest_magma.txt`, and the equation catalog.
- `fetch_problem_sets.py`: maintains local mirrors of problem-set data.
- `problem_set_catalog.py`: central policy for root `data/hf_cache/` subsets and `data/stage2_official_problems/` mirrors.
- `smoke_problem_sets.py`: fast path check for official problem mirrors and analysis-only subsets.

Useful commands:

```powershell
Push-Location theory\tools
..\..\.venv311\Scripts\python.exe fetch_teorth_data.py --check
Pop-Location

.\.venv311\Scripts\python.exe theory\tools\smoke_problem_sets.py
```

Use `fetch_teorth_data.py --force` only when intentionally syncing from network. Record the upstream commit/timestamp from the live Teorth implication explorer when a cache refresh matters for team memory.

## Graph And Provenance Query

- `teorth_true_proof_agent.py`: decodes selected cells from the Teorth implication graph, joins `full_entries.json`, and labels benchmark pairs as explicit/implicit proof/conjecture/unknown.
- `v21_data_infrastructure.py`: shared equation loading, normalization, and mapping helpers.
- `atlas_public_dev.py`: public-development atlas helpers.

Use these before scraping proof pages. Cached graph/provenance is faster, reproducible, and enough to decide whether a pair is worth deeper proof-page work.

## Proof-Page Scraping And Atlas Building

- `proof_scraping_lab.py`: focused or recursive scraper for Teorth proof pages such as `show_proof.html?pair=310,118`.
- `proof_construction_atlas.py`: second pass over scraped proof pages; joins `full_entries.json` and classifies recurring construction families.
- `proof_atlas.py`: family-template definitions used by atlas tooling.

Keep scraping focused. Prefer `--pairs`, `--pairs-file`, or failure-ledger-derived inputs. Store durable outputs under `stage2/results/` with a date-stamped name; keep exploratory cache files out of the submitted solver path.

## Structural Rule And Witness Mining

- `v22_mine_sound_rules.py`: mines candidate structural rules.
- `v22_coverage_analysis.py`: analyzes coverage for mined rules and solver routes.
- `v21_verify_structural_rules.py`: verifies structural rules against local data.
- `spine_classify.py`: classifies equation spine/shape features for route triggers.

FALSE witness candidates should pass local semantic validation before becoming named witnesses or formulaic solver families. TRUE structural rules should become standalone Lean certificate templates and pass the official runner before promotion.

## Benchmark And Coverage Products

Use tool outputs to create small, reviewable artifacts:

- pair status ledgers with equation ids, Teorth graph status, and proof-page links
- construction-family atlases for TRUE proof motifs and FALSE witnesses
- route-coverage summaries tied to `stage2/results/` failure ledgers
- motif cards following `theory/TEORTH_WORKFLOW.md`

Do not treat analysis-only Hugging Face `evaluation_*` subsets as official benchmark evidence. They are useful for route discovery, not promotion claims, unless explicitly added to an official workflow later.

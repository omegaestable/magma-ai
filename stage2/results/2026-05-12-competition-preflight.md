# Competition Preflight

Date: 2026-05-12

## Packaging

- submission entries: ['solver.py']
- solver size bytes: 247239
- single-file layout ok: True

## Data Caches

- hf manifest: present
- official stage2 mirror manifest: present

## Tool Imports

- `atlas_public_dev.py`: ok
- `proof_atlas.py`: ok
- `proof_construction_atlas.py`: ok
- `smoke_problem_sets.py`: ok

## Public Result Coverage

- `normal`: problems=1000, result_rows=1000, solved=743, exists=True
- `hard1`: problems=69, result_rows=69, solved=17, exists=True
- `hard2`: problems=200, result_rows=200, solved=52, exists=True
- `hard3`: problems=400, result_rows=400, solved=186, exists=True

## Marathon Budget Ambiguity

- docs/marathon_mode.md mentions `600 s/problem`: True
- rules/evaluation.md mentions `3600 s/problem`: True
- local recommendation: parameterize preflight and long-run tests for both reference values


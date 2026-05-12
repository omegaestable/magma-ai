# Latest Handoff

Updated: 2026-05-12

This is the compressed team-memory note for the current Stage 2 solver state.

## What Changed

- The solver is no longer false-only.
- New accepted deterministic TRUE routes exist for:
  - `true:reflexive`
  - `true:singleton`
  - `true:rewrite`
  - `true:rewrite:symm`
  - `true:bridge:11`
- The FALSE lane still keeps named compact witnesses first, but now also tries
  affine/linear finite families before bounded brute-force enumeration.
- Marathon ordering is now route-aware and has a local budget-interpretation
  knob: `MAGMA_MARATHON_REF_SECONDS_PER_PROBLEM`.

## Best Public Evidence

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`, `llm:0`
- `normal`: `743/1000` solved, `245 TRUE + 498 FALSE`, `llm:0`
- `hard1`: `17/69` solved, all `FALSE`, `llm:0`
- `hard2`: `52/200` solved, all `FALSE`, `llm:0`
- `hard3`: `186/400` solved, `3 TRUE + 183 FALSE`, `llm:0`

Public total: `998/1669` solved, `248 TRUE + 750 FALSE`, `llm:0`.

Canonical generated evidence:

- `stage2/results/2026-05-12-public-finite-countermodels-summary.md`
- `stage2/results/2026-05-12-public-failure-ledger.jsonl`
- `stage2/results/2026-05-12-competition-preflight.md`

## Highest-Value Learnings

1. `true:singleton` is the current dominant TRUE lane by a mile.
2. `LP`, `RP`, and `C0` still dominate the compact FALSE route inventory.
3. Small affine/linear families are already contributing on harder FALSE sets,
   especially over `z3` and `z5`; this lane is worth expanding.
4. The remaining public frontier is mostly TRUE work:
   - `571` `true_template_gap`
   - `100` `finite_countermodel_gap`
5. `hard1` stayed flat while `normal` jumped sharply. That means the current
   TRUE gain is real but concentrated; we still need stronger proof families
   and more structured hard FALSE witnesses.

## Operational Cautions

1. The official judge answer JSON must contain exactly `verdict` and `code`.
   Do not try to include route labels or metadata in the submitted payload.
   Put those in solver stderr and result summaries instead.
2. The current packaged solver is about `20 KB`, still far below the `500 KB`
   limit, but no longer the tiny `8.7 KB` baseline.
3. The official docs currently disagree on Marathon wall-clock reference:
   `docs/marathon_mode.md` uses `600 s/problem`, while
   `rules/evaluation.md` describes `3600 s/problem`-derived budgeting.
   Keep local tests parameterized for both.
4. The imported Hugging Face `evaluation_*` subsets remain analysis-only until
   explicitly promoted into an official workflow.

## Recommended Next Steps

1. Mine the failure ledger for reusable TRUE motifs before touching LLMs.
2. Add more safe rewrite/closure templates that render as explicit Lean proofs.
3. Expand the affine/linear and other structured finite witness families before
   increasing brute-force search bounds.
4. Rerun `scripts/run_harness.py` and `scripts/run_marathon_harness.py` before
   calling the upgraded solver a promotion candidate.
5. After major solver changes, rerun:

```powershell
.\stage2\solver\package_solver.ps1
.\.venv\Scripts\python.exe theory\tools\smoke_problem_sets.py
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\normal.jsonl --output ..\..\stage2\results\2026-05-12-normal-finite-countermodels.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\hard1.jsonl --output ..\..\stage2\results\2026-05-12-hard1-finite-countermodels.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\hard2.jsonl --output ..\..\stage2\results\2026-05-12-hard2-finite-countermodels.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\hard3.jsonl --output ..\..\stage2\results\2026-05-12-hard3-finite-countermodels.json
Pop-Location
.\.venv\Scripts\python.exe stage2\experiments\summarize_public_benchmarks.py
.\.venv\Scripts\python.exe stage2\experiments\competition_preflight.py
```

# Latest Handoff

Updated: 2026-05-13

This is the compressed team-memory note for the current Stage 2 solver state.

## What Changed

- The solver is no longer false-only.
- New accepted deterministic TRUE routes exist for:
  - `true:reflexive`
  - `true:singleton`
  - `true:rewrite`
  - `true:rewrite:symm`
  - `true:bridge:11`
   - `true:projection:right`
- The FALSE lane still keeps named compact witnesses first, but now also tries
   structured tables, affine/quadratic finite families, dualized witnesses, and
   bounded brute-force enumeration.
- Larger named compact witnesses are allowed independently of the brute-force
   `Fin 2..3` bound. Recent additions include `S4A` and `S5A`.
- `Fin 7+` false certificates set `maxRecDepth 20000` so `decideFin!` can
   finish under the official runner.
- Marathon ordering is now route-aware and has a local budget-interpretation
  knob: `MAGMA_MARATHON_REF_SECONDS_PER_PROBLEM`.

## Best Public Evidence

Canonical full public benchmark evidence remains the 2026-05-12 generated run:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`, `llm:0`
- `normal`: `743/1000` solved, `245 TRUE + 498 FALSE`, `llm:0`
- `hard1`: `17/69` solved, all `FALSE`, `llm:0`
- `hard2`: `52/200` solved, all `FALSE`, `llm:0`
- `hard3`: `186/400` solved, `3 TRUE + 183 FALSE`, `llm:0`

Public total: `998/1669` solved, `248 TRUE + 750 FALSE`, `llm:0`.

Latest local smoke-only evidence from 2026-05-13:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`
- `sample_200`: `165/200` solved; all remaining sample misses are TRUE
- Marathon `normal_100`, zero token budget: `70/100` accepted, `0` tokens
- packaged solver size: `52098` bytes
- focused hard3 TRUE probe: `hard3_0001` accepted via `true:projection:right`; `hard3_0002` reached the LLM path and failed locally because no upstream key was set

Canonical generated evidence:

- `stage2/results/2026-05-12-public-finite-countermodels-summary.md`
- `stage2/results/2026-05-12-public-failure-ledger.jsonl`
- `stage2/results/2026-05-12-competition-preflight.md`

## Highest-Value Learnings

1. `true:singleton` is the current dominant TRUE lane by a mile.
2. `LP`, `RP`, and `C0` still dominate the compact FALSE route inventory.
3. Small affine/linear families are already contributing on harder FALSE sets,
   especially over `z3` and `z5`; this lane is worth expanding.
4. `Fin 7` table certificates can fail with Lean max recursion depth unless
   the emitted certificate includes `set_option maxRecDepth 20000` before
   `decideFin!`.
5. Direct `judge.verify.verify_answer(problem, ...)` is not runner-equivalent
   because it omits the pipeline default proof policy. Use the official runner
   or `verify_answer(_to_judge_problem(problem), raw_answer)` for certificate
   debugging.
6. The remaining public frontier is mostly TRUE work:
   - `571` `true_template_gap`
   - `100` `finite_countermodel_gap`
7. `hard1` stayed flat while `normal` jumped sharply. That means the current
   TRUE gain is real but concentrated; we still need stronger proof families
   and more structured hard FALSE witnesses.

## Operational Cautions

1. The official judge answer JSON must contain exactly `verdict` and `code`.
   Do not try to include route labels or metadata in the submitted payload.
   Put those in solver stderr and result summaries instead.
2. The current packaged solver is `52098` bytes, still far below the `500 KB`
   limit.
3. The official docs currently disagree on Marathon wall-clock reference:
   `docs/marathon_mode.md` uses `600 s/problem`, while
   `rules/evaluation.md` describes `3600 s/problem`-derived budgeting.
   Keep local tests parameterized for both.
4. The imported Hugging Face `evaluation_*` subsets remain analysis-only until
   explicitly promoted into an official workflow.
5. Custom local Solo knobs may be stripped by the official proxy environment.
   Treat proxy/runner behavior as authoritative.
6. Local `OPENAI_API_KEY or OPENROUTER_API_KEY not set` errors mean the local
   runner proxy lacks an upstream credential, not that the submitted solver has
   access to missing secrets.
7. `tmp_stage2_smoke/` is for local debugging. Promote durable evidence into
   `stage2/results/` before citing it as benchmark proof.

## Playground Readiness

Use `stage2/docs/playground-preflight.md` before upload or playground checks.
The current packaged solver is deterministic-ready under the official
single-file and proxy contracts: `stage2/submissions/` contains only
`solver.py`, the file is below the 500 KB cap, deterministic certificates have
official runner evidence, and unresolved cases use the proxy LLM protocol. Full
LLM success still depends on the playground proxy being enabled and configured.

## Recommended Next Steps

1. Mine the failure ledger for reusable TRUE motifs before touching LLMs.
2. Use `theory/TEORTH_WORKFLOW.md` to move from Teorth graph/proof-page/paper
   evidence into small motif cards with Lean rendering sketches.
3. Add more safe rewrite/closure templates that render as explicit Lean proofs.
4. Expand the affine/linear and other structured finite witness families before
   increasing brute-force search bounds.
5. Rerun `scripts/run_harness.py` and `scripts/run_marathon_harness.py` before
   calling the upgraded solver a promotion candidate.
6. Run `stage2/docs/playground-preflight.md` before upload/playground testing.
7. After major solver changes, rerun:

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

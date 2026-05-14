# Current State

This file is the short-lived operational truth for the Stage 2 lab. Update it when the active solver, harness snapshot, validation evidence, or upstream rules change.

Last updated: 2026-05-13.

## Stage

- Active competition: SAIR Equational Theories Stage 2.
- Deadline: August 31, 2026, 23:59 AoE.
- Submission artifact: one `solver.py` file, <= 500 KB.
- Preferred track focus: Marathon first, with shared logic for Solo.
- Proof standard: official Lean 4 judge acceptance.

## Current Artifacts

- Official harness snapshot: `vendor/stage2-official/` at upstream commit `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.
- Local solver scaffold: `stage2/solver/solver.py`.
- Packaged submission target: `stage2/submissions/solver.py`.
- Latest compressed handoff: `stage2/docs/LATEST_HANDOFF.md`.
- Theory extraction workflow: `theory/TEORTH_WORKFLOW.md`.
- Theory tool index: `theory/tools/README.md`.
- Stage 1 archive: `stage1/`.
- Shared theory cache: `data/exports/` and `data/teorth_cache/`.

## Current Solver Capability

The active solver is still conservative, but no longer reflexivity-only:

1. Detects Marathon mode from official environment variables.
2. Detects Solo mode from stdin JSON.
3. Emits a TRUE certificate for the trivial case `eq1_id == eq2_id`.
4. Emits TRUE certificates for singleton/collapse implications where `eq1` forces one-element models.
5. Emits TRUE certificates for exact substitution instances, short bridge/constancy chains, and bounded subterm rewrite chains.
6. Searches finite FALSE witnesses using named compact witnesses, structured table families, affine/quadratic finite families, dualized witnesses, and bounded `Fin 2..3` enumeration.
7. Emits FALSE certificates with `finOpTable` and `decideFin!`; larger `Fin 7+` tables get `set_option maxRecDepth 20000` to avoid Lean recursion-depth failures.
8. Skips unresolved problems rather than submitting speculative certificates.

## Current Smoke Status

Python-side packaging and lint smokes pass. The packaged submission directory must contain only `solver.py`; the official Solo runner rejects extra entries such as `.gitkeep` or `__pycache__` before executing the solver.

Native Windows Lean is installed through Elan and pinned to the official `leanprover/lean4:v4.30.0-rc2` toolchain. The vendored Lean project builds locally with Lake.

Current Windows evidence, after documented local compatibility patches under `vendor/stage2-official/UPSTREAM.md`:

1. `scripts/run_harness.py`: green, with 66/66 judge cases, 79/79 public attacks, 55/55 pipeline regressions, 32/32 judge internals, 11/11 submit CLI checks, and no failing buckets.
2. `scripts/run_marathon_harness.py`: green, 25/25 checks with Lean available.
3. Packaged local solver: `stage2/submissions/solver.py` at 49483 bytes, with `stage2/submissions/` containing only `solver.py`.
4. Official Solo runner on `examples/problems/sample_20.json`: 14/20 solved, with 4 TRUE + 10 FALSE certificates, `llm:0`.
5. Official Solo runner on `examples/problems/sample_200.json`: 165/200 solved after the `Fin 7` recursion-depth fix and `S4A`/`S5A` witnesses; the remaining 35 smoke misses are all TRUE cases.
6. Official Marathon runner on `examples/problems/marathon/normal_100.jsonl` with zero token budget: 70/100 accepted, with 70 attempted and no rejected certificates.
7. Canonical full public benchmark totals remain from the 2026-05-12 generated evidence until the full public suite is rerun:
   - `normal.jsonl`: 743/1000 solved, with 245 TRUE + 498 FALSE, `llm:0`.
   - `hard1.jsonl`: 17/69 solved, all FALSE, `llm:0`.
   - `hard2.jsonl`: 52/200 solved, all FALSE, `llm:0`.
   - `hard3.jsonl`: 186/400 solved, with 3 TRUE + 183 FALSE, `llm:0`.
8. Generated team-memory artifacts:
   - `stage2/results/2026-05-12-public-finite-countermodels-summary.md`
   - `stage2/results/2026-05-12-public-failure-ledger.jsonl`
   - `stage2/results/2026-05-12-competition-preflight.md`

Recent operational lessons:

1. For runner-equivalent certificate debugging, use the official runner or call `verify_answer(_to_judge_problem(problem), raw_answer)`. A direct `verify_answer(problem, ...)` omits the pipeline default proof policy and can report disallowed `propext`, `Classical.choice`, or `Quot.sound` for certificates accepted by the runner.
2. Custom local Solo environment knobs can be stripped by the official proxy environment; do not rely on them for official-run behavior.
3. `tmp_stage2_smoke/` files are temporary smoke/debug artifacts. Promote evidence to `stage2/results/` with a date-stamped name before treating it as team memory.

## Upstream TBDs

Keep these configurable:

1. Final scoring and tie-breakers.
2. Final model/provider/route.
3. Final generation parameters.
4. Private problem-set size and composition.
5. Marathon compression ratio and sandbox resource limits if upstream changes them.

## Immediate Next Work

1. Attack the 571 remaining public TRUE gaps with additional safe rewrite templates, closure-backed short derivations, and Teorth-guided motif cards.
2. Expand deterministic FALSE routes for the 100 remaining public FALSE gaps, prioritizing reusable formulaic families and named compact witnesses over brute-force bound increases.
3. Mine the route histogram, failure ledger, Teorth implication graph, proof pages, and paper notes into solver-facing route labels and witness/proof families.
4. Keep Marathon triage parameterized for the 600s-vs-3600s reference-budget doc ambiguity.
5. Keep Windows vendor patches documented and rerun both official harnesses after upstream syncs.

## Non-Goals

1. Do not edit archived Stage 1 cheatsheets as active solver work.
2. Do not promote any certificate template without official judge acceptance.
3. Do not rely on Teorth theorem imports unless the official judge allowlist explicitly permits them.

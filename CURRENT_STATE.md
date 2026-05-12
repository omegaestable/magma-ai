# Current State

This file is the short-lived operational truth for the Stage 2 lab. Update it when the active solver, harness snapshot, validation evidence, or upstream rules change.

Last updated: 2026-05-12.

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
- Stage 1 archive: `stage1/`.
- Shared theory cache: `data/exports/` and `data/teorth_cache/`.

## Current Solver Capability

The active solver is still conservative, but no longer reflexivity-only:

1. Detects Marathon mode from official environment variables.
2. Detects Solo mode from stdin JSON.
3. Emits a TRUE certificate for the trivial case `eq1_id == eq2_id`.
4. Emits TRUE certificates for singleton/collapse implications where `eq1` forces one-element models.
5. Emits TRUE certificates for exact substitution instances and short two-instance rewrite chains.
6. Searches finite FALSE witnesses using a named witness pass, affine/linear magma families, and bounded `Fin 2..3` enumeration.
7. Emits FALSE certificates with `finOpTable` and `decideFin!`.
8. Skips unresolved problems rather than submitting speculative certificates.

## Current Smoke Status

Python-side packaging and lint smokes pass. The packaged submission directory must contain only `solver.py`; the official Solo runner rejects extra entries such as `.gitkeep` or `__pycache__` before executing the solver.

Native Windows Lean is installed through Elan and pinned to the official `leanprover/lean4:v4.30.0-rc2` toolchain. The vendored Lean project builds locally with Lake.

Current Windows evidence, after documented local compatibility patches under `vendor/stage2-official/UPSTREAM.md`:

1. `scripts/run_harness.py`: green, with 66/66 judge cases, 79/79 public attacks, 55/55 pipeline regressions, 32/32 judge internals, 11/11 submit CLI checks, and no failing buckets.
2. `scripts/run_marathon_harness.py`: green, 25/25 checks with Lean available.
3. Packaged local solver: `stage2/submissions/solver.py` at 19990 bytes.
4. Official Solo runner on `examples/problems/sample_20.json`: 14/20 solved, with 4 TRUE + 10 FALSE certificates, `llm:0`.
5. Public `normal.jsonl`: 743/1000 solved, with 245 TRUE + 498 FALSE, `llm:0`.
6. Public `hard1.jsonl`: 17/69 solved, all FALSE, `llm:0`.
7. Public `hard2.jsonl`: 52/200 solved, all FALSE, `llm:0`.
8. Public `hard3.jsonl`: 186/400 solved, with 3 TRUE + 183 FALSE, `llm:0`.
9. Generated team-memory artifacts:
   - `stage2/results/2026-05-12-public-finite-countermodels-summary.md`
   - `stage2/results/2026-05-12-public-failure-ledger.jsonl`
   - `stage2/results/2026-05-12-competition-preflight.md`

## Upstream TBDs

Keep these configurable:

1. Final scoring and tie-breakers.
2. Final model/provider/route.
3. Final generation parameters.
4. Private problem-set size and composition.
5. Marathon compression ratio and sandbox resource limits if upstream changes them.

## Immediate Next Work

1. Attack the 571 remaining public TRUE gaps with additional safe rewrite templates and closure-backed short derivations.
2. Expand deterministic FALSE routes for the 100 remaining public FALSE gaps, prioritizing reusable formulaic families over brute-force bound increases.
3. Mine the new route histogram and failure ledger in `stage2/results/` into solver-facing route labels and witness families.
4. Keep Marathon triage parameterized for the 600s-vs-3600s reference-budget doc ambiguity.
5. Keep Windows vendor patches documented and rerun both official harnesses after upstream syncs.

## Non-Goals

1. Do not edit archived Stage 1 cheatsheets as active solver work.
2. Do not promote any certificate template without official judge acceptance.
3. Do not rely on Teorth theorem imports unless the official judge allowlist explicitly permits them.

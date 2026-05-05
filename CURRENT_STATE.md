# Current State

This file is the short-lived operational truth for the Stage 2 lab. Update it when the active solver, harness snapshot, validation evidence, or upstream rules change.

Last updated: 2026-05-05.

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
- Stage 1 archive: `stage1/`.
- Shared theory cache: `data/exports/` and `data/teorth_cache/`.

## Current Solver Capability

The initial scaffold is intentionally conservative:

1. Detects Marathon mode from official environment variables.
2. Detects Solo mode from stdin JSON.
3. Emits a TRUE certificate only for the trivial case `eq1_id == eq2_id`.
4. Skips all other problems rather than submitting speculative certificates.

This gives the repo a valid integration target without overstating solver performance.

## Current Smoke Status

Python-side packaging and lint smokes pass. The packaged submission directory must contain only `solver.py`; the official Solo runner rejects extra entries such as `.gitkeep` or `__pycache__` before executing the solver.

The local scaffold reaches the official Solo judge path on a reflexive fixture. Current official-runner failure is environment-only: `missing lean binary: lean`.

Native Windows is not a faithful official Marathon environment right now because the runner uses POSIX process-group behavior. Use WSL 2, Linux, or macOS for official Lean and Marathon validation.

## Upstream TBDs

Keep these configurable:

1. Final scoring and tie-breakers.
2. Final model/provider/route.
3. Final generation parameters.
4. Private problem-set size and composition.
5. Marathon compression ratio and sandbox resource limits if upstream changes them.

## Immediate Next Work

1. Run official harness setup in WSL/Linux.
2. Validate the local scaffold against official Solo and Marathon sample runners once Lean is available.
3. Build the first deterministic false-certificate generator using finite magma tables.
4. Build a Teorth graph index for proof/witness triage.
5. Add adversarial review checks for single-file packaging, no-secret assumptions, judge I/O, and Lean dependency policy.

## Non-Goals

1. Do not edit archived Stage 1 cheatsheets as active solver work.
2. Do not promote any certificate template without official judge acceptance.
3. Do not rely on Teorth theorem imports unless the official judge allowlist explicitly permits them.

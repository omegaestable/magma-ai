# Solver Scaffold

This directory contains the local Stage 2 solver source.

The competition submission is a single Python file named `solver.py`, <= 500 KB. The current scaffold is already single-file friendly. Future multi-file local development should include a bundling step that produces `stage2/submissions/solver.py`.

## Current Behavior

- Marathon mode: detected by `JUDGE_MARATHON_MANIFEST` and `JUDGE_MARATHON_OUTPUT`.
- Solo mode: detected by stdin JSON.
- Solves reflexive implications where `eq1_id == eq2_id`.
- Searches small finite magmas for FALSE countermodels.
- Emits finite FALSE certificates with `finOpTable` and `decideFin!`.
- Skips unresolved problems.

## Package

```powershell
.\stage2\solver\package_solver.ps1
```

## Next Work

1. Benchmark finite magma false-certificate coverage across public sets.
2. Add proof-template registry for true implications.
3. Add Marathon triage scoring and budget tracking.
4. Add fixture tests using the official judge.

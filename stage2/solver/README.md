# Solver Scaffold

This directory contains the local Stage 2 solver source.

The competition submission is a single Python file named `solver.py`, <= 500 KB. The current scaffold is already single-file friendly. Future multi-file local development should include a bundling step that produces `stage2/submissions/solver.py`.

## Current Behavior

This list is a scaffold summary and predates most of the engines. The route
inventory that is kept current lives in `CLAUDE.md` ("How the solver is
organised") and `stage2/docs/solver-route-ledger.md`; the `TRUE_ROUTES` table in
`solver.py` is the source of truth for dispatch order.

- Marathon mode: detected by `JUDGE_MARATHON_MANIFEST` and `JUDGE_MARATHON_OUTPUT`.
- Solo mode: detected by stdin JSON.
- Solves reflexive implications where `eq1_id == eq2_id`.
- Emits TRUE certificates for singleton/collapse cases, exact substitutions, projection-boundary laws, short bridge/constancy rewrites, and bounded subterm rewrite chains.
- Searches named compact witnesses, structured tables, affine/quadratic families, dualized witnesses, and bounded `Fin 2..3` enumeration for FALSE countermodels.
- Emits finite FALSE certificates with `finOpTable` (order <= 10) or an inlined `List.getD` table (above it) plus `decideFin!`; `maxRecDepth 20000` is set from the decide cost `n ** variables` (> 4,096), not from the order alone.
- Escalates unresolved Solo cases through the official LLM proxy and skips unsupported cases rather than submitting speculative certificates.
- Uses Marathon LLM calls only when the official runner injects `marathon_llm` and a token budget is available.

## Package

```powershell
.\stage2\solver\package_solver.ps1
```

Then run `stage2/docs/playground-preflight.md` before upload or playground testing.

## Next Work

1. Mine the remaining TRUE frontier into more safe Lean proof templates.
2. Expand reusable structured FALSE witness families.
3. Validate LLM escalation with a configured local proxy or organizer playground.
4. Rerun full public benchmarks before updating top-level totals.

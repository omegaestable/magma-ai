# Solver Scaffold

This directory contains the local Stage 2 solver source.

The competition submission is a single Python file named `solver.py`, <= 500 KB. The current scaffold is already single-file friendly. Future multi-file local development should include a bundling step that produces `stage2/submissions/solver.py`.

## Current Behavior

- Marathon mode: detected by `JUDGE_MARATHON_MANIFEST` and `JUDGE_MARATHON_OUTPUT`.
- Solo mode: detected by stdin JSON.
- Solves reflexive implications where `eq1_id == eq2_id`.
- Emits TRUE certificates for singleton/collapse cases, exact substitutions, projection-boundary laws, short bridge/constancy rewrites, and bounded subterm rewrite chains.
- Searches named compact witnesses, structured tables, affine/quadratic families, dualized witnesses, and bounded `Fin 2..3` enumeration for FALSE countermodels.
- Emits finite FALSE certificates with `finOpTable` and `decideFin!`; larger `Fin 7+` witnesses set `maxRecDepth 20000`.
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

# Motif Card: Finite Countermodel Witnesses

Updated: 2026-05-19

## Scope

Routes covered: named witnesses, structured finite families, affine/linear families, quadratic families, bounded enumeration, dualized witnesses, and `llm:false:table`.

## Mathematical Motif

To prove an implication false, it is enough to exhibit one finite magma satisfying the hypothesis equation and refuting the goal equation. The solver checks this semantically before emitting a Lean `Fin n` witness.

## Trigger Summary

- Named witnesses: compact curated magmas in `WITNESS_TABLES`.
- Structured families: semilattice, spine, central, and rectangular-band style generators.
- Affine/linear: operations over small `Z_n` of the form `a*x + b*y + c`.
- Quadratic: small bilinear or one-variable quadratic variants.
- Enumeration: exhaustive tables for `Fin 2..3`.
- Dual: search dual pair and transpose the table back.
- LLM table: accept only if `normalize_table` and `table_is_counterexample` pass.

## Lean Rendering Sketch

```lean
import JudgeProblem
import JudgeDecide.DecideBang
import JudgeFinOp.MemoFinOp
open MemoFinOp

def submission : Goal := by
  let m : Magma (Fin n) := {
    op := finOpTable "[[...]]"
  }
  refine Exists.intro (Fin n) ?_
  refine Exists.intro m ?_
  decideFin!
```

For larger tables, the emitted certificate includes `set_option maxRecDepth 20000` before `decideFin!`.

## Local Semantic Check

1. Validate the table is square and all entries are in range.
2. Evaluate the hypothesis for all variable assignments; it must hold.
3. Evaluate the goal for all variable assignments; it must fail for at least one assignment.
4. Only then emit the Lean finite witness.

## Provenance

- `data/teorth_cache/smallest_magma.txt` gives witness-size hints.
- Teorth graph and proof pages mark many false implications by finite countermodel evidence.
- Compact witnesses S4D, S4E, and S5D came from hard-mix witness mining and are summarized in May 2026 result notes.

## Evidence

- Historical public baseline accepted 811 finite FALSE certificates.
- Compact witness fixture accepted 8/8 with the recent structured table additions.
- OpenRouter/LLM false-table path is safe only because the solver rechecks the table locally before Lean emission.

## Limits

- Broadly raising brute-force `Fin n` limits is not a good Marathon strategy.
- New named tables should come from targeted misses, Teorth witness hints, or mined fixtures, then pass official runner checks.
- Large finite witnesses can stress Lean recursion depth and certificate size.

## Regression Needs

- Fixture covering S4D, S4E, S5D.
- One structured-family witness.
- One affine/linear witness.
- One quadratic witness.
- One dual witness.
- One LLM-provided table accepted after local semantic verification.

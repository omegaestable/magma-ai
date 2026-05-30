# Motif Card: Projection Boundary Laws

Updated: 2026-05-19

## Scope

Routes covered: `true:projection:*` and the `projection_cue` priority signal.

## Mathematical Motif

A projection law turns every composite term into one of its boundary variables. Once both sides of the goal reduce to the same variable, the implication is proved by transitivity.

Typical shapes:

- `x = x ◇ y`
- `x = y ◇ x`
- dual/right-boundary variants

## Trigger Summary

1. Detect a projection-like hypothesis with `projection_law_route`.
2. Recursively reduce each goal term to the boundary variable implied by the law.
3. If goal lhs and rhs reduce to the same variable, emit the joined proof.

## Lean Rendering Sketch

```lean
import JudgeProblem

def submission : Goal := by
  intro G _ h
  intro x y z
  exact (projection_proof_left).trans (projection_proof_right).symm
```

Each `projection_proof_*` is built from explicit applications of `h` and congruence over subterms.

## Local Semantic Check

- Compute boundary variables of each term.
- Verify each recursive reduction step is justified by the hypothesis orientation or symmetry.
- Only emit the final certificate when both sides reduce to the same variable.

## Provenance

- Projection laws are standard finite algebra motifs and appear frequently in Teorth implication graph reductions.
- Duality is relevant: left and right projection families should be checked together.
- Teorth proof pages often expose these as simple rewrite or rewrite-goal steps.

## Evidence

- Active deterministic route in `solve_problem` before generic rewrite-chain and closure search.
- Official acceptance evidence is included inside historical public `true:certificate` totals.

## Limits

- The route is intentionally boundary-based. It should not attempt arbitrary normal-form completion.
- Incorrect boundary detection would be dangerous; route fixtures should include both triggering and non-triggering examples.

## Regression Needs

- Left projection example.
- Right projection example.
- Dual projection example.
- Non-projection equation with similar boundary variables that must not trigger.

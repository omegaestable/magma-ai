# Motif Card: Basic TRUE Rewrites

Updated: 2026-05-19

## Scope

Routes covered: `true:reflexive`, `true:singleton`, `true:rewrite`, `true:rewrite:symm`, `true:bridge:*`, and `true:constancy:*`.

## Mathematical Motif

These routes are the smallest equational-logic derivations available to the solver. They use only identity, substitution, symmetry, and transitivity of equality. No Teorth theorem name is needed at runtime.

## Trigger Summary

- Reflexive: hypothesis and goal are the same equation id.
- Singleton/collapse: the hypothesis contains a variable alone on one side and absent from the other side, forcing all carrier elements equal by two substitutions.
- Direct substitution: the goal is a direct instance of the hypothesis, possibly using symmetry.
- Bridge/constancy: two instances of the hypothesis share a middle term; missing variables may be filled from a small goal-derived term pool.

## Lean Rendering Sketch

Reflexive:

```lean
import JudgeProblem

def submission : Goal := by
  intro G _ h
  exact h
```

Singleton/collapse:

```lean
import JudgeProblem

def submission : Goal := by
  intro G _ h
  have hall : forall a b : G, a = b := by
    intro a b
    exact (h ...).trans (h ...).symm
  exact hall _ _
```

Bridge:

```lean
import JudgeProblem

def submission : Goal := by
  intro G _ h
  intro x y
  exact (h ...).trans (h ...).symm
```

## Local Semantic Check

1. Parse both equation terms.
2. Build a substitution from hypothesis variables to goal terms.
3. Confirm each proof step is either `h subst`, `(h subst).symm`, or `.trans` between matching endpoints.
4. Render only the checked proof expression into Lean.

## Provenance

- Teorth graph and proof pages label many such implications as simple rewrites or nth rewrites.
- `paper/blueprint.tex` gives the standard rewrite-system background: substitution instances and equality transitivity generate equational derivations.
- The solver-owned certificate is standalone and depends only on `JudgeProblem`.

## Evidence

- Public zero-token runs accepted many `true:certificate` rows through these routes.
- These routes are first in `solve_problem`, so they are naturally exercised by Solo samples and public Marathon sweeps.

## Limits

- Completed bridge/constancy uses empirical `max_trials` bounds.
- Widening the fill pool can increase runtime and false proof attempts if not checked by endpoint matching.
- Keep this family conservative; use closure routes or LLM DSL for longer chains.

## Regression Needs

- Fixture with direct substitution and symmetric substitution.
- Fixture with a two-instance bridge.
- Fixture with a completed-bridge fill from the goal term pool.

# Solver Motif Cards

Updated: 2026-05-19

These cards justify solver route families with mathematical triggers, Lean rendering sketches, local semantic checks, evidence, limits, and regression needs. Start with `../solver-route-ledger.md` for the route inventory, then read the card for the family you plan to change.

## Cards

- `true-basic-rewrites.md` — reflexive, singleton/collapse, direct substitution, bridge, and constancy routes.
- `true-projection-laws.md` — projection and boundary-variable TRUE routes.
- `true-closure-routes.md` — bounded rewrite chains, absorption closure, deep absorption, equational closure, and opt-in grind archaeology.
- `false-finite-witnesses.md` — named, structured, affine, quadratic, enumerated, dual, and LLM-proposed finite countermodels.
- `llm-proxy-dsl.md` — Solo/Marathon proxy paths and accepted LLM DSL shapes.

## Maintenance Rules

1. A solver route change should update the relevant card in the same session.
2. A new route should get a card before it is promoted beyond a local experiment.
3. Teorth data belongs in card provenance, not in submitted solver runtime behavior.
4. Official runner acceptance remains the final evidence standard.

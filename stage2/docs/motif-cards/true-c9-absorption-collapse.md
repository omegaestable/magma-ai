# Motif Card: C9 Absorption Collapse Candidate

Updated: 2026-05-20

## Scope

Partially active TRUE route family. The narrow `E1072`-shape collapse into `E19` is implemented in `stage2/solver/solver.py`; the broader `E1806` collapse remains candidate work.

This card records the lesson from the 2026-05-20 unresolved TRUE proxy round: several hard TRUE misses appear to need a local collapse from a C9-like absorption hypothesis into a smaller representative such as `E19` or `E13`, followed by existing absorption or closure reasoning.

## Source Pairs

- `hard3_0140`: `E1072 -> E1251`
  - `E1072`: `x = y ◇ ((x ◇ (x ◇ x)) ◇ x)`
  - `E1251`: `x = x ◇ (((y ◇ y) ◇ y) ◇ x)`
- `hard3_0196`: `E1806 -> E545`
  - `E1806`: `x = (y ◇ z) ◇ ((w ◇ x) ◇ x)`
  - `E545`: `x = y ◇ (z ◇ (x ◇ (z ◇ x)))`
- Related fixture candidates: `hard3_0139`, `hard3_0197`, `normal_0203`.

`hard3_0114` from the same proxy round is also `implicit_proof_true`, but its graph hints pass through VampireProven legs and should remain a separate theorem-chain target.

## Teorth Status

- `stage2/results/2026-05-20-unresolved-true-teorth.jsonl` labels all three targeted rows as `implicit_proof_true`.
- `proof_scraping_lab.py` reached the proof pages for `1072,1251`, `922,1444`, and `1806,545`, but extracted only JS-shell pages with no theorem links, code blocks, facts, or pair links.
- Graph exploration found `E1072` and `E1806` in a C9-style source class with representatives such as `E13` and `E19`.

## Family Trigger

A hypothesis has an absorption-like shape where a distinguished variable occurs alone on the left and also appears deeply inside the right context, with enough free variables around it to instantiate smaller absorption representatives.

Candidate examples:

- `x = y ◇ ((x ◇ (x ◇ x)) ◇ x)` should collapse toward `E19` or a related representative.
- `x = (y ◇ z) ◇ ((w ◇ x) ◇ x)` should collapse toward `E13` or `E19`.

This trigger is intentionally narrower than broad deep absorption closure. Do not widen it until an accepted local-lemma fixture exists.

## Lean Rendering Sketch

The desired certificate shape is a local theorem chain:

```lean
import JudgeProblem

def submission : Goal := by
  intro G _ h
  intro x y z
  have hcollapse : x = y ◇ (z ◇ x) := by
    -- proved by solver-owned local lemma search from h
    exact ...
  have htarget : y ◇ (z ◇ x) = y ◇ (z ◇ (x ◇ (z ◇ x))) := by
    -- existing closure/absorption route, or congrArg over a smaller local fact
    exact ...
  exact hcollapse.trans htarget
```

The actual generated proof must contain only explicit hypothesis rewrites, congruence, and transitivity. It must not import Teorth theorem names.

## Local Check

1. Detect a narrow C9-like absorption hypothesis.
2. Try to synthesize one or two intermediate lemmas such as `E1072 -> E19`, `E1806 -> E19`, or `E1806 -> E13`.
3. Prove each local lemma with the existing proof-producing rewrite/closure helpers, possibly with target-guided term pools.
4. Compose the local lemmas with existing absorption or equational closure routes.
5. Emit a certificate only when every edge has a proof expression.

## Implementation

- Active route: `true:c9_e1072_collapse:*`.
- Trigger: structurally matches `x = y ◇ ((x ◇ (x ◇ x)) ◇ x)` without checking problem ids.
- Certificate shape: introduces local `h19 : ∀ a b c : G, a = b ◇ (c ◇ a)` using only `h`, `.trans`, `.symm`, and `congrArg`, then composes through existing direct/bridge proof-expression helpers for `E19 -> target`.
- Accepted focused smoke: `hard3_0140` (`E1072 -> E1251`) solved by official Solo with `0` LLM calls and `1` judge call after packaging at `76088` bytes.

## Evidence

- Positive-token proxy round: `stage2/results/2026-05-20-unresolved-true-proxy-round.md`.
- Row error ledger: `stage2/results/2026-05-20-unresolved-true-proxy-errors.jsonl`.
- Teorth labels: `stage2/results/2026-05-20-unresolved-true-teorth.jsonl`.
- Focused official Solo result: `tmp_stage2_smoke/2026-05-20-c9-hard3-0140-solo-result-after-guard.json`.

## Limits

- This is not a reason to revive `true:grind`.
- This is not evidence for raising global closure bounds.
- Direct proof-page scraping did not yield Lean code or theorem links for the target pairs.
- The route must not hardcode public problem ids or read Teorth caches at runtime.

## Regression Needs

- Focused official Solo fixture with `hard3_0196` and nearby intermediates after an `E1806` local collapse exists.
- Negative fixture for absorption-like equations that are not C9 collapses.
- No-loss smoke against an existing accepted deep absorption fixture.
- Positive-token parity rerun after the route exists, using structured LLM rejection reasons from the updated solver.

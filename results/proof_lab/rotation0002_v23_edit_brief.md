# Rotation0002 V23 Edit Brief

This brief is for the next conservative edit to `cheatsheets/v23.txt`.

Goal: improve FALSE recall on fresh unseen hard-style failures without damaging normal TRUE recall or causing prompt collapse.

## Evidence Base

- Fresh unseen normal 30/30 run: 56/60 = 93.3%, with 4 false positives and 0 false negatives.
- Fresh unseen hard3 20/20 run: 20/40 = 50.0%, with 20 false positives and 0 false negatives.
- Combined fresh unseen failures: 24, all false positives.
- Full corrected ledger: `results/proof_lab/rotation0002_failure_ledger.md`.
- Family prior from earlier rotating hard analysis: `results/proof_lab/rotating_hard_false_report.md`.

## Current Failure Mode

The model is not hallucinating proofs. It is doing exactly what the current prompt tells it to do:

- run only LP, RP, C0, VARS
- if no separator fires, answer TRUE

Across all 24 failures the model's explanation was effectively the same:

`REASONING: No test separates E1 from E2.`

So the next edit should not broaden the TRUE lane. It should add one narrow post-4-test FALSE rescue lane.

## Failure Shape Summary

- 15/24 failures have the shape `x = ...` implies `x = ...`.
- Most failures still end in nested right-hand products, so LP/RP/C0/VARS often all miss together.
- Only 2 fresh unseen failures surfaced direct named witnesses from the current deterministic library:
  - `normal_0618` via `XOR` and `XNOR`
  - `normal_0301` via `T3L`
- `hard3_0359` is another direct `T3L` witness case.
- Earlier hard-family ranking suggests the dominant rescue families are:
  - `all4x4_table_counterexamples`
  - `small_finite_magma`
  - projection-family triggers only as a minority lane

## Safe Edit Direction

Keep the current 4-test backbone and singleton TRUE rule. Do not replace them.

Add a short hard-false rescue block after the 4 tests and before the unconditional TRUE fallback:

1. If LP/RP/C0/VARS found a separator, answer FALSE exactly as today.
2. If not, do not jump straight to TRUE on hard-looking pairs.
3. Run one fixed finite-witness rescue ladder, but keep it tiny and explicit.
4. Only answer FALSE if one named witness is explicitly checked and shown to satisfy E1 while falsifying E2.
5. Otherwise keep the current TRUE fallback.

The witness ladder should be short. Suggested order:

1. `C0`
2. `XOR`
3. `XNOR`
4. `AND`
5. `OR`
6. `T3L`

Why this order:

- It matches repo evidence that compact finite witnesses are the highest-yield next lane.
- It keeps the edit grounded in named, already-known witness objects instead of vague construction prose.
- It avoids trying to compress 4x4 table reasoning directly into the prompt, which is likely too large and too brittle.

## What To Change In V23

The most important line to change is this current rule:

`After all 4 tests with no separation → answer TRUE.`

Replace it conceptually with:

`After all 4 tests with no separation, try the fixed finite-witness rescue ladder. Only if no named witness is explicitly verified should you answer TRUE.`

The output contract should also change slightly:

- If a witness from the rescue ladder separates, `COUNTEREXAMPLE` should name that witness.
- If no witness is verified, TRUE remains allowed.
- The prompt must forbid inventing 4x4 or matrix facts.

## Worked Example Candidates

Use fresh unseen misses, not old benchmark favorites.

### Candidate FALSE Example 1

- id: `normal_0618`
- E1: `x = y * (y * (z * (z * x)))`
- E2: `x = (x * y) * (z * x)`
- certified FALSE by `XOR` and `XNOR`

Why it matters:

- It is a fresh unseen normal miss, so it helps the new lane without overfitting only to hard3.
- It demonstrates that “no separator in the 4 current tests” does not imply TRUE.

### Candidate FALSE Example 2

- id: `normal_0301`
- E1: `(x * y) * y = (y * z) * z`
- E2: `x * (y * z) = (z * y) * x`
- certified FALSE by `T3L`

Why it matters:

- It introduces the ternary witness lane in one compact example.
- It is a fresh unseen normal failure, so it is safer than introducing T3L only from hard3.

### Candidate FALSE Example 3

- id: `hard3_0359`
- E1: `x * x = y * ((y * x) * z)`
- E2: `x * y = (y * y) * (z * z)`
- certified FALSE by `T3L`

Why it matters:

- Confirms T3L is not a one-off normal artifact.
- Gives hard3 coverage without requiring matrix-only explanation.

## Guardrails

Do not do any of the following in the next edit:

- Do not add many new algebraic families in prose.
- Do not mention 4x4 tables unless the model can explicitly verify a named witness. The prompt budget is too small for generic 4x4 reasoning.
- Do not tell the model to use matrix facts or provenance it cannot actually see.
- Do not add open-ended “try a construction” language.
- Do not remove the current singleton TRUE shortcut.
- Do not change the output format.

## Recommended Patch Shape

Target a small patch, roughly:

- one short paragraph introducing the finite-witness rescue ladder
- one decision rule clarifying that TRUE comes only after the ladder fails
- one or two worked FALSE examples from `normal_0618` and `normal_0301`

Avoid a large rewrite. This should be a narrow lane addition, not a new prompt architecture.

## Post-Edit Verification

After the edit, re-run exactly these two files first:

- `data/benchmark/normal_balanced60_true30_false30_rotation0002_20260403_185904.jsonl`
- `data/benchmark/hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl`

Success criterion for the next edit:

- keep normal TRUE recall at 30/30
- reduce the 4 normal false positives
- improve hard3 FALSE accuracy above 0/20 without introducing false negatives

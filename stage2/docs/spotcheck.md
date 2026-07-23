# Spot-check harness

`stage2/experiments/spotcheck.py` — randomized, balanced, cross-source accuracy
testing for the solver. The aim is *accuracy* (never submit a wrong verdict),
approached by running many small random batches across many sources so latent
mistakes surface over many sessions. Skipping a row is safe; submitting a wrong
answer is the only thing this hunts.

## Running it

```powershell
# default: 5 TRUE + 5 FALSE from each of 9 sources (90 rows)
.\.venv\Scripts\python.exe stage2\experiments\spotcheck.py

.\.venv\Scripts\python.exe stage2\experiments\spotcheck.py --true 10 --false 10
.\.venv\Scripts\python.exe stage2\experiments\spotcheck.py --sources etp,hard3
.\.venv\Scripts\python.exe stage2\experiments\spotcheck.py --seed 123 --pure-random
```

Exit code is `1` if any mistake was found (and pinned), `0` otherwise — so it
can gate a loop or a scheduled run.

## Sources

Eight **distinct** benchmark sets — official `normal/hard1/hard2/hard3` and the
HF `eval_normal/eval_hard/eval_extra_hard/eval_order5` — plus `etp`.

The HF `normal/hard/hard1/hard2/hard3` files are **not** sources: they are the
same problems as the official sets in `*` instead of `◇` notation (identical
`eq1_id/eq2_id/answer`). Across every local file there are only 2,669 distinct
benchmark problems, all already covered by `audit_corpus.py`.

`etp` is the real reason this harness exists. `data/exports/general_outcomes.json.gz`
is the Equational Theories Project outcome matrix: 4694×4694 ≈ **22M labelled
implication pairs** (~37% TRUE), with `data/exports/equations.txt` giving each
equation's `◇` text. It is validated ground truth — it agrees with 2,269/2,269
in-range benchmark rows — and an essentially unlimited pool the solver has never
been sampled against. (Equations with id > 4694, e.g. the order-5 sets, are
outside this matrix; those rows only come from the benchmark files.)

## What counts as a mistake

Each row goes through `audit_corpus.audit_row` — the same `solve_problem` +
offline-oracle path the full corpus audit uses (proof kernel for
`exact_expr`/`singleton`/`lemma` certificates, finite-model check on every TRUE,
witness re-verification on every FALSE, ground-truth label cross-check).

- **mistake** — `crash`, an oracle failure (unsound certificate), or a verdict
  that contradicts the label. These are pinned.
- **skip** — the solver declined to answer. Safe; costs coverage, not accuracy.
- **correct** — solved and every check passed.

For benchmark rows in ETP range the harness also cross-checks the fixture label
against the ETP matrix independently (a data-integrity check, reported but not
pinned as a solver bug).

## The regression loop

A caught mistake is appended to the git-tracked
`stage2/fixtures/spotcheck_failures.jsonl` (deduped by `(eq1_id, eq2_id)`) with
the observed failure. `stage2/tests/test_spotcheck_regressions.py` replays every
pinned row and asserts the solver never submits the wrong verdict and never
emits an unsound certificate for it. That test runs inside `pytest stage2/tests`
— the pre-package gate — so **a mistake found once can never silently return**.
A pinned row that the solver later chooses to *skip* passes (skip is safe); the
gate only fails on a wrong submission.

Workflow when a batch reports a mistake:

1. It is already pinned. Run `pytest stage2/tests` to confirm the red row.
2. Fix the solver until the gate is green.
3. The fixture entry stays forever as a guard.

## Coverage ledger

`stage2/results/spotcheck-coverage.json` (gitignored scratch) records tested
`(source, eq1_id, eq2_id)` keys. By default each batch prefers rows not in the
ledger, so repeated runs fan out across the corpus instead of re-testing the
same rows — even with a fixed `--seed`. `--pure-random` ignores and does not
write the ledger, for a clean independent uniform draw.

## Reuse (no new verification code)

- `audit_corpus.audit_row` / `build_battery` — the per-row solve+verify engine.
- `stage2/tests/oracles.py` — every `check_*` and the finite-model battery.
- `data/exports/` — ETP matrix and equation texts.

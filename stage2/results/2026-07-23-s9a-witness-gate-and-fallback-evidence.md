# 2026-07-23 (session 2) — the `S9A` witness gate, and what "no counterexample" means

A real playground Solo run returned eight `TRUE INCORRECT` rows, each burning
400–630 s and each submitting the same speculative certificate:

```lean
import JudgeProblem

def submission : Goal := by
  intro G _ h
  intro x y z
  set_option maxHeartbeats 100000 in
  grind
```

That is `fallback:unsolved_grind` in `run_solo`. Seven of the eight rows are
labelled **FALSE**, so a `verdict: "true"` there can never be accepted. This
file records the root cause, the fix, and the evidence.

## Reported rows

| Playground id | eq1 | eq2 | label |
| --- | ---: | ---: | --- |
| `evaluation_extra_hard_false_0180` | 168 | 3864 | false |
| `evaluation_extra_hard_false_0181` | 168 | 3883 | false |
| `evaluation_extra_hard_false_0182` | 168 | 3915 | false |
| `evaluation_extra_hard_false_0183` | 168 | 3921 | false |
| `evaluation_extra_hard_false_0184` | 168 | 3952 | false |
| `evaluation_extra_hard_false_0197` | 168 | 4615 | false |
| `evaluation_extra_hard_false_0198` | 168 | 4645 | false |
| `evaluation_hard_true_0116` | 469 | 4090 | true |

All seven FALSE rows share **`eq1_id = 168`**, `x = (y ◇ x) ◇ (x ◇ z)` — the
central groupoid law.

## Root cause: a sound witness the solver owned but refused to try

`find_counterexample` gated the 9-element named witness `S9A` behind
`LARGE_WITNESS_SHAPE_KEYS`, which pinned it to the **exact `(eq1, eq2)` pair it
was discovered on**:

```python
LARGE_WITNESS_SHAPE_KEYS = {
    "S9A": equation_pair_shape_key(
        parse_equation("x = (y * x) * (x * z)"),
        parse_equation("x * (y * y) = x * (y * z)"),   # <- one goal only
    ),
}
```

Every reported row matches that `eq1` and none matches that `eq2`, so `S9A` was
skipped. **`S9A` refutes all eight of them.**

A witness table is a property of the *hypothesis*; whether it refutes the goal
is what `table_is_counterexample` already decides, and it short-circuits on
`equation_holds(eq1, table)`. Measured cost of testing `S9A` unconditionally:
**0.021 ms/problem** (all 29 named tables ungated: 0.253 ms/problem). The guard
bought nothing and hid a whole family. A full equation-pair shape key is a
benchmark id in disguise — see Operational Note 2.

## Why nothing else caught it

The FALSE search on an `Eq168` row inspects almost no models of the hypothesis:

| Source | tables tried | models of Eq168 |
| --- | ---: | ---: |
| `enumerate_tables(2)` | 16 | **0** |
| `enumerate_tables(3)` | 19,683 | **0** |
| `structured_family_tables` | 49 | **0** |
| `affine_family_tables` | 1,808 | **0** |
| `quadratic_family_tables` | 678 | **0** |
| `WITNESS_TABLES` | 29 | 2 (`S4C`, `S9A`) |

Central groupoids have order `m²`, so orders 2 and 3 contain **no model at
all** and the enumeration is vacuous. A lazy DFS model finder confirms no
witness exists at order 4 or 5 (`n=4` exhausted in 0.0 s, `n=5` in 0.8 s) —
the witness genuinely lives at order 9, and `S9A` is the only one the solver
has.

The solver then treated "`find_counterexample` returned `None`" as license to
fall through to the TRUE engines and finally to a speculative `verdict:
"true"`. **That inference is only valid if the search actually looked at
some models.** Here it looked at two.

## Fixes (`stage2/solver/solver.py`)

1. **`LARGE_WITNESS_SHAPE_KEYS` deleted**; all named witness tables are tried
   on every problem. `find_counterexample` now calls `witness_check`.
2. **Hypothesis-model counter.** `witness_check` and
   `local_model_counterexample` call `note_hypothesis_model()` whenever a table
   satisfies `eq1`; `solve_problem` resets it per problem;
   `hypothesis_models_seen()` reads it. It is free — the same short-circuit as
   before, no extra `equation_holds` call.
3. **The speculative TRUE fallback is evidence-gated.** When
   `hypothesis_models_seen() == 0`, `run_solo` logs
   `fallback:skip_no_model_evidence` and submits nothing instead of guessing
   `true`. A failed witness search over zero models refutes nothing and proves
   nothing.

The counter discriminates cleanly on exactly the reported rows:

| Row | label | `models_seen` | outcome |
| --- | --- | ---: | --- |
| the seven `Eq168` rows | false | 2 | solved `false:witness:S9A` |
| `evaluation_hard_0116` | true | 3,691 | still open; grind lottery kept |

## Evidence

**Reported rows, `fast` tier** — all seven FALSE rows plus
`evaluation_extra_hard_0190` (recorded as an open playground miss on
2026-07-22, "no witness ≤ 4 exists") go from a ~40 s skip to a witness in
**0.05 s**:

```
evaluation_extra_hard_0180 .. 0184, 0190, 0197, 0198
   before: 38-45 s  route=SKIP        -> fallback grind TRUE -> INCORRECT
   after :  0.05 s  route=false:witness:S9A verdict=false
```

**Real local Lean judge** (`judge.verify.verify_answer`, production proof
policy) — this cert shape had no prior judge evidence, so it was checked
directly:

| Row | judge | seconds |
| --- | --- | ---: |
| `evaluation_extra_hard_0180` | `accepted` | 48.5 (cold, includes build) |
| `evaluation_extra_hard_0183` | `accepted` | 16.1 |
| `evaluation_extra_hard_0190` | `accepted` | 14.3 |
| `evaluation_extra_hard_0197` | `accepted` | 14.5 |
| `evaluation_extra_hard_0198` | `accepted` | 15.4 |

5/5 accepted, warm runs 14–16 s against the judge's `LEAN_TIMEOUT_SECONDS =
120`. Cert is 462 bytes against `MAX_FALSE_CERT_BYTES = 10_000`. Unlike a
`grind` cert, `decideFin!` is kernel reduction, so acceptance transfers — see
`grind-local-accept-is-not-cloud-evidence`.

**Offline correctness gate**: `pytest stage2/tests` — 196 passed, 2 skipped.

**Official sets** (`fast` tier, vs the 2026-07-23 egg baseline) — **identical,
row for row**:

| Set | before | after | +/− by id |
| --- | ---: | ---: | --- |
| `hard1` | `64/69` | `64/69` | +0 / −0 |
| `hard2` | `177/200` | `177/200` | +0 / −0 |
| `hard3` | `387/400` | `387/400` | +0 / −0 |
| `normal` | `989/1000` | `989/1000` | +0 / −0 |
| **Total** | **`1617/1669`** | **`1617/1669`** | TRUE `789` → `789` |

The `Eq168` family lives in the HF `evaluation_extra_hard` set, so the official
sets neither gain nor lose. Zero oracle failures.

**HF evaluation sets** (`fast` tier, same baseline):

| Set | before | after | +/− by id |
| --- | ---: | ---: | --- |
| `hf_evaluation_extra_hard` | `170/200` | `200/200` | **+30 / −0** |
| `hf_evaluation_hard` | `198/200` | `197/200` | +0 / −1 |
| `hf_evaluation_normal` | `198/200` | `198/200` | +0 / −0 |
| `hf_evaluation_order5` | `188/200` | `188/200` | +0 / −0 |
| **Total** | **`754/800`** | **`783/800`** | **+30 / −1** |

All 30 gains are `false:witness:S9A`. `hf_evaluation_extra_hard` also drops
from 185.3 s to 24.7 s, because 30 rows no longer run the whole TRUE engine
stack before skipping. Zero oracle failures.

The single loss, `evaluation_hard_0178`, is **wall-clock noise, not this
change**: three consecutive `fast`-tier runs of the *same* code on that row
gave `45.7 s → SKIP`, `17.2 s → true:projection_bootstrap:left`,
`10.0 s → true:projection_bootstrap:left`. It sits on a budget edge and its
outcome tracks cache warmth. Worth recording as an amendment to
`audit-solved-count-noise-band`: the TRUE column is *mostly* stable, but
budget-marginal TRUE routes like `projection_bootstrap` can flip too, so diff
row ids rather than trusting the TRUE total alone.

## What is *not* fixed

`evaluation_hard_true_0116` (`x = y ◇ (x ◇ (x ◇ (z ◇ x)))` ⊢
`x ◇ x = ((y ◇ y) ◇ x) ◇ x`) is a genuine TRUE row no engine proves. Its
`models_seen` is 3,691, so the evidence gate keeps the grind attempt and the
row will still report `TRUE INCORRECT` in the field. That is an open frontier
row, not a bug.

Note also that an unresolved row still submits `fallback:insurance_reflexive`
(a deliberately-failing TRUE cert banked before the LLM loop to prevent the
2026-07-22 `ERROR` class). Unresolved rows therefore still surface as
`TRUE INCORRECT`; the fix removes the second, far more expensive grind call.

## Next lever

`hypothesis_models_seen()` now measures FALSE-search coverage directly. The
lazy DFS model finder used above (build models *of* `eq1` with constraint
propagation, rather than testing a fixed table library against it) exhausts
order 4 in 0.0 s and order 5 in 0.8 s. Promoting it into the solver is the
general version of this fix: it would make the FALSE lane independent of
whether a hypothesis's models happen to live in the canned families.

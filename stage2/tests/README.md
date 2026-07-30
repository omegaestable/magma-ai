# Stage 2 offline correctness gate

The official Lean judge runs in the cloud, so nothing here calls Lean. These
tests verify the **mathematics** of every certificate the solver emits, which
is exactly where builder bugs turn into judge `incorrect` verdicts.

Run the gate:

```powershell
.\.venv\Scripts\python.exe -m pytest stage2/tests -q -n auto
```

`-n auto` (pytest-xdist) matters: the gate re-solves ~170 real problems, which is
~160 s serially and ~47 s across cores. A slow gate is a gate people skip.

`stage2/solver/package_solver.ps1` runs it automatically and refuses to
package on failure (`-SkipTests` only for a deliberate spike).

## What each layer checks

| File | Guards against |
| --- | --- |
| `oracles.py` | Library: an independent term parser/evaluator, a proof-expression kernel, a finite-model oracle, and a banned-tactic check. Deliberately shares no code with `solver.py`, so a bug in a solver primitive cannot hide itself here. |
| `test_primitives.py` | The ~8 shared primitives every certificate depends on (`match_term`, `instantiate_term`, `context_to_lean`, `call_expression`, `replace_subterm`, `dual_term`, `_kb_unify`, `critical_pair_rules`). Includes mutation tests proving the oracles reject corrupted certificates. |
| `test_golden.py` | Coverage loss, route drift, and soundness loss on a route-diverse sample of real public problems. |
| `test_judge_verified.py` | Builder regressions in certificates the proof kernel *cannot* check. See below. |
| `test_spotcheck_regressions.py` | Replays every mistake `spotcheck.py` has ever caught. |

## Certificates the kernel cannot check

`classify_true_certificate` returns `other` for the hand-written `*_block`
combinator proofs and the nested-`have` collapse proofs — 34 rows on the official
sets, across 18 routes. Those get no kernel check, and the model oracle is
*also* powerless on many of them: every `*_singleton` / `*_collapse` route asserts
eq1 forces a one-element magma, and the trivial magma satisfies every equation,
so there is nothing for a finite model to refute. Measured 2026-07-29: 10 of them
had no offline verification of any kind.

They are pinned against the real Lean judge instead. All 34 were run through
`judge.verify.verify_answer` and **all 34 returned `accepted`** (4.3-7.3 s each);
the exact certificate text is stored in
`stage2/fixtures/judge_verified_certs.jsonl`, and `test_judge_verified.py`
asserts the builders still emit it byte-for-byte. Regenerate with:

```powershell
.\.venv\Scripts\python.exe stage2/experiments/judge_rows.py `
    --from-audit stage2/results/audit-<date>.json --shape other --write-fixture
```

Never hand-edit that fixture: its value is that a human did not write it.

## Witness rendering: the one thing the oracles could not see

Every check in `oracles.py` reads the *parsed Python table*. The judge does not —
it builds the magma with `MemoFinOp.finOpTable`, whose parser (`extractDigits`)
keeps **one value per digit character**. A cell holding `10` becomes two cells,
`1` and `0`, and the whole table shifts.

Found 2026-07-29 by a `Fin 13` witness for `hard2_0051` — the linear model
`x ◇ y = 7x + 7y (mod 13)` — that was verified by hand, by `equation_holds`, and
by the solver's own `table_is_counterexample`, and still came back
`LEAN_REJECTED` with `decide` reporting the conjunction *false*. Building the
magma from a formula instead fails the proof policy (`HAdd.hAdd` / `HMul.hMul`
are not allowlisted), so `finOpTable` is the only sanctioned constructor.

Consequences now enforced in two places:

- `solver.table_is_renderable()`, called inside `table_is_counterexample` — the
  single gate every FALSE witness crosses. `MAX_WITNESS_ORDER = 10`.
- `oracles.check_false_certificate` rejects multi-digit tables, so this class is
  finally visible offline, plus a test pinning every witness-order constant.

A FALSE row whose smallest countermodel exceeds order 10 is **unreachable**.

## Banned tactics

`check_no_banned_tactics` rejects `grind`/`simp`/`aesop`/`sorry` in any emitted
certificate, except `true:narrow_grind` and the Solo `fallback:unsolved_grind`.
`sanitize_lean_code` already enforced this on *LLM* output but never on
solver-generated code — which is how a `grind` step lived inside
`true:right_projection_collapse:left_pair_tail` unnoticed. A tactic step cannot
be kernel-checked, so it is invisible to every gate here, and the cloud judge has
rejected such a proof in the field. `test_primitives.py` also scans the solver
source statically, so a template no pinned row exercises still gets caught.

## The proof kernel

`ProofKernel` evaluates the restricted Lean grammar the closure/critical-pair
builders emit —

```
h t1 .. tk | (E).symm | (E1).trans (E2) | congrArg (fun t => CTX) (E) | rfl
```

— to the equation each expression proves. A TRUE certificate passes only if
its `exact` expression proves exactly `eq2.lhs = eq2.rhs` from instances of
`eq1`. This is the same failure Lean would report as a type mismatch, caught
locally in milliseconds.

Certificates outside this grammar (the hand-written `*_block` proof terms,
which use `let`/`have` chains and the `M/R/S/T/C` combinators) are reported as
shape `other` and fall back to model-checking only.

One `have`-chain shape *is* fully checked: `lemma`, emitted by
`true:projection_bootstrap`, `true:lemma_bootstrap` and the LLM's
`llm:true:lemma`. These prove a small law as a named lemma and then derive the
goal from it, so `check_true_lemma_certificate` runs the kernel twice: the
lemma body must prove exactly the law the certificate *states* from instances
of eq1, and the goal body must prove exactly `eq2.lhs = eq2.rhs` treating that
stated law as its hypothesis. The statement is parsed back out of the
certificate rather than assumed, so a builder that proves one law and applies a
different one cannot pass. Neither half is taken on trust.

The same technique would extend to the other lemma-shaped certificates
(`derived_left_projection` and friends), which are still `other`.

## The finite-model oracle

Independent of proof syntax: build finite magmas satisfying `eq1`, then check
`eq2` holds in all of them. A TRUE verdict refuted by any such model is
unsound — the row was actually FALSE. This catches whole classes of bug the
proof kernel cannot see.

## Regenerating the golden fixture

Only after an **intentional** route change. Never hand-edit it.

```powershell
.\.venv\Scripts\python.exe stage2/experiments/audit_corpus.py --all --subsumption --out stage2/results/audit.json
.\.venv\Scripts\python.exe stage2/experiments/make_golden.py --audit stage2/results/audit.json
```

`audit_corpus.py` is also the full-corpus soundness sweep and the source of
the de-bloat subsumption matrix (`analyze_subsumption.py`). It parallelises
across cores; a full public sweep is minutes, not hours.

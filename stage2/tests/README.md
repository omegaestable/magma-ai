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
it builds the magma from the rendered Lean source, and the two available shapes
have very different limits.

`finOpTable` parses its table string with `extractDigits`, keeping **one value
per digit character**. A cell holding `10` becomes two cells, `1` and `0`, and
the whole table shifts. Found 2026-07-29 by a `Fin 13` witness for `hard2_0051`
— the linear model `x ◇ y = 7x + 7y (mod 13)` — verified by hand, by
`equation_holds`, and by the solver's own `table_is_counterexample`, and still
`LEAN_REJECTED` with `decide` reporting the conjunction *false*.

That is a limit of one constructor, not of the judge. The conclusion drawn at
the time — "formula magmas fail the proof policy, so `finOpTable` is the only
sanctioned constructor and order ≤ 10 is a hard rail" — was **wrong, and cost
every FALSE row above order 10 for two days**. It rested on one experiment,
`fun i j => 7 * i + 7 * j`, rejected on `HAdd.hAdd` / `HMul.hMul`. The
*notation* was what failed the allowlist: `Nat.add`, `Nat.mul`, `Nat.mod`,
`List.getD`, `Fin.mk` and `Fin.val` are all under allowed prefixes. Rewritten
that way and judge-verified 2026-07-31, the same `Fin 13` witness is `accepted`
in 5.8 s, and orders 17 and 25 follow (11.2 s, 30.2 s).

So the shapes now split by order, and what bounds them is size and time:

- `solver.false_certificate()` renders order ≤ 10 through `finOpTable`
  unchanged — that is where all the accepted-cert evidence is — and everything
  above through an inlined `List.getD` lookup.
- `solver.table_is_renderable()`, inside `table_is_counterexample`, is the
  single gate every FALSE witness crosses. It measures the rendered certificate
  against the judge's 10,000-byte FALSE cap rather than guessing from order.
- `solver.witness_decide_is_affordable()` bounds the other limit. `decideFin!`
  is exhaustive, so an equation in `k` variables costs `n ** k` applications;
  order alone says nothing. Order 25 against a 3-variable goal is 15,625 and
  measured 30.2 s of the judge's 120 s. Orders ≤ 10 are exempt — the cost model
  is for new territory and must never veto the proven envelope.
- `oracles.check_false_certificate` re-verifies both shapes, still rejects a
  multi-digit `finOpTable` table, and independently re-checks the byte cap and
  the `decide` cost.

`MAX_WITNESS_ORDER = 25`. A FALSE row needing a *complete* table above that is
still out of reach, but the reach is now set by measurement, not by a parser
quirk.

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

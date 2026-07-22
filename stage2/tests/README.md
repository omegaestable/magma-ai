# Stage 2 offline correctness gate

The official Lean judge runs in the cloud, so nothing here calls Lean. These
tests verify the **mathematics** of every certificate the solver emits, which
is exactly where builder bugs turn into judge `incorrect` verdicts.

Run the gate:

```powershell
.\.venv\Scripts\python.exe -m pytest stage2/tests -q
```

`stage2/solver/package_solver.ps1` runs it automatically and refuses to
package on failure (`-SkipTests` only for a deliberate spike).

## What each layer checks

| File | Guards against |
| --- | --- |
| `oracles.py` | Library: an independent term parser/evaluator, a proof-expression kernel, and a finite-model oracle. Deliberately shares no code with `solver.py`, so a bug in a solver primitive cannot hide itself here. |
| `test_primitives.py` | The ~8 shared primitives every certificate depends on (`match_term`, `instantiate_term`, `context_to_lean`, `call_expression`, `replace_subterm`, `dual_term`, `_kb_unify`, `critical_pair_rules`). Includes mutation tests proving the oracles reject corrupted certificates. |
| `test_golden.py` | Coverage loss, route drift, and soundness loss on a route-diverse sample of real public problems. |

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

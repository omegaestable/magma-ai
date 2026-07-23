# 2026-07-22 session 3 — spot-check harness in use + soundness sweep

Built the randomized cross-source accuracy harness (design:
`stage2/docs/spotcheck.md`) and put it to work. This is the standing accuracy
loop from now on: run batches, fix anything pinned.

## Spot-check batches (accuracy loop)

Default effort `fast`, 5 TRUE + 5 FALSE per source, 9 sources = 90 rows/batch.
Ran the baseline plus seeds 101-104, 201-203, 301-305 (13 batches), an 80-row
ETP-only sweep, an 80-row `standard`-effort hard-set sweep, and edge-case runs.

- **1,189 distinct rows tested** (coverage ledger, deduped), spread across all
  nine sources — including 216 from the `etp` source (Equational Theories
  Project matrix, problems well outside the benchmark distribution), and hard1's
  entire 69-row pool.
- **100% accuracy on every single batch. 0 mistakes. Nothing pinned.**
- Coverage 82-96% per batch; the remainder are safe skips (the solver declines
  rather than guess). The prefer-unseen ledger fanned batches across the corpus
  so repeated runs kept finding fresh rows even at fixed seeds.
- Edge case verified: requesting more rows than a small pool holds (40 TRUE from
  hard1's 24) caps gracefully, no duplication or crash.

## Soundness surface — mapped and swept

The offline oracle chain has exactly one model-check-only surface; everything
else is exact and cannot pass an unsound certificate:

| Certificate | Check | Gap |
| --- | --- | --- |
| FALSE (finite witness) | exhaustive re-verify — table satisfies eq1 and refutes eq2 over all assignments | none |
| TRUE `exact_expr` / `singleton` / `lemma` | proof kernel — exact equational derivation from eq1 | none |
| TRUE `other` (hand-written `*_block` combinator proofs) | finite-model refutation only | sampled |

The spot-check already model-checks every TRUE verdict, `other`-shapes included,
via the audit battery (exhaustive Fin2 + 300 Fin3 samples + the named
witness/structured/affine families). On top of that, a dedicated sweep re-checks
that one surface with a **heavy** battery — exhaustive Fin2 + Fin3 plus a
4,000-table random Fin4 sample of eq1-models — across `other`-shape TRUE
certificates. It confirmed **0 unsound across the first 20 `other`-shape certs
(463 rows scanned)** before it was stopped — because it surfaced a real bug
(below), not because it found an unsound proof.

### The sweep surfaced (and we fixed) a scalability bug

The sweep called `solve_problem` in a tight loop and climbed to **16 GB RSS** —
the same unbounded module-level term caches the 2026-07-21 session found in
Marathon. The session-2 fix (`clear_term_caches()` per problem) only lived
inside `run_marathon()`. This session added the same clear to
`audit_corpus.audit_row` — the shared per-row entry point for the corpus audit
*and* the new spot-check harness — so long sweeps and large batches stay flat
instead of leaking to double-digit GB. A full `other`-shape Fin4 sweep is cheap
to re-run next session now that the leak is closed.

## Takeaway

Zero mistakes is the intended outcome, not a null result. The solver is
deterministic-first and skips rather than guess, so **accuracy is its design
invariant** and this session is the empirical confirmation across a wide,
partly-novel sample. The lasting value is a **regression tripwire**:
`stage2/experiments/spotcheck.py` + `stage2/tests/test_spotcheck_regressions.py`
mean any future change that introduces an unsound certificate or a wrong verdict
gets caught on the next batch and pinned into the pre-package gate forever.

## Next session

`python stage2/experiments/spotcheck.py` a few times (optionally `--effort
standard`, `--true 10 --false 10`, or `--sources etp` for the unlimited fresh
pool); fix anything it pins. After any change to a `*_block` route, re-run the
`other`-shape Fin4 sweep to re-cover the one model-check-only surface.

# Session notebook — preserve before pruning

This directory is the frozen working notebook behind the 2026-08-29 Austin
handoff. It contains 1,442 tracked files: 791 Python experiments, 317 Lean
files, 162 text artifacts, 60 research notes, and smaller judge/output sets.
The filename is not a reliability classification.

## Canonical documents

- `LEMMA_LIBRARY.md` — construction patterns and the validation ladder.
- `NOTES_*`, `PLAYBOOK_*`, `P2_*` — per-law mathematics and reusable methods.
- `SEMANTIC_TABLE.md` and `IDENTITY_INSTANCES.md` — classification evidence.
- `rec*.lean`, quotient/carrier proofs, and accepted/reusable proof fragments —
  inspect their judge/ledger status before editing or moving them.

## Reliability labels

- **Accepted:** present in `../certs/ledger.jsonl` and independently re-judged.
- **Candidate:** compiles or has zero sorries but is not ledger-accepted.
- **Model hypothesis:** passes some computational checks; must still pass every
  rung in `LEMMA_LIBRARY.md`.
- **Refuted/diagnostic:** retained because it records a counterexample, a bad
  guard, a failed oracle, or a reusable dead end.

Session 8 proved that `_orch_min*`, “CLEAN” logs, exhaustive bounded pools, and
one-sorry/zero-sorry appearance are not interchangeable with acceptance.
Do not bulk-remove underscore-prefixed files: `_sq33020.lean` was a complete
proof hidden only by the certificate byte cap.

## Cleanup rule

Generated `__pycache__`, `.pyc`, and new runtime logs may be removed. Everything
else must first receive a status, law/row id, last validation, and replacement
or archive location. The next solver-focused session should work from the
handoff's ranked open list rather than scanning this directory alphabetically.

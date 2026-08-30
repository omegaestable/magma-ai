# Austin research set

This is the archived construction laboratory for
`data/hf_cache/research_order5_hard.jsonl`. It is not imported by the submitted
solver and is not a benchmark runner.

Current measured state (2026-08-29): **60/100 rows have real-judge-accepted
certificates** and are distilled into the solver. The authoritative research
handoff is [`stage2/docs/DEEP_SESSION_8_AUSTIN_HANDOVER.md`](../../docs/DEEP_SESSION_8_AUSTIN_HANDOVER.md).
Read that file and [`automata/gen/LEMMA_LIBRARY.md`](automata/gen/LEMMA_LIBRARY.md)
before resuming solver work.

## Directory map

| Path | Role |
| --- | --- |
| `automata/` | Current tag-automaton, quotient-carrier, renderer, judge, and ledger tooling. |
| `automata/certs/ledger.jsonl` | Append-only accepted-certificate research ledger. |
| `automata/gen/` | Frozen session notebook: proofs, validators, notes, generated candidates, and failure evidence. See its README before changing it. |
| `austin_z3.py`, `pwl_search.py`, `term_model.py`, `tagged_model.py`, `repair_model.py` | Earlier diagnostic families. Their negative results are historical evidence, not current next steps. |

The 2026-08-28 first-pass diagnosis and its 69-hypothesis table remain in
`stage2/results/2026-08-28-assessment-deterministic-austin-tidy.md`. They are
superseded operationally by session 8; do not read “nothing here is a solver
route” as current status.

## Retention policy

- Keep judge-accepted certificates, zero-sorry Lean files, `NOTES_*`,
  `PLAYBOOK_*`, `P2_*`, `LEMMA_LIBRARY.md`, validators, and ledgers.
- Treat `_orch_min*` and any “clean” model without the session-8 oracle ladder
  as hypotheses, not proof evidence.
- Do not bulk-delete underscore-prefixed files. Session 8 harvested a complete
  proof from one such file.
- Runtime caches, bytecode, and new `.log` output are disposable and ignored.
- Promote only through the append-only ledger, real judge verification,
  fixture pinning, packaging, and the repository gate.

Run tools from the repository root with the Python 3.11 environment unless a
tool's own help says otherwise.

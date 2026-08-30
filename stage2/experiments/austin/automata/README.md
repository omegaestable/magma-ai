# Austin automata laboratory

This directory contains the reusable construction machinery behind the Austin
research set. It is an experiment surface, not a dependency of
`stage2/solver/solver.py`.

Start with:

1. [`../../../docs/DEEP_SESSION_8_AUSTIN_HANDOVER.md`](../../../docs/DEEP_SESSION_8_AUSTIN_HANDOVER.md)
2. [`gen/LEMMA_LIBRARY.md`](gen/LEMMA_LIBRARY.md)
3. [`gen/README.md`](gen/README.md)

Session 8 raised the accepted set to 60/100 and invalidated several models
that earlier bounded checks had called clean. The handoff's twelve-rung oracle
ladder is therefore part of the correctness contract for every future model.

## Stable entry points

| File | Role |
| --- | --- |
| `laws.py` | Parsing, law catalogue ids, and duality. |
| `symb.py` | Symbolic model verifier. A zero result is one oracle, not sufficient promotion evidence. |
| `synth.py` | Seeds, CEGIS repairs, minimisation, and dual-model helpers. |
| `render2.py` | Lean certificate renderer. |
| `concrete.py` | Ground evaluator and biased random checks. |
| `batch.py` | Batch model search. |
| `pipeline.py` | Render candidates, judge them, and prepare ledger entries. |
| `verify_certs.py` | Re-judge candidate certificates; writes a verification report only. |
| `append_ledger.py` | Append verified rows to `certs/ledger.jsonl` idempotently. |
| `ship.py` / `splice_certs.py` | Prepare fixture and distilled-certificate changes from accepted ledger rows. |
| `judge1.py` | Judge one certificate against one implication pair. |
| `ledger.py` | Accepted-row summary. |
| `killbatch.py` | Stop a batch driver and its worker tree. |

`complete.py` and the earlier tag-model scripts are retained measurements of
approaches that diverge or need stronger validation. They are not production
routes.

Run commands from this directory with `PYTHONIOENCODING=utf-8` and the
repository's Python 3.11 interpreter. Never replace the fixture wholesale;
Austin promotion must preserve pins written by other route families.

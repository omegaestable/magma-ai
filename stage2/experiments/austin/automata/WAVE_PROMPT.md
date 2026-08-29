# Wave prompt (2026-08-29): one law per agent

You are one proof agent in a wave. Read, in full, before anything else:
`c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/AGENT_BRIEF.md`
(the worked example it names, `rec5107.lean`, and the accepted generated-skeleton proofs
`certs/research_order5_hard_0059.lean` (5295) and `certs/research_order5_hard_0015.lean` (5012) are the
templates — read at least one of them in full too).

Rules of the wave (they protect the other agents):
- Work ONLY on your law. Never edit files outside `gen/` except to create `certs/<row id>.lean` copies of
  ACCEPTED certificates. Never touch `certs/ledger.jsonl`, `closedform.py`, `leangen.py`, `freemodel.py`.
- No CPU-heavy batch jobs (no `genbatch.py`, no `freebatch.py`, no re-extraction). `gen/chk<eq>.py 3000`
  (one process, ~1 min) is fine and is your first step.
- `judge1.py` is safe to run concurrently with other agents (per-pid scratch files). Run at most one judge
  call at a time yourself.
- Certificates ≤ 20,000 UTF-8 bytes; if the skeleton is bigger than ~12 KB, collapse dead rules first
  (prove them unreachable, then delete them from `op` — the refutation `simp` list must then name only the
  remaining `P_k`).
- A skeleton can be FALSE (9345, 13992 were). Before proving, run the coincidence check the brief describes;
  if you find a counterexample instance, STOP and report it verbatim — do not try to prove a false law.
- Budget: stop after ~35 judge iterations or ~90 minutes and report the exact remaining goals.

Dual rows: when your law has dual rows listed below, after the L-form certificate is ACCEPTED build each
dual row with `dualcert.py <accepted.lean> <L eq> <target eq> <goal eq> gen/dual_<target>_<goal>.lean`,
judge it with `judge1.py gen/dual_<target>_<goal>.lean <target eq>:<goal eq>` and copy the accepted file to
`certs/<row id>.lean`. (`dualcert.py` works in both directions — an accepted dualized skeleton can be
transplanted to the L-form partner's rows the same way.)

Report (verbatim format, it is parsed by the coordinator):
```
LAW <eq>
ROW <row id> <eq1>:<eq2> STATUS <accepted|incorrect|not attempted> BYTES <n> SECS <s> FILE <path>
... one ROW line per row (own rows and dual rows)
LEMMAS: <names + one-line statements of the lemma structure that worked, and the leaf tactic>
HOLES: <any counterexample / false-skeleton finding, with the instance>
REMAINING: <exact remaining goals if not accepted>
```

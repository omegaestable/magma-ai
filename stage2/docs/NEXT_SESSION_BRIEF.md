# Next session brief — the deep sweeps

**State: end of the 2026-08-27 improvement pass 2.** Read `CLAUDE.md` first
(authoritative), then this file for what to do, then
`stage2/docs/DEEP_SWEEP_RUNBOOK.md` for the exact commands. Session evidence:
`stage2/results/2026-08-27-improvement-pass-2.md`; the pass-1 record is
`stage2/results/2026-08-26-improvement-pass.md`.

Deadline **2026-08-31 23:59 AoE**. The deliverable is unchanged: one
`stage2/submissions/solver.py` ≤ 500 KB, plus
`stage2/solver/SUBMISSION_NOTE.md`.

---

## 1. Where the numbers go

```
<<FINAL-NUMBERS: filled at session end>>
```

Coverage, gate, packaged size and real-judge counts for pass 2 are filled in by
the verification run and mirror into `CLAUDE.md`'s *Current measured state*
table (which carries the same marker). Until then, **quote the pass-1 table in
`CLAUDE.md` and say so** — do not write a predicted number as a measured one.
That mistake is on the record: the "1650" headline of 2026-07-29 was 1647 plus
three predicted rows, and it made a clean run look like a regression.

Rules for every number this session produces:

- diff by **row id**, never by total (rail 2);
- record the **worker count and the machine load** next to every wall clock
  (rails 19, 22);
- label any stratified batch as stratified (rails 18, 33);
- after any fixture or test change compare the **skip** count, not just the
  pass count (rail 16).

---

## 2. What shipped in improvement pass 2 (2026-08-27), by agent

Seven agents worked in parallel git worktrees off `319d778`. Branch names are
`impl/<key>`.

| Key | What it owned |
| --- | --- |
| `compliance-tests` | Submission-layout enforcement (a stray `__pycache__` makes the official runner reject the whole submission — rail 23), the judge input-grammar hardening (`[A-Za-z0-9]` identifiers are legal — rail 27), banned-token / fixture / packaged-artifact test coverage, and the `run_solo` and memory-guard-reset regression tests that had never existed. |
| `false-side` | The z3-harvested order-5 witness library and the FALSE-search deadline fixes — `local_model_counterexample`'s size loop and the cheap constraint schedule were each running under **one** deadline for the whole loop (rail 28), so every size and order after the first was dead code. |
| `completion` | Unfailing-inference work on the order-5 collapse bucket: equations with incomparable variable sets were inert (`ori == []` blocked both rewriting and superposition), the passive queue truncated silently at its cap, and hitting `COMPLETION_MAX_ACTIVE` set the *global* expiry flag and skipped the post-saturation goal bridge. |
| `lean-formula` | Closed-form witness rendering — arithmetic and bitwise magmas instead of `List.getD` tables (7x cheaper, 2.7x smaller, and it reaches orders 26–60), the corrected `decide`-cost axis (rail 26), and a mechanised infinite-ℕ countermodel route replacing hand-distilled certificates. |
| `pacing` | Route ordering and budget: the last-resort FALSE searches ran after all fourteen TRUE engines, so a 0.2 s witness cost 262.9 s end-to-end; Solo withheld 1,310 s for an LLM lane with 0 accepts in 433 real calls; `COMPLETION_ROUTE_MAX_SECONDS` clamped the one engine measured to be budget-bound. |
| `mined-laws` | The 31 LLM-mined rung laws that close **19 of 51** order-4 residual rows deterministically (3/3 real-judge accepted); one law closes all 17 residual eq1-`3983` rows. Two of the three best are outside `enumerated_lemma_library()`'s grammar, which is why the ladder never found them. |
| `llm-lane` | Marathon LLM pacing (one call per row per run under a flat 64-call cap that ignores N; 1.3% / 0.03% budget utilisation), the derivation-consuming parser, and the measurement that retired several protocols outright. |

Documentation, rails and this handover: `impl/docs`.

---

## 3. What to do next, ranked

### 3.1 Sweep the half of order-5 nobody has measured

**The single largest unknown.** Every order-5 sweep on record ran at
`--max-variables 3`, but **56.9%** of `eq_size5.txt`'s 62,576 laws have ≥ 4
variables, and the only local proxy for the private Order-5 category
(`data/hf_cache/evaluation_order5.jsonl`) is 50% ≥ 4 variables and exactly
100 TRUE / 100 FALSE, against a uniform catalog draw whose TRUE fraction is far
lower. Order 5 is **a quarter of the final score**.

A 250-row batch is already generated:
`stage2/experiments/order5-ge4var-250-2026-08-27.jsonl` (seed 20260827; tracked
in the repo since 2026-08-27 — eq1 variable counts 4:175, 5:65, 6:9, 7:1). Audit
it first — `audit_corpus.py --file <it> --effort fast --row-budget 60 --workers 3`
on an idle box — and report its skip rate **next to** the ≤3-var 1.76%. If it is
materially higher, that is a bigger lever than anything else in this file; if it
is lower, the collapse work is correctly sized as marginal. Then draw a larger
batch with the new `sample_order5_pairs.py --min-variables 4`.

### 3.2 Order-4 at scale, and at the tiers we ship

The order-4 frontier concentration (four laws = 70% of misses) was measured at
110,000 rows and rose with sample size. Re-measure it after pass 2's mined laws
and pacing changes: the 19/51 residual rows the mined laws close are exactly
this population. Then run the two tier passes the audit default never exercises
(rail 12): `--effort standard --row-budget 540` (models Marathon) and
`--effort deep --row-budget 1980` (models Solo).

### 3.3 Keep harvesting z3 witnesses

The only measured-productive source of new order-5 FALSE coverage: 13 tables /
2,091 B cover 30.7% of the misses, and it is **not saturated** — 100 further
held-out misses yielded 17 more FALSE, all at order 9. Loop and numbers in the
runbook, §6.

### 3.4 Preflight and upload

`stage2/docs/playground-preflight.md`, end to end. It now checks that
`stage2/submissions/` holds `solver.py` **and nothing else**, and that
`SUBMISSION_NOTE.md` discloses every generated payload the artifact ships
(distilled certificates, the witness tables, the mined-law library, the
formula witnesses).

### 3.5 Bytes, if a change needs them

The packaged artifact had 73 KB of headroom after pass 1. `DISTILLED_CERTS`
remains the dominant cost and many entries are live-solvable, but they are
**judge-pinned bytes**: delete one only when a new engine needs the room, and
only after confirming the live route re-derives it and the real judge accepts
the result (rails 1, 5h, 3c).

---

## 4. Do not re-run these

All measured on 2026-08-27; the numbers are in `CLAUDE.md`'s dead-ends table
with the diagnosis file for each.

- Widening `FP_WITNESS_TABLES` from the rest of teorth's FinitePoly library for
  order-5 — the whole 1,048-table remainder is worth **2 rows of 351**.
- A random Latin-square / quasigroup generator — **800** squares of orders 8–9
  satisfy **0** of 280 order-5 hypotheses.
- A FALSE-table LLM protocol or table-repair loop for the hard frontier —
  24/24 rows steered to FALSE, **0 valid tables**, including on 10 positive
  controls with shipped witnesses.
- `reasoning_effort=medium` — 2.8x tokens, 7x wall, **the same 2 of 37** rows.
- Any further completion cap / selection strategy for the order-5 collapse
  bucket — **eleven strategies converge on the same 6 of 40**, a mirrored KBO
  (a genuinely different ordering) finds *exactly the same six*, and 60 s buys
  nothing over 20 s. The only untried idea with upside is a much faster core
  (term interning + discrimination-tree indexing, ~15 → 1000+ equations/s),
  which is a repo-wide rewrite and the wrong shape of change now.
- An LLM lane or mined-law pass on order-5 — 120 calls / 0 settled, and 0/80
  for the mined laws.
- An infinite-carrier confluence certificate for the order-4 FALSE residue
  (eq1 `481`, `2531`, `1661`, `1486`) — **NO-GO offline**: the teorth cache
  stores entry names and file:line only, no Lean source, and the sandbox has no
  network. With network, the first step is fetching
  `equational_theories/Confluence3.lean` and transcribing the `rw481`
  construction.

---

## 5. Free signal worth using

When `_completion_prove_once` **saturates with `n_dropped_size == 0`**, the
resulting terminating ground-confluent system whose normal forms are not all
identified *is* a model of eq1 with ≥ 2 elements — so eq1 does not force
triviality and the row cannot be TRUE-by-collapse. `order5_22455_53402` is
provably in that state despite being tagged a collapse candidate. Read such a
saturation as "saturated under *this* ordering" (`order5_12073_57821` saturates
under a mirrored KBO but not the standard one) and route the row to the
FALSE/infinite-countermodel queue instead of spending more TRUE budget on it.
Record it as a stderr route label only — the answer JSON is exactly
`{verdict, code}` (rail 8).

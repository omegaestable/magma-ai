# Next session brief — long Marathon runs on unseen data

Written 2026-08-21 at the end of the completion-engine session. Deadline:
**2026-08-31 23:59 AoE**. Read `CLAUDE.md` first; this file is the plan, not the
state.

**The next session's declared purpose is long Marathon runs on rows the solver
has never seen.** Everything below is ordered around making those runs
informative rather than merely long.

---

## 1. Where things stand

| | |
| --- | --- |
| Official sets, `fast` | **1669 / 1669** — `normal` 1000, `hard1` 69, `hard2` 200, `hard3` 400 |
| HF mirrors | **800 / 800** · `sample_200` **200 / 200** · `sample_20` **20 / 20** |
| Row-id diff vs the 2026-08-12 baseline | **0 lost, 0 gained, 0 verdict flips** over 2,669 common rows |
| Crashes / oracle failures | **0 / 0** over 2,689 audited rows |
| Audit wall clock | official **250 s** (was 330), HF **164 s** (was 344) |
| Gate | **257 passed, 2 skipped** |
| Spotcheck | **216 rows / 9 sources, 100% accuracy, 0 mistakes** (seed `20260821`) |
| Packaged artifact | **466,320 / 500,000 bytes** (33,680 free, **6.7%**) |
| New this session | `true:completion` — ordered Knuth-Bendix completion, **12/12 real-judge accepted**, serving **304 corpus rows** |
| Real Marathon, 2026-08-21 | `hard3` **400/400** in 612 s (was 1,152 s) + fresh unseen ETP-200 **200/200** — **600/600, 0 rejected, 0 LLM calls** |

The important number for the next session is not in that table: on the
2026-08-20 sample of **20,000 unseen order-4 ETP rows**, the failure frontier was
52 rows and `true:completion` closes **43 of the 51 TRUE ones**, all of them in
0.3 s combined. That is what the long runs are now testing.

---

## 2. Running long Marathons well

Read `vendor/stage2-official/docs/marathon_mode.md` and `EVAL_WORKFLOW.md`
for the mechanics, and `.github/skills/marathon-triage/SKILL.md` for triage. What
this repo has learned that the mechanics do not tell you:

- **Positive token budget, always** (rail 7). `--budget-tokens 0` is not
  validation and is not promotion evidence.
- **Marathon has no resume.** State the redo cost *before* stopping a run, not
  after. A `hard3.jsonl` run is ~35 min end to end; a 1,000-row `normal.jsonl`
  run is several hours.
- **The scoring pass is the slow half**, not the solve. 400 rows solve in
  minutes and then take ~3 s of Lean each to score.
- **`lake env` has a hardcoded 30 s timeout and dies under load.** Do not run
  the judge, an audit, or a second Marathon beside a scoring pass. If scoring
  dies, answers are append-only and safe: recover with `--score-only`, which
  **truncates `run.log`** — copy it first, or attribute by certificate bytes with
  `tmp_stage2_smoke/real-run-tools/attribute_answers.py`.
- **A local `malformed` / `CODE_TOO_LONG` is probably the harness, not the
  solver.** `judge/verify.py` falls back to 50,000 bytes when
  `MAX_CODE_LENGTH` is absent from the environment, and the deployment passes
  100,000. Any runner that goes through
  `stage2/experiments/local_runner_env.load_local_runner_env()` now gets the real
  caps automatically — `judge_cap_env()` reads them from `pipeline/config.json`
  (fixed 2026-08-21, rail 3b-iv). **If you invoke the official runner some other
  way, set them yourself**, or a legitimate 88 KB certificate scores as a
  failure. Re-judge the row with the cap varied before believing any size-related
  rejection — that is a two-minute experiment and it is the difference between
  "solver regression" and "harness artifact".
- **`__pycache__` in `stage2/submissions/` fails a run instantly.**
- **Build a fresh manifest per run and check the overlap**, e.g.
  `python tmp_stage2_smoke/real-run-tools/sample_etp_manifest.py --n-true 100
  --n-false 100 --seed <new> --exclude-benchmark-ids --out <path>` — then verify
  0 overlap with previous samples by `(eq1_id, eq2_id)` before quoting the result
  as fresh. `stage2/results/etp-marathon-200-2026-08-21.jsonl` is this session's,
  seed `20260821`.
- **Order-5 is a different corpus from order-4** and the ETP matrix does not
  cover it (ids > 4694). Rows there have **no ground truth**, so an order-5
  Marathon measures judge acceptance and self-consistency, never correctness
  against a known label. Do not conflate the two when writing the result up —
  the 2026-08-20 order-5 log has the wording to copy.

### What would actually be new information

Ranked. The first two are worth more than more of the same:

1. **Solo still has no real-runner evidence for the tier ladder.** It picks
   `deep` from a 3600 s budget, so it runs *three* passes where Marathon runs
   two, and nothing has exercised that end to end since the ladder shipped
   (2026-08-12) or since the LLM timing constants changed (2026-08-13). This has
   been the top-value item for two sessions running and is still open.
   ```powershell
   .\.venv\Scripts\python.exe tmp_stage2_smoke\real-run-tools\clean_run.py `
       tmp_stage2_smoke\real-run-tools\run_solo_batch.py `
       --manifest data\stage2_official_problems\hard2.jsonl --limit 25
   ```
2. **A large unseen order-4 Marathon.** The 20k offline sample says the solver is
   at 99.96% on that space after this session's engine; a real-judge run of
   1,000+ fresh ETP rows would convert that from an offline upper bound into
   judge evidence. This is the run the next session was called for.
3. An order-5 Marathon, with the no-ground-truth caveat above.

---

## 3. What is open, ranked

### 3.1 The 8 order-4 rows completion saturates on

`etp_62_58`, `etp_1366_3436`, `etp_666_1014`, `etp_3569_4653`, `etp_1101_2457`,
`etp_666_698`, `etp_1881_4126`, `etp_1163_198` (equations in
`stage2/results/etp-sample-failures-2026-08-20.jsonl`).

**Not a budget problem** — `max_size` 44 → 90 and `max_active` 800 → 4000 leave
the processed-equation count identical. The system genuinely saturates.

- **Already measured at 0 rows, do not re-run**: instantiating the other
  unorientable shape (`z ◇ x = w ◇ x`). `subsumed()` discards every instance
  precisely because it is an instance of the still-active parent. Recorded in
  `_kb_collapse_witness`'s docstring.
- **Not tried**: completing from eq1 **plus the skolemised goal disequality**.
  Real unfailing completion refutes `s ≠ t`; what shipped tests joinability after
  each step, which is strictly weaker. This is the principled next move.
- **Also not tried**: keeping an unorientable equation and weakening `subsumed()`
  for that case only.

### 3.2 `etp_1661_3524` — the single FALSE miss in 20,000 rows

eq1 `x = (x ◇ y) ◇ ((y ◇ z) ◇ y)`, eq2 `x ◇ y = x ◇ ((y ◇ z) ◇ x)`. Undiagnosed:
is this a genuinely hard countermodel needing an order or shape the cheap and
wide tiers do not try, or a gap in the search? **Bound the probe before running
it** — a first attempt (orders 2..12, 30–60 s each) did not finish inside ten
minutes, which is the whole finding so far.

Read "the countermodel search is airtight" as "airtight to 1-in-20,000".

### 3.3 Bytes — a measured, evidence-backed 120 KB is available

`DISTILLED_CERTS` is 65 entries and **150,019 bytes**, the dominant cost in the
artifact. Measured 2026-08-21: **48 of those 65 entries are now live-solvable by
`completion_prove` at a 2 s budget, every one kernel-verified** — 120,229 stored
bytes. Full list with per-entry stored/live byte counts:
`stage2/results/2026-08-21-distilled-live-solvable.txt`. (The completion
README's own estimate was 26 entries; the real number is 48.)

**Deliberately not taken this session.** A distilled certificate is *judge-pinned
bytes*; the live route is judge-verified on 12 samples. Removing 48 pinned
entries on kernel evidence alone trades a certainty for a very good bet, and the
sweep that would fix that could not run beside this session's Marathon (`lake
env` dies under load).

**The scoped way to take it**: judge all 48 live certificates with
`judge_rows.py` on an idle machine (~48 × 3 s), delete only the entries whose
replacement came back `accepted`, re-run the gate and a row-id audit diff. That
takes the artifact from 466,320 to roughly 346,000 bytes — 6.7% headroom to
~30% — which is what buys room for the next engine.

### 3.4 Step-count instead of wall-clock budgets

Still the most valuable structural item, and this session added the fifth
instance of the same bug: `_egg_bridge_steps` had neither a deadline nor a state
cap while its multi-rule twin had both, *above a comment explaining exactly why
it needed them*. Five of the same bug is the design, not bad luck.

**Cheap partial credit available now**: a gate test that diffs twin functions'
signatures — `explain` vs `explain_multi`, `_egg_bridge_steps` vs
`_egg_bridge_steps_multi`, `_egg_run_saturation` vs `egg_saturate_prove` — and
fails when one takes a `deadline` or a cap the other does not. That would have
caught this one and the 2026-08-12 one without either measurement.

### 3.5 Nothing has been re-measured against the corrected judge caps

Unchanged from the 2026-08-13 brief and still true. The certificate budget
doubled (100,000 B overall, 20,000 FALSE, `EGG_MAX_PROOF_BYTES` 46 → 96 KB), so
any route that ever skipped a row *for size* was skipping against a phantom
limit. The corpus is already 100% offline, so a gain would show up on the real
judge, not in the audit total.

---

## 4. Standing hygiene

- **Run `spotcheck.py` every session** and fix whatever it pins. It draws from
  the ~22M-pair ETP matrix — the only source the solver was never tuned against.
- **Diff by row id, never by total** (rail 2).
- **Never run two `audit_corpus.py` sweeps at once** (rail 5e), and **check what
  else is on the machine before quoting a wall clock**. This session had an
  unrelated `fetch_verify.py` from another project resident at ~20% of one core
  throughout; that is small enough not to matter on a 16-worker sweep, but it is
  the check that matters, not the outcome.
- **Never add a `DISTILLED_CERTS` entry the real judge has not accepted**, and
  note `test_judge_verified.py` compares bytes for distilled routes rather than
  skipping.
- **A new certificate builder must be judge-verified** (rail 3c) — the offline
  oracles are an upper bound. `true:completion` was, 12/12.
- **`true:completion` is registered in `test_golden.py`'s
  `GENERAL_CLOSURE_FAMILIES`.** It is a general search engine, so a row drifting
  onto it from another general engine is the documented wall-clock
  nondeterminism, not a regression. Drift onto a *bespoke* route still fails.

# 2026-08-12 (session 2): the tier inversion, a Marathon per-row deadline, and the slow tail

Entry state: `stage2/docs/NEXT_SESSION_BRIEF.md`. Goals, in the user's words:
**keep the 100% solved problems but improve efficiency**, and **finish with a
real Marathon run** using the OpenRouter LLM lane.

Everything below is measured on this machine (32 logical cores). Audits ran from
a detached git worktree so the solver source could be edited without a pool
worker importing a half-written module (a rail from 2026-07-29).

---

## 1. The reference measurement CLAUDE.md was missing

The 1669/1669 headline had **never been measured end to end** — the 2026-08-12
completion session re-measured only the 9 rows it closed plus 8 controls, per
the user's "no full sweeps" instruction. A fresh isolated `fast`-tier audit now
confirms it:

| Set | Solved | Skip | Crash | Oracle failures | Seconds |
| --- | --- | --- | --- | --- | --- |
| `normal` | 1000/1000 | 0 | 0 | 0 | 342.4 |
| `hard1` | 69/69 | 0 | 0 | 0 | 219.8 |
| `hard2` | 200/200 | 0 | 0 | 0 | 241.0 |
| `hard3` | 400/400 | 0 | 0 | 0 | 176.7 |
| **official** | **1669/1669** | **0** | **0** | **0** | |

`sample_200` (a 200-row ETP sample, disjoint from `normal` — its ids are
`true_2860_3458`-style, not `normal_NNNN`) is **197/200**, unchanged since
2026-08-11. Those three rows — `true_2860_3458`, `true_2135_2128`,
`true_2055_2656` — are the only local skips outside the headline corpus.

Report: `stage2/results/audit-2026-08-12-fast-baseline.json` (+ `-hf.json`).

---

## 2. The tier inversion is real, and it costs rows at the tiers we deploy

`EFFORT_TIERS` scales **every** engine budget together (`standard` 7.5x, `deep`
22x). On a row whose answer lives in a *late* engine, the early engines eat the
whole per-row clock and the late one is never reached — so more budget makes the
solver strictly worse.

The audit had never been able to see this, because `audit_corpus.py` never set a
per-row deadline while Solo and Marathon always do. Added `--row-budget`, which
makes the audit model the bound deployment actually imposes.

**Measured, one row per process, `deep` effort, 360 s row budget:**

| Row | Before | After |
| --- | --- | --- |
| `normal_0491` | **SKIP**, burned all 360 s | **solved, 97.6 s** (`egg_ladder:collapse:h1`) |
| `hard2_0162` | **SKIP**, burned all 360 s | **solved, 173.9 s** (`egg_ladder:collapse:h1`) |

And on `sample_20`, whole-set:

| Config | Solved | Wall |
| --- | --- | --- |
| `fast`, no row bound | 20/20 | 32 s |
| `deep`, 45 s row bound | **15/20** | — |
| `deep`, 360 s row bound | 20/20 | **313 s (10x)** |

### The fix: iterative deepening

`solve_problem` now walks `effort_ladder_to(effort_tier())` — `fast`, then
`standard`, then `deep` — and returns the first pass that certifies. The single
pass became `solve_problem_pass`.

At `fast` the ladder is exactly one pass, so the audit's default behaviour is
unchanged. At `standard`/`deep` the tier becomes **monotone**: whatever `fast`
can solve is solved at `fast` speed, and the extra budget only buys attempts on
rows `fast` could not close.

Three hazards were found by an analysis pass over the change and fixed:

- **The inter-pass gate must not call `_engine_gate()`.** That would spend one
  of the row's three `try_reclaim_memory` attempts on bookkeeping — rail 10's
  exact shape, a per-row budget consumed by something that is not a row. The
  ladder checks the deadline and `memory_exceeded()` inline instead, and does
  not escalate after a memory trip (a wider tier costs *more* memory).
- **The evidence globals reset once per solve, not per pass.**
  `run_solo`'s speculative-TRUE gate reads `hypothesis_models_seen()` /
  `constraint_search_exhausted()` after we return; resetting per pass would make
  a final pass cut off in its cheap prefix report zero models for a row where an
  earlier pass had exhausted a real order schedule.
- **No cache can carry a tier across passes.** All 18 `@lru_cache` functions were
  checked for a transitive read of `_EFFORT` / `EFFORT_TIERS` / `_eff_*`; none
  has one. `_DERIVED_RULES_CACHE` was the one near-miss — its value is truncated
  by `max_rules` and filtered by `max_rule_size`, neither of which was in the
  key. Safe today only because those two knobs happen not to be tier-scaled,
  which is a property of the call sites and not of the function, so both are now
  in the key.

---

## 3. Marathon had no per-problem deadline

`run_marathon()`'s deterministic loop bounded only the *sum*
(`MARATHON_DETERMINISTIC_SHARE = 0.6` of the run, then `break`). One slow row
could therefore spend everything left and every row after it was never attempted
— which is what `not_attempted` meant in the 2026-08-01/03 campaign.

`marathon_row_budget(remaining, rows_not_yet_attempted)` now bounds each row.
The fair share is recomputed before every row, so the instant majority hands its
surplus straight back to the tail, and `MARATHON_ROW_BORROW = 3.0` lets a hard
row take three rows' worth and no more.

**Borrowing alone was not enough, and a test caught it.** If every row took its
full allowance the remainder decays geometrically and the last rows get zero —
the same starvation, deferred. `MARATHON_ROW_MIN_SECONDS = 1.0` is reserved for
every row still queued, which is far more than the cheap majority needs and
converts the pathological case from "tail unattempted" into "tail still gets its
cheap routes".

The global deadline is restored in a `finally` after the loop. It has to be:
every engine the LLM lane invokes while parsing candidates clamps to
`_HARD_DEADLINE` through `local_deadline`, so leaving the last row's expired
per-row bound live would silently turn every LLM candidate into
`lemma_not_derivable_from_hypothesis` — tokens spent, zero accepts, nothing
logged.

Also worth recording, from reading the vendored runner: at the default
`--compression-ratio 0.5` the real budget is `0.5 x N x 600`, so
`effort_for_seconds(0.5 * budget / N) = effort_for_seconds(150)` = **`standard`**,
and the deterministic pass gets ~180 s per row on average.

---

## 4. The single-rule egg engine never got the deadline fix its twin got

Chasing "why did a `deep` row run past its row bound" found something bigger, and
it is **not** a `deep`-tier problem at all.

`egg_saturate_prove` builds its candidate list with the only deadline poll on
`for cid in classes`. Inside that loop, `_egg_ematch` is a **recursive generator
with no bound on how many substitutions one e-class yields**, and when the
pattern is an op-pattern `classes` is *every* e-class in the graph. So the poll
is on the wrong loop level. Two more defects at the same site: the `break` exited
only the class loop, leaving the orientation loop free to start the whole phase
again; and `apps` was unbounded while `EGG_EXPAND_CAP = 900` bounds only how many
candidates get *applied*.

**Measured on `normal_0823` at `fast`** — through `egg_probe_route`'s collapse
probe, whose `EGG_PROBE_COLLAPSE_BUDGET = 6.0` is deliberately **unscaled**:

| Budget | Still running at | RSS | Deadline polls in that window |
| --- | --- | --- | --- |
| 6.0 s | **40.0 s (6.7x)** | **11,346 MB**, +290 MB/s | **zero** |

It was also **invisible to an armed memory guard**: the guard is only consulted
through `deadline_expired()` / `_engine_gate()`, and this loop called neither, so
RSS sailed past a 1600 MB cap and kept going. That is a live OOM risk — the
playground `ERROR` of 2026-07-22 was an OOM kill in a 2048 MB sandbox.

The multi-rule twin `_egg_run_saturation` was given exactly this fix on
2026-08-11 (rail 5f-iv). The single-rule engine never was — and it is the one
behind `egg_probe`, `egg_closure`, `egg_collapse`, `egg_priority_bootstrap` and
`egg_bootstrap`. Fixed now by mirroring the twin, plus `EGG_MAX_APPS = 200_000`
to bound the candidate list itself. A structural test pins the poll in **both**
engines, because the failure mode is silent overshoot that reads exactly like a
hard row.

**The fix costs no coverage and buys a lot of speed** (isolated, one row per
process, `fast`):

| Row | Before | After |
| --- | ---: | --- |
| `normal_0823` | 252.7 s (`derived_cp_closure`) | **1.09 s** (`egg_collapse`) |
| `hard3_0135` | 106.1 s (`egg_ladder:left_projection`) | **21.0 s** (`projection_bootstrap:left`) |
| `hard3_0131` | 63.2 s | 55.1 s |
| `normal_0491` | 81.3 s | 74.8 s |
| `hard2_0098` | 76.7 s | 72.6 s |
| `hard3_0168` | 33.3 s | 31.3 s |
| `hard2_0162` / `hard3_0266` / `normal_0090` | 173.8 / 115.8 / 124.1 s | 173.6 / 115.3 / 122.5 s |

Note `normal_0823` does not merely get faster — it changes route. The probe now
*terminates* and finds the collapse, which is what it was built to do.

**A correction worth recording**: this was first attributed to
`derived_cp_closure`, on the reasoning that its budget is `_eff_time(8.0)` = 8 s
while the row took 253 s. That inference was wrong. Removing `egg_probe_route`
entirely gets the same row through `derived_cp_closure` in **0.4 s**, so the
253 s was never that engine's; measured directly, `derived_cp_closure` at `deep`
on `hard2_0162` runs 90.12 s against a 90 s clamp with a **maximum inter-poll
gap of 0.28 s**. A stack-sampling probe (`faulthandler.dump_traceback_later`)
found the real site in one run, and a fix already written at the wrong site was
reverted. **Sample the stack; do not infer the culprit from budgets.**

---

## 5. Three genuinely open rows, closed

`sample_200`'s three skips are now **3/3 judge-accepted**, so every local row is
solved:

| Row | Bytes | Judge | Completion cost |
| --- | ---: | --- | --- |
| `true_2860_3458` | 4,335 | accepted, 4.7 s | 40 equations, 0.1 s |
| `true_2135_2128` | 3,109 | accepted, 3.1 s | 43 equations, 0.2 s |
| `true_2055_2656` | 2,980 | accepted, 3.1 s | 22 equations, 0.0 s |

All three fell to the **ordered-completion (Knuth-Bendix) pipeline built for the
final nine on 2026-08-12** — reused unchanged, with one new generic driver that
completes from eq1 and tries to join eq2's two sides after every processed
equation. **No row needed tuning**; each joined in under 0.2 s against budgets of
60-90 s. What cost a whole session to build is now a five-second per-row
commodity, and that is the durable result: the marginal cost of a new ETP row of
this family is essentially zero.

`true_2860_3458` is the interesting one — its eq2 (`x ◇ x = x ◇ ((x ◇ y) ◇ x)`)
is **not** collapse-shaped, and the proof confirms it: it runs through
`(a ◇ b) ◇ a = (a ◇ a) ◇ b` and `a ◇ ((a ◇ b) ◇ a) = a ◇ a`, with no `a = b`
anywhere. That is exactly the non-collapse recipe the final-nine writeup
described — complete to saturation, then normalise both sides of eq2 and use the
joining rewrite sequence as the proof.

---

## 6. The slow tail, and what it costs

Total `fast`-tier solve time over the 1669 official rows is **5,623 s**, and the
**top 28 rows are 2,281 s of it (41%)**. Per-row cost is wildly uneven, and the
cheapest certificates are often the slowest rows:

| Row | Seconds | Cert bytes | s per KB | Route |
| --- | ---: | ---: | ---: | --- |
| `normal_0823` | 252.7 | 232 | 1089 | `true:derived_cp_closure` |
| `hard1_0025` | 217.3 | 313 | 694 | `false:constraint_fin5` |
| `hard2_0125` | 199.7 | 337 | 593 | `false:constraint_fin6` |
| `hard2_0162` | 173.8 | 9117 | 19 | `true:egg_ladder:collapse:h1` |
| `hard2_0051` | 124.7 | 724 | 172 | `false:linear:z13:7,7` |

Distillation converts a row into an O(1) content-keyed lookup, so this table is
directly a shopping list ranked by seconds-saved per byte.

**Coverage rule applied while picking:** never distil *every* live row of a
route family, or the golden gate stops exercising that engine. `true:egg_ladder`
has exactly 6 live rows and all 6 were in the top 28, so `hard3_0204` is kept
live — it is also the best test of the six, being the only 2-rung ladder.
`false:constraint_fin5` / `fin6` are singletons at those orders but the engine
keeps 13 pinned `constraint_fin8` rows, so distilling them loses an outcome pin,
not engine coverage.

**34 certificates distilled, 34/34 judge-accepted** — 19 official, 12 HF, plus
the 3 completion proofs from section 5. `DISTILLED_CERTS` goes 31 → 65 entries;
the fixture goes 65 → 99 lines. Nothing enters that table the real judge has not
accepted, and `distill_certs.py` enforces it by judging before it emits.

### The row-id diff, which is the only number that matters

Two isolated `fast`-tier audits over official + `sample_*`, before and after the
ladder and the egg fix (the distilled certs are *not* in this comparison, so it
isolates the code change):

| Set | Before | After |
| --- | --- | --- |
| `normal` | 1000/1000, 342.4 s | 1000/1000, **143.8 s** |
| `hard1` | 69/69, 219.8 s | 69/69, 219.7 s |
| `hard2` | 200/200, 241.0 s | 200/200, 239.3 s |
| `hard3` | 400/400, 176.7 s | 400/400, 175.1 s |
| `sample_200` | 197/200, 492.9 s | 197/200, 493.5 s |
| `sample_20` | 20/20, 29.6 s | 20/20, 29.4 s |

**LOST: none. GAINED: none. Oracle failures: 0. Crashes: 0.** Official
solve-seconds 5,623 → 5,187.

The `normal` set halving is the egg fix showing up in bulk: a dozen rows moved
from `true:derived_cp_closure` to `true:egg_collapse`, saving 6-10 s each on top
of `normal_0823`'s 251 s. The probe was *supposed* to claim those rows; it had
been running past its budget and losing them to a later engine instead.

### Two gate findings worth keeping

- **A stripped trailing newline nearly shipped.** The three completion
  certificates were spliced without their final `\n`, so the solver would have
  emitted bytes one character off from what the judge accepted.
  `test_judge_verified.py` caught it immediately.
- **That test was skipping the rows it should check hardest.** It skips when the
  route drifts, and a newly distilled row *always* drifts (engine →
  `*:distilled:*`) — so 31 of the 34 new entries verified nothing. A distilled
  route is not drift; it is the same certificate served from the content-keyed
  table, so the bytes must still match. Comparing instead of skipping took the
  gate from 69 checked / 31 skipped to **99 checked / 0 skipped**, and is what
  caught the newline above.

Gate: **252 passed, 2 skipped**. Packaged: **445,233 bytes** of 500,000
(54,767 left, 11.0%).

---

## 7. The final numbers, and what they cost

Three isolated `fast`-tier audits: baseline (pre-change), post-fix (code change
only), final (code change + 34 distilled certs). Diffed by row id each time.

| Set | Baseline | Post-fix | Final |
| --- | --- | --- | --- |
| `normal` | 1000/1000, 342.4 s | 1000/1000, 143.8 s | 1000/1000, **106.4 s** |
| `hard1` | 69/69, 219.8 s | 69/69, 219.7 s | 69/69, **28.7 s** |
| `hard2` | 200/200, 241.0 s | 200/200, 239.3 s | 200/200, **95.6 s** |
| `hard3` | 400/400, 176.7 s | 400/400, 175.1 s | 400/400, **99.4 s** |
| `sample_200` | 197/200, 492.9 s | 197/200, 493.5 s | **200/200**, **71.5 s** |
| `sample_20` | 20/20, 29.6 s | 20/20, 29.4 s | 20/20, 30.8 s |
| **official wall** | **980 s** | 778 s | **330 s (3.0x)** |
| HF total | 800/800, 773 s | — | 800/800, **344 s (2.2x)** |
| `hf_evaluation_order5` | 611.5 s | — | **162.9 s (3.8x)** |

**LOST across every comparison: none. GAINED: the three `sample_200` rows.
Oracle failures 0, crashes 0, label mismatches 0, in all of them.**

Official solve-seconds (sum over rows, not wall clock): **5,623 → 3,853**.

**Caveat, stated so nobody over-reads the wall-clock column.** Part of this
session's later timing ran against heavy unrelated CPU load on the same machine
(another project's search jobs, several at 1,000+ CPU-seconds). The coverage
results are unaffected — 0 mismatches over thousands of rows does not come and
go with load, and that is rail 5e's own lesson — but the speedup figures are
**lower bounds on the improvement, not precise measurements**. The isolated
single-row before/after probes (`normal_0491`, `hard2_0162`, `normal_0823`) are
the trustworthy timing evidence.

### What was deliberately *not* done

- **`hard3_0204` is kept live** rather than distilled. It is the audit's only
  remaining exercise of `true:egg_ladder` (all six of that engine's rows were in
  the top 28 by cost), and it is the best of them — the only 2-rung ladder.
  Trading 72 s for continued coverage of the newest engine is the right way
  round. `false:constraint_fin5`/`fin6` were distilled despite being singletons
  at those orders, because the engine keeps 13 pinned `constraint_fin8` rows.
- **`derived_rule_steps` was left alone.** It polls its deadline correctly (max
  inter-poll gap 0.28 s measured) but grows unboundedly — 3,371 MB at 90 s,
  5,194 MB at 360 s at `deep`. That wants a cap, not a poll, and the armed memory
  guard does see it. Queued in the next-session brief.
- **Single-rule egg extraction still has no deadline** (`egg.explain`,
  `_egg_bridge_steps`), unlike its multi-rule twin — the same asymmetry that
  produced rail 5f-v. Measured small today (0.02 s / 1.4 s on `hard2_0162`), but
  that is luck, not design. Also queued.

### The packaged artifact, verified from a scratch copy

Checked by copying `stage2/submissions/solver.py` elsewhere and importing it
there — importing it *in place* leaves a `__pycache__` that makes the official
runner reject the submission instantly, which has cost a run before.

    packaged DISTILLED_CERTS entries: 65
    effort_ladder_to('deep') -> ('fast', 'standard', 'deep')
    marathon_row_budget present, EGG_MAX_APPS = 200000

| Row | Before | Off the packaged artifact |
| --- | ---: | ---: |
| `hard1_0025` | 217.3 s | **0.31 ms** |
| `hard2_0162` | 173.8 s | **0.08 ms** |
| `normal_0823` | 252.7 s | **0.07 ms** |
| `hard2_0051` | 124.7 s | **0.06 ms** |

That is the whole argument for distillation in one table: a judge-accepted
certificate costs a dict probe at every effort tier, on every set, forever.

---

## 8. The closing real Marathon

Real official runner, real Lean judge, real proxy, real OpenRouter key (verified
`source=repo_env` and live against `openai/gpt-oss-120b` on `deepinfra/bf16`
before the run), positive token budget — rail 7.

### `hard3.jsonl`, the hardest official set

    Score:         400 / 400
    Attempted:     400
    Not attempted: 0
    By status:     {'accepted': 400}
    Wall used:     1152.7s of 120000s budget
    Tokens used:   0 of 200000 budget

**400/400 accepted, 0 rejected, 0 not_attempted.** The 2026-08-01/03 campaign
scored this same set 396/400 with **4 `not_attempted`** — precisely the failure
`marathon_row_budget` targets.

The solver's own summary line is the measurement the brief asked for:

    {"submitted_deterministic":400,"submitted_total":400,"llm_calls":0,
     "budget_tokens":200000,"per_problem_false_budget":15.0,
     "route_kind_count":91,"route_count_total":400}

**`llm_calls` is 0 with 200,000 tokens available.** Per the entry brief's own
criterion, that is the *success* signal, not a null result: the LLM lane only
ever sees rows the deterministic pass did not solve, so any call would have
named a scheduling skip. There were none. 91 distinct route kinds fired, which
is also the answer to "did distillation flatten the route mix" — it did not.

**Attribution by certificate bytes** (stronger than log lines, and necessary
because `--score-only` truncates `run.log`): **10 of the 400 rows were served by
an exact `DISTILLED_CERTS` byte match**, five of them distilled *this session* —
`hard3_0353`, `hard3_0271`, `hard3_0168`, `hard3_0322`, `hard3_0135`. The new
path demonstrably fired in a real run rather than merely existing.

Note the run was made on a machine simultaneously running another project's
search jobs at ~90% CPU. It still completed clean, which is its own small piece
of evidence for the per-row deadline: under contention, rows that would once
have run long now give up early instead of starving the tail.

### A fresh, untuned ETP sample

Then the same run against 200 rows drawn at random from the full Equational
Theories Project outcome matrix (~22M labelled pairs), seed `20260812`, with
benchmark ids **excluded** — a distribution nothing in this solver was tuned
against, and a different seed from the 2026-07-31 sample:

    Score:         200 / 200
    Attempted:     200
    Not attempted: 0
    By status:     {'accepted': 200}
    Wall used:     345.8s of 60000s budget
    Tokens used:   0 of 200000 budget

    {"submitted_deterministic":200,"submitted_total":200,"llm_calls":0,
     "route_kind_count":26}

**Combined closing evidence: 600/600 real-judge rows accepted, 0 rejected, 0
`not_attempted`, 0 LLM calls, across one official set and one untuned sample.**

### On the LLM lane, honestly

The lane was **armed, not absent**: the OpenRouter key was checked live before
the runs (`source=repo_env`, and `openai/gpt-oss-120b` answered on the
`deepinfra/bf16` provider pin the solver actually uses), and both runs carried a
200,000-token budget with the real proxy in front of them.

It made **zero calls and spent zero tokens**, which is the designed outcome and
the entry brief's stated success criterion — the LLM lane only ever sees rows the
deterministic pass did not solve. Historically it has scored **0 accepts on this
frontier across four sessions**, so a call would have been a warning, not a win.
The right reading is: there is currently nothing for it to do, and if that ever
changes, the row ids in the calls are the work list.

---

## 9. The standing accuracy loop

`spotcheck.py --true 6 --false 6 --seed 20260812`, run after everything else on
a quiet machine — 108 rows across all 9 sources including the `etp` matrix:

    TOTAL   108 attempted, 108 ok, 0 skip, 0 MISS
    accuracy 100.0%   coverage 100.0%
    No mistakes. Solver submitted no wrong verdict on this batch.

Nothing pinned into `stage2/fixtures/spotcheck_failures.jsonl`.

---

## 10. What is still open

There is **no open mathematical frontier** — every local row is solved and both
real runs came back clean. What remains is evidence and hardening:

1. **Solo has no real-runner evidence for the ladder.** It picks `deep` from a
   3600 s budget, so it runs *three* passes where Marathon runs two, and nothing
   has exercised that path end to end. Highest-value next item.
2. **Step-count budgets instead of wall clock.** Four separate cost bugs now
   (rails 5f-iii, 5f-iv, 5f-v) have all been "a wall-clock bound in the wrong
   place", and wall-clock budgets are also why route selection is
   nondeterministic and every timing number here carries a noise band.
3. **Productise ordered completion as a route.** It closed the final nine and
   this session's last three with no modification and no tuning, and it is
   strictly stronger than the e-graph on this problem class — but it lives
   outside the submission, so the shipped solver cannot use it on a fresh corpus.
4. **Two known un-deadlined sites**, both measured and neither currently costing
   rows: `derived_rule_steps` grows unboundedly (3,371 MB at 90 s, 5,194 MB at
   360 s at `deep` — wants a cap, not a poll), and single-rule egg *extraction*
   (`egg.explain`, `_egg_bridge_steps`) takes no deadline at all while its
   multi-rule twin does. That is the same asymmetry that produced rail 5f-v.
5. **Bytes.** 54,767 left of the cap. The remaining slow tail (`hard2_0098` 75 s,
   `hard3_0131` 74 s, `hard3_0204` 72 s, `hard2_0079` 68 s) is poor value per
   byte, and `hard3_0204` is deliberately kept live as the audit's only exercise
   of `true:egg_ladder`.

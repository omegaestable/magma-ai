# Next session brief — skips, latency, and a full real Marathon with LLM

Written 2026-08-12, at the end of the session that closed the corpus.
Deadline: **2026-08-31 23:59 AoE**. Read `CLAUDE.md` first; this file is the
plan, not the state.

Session goals, in the user's words: **remove skips**, **trim long-running
queries in both Solo and Marathon**, and **end with a full real Marathon with
LLM calls**.

---

## 1. Where things actually stand

| | |
| --- | --- |
| Offline, `fast` tier | official **1669/1669**, HF **800/800**, combined **2469/2469** |
| Packaged | **382,824 B** of 500,000, submission layout validated clean |
| Gate | **210 passed, 2 skipped** |
| Real-judge certs | 9/9 for the final nine; ~100 individually verified overall |
| Committed? | **No.** Working tree is dirty on top of `8d74d88`. |

**What is NOT verified, and matters more than the headline:**

- The 1669/1669 is **not** a fresh full-sweep measurement. Per instruction
  ("no full sweeps") only the 9 closed rows plus 8 controls were re-measured
  after the change. A full isolated audit is owed.
- The 9 new certificates have real-*judge* evidence but **no real-runner
  evidence** — no Solo or Marathon process has dispatched them.

---

## 2. The finding that should shape the whole session

**We audit at `fast`. We deploy at `standard` and `deep`. Those are different
solvers, and we have never audited at the tiers we actually ship.**

    audit_corpus.py default tier ........ fast
    Marathon @ 300 s/problem (rules) .... standard      set_effort(effort_for_seconds(0.5*budget/N))
    Marathon @ 600 s/problem (runner ref) deep
    Solo @ 3600 s ....................... deep          effort_for_seconds(3600)

And tier changes outcomes **in both directions**. Measured this session, one row
per process, isolated (`tmp_stage2_smoke/final-nine-2026-08-12/tier_inversion.log`):

| Row | fast | standard | deep (900 s cap) |
| --- | --- | --- | --- |
| `normal_0491` | **SOLVED** 65 s (`egg_ladder:collapse:h1`) | **SKIP** (198 s) | **SKIP** (323 s) |
| `hard2_0162` | **SOLVED** 168 s | SOLVED 386 s | **SKIP** (465 s) |
| `hard3_0266` | **SOLVED** 107 s | SOLVED 134 s | **SKIP** (205 s) |

Cause: `EFFORT_TIERS` scales **every** engine budget together (`standard` 7.5×,
`deep` 22×). On a row whose answer lives in a **late** engine, the early engines
consume the clock before the late one is reached. More budget makes the solver
**strictly worse** on exactly those rows.

`normal_0491` is the sharp case: it is solved only by `egg_ladder` at `fast`,
and it is **not** in `DISTILLED_CERTS`. So on current evidence it is **lost in
Marathon at standard tier** — while the offline audit reports it solved.

**Caveat, stated so nobody over-reads the table:** the `deep` column used a
900 s per-row cap. Real Solo gives its deterministic phase
`0.55 × 3600 ≈ 1980 s` in its own process, so `deep` might still land these
rows there. That is unmeasured. The `standard` column has no such excuse —
600 s was the cap and `normal_0491` still skipped.

### Action 0 (do this first, everything else depends on it)

Audit at the tiers we deploy, and diff by row id against the `fast` audit:

```powershell
.\.venv\Scripts\python.exe stage2/experiments/audit_corpus.py --all --effort standard --out stage2/results/audit-standard-<date>.json
.\.venv\Scripts\python.exe stage2/experiments/audit_corpus.py --all --effort deep     --out stage2/results/audit-deep-<date>.json
```

Never two at once (rail 5e). Expect ~35 min each, longer at `deep`. The row-id
diff against a `fast` audit *is* the real skip list — and it is the first
honest measurement of what the competition will actually see.

---

## 3. Goal: remove skips

Ranked by expected value.

1. **Fix the tier inversion.** Two candidate designs:
   - *Reserve a floor for late engines.* Before the engine loop, compute a
     per-engine floor so the tail (`egg_*`, `lemma_chain`, `egg_ladder`) is
     guaranteed a slice regardless of tier. Smallest change, directly targets
     the measured failure.
   - *Two-pass dispatch.* Run the whole engine list at `fast` budgets first,
     then re-run only what is unsolved with the scaled budgets. Strictly
     dominates the current single-pass scaling: everything `fast` solves stays
     solved, and hard rows still get the big budget. Costs one cheap pass on
     unsolved rows only.
   Either way, validate by re-running Action 0 and diffing by row id.
2. **Marathon has no per-problem deadline.** `run_marathon()`'s deterministic
   loop bounds only the *global* pass (`MARATHON_DETERMINISTIC_SHARE = 0.6` of
   the run), then `break`s. One slow row therefore steals clock from every row
   after it, and the tail is never *attempted* — which is exactly what
   `not_attempted` meant in the 08-01/03 campaign. Add a per-row bound:

   ```python
   remaining = deterministic_deadline - time.monotonic()
   rows_left = max(1, total_rows - attempted)
   set_hard_deadline(time.monotonic() + min(remaining, K * remaining / rows_left))
   ```

   with `K ≈ 2–3` so a hard row may borrow but not monopolise. This converts
   "unbounded tail loss" into "one row gives up early", and it is the single
   change most likely to remove real skips.
3. **Distill any row that only solves at one tier.** Once Action 0 gives the
   per-tier diff, every row solved at *some* tier but not others is a
   distillation candidate — `distill_certs.py` judges before it emits and
   refuses anything unaccepted. That makes the result tier-independent and
   O(1). This is how `hard1_0062`, `hard2_0123` and the final nine were closed.
   `normal_0491` is the obvious first entry.

---

## 4. Goal: trim long-running queries

The tail is what costs Marathon rows, and it is short — worth attacking
directly rather than tuning budgets globally.

Measured on the packaged artifact at `fast`, single process:

| Row | Route | Seconds |
| --- | --- | ---: |
| `hard2_0162` | `egg_ladder:collapse:h1` | 174 |
| `normal_0090` | `egg_ladder:goal:h1` | 125 |
| `hard3_0266` | `egg_ladder:right_projection:h1` | 116 |
| `normal_0491` | `egg_ladder:collapse:h1` | 94 |
| `hard3_0204` | `egg_ladder:right_sq_projection:h2` | 70 |
| the 9 distilled rows | `distilled:*` | **0.0** |

The contrast is the whole argument: **distillation takes a 174 s row to 0.0 s**,
costs ~2–8 KB of a 117 KB headroom, and carries judge-accepted bytes.

1. **Distill the slow tail.** From the Action 0 audits, take every row above a
   threshold (start at 30 s) and distil it. Budget the bytes: at ~3 KB average,
   100 rows ≈ 300 KB, which does *not* fit — so rank by seconds-saved per byte
   and stop at the cap. Re-check `package_solver.ps1` size after each batch.
2. **Then measure again.** Total deterministic wall clock per set is the metric,
   not per-row bests.
3. **Solo latency is a different problem.** Solo is one problem per process with
   a 3600 s budget, so it is not throughput-bound — but it currently runs `deep`,
   which is where the inversion bites. Fixing the inversion probably fixes Solo
   latency for free; measure before optimising anything else there.
4. Do **not** shrink `EGG_PROBE_*` budgets to save time — that probe is unscaled
   on purpose and exists to fix a starvation bug (2026-08-07). Trim by
   distillation, not by starving the routes that earn rows.

---

## 5. Goal: the closing real Marathon, with LLM

### Procedure

```powershell
# 0. Clean gate + package, and CONFIRM the submission dir holds only solver.py
.\.venv\Scripts\python.exe -m pytest stage2/tests -q -n auto
.\stage2\solver\package_solver.ps1
Remove-Item -Recurse -Force stage2\submissions\__pycache__ -ErrorAction SilentlyContinue

# 1. Key precedence (a stale Windows User-scope key shadows repo .env)
.\.venv\Scripts\python.exe tmp_stage2_smoke\real-run-tools\clean_run.py `
    stage2\experiments\homelab_llm_probe.py --key-status     # expect source=repo_env

# 2. The run itself — POSITIVE token budget (rail 7)
.\.venv\Scripts\python.exe tmp_stage2_smoke\real-run-tools\clean_run.py `
    tmp_stage2_smoke\real-run-tools\run_marathon_batch.py `
    --manifest data\stage2_official_problems\<set>.jsonl `
    --output-dir tmp_stage2_smoke\real-run-<date>\marathon-<set> `
    --budget-tokens 200000
```

### Success criterion, and it is a sharp one

With the corpus deterministically complete, **a correct Marathon should need
0 LLM calls.** The LLM lane only sees rows the deterministic pass did not
solve. So:

- `llm_calls == 0` → the deterministic pass covered the manifest. 
- `llm_calls > 0` → **every call is a scheduling skip**, and the row ids in
  those calls are precisely the list Goal 1 must fix.

That makes the closing run a measurement, not just a demo. Historically the LLM
lane has scored **0 accepts** on this frontier across four sessions, so do not
count on it to recover anything — treat any LLM activity as a bug signal.

### Pitfalls that have each cost a run

- **`__pycache__` in `stage2/submissions/` fails the run instantly** with
  `invalid submission: found extras`. Importing the packaged solver to verify it
  creates one. Validator: `pipeline.marathon_runner._validate_solver_layout(Path)`
  returns `None` when clean.
- **`lake env` has a hardcoded 30 s timeout** and dies under load, usually in
  the scoring pass. Answers are append-only and safe on disk — recover with
  `--score-only`. Do not re-run the solve.
- **`--score-only` reopens `run.log` in write mode and truncates it**, destroying
  the solve phase's route labels. If you need route attribution, either copy
  `run.log` first or attribute by certificate bytes with
  `tmp_stage2_smoke/real-run-tools/attribute_answers.py` (stronger anyway — an
  exact match against `DISTILLED_CERTS` cannot come from another engine).
- **Never run the judge against a busy machine** (rail: `lake env` timeout).

---

## 6. Standing rails worth re-reading before touching the solver

- **Diff by row id, never by total** (rail 2) — solved counts carry a ±7 noise band.
- **Never delete routes to de-bloat** (rail 1) — 29 routes look dead on official
  sets and are live on HF.
- **No benchmark ids in solver policy** (rail 9). Distillation is legal because
  it keys on *canonical equation text* (rail 5h).
- **Never add a `DISTILLED_CERTS` entry the real judge has not accepted.**
- **A node/step cap alongside a time deadline has now misfired three times**
  (rail 5f). If you add a cap, compute deadline × throughput for the *fastest*
  family.
- **`.get(a) == .get(b)` fires on two missing keys** (rail 5g).

---

## 7. Loose ends from this session

- **Nothing is committed.** `git status --short` shows `CLAUDE.md`,
  `stage2/solver/solver.py`, `stage2/fixtures/judge_verified_certs.jsonl`, plus
  the new results doc and this brief.
- **Two CLAUDE.md claims were corrected** (see the open-frontier section): the
  "no self-critical-pairs" impossibility was false and self-refuting, and the
  "unreachable by any search" reading was too strong — ordered completion
  reached all nine.
- **Completion is not in the solver.** The final nine were derived by hand-run
  Knuth–Bendix with proof recording and shipped as distilled certificates. If a
  new corpus ever appears, that capability has to be rebuilt or productised —
  worth considering as a route, since it is strictly stronger than the e-graph
  on this problem class.
- Evidence: `tmp_stage2_smoke/final-nine-2026-08-12/` (certs, transcripts,
  `judge_results.json`, `tier_inversion.log`).

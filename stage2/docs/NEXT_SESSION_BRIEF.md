# Next session brief — Solo evidence, step budgets, and productising completion

Written 2026-08-12 at the end of session 2 (tier inversion / latency / real
Marathon). Deadline: **2026-08-31 23:59 AoE**. Read `CLAUDE.md` first; this file
is the plan, not the state.

---

## 1. Where things stand

| | |
| --- | --- |
| Offline, `fast` tier | official **1669/1669**, HF **800/800**, `sample_200` **200/200** — **2689/2689** |
| Row-id diff, three isolated audits this session | **0 lost, +3 gained**, 0 oracle failures, 0 crashes |
| Audit wall clock | official **980 s → 330 s**, HF **773 s → 344 s** |
| Gate | **252 passed, 2 skipped** |
| Judge-pinned certs | **99, all 99 re-checked by the gate** (was 69 checked / 31 skipped) |
| Packaged | **445,233 B** of 500,000 (54,767 left, 11.0%) |
| Closing real Marathon | `hard3.jsonl` **400/400**, fresh ETP sample **200/200** — **600/600 accepted, 0 rejected, 0 `not_attempted`, 0 LLM calls** |
| Spotcheck | 108 rows / 9 sources, **100% accuracy, 0 mistakes** |

**The previous brief's Action 0 is done and its headline finding is fixed** —
the tier inversion (rail 12), the missing Marathon per-row deadline (rail 13),
and, found while chasing them, the single-rule egg engine's misplaced deadline
poll (rail 5f-v).

---

## 2. What is actually left

Ranked by expected value. Note there is **no open mathematical frontier** — every
local row is solved — so this list is robustness, evidence and cost.

### 2.1 Real **Solo** evidence for the new dispatch (highest value)

Marathon has real-runner evidence from this session. Solo does not, and Solo is
where the ladder matters most: it picks `deep` from a 3600 s budget, so it runs
**three passes** where Marathon runs two. Nothing has exercised that path end to
end.

```powershell
.\.venv\Scripts\python.exe tmp_stage2_smoke\real-run-tools\clean_run.py `
    tmp_stage2_smoke\real-run-tools\run_solo_batch.py `
    --manifest data\stage2_official_problems\hard2.jsonl --limit 25
```

Watch for: per-row latency (the ladder should *reduce* it — a `fast` answer no
longer waits behind `deep`-scaled early engines), and any row where the fast and
standard passes both run to no purpose.

### 2.2 Step-count budgets instead of wall clock

Still the most valuable structural item, and this session added two more reasons.
Wall-clock budgets are why route selection is nondeterministic, why the golden
gate has to tolerate drift, and why every timing number in this repo carries a
noise band. Four separate cost bugs (rails 5f-iii, 5f-iv, 5f-v) have all been
"a wall-clock bound in the wrong place".

### 2.3 Productise ordered completion as a solver route

The completion pipeline in `tmp_stage2_smoke/final-nine-2026-08-12/` closed the
final nine **and** this session's last three with **no modification and no
tuning**, each in under 0.2 s. It is strictly stronger than the e-graph on this
problem class — it derives new rules by superposition and rewrites with them,
where an e-graph only propagates congruence over terms it already built.

Right now that capability lives outside the submission. If a fresh corpus
appears, the solver cannot use it. Porting it in is the single biggest coverage
insurance available, and 54,767 bytes of headroom is probably enough for a
compact implementation.

### 2.4 Two known un-deadlined sites (measured, not yet fixed)

Both found by the overshoot probe; neither is currently costing rows, so they are
hardening, not bugs to panic about:

- **`derived_rule_steps` grows unboundedly.** `seen`/`steps` have no cap and
  `steps.sort()` at the end is not deadline-checked. Measured at `deep` on
  `hard2_0162`: polls fine (max inter-poll gap 0.28 s) but reaches **3,371 MB at
  90 s and 5,194 MB at 360 s**. Wants a cap, not a poll. The armed memory guard
  does see this one.
- **Single-rule egg extraction has no deadline at all**, unlike its multi-rule
  twin: `egg.explain` takes no `deadline` parameter while `explain_multi` does
  and polls it; `_egg_bridge_steps` (O(n²)) takes none while
  `_egg_bridge_steps_multi` does. Same asymmetry that produced rail 5f-v.
  Measured small today (0.02 s / 1.4 s on `hard2_0162`), but that is luck.

### 2.5 More distillation, if bytes are wanted elsewhere

The remaining slow tail after this session, all `fast` tier, isolated:

| Row | Seconds | Cert bytes |
| --- | ---: | ---: |
| `hard2_0098` | 75.2 | 8,544 |
| `hard3_0131` | 73.9 | 13,783 |
| `hard3_0204` | 72.3 | 2,644 |
| `hard2_0079` | 67.8 | 8,544 |
| `hard3_0106` | 56.3 | 14,641 |

`hard3_0204` is the best remaining trade and is **deliberately kept live** as the
audit's only exercise of `true:egg_ladder` — distil it only if something else
covers that engine. The rest are poor value per byte; do not spend the headroom
on them without a reason.

---

## 3. Standing hygiene

- **Run `spotcheck.py` every session** and fix whatever it pins. It draws from
  the ~22M-pair ETP matrix, which is the only source the solver was never tuned
  against.
- **Diff by row id, never by total** (rail 2).
- **Never run two `audit_corpus.py` sweeps at once** (rail 5e) — and check what
  else is on the machine first. Part of this session's timing ran against heavy
  unrelated CPU load from another project on the same box; the coverage numbers
  are unaffected (0 mismatches does not come and go with load) but the wall-clock
  figures are lower bounds on the improvement, not precise measurements.
- **Never add a `DISTILLED_CERTS` entry the real judge has not accepted**, and
  remember `test_judge_verified.py` now compares bytes for distilled routes
  rather than skipping — that is what caught a stripped trailing newline here.
- **`lake env` has a hardcoded 30 s timeout** and dies under load, usually in the
  scoring pass. Answers are append-only and safe; recover with `--score-only`,
  which **truncates `run.log`** — copy it first, or attribute by certificate
  bytes with `tmp_stage2_smoke/real-run-tools/attribute_answers.py`.
- **`__pycache__` in `stage2/submissions/` fails a run instantly.**

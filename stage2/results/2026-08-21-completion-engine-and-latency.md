# 2026-08-21: ordered completion ships as a solver route

Acting on the 2026-08-20 measurement session, which drew a 20,000-row random
sample of the full order-4 ETP matrix and a 4,000-row generated order-5 sample
and deliberately changed nothing. Both logs named the same top lever, and this
session shipped it.

Two goals, both met and both measured: **close the order-4 failure frontier**,
and **make the solver faster** so Marathon's per-row budget goes further.

## Headline

| | Before (2026-08-12/13) | After |
| --- | --- | --- |
| Official sets, `fast` | 1669 / 1669 | **1669 / 1669** (0 lost, 0 gained by row id) |
| HF mirrors | 800 / 800 | **800 / 800** |
| `sample_200` / `sample_20` | 200 / 200, 20 / 20 | **200 / 200, 20 / 20** |
| Crashes / oracle failures | 0 / 0 | **0 / 0** over 2,689 audited rows |
| Official wall clock (16 workers) | 330.1 s | **249.9 s (−24%)** |
| HF wall clock | 344 s | **163.9 s (−52%)** |
| 20k-ETP-sample frontier (51 TRUE rows) | 0 / 51 | **43 / 51, 0.3 s for all of them** |
| Order-5 frontier (25-row probe) | 0 / 25 | **9 / 25** |
| Offline gate | 252 passed | **257 passed, 2 skipped** |
| Spotcheck | 108 rows, 0 mistakes | **216 rows / 9 sources, 0 mistakes** |
| Packaged artifact | 445,640 B | **466,320 B** of 500,000 (33,680 free, 6.7%) |

## What shipped: `true:completion`

Ordered (unfailing) Knuth-Bendix completion with proof recording, ported into
`solver.py` from `stage2/experiments/completion` — the dev tool that closed the
final nine official/HF rows and the last three `sample_200` holdouts in the
2026-08-12 session, by hand, one row at a time. `CLAUDE.md` has carried a **GO**
verdict on porting it since 2026-08-13. It is strictly stronger than the e-graph
on this problem class because it derives new rules by superposition and then
rewrites with them, where an e-graph only propagates congruence over terms it has
already built.

Two dispatch slots, mirroring the `egg_probe` / `egg_closure` pattern:

- `completion_probe_route` — **unscaled 2 s**, immediately after `egg_probe_route`.
- `completion_route` — tier-scaled 8 s, after the whole egg family.

The early slot pays rather than costs because completion's *loss* is cheap: it
saturates (empty passive queue) in ~0 s on most rows rather than spending its
budget, unlike every search engine below it.

### Three things the port has that the dev tool did not

Each is a coverage difference, not a tidy-up. Measured on the 51 TRUE rows of the
20k-sample frontier:

1. **A derived collapse is used, not discarded.** The dev tool's README flagged
   `x = y` being thrown away unoriented as its own top next lever. The real shape
   is wider: any derived `t = v` with `v` not occurring in `t` says every element
   of the carrier equals that one instance of `t`, so the magma is trivial and any
   goal follows. `x = y` alone closes **19** rows; the general shape is what **12
   more** were sitting on (`z ◇ y' = y`, `y' ◇ x = y`, …). Both are the same fact
   — only the second is invisible if you look for the literal two-variable
   equation.
2. **The goal is skolemised before joining.** KBO cannot orient two distinct
   variables, so leaving the goal's variables *as* variables silently blocks every
   unorientable equation from ever rewriting it. Worth **3** rows, and a
   correctness fix regardless: ordered rewriting is total on ground terms, which
   is the entire point of unfailing completion, and the goal's variables are
   exactly Lean's `intro`d locals — already constants. It costs nothing to
   implement: a `ground=True` flag on the ordering.
3. **The deadline is polled per unit of work** (rails 5f-iv, 5f-v) and the caches
   are the repo's own per-row ones (rail 10). The dev tool polls once per outer
   iteration, which is the exact shape that ran 40 s on a 6 s budget at 11 GB RSS
   in the egg engine.

### Evidence

- **Frontier**: 43 of 51 (32 collapse, 11 join), **every certificate
  proof-kernel-verified**, **0.3 s of solver time for all 43** — against ~450 s of
  deterministic search *per row* and a real `gpt-oss-120b` lemma-lane pass that
  both scored 0/51 in the 2026-08-20 session.
- **Real Lean judge: 12 / 12 accepted** (rail 3c), a deliberate spread over both
  certificate shapes, 624–2,559 bytes, ~3 s per judge call. Includes the two
  official rows the probe now wins ahead of `projection_bootstrap`
  (`evaluation_normal_0082`, `evaluation_hard_0180`).
- **Corpus**: the route serves **304 rows** across official + HF (166 `join`, 138
  `collapse`) with 0 oracle failures.
- **Order-5**: 9 of a 25-row probe of the 2026-08-20 order-5 frontier now solve.
  `order5_23416_48258` — the row that ran **3,538 s against a 300 s budget** —
  now answers in **4.9 s**.

## Latency: where the 24% came from

| Set | Was | Now | |
| --- | ---: | ---: | ---: |
| `normal` | 106.4 s | 98.1 s | −8% |
| `hard1` | 28.7 s | 21.2 s | −26% |
| `hard2` | 95.6 s | 65.7 s | −31% |
| `hard3` | 99.4 s | 64.9 s | −35% |
| **official total** | **330.1 s** | **249.9 s** | **−24%** |
| `sample_200` | 71.5 s | 22.3 s | −69% |
| `hf_evaluation_order5` | 162.9 s | 73.4 s | −55% |
| **HF total** | **344 s** | **163.9 s** | **−52%** |

Two causes, and they are not the same one:

- **Completion preempts slower engines.** 304 rows now answer in milliseconds
  that previously waited on tier-scaled closure or egg engines. This is most of
  the official-set gain.
- **The single-rule egg extraction had no deadline at all.** `_egg_bridge_steps`
  is O(states²) with each test trying the rule both ways, and it had **neither a
  deadline nor a state cap** — while its multi-rule twin `_egg_bridge_steps_multi`
  has had both since it was written, with a comment spelling out exactly why
  ("a 1500-step chain is ~22M pattern matches — minutes, silently, inside what was
  meant to be a 2 s attempt"). `explain` likewise took no `deadline` while
  `explain_multi` did. Both now match their twins
  (`EGG_BRIDGE_MAX_STATES = 400`, the twin's number). This is the **fifth**
  instance of rail 5f-v: fix a bug in one engine, fix its twin the same day.

  It stayed invisible while every corpus was order-4. The 2026-08-20 order-5
  sample is the first thing that fed it long chains over big terms, and 9 of its
  205 skip rows overran a 300 s row budget, one of them by 11.8x.

  The cap costs nothing measurable: the audit diff is 0 lost rows.

## Two dead ends, measured, so nobody re-runs them

- **Instantiating the *other* unorientable shape.** An equation like
  `z ◇ x = w ◇ x` ("the left argument does not matter") also gets no orientation
  and is also discarded. Pushing its variable-for-variable instances is sound and
  the recorded chains survive substitution — and it closes **0** of the 8 rows the
  collapse fix leaves. `subsumed()` throws every instance away precisely *because*
  each is an instance of the parent equation, which is still active. Making it
  work means weakening subsumption, which is what keeps the search small. Recorded
  in `_kb_collapse_witness`'s docstring, where the next reader will look.
- **A cap on `derived_rule_steps`.** `NEXT_SESSION_BRIEF.md` §2.4 lists it as
  growing unboundedly to 5,194 MB at 360 s and says it "wants a cap, not a poll".
  Measured across 2,737 calls over 72 rows at both `fast` and `deep`: the **maximum
  steps any single call returns is 619**. A cap there cannot bind without becoming
  a second binding constraint (rail 5f), so none was added. The memory is in the
  *caller* — `derived_cp_closure_proof_expr`'s `left_seen`/`right_seen` hold
  `chain_trans`-concatenated proof strings, `frontier_limit` of them — which the
  armed memory guard does see. Same lesson as rail 5f-vi: the named function was
  not the growing one.

## Verification

| Check | Result |
| --- | --- |
| Offline gate | **257 passed, 2 skipped** (`-n auto`) |
| Full audit, official | 1669/1669 + `sample_200` 200/200 + `sample_20` 20/20, 0 crashes, 0 oracle failures |
| Full audit, HF | 800/800, 0 crashes, 0 oracle failures |
| Row-id diff vs `audit-2026-08-12-final.json` (+ HF) | **0 lost, 0 gained, 0 verdict flips** over 2,669 common rows |
| Real Lean judge, new builder | **12/12 accepted** |
| Spotcheck (seed `20260821`) | **216 rows / 9 sources, 100% accuracy, 100% coverage, 0 mistakes** |
| Packaging | 466,320 / 500,000 bytes, gate green |

`true:completion` was added to `GENERAL_CLOSURE_FAMILIES` in `test_golden.py` —
it is a general search engine like the closures and the egg family, so a row
drifting onto it from another general engine is the documented wall-clock
nondeterminism, not a regression. Two golden rows
(`evaluation_normal_0082`, `evaluation_hard_0180`) genuinely moved
`projection_bootstrap` → `completion`; both are still solved, still TRUE, still
oracle-checked, and both are now judge-accepted through the new route.

## Real-runner evidence, and a harness bug it exposed

Both runs used the packaged artifact, the real OpenRouter key, and a positive
token budget (rail 7). Neither needed a single LLM call — the deterministic
engines cleared everything.

| Run | Result | Wall | Tokens |
| --- | --- | ---: | ---: |
| Marathon `hard3.jsonl` (400 rows) | **400 / 400 accepted, 0 rejected, 0 `not_attempted`** | **612 s** (was 1,152 s on 2026-08-12, **−47%**) | 0 of 200,000 |
| Marathon, fresh unseen ETP (200 rows, seed `20260821`, 0 overlap with any prior sample) | **200 / 200 accepted, 0 rejected, 0 `not_attempted`** | 510 s | 0 of 200,000 |

The ETP run first scored **199/200**, and the one failure was **our harness, not
the solver** — rail 3b, fourth instance:

`etp_1555_205` came back `malformed`, "code must have UTF-8 length <= 50000
bytes", on an 88,539-byte certificate. 50,000 is `judge/verify.py`'s **fallback**,
used when `MAX_CODE_LENGTH` is absent from the environment; the deployed pipeline
passes `config.json`'s **100,000**. Settled the same way the caps were settled on
2026-08-13 — the identical certificate, judged twice, nothing varying but the cap:

| Certificate | `MAX_CODE_LENGTH=50000` | `MAX_CODE_LENGTH=100000` |
| ---: | --- | --- |
| 88,539 bytes | `malformed` / `CODE_TOO_LONG` | **`accepted`** |

`judge_rows.py` was fixed to set the production values on 2026-08-13.
`run_marathon_batch.py` and `run_solo_batch.py` were **not**, so every local
Marathon since has been scored against a phantom cap — invisible until a
certificate finally exceeded 50,000 bytes in a real run.

The fix went into **`stage2/experiments/local_runner_env.py`**, not into the
runners: `judge_cap_env()` reads `LEAN_TIMEOUT_SECONDS` / `MAX_CODE_LENGTH` /
`MAX_FALSE_CERT_BYTES` straight out of `pipeline/config.json` and
`load_local_runner_env()` fills them in, so every current and future runner gets
them and no copy of the numbers exists to drift. That placement is deliberate —
`tmp_stage2_smoke/real-run-tools/` is under `.gitignore`'s `tmp*/`, and a fix
living only there is exactly how the completion pipeline once ended up tracked in
0 files. The runners keep a one-line assert so a restored copy fails loudly
instead of silently re-inventing the bug. Re-scored with `--score-only`: **200/200 accepted, 0
non-accepted of any kind.** The pre-fix summary is kept beside it as
`summary.fallback-cap.json`, and `run.log.solve-and-first-score.bak` is the
original log (`--score-only` truncates `run.log`).

Session real-runner total: **600 / 600 judge-accepted rows, 0 rejected, 0
`not_attempted`, 0 LLM calls** — both runs carrying a positive 200,000-token
budget.

The generalisable lesson is not "check the judge limits" — that was 3b and
3b-iii. It is: **when you fix one harness to match deployment, grep for every
other caller of the same library the same day.** That is rail 5f-v's shape in a
different subsystem. Worth naming the near miss: this looked exactly like a
solver regression, and reporting it as 199/200 would have been wrong in the
pessimistic direction.

## Timing caveat

An unrelated process from another project (`fetch_verify.py`, ~20% of one core)
was resident throughout. On a 16-worker sweep that is ~1% of the box and the
speedup figures above are not sensitive to it, but the **baseline** numbers this
is compared against carry `CLAUDE.md`'s much larger 2026-08-12 load caveat, so
treat the percentages as good-faith comparisons rather than lab measurements. The
coverage numbers are unaffected — 0 mismatches over thousands of rows does not
come and go with load.

## Artifacts

- `stage2/solver/solver.py` — the `true:completion` engine, and the egg
  extraction deadline/cap
- `stage2/tests/test_golden.py` — `true:completion` registered as a general family
- `stage2/results/audit-2026-08-21-completion.json` — official audit
- `stage2/results/audit-2026-08-21-completion-hf.json` — HF audit
- `stage2/results/etp-marathon-200-2026-08-21.jsonl` — fresh unseen ETP manifest
  (seed `20260821`, benchmark ids excluded, 0 overlap with the 20k sample frontier)

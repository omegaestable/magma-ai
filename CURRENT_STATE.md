# Current State

Short operational snapshot for the Stage 2 lab. **`CLAUDE.md` is authoritative** —
headline numbers, the four commands and the rails live there, and if this file
disagrees with it, this file is the one that is wrong. What lives here instead:
the operational detail that does not belong in the entry point (effort tiers,
deployed budgets, artifact inventory) and a dated index into `stage2/results/`,
which is the evidence.

Last updated: **2026-08-21** — ordered Knuth-Bendix completion shipped as the
`true:completion` solver route. Coverage held (0 lost / 0 gained by row id) and
the corpus audit got 24% faster; the first frontier *outside* the local corpus,
found by the 2026-08-20 20,000-row ETP sample, went from 0/51 to 43/51.

---

## Status at a glance

| | |
| --- | --- |
| Official sets, `fast` tier | **1669 / 1669** (TRUE 819/819, FALSE 850/850) |
| HF mirror sets | **800 / 800** |
| `sample_200` (ETP sample, disjoint from `normal`) | **200 / 200** |
| Distinct local rows | **2669 / 2669** — see the double-count note |
| Oracle failures / crashes / label mismatches | 0 / 0 / 0 |
| Open mathematical frontier | **none locally**; outside the corpus, the 20,000-row ETP sample's 52-row frontier is down to **8 order-4 TRUE rows + 1 FALSE row** |
| Audit wall clock | official **250 s** (was 330 s), HF **164 s** (was 344 s) |
| Packaged artifact | **466,320 of 500,000 bytes** (33,680 free, 6.7%), built 2026-08-21 |

Measured by a `fast`-tier audit on 2026-08-21 —
`stage2/results/audit-2026-08-21-completion.json` and
`...-completion-hf.json` — diffed by row id against the 2026-08-12 baseline
(`audit-2026-08-12-final.json` + `audit-2026-08-12-postfix-fast-hf.json`):
**0 lost, 0 gained, 0 verdict flips** over 2,669 common rows. Narrative:
`stage2/results/2026-08-21-completion-engine-and-latency.md`.

**Do not add those three lines together.** 1669 + 800 + 200 = **2669 distinct
rows**. The "2689" that circulated was that sum plus `sample_20`, whose 20 rows
are a strict subset of `normal` and so are already counted in the official 1669.
The HF mirrors do *not* overlap the official sets (intersection 0, by id and by
canonical content). Quote the three numbers separately.

Per-set, from `audit-2026-08-21-completion.json` (`fast`, 16 workers; `seconds`
is that set's wall clock, and the four official sets sum to the 250 s headline).
The 2026-08-12 figure is in the last column for comparison — read it as a
good-faith comparison, not a lab measurement, since that run carried its own
load caveat:

| Set | Solved | TRUE | FALSE | Skip | Crash | Oracle fail | Seconds | (was) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `normal` | 1000/1000 | 500 | 500 | 0 | 0 | 0 | 98.1 | 106.4 |
| `hard1` | 69/69 | 24 | 45 | 0 | 0 | 0 | 21.2 | 28.7 |
| `hard2` | 200/200 | 100 | 100 | 0 | 0 | 0 | 65.7 | 95.6 |
| `hard3` | 400/400 | 195 | 205 | 0 | 0 | 0 | 64.9 | 99.4 |
| **official** | **1669/1669** | **819** | **850** | **0** | **0** | **0** | **249.9** | **330.1** |
| `sample_200` | 200/200 | 100 | 100 | 0 | 0 | 0 | 22.3 | 71.5 |
| `sample_20` | 20/20 | 10 | 10 | 0 | 0 | 0 | 26.3 | 30.8 |

HF, same run: `hf_evaluation_normal` 39.8 s, `hf_evaluation_hard` 25.6 s,
`hf_evaluation_extra_hard` 25.1 s, `hf_evaluation_order5` **73.4 s** (was 162.9),
200/200 each — **163.9 s total, was 344 s**.

`true:completion` serves **304** of these rows (166 `join`, 138 `collapse`).

HF mirrors are 200/200 on each of `hf_evaluation_normal`, `hf_evaluation_hard`,
`hf_evaluation_extra_hard`, `hf_evaluation_order5` — 800/800, 0 oracle failures.
Wall clocks for that run carry the load caveat in `CLAUDE.md`; treat them as
lower bounds on the speedup, not measurements.

> The 2026-08-13 note that once stood here — "an audit is running and its result
> is not included, so coverage is a prediction" — is **discharged**. Two full
> audits have landed since (2026-08-13 limits, 2026-08-21 completion) and both
> read row-for-row identical to the 2026-08-12 baseline.

### Evidence base, in one paragraph

The audit numbers are **offline** evidence (independent proof kernel +
finite-model oracles) and therefore an upper bound on judge acceptance. Against
that: **99 certificates byte-pinned in `stage2/fixtures/judge_verified_certs.jsonl`
and all 99 re-checked by the gate**; real-runner Marathon on `hard3.jsonl`
**400/400 accepted, 0 rejected, 0 `not_attempted`, 0 LLM calls** and on 200
fresh ETP rows (seed `20260812`, benchmark ids excluded) **200/200**, for
**600/600 real-judge rows with 0 rejections** on 2026-08-12. The 2026-08-01/03
campaign adds 2863/2894 real-judge rows, 0 rejected. **Solo still has no
real-runner evidence for the tier ladder** — it runs `deep`, so three passes,
and nothing has exercised that end to end.

---

## What changed on 2026-08-13

### The judge limits were wrong, in the solver and in the docs

`vendor/stage2-official/pipeline/config.json` is what
`vendor/stage2-official/pipeline/proxy.py` (lines 1004-1012) passes into the
judge, and it says:

    lean_timeout_seconds  300        max_code_length       100000
    max_false_cert_bytes  20000      max_solver_bytes      500000
    solver.timeout_seconds 3600      llm.max_output_tokens  65536

The `50_000` / `10_000` / `120` in `vendor/stage2-official/judge/verify.py` are
only the **fallback** used when the verifier is invoked directly with no config.
On 2026-07-29 the solver's caps were halved to match that fallback, on evidence
from a 2026-07-23 measurement taken through `judge_rows.py` — which called
`verify_answer()` with no config, and so measured the fallback against itself.

Settled by experiment on 2026-08-13, one certificate judged twice with only the
configured cap varying:

| Certificate bytes | 50,000 cap | 100,000 cap |
| ---: | --- | --- |
| 48,003 | accepted | accepted |
| 60,015 | `malformed` / `CODE_TOO_LONG` | **accepted** |
| 90,023 | `malformed` / `CODE_TOO_LONG` | **accepted** |

This is the **third** instance of the rail-3b error class: a hard limit inferred
from one insufficient experiment. See also the retired order-10 witness ceiling
and the `maxRecDepth` trigger.

### Constants realigned (all with the offline gate green)

| Constant | Was | Now |
| --- | ---: | ---: |
| `JUDGE_MAX_CODE_LENGTH` (`MAX_LEAN_CODE_BYTES`) | 50,000 (49,500) | **100,000 (99,500)** |
| `JUDGE_MAX_FALSE_CERT_BYTES` (`MAX_FALSE_CERT_BYTES`) | 10,000 (9,500) | **20,000 (19,500)** |
| `EGG_MAX_PROOF_BYTES` | 46,000 | **96,000** |
| `MAX_WITNESS_DECIDE_APPLICATIONS` | 20,000 | **50,000** (recalibrated to the real 300 s Lean timeout) |
| `LLM_HTTP_TIMEOUT_SECONDS` | 75.0 | **300.0** |
| `SOLO_FALLBACK_RESERVE_SECONDS` | 90.0 | **310.0** (one 300 s judge call + margin) |
| `SOLO_LLM_ROUND_MIN_SECONDS` | 150.0 | **620.0** (one LLM call + one judge call + margin) |

The 75 s HTTP timeout **aborted 225 of 446 logged real LLM calls**, and an abort
still spends the tokens while losing the row. `LLM_CONFIG["model"]` now honours
the organizers' `JUDGE_MARATHON_MODEL` env var instead of hardcoding
`openai/gpt-oss-120b`, which had made a documented knob unreachable (the
published spec also lists `google/gemma-4-31b-it`).
`constraint_countermodel_wide_domain` now skips an order whose `decide` cost the
gate will veto **before** searching it — it was burning up to 1,760 s/row at
`deep` on work guaranteed to be discarded.

### Tooling and CI

- `stage2/tests/oracles.py` — the same two cap constants corrected, so the
  offline gate no longer polices a limit the judge does not impose.
- `stage2/experiments/judge_rows.py` — now sets `LEAN_TIMEOUT_SECONDS` /
  `MAX_CODE_LENGTH` / `MAX_FALSE_CERT_BYTES` to the production values, so local
  judging matches deployment instead of the fallback.
- `stage2/solver/minify_submission.py` — line transforms are now **string-aware**.
  They were rewriting the *contents* of multi-line string literals (collapsing
  blank runs, stripping trailing whitespace), which hard-fails the parse-tree
  check. `DISTILLED_CERTS` stores every certificate as triple-quoted Lean, so one
  cert with a trailing space would have bricked the packager. `check()` now names
  the first differing top-level statement.
- `stage2/solver/package_solver.ps1` — builds to a temp file and swaps in only
  after the size check passes. It used to wipe `stage2/submissions/` *before*
  running the minifier (a failure left no artifact at all, and none in git either
  since it is gitignored) and left an oversized artifact in place while claiming
  to refuse to package.
- `ruff.toml` — `exclude` → `extend-exclude`. Plain `exclude` **replaces** ruff's
  defaults, so ruff walked into `.git/` and reported 443 invalid-syntax errors
  from a pasted error log saved as `.git/logs/errorsaug.py` (removed; backed up
  outside the repo).
- `.github/workflows/gate.yml` — rewritten; it was red on two steps.
  - Now **python 3.11**, matching the evaluation sandbox's `python:3.11-slim`.
    It was 3.12, so CI had never run the solver on the interpreter that grades it.
  - It now **builds** the submission and checks the 500,000-byte cap on the
    **artifact**. The old step asserted the cap against `stage2/solver/solver.py`
    — the *source*, 529,700 bytes at HEAD and legitimately over the cap because it
    carries comments and docstrings — so CI was red on every push while the real
    deliverable had ~11% headroom. The artifact is gitignored, so CI must build it
    to check it.
  - New step: asserts the solver's judge-limit constants still match
    `vendor/stage2-official/pipeline/config.json`, so this drift cannot recur
    silently.

---

## Effort tiers, and the ladder

`EFFORT_TIERS` + `set_effort()` scale time *and* search caps together (a budget
sweep showed both bind; widening one alone leaves rows unclaimed).

| Tier | CP time | frontier | fills | pool | depth |
| --- | ---: | ---: | ---: | ---: | ---: |
| `fast` | 8 s | 2600 | 1200 | 16 | 4 |
| `standard` | 60 s | 11959 | 3960 | 22 | 4 |
| `deep` | 176 s | 29900 | 7920 | 26 | 5 |

`effort_for_seconds()` picks the tier from the wall clock actually available per
problem: **≥ 240 s → `deep`, ≥ 45 s → `standard`, else `fast`**. `fast` is the
audit default.

**Since 2026-08-12, `solve_problem` walks the ladder rather than jumping to the
tier** (`effort_ladder_to`, `EFFORT_LADDER = ("fast", "standard", "deep")`;
`solve_problem_pass` is the single pass). Scaling every engine together meant
that on a row whose answer lives in a *late* engine the early engines ate the
whole per-row clock — **more budget made the solver strictly worse**. Measured:
at `deep` with a 360 s row budget, `normal_0491` and `hard2_0162` were SKIP and
solve in 97.6 s / 173.9 s after the fix; `sample_20` is 20/20 at `fast` in 32 s
but 15/20 at `deep` under a 45 s row bound. At `fast` the ladder is exactly one
pass, so the audit default is unchanged. Full rationale: `CLAUDE.md` rail 12.

**Measure at the tier you ship, with the bound deployment imposes.**
`audit_corpus.py --row-budget` exists because the audit sets no per-row deadline
while Solo and Marathon always do. Real Marathon at the default compression ratio
is `standard` with ~180 s per row on average (`--effort standard --row-budget 540`
models the borrow ceiling); real Solo is `deep` with 1980 s.

Marathon's deterministic pass is capped at `MARATHON_DETERMINISTIC_SHARE` (0.6)
of the run, and since 2026-08-12 each **row** is bounded too:
`marathon_row_budget` recomputes the fair share from what is left,
`MARATHON_ROW_BORROW = 3.0` lets a hard row take three rows' worth, and
`MARATHON_ROW_MIN_SECONDS = 1.0` is reserved for every row still queued
(borrowing alone starves the tail geometrically — a test caught that). The global
deadline is restored in a `finally` afterwards; a stale expired bound turns every
LLM candidate into `lemma_not_derivable_from_hypothesis`.

---

## Deployed budgets and the evaluation sandbox

Organizers' current spec, mirrored here because several solver constants are
derived from it.

- **Sandbox per submission**: `python:3.11-slim`, 2 vCPU, 2048 MB RAM, 64 PIDs,
  `/tmp` 64 MB tmpfs, read-only filesystem, network disabled, all capabilities
  dropped, env allowlist `PATH`/`HOME`/`LANG`/`PYTHONDONTWRITEBYTECODE`. No
  third-party packages.
- **Submission**: a single `solver.py`, max **500,000 bytes**.
- **Budgets**: solver wall clock **3600 s per problem**; Lean judge **300 s per
  call**; Lean code **100,000 bytes per call**; FALSE certificate **20,000 bytes
  per call**; LLM output **65,536 tokens per call**.
- **Tracks**: Solo (one problem per subprocess, stdin/stdout) and Marathon (N
  problems per subprocess, manifest JSONL in, append-only JSONL out, **one global
  budget**; SIGTERM at budget and the output JSONL is frozen at that moment).
- **LLM**: `openai/gpt-oss-120b` and `google/gemma-4-31b-it`, OpenRouter pinned to
  DeepInfra, fallback disabled, temperature 0.0, seed 0.
- **Judge statuses**: `accepted` | `unparsed` | `malformed` | `incomplete_proof` |
  `incorrect`. Trusted axioms allowed: `propext`, `Quot.sound`, `Classical.choice`.
- Per-problem headline budgets, as clarified 2026-07-31: **Solo 60 min, Marathon
  5 min on average**; `compression_ratio` was withdrawn as misleading. The
  vendored `rules/evaluation.md` is **stale** on the global-budget formula —
  `scripts/run_marathon.py` (600 s reference) is what the organizers confirmed.

---

## Current solver capability

`CLAUDE.md`'s "How the solver is organised" owns the route order and the engine
list; the route inventory is `stage2/docs/solver-route-ledger.md` and
`stage2/docs/motif-cards/`. Only the operational rails that live nowhere else:

1. Deterministic-first. Unresolved rows are **skipped**, not guessed at — there is
   no active broad `true:grind` fallback (the cloud judge scored it 34 accepted /
   433 incorrect). Old grind ledgers are historical discovery evidence only.
2. **FALSE certificate shapes**: `decideFin!` over a `finOpTable` at orders ≤ 10,
   and an inlined `List.getD` lookup above that, where the digit parser cannot
   round-trip (`extractDigits` keeps one value per digit character). Both
   judge-verified 2026-07-31 up to order 25. `MAX_WITNESS_ORDER = 25`, bounded by
   the FALSE byte cap and by `witness_decide_is_affordable()`.
   `set_option maxRecDepth 20000` is emitted by **`n ** variables`**, not by
   order — `DECIDE_MAX_REC_DEPTH_APPLICATIONS = 4_096` (rail 3b-iii).
   `constraint_countermodel_wide_domain` searches narrow-range wide-carrier tables
   up to order 60.
3. **Infinite countermodels are legal** and one ships (`hard2_0027`: carrier
   `Nat`, parity op, `omega` under the allowlist). Only worth it on a row with no
   finite countermodel.
4. **LLM lane boundary.** Marathon accepts solver-owned `rewrite_chain` /
   `guided_chain` outputs only; raw TRUE Lean is disabled for that lane. Solo runs
   up to `LLM_MAX_ROUNDS = 6` repair rounds and feeds parse-level rejects back via
   `{solver.feedback}`; `LLM_GUIDED_CHAIN_MAX_DEPTH = 8`. Nothing the model says
   is trusted — the solver proves it and the kernel checks it.
5. **Raw TRUE payloads**: complete Lean source in `code` only, helper declarations
   allowed above `submission`. `proof` / `proof_body` are retired shapes.
6. `_engine_gate()` before every engine enforces the global hard deadline and the
   memory guard (2048 MB sandbox vs. deep-tier closures measured at 5-17 GB RSS).
   A loop that polls neither has no memory guard either — rail 5f-v.
7. `DISTILLED_CERTS` (65 entries) is keyed by **canonical equation text**, never
   by row id, so one entry covers the official row, its HF `*`-notation mirror and
   any future ETP sample of the same implication. Nothing enters it that the real
   judge has not accepted; `distill_certs.py` judges before it emits.

---

## What is still open

No open mathematical frontier. What remains is evidence and hardening, ranked:

1. **Re-audit after the 2026-08-13 constant changes** (running as this was
   written) and refresh the table above from it.
2. **Solo has no real-runner evidence for the tier ladder.** It picks `deep` from
   a 3600 s budget, so it runs three passes where Marathon runs two, and nothing
   has exercised that path end to end. Highest-value real-run item.
3. **Step-count budgets instead of wall clock.** Four cost bugs now (rails 5f-iii,
   5f-iv, 5f-v) have all been "a wall-clock bound in the wrong place", and
   wall-clock budgets are also why route selection is nondeterministic and every
   timing number carries a noise band.
4. **Productise ordered completion as a route.** It closed the final nine and
   `sample_200`'s last three with no modification and no tuning, and it is
   strictly stronger than the e-graph on this problem class — but it lives outside
   the submission, so the shipped solver cannot use it on a fresh corpus. A new
   ETP row of that family currently costs about five seconds *by hand*. The
   pipeline moved into the repo on 2026-08-13 as
   `stage2/experiments/completion/` (it was gitignored scratch in
   `tmp_stage2_smoke/final-nine-2026-08-12/` until then); its `README.md` holds
   the judge evidence, the **GO** assessment for the port, and the one
   reproducible defect blocking five of the nine rows in the driver as shipped.
5. **Two known un-deadlined sites**, both measured, neither currently costing
   rows: `derived_rule_steps` grows unboundedly (3,371 MB at 90 s, 5,194 MB at
   360 s at `deep` — wants a cap, not a poll), and single-rule egg *extraction*
   (`egg.explain`, `_egg_bridge_steps`) takes no deadline at all while its
   multi-rule twin does. Same asymmetry that produced rail 5f-v.
6. **Bytes.** ~54.6 KB left of the cap. The remaining slow tail (`hard2_0098`
   75 s, `hard3_0131` 74 s, `hard3_0204` 72 s, `hard2_0079` 68 s) is poor value
   per byte, and `hard3_0204` is **deliberately kept live** as the audit's only
   exercise of `true:egg_ladder`. Rank distillation candidates by
   **seconds-saved per byte**, never by seconds.

---

## Current artifacts

- Official harness snapshot: `vendor/stage2-official/` at upstream commit
  `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.
- Active solver source: `stage2/solver/solver.py` (~9.1k lines, single file by
  contract). Over the 500 KB cap **by design** — it carries comments and
  docstrings that the packager strips.
- Packaged submission: `stage2/submissions/solver.py`, gitignored build output.
  Build with `stage2/solver/package_solver.ps1` (re-runs the gate and refuses to
  package on failure).
- Judge-accepted certificate fixture: `stage2/fixtures/judge_verified_certs.jsonl`
  (99 entries, all re-checked by the gate).
- Spot-check failure fixture: `stage2/fixtures/spotcheck_failures.jsonl`
  (auto-pinned, replayed forever by `test_spotcheck_regressions.py`).
- Real-judge wrapper: `stage2/experiments/judge_rows.py` (works on Windows via
  `elan`; ~3-8 s per row warm).
- Distillation tool: `stage2/experiments/distill_certs.py`.
- Corpus audit: `stage2/experiments/audit_corpus.py`; golden regeneration:
  `stage2/experiments/make_golden.py`; accuracy loop:
  `stage2/experiments/spotcheck.py`.
- Dev-only LLM loops: `dev_true_loop.py` / `analyze_true_loop.py` /
  `llm_balanced_eval.py`; ETP mining: `etp_chain.py`, `etp_pivots.py`; dev model
  finder: `mace_finder.py` (the solver's twin — when it outperforms the solver on
  a row, the gap is a bug, not a tuning difference).
- Docs: `stage2/docs/NEXT_SESSION_BRIEF.md`, `stage2/docs/LATEST_HANDOFF.md`,
  `stage2/docs/solver-route-ledger.md`, `stage2/docs/motif-cards/`,
  `stage2/docs/spotcheck.md`, `stage2/docs/playground-preflight.md`,
  `stage2/tests/README.md`, `stage2/docs/cleanup-manifest.md`.
- Theory and provenance: `theory/TEORTH_WORKFLOW.md`, `theory/TEORTH_NOTES.md`,
  `theory/tools/README.md`, `data/exports/` (~22M validated labelled ETP pairs),
  `data/teorth_cache/`.
- Stage 1 archive: `stage1/`. Finished; do not treat it as the active workflow.

---

## Operational notes

1. **`stage2/submissions/__pycache__/` must not exist when a real run starts.**
   Importing the packaged solver *in place* leaves one, and the official runner
   rejects the submission instantly. It has cost a run before; verify the packaged
   artifact by copying it elsewhere first. (One is present in the working tree as
   of this writing.)
2. `vendor/stage2-official/judge/verify.py`'s `50_000` / `10_000` / `120` are
   **fallbacks**, not the deployed caps. Read
   `vendor/stage2-official/pipeline/config.json`. CI now pins this.
3. The vendored `rules/evaluation.md` global-budget formula is **stale**; the CLI
   (`scripts/run_marathon.py`) is what the organizers confirmed.
4. The vendored official README still shows a tactic-body `proof` example. Treat
   it as upstream doc drift unless an explicit harness sync changes the contract.
5. Judge answer JSON contains **exactly** `verdict` and `code`. Route labels go to
   stderr (rail 8).
6. No benchmark ids in solver policy (rail 9). Pasted row lists are diagnostics
   and regression fixtures only.
7. **Never run two `audit_corpus.py` sweeps concurrently** (rail 5e), and never
   race `lake env` against a full audit — it has a 30 s timeout and fails under
   load.
8. Marathon validation with `--budget-tokens 0` is banned as guardrail or
   promotion evidence (rail 7).
9. For runner-equivalent certificate debugging use the official runner or
   `verify_answer(_to_judge_problem(problem), raw_answer)`. Direct
   `verify_answer(problem, ...)` omits runner proof policy — and supply the
   production judge limits, or you are measuring the fallback.
10. Local `OPENAI_API_KEY` / `OPENROUTER_API_KEY` errors are transport/setup
    issues, not submitted-solver protocol failures. Repo entrypoints load process
    env first, the ignored root `.env` second, legacy Windows User env last — a
    stale process-env key silently shadows a freshly rotated `.env` key.
11. The vendored Solo harness has local OpenRouter provider-normalization drift;
    call it out before treating local positive-token proxy output as
    upstream-clean.
12. A Solo fallback `TRUE INCORRECT` row and a Marathon `not_attempted` row can be
    the same unresolved deterministic gap under two runner policies.
13. Treat `tmp_stage2_smoke/` as scratch. Promote only concise dated summaries
    into `stage2/results/`.
14. Printing `◇` crashes on Windows cp1252 — set `PYTHONIOENCODING=utf-8` for
    ad-hoc scripts. `du`/`find` at the repo root will hang (7.4 GB / 154k files,
    mostly `vendor/stage2-official/.lake`); scope every search.

---

## Session index

Newest first. Each line points at the evidence; the detail is in the linked doc,
not here.

| Date | What it was | Evidence |
| --- | --- | --- |
| 2026-08-13 | Judge limits were configuration, not judge properties: caps doubled, LLM/Solo timeouts recalibrated, minifier made string-aware, packager made atomic, CI rebuilt on py3.11 and now checks the **artifact** | this file; `CLAUDE.md` |
| 2026-08-12 (s2) | Tier inversion fixed (more budget was losing rows); Marathon per-row deadline; single-rule egg deadline (6 s budget ran 40 s at 11 GB, defeating an armed memory guard); 34 certs distilled; `sample_200`'s last 3 closed; official wall 980 s → 330 s; real Marathon 400/400 + 200/200 untuned | `2026-08-12-tier-inversion-and-latency.md` |
| 2026-08-12 | The final nine closed by **ordered completion (Knuth-Bendix)** with proof recording, not by any engine in the solver; a standing impossibility claim in `CLAUDE.md` was provably wrong | `2026-08-12-final-nine-completion.md` |
| 2026-08-11 (late) | Simplification −51 KB (37 bespoke matchers → one `law_matcher` + a table row each, byte-identical Lean over all 5,090 real equations) and submission stripping −74 KB | `2026-08-11-solver-simplification.md` |
| 2026-08-11 | `true:egg_ladder` — the only engine that reasons with more than one law at a time; FALSE completed at 850/850; two starved-search fixes (rails 5f-ii, 5f-iii, 5f-iv) | `2026-08-11-lemma-ladder-and-starved-search-fixes.md` |
| 2026-08-07 | `DISTILLED_CERTS` + `egg_probe_route` + the first infinite countermodel; the latent `is_reflexive_problem` bug (rail 5g) | `2026-08-07-distilled-library-and-egg-probe.md` |
| 2026-08-01/03 | First real-judge campaign at scale. Two Marathon-only bugs (module-level reclaim counter never reset per row; an unguarded per-row loop body) — both fixed and confirmed. 2863/2894 real-judge rows, 0 rejected | `2026-08-01-real-judge-broad-runs-and-marathon-memory-guard-bug.md` |
| 2026-07-31 | Rules review; the "FALSE witness order ≤ 10" ceiling retired as **ours, not the judge's** — `List.getD` certs accepted at orders 13/17/25 | `2026-07-31-rules-review-and-witness-ceiling.md` |
| 2026-07-29 (v4/v4b) | Three engines: `constraint_fin*`, `egg_collapse`, `egg_bootstrap`. The node-cap bug (rail 5f) | `2026-07-29-v4-coverage-push.md`, `2026-07-29-v4b-wide-domain-and-node-cap.md` |
| 2026-07-29 (QA) | `grind` removed from a deterministic route (37 s → 4.8 s); the finite-model oracle was vacuous on 28% of rows; 34 certs judge-pinned; `solve_problem` 510 → 104 lines; `CLAUDE.md` became the entry point | `2026-07-29-qa-pass-soundness-and-refactor.md` |
| 2026-07-23 (s2) | `LARGE_WITNESS_SHAPE_KEYS` deleted — a sound witness gated on an equation-pair shape cost 30 rows to save 0.021 ms (rail 4). `Fin 9` certs judge-validated. `models_seen > 0` shown not to be TRUE evidence (rail 5) | `2026-07-23-s9a-witness-gate-and-fallback-evidence.md` |
| 2026-07-23 | The egg mechanism (`true:egg_closure`); spotcheck batches | `2026-07-23-spotcheck-batches-and-egg-frontier-study.md` |
| 2026-07-22 (s4) | ERROR class eliminated: Solo hard deadline, memory guard, insurance judge call; `narrow_grind` demoted; the lemma library and multi-hop `lemma_chain` | `2026-07-22-playground-failure-fixes.md` |
| 2026-07-22 (s3) | `universal_identity` / `projection_bootstrap` / `lemma_bootstrap` — all from one idea: **proof-search cost scales with goal size, so a small law that implies the goal can be reachable when the goal is not** | `2026-07-22-universal-identity-route-and-cache-bound.md` |
| 2026-07-22 | Spotcheck harness baseline: 1,189 distinct rows, 100% accuracy | `2026-07-22-spotcheck-baseline-and-soundness-sweep.md` |
| 2026-07-22 | hard1/hard2/eval_normal + real Marathon session | `2026-07-22-hard1-hard2-evalnormal-marathon-session.md` |
| 2026-07-21 | The offline correctness gate and effort scaling; the de-bloat plan disproven by evidence (rail 1) | `2026-07-21-correctness-harness-and-budget-scaling.md` |
| 2026-07-20 | LLM TRUE loop and prompt v3; seeded closure + derived critical pairs | `2026-07-20-llm-true-loop-and-prompt-v3.md` |
| ≤ 2026-06 | Archive. Every coverage number in those docs is superseded; the method notes are not | `stage2/results/2026-05-*.md`, `2026-06-14-*.md` |

---

## Non-goals

1. Do not edit archived Stage 1 material as active solver work.
2. Do not promote any certificate template without **official** judge acceptance.
   Local Lean acceptance of a tactic proof is not cloud evidence (rail 3).
3. Do not rely on Teorth theorem imports unless the judge allowlist permits them.
4. Do not treat secrets, network access, or repo-local imports as available to
   submitted solver code.
5. Do not delete solver routes to "de-bloat" (rail 1). De-bloat means junk files
   and stale docs, never coverage.

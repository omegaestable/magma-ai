# Eval Workflow

This is the canonical Stage 2 evaluation and promotion workflow.

## Goal

Promote a `solver.py` candidate only when it is reproducible, accepted by the official judge on local samples, robust under Solo and Marathon I/O, and reviewed adversarially.

## Official Harness

The official Stage 2 harness is vendored at `vendor/stage2-official/`.

Use upstream docs as the source of truth:

- `vendor/stage2-official/README.md`
- `vendor/stage2-official/docs/solo_mode.md`
- `vendor/stage2-official/docs/marathon_mode.md`
- `vendor/stage2-official/examples/solo/TUTORIAL.md`
- `vendor/stage2-official/examples/marathon/TUTORIAL.md`
- `vendor/stage2-official/pipeline/config.json`

**`pipeline/config.json` is the authority on every budget and judge cap**, and
`pipeline/proxy.py` passes its `judge` block straight into the judge: Lean
timeout **300 s**, Lean code **100,000 bytes**, FALSE certificate **20,000
bytes**, solver wall clock **3600 s** per problem, LLM output **65,536 tokens**.
The `50_000` / `10_000` / `120` in `vendor/stage2-official/judge/verify.py` are
the fallback for invoking the verifier with no config — reading them as the
judge's limits cost this repo two weeks of halved caps (`CLAUDE.md`, rail 3b,
third instance). Anything that judges locally must pass the production values;
`stage2/experiments/judge_rows.py` now sets them for you.

## Setup Gate

Native Windows gate:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor/stage2-official
lake update
lake exe cache get
lake build JudgeMagma.Magma JudgeDecide.DecideBang JudgeFinOp.MemoFinOp JudgeSupport.Inspect
c:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe scripts/run_harness.py
c:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe scripts/run_marathon_harness.py
Pop-Location
```

WSL 2, Linux, or macOS comparison gate:

```bash
cd vendor/stage2-official
bash scripts/setup.sh
source .env.judge
python3 scripts/run_harness.py
python3 scripts/run_marathon_harness.py
```

Do not diagnose local solver performance until the official harness is green.

The vendored harness has documented local Windows compatibility patches in `vendor/stage2-official/UPSTREAM.md`. Treat those patches as local drift from the upstream snapshot, and rerun both official harnesses after any upstream sync.

## Packaging Gate

From PowerShell:

```powershell
.\stage2\solver\package_solver.ps1
```

Check:

1. `stage2/submissions/solver.py` exists.
2. File size is below 500 KB.
3. `stage2/submissions/` contains no extra files or directories.
4. It uses no repo-local imports.
5. It does not read local secrets.

The packager enforces 1-3 itself: since 2026-08-13 it minifies to a temp file and
swaps it into `stage2/submissions/` only after the 500,000-byte check passes,
then asserts the directory holds nothing but `solver.py`. A failed build
therefore leaves the previous artifact intact rather than an empty directory.

Do not carry package sizes forward in this file; the current figure lives in
`CLAUDE.md` (**466,320 bytes** on 2026-08-21). The `138939` bytes this line used
to quote was a 2026-05-30 measurement and was stale by ~300 KB.

The cap that matters is on the **artifact**, not on `stage2/solver/solver.py` —
the source carries comments and docstrings and is legitimately over 500 KB. CI
builds the artifact and asserts the cap on it.

## Playground Preflight Gate

Before upload or playground testing, run `stage2/docs/playground-preflight.md` as a focused gate. It exists to prevent three common mistakes:

1. Submitting a directory with extra files instead of the single generated `solver.py`.
2. Confusing a local runner proxy missing `OPENAI_API_KEY` or `OPENROUTER_API_KEY` with a solver-side protocol bug.
3. Updating public benchmark claims from smoke-only evidence.

The current solver does not expose broad `true:grind` as an active route. LLM readiness requires a positive-token proxy run with nonzero LLM calls, nonzero Marathon token usage, and classified LLM/proxy/judge outcomes; the solver should never carry local keys or call model APIs directly.
For wide official public validation under the published playground budget model,
use `stage2/experiments/run_playground_public_sweeps.py`; it packages the
single-file solver, applies the public `3600 s` / `65536 token` reference
budgets per problem, and fails closed on nonpositive token budgets or zero-call
runs.
For standard local LLM runs, configure the rotated upstream key in the ignored
root `.env` with `stage2/experiments/set_openrouter_repo_env.ps1`. The
repo-owned probe/parity entrypoints load process env first, root `.env`
second, and legacy Windows User env last.

Active Marathon validation in this repo must use a positive token budget. Do
not run or promote `--budget-tokens 0` as a guardrail, regression gate, or
readiness signal; archived no-LLM summaries are historical archaeology only.

## Solo Debug Loop

Use Solo for fast proof debugging and judge feedback.

For the pinned harness snapshot, `pipeline/proxy.py` and the official Solo demos use `{"call":"judge","verdict":...,"code":...}`. If prose docs mention a terminal `type: submit` shape, verify against the proxy before changing solver I/O.

1. Pick a small public problem file from `vendor/stage2-official/examples/problems/`.
2. Run the official baseline to confirm harness health.
3. Run the local packaged solver.
4. Inspect judge statuses: `accepted`, `unparsed`, `malformed`, `incomplete_proof`, `incorrect`.
5. Fix the certificate generator, not only the prompt.

Operational reminder: the judge answer schema is exact. The submitted JSON must
contain only `verdict` and `code`. Route labels and solver-family notes belong
in stderr/log-derived summaries, not in the answer payload.

For fast deterministic Solo smokes on a machine with local upstream keys
configured, blank `OPENAI_API_KEY` and `OPENROUTER_API_KEY` in the runner
process. This makes unresolved LLM proxy calls fail fast while still checking
schema-valid fallback behavior. Use the positive-token parity runner only when
intentionally testing LLM readiness.

For runner-equivalent certificate debugging, prefer the official runner. If a direct Python check is needed inside the harness code, convert the public problem row with `_to_judge_problem(problem)` before calling `verify_answer(_to_judge_problem(problem), raw_answer)`. A plain `verify_answer(problem, ...)` omits the pipeline default proof policy and can report dependency-policy failures that the runner does not report.

Recent FALSE-certificate lesson: a table needs `set_option maxRecDepth 20000`
before `decideFin!` when the goal is expensive to decide, and the axis is
`n ** variables`, not order. `decideFin!` is exhaustive, so a `Fin 6` table
against a 5-variable goal is 7,776 applications and was **`LEAN_REJECTED`**
without the option and `accepted` with it (real judge, 2026-08-11); the same
table against a 4-variable goal (1,296) is accepted either way. The renderer
triggers on `n >= 7` **or** `decide_applications > DECIDE_MAX_REC_DEPTH_APPLICATIONS`
(4,096). An order-only rule of thumb misses the `Fin 6` case entirely. This is a
certificate-generation detail, not a harness patch.

## Marathon Loop

Use Marathon for competition-relevant triage and budget behavior.

1. Read the manifest once.
2. Rank problems by deterministic solve probability and expected token cost.
3. Submit deterministic certificates first.
4. Spend LLM budget only on unresolved high-value cases.
5. Respect append-only JSONL output and last-write-wins semantics.
6. Track tokens, wall-clock, accepted count, and failure class.

The local solver now also supports a repo-local knob
`MAGMA_MARATHON_REF_SECONDS_PER_PROBLEM` so the same Marathon triage can be
tested against both current upstream budget interpretations (`600` vs `3600`
seconds per reference problem).

Custom local Solo environment knobs are not reliable official behavior because the proxy sanitizes the solver subprocess environment. Treat runner/proxy behavior as authoritative.

## Certificate Distillation

For each failed certificate attempt, record:

1. problem id, equation ids, and verdict attempted
2. generated Lean code hash or path
3. judge status
4. relevant stderr excerpt
5. expected proof family or witness family
6. root cause: syntax, type mismatch, dependency policy, bad witness, bad proof idea, timeout, or unsupported import

After any meaningful public benchmark run, regenerate:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\summarize_public_benchmarks.py
.\.venv\Scripts\python.exe stage2\experiments\competition_preflight.py
```

These are now part of the team-memory chain, not optional extras.

Keep smoke evidence separate from full benchmark evidence. `sample_20`, `sample_200`, targeted fixtures, and Marathon slices are useful for debugging and pacing, but top-level public totals should only change after the full public suite is rerun and summarized under `stage2/results/`.

Selected-row reproductions are diagnostic fixtures. Normalize labels to local ids, verify direct probes with `_to_judge_problem(problem)`, and convert any finding into a reusable proof/witness family or a focused regression fixture instead of hardcoding benchmark ids into solver policy.

## Promotion Rule

A candidate can be called a Stage 2 champion only if:

1. Official harness tests pass locally.
2. Packaged solver is <= 500 KB.
3. Solo sample runs are reproducible.
4. Marathon sample runs are reproducible.
5. Deterministic certificates are judge-accepted on their fixture set.
6. Red-team review finds no blocker.
7. The candidate has a result summary under `stage2/results/`.
8. Marathon evidence uses a positive token budget and records the LLM/proxy
   outcome, even when no LLM certificate is ultimately accepted.

## Banned Shortcuts

1. No benchmark-pair memorization as solver policy.
2. No hidden dependency on local files outside the submitted `solver.py`.
3. No hidden dependency on local API keys or environment variables.
4. No proof template promotion without accepted Lean evidence.
5. No changing official reference config and calling the result official.
6. No runtime dependence on Teorth caches, live scraping, or paper files from the submitted solver.
7. No `--budget-tokens 0` Marathon runs as validation, promotion evidence, or
   default workflow.

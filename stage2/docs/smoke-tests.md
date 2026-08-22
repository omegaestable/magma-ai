# Stage 2 Smoke Tests

Reviewed 2026-08-13. `CLAUDE.md` is authoritative; this file is the *runnable*
companion to it — what to run for a fast confidence check, what each command
actually proves, and the operational rules that cost sessions to learn.

A smoke test here is not a benchmark. It answers "is the artifact well-formed,
does the harness accept it, does transport work" in minutes. Coverage numbers
come from `audit_corpus.py` and the real judge, never from a smoke run — see
**Evidence boundary** at the end.

Three tiers, in increasing order of what they need from the machine:

| Tier | Needs | Section |
| --- | --- | --- |
| Lean-free smokes | nothing but `.venv` | [1](#1-lean-free-smokes) |
| Official runner probes | `elan` + a built Lean toolchain | [2](#2-official-runner-probes-need-elan) |
| LLM transport probes | an OpenRouter key | [3](#3-llm-transport-probes-need-a-key) |

## 0. Facts every smoke run depends on (verified 2026-08-13)

**Deployed judge limits come from `vendor/stage2-official/pipeline/config.json`**
(the `judge` block), which `pipeline/proxy.py:1004-1012` passes into the judge on
every call:

| Limit | Deployed value |
| --- | --- |
| Lean timeout per judge call | **300 s** |
| Lean code per call | **100,000 bytes** |
| FALSE certificate per call | **20,000 bytes** |
| Solver artifact | **500,000 bytes** |
| Solver wall clock, per problem | **3600 s** |
| LLM output tokens, per call | **65,536** |

The `50_000` / `10_000` / `120` in `vendor/stage2-official/judge/verify.py` are
the **fallback used only when the verifier is invoked with no config**. Calling
`verify_answer()` directly and reading its caps measures the fallback against
itself; that mistake halved the solver's caps for two weeks (see rule 9).
`stage2/experiments/judge_rows.py` now sets `LEAN_TIMEOUT_SECONDS`,
`MAX_CODE_LENGTH` and `MAX_FALSE_CERT_BYTES` to the production values, so local
judging matches deployment.

The Lean timeout the judge actually gets is
`min(config cap, wall-clock remaining)` — a judge call late in a Solo budget
gets less than 300 s, which is why `SOLO_FALLBACK_RESERVE_SECONDS` reserves
310 s for the last one.

**Sandbox the submission is graded in:** `python:3.11-slim`, 2 vCPU, 2048 MB RAM,
64 PIDs, 64 MB `/tmp` tmpfs, read-only filesystem, no network, all capabilities
dropped, env allowlist `PATH`/`HOME`/`LANG`/`PYTHONDONTWRITEBYTECODE`, no
third-party packages.

**Interpreter mismatch to keep in mind:** the local `.venv` is Python **3.14.3**
(checked 2026-08-13) and the graders run **3.11**. CI pins 3.11 for exactly this
reason — it said 3.12 until 2026-08-13, so nothing had ever executed the solver
on the interpreter that grades it. A local smoke passing on 3.14 is not proof
the artifact imports on 3.11; the CI gate is.

## 1. Lean-free smokes

No Lean, no key, no network. These always work and are the right first move
after any solver edit.

```powershell
.\.venv\Scripts\python.exe -m py_compile stage2\solver\solver.py stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe theory\tools\smoke_problem_sets.py
.\stage2\solver\package_solver.ps1
```

What each proves:

- `smoke_llm_dsl.py` — solver-owned LLM DSL parsing against **fake** payloads
  only: no model call, no secret read, no proxy. It accepts helper-bearing
  full-file TRUE `code` payloads and rejects the legacy `proof` / `proof_body`
  shapes.
- `smoke_problem_sets.py` — the official mirrors load and the analysis-only
  problem-set policy holds.
- `package_solver.ps1` — the real packaging path: it runs the offline gate
  (`pytest stage2/tests -q -n auto`), minifies via
  `stage2/solver/minify_submission.py`, and **builds to a temp file, swapping
  into `stage2/submissions/solver.py` only after both the gate and the
  500,000-byte check pass.** `-SkipTests` exists for a deliberate spike; do not
  use it before an upload. `-WarnBytes 450000` is a "within 10% of the cap"
  alarm, not a de-bloat target (rail 1).

Artifact size, most recent measurement: **466,320 of 500,000 bytes (33,680
free, 6.7%)**, packaged 2026-08-21 after the `true:completion` engine landed
(+20,680 bytes over the 2026-08-13 build's 445,640). That is past the packager's
`-WarnBytes 450000` alarm, which is the alarm doing its job — not a signal to
de-bloat (rail 1). The headroom to spend, if it is ever needed, is measured and
listed: 48 of the 65 `DISTILLED_CERTS` entries (120,229 bytes) are now
live-solvable by the completion engine, per
`stage2/results/2026-08-21-distilled-live-solvable.txt` — but every one of them
is judge-pinned, so read `NEXT_SESSION_BRIEF` §3.3 before deleting any.

This is exactly why the artifact is a gitignored build output: **re-package and
read the number the packager prints; never quote a stored figure.** This file
carried a stale `138939` for months, and then a 2026-08-13 figure with a
"10.9% headroom" clause that survived one number being updated under it.

The minifier is the reason the artifact fits at all (comments and docstrings are
~17% of the source, LF instead of CRLF another ~2%), and it proves the artifact
parses to the same tree as the source before writing. Two things about it worth
knowing when a smoke fails there:

- its line transforms are **string-aware** as of 2026-08-13. They previously
  rewrote the *contents* of multi-line string literals (collapsing blank runs,
  stripping trailing whitespace), which hard-fails the parse-tree check —
  `DISTILLED_CERTS` stores every certificate as triple-quoted Lean, so one cert
  with a trailing space would have bricked the packager.
- `check()` now names the first differing top-level statement instead of failing
  with a bare message.

### CI does a stricter version of this

`.github/workflows/gate.yml` on every push and PR: Python 3.11, `ruff check .`,
the offline pytest gate, then it **builds the submission and asserts the
500,000-byte cap on the artifact** (not on `stage2/solver/solver.py`, which
carries comments and is legitimately over the cap), and finally asserts the
solver's judge-limit constants still match `pipeline/config.json`. That last
step exists so the cap drift in rule 9 cannot recur silently.

### The heavy local commands are in CLAUDE.md, not here

`pytest stage2/tests`, `audit_corpus.py`, `spotcheck.py` and `judge_rows.py` are
the four commands in `CLAUDE.md`. Two smoke-relevant rules about them:

- **Never run two `audit_corpus.py` sweeps at once, and check what else is on
  the machine before quoting any wall clock** (rail 5e). Engines below
  `equational_closure` are wall-clock-budgeted, so contention manufactures
  spurious "losses". The same applies to `lake env`, which times out at 30 s
  under heavy load.
- **`--row-budget` when measuring a deployed tier** (rail 12). Solo and Marathon
  always bound a row; the audit does not unless told to, so `--effort
  standard/deep` without it measures a solver no runner will ever be.

## 2. Official runner probes (need elan)

### Toolchain

`vendor/stage2-official/lean-toolchain` pins `leanprover/lean4:v4.30.0-rc2`
(checked 2026-08-13). The local native-Windows install validated in the
2026-05-30 setup run was Elan `4.2.1`, Lean `4.30.0-rc2`
(`x86_64-w64-windows-gnu`), Lake `5.0.0-src+3dc1a08`.

```powershell
winget install --id Lean.Elan -e --accept-source-agreements --accept-package-agreements
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
elan toolchain install leanprover/lean4:v4.30.0-rc2
elan default leanprover/lean4:v4.30.0-rc2
Push-Location vendor/stage2-official
lake update
lake exe cache get
lake build JudgeMagma.Magma JudgeDecide.DecideBang JudgeFinOp.MemoFinOp JudgeSupport.Inspect
Pop-Location
```

The local Lean judge **does** work on native Windows via `elan`, despite the
docs saying WSL/Linux only.

### Before any runner invocation

```powershell
$env:PYTHONUTF8 = '1'
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Get-ChildItem stage2\submissions   # must list solver.py and nothing else
```

**`stage2/submissions/` must contain only `solver.py`.** Both runners enforce
the single-file contract and fail the whole run with
`submission must contain only solver.py; found extras: [...]`
(`pipeline/proxy.py:588` for Solo, `pipeline/marathon_runner.py:154` for
Marathon). `.gitkeep`, `__pycache__`, editor backups — all fatal. This is not
hypothetical: on 2026-08-13 the directory held a `__pycache__/` next to
`solver.py`.

**Package last.** Run `package_solver.ps1` immediately before the runner
invocation, after anything that might import from the submission path —
`compileall stage2` and a bare `python stage2/submissions/solver.py` both create
bytecode caches under it.

### Solo

```powershell
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions `
    --problems examples\problems\sample_20.json `
    --output ..\..\tmp_stage2_smoke\<date>-sample20-solo.json
Pop-Location
```

`--problems` also takes `sample_200.json`, `hard1.jsonl`, `hard2.jsonl`,
`hard3.jsonl`, `normal.jsonl` from `examples/problems/`. **Always pass an
explicit `--output`**; the default `pipeline/results/submissions.json` is
trivially confused with an earlier smoke's rows.

If upstream keys are configured locally, blank `OPENAI_API_KEY` and
`OPENROUTER_API_KEY` for a fast deterministic Solo smoke. The official proxy
sanitizes custom solver env vars, so blanking the *runner's* keys is the
reliable way to avoid accidental long LLM calls while still exercising the final
fallback path.

Solo runs `deep` effort (three tier passes) with a 3600 s per-problem budget.
`CLAUDE.md` still records Solo as having **no** end-to-end evidence for the tier
ladder — a Solo run over a real set is the smoke worth doing here.

### Marathon

```powershell
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe scripts\run_marathon.py --solver ..\..\stage2\submissions `
    --manifest examples\problems\marathon\normal_100.jsonl `
    --output-dir ..\..\tmp_stage2_smoke\<date>-normal100-marathon
Pop-Location
```

Note `--output-dir` (Marathon), not `--output` (Solo).

**Omit the budget flags and take the defaults.** `run_marathon.py` derives them
as `compression_ratio × N × reference`, with `DEFAULT_COMPRESSION_RATIO = 0.5`,
`REF_PER_PROBLEM_SECONDS = 600` and `REF_PER_PROBLEM_TOKENS = 65536` — for the
100-row manifest that is 30,000 s and 3,276,800 tokens, i.e. the 300 s and
32,768 tokens per problem that deployment actually gives. Hand-picked budgets
mostly manufacture an unrepresentative run: the 2026-05-30 smoke below passed
`--budget-seconds 360000`, which is 3600 s a row, ten times the real pace.
(`compression_ratio` was withdrawn by the organizers as a *reported metric*; the
CLI knob and the 5 min/problem average it produces are what they confirmed.)

**Never use `--budget-tokens 0` as validation or promotion evidence** (rail 7).
Marathon guardrails require a positive token budget.

Marathon-specific things a smoke can catch that nothing else can — both were
found the expensive way:

- Marathon is **one process for the whole manifest**, so any module-level
  per-row counter accumulates across it. `_mem_reclaims_left` did, and 3
  memory-guard trips anywhere disabled every general engine for every remaining
  problem (rail 10). Neither the audit nor Solo can see this.
- One bad row must not kill the manifest; the `try/except` wraps the **entire**
  per-row body, not just `solve_problem()` (rail 11). Symptom of a regression
  here is a silent stop partway through with no traceback anywhere.
- Marathon has **no resume**. State the redo-cost before stopping a run.

### Harness suites

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe scripts\run_harness.py
..\..\.venv\Scripts\python.exe scripts\run_marathon_harness.py
Pop-Location
```

These validate the harness itself (judge cases, public attacks, pipeline
regressions) after local patches documented in
`vendor/stage2-official/UPSTREAM.md`. Last recorded pass: 2026-05-25 — see
[Superseded measurements](#superseded-measurements).

### Certificate debugging inside the harness

- **`verify_answer(problem, ...)` called directly is not runner-equivalent.**
  Use the official runner, or
  `verify_answer(_to_judge_problem(problem), raw_answer)`. With no config it
  also silently applies the *fallback* limits, which is precisely how the wrong
  caps got written down (rule 9).
- Judge statuses are `accepted | unparsed | malformed | incomplete_proof |
  incorrect`. A size violation surfaces as `malformed` / `CODE_TOO_LONG`, not as
  a clear cap message.
- Allowed trusted axioms: `propext`, `Quot.sound`, `Classical.choice`.
- Protocol: `pipeline/proxy.py` and the official Solo demo solvers use
  `{"call": "judge", "verdict": ..., "code": ...}` and finish when the judge
  accepts. `docs/solo_mode.md` also describes a terminal `type: submit` shape —
  treat the proxy and examples as executable truth for this snapshot.
- For row-level real-judge checks, prefer
  `stage2/experiments/judge_rows.py --ids <id>,<id>` (3-8 s per row warm) over
  hand-rolled verifier calls.

## 3. LLM transport probes (need a key)

```powershell
.\.venv\Scripts\python.exe stage2\experiments\homelab_llm_probe.py --key-status
.\.venv\Scripts\python.exe stage2\experiments\homelab_llm_probe.py --run-direct-openrouter-smoke
.\.venv\Scripts\python.exe stage2\experiments\homelab_llm_probe.py --run-proxy-smoke `
    --marathon-budget-tokens 4096 --marathon-budget-seconds 180
```

- `--key-status` prints only non-secret key-shape metadata. It reads process env
  first, then the gitignored root `.env`, then the legacy Windows User env
  fallback. **A stale process-env key silently shadows a freshly rotated `.env`
  key** — strip it with `env -u` to verify which one is live.
- `--run-direct-openrouter-smoke` checks plain, pinned-provider, and
  pinned-provider-plus-reasoning request shapes.
- `--run-proxy-smoke` exercises Solo and Marathon transport through the official
  proxy. Other flags: `--run-solo` / `--solo-output`, `--run-marathon` /
  `--marathon-output-dir`, `--limit`.

**This is transport evidence only.** A proxy smoke says the wire works; it says
nothing about proof quality, and hard TRUE probes are far slower.

Model configuration, as the organizers publish it: `openai/gpt-oss-120b` and
`google/gemma-4-31b-it`, OpenRouter pinned to DeepInfra with fallback disabled,
`temperature 0.0`, `seed 0`, 65,536 max output tokens. The solver's
`LLM_CONFIG["model"]` honours the `JUDGE_MARATHON_MODEL` env var as of
2026-08-13 (it was hardcoded before, which made the documented knob
unreachable); `pipeline/marathon_llm.py:145` uses the same precedence.

`LLM_HTTP_TIMEOUT_SECONDS` is **300.0** as of 2026-08-13, raised from 75.0: 75 s
aborted 225 of 446 logged real calls, and an abort still spends the tokens and
loses the row. If a transport smoke used to "pass" quickly by timing out, it
will now take longer and actually complete.

## Durable operational rules

1. **`stage2/submissions/` holds `solver.py` and nothing else.** Both official
   runners reject extras before executing anything.
2. **Package last**, after any command that could write bytecode under the
   submission path.
3. **`PYTHONUTF8=1` and elan on `PATH`** for official runner checks. Certificates
   carry `◇`; printing it under Windows cp1252 raises `UnicodeEncodeError`. CI
   sets `PYTHONIOENCODING=utf-8` for the same reason.
4. **Explicit `--output` (Solo) / `--output-dir` (Marathon).** Defaults collide
   with earlier smoke rows.
5. **No `--budget-tokens 0` runs as evidence** (rail 7), and prefer the runner's
   default derived budgets over hand-picked ones.
6. **Selected rows are diagnostics, not policy.** Generalize a fix into a proof
   or witness family; never paste benchmark ids into solver policy (rail 9).
7. **A smoke number is not a coverage number.** Route selection races a wall
   clock, so solved totals carry a run-to-run noise band — diff by row id, never
   by total (rail 2).
8. **Local Lean acceptance of a tactic proof is not cloud evidence** (rail 3).
   Certificates must be kernel-checkable.
9. **Verify a limit against the configuration that deploys it, not against a
   library's fallback.** The 2026-08-13 experiment — one certificate judged
   twice, only the configured cap varying — settled it: 48,003 bytes accepted
   under both caps; 60,015 and 90,023 bytes `malformed`/`CODE_TOO_LONG` at
   50,000 and **accepted** at 100,000. The cap is configuration. This was the
   third instance of the rail-3b error class (a hard limit inferred from one
   insufficient experiment), and CI now pins the solver's mirrors to
   `pipeline/config.json`.

## Superseded measurements

Kept with their original dates. These were real measurements; they are simply
no longer current, and the corpus they were taken against is now fully solved
locally.

- **2026-05-25, no-key Solo smoke:** `sample_20` `15/20`, `sample_200`
  `169/200`. Superseded — the corpus is complete locally
  (2026-08-12 session 2: official 1669/1669, HF mirrors 800/800, `sample_200`
  200/200; 2669 distinct rows, because the HF mirrors overlap the official sets
  by 20). For reference, `audit_corpus.py` reads `sample_20` as 20/20 at `fast`
  in 32 s (2026-08-12) — an audit-harness figure, not an official-runner one.
- **2026-05-30, packaged Marathon smoke:** `normal_100` `75/100` accepted,
  `47419` tokens, no incorrect submissions. Superseded by real-judge Marathon
  evidence: `hard3.jsonl` 400/400 accepted with 0 rejected, 0 `not_attempted`
  and 0 LLM calls, plus 200/200 on 200 fresh ETP rows (seed `20260812`),
  both 2026-08-12.
- **2026-05-30, packaged artifact `138939` bytes.** Superseded; see section 1.
- **2026-05-25, harness suites:** Solo/Lean harness no failing buckets — 66/66
  judge cases, 79/79 public attacks, 55/55 pipeline regressions; Marathon
  harness 25/25 with Lean available.
- **2026-05-21 focused reproduction:** closure-route dedupe preserved
  `normal_100 = 74/100`; a 27-row pasted fallback list scored `3/27` in archived
  Marathon evidence (three `evaluation_extra_hard_false_*` rows via
  `false:witness:S4C`, the rest `not_attempted` in Marathon and fallback
  `TRUE INCORRECT` in Solo-style probing).
- **2026-05-20 route profiling**, `stage2/experiments/profile_solver_routes.py`
  with `ABSORPTION_TIME_BUDGET = 0.05`: `normal_100` produced 74 deterministic
  candidates in 51.0 s, `sample_200` 169 in 62.2 s, no judge or LLM calls. The
  tool and the constant both still exist; the counts are superseded.
  ```powershell
  .\.venv\Scripts\python.exe stage2\experiments\profile_solver_routes.py `
      --manifest vendor\stage2-official\examples\problems\marathon\normal_100.jsonl `
      --output tmp_stage2_smoke\solver_route_profile.json `
      --marathon-budget-seconds 600 --reference-seconds-per-problem 600
  ```
- **2026-05-14 hard-mix probe**, seed `20260514`: `73/150` (up from `68/150`),
  no regressions; full hard-only reruns `hard1 24/69`, `hard2 64/200`,
  `hard3 211/400`. All superseded by the complete official sets.
- **Certificate lessons from the 2026-05 fixtures**, still true as mechanism:
  `false_907_2534` exposed a Lean recursion-depth failure for a `Fin 7` witness,
  fixed by emitting `set_option maxRecDepth 20000` before `decideFin!`;
  `false_1682_411` and `false_3145_3481` needed larger named compact witnesses
  (`S5A`, `S4A`) and a named-witness cap independent of the bounded brute-force
  cap. The `maxRecDepth` trigger has since been characterised properly — it is
  driven by `n ** variables`, not by order (rail 3b-iii).
- **Stale fixture note:** `tmp_stage2_smoke/hard3_true2.jsonl` was retired as an
  LLM-path probe once `hard3_0002` became deterministic. There is no longer any
  locally-unsolved official row to use in its place, so a no-key LLM-path probe
  now needs a fresh ETP row outside the benchmark ids.

## Evidence boundary

- Smoke runs prove **well-formedness and transport**. Coverage comes from
  `audit_corpus.py` (offline oracles — an *upper bound* on judge acceptance) and
  from the real judge (ground truth).
- Current corpus and real-judge totals live in `CLAUDE.md`; do not restate them
  here, or this file will drift again.
- Session evidence lives in `stage2/results/`. The most recent are
  `2026-08-12-tier-inversion-and-latency.md`,
  `2026-08-12-final-nine-completion.md` and
  `2026-08-11-lemma-ladder-and-starved-search-fixes.md`. The 2026-05 summaries
  (`2026-05-12-public-finite-countermodels-summary.md`,
  `2026-05-14-hard-affine-absorption-summary.md`) remain the record of that era,
  not the current benchmark state.
- Raw files under `tmp_stage2_smoke/` are local debugging artifacts, not
  evidence.
- Before any upload: `stage2/docs/playground-preflight.md`.

# Restart Checklist

For a cold start: a new agent, or you after time away. Deadline **2026-08-31
23:59 AoE**.

Five minutes of reading, then the four commands. If anything here disagrees with
`CLAUDE.md`, **`CLAUDE.md` wins and this file gets fixed**.

## 1. Read `CLAUDE.md`. That is the whole orientation step.

It is the authoritative entry point: what the deliverable is, the measured state
with dates, and the rails that cost real points to relearn. Read it end to end
before touching anything. Everything else is on-demand:

| Only if the task needs it | Read |
| --- | --- |
| What to do next | `stage2/docs/NEXT_SESSION_BRIEF.md` |
| What last session did, in detail | `stage2/docs/LATEST_HANDOFF.md` |
| Operational truth, effort tiers | `CURRENT_STATE.md` |
| Which route solves what | `stage2/docs/solver-route-ledger.md`, `stage2/docs/motif-cards/` |
| How the offline gate is built | `stage2/tests/README.md` |
| Spot-check design | `stage2/docs/spotcheck.md` |
| Running the official harness | `EVAL_WORKFLOW.md`, `vendor/stage2-official/` |
| Before an upload | `stage2/docs/playground-preflight.md` |
| Mining teorth for theory | `theory/TEORTH_WORKFLOW.md` |
| Per-session evidence | `stage2/results/` (dated, keep, do not rewrite) |

`stage1/` is a finished archive. Do not start work there.

## 2. Check the environment

```powershell
.\.venv\Scripts\python.exe -V
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

**The local venv is Python 3.14, and the sandbox that grades the submission is
`python:3.11-slim`.** This line used to say "expect 3.11", which had stopped
being true, and leaving it there made a real risk look checked. The guard
is CI (`.github/workflows/gate.yml` pins `python-version: "3.11"`), not the local
interpreter. The risk it guards against is syntax newer than 3.11 — PEP 701
f-strings (nested same-type quotes) are the easy one to write by accident on
3.12+ and they are a hard `SyntaxError` on 3.11, which would fail the whole
submission rather than one row.

The offline gate carries the local half of that guard:
`test_solver_uses_no_syntax_newer_than_the_interpreter_that_grades_it`, which
scans `solver.py` for the PEP 701 relaxations and asserts on a known-bad probe
that its own scanner still bites.

**Do not "simplify" it to `ast.parse(..., feature_version=(3, 11))`.** That was
tried on 2026-08-21 and it is **vacuous** — `feature_version` does not gate PEP
701, so it parses `f"{d["k"]}"` without complaint and the test passes on code the
sandbox cannot import. A guard that cannot fail is worse than no guard.

Only if you need the Lean judge (i.e. you are touching a certificate builder):

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
elan toolchain install leanprover/lean4:v4.30.0-rc2   # pinned in vendor/stage2-official/lean-toolchain
Push-Location vendor/stage2-official
lake exe cache get
lake build JudgeMagma.Magma JudgeDecide.DecideBang JudgeFinOp.MemoFinOp JudgeSupport.Inspect
Pop-Location
```

The 7.06 GB `.lake` build cache already in the tree is this, prebuilt. Keep it.

## 3. The four commands, and when to run each

```powershell
# 1. Offline correctness gate (~24 s on -n auto). BEFORE and AFTER any solver change.
.\.venv\Scripts\python.exe -m pytest stage2/tests -q -n auto

# 2. Full corpus audit. Once per session, never two at once (see gotchas).
#    Add --hf for the HF mirrors. Add --row-budget when measuring a tier you
#    actually deploy: Solo and Marathon always bound a row, the audit does not.
.\.venv\Scripts\python.exe stage2/experiments/audit_corpus.py --all --out stage2/results/audit-<date>.json

# 3. The standing accuracy loop. Every session; fix whatever it pins.
.\.venv\Scripts\python.exe stage2/experiments/spotcheck.py

# 4. Package (re-runs the gate and refuses to package on failure).
.\stage2\solver\package_solver.ps1
```

Touched a certificate builder? Add a fifth — the real Lean judge is the only
thing that is not an upper bound:

```powershell
.\.venv\Scripts\python.exe stage2/experiments/judge_rows.py --ids hard2_0080,normal_0747
```

Judge limits, read from `vendor/stage2-official/pipeline/config.json` and
confirmed by experiment 2026-08-13: **300 s** per Lean call, **100,000 bytes**
per certificate, **20,000 bytes** for a FALSE certificate, 3600 s of solver wall
clock per problem. The smaller numbers in `judge/verify.py` are the no-config
fallback, not the deployed limits; `judge_rows.py` now sets the production values
so local judging matches deployment.

## 4. Gotchas that actually bite

- **UTF-8.** Certificates carry `◇`, and printing it dies with
  `UnicodeEncodeError` on a Windows cp1252 console. Set `$env:PYTHONUTF8='1'`
  (or `PYTHONIOENCODING=utf-8`) in any ad-hoc script; the repo entrypoints
  already do.
- **Scope every search.** The working tree is ~7.4 GB / 154k files, 7.06 GB of it
  `vendor/stage2-official/.lake`. `du`/`find` at the repo root will hang. Use
  `Grep`/`Glob` (they respect `.gitignore`) or point `find` at a subdirectory.
- **The local Lean judge works on Windows** via `elan`, despite the vendored docs
  saying WSL/Linux only. Caveat: `lake env` times out (30 s) under heavy CPU
  load, so never judge while an audit is running.
- **Never run two `audit_corpus.py` sweeps concurrently.** Every engine below
  `equational_closure` is wall-clock-budgeted, so competing 16-worker pools starve
  each other and invent losses — 16 spurious ones in a measured case, 0 real.
  Check what else is on the machine before quoting any wall clock; killing a sweep
  does not necessarily kill its worker pool.
- **Diff by row id, not by total.** Solved counts carry a ±7 run-to-run noise
  band, so a total tells you nothing about a route change.
- **No `--budget-tokens 0` Marathon runs** as validation or promotion evidence.
- **Never write an extrapolated number as a measurement.** A headline of
  "last audit + 3 verified rows" once made a clean run look like a regression.

## 5. Before submitting

```powershell
.\stage2\solver\package_solver.ps1
Get-ChildItem -Force stage2/submissions
```

1. The packager runs the gate first and refuses to package on failure. It builds
   to a temp file and swaps in only after the 500,000-byte check passes, so a
   failure leaves the previous artifact intact.
2. `stage2/submissions/` must contain **`solver.py` and nothing else** — the
   official Solo runner rejects the directory before executing the solver. Delete
   any `__pycache__`, `.gitkeep` or stray file. (The directory is gitignored, so
   git will not warn you.)
3. Size under 500,000 bytes. Last packaged: **466,320 bytes, 6.7% headroom**
   (2026-08-21). Never shrink it by deleting routes — rail 1. If headroom is ever
   needed, the measured slack is in `DISTILLED_CERTS`, not in routes: see
   `stage2/docs/NEXT_SESSION_BRIEF.md` §3.3.
4. Single file, no repo-local imports, no network, no secrets. The sandbox is
   `python:3.11-slim`, 2 vCPU, 2048 MB RAM, read-only filesystem, network
   disabled.
5. CI (`.github/workflows/gate.yml`) mirrors this: ruff, the pytest gate, a real
   build of the artifact with the cap asserted on the *artifact* (not the source,
   which legitimately exceeds it), and a check that the solver's judge-limit
   constants still match `vendor/stage2-official/pipeline/config.json`.

## 6. Traps

1. Treating archived Stage 1 results as Stage 2 proof evidence.
2. Shipping Lean the real judge has not accepted. Local acceptance of a tactic
   proof is not cloud evidence; certificates must be kernel-checkable.
3. Inferring a hard limit from one failed experiment. Three rails have been
   written this way and all three were wrong — the order-10 witness cap, the
   `maxRecDepth` trigger, and the halved judge limits. Vary the spelling once
   before writing the rail down.
4. Putting anything but `verdict` and `code` in the judge answer JSON. Route
   labels go to stderr.
5. Hardcoding benchmark row ids into solver policy. Generalise into a proof or
   witness family; distillation is keyed by canonical *equation text*, never by
   row id.
6. Forgetting that solver subprocesses do not inherit local secrets, and that the
   submitted solver may use only the official proxy protocol.
7. Editing `vendor/stage2-official/` without recording the drift in
   `vendor/stage2-official/UPSTREAM.md`.
8. Treating `tmp_stage2_smoke/` output as durable evidence before promoting it to
   `stage2/results/`.

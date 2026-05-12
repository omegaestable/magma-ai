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

## Promotion Rule

A candidate can be called a Stage 2 champion only if:

1. Official harness tests pass locally.
2. Packaged solver is <= 500 KB.
3. Solo sample runs are reproducible.
4. Marathon sample runs are reproducible.
5. Deterministic certificates are judge-accepted on their fixture set.
6. Red-team review finds no blocker.
7. The candidate has a result summary under `stage2/results/`.

## Banned Shortcuts

1. No benchmark-pair memorization as solver policy.
2. No hidden dependency on local files outside the submitted `solver.py`.
3. No hidden dependency on local API keys or environment variables.
4. No proof template promotion without accepted Lean evidence.
5. No changing official reference config and calling the result official.

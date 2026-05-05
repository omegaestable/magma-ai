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

Run inside WSL 2, Linux, or macOS:

```bash
cd vendor/stage2-official
bash scripts/setup.sh
source .env.judge
python3 scripts/run_harness.py
python3 scripts/run_marathon_harness.py
```

Do not diagnose local solver performance until the official harness is green.

Native Windows is useful for Python-only smoke tests, but it is not currently a faithful official harness environment here: Lean/Lake/elan/bash/docker are absent, WSL has no installed distro, and the Marathon runner uses POSIX process groups. Prefer WSL 2 or Linux/macOS for judge evidence.

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

## Marathon Loop

Use Marathon for competition-relevant triage and budget behavior.

1. Read the manifest once.
2. Rank problems by deterministic solve probability and expected token cost.
3. Submit deterministic certificates first.
4. Spend LLM budget only on unresolved high-value cases.
5. Respect append-only JSONL output and last-write-wins semantics.
6. Track tokens, wall-clock, accepted count, and failure class.

## Certificate Distillation

For each failed certificate attempt, record:

1. problem id, equation ids, and verdict attempted
2. generated Lean code hash or path
3. judge status
4. relevant stderr excerpt
5. expected proof family or witness family
6. root cause: syntax, type mismatch, dependency policy, bad witness, bad proof idea, timeout, or unsupported import

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

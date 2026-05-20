# Playground Preflight

Updated: 2026-05-20

Use this checklist before trying the packaged solver in the official Stage 2 playground or calling a local candidate playground-ready.

## Contract

The playground-facing artifact is the generated single file:

```text
stage2/submissions/solver.py
```

It must satisfy the official submission contract:

1. The submission directory contains exactly one file named `solver.py`.
2. `solver.py` is below the 500 KB limit.
3. The solver uses no repo-local imports and does not read repo-local caches.
4. The solver does not require local secrets or direct network access.
5. Judge answers contain exactly `verdict` and `code`; route labels stay in stderr and result summaries.
6. LLM escalation goes only through the official Solo or Marathon proxy.
7. Unsolved Solo runs make a final schema-valid judge call before exiting, so the playground can distinguish a clean miss from a solver crash. Do not emit verdict-less terminal markers such as `{"call":"done"}`; the playground can reject them as malformed verdict payloads.
8. The broad `grind` TRUE fallback is not an active solver route. Historical grind ledgers remain discovery evidence only.

Current packaged state from the latest local package pass: `71662` bytes, with `stage2/submissions/` containing only `solver.py`.

## Proxy Reality

Local no-key failures are not, by themselves, solver protocol failures.

In Solo mode, the solver sends:

```json
{"call":"llm","context":{"round":"0","analysis":"..."}}
```

The official proxy extracts the top-level `PROMPT` constant from `solver.py`, fills the prompt placeholders, calls the model, and returns a response. The solver never sees real API keys.

In Marathon mode, the runner injects `JUDGE_MARATHON_LIB_DIR`; the solver imports `marathon_llm` from that directory and calls `marathon_llm.call_llm` only when a token budget is available.

Zero-token Marathon runs prove only deterministic append-only behavior. They do
not exercise the LLM proxy path and must not be cited as evidence for an LLM
strategy. Positive-token LLM evidence must show both `llm_calls > 0` from the
solver stderr summary and `tokens_used > 0` from the official Marathon summary.

On a local machine, the proxy still needs one upstream key in the runner environment, usually `OPENAI_API_KEY` or `OPENROUTER_API_KEY`. If neither is set, unresolved cases can fail with:

```text
OPENAI_API_KEY or OPENROUTER_API_KEY not set
```

That means local LLM plumbing reached the proxy, but the local upstream credential was absent. In a playground that provides the organizer proxy, the submitted solver does not need its own key. If a playground disables LLM access, deterministic certificates still work and unresolved TRUE cases remain unsolved.

## Local OpenRouter Setup

Do not put real upstream keys in `solver.py`, result summaries, repository docs,
or ad hoc shell commands that are likely to be copied into logs. To configure a
Windows homelab runner, use the secret-safe helper from the repository root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\stage2\experiments\set_openrouter_user_env.ps1
```

The helper prompts with hidden input, stores `OPENROUTER_API_KEY` in the Windows
User environment, and also sets it for the current PowerShell process. Restart
VS Code terminals before long runs. If a key was pasted into chat or logs,
rotate it first and configure the rotated value.

If terminal hidden input is unreliable, copy the rotated key to the local
Windows clipboard and use the clipboard mode instead:

```powershell
.\stage2\experiments\set_openrouter_user_env.ps1 -FromClipboard
```

This mode reads the key from the local clipboard, validates that it looks like a
full OpenRouter key, stores it in the Windows User environment, and clears the
clipboard unless `-KeepClipboard` is supplied. It prints only shape metadata,
never the key value.

Verify the local proxy path without printing the key:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\homelab_llm_probe.py --key-status
```

This reports only non-secret shape metadata. The probe reads the Windows User
environment directly if the current terminal has not inherited the key yet. For
a low-token direct OpenRouter request-shape smoke:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\homelab_llm_probe.py --run-direct-openrouter-smoke
```

Once the key is present and the solver is packaged, run a Solo LLM-path probe:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\homelab_llm_probe.py --run-solo
```

For a small positive-token Marathon proxy probe:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\homelab_llm_probe.py --run-marathon --marathon-budget-tokens 131072 --marathon-budget-seconds 600
```

For the preferred local playground-parity LLM check, use the positive-token
runner. By default it builds a small reproducible mixed fixture from the
official `normal`, `hard1`, `hard2`, and `hard3` files, runs packaging, runs the
direct OpenRouter request-shape smoke, then runs official Solo and Marathon
through the proxy. It fails closed if the submission directory is dirty, if the
local upstream key is missing, if Solo/Marathon records zero LLM usage, if
Marathon records zero tokens, or if LLM/proxy/judge failures are only visible in
logs instead of the summary.

```powershell
.\.venv\Scripts\python.exe stage2\experiments\run_playground_parity_llm.py
```

For a targeted unresolved-TRUE run, use:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\run_playground_parity_llm.py --fixture-mode unresolved-true
```

The runner defaults Marathon to at least `131072` tokens so the official
`65536` max-output setting has enough headroom. Smaller explicit budgets are
allowed for debugging, but they should fail the parity gate if they prevent real
LLM use.

For a fast transport-only smoke that avoids long hard-problem proof attempts,
use the temporary one-call proxy smoke:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\homelab_llm_probe.py --run-proxy-smoke --marathon-budget-tokens 4096 --marathon-budget-seconds 180
```

Latest local evidence for that smoke: Solo `1/1` accepted with `llm_calls=1`,
`missing_key_rows=0`, solver return code `0`, wall `5.4s`; Marathon `1/1`
accepted with `74/4096` tokens used, wall `3.0s`, and solver return code `0`.
Treat the smoke as transport evidence, not a speed benchmark.

Treat any printed key material as a failure of the local procedure; the expected
diagnostic output contains only booleans, counts, ids, statuses, and paths.

## Required Local Check

Run from the repository root in PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
$env:PYTHONUTF8='1'
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
.\.venv\Scripts\python.exe -m py_compile stage2\solver\solver.py stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe theory\tools\smoke_problem_sets.py
.\stage2\solver\package_solver.ps1
Get-ChildItem -Force stage2\submissions
(Get-Item stage2\submissions\solver.py).Length
```

Keep the package command after Python syntax/smoke commands. Running
`py_compile`, `compileall`, or tests against the generated submission path can
create `__pycache__`, and the official runner rejects extra submission entries.

Then run official smokes from `vendor/stage2-official/`:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
$env:PYTHONUTF8='1'
Push-Location vendor\stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_20.json --output ..\..\tmp_stage2_smoke\sample20_playground_preflight.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_200.json --output ..\..\tmp_stage2_smoke\sample200_playground_preflight.json
Pop-Location
```

Use explicit Solo output paths when recording smoke evidence. The runner's
default `pipeline/results/submissions.json` is easy to confuse with earlier
local smoke rows. Zero-token Marathon remains useful as an optional deterministic
regression check, but it is no longer a playground-readiness gate.

Optional focused LLM-path check when no local key is available. First create or select a tiny fixture containing a currently unresolved TRUE row from the latest hard-mix or hard-only run:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor\stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems ..\..\tmp_stage2_smoke\unresolved_true_probe.jsonl --output ..\..\tmp_stage2_smoke\unresolved_true_probe_result.json
Pop-Location
```

The old `hard3_true2.jsonl` probe is no longer a good LLM-path check because `hard3_0002` is now accepted deterministically by `true:absorption_closure`. For LLM-path testing, use a currently unresolved TRUE fixture from the latest hard-mix or hard-only run. Expected local no-key behavior is still: the row reaches the LLM proxy, reports `OPENAI_API_KEY or OPENROUTER_API_KEY not set`, then makes a final fallback judge call with a valid `verdict` and `code`. A rejected fallback certificate is a clean miss, not a protocol collapse.

## Ready Criteria

A candidate is playground-ready when:

1. `stage2/submissions/` contains only `solver.py`.
2. The packaged size is below 500 KB.
3. Syntax and local DSL smokes pass.
4. Official Solo samples run under the vendored runner.
5. Positive-token playground parity has been run through the official proxy path, with `llm_calls > 0`, Marathon `tokens_used > 0`, and no missing-key/protocol errors.
6. Any LLM failure is classified as local missing-key setup, proxy/upstream breakage, token-budget exhaustion, malformed LLM output, or judge rejection in the parity summary.
7. Unsolved Solo paths make a final schema-valid judge call instead of silently exiting or emitting verdict-less terminal markers.
8. Public benchmark totals are not updated from smoke-only evidence.

For the current solver, deterministic regression and LLM readiness are separate
lanes. A candidate is not playground-ready until the positive-token parity
runner, or an equivalent official-runner command, proves nonzero proxy usage and
classifies all failures.

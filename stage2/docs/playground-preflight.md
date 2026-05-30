# Playground Preflight

Updated: 2026-05-30

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

Current packaged state from the latest local package pass: `138939` bytes, with `stage2/submissions/` containing only `solver.py`.

Current TRUE boundary rails:

- Preferred TRUE LLM outputs remain solver-owned `rewrite_chain` or `guided_chain` JSON.
- Marathon TRUE LLM submissions must be solver-checked chains; raw TRUE Lean is disabled for that lane.
- Raw TRUE fallback, where used in Solo/debug tooling, must use `code` containing a complete Lean file that exposes `submission`.
- Helper theorems, defs, lemmas, namespaces, and notation above `submission` are allowed in that raw-file rail.
- Legacy body-only `proof` / `proof_body` JSON is intentionally unsupported locally and should be treated as stale prompt drift, including the older example still present in the vendored `vendor/stage2-official/README.md`.

## Proxy Reality

Local no-key failures are not, by themselves, solver protocol failures.

In Solo mode, the solver sends:

```json
{"call":"llm","context":{"round":"0","analysis":"..."}}
```

The official proxy extracts the top-level `PROMPT` constant from `solver.py`, fills the prompt placeholders, calls the model, and returns a response. The solver never sees real API keys.

In Marathon mode, the runner injects `JUDGE_MARATHON_LIB_DIR`; the solver imports `marathon_llm` from that directory and calls `marathon_llm.call_llm` only when a token budget is available.

Marathon runs with `--budget-tokens 0` are banned as active validation in this
repo. Use positive-token official runs and record both `llm_calls` from the
solver stderr summary and `tokens_used` from the official Marathon summary.

On a local machine, the proxy still needs one upstream key in the runner environment, usually `OPENAI_API_KEY` or `OPENROUTER_API_KEY`. The repo-owned probe and parity entrypoints populate that runner environment from process env first, then the ignored root `.env`, then legacy Windows User env fallback. If neither source is configured, unresolved cases can fail with:

```text
OPENAI_API_KEY or OPENROUTER_API_KEY not set
```

That means local LLM plumbing reached the proxy, but the local upstream credential was absent. In a playground that provides the organizer proxy, the submitted solver does not need its own key. If a playground disables LLM access, deterministic certificates still work and unresolved TRUE cases remain unsolved.

## Local OpenRouter Setup

Do not put real upstream keys in `solver.py`, result summaries, repository docs,
or ad hoc shell commands that are likely to be copied into logs. For standard
local Stage 2 runs, use the repo-local helper from the repository root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\stage2\experiments\set_openrouter_repo_env.ps1
```

The helper prompts with hidden input, writes `OPENROUTER_API_KEY` to the ignored
root `.env`, and also sets it for the current PowerShell process. Repo-owned
Stage 2 LLM entrypoints load process env first, then `.env`, then legacy
Windows User env fallback. If a key was pasted into chat or logs, rotate it
first and configure the rotated value.

If terminal hidden input is unreliable, copy the rotated key to the local
Windows clipboard and use the clipboard mode instead:

```powershell
.\stage2\experiments\set_openrouter_repo_env.ps1 -FromClipboard
```

This mode reads the key from the local clipboard, validates that it looks like a
full OpenRouter key, stores it in the ignored root `.env`, and clears the
clipboard unless `-KeepClipboard` is supplied. It prints only shape metadata,
never the key value.

The legacy Windows User environment helper,
`stage2/experiments/set_openrouter_user_env.ps1`, still exists for machine-wide
storage, but it is no longer the standard repo path.

Verify the local proxy path without printing the key:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\homelab_llm_probe.py --key-status
```

This reports only non-secret shape metadata, including whether the key came
from `process_env`, `repo_env`, or `windows_user_env`. The probe and parity
runner read the ignored root `.env` directly, so new VS Code terminals do not
need to inherit the key first. For a low-token direct OpenRouter request-shape
smoke:

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

For the default wide public hard-set check, use the playground-equivalent
public sweep helper. It packages the single-file submission, runs the official
public `hard1`, `hard2`, and `hard3` manifests through the Marathon proxy, uses
the published evaluation-setup reference budgets (`3600` seconds and `65536`
tokens per problem, scaled by compression ratio), requires nonzero LLM usage,
and writes combined gap-analysis summaries under `tmp_stage2_smoke/`.

```powershell
.\.venv\Scripts\python.exe stage2\experiments\run_playground_public_sweeps.py
```

For a targeted unresolved-TRUE run, use:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\run_playground_parity_llm.py --fixture-mode unresolved-true
```

The runner defaults Marathon to at least `131072` tokens so the official
`65536` max-output setting has enough headroom. Smaller explicit budgets are
allowed for debugging, but they should fail the parity gate if they prevent real
LLM use.

The wide public sweep helper defaults to the published `0.5` compression ratio.
Override `--compression-ratio` only when intentionally simulating a different
official budget share.

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
local smoke rows. Marathon guardrails must use a positive token budget.

On machines with local upstream keys configured, blank `OPENAI_API_KEY` and
`OPENROUTER_API_KEY` for these fast deterministic Solo smokes. Otherwise
unresolved rows will make real proxy calls and the sample runs become slow
positive-token experiments. Keep positive-token LLM checks in the parity runner
or bounded proxy smoke section above.

Optional focused LLM-path check when no local key is available. First create or select a tiny fixture containing a currently unresolved TRUE row from the latest hard-mix or hard-only run:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor\stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems ..\..\tmp_stage2_smoke\unresolved_true_probe.jsonl --output ..\..\tmp_stage2_smoke\unresolved_true_probe_result.json
Pop-Location
```

The old `hard3_true2.jsonl` probe is no longer a good LLM-path check because `hard3_0002` is now accepted deterministically by `true:absorption_closure`. For LLM-path testing, use a currently unresolved TRUE fixture from the latest hard-mix or hard-only run. Expected local no-key behavior is still: the row reaches the LLM proxy, reports `OPENAI_API_KEY or OPENROUTER_API_KEY not set`, then makes a final fallback judge call with a valid `verdict` and `code`. A rejected fallback certificate is a clean miss, not a protocol collapse.

When reproducing pasted public/evaluation rows, keep the result as a fixture or handoff note. Do not add benchmark-id-specific solver policy; extract a reusable proof template, finite witness family, or LLM-quality fix.

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

Latest local note: the 2026-05-20 positive-token parity probe proved proxy
transport with Solo `llm_calls=2`, Marathon `llm_calls=1`, and Marathon
`tokens_used=7208`, but it is not promotion-clean because the unresolved TRUE
row failed by judge rejection / rejected LLM output.

Latest positive-token guardrail note: on 2026-05-30, official Marathon
`normal_100` with Lean on PATH accepted `75/100`, left `25` unresolved before
judge submission, used `47419` tokens, and made no incorrect submissions. A
targeted TRUE red-flag run accepted `2/13`, used `22764` tokens, and rejected
the remaining LLM proposals locally. The resumed mixed-lane `hard1` run
accepted `39/69`, used `240164` tokens across `30` LLM calls, and made no
incorrect submissions.

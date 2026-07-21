# magma-ai

Stage 2 lab for the SAIR Mathematics Distillation Challenge on equational theories.

The Stage 1 prompt-cheatsheet work is archived under `stage1/`. This top-level workspace is now for building a single-file Python solver that emits Lean 4 proof certificates for Stage 2.

## Mission

Build a competition-ready `solver.py` for Stage 2, with a Marathon-first architecture and Solo compatibility.

The solver must decide implications between magma equations by producing certificates accepted by the official Lean judge:

1. TRUE: a Lean proof that the hypothesis equation implies the goal equation.
2. FALSE: a Lean proof of a finite magma satisfying the hypothesis but not the goal.

The submission artifact is one Python file, `solver.py`, with a size limit of 500 KB.

## Current Direction

- Stage 2 officially started: May 1, 2026.
- Deadline: August 31, 2026, 23:59 AoE.
- Strategy: Marathon-first solver with shared Solo/Marathon core.
- Official harness: vendored at `vendor/stage2-official/`.
- Official harness snapshot: `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.
- Local solver scaffold: `stage2/solver/solver.py`.

Scoring, final model routing, and final private problem-set composition are still TBD upstream. Keep those as configuration assumptions, not hardcoded policy.

Active Marathon validation policy as of 2026-05-30: use positive token budgets
only. Do not run or cite `--budget-tokens 0` as a guardrail, promotion signal,
or default regression path.

## Start Here

Cold-start read order:

1. `README.md`
2. `CURRENT_STATE.md`
3. `AGENTS.md`
4. `.github/copilot-instructions.md`
5. `RESTART_CHECKLIST.md`
6. `EVAL_WORKFLOW.md`
7. `BENCHMARK_MANIFEST.md`
8. `stage2/README.md`
9. `stage2/docs/playground-preflight.md`
10. `theory/README.md`
11. `theory/TEORTH_WORKFLOW.md`
12. `theory/tools/README.md`
13. `stage2/docs/LATEST_HANDOFF.md`

## Current Evidence

2026-07-20: added a self-verifying LLM TRUE-proof loop (`stage2/experiments/dev_true_loop.py`: gpt-oss-120b via OpenRouter → solver chain/parse → local Lean judge → repair) and rewrote the solver `PROMPT` to be chain-primary. On a solvable TRUE set the LLM accept rate went 25% → 75%, but the deterministic-skip frontier remains hard for gpt-oss (≈0 at low reasoning); a big-budget deterministic closure cracks only 1/20. Details and the recommended hybrid next step: `stage2/results/2026-07-20-llm-true-loop-and-prompt-v3.md`.

Latest completed full public benchmark snapshot from the packaged deterministic solver, generated on 2026-05-18 before the final heartbeat/path-helper optimization patch and before the default grind rollback:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`, `llm:0`
- `normal`: `803/1000` solved, `305 TRUE + 498 FALSE`, `llm:0`
- `hard1`: `42/69` solved, `6 TRUE + 36 FALSE`, `llm:0`
- `hard2`: `92/200` solved, `16 TRUE + 76 FALSE`, `llm:0`
- `hard3`: `264/400` solved, `63 TRUE + 201 FALSE`, `llm:0`

Historical completed public total: `1201/1669` solved. This included `34` accepted `true:grind` rows; broad grind is no longer an active route after playground error-rate failures.

Latest local candidate evidence after the final optimization patch, not a replacement for the full public totals above:

- Packaged `stage2/submissions/solver.py`: `138939` bytes, single-file submission directory after the 2026-05-30 mixed-lane resume.
- May 21 prune/refactor evidence: closure-route dedupe preserved `normal_100 = 74/100` historical Marathon behavior, and selected fallback reproduction is summarized in `stage2/results/2026-05-21-prune-refactor-and-fallback-reproduction.md`.
- Official Solo `sample_20` no-key smoke: `15/20` solved on 2026-05-25.
- Official Solo `sample_200` no-key smoke: `169/200` solved on 2026-05-25.
- Recent compact named FALSE witnesses include `S4D`, `S4E`, and `S5D`.
- Accepted-grind fixture with heartbeat cap: historical discovery evidence only; the active solver no longer exposes this route.
- Compact witness fixture: `8/8` accepted, `0` LLM calls.
- Fresh 150-row hard mixes are archived deterministic discovery evidence with `91/150`, `83/150`, and `72/150` on seeds `20260516`, `20260517`, and `20260518`.
- Positive-token local proxy evidence: direct OpenRouter smokes passed; targeted parity recorded Solo `llm_calls=2`, Marathon `llm_calls=1`, and Marathon `tokens_used=7208`. Use this as transport evidence, not proof-quality promotion evidence.
- 2026-05-30 TRUE red-flag positive-token Marathon after trimming raw/grind TRUE behavior: `2/13` accepted, `11` LLM calls, `22764` tokens, and `0` incorrect submissions. The remaining rows were rejected before judge submission by solver-owned LLM validation.
- 2026-05-30 official `normal_100` positive-token Marathon guardrail with Lean on PATH: `75/100` accepted, `25` not attempted, `47419` tokens used, and no incorrect submissions.
- 2026-05-30 official `hard1` positive-token mixed-lane Marathon: `39/69` accepted, `30` not attempted, `30` LLM calls, `240164` tokens used, and no incorrect submissions. The LLM did not yet produce an accepted table or TRUE chain; rejects were malformed/prose output, unsupported guided-chain edges, bad finite tables, or proxy timeouts.
- Full public validation of the post-rollback package is pending; require positive-token official/proxy evidence before LLM-backed promotion.
- Pasted public/evaluation row lists are diagnostic fixtures. Do not hardcode ids; generalize fixes into reusable proof or witness families.

The full generated evidence lives in:

- `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`
- `stage2/results/2026-05-14-hard-affine-absorption-summary.md`
- `stage2/results/2026-05-21-prune-refactor-and-fallback-reproduction.md`
- `stage2/results/2026-05-17-hard-mix-witness-summary.md`
- `stage2/results/2026-05-17-homelab-openrouter-proxy-smoke.md`
- `stage2/results/2026-05-20-optimization-readiness.md`
- `stage2/results/2026-05-30-positive-token-mixed-lane-resume.md`
- `stage2/results/2026-05-12-public-finite-countermodels-summary.md`
- `stage2/results/2026-05-12-public-failure-ledger.jsonl`
- `stage2/results/2026-05-12-competition-preflight.md`
- `stage2/results/2026-05-25-cleanup-and-smoke.md`

For upload/playground readiness, use `stage2/docs/playground-preflight.md`. It keeps the single-file packaging contract, proxy-mediated LLM behavior, local no-key caveat, failure classification, and positive-token parity runner in one place.

Most important current lesson: the compact witness patch further reduced sampled FALSE misses, broad grind failed playground error discipline, and the hard frontier is even more TRUE-heavy. Canonical full public gap counts stay at the 2026-05-12 values until `normal|hard1|hard2|hard3` are refreshed together.

For route review, start from `stage2/docs/solver-route-ledger.md` and `stage2/docs/motif-cards/`. For math extraction and Teorth provenance work, start from `theory/TEORTH_WORKFLOW.md` and `theory/TEORTH_NOTES.md`; they document the cache-first path from implication graph and proof pages to solver motifs.

## Repository Layout

- `vendor/stage2-official/`: vendored official Stage 2 judge, pipeline, docs, tutorials, examples, and Lean package.
- `stage2/`: local Stage 2 solver work, submissions, docs, experiments, and results.
- `theory/`: reusable Teorth data/proof/witness tools and theory workflow notes.
- `paper/`: math papers, TeX sources, figures, and theory reading material.
- `data/exports/`: shared implication matrix and equation exports.
- `data/teorth_cache/`: shared Teorth graph, proof-page cache, and witness/provenance data.
- `stage1/`: complete Stage 1 archive, including cheatsheets, benchmark artifacts, eval scripts, old docs, and results.

## Quick Start

Create or activate the Python environment from PowerShell:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Set local LLM credentials only for local experiments. Repo-owned Stage 2 LLM
entrypoints load the ignored root `.env` before falling back to legacy Windows
User environment variables. Do not assume these exist in the official solver
subprocess.

```powershell
.\stage2\experiments\set_openrouter_repo_env.ps1
```

Use `-FromClipboard` if hidden terminal input is unreliable.

Official Lean setup should run inside WSL 2 or Linux/macOS:

```bash
cd /mnt/c/Users/nacho/Documents/GitHub/magma-ai/vendor/stage2-official
bash scripts/setup.sh
source .env.judge
python3 scripts/run_harness.py
python3 scripts/run_marathon_harness.py
```

Run the official demo solver after setup:

```bash
python3 -m pipeline.runner \
  --submission examples/solo/demos/baseline \
  --problems examples/problems/sample_20.json
```

Package the local scaffold from PowerShell:

```powershell
.\stage2\solver\package_solver.ps1
```

## Development Loop

1. Improve deterministic certificate generation first.
2. Validate generated Lean certificates with the official judge.
3. Use positive-token playground parity as the active local LLM gate; do not run `--budget-tokens 0` Marathon sweeps as validation.
4. Run Solo samples for quick proof debugging.
5. Run Marathon samples for budget, triage, cache, and append-only output behavior.
6. Regenerate `stage2/results/` summaries and preflight notes after meaningful solver changes.
7. Red-team every candidate before calling it a champion.

## Stage 1 Archive

Stage 1 ended with a prompt-cheatsheet system and the active candidate `v28d`. The historical code and results are under `stage1/`; they are reference material only. Do not start new Stage 2 work by editing archived cheatsheets or running Stage 1 gates.

## Useful External Resources

- Stage 2 competition overview: https://competition.sair.foundation/competitions/mathematics-distillation-challenge-equational-theories-stage2/overview
- Stage 2 evaluation setup: https://competition.sair.foundation/competitions/mathematics-distillation-challenge-equational-theories-stage2/evaluation-setup
- Official Stage 2 repository: https://github.com/SAIRcompetition/equational-theories-lean-stage2
- Teorth Equational Theories Project: https://teorth.github.io/equational_theories/
- Teorth implication explorer: https://teorth.github.io/equational_theories/implications/

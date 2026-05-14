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

Canonical full public benchmark snapshot from the packaged deterministic solver, generated on 2026-05-12:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`, `llm:0`
- `normal`: `743/1000` solved, `245 TRUE + 498 FALSE`, `llm:0`
- `hard1`: `17/69` solved, all `FALSE`, `llm:0`
- `hard2`: `52/200` solved, all `FALSE`, `llm:0`
- `hard3`: `186/400` solved, `3 TRUE + 183 FALSE`, `llm:0`

Current public total: `998/1669` solved.

Latest local candidate evidence from 2026-05-14, not a replacement for the full public totals above:

- Packaged `stage2/submissions/solver.py`: `60614` bytes, single-file submission directory.
- Official Solo `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`.
- Official Solo `sample_200`: `165/200` solved after the `Fin 7` recursion-depth fix and `S4A`/`S5A` named witnesses; the remaining `35` sample misses are all TRUE cases.
- Official Marathon `examples/problems/marathon/normal_100.jsonl` with zero token budget: `70/100` accepted, `0` tokens.
- 150-row mixed hard slice, seed `20260514`: `73/150` accepted, up from `68/150`, with no regressions. New wins were 2 TRUE `true:absorption_closure` certificates plus 3 expanded affine/linear FALSE witnesses.
- Hard-only official reruns after the affine/absorption patch: `hard1 = 24/69`, `hard2 = 64/200`, `hard3 = 211/400`, with no regressions versus the 2026-05-12 hard artifacts.

The full generated evidence lives in:

- `stage2/results/2026-05-14-hard-affine-absorption-summary.md`
- `stage2/results/2026-05-12-public-finite-countermodels-summary.md`
- `stage2/results/2026-05-12-public-failure-ledger.jsonl`
- `stage2/results/2026-05-12-competition-preflight.md`

For upload/playground readiness, use `stage2/docs/playground-preflight.md`. It keeps the single-file packaging contract, proxy-mediated LLM behavior, local no-key caveat, and smoke/full-benchmark evidence boundary in one place.

Most important current lesson: the solver is no longer false-only, but the hard frontier is still dominated by TRUE templates. The latest hard-only rerun leaves `292` TRUE misses versus `78` FALSE misses; canonical full public gap counts stay at the 2026-05-12 values until `normal|hard1|hard2|hard3` are refreshed together.

For math extraction and Teorth provenance work, start from `theory/TEORTH_WORKFLOW.md`; it documents the cache-first path from implication graph and proof pages to solver motifs.

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

Set local LLM credentials only for local experiments. Do not assume these exist in the official solver subprocess.

```powershell
Copy-Item .env.example .env
```

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
3. Add LLM calls only when deterministic methods leave useful budget gaps.
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

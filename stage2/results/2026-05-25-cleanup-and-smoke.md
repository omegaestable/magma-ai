# 2026-05-25 Cleanup And Smoke Pass

This note records the repository usability pass requested on 2026-05-25. Raw runner outputs remain under `tmp_stage2_smoke/`; this file is the durable summary.

## Cleanup

- Removed generated repo-side `__pycache__` directories from `stage2/solver`, `stage2/experiments`, `theory/tools`, `vendor/stage2-official/{judge,pipeline,scripts}`, and archived Stage 1 helper paths.
- Left `.venv/` bytecode caches in place because `.venv/` is ignored local environment state.
- Removed tracked LaTeX build outputs (`.aux`, `.bbl`, `.blg`, `.fdb_latexmk`, `.fls`, `.out`, `.synctex.gz`, `.toc`) from `paper/` and archived Stage 1 paper paths; source TeX, PDFs, figures, and bibliography files remain.
- Left `tmp_stage2_smoke/` raw outputs in place because current docs use it as scratch/evidence staging. New durable results should be summarized under `stage2/results/`.

## Packaging

- Command: `.\stage2\solver\package_solver.ps1`
- Packaged artifact: `stage2/submissions/solver.py`
- Packaged size: `116670` bytes
- Submission directory audit via `rg --files --hidden --no-ignore stage2/submissions`: only `solver.py`

## Fast Local Checks

- `py_compile` for `stage2/solver/solver.py` and `stage2/experiments/smoke_llm_dsl.py`: passed.
- `stage2/experiments/smoke_llm_dsl.py`: passed (`fake_llm_dsl_smoke_ok`).
- `theory/tools/smoke_problem_sets.py`: passed HF subset checks, official mirror checks, overlap consistency, active loaders, and active module imports.

## Official Harness Checks

- `scripts/run_harness.py`: passed with Lean on PATH and no failing buckets.
- `scripts/run_marathon_harness.py`: `25` passed, `0` failed, Lean available.

## Packaged Solver Smokes

Solo runs were performed through the official runner with local upstream API keys blanked. This keeps the smoke deterministic/protocol-focused by making unresolved LLM proxy calls fail fast while still checking schema-valid fallback behavior.

- `sample_20`: `15/20` solved, `5` failed cleanly, total time `67.0s`.
- `sample_200`: `169/200` solved, `31` failed cleanly, total time `698.1s`.
- Zero-token Marathon `normal_100`: `74/100` accepted, `26` not attempted, `0` tokens, solver wall `60.6s`, no SIGTERM/SIGKILL.

Raw paths:

- `tmp_stage2_smoke/2026-05-25-cleanup-sample20-no-key.json`
- `tmp_stage2_smoke/2026-05-25-cleanup-sample200-no-key.json`
- `tmp_stage2_smoke/2026-05-25-cleanup-normal100-zero/`

## LLM Proxy Smoke

- Key-status probe: upstream key present; output showed only non-secret shape/source metadata.
- Bounded proxy smoke: Solo `1/1` solved with `llm_calls=1`; Marathon `1/1` solved with `89/4096` tokens used.

Raw paths:

- `tmp_stage2_smoke/llm_proxy_smoke_result.json`
- `tmp_stage2_smoke/llm_proxy_smoke_marathon/`

## Usability Findings

- Stale docs were the main clutter risk: several first-read docs still listed package sizes `85173` or `112696`, and older smoke counts `sample_20=14/20`, `sample_200=165/200`.
- Tracked LaTeX build outputs were also real repository clutter because `.gitignore` already marks those extensions as generated.
- Local positive-key Solo runs are slow on unresolved rows because they exercise real LLM calls. For fast deterministic smoke, blank runner `OPENAI_API_KEY` and `OPENROUTER_API_KEY`; use positive-token parity only when intentionally testing LLM readiness.
- No source-code cleanup was needed in `stage2/solver/solver.py` during this pass; the priority was integration evidence, scratch hygiene, and doc accuracy.

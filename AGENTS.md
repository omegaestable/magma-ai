# AGENTS.md

This file is the repo-wide navigation contract for coding agents.

## Mission

Build, evaluate, and promote a Stage 2 `solver.py` for SAIR Equational Theories. The solver must produce Lean 4 proof certificates accepted by the official judge.

Stage 1 prompt-cheatsheet work is archived under `stage1/` and is not the active workflow.

## Cold-Start Read Order

Follow this order exactly:

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
14. Only then inspect solver code, theory tools, or archived Stage 1 files.

## Current Operating Model

- Active artifact: `stage2/solver/solver.py`.
- Packaged output: `stage2/submissions/solver.py`.
- Official harness: `vendor/stage2-official/`.
- Official harness commit: `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.
- Strategy: Marathon-first, deterministic certificates first, LLM calls second.
- Active deterministic TRUE routes: reflexive, singleton/collapse, exact substitution, projection-boundary laws, short bridge/constancy rewrites, bounded subterm rewrite chains, bounded absorption closure, deep absorption, and bounded equational closure.
- Active deterministic FALSE routes: named compact witnesses, structured finite families, expanded linear/affine families, bounded quadratic families, dualized witnesses, and bounded `Fin 2..3` search.
- Shared data: `data/exports/`, `data/teorth_cache/`, and `paper/`.
- Stage 1 archive: `stage1/`.

Latest completed public benchmark snapshot, before the final heartbeat/path-helper optimization patch:

- `normal`: `803/1000`
- `hard1`: `42/69`
- `hard2`: `92/200`
- `hard3`: `264/400`
- total: `1201/1669`, split `390 TRUE + 811 FALSE`, with `0` solver tokens

Use `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md` and
`stage2/docs/LATEST_HANDOFF.md` as the current team-memory bridge before
starting new solver work. Use `stage2/docs/playground-preflight.md` before any
upload/playground check.

Latest local candidate evidence after the final optimization patch, not a full public rerun:

- `sample_20`: `15/20` in the 2026-05-25 no-key Solo smoke
- `sample_200`: `169/200` in the 2026-05-25 no-key Solo smoke
- Marathon `normal_100` with zero tokens: `74/100` accepted in `60.6s` on 2026-05-25
- accepted-grind fixture with heartbeat cap: `34/34` accepted only with `MAGMA_ENABLE_GRIND=1`
- compact witness fixture: `8/8` accepted, `0` LLM calls
- Fresh 150-row hard mixes with zero-token Marathon: `91/150`, `83/150`, and `72/150` on seeds `20260516`, `20260517`, and `20260518`
- Bounded local OpenRouter proxy smoke on 2026-05-25: Solo `1/1` and Marathon `1/1` accepted through official proxy paths, with Marathon `89/4096` tokens used
- Packaged solver size: `116670` bytes
- May 21 prune/refactor evidence: `_closure_route_impl` dedupe preserved `normal_100 = 74/100` zero-token Marathon behavior; selected fallback reproduction lives at `stage2/results/2026-05-21-prune-refactor-and-fallback-reproduction.md`.
- Full public validation of the post-rollback package is pending. Treat the prior `1201/1669` as historical zero-token evidence that included `34` default-disabled grind wins; require positive-token proxy evidence before LLM-backed promotion.

## Banned Approaches

1. Do not treat Stage 1 prompt accuracy as Stage 2 evidence.
2. Do not submit speculative Lean code as a solved case without judge acceptance.
3. Do not hardcode private or benchmark-specific answers as policy. Generalize row-list findings into proof/witness families or reusable fixtures; pasted ids are diagnostics, not solver policy.
4. Do not rely on network, local secrets, or repo-local imports from the submitted solver.
5. Do not import Teorth theorem names in official certificates unless upstream allowlists them.
6. Do not edit vendored official harness files casually; document any local patch.
7. Do not treat live Teorth scraping, `tmp_stage2_smoke/`, or direct `verify_answer(problem, ...)` output as promotion evidence without runner-equivalent validation.

## Canonical Workflow

1. Read the official Stage 2 docs in `vendor/stage2-official/docs/` and examples tutorials.
2. Package the local solver with `stage2/solver/package_solver.ps1`.
3. Validate syntax and size of `stage2/submissions/solver.py`.
4. Run the playground preflight checks in `stage2/docs/playground-preflight.md`.
5. Run official Solo samples for fast certificate debugging.
6. Run official Marathon samples for pacing, triage, and append-only output behavior.
7. Distill failures into certificate-template fixes, not prompt folklore.
8. For theory dives, use `theory/TEORTH_WORKFLOW.md` to move from graph/proof-page evidence to Lean motif cards.
9. Red-team candidate behavior before promotion.

Important operational lesson:

- Judge answer JSON must contain exactly `verdict` and `code`. Route labels,
  strategy annotations, and team-memory breadcrumbs belong in solver stderr,
  benchmark summaries, or handoff docs, not in the submitted answer payload.

## Primary Roles

### Harness Runner

Use when the task is official setup, runner invocation, result collection, or config drift checks.

Primary files:

- `vendor/stage2-official/`
- `EVAL_WORKFLOW.md`
- `BENCHMARK_MANIFEST.md`
- `stage2/docs/playground-preflight.md`

### Solver Engineer

Use when the task is `solver.py`, packaging, Marathon/Solo I/O, budgeting, caching, or no-secret/no-network constraints.

Primary files:

- `stage2/solver/solver.py`
- `stage2/solver/package_solver.ps1`
- `stage2/README.md`

### Lean Certificate Engineer

Use when the task is Lean proof code, judge statuses, proof dependency policy, or true-certificate templates.

Primary files:

- `vendor/stage2-official/judge/`
- `vendor/stage2-official/docs/solo_mode.md`
- `vendor/stage2-official/docs/marathon_mode.md`

### Counterexample Miner

Use when the task is finite magma search, false certificates, witness tables, or `decideFin!` proof generation.

Primary files:

- `data/teorth_cache/smallest_magma.txt`
- `data/teorth_cache/proof_page_cache/`
- `theory/tools/`

### Graph Explorer

Use when the task is Teorth implication graph navigation, random equation dives, proof provenance, shortest paths, or theory cards.

Primary files:

- `data/exports/export_raw_implications_14_3_2026.csv`
- `data/exports/equations.txt`
- `data/teorth_cache/graph.json`
- `data/teorth_cache/full_entries.json`
- `theory/TEORTH_WORKFLOW.md`
- `theory/tools/README.md`

### Red-Team Reviewer

Use before a candidate is promoted. Focus on malformed I/O, forbidden imports/tokens, budget failures, local-vs-official drift, and Lean dependency policy.

## Active Versus Archive Paths

Active starting points:

- `README.md`
- `CURRENT_STATE.md`
- `stage2/solver/solver.py`
- `vendor/stage2-official/README.md`
- `vendor/stage2-official/examples/solo/TUTORIAL.md`
- `vendor/stage2-official/examples/marathon/TUTORIAL.md`
- `theory/README.md`

Archive paths:

- `stage1/cheatsheets/`
- `stage1/eval/`
- `stage1/analysis/`
- `stage1/results/`

Do not start from archive paths unless the task explicitly asks for Stage 1 archaeology.

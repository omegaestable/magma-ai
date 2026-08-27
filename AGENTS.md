# AGENTS.md

Role playbooks and navigation for coding agents.

**Read `CLAUDE.md` first.** It holds the current measured state, the four
commands that matter, and the rails. This file adds role-specific file maps on
top of it. If the two disagree, `CLAUDE.md` wins.

## Mission

Build, evaluate, and promote a Stage 2 `solver.py` for SAIR Equational Theories. The solver must produce Lean 4 proof certificates accepted by the official judge.

Stage 1 prompt-cheatsheet work is archived under `stage1/` and is not the active workflow.

## Cold-Start Read Order

The old mandatory 13-file order cost ~36k tokens before any work could start,
and the files contradicted each other. Read on demand instead:

1. `CLAUDE.md` — always. Current numbers, commands, rails, gotchas.
2. `stage2/docs/LATEST_HANDOFF.md` — latest session detail and ranked next levers.
3. Then only what the task needs, via the "Going deeper" table in `CLAUDE.md`.

`README.md`, `CURRENT_STATE.md`, `RESTART_CHECKLIST.md`, `EVAL_WORKFLOW.md`,
`BENCHMARK_MANIFEST.md`, `stage2/README.md`, `theory/*` and
`stage2/docs/playground-preflight.md` remain accurate references for their own
topics; none is required reading to make a solver change.

## Current Operating Model

- Active artifact: `stage2/solver/solver.py`.
- Packaged output: `stage2/submissions/solver.py`.
- Official harness: `vendor/stage2-official/`.
- Official harness commit: `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.
- Strategy: Marathon-first, deterministic certificates first, LLM calls second.
- LLM lane (2026-07-20): the `PROMPT` is chain-primary — the model proposes a
  guided-chain of intermediate terms and the solver renders/verifies the Lean, since
  gpt-oss-120b is reliable at *which terms* but not at exact Lean bookkeeping. It
  forbids `simp`/`aesop`/`grind` and warns ◇ is non-associative. Every LLM candidate
  is judge-verified before it counts (Solo records the last `accepted` judge call),
  so no `incorrect` submissions. Iterate the loop with
  `stage2/experiments/dev_true_loop.py` (local judge + OpenRouter, dev-only).
- Active validation policy: Marathon guardrails and promotion runs must use a
  positive token budget; do not run or cite `--budget-tokens 0` as current
  evidence.
- Active route inventory: see `CLAUDE.md` ("How the solver is organised") and
  `stage2/docs/solver-route-ledger.md`. The list that used to sit here went stale
  and omitted every engine added after 2026-05.
- Shared data: `data/exports/`, `data/teorth_cache/`, and `paper/`.
- Stage 1 archive: `stage1/`.

### Benchmark numbers live in one place

Current measured state is in **`CLAUDE.md`** — its measured-state table, which
is the only copy; every other doc points at it. Regenerate with
`stage2/experiments/audit_corpus.py --all` (and `--hf`). Deep-sweep commands:
`stage2/docs/DEEP_SWEEP_RUNBOOK.md`.

This section used to carry `1201/1669` and a `138939`-byte package as the
"latest snapshot". Both were stale by a wide margin — the real figures on
2026-07-29 are `1617/1669` and ~333 KB — and a cold-start agent read the stale
ones first and planned against them. Historical baselines belong in
`stage2/results/` with their dates, not here.

Historical context worth keeping: the `1201/1669` figure is the 2026-05-18
public Marathon refresh and included `34` accepted `true:grind` rows against
`433` incorrect. It is archived at
`stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`. Use
`stage2/docs/LATEST_HANDOFF.md` as the team-memory bridge and
`stage2/docs/playground-preflight.md` before any upload.

## Banned Approaches

1. Do not treat Stage 1 prompt accuracy as Stage 2 evidence.
2. Do not submit speculative Lean code as a solved case without judge acceptance.
3. Do not hardcode private or benchmark-specific answers as policy. Generalize row-list findings into proof/witness families or reusable fixtures; pasted ids are diagnostics, not solver policy.
4. Do not rely on network, local secrets, or repo-local imports from the submitted solver.
5. Do not import Teorth theorem names in official certificates unless upstream allowlists them.
6. Do not edit vendored official harness files casually; document any local patch.
7. Do not treat live Teorth scraping, `tmp_stage2_smoke/`, or direct `verify_answer(problem, ...)` output as promotion evidence without runner-equivalent validation.
8. Do not use `--budget-tokens 0` Marathon runs as active validation,
   promotion evidence, or default workflow.

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

- `vendor/stage2-official/pipeline/config.json` — **read this before
  `judge/verify.py`.** Its `judge` block is what the runner passes to the judge
  (Lean timeout 300 s, code 100,000 bytes, FALSE certificate 20,000 bytes);
  `verify.py`'s `50_000` / `10_000` / `120` are the no-config fallback. Mistaking
  the second for the first cost two weeks of halved caps — `CLAUDE.md`, rail 3b,
  third instance.
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

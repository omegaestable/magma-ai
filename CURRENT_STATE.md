# Current State

This is the short-lived operational truth for the Stage 2 lab. Update it when the active solver, harness snapshot, validation evidence, or upstream rules change.

Last updated: 2026-05-18.

## Stage

- Active competition: SAIR Equational Theories Stage 2.
- Deadline: August 31, 2026, 23:59 AoE.
- Submission artifact: one `solver.py` file, <= 500 KB.
- Preferred track focus: Marathon first, with shared logic for Solo.
- Proof standard: official Lean 4 judge acceptance.

## Current Artifacts

- Official harness snapshot: `vendor/stage2-official/` at upstream commit `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.
- Active solver scaffold: `stage2/solver/solver.py`.
- Packaged submission: `stage2/submissions/solver.py`, last packaged at `70631` bytes.
- Latest compressed handoff: `stage2/docs/LATEST_HANDOFF.md`.
- Latest public refresh summary: `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`.
- Playground preflight checklist: `stage2/docs/playground-preflight.md`.
- Theory workflow and tools: `theory/TEORTH_WORKFLOW.md`, `theory/tools/README.md`.
- Shared theory/provenance data: `data/exports/` and `data/teorth_cache/`.
- Stage 1 archive: `stage1/`; do not treat it as the active workflow.

## Current Solver Capability

The active solver is deterministic-first and skips unresolved rows rather than submitting speculative certificates.

1. Handles official Marathon and Solo I/O.
2. Emits TRUE certificates for reflexive problems, singleton/collapse implications, exact substitutions, projection-boundary laws, bridge/constancy chains, bounded rewrite chains, absorption closure, deep absorption, and bounded equational closure.
3. Uses a last-resort `true:grind` certificate for short absorption/congruence-shaped TRUE candidates. The emitted proof is heartbeat-capped with `set_option maxHeartbeats 10 in` to reduce failed Lean proof cost.
4. Searches FALSE finite witnesses via named compact tables, structured families, affine/linear families, quadratic families, dualized witnesses, and bounded `Fin 2..3` enumeration.
5. Current named witness set includes the recent `S4D`, `S4E`, and `S5D` additions.
6. Emits FALSE certificates with `finOpTable` and `decideFin!`; larger `Fin 7+` tables use `set_option maxRecDepth 20000`.
7. Caches repeated term metadata and path/context helper work in the solver hot paths.

## Best Evidence

Latest completed public zero-token Marathon baseline, from the post-witness refresh before the final heartbeat/path-helper optimization patch:

| Set | Solved | TRUE | FALSE | Tokens |
| --- | ---: | ---: | ---: | ---: |
| `normal` | `803/1000` | 305 | 498 | 0 |
| `hard1` | `42/69` | 6 | 36 | 0 |
| `hard2` | `92/200` | 16 | 76 | 0 |
| `hard3` | `264/400` | 63 | 201 | 0 |
| **Total** | `1201/1669` | 390 | 811 | 0 |

Answer-kind totals for that baseline:

- `false:finite`: `811` accepted.
- `true:certificate`: `356` accepted.
- `true:grind`: `34` accepted, `433` incorrect.
- Remaining public misses by labels: `429` TRUE and `39` FALSE.

Latest local regression evidence after the final optimization patch:

- Exact grind ledgers reconcile to `34 accepted / 433 incorrect`.
- Accepted-grind fixture with heartbeat cap: `34/34` accepted.
- Compact witness fixture: `8/8` accepted.
- Official `normal_100` smoke: `76/100`, unchanged from the immediate pre-patch smoke.
- Python syntax/editor diagnostics and packaged submission syntax checks pass.

Full public no-loss validation of the optimized package is pending. Required target is at least the `1201/1669` baseline above, with no lost accepted-grind rows.

## Durable Session Outputs

- `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`
- `stage2/experiments/run_zero_token_sweeps.py`
- `stage2/experiments/analyze_zero_token_run.py`
- `stage2/experiments/extract_grind_ledger.py`
- `stage2/docs/LATEST_HANDOFF.md`

## Operational Notes

1. Treat `tmp_stage2_smoke/` as scratch. Promote only concise dated summaries under `stage2/results/`.
2. Do not hardcode public benchmark ids into solver policy. Grind ledgers are regression fixtures only.
3. The vendored Solo harness has local OpenRouter provider-normalization drift; this does not affect zero-token Marathon scoring, but call it out before treating harness output as upstream-clean.
4. For runner-equivalent certificate debugging, use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)`. Direct `verify_answer(problem, ...)` omits runner proof policy.
5. Judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr, summaries, or ledgers.
6. Local `OPENAI_API_KEY` or `OPENROUTER_API_KEY` errors are transport/setup issues, not submitted-solver protocol failures.

## Immediate Next Work

1. Run full public no-loss validation when time allows: `normal`, `hard1`, `hard2`, and `hard3` with zero tokens against the optimized packaged solver.
2. If the no-loss check passes, update or add a dated result summary and mark the optimized package as promotion-ready for red-team review.
3. Implement proof-producing local congruence/e-graph TRUE extraction before fallback `true:grind`; use explicit `h`, `.symm`, `.trans`, `congrArg`, and `rfl` proof terms.
4. Avoid heuristic `grind_true_candidate` tightening unless the accepted-grind fixture remains `34/34`.
5. Keep HF mirror sweeps separate from public evidence.

## Non-Goals

1. Do not edit archived Stage 1 cheatsheets as active solver work.
2. Do not promote any certificate template without official judge acceptance.
3. Do not rely on Teorth theorem imports unless the official judge allowlist explicitly permits them.
4. Do not treat local secrets, network access, or repo-local imports as available to submitted solver code.
# 2026-05-20 Optimization Readiness Pass

This pass focused on competition readiness, wall-time bottlenecks, and LLM proxy health for the active Stage 2 package.

## Package

- Source: `stage2/solver/solver.py`
- Packaged artifact: `stage2/submissions/solver.py`
- Packaged size: `76136` bytes
- Submission directory: single-file `solver.py`

## Local Preflight

Passed before and after packaging:

- `py_compile` for `stage2/solver/solver.py`, `stage2/experiments/smoke_llm_dsl.py`, and `stage2/experiments/profile_solver_routes.py`
- `stage2/experiments/smoke_llm_dsl.py`
- `theory/tools/smoke_problem_sets.py`
- `stage2/solver/package_solver.ps1`

## Bottleneck Fix

The regular `true:absorption_closure` route had no wall-time cap, unlike deep absorption and equational closure. Under the official zero-token Marathon `normal_100` smoke with a 600s wall budget, the solver was killed at the budget limit:

| Run | Score | Wall | Exit | Tokens |
| --- | ---: | ---: | --- | ---: |
| before cap | `41/100` | `600.5s` | SIGTERM / rc `3221225786` | `0` |
| after `0.75s` cap | `74/100` | `78.6s` | rc `0` | `0` |
| after `0.05s` cap | `74/100` | `56.6s` | rc `0` | `0` |

The active cap after this pass is `ABSORPTION_TIME_BUDGET = 0.05`.

## Route Profiling

Added `stage2/experiments/profile_solver_routes.py` to time deterministic solver routes without calling the official judge or LLM.

Profile evidence with the `0.05s` absorption cap:

| Manifest | Candidates | Skips | Solver wall | Notes |
| --- | ---: | ---: | ---: | --- |
| `examples/problems/marathon/normal_100.jsonl` | `74` | `26` | `51.0s` | same candidate count as wider caps, much faster |
| `examples/problems/sample_200.json` | `169` | `31` | `62.2s` | local deterministic candidates only, not judge-scored |

The broader sample profile is not a replacement for an official `sample_200` runner result, but it is useful speed evidence and currently exceeds the last recorded `165/200` sample note.

## LLM Proxy Evidence

Positive-token playground parity was run on two unresolved TRUE rows from the hard-mix frontier.

| Lane | Result | LLM calls | Tokens | Main outcome |
| --- | ---: | ---: | ---: | --- |
| Direct OpenRouter smoke | OK | 3 request shapes | `87`, `74`, `74` total-token reports | transport/config works |
| Solo proxy | `1/2` | `2` | runner-local | `hard3_0140` deterministic accepted; `hard3_0114` fallback judge rejection |
| Marathon proxy | `1/2` | `1` | `7208/131072` | LLM response rejected as `no_json_object` |

Conclusion: LLM transport is working locally through the official proxy paths, but the positive-token parity gate is not promotion-clean because unresolved TRUE proof quality still fails by judge rejection or solver rejection.

## Current Readiness

- Deterministic package is much faster on the `normal_100` smoke and no longer exhausts the 600s wall budget.
- Package cleanliness and size are good.
- LLM calls work through the proxy, with nonzero Solo calls and nonzero Marathon token use.
- Full public no-loss validation of the speed-capped package is still pending.
- The latest `normal_100` smoke is `74/100`, below the older historical `76/100` smoke; treat this as a speed-first candidate until broader validation decides whether the two-smoke delta matters.

## Raw Artifacts

- `stage2/results/archive/optimization-readiness-2026-05-20/2026-05-20-optimization-normal100-zero-token-absorption-50ms/`
- `stage2/results/archive/optimization-readiness-2026-05-20/2026-05-20-optimization-normal100-route-profile-absorption-50ms.json`
- `stage2/results/archive/optimization-readiness-2026-05-20/2026-05-20-optimization-sample200-route-profile-absorption-50ms.json`
- `stage2/results/archive/optimization-readiness-2026-05-20/2026-05-20-optimization-playground-parity-limit2/`
- Archive manifest: `stage2/results/archive/optimization-readiness-2026-05-20/MANIFEST.md`

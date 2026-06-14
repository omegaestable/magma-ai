# 2026-06-14 Solver Hardening And Focused Fixture

## Scope

Implemented the first hardening slice from the focused improvement plan:

- Marathon LLM TRUE candidates now reject raw Lean by default.
- Solo fallback still exists for debugging, but logs as `fallback:unsolved_exact_h`.
- Added a focused fixture for the pasted red-flag rows.
- Added local secret scanning and wired it into the playground parity preflight path.
- Added focused deterministic profiling, finite-countermodel mining, and Teorth edge tracing helpers.

The pasted OpenRouter key was treated as compromised and was not used.

## Focused Fixture

Fixture: `stage2/fixtures/focused_failure_rows_2026-06-14.jsonl`

Rows:

- TRUE gaps: `normal_0422`, `normal_0457`, `normal_0480`, `normal_0749`, `normal_0750`,
  `evaluation_normal_0028`, `evaluation_normal_0132`, `evaluation_normal_0194`,
  `hard2_0131`, `hard2_0136`, `hard2_0154`, `hard2_0155`, `hard2_0159`,
  `hard2_0189`, `hard2_0198`
- FALSE gap: `hard2_0165`
- Regression FALSE rows: `normal_0434`, `normal_0443`

Deterministic profile after the patch:

```json
{"rows":18,"routes":{"false:witness:LP":1,"false:witness:RP":1,"unresolved":16},"verdicts":{"false":2,"none":16}}
```

The regression rows remain deterministic FALSE:

- `normal_0434`: `false:witness:RP`
- `normal_0443`: `false:witness:LP`

## Mining Notes

`hard2_0165` Z3 finite-countermodel search:

- `n = 2..5`, timeout 30s each: no model found.
- `n = 6`, timeout 90s: no model found before timeout/unknown.

Teorth cached graph/provenance:

- All listed TRUE gaps are `implicit_proof_true`.
- `hard2_0165` is `implicit_proof_false`.
- No direct proof-page source was attached for these rows.
- `normal_0422` has explicit outgoing edge `Equation2170_implies_Equation711`, but no explicit path to `Equation4640` up to depth 8 in cached explicit entries.
- `hard2_0165` has explicit outgoing edges to `Equation2043`, `Equation2088`, and `Equation898`, but no explicit path to `Equation692` up to depth 8.

## Validation

Passed:

- `py_compile` on the solver and touched experiment/preflight helpers.
- `stage2/experiments/secret_scan.py --include-untracked`
- `stage2/experiments/smoke_llm_dsl.py`
- `stage2/solver/package_solver.ps1`
- `py_compile stage2/submissions/solver.py`

Packaged solver size:

```text
195764 bytes
```

Focused Marathon wrapper run:

- Manifest: `stage2/fixtures/focused_failure_rows_2026-06-14.jsonl`
- Budget: positive token budget, `4096`
- Solver submitted only the two deterministic FALSE rows and skipped 16 unresolved rows.
- Local result status was `harness_error` for the two attempted rows because this Windows environment has no `lean` binary on PATH.

The focused Marathon run therefore validates submission policy shape, not Lean acceptance.

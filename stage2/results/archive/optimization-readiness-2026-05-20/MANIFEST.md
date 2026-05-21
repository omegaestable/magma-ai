# Archive Batch 2026-05-20

Source: `tmp_stage2_smoke/2026-05-20-optimization*` and `tmp_stage2_smoke/playground_parity_llm_fixture.jsonl`

Destination: `stage2/results/archive/optimization-readiness-2026-05-20/`

Summary artifact: `stage2/results/2026-05-20-optimization-readiness.md`

Reason: optimization profiling, zero-token Marathon speed evidence, aborted Solo sample attempts, and positive-token LLM parity evidence from the 2026-05-20 competition-readiness pass.

Safe to delete later: no, keep until a newer full public no-loss validation and LLM parity summary supersede this pass.

## Archived Items

- `2026-05-20-optimization-normal100-zero-token/` — pre-cap zero-token Marathon run killed at 600s.
- `2026-05-20-optimization-normal100-zero-token-after-absorption-cap/` — official run with the initial `0.75s` absorption cap.
- `2026-05-20-optimization-normal100-zero-token-absorption-50ms/` — official run with the final `0.05s` absorption cap.
- `2026-05-20-optimization-playground-parity-limit2/` — positive-token parity probe output.
- `2026-05-20-optimization-normal100-route-profile-after-absorption-cap.json` and `.jsonl` — route profile for the initial cap.
- `2026-05-20-optimization-normal100-route-profile-absorption-1250ms.json` and `.jsonl` — cap-tuning profile.
- `2026-05-20-optimization-normal100-route-profile-absorption-250ms.json` and `.jsonl` — cap-tuning profile.
- `2026-05-20-optimization-normal100-route-profile-absorption-100ms.json` and `.jsonl` — cap-tuning profile.
- `2026-05-20-optimization-normal100-route-profile-absorption-50ms.json` and `.jsonl` — final cap profile.
- `2026-05-20-optimization-sample200-route-profile-absorption-50ms.json` and `.jsonl` — broader deterministic profile for the final cap.
- `2026-05-20-optimization-sample20.json` — aborted official Solo sample attempt with default LLM behavior.
- `2026-05-20-optimization-sample20-deterministic.json` — aborted official Solo sample attempt after trying a local env knob that the Solo proxy sanitized.
- `playground_parity_llm_fixture.jsonl` — generated unresolved TRUE parity fixture.

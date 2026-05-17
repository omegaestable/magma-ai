# Latest Handoff

Updated: 2026-05-17

This is the compressed team-memory note for the current Stage 2 solver and homelab state.

## What Changed

- Added four compact named FALSE witness tables to `stage2/solver/solver.py`: `S4B`, `S5B`, `S5C`, and `S4C`.
- Packaged `stage2/submissions/solver.py` is `68398` bytes, and `stage2/submissions/` contains only `solver.py`.
- Added secret-safe local OpenRouter helpers:
  - `stage2/experiments/set_openrouter_user_env.ps1`
  - `stage2/experiments/homelab_llm_probe.py`
- Added a bounded one-call proxy smoke for Solo and Marathon LLM transport, so local plumbing can be checked without sending hard TRUE proof prompts.
- Added local OpenRouter provider normalization in the vendored harness so `deepinfra/bf16` is sent to OpenRouter as provider `DeepInfra` plus quantization `bf16`.
- Documented that provider normalization as local harness drift in `vendor/stage2-official/UPSTREAM.md`.

## Best Public Evidence

Canonical full public benchmark evidence is still the 2026-05-12 full refresh. Do not replace these totals with smoke-only or hard-mix-only runs:

- `normal`: `743/1000` solved, `245 TRUE + 498 FALSE`, `llm:0`
- `hard1`: `17/69` solved, all `FALSE`, `llm:0`
- `hard2`: `52/200` solved, all `FALSE`, `llm:0`
- `hard3`: `186/400` solved, `3 TRUE + 183 FALSE`, `llm:0`

Public total remains `998/1669` until `normal|hard1|hard2|hard3` are refreshed together.

## Latest Local Evidence

Local runner-equivalent evidence after the May 17 witness patch:

- New witness focused fixture: `10/10` accepted, `0` LLM calls.
- Equational-closure TRUE fixture after witness patch: `26/26` accepted, `0` LLM calls.
- `sample_20`: `14/20`, unchanged.
- Fresh 150-row hard mixes with zero-token Marathon:
  - seed `20260516`: `91/150`, up by `10`
  - seed `20260517`: `83/150`, up by `5`
  - seed `20260518`: `72/150`, up by `8`
- Post-patch sampled misses are TRUE-heavy: FALSE misses fell to `4`, `11`, and `4` on the three mixes.
- Bounded OpenRouter proxy smoke:
  - Solo: `1/1` accepted, `llm_calls=1`, `missing_key_rows=0`, solver return code `0`, wall `72.4s`
  - Marathon: `1/1` accepted, `89/4096` tokens, solver return code `0`, wall `3.5s`
- Full-looking OpenRouter key pattern scan over repo text files: `0` matches.

Durable notes:

- `stage2/results/2026-05-17-hard-mix-witness-summary.md`
- `stage2/results/2026-05-17-homelab-openrouter-proxy-smoke.md`
- `stage2/docs/playground-preflight.md`

## Highest-Value Learnings

1. The new compact witnesses are low-risk deterministic FALSE improvements, but they do not change the main bottleneck.
2. The sampled hard frontier is now more TRUE-heavy. The next solver gains should come from proof-producing TRUE synthesis: target-guided closure, local theorem chaining, rewrite scripts, or congruence/completion.
3. Blindly raising closure or absorption bounds was already tried on representative TRUE misses and did not help enough to justify runtime expansion.
4. Local LLM transport is now configured and smoke-tested, but hard TRUE LLM probes are slow and should be reserved for proof-quality experiments, not plumbing checks.
5. OpenRouter provider normalization is a documented local harness patch. Treat it as local drift unless and until upstream carries equivalent behavior.

## Risks And Cautions

1. Do not update canonical public totals from the May 17 hard-mix evidence. Rerun `normal`, `hard1`, `hard2`, and `hard3` together first.
2. Do not call vendored harness behavior official-clean without noting the local provider-normalization drift.
3. The stored OpenRouter key should be rotated before long runs if any earlier key was pasted into chat or terminal logs during setup troubleshooting.
4. Positive-token hard TRUE LLM probes can spend minutes per row. Use `homelab_llm_probe.py --run-proxy-smoke` for transport checks.
5. `tmp_stage2_smoke/` remains scratch space. Promote only date-stamped summaries under `stage2/results/` into team memory.
6. The judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr and summaries.
7. Runner-equivalent certificate debugging should use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)`.

## Recommended Next Steps

1. Start TRUE synthesis work from the remaining hard TRUE misses, not more broad FALSE brute force.
2. Keep the witness patch protected with the focused `10/10` fixture and the `26/26` TRUE closure fixture.
3. Rerun `sample_20`, `sample_200`, Marathon `normal_100` with zero tokens, then a full `normal|hard1|hard2|hard3` refresh before changing public totals.
4. When validating local LLM plumbing, run:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\homelab_llm_probe.py --run-proxy-smoke --marathon-budget-tokens 4096 --marathon-budget-seconds 180
```

5. Before promotion, run the adversarial review checklist from `.github/skills/adversarial-solver-review/SKILL.md` and re-check `stage2/docs/playground-preflight.md`.
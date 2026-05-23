# 2026-05-23 Held-Out Structural Route Expansion

Purpose: continue improving Stage 2 deterministic coverage one unseen problem family at a time, without id-specific policy.

## Summary

The active solver gained six narrow TRUE certificate families in `stage2/solver/solver.py` and was repackaged to `stage2/submissions/solver.py` at `112696` bytes. Each promoted family has a focused official zero-token Marathon acceptance check.

The routes are structural matchers over equation shape, not benchmark ids:

| Route | Source shape | Main derived fact | Official check |
| --- | --- | --- | --- |
| `true:middle_self_collapse` | `r = (p * r) * q` | singleton collapse | `evaluation_hard_0004`, accepted 1/1, 0 tokens |
| `true:square_twist_comm` | `a * b = (b * b) * a` | commutativity, target modulo child swaps | `evaluation_extra_hard_0034`, accepted 1/1, 0 tokens |
| `true:front_double_self_collapse` | `r = p * (r * (r * q))` | singleton collapse | `evaluation_hard_0010`, accepted 1/1, 0 tokens |
| `true:alternating_front_self_collapse` | `r = p * (r * (p * q))` | singleton collapse via bounded closure-derived `hall` | `evaluation_hard_0026`, accepted 1/1, 0 tokens |
| `true:mirrored_alternating_front_self_collapse` | `r = p * (r * (q * p))` | middle-self collapse, then singleton | `evaluation_hard_0052`, accepted 1/1, 0 tokens |
| `true:sandwich_left_projection` | `r = r * (p * (q * p))` | left projection `forall a b, a = a * b` | `evaluation_hard_0070`, accepted 1/1, 0 tokens |

## Local Profiles

Held-out hard first 80:

- Before May 23 route expansion: skipped rows included `evaluation_hard_0004`, `0010`, `0026`, `0052`, `0070`, plus later misses.
- After `mirrored_alternating_front_self_collapse`: `75` candidates, `5` skips.
- After `sandwich_left_projection`: `76` candidates, `4` skips in `7.854s`.
- Remaining hard80 TRUE skips: `evaluation_hard_0072`, `evaluation_hard_0074`, `evaluation_hard_0078`, `evaluation_hard_0080`.

Held-out extra-hard:

- First 40 after square-twist: `40` candidates, `0` skips; route `true:square_twist_comm` triggered 3 times.
- First 80: `80` candidates, `0` skips.
- First 120: `120` candidates, `0` skips.
- First 200: `161` candidates, `39` skips.

Public normal guardrail:

- After square-twist/front-double/alternating/mirrored routes: stayed at `74` candidates, `26` skips.
- After `sandwich_left_projection`: stayed at `74` candidates, `26` skips in `47.479s`.

## Scratch Evidence

Focused manifests and official run dirs:

- `tmp_stage2_smoke/2026-05-23-evaluation-hard-0004.jsonl`
- `tmp_stage2_smoke/2026-05-23-evaluation-hard-0004-zero/`
- `tmp_stage2_smoke/2026-05-23-evaluation-extra-hard-0034.jsonl`
- `tmp_stage2_smoke/2026-05-23-evaluation-extra-hard-0034-zero/`
- `tmp_stage2_smoke/2026-05-23-evaluation-hard-0010.jsonl`
- `tmp_stage2_smoke/2026-05-23-evaluation-hard-0010-zero/`
- `tmp_stage2_smoke/2026-05-23-evaluation-hard-0026.jsonl`
- `tmp_stage2_smoke/2026-05-23-evaluation-hard-0026-zero/`
- `tmp_stage2_smoke/2026-05-23-evaluation-hard-0052.jsonl`
- `tmp_stage2_smoke/2026-05-23-evaluation-hard-0052-zero/`
- `tmp_stage2_smoke/2026-05-23-evaluation-hard-0070.jsonl`
- `tmp_stage2_smoke/2026-05-23-evaluation-hard-0070-zero/`

Profiles:

- `tmp_stage2_smoke/2026-05-23-eval-hard80-after-sandwich-left-projection-profile.json`
- `tmp_stage2_smoke/2026-05-23-eval-hard80-after-sandwich-left-projection-profile.jsonl`
- `tmp_stage2_smoke/2026-05-23-public-normal100-after-sandwich-left-projection-profile.json`
- `tmp_stage2_smoke/2026-05-23-public-normal100-after-sandwich-left-projection-profile.jsonl`
- `tmp_stage2_smoke/2026-05-23-eval-extra-hard200-after-square-twist-profile.json`
- `tmp_stage2_smoke/2026-05-23-eval-extra-hard200-after-square-twist-profile.jsonl`

## Notes For Continuation

- Do not widen these matchers without a standalone Lean proof and official zero-token evidence.
- Teorth/provenance graph paths are useful for motifs, but submitted certificates are local Lean proofs and must not call Teorth theorem names.
- For the next hard80 pass, start at `evaluation_hard_0072`: `eq1_id=86`, `eq2_id=1009`, answer true.
- For extra-hard continuation, first 120 rows are clean; inspect skips after row 120 from `tmp_stage2_smoke/2026-05-23-eval-extra-hard200-after-square-twist-profile.jsonl`.
- Keep `ABSORPTION_TIME_BUDGET = 0.05`; public `normal_100` remains the quick regression guardrail.

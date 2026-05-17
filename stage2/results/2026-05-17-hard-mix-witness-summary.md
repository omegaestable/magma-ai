# 2026-05-17 Hard-Mix Witness Summary

This is local runner-equivalent evidence for the compact witness patch. It is not a
canonical full public refresh because `normal` and `sample_200` were not rerun after the
patch.

## Solver Patch

- Added four named finite witness tables to `WITNESS_TABLES`: `S4B`, `S5B`, `S5C`, and
  `S4C`.
- The tables were mined from repeated hard-mix FALSE misses with local Z3 finite-model
  search, then selected by public false-row coverage rather than single-row fit.
- Focused candidate coverage before editing:
  - Z3 found compact witnesses for `25/30` unique FALSE misses from three fresh hard
    samples.
  - The selected four tables covered `11/30` of those unique misses.
  - Public false-row coverage, before accounting for overlap with existing routes:
    `S4B`: `78`, `S5B`: `52`, `S5C`: `46`, `S4C`: `32`.
- Packaged solver size after patch: `68398` bytes.

## Focused Validation

- New witness focus fixture, `10` rows from hard-mix FALSE misses: `10/10` accepted.
- All focused wins used deterministic FALSE certificates; `0` LLM calls.
- The packaged submission directory contained only `solver.py`.

## Fresh Hard-Mix Evidence

All Marathon rows below used the official runner with `--budget-tokens 0` and
`compression_ratio=0.5`. Accepted rows were judge-verified; unattempted rows were silent
deterministic misses.

| Fixture | Before | After | Delta | Accepted TRUE | Accepted FALSE | FALSE misses after | Wall after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| seed `20260516` | `81/150` Solo accepted | `91/150` Marathon | `+10` | `13` | `78` | `4` | `115.7s` |
| seed `20260517` | `78/150` Marathon | `83/150` Marathon | `+5` | `17` | `66` | `11` | `122.1s` |
| seed `20260518` | `64/150` Marathon | `72/150` Marathon | `+8` | `11` | `61` | `4` | `139.1s` |

Post-patch status on all three Marathon runs: only `accepted` and `not_attempted`; no
`incorrect`, `malformed`, or incomplete certificates. Token use was `0/0` on every run.

The selected witnesses can preempt older FALSE routes, so route counts are not equal to
net new wins. The important miss reduction was:

- seed `20260516`: FALSE misses `14 -> 4`
- seed `20260517`: FALSE misses `16 -> 11`
- seed `20260518`: FALSE misses `12 -> 4`

## Regression Checks

- `py_compile` on `stage2/solver/solver.py` and `stage2/experiments/smoke_llm_dsl.py`:
  passed.
- `stage2/experiments/smoke_llm_dsl.py`: `fake_llm_dsl_smoke_ok`.
- `theory/tools/smoke_problem_sets.py`: passed HF/official mirror, overlap, loader, and
  import checks.
- Official `sample_20`: `14/20`, matching the known local no-key LLM miss shape; no
  deterministic rejection.
- Equational-closure TRUE fixture after witness patch: `26/26` accepted, `0` LLM calls,
  total time `86.0s`.

## Remaining Gap

The sampled misses are now even more TRUE-heavy. After the witness patch, FALSE misses
left in the three samples were `4`, `11`, and `4`; TRUE misses were `55`, `56`, and `74`.

The short Z3 pass did not find compact `Fin 4..6` witnesses for these sampled FALSE ids:

- `hard1_0005`
- `hard2_0012`
- `hard2_0027`
- `hard2_0165`
- `hard2_0133`

Next solver work should return to TRUE proof synthesis: theorem-chaining, target-guided
rewrites, or proof-producing congruence/completion. Blindly increasing closure bounds was
tested earlier and did not help the representative short-path TRUE misses.

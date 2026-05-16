# 2026-05-15 Deep Absorption Summary

This is local runner-equivalent evidence for the deep absorption solver patch. It is not a canonical full public refresh because `normal` was not rerun.

## Solver Patch

- Parameterized the existing absorption closure route instead of raising global shallow bounds.
- Kept the original `true:absorption_closure` pass unchanged.
- Added `true:absorption_closure:deep` after finite counterexample search fails, with:
  - depth `3`
  - pool limit `12`
  - frontier limit `260`
  - max fills `120`
  - term slack `8`
  - per-route time budget `1.25s`
- Packaged solver size: `62966` bytes.

## Focused Validation

- Focused hard TRUE fixture from the read-only sweep: `15/15` accepted.
- Same 150-row hard mix from `hard1|hard2|hard3`, seed `20260514`: `75/150`, up from `73/150`.
- Hard-mix new wins:
  - `hard2_0024`
  - `hard3_0015`
- Hard-mix regressions: none.

## Hard-Only Reruns

Compared with the 2026-05-14 hard affine/absorption artifacts:

- `hard1`: `25/69`, up from `24/69`
- `hard2`: `70/200`, up from `64/200`
- `hard3`: `219/400`, up from `211/400`
- Combined hard-only: `314/669`, up from `299/669`
- Regressions: none

New hard-only wins:

- `hard1_0003`
- `hard2_0006`
- `hard2_0019`
- `hard2_0024`
- `hard2_0035`
- `hard2_0114`
- `hard2_0126`
- `hard3_0015`
- `hard3_0067`
- `hard3_0221`
- `hard3_0257`
- `hard3_0261`
- `hard3_0326`
- `hard3_0333`
- `hard3_0336`

## Smoke Checks

- `sample_20`: `14/20`, unchanged.
- `sample_200`: `166/200`, up from `165/200`.
- Marathon `normal_100` with zero token budget: `70/100`, unchanged.

## Next Diagnosis

The deep profile is validated and still deliberately bounded. It improves TRUE coverage without known regressions, but it increases wall-clock on unresolved rows, so future expansions should use focused fixtures and explicit route budgets rather than broad bound increases.

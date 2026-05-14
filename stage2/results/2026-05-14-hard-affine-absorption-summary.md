# 2026-05-14 Hard Affine/Absorption Summary

This is local runner-equivalent evidence for the 2026-05-14 solver patch. It is not a canonical full public refresh because `normal` was not rerun after the patch.

## Solver Patch

- Expanded linear/affine FALSE search to sizes `2,3,4,5,7,8,9`.
- Kept quadratic search on the older bounded size policy.
- Added bounded TRUE route `true:absorption_closure`.
- Packaged solver size: `60614` bytes.

## Focused Validation

- Composite-affine public candidate fixture: `14/14` accepted.
- Same 150-row hard mix from `hard1|hard2|hard3`, seed `20260514`: `73/150` accepted, up from the prior `68/150`.
- Hard-mix new wins:
  - `hard3_0212`: TRUE via `true:absorption_closure`
  - `hard3_0002`: TRUE via `true:absorption_closure`
  - `hard2_0169`: FALSE via `false:linear:z8:1,5`
  - `hard1_0024`: FALSE via `false:linear:z9:3,1`
  - `hard3_0035`: FALSE via `false:affine:z4:2,1,1`
- Hard-mix regressions: none.

## Hard-Only Reruns

Compared with the 2026-05-12 hard artifacts:

- `hard1`: `24/69`, up from `17/69`
- `hard2`: `64/200`, up from `52/200`
- `hard3`: `211/400`, up from `186/400`
- Combined hard-only: `299/669`, up from `255/669`
- Regressions: none

By label after the patch:

- TRUE: `27/319`
- FALSE: `272/350`
- Remaining misses: `292` TRUE and `78` FALSE

## Smoke Checks

- `sample_20`: `14/20`, unchanged.
- `sample_200`: `165/200`, unchanged.

## Next Diagnosis

The affine patch is validated and low risk. The absorption route has accepted hard TRUE certificates, but the frontier is still TRUE-heavy. Next work should extend absorption/projection proof search with focused fixtures before updating any canonical public totals.

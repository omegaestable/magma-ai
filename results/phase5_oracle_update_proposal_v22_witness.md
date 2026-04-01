# Phase 5 Hard-Signature Oracle Proposal (v22_witness)

## Inputs Used
- Paid campaign results:
  - `results/sim_paid_hard3_seed20260401_v22_witness.json`
  - `results/sim_paid_hard3_seed20260402_v22_witness.json`
  - `results/sim_paid_normal_seed20260401_v22_witness.json`
  - `results/sim_paid_normal_seed20260402_v22_witness.json`
- Full subset risk check:
  - `data/hf_cache/normal.jsonl`
  - `data/hf_cache/hard3.jsonl`

## Observed Hard3 FALSE Miss Signatures (current `hard_sig`)
`hard_sig = e1_star_tot|e2_star_tot|len(e1)|len(e2)`

Top missed-FALSE signatures (hard3 seeds only):
- `4|4|17|17`: 20 misses
- `4|4|17|15`: 16 misses
- `4|4|15|15`: 7 misses
- `3|4|13|15`: 6 misses
- `3|4|13|17`: 3 misses

## Safety Check Against Normal TRUE
For each top signature above, normal TRUE collisions are substantial on full `normal.jsonl`:
- `4|4|17|17`: 233 TRUE collisions
- `4|4|17|15`: 132 TRUE collisions
- `4|4|15|15`: 37 TRUE collisions
- `3|4|13|15`: 10 TRUE collisions
- `3|4|13|17`: 23 TRUE collisions

Conclusion: these signatures are unsafe as deterministic FALSE oracle rules.

## Search for Compact Safe Signatures
Exhaustive mining over compact numeric feature combinations (star counts and side lengths) found:
- No multi-hit candidate with meaningful hard3 lift and acceptable normal TRUE safety.
- No candidate with >=2 hard3 FALSE support and zero collisions on both hard3 TRUE and normal TRUE under tested compact signatures.
- Only two singleton `hard_sig` values had zero normal TRUE collisions:
  - `3|3|11|11` (1 miss)
  - `3|3|13|13` (1 miss)

These singleton additions are too weak to justify oracle growth and provide negligible measurable lift.

## Proposal
- **Do not patch the hard oracle in this pass.**
- Keep current oracle starter minimal.
- Continue mining with additional hard3 unseen seeds; only add signatures that satisfy all:
  1. Repeated support across independent hard3 seeds.
  2. Zero normal TRUE collisions on unseen normal gates before merge.
  3. Compact representation compatible with 10KB cap.

## Promotion Impact
Because no safe compact oracle expansion is currently justified, hard3 FALSE lift is blocked on additional mining rather than patching now.

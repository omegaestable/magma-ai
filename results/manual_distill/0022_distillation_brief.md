=== DISTILLATION BRIEF (randmix FN pass 0022) ===
Source run: sim_meta-llama_llama-3.3-70b-instruct_normal_balanced20_true10_false10_randmix_seed20260324_unseen_20260324_v19_noncollapse_20260324_124647.json

Targeted failures: 9 false negatives

Top reusable TRUE-side patterns:
  [1] fn_xtarget_xtarget_invalid_c0 (n=9)
      All 9 false negatives were x = T -> x = U implications.
      The model repeatedly forced FALSE through invalid C0 reasoning where E1 rewrote to x = 0.
      Lesson: for x = T forms, C0 is almost never a safe FALSE route unless the full rewrite of E1 is a literal identity.

  [2] fn_new_vars_not_enough_in_xtarget_family (n=8)
      In 8 of 9 false negatives, E2 introduced variables absent from E1.
      These were still TRUE.
      Lesson: new variables in E2 are not a reliable FALSE cue inside the x = T -> x = U family once projection witnesses fail.

  [3] fn_shared_left_anchor_family (n=7)
      In 7 of 9 false negatives, both RHS started with the same outer left leaf y.
      Lesson: when both equations are x = term and preserve the same left anchor, do not force FALSE without a verified witness.

  [4] fn_e2_more_x_anchored (n=5)
      Several false negatives made E2 more x-anchored than E1: starts with x, ends with x, or repeats x more heavily.
      Lesson: stronger x-anchoring in E2 is a TRUE cue in this family, not evidence for FALSE.

Candidate edit direction:
  Build a small TRUE lane only for x = T -> x = U cases.
  Keep witness verification strict.
  Demote all structural FALSE heuristics unless a named witness survives exact checking.

Representative false negatives:
  - normal_0932: x = y * ((x * x) * z)  ->  x = (((y * z) * x) * w) * y
  - normal_0063: x = ((y * (x * y)) * y) * z  ->  x = ((y * z) * x) * (z * z)
  - normal_0888: x = (y * y) * (x * (y * z))  ->  x = x * (((y * x) * z) * x)
  - normal_0549: x = (y * ((x * z) * z)) * x  ->  x = (((y * z) * w) * y) * x
  - normal_0813: x = (y * (y * x)) * (z * y)  ->  x = (((y * z) * w) * y) * u
  - normal_0561: x = y * ((z * (x * x)) * y)  ->  x = x * (y * ((y * x) * z))
  - normal_0502: x = (y * (z * z)) * w  ->  x = ((y * z) * (y * w)) * z
  - normal_0559: x = ((y * (z * z)) * y) * z  ->  x = y * ((x * (z * x)) * z)
  - normal_0757: x = y * (x * ((z * z) * w))  ->  x = (y * (x * y)) * (y * y)

Edit priority: add only the compact x-target TRUE lane; do not re-expand the global prompt.
=== END DISTILLATION BRIEF ===
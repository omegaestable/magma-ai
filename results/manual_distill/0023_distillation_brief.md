=== DISTILLATION BRIEF (randmix FP pass 0023) ===
Source run: sim_meta-llama_llama-3.3-70b-instruct_normal_balanced20_true10_false10_randmix_seed20260324_unseen_20260324_v19_hybrid_candidate2_20260324_131729.json

Targeted failures: 10 false positives

Top reusable FALSE-side patterns:
  [1] fp_mixed_shape_drift (n=5)
      One equation is x = term and the other is not, or both sides use visibly different outer equation shapes.
      The TRUE lane should not fire on this family.
      Candidate false witnesses should continue past AND/OR into asymmetric small tables before TRUE.

  [2] fp_xtarget_boundary_drift (n=5)
      Both equations are x = term, but the boundary pair drifts: one of leftmost/rightmost leaf changes.
      This was enough to defeat the current TRUE lane even when it required multiple cues.
      If the boundary pair drifts, do not use the x-target TRUE shortcut.

  [3] fp_xtarget_freshvar_or_anchor_loss (n=4+)
      Several x = term false positives either introduced fresh variables in E2 or changed x-anchoring in the wrong direction.
      These should trigger one more FALSE search pass with A2, T3L, and T3R before any TRUE fallback.

Edit direction:
  Keep the narrow TRUE lane only for genuinely stable x = term families.
  Add a blocker: no TRUE shortcut when equation shape drifts or boundary pair drifts.
  Add one compact late FALSE pass: A2, T3L, T3R on these blocked families.
=== END DISTILLATION BRIEF ===
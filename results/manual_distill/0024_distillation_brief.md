=== DISTILLATION BRIEF (candidate3 cross-seed FP pass 0024) ===
Source runs:
  - sim_meta-llama_llama-3.3-70b-instruct_normal_balanced20_true10_false10_randmix_seed20260324_unseen_20260324_v19_hybrid_candidate3_20260324_132127.json
  - sim_meta-llama_llama-3.3-70b-instruct_normal_balanced10_true5_false5_randmix_seed0_unseen_20260324_v19_hybrid_candidate3_20260324_132544.json
  - sim_meta-llama_llama-3.3-70b-instruct_normal_balanced10_true5_false5_randmix_seed1_unseen_20260324_v19_hybrid_candidate3_20260324_132612.json
  - sim_meta-llama_llama-3.3-70b-instruct_normal_balanced10_true5_false5_randmix_seed2_unseen_20260324_v19_hybrid_candidate3_20260324_132633.json

Targeted failures: 24 false positives

Top reusable lessons:
  [1] fp_illegal_true_lane_reuse (n=13)
      The model kept citing the x-target TRUE lane even when one equation was not literally of the form x = term.
      Candidate4 should explicitly forbid x-target TRUE language on any mixed-shape or non-x-target pair.

  [2] fp_xtarget_xanchor_loss (n=7)
      Many remaining x = term false positives lost x-anchoring in E2: fewer x occurrences, or E1 ended in x while E2 no longer did.
      These should be FALSE-leaning blocked families, not TRUE-lane candidates.

  [3] fp_xtarget_same_left_not_enough (n=5+)
      Shared left anchor by itself is too weak.
      The surviving stable TRUE family needs same left anchor plus either fresh variables in E2 or strictly stronger x-anchoring in E2.

Candidate edit direction:
  Forbid the x-target TRUE lane unless both equations are literally x = term.
  Add hard blockers for x-anchor loss and terminal-x loss.
  Require a stabilizer for TRUE: same left anchor plus fresh-var gain or stronger x-anchoring in E2.
=== END DISTILLATION BRIEF ===
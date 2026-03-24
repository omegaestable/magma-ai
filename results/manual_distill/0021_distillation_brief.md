=== DISTILLATION BRIEF (cycle 21) ===
Total failures: 10  |  FP=9  FN=1

Top failure patterns (most frequent first):
  [1] fp_new_variable_trap (n=6)
      FP: E2 introduces variables absent from E1 (strong FALSE signal)
      E1: x * x = x * (x * (x * x))
      E2: x = x * ((y * (y * z)) * y)
  [2] fp_rp_obstruction_missed (n=5)
      FP: RP obstruction was applicable but missed
      E1: x * x = x * (x * (x * x))
      E2: x = x * ((y * (y * z)) * y)
  [3] fn_no_projection_handle (n=1)
      FN: No LP/RP obstruction available; TRUE proof missed
      E1: x = (y * z) * ((z * z) * z)
      E2: x = y * (x * (y * (z * x)))
  [4] fp_both_projections_missed (n=1)
      FP: Both LP and RP obstructions applicable, both missed
      E1: x = x * (y * (x * (y * x)))
      E2: x = y * ((z * (y * w)) * z)

Edit priority: address the top-ranked pattern first.
=== END DISTILLATION BRIEF ===
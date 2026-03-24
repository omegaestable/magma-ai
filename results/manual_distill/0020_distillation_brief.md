=== DISTILLATION BRIEF (cycle 20) ===
Total failures: 14  |  FP=8  FN=3

Top failure patterns (most frequent first):
  [1] fp_new_variable_trap (n=4)
      FP: E2 introduces variables absent from E1 (strong FALSE signal)
      E1: x = ((y * z) * (x * z)) * y
      E2: x * y = (z * (w * y)) * z
  [2] fp_rp_obstruction_missed (n=4)
      FP: RP obstruction was applicable but missed
      E1: x * y = z * (w * y)
      E2: x = (y * ((z * w) * w)) * u
  [3] fn_no_projection_handle (n=3)
      FN: No LP/RP obstruction available; TRUE proof missed
      E1: x = y * ((z * (x * w)) * u)
      E2: x * y = (z * (x * y)) * x
  [4] fp_lp_obstruction_missed (n=1)
      FP: LP obstruction was applicable but missed
      E1: x * (y * z) = x * (z * w)
      E2: x = y * ((y * (y * z)) * x)

Edit priority: address the top-ranked pattern first.
=== END DISTILLATION BRIEF ===
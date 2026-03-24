=== DISTILLATION BRIEF (cycle 1) ===
Total failures: 17  |  FP=14  FN=3

Top failure patterns (most frequent first):
  [1] generic_fp (n=6)
      FP: No detected structural pattern
      E1: x * y = (y * y) * x
      E2: x = x * (y * ((x * x) * y))
  [2] fp_new_variable_trap (n=5)
      FP: E2 introduces variables absent from E1 (strong FALSE signal)
      E1: x * y = y * (x * (x * x))
      E2: x * y = ((z * y) * z) * x
  [3] fp_lp_obstruction_missed (n=3)
      FP: LP obstruction was applicable but missed
      E1: x = (x * x) * (y * (y * x))
      E2: x = (y * ((x * x) * y)) * x
  [4] fn_no_projection_handle (n=3)
      FN: No LP/RP obstruction available; TRUE proof missed
      E1: x = y * (((y * z) * w) * u)
      E2: x = (y * (y * x)) * y
  [5] fp_rp_obstruction_missed (n=2)
      FP: RP obstruction was applicable but missed
      E1: x * x = (y * (x * z)) * x
      E2: x * y = y * (x * x)

Edit priority: address the top-ranked pattern first.
=== END DISTILLATION BRIEF ===
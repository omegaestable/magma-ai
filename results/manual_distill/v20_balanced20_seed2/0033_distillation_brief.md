=== DISTILLATION BRIEF (cycle 33) ===
Total failures: 6  |  FP=1  FN=5

Top failure patterns (most frequent first):
  [1] fn_no_projection_handle (n=5)
      FN: No LP/RP obstruction available; TRUE proof missed
      E1: x = (y * (y * (z * y))) * z
      E2: x * y = (x * (z * y)) * x
  [2] fp_rp_obstruction_missed (n=1)
      FP: RP obstruction was applicable but missed
      E1: x = y * ((y * x) * x)
      E2: (x * y) * y = (y * x) * x

Edit priority: address the top-ranked pattern first.
=== END DISTILLATION BRIEF ===
=== DISTILLATION BRIEF (cycle 31) ===
Total failures: 9  |  FP=1  FN=8

Top failure patterns (most frequent first):
  [1] fn_no_projection_handle (n=8)
      FN: No LP/RP obstruction available; TRUE proof missed
      E1: x = (y * x) * ((z * w) * z)
      E2: x * y = (x * x) * x
  [2] fp_rp_obstruction_missed (n=1)
      FP: RP obstruction was applicable but missed
      E1: x * (x * y) = (x * z) * y
      E2: x = ((x * x) * x) * (y * z)

Edit priority: address the top-ranked pattern first.
=== END DISTILLATION BRIEF ===
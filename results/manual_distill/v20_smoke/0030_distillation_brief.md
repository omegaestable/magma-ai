=== DISTILLATION BRIEF (cycle 30) ===
Total failures: 5  |  FP=2  FN=3

Top failure patterns (most frequent first):
  [1] fn_no_projection_handle (n=3)
      FN: No LP/RP obstruction available; TRUE proof missed
      E1: x = ((y * (y * z)) * x) * y
      E2: x = (y * z) * (w * z)
  [2] fp_rp_obstruction_missed (n=2)
      FP: RP obstruction was applicable but missed
      E1: x = ((y * x) * x) * (y * x)
      E2: x = (x * y) * (y * (x * y))

Edit priority: address the top-ranked pattern first.
=== END DISTILLATION BRIEF ===
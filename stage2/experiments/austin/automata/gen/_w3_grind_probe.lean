
theorem gprobe1 (u v : M) (h : op u v = J u v) (h2 : a2 v = a2 (op u v)) : sz v = sz u + sz v + 1 := by
  grind [sz, a1_J_eq, a2_J_eq]

theorem gprobe2 (u v : M) (hd : op u v ≠ J u v) (h : a2 (a1 v) = a2 (a2 v)) (ht : tg v = 2) :
    sz (a2 (a1 v)) ≤ sz v := by
  grind [sz, sz_a1, sz_a2, sz_tg]

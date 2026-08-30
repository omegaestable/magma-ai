
theorem gsub {a b u v : M} (ha : sz a < sz v) (hb : sz b < sz v) : msr a b < msr u v :=
  msr_lt_of_max_lt (Nat.lt_of_lt_of_le (Nat.max_lt.mpr ⟨ha, hb⟩) (Nat.le_max_right (sz u) (sz v)))

theorem gm {a b u v : M} (ha : sz a ≤ sz u) (hb : sz b < sz v) : msr a b < msr u v := by
  rcases Nat.lt_or_ge (max (sz a) (sz b)) (max (sz u) (sz v)) with h | h
  · exact msr_lt_of_max_lt h
  · refine msr_lt_of_max_eq (Nat.le_antisymm ?_ h) (by omega)
    exact Nat.max_le.mpr ⟨Nat.le_trans ha (Nat.le_max_left _ _),
      Nat.le_trans (Nat.le_of_lt hb) (Nat.le_max_right _ _)⟩

/-- MAIN: every chain product free, rule 1 fires and every guard is `rfl` -/
theorem opR1 (x y z : M) : op y (J (J (J y x) z) (J x z)) = x := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, -, -, -, -, -, -, -, -, -, hop⟩ :=
    op_cases y (J (J (J y x) z) (J x z))
  have h1 : P1 y (J (J (J y x) z) (J x z)) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  rw [hop, if_pos h1]

/-- the third product decodes, the first two are free: rule 2 fires, its guard is `rfl` -/
theorem opR2 {x z : M} (hC : op x z ≠ J x z) (y : M) :
    op y (J (J (J y x) z) (op x z)) = x := by
  have hs : sz (op x z) < sz z := SZ hC
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, hp1, -, -, -, -, -, -, -, -, hop⟩ :=
    op_cases y (J (J (J y x) z) (op x z))
  have hg : msr x z < msr y (J (J (J y x) z) (op x z)) := by
    refine gsub ?_ ?_ <;> simp only [sz] <;> omega
  rw [dif_pos hg] at hp1
  rw [hop]
  split
  · rename_i h
    exfalso
    have e := h.2.2.2.2.2.2
    simp only [a1_J_eq, a2_J_eq] at e
    have := sz_a2 (op x z)
    have := congrArg sz e
    omega
  · split
    · rfl
    · rename_i h1 h2
      exact absurd ⟨⟨rfl, rfl, rfl, rfl⟩, hg, hp1.symm⟩ h2


/-- every branch of `op` returns the free product, the tag, or a proper subterm of `v` -/
theorem SZ (u v : M) : op u v = J u v ∨ op u v = E u v ∨ sz (op u v) < sz v := by
  obtain ⟨r1, r2, r3, r4, r5, r6, -, -, -, -, -, -, hop⟩ := oc u v
  rw [hop]
  split
  · rename_i h
    refine Or.inr (Or.inr ?_)
    have hv : tg v ≠ 1 := by rw [h.1]; decide
    have := s1 (a2 v); have := s2l hv
    simp only [K1]; omega
  · split
    · rename_i h1 h
      refine Or.inr (Or.inr ?_)
      have hv : tg v ≠ 1 := by rw [h.1]; decide
      have := s1 (a1 (a1 (a2 (a1 v)))); have := s1 (a1 (a2 (a1 v))); have := s1 (a2 (a1 v))
      have := s2 (a1 v); have := s1l hv
      simp only [K2]; omega
    · split
      · exact Or.inr (Or.inl rfl)
      · split
        · exact Or.inr (Or.inl rfl)
        · exact Or.inl rfl

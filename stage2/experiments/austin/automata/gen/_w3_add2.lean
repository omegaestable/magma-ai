
/-- the third product is free: whatever rule fires on the last product, it returns `x` -/
theorem opCF (x y z : M) : op y (J (op (op y x) z) (J x z)) = x := by
  have hb : sz (a2 (op (op y x) z)) ≤ sz x + sz z := by
    by_cases h : op (op y x) z = J (op y x) z
    · rw [h]; simp only [a2_J_eq]; omega
    · have := SZ h; have := sz_a2 (op (op y x) z); omega
  have hA : sz (op y x) < sz (J (op (op y x) z) (J x z)) := by
    have := sz_pos (op (op y x) z)
    by_cases h : op (op y x) z = J (op y x) z
    · rw [h]; simp only [sz]; omega
    · have h1 := SU h; simp only [sz]; omega
  have g2 : msr y (a1 (a2 (J (op (op y x) z) (J x z)))) < msr y (J (op (op y x) z) (J x z)) := by
    refine gm (Nat.le_refl _) ?_
    have := sz_pos (op (op y x) z); have := sz_pos z
    simp only [a1_J_eq, a2_J_eq, sz]; omega
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hop⟩ :=
    op_cases y (J (op (op y x) z) (J x z))
  have hq2 : p2 = op y x := by rw [hp2]; exact dif_pos g2
  rw [hq2] at hp9
  have g9 : msr (op y x) (a2 (a2 (J (op (op y x) z) (J x z)))) < msr y (J (op (op y x) z) (J x z)) := by
    refine gsub hA ?_
    have := sz_pos (op (op y x) z); have := sz_pos x
    simp only [a2_J_eq, sz]; omega
  have hq9 : p9 = op (op y x) z := by rw [hp9]; exact dif_pos g9
  rw [hop]
  split
  · rename_i h; exact h.2.2.2.2.2.1
  · split
    · rename_i h1 h
      obtain ⟨-, hs, he⟩ := h
      have hq : p1 = op (a2 (a1 (a1 (J (op (op y x) z) (J x z))))) (a2 (a1 (J (op (op y x) z) (J x z)))) := by
        rw [hp1]; exact dif_pos hs
      exact (noBig (he.trans hq).symm hb).1
    · split
      · rfl
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨-, hs3, -, he3, -⟩ := h
          have hq : p3 = op (a1 (a1 (a1 (a2 (a1 (J (op (op y x) z) (J x z))))))) (a2 (a1 (J (op (op y x) z) (J x z)))) := by
            rw [hp3]; exact dif_pos hs3
          exact (noBig (he3.trans hq).symm hb).1
        · split
          · rename_i h1 h2 h3 h4 h
            obtain ⟨-, -, hs6, -, -, he6, -⟩ := h
            have hq : p6 = op (a1 (a1 (a1 (a2 (J (op (op y x) z) (J x z)))))) (a2 (a1 (J (op (op y x) z) (J x z)))) := by
              rw [hp6]; exact dif_pos hs6
            exact (noBig (he6.trans hq).symm hb).1
          · split
            · rename_i h1 h2 h3 h4 h5 h
              obtain ⟨-, -, -, hs6, -, -, -, he6, -⟩ := h
              have hq : p6 = op (a1 (a1 (a1 (a2 (J (op (op y x) z) (J x z)))))) (a2 (a1 (J (op (op y x) z) (J x z)))) := by
                rw [hp6]; exact dif_pos hs6
              exact (noBig (he6.trans hq).symm hb).1
            · split
              · rfl
              · rename_i h1 h2 h3 h4 h5 h6 h7
                exact absurd ⟨⟨rfl, rfl⟩, g2, g9, hq9.symm⟩ h7

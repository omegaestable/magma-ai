  rw [FREE2 z x, FREE2 y (J z (op x z))]
  by_cases h1 : op x z = J x z
  · rw [h1]
    by_cases h3 : op (J z (J x z)) y = J (J z (J x z)) y
    · rw [h3]
      exact op_R1 x y z
    · rcases TRa (J z (J x z)) y with hf | ⟨g1, g2, g3, -⟩
      · exact absurd hf h3
      · exact op_R3 g1 g2 (by rw [g2]) g3
  · rcases TRa x z with hf | ⟨q1, q2, q3, -⟩
    · exact absurd hf h1
    · by_cases h3 : op (J z (op x z)) y = J (J z (op x z)) y
      · rw [h3]
        exact op_R2 q1 q2 rfl q3
      · rcases TRa (J z (op x z)) y with hf2 | ⟨g1, g2, g3, -⟩
        · exact absurd hf2 h3
        · exact op_R4 q1 q2 rfl q3 g1 g2 (by rw [g2]) g3

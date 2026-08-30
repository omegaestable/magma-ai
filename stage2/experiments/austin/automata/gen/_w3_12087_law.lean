  rw [VF x y z]
  by_cases hC : op x z = J x z
  · rw [hC]; exact opCF x y z
  · have hB : op (op y x) z = J (op y x) z := by
      by_cases h : op (op y x) z = J (op y x) z
      · exact h
      · exact absurd (BC x y z h) hC
    rw [hB]
    by_cases hA : op y x = J y x
    · rw [hA]; exact opR2 hC y
    · exact AD hA hC

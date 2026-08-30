theorem law (x y z : M) : op y (op (op (op y x) x) (op z z)) = x := by
  rw [sqE z]
  by_cases hxE : x = E
  · subst hxE
    by_cases hyE : y = E
    · subst hyE; simp only [sqE]
    · rw [opE hyE, opE (show (C y : M) ≠ E by simp), opE (show (C (C y) : M) ≠ E by simp),
        opC, if_neg (by intro j; have := congrArg sz j; simp only [szC] at this; omega),
        if_pos ⟨hyE, rfl, rfl⟩]
  · by_cases hx3 : tg x = 3
    · obtain ⟨m, rfl⟩ := G3 hx3
      rcases QD (op y (C m)) m with hw | ⟨hw, k1, k2, k3⟩ | ⟨hw, k1, k2⟩ | ⟨hw, k1, k2⟩ | hw
      · exfalso
        rcases EE hw with c | ⟨c1, -, c3, c4⟩
        · exact absurd (SV1 c) (by simp)
        · simp only [a1C] at c3 c4
          have s1 := AC c3
          have s2 := congrArg sz c4
          simp only [szC] at s2
          exact NB c3 (by rw [c4]; simp) (by omega) c1 rfl
      · have hb : a2 m ≠ E := by
          intro j
          rw [j] at k2
          by_cases ja : a1 m = E
          · rw [ja, sqE] at k2; rw [← k2] at k1; exact absurd k1 (by simp)
          · rw [opE ja] at k2; rw [← k2] at k1; exact absurd k1 (by simp)
        rw [hw, opE hb]
        rcases CC k1 k2 k3 with hc | ⟨d1, d2⟩
        · rw [hc] at k3 ⊢
          rw [sqE] at k3
          refine TOP4 (by simp) ?_
          rw [opC, if_neg (by simp), if_neg (by rintro ⟨j1, -, -⟩; exact j1 rfl),
            if_pos ⟨k1, k2, k3⟩]
        · rw [TOP5 hb d2, ← d1, k2]
      · rw [hw, opE k1, TOP5 k1 (CD k1 k2), k2]
      · exfalso
        rcases EE k2 with c | ⟨c1, c2, c3, c4⟩
        · exact NM k1 c
        · have s1 := AC c2
          have s2 := AC c3
          have s3 := congrArg sz c4
          simp only [szC] at s3
          exact NB c2 c3 (by omega) c1 rfl
      · exact FIN hw
    · exact FIN (opF (fun j => hxE (SV1 j)) hx3 hxE)

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

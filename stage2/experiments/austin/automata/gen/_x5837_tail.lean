theorem noFix (a b : M) : op a b ≠ b := by
  intro he
  rcases TR2 a b with h | ⟨-, -, -, hs⟩ | ⟨hv, -, -, -, -, hs⟩
  · rw [h] at he; have := congrArg sz he; simp only [sz_J] at this; have := sz_pos a; omega
  · rw [he] at hs; omega
  · rw [he] at hs; have := congrArg sz hv; omega

/-- the second chain product is free, or the whole chain collapses onto `a1 y` -/
theorem Wdig (z y : M) : op (op z y) y = J (op z y) y ∨
    (tg y = 2 ∧ tg (a2 y) = 2 ∧ a1 y = a1 (a2 y) ∧ op z y = a1 y ∧ op (op z y) y = a1 y) := by
  rcases TR (op z y) y with h | ⟨h1, h2, h3, h4, -⟩ | ⟨h1, -, -, -, -, -, -, -⟩
  · exact Or.inl h
  · rcases TR z y with g | ⟨-, -, -, g4, -⟩ | ⟨g1, -, -, g4, g5, -, g7, -⟩
    · exfalso
      rw [g] at h3
      have e1 := congrArg sz h3
      simp only [sz_J] at e1
      have := sz_a1 (a2 y); have := sz_a2 y; have := sz_pos z; omega
    · exact Or.inr ⟨h1, h2, g4.symm.trans h3, g4, h4⟩
    · exfalso
      rw [← g1] at g4 g5 g7 h3
      have e1 : a1 (a1 y) = a1 (a2 y) := g7.symm.trans h3
      rw [← g4] at e1
      have := sz_a1_lt g5
      have := congrArg sz e1
      omega
  · exact absurd h1.symm (noFix z y)

/-- one of the four `a1 v` branches fires -/
theorem opB {u v w : M} (hw : a1 v = w) (h : P1 u v ∨
    (P2 u v ∧ msr (a1 (a2 u)) u < msr u v ∧ a1 (a2 (a2 v)) = op (a1 (a2 u)) u) ∨
    (P3 u v ∧ msr u u < msr u v ∧ a1 (a2 (a2 v)) = op u u) ∨
    (P4 u v ∧ msr (a1 (a2 u)) u < msr u v ∧ a2 (a2 v) = op (a1 (a2 u)) u ∧
      a1 (a2 u) = op (a1 (a2 u)) u)) : op u v = w := by
  obtain ⟨p1, p2, p3, p4, p5, hp1, hp2, hp3, hp4, hp5, hop⟩ := op_cases u v
  rw [hop]
  split
  · exact hw
  split
  · exact hw
  split
  · exact hw
  split
  · exact hw
  exfalso
  rename_i n1 n2 n3 n4
  rcases h with c | c | c | c
  · exact n1 c
  · rw [dif_pos c.2.1] at hp1
    exact n2 ⟨c.1, c.2.1, by rw [hp1]; exact c.2.2⟩
  · rw [dif_pos c.2.1] at hp2
    exact n3 ⟨c.1, c.2.1, by rw [hp2]; exact c.2.2⟩
  · rw [dif_pos c.2.1] at hp1
    exact n4 ⟨c.1, c.2.1, by rw [hp1]; exact c.2.2.1, by rw [hp1]; exact c.2.2.2⟩

/-- the diagonal pair: one of the four `a1 (a1 u)` branches fires -/
theorem opC {u w : M} (hw : a1 (a1 u) = w) (h1 : tg u = 2) (h2 : tg (a2 u) = 2)
    (h3 : a1 u = a1 (a2 u)) (h4 : tg (a1 u) = 2) (h5 : op (a1 u) u = a1 u)
    (h6 : (tg (a2 (a1 u)) = 2 ∧ (
          (tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a1 u) = a2 (a1 (a2 (a1 u))) ∧ a1 (a1 u) = a2 (a2 (a1 u))) ∨
          (a1 (a1 u) = a2 (a2 (a1 u)) ∧ tg (a1 (a1 u)) = 2 ∧ tg (a2 (a1 (a1 u))) = 2 ∧
            a1 (a2 (a1 u)) = op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))) ∨
          (a1 (a1 u) = a2 (a2 (a1 u)) ∧ op (a1 (a1 u)) (a1 (a1 u)) = a1 (a2 (a1 u))))) ∨
       (tg (a1 (a1 u)) = 2 ∧ tg (a2 (a1 (a1 u))) = 2 ∧
          a2 (a1 u) = op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) ∧
          a1 (a2 (a1 (a1 u))) = op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)))) : op u u = w := by
  have hne : ¬ (u = a1 (a2 u)) := by
    rw [← h3]; intro he; have := sz_a1_lt h1; have := congrArg sz he; omega
  have g3 : msr (a1 u) u < msr u u :=
    msr_lt_of_max_eq (by have := sz_a1 u; omega) (by have := sz_a1_lt h1; omega)
  have s1 := sz_a1_lt h1
  have s2 := sz_a1 (a1 u)
  have s3 := sz_a1 (a2 (a1 (a1 u)))
  have s4 := sz_a2 (a1 (a1 u))
  have g4 : msr (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) < msr u u :=
    msr_lt_both (by omega) (by omega)
  have g5 : msr (a1 (a1 u)) (a1 (a1 u)) < msr u u := msr_lt_both (by omega) (by omega)
  obtain ⟨p1, p2, p3, p4, p5, hp1, hp2, hp3, hp4, hp5, hop⟩ := op_cases u u
  rw [dif_pos g3] at hp3
  rw [dif_pos g4] at hp4
  rw [dif_pos g5] at hp5
  rw [hop]
  split
  · rename_i c; exact absurd c.2.2.1 hne
  split
  · rename_i c; exact absurd c.1.2.2.1 hne
  split
  · rename_i c; exact absurd c.1.2.2.1 hne
  split
  · rename_i c; exact absurd c.1.2.2.1 hne
  split
  · exact hw
  split
  · exact hw
  split
  · exact hw
  split
  · exact hw
  exfalso
  rename_i n5 n6 n7 n8
  rcases h6 with ⟨ha, hb | hb | hb⟩ | hb
  · exact n5 ⟨⟨rfl, h1, h2, h3, h4, ha, hb.1, hb.2.1, hb.2.2⟩, g3, by rw [hp3]; exact h5.symm⟩
  · exact n6 ⟨⟨rfl, h1, h2, h3, h4, ha, hb.1, hb.2.1, hb.2.2.1⟩, g3, g4,
      by rw [hp3]; exact h5.symm, by rw [hp4]; exact hb.2.2.2⟩
  · exact n7 ⟨⟨rfl, h1, h2, h3, h4, ha, hb.1⟩, g3, g5,
      by rw [hp3]; exact h5.symm, by rw [hp5]; exact hb.2.symm⟩
  · exact n8 ⟨⟨rfl, h1, h2, h3, h4, hb.1, hb.2.1⟩, g3, g4,
      by rw [hp3]; exact h5.symm, by rw [hp4]; exact hb.2.2.1, by rw [hp4]; exact hb.2.2.2⟩

/-- the gate of a nested call whose arguments are bounded by `b`, against `(b, J x (J b t))` -/
theorem gL {a b x t : M} (h : sz a ≤ sz b) : msr a b < msr b (J x (J b t)) :=
  msr_lt_both (by simp only [sz_J]; have := sz_pos x; have := sz_pos t; omega)
    (by simp only [sz_J]; have := sz_pos x; have := sz_pos t; omega)

theorem main (x y z : M) : op y (op x (J y (op (op z y) y))) = x := by
  rcases TR x (J y (op (op z y) y)) with hE | ⟨-, hEt, hEx, hEv, hEs⟩ |
    ⟨hC1, -, hC3, hC4, -, -, -, -⟩
  · rw [hE]
    rcases Wdig z y with hW | ⟨hy1, hy2, hy3, hZ, hWv⟩
    · rw [hW]
      rcases TR z y with hz | ⟨hz1, hz2, hz3, -, -⟩ | ⟨hz1, -, -, -, -, -, -, -⟩
      · rw [hz]
        exact opB rfl (Or.inl ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩)
      · exact opB rfl (Or.inr (Or.inl ⟨⟨rfl, rfl, rfl, rfl, rfl, hz1, hz2⟩,
          gL (by have := sz_a1 (a2 y); have := sz_a2 y; omega),
          by simp only [a1_J_eq, a2_J_eq]; rw [← hz3]⟩))
      · rw [← hz1]
        exact opB rfl (Or.inr (Or.inr (Or.inl ⟨⟨rfl, rfl, rfl, rfl, rfl⟩, gL (Nat.le_refl _),
          by simp only [a1_J_eq, a2_J_eq]⟩)))
    · have h5 : op (a1 y) y = a1 y := by rw [← hZ]; exact hWv.trans hZ.symm
      rw [hWv]
      exact opB rfl (Or.inr (Or.inr (Or.inr ⟨⟨rfl, rfl, rfl, hy1, hy2⟩,
        gL (by have := sz_a1 (a2 y); have := sz_a2 y; omega),
        by simp only [a2_J_eq]; rw [← hy3]; exact h5.symm,
        by rw [← hy3]; exact h5.symm⟩)))
  · simp only [a1_J_eq, a2_J_eq] at hEt hEx hEv hEs
    rw [hEv]
    rcases Wdig z y with hW | ⟨hy1, hy2, hy3, hZ, hWv⟩
    · rw [hW] at hEt hEx hEs
      simp only [a1_J_eq, a2_J_eq] at hEt hEx hEs
      rcases TR z y with hz | ⟨hz1, -, -, hz4, -⟩ | ⟨hz1, -, -, -, -, -, -, -⟩
      · exfalso
        rw [hz] at hEx
        subst hEx
        simp only [a1_J_eq, a2_J_eq] at hEs
        rcases hEs with ⟨ht, ⟨-, -, h⟩ | ⟨h, -, -, -⟩ | ⟨h, -⟩⟩ | ⟨-, hb2, hb3, hb4⟩
        · have := congrArg sz h; simp only [sz_J] at this
          have := sz_a2_lt ht; have := sz_pos z; omega
        · have := congrArg sz h; simp only [sz_J] at this
          have := sz_a2_lt ht; have := sz_pos z; omega
        · have := congrArg sz h; simp only [sz_J] at this
          have := sz_a2_lt ht; have := sz_pos z; omega
        · have hy : y = a1 (a2 (J z y)) := hb3.trans hb4.symm
          simp only [a1_J_eq, a2_J_eq] at hy hb2
          have := sz_a1_lt hb2; have := congrArg sz hy; omega
      · exfalso
        rw [hz4] at hEx
        subst hEx
        rcases hEs with ⟨-, ⟨h1, h2, -⟩ | ⟨-, -, -, h4⟩ | ⟨-, h2⟩⟩ | ⟨hb1, -, hb3, hb4⟩
        · have := sz_a2_lt h1; have := congrArg sz h2; omega
        · exact noFix _ _ h4.symm
        · exact noFix _ _ h2
        · have hy : y = a1 (a2 (a1 y)) := hb3.trans hb4.symm
          have := sz_a1 (a2 (a1 y)); have := sz_a2_lt hb1; have := sz_a1_lt hz1
          have := congrArg sz hy; omega
      · rw [← hz1] at hEx
        exact hEx.symm
    · rw [hWv] at hEt hEx hEs
      subst hEx
      have h5 : op (a1 y) y = a1 y := by rw [← hZ]; exact hWv.trans hZ.symm
      exact opC rfl hy1 hy2 hy3 hEt h5 hEs
  · exfalso
    subst hC1
    simp only [a1_J_eq, a2_J_eq] at hC3 hC4
    rcases Wdig z y with hW | ⟨hy1, -, -, -, hWv⟩
    · rw [hW] at hC4
      simp only [a1_J_eq] at hC4
      exact noFix z y hC4.symm
    · rw [hWv] at hC3 hC4
      have := sz_a1_lt hy1; have := sz_a1_lt hC3; have := congrArg sz hC4; omega

/-- THE LAW: x = y * (x * (y * ((z * y) * y))) -/
theorem law (x y z : M) : op (y) (op (x) (op (y) (op (op (z) (y)) (y)))) = x := by
  have h1 : op y (op (op z y) y) = J y (op (op z y) y) := Tfree_L3 rfl rfl
  rw [h1]
  exact main x y z


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

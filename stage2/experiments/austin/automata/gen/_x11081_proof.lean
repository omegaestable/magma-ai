theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 : M,
    p1 = (if hs1 : msr (a1 (a2 (a1 u))) (u) < msr u v then op (a1 (a2 (a1 u))) (u) else J u v) ∧
    p2 = (if hs2 : msr (a2 (a2 u)) (a2 v) < msr u v then op (a2 (a2 u)) (a2 v) else J u v) ∧
    p3 = (if hs3 : msr (a2 (a2 u)) (u) < msr u v then op (a2 (a2 u)) (u) else J u v) ∧
    p4 = (if hs4 : msr (u) (a1 (a1 v)) < msr u v then op (u) (a1 (a1 v)) else J u v) ∧
    op u v = (
  if P1 u v then a1 (a1 v)
  else if P2 u v ∧ msr (a1 (a2 (a1 u))) (u) < msr u v ∧ a2 v = p1 then a1 (a1 v)
  else if P3 u v ∧ msr (a2 (a2 u)) (a2 v) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a2 (a1 u) = p2 ∧ a2 v = p3 then a1 (a1 v)
  else if P4 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ a2 (a1 v) = p4 then a1 (a1 v)
  else if P5 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a1 (a2 (a1 u))) (u) < msr u v ∧ a2 (a1 v) = p4 ∧ a2 v = p1 then a1 (a1 v)
  else J u v
    ) :=
  ⟨_, _, _, _, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or the single common shape, with the firing branch's data -/
theorem TR (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ tg (a1 v) = 2 ∧ op u v = a1 (a1 v) ∧
    ( (tg (a2 (a1 v)) = 2 ∧ u = a1 (a2 (a1 v)) ∧ a1 (a1 v) = a2 (a2 (a1 v)) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v))
    ∨ (tg (a2 (a1 v)) = 2 ∧ u = a1 (a2 (a1 v)) ∧ a1 (a1 v) = a2 (a2 (a1 v)) ∧ a2 v = op (a1 (a2 (a1 u))) u)
    ∨ (tg (a2 (a1 v)) = 2 ∧ u = a1 (a2 (a1 v)) ∧ a1 (a1 v) = a2 (a2 (a1 v)) ∧ a2 v = a1 (a1 u) ∧
        a2 (a1 u) = op (a2 (a2 u)) (a2 v) ∧ a2 v = op (a2 (a2 u)) u)
    ∨ (tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ a2 (a1 v) = op u (a1 (a1 v)))
    ∨ (a2 (a1 v) = op u (a1 (a1 v)) ∧ a2 v = op (a1 (a2 (a1 u))) u) )) := by
  obtain ⟨p1, p2, p3, p4, hp1, hp2, hp3, hp4, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h
    exact Or.inr ⟨h.1, h.2.1, rfl, Or.inl ⟨h.2.2.1, h.2.2.2.1, h.2.2.2.2.1, h.2.2.2.2.2.1, h.2.2.2.2.2.2⟩⟩
  · split
    · rename_i h
      obtain ⟨hP, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr ⟨hP.1, hP.2.1, rfl,
        Or.inr (Or.inl ⟨hP.2.2.1, hP.2.2.2.1, hP.2.2.2.2.1, he⟩)⟩
    · split
      · rename_i h
        obtain ⟨hP, hs2, hs3, he2, he3⟩ := h
        rw [dif_pos hs2] at hp2; subst hp2
        rw [dif_pos hs3] at hp3; subst hp3
        exact Or.inr ⟨hP.1, hP.2.1, rfl,
          Or.inr (Or.inr (Or.inl ⟨hP.2.2.1, hP.2.2.2.1, hP.2.2.2.2.1,
            hP.2.2.2.2.2.2.2.1, he2, he3⟩))⟩
      · split
        · rename_i h
          obtain ⟨hP, hs4, he⟩ := h
          rw [dif_pos hs4] at hp4; subst hp4
          exact Or.inr ⟨hP.1, hP.2.1, rfl,
            Or.inr (Or.inr (Or.inr (Or.inl ⟨hP.2.2.1, hP.2.2.2, he⟩)))⟩
        · split
          · rename_i h
            obtain ⟨hP, hs4, hs1, he4, he1⟩ := h
            rw [dif_pos hs4] at hp4; subst hp4
            rw [dif_pos hs1] at hp1; subst hp1
            exact Or.inr ⟨hP.1, hP.2.1, rfl,
              Or.inr (Or.inr (Or.inr (Or.inr ⟨he4, he1⟩)))⟩
          · exact Or.inl rfl

/-- free, or the result is at least four smaller than `v` -/
theorem W (u v : M) : op u v = J u v ∨ (op u v = a1 (a1 v) ∧ sz (op u v) + 4 ≤ sz v) := by
  rcases TR u v with h | ⟨h1, h2, h3, -⟩
  · exact Or.inl h
  · refine Or.inr ⟨h3, ?_⟩
    have e1 := sz_tg v h1
    have e2 := sz_tg (a1 v) h2
    have e3 := sz_pos (a2 v)
    have e4 := sz_pos (a2 (a1 v))
    rw [h3]; omega

theorem NF {a b : M} (h : op a b = b) : False := by
  rcases W a b with hf | ⟨-, hs⟩
  · rw [hf] at h; have := congrArg sz h; simp only [sz] at this; have := sz_pos a; omega
  · rw [h] at hs; omega

/-- the second chain product `op x (op y x)` is always free -/
theorem Bfree (x y : M) : op x (op y x) = J x (op y x) := by
  rcases W y x with hA | ⟨hA1, hA2⟩
  · rw [hA]
    rcases TR x (J y x) with h | ⟨-, -, -, hd⟩
    · exact h
    · exfalso
      simp only [a1_J_eq, a2_J_eq] at hd
      rcases hd with ⟨-, -, -, ht, he⟩ | ⟨-, -, -, he⟩ | ⟨-, -, -, -, -, he⟩ | ⟨ht, he, -⟩ | ⟨-, he⟩
      · have := sz_a2_lt ht; rw [← he] at this; omega
      · exact NF he.symm
      · exact NF he.symm
      · have := sz_a2_lt ht; rw [← he] at this; omega
      · exact NF he.symm
  · rcases TR x (op y x) with h | ⟨h1, -, -, hd⟩
    · exact h
    · exfalso
      have b1 := sz_a2 (a2 (op y x))
      have b2 := sz_a2 (op y x)
      have b3 := sz_a1 (a2 (a1 (op y x)))
      have b4 := sz_a2 (a1 (op y x))
      have b5 := sz_a1 (op y x)
      rcases hd with ⟨-, -, -, -, he⟩ | ⟨-, he, -, -⟩ | ⟨-, he, -, -, -, -⟩ | ⟨-, he, -⟩ | ⟨-, he1⟩
      · rw [← he] at b1; omega
      · rw [← he] at b3; omega
      · rw [← he] at b3; omega
      · rw [← he] at b1; omega
      · rcases W (a1 (a2 (a1 x))) x with hf | ⟨hr, -⟩
        · rw [hf] at he1
          have := congrArg sz he1
          simp only [sz] at this
          have := sz_pos (a1 (a2 (a1 x)))
          omega
        · rw [hr, ← hA1] at he1
          have := sz_a2_lt h1
          rw [he1] at this
          omega

theorem law (x y z : M) : op (y) (op (op (x) (op (y) (x))) (op (z) (y))) = x := by
  sorry

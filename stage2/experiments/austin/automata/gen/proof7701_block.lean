theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem gate_a1 {u v : M} (h : sz u < sz v) : msr (a1 u) u < msr u v :=
  msr_lt_of_max_lt (by have := sz_a1 u; omega)
theorem gate_x {x u v : M} (h : sz x < sz v) : msr (a1 x) x < msr u v :=
  msr_lt_of_max_lt (by have := sz_a1 x; omega)

/-- the unfolding of `op` with the three nested calls packed away as opaque variables -/
theorem op_cases (u v : M) : ∃ p1 p2 p3 : M,
    p1 = (if hs1 : msr (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) < msr u v then op (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) else J u v) ∧
    p2 = (if hs2 : msr (a1 u) (u) < msr u v then op (a1 u) (u) else J u v) ∧
    p3 = (if hs3 : msr (a1 (a1 (a1 u))) (a1 (a1 u)) < msr u v then op (a1 (a1 (a1 u))) (a1 (a1 u)) else J u v) ∧
    op u v = (
  if P1 u v then a1 (a1 (a2 v))
  else if P2 u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) < msr u v ∧ a2 (a1 (a2 v)) = p1 then a1 (a1 (a2 v))
  else if P3 u v ∧ msr (a1 u) (u) < msr u v ∧ a2 v = p2 then a1 (a1 u)
  else if P4 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a1 (a1 u))) (a1 (a1 u)) < msr u v ∧ a2 v = p2 ∧ a2 (a1 u) = p3 then a1 (a1 u)
  else J u v) :=
  ⟨_, _, _, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the four rules fired (with its op-guards) -/
theorem TR4 (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a1 (a1 (a2 v))) ∨
    (P2 u v ∧ a2 (a1 (a2 v)) = op (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) ∧ op u v = a1 (a1 (a2 v))) ∨
    (P3 u v ∧ a2 v = op (a1 u) u ∧ op u v = a1 (a1 u)) ∨
    (P4 u v ∧ a2 v = op (a1 u) u ∧ a2 (a1 u) = op (a1 (a1 (a1 u))) (a1 (a1 u)) ∧ op u v = a1 (a1 u)) := by
  obtain ⟨p1, p2, p3, hp1, hp2, hp3, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h1 h
      obtain ⟨h2, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr (Or.inr (Or.inl ⟨h2, he, rfl⟩))
    · split
      · rename_i h1 h2 h
        obtain ⟨h3, hs2, he⟩ := h
        rw [dif_pos hs2] at hp2; subst hp2
        exact Or.inr (Or.inr (Or.inr (Or.inl ⟨h3, he, rfl⟩)))
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨h4, hs2, hs3, he2, he3⟩ := h
          rw [dif_pos hs2] at hp2; subst hp2
          rw [dif_pos hs3] at hp3; subst hp3
          exact Or.inr (Or.inr (Or.inr (Or.inr ⟨h4, he2, he3, rfl⟩)))
        · left; rfl

/-- every rule needs `u = a1 v` and returns a proper subterm of `v` -/
theorem TRs (u v : M) : op u v = J u v ∨ (u = a1 v ∧ tg v = 2 ∧ sz (op u v) < sz v) := by
  rcases TR4 u v with h | ⟨h1, h⟩ | ⟨h2, -, h⟩ | ⟨h3, -, h⟩ | ⟨h4, -, -, h⟩
  · exact Or.inl h
  · refine Or.inr ⟨h1.2.1, h1.1, ?_⟩
    rw [h]; have := sz_a2_lt h1.1; have := sz_a1 (a2 v); have := sz_a1 (a1 (a2 v)); omega
  · refine Or.inr ⟨h2.2.1, h2.1, ?_⟩
    rw [h]; have := sz_a2_lt h2.1; have := sz_a1 (a2 v); have := sz_a1 (a1 (a2 v)); omega
  · refine Or.inr ⟨h3.2.1, h3.1, ?_⟩
    rw [h]; have := sz_a1_lt h3.1; have := congrArg sz h3.2.1; have := sz_a1 u; have := sz_a1 (a1 u); omega
  · refine Or.inr ⟨h4.2.1, h4.1, ?_⟩
    rw [h]; have := sz_a1_lt h4.1; have := congrArg sz h4.2.1; have := sz_a1 u; have := sz_a1 (a1 u); omega

/-- `x ◇ (x ◇ x)` is free -/
theorem NF_xx (x : M) : op x (J x x) = J x (J x x) := by
  rcases TR4 x (J x x) with h | ⟨h1, -⟩ | ⟨h2, -, -⟩ | ⟨-, hg, -⟩ | ⟨-, hg, -, -⟩
  · exact h
  · obtain ⟨-, -, t3, -, -, -, t7⟩ := h1
    simp only [a2_J_eq] at t3 t7
    exfalso; have := sz_a2_lt t3; have := congrArg sz t7; omega
  · obtain ⟨-, -, t3, -, t5, -⟩ := h2
    simp only [a2_J_eq] at t3 t5
    exfalso; have := sz_a2_lt t3; have := congrArg sz t5; omega
  · simp only [a2_J_eq] at hg
    rcases TRs (a1 x) x with h' | ⟨-, -, hs'⟩
    · rw [h'] at hg; have := congrArg sz hg; simp only [sz_J] at this; omega
    · rw [← hg] at hs'; exact absurd hs' (Nat.lt_irrefl _)
  · simp only [a2_J_eq] at hg
    rcases TRs (a1 x) x with h' | ⟨-, -, hs'⟩
    · rw [h'] at hg; have := congrArg sz hg; simp only [sz_J] at this; omega
    · rw [← hg] at hs'; exact absurd hs' (Nat.lt_irrefl _)

/-- `b ◇ (a ◇ b)` is always free: a rule would need `b = a1 (a ◇ b)` -/
theorem Lfree (a b : M) : op b (op a b) = J b (op a b) := by
  rcases TRs a b with h | ⟨-, -, hs⟩
  · rw [h]
    rcases TRs b (J a b) with h' | ⟨hba, -, -⟩
    · exact h'
    · simp only [a1_J_eq] at hba; subst hba; exact NF_xx _
  · rcases TRs b (op a b) with h' | ⟨hba, -, -⟩
    · exact h'
    · exfalso; have := congrArg sz hba; have := sz_a1 (op a b); omega

/-- R1: the fully free encoding -/
theorem op_R1 (u x z : M) : op u (J u (J (J x (J z x)) u)) = x := by
  obtain ⟨p1, p2, p3, -, -, -, hop⟩ := op_cases u (J u (J (J x (J z x)) u))
  have h1 : P1 u (J u (J (J x (J z x)) u)) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  rw [hop, if_pos h1]
  rfl

/-- R2: `z ◇ x` decoded (so `z = a1 x`), the outer products free -/
theorem op_R2 (u x : M) (hx : tg x = 2) : op u (J u (J (J x (op (a1 x) x)) u)) = x := by
  obtain ⟨p1, p2, p3, hp1, hp2, hp3, hop⟩ := op_cases u (J u (J (J x (op (a1 x) x)) u))
  have hs1 : msr (a1 (a1 (a1 (a2 (J u (J (J x (op (a1 x) x)) u)))))) (a1 (a1 (a2 (J u (J (J x (op (a1 x) x)) u))))) < msr u (J u (J (J x (op (a1 x) x)) u)) := by
    simp only [a1_J_eq, a2_J_eq]
    exact gate_x (by simp only [sz_J]; omega)
  rw [dif_pos hs1] at hp1; subst hp1
  rw [hop]
  split
  · rfl
  · split
    · rfl
    · rename_i h1 h2
      exfalso; apply h2
      exact ⟨⟨rfl, rfl, rfl, rfl, rfl, hx⟩, hs1, rfl⟩

/-- R3: `(x ◇ (z ◇ x)) ◇ y` decoded (y = J (x ◇ (z ◇ x)) B), `z ◇ x` free -/
theorem op_R3 (x z B : M)
    (hs : sz (op (J x (J z x)) (J (J x (J z x)) B)) < sz (J (J x (J z x)) B)) :
    op (J (J x (J z x)) B) (J (J (J x (J z x)) B) (op (J x (J z x)) (J (J x (J z x)) B))) = x := by
  obtain ⟨p1, p2, p3, hp1, hp2, hp3, hop⟩ := op_cases (J (J x (J z x)) B) (J (J (J x (J z x)) B) (op (J x (J z x)) (J (J x (J z x)) B)))
  have hs2 : msr (a1 (J (J x (J z x)) B)) (J (J x (J z x)) B) < msr (J (J x (J z x)) B) (J (J (J x (J z x)) B) (op (J x (J z x)) (J (J x (J z x)) B))) :=
    gate_a1 (by simp only [sz_J]; omega)
  rw [dif_pos hs2] at hp2; subst hp2
  rw [hop]
  split
  · rename_i h
    obtain ⟨-, -, t3, -, -, -, t7⟩ := h
    simp only [a1_J_eq, a2_J_eq] at t3 t7
    exfalso; have := sz_a2_lt t3; have := congrArg sz t7; omega
  · split
    · rename_i h1 h
      obtain ⟨⟨-, -, t3, -, t5, -⟩, -, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at t3 t5
      exfalso; have := sz_a2_lt t3; have := congrArg sz t5; omega
    · split
      · rfl
      · rename_i h1 h2 h3
        exfalso; apply h3
        exact ⟨⟨rfl, rfl, rfl, rfl, rfl, rfl⟩, hs2, rfl⟩

/-- R4: both `z ◇ x` and `(x ◇ (z ◇ x)) ◇ y` decoded -/
theorem op_R4 (x B : M) (hx : tg x = 2) (hq : sz (op (a1 x) x) < sz x)
    (hs : sz (op (J x (op (a1 x) x)) (J (J x (op (a1 x) x)) B)) < sz (J (J x (op (a1 x) x)) B)) :
    op (J (J x (op (a1 x) x)) B) (J (J (J x (op (a1 x) x)) B) (op (J x (op (a1 x) x)) (J (J x (op (a1 x) x)) B))) = x := by
  obtain ⟨p1, p2, p3, hp1, hp2, hp3, hop⟩ := op_cases (J (J x (op (a1 x) x)) B) (J (J (J x (op (a1 x) x)) B) (op (J x (op (a1 x) x)) (J (J x (op (a1 x) x)) B)))
  have hs2 : msr (a1 (J (J x (op (a1 x) x)) B)) (J (J x (op (a1 x) x)) B) < msr (J (J x (op (a1 x) x)) B) (J (J (J x (op (a1 x) x)) B) (op (J x (op (a1 x) x)) (J (J x (op (a1 x) x)) B))) :=
    gate_a1 (by simp only [sz_J]; omega)
  have hs3 : msr (a1 (a1 (a1 (J (J x (op (a1 x) x)) B)))) (a1 (a1 (J (J x (op (a1 x) x)) B))) < msr (J (J x (op (a1 x) x)) B) (J (J (J x (op (a1 x) x)) B) (op (J x (op (a1 x) x)) (J (J x (op (a1 x) x)) B))) := by
    simp only [a1_J_eq]
    exact gate_x (by simp only [sz_J]; omega)
  rw [dif_pos hs2] at hp2; subst hp2
  rw [dif_pos hs3] at hp3; subst hp3
  rw [hop]
  split
  · rename_i h
    obtain ⟨-, -, t3, -, -, -, t7⟩ := h
    simp only [a1_J_eq, a2_J_eq] at t3 t7
    exfalso; have := sz_a2_lt t3; have := congrArg sz t7; omega
  · split
    · rename_i h1 h
      obtain ⟨⟨-, -, t3, -, t5, -⟩, -, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at t3 t5
      exfalso; have := sz_a2_lt t3; have := congrArg sz t5; omega
    · split
      · rename_i h1 h2 h
        obtain ⟨⟨-, -, -, -, t5, t6⟩, -, -⟩ := h
        simp only [a1_J_eq, a2_J_eq] at t5 t6
        exfalso; have := sz_a2_lt t5; have := congrArg sz t6; omega
      · split
        · rfl
        · rename_i h1 h2 h3 h4
          exfalso; apply h4
          exact ⟨⟨rfl, rfl, rfl, rfl, hx⟩, hs2, hs3, rfl, rfl⟩

/-- THE LAW: x = y * (y * ((x * (z * x)) * y)) -/
theorem law (x y z : M) : op (y) (op (y) (op (op (x) (op (z) (x))) (y))) = x := by
  rw [Lfree z x, Lfree (J x (op z x)) y]
  rcases TRs (J x (op z x)) y with h3 | ⟨hy, hty, hs3⟩
  · rw [h3]
    rcases TRs z x with h1 | ⟨hz, htx, hs1⟩
    · rw [h1]; exact op_R1 y x z
    · subst hz; exact op_R2 y x htx
  · obtain ⟨b0, b1, rfl⟩ := tg_J y hty
    simp only [a1_J_eq] at hy
    subst hy
    rcases TRs z x with h1 | ⟨hz, htx, hs1⟩
    · rw [h1] at hs3 ⊢; exact op_R3 x z b1 hs3
    · subst hz; exact op_R4 x b1 htx hs1 hs3

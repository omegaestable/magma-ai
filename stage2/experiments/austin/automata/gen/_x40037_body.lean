theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 : M,
    p1 = (if hs1 : msr (a2 (a2 (a2 v))) (a1 v) < msr u v then op (a2 (a2 (a2 v))) (a1 v) else J u v) ∧
    p2 = (if hs2 : msr (a1 (a2 (a1 v))) (a1 v) < msr u v then op (a1 (a2 (a1 v))) (a1 v) else J u v) ∧
    p3 = (if hs3 : msr (p2) (a1 (a2 (a1 v))) < msr u v then op (p2) (a1 (a2 (a1 v))) else J u v) ∧
    p4 = (if hs4 : msr (u) (p3) < msr u v then op (u) (p3) else J u v) ∧
    p5 = (if hs5 : msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else J u v) ∧
    p6 = (if hs6 : msr (p5) (a1 (a2 v)) < msr u v then op (p5) (a1 (a2 v)) else J u v) ∧
    p7 = (if hs7 : msr (u) (p6) < msr u v then op (u) (p6) else J u v) ∧
    op u v = (
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a2 (a2 (a2 v))) (a1 v) < msr u v ∧ a1 (a2 (a2 v)) = p1 then a1 v
  else if P3 u v ∧ msr (a1 (a2 (a1 v))) (a1 v) < msr u v ∧ msr (p2) (a1 (a2 (a1 v))) < msr u v ∧ msr (u) (p3) < msr u v ∧ a2 v = p4 then a1 v
  else if P4 u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (p5) (a1 (a2 v)) < msr u v ∧ msr (u) (p6) < msr u v ∧ a2 v = p7 then a1 v
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the four rules fired (with its op-guard). -/
theorem TR4 (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a1 v) ∨
    (P2 u v ∧ a1 (a2 (a2 v)) = op (a2 (a2 (a2 v))) (a1 v) ∧ op u v = a1 v) ∨
    (P3 u v ∧ a2 v = op u (op (op (a1 (a2 (a1 v))) (a1 v)) (a1 (a2 (a1 v)))) ∧ op u v = a1 v) ∨
    (P4 u v ∧ a2 v = op u (op (op (a1 (a2 v)) (a1 v)) (a1 (a2 v))) ∧ op u v = a1 v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hop⟩ := op_cases u v
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
        obtain ⟨h3, hs2, hs3, hs4, he⟩ := h
        rw [dif_pos hs2] at hp2; subst hp2
        rw [dif_pos hs3] at hp3; subst hp3
        rw [dif_pos hs4] at hp4; subst hp4
        exact Or.inr (Or.inr (Or.inr (Or.inl ⟨h3, he, rfl⟩)))
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨h4, hs5, hs6, hs7, he⟩ := h
          rw [dif_pos hs5] at hp5; subst hp5
          rw [dif_pos hs6] at hp6; subst hp6
          rw [dif_pos hs7] at hp7; subst hp7
          exact Or.inr (Or.inr (Or.inr (Or.inr ⟨h4, he, rfl⟩)))
        · left; rfl

/-- the digest: every rule needs `tg v = 2` and returns `a1 v`. -/
theorem TRs (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ op u v = a1 v) := by
  rcases TR4 u v with h | ⟨h, e⟩ | ⟨h, -, e⟩ | ⟨h, -, e⟩ | ⟨h, -, e⟩
  · exact Or.inl h
  · exact Or.inr ⟨h.1, e⟩
  · exact Or.inr ⟨h.1, e⟩
  · exact Or.inr ⟨h.1, e⟩
  · exact Or.inr ⟨h.1, e⟩

/-- a decoded product is strictly smaller than its right argument. -/
theorem TRsz (u v : M) : op u v = J u v ∨ sz (op u v) < sz v := by
  rcases TRs u v with h | ⟨ht, e⟩
  · exact Or.inl h
  · exact Or.inr (by rw [e]; exact sz_a1_lt ht)

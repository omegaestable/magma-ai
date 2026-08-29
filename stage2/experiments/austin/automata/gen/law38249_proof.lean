/-- the unfolding of `op` with the nested call packed away as an opaque variable -/
theorem op_cases (u v : M) : ∃ p1 : M,
    p1 = (if hs1 : msr (a1 u) u < msr u v then op (a1 u) u else J u v) ∧
    op u v = (
  if P1 u v then a1 (a2 (a1 (a2 v)))
  else if P2 u v ∧ msr (a1 u) u < msr u v ∧ a2 v = p1 then a1 (a2 (a1 u))
  else J u v) :=
  ⟨_, rfl, op.eq_1 u v⟩

theorem P1_sz {u v : M} (h : P1 u v) : sz v = sz u + sz u + sz (a1 (a1 (a2 v))) + sz (a1 (a2 (a1 (a2 v)))) + sz (a1 (a2 (a1 (a2 v)))) + 4 := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7⟩ := h
  have s1 := sz_tg v h1
  have s2 := sz_tg _ h3
  have s3 := sz_tg _ h4
  have s4 := sz_tg _ h5
  have e2 := congrArg sz h2
  have e6 := congrArg sz h6
  have e7 := congrArg sz h7
  omega

theorem P2_sz {u v : M} (h : P2 u v) : sz (a1 (a2 (a1 u))) < sz u := by
  obtain ⟨-, -, h3, h4, -⟩ := h
  have s1 := sz_tg _ h3
  have s2 := sz_tg _ h4
  have s3 := sz_a1 u
  omega

/-- one unfold of `op`: free, or R1 on its shape, or R2 with its recursive guard -/
theorem TR (u v : M) : op u v = J u v ∨ (P1 u v ∧ op u v = a1 (a2 (a1 (a2 v)))) ∨
    (P2 u v ∧ a2 v = op (a1 u) u ∧ op u v = a1 (a2 (a1 u))) := by
  obtain ⟨p1, hp1, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h1 h
      obtain ⟨h2, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr (Or.inr ⟨h2, he, rfl⟩)
    · left; rfl

/-- the size invariant: a reduction returns a proper subterm of v (R1) or of u (R2) -/
theorem TRs (u v : M) : op u v = J u v ∨ sz (op u v) < sz v ∨ sz (op u v) < sz u := by
  rcases TR u v with h | ⟨h1, h⟩ | ⟨h1, -, h⟩
  · exact Or.inl h
  · right; left; rw [h]; have := P1_sz h1; omega
  · right; right; rw [h]; exact P2_sz h1

/-- every reduction has  v = J u _ -/
theorem red_a1 {u v : M} (h : op u v ≠ J u v) : tg v = 2 ∧ u = a1 v := by
  rcases TR u v with h' | ⟨h1, -⟩ | ⟨h1, -, -⟩
  · exact absurd h' h
  · exact ⟨h1.1, h1.2.1⟩
  · exact ⟨h1.1, h1.2.1⟩

/-- `op (a1 y) y` is never `y` itself -/
theorem no_self (y : M) : y ≠ op (a1 y) y := by
  intro he
  have s := sz_a1 y
  rcases TRs (a1 y) y with h' | h' | h'
  · rw [h'] at he; have := congrArg sz he; simp only [sz] at this; omega
  · rw [← he] at h'; exact absurd h' (Nat.lt_irrefl _)
  · rw [← he] at h'; omega

/-- first product of the chain: x * x is free -/
theorem S1 (x : M) : op x x = J x x := by
  rcases TR x x with h | ⟨h1, -⟩ | ⟨h1, -, -⟩
  · exact h
  · have := sz_tg x h1.1; have := congrArg sz h1.2.1; omega
  · have := sz_tg x h1.1; have := congrArg sz h1.2.1; omega

/-- second product: z * (x * x) is free -/
theorem S2 (x z : M) : op z (J x x) = J z (J x x) := by
  rcases TR z (J x x) with h | ⟨h1, -⟩ | ⟨h1, he, -⟩
  · exact h
  · obtain ⟨-, h2, h3, -, -, -, h7⟩ := h1
    simp only [a1_J_eq, a2_J_eq] at h2 h3 h7
    have := sz_tg x h3; have := congrArg sz h2; have := congrArg sz h7; omega
  · obtain ⟨-, h2, -, -, -⟩ := h1
    simp only [a1_J_eq, a2_J_eq] at h2 he
    rw [h2] at he
    exact absurd he (no_self x)

/-- fourth product when the third is free -/
theorem S4a (x y z : M) : op y (J (J z (J x x)) y) = J y (J (J z (J x x)) y) := by
  rcases TR y (J (J z (J x x)) y) with h | ⟨h1, -⟩ | ⟨h1, he, -⟩
  · exact h
  · obtain ⟨-, -, h3, -, -, -, h7⟩ := h1
    simp only [a2_J_eq] at h3 h7
    have := sz_tg y h3; have := congrArg sz h7; omega
  · simp only [a2_J_eq] at he
    exact absurd he (no_self y)

/-- fourth product when the third reduced (to a term smaller than y) -/
theorem S4b {y c : M} (hc : sz c < sz y) : op y c = J y c := by
  rcases TR y c with h | ⟨h1, -⟩ | ⟨h1, -, -⟩
  · exact h
  · have := congrArg sz h1.2.1; have := sz_a1 c; omega
  · have := congrArg sz h1.2.1; have := sz_a1 c; omega

theorem op_R1 (x y z : M) : op y (J y (J (J z (J x x)) y)) = x := by
  obtain ⟨p1, -, hop⟩ := op_cases y (J y (J (J z (J x x)) y))
  have h1 : P1 y (J y (J (J z (J x x)) y)) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  rw [hop, if_pos h1]
  rfl

theorem op_R2 {y c : M} (x z : M) (hy : a1 y = J z (J x x)) (hc : op (a1 y) y = c) (hs : sz c < sz y) :
    op y (J y c) = x := by
  obtain ⟨p1, hp1, hop⟩ := op_cases y (J y c)
  have hs1 : msr (a1 y) y < msr y (J y c) := by
    apply msr_lt_of_max_lt
    have := sz_a1 y
    simp only [sz]; omega
  rw [dif_pos hs1] at hp1; subst hp1
  rw [hop]
  split
  · rename_i h
    exfalso
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    have := congrArg sz h7; have := sz_a2 c; omega
  · split
    · simp only [hy, a1_J_eq, a2_J_eq]
    · rename_i h1 h2
      exfalso; apply h2
      refine ⟨⟨rfl, rfl, ?_, ?_, ?_⟩, hs1, ?_⟩
      · simp only [hy, tg_J_eq]
      · simp only [hy, a2_J_eq, tg_J_eq]
      · simp only [hy, a1_J_eq, a2_J_eq]
      · simp only [a2_J_eq]; exact hc.symm

/-- THE LAW: x = ((y * ((x * x) * z)) * y) * y (stated for the DUAL L-form law; the served magma flips op, so EquationLHS unfolds to exactly this) -/
theorem law (x y z : M) : op (y) (op (y) (op (op (z) (op (x) (x))) (y))) = x := by
  rw [S1, S2]
  by_cases hf : op (J z (J x x)) y = J (J z (J x x)) y
  · rw [hf, S4a, op_R1]
  · obtain ⟨-, hy⟩ := red_a1 hf
    have hs : sz (op (J z (J x x)) y) < sz y := by
      have := sz_a1 y
      have := congrArg sz hy
      rcases TRs (J z (J x x)) y with h | h | h
      · exact absurd h hf
      · exact h
      · omega
    have hc : op (a1 y) y = op (J z (J x x)) y := by rw [← hy]
    rw [S4b hs]
    exact op_R2 x z hy.symm hc hs


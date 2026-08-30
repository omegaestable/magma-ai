theorem szP (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem szJ (a b : M) : sz (J a b) = sz a + sz b + 1 := by simp [sz]
theorem sA1 {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp only [a1_J_eq, szJ]; have := szP b; omega
theorem sA2 {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp only [a2_J_eq, szJ]; have := szP a; omega

theorem op_cases (u v : M) : ∃ p1 p2 p3 : M,
    p1 = (if hs1 : msr (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) < msr u v then op (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) else J u v) ∧
    p2 = (if hs2 : msr (a1 u) (u) < msr u v then op (a1 u) (u) else J u v) ∧
    p3 = (if hs3 : msr (a1 (a1 (a1 u))) (a1 (a1 u)) < msr u v then op (a1 (a1 (a1 u))) (a1 (a1 u)) else J u v) ∧
    op u v = (
  if P1 u v then a1 (a2 (a1 (a2 v)))
  else if P2 u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) < msr u v ∧ a2 (a1 (a2 v)) = p1 then a1 (a1 (a1 (a2 v)))
  else if P3 u v ∧ msr (a1 u) (u) < msr u v ∧ a2 v = p2 then a1 (a2 (a1 u))
  else if P4 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a1 (a1 u))) (a1 (a1 u)) < msr u v ∧ a2 v = p2 ∧ a2 (a1 u) = p3 then a1 (a1 (a1 u))
  else J u v
    ) :=
  ⟨_, _, _, rfl, rfl, rfl, op.eq_1 u v⟩

/-- the digest: a product is free, or `v = J u _`, its value is a proper subterm of `v`, and
    either the encoding's outer shape is visible (`a2 (a2 v) = u`) or `a2 v` is the value of
    `op (a1 u) u`. -/
theorem TRa (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ a1 v = u ∧ sz (op u v) < sz v ∧
    ((tg (a2 v) = 2 ∧ a2 (a2 v) = u) ∨ a2 v = op (a1 u) u)) := by
  obtain ⟨p1, p2, p3, hp1, hp2, hp3, hop⟩ := op_cases u v
  split at hop
  · rename_i h
    obtain ⟨h1, h2, h3, h4, h5, h6, h7⟩ := h
    refine Or.inr ⟨h1, h2.symm, ?_, Or.inl ⟨h3, h7.symm⟩⟩
    rw [hop]
    have e1 := sA1 h5; have e2 := sA2 h4; have e3 := sA1 h3; have e4 := sA2 h1
    omega
  · split at hop
    · rename_i h
      obtain ⟨⟨h1, h2, h3, h4, h5, h6⟩, -, -⟩ := h
      refine Or.inr ⟨h1, h2.symm, ?_, Or.inl ⟨h3, h5.symm⟩⟩
      rw [hop]
      have e1 := sA1 h6; have e2 := sA1 h4; have e3 := sA1 h3; have e4 := sA2 h1
      omega
    · split at hop
      · rename_i h
        obtain ⟨⟨h1, h2, h3, h4, h5, h6⟩, hg, he⟩ := h
        rw [dif_pos hg] at hp2
        subst hp2
        refine Or.inr ⟨h1, h2.symm, ?_, Or.inr he⟩
        rw [hop]
        have e0 := congrArg sz h2
        have e1 := sA1 h5; have e2 := sA2 h4; have e3 := sA1 h3; have e4 := sA1 h1
        omega
      · split at hop
        · rename_i h
          obtain ⟨⟨h1, h2, h3, h4, h5⟩, hg, hg2, he, he2⟩ := h
          rw [dif_pos hg] at hp2
          subst hp2
          refine Or.inr ⟨h1, h2.symm, ?_, Or.inr he⟩
          rw [hop]
          have e0 := congrArg sz h2
          have e1 := sA1 h5; have e2 := sA1 h4; have e3 := sA1 h3; have e4 := sA1 h1
          omega
        · exact Or.inl hop

/-- no product returns its own right argument -/
theorem NF (a b : M) : op a b ≠ b := by
  intro h
  rcases TRa a b with hf | ⟨-, -, hs, -⟩
  · rw [hf] at h
    have e := congrArg sz h
    rw [szJ] at e
    have := szP a; omega
  · rw [h] at hs; omega

/-- every product of the shape `a * (b * a)` is free: this covers both `z * (x * z)` and
    `y * (((z * (x * z))) * y)`, so the chain's 2nd and 4th products are never decoded. -/
theorem FREE2 (a b : M) : op a (op b a) = J a (op b a) := by
  rcases TRa a (op b a) with hf | ⟨h1, h2, h3, hd⟩
  · exact hf
  · exfalso
    rcases TRa b a with hf2 | ⟨g1, g2, g3, -⟩
    · rw [hf2] at h2 hd
      simp only [a1_J_eq, a2_J_eq] at h2 hd
      subst h2
      rcases hd with ⟨hd1, hd2⟩ | hd
      · have := sA2 hd1
        have e := congrArg sz hd2
        omega
      · exact NF _ _ hd.symm
    · have e := sz_a1 (op b a)
      rw [h2] at e
      omega

/-- everything free -/
theorem op_R1 (x y z : M) : op y (J y (J (J z (J x z)) y)) = x := by
  obtain ⟨p1, p2, p3, -, -, -, hop⟩ := op_cases y (J y (J (J z (J x z)) y))
  have hP : P1 y (J y (J (J z (J x z)) y)) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  split at hop
  · rw [hop]; simp only [a1_J_eq, a2_J_eq]
  · exact absurd hP (by assumption)

/-- `x * z` decoded, the rest free -/
theorem op_R2 {x y z S : M} (hz : tg z = 2) (hx : a1 z = x) (hS : op x z = S) (hlt : sz S < sz z) :
    op y (J y (J (J z S) y)) = x := by
  obtain ⟨p1, p2, p3, hp1, -, -, hop⟩ := op_cases y (J y (J (J z S) y))
  have hg : msr (a1 (a1 (a1 (a2 (J y (J (J z S) y)))))) (a1 (a1 (a2 (J y (J (J z S) y))))) <
      msr y (J y (J (J z S) y)) := by
    simp only [a1_J_eq, a2_J_eq]
    exact msr_lt_of_max_lt (by simp only [szJ]; have := sz_a1 z; have := szP y; have := szP S; omega)
  rw [dif_pos hg] at hp1
  subst hp1
  have hc2 : P2 y (J y (J (J z S) y)) ∧
      msr (a1 (a1 (a1 (a2 (J y (J (J z S) y)))))) (a1 (a1 (a2 (J y (J (J z S) y))))) <
        msr y (J y (J (J z S) y)) ∧
      a2 (a1 (a2 (J y (J (J z S) y)))) =
        op (a1 (a1 (a1 (a2 (J y (J (J z S) y)))))) (a1 (a1 (a2 (J y (J (J z S) y))))) := by
    refine ⟨⟨rfl, rfl, rfl, rfl, rfl, hz⟩, hg, ?_⟩
    simp only [a1_J_eq, a2_J_eq]
    rw [hx, hS]
  split at hop
  · rename_i h
    exfalso
    obtain ⟨-, -, -, -, -, h6, -⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h6
    have e := congrArg sz h6
    have := sz_a2 S
    omega
  · rw [hop]
    simp only [a1_J_eq, a2_J_eq]
    exact hx

/-- `(z * (x * z)) * y` decoded, `x * z` free -/
theorem op_R3 {x y z S3 : M} (hy : tg y = 2) (hay : a1 y = J z (J x z))
    (hS3 : op (a1 y) y = S3) (hlt : sz S3 < sz y) : op y (J y S3) = x := by
  obtain ⟨p1, p2, p3, -, hp2, -, hop⟩ := op_cases y (J y S3)
  have hg : msr (a1 y) (y) < msr y (J y S3) :=
    msr_lt_of_max_lt (by simp only [szJ]; have := sz_a1 y; have := szP S3; omega)
  rw [dif_pos hg] at hp2
  subst hp2
  have hc3 : P3 y (J y S3) ∧ msr (a1 y) (y) < msr y (J y S3) ∧
      a2 (J y S3) = op (a1 y) y := by
    refine ⟨⟨rfl, rfl, hy, ?_, ?_, ?_⟩, hg, ?_⟩
    · simp only [hay, tg_J_eq]
    · simp only [hay, a2_J_eq, tg_J_eq]
    · simp only [hay, a1_J_eq, a2_J_eq]
    · simp only [a2_J_eq]
      exact hS3.symm
  split at hop
  · rename_i h
    exfalso
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    have e := congrArg sz h7
    have := sz_a2 S3
    omega
  · split at hop
    · rename_i h
      exfalso
      obtain ⟨⟨-, -, -, -, h5, -⟩, -, -⟩ := h
      simp only [a2_J_eq] at h5
      have e := congrArg sz h5
      have := sz_a2 S3
      omega
    · rw [hop]
      simp only [hay, a1_J_eq, a2_J_eq]

/-- both `x * z` and `(z * (x * z)) * y` decoded -/
theorem op_R4 {x y z S1 S3 : M} (hz : tg z = 2) (hx : a1 z = x) (hS1 : op x z = S1)
    (hlt1 : sz S1 < sz z) (hy : tg y = 2) (hay : a1 y = J z S1)
    (hS3 : op (a1 y) y = S3) (hlt3 : sz S3 < sz y) : op y (J y S3) = x := by
  obtain ⟨p1, p2, p3, -, hp2, hp3, hop⟩ := op_cases y (J y S3)
  have hyz : sz z < sz y := by
    have e := sz_a1 y
    rw [hay, szJ] at e
    have := szP S1; omega
  have hg2 : msr (a1 y) (y) < msr y (J y S3) :=
    msr_lt_of_max_lt (by simp only [szJ]; have := sz_a1 y; have := szP S3; omega)
  have hg3 : msr (a1 (a1 (a1 y))) (a1 (a1 y)) < msr y (J y S3) := by
    simp only [hay, a1_J_eq]
    exact msr_lt_of_max_lt (by simp only [szJ]; have := sz_a1 z; have := szP S3; omega)
  rw [dif_pos hg2] at hp2
  subst hp2
  rw [dif_pos hg3] at hp3
  subst hp3
  have hc4 : P4 y (J y S3) ∧ msr (a1 y) (y) < msr y (J y S3) ∧
      msr (a1 (a1 (a1 y))) (a1 (a1 y)) < msr y (J y S3) ∧
      a2 (J y S3) = op (a1 y) y ∧
      a2 (a1 y) = op (a1 (a1 (a1 y))) (a1 (a1 y)) := by
    refine ⟨⟨rfl, rfl, hy, ?_, ?_⟩, hg2, hg3, ?_, ?_⟩
    · simp only [hay, tg_J_eq]
    · simp only [hay, a1_J_eq]
      exact hz
    · simp only [a2_J_eq]
      exact hS3.symm
    · simp only [hay, a1_J_eq, a2_J_eq]
      rw [hx, hS1]
  split at hop
  · rename_i h
    exfalso
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    have e := congrArg sz h7
    have := sz_a2 S3
    omega
  · split at hop
    · rename_i h
      exfalso
      obtain ⟨⟨-, -, -, -, h5, -⟩, -, -⟩ := h
      simp only [a2_J_eq] at h5
      have e := congrArg sz h5
      have := sz_a2 S3
      omega
    · split at hop
      · rename_i h
        exfalso
        obtain ⟨⟨-, -, -, -, -, h6⟩, -, -⟩ := h
        simp only [hay, a1_J_eq, a2_J_eq] at h6
        have e := congrArg sz h6
        have := sz_a2 S1
        omega
      · rw [hop]
        simp only [hay, a1_J_eq]
        exact hx

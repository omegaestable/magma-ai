
theorem oc (u v : M) : ∃ r1 r2 r3 r4 r5 r6 : M,
    r1 = (if h : W u (K1 v) < W u v then op u (K1 v) else J u v) ∧
    r2 = (if h : W (K1 v) (a2 (a1 v)) < W u v then op (K1 v) (a2 (a1 v)) else J u v) ∧
    r3 = (if h : W u (K2 v) < W u v then op u (K2 v) else J u v) ∧
    r4 = (if h : W (K2 v) (a2 (a1 v)) < W u v then op (K2 v) (a2 (a1 v)) else J u v) ∧
    r5 = (if h : W (L1 u) (a2 u) < W u v then op (L1 u) (a2 u) else J u v) ∧
    r6 = (if h : W (L2 u) (a2 u) < W u v then op (L2 u) (a2 u) else J u v) ∧
    op u v = (
  if tg v = 3 ∧ tg (a2 v) ≠ 1 ∧ r1 = a1 (a1 v) ∧ r2 = a2 v then K1 v
  else if tg v = 3 ∧ tg (a2 (a1 v)) = 3 ∧ r3 = a1 (a1 v) ∧ r4 = a2 v then K2 v
  else if tg u ≠ 1 ∧ tg (a1 u) ≠ 1 ∧ r5 = v then E u v
  else if tg u ≠ 1 ∧ tg (a2 u) = 3 ∧ r6 = v then E u v
  else J u v) :=
  ⟨_, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- the tag fires on the (N2,N3) pair when N1 and N2 are free: every guard is `rfl` -/
theorem tag (x y z : M) (h3 : op x z = J x z) :
    op (J (J y x) z) (J x z) = E (J (J y x) z) (J x z) := by
  obtain ⟨r1, r2, r3, r4, r5, r6, -, -, -, -, hr5, -, hop⟩ := oc (J (J y x) z) (J x z)
  have g5 : W (L1 (J (J y x) z)) (a2 (J (J y x) z)) < W (J (J y x) z) (J x z) := by
    refine gu ?_ ?_ <;> simp only [L1, q1J, q2J, sJ] <;> have := szp x <;> have := szp y <;>
      have := szp z <;> omega
  have h5 : r5 = J x z := by rw [hr5, dif_pos g5]; simpa only [L1, q1J, q2J] using h3
  rw [hop, if_neg (by simp), if_neg (by simp), if_pos ⟨by simp, by simp, h5⟩]

/-- the root decodes the tag: both certificates are `rfl` -/
theorem root (x y z : M) (h1 : op y x = J y x) (h3 : op x z = J x z) :
    op y (E (J (J y x) z) (J x z)) = x := by
  obtain ⟨r1, r2, r3, r4, r5, r6, hr1, hr2, -, -, -, -, hop⟩ := oc y (E (J (J y x) z) (J x z))
  have g1 : W y (K1 (E (J (J y x) z) (J x z))) < W y (E (J (J y x) z) (J x z)) := by
    refine gm (Nat.le_refl _) ?_ <;> simp only [K1, q1E, q2E, q1J, q2J, sE, sJ] <;>
      have := szp y <;> have := szp z <;> omega
  have g2 : W (K1 (E (J (J y x) z) (J x z))) (a2 (a1 (E (J (J y x) z) (J x z))))
      < W y (E (J (J y x) z) (J x z)) := by
    refine gv ?_ ?_ <;> simp only [K1, q1E, q2E, q1J, q2J, sE, sJ] <;>
      have := szp x <;> have := szp y <;> have := szp z <;> omega
  have e1 : r1 = J y x := by rw [hr1, dif_pos g1]; simpa only [K1, q1E, q2E, q1J] using h1
  have e2 : r2 = J x z := by rw [hr2, dif_pos g2]; simpa only [K1, q1E, q2E, q1J, q2J] using h3
  rw [hop, if_pos ⟨by simp, by simp, by simpa only [q1E, q1J] using e1, by simpa only [q2E] using e2⟩]
  simp only [K1, q2E, q1J]

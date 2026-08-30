theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
@[simp] theorem sz_J (a b : M) : sz (M.J a b) = sz a + sz b + 1 := rfl

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 : M,
    p1 = (if hs1 : msr (a2 (a1 (a1 u))) (a2 v) < msr u v then op (a2 (a1 (a1 u))) (a2 v) else J u v) ∧
    p2 = (if hs2 : msr (a2 (a2 (a1 u))) (v) < msr u v then op (a2 (a2 (a1 u))) (v) else J u v) ∧
    p3 = (if hs3 : msr (a2 (a1 u)) (a2 (a1 (a1 (a1 u)))) < msr u v then op (a2 (a1 u)) (a2 (a1 (a1 (a1 u)))) else J u v) ∧
    p4 = (if hs4 : msr (a2 (a1 u)) (a2 (a2 (a1 u))) < msr u v then op (a2 (a1 u)) (a2 (a2 (a1 u))) else J u v) ∧
    p5 = (if hs5 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v) ∧
    p6 = (if hs6 : msr (a2 (a2 u)) (a2 v) < msr u v then op (a2 (a2 u)) (a2 v) else J u v) ∧
    p7 = (if hs7 : msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else J u v) ∧
    p8 = (if hs8 : msr (p7) (a1 (a2 v)) < msr u v then op (p7) (a1 (a2 v)) else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 u)
  else if P2 u v then a2 (a1 u)
  else if P3 u v ∧ msr (a2 (a1 (a1 u))) (a2 v) < msr u v ∧ a1 (a1 (a1 u)) = p1 then a2 (a1 u)
  else if P4 u v then a2 (a1 u)
  else if P5 u v ∧ msr (a2 (a2 (a1 u))) (v) < msr u v ∧ a1 (a2 (a1 u)) = p2 then a2 (a1 u)
  else if P6 u v ∧ msr (a2 (a1 u)) (a2 (a1 (a1 (a1 u)))) < msr u v ∧ v = p3 then a2 (a1 u)
  else if P7 u v then a2 (a1 u)
  else if P8 u v ∧ msr (a2 (a1 u)) (a2 (a2 (a1 u))) < msr u v ∧ v = p4 then a2 (a1 u)
  else if P9 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a1 u = p5 then a1 v
  else if P10 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a1 u = p5 then a1 v
  else if P11 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (a2 (a2 u)) (a2 v) < msr u v ∧ a1 u = p5 ∧ a1 (a2 u) = p6 then a1 v
  else if P12 u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (p7) (a1 (a2 v)) < msr u v ∧ u = p8 then a1 v
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- the digest: `op` is free, or an L-decode (rules 1-8, result `a2 (a1 u)`) or an R-decode
    (rules 9-12, result `a1 v`). -/
theorem TR (u v : M) : op u v = J u v ∨
    (tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ op u v = a2 (a1 u)) ∨
    (tg v = 2 ∧ op u v = a1 v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, -, -, -, -, -, -, -, -, hop⟩ := op_cases u v
  by_cases c1 : P1 u v
  · exact Or.inr (Or.inl ⟨c1.1, c1.2.1, c1.2.2.1, by rw [hop, if_pos c1]⟩)
  rw [if_neg c1] at hop
  by_cases c2 : P2 u v
  · exact Or.inr (Or.inl ⟨c2.1, c2.2.1, c2.2.2.1, by rw [hop, if_pos c2]⟩)
  rw [if_neg c2] at hop
  by_cases c3 : P3 u v ∧ msr (a2 (a1 (a1 u))) (a2 v) < msr u v ∧ a1 (a1 (a1 u)) = p1
  · exact Or.inr (Or.inl ⟨c3.1.1, c3.1.2.1, c3.1.2.2.1, by rw [hop, if_pos c3]⟩)
  rw [if_neg c3] at hop
  by_cases c4 : P4 u v
  · exact Or.inr (Or.inl ⟨c4.1, c4.2.1, c4.2.2.1, by rw [hop, if_pos c4]⟩)
  rw [if_neg c4] at hop
  by_cases c5 : P5 u v ∧ msr (a2 (a2 (a1 u))) (v) < msr u v ∧ a1 (a2 (a1 u)) = p2
  · exact Or.inr (Or.inl ⟨c5.1.1, c5.1.2.1, c5.1.2.2.1, by rw [hop, if_pos c5]⟩)
  rw [if_neg c5] at hop
  by_cases c6 : P6 u v ∧ msr (a2 (a1 u)) (a2 (a1 (a1 (a1 u)))) < msr u v ∧ v = p3
  · exact Or.inr (Or.inl ⟨c6.1.1, c6.1.2.1, c6.1.2.2.1, by rw [hop, if_pos c6]⟩)
  rw [if_neg c6] at hop
  by_cases c7 : P7 u v
  · exact Or.inr (Or.inl ⟨c7.1, c7.2.1, c7.2.2.1, by rw [hop, if_pos c7]⟩)
  rw [if_neg c7] at hop
  by_cases c8 : P8 u v ∧ msr (a2 (a1 u)) (a2 (a2 (a1 u))) < msr u v ∧ v = p4
  · exact Or.inr (Or.inl ⟨c8.1.1, c8.1.2.1, c8.1.2.2.1, by rw [hop, if_pos c8]⟩)
  rw [if_neg c8] at hop
  by_cases c9 : P9 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a1 u = p5
  · exact Or.inr (Or.inr ⟨c9.1.2.1, by rw [hop, if_pos c9]⟩)
  rw [if_neg c9] at hop
  by_cases c10 : P10 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a1 u = p5
  · exact Or.inr (Or.inr ⟨c10.1.2.1, by rw [hop, if_pos c10]⟩)
  rw [if_neg c10] at hop
  by_cases c11 : P11 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (a2 (a2 u)) (a2 v) < msr u v ∧ a1 u = p5 ∧ a1 (a2 u) = p6
  · exact Or.inr (Or.inr ⟨c11.1.2.1, by rw [hop, if_pos c11]⟩)
  rw [if_neg c11] at hop
  by_cases c12 : P12 u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (p7) (a1 (a2 v)) < msr u v ∧ u = p8
  · exact Or.inr (Or.inr ⟨c12.1.1, by rw [hop, if_pos c12]⟩)
  rw [if_neg c12] at hop
  exact Or.inl hop

/-- sizes: a decode is strictly smaller than the side it came from -/
theorem SZ (u v : M) : op u v = J u v ∨ sz (op u v) + 3 ≤ sz u ∨ sz (op u v) < sz v := by
  rcases TR u v with h | ⟨h1, h2, -, h4⟩ | ⟨h1, h2⟩
  · exact Or.inl h
  · refine Or.inr (Or.inl ?_)
    have e1 := sz_tg u h1
    have e2 := sz_tg (a1 u) h2
    have e3 := sz_pos (a1 (a1 u))
    have e4 := sz_pos (a2 u)
    rw [h4]; omega
  · refine Or.inr (Or.inr ?_)
    rw [h2]; exact sz_a1_lt h1

/-- THE LAW: x = ((y * x) * y) * (x * (y * z)) -/
theorem law (x y z : M) : op (op (op (y) (x)) (y)) (op (x) (op (y) (z))) = x := by
  sorry

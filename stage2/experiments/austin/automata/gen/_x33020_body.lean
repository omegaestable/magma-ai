theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
@[simp] theorem szJ (a b : M) : sz (M.J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp only [a1_J_eq, szJ]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp only [a2_J_eq, szJ]; have := sz_pos a; omega

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 : M,
    p1 = (if hs1 : msr (u) (a1 (a1 v)) < msr u v then op (u) (a1 (a1 v)) else J u v) ∧
    p2 = (if hs2 : msr (a1 (a2 (a1 v))) (a2 (a2 (a1 v))) < msr u v then op (a1 (a2 (a1 v))) (a2 (a2 (a1 v))) else J u v) ∧
    p3 = (if hs3 : msr (a1 (a1 v)) (a2 (a1 v)) < msr u v then op (a1 (a1 v)) (a2 (a1 v)) else J u v) ∧
    p4 = (if hs4 : msr (a1 v) (u) < msr u v then op (a1 v) (u) else J u v) ∧
    p5 = (if hs5 : msr (a2 (p1)) (p1) < msr u v then op (a2 (p1)) (p1) else J u v) ∧
    p6 = (if hs6 : msr (u) (a2 (a1 u)) < msr u v then op (u) (a2 (a1 u)) else J u v) ∧
    p7 = (if hs7 : msr (a2 (a1 u)) (a1 u) < msr u v then op (a2 (a1 u)) (a1 u) else J u v) ∧
    p8 = (if hs8 : msr (a1 (a2 u)) (a2 (a2 u)) < msr u v then op (a1 (a2 u)) (a2 (a2 u)) else J u v) ∧
    p9 = (if hs9 : msr (a1 u) (a2 u) < msr u v then op (a1 u) (a2 u) else J u v) ∧
    p10 = (if hs10 : msr (a2 (p7)) (p7) < msr u v then op (a2 (p7)) (p7) else J u v) ∧
    op u v = (
  if P1 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a1 (a2 (a1 v))) (a2 (a2 (a1 v))) < msr u v ∧ msr (a1 (a1 v)) (a2 (a1 v)) < msr u v ∧ msr (a1 v) (u) < msr u v ∧ a2 (a2 (a1 v)) = p1 ∧ a2 (a1 v) = p2 ∧ a1 v = p3 ∧ v = p4 then a1 (a1 v)
  else if P2 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a2 (p1)) (p1) < msr u v ∧ msr (a1 (a1 v)) (a2 (a1 v)) < msr u v ∧ msr (a1 v) (u) < msr u v ∧ tg (p1) = 2 ∧ a2 (a1 v) = p5 ∧ a1 v = p3 ∧ v = p4 then a1 (a1 v)
  else if P3 u v ∧ msr (u) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (a1 u) < msr u v ∧ msr (a1 (a2 u)) (a2 (a2 u)) < msr u v ∧ msr (a1 u) (a2 u) < msr u v ∧ msr (a1 v) (u) < msr u v ∧ J (u) (a2 (a1 u)) = p6 ∧ a2 (a2 u) = p7 ∧ a2 u = p8 ∧ u = p9 ∧ a1 v = p7 ∧ v = p4 then a2 (a1 u)
  else if P4 u v ∧ msr (u) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (a1 u) < msr u v ∧ msr (a2 (p7)) (p7) < msr u v ∧ msr (a1 u) (a2 u) < msr u v ∧ msr (a1 v) (u) < msr u v ∧ J (u) (a2 (a1 u)) = p6 ∧ tg (p7) = 2 ∧ a2 u = p10 ∧ u = p9 ∧ a1 v = p7 ∧ v = p4 then a2 (a1 u)
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

theorem TRs (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ a2 v = u ∧
    ((tg (a1 v) = 2 ∧ op u v = a1 (a1 v) ∧ op (a1 (a1 v)) (a2 (a1 v)) = a1 v ∧
        ((tg (a2 (a1 v)) = 2 ∧ op u (a1 (a1 v)) = a2 (a2 (a1 v)) ∧
            op (a1 (a2 (a1 v))) (a2 (a2 (a1 v))) = a2 (a1 v)) ∨
          (tg (op u (a1 (a1 v))) = 2 ∧
            op (a2 (op u (a1 (a1 v)))) (op u (a1 (a1 v))) = a2 (a1 v)))) ∨
      (tg u = 2 ∧ tg (a1 u) = 2 ∧ op u v = a2 (a1 u) ∧ op (a2 (a1 u)) (a1 u) = a1 v))) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hp10, hop⟩ :=
    op_cases u v
  rw [hop]
  split
  · rename_i h
    have c1 := h.2.2.2.2.2.1
    have c2 := h.2.2.2.2.2.2.1
    have c3 := h.2.2.2.2.2.2.2.1
    rw [dif_pos h.2.1] at hp1
    rw [dif_pos h.2.2.1] at hp2
    rw [dif_pos h.2.2.2.1] at hp3
    rw [hp1] at c1
    rw [hp2] at c2
    rw [hp3] at c3
    exact Or.inr ⟨h.1.1, h.1.2.2.2.symm, Or.inl ⟨h.1.2.1, rfl, c3.symm,
      Or.inl ⟨h.1.2.2.1, c1.symm, c2.symm⟩⟩⟩
  · split
    · rename_i h
      have tq := h.2.2.2.2.2.1
      have c5 := h.2.2.2.2.2.2.1
      have c3 := h.2.2.2.2.2.2.2.1
      have g5 := h.2.2.1
      rw [dif_pos h.2.1] at hp1
      rw [hp1] at tq g5 hp5
      rw [dif_pos g5] at hp5
      rw [hp5] at c5
      rw [dif_pos h.2.2.2.1] at hp3
      rw [hp3] at c3
      exact Or.inr ⟨h.1.1, h.1.2.2.symm, Or.inl ⟨h.1.2.1, rfl, c3.symm, Or.inr ⟨tq, c5.symm⟩⟩⟩
    · split
      · rename_i h
        have c7 := h.2.2.2.2.2.2.2.2.2.2.1
        rw [dif_pos h.2.2.1] at hp7
        rw [hp7] at c7
        exact Or.inr ⟨h.1.1, h.1.2.1.symm, Or.inr ⟨h.1.2.2.1, h.1.2.2.2.1, rfl, c7.symm⟩⟩
      · split
        · rename_i h
          have c7 := h.2.2.2.2.2.2.2.2.2.2.1
          rw [dif_pos h.2.2.1] at hp7
          rw [hp7] at c7
          exact Or.inr ⟨h.1.1, h.1.2.1.symm, Or.inr ⟨h.1.2.2.1, h.1.2.2.2, rfl, c7.symm⟩⟩
        · exact Or.inl rfl

theorem Wsz {u v : M} (h : sz v ≤ sz u) : op u v = J u v := by
  rcases TRs u v with hz | ⟨tv, av, -⟩
  · exact hz
  · exfalso; have q := sz_a2_lt tv; rw [av] at q; omega

theorem Wlt {u v : M} (h : op u v ≠ J u v) : sz (op u v) < sz v := by
  rcases TRs u v with hz | ⟨tv, av, hd⟩
  · exact absurd hz h
  · have q1 := sz_a2_lt tv
    rw [av] at q1
    rcases hd with ⟨t1, hr, -, -⟩ | ⟨tu, tau, hr, -⟩
    · rw [hr]; have := sz_a1_lt t1; have := sz_a1_lt tv; omega
    · rw [hr]; have := sz_a2_lt tau; have := sz_a1_lt tu; omega

theorem NY {u w : M} (hw : sz w < sz (a1 u)) (hu : sz (a1 u) < sz u)
    (h : a2 (a2 w) = J u (a1 w)) : False := by
  have e := congrArg sz h
  simp only [szJ] at e
  have := sz_a2 w; have := sz_a2 (a2 w); omega

theorem NX {u w : M} (hw : sz w < sz (a1 u)) (hu : sz (a1 u) < sz u)
    (h : op (a1 w) (J u (a1 w)) = a2 w) : False := by
  have b1 := sz_a1 w
  have b2 := sz_a2 w
  rcases TRs (a1 w) (J u (a1 w)) with hz | ⟨-, -, hA | hB⟩
  · rw [hz] at h; have e := congrArg sz h; simp only [szJ] at e; omega
  · obtain ⟨-, hr, -, -⟩ := hA
    simp only [a1_J_eq] at hr
    rw [hr] at h
    have e := congrArg sz h; omega
  · obtain ⟨-, -, hr, hq⟩ := hB
    simp only [a1_J_eq] at hq
    rw [hr] at h
    rw [h] at hq
    by_cases hz : op (a2 w) (a1 (a1 w)) = J (a2 w) (a1 (a1 w))
    · rw [hz] at hq
      have e := congrArg a1 hq
      simp only [a1_J_eq] at e
      have e2 := congrArg sz e; omega
    · have q := Wlt hz
      rw [hq] at q
      have b3 := sz_a1 (a1 w); omega

theorem op_R12 (u v : M) (t0 : tg v = 2) (t1 : tg (a1 v) = 2) (hv : a2 v = u)
    (k3 : op (a1 (a1 v)) (a2 (a1 v)) = a1 v) (k4 : op (a1 v) u = v)
    (H : (tg (a2 (a1 v)) = 2 ∧ op u (a1 (a1 v)) = a2 (a2 (a1 v)) ∧
            op (a1 (a2 (a1 v))) (a2 (a2 (a1 v))) = a2 (a1 v))
       ∨ (tg (op u (a1 (a1 v))) = 2 ∧ sz (op u (a1 (a1 v))) < sz v ∧
            op (a2 (op u (a1 (a1 v)))) (op u (a1 (a1 v))) = a2 (a1 v))) :
    op u v = a1 (a1 v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, hp1, hp2, hp3, hp4, hp5, -, -, -, -, -, hop⟩ :=
    op_cases u v
  have s0 := sz_a1_lt t0
  have s0' := sz_a2_lt t0
  rw [hv] at s0'
  have s1 := sz_a1_lt t1
  have s1' := sz_a2_lt t1
  have s2 := sz_a1 (a2 (a1 v))
  have s3 := sz_a2 (a2 (a1 v))
  have s4 := sz_a2 (op u (a1 (a1 v)))
  have g1 : msr u (a1 (a1 v)) < msr u v := msr_lt_of_max_lt (by omega)
  have g2 : msr (a1 (a2 (a1 v))) (a2 (a2 (a1 v))) < msr u v := msr_lt_of_max_lt (by omega)
  have g3 : msr (a1 (a1 v)) (a2 (a1 v)) < msr u v := msr_lt_of_max_lt (by omega)
  have g4 : msr (a1 v) u < msr u v := msr_lt_of_max_lt (by omega)
  rw [dif_pos g1] at hp1
  rw [dif_pos g2] at hp2
  rw [dif_pos g3] at hp3
  rw [dif_pos g4] at hp4
  rw [hp1] at hp5
  rw [hop]
  split
  · rfl
  · split
    · rfl
    · rename_i h1 h2
      rcases H with ⟨d1, d2, d3⟩ | ⟨d1, d0, d2⟩
      · exact absurd ⟨⟨t0, t1, d1, hv.symm⟩, g1, g2, g3, g4, d2.symm.trans hp1.symm,
          d3.symm.trans hp2.symm, k3.symm.trans hp3.symm, k4.symm.trans hp4.symm⟩ h1
      · have g5 : msr (a2 (op u (a1 (a1 v)))) (op u (a1 (a1 v))) < msr u v :=
          msr_lt_of_max_lt (by omega)
        rw [dif_pos g5] at hp5
        exact absurd ⟨⟨t0, t1, hv.symm⟩, g1, (by rw [hp1]; exact g5), g3, g4,
          (by rw [hp1]; exact d1), d2.symm.trans hp5.symm, k3.symm.trans hp3.symm,
          k4.symm.trans hp4.symm⟩ h2

theorem op_R34 (u v : M) (t0 : tg v = 2) (hv : a2 v = u) (t1 : tg u = 2) (t2 : tg (a1 u) = 2)
    (k1 : op u (a2 (a1 u)) = J u (a2 (a1 u)))
    (k4 : op (a1 u) (a2 u) = u)
    (k5 : a1 v = op (a2 (a1 u)) (a1 u))
    (k6 : op (a1 v) u = v)
    (k7 : sz (a1 v) < sz (a1 u))
    (H : (tg (a2 u) = 2 ∧ a2 (a2 u) = a1 v ∧ op (a1 (a2 u)) (a2 (a2 u)) = a2 u)
       ∨ (tg (a1 v) = 2 ∧ op (a2 (a1 v)) (a1 v) = a2 u)) : op u v = a2 (a1 u) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, hp1, -, -, hp4, hp5, hp6, hp7, hp8, hp9, hp10, hop⟩ :=
    op_cases u v
  have s0 := sz_a1_lt t0
  have s0' := sz_a2_lt t0
  rw [hv] at s0'
  have q1 := sz_a1_lt t1
  have q1' := sz_a2_lt t1
  have q2 := sz_a1_lt t2
  have q2' := sz_a2_lt t2
  have q4 := sz_a1 (a1 v)
  have q5 := sz_a2 (a1 v)
  have q6 := sz_a1 (a2 u)
  have q7 := sz_a2 (a2 u)
  have hb : sz (a1 (a1 v)) ≤ sz u := by omega
  have g6 : msr u (a2 (a1 u)) < msr u v := msr_lt_of_max_lt (by omega)
  have g7 : msr (a2 (a1 u)) (a1 u) < msr u v := msr_lt_of_max_lt (by omega)
  have g8 : msr (a1 (a2 u)) (a2 (a2 u)) < msr u v := msr_lt_of_max_lt (by omega)
  have g9 : msr (a1 u) (a2 u) < msr u v := msr_lt_of_max_lt (by omega)
  have g4 : msr (a1 v) u < msr u v := msr_lt_of_max_lt (by omega)
  have g10 : msr (a2 (op (a2 (a1 u)) (a1 u))) (op (a2 (a1 u)) (a1 u)) < msr u v := by
    rw [← k5]; exact msr_lt_of_max_lt (by omega)
  rw [dif_pos g6] at hp6
  rw [dif_pos g7] at hp7
  rw [hp7] at hp10
  rw [dif_pos g10] at hp10
  rw [dif_pos g8] at hp8
  rw [dif_pos g9] at hp9
  rw [dif_pos g4] at hp4
  rw [hop]
  split
  · rename_i h
    exfalso
    have c1 := h.2.2.2.2.2.1
    rw [dif_pos h.2.1] at hp1
    rw [hp1, Wsz hb] at c1
    exact NY k7 q1 c1
  · split
    · rename_i h
      exfalso
      have c5 := h.2.2.2.2.2.2.1
      have g5 := h.2.2.1
      rw [dif_pos h.2.1] at hp1
      rw [hp1, Wsz hb] at g5 hp5
      rw [dif_pos g5] at hp5
      rw [hp5] at c5
      simp only [a2_J_eq] at c5
      exact NX k7 q1 c5.symm
    · split
      · rfl
      · split
        · rfl
        · rename_i h1 h2 h3 h4
          rcases H with ⟨d1, d2, d3⟩ | ⟨d1, d2⟩
          · exact absurd ⟨⟨t0, hv.symm, t1, t2, d1⟩, g6, g7, g8, g9, g4,
              k1.symm.trans hp6.symm, (d2.trans k5).trans hp7.symm, d3.symm.trans hp8.symm,
              k4.symm.trans hp9.symm, k5.trans hp7.symm, k6.symm.trans hp4.symm⟩ h3
          · exact absurd ⟨⟨t0, hv.symm, t1, t2⟩, g6, g7, (by rw [hp7]; exact g10), g9, g4,
              k1.symm.trans hp6.symm, (by rw [hp7, ← k5]; exact d1),
              (by rw [hp10, ← k5]; exact d2.symm), k4.symm.trans hp9.symm,
              k5.trans hp7.symm, k6.symm.trans hp4.symm⟩ h4

theorem main (x y z s1 s2 s3 s4 : M)
    (e1 : s1 = op y x) (e2 : s2 = op z s1) (e3 : s3 = op x s2) (e4 : s4 = op s3 y) :
    op y s4 = x := by
  by_cases h3 : op x s2 = J x s2
  · have E3 : s3 = J x s2 := e3.trans h3
    have h4 : op s3 y = J s3 y := by
      by_cases hh : op s3 y = J s3 y
      · exact hh
      exfalso
      rcases TRs s3 y with hz | ⟨ty, ay, -⟩
      · exact hh hz
      have qy := sz_tg y ty
      rw [ay, E3] at qy
      simp only [szJ] at qy
      have w1 := sz_pos (a1 y)
      have w4 := sz_pos x
      have w5 := sz_pos s2
      by_cases h1 : op y x = J y x
      · have E1 : s1 = J y x := e1.trans h1
        have n1 : a1 s1 = y := (congrArg a1 E1).trans (a1_J_eq y x)
        have n2 : a2 s1 = x := (congrArg a2 E1).trans (a2_J_eq y x)
        have eS := congrArg sz E1
        simp only [szJ] at eS
        by_cases h2 : op z s1 = J z s1
        · have eT := congrArg sz (e2.trans h2)
          simp only [szJ] at eT
          have := sz_pos z
          omega
        rcases TRs z s1 with hz2 | ⟨t1, aq, hD⟩
        · exact absurd hz2 h2
        rw [n2] at aq
        rcases hD with hA | hB
        · obtain ⟨tv, hr, hf, hs⟩ := hA
          rw [n1] at tv hr hf hs
          have hq : s2 = a1 y := e2.trans hr
          rcases hs with ⟨ti, hi1, hi2⟩ | ⟨ti, hi⟩
          · rw [← aq, ← hq, ← e3, ay] at hi1
            rw [ay] at ti
            have hd := sz_a2_lt ti
            rw [← hi1] at hd
            omega
          · rw [← aq, ← hq, ← e3, ay] at hi
            rw [← hq, ay] at hf
            rw [(congrArg a2 E3).trans (a2_J_eq x s2)] at hi
            have hys : y = s3 := hf.symm.trans hi
            rw [← hys] at ay
            have := congrArg sz ay
            have := sz_a2_lt ty
            omega
        · obtain ⟨tu, tau, hr, hq2⟩ := hB
          rw [n1] at hq2
          have hq : s2 = a2 (a1 z) := e2.trans hr
          rw [← hq] at hq2
          rw [← aq] at tu tau hq hq2
          have d1 := sz_a2_lt tau
          rw [← hq] at d1
          have d2 := sz_a1_lt tu
          by_cases hf2 : op s2 (a1 x) = J s2 (a1 x)
          · rw [hf2] at hq2
            have := congrArg sz hq2
            simp only [szJ] at this
            omega
          · have wq := Wlt hf2
            rw [hq2] at wq
            omega
      · rcases TRs y x with hz3 | ⟨tx, ax, -⟩
        · exact h1 hz3
        · have d := sz_a2_lt tx
          rw [ax] at d
          omega
    rw [e4, h4, E3]
    refine op_R12 y (J (J x s2) y) rfl rfl rfl h3 (by rw [← E3]; exact h4) ?_
    by_cases h2 : op z s1 = J z s1
    · have E2 : s2 = J z s1 := e2.trans h2
      refine Or.inl ⟨by rw [E2], ?_, ?_⟩
      · show op y x = a2 s2
        rw [E2]; exact e1.symm
      · show op (a1 s2) (a2 s2) = s2
        rw [E2]; exact h2
    · rcases TRs z s1 with hz2 | ⟨t1, aq, -⟩
      · exact absurd hz2 h2
      · refine Or.inr ⟨?_, ?_, ?_⟩
        · show tg (op y x) = 2
          rw [← e1]; exact t1
        · show sz (op y x) < sz (J (J x s2) y)
          simp only [szJ]
          have := sz_pos s2
          by_cases h1 : op y x = J y x
          · rw [h1]; simp only [szJ]; omega
          · have := Wlt h1; omega
        · show op (a2 (op y x)) (op y x) = s2
          rw [← e1, aq]; exact e2.symm
  · rcases TRs x s2 with hz | ⟨t2, aw, -⟩
    · exact absurd hz h3
    have hL := Wlt h3
    rw [← e3] at hL
    have w3 : sz x < sz s2 := by
      have q := sz_tg s2 t2
      rw [aw] at q
      have := sz_pos (a1 s2)
      omega
    have h2 : ¬ (op z s1 = J z s1) := by
      intro hc
      rw [e2.trans hc] at aw
      simp only [a2_J_eq] at aw
      rw [aw] at e1
      by_cases hf : op y x = J y x
      · rw [hf] at e1
        have := congrArg sz e1
        simp only [szJ] at this
        have := sz_pos y
        omega
      · have q := Wlt hf
        rw [← e1] at q
        omega
    rcases TRs z s1 with hz2 | ⟨t1, aq, hD⟩
    · exact absurd hz2 h2
    have w2 : sz s2 < sz s1 := by rw [e2]; exact Wlt h2
    have h1 : op y x = J y x := by
      by_cases hf : op y x = J y x
      · exact hf
      exfalso
      have q := Wlt hf
      rw [← e1] at q
      omega
    have E1 : s1 = J y x := e1.trans h1
    have n1 : a1 s1 = y := (congrArg a1 E1).trans (a1_J_eq y x)
    have n2 : a2 s1 = x := (congrArg a2 E1).trans (a2_J_eq y x)
    rw [n2] at aq
    rcases hD with hA | hB
    · obtain ⟨tv, hr, hf, hs⟩ := hA
      rw [n1] at tv hr hf hs
      have hq : s2 = a1 y := e2.trans hr
      rw [← hq] at hf
      have HP : (op s3 y = J s3 y) ∧
          ((tg (a2 y) = 2 ∧ a2 (a2 y) = s3 ∧ op (a1 (a2 y)) (a2 (a2 y)) = a2 y)
            ∨ (tg s3 = 2 ∧ op (a2 s3) s3 = a2 y)) := by
        rcases hs with ⟨ti, hi1, hi2⟩ | ⟨ti, hi⟩
        · rw [← aq, ← hq, ← e3] at hi1
          refine ⟨?_, Or.inl ⟨ti, hi1.symm, hi2⟩⟩
          by_cases hh : op s3 y = J s3 y
          · exact hh
          exfalso
          rcases TRs s3 y with hz4 | ⟨-, ay, -⟩
          · exact hh hz4
          rw [ay] at hi1 ti
          have hd := sz_a2_lt ti
          rw [← hi1] at hd
          omega
        · rw [← aq, ← hq, ← e3] at ti hi
          refine ⟨?_, Or.inr ⟨ti, hi⟩⟩
          by_cases hh : op s3 y = J s3 y
          · exact hh
          exfalso
          rcases TRs s3 y with hz4 | ⟨-, ay, -⟩
          · exact hh hz4
          rw [ay] at hi
          by_cases hf2 : op (a2 s3) s3 = J (a2 s3) s3
          · rw [hf2] at hi
            have := congrArg sz hi
            simp only [szJ] at this
            have := sz_pos (a2 s3)
            omega
          · have q := Wlt hf2
            rw [hi] at q
            omega
      obtain ⟨h4, HH⟩ := HP
      rw [e4, h4]
      refine (op_R34 y (J s3 y) rfl rfl tv (by rw [← hq]; exact t2) ?_ ?_ ?_ h4 ?_ HH).trans ?_
      · rw [← hq, aw]; exact h1
      · rw [← hq]; exact hf
      · show s3 = op (a2 (a1 y)) (a1 y)
        rw [← hq, aw]; exact e3
      · show sz s3 < sz (a1 y)
        rw [← hq]; exact hL
      · rw [← hq]; exact aw
    · obtain ⟨tu, tau, hr, -⟩ := hB
      exfalso
      have hq : s2 = a2 (a1 z) := e2.trans hr
      rw [← aq] at tu tau hq
      have d1 := sz_a2_lt tau
      rw [← hq] at d1
      have d2 := sz_a1_lt tu
      omega


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem szJ (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

theorem itec (R : M → Prop) {c : Prop} [inst : Decidable c] {a b : M}
    (h1 : c → R a) (h2 : ¬ c → R b) : R (if c then a else b) := by
  cases inst with
  | isTrue h => exact h1 h
  | isFalse h => exact h2 h

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 : M,
    p1 = (if hs1 : msr (a2 (a1 u)) (a2 v) < msr u v then op (a2 (a1 u)) (a2 v) else J u v) ∧
    p2 = (if hs2 : msr (v) (a2 v) < msr u v then op (v) (a2 v) else J u v) ∧
    p3 = (if hs3 : msr (a2 (a1 u)) (v) < msr u v then op (a2 (a1 u)) (v) else J u v) ∧
    p4 = (if hs4 : msr (p3) (v) < msr u v then op (p3) (v) else J u v) ∧
    p5 = (if hs5 : msr (a1 u) (a2 (a2 u)) < msr u v then op (a1 u) (a2 (a2 u)) else J u v) ∧
    p6 = (if hs6 : msr (a2 u) (a2 v) < msr u v then op (a2 u) (a2 v) else J u v) ∧
    p7 = (if hs7 : msr (a2 u) (v) < msr u v then op (a2 u) (v) else J u v) ∧
    p8 = (if hs8 : msr (p7) (v) < msr u v then op (p7) (v) else J u v) ∧
    p9 = (if hs9 : msr (u) (a2 (a1 (a1 v))) < msr u v then op (u) (a2 (a1 (a1 v))) else J u v) ∧
    p10 = (if hs10 : msr (u) (a2 u) < msr u v then op (u) (a2 u) else J u v) ∧
    p11 = (if hs11 : msr (u) (a2 v) < msr u v then op (u) (a2 v) else J u v) ∧
    p12 = (if hs12 : msr (u) (v) < msr u v then op (u) (v) else J u v) ∧
    p13 = (if hs13 : msr (p12) (v) < msr u v then op (p12) (v) else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 u)
  else if P2 u v ∧ msr (a2 (a1 u)) (a2 v) < msr u v ∧ a1 v = p1 then a2 (a1 u)
  else if P3 u v ∧ msr (v) (a2 v) < msr u v ∧ msr (a2 (a1 u)) (v) < msr u v ∧ msr (p3) (v) < msr u v ∧ a1 v = p2 ∧ v = p4 then a2 (a1 u)
  else if P4 u v then a2 u
  else if P5 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ a1 (a2 u) = p5 then a2 u
  else if P6 u v ∧ msr (a2 u) (a2 v) < msr u v ∧ a1 v = p6 then a2 u
  else if P7 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ msr (a2 u) (a2 v) < msr u v ∧ a1 (a2 u) = p5 ∧ a1 v = p6 then a2 u
  else if P8 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ msr (a2 u) (v) < msr u v ∧ msr (p7) (v) < msr u v ∧ a1 (a2 u) = p5 ∧ a1 v = p2 ∧ v = p8 then a2 u
  else if P9 u v then a1 (a1 v)
  else if P10 u v ∧ msr (u) (a2 (a1 (a1 v))) < msr u v ∧ a1 (a1 (a1 v)) = p9 then a1 (a1 v)
  else if P11 u v ∧ msr (u) (a2 u) < msr u v ∧ msr (u) (a2 v) < msr u v ∧ a1 u = p10 ∧ a1 v = p11 then u
  else if P12 u v ∧ msr (u) (a2 u) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ msr (u) (v) < msr u v ∧ msr (p12) (v) < msr u v ∧ a1 u = p10 ∧ a1 v = p2 ∧ v = p13 then u
  else if P13 u v ∧ msr (v) (a2 v) < msr u v ∧ a1 v = p2 then a2 (a1 u)
  else if P14 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ a1 (a2 u) = p5 ∧ a1 v = p2 then a2 u
  else if P15 u v ∧ msr (u) (a2 u) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ a1 u = p10 ∧ a1 v = p2 then u
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

def Dg (u v w : M) : Prop := w = J u v ∨ (tg u = 2 ∧ tg v = 2 ∧
  ((w = a2 u ∧ ((tg (a1 v) = 2 ∧ a1 (a1 v) = a2 u ∧ a2 (a1 v) = a2 v)
      ∨ a1 v = op (a2 u) (a2 v) ∨ a1 v = op v (a2 v)))
   ∨ (w = u ∧ a1 u = op u (a2 u))))

theorem Dg0 (u v : M) : Dg u v (op u v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13,
    hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hp10, hp11, hp12, hp13, hop⟩ := op_cases u v
  rw [hop]
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨A1, -, A3, A4, A5, A6, A7⟩ := k
    exact Or.inr ⟨A1, A4, Or.inl ⟨A3, Or.inl ⟨A5, A6.symm.trans A3, A7⟩⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, A3, A4⟩, gg, ge⟩ := k
    rw [dif_pos gg] at hp1
    rw [A3] at hp1
    exact Or.inr ⟨A1, A4, Or.inl ⟨A3, Or.inr (Or.inl (ge.trans hp1))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, A3, -, -, A6⟩, g2, -, -, ge, -⟩ := k
    rw [dif_pos g2] at hp2
    exact Or.inr ⟨A1, A6, Or.inl ⟨A3, Or.inr (Or.inr (ge.trans hp2))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨A1, A2, A3, A4, A5, -, -, -, -⟩ := k
    exact Or.inr ⟨A1, A2, Or.inl ⟨rfl, Or.inl ⟨A3, A4.symm, A5⟩⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2, A3, A4, A5, -⟩, -, -⟩ := k
    exact Or.inr ⟨A1, A2, Or.inl ⟨rfl, Or.inl ⟨A3, A4.symm, A5⟩⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2, -, -, -, -⟩, gg, ge⟩ := k
    rw [dif_pos gg] at hp6
    exact Or.inr ⟨A1, A2, Or.inl ⟨rfl, Or.inr (Or.inl (ge.trans hp6))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2, -⟩, -, gg, -, ge⟩ := k
    rw [dif_pos gg] at hp6
    exact Or.inr ⟨A1, A2, Or.inl ⟨rfl, Or.inr (Or.inl (ge.trans hp6))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, -, A4⟩, -, g2, -, -, -, ge, -⟩ := k
    rw [dif_pos g2] at hp2
    exact Or.inr ⟨A1, A4, Or.inl ⟨rfl, Or.inr (Or.inr (ge.trans hp2))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · exfalso
    obtain ⟨-, -, -, A4, -, A6, -, A8⟩ := k
    rw [A8] at A4 A6
    have h1 := sz_a1_lt A4
    have h2 := sz_a1 (a1 u)
    have h3 := congrArg sz A6
    omega
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, -, A4, A5⟩, gg, ge⟩ := k
    rw [A5] at A4 gg ge hp9
    rw [dif_pos gg] at hp9
    exact Or.inr ⟨A4, A1, Or.inr ⟨A5, ge.trans hp9⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2⟩, g10, -, e1, -⟩ := k
    rw [dif_pos g10] at hp10
    exact Or.inr ⟨A2, A1, Or.inr ⟨rfl, e1.trans hp10⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, A3⟩, g10, -, -, -, e1, -, -⟩ := k
    rw [dif_pos g10] at hp10
    exact Or.inr ⟨A1, A3, Or.inr ⟨rfl, e1.trans hp10⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, A3, -, -, A6⟩, g2, ge⟩ := k
    rw [dif_pos g2] at hp2
    exact Or.inr ⟨A1, A6, Or.inl ⟨A3, Or.inr (Or.inr (ge.trans hp2))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, -, A4⟩, -, g2, -, ge⟩ := k
    rw [dif_pos g2] at hp2
    exact Or.inr ⟨A1, A4, Or.inl ⟨rfl, Or.inr (Or.inr (ge.trans hp2))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, A3⟩, g10, -, e1, -⟩ := k
    rw [dif_pos g10] at hp10
    exact Or.inr ⟨A1, A3, Or.inr ⟨rfl, e1.trans hp10⟩⟩
  exact Or.inl rfl

theorem NOQ (n : Nat) : ∀ u : M, sz u ≤ n → tg u = 2 → a1 u ≠ op u (a2 u) := by
  induction n with
  | zero => intro u hn _ _; have := sz_pos u; omega
  | succ n ih =>
    intro u hn ht he
    have h2 := sz_a1_lt ht
    have h3 := sz_a2_lt ht
    rcases Dg0 u (a2 u) with hf | ⟨-, hv, hd⟩
    · rw [hf] at he
      have := congrArg sz he
      rw [szJ] at this
      have := sz_pos (a2 u)
      omega
    · rcases hd with ⟨hr, hb⟩ | ⟨hr, -⟩
      · rw [hr] at he
        rcases hb with ⟨-, q2, -⟩ | q | q
        · have e1 := sz_a1_lt hv
          have e2 := sz_a1 (a1 (a2 u))
          have e3 := congrArg sz q2
          omega
        · exact ih (a2 u) (by omega) hv q
        · exact ih (a2 u) (by omega) hv q
      · rw [hr] at he
        have := congrArg sz he
        omega

theorem Dg3 (u v : M) : op u v = J u v ∨ (tg u = 2 ∧ tg v = 2 ∧ op u v = a2 u ∧
    ((tg (a1 v) = 2 ∧ a1 (a1 v) = a2 u ∧ a2 (a1 v) = a2 v) ∨ a1 v = op (a2 u) (a2 v))) := by
  rcases Dg0 u v with hf | ⟨hu, hv, hd⟩
  · exact Or.inl hf
  · rcases hd with ⟨hr, hb⟩ | ⟨-, hq⟩
    · rcases hb with q | q | q
      · exact Or.inr ⟨hu, hv, hr, Or.inl q⟩
      · exact Or.inr ⟨hu, hv, hr, Or.inr q⟩
      · exact absurd q (NOQ (sz v) v (Nat.le_refl _) hv)
    · exact absurd hq (NOQ (sz u) u (Nat.le_refl _) hu)

theorem DD (u v : M) : op u v = J u v ∨ (tg u = 2 ∧ op u v = a2 u) := by
  rcases Dg3 u v with h | ⟨hu, -, hr, -⟩
  · exact Or.inl h
  · exact Or.inr ⟨hu, hr⟩

theorem key {b w : M} (hw : tg w = 2)
    (hi : (tg (a1 b) = 2 ∧ a1 (a1 b) = w ∧ a2 (a1 b) = a2 b) ∨ a1 b = op w (a2 b))
    (ho : (tg (a1 b) = 2 ∧ a1 (a1 b) = a2 w ∧ a2 (a1 b) = a2 b) ∨ a1 b = op (a2 w) (a2 b)) :
    False := by
  have s1 := sz_a2_lt hw
  have s2 := sz_a2 (a2 w)
  have s3 := sz_pos (a2 b)
  have s4 := sz_a1 (a1 b)
  rcases hi with ⟨q1, q2, -⟩ | q
  · have s5 := sz_a1_lt q1
    rcases ho with ⟨-, r2, -⟩ | r
    · have := congrArg sz (q2.symm.trans r2); omega
    · rcases DD (a2 w) (a2 b) with hd | ⟨-, hd⟩ <;> rw [hd] at r
      · rw [r] at q2
        simp only [a1_J_eq] at q2
        have := congrArg sz q2; omega
      · have e1 := congrArg sz r
        have e2 := congrArg sz q2
        omega
  · rcases ho with ⟨r1, r2, -⟩ | r
    · have s5 := sz_a1_lt r1
      rcases DD w (a2 b) with hd | ⟨-, hd⟩ <;> rw [hd] at q
      · rw [q] at r2
        simp only [a1_J_eq] at r2
        have := congrArg sz r2; omega
      · have e1 := congrArg sz q
        have e2 := congrArg sz r2
        omega
    · rcases DD w (a2 b) with hd | ⟨-, hd⟩ <;> rw [hd] at q <;>
        rcases DD (a2 w) (a2 b) with he | ⟨ht, he⟩ <;> rw [he] at r
      · have := congrArg sz (q.symm.trans r)
        rw [szJ, szJ] at this; omega
      · have := congrArg sz (q.symm.trans r)
        rw [szJ] at this; omega
      · have := congrArg sz (q.symm.trans r)
        rw [szJ] at this; omega
      · have h9 := sz_a2_lt ht
        have := congrArg sz (q.symm.trans r)
        omega

theorem FREE (a b : M) : op (op a b) b = J (op a b) b := by
  by_cases hF : op (op a b) b = J (op a b) b
  · exact hF
  exfalso
  rcases Dg3 (op a b) b with h | ⟨hu, hv, -, hb⟩
  · exact hF h
  rcases Dg3 a b with hi | ⟨-, -, hres, hbi⟩
  · rw [hi] at hb
    simp only [a2_J_eq] at hb
    rcases hb with ⟨q1, q2, -⟩ | q
    · have e1 := sz_a1_lt hv
      have e2 := sz_a1_lt q1
      have e3 := congrArg sz q2
      omega
    · exact NOQ (sz b) b (Nat.le_refl _) hv q
  · rw [hres] at hb hu
    exact key hu hbi hb

theorem fires {u v : M} (hu : tg u = 2) (hv : tg v = 2)
    (g1 : msr (a2 u) (a2 v) < msr u v)
    (gv : a1 v = op (a2 u) (a2 v))
    (h : (tg (a1 u) = 2 ∧ a2 (a1 u) = a2 u)
       ∨ (tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a1 (a1 (a2 u)) = a1 u ∧ a2 (a1 (a2 u)) = a2 (a2 u))
       ∨ (tg (a2 u) = 2 ∧ a1 (a2 u) = op (a1 u) (a2 (a2 u))
            ∧ msr (a1 u) (a2 (a2 u)) < msr u v)) :
    op u v = a2 u := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13,
    hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hp10, hp11, hp12, hp13, hop⟩ := op_cases u v
  rw [hop]
  refine itec (fun t => t = a2 u) (fun k => k.2.2.1) (fun _ => ?_)
  refine itec (fun t => t = a2 u) (fun k => k.1.2.2.1) (fun n2 => ?_)
  refine itec (fun t => t = a2 u) (fun k => k.1.2.2.1) (fun _ => ?_)
  refine itec (fun t => t = a2 u) (fun _ => rfl) (fun _ => ?_)
  refine itec (fun t => t = a2 u) (fun _ => rfl) (fun _ => ?_)
  refine itec (fun t => t = a2 u) (fun _ => rfl) (fun n6 => ?_)
  refine itec (fun t => t = a2 u) (fun _ => rfl) (fun n7 => ?_)
  exfalso
  rcases h with ⟨ht, he⟩ | ⟨t1, t2, t3, t4⟩ | ⟨t1, t2, t3⟩
  · have gg : msr (a2 (a1 u)) (a2 v) < msr u v := by rw [he]; exact g1
    rw [dif_pos gg] at hp1
    rw [he] at hp1
    exact n2 ⟨⟨hu, ht, he, hv⟩, gg, gv.trans hp1.symm⟩
  · rw [dif_pos g1] at hp6
    exact n6 ⟨⟨hu, hv, t1, t2, t3.symm, t4⟩, g1, gv.trans hp6.symm⟩
  · rw [dif_pos t3] at hp5
    rw [dif_pos g1] at hp6
    exact n7 ⟨⟨hu, hv, t1⟩, t3, g1, t2.trans hp5.symm, gv.trans hp6.symm⟩

theorem law (x y z : M) : op (op (op (y) (x)) (x)) (op (op (x) (z)) (z)) = x := by
  rw [FREE y x, FREE x z]
  show op (J (op y x) x) (J (op x z) z) = a2 (J (op y x) x)
  refine fires rfl rfl ?_ ?_ ?_
  · simp only [a2_J_eq]
    apply msr_lt_of_max_lt
    simp only [szJ]
    have := sz_pos (op y x); have := sz_pos (op x z); have := sz_pos x; have := sz_pos z
    omega
  · simp only [a1_J_eq, a2_J_eq]
  · simp only [a1_J_eq, a2_J_eq]
    rcases Dg3 y x with hf | ⟨-, hx, hres, hb⟩
    · exact Or.inl ⟨by rw [hf]; rfl, by rw [hf]; rfl⟩
    · rcases hb with ⟨q1, q2, q3⟩ | q
      · exact Or.inr (Or.inl ⟨hx, q1, q2.trans hres.symm, q3⟩)
      · refine Or.inr (Or.inr ⟨hx, q.trans (by rw [hres]), ?_⟩)
        apply msr_lt_of_max_lt
        simp only [szJ]
        have := sz_a2 x; have := sz_pos (op x z); have := sz_pos z; have := sz_pos x
        omega

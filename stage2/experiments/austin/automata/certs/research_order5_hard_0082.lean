import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .g _ => 1
  | .J _ _ => 2

def a1 : M → M
  | .J x _ => x
  | t => t

def a2 : M → M
  | .J _ x => x
  | t => t

def sz : M → Nat
  | .g _ => 1
  | .J b0 b1 => sz b0 + sz b1 + 1

theorem sz_a1 (u : M) : sz (a1 u) ≤ sz u := by cases u <;> simp [a1, sz] <;> omega
theorem sz_a2 (u : M) : sz (a2 u) ≤ sz u := by cases u <;> simp [a2, sz] <;> omega
theorem tg_J (t : M) (h : tg t = 2) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem tg_g (t : M) (h : tg t ≠ 2) : ∃ n, t = M.g n := by cases t <;> simp_all [tg]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 1 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n) = M.g n := rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n) = M.g n := rfl

/-- G0 : v = J u (J u w) -/
def G0 (u v : M) : Prop := tg v = 2 ∧ a1 v = u ∧ tg (a2 v) = 2 ∧ a1 (a2 v) = u

instance (u v : M) : Decidable (G0 u v) := by unfold G0; infer_instance

theorem G0_sz {u v : M} (h : G0 u v) : sz v = sz u + sz u + sz (a2 (a2 v)) + 2 := by
  obtain ⟨h1, h2, h3, h4⟩ := h
  obtain ⟨b0, b1, rfl⟩ := tg_J _ h1
  simp at h2 h3 h4
  obtain ⟨c0, c1, rfl⟩ := tg_J _ h3
  simp at h4; subst h2; subst h4; simp [sz]; omega

def op (u v : M) : M :=
  if hg : G0 u v then
    let w := a2 (a2 v)
    if tg w = 2 ∧ tg (a2 w) = 2 ∧ a2 (a2 w) = u then a1 (a2 w)
    else
      let p := op (a1 u) u
      if tg w = 2 ∧ a2 w = p then a1 u
      else if tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ a1 (a2 (a2 u)) = w ∧ a2 (a2 (a2 u)) = a1 u then a1 u
      else if hs : sz (a1 p) + sz p < sz u + sz v then
        (if w = op (a1 p) p then a1 u else J u v)
      else J u v
  else J u v
termination_by sz u + sz v
decreasing_by
  · have := G0_sz hg; have := sz_a1 u; omega
  · exact hs

def inst : Magma M := { op := op }

theorem eqf (a b : M) (h : sz a ≠ sz b) : (a = b) = False := eq_false (fun e => h (congrArg sz e))

theorem op_nJ {u v : M} (h : ¬ G0 u v) : op u v = J u v := by rw [op.eq_1, dif_neg h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (M.g 0) (M.g 1) (M.g 2)
  revert this
  change ¬ g 0 = op (op (g 1) (op (g 2) (g 1))) (op (op (g 0) (g 0)) (g 1))
  simp (disch := decide) [op_nJ]

theorem TR3 (u v : M) : op u v = J u v ∨ (G0 u v ∧ (op u v = a1 u ∨ ∃ z x, a2 (a2 v) = J z (J x u) ∧ op u v = x)) := by
  by_cases hg : G0 u v
  · rw [op.eq_1, dif_pos hg]
    simp only
    split
    · rename_i h1
      right
      refine ⟨hg, Or.inr ?_⟩
      obtain ⟨h1, h2, h3⟩ := h1
      obtain ⟨b0, b1, hb⟩ := tg_J _ h1
      rw [hb] at h2 h3 ⊢
      simp only [a2_J_eq] at h2 h3
      obtain ⟨c0, c1, rfl⟩ := tg_J _ h2
      simp only [a2_J_eq] at h3
      subst h3
      exact ⟨b0, c0, rfl, rfl⟩
    · split
      · exact Or.inr ⟨hg, Or.inl rfl⟩
      · split
        · exact Or.inr ⟨hg, Or.inl rfl⟩
        · split
          · split
            · exact Or.inr ⟨hg, Or.inl rfl⟩
            · left; rfl
          · left; rfl
  · left; exact op_nJ hg

theorem TR (u v : M) : op u v = J u v ∨ (G0 u v ∧ (op u v = a1 u ∨ sz (op u v) < sz (a2 (a2 v)))) := by
  rcases TR3 u v with h | ⟨hg, h | ⟨z, x, h, h2⟩⟩
  · exact Or.inl h
  · exact Or.inr ⟨hg, Or.inl h⟩
  · right; refine ⟨hg, Or.inr ?_⟩; rw [h, h2]; simp [sz]; omega

theorem TRs (u v : M) : op u v = J u v ∨ (G0 u v ∧ sz (op u v) < sz v) := by
  rcases TR u v with h | ⟨hg, h | h⟩
  · exact Or.inl h
  · right; refine ⟨hg, ?_⟩; rw [h]; have := G0_sz hg; have := sz_a1 u; omega
  · right; refine ⟨hg, ?_⟩; have := G0_sz hg; omega

theorem hs_ok {u v : M} (hg : G0 u v) : sz (a1 (op (a1 u) u)) + sz (op (a1 u) u) < sz u + sz v := by
  have g := G0_sz hg
  have s1 := sz_a1 u
  have s2 := sz_a1 (a1 u)
  have s3 := sz_a1 (op (a1 u) u)
  have s4 := sz_a1 (a1 (a1 u))
  rcases TR (a1 u) u with h | ⟨hg2, h | h⟩
  · rw [h]; simp [sz]; omega
  · rw [h]; omega
  · have := G0_sz hg2; have := sz_a2 (a2 u); have := sz_a2 u; omega

theorem op_R1 (u z x : M) : op u (J u (J u (J z (J x u)))) = x := by
  rw [op.eq_1]; simp [G0]

theorem op_R2 (u z : M) : op u (J u (J u (J z (op (a1 u) u)))) = a1 u := by
  have tr := TR (a1 u) u
  have s1 := sz_a1 u
  have s2 := sz_a1 (a1 u)
  have s3 := sz_a2 u
  have s4 := sz_a2 (a2 u)
  rw [op.eq_1]
  generalize op (a1 u) u = p at *
  simp [G0]
  intro h1 h2
  obtain ⟨b0, b1, rfl⟩ := tg_J _ h1
  simp at h2; subst h2
  rcases tr with h | ⟨hg, h | h⟩
  · simp_all
  · have := congrArg sz h; simp [sz] at this; omega
  · have := G0_sz hg; simp [sz] at h; omega

theorem G0_sz2 {u v : M} (h : G0 u v) : sz (a2 v) = sz u + sz (a2 (a2 v)) + 1 := by
  obtain ⟨h1, h2, h3, h4⟩ := h
  obtain ⟨b0, b1, rfl⟩ := tg_J _ h1
  simp at h2 h3 h4
  obtain ⟨c0, c1, rfl⟩ := tg_J _ h3
  simp at h4; subst h2; subst h4; simp [sz]

theorem G0_a1 {u v : M} (h : G0 u v) : a1 v = u := h.2.1
theorem G0_a12 {u v : M} (h : G0 u v) : a1 (a2 v) = u := h.2.2.2

theorem op_R4 (u : M) : op u (J u (J u (op (a1 (op (a1 u) u)) (op (a1 u) u)))) = a1 u := by
  have hg : G0 u (J u (J u (op (a1 (op (a1 u) u)) (op (a1 u) u)))) := by simp [G0]
  have hs := hs_ok hg
  have tp := TR (a1 u) u
  have tq := TR (a1 (op (a1 u) u)) (op (a1 u) u)
  have s1 := sz_a1 u
  have s2 := sz_a1 (a1 u)
  have s3 := sz_a2 u
  have s4 := sz_a2 (a2 u)
  have s5 := sz_a1 (a1 (a1 u))
  have s6 := sz_a1 (a1 (a1 (a1 u)))
  have s7 := sz_a1 (op (a1 u) u)
  have s8 := sz_a1 (a1 (op (a1 u) u))
  have s9 := sz_a2 (op (a1 u) u)
  have s10 := sz_a2 (a2 (op (a1 u) u))
  rw [op.eq_1, dif_pos hg]
  simp only
  generalize op (a1 (op (a1 u) u)) (op (a1 u) u) = q at *
  generalize op (a1 u) u = p at *
  simp [hs]
  intro h1 h2 h3
  obtain ⟨q1, q2, rfl⟩ := tg_J _ h1
  simp at h2 h3 ⊢
  obtain ⟨q3, q4, rfl⟩ := tg_J _ h2
  simp at h3 ⊢; subst h3
  rcases tq with h | ⟨hg2, h | h⟩
  · rcases tp with h' | ⟨hg3, h' | h'⟩
    · grind [sz, a1, a2]
    · have := G0_sz hg3; grind [sz, a1, a2]
    · have := G0_sz hg3; grind [sz, a1, a2]
  · rcases tp with h' | ⟨hg3, h' | h'⟩
    · have := G0_sz hg2; grind [sz, a1, a2]
    · have := G0_sz hg3; have := G0_sz hg2; grind [sz, a1, a2]
    · have := G0_sz hg3; have := G0_sz hg2; grind [sz, a1, a2]
  · rcases tp with h' | ⟨hg3, h' | h'⟩
    · have := G0_sz hg2; grind [sz, a1, a2]
    · have := G0_sz hg3; have := G0_sz hg2; grind [sz, a1, a2]
    · have := G0_sz hg3; have := G0_sz hg2; grind [sz, a1, a2]

theorem sz_tg (t : M) (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz]

theorem G0_J {u a b : M} (h : G0 u (J a b)) : a = u ∧ tg b = 2 ∧ a1 b = u := by
  obtain ⟨_, h2, h3, h4⟩ := h; simp at h2 h3 h4; exact ⟨h2, h3, h4⟩

theorem TR4 (u v : M) : op u v = J u v ∨ (G0 u v ∧ (
    (∃ z x, a2 (a2 v) = J z (J x u) ∧ op u v = x) ∨
    (∃ z, a2 (a2 v) = J z (op (a1 u) u) ∧ op u v = a1 u) ∨
    (∃ a z3, u = J a (J z3 (J (a2 (a2 v)) a)) ∧ op u v = a1 u) ∨
    (a2 (a2 v) = op (a1 (op (a1 u) u)) (op (a1 u) u) ∧ op u v = a1 u))) := by
  by_cases hg : G0 u v
  · rw [op.eq_1, dif_pos hg]
    simp only
    split
    · rename_i h1
      refine Or.inr ⟨hg, Or.inl ?_⟩
      obtain ⟨h1, h2, h3⟩ := h1
      obtain ⟨b0, b1, hb⟩ := tg_J _ h1
      rw [hb] at h2 h3 ⊢
      simp only [a2_J_eq] at h2 h3
      obtain ⟨c0, c1, rfl⟩ := tg_J _ h2
      simp only [a2_J_eq] at h3
      subst h3
      exact ⟨b0, c0, rfl, rfl⟩
    · split
      · rename_i h1 h2
        refine Or.inr ⟨hg, Or.inr (Or.inl ?_)⟩
        obtain ⟨h2, h3⟩ := h2
        obtain ⟨b0, b1, hb⟩ := tg_J _ h2
        rw [hb] at h3 ⊢
        simp only [a2_J_eq] at h3
        subst h3
        exact ⟨b0, rfl, rfl⟩
      · split
        · rename_i h1 h2 h3
          refine Or.inr ⟨hg, Or.inr (Or.inr (Or.inl ?_))⟩
          obtain ⟨h3, h4, h5, h6, h7⟩ := h3
          obtain ⟨a, u2, rfl⟩ := tg_J _ h3
          simp only [a2_J_eq, a1_J_eq] at h4 h5 h6 h7 ⊢
          obtain ⟨z3, u3, rfl⟩ := tg_J _ h4
          simp only [a2_J_eq] at h5 h6 h7
          obtain ⟨w, a', rfl⟩ := tg_J _ h5
          simp only [a2_J_eq, a1_J_eq] at h6 h7
          subst h6; subst h7
          first | exact ⟨_, _, rfl, trivial⟩ | exact ⟨_, _, rfl, rfl⟩ | exact ⟨_, _, trivial, rfl⟩
        · split
          · split
            · rename_i h4
              exact Or.inr ⟨hg, Or.inr (Or.inr (Or.inr ⟨h4, rfl⟩))⟩
            · left; rfl
          · left; rfl
  · left; exact op_nJ hg

/-- step 4 with z = y: no rule fires on `J y (J y P)` for `P = op x y`. -/
theorem S4 (x y : M) : op y (J y (J y (op x y))) = J y (J y (J y (op x y))) := by
  have hg : G0 y (J y (J y (op x y))) := by simp [G0]
  have t1 := TR4 x y
  have t2 := TR3 (a1 y) y
  have t3 := TR3 (a1 (op (a1 y) y)) (op (a1 y) y)
  have t4 := TR3 (a1 x) x
  have t5 := TR3 (a1 (op (a1 x) x)) (op (a1 x) x)
  rw [op.eq_1, dif_pos hg]
  simp only
  split
  · rename_i h
    simp only [a2_J_eq, a1_J_eq, tg_J_eq] at h ⊢
    obtain ⟨h1, h2, h3⟩ := h
    obtain ⟨b0, b1, hb⟩ := tg_J _ h1
    rw [hb] at h2 h3 ⊢
    simp only [a2_J_eq] at h2 h3
    obtain ⟨c0, c1, rfl⟩ := tg_J _ h2
    simp only [a2_J_eq] at h3
    subst h3
    grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, G0_sz, G0_sz2, G0_a1, G0_a12]
  · split
    · rename_i h1 h
      simp only [a2_J_eq, a1_J_eq, tg_J_eq] at h ⊢
      obtain ⟨h2, h3⟩ := h
      obtain ⟨b0, b1, hb⟩ := tg_J _ h2
      rw [hb] at h3 ⊢
      simp only [a2_J_eq] at h3
      subst h3
      grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, G0_sz, G0_sz2, G0_a1, G0_a12]
    · split
      · rename_i h1 h2 h
        simp only [a2_J_eq, a1_J_eq, tg_J_eq] at h ⊢
        obtain ⟨h3, h4, h5, h6, h7⟩ := h
        obtain ⟨a, u2, hy⟩ := tg_J _ h3
        subst hy
        simp only [a2_J_eq, a1_J_eq] at *
        obtain ⟨z3, u3, rfl⟩ := tg_J _ h4
        simp only [a2_J_eq] at *
        obtain ⟨w, a', rfl⟩ := tg_J _ h5
        simp only [a2_J_eq, a1_J_eq] at *
        subst h7
        grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, G0_sz, G0_sz2, G0_a1, G0_a12]
      · split
        · split
          · rename_i h
            simp only [a2_J_eq, a1_J_eq, tg_J_eq] at h ⊢
            grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, G0_sz, G0_sz2, G0_a1, G0_a12]
          · rfl
        · rfl

theorem SELF (u : M) : op u (J u (J u u)) = J u (J u (J u u)) := by
  have hg : G0 u (J u (J u u)) := by simp [G0]
  have t2 := TR3 (a1 u) u
  have t3 := TR3 (a1 (op (a1 u) u)) (op (a1 u) u)
  rw [op.eq_1, dif_pos hg]
  simp only
  split
  · rename_i h
    simp only [a2_J_eq, a1_J_eq, tg_J_eq] at h ⊢
    obtain ⟨h1, h2, h3⟩ := h
    obtain ⟨b0, b1, rfl⟩ := tg_J _ h1
    simp only [a2_J_eq] at h2 h3
    obtain ⟨c0, c1, rfl⟩ := tg_J _ h2
    simp only [a2_J_eq] at h3
    grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, G0_sz, G0_sz2, G0_a1, G0_a12]
  · split
    · rename_i h1 h
      simp only [a2_J_eq, a1_J_eq, tg_J_eq] at h ⊢
      obtain ⟨h2, h3⟩ := h
      obtain ⟨b0, b1, rfl⟩ := tg_J _ h2
      simp only [a2_J_eq] at h3
      grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, G0_sz, G0_sz2, G0_a1, G0_a12]
    · split
      · rename_i h1 h2 h
        simp only [a2_J_eq, a1_J_eq, tg_J_eq] at h ⊢
        obtain ⟨h3, h4, h5, h6, h7⟩ := h
        obtain ⟨a, u2, rfl⟩ := tg_J _ h3
        simp only [a2_J_eq, a1_J_eq] at *
        obtain ⟨z3, u3, rfl⟩ := tg_J _ h4
        simp only [a2_J_eq] at *
        obtain ⟨w, a', rfl⟩ := tg_J _ h5
        simp only [a2_J_eq, a1_J_eq] at *
        grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, G0_sz, G0_sz2, G0_a1, G0_a12]
      · split
        · split
          · rename_i h
            simp only [a2_J_eq, a1_J_eq, tg_J_eq] at h ⊢
            grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, G0_sz, G0_sz2, G0_a1, G0_a12]
          · rfl
        · rfl

theorem nG0_self (y : M) : ¬ G0 y (J y y) := by
  intro h
  obtain ⟨_, _, h3, h4⟩ := h
  simp only [a2_J_eq] at h3 h4
  obtain ⟨y1, y2, rfl⟩ := tg_J _ h3
  simp only [a1_J_eq] at h4
  have := congrArg sz h4; simp [sz] at this; omega

theorem N3 (x y z : M) : op y (op z (op x y)) = J y (op z (op x y)) := by
  by_cases hg : G0 y (op z (op x y))
  · have tp := TR3 x y
    have tq := TR3 z (op x y)
    have s1 := sz_a1 y
    have s2 := sz_a1 z
    have s3 := sz_a2 y
    have s4 := sz_a2 (a2 y)
    have s5 := sz_a1 x
    have s6 := sz_a2 (op x y)
    have s7 := sz_a2 (a2 (op x y))
    have key : x = y ∧ z = y ∧ op x y = J y y := by
      generalize op z (op x y) = q at *
      generalize op x y = p at *
      grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, G0_sz, G0_sz2, G0_a1, G0_a12]
    obtain ⟨hx, hz, h⟩ := key
    rw [hx] at h ⊢; rw [hz, h, op_nJ (nG0_self y), SELF]
  · exact op_nJ hg

theorem N4 (x y z : M) : op y (J y (op z (op x y))) = J y (J y (op z (op x y))) := by
  by_cases hg : G0 y (J y (op z (op x y)))
  · have tp := TR3 x y
    have tq := TR3 z (op x y)
    have s1 := sz_a1 y
    have s2 := sz_a1 z
    have s3 := sz_a2 y
    have s4 := sz_a2 (a2 y)
    have s5 := sz_a1 x
    have s6 := sz_a2 (op x y)
    have s7 := sz_a2 (a2 (op x y))
    have key : z = y ∧ op z (op x y) = J y (op x y) := by
      generalize op z (op x y) = q at *
      generalize op x y = p at *
      grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, G0_sz, G0_sz2, G0_a1, G0_a12]
    obtain ⟨hz, h⟩ := key
    rw [hz] at h ⊢; rw [h, S4]
  · exact op_nJ hg

theorem law (x y z : M) : op y (op y (op y (op z (op x y)))) = x := by
  rw [N3, N4]
  rcases TR3 x y with hP | ⟨hg, hP | ⟨z1, x1, hy, hP⟩⟩
  · rw [hP]
    rcases TR3 z (J x y) with hQ | ⟨hg2, -⟩
    · rw [hQ]; exact op_R1 y z x
    · obtain ⟨hxz, hty, hy1⟩ := G0_J hg2
      subst hxz
      have r := op_R4 y
      rw [hy1, hP] at r
      simp only [a1_J_eq] at r
      exact r
  · rw [hP]
    have hy1 : a1 y = x := hg.2.1
    rcases TR3 z (a1 x) with hQ | ⟨hg2, -⟩
    · rw [hQ]; have r := op_R2 y z; rw [hy1, hP] at r; exact r
    · have r := op_R4 y; rw [hy1, hP, hg2.2.1] at r; exact r
  · rw [hP]
    have hy1 : a1 y = x := hg.2.1
    rcases TR3 z x1 with hQ | ⟨hg2, -⟩
    · rw [hQ]; have r := op_R2 y z; rw [hy1, hP] at r; exact r
    · have r := op_R4 y; rw [hy1, hP, hg2.2.1] at r; exact r

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

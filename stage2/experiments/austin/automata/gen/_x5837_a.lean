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
theorem sz_tg (t : M) (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1, a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 1 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n) = M.g n := rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n) = M.g n := rfl
/-- the recursion measure: lexicographic (max size, total size), packed into one Nat -/
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b) < max (sz u) (sz v)) : msr a b < msr u v := by
  unfold msr
  have h1 : sz a + sz b ≤ 2 * max (sz a) (sz b) := by omega
  have h2 : (max (sz a) (sz b) + 1) * (max (sz a) (sz b) + 1) ≤ max (sz u) (sz v) * max (sz u) (sz v) := Nat.mul_le_mul h h
  simp only [Nat.mul_succ, Nat.succ_mul] at h2
  omega
theorem msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b) = max (sz u) (sz v)) (h2 : sz a + sz b < sz u + sz v) : msr a b < msr u v := by
  unfold msr; rw [h]; omega

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ tg (a1 (a2 (a2 v))) = 2 ∧ u = a2 (a1 (a2 (a2 v))) ∧ u = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := v = u ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a1 u) = a2 (a1 (a2 (a1 u))) ∧ a1 (a1 u) = a2 (a2 (a1 u))
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := v = u ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ a1 (a1 u) = a2 (a2 (a1 u)) ∧ tg (a1 (a1 u)) = 2 ∧ tg (a2 (a1 (a1 u))) = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := v = u ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ a1 (a1 u) = a2 (a2 (a1 u))
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def P8 (u v : M) : Prop := v = u ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a1 u) = 2 ∧ tg (a1 (a1 u)) = 2 ∧ tg (a2 (a1 (a1 u))) = 2
instance (u v : M) : Decidable (P8 u v) := by unfold P8; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a2 u)) (u) < msr u v then op (a1 (a2 u)) (u) else J u v
  let p2 := if hs2 : msr (u) (u) < msr u v then op (u) (u) else J u v
  let p3 := if hs3 : msr (a1 u) (u) < msr u v then op (a1 u) (u) else J u v
  let p4 := if hs4 : msr (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) < msr u v then op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) else J u v
  let p5 := if hs5 : msr (a1 (a1 u)) (a1 (a1 u)) < msr u v then op (a1 (a1 u)) (a1 (a1 u)) else J u v
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a1 (a2 u)) (u) < msr u v ∧ a1 (a2 (a2 v)) = p1 then a1 v
  else if P3 u v ∧ msr (u) (u) < msr u v ∧ a1 (a2 (a2 v)) = p2 then a1 v
  else if P4 u v ∧ msr (a1 (a2 u)) (u) < msr u v ∧ a2 (a2 v) = p1 ∧ a1 (a2 u) = p1 then a1 v
  else if P5 u v ∧ msr (a1 u) (u) < msr u v ∧ a1 u = p3 then a1 (a1 u)
  else if P6 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) < msr u v ∧ a1 u = p3 ∧ a1 (a2 (a1 u)) = p4 then a1 (a1 u)
  else if P7 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a1 u)) (a1 (a1 u)) < msr u v ∧ a1 u = p3 ∧ a1 (a2 (a1 u)) = p5 then a1 (a1 u)
  else if P8 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) < msr u v ∧ a1 u = p3 ∧ a2 (a1 u) = p4 ∧ a1 (a2 (a1 (a1 u))) = p4 then a1 (a1 u)
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v ∨ P8 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (op (g 1) (g 0))) (op (op (g 2) (g 2)) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6, P7, P8]

theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem msr_lt_both {a b u v : M} (ha : sz a < sz v) (hb : sz b < sz v) : msr a b < msr u v :=
  msr_lt_of_max_lt (by omega)

/-- the unfolding of `op` with the five nested calls packed away as opaque variables -/
theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 : M,
    p1 = (if hs1 : msr (a1 (a2 u)) u < msr u v then op (a1 (a2 u)) u else J u v) ∧
    p2 = (if hs2 : msr u u < msr u v then op u u else J u v) ∧
    p3 = (if hs3 : msr (a1 u) u < msr u v then op (a1 u) u else J u v) ∧
    p4 = (if hs4 : msr (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) < msr u v then op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) else J u v) ∧
    p5 = (if hs5 : msr (a1 (a1 u)) (a1 (a1 u)) < msr u v then op (a1 (a1 u)) (a1 (a1 u)) else J u v) ∧
    op u v = (
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a1 (a2 u)) u < msr u v ∧ a1 (a2 (a2 v)) = p1 then a1 v
  else if P3 u v ∧ msr u u < msr u v ∧ a1 (a2 (a2 v)) = p2 then a1 v
  else if P4 u v ∧ msr (a1 (a2 u)) u < msr u v ∧ a2 (a2 v) = p1 ∧ a1 (a2 u) = p1 then a1 v
  else if P5 u v ∧ msr (a1 u) u < msr u v ∧ a1 u = p3 then a1 (a1 u)
  else if P6 u v ∧ msr (a1 u) u < msr u v ∧ msr (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) < msr u v ∧ a1 u = p3 ∧ a1 (a2 (a1 u)) = p4 then a1 (a1 u)
  else if P7 u v ∧ msr (a1 u) u < msr u v ∧ msr (a1 (a1 u)) (a1 (a1 u)) < msr u v ∧ a1 u = p3 ∧ a1 (a2 (a1 u)) = p5 then a1 (a1 u)
  else if P8 u v ∧ msr (a1 u) u < msr u v ∧ msr (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) < msr u v ∧ a1 u = p3 ∧ a2 (a1 u) = p4 ∧ a1 (a2 (a1 (a1 u))) = p4 then a1 (a1 u)
  else J u v) :=
  ⟨_, _, _, _, _, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or bucket B (u = a1 (a2 v), value a1 v), or bucket C (v = u, value a1 (a1 u)) -/
theorem TR (u v : M) : op u v = J u v ∨
    (tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ op u v = a1 v ∧ (
       (tg (a2 (a2 v)) = 2 ∧ (
          (tg (a1 (a2 (a2 v))) = 2 ∧ u = a2 (a1 (a2 (a2 v))) ∧ u = a2 (a2 (a2 v))) ∨
          (u = a2 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 (a2 (a2 v)) = op (a1 (a2 u)) u) ∨
          (u = a2 (a2 (a2 v)) ∧ op u u = a1 (a2 (a2 v))))) ∨
       (tg u = 2 ∧ tg (a2 u) = 2 ∧ a2 (a2 v) = op (a1 (a2 u)) u ∧ a1 (a2 u) = op (a1 (a2 u)) u))) ∨
    (v = u ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a1 u) = 2 ∧ op (a1 u) u = a1 u ∧ op u v = a1 (a1 u) ∧ (
       (tg (a2 (a1 u)) = 2 ∧ (
          (tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a1 u) = a2 (a1 (a2 (a1 u))) ∧ a1 (a1 u) = a2 (a2 (a1 u))) ∨
          (a1 (a1 u) = a2 (a2 (a1 u)) ∧ tg (a1 (a1 u)) = 2 ∧ tg (a2 (a1 (a1 u))) = 2 ∧ a1 (a2 (a1 u)) = op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))) ∨
          (a1 (a1 u) = a2 (a2 (a1 u)) ∧ op (a1 (a1 u)) (a1 (a1 u)) = a1 (a2 (a1 u))))) ∨
       (tg (a1 (a1 u)) = 2 ∧ tg (a2 (a1 (a1 u))) = 2 ∧ a2 (a1 u) = op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) ∧ a1 (a2 (a1 (a1 u))) = op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))))) := by
  obtain ⟨p1, p2, p3, p4, p5, hp1, hp2, hp3, hp4, hp5, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h
    exact Or.inr (Or.inl ⟨h.1, h.2.1, h.2.2.1, rfl, Or.inl ⟨h.2.2.2.1, Or.inl ⟨h.2.2.2.2.1, h.2.2.2.2.2.1, h.2.2.2.2.2.2⟩⟩⟩)
  · split
    · rename_i h1 h
      obtain ⟨hP2, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr (Or.inl ⟨hP2.1, hP2.2.1, hP2.2.2.1, rfl, Or.inl ⟨hP2.2.2.2.1, Or.inr (Or.inl ⟨hP2.2.2.2.2.1, hP2.2.2.2.2.2.1, hP2.2.2.2.2.2.2, he⟩)⟩⟩)
    · split
      · rename_i h1 h2 h
        obtain ⟨hP3, hs2, he⟩ := h
        rw [dif_pos hs2] at hp2; subst hp2
        exact Or.inr (Or.inl ⟨hP3.1, hP3.2.1, hP3.2.2.1, rfl, Or.inl ⟨hP3.2.2.2.1, Or.inr (Or.inr ⟨hP3.2.2.2.2, he.symm⟩)⟩⟩)
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨hP4, hs1, heA, heB⟩ := h
          rw [dif_pos hs1] at hp1; subst hp1
          exact Or.inr (Or.inl ⟨hP4.1, hP4.2.1, hP4.2.2.1, rfl, Or.inr ⟨hP4.2.2.2.1, hP4.2.2.2.2, heA, heB⟩⟩)
        · split
          · rename_i h1 h2 h3 h4 h
            obtain ⟨hP5, hs3, he⟩ := h
            rw [dif_pos hs3] at hp3; subst hp3
            exact Or.inr (Or.inr ⟨hP5.1, hP5.2.1, hP5.2.2.1, hP5.2.2.2.1, hP5.2.2.2.2.1, he.symm, rfl,
              Or.inl ⟨hP5.2.2.2.2.2.1, Or.inl ⟨hP5.2.2.2.2.2.2.1, hP5.2.2.2.2.2.2.2.1, hP5.2.2.2.2.2.2.2.2⟩⟩⟩)
          · split
            · rename_i h1 h2 h3 h4 h5 h
              obtain ⟨hP6, hs3, hs4, heA, heB⟩ := h
              rw [dif_pos hs3] at hp3; subst hp3
              rw [dif_pos hs4] at hp4; subst hp4
              exact Or.inr (Or.inr ⟨hP6.1, hP6.2.1, hP6.2.2.1, hP6.2.2.2.1, hP6.2.2.2.2.1, heA.symm, rfl,
                Or.inl ⟨hP6.2.2.2.2.2.1, Or.inr (Or.inl ⟨hP6.2.2.2.2.2.2.1, hP6.2.2.2.2.2.2.2.1, hP6.2.2.2.2.2.2.2.2, heB⟩)⟩⟩)
            · split
              · rename_i h1 h2 h3 h4 h5 h6 h
                obtain ⟨hP7, hs3, hs5, heA, heB⟩ := h
                rw [dif_pos hs3] at hp3; subst hp3
                rw [dif_pos hs5] at hp5; subst hp5
                exact Or.inr (Or.inr ⟨hP7.1, hP7.2.1, hP7.2.2.1, hP7.2.2.2.1, hP7.2.2.2.2.1, heA.symm, rfl,
                  Or.inl ⟨hP7.2.2.2.2.2.1, Or.inr (Or.inr ⟨hP7.2.2.2.2.2.2, heB.symm⟩)⟩⟩)
              · split
                · rename_i h1 h2 h3 h4 h5 h6 h7 h
                  obtain ⟨hP8, hs3, hs4, heA, heB, heC⟩ := h
                  rw [dif_pos hs3] at hp3; subst hp3
                  rw [dif_pos hs4] at hp4; subst hp4
                  exact Or.inr (Or.inr ⟨hP8.1, hP8.2.1, hP8.2.2.1, hP8.2.2.2.1, hP8.2.2.2.2.1, heA.symm, rfl,
                    Or.inr ⟨hP8.2.2.2.2.2.1, hP8.2.2.2.2.2.2, heB, heC⟩⟩)
                · left; rfl

/-- the size bound: free, or a proper accessor of v, or a proper accessor of u -/
theorem TR2 (u v : M) : op u v = J u v ∨ (u = a1 (a2 v) ∧ tg v = 2 ∧ tg (a2 v) = 2 ∧ sz (op u v) < sz v) ∨
    (v = u ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a1 u) = 2 ∧ sz (op u v) < sz u) := by
  rcases TR u v with h | ⟨h1, h2, h3, h4, -⟩ | ⟨h1, h2, h3, h4, h5, h6, h7, -⟩
  · exact Or.inl h
  · refine Or.inr (Or.inl ⟨h3, h1, h2, ?_⟩)
    rw [h4]; have := sz_a1_lt h1; omega
  · refine Or.inr (Or.inr ⟨h1, h2, h3, h4, h5, ?_⟩)
    rw [h7]; have := sz_a1_lt h5; have s := sz_a1 u; omega

/-- `op y (op (op z y) y)` is always free (regardless of how `op z y` and `op (op z y) y` decode) -/
theorem Tfree_L3 {z y P0 P1 : M} (hP0 : op z y = P0) (hP1 : op P0 y = P1) :
    op y P1 = J y P1 := by
  have tP := TR2 P0 y; rw [hP1] at tP
  have tZ := TR2 z y; rw [hP0] at tZ
  rcases TR y P1 with h | ⟨h1, h2, h3, -, -⟩ | ⟨hC1, hC2, hC3, hC4, hC5, -, -, -⟩
  · exact h
  · exfalso
    rcases tP with hPf | ⟨hP0eq, hty, hta2y, hszP1⟩ | ⟨hP0eq2, htP0, hta2P0, ha1eq, htaP0, hszP1⟩
    · rw [hPf] at h2 h3
      simp only [a2_J_eq] at h2 h3
      have := congrArg sz h3; have := sz_a1_lt h2; omega
    · have := congrArg sz h3
      have := sz_a2_lt h1; have := sz_a1_lt h2
      omega
    · rcases tZ with hZf | ⟨-, -, -, hszP0⟩ | ⟨hyz, -, -, -, -, hszP0⟩
      · rw [← hP0eq2] at hZf
        have := congrArg sz hZf; simp only [sz_J] at this; omega
      · have := congrArg sz hP0eq2; omega
      · have e1 := congrArg sz hP0eq2; have e2 := congrArg sz hyz; omega
  · exfalso
    rcases tP with hPf | ⟨-, -, -, hszP1⟩ | ⟨hP0eq2, -, -, -, -, hszP1⟩
    · rw [hC1] at hPf
      have := congrArg sz hPf; simp only [sz_J] at this; omega
    · have := congrArg sz hC1; omega
    · have e1 := congrArg sz hC1; have e2 := congrArg sz hP0eq2; omega


theorem noFix (a b : M) : op a b ≠ b := by
  intro he
  rcases TR2 a b with h | ⟨-, -, -, hs⟩ | ⟨hv, -, -, -, -, hs⟩
  · rw [h] at he; have := congrArg sz he; simp only [sz_J] at this; have := sz_pos a; omega
  · rw [he] at hs; omega
  · rw [he] at hs; have := congrArg sz hv; omega

/-- the second chain product is free, or the whole chain collapses onto `a1 y` -/
theorem Wdig (z y : M) : op (op z y) y = J (op z y) y ∨
    (tg y = 2 ∧ tg (a2 y) = 2 ∧ a1 y = a1 (a2 y) ∧ op z y = a1 y ∧ op (op z y) y = a1 y) := by
  rcases TR (op z y) y with h | ⟨h1, h2, h3, h4, -⟩ | ⟨h1, -, -, -, -, -, -, -⟩
  · exact Or.inl h
  · rcases TR z y with g | ⟨-, -, -, g4, -⟩ | ⟨g1, -, -, g4, g5, -, g7, -⟩
    · exfalso
      rw [g] at h3
      have e1 := congrArg sz h3
      simp only [sz_J] at e1
      have := sz_a1 (a2 y); have := sz_a2 y; have := sz_pos z; omega
    · exact Or.inr ⟨h1, h2, g4.symm.trans h3, g4, h4⟩
    · exfalso
      rw [← g1] at g4 g5 g7 h3
      have e1 : a1 (a1 y) = a1 (a2 y) := g7.symm.trans h3
      rw [← g4] at e1
      have := sz_a1_lt g5
      have := congrArg sz e1
      omega
  · exact absurd h1.symm (noFix z y)

/-- one of the four `a1 v` branches fires -/
theorem opB {u v w : M} (hw : a1 v = w) (h : P1 u v ∨
    (P2 u v ∧ msr (a1 (a2 u)) u < msr u v ∧ a1 (a2 (a2 v)) = op (a1 (a2 u)) u) ∨
    (P3 u v ∧ msr u u < msr u v ∧ a1 (a2 (a2 v)) = op u u) ∨
    (P4 u v ∧ msr (a1 (a2 u)) u < msr u v ∧ a2 (a2 v) = op (a1 (a2 u)) u ∧
      a1 (a2 u) = op (a1 (a2 u)) u)) : op u v = w := by
  obtain ⟨p1, p2, p3, p4, p5, hp1, hp2, hp3, hp4, hp5, hop⟩ := op_cases u v
  rw [hop]
  split
  · exact hw
  split
  · exact hw
  split
  · exact hw
  split
  · exact hw
  exfalso
  rename_i n1 n2 n3 n4
  rcases h with c | c | c | c
  · exact n1 c
  · rw [dif_pos c.2.1] at hp1
    exact n2 ⟨c.1, c.2.1, by rw [hp1]; exact c.2.2⟩
  · rw [dif_pos c.2.1] at hp2
    exact n3 ⟨c.1, c.2.1, by rw [hp2]; exact c.2.2⟩
  · rw [dif_pos c.2.1] at hp1
    exact n4 ⟨c.1, c.2.1, by rw [hp1]; exact c.2.2.1, by rw [hp1]; exact c.2.2.2⟩

/-- the diagonal pair: one of the four `a1 (a1 u)` branches fires -/
theorem opC {u w : M} (hw : a1 (a1 u) = w) (h1 : tg u = 2) (h2 : tg (a2 u) = 2)
    (h3 : a1 u = a1 (a2 u)) (h4 : tg (a1 u) = 2) (h5 : op (a1 u) u = a1 u)
    (h6 : (tg (a2 (a1 u)) = 2 ∧ (
          (tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a1 u) = a2 (a1 (a2 (a1 u))) ∧ a1 (a1 u) = a2 (a2 (a1 u))) ∨
          (a1 (a1 u) = a2 (a2 (a1 u)) ∧ tg (a1 (a1 u)) = 2 ∧ tg (a2 (a1 (a1 u))) = 2 ∧
            a1 (a2 (a1 u)) = op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))) ∨
          (a1 (a1 u) = a2 (a2 (a1 u)) ∧ op (a1 (a1 u)) (a1 (a1 u)) = a1 (a2 (a1 u))))) ∨
       (tg (a1 (a1 u)) = 2 ∧ tg (a2 (a1 (a1 u))) = 2 ∧
          a2 (a1 u) = op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) ∧
          a1 (a2 (a1 (a1 u))) = op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)))) : op u u = w := by
  have hne : ¬ (u = a1 (a2 u)) := by
    rw [← h3]; intro he; have := sz_a1_lt h1; have := congrArg sz he; omega
  have g3 : msr (a1 u) u < msr u u :=
    msr_lt_of_max_eq (by have := sz_a1 u; omega) (by have := sz_a1_lt h1; omega)
  have s1 := sz_a1_lt h1
  have s2 := sz_a1 (a1 u)
  have s3 := sz_a1 (a2 (a1 (a1 u)))
  have s4 := sz_a2 (a1 (a1 u))
  have g4 : msr (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) < msr u u :=
    msr_lt_both (by omega) (by omega)
  have g5 : msr (a1 (a1 u)) (a1 (a1 u)) < msr u u := msr_lt_both (by omega) (by omega)
  obtain ⟨p1, p2, p3, p4, p5, hp1, hp2, hp3, hp4, hp5, hop⟩ := op_cases u u
  rw [dif_pos g3] at hp3
  rw [dif_pos g4] at hp4
  rw [dif_pos g5] at hp5
  rw [hop]
  split
  · rename_i c; exact absurd c.2.2.1 hne
  split
  · rename_i c; exact absurd c.1.2.2.1 hne
  split
  · rename_i c; exact absurd c.1.2.2.1 hne
  split
  · rename_i c; exact absurd c.1.2.2.1 hne
  split
  · exact hw
  split
  · exact hw
  split
  · exact hw
  split
  · exact hw
  exfalso
  rename_i n5 n6 n7 n8
  rcases h6 with ⟨ha, hb | hb | hb⟩ | hb
  · exact n5 ⟨⟨rfl, h1, h2, h3, h4, ha, hb.1, hb.2.1, hb.2.2⟩, g3, by rw [hp3]; exact h5.symm⟩
  · exact n6 ⟨⟨rfl, h1, h2, h3, h4, ha, hb.1, hb.2.1, hb.2.2.1⟩, g3, g4,
      by rw [hp3]; exact h5.symm, by rw [hp4]; exact hb.2.2.2⟩
  · exact n7 ⟨⟨rfl, h1, h2, h3, h4, ha, hb.1⟩, g3, g5,
      by rw [hp3]; exact h5.symm, by rw [hp5]; exact hb.2.symm⟩
  · exact n8 ⟨⟨rfl, h1, h2, h3, h4, hb.1, hb.2.1⟩, g3, g4,
      by rw [hp3]; exact h5.symm, by rw [hp4]; exact hb.2.2.1, by rw [hp4]; exact hb.2.2.2⟩

/-- the gate of a nested call whose arguments are bounded by `b`, against `(b, J x (J b t))` -/
theorem gL {a b x t : M} (h : sz a ≤ sz b) : msr a b < msr b (J x (J b t)) :=
  msr_lt_both (by simp only [sz_J]; have := sz_pos x; have := sz_pos t; omega)
    (by simp only [sz_J]; have := sz_pos x; have := sz_pos t; omega)

theorem main (x y z : M) : op y (op x (J y (op (op z y) y))) = x := by
  rcases TR x (J y (op (op z y) y)) with hE | ⟨-, hEt, hEx, hEv, hEs⟩ |
    ⟨hC1, -, hC3, hC4, -, -, -, -⟩
  · rw [hE]
    rcases Wdig z y with hW | ⟨hy1, hy2, hy3, hZ, hWv⟩
    · rw [hW]
      rcases TR z y with hz | ⟨hz1, hz2, hz3, -, -⟩ | ⟨hz1, -, -, -, -, -, -, -⟩
      · rw [hz]
        exact opB rfl (Or.inl ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩)
      · exact opB rfl (Or.inr (Or.inl ⟨⟨rfl, rfl, rfl, rfl, rfl, hz1, hz2⟩,
          gL (by have := sz_a1 (a2 y); have := sz_a2 y; omega),
          by simp only [a1_J_eq, a2_J_eq]; rw [← hz3]⟩))
      · rw [← hz1]
        exact opB rfl (Or.inr (Or.inr (Or.inl ⟨⟨rfl, rfl, rfl, rfl, rfl⟩, gL (Nat.le_refl _),
          by simp only [a1_J_eq, a2_J_eq]⟩)))
    · have h5 : op (a1 y) y = a1 y := by rw [← hZ]; exact hWv.trans hZ.symm
      rw [hWv]
      exact opB rfl (Or.inr (Or.inr (Or.inr ⟨⟨rfl, rfl, rfl, hy1, hy2⟩,
        gL (by have := sz_a1 (a2 y); have := sz_a2 y; omega),
        by simp only [a2_J_eq]; rw [← hy3]; exact h5.symm,
        by rw [← hy3]; exact h5.symm⟩)))
  · simp only [a1_J_eq, a2_J_eq] at hEt hEx hEv hEs
    rw [hEv]
    rcases Wdig z y with hW | ⟨hy1, hy2, hy3, hZ, hWv⟩
    · rw [hW] at hEt hEx hEs
      simp only [a1_J_eq, a2_J_eq] at hEt hEx hEs
      rcases TR z y with hz | ⟨hz1, -, -, hz4, -⟩ | ⟨hz1, -, -, -, -, -, -, -⟩
      · exfalso
        rw [hz] at hEx
        subst hEx
        simp only [a1_J_eq, a2_J_eq] at hEs
        rcases hEs with ⟨ht, ⟨-, -, h⟩ | ⟨h, -, -, -⟩ | ⟨h, -⟩⟩ | ⟨-, hb2, hb3, hb4⟩
        · have := congrArg sz h; simp only [sz_J] at this
          have := sz_a2_lt ht; have := sz_pos z; omega
        · have := congrArg sz h; simp only [sz_J] at this
          have := sz_a2_lt ht; have := sz_pos z; omega
        · have := congrArg sz h; simp only [sz_J] at this
          have := sz_a2_lt ht; have := sz_pos z; omega
        · have hy : y = a1 (a2 (J z y)) := hb3.trans hb4.symm
          simp only [a1_J_eq, a2_J_eq] at hy hb2
          have := sz_a1_lt hb2; have := congrArg sz hy; omega
      · exfalso
        rw [hz4] at hEx
        subst hEx
        rcases hEs with ⟨-, ⟨h1, h2, -⟩ | ⟨-, -, -, h4⟩ | ⟨-, h2⟩⟩ | ⟨hb1, -, hb3, hb4⟩
        · have := sz_a2_lt h1; have := congrArg sz h2; omega
        · exact noFix _ _ h4.symm
        · exact noFix _ _ h2
        · have hy : y = a1 (a2 (a1 y)) := hb3.trans hb4.symm
          have := sz_a1 (a2 (a1 y)); have := sz_a2_lt hb1; have := sz_a1_lt hz1
          have := congrArg sz hy; omega
      · rw [← hz1] at hEx
        exact hEx.symm
    · rw [hWv] at hEt hEx hEs
      subst hEx
      have h5 : op (a1 y) y = a1 y := by rw [← hZ]; exact hWv.trans hZ.symm
      exact opC rfl hy1 hy2 hy3 hEt h5 hEs
  · exfalso
    subst hC1
    simp only [a1_J_eq, a2_J_eq] at hC3 hC4
    rcases Wdig z y with hW | ⟨hy1, -, -, -, hWv⟩
    · rw [hW] at hC4
      simp only [a1_J_eq] at hC4
      exact noFix z y hC4.symm
    · rw [hWv] at hC3 hC4
      have := sz_a1_lt hy1; have := sz_a1_lt hC3; have := congrArg sz hC4; omega

/-- THE LAW: x = y * (x * (y * ((z * y) * y))) -/
theorem law (x y z : M) : op (y) (op (x) (op (y) (op (op (z) (y)) (y)))) = x := by
  have h1 : op y (op (op z y) y) = J y (op (op z y) y) := Tfree_L3 rfl rfl
  rw [h1]
  exact main x y z


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

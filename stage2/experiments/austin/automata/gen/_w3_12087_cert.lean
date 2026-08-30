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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a1 (a1 v)) = 2 ∧ u = a1 (a1 (a1 v)) ∧ tg (a2 v) = 2 ∧ a2 (a1 (a1 v)) = a1 (a2 v) ∧ a2 (a1 v) = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a1 (a1 v)) = 2 ∧ u = a1 (a1 (a1 v))
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 v) = 2 ∧ a2 (a1 v) = a2 (a2 v)
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ tg (a1 (a2 (a1 v))) = 2 ∧ tg (a1 (a1 (a2 (a1 v)))) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ tg (a1 (a2 (a1 v))) = 2 ∧ tg (a2 (a2 (a1 v))) = 2 ∧ a2 v = a1 (a2 (a2 (a1 v))) ∧ a2 (a1 (a2 (a1 v))) = a2 (a2 (a2 (a1 v))) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a1 (a1 (a2 v))) = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ tg (a2 (a2 (a1 v))) = 2 ∧ a2 v = a1 (a2 (a2 (a1 v))) ∧ tg (a2 (a2 (a2 (a1 v)))) = 2 ∧ tg (a1 (a2 (a2 (a2 (a1 v))))) = 2 ∧ tg (a1 (a1 (a2 (a2 (a2 (a1 v)))))) = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a1 (a1 (a2 v))) = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v then op (a2 (a1 (a1 v))) (a2 (a1 v)) else J u v
  let p2 := if hs2 : msr (u) (a1 (a2 v)) < msr u v then op (u) (a1 (a2 v)) else J u v
  let p3 := if hs3 : msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v then op (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) else J u v
  let p4 := if hs4 : msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v then op (u) (a1 (a1 (a1 (a2 (a1 v))))) else J u v
  let p5 := if hs5 : msr (a1 (a1 (a1 (a2 v)))) (a2 v) < msr u v then op (a1 (a1 (a1 (a2 v)))) (a2 v) else J u v
  let p6 := if hs6 : msr (a1 (a1 (a1 (a2 v)))) (a2 (a1 v)) < msr u v then op (a1 (a1 (a1 (a2 v)))) (a2 (a1 v)) else J u v
  let p7 := if hs7 : msr (u) (a1 (a1 (a1 (a2 v)))) < msr u v then op (u) (a1 (a1 (a1 (a2 v)))) else J u v
  let p8 := if hs8 : msr (a1 (a1 (a1 (a2 (a2 (a2 (a1 v))))))) (a2 (a2 (a2 (a1 v)))) < msr u v then op (a1 (a1 (a1 (a2 (a2 (a2 (a1 v))))))) (a2 (a2 (a2 (a1 v)))) else J u v
  let p9 := if hs9 : msr (p2) (a2 (a2 v)) < msr u v then op (p2) (a2 (a2 v)) else J u v
  if P1 u v then a2 (a1 (a1 v))
  else if P2 u v ∧ msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v ∧ a2 v = p1 then a2 (a1 (a1 v))
  else if P3 u v ∧ msr (u) (a1 (a2 v)) < msr u v ∧ a1 (a1 v) = p2 then a1 (a2 v)
  else if P4 u v ∧ msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v ∧ msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v ∧ a2 v = p3 ∧ a1 (a1 v) = p4 then a1 (a1 (a1 (a2 (a1 v))))
  else if P5 u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a2 v) < msr u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a2 (a1 v)) < msr u v ∧ msr (u) (a1 (a1 (a1 (a2 v)))) < msr u v ∧ a1 (a1 (a2 (a1 v))) = p5 ∧ a2 v = p6 ∧ a1 (a1 v) = p7 then a1 (a1 (a1 (a2 v)))
  else if P6 u v ∧ msr (a1 (a1 (a1 (a2 (a2 (a2 (a1 v))))))) (a2 (a2 (a2 (a1 v)))) < msr u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a2 v) < msr u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a2 (a1 v)) < msr u v ∧ msr (u) (a1 (a1 (a1 (a2 v)))) < msr u v ∧ a1 (a2 (a1 v)) = p8 ∧ a1 (a1 (a1 (a2 (a2 (a2 (a1 v)))))) = p5 ∧ a2 v = p6 ∧ a1 (a1 v) = p7 then a1 (a1 (a1 (a2 v)))
  else if P7 u v ∧ msr (u) (a1 (a2 v)) < msr u v ∧ msr (p2) (a2 (a2 v)) < msr u v ∧ a1 v = p9 then a1 (a2 v)
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (op (op (g 0) (g 0)) (g 0)) (g 1)) (op (g 0) (g 2))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6, P7]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem tgJ2 {t : M} (h : tg t = 2) : t = J (a1 t) (a2 t) := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp only [a1_J_eq, a2_J_eq]
theorem Jinj {a b c d : M} (h : J a b = J c d) : a = c ∧ b = d := by
  injection h with h1 h2; exact ⟨h1, h2⟩

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 p9 : M,
    p1 = (if hs1 : msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v then op (a2 (a1 (a1 v))) (a2 (a1 v)) else J u v) ∧
    p2 = (if hs2 : msr (u) (a1 (a2 v)) < msr u v then op (u) (a1 (a2 v)) else J u v) ∧
    p3 = (if hs3 : msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v then op (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) else J u v) ∧
    p4 = (if hs4 : msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v then op (u) (a1 (a1 (a1 (a2 (a1 v))))) else J u v) ∧
    p5 = (if hs5 : msr (a1 (a1 (a1 (a2 v)))) (a2 v) < msr u v then op (a1 (a1 (a1 (a2 v)))) (a2 v) else J u v) ∧
    p6 = (if hs6 : msr (a1 (a1 (a1 (a2 v)))) (a2 (a1 v)) < msr u v then op (a1 (a1 (a1 (a2 v)))) (a2 (a1 v)) else J u v) ∧
    p7 = (if hs7 : msr (u) (a1 (a1 (a1 (a2 v)))) < msr u v then op (u) (a1 (a1 (a1 (a2 v)))) else J u v) ∧
    p8 = (if hs8 : msr (a1 (a1 (a1 (a2 (a2 (a2 (a1 v))))))) (a2 (a2 (a2 (a1 v)))) < msr u v then op (a1 (a1 (a1 (a2 (a2 (a2 (a1 v))))))) (a2 (a2 (a2 (a1 v)))) else J u v) ∧
    p9 = (if hs9 : msr (p2) (a2 (a2 v)) < msr u v then op (p2) (a2 (a2 v)) else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 (a1 v))
  else if P2 u v ∧ msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v ∧ a2 v = p1 then a2 (a1 (a1 v))
  else if P3 u v ∧ msr (u) (a1 (a2 v)) < msr u v ∧ a1 (a1 v) = p2 then a1 (a2 v)
  else if P4 u v ∧ msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v ∧ msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v ∧ a2 v = p3 ∧ a1 (a1 v) = p4 then a1 (a1 (a1 (a2 (a1 v))))
  else if P5 u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a2 v) < msr u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a2 (a1 v)) < msr u v ∧ msr (u) (a1 (a1 (a1 (a2 v)))) < msr u v ∧ a1 (a1 (a2 (a1 v))) = p5 ∧ a2 v = p6 ∧ a1 (a1 v) = p7 then a1 (a1 (a1 (a2 v)))
  else if P6 u v ∧ msr (a1 (a1 (a1 (a2 (a2 (a2 (a1 v))))))) (a2 (a2 (a2 (a1 v)))) < msr u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a2 v) < msr u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a2 (a1 v)) < msr u v ∧ msr (u) (a1 (a1 (a1 (a2 v)))) < msr u v ∧ a1 (a2 (a1 v)) = p8 ∧ a1 (a1 (a1 (a2 (a2 (a2 (a1 v)))))) = p5 ∧ a2 v = p6 ∧ a1 (a1 v) = p7 then a1 (a1 (a1 (a2 v)))
  else if P7 u v ∧ msr (u) (a1 (a2 v)) < msr u v ∧ msr (p2) (a2 (a2 v)) < msr u v ∧ a1 v = p9 then a1 (a2 v)
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the seven rules fired.  The three deep rules (P4,P5,P6)
    share a single disjunct keyed on `op u v` itself, which also carries their size bound. -/
theorem TR7 (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a2 (a1 (a1 v))) ∨
    (P2 u v ∧ a2 v = op (a2 (a1 (a1 v))) (a2 (a1 v)) ∧ op u v = a2 (a1 (a1 v))) ∨
    (P3 u v ∧ a1 (a1 v) = op u (a1 (a2 v)) ∧ op u v = a1 (a2 v)) ∨
    (tg v = 2 ∧ tg (a1 v) = 2 ∧ sz (op u v) < sz v ∧
      a2 v = op (op u v) (a2 (a1 v)) ∧ a1 (a1 v) = op u (op u v)) ∨
    (P7 u v ∧ a1 v = op (op u (a1 (a2 v))) (a2 (a2 v)) ∧ op u v = a1 (a2 v)) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hop⟩ := op_cases u v
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
          obtain ⟨h4, hs3, hs4, he3, he4⟩ := h
          rw [dif_pos hs3] at hp3; subst hp3
          rw [dif_pos hs4] at hp4; subst hp4
          refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h4.1, h4.2.1, ?_, he3, he4⟩))))
          have := sz_a1 (a1 (a1 (a2 (a1 v)))); have := sz_a1 (a1 (a2 (a1 v)))
          have := sz_a1 (a2 (a1 v)); have := sz_a2_lt h4.2.1; have := sz_a1_lt h4.1; omega
        · split
          · rename_i h1 h2 h3 h4 h
            obtain ⟨h5, hs5, hs6, hs7, he5, he6, he7⟩ := h
            rw [dif_pos hs6] at hp6; subst hp6
            rw [dif_pos hs7] at hp7; subst hp7
            refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h5.1, h5.2.1, ?_, he6, he7⟩))))
            have := sz_a1 (a1 (a1 (a2 v))); have := sz_a1 (a1 (a2 v)); have := sz_a1 (a2 v)
            have := sz_a2_lt h5.1; omega
          · split
            · rename_i h1 h2 h3 h4 h5 h
              obtain ⟨h6, hs8, hs5, hs6, hs7, he8, he5, he6, he7⟩ := h
              rw [dif_pos hs6] at hp6; subst hp6
              rw [dif_pos hs7] at hp7; subst hp7
              refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h6.1, h6.2.1, ?_, he6, he7⟩))))
              have := sz_a1 (a1 (a1 (a2 v))); have := sz_a1 (a1 (a2 v)); have := sz_a1 (a2 v)
              have := sz_a2_lt h6.1; omega
            · split
              · rename_i h1 h2 h3 h4 h5 h6 h
                obtain ⟨h7, hs2, hs9, he⟩ := h
                rw [dif_pos hs2] at hp2; subst hp2
                rw [dif_pos hs9] at hp9; subst hp9
                exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr ⟨h7, he, rfl⟩))))
              · left; rfl

/-- every rule returns a proper subterm of `v` -/
theorem SZV (u v : M) : op u v = J u v ∨ sz (op u v) < sz v := by
  rcases TR7 u v with h | ⟨h1, h⟩ | ⟨h2, -, h⟩ | ⟨h3, -, h⟩ | ⟨-, -, h, -⟩ | ⟨h7, -, h⟩
  · exact Or.inl h
  · right; rw [h]
    have := sz_a2_lt h1.2.2.1; have := sz_a1_lt h1.2.1; have := sz_a1_lt h1.1
    have := sz_a1 (a1 v); omega
  · right; rw [h]
    have := sz_a2_lt h2.2.2.1; have := sz_a1_lt h2.2.1; have := sz_a1_lt h2.1
    have := sz_a1 (a1 v); omega
  · right; rw [h]
    have := sz_a1_lt h3.2.2.1; have := sz_a2_lt h3.1; omega
  · exact Or.inr h
  · right; rw [h]
    have := sz_a1_lt h7.2; have := sz_a2_lt h7.1; omega

/-- a `J`-shaped value at least as big as `w` can only be the free product -/
theorem noBig {p w a b : M} (h : op p w = J a b) (hb : sz w ≤ sz a + sz b) : p = a ∧ w = b := by
  rcases SZV p w with hf | hs
  · rw [hf] at h; exact Jinj h
  · rw [h] at hs; simp only [sz_J] at hs; omega

/-- a decoded product has a strictly smaller left argument -/
theorem SUn (n : Nat) : ∀ u v : M, sz v ≤ n → op u v ≠ J u v → sz u < sz v := by
  induction n with
  | zero => intro u v hn _; have := sz_pos v; omega
  | succ n ih =>
    intro u v hn hd
    have step : ∀ Y : M, sz Y < sz v → tg v = 2 → a1 (a1 v) = op u Y → sz u < sz v := by
      intro Y hY hv hg
      by_cases hW : op u Y = J u Y
      · rw [hW] at hg
        have := congrArg sz hg; simp only [sz_J] at this
        have := sz_a1 (a1 v); have := sz_a1_lt hv; omega
      · have h9 := ih u Y (by omega) hW; omega
    rcases TR7 u v with h | ⟨h1, -⟩ | ⟨h2, -, -⟩ | ⟨h3, hg, -⟩ | ⟨hv, -, hsz, -, hg⟩ | ⟨h7, hg, -⟩
    · exact absurd h hd
    · have := sz_a1 (a1 (a1 v)); have := sz_a1_lt h1.2.2.1; have := sz_a1_lt h1.2.1
      have := sz_a1_lt h1.1; rw [h1.2.2.2.1]; omega
    · have := sz_a1 (a1 (a1 v)); have := sz_a1_lt h2.2.2.1; have := sz_a1_lt h2.2.1
      have := sz_a1_lt h2.1; rw [h2.2.2.2]; omega
    · exact step (a1 (a2 v)) (by have := sz_a1_lt h3.2.2.1; have := sz_a2_lt h3.1; omega) h3.1 hg
    · exact step (op u v) hsz hv hg
    · have hv := h7.1; have ha2v := h7.2
      have hX : sz (a1 (a2 v)) < sz v := by have := sz_a1_lt ha2v; have := sz_a2_lt hv; omega
      have hZ : sz (a2 (a2 v)) < sz v := by have := sz_a2_lt ha2v; have := sz_a2_lt hv; omega
      have hA : sz (a1 v) < sz v := sz_a1_lt hv
      by_cases hW : op u (a1 (a2 v)) = J u (a1 (a2 v))
      · by_cases hR : op (op u (a1 (a2 v))) (a2 (a2 v)) = J (op u (a1 (a2 v))) (a2 (a2 v))
        · rw [hR, hW] at hg
          have := congrArg sz hg; simp only [sz_J] at this; omega
        · have h9 := ih (op u (a1 (a2 v))) (a2 (a2 v)) (by omega) hR
          rw [hW] at h9; simp only [sz_J] at h9; omega
      · have h9 := ih u (a1 (a2 v)) (by omega) hW; omega

theorem SU {u v : M} (h : op u v ≠ J u v) : sz u < sz v := SUn (sz v) u v (Nat.le_refl _) h
theorem SZ {u v : M} (h : op u v ≠ J u v) : sz (op u v) < sz v := by
  rcases SZV u v with hf | hs
  · exact absurd hf h
  · exact hs

/-- the shape of `v` when it decodes for `u`: the chain form (rules 1-6) or the third-product
    form (rule 7). -/
theorem SH_of {u v : M} (hd : op u v ≠ J u v) :
    tg v = 2 ∧ (
      (tg (a1 v) = 2 ∧ (a1 (a1 v) = J u (op u v) ∨ a1 (a1 v) = op u (op u v))
        ∧ (a2 v = J (op u v) (a2 (a1 v)) ∨ a2 v = op (op u v) (a2 (a1 v))))
      ∨ (a2 v = J (op u v) (a2 (a2 v)) ∧ a1 v = op (op u (op u v)) (a2 (a2 v)))) := by
  rcases TR7 u v with h | ⟨h1, he⟩ | ⟨h2, hg, he⟩ | ⟨h3, hg, he⟩ | ⟨hv, hav, -, hg1, hg2⟩ | ⟨h7, hg, he⟩
  · exact absurd h hd
  · refine ⟨h1.1, Or.inl ⟨h1.2.1, Or.inl ?_, Or.inl ?_⟩⟩
    · rw [he, h1.2.2.2.1]; exact tgJ2 h1.2.2.1
    · rw [he, h1.2.2.2.2.2.1, h1.2.2.2.2.2.2]; exact tgJ2 h1.2.2.2.2.1
  · refine ⟨h2.1, Or.inl ⟨h2.2.1, Or.inl ?_, Or.inr ?_⟩⟩
    · rw [he, h2.2.2.2]; exact tgJ2 h2.2.2.1
    · rw [he]; exact hg
  · refine ⟨h3.1, Or.inl ⟨h3.2.1, Or.inr ?_, Or.inl ?_⟩⟩
    · rw [he]; exact hg
    · rw [he, h3.2.2.2]; exact tgJ2 h3.2.2.1
  · exact ⟨hv, Or.inl ⟨hav, Or.inr hg2, Or.inr hg1⟩⟩
  · refine ⟨h7.1, Or.inr ⟨?_, ?_⟩⟩
    · rw [he]; exact tgJ2 h7.2
    · rw [he]; exact hg

/-- injectivity of a decoded product in its left argument (fuel induction on `sz v`) -/
theorem INJn (n : Nat) : ∀ v u u' : M, sz v ≤ n → op u v ≠ J u v → op u' v = op u v → u = u' := by
  induction n with
  | zero => intro v u u' hn _ _; have := sz_pos v; omega
  | succ n ih =>
    intro v u u' hn hd he
    have hr : sz (op u v) < sz v := SZ hd
    have hd' : op u' v ≠ J u' v := by
      intro hf; rw [hf] at he; have := congrArg sz he; simp only [sz_J] at this
      have := sz_pos u'; omega
    have same : ∀ a b w : M, sz w ≤ n → op a w = op b w → a = b := by
      intro a b w hw hab
      by_cases hf : op a w = J a w
      · rw [hf] at hab
        exact (noBig hab.symm (by omega)).1.symm
      · exact ih w a b hw hf hab.symm
    have hZv : sz (op u v) ≤ n := by omega
    obtain ⟨hv, hs⟩ := SH_of hd
    obtain ⟨-, hs'⟩ := SH_of hd'
    rw [he] at hs'
    have mixed : ∀ a b : M,
        (a1 (a1 v) = J a (op u v) ∨ a1 (a1 v) = op a (op u v)) →
        (a2 v = J (op u v) (a2 (a1 v)) ∨ a2 v = op (op u v) (a2 (a1 v))) →
        tg (a1 v) = 2 →
        a2 v = J (op u v) (a2 (a2 v)) →
        a1 v = op (op b (op u v)) (a2 (a2 v)) → a = b := by
      intro a b hk hq hav hq' hk'
      by_cases hf : op (op b (op u v)) (a2 (a2 v)) = J (op b (op u v)) (a2 (a2 v))
      · rw [hf] at hk'
        obtain ⟨e1, -⟩ := Jinj ((tgJ2 hav).symm.trans hk')
        rcases hk with hL | hQ
        · exact (noBig ((hL.symm.trans e1).symm) (by omega)).1.symm
        · exact same a b (op u v) hZv (hQ.symm.trans e1)
      · exfalso
        have hlt : sz (a1 v) < sz (a2 (a2 v)) := by rw [hk']; exact SZ hf
        have hs1 : sz (a1 v) = sz (a1 (a1 v)) + sz (a2 (a1 v)) + 1 := sz_tg _ hav
        rcases hq with hJ | hO
        · have := congrArg sz (Jinj (hJ.symm.trans hq')).2; omega
        · by_cases hf2 : op (op u v) (a2 (a1 v)) = J (op u v) (a2 (a1 v))
          · rw [hf2] at hO
            have := congrArg sz (Jinj (hO.symm.trans hq')).2; omega
          · have hb := SZ hf2
            rw [hO.symm.trans hq'] at hb; simp only [sz_J] at hb; omega
    rcases hs with ⟨hav, hk, hq⟩ | ⟨hq, hk⟩
    · rcases hs' with ⟨-, hk', -⟩ | ⟨hq', hk'⟩
      · rcases hk with hL | hQ <;> rcases hk' with hL' | hQ'
        · exact (Jinj (hL.symm.trans hL')).1
        · exact ((noBig (hQ'.symm.trans hL) (by omega)).1).symm
        · exact (noBig (hQ.symm.trans hL') (by omega)).1
        · exact same u u' (op u v) hZv (hQ.symm.trans hQ')
      · exact mixed u u' hk hq hav hq' hk'
    · rcases hs' with ⟨hav', hk', hq'⟩ | ⟨hq', hk'⟩
      · exact (mixed u' u hk' hq' hav' hq hk).symm
      · by_cases hf : op (op u (op u v)) (a2 (a2 v)) = J (op u (op u v)) (a2 (a2 v))
        · rw [hf] at hk
          exact (same u' u (op u v) hZv (noBig (hk'.symm.trans hk) (by omega)).1).symm
        · have hlt : sz (a1 v) < sz (a2 (a2 v)) := by rw [hk]; exact SZ hf
          have ht : tg (a2 v) = 2 := by rw [hq]; rfl
          have hd2 : sz (a2 (a2 v)) ≤ n := by
            have := sz_a2_lt hv; have := sz_a2_lt ht; omega
          have hq2 := ih (a2 (a2 v)) (op u (op u v)) (op u' (op u v)) hd2 hf (hk'.symm.trans hk)
          exact same u u' (op u v) hZv hq2

theorem INJ {v u u' : M} (hd : op u v ≠ J u v) (he : op u' v = op u v) : u = u' :=
  INJn (sz v) v u u' (Nat.le_refl _) hd he

theorem gsub {a b u v : M} (ha : sz a < sz v) (hb : sz b < sz v) : msr a b < msr u v :=
  msr_lt_of_max_lt (Nat.lt_of_lt_of_le (Nat.max_lt.mpr ⟨ha, hb⟩) (Nat.le_max_right (sz u) (sz v)))

theorem gm {a b u v : M} (ha : sz a ≤ sz u) (hb : sz b < sz v) : msr a b < msr u v := by
  rcases Nat.lt_or_ge (max (sz a) (sz b)) (max (sz u) (sz v)) with h | h
  · exact msr_lt_of_max_lt h
  · refine msr_lt_of_max_eq (Nat.le_antisymm ?_ h) (by omega)
    exact Nat.max_le.mpr ⟨Nat.le_trans ha (Nat.le_max_left _ _),
      Nat.le_trans (Nat.le_of_lt hb) (Nat.le_max_right _ _)⟩

/-- MAIN: every chain product free, rule 1 fires and every guard is `rfl` -/
theorem opR1 (x y z : M) : op y (J (J (J y x) z) (J x z)) = x := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, -, -, -, -, -, -, -, -, -, hop⟩ :=
    op_cases y (J (J (J y x) z) (J x z))
  have h1 : P1 y (J (J (J y x) z) (J x z)) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  rw [hop, if_pos h1]
  rfl

/-- the third product decodes, the first two are free: rule 2 fires, its guard is `rfl` -/
theorem opR2 {x z : M} (hC : op x z ≠ J x z) (y : M) :
    op y (J (J (J y x) z) (op x z)) = x := by
  have hs : sz (op x z) < sz z := SZ hC
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, hp1, -, -, -, -, -, -, -, -, hop⟩ :=
    op_cases y (J (J (J y x) z) (op x z))
  have hg : msr x z < msr y (J (J (J y x) z) (op x z)) := by
    refine gsub ?_ ?_ <;> simp only [sz] <;> omega
  have hq : p1 = op x z := by rw [hp1]; exact dif_pos hg
  rw [hop]
  split
  · rename_i h
    exfalso
    have e := h.2.2.2.2.2.2
    simp only [a1_J_eq, a2_J_eq] at e
    have := sz_a2 (op x z)
    have := congrArg sz e
    omega
  · split
    · rfl
    · rename_i h1 h2
      exact absurd ⟨⟨rfl, rfl, rfl, rfl⟩, hg, hq.symm⟩ h2

/-- the third product is free: whatever rule fires on the last product, it returns `x` -/
theorem opCF (x y z : M) : op y (J (op (op y x) z) (J x z)) = x := by
  have hb : sz (a2 (op (op y x) z)) ≤ sz x + sz z := by
    by_cases h : op (op y x) z = J (op y x) z
    · rw [h]; simp only [a2_J_eq]; omega
    · have := SZ h; have := sz_a2 (op (op y x) z); omega
  have hA : sz (op y x) < sz (J (op (op y x) z) (J x z)) := by
    have := sz_pos (op (op y x) z)
    by_cases h : op (op y x) z = J (op y x) z
    · rw [h]; simp only [sz]; omega
    · have h1 := SU h; simp only [sz]; omega
  have g2 : msr y (a1 (a2 (J (op (op y x) z) (J x z)))) < msr y (J (op (op y x) z) (J x z)) := by
    refine gm (Nat.le_refl _) ?_
    have := sz_pos (op (op y x) z); have := sz_pos z
    simp only [a1_J_eq, a2_J_eq, sz]; omega
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hop⟩ :=
    op_cases y (J (op (op y x) z) (J x z))
  have hq2 : p2 = op y x := by rw [hp2]; exact dif_pos g2
  rw [hq2] at hp9
  have g9 : msr (op y x) (a2 (a2 (J (op (op y x) z) (J x z)))) < msr y (J (op (op y x) z) (J x z)) := by
    refine gsub hA ?_
    have := sz_pos (op (op y x) z); have := sz_pos x
    simp only [a2_J_eq, sz]; omega
  have hq9 : p9 = op (op y x) z := by rw [hp9]; exact dif_pos g9
  rw [hop]
  split
  · rename_i h; exact h.2.2.2.2.2.1
  · split
    · rename_i h1 h
      obtain ⟨-, hs, he⟩ := h
      have hq : p1 = op (a2 (a1 (a1 (J (op (op y x) z) (J x z))))) (a2 (a1 (J (op (op y x) z) (J x z)))) := by
        rw [hp1]; exact dif_pos hs
      exact (noBig (he.trans hq).symm hb).1
    · split
      · rfl
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨-, hs3, -, he3, -⟩ := h
          have hq : p3 = op (a1 (a1 (a1 (a2 (a1 (J (op (op y x) z) (J x z))))))) (a2 (a1 (J (op (op y x) z) (J x z)))) := by
            rw [hp3]; exact dif_pos hs3
          exact (noBig (he3.trans hq).symm hb).1
        · split
          · rename_i h1 h2 h3 h4 h
            obtain ⟨-, -, hs6, -, -, he6, -⟩ := h
            have hq : p6 = op (a1 (a1 (a1 (a2 (J (op (op y x) z) (J x z)))))) (a2 (a1 (J (op (op y x) z) (J x z)))) := by
              rw [hp6]; exact dif_pos hs6
            exact (noBig (he6.trans hq).symm hb).1
          · split
            · rename_i h1 h2 h3 h4 h5 h
              obtain ⟨-, -, -, hs6, -, -, -, he6, -⟩ := h
              have hq : p6 = op (a1 (a1 (a1 (a2 (J (op (op y x) z) (J x z)))))) (a2 (a1 (J (op (op y x) z) (J x z)))) := by
                rw [hp6]; exact dif_pos hs6
              exact (noBig (he6.trans hq).symm hb).1
            · split
              · rfl
              · rename_i h1 h2 h3 h4 h5 h6 h7
                have g9' : msr p2 (a2 (a2 (J (op (op y x) z) (J x z)))) < msr y (J (op (op y x) z) (J x z)) := by
                  rw [hq2]; exact g9
                exact absurd ⟨⟨rfl, rfl⟩, g2, g9', hq9.symm⟩ h7

/-- HOLE 1 -- the fourth product is free.  0 violations in 24,000 targeted trials
    (gen/_w3_12087_tree.py: V is 'F' in every reachable cell). -/
theorem VF (x y z : M) : op (op (op y x) z) (op x z) = J (op (op y x) z) (op x z) := sorry

/-- HOLE 2 -- the second and third products never both decode.  0 violations in 24,000 trials. -/
theorem BC (x y z : M) (hB : op (op y x) z ≠ J (op y x) z) : op x z = J x z := sorry

/-- HOLE 3 -- first and third products decode, second free (1007/6000 census hits). -/
theorem AD {x y z : M} (hA : op y x ≠ J y x) (hC : op x z ≠ J x z) :
    op y (J (J (op y x) z) (op x z)) = x := sorry

theorem law (x y z : M) : op (y) (op (op (op (y) (x)) (z)) (op (x) (z))) = x := by
  rw [VF x y z]
  by_cases hC : op x z = J x z
  · rw [hC]; exact opCF x y z
  · have hB : op (op y x) z = J (op y x) z := by
      by_cases h : op (op y x) z = J (op y x) z
      · exact h
      · exact absurd (BC x y z h) hC
    rw [hB]
    by_cases hA : op y x = J y x
    · rw [hA]; exact opR2 hC y
    · exact AD hA hC


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

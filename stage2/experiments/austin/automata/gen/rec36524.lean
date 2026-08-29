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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a2 (a2 v) = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a2 (a2 v) = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def P8 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P8 u v) := by unfold P8; infer_instance
def P9 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P9 u v) := by unfold P9; infer_instance
def P10 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P10 u v) := by unfold P10; infer_instance
def P11 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u)) ∧ a2 (a1 u) = a1 (a2 u) ∧ a2 (a2 v) = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P11 u v) := by unfold P11; infer_instance
def P12 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P12 u v) := by unfold P12; infer_instance
def P13 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P13 u v) := by unfold P13; infer_instance
def P14 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P14 u v) := by unfold P14; infer_instance
def P15 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P15 u v) := by unfold P15; infer_instance
def P16 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ v = a1 u
instance (u v : M) : Decidable (P16 u v) := by unfold P16; infer_instance
def P17 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P17 u v) := by unfold P17; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a1 u)) (u) < msr u v then op (a2 (a1 u)) (u) else J u v
  let p2 := if hs2 : msr (u) (p1) < msr u v then op (u) (p1) else J u v
  let p3 := if hs3 : msr (a2 (a1 (p2))) (p2) < msr u v then op (a2 (a1 (p2))) (p2) else J u v
  let p4 := if hs4 : msr (p1) (u) < msr u v then op (p1) (u) else J u v
  let p5 := if hs5 : msr (u) (p4) < msr u v then op (u) (p4) else J u v
  let p6 := if hs6 : msr (p1) (p5) < msr u v then op (p1) (p5) else J u v
  let p7 := if hs7 : msr (p1) (p2) < msr u v then op (p1) (p2) else J u v
  if P1 u v then a1 (a2 (a2 v))
  else if P2 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 (a2 v) = p1 then a2 (a1 u)
  else if P3 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 (a2 v) = p1 then a2 (a1 u)
  else if P4 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (u) (p1) < msr u v ∧ a2 v = p2 then a2 (a1 u)
  else if P5 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 then a1 (a2 (a2 v))
  else if P6 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a2 (a2 v) = p1 then a2 (a1 u)
  else if P7 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a2 (a2 v) = p1 then a2 (a1 u)
  else if P8 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (u) (p1) < msr u v ∧ a1 v = p1 ∧ a2 v = p2 then a2 (a1 u)
  else if P9 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 then a1 (a2 (a2 v))
  else if P10 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a2 (a2 v) = p1 then a2 (a1 u)
  else if P11 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a2 (a2 v) = p1 then a2 (a1 u)
  else if P12 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (u) (p1) < msr u v ∧ a1 v = p1 ∧ a2 v = p2 then a2 (a1 u)
  else if P13 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (u) (p1) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ v = p3 ∧ tg (a2 (a1 (p2))) = 2 ∧ u = a2 (a2 (a1 (p2))) then a2 (a1 u)
  else if P14 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (u) (p1) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ v = p3 ∧ a2 (a1 (p2)) = p1 then a2 (a1 u)
  else if P15 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (u) (p1) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ v = p3 ∧ a2 (a1 (p2)) = a1 (a2 (a2 u)) ∧ a2 (a1 (p2)) = p1 then a2 (a1 u)
  else if P16 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (u) (p4) < msr u v ∧ msr (p1) (p5) < msr u v ∧ p1 = a2 u ∧ p1 = a2 u ∧ v = p6 then p1
  else if P17 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (u) (p1) < msr u v ∧ msr (p1) (p2) < msr u v ∧ v = p7 then a2 (a1 u)
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


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v ∨ P8 u v ∨ P9 u v ∨ P10 u v ∨ P11 u v ∨ P12 u v ∨ P13 u v ∨ P14 u v ∨ P15 u v ∨ P16 u v ∨ P17 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (g 1) (op (g 2) (op (g 2) (op (g 1) (op (g 0) (g 0)))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12, P13, P14, P15, P16, P17]


/-- THE LAW: x = (((y * x) * y) * (y * z)) * y (stated for the DUAL L-form law; the served magma flips op, so EquationLHS unfolds to exactly this) -/
theorem law (x y z : M) : op (y) (op (op (z) (y)) (op (y) (op (x) (y)))) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

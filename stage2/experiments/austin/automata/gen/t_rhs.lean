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

def P1 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ tg (a2 (a2 (a2 v))) = 2 ∧ u = a2 (a2 (a2 (a2 v)))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ tg u = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ tg (a2 (a2 (a2 u))) = 2 ∧ a2 (a2 (a2 v)) = a1 (a2 (a2 (a2 u))) ∧ a1 u = a2 (a2 (a2 (a2 u)))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ a2 (a2 v) = a1 (a2 (a2 u)) ∧ a1 u = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg u = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg u = 2
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : sz (a1 u) + sz (u) < sz u + sz v then op (a1 u) (u) else J u v
  let p2 := if hs2 : sz (a1 u) + sz (p1) < sz u + sz v then op (a1 u) (p1) else J u v
  let p3 := if hs3 : sz (a1 (p1)) + sz (p1) < sz u + sz v then op (a1 (p1)) (p1) else J u v
  let p4 := if hs4 : sz (u) + sz (p3) < sz u + sz v then op (u) (p3) else J u v
  let p5 := if hs5 : sz (u) + sz (p4) < sz u + sz v then op (u) (p4) else J u v
  if P1 u v then a1 (a2 (a2 (a2 v)))
  else if P2 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 u
  else if P3 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 u
  else if P4 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ sz (a1 u) + sz (p1) < sz u + sz v ∧ a2 (a2 v) = p2 then a1 u
  else if P5 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ sz (a1 (p1)) + sz (p1) < sz u + sz v ∧ tg (p1) = 2 ∧ a2 (a2 v) = p3 then a1 u
  else if P6 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ sz (a1 (p1)) + sz (p1) < sz u + sz v ∧ sz (u) + sz (p3) < sz u + sz v ∧ tg (p1) = 2 ∧ a2 v = p4 then a1 u
  else if P7 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ sz (a1 (p1)) + sz (p1) < sz u + sz v ∧ sz (u) + sz (p3) < sz u + sz v ∧ sz (u) + sz (p4) < sz u + sz v ∧ tg (p1) = 2 ∧ v = p5 then a1 u
  else J u v
termination_by sz u + sz v
decreasing_by
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
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (op (g 1) (g 0))) (op (op (g 2) (g 2)) (g 0))
  repeat (rw [op.eq_1]; simp (config := {decide := true}) [sz, P1, P2, P3, P4, P5, P6, P7])


/-- THE LAW: x = y * (y * (y * (z * (x * y)))) -/
theorem law (x y z : M) : op (y) (op (y) (op (y) (op (z) (op (x) (y))))) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

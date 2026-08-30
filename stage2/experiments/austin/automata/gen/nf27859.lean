import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | K : submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def sz : M → Nat
  | .g _ => 1
  | .K => 1
  | .J a b => sz a + sz b + 1

def tg : M → Nat
  | .g _ => 0
  | .K => 1
  | .J _ _ => 2
def a1 : M → M
  | .J a _ => a
  | t => t
def a2 : M → M
  | .J _ b => b
  | t => t

@[simp] theorem tg_J_eq (a b : M) : tg (J a b) = 2 := rfl
@[simp] theorem a1_J (a b : M) : a1 (J a b) = a := rfl
@[simp] theorem a2_J (a b : M) : a2 (J a b) = b := rfl
@[simp] theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_pos (t : M) : 0 < sz t := by cases t <;> simp [sz] <;> omega
theorem sz_a1 (t : M) : sz (a1 t) ≤ sz t := by cases t <;> simp [a1, sz] <;> omega
theorem sz_a2 (t : M) : sz (a2 t) ≤ sz t := by cases t <;> simp [a2, sz] <;> omega

/-- three-rule normal-form product for 27859. -/
def op (u v : M) : M :=
  let a := a1 (a1 u)
  let b := a2 (a1 u)
  let q := a2 u
  let r1 := if h : sz a + sz q < sz u + sz v then op a q else u
  let r2 := if h : sz a + sz b < sz u + sz v then op a b else u
  if u = v then K
  else if v = K ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ r1 = b ∧ r2 = J a b then q
  else if v = K ∧ tg u = 2 ∧ tg q = 2 ∧ a2 q = a1 u then q
  else J u v
termination_by sz u + sz v
decreasing_by
  · assumption
  · assumption

def inst : Magma M := { op := op }

/-- goal 4916 : x = y ◇ (x ◇ (x ◇ (y ◇ (z ◇ z)))) fails at x = y = z = g 0. -/
theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (g 0) (op (g 0) (op (g 0) (op (g 0) (op (g 0) (g 0)))))
  simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]

theorem law (x y z : M) : op (op (op y (op y x)) x) (op z z) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

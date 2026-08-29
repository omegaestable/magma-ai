import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

-- Lean check of gen/cex38249.py: the generator's single rule (gen/rec38249_gen0.lean) is NOT a model of
-- the dual law  x = y * (y * ((z * (x * x)) * y)).  Definitions copied verbatim from the original skeleton.

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
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v

def P1 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ a1 (a2 (a1 (a2 v))) = a2 (a2 (a1 (a2 v))) ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def op (u v : M) : M :=
  if P1 u v then a1 (a2 (a1 (a2 v)))
  else J u v
termination_by msr u v
decreasing_by

/-- x = g0, z = g1, y = J (J z (J x x)) (J (J g2 (J g3 g3)) (J z (J x x))): the third product fires R1. -/
theorem cex : ¬ (∀ x y z : M, op y (op y (op (op z (op x x)) y)) = x) := by
  intro h
  have := h (g 0) (J (J (g 1) (J (g 0) (g 0))) (J (J (g 2) (J (g 3) (g 3))) (J (g 1) (J (g 0) (g 0))))) (g 1)
  revert this
  simp (config := {decide := true}) [op.eq_1, sz, P1]

end submission

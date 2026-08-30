import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | E : submission.M
  | g : Nat → submission.M
  | P : submission.M → submission.M → submission.M
  | C : submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .E => 0
  | .g _ => 1
  | .P _ _ => 2
  | .C _ => 3
def a1 : M → M
  | .P x _ => x
  | .C x => x
  | t => t
def a2 : M → M
  | .P _ x => x
  | t => t
def sz : M → Nat
  | .E => 1
  | .g _ => 1
  | .P b0 b1 => sz b0 + sz b1 + 1
  | .C b0 => sz b0 + 1

def op (u v : M) : M :=
  let m := a1 v
  let p1 := if h1 : sz (a1 m) + sz (a2 m) < sz u + sz v then op (a1 m) (a2 m) else E
  let p2 := if h2 : sz u + sz (a2 m) < sz u + sz v then op u (a2 m) else E
  let p3 := if h3 : sz E + sz u < sz u + sz v then op E u else E
  let p4 := if h4 : sz u + sz m < sz u + sz v then op u m else E
  let p5 := if h5 : sz E + sz m < sz u + sz v then op E m else E
  if u = v then E
  else if tg v = 3 ∧ u ≠ E ∧ tg m = 3 ∧ a1 m = C u then E
  else if tg v = 3 ∧ tg m = 2 ∧ sz (a1 m) + sz (a2 m) < sz u + sz v ∧
      sz u + sz (a2 m) < sz u + sz v ∧ p1 = m ∧ p2 = a1 m then a2 m
  else if tg v = 3 ∧ u ≠ E ∧ sz E + sz u < sz u + sz v ∧ p3 = m then u
  else if tg v = 3 ∧ m ≠ E ∧ sz u + sz m < sz u + sz v ∧ sz E + sz m < sz u + sz v ∧ p4 = E then C p5
  else if v = E then C u
  else P u v
termination_by sz u + sz v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption

def inst : Magma M := { op := op }

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h E E (g 0)
  revert this
  change ¬ E = op (op (op (op E E) E) E) (op E (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]

example : op (C (P (g 1) (C E))) (P (g 1) (C (C (g 1)))) = (P (C (P (g 1) (C E))) (P (g 1) (C (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) (g 1)) (g 0)) (C (C (g 1))) = (P (P (P (g 0) (g 1)) (g 0)) (C (C (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 1)) (C E)) (C (P (g 1) (C (g 0)))) = (P (P (C (g 1)) (C E)) (C (P (g 1) (C (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (g 1)) (P (C (g 0)) (g 1)) = (P (P (g 1) (g 1)) (P (C (g 0)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P E (g 1))) (P (g 1) (P (g 0) E)) = (P (C (P E (g 1))) (P (g 1) (P (g 0) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C E) (C (g 0))) (C (P (g 1) (C (g 0)))) = (P (P (C E) (C (g 0))) (C (P (g 1) (C (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (P (g 1) (g 1))) (P (P (g 0) E) (g 1)) = (P (P (g 1) (P (g 1) (g 1))) (P (P (g 0) E) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (g 1) E)) (P (P (g 1) (g 1)) E) = (P (C (P (g 1) E)) (P (P (g 1) (g 1)) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (g 1) (C (g 0)))) (C (g 0)) = (P (C (P (g 1) (C (g 0)))) (C (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (C (P (g 1) (g 1)))) (P E (C (C E))) = (P (C (C (P (g 1) (g 1)))) (P E (C (C E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C (g 0)) E)) (P (C E) (g 1)) = (P (C (P (C (g 0)) E)) (P (C E) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (P E (g 0))) (P (C (g 0)) (g 1)) = (P (P (g 1) (P E (g 0))) (P (C (g 0)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (C (C (g 0)))) (P (g 1) (C E)) = (P (C (C (C (g 0)))) (P (g 1) (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P E E) E) (P (P E E) E) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (P E E)) (P (g 0) (C E)) = (P (P E (P E E)) (P (g 0) (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (C (g 0))) (g 0) = (P (P (g 1) (C (g 0))) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (g 1) (C (C (P (g 0) E))) = (P (g 1) (C (C (P (g 0) E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (C (P (g 1) (g 1)))) (P (C (g 1)) (g 0)) = (P (C (C (P (g 1) (g 1)))) (P (C (g 1)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 1)) (g 0)) (C (P (C (g 1)) E)) = (P (P (C (g 1)) (g 0)) (C (P (C (g 1)) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (C (C E))) (C (C (C (C E)))) = (P (P (g 0) (C (C E))) (C (C (C (C E))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) E) (g 0)) (C (C (P (g 0) (g 1)))) = (P (P (P (g 0) E) (g 0)) (C (C (P (g 0) (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C E) (g 1)) (C (C (C (C E)))) = (P (P (C E) (g 1)) (C (C (C (C E))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (P (g 1) E)) (C (P (C E) (g 1))) = (P (P (g 1) (P (g 1) E)) (C (P (C E) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C E) (P (g 1) (C (C E))) = (P (C E) (P (g 1) (C (C E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (P (g 0) (g 1))) (P (C (g 1)) (g 0)) = (P (P E (P (g 0) (g 1))) (P (C (g 1)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (C (g 1))) (C (P E (C (g 1)))) = (C (P E (P E (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (g 1)) (P (g 0) (P (g 1) (g 0))) = (P (P E (g 1)) (P (g 0) (P (g 1) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C E) E)) (P (P E (g 1)) (g 1)) = (P (C (P (C E) E)) (P (P E (g 1)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P E (g 0)) (g 0)) (g 0) = (P (P (P E (g 0)) (g 0)) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P E (g 0)) E) (P (g 0) (P (g 1) E)) = (P (P (P E (g 0)) E) (P (g 0) (P (g 1) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (g 1)) (P (g 0) (C (C (g 1)))) = (P (P E (g 1)) (P (g 0) (C (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (C (C (g 0)))) (P (g 0) (C (C (g 0)))) = (P (P (g 1) (C (C (g 0)))) (P (g 0) (C (C (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C (g 0))) (g 0)) (P (g 0) (C (C E))) = (P (P (C (C (g 0))) (g 0)) (P (g 0) (C (C E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C E) E) (P (C (C (g 0))) (g 0)) = (P (P (C E) E) (P (C (C (g 0))) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C E) (C (g 0))) (P (C E) (g 0)) = (P (P (C E) (C (g 0))) (P (C E) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) E) (C (P (g 1) (C E))) = (P (P (g 1) E) (C (P (g 1) (C E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C E) (P (g 1) (C (C (g 1)))) = (P (C E) (P (g 1) (C (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (C (C (g 1)))) (C (g 1)) = (P (P E (C (C (g 1)))) (C (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) E) E) (P E (P (g 0) E)) = (P (P (P (g 0) E) E) (P E (P (g 0) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (P (g 0) (g 0))) (P (g 1) (P (g 1) (g 0))) = (P (P (g 1) (P (g 0) (g 0))) (P (g 1) (P (g 1) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 1) E) (g 1)) E = (C (P (P (g 1) E) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 0)) (C (g 1))) (P (g 0) E) = (P (P (C (g 0)) (C (g 1))) (P (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (C (g 0))) (C (P (g 0) (C E))) = (P (P (g 0) (C (g 0))) (C (P (g 0) (C E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 1)) (C (g 1))) (P (g 0) (P E (g 1))) = (P (P (C (g 1)) (C (g 1))) (P (g 0) (P E (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C E)) E) (P (g 1) (C (C (g 0)))) = (P (P (C (C E)) E) (P (g 1) (C (C (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) (g 0)) E) (C (P (g 1) (C (g 1)))) = (P (P (P (g 0) (g 0)) E) (C (P (g 1) (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 1)) (C (g 1))) (C (P E (g 0))) = (P (P (C (g 1)) (C (g 1))) (C (P E (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P E (g 0)) (g 0)) (P (g 1) (P (g 0) (g 1))) = (P (P (P E (g 0)) (g 0)) (P (g 1) (P (g 0) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C E) (g 0))) (P (g 0) (g 0)) = (P (C (P (C E) (g 0))) (P (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (P (g 1) E)) (C (P (g 0) E)) = (P (P E (P (g 1) E)) (C (P (g 0) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (C (P (g 0) E))) (P (g 0) (P E (g 0))) = (P (C (C (P (g 0) E))) (P (g 0) (P E (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C E)) E) (P (P E E) (g 0)) = (P (P (C (C E)) E) (P (P E E) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (C (C E))) (P E (C (g 1))) = (P (P (g 1) (C (C E))) (P E (C (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (P E (g 0))) (C (P (C (g 0)) (g 1))) = (P (P (g 0) (P E (g 0))) (C (P (C (g 0)) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) E) (g 1)) (C (P (g 0) E)) = (P (P (P (g 0) E) (g 1)) (C (P (g 0) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (C (C (g 1)))) (P (g 0) (P (g 0) (g 0))) = (P (P (g 0) (C (C (g 1)))) (P (g 0) (P (g 0) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (C (C (g 0)))) (P (C E) (g 0)) = (P (P (g 0) (C (C (g 0)))) (P (C E) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (C (C E))) (P E (C E)) = (P (C (C (C E))) (P E (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (C (C (g 1)))) (P (C (C (g 0))) (g 0)) = (P (P (g 0) (C (C (g 1)))) (P (C (C (g 0))) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 0)) E) (P (g 1) (g 0)) = (P (P (C (g 0)) E) (P (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (C (C E))) (P (P E (g 1)) (g 0)) = (P (C (C (C E))) (P (P E (g 1)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) (g 1)) (g 1)) (P E (C (C (g 1)))) = (P (P (P (g 0) (g 1)) (g 1)) (P E (C (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (C E)) (C (P (g 0) (C (g 0)))) = (P (C (C E)) (C (P (g 0) (C (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P E (g 0)) E) (P (g 0) (P E (g 1))) = (P (P (P E (g 0)) E) (P (g 0) (P E (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (g 1) (C (g 1)))) (P (C (g 0)) (C E)) = (P (C (P (g 1) (C (g 1)))) (P (C (g 0)) (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (P (g 0) E)) (P E (C (g 1))) = (P (P E (P (g 0) E)) (P E (C (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) E) (C (C E)) = (P (P (g 1) E) (C (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C (g 1))) (g 0)) (P (g 0) (P (g 1) (g 1))) = (P (P (C (C (g 1))) (g 0)) (P (g 0) (P (g 1) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (C (P (g 0) E))) (P (g 1) (C (g 0))) = (P (C (C (P (g 0) E))) (P (g 1) (C (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 1) (g 1)) (g 0)) (P (g 1) (C (g 0))) = (P (P (P (g 1) (g 1)) (g 0)) (P (g 1) (C (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (P (g 0) (g 0))) (C (P E (g 0))) = (P (P E (P (g 0) (g 0))) (C (P E (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 1)) (g 1)) (P E (P E (g 0))) = (P (P (C (g 1)) (g 1)) (P E (P E (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (P (g 0) E)) (P E (C E)) = (P (P (g 1) (P (g 0) E)) (P E (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (g 0)) (P E (P (g 0) E)) = (P (P E (g 0)) (P E (P (g 0) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C E) (g 0))) (P E (C (g 0))) = (P (C (P (C E) (g 0))) (P E (C (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 0)) (C E)) (P (P E E) E) = (P (P (C (g 0)) (C E)) (P (P E E) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 1)) (g 1)) (P (P (g 0) (g 0)) (g 1)) = (P (P (C (g 1)) (g 1)) (P (P (g 0) (g 0)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 0)) (C E)) (P (C (C (g 0))) (g 1)) = (P (P (C (g 0)) (C E)) (P (C (C (g 0))) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (P (g 0) (g 0))) (P (C E) (C E)) = (P (P (g 0) (P (g 0) (g 0))) (P (C E) (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C E) (C (g 0))) (P (C E) (C (g 0))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C (g 0)) (g 1))) (C (P (C (g 1)) E)) = (P (C (P (C (g 0)) (g 1))) (C (P (C (g 1)) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (P (C (g 0)) (g 1))) (C (P (C (g 1)) E))) (C (P (C (g 1)) E)) = (P (P (C (P (C (g 0)) (g 1))) (C (P (C (g 1)) E))) (C (P (C (g 1)) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (C (P (C (g 0)) (g 1))) (C (P (C (g 1)) E))) (C (P (C (g 1)) E))) E = (C (P (P (C (P (C (g 0)) (g 1))) (C (P (C (g 1)) E))) (C (P (C (g 1)) E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C (g 0)) (g 1))) (C (P (P (C (P (C (g 0)) (g 1))) (C (P (C (g 1)) E))) (C (P (C (g 1)) E)))) = (C (P (C (g 1)) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P E (g 1))) (C (P E (g 1))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (C (C (g 1)))) (P E (C (g 1))) = (P (P E (C (C (g 1)))) (P E (C (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P E (C (C (g 1)))) (P E (C (g 1)))) (P E (C (g 1))) = (P (P (P E (C (C (g 1)))) (P E (C (g 1)))) (P E (C (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P E (C (C (g 1)))) (P E (C (g 1)))) (P E (C (g 1)))) E = (C (P (P (P E (C (C (g 1)))) (P E (C (g 1)))) (P E (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (C (C (g 1)))) (C (P (P (P E (C (C (g 1)))) (P E (C (g 1)))) (P E (C (g 1))))) = (P E (C (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C E) (g 0)) (P (C E) (g 0)) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (P (g 1) (g 0))) (P (P (g 0) (g 1)) (g 1)) = (P (P (g 1) (P (g 1) (g 0))) (P (P (g 0) (g 1)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 1) (P (g 1) (g 0))) (P (P (g 0) (g 1)) (g 1))) (P (P (g 0) (g 1)) (g 1)) = (P (P (P (g 1) (P (g 1) (g 0))) (P (P (g 0) (g 1)) (g 1))) (P (P (g 0) (g 1)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (g 1) (P (g 1) (g 0))) (P (P (g 0) (g 1)) (g 1))) (P (P (g 0) (g 1)) (g 1))) E = (C (P (P (P (g 1) (P (g 1) (g 0))) (P (P (g 0) (g 1)) (g 1))) (P (P (g 0) (g 1)) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (P (g 1) (g 0))) (C (P (P (P (g 1) (P (g 1) (g 0))) (P (P (g 0) (g 1)) (g 1))) (P (P (g 0) (g 1)) (g 1)))) = (P (P (g 0) (g 1)) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C E) (g 1)) (P (C E) (g 1)) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C (g 1))) (g 1)) (P (g 0) (P (g 1) E)) = (P (P (C (C (g 1))) (g 1)) (P (g 0) (P (g 1) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (C (C (g 1))) (g 1)) (P (g 0) (P (g 1) E))) (P (g 0) (P (g 1) E)) = (P (P (P (C (C (g 1))) (g 1)) (P (g 0) (P (g 1) E))) (P (g 0) (P (g 1) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (C (C (g 1))) (g 1)) (P (g 0) (P (g 1) E))) (P (g 0) (P (g 1) E))) E = (C (P (P (P (C (C (g 1))) (g 1)) (P (g 0) (P (g 1) E))) (P (g 0) (P (g 1) E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C (g 1))) (g 1)) (C (P (P (P (C (C (g 1))) (g 1)) (P (g 0) (P (g 1) E))) (P (g 0) (P (g 1) E)))) = (P (g 0) (P (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C (g 0)) (g 0))) (C (P (C (g 0)) (g 0))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (g 0) (g 1))) (P (C (C (g 0))) E) = (P (C (P (g 0) (g 1))) (P (C (C (g 0))) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (P (g 0) (g 1))) (P (C (C (g 0))) E)) (P (C (C (g 0))) E) = (P (P (C (P (g 0) (g 1))) (P (C (C (g 0))) E)) (P (C (C (g 0))) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (C (P (g 0) (g 1))) (P (C (C (g 0))) E)) (P (C (C (g 0))) E)) E = (C (P (P (C (P (g 0) (g 1))) (P (C (C (g 0))) E)) (P (C (C (g 0))) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (g 0) (g 1))) (C (P (P (C (P (g 0) (g 1))) (P (C (C (g 0))) E)) (P (C (C (g 0))) E))) = (P (C (C (g 0))) E) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C (g 1))) E) (P (C (C (g 1))) E) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C E)) E) (P (P (g 0) E) E) = (P (P (C (C E)) E) (P (P (g 0) E) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (C (C E)) E) (P (P (g 0) E) E)) (P (P (g 0) E) E) = (P (P (P (C (C E)) E) (P (P (g 0) E) E)) (P (P (g 0) E) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (C (C E)) E) (P (P (g 0) E) E)) (P (P (g 0) E) E)) E = (C (P (P (P (C (C E)) E) (P (P (g 0) E) E)) (P (P (g 0) E) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C E)) E) (C (P (P (P (C (C E)) E) (P (P (g 0) E) E)) (P (P (g 0) E) E))) = (P (P (g 0) E) E) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (C (C (g 1)))) (P (g 1) (C (C (g 1)))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (C (C E))) (P E (g 1)) = (P (P (g 1) (C (C E))) (P E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 1) (C (C E))) (P E (g 1))) (P E (g 1)) = (P (P (P (g 1) (C (C E))) (P E (g 1))) (P E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (g 1) (C (C E))) (P E (g 1))) (P E (g 1))) E = (C (P (P (P (g 1) (C (C E))) (P E (g 1))) (P E (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (C (C E))) (C (P (P (P (g 1) (C (C E))) (P E (g 1))) (P E (g 1)))) = (P E (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (C (C (g 0)))) (P (g 0) (C (C (g 0)))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P E (g 0)) (g 0)) (C (C E)) = (P (P (P E (g 0)) (g 0)) (C (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P E (g 0)) (g 0)) (C (C E))) (C (C E)) = (P (P (P (P E (g 0)) (g 0)) (C (C E))) (C (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (P E (g 0)) (g 0)) (C (C E))) (C (C E))) E = (C (P (P (P (P E (g 0)) (g 0)) (C (C E))) (C (C E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P E (g 0)) (g 0)) (C (P (P (P (P E (g 0)) (g 0)) (C (C E))) (C (C E)))) = (C (C E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C (g 0)) E)) (C (P (C (g 0)) E)) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (P (g 0) (g 0))) (P (P (g 1) (g 0)) E) = (P (P (g 1) (P (g 0) (g 0))) (P (P (g 1) (g 0)) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 1) (P (g 0) (g 0))) (P (P (g 1) (g 0)) E)) (P (P (g 1) (g 0)) E) = (P (P (P (g 1) (P (g 0) (g 0))) (P (P (g 1) (g 0)) E)) (P (P (g 1) (g 0)) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (g 1) (P (g 0) (g 0))) (P (P (g 1) (g 0)) E)) (P (P (g 1) (g 0)) E)) E = (C (P (P (P (g 1) (P (g 0) (g 0))) (P (P (g 1) (g 0)) E)) (P (P (g 1) (g 0)) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (P (g 0) (g 0))) (C (P (P (P (g 1) (P (g 0) (g 0))) (P (P (g 1) (g 0)) E)) (P (P (g 1) (g 0)) E))) = (P (P (g 1) (g 0)) E) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C E) (g 0))) (C (P (C E) (g 0))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C (g 0))) (g 1)) (C (P E (C (g 1)))) = (P (P (C (C (g 0))) (g 1)) (C (P E (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (C (C (g 0))) (g 1)) (C (P E (C (g 1))))) (C (P E (C (g 1)))) = (P (P (P (C (C (g 0))) (g 1)) (C (P E (C (g 1))))) (C (P E (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (C (C (g 0))) (g 1)) (C (P E (C (g 1))))) (C (P E (C (g 1))))) E = (C (P (P (P (C (C (g 0))) (g 1)) (C (P E (C (g 1))))) (C (P E (C (g 1)))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (C (g 0))) (g 1)) (C (P (P (P (C (C (g 0))) (g 1)) (C (P E (C (g 1))))) (C (P E (C (g 1)))))) = (C (P E (C (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 1) E) (g 1)) (P (P (g 1) E) (g 1)) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (P E (g 0))) (P (C E) (g 0)) = (P (P (g 0) (P E (g 0))) (P (C E) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) (P E (g 0))) (P (C E) (g 0))) (P (C E) (g 0)) = (P (P (P (g 0) (P E (g 0))) (P (C E) (g 0))) (P (C E) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (g 0) (P E (g 0))) (P (C E) (g 0))) (P (C E) (g 0))) E = (C (P (P (P (g 0) (P E (g 0))) (P (C E) (g 0))) (P (C E) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (P E (g 0))) (C (P (P (P (g 0) (P E (g 0))) (P (C E) (g 0))) (P (C E) (g 0)))) = (P (C E) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) E) E) (P (P (g 0) E) E) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op E (P (C E) (C (g 1))) = (P E (P (C E) (C (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (P (C E) (C (g 1)))) (P (C E) (C (g 1))) = (P (P E (P (C E) (C (g 1)))) (P (C E) (C (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P E (P (C E) (C (g 1)))) (P (C E) (C (g 1)))) E = (C (P (P E (P (C E) (C (g 1)))) (P (C E) (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op E (C (P (P E (P (C E) (C (g 1)))) (P (C E) (C (g 1))))) = (P (C E) (C (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C (g 0)) (g 1))) (C (P (C (g 0)) (g 1))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (g 1) (C (g 1)))) (P (g 0) (P (g 0) E)) = (P (C (P (g 1) (C (g 1)))) (P (g 0) (P (g 0) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (P (g 1) (C (g 1)))) (P (g 0) (P (g 0) E))) (P (g 0) (P (g 0) E)) = (P (P (C (P (g 1) (C (g 1)))) (P (g 0) (P (g 0) E))) (P (g 0) (P (g 0) E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (C (P (g 1) (C (g 1)))) (P (g 0) (P (g 0) E))) (P (g 0) (P (g 0) E))) E = (C (P (P (C (P (g 1) (C (g 1)))) (P (g 0) (P (g 0) E))) (P (g 0) (P (g 0) E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (g 1) (C (g 1)))) (C (P (P (C (P (g 1) (C (g 1)))) (P (g 0) (P (g 0) E))) (P (g 0) (P (g 0) E)))) = (P (g 0) (P (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 1)) (C (g 1))) (C (P (C (g 1)) (g 1))) = (P (P (C (g 1)) (C (g 1))) (C (P (C (g 1)) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (C (g 1)) (C (g 1))) (C (P (C (g 1)) (g 1)))) (C (P (C (g 1)) (g 1))) = (P (P (P (C (g 1)) (C (g 1))) (C (P (C (g 1)) (g 1)))) (C (P (C (g 1)) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (C (g 1)) (C (g 1))) (C (P (C (g 1)) (g 1)))) (C (P (C (g 1)) (g 1)))) E = (C (P (P (P (C (g 1)) (C (g 1))) (C (P (C (g 1)) (g 1)))) (C (P (C (g 1)) (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 1)) (C (g 1))) (C (P (P (P (C (g 1)) (C (g 1))) (C (P (C (g 1)) (g 1)))) (C (P (C (g 1)) (g 1))))) = (C (P (C (g 1)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (C (C (g 1)))) (P (g 0) (P E E)) = (P (P (g 1) (C (C (g 1)))) (P (g 0) (P E E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 1) (C (C (g 1)))) (P (g 0) (P E E))) (P (g 0) (P E E)) = (P (P (P (g 1) (C (C (g 1)))) (P (g 0) (P E E))) (P (g 0) (P E E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (g 1) (C (C (g 1)))) (P (g 0) (P E E))) (P (g 0) (P E E))) E = (C (P (P (P (g 1) (C (C (g 1)))) (P (g 0) (P E E))) (P (g 0) (P E E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (C (C (g 1)))) (C (P (P (P (g 1) (C (C (g 1)))) (P (g 0) (P E E))) (P (g 0) (P E E)))) = (P (g 0) (P E E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (P E E)) (P (g 0) (P E E)) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (P E (g 1))) (P E (C (C E))) = (P (P (g 0) (P E (g 1))) (P E (C (C E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) (P E (g 1))) (P E (C (C E)))) (P E (C (C E))) = (P (P (P (g 0) (P E (g 1))) (P E (C (C E)))) (P E (C (C E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (g 0) (P E (g 1))) (P E (C (C E)))) (P E (C (C E)))) E = (C (P (P (P (g 0) (P E (g 1))) (P E (C (C E)))) (P E (C (C E))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (P E (g 1))) (C (P (P (P (g 0) (P E (g 1))) (P E (C (C E)))) (P E (C (C E))))) = (P E (C (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (P (g 0) (g 0))) (P (g 1) (P (g 0) (g 0))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 1)) E) (P (C (g 0)) (C (g 1))) = (P (P (C (g 1)) E) (P (C (g 0)) (C (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (C (g 1)) E) (P (C (g 0)) (C (g 1)))) (P (C (g 0)) (C (g 1))) = (P (P (P (C (g 1)) E) (P (C (g 0)) (C (g 1)))) (P (C (g 0)) (C (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (C (g 1)) E) (P (C (g 0)) (C (g 1)))) (P (C (g 0)) (C (g 1)))) E = (C (P (P (P (C (g 1)) E) (P (C (g 0)) (C (g 1)))) (P (C (g 0)) (C (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (C (g 1)) E) (C (P (P (P (C (g 1)) E) (P (C (g 0)) (C (g 1)))) (P (C (g 0)) (C (g 1))))) = (P (C (g 0)) (C (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P E (C (g 0))) (P E (C (g 0))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (P (g 1) (g 1))) (P (P (g 0) (g 0)) (g 0)) = (P (P (g 0) (P (g 1) (g 1))) (P (P (g 0) (g 0)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) (P (g 1) (g 1))) (P (P (g 0) (g 0)) (g 0))) (P (P (g 0) (g 0)) (g 0)) = (P (P (P (g 0) (P (g 1) (g 1))) (P (P (g 0) (g 0)) (g 0))) (P (P (g 0) (g 0)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (g 0) (P (g 1) (g 1))) (P (P (g 0) (g 0)) (g 0))) (P (P (g 0) (g 0)) (g 0))) E = (C (P (P (P (g 0) (P (g 1) (g 1))) (P (P (g 0) (g 0)) (g 0))) (P (P (g 0) (g 0)) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 0) (P (g 1) (g 1))) (C (P (P (P (g 0) (P (g 1) (g 1))) (P (P (g 0) (g 0)) (g 0))) (P (P (g 0) (g 0)) (g 0)))) = (P (P (g 0) (g 0)) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (C (C (C E)))) (C (C (C (C E)))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) (g 1)) (g 0)) (P (C (g 1)) (g 0)) = (P (P (P (g 0) (g 1)) (g 0)) (P (C (g 1)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (g 0) (g 1)) (g 0)) (P (C (g 1)) (g 0))) (P (C (g 1)) (g 0)) = (P (P (P (P (g 0) (g 1)) (g 0)) (P (C (g 1)) (g 0))) (P (C (g 1)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (P (g 0) (g 1)) (g 0)) (P (C (g 1)) (g 0))) (P (C (g 1)) (g 0))) E = (C (P (P (P (P (g 0) (g 1)) (g 0)) (P (C (g 1)) (g 0))) (P (C (g 1)) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 0) (g 1)) (g 0)) (C (P (P (P (P (g 0) (g 1)) (g 0)) (P (C (g 1)) (g 0))) (P (C (g 1)) (g 0)))) = (P (C (g 1)) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (C (P (C (g 1)) (g 0))) (C (P (C (g 1)) (g 0))) = E := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (C (C E))) (P (C E) (C E)) = (P (P (g 1) (C (C E))) (P (C E) (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (g 1) (C (C E))) (P (C E) (C E))) (P (C E) (C E)) = (P (P (P (g 1) (C (C E))) (P (C E) (C E))) (P (C E) (C E))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (P (P (g 1) (C (C E))) (P (C E) (C E))) (P (C E) (C E))) E = (C (P (P (P (g 1) (C (C E))) (P (C E) (C E))) (P (C E) (C E)))) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]
example : op (P (g 1) (C (C E))) (C (P (P (P (g 1) (C (C E))) (P (C E) (C E))) (P (C E) (C E)))) = (P (C E) (C E)) := by simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]

theorem law (x y z : M) : op y (op (op (op y x) x) (op z z)) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

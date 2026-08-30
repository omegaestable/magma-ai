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
  have := h (g 0) E E
  revert this
  change ¬ g 0 = op (op (op (op (op E E) E) (g 0)) (g 0)) E
  simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]


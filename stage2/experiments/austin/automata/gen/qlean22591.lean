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
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b) < max (sz u) (sz v)) : msr a b < msr u v := by
  unfold msr
  have h1 : sz a + sz b <= 2 * max (sz a) (sz b) := by omega
  have h2 : (max (sz a) (sz b) + 1) * (max (sz a) (sz b) + 1) <= max (sz u) (sz v) * max (sz u) (sz v) := Nat.mul_le_mul h h
  simp only [Nat.mul_succ, Nat.succ_mul] at h2
  omega
theorem msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b) = max (sz u) (sz v))
    (h2 : sz a + sz b < sz u + sz v) : msr a b < msr u v := by unfold msr; rw [h]; omega

/-- `op` for 22591 :  x = (y*(y*x)) * ((x*x)*z).   The payload is read on BOTH sides, and each
  reading checks the other side, so a decoded product on either side is still recognised.
  R1a  u = (a*(a*b)), v = (s*t), s = op b b   -> b
  R1b  v = ((b*b)*t), u = (a*c),  c = op a b  -> b
-/
def op (u v : M) : M :=
  let s := if h : msr (a2 (a2 u)) (a2 (a2 u)) < msr u v then op (a2 (a2 u)) (a2 (a2 u)) else J u v
  let t := if h : msr (a1 u) (a1 (a1 v)) < msr u v then op (a1 u) (a1 (a1 v)) else J u v
  if tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 (a2 u) = a1 u ∧ s = a1 v then a2 (a2 u)
  else if tg v = 2 ∧ tg u = 2 ∧ tg (a1 v) = 2 ∧ a1 (a1 v) = a2 (a1 v) ∧ t = a2 u then a1 (a1 v)
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption

def inst : Magma M := { op := op }

theorem T1 : op (op (g 1) (op (g 1) (g 0))) (op (op (g 0) (g 0)) (g 2)) = g 0 := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T2 : op (op (g 0) (op (g 0) (g 0))) (op (op (g 0) (g 0)) (g 0)) = g 0 := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T3 :
    op (op (J (g 0) (J (g 0) (g 0))) (op (J (g 0) (J (g 0) (g 0))) (J (g 0) (g 0))))
      (op (op (J (g 0) (g 0)) (J (g 0) (g 0))) (g 0)) = J (g 0) (g 0) := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T4 :
    op (op (g 0) (op (g 0) (J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (g 0)))))
      (op (op (J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (g 0))) (J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (g 0)))) (g 0))
    = J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (g 0)) := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (g 0) (g 0)) (op (op (g 0) (op (g 0) (g 0))) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]

theorem law (x y z : M) : op (op y (op y x)) (op (op x x) z) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

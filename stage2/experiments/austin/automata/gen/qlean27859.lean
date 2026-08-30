import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | E : submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .g _ => 1
  | .E => 3
  | .J _ _ => 2
def a1 : M → M
  | .J x _ => x
  | t => t
def a2 : M → M
  | .J _ x => x
  | t => t
def sz : M → Nat
  | .g _ => 1
  | .E => 1
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

/-- `op` for 27859 : all squares are E, so the law is  op (op (op y (op y x)) x) E = x.
  R1 SQ    u = v                                            -> E
  R2 DEC   v = E, u = ((a*q)*b), p2 = a1 u                  -> b   (p1 = op a b, p2 = op a p1)
  R3 SELF  v = E, u = (d*b), r = d                          -> b   (r = op b E; the y = x chain)
-/
def op (u v : M) : M :=
  let p1 := if h : msr (a1 (a1 u)) (a2 u) < msr u v then op (a1 (a1 u)) (a2 u) else J u v
  let p2 := if h : msr (a1 (a1 u)) p1 < msr u v then op (a1 (a1 u)) p1 else J u v
  let r := if h : msr (a2 u) E < msr u v then op (a2 u) E else J u v
  if u = v then E
  else if v = E ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ p2 = a1 u then a2 u
  else if v = E ∧ tg u = 2 ∧ r = a1 u then a2 u
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption

def inst : Magma M := { op := op }

theorem T1 : op (op (op (g 1) (op (g 1) (g 0))) (g 0)) (op (g 2) (g 2)) = g 0 := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T2 : op (op (op (g 0) (op (g 0) (g 0))) (g 0)) (op (g 1) (g 1)) = g 0 := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T3 : op (op (op (g 0) (op (g 0) E)) E) (op (g 1) (g 1)) = E := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T4 :
    op (op (op (J (J (g 0) E) (g 0)) (op (J (J (g 0) E) (g 0)) (J (J (g 0) E) (g 0))))
      (J (J (g 0) E) (g 0))) (op (g 1) (g 1)) = J (J (g 0) E) (g 0) := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (g 0) (op (g 0) (op (g 0) (op (g 0) (op (g 0) (g 0)))))
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]

theorem law (x y z : M) : op (op (op y (op y x)) x) (op z z) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

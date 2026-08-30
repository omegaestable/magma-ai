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
theorem sz_pos (u : M) : 0 < sz u := by cases u <;> simp [sz] <;> omega
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b) < max (sz u) (sz v)) : msr a b < msr u v := by
  unfold msr
  have h1 : sz a + sz b <= 2 * max (sz a) (sz b) := by omega
  have h2 : (max (sz a) (sz b) + 1) * (max (sz a) (sz b) + 1) <= max (sz u) (sz v) * max (sz u) (sz v) := Nat.mul_le_mul h h
  simp only [Nat.mul_succ, Nat.succ_mul] at h2
  omega
theorem msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b) = max (sz u) (sz v))
    (h2 : sz a + sz b < sz u + sz v) : msr a b < msr u v := by unfold msr; rw [h]; omega

/-- `op` : five rules and the free fallback.
  R1 SQ    u = v                                 -> E
  R2 DEC   v = ((a*b)*E),  p2 = a1 v             -> b        (p1 = op u b, p2 = op p1 b)
  R3 SELF  v = (d*E), u <> E, q = d              -> u        (q  = op E u)
  R4 SCODE v = (u*E), u <> E                     -> (q*E)
  R5 GSC   v = (w*E), not (u = E and w = E), r = E -> ((E*w)*E)   (r = op u w)
-/
def op (u v : M) : M :=
  let p1 := if h : msr u (a2 (a1 v)) < msr u v then op u (a2 (a1 v)) else J u v
  let p2 := if h : msr p1 (a2 (a1 v)) < msr u v then op p1 (a2 (a1 v)) else J u v
  let q := if h : msr E u < msr u v then op E u else J u v
  let r := if h : msr u (a1 v) < msr u v then op u (a1 v) else J u v
  if u = v then E
  else if tg v = 2 ∧ a2 v = E ∧ tg (a1 v) = 2 ∧ p2 = a1 v then a2 (a1 v)
  else if tg v = 2 ∧ a2 v = E ∧ ¬ (u = E) ∧ q = a1 v then u
  else if tg v = 2 ∧ a2 v = E ∧ ¬ (u = E) ∧ a1 v = u then J q E
  else if tg v = 2 ∧ a2 v = E ∧ ¬ (u = E ∧ a1 v = E) ∧ r = E then J (J E (a1 v)) E
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption

def inst : Magma M := { op := op }

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (op (op (g 0) (g 0)) (g 0)) (g 0)) (op (g 0) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]


/-- faithfulness spot-checks against the python model gen/q12073e.py (removed from the shipped cert) -/
theorem T1 : op (g 1) (op (op (op (g 1) (g 0)) (g 0)) (op (g 2) (g 2))) = g 0 := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T2 : op (g 0) (op (op (op (g 0) E) E) (op (g 1) (g 1))) = E := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T3 : op (g 0) (op (op (op (g 0) (g 0)) (g 0)) (op (g 1) (g 1))) = g 0 := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T4 : op (g 0) (op (op (op (g 0) (J (J E (g 0)) E)) (J (J E (g 0)) E)) (op (g 1) (g 1)))
    = J (J E (g 0)) E := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T5 : op (J (J (J E (g 0)) (g 0)) E)
      (op (op (op (J (J (J E (g 0)) (g 0)) E) (J (g 0) E)) (J (g 0) E)) (op (g 1) (g 1)))
    = J (g 0) E := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem T6 : op E (op (op (op E (J (J E E) E)) (J (J E E) E)) (op (g 1) (g 1))) = J (J E E) E := by
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]

theorem law (x y z : M) : op y (op (op (op y x) x) (op z z)) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

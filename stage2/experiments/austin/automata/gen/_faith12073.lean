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

theorem F0 : op (g 0) (g 0) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F1 : op (g 0) (g 1) = (J (g 0) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F2 : op (g 0) E = (J (g 0) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F3 : op (g 0) (J (g 0) (g 0)) = (J (g 0) (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F4 : op (g 0) (J (g 0) (g 1)) = (J (g 0) (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F5 : op (g 0) (J (g 0) E) = (J (J E (g 0)) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F6 : op (g 0) (J (g 1) (g 0)) = (J (g 0) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F7 : op (g 0) (J (g 1) (g 1)) = (J (g 0) (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F8 : op (g 0) (J (g 1) E) = (J (g 0) (J (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F9 : op (g 0) (J E (g 0)) = (J (g 0) (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F10 : op (g 0) (J E (g 1)) = (J (g 0) (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F11 : op (g 0) (J E E) = (J (g 0) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F12 : op (g 1) (g 0) = (J (g 1) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F13 : op (g 1) (g 1) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F14 : op (g 1) E = (J (g 1) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F15 : op (g 1) (J (g 0) (g 0)) = (J (g 1) (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F16 : op (g 1) (J (g 0) (g 1)) = (J (g 1) (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F17 : op (g 1) (J (g 0) E) = (J (g 1) (J (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F18 : op (g 1) (J (g 1) (g 0)) = (J (g 1) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F19 : op (g 1) (J (g 1) (g 1)) = (J (g 1) (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F20 : op (g 1) (J (g 1) E) = (J (J E (g 1)) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F21 : op (g 1) (J E (g 0)) = (J (g 1) (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F22 : op (g 1) (J E (g 1)) = (J (g 1) (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F23 : op (g 1) (J E E) = (J (g 1) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F24 : op E (g 0) = (J E (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F25 : op E (g 1) = (J E (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F26 : op E E = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F27 : op E (J (g 0) (g 0)) = (J E (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F28 : op E (J (g 0) (g 1)) = (J E (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F29 : op E (J (g 0) E) = (J E (J (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F30 : op E (J (g 1) (g 0)) = (J E (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F31 : op E (J (g 1) (g 1)) = (J E (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F32 : op E (J (g 1) E) = (J E (J (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F33 : op E (J E (g 0)) = (J E (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F34 : op E (J E (g 1)) = (J E (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F35 : op E (J E E) = (J E (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F36 : op (J (g 0) (g 0)) (g 0) = (J (J (g 0) (g 0)) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F37 : op (J (g 0) (g 0)) (g 1) = (J (J (g 0) (g 0)) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F38 : op (J (g 0) (g 0)) E = (J (J (g 0) (g 0)) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F39 : op (J (g 0) (g 0)) (J (g 0) (g 0)) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F40 : op (J (g 0) (g 0)) (J (g 0) (g 1)) = (J (J (g 0) (g 0)) (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F41 : op (J (g 0) (g 0)) (J (g 0) E) = (J (J (g 0) (g 0)) (J (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F42 : op (J (g 0) (g 0)) (J (g 1) (g 0)) = (J (J (g 0) (g 0)) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F43 : op (J (g 0) (g 0)) (J (g 1) (g 1)) = (J (J (g 0) (g 0)) (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F44 : op (J (g 0) (g 0)) (J (g 1) E) = (J (J (g 0) (g 0)) (J (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F45 : op (J (g 0) (g 0)) (J E (g 0)) = (J (J (g 0) (g 0)) (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F46 : op (J (g 0) (g 0)) (J E (g 1)) = (J (J (g 0) (g 0)) (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F47 : op (J (g 0) (g 0)) (J E E) = (J (J (g 0) (g 0)) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F48 : op (J (g 0) (g 1)) (g 0) = (J (J (g 0) (g 1)) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F49 : op (J (g 0) (g 1)) (g 1) = (J (J (g 0) (g 1)) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F50 : op (J (g 0) (g 1)) E = (J (J (g 0) (g 1)) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F51 : op (J (g 0) (g 1)) (J (g 0) (g 0)) = (J (J (g 0) (g 1)) (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F52 : op (J (g 0) (g 1)) (J (g 0) (g 1)) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F53 : op (J (g 0) (g 1)) (J (g 0) E) = (J (J (g 0) (g 1)) (J (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F54 : op (J (g 0) (g 1)) (J (g 1) (g 0)) = (J (J (g 0) (g 1)) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F55 : op (J (g 0) (g 1)) (J (g 1) (g 1)) = (J (J (g 0) (g 1)) (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F56 : op (J (g 0) (g 1)) (J (g 1) E) = (J (J (g 0) (g 1)) (J (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F57 : op (J (g 0) (g 1)) (J E (g 0)) = (J (J (g 0) (g 1)) (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F58 : op (J (g 0) (g 1)) (J E (g 1)) = (J (J (g 0) (g 1)) (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F59 : op (J (g 0) (g 1)) (J E E) = (J (J (g 0) (g 1)) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F60 : op (J (g 0) E) (g 0) = (J (J (g 0) E) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F61 : op (J (g 0) E) (g 1) = (J (J (g 0) E) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F62 : op (J (g 0) E) E = (J (J (g 0) E) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F63 : op (J (g 0) E) (J (g 0) (g 0)) = (J (J (g 0) E) (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F64 : op (J (g 0) E) (J (g 0) (g 1)) = (J (J (g 0) E) (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F65 : op (J (g 0) E) (J (g 0) E) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F66 : op (J (g 0) E) (J (g 1) (g 0)) = (J (J (g 0) E) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F67 : op (J (g 0) E) (J (g 1) (g 1)) = (J (J (g 0) E) (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F68 : op (J (g 0) E) (J (g 1) E) = (J (J (g 0) E) (J (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F69 : op (J (g 0) E) (J E (g 0)) = (J (J (g 0) E) (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F70 : op (J (g 0) E) (J E (g 1)) = (J (J (g 0) E) (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F71 : op (J (g 0) E) (J E E) = (J (J (g 0) E) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F72 : op (J (g 1) (g 0)) (g 0) = (J (J (g 1) (g 0)) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F73 : op (J (g 1) (g 0)) (g 1) = (J (J (g 1) (g 0)) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F74 : op (J (g 1) (g 0)) E = (J (J (g 1) (g 0)) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F75 : op (J (g 1) (g 0)) (J (g 0) (g 0)) = (J (J (g 1) (g 0)) (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F76 : op (J (g 1) (g 0)) (J (g 0) (g 1)) = (J (J (g 1) (g 0)) (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F77 : op (J (g 1) (g 0)) (J (g 0) E) = (J (J (g 1) (g 0)) (J (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F78 : op (J (g 1) (g 0)) (J (g 1) (g 0)) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F79 : op (J (g 1) (g 0)) (J (g 1) (g 1)) = (J (J (g 1) (g 0)) (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F80 : op (J (g 1) (g 0)) (J (g 1) E) = (J (J (g 1) (g 0)) (J (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F81 : op (J (g 1) (g 0)) (J E (g 0)) = (J (J (g 1) (g 0)) (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F82 : op (J (g 1) (g 0)) (J E (g 1)) = (J (J (g 1) (g 0)) (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F83 : op (J (g 1) (g 0)) (J E E) = (J (J (g 1) (g 0)) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F84 : op (J (g 1) (g 1)) (g 0) = (J (J (g 1) (g 1)) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F85 : op (J (g 1) (g 1)) (g 1) = (J (J (g 1) (g 1)) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F86 : op (J (g 1) (g 1)) E = (J (J (g 1) (g 1)) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F87 : op (J (g 1) (g 1)) (J (g 0) (g 0)) = (J (J (g 1) (g 1)) (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F88 : op (J (g 1) (g 1)) (J (g 0) (g 1)) = (J (J (g 1) (g 1)) (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F89 : op (J (g 1) (g 1)) (J (g 0) E) = (J (J (g 1) (g 1)) (J (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F90 : op (J (g 1) (g 1)) (J (g 1) (g 0)) = (J (J (g 1) (g 1)) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F91 : op (J (g 1) (g 1)) (J (g 1) (g 1)) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F92 : op (J (g 1) (g 1)) (J (g 1) E) = (J (J (g 1) (g 1)) (J (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F93 : op (J (g 1) (g 1)) (J E (g 0)) = (J (J (g 1) (g 1)) (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F94 : op (J (g 1) (g 1)) (J E (g 1)) = (J (J (g 1) (g 1)) (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F95 : op (J (g 1) (g 1)) (J E E) = (J (J (g 1) (g 1)) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F96 : op (J (g 1) E) (g 0) = (J (J (g 1) E) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F97 : op (J (g 1) E) (g 1) = (J (J (g 1) E) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F98 : op (J (g 1) E) E = (J (J (g 1) E) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F99 : op (J (g 1) E) (J (g 0) (g 0)) = (J (J (g 1) E) (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F100 : op (J (g 1) E) (J (g 0) (g 1)) = (J (J (g 1) E) (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F101 : op (J (g 1) E) (J (g 0) E) = (J (J (g 1) E) (J (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F102 : op (J (g 1) E) (J (g 1) (g 0)) = (J (J (g 1) E) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F103 : op (J (g 1) E) (J (g 1) (g 1)) = (J (J (g 1) E) (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F104 : op (J (g 1) E) (J (g 1) E) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F105 : op (J (g 1) E) (J E (g 0)) = (J (J (g 1) E) (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F106 : op (J (g 1) E) (J E (g 1)) = (J (J (g 1) E) (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F107 : op (J (g 1) E) (J E E) = (J (J (g 1) E) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F108 : op (J E (g 0)) (g 0) = (J (J E (g 0)) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F109 : op (J E (g 0)) (g 1) = (J (J E (g 0)) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F110 : op (J E (g 0)) E = (J (J E (g 0)) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F111 : op (J E (g 0)) (J (g 0) (g 0)) = (J (J E (g 0)) (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F112 : op (J E (g 0)) (J (g 0) (g 1)) = (J (J E (g 0)) (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F113 : op (J E (g 0)) (J (g 0) E) = (J (J E (g 0)) (J (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F114 : op (J E (g 0)) (J (g 1) (g 0)) = (J (J E (g 0)) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F115 : op (J E (g 0)) (J (g 1) (g 1)) = (J (J E (g 0)) (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F116 : op (J E (g 0)) (J (g 1) E) = (J (J E (g 0)) (J (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F117 : op (J E (g 0)) (J E (g 0)) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F118 : op (J E (g 0)) (J E (g 1)) = (J (J E (g 0)) (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F119 : op (J E (g 0)) (J E E) = (J (J E (g 0)) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F120 : op (J E (g 1)) (g 0) = (J (J E (g 1)) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F121 : op (J E (g 1)) (g 1) = (J (J E (g 1)) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F122 : op (J E (g 1)) E = (J (J E (g 1)) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F123 : op (J E (g 1)) (J (g 0) (g 0)) = (J (J E (g 1)) (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F124 : op (J E (g 1)) (J (g 0) (g 1)) = (J (J E (g 1)) (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F125 : op (J E (g 1)) (J (g 0) E) = (J (J E (g 1)) (J (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F126 : op (J E (g 1)) (J (g 1) (g 0)) = (J (J E (g 1)) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F127 : op (J E (g 1)) (J (g 1) (g 1)) = (J (J E (g 1)) (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F128 : op (J E (g 1)) (J (g 1) E) = (J (J E (g 1)) (J (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F129 : op (J E (g 1)) (J E (g 0)) = (J (J E (g 1)) (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F130 : op (J E (g 1)) (J E (g 1)) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F131 : op (J E (g 1)) (J E E) = (J (J E (g 1)) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F132 : op (J E E) (g 0) = (J (J E E) (g 0)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F133 : op (J E E) (g 1) = (J (J E E) (g 1)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F134 : op (J E E) E = (J (J E E) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F135 : op (J E E) (J (g 0) (g 0)) = (J (J E E) (J (g 0) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F136 : op (J E E) (J (g 0) (g 1)) = (J (J E E) (J (g 0) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F137 : op (J E E) (J (g 0) E) = (J (J E E) (J (g 0) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F138 : op (J E E) (J (g 1) (g 0)) = (J (J E E) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F139 : op (J E E) (J (g 1) (g 1)) = (J (J E E) (J (g 1) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F140 : op (J E E) (J (g 1) E) = (J (J E E) (J (g 1) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F141 : op (J E E) (J E (g 0)) = (J (J E E) (J E (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F142 : op (J E E) (J E (g 1)) = (J (J E E) (J E (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F143 : op (J E E) (J E E) = E := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F144 : op (J (J (g 0) (g 0)) E) (J (g 0) (J (g 1) (J (g 0) E))) = (J (J (J (g 0) (g 0)) E) (J (g 0) (J (g 1) (J (g 0) E)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F145 : op (J (J (g 1) (g 0)) E) (J (J (g 0) (J E E)) (g 0)) = (J (J (J (g 1) (g 0)) E) (J (J (g 0) (J E E)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F146 : op (J (g 1) (g 0)) (J E (J E (g 1))) = (J (J (g 1) (g 0)) (J E (J E (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F147 : op (J (g 0) (J (g 0) (g 0))) (J E (J (g 1) (J (g 1) (g 1)))) = (J (J (g 0) (J (g 0) (g 0))) (J E (J (g 1) (J (g 1) (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F148 : op (J (g 1) (g 1)) (J (J (J E E) (g 1)) (g 0)) = (J (J (g 1) (g 1)) (J (J (J E E) (g 1)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F149 : op (J (J E E) (g 1)) (J (g 0) (J (J (g 1) E) (g 1))) = (J (J (J E E) (g 1)) (J (g 0) (J (J (g 1) E) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F150 : op (J (g 0) (g 1)) (J (J (g 0) (g 1)) E) = (J (J E (J (g 0) (g 1))) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F151 : op (J (J (g 1) E) (g 1)) (J E (J (J (g 1) (g 1)) (g 1))) = (J (J (J (g 1) E) (g 1)) (J E (J (J (g 1) (g 1)) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F152 : op (J (g 1) E) (J (g 1) (J (g 0) (J (g 1) (g 0)))) = (J (J (g 1) E) (J (g 1) (J (g 0) (J (g 1) (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F153 : op (J E E) (J (J E (g 0)) (J (g 0) (g 0))) = (J (J E E) (J (J E (g 0)) (J (g 0) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F154 : op (J (J (g 1) E) (g 0)) (J E (J (g 0) (g 0))) = (J (J (J (g 1) E) (g 0)) (J E (J (g 0) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F155 : op (J (g 0) (J (g 1) (g 0))) (J (g 0) (J (J E (g 1)) (g 0))) = (J (J (g 0) (J (g 1) (g 0))) (J (g 0) (J (J E (g 1)) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F156 : op (J (g 1) (g 1)) (J (J E (g 1)) (J (g 1) (g 1))) = (J (J (g 1) (g 1)) (J (J E (g 1)) (J (g 1) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F157 : op (J (J (g 1) (g 0)) E) (J (g 1) (J (g 1) (g 1))) = (J (J (J (g 1) (g 0)) E) (J (g 1) (J (g 1) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F158 : op (J (g 1) (J E (g 1))) (J (g 1) (J (g 0) E)) = (J (J (g 1) (J E (g 1))) (J (g 1) (J (g 0) E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F159 : op (J (g 0) (J (g 1) E)) (J (g 1) (J (J (g 0) (g 0)) (g 1))) = (J (J (g 0) (J (g 1) E)) (J (g 1) (J (J (g 0) (g 0)) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F160 : op (J (J (g 1) (g 1)) E) (J (g 0) (J (g 0) (J E (g 1)))) = (J (J (J (g 1) (g 1)) E) (J (g 0) (J (g 0) (J E (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F161 : op (J (g 0) (J (g 1) (g 0))) (J (J E (g 1)) (J (g 0) (g 1))) = (J (J (g 0) (J (g 1) (g 0))) (J (J E (g 1)) (J (g 0) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F162 : op (J (J (g 0) (g 0)) (g 0)) (J (J E (g 0)) (J (g 1) (g 1))) = (J (J (J (g 0) (g 0)) (g 0)) (J (J E (g 0)) (J (g 1) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F163 : op (J (g 1) (J (g 0) E)) (J (J (g 1) (g 1)) (g 1)) = (J (J (g 1) (J (g 0) E)) (J (J (g 1) (g 1)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F164 : op (J (g 1) (J (g 1) (g 0))) (J E (J (g 1) (J E (g 1)))) = (J (J (g 1) (J (g 1) (g 0))) (J E (J (g 1) (J E (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F165 : op (J (g 0) (J (g 0) (g 0))) (J (J (g 1) E) (J E (g 1))) = (J (J (g 0) (J (g 0) (g 0))) (J (J (g 1) E) (J E (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F166 : op (J (g 1) E) (J (J E (g 0)) (J E (g 0))) = (J (J (g 1) E) (J (J E (g 0)) (J E (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F167 : op (J (g 1) (g 1)) (J (J (g 0) (J (g 0) E)) (g 1)) = (J (J (g 1) (g 1)) (J (J (g 0) (J (g 0) E)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F168 : op (J (g 1) (J (g 1) E)) (J (J (g 0) E) (J E E)) = (J (J (g 1) (J (g 1) E)) (J (J (g 0) E) (J E E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F169 : op (J (J (g 1) E) (g 0)) (J (J (J (g 0) (g 0)) E) (g 1)) = (J (J (J (g 1) E) (g 0)) (J (J (J (g 0) (g 0)) E) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F170 : op (J (J (g 0) (g 0)) (g 1)) (J (J (g 0) (g 1)) (J (g 0) (g 1))) = (J (J (J (g 0) (g 0)) (g 1)) (J (J (g 0) (g 1)) (J (g 0) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F171 : op (J (J E (g 0)) (g 1)) (J E (J (g 1) (J (g 0) E))) = (J (J (J E (g 0)) (g 1)) (J E (J (g 1) (J (g 0) E)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F172 : op (J E (J E E)) (J (g 1) (J (g 0) (J E (g 1)))) = (J (J E (J E E)) (J (g 1) (J (g 0) (J E (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F173 : op (J (g 1) (J (g 0) E)) (J (J (g 1) (J E (g 1))) (g 0)) = (J (J (g 1) (J (g 0) E)) (J (J (g 1) (J E (g 1))) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F174 : op (J E (J (g 0) (g 1))) (J (J (g 0) (g 0)) E) = (J (J E (J (g 0) (g 1))) (J (J (g 0) (g 0)) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F175 : op (J E (J E E)) (J (J (g 1) (g 1)) (J (g 1) (g 1))) = (J (J E (J E E)) (J (J (g 1) (g 1)) (J (g 1) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F176 : op (J (J E E) (g 0)) (J (J (J E (g 0)) (g 1)) (g 1)) = (J (J (J E E) (g 0)) (J (J (J E (g 0)) (g 1)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F177 : op (J (J (g 0) (g 1)) (g 1)) (J (J E (J (g 1) (g 0))) (g 1)) = (J (J (J (g 0) (g 1)) (g 1)) (J (J E (J (g 1) (g 0))) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F178 : op (J (J E (g 0)) (g 0)) (J (g 1) (J (J (g 0) (g 0)) (g 0))) = (J (J (J E (g 0)) (g 0)) (J (g 1) (J (J (g 0) (g 0)) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F179 : op (J E (g 0)) (J (J E (g 1)) (g 0)) = (J (J E (g 0)) (J (J E (g 1)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F180 : op (J (J E E) E) (J E (J (J (g 1) (g 1)) (g 1))) = (J (J (J E E) E) (J E (J (J (g 1) (g 1)) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F181 : op (J (g 1) (J (g 0) (g 0))) (J (J E (J E E)) (g 0)) = (J (J (g 1) (J (g 0) (g 0))) (J (J E (J E E)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F182 : op (J (J (g 0) (g 1)) (g 1)) (J (g 0) (J (g 1) (J (g 0) E))) = (J (J (J (g 0) (g 1)) (g 1)) (J (g 0) (J (g 1) (J (g 0) E)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F183 : op (J (J E (g 1)) E) (J E (J (J (g 1) (g 1)) E)) = (J (J (J E (g 1)) E) (J E (J (J (g 1) (g 1)) E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F184 : op (J (g 0) E) (J (J (g 1) (J (g 0) E)) (g 0)) = (J (J (g 0) E) (J (J (g 1) (J (g 0) E)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F185 : op (J E (g 0)) (J (J (J (g 0) (g 0)) (g 0)) (g 1)) = (J (J E (g 0)) (J (J (J (g 0) (g 0)) (g 0)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F186 : op (J (J (g 0) (g 0)) (g 1)) (J E (J (g 0) (J (g 0) (g 0)))) = (J (J (J (g 0) (g 0)) (g 1)) (J E (J (g 0) (J (g 0) (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F187 : op (J (J (g 0) (g 1)) E) (J (J E E) (J (g 1) (g 1))) = (J (J (J (g 0) (g 1)) E) (J (J E E) (J (g 1) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F188 : op (J (J E E) (g 0)) (J (J E (g 1)) (J (g 1) E)) = (J (J (J E E) (g 0)) (J (J E (g 1)) (J (g 1) E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F189 : op (J (J E (g 0)) (g 1)) (J E (J (g 1) E)) = (J (J (J E (g 0)) (g 1)) (J E (J (g 1) E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F190 : op (J E E) (J (g 1) (J E (J (g 0) (g 0)))) = (J (J E E) (J (g 1) (J E (J (g 0) (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F191 : op (J (J E (g 1)) (g 0)) (J (J (g 1) (J E (g 0))) E) = (J (J (J E (g 1)) (g 0)) (J (J (g 1) (J E (g 0))) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F192 : op (J (g 1) E) (J E (J (g 0) (g 1))) = (J (J (g 1) E) (J E (J (g 0) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F193 : op (J (J (g 0) (g 0)) (g 0)) (J (J (g 0) (J E (g 1))) (g 1)) = (J (J (J (g 0) (g 0)) (g 0)) (J (J (g 0) (J E (g 1))) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F194 : op (J (J E (g 0)) (g 0)) (J (g 1) (J E (J E (g 1)))) = (J (J (J E (g 0)) (g 0)) (J (g 1) (J E (J E (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F195 : op (J (J (g 1) (g 0)) (g 1)) (J (J (J E (g 1)) (g 0)) (g 1)) = (J (J (J (g 1) (g 0)) (g 1)) (J (J (J E (g 1)) (g 0)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F196 : op (J (J (g 0) (g 1)) E) (J E E) = (J (J (J (g 0) (g 1)) E) (J E E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F197 : op (J (J E (g 0)) E) (J E (J (g 0) (J E (g 1)))) = (J (J (J E (g 0)) E) (J E (J (g 0) (J E (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F198 : op (J (g 1) (J (g 0) (g 0))) (J (J (g 0) (J (g 0) (g 1))) (g 0)) = (J (J (g 1) (J (g 0) (g 0))) (J (J (g 0) (J (g 0) (g 1))) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F199 : op (J (g 0) (J (g 0) E)) (J (J (g 0) E) (J E (g 0))) = (J (J (g 0) (J (g 0) E)) (J (J (g 0) E) (J E (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F200 : op (J (g 1) (g 1)) (J (g 0) (J (J E (g 0)) (g 0))) = (J (J (g 1) (g 1)) (J (g 0) (J (J E (g 0)) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F201 : op (J E (J E (g 0))) (J (g 0) (J (g 0) (J (g 0) (g 0)))) = (J (J E (J E (g 0))) (J (g 0) (J (g 0) (J (g 0) (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F202 : op (J E (J (g 0) (g 1))) (J E (J (J (g 0) (g 0)) E)) = (J (J E (J (g 0) (g 1))) (J E (J (J (g 0) (g 0)) E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F203 : op (J (J (g 1) (g 0)) E) (J (J (J E E) E) (g 1)) = (J (J (J (g 1) (g 0)) E) (J (J (J E E) E) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F204 : op (J (J E E) (g 0)) (J (J (g 0) (g 0)) E) = (J (J (J E E) (g 0)) (J (J (g 0) (g 0)) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F205 : op (J (g 1) (J (g 0) (g 0))) (J (J (g 0) (g 0)) (J (g 0) (g 1))) = (J (J (g 1) (J (g 0) (g 0))) (J (J (g 0) (g 0)) (J (g 0) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F206 : op (J (J (g 1) (g 1)) (g 0)) (J (J (g 1) E) (J E E)) = (J (J (J (g 1) (g 1)) (g 0)) (J (J (g 1) E) (J E E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F207 : op (J E (J (g 1) E)) (J (J (J E (g 0)) E) E) = (J (J E (J (g 1) E)) (J (J (J E (g 0)) E) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F208 : op (J (g 0) (J (g 1) E)) (J (J (J (g 1) (g 0)) (g 0)) E) = (J (J (g 0) (J (g 1) E)) (J (J (J (g 1) (g 0)) (g 0)) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F209 : op (J (J (g 1) E) (g 1)) (J (J (J (g 1) E) E) (g 1)) = (J (J (J (g 1) E) (g 1)) (J (J (J (g 1) E) E) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F210 : op (J E (J (g 1) E)) (J (J (g 1) (J E E)) (g 1)) = (J (J E (J (g 1) E)) (J (J (g 1) (J E E)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F211 : op (J (J (g 1) (g 1)) E) (J E (J (g 1) (J (g 0) (g 0)))) = (J (J (J (g 1) (g 1)) E) (J E (J (g 1) (J (g 0) (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F212 : op (J (J (g 1) (g 0)) (g 0)) (J (g 0) (J (J E E) (g 1))) = (J (J (J (g 1) (g 0)) (g 0)) (J (g 0) (J (J E E) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F213 : op (J (g 0) (J E (g 1))) (J (J (g 0) (g 1)) (g 0)) = (J (J (g 0) (J E (g 1))) (J (J (g 0) (g 1)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F214 : op (J (g 1) (J (g 0) (g 1))) (J (g 0) (J (g 1) (J (g 0) E))) = (J (J (g 1) (J (g 0) (g 1))) (J (g 0) (J (g 1) (J (g 0) E)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F215 : op (J (g 1) (J E E)) (J (J (g 1) (J (g 0) (g 0))) (g 1)) = (J (J (g 1) (J E E)) (J (J (g 1) (J (g 0) (g 0))) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F216 : op (J (g 1) (J E E)) (J (g 1) (g 0)) = (J (J (g 1) (J E E)) (J (g 1) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F217 : op (J (J E (g 1)) E) (J (J (J (g 1) (g 0)) E) E) = (J (J (J E (g 1)) E) (J (J (J (g 1) (g 0)) E) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F218 : op (J (g 1) (J (g 0) E)) (J (g 1) (J (g 1) (J (g 1) E))) = (J (J (g 1) (J (g 0) E)) (J (g 1) (J (g 1) (J (g 1) E)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F219 : op (J E (J E (g 0))) E = (J (J E (J E (g 0))) E) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F220 : op (J (g 0) (J E (g 0))) (J E (J (J (g 1) (g 1)) (g 1))) = (J (J (g 0) (J E (g 0))) (J E (J (J (g 1) (g 1)) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F221 : op (J (J (g 0) E) E) (J (J (g 0) (J (g 0) (g 1))) (g 0)) = (J (J (J (g 0) E) E) (J (J (g 0) (J (g 0) (g 1))) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F222 : op (J (J (g 0) (g 0)) (g 1)) (J (J E E) (g 1)) = (J (J (J (g 0) (g 0)) (g 1)) (J (J E E) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F223 : op (J (J E E) E) (J (J (g 0) (J (g 0) E)) (g 1)) = (J (J (J E E) E) (J (J (g 0) (J (g 0) E)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F224 : op (J (g 1) (g 0)) (J (J (g 0) (g 0)) (J (g 1) E)) = (J (J (g 1) (g 0)) (J (J (g 0) (g 0)) (J (g 1) E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F225 : op (J (J (g 1) (g 0)) E) (J E (J (J (g 0) (g 0)) E)) = (J (J (J (g 1) (g 0)) E) (J E (J (J (g 0) (g 0)) E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F226 : op (J (J (g 1) (g 1)) (g 0)) (J E (J (J (g 0) (g 0)) (g 0))) = (J (J (J (g 1) (g 1)) (g 0)) (J E (J (J (g 0) (g 0)) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F227 : op (J (g 0) (J (g 0) (g 1))) (J (J (g 0) E) (J (g 0) (g 0))) = (J (J (g 0) (J (g 0) (g 1))) (J (J (g 0) E) (J (g 0) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F228 : op (J (J (g 1) (g 1)) (g 0)) (J E (J (g 0) (g 1))) = (J (J (J (g 1) (g 1)) (g 0)) (J E (J (g 0) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F229 : op (J (g 1) (J (g 1) (g 0))) (J E (J (g 1) (g 1))) = (J (J (g 1) (J (g 1) (g 0))) (J E (J (g 1) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F230 : op (J (g 1) (J (g 1) E)) (J E (J (J E E) (g 0))) = (J (J (g 1) (J (g 1) E)) (J E (J (J E E) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F231 : op (J (g 0) (J E E)) (J (J (g 1) E) E) = (J (J (g 0) (J E E)) (J (J (g 1) E) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F232 : op (J (J (g 0) (g 1)) (g 1)) (J (J E E) (J E (g 1))) = (J (J (J (g 0) (g 1)) (g 1)) (J (J E E) (J E (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F233 : op (J (g 1) (g 0)) (J (J (g 1) (g 1)) (g 1)) = (J (J (g 1) (g 0)) (J (J (g 1) (g 1)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F234 : op (g 0) (J (J E (g 0)) (J E E)) = (J (g 0) (J (J E (g 0)) (J E E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F235 : op (J (g 0) (J E (g 1))) (J (J (g 1) E) (J (g 0) (g 1))) = (J (J (g 0) (J E (g 1))) (J (J (g 1) E) (J (g 0) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F236 : op (J (g 0) (J (g 0) (g 0))) (J E (J (g 1) (J (g 1) (g 0)))) = (J (J (g 0) (J (g 0) (g 0))) (J E (J (g 1) (J (g 1) (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F237 : op (J (g 0) (g 0)) (J E (J E (g 0))) = (J (J (g 0) (g 0)) (J E (J E (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F238 : op (J (g 1) (J (g 1) E)) (J (J (g 0) (J (g 0) (g 1))) E) = (J (J (g 1) (J (g 1) E)) (J (J (g 0) (J (g 0) (g 1))) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F239 : op (J (J (g 1) (g 0)) (g 0)) (J (g 0) (J (g 1) (J (g 0) (g 1)))) = (J (J (J (g 1) (g 0)) (g 0)) (J (g 0) (J (g 1) (J (g 0) (g 1))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F240 : op (J E (J (g 0) E)) (J E (J (g 0) (J (g 1) (g 0)))) = (J (J E (J (g 0) E)) (J E (J (g 0) (J (g 1) (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F241 : op (J (J (g 0) E) (g 1)) (J (J (g 0) (g 1)) (J (g 1) E)) = (J (J (J (g 0) E) (g 1)) (J (J (g 0) (g 1)) (J (g 1) E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F242 : op (J (g 0) (J (g 1) (g 0))) (J (J E (g 0)) E) = (J (J (g 0) (J (g 1) (g 0))) (J (J E (g 0)) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F243 : op (J (J E (g 1)) E) (J (J (g 0) (g 1)) (J (g 0) (g 1))) = (J (J (J E (g 1)) E) (J (J (g 0) (g 1)) (J (g 0) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F244 : op (J (J E (g 1)) (g 1)) (J (J (g 0) E) (J (g 0) (g 1))) = (J (J (J E (g 1)) (g 1)) (J (J (g 0) E) (J (g 0) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F245 : op (J (J (g 0) (g 0)) (g 0)) (J (J (g 0) (g 1)) (g 1)) = (J (J (J (g 0) (g 0)) (g 0)) (J (J (g 0) (g 1)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F246 : op (J (g 0) (J E (g 0))) (J (J (g 1) (g 1)) (g 1)) = (J (J (g 0) (J E (g 0))) (J (J (g 1) (g 1)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F247 : op (J (J (g 0) (g 1)) (g 1)) (J (J E (J (g 1) E)) (g 1)) = (J (J (J (g 0) (g 1)) (g 1)) (J (J E (J (g 1) E)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F248 : op (J E (J (g 1) (g 0))) (J (J (g 0) (g 1)) (J E E)) = (J (J E (J (g 1) (g 0))) (J (J (g 0) (g 1)) (J E E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F249 : op (J (g 0) (J E E)) (J (J (g 1) (g 1)) (J (g 0) (g 0))) = (J (J (g 0) (J E E)) (J (J (g 1) (g 1)) (J (g 0) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F250 : op E (J (g 0) (J (J (g 1) (g 1)) (g 0))) = (J E (J (g 0) (J (J (g 1) (g 1)) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F251 : op (J (J (g 0) E) (g 1)) (J (g 0) (J (g 1) (J (g 0) (g 0)))) = (J (J (J (g 0) E) (g 1)) (J (g 0) (J (g 1) (J (g 0) (g 0))))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F252 : op (J (g 0) (g 0)) (J (J E (J E E)) (g 1)) = (J (J (g 0) (g 0)) (J (J E (J E E)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F253 : op (J E (J E E)) (J (J (g 0) (J E (g 0))) E) = (J (J E (J E E)) (J (J (g 0) (J E (g 0))) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F254 : op (J E E) (J (J (g 1) (J E (g 0))) E) = (J (J E E) (J (J (g 1) (J E (g 0))) E)) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F255 : op (J E (J (g 1) (g 0))) (J (J (g 1) (g 1)) (J (g 0) (g 1))) = (J (J E (J (g 1) (g 0))) (J (J (g 1) (g 1)) (J (g 0) (g 1)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F256 : op (J (J (g 0) E) (g 1)) (J (J (J E E) (g 1)) (g 0)) = (J (J (J (g 0) E) (g 1)) (J (J (J E E) (g 1)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F257 : op (J (g 1) (J (g 0) (g 0))) (J E (J (g 0) (J E E))) = (J (J (g 1) (J (g 0) (g 0))) (J E (J (g 0) (J E E)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F258 : op (J (g 1) (J E (g 1))) (J (J (g 1) (g 1)) (J E E)) = (J (J (g 1) (J E (g 1))) (J (J (g 1) (g 1)) (J E E))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F259 : op (J (J E E) (g 1)) (J (g 1) (J (J E (g 1)) (g 0))) = (J (J (J E E) (g 1)) (J (g 1) (J (J E (g 1)) (g 0)))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F260 : op (J (g 1) (J E (g 1))) (J (J (g 0) (J (g 0) (g 1))) (g 1)) = (J (J (g 1) (J E (g 1))) (J (J (g 0) (J (g 0) (g 1))) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F261 : op (J (g 1) (J (g 1) (g 0))) (J (J (J (g 0) E) (g 1)) (g 1)) = (J (J (g 1) (J (g 1) (g 0))) (J (J (J (g 0) E) (g 1)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F262 : op (J E (J (g 0) (g 0))) (J (J (J (g 1) (g 0)) (g 0)) (g 1)) = (J (J E (J (g 0) (g 0))) (J (J (J (g 1) (g 0)) (g 0)) (g 1))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]
theorem F263 : op (J (J (g 1) (g 1)) (g 0)) (J (J E (J (g 1) E)) (g 0)) = (J (J (J (g 1) (g 1)) (g 0)) (J (J E (J (g 1) E)) (g 0))) := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]


theorem law (x y z : M) : op y (op (op (op y x) x) (op z z)) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))

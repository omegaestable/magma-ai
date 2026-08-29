import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

-- cex33020.lean : `theorem law` of gen/rec33020.lean is FALSE in the skeleton's own model.
-- Everything up to `rhs` is gen/rec33020.lean verbatim; the counterexamples follow.
-- Compile: D=<dev_33020_28770> bash devlean2.sh gen/cex33020.lean

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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ tg (a2 (a2 (a1 v))) = 2 ∧ u = a1 (a2 (a2 (a1 v))) ∧ a1 (a1 v) = a2 (a2 (a2 (a1 v))) ∧ u = a2 v
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ u = a2 v
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 v
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (u) (a1 (a1 v)) < msr u v then op (u) (a1 (a1 v)) else J u v
  let p2 := if hs2 : msr (a1 (a2 (a2 (a1 (p1))))) (p1) < msr u v then op (a1 (a2 (a2 (a1 (p1))))) (p1) else J u v
  if P1 u v then a1 (a1 v)
  else if P2 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ a2 (a2 (a1 v)) = p1 then a1 (a1 v)
  else if P3 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a1 (a2 (a2 (a1 (p1))))) (p1) < msr u v ∧ tg (p1) = 2 ∧ tg (a1 (p1)) = 2 ∧ tg (a2 (a1 (p1))) = 2 ∧ tg (a2 (a2 (a1 (p1)))) = 2 ∧ a2 (a1 v) = p2 then a1 (a1 v)
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (g 2) (g 0)) (op (g 1) (op (g 0) (op (g 0) (g 0))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3]

-- ---------------------------------------------------------------------------------------------
-- y1 = T(g0, g1, g2) evaluated freely: it genuinely encodes g0 by g1, so op (g 1) y1 = g 0 (R1).
def y1 : M := J (J (g 0) (J (g 2) (J (g 1) (g 0)))) (g 1)

theorem c3 : op (g 1) y1 = g 0 := by
  rw [op.eq_1]; rw [if_pos (by decide)]; rfl

-- Instance I2: y = J y1 (J g2 g0) is the encoding of y1 by g1 whose inner product g1*y1 = g0 was decoded.
def cy : M := J y1 (J (g 2) (g 0))

theorem c0 : op cy (g 1) = J cy (g 1) := op_free (by unfold Pre; decide)
theorem c1 : op (g 1) (a1 (a1 (J cy (g 1)))) = g 0 := by
  rw [op.eq_1]; rw [if_pos (by decide)]; rfl
/-- s2 = g1 * (y * g1) fires by R2 (correctly: J y g1 = T(y1, g1, g2) in the model) and returns y1 -/
theorem c2 : op (g 1) (J cy (g 1)) = y1 := by
  rw [op.eq_1]
  rw [if_neg (by decide : ¬ P1 (g 1) (J cy (g 1)))]
  rw [dif_pos (by decide : msr (g 1) (a1 (a1 (J cy (g 1)))) < msr (g 1) (J cy (g 1)))]
  rw [c1]
  rw [if_pos (by decide)]; rfl
/-- s3 = g1 * y1 = g0 fires (R1); then s4 = g0 * y and y * s4 are free: no rule decodes (y, J g0 y) -/
theorem c4 : op (g 0) cy = J (g 0) cy := op_free (by unfold Pre; decide)
theorem c5 : op cy (J (g 0) cy) = J cy (J (g 0) cy) := op_free (by unfold Pre; decide)

/-- the statement of `theorem law` (x = g 1, y = cy, z = g 1) is FALSE in this model -/
theorem cexI2 : op cy (op (op (g 1) (op (g 1) (op cy (g 1)))) cy) ≠ g 1 := by
  rw [c0, c2, c3, c4, c5]; decide

-- Instance I1: y = J y1 (J g2 (J g1 y1)) has the R1 SHAPE for u = g1 (x' = y1, z' = g2) although
-- J g1 y1 ≠ op (g 1) y1 = g 0, so R1 [free] decodes a term that is not an encoding.
def cy1 : M := J y1 (J (g 2) (J (g 1) y1))

theorem d0 : op cy1 (g 1) = J cy1 (g 1) := op_free (by unfold Pre; decide)
theorem d2 : op (g 1) (J cy1 (g 1)) = y1 := by
  rw [op.eq_1]; rw [if_pos (by decide)]; rfl
theorem d4 : op (g 0) cy1 = J (g 0) cy1 := op_free (by unfold Pre; decide)
theorem d5 : op cy1 (J (g 0) cy1) = J cy1 (J (g 0) cy1) := op_free (by unfold Pre; decide)

theorem cexI1 : op cy1 (op (op (g 1) (op (g 1) (op cy1 (g 1)))) cy1) ≠ g 1 := by
  rw [d0, d2, c3, d4, d5]; decide

-- Instance I3 (the smallest; oriented deep tests, seed 11): x = z = J g1 (J g1 (J g0 g1)), y = J g0 g1.
-- s2 = x * (y * x) fires by R3 (correctly: J y x = T(g0, x, g0) in the model) to g0; s3 = x * g0 and
-- s4 = (x * g0) * y are free; the decoder R3 at (y, J (J x g0) y) looks for z at (y * x).1.2.2.1 = y.2.2.1,
-- but y.2 = g1 is not a J -- the `u = v.2` invariant says z = (y * x).2 = x.
def x3 : M := J (g 1) (J (g 1) (J (g 0) (g 1)))
def y3 : M := J (g 0) (g 1)

theorem e0 : op y3 x3 = J y3 x3 := op_free (by unfold Pre; decide)
theorem e1 : op x3 (a1 (a1 (J y3 x3))) = J x3 (a1 (a1 (J y3 x3))) := op_free (by unfold Pre; decide)
theorem e2 : op (a1 (a2 (a2 (a1 (J x3 (a1 (a1 (J y3 x3)))))))) (J x3 (a1 (a1 (J y3 x3)))) = g 1 := by
  rw [op.eq_1]; rw [if_pos (by decide)]; rfl
theorem e3 : op x3 (J y3 x3) = g 0 := by
  rw [op.eq_1]
  rw [if_neg (by decide : ¬ P1 x3 (J y3 x3))]
  rw [dif_pos (by decide : msr x3 (a1 (a1 (J y3 x3))) < msr x3 (J y3 x3))]
  rw [e1]
  rw [dif_pos (by decide : msr (a1 (a2 (a2 (a1 (J x3 (a1 (a1 (J y3 x3)))))))) (J x3 (a1 (a1 (J y3 x3)))) < msr x3 (J y3 x3))]
  rw [e2]
  rw [if_neg (by decide)]
  rw [if_pos (by decide)]; rfl
theorem e4 : op x3 (g 0) = J x3 (g 0) := op_free (by unfold Pre; decide)
theorem e5 : op (J x3 (g 0)) y3 = J (J x3 (g 0)) y3 := op_free (by unfold Pre; decide)
-- P3 y3 (J (J x3 g0) y3) HOLDS (so op_free does not apply); R3's full guard then fails on tg y3.2 = tg g1.
theorem f1 : op y3 (a1 (a1 (J (J x3 (g 0)) y3))) = J y3 (a1 (a1 (J (J x3 (g 0)) y3))) := op_free (by unfold Pre; decide)
theorem f2 : op (a1 (a2 (a2 (a1 (J y3 (a1 (a1 (J (J x3 (g 0)) y3)))))))) (J y3 (a1 (a1 (J (J x3 (g 0)) y3)))) =
    J (a1 (a2 (a2 (a1 (J y3 (a1 (a1 (J (J x3 (g 0)) y3)))))))) (J y3 (a1 (a1 (J (J x3 (g 0)) y3)))) :=
  op_free (by unfold Pre; decide)
theorem e6 : op y3 (J (J x3 (g 0)) y3) = J y3 (J (J x3 (g 0)) y3) := by
  rw [op.eq_1]
  rw [if_neg (by decide : ¬ P1 y3 (J (J x3 (g 0)) y3))]
  rw [dif_pos (by decide : msr y3 (a1 (a1 (J (J x3 (g 0)) y3))) < msr y3 (J (J x3 (g 0)) y3))]
  rw [f1]
  rw [dif_pos (by decide : msr (a1 (a2 (a2 (a1 (J y3 (a1 (a1 (J (J x3 (g 0)) y3)))))))) (J y3 (a1 (a1 (J (J x3 (g 0)) y3)))) < msr y3 (J (J x3 (g 0)) y3))]
  rw [f2]
  rw [if_neg (by decide)]
  rw [if_neg (by decide)]

theorem cexI3 : op y3 (op (op x3 (op x3 (op y3 x3))) y3) ≠ x3 := by
  rw [e0, e3, e4, e5, e6]; decide

/-- hence the served (flipped) magma violates EquationLHS of 33020: `lhs` of the skeleton is unprovable -/
theorem not_lhs : ¬ @EquationLHS M inst := by
  intro h
  have := h (g 1) cy (g 1)
  revert this
  change ¬ g 1 = op cy (op (op (g 1) (op (g 1) (op cy (g 1)))) cy)
  intro e; exact cexI2 e.symm

theorem not_lhs' : ¬ @EquationLHS M inst := by
  intro h
  have := h x3 y3 x3
  revert this
  change ¬ x3 = op y3 (op (op x3 (op x3 (op y3 x3))) y3)
  intro e; exact cexI3 e.symm

end submission

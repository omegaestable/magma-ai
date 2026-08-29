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

def P1 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ a1 (a1 (a2 v)) = a2 (a2 (a1 (a2 v))) ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a2 v) ∧ tg (a1 (a1 (a2 v))) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ a1 (a1 u) = a2 (a2 (a1 u))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) < msr u v then op (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) else J u v
  let p2 := if hs2 : msr (a1 u) (u) < msr u v then op (a1 u) (u) else J u v
  if P1 u v then a1 (a1 (a2 v))
  else if P2 u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) < msr u v ∧ a2 (a1 (a2 v)) = p1 then a1 (a1 (a2 v))
  else if P3 u v ∧ msr (a1 u) (u) < msr u v ∧ a2 v = p2 then a1 (a1 u)
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]


/-! Counterexample to `law` for the generated 7701 skeleton (a level-2 decoder hole).
    x encodes g1 by z = g0, so z◇x decodes to g1 and q2 = x◇(z◇x) = J x g1 carries a DECODED right child;
    y then encodes g3 by q2 (R1 shape), so (q2◇y) = g3, y◇g3 is free, and at the top neither R1 nor R3
    can fire (both need the right child of a1 y to be a J-product `J z x`), so the result is J y (J y g3) ≠ x. -/
def cxZ : M := g 0
def cxX : M := J (g 0) (J (J (g 1) (J (g 2) (g 1))) (g 0))
def cxQ2 : M := J cxX (g 1)
def cxY : M := J cxQ2 (J (J (g 3) (J (g 4) (g 3))) cxQ2)

theorem cx_steps :
    op cxZ cxX = g 1 ∧
    op cxX (g 1) = J cxX (g 1) ∧
    op cxQ2 cxY = g 3 ∧
    op cxY (g 3) = J cxY (g 3) ∧
    op cxY (J cxY (g 3)) = J cxY (J cxY (g 3)) := by
  simp (config := {decide := true}) [cxZ, cxX, cxQ2, cxY, op.eq_1, sz, msr, P1, P2, P3]

theorem cx_law_fails : op cxY (op cxY (op (op cxX (op cxZ cxX)) cxY)) ≠ cxX := by
  simp (config := {decide := true}) [cxZ, cxX, cxQ2, cxY, op.eq_1, sz, msr, P1, P2, P3]

/-- the same hole with a single generator -/
def c0X : M := J (g 0) (J (J (g 0) (J (g 0) (g 0))) (g 0))
def c0Q2 : M := J c0X (g 0)
def c0Y : M := J c0Q2 (J (J (g 0) (J (g 0) (g 0))) c0Q2)

theorem cx_law_fails_g0 : op c0Y (op c0Y (op (op c0X (op (g 0) c0X)) c0Y)) ≠ c0X := by
  simp (config := {decide := true}) [c0X, c0Q2, c0Y, op.eq_1, sz, msr, P1, P2, P3]


theorem NEG_CONTROL : op cxZ cxX = g 2 := by
  simp (config := {decide := true}) [cxZ, cxX, cxQ2, cxY, op.eq_1, sz, msr, P1, P2, P3]

end submission
